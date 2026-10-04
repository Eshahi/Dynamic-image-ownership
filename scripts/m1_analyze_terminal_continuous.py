"""CPU-only A-C receipt, saved-endpoint and quality-cap analysis; no model loads."""
from __future__ import annotations
import argparse, csv, hashlib, json, math, subprocess, sys, time
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import m1_terminal_continuous as runner
import m1_blind_noise_core as core
from m1_latent_reconstruction import quality
VERSION='m1-terminal-continuous-analysis-v1'
DEPENDENCIES=('scripts/m1_terminal_continuous.py','research/m1-terminal-continuous-dev.json',
 'research/m1-terminal-continuous-design.md','scripts/m1_blind_noise_core.py','scripts/m1_blind_noise.py',
 'scripts/m1_dual_latent.py','scripts/m1_phase_residual.py','scripts/m1_phasemark.py',
 'scripts/m1_latent_reconstruction.py','scripts/revised_watermark_v5.py','scripts/revised_watermark_v4.py',
 'scripts/three_threat_models.py','scripts/three_threat_protocol.py','scripts/a6_clip_visual.py',
 'scripts/verify_science_assets.py','scripts/check_a6_lpips_assets.py','research/a6-candidate-model-assets.json',
 'research/m1-reconstruction-dev.json','configs/revised-watermark-v5.example.json')

def sha(p):
    digest=hashlib.sha256()
    with Path(p).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):digest.update(chunk)
    return digest.hexdigest()
def read(p):
    def invalid(value):raise ValueError('Nonfinite JSON token: '+value)
    return json.loads(Path(p).read_text(encoding='utf-8'),parse_constant=invalid)
def write(p,v):Path(p).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def finite(x):return type(x) in (int,float) and math.isfinite(x)
def equal(actual,expected,path='',tol=1e-10):
    if isinstance(expected,dict):
        if not isinstance(actual,dict) or set(actual)!=set(expected):raise ValueError(path+': key mismatch')
        for k,v in expected.items():equal(actual[k],v,path+'.'+k,tol)
    elif isinstance(expected,list):
        if not isinstance(actual,list) or len(actual)!=len(expected):raise ValueError(path+': list mismatch')
        for j,v in enumerate(expected):equal(actual[j],v,path+str(j),tol)
    elif type(expected) is bool or expected is None or isinstance(expected,str):
        if type(actual)!=type(expected) or actual!=expected:raise ValueError(path+': value mismatch')
    elif not finite(actual) or not math.isclose(actual,expected,rel_tol=tol,abs_tol=tol):raise ValueError(path+': numerical mismatch')

def quality_pass(q):
    if not isinstance(q,dict) or type(q.get('psnr_infinite')) is not bool:return None
    if q['psnr_infinite']:
        if q.get('psnr_db') is not None or q.get('mse_rgb8')!=0:return None
    elif not finite(q.get('psnr_db')):return None
    if not all(finite(q.get(k)) for k in ('mse_rgb8','ssim_rgb','lpips')):return None
    if q['mse_rgb8']<0 or q['lpips']<0:return None
    return (q['psnr_infinite'] or q['psnr_db']>35) and q['ssim_rgb']>.9 and q['lpips']<.1

def cap(source,delta):
    """Independent RGB8 replay of the frozen scalar bisection."""
    if source.dtype!=np.uint8 or delta.shape!=source.shape or not np.isfinite(delta).all():raise ValueError('Invalid cap inputs')
    def compose(w):return np.rint(255*np.clip(source.astype(np.float64)/255+w*delta,0,1)).astype(np.uint8)
    def sse(rgb):return int(np.square(source.astype(np.int64)-rgb.astype(np.int64)).sum())
    budget=255**2*10**(-35.2/10);lo,hi=0.,1.
    if sse(compose(1.))/source.size<=budget:lo=hi=1.
    else:
        for _ in range(36):
            mid=(lo+hi)/2
            if sse(compose(mid))/source.size<=budget:lo=mid
            else:hi=mid
    rgb=compose(lo);error=sse(rgb)
    return rgb,dict(weight=lo,lo=lo,hi=hi,budget_mse_rgb8=budget,sse_rgb8=error,mse_rgb8=error/source.size,iterations=0 if lo==1 else 36)

def inventory(rows):
    expected={r['id']:r for r in runner.planned()};groups={k:[] for k in expected};errors=[]
    if not isinstance(rows,list):return {k:None for k in expected},['conditions is not a list']
    for row in rows:
        if not isinstance(row,dict) or row.get('id') not in expected:errors.append('Unexpected/malformed condition');continue
        groups[row['id']].append(row)
    result={}
    for k,items in groups.items():
        if len(items)!=1:errors.append(k+': missing or duplicate');result[k]=None;continue
        r=items[0]
        if any(r.get(f)!=expected[k][f] for f in ('source_id','control','dose')):errors.append(k+': membership mismatch');result[k]=None
        else:result[k]=r
    return result,errors

def gates(rows,integrity):
    """Only independently verified blind endpoints count; missing never becomes zero."""
    expected=runner.planned();complete=all(rows.get(r['id'],{}).get('verified') is True for r in expected)
    def count(predicate,field):
        selected=[rows.get(r['id'],{}) for r in expected if predicate(r)]
        vals=[r.get(field) for r in selected]
        return dict(planned=len(vals),observed=sum(type(v) is bool for v in vals),positive=sum(v is True for v in vals))
    clean=lambda r:r['control']=='C1' and r['dose']=='clean'
    cycle=lambda r:r['control']=='C1' and r['dose']=='vae_cycle'
    cleanq=count(clean,'quality_pass');cleanboth=count(clean,'blind_both');cycles=count(cycle,'blind_semantic')
    negatives=[]
    for r in expected:
        item=rows.get(r['id'],{})
        for owner in core.OWNERS:
            if r['control']=='C0' or owner!=core.OWNERS[0]:
                d=item.get('blind',{}).get(owner,{})
                negatives.append(None if not item.get('verified') or not finite(d.get('s')) or not finite(d.get('i')) else d['s']<4 and d['i']<4)
    neg=dict(planned=28,observed=sum(type(v) is bool for v in negatives),below_both=sum(v is True for v in negatives))
    eligible=integrity and complete and neg['observed']==28
    return dict(inventory_complete=complete,receipt_integrity=integrity,clean_quality=cleanq,clean_blind_both=cleanboth,
        cycle_blind_semantic=cycles,negative_queries=neg,
        promotion=None if not eligible else cleanq['positive']==2 and cleanboth['positive']==2 and cycles['positive']==2 and neg['below_both']==28)

class Audit:
    def __init__(self,input_dir):self.base=Path(input_dir).resolve();self.artifacts={};self.paths={}
    def receipt(self,r,label,png=False,array=False,inside=True):
        if not isinstance(r,dict):raise ValueError(label+': missing receipt')
        p=Path(r['path']).resolve()
        if inside and not p.is_relative_to(self.base):raise ValueError(label+': artifact outside run')
        if sha(p)!=r['sha256']:raise ValueError(label+': hash mismatch')
        if inside:
            if p in self.paths and self.paths[p]!=label:raise ValueError(label+': duplicate artifact path')
            self.paths[p]=label
        self.artifacts[str(p)]=r['sha256']
        if png:
            with Image.open(p) as im:
                if im.mode!='RGB' or im.size!=(512,512):raise ValueError(label+': expected RGB512 PNG')
                value=np.asarray(im).copy()
            if hashlib.sha256(value.tobytes()).hexdigest()!=r.get('rgb8_sha256'):raise ValueError(label+': RGB8 hash mismatch')
            return value
        if array:
            value=np.load(p,allow_pickle=False)
            if value.dtype!=np.float64 or not np.isfinite(value).all():raise ValueError(label+': finite float64 array required')
            return value
        return p

def pixel_quality(q,a,b):
    if quality_pass(q) is None:raise ValueError('Malformed/nonfinite quality')
    for k,v in quality(a,b).items():equal(q.get(k),v,'quality.'+k,tol=1e-9)
    if type(q.get('quality_admissible')) is not bool or q['quality_admissible']!=quality_pass(q):raise ValueError('Quality conjunction mismatch')

def verify_case(audit,ce,recon):
    sid=ce['source_id'];source=audit.receipt(ce['source'],f'{sid}:source',png=True)
    frozen=next(c for c in runner.configuration()['cases'] if c['id']==sid)
    canonical,_=runner.old_a.source_rgb(frozen)
    if not np.array_equal(source,canonical):raise ValueError('Source preprocessing identity mismatch')
    if Path(ce['source']['path']).name!=f'{sid}-source.png':raise ValueError('Source artifact membership')
    init=ce['initialization'];audit.receipt(init,f'{sid}:initialization',inside=False)
    if init.get('run_json_sha256')!=sha(Path(runner.RECONSTRUCTION)/'run.json') or init.get('checkpoint_receipt',{}).get('step')!=200:raise ValueError('Initialization provenance mismatch')
    candidates=[v for v in recon.get('cases',[]) if v.get('id')==sid and v.get('outcome')=='completed']
    if len(candidates)!=1 or candidates[0].get('source_rgb8_sha256')!=ce['source']['rgb8_sha256']:raise ValueError('Initialization source identity mismatch')
    init_rows=[c for c in candidates[0]['checkpoints'] if c.get('step')==200]
    if len(init_rows)!=1 or init_rows[0]!=init['checkpoint_receipt'] or init['sha256']!=init_rows[0]['latent_sha256'] or Path(init['path']).resolve()!=(runner.RECONSTRUCTION/f'{sid}-step200.pt').resolve():raise ValueError('Initialization checkpoint receipt mismatch')
    checkpoints=ce.get('checkpoints',[])
    if not checkpoints or checkpoints[-1].get('step')!=100:raise ValueError('Final fixed checkpoint absent')
    steps=[]
    for c in checkpoints:
        audit.receipt(c,f'{sid}:checkpoint:{c.get("step")}');steps.append(c.get('step'))
        if Path(c['path']).name!=f'{sid}-step{c["step"]:03d}.pt':raise ValueError('Checkpoint path membership')
    if len(set(steps))!=len(steps) or any(type(s) is not int or s<0 or s>100 or s%10 for s in steps):raise ValueError('Malformed checkpoint sequence')
    if any(Path(v['path']).name!=f'{sid}-{k}.npy' for k,v in ce['float_arrays'].items()):raise ValueError('Float artifact membership')
    arrays={k:audit.receipt(v,f'{sid}:{k}',array=True) for k,v in ce['float_arrays'].items()}
    if set(arrays)!=set(('reference','decoded','residual','surrogate')) or any(v.shape!=(512,512,3) for v in arrays.values()):raise ValueError('Float stage inventory mismatch')
    if not np.allclose(arrays['decoded']-arrays['reference'],arrays['residual'],rtol=0,atol=7e-8):raise ValueError('Pure decoder residual mismatch')
    marked,receipt=cap(source,arrays['residual']);equal(ce['cap'],receipt,'cap')
    rho=float(np.sqrt(np.mean(arrays['residual']**2)));beta=min(1.,runner.EPSILON/rho) if rho else 1.
    equal(ce['residual_rms'],rho,'rho',tol=1e-6);equal(ce['beta_final'],beta,'beta',tol=1e-6)
    target=np.clip(source.astype(np.float64)/255+beta*arrays['residual'],0,1)
    if not np.allclose(target,arrays['surrogate'],rtol=0,atol=2e-7):raise ValueError('Differentiable cap stage mismatch')
    equal(ce['surrogate_vs_capped_rmse'],float(np.sqrt(np.mean((arrays['surrogate']-marked/255.)**2))),'cap rounding')
    for field,key in (('pure_reference_quality','reference'),('pure_final_quality','decoded')):
        pixel_quality(ce[field],source,np.rint(255*np.clip(arrays[key],0,1)).astype(np.uint8))
    for key in ('final_surrogate_scores','final_surrogate_cycle_scores'):
        if len(ce[key])!=2 or not all(finite(v) for v in ce[key]):raise ValueError('Missing float-stage oracle scores')
    return source,marked

def verify_row(audit,row,ce,source,marked,profile):
    rid=row['id']
    if row.get('outcome')!='completed':raise ValueError('Condition '+str(row.get('outcome'))+': '+str(row.get('error','not completed')))
    if Path(row['image']['path']).name!=rid+'.png' or Path(row['terminal_reader_latent']['path']).name!=rid+'-reader-z.npy' or Path(row['terminal_fp32_latent']['path']).name!=rid+'-fp32-z.npy':raise ValueError('Endpoint artifact membership')
    rgb=audit.receipt(row['image'],rid+':image',png=True)
    if row.get('source')!=ce['source']:raise ValueError('Source receipt differs')
    if row['dose']=='clean' and not np.array_equal(rgb,source if row['control']=='C0' else marked):raise ValueError('Clean PNG does not match source/cap')
    e=np.asarray(row['suspect_E'],np.float64);E=np.asarray(ce['source_E'],np.float64);h=row['suspect_H'];H=ce['source_H']
    for vector in (E,e):
        if vector.shape!=(512,) or not np.isfinite(vector).all() or abs(np.linalg.norm(vector)-1)>1e-6:raise ValueError('Invalid saved CLIP feature')
    for image,saved in ((rgb,h),(source,H)):
        actual=runner.codec.perceptual_hash(runner.codec.luminance_from_rgb(image.tolist()),profile=profile)
        if type(saved) is not int or actual!=saved:raise ValueError('Saved pHash differs from PNG')
    if row['control']=='C0' and row['dose']=='clean':
        if not np.array_equal(E,e) or H!=h:raise ValueError('Unchanged C0 feature identity mismatch')
    equal(row['source_clip_cosine'],float(E@e),'CLIP cosine');equal(row['source_phash_distance'],int((H^h).bit_count()),'pHash distance')
    z=audit.receipt(row['terminal_reader_latent'],rid+':reader',array=True)
    z32=audit.receipt(row['terminal_fp32_latent'],rid+':fp32',array=True)
    if z.shape!=(core.N,) or z32.shape!=(core.N,):raise ValueError('Endpoint latent shape')
    blind={owner:core.scores(z,e,h,owner) for owner in core.OWNERS}
    equal(row['owner_decisions'],blind,'blind')
    oracle16=core.scores(z,E,H,core.OWNERS[0]);oracle32=core.scores(z32,E,H,core.OWNERS[0])
    equal(row['source_template_oracle_fp16'],oracle16,'oracle16');equal(row['source_template_oracle_fp32'],oracle32,'oracle32')
    expected={owner:core.projection_diagnostic(E,H,e,h,owner) for owner in core.OWNERS}
    equal(row['projection_diagnostics'],expected,'projection')
    if not finite(row.get('extract_seconds')) or row['extract_seconds']<0:raise ValueError('Invalid latency')
    pixel_quality(row['quality_vs_source'],source,rgb)
    pixel_quality(row['quality_vs_same_arm_clean'],source if row['control']=='C0' else marked,rgb)
    if any(d['state']=='invalid_measurement' for d in blind.values()):raise ValueError('Invalid blind measurement')
    return dict(id=rid,source_id=row['source_id'],control=row['control'],dose=row['dose'],verified=True,
        quality_pass=quality_pass(row['quality_vs_source']),quality_vs_source=row['quality_vs_source'],
        quality_vs_same_arm_clean=row['quality_vs_same_arm_clean'],blind=blind,
        oracle_fp16=oracle16,oracle_fp32=oracle32,blind_both=blind[core.OWNERS[0]]['state']=='both_match',
        blind_semantic=blind[core.OWNERS[0]]['flags']['s'],extract_seconds=row['extract_seconds'],
        source_clip_cosine=row['source_clip_cosine'],source_phash_distance=row['source_phash_distance'])

def analyze(input_dir,output_dir):
    started=time.monotonic();base=Path(input_dir).resolve();out=Path(output_dir).resolve()
    if not out.is_relative_to((runner.MAIN/'.thesis-build/dev-runs').resolve()):raise ValueError('Fresh MAIN development output required')
    out.mkdir(parents=True,exist_ok=False)
    record=dict(schema=VERSION,commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=sys.argv,data_split='development',seeds=[0],config={'input_dir':str(base),'fixed_conditions':8,'fixed_queries':32,'source_clusters':2},
        outcome='started',duration_seconds=0.,inputs={},errors=[],outputs={})
    write(out/'run.json',record);errors=record['errors'];results={};audit=Audit(base)
    def attempt(label,fn):
        try:return fn()
        except Exception as ex:errors.append(label+': '+str(ex));return None
    run=attempt('run.json',lambda:read(base/'run.json')) or {}
    for name in ('run.json','manifest.json','conditions.json','journal.jsonl'):
        value=attempt(name,lambda n=name:sha(base/n))
        if value:record['inputs'][str(base/name)]=value
    def provenance():
        if run.get('schema')!=runner.VERSION or run.get('data_split')!='development':raise ValueError('Wrong source schema/split')
        cfg=runner.configuration();equal(run.get('config'),cfg,'config');equal(read(base/'manifest.json'),cfg,'manifest')
        if run.get('manifest_sha256')!=sha(base/'manifest.json'):raise ValueError('Manifest hash mismatch')
        deps=run.get('committed_files',{})
        if set(deps)!=set(DEPENDENCIES):raise ValueError('Dependency set incomplete/unexpected')
        for rel,r in deps.items():
            p=ROOT/rel
            if sha(p)!=r['working_sha256']:raise ValueError('Dependency working SHA: '+rel)
            oid=subprocess.check_output(['git','rev-parse',run['commit']+':'+rel],cwd=ROOT,text=True).strip()
            working=subprocess.check_output(['git','hash-object','--path='+rel,str(p)],cwd=ROOT,text=True).strip()
            if oid!=r['git_blob_oid'] or oid!=working:raise ValueError('Dependency commit/blob: '+rel)
        for c in cfg['cases']:
            if sha(c['path'])!=c['sha256']:raise ValueError('Raw development source SHA mismatch')
        for path,digest in run.get('output_hashes',{}).items():
            p=Path(path)
            if not p.is_absolute():p=base/p
            if not p.resolve().is_relative_to(base) or sha(p)!=digest:raise ValueError('Output SHA mismatch: '+str(path))
        expected_files={str(p.resolve()) for p in base.rglob('*') if p.is_file() and p.name!='run.json'}
        pinned_files={str((Path(p) if Path(p).is_absolute() else base/p).resolve()) for p in run.get('output_hashes',{})}
        if pinned_files!=expected_files:raise ValueError('Output hash inventory incomplete')
        from three_threat_models import verify_assets
        asset_receipt,package=verify_assets(runner.util.ASSETS,ROOT/'research/a6-candidate-model-assets.json')
        equal(run.get('assets'),asset_receipt,'assets')
        if run.get('lpips_learned_sha256')!=sha(package/'weights/v0.1/alex.pth'):raise ValueError('LPIPS receipt changed')
        if not finite(run.get('duration_seconds')) or run['duration_seconds']<0:raise ValueError('Invalid duration')
        if run.get('reconstruction_run_sha256')!=sha(runner.RECONSTRUCTION/'run.json'):raise ValueError('Reconstruction run hash mismatch')
        budget=run.get('gpu_allocation_budget',{})
        equal(budget,runner.gpu_allocation_budget(cfg['gpu_budget_bytes'],budget.get('free_bytes_before_models'),budget.get('total_bytes'),cfg['gpu_reserve_bytes']),'GPU allocation budget')
        if run.get('outcome')=='completed':
            peak=run.get('peak_allocated_bytes')
            if type(peak) is not int or peak<0 or peak>budget['effective_allocation_bytes']:raise ValueError('GPU peak exceeds cap or missing')
            if run['duration_seconds']>cfg['run_seconds_cap']:raise ValueError('Cumulative wall cap exceeded')
            if sum(p.stat().st_size for p in base.rglob('*') if p.is_file())>cfg['artifact_budget_bytes']:raise ValueError('Artifact cap exceeded')
        if run.get('resume_input'):
            r=run['resume_input'];p=Path(r['path'])/'run.json'
            if sha(p)!=r['run_sha256']:raise ValueError('Resume source receipt changed')
            prior=read(p)
            for k in ('commit','committed_files','manifest_sha256'):
                if prior.get(k)!=run.get(k):raise ValueError('Resume fingerprint mismatch')
        return True
    integrity=attempt('provenance',provenance) is True
    raw=attempt('conditions',lambda:read(base/'conditions.json')) or []
    if run.get('conditions')!=raw:errors.append('run/conditions snapshot mismatch')
    selected,inv_errors=inventory(raw);errors.extend(inv_errors)
    write(out/'input-conditions.json',raw)
    recon=attempt('reconstruction',lambda:read(runner.RECONSTRUCTION/'run.json')) or {}
    profile=attempt('profile',lambda:runner.codec.validate_profile(runner.codec.load_profile(ROOT/'configs/revised-watermark-v5.example.json')))
    events=run.get('case_events',[]);contexts={}
    if not isinstance(events,list) or any(not isinstance(c,dict) or c.get('source_id') not in runner.IDS for c in events):
        errors.append('Unexpected/malformed case events');events=[]
    for sid in runner.IDS:
        cases=[c for c in events if c.get('source_id')==sid]
        if len(cases)!=1:errors.append(str(sid)+': missing/duplicate source event');continue
        ce=cases[0]
        if ce.get('outcome')!='completed':errors.append(str(sid)+': source event '+str(ce.get('outcome')))
        ctx=attempt(str(sid)+':source stages',lambda:verify_case(audit,ce,recon))
        if ctx:contexts[sid]=(ce,*ctx)
    for planned in runner.planned():
        rid=planned['id'];row=selected[rid];ctx=contexts.get(planned['source_id'])
        before=len(errors)
        value=attempt(rid,lambda:verify_row(audit,row,*ctx,profile)) if row and ctx and profile else None
        results[rid]=value or dict(**planned,verified=False,input_outcome=row.get('outcome') if row else None,reason=errors[before:] or ['Missing/invalid source or condition'],quality_pass=None,blind_both=None,blind_semantic=None)
        results[rid]['human_visual_verdict']=None
    record['source_outcome']=run.get('outcome');record['source_error']=run.get('error')
    if run.get('outcome')!='completed':errors.append('Source run is '+str(run.get('outcome'))+'; retained source error: '+str(run.get('error')))
    for r in results.values():
        with (out/'journal.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(r,allow_nan=False)+'\n')
    record['gate']=gates(results,integrity and not errors)
    record['stage_scope']='Surrogate float oracle is recorded-only; saved PNG fp32/source-oracle, fp16/source-oracle and blind endpoints recomputed float64. LPIPS and CLIP model inference not repeated.'
    record['budget_limitations']='RAM checked during execution; no retained peak RAM measurement. Artifact bytes recomputed; GPU/wall receipts verified, not independently monitored.'
    record['budget_receipt']={k:run.get(k) for k in ('duration_seconds','attempt_duration_seconds','peak_allocated_bytes','gpu_allocation_budget')}
    write(out/'conditions.json',list(results.values()))
    table=[]
    for r in results.values():
        for owner in core.OWNERS:
            d=r.get('blind',{}).get(owner,{})
            table.append(dict(id=r['id'],source_id=r['source_id'],control=r['control'],dose=r['dose'],owner=owner,
                verified=r['verified'],s=d.get('s'),i=d.get('i'),state=d.get('state'),quality_pass=r.get('quality_pass'),
                psnr_db=r.get('quality_vs_source',{}).get('psnr_db'),ssim=r.get('quality_vs_source',{}).get('ssim_rgb'),
                lpips=r.get('quality_vs_source',{}).get('lpips'),extract_seconds=r.get('extract_seconds')))
    with (out/'queries.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(table[0]));writer.writeheader();writer.writerows(table)
    stages=[]
    for sid in runner.IDS:
        ce=next((v for v in events if v.get('source_id')==sid),{})
        for field,dose in (('final_surrogate_scores','clean'),('final_surrogate_cycle_scores','vae_cycle')):
            values=ce.get(field,[None,None])
            if not isinstance(values,list) or len(values)!=2 or not all(finite(v) for v in values):values=[None,None]
            stages.append(dict(source_id=sid,control='C1',dose=dose,stage='float-surrogate-source-oracle-recorded-only',s=values[0] if len(values)==2 else None,i=values[1] if len(values)==2 else None,verified=False))
    for r in results.values():
        for field,stage in (('oracle_fp32','PNG-fp32-source-oracle'),('oracle_fp16','PNG-fp16-source-oracle'),('blind','PNG-fp16-suspect-blind')):
            d=r.get(field,{})
            if field=='blind':d=d.get(core.OWNERS[0],{})
            stages.append(dict(source_id=r['source_id'],control=r['control'],dose=r['dose'],stage=stage,s=d.get('s'),i=d.get('i'),verified=r['verified']))
    write(out/'stages.json',stages)
    write(out/'artifact-receipts.json',audit.artifacts)
    record['outcome']='completed' if not errors and run.get('outcome')=='completed' and record['gate']['inventory_complete'] else 'incomplete'
    record['duration_seconds']=time.monotonic()-started
    record['outputs']={p.name:sha(p) for p in out.iterdir() if p.is_file() and p.name!='run.json'}
    write(out/'run.json',record)
    return record

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input-dir',type=Path,required=True);p.add_argument('--output-dir',type=Path,required=True)
    args=p.parse_args();result=analyze(args.input_dir,args.output_dir);print(json.dumps({'outcome':result['outcome'],'gate':result['gate'],'errors':result['errors']},allow_nan=False))
    return 0 if result['outcome']=='completed' else 2
if __name__=='__main__':raise SystemExit(main())
