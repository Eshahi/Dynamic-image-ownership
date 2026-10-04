"""Fixed B3-C pilot analysis; no inference, threshold fitting or exclusions."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
MAIN=Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5')
VERSION='m1-blind-noise-analysis-v1'
IDS=(1675,4795)
ALPHAS=(.025,.05,.1)
ROUTES=('pure','hybrid')
OWNERS=tuple('qim-pilot-owner-'+s for s in ('alpha','beta','gamma','delta'))
DOSES=('clean','vae_cycle')
PROJECTION=('kernel_exact','kernel_projected_raw','kernel_projected_normalized','norm_sq_1','norm_sq_2','inner_error','normalized_error','delta','variance_inner','variance_norm_1','variance_norm_2','sampling_fraction')
REQUIRED_CODE={'scripts/m1_blind_noise.py','research/m1-blind-noise-dev.json','scripts/m1_blind_noise_core.py','research/m1-blind-noise-template-design.md','scripts/m1_gaussian_shading.py','scripts/m1_phasemark.py','scripts/m1_latent_reconstruction.py','scripts/three_threat_models.py','scripts/a6_clip_visual.py','scripts/verify_science_assets.py','scripts/check_a6_lpips_assets.py','research/a6-candidate-model-assets.json','research/m1-reconstruction-dev.json','configs/revised-watermark-v5.example.json','scripts/revised_watermark_v5.py'}

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def sanitized(value):
    if isinstance(value,float) and not math.isfinite(value):return 'nonfinite: '+repr(value)
    if isinstance(value,dict):return {k:sanitized(v) for k,v in value.items()}
    if isinstance(value,list):return [sanitized(v) for v in value]
    return value
def write(path,value):Path(path).write_text(json.dumps(sanitized(value),indent=2,allow_nan=False)+'\n',encoding='utf-8')
def finite(value):return type(value) in (int,float) and math.isfinite(value)
def planned():
    return [dict(id=f'{ident}-{alpha}-{route}-{control}-{dose}',source_id=ident,alpha=alpha,route=route,control=control,dose=dose)
            for ident in IDS for alpha in ALPHAS for route in ROUTES for control in ('C0','C1') for dose in DOSES]

def quality_valid(q):
    if not isinstance(q,dict) or type(q.get('psnr_infinite'))!=bool:return False
    psnr=(q.get('psnr_db') is None and q.get('mse_rgb8')==0 and type(q.get('mse_rgb8')) in (int,float)) if q['psnr_infinite'] else finite(q.get('psnr_db'))
    return psnr and finite(q.get('mse_rgb8')) and q['mse_rgb8']>=0 and all(finite(q.get(k)) for k in ('ssim_rgb','lpips'))

def quality_pass(q):
    return quality_valid(q) and (q['psnr_infinite'] or q['psnr_db']>35) and q['ssim_rgb']>.9 and q['lpips']<.1

def expected_state(s,i):
    if s is None or i is None:return 'invalid_measurement'
    return ('both_match' if i>=4 else 'semantic_only') if s>=4 else ('ambiguous_instance_only' if i>=4 else 'neither_supported')

def decision_errors(d):
    if not isinstance(d,dict):return ['missing owner decision']
    if not {'s','i','flags','denominators','state','errors'}.issubset(d) or any(not isinstance(d.get(k),dict) or set(d[k])!={'s','i'} for k in ('flags','denominators')):return ['missing/malformed score/flag/denominator fields']
    invalid=d.get('state')=='invalid_measurement'
    errors=[]
    for k in ('s','i'):
        value=d.get(k);flag=d.get('flags',{}).get(k);den=d.get('denominators',{}).get(k)
        if invalid and value is None:
            if flag is not None or den is not None:errors.append('invalid score flag/denominator mismatch')
        elif not finite(value) or not finite(den) or den<=0 or type(flag)!=bool or flag!=(value>=4):errors.append('malformed score/flag/denominator '+k)
    if not isinstance(d.get('errors'),list):errors.append('missing decision errors')
    if not errors and d.get('state')!=expected_state(d.get('s'),d.get('i')):errors.append('state differs from frozen threshold')
    return errors

def projection_errors(d):
    if not isinstance(d,dict) or 'normalization_error_bound' not in d or any(not finite(d.get(k)) for k in PROJECTION):return ['missing/nonfinite projection fields']
    if d['norm_sq_1']<=0 or d['norm_sq_2']<=0 or any(d[k]<0 for k in ('inner_error','normalized_error','delta','variance_inner','variance_norm_1','variance_norm_2')):return ['invalid projection norms/errors/variances']
    bound=d.get('normalization_error_bound')
    if (d['delta']<1 and (not finite(bound) or bound<0)) or (d['delta']>=1 and bound is not None):return ['invalid normalization bound']
    return []

def row_errors(row):
    errors=[]
    if row.get('outcome')!='completed':return ['source row '+str(row.get('outcome','missing'))]
    if set(row.get('owner_decisions',{}))!=set(OWNERS):errors.append('four-owner roster missing')
    for owner in OWNERS:
        errors.extend(owner+': '+e for e in decision_errors(row.get('owner_decisions',{}).get(owner)))
        errors.extend(owner+': '+e for e in projection_errors(row.get('projection_diagnostics',{}).get(owner)))
    for key in ('quality_vs_source','quality_vs_same_arm_clean'):
        if not quality_valid(row.get(key)):errors.append('malformed quality '+key)
    for key in ('extract_seconds','source_clip_cosine','semantic_template_cosine'):
        if not finite(row.get(key)) or (key=='extract_seconds' and row[key]<0):errors.append('nonfinite/missing '+key)
    if type(row.get('source_phash_distance'))!=int or not 0<=row['source_phash_distance']<=32:errors.append('invalid source hash drift')
    if type(row.get('suspect_H'))!=int or not 0<=row['suspect_H']<2**32:errors.append('invalid suspect hash')
    feature=row.get('suspect_E')
    if not isinstance(feature,list) or len(feature)!=512 or not all(finite(v) for v in feature) or abs(sum(v*v for v in feature)-1)>2.1e-6:errors.append('invalid suspect feature')
    forward=row.get('forward',{})
    if not finite(forward.get('seconds')) or forward.get('seconds',-1)<0 or type(forward.get('nfe'))!=int or forward.get('nfe')!=50 or forward.get('safety_blocked') is not False:errors.append('invalid forward receipt')
    if row.get('control')=='C1':
        p=row.get('perturbation',{})
        if any(not finite(p.get(k)) or p[k]<0 for k in ('l2','rounding_l2','template_rms')):errors.append('missing/nonfinite perturbation')
    return errors

def normalize(rows):
    index={};unexpected=[]
    for row in rows:
        if not isinstance(row,dict):unexpected.append({'row':row,'error':'non-object row'});continue
        index.setdefault(row.get('id'),[]).append(row)
    expected=planned();ids={p['id'] for p in expected}
    unexpected.extend({'row':r,'error':'unexpected identity'} for ident,rs in index.items() if ident not in ids for r in rs)
    result=[]
    for p in expected:
        found=index.get(p['id'],[])
        if len(found)!=1:
            result.append(dict(**p,outcome='missing' if not found else 'duplicate',complete=False,errors=['missing row' if not found else 'duplicate identity'],attempts=found));continue
        row=dict(found[0]);errors=['identity field differs '+k for k,v in p.items() if type(row.get(k))!=type(v) or row.get(k)!=v]
        try:errors+=row_errors(row)
        except (TypeError,ValueError,KeyError,AttributeError) as e:errors.append('malformed nested measurement: '+repr(e))
        row.update(complete=not errors,errors_analysis=errors);result.append(row)
    return result,unexpected

def distribution(values):
    values=[v for v in values if finite(v)]
    return dict(n=len(values),mean=statistics.mean(values) if values else None,median=statistics.median(values) if values else None,
                sample_sd=statistics.stdev(values) if len(values)>1 else None,min=min(values) if values else None,max=max(values) if values else None)

def summarize(rows,provenance_ok):
    groups=[];queries=[]
    for p in rows:
        for owner in OWNERS:
            decisions=p.get('owner_decisions',{})
            d=decisions.get(owner,{}) if isinstance(decisions,dict) else {}
            if not isinstance(d,dict):d={}
            queries.append({k:p.get(k) for k in ('id','source_id','alpha','route','control','dose')}|dict(owner=owner,row_complete=p['complete'],s=d.get('s'),i=d.get('i'),state=d.get('state','missing'),flags=d.get('flags'),errors=d.get('errors')))
    for route in ROUTES:
        for alpha in ALPHAS:
            for control in ('C0','C1'):
                for dose in DOSES:
                    g=[r for r in rows if (r['route'],r['alpha'],r['control'],r['dose'])==(route,alpha,control,dose)];valid=[r for r in g if r['complete']]
                    states={o:{s:sum(r.get('owner_decisions',{}).get(o,{}).get('state')==s for r in valid) for s in ('both_match','semantic_only','neither_supported','ambiguous_instance_only','invalid_measurement')} for o in OWNERS}
                    metrics={k:distribution([r.get(k) for r in valid]) for k in ('extract_seconds','source_clip_cosine','semantic_template_cosine','source_phash_distance')}
                    for k in ('psnr_db','ssim_rgb','lpips'):metrics['quality_vs_source_'+k]=distribution([r['quality_vs_source'][k] for r in valid])
                    metrics['psnr_infinite_n']=sum(r['quality_vs_source']['psnr_infinite'] for r in valid)
                    for o in OWNERS:
                        for k in ('s','i'):metrics[o+'_'+k]=distribution([r['owner_decisions'][o][k] for r in valid])
                        for k in PROJECTION+('normalization_error_bound',):metrics[o+'_projection_'+k]=distribution([r['projection_diagnostics'][o][k] for r in valid])
                    for k in ('l2','rounding_l2','template_rms'):metrics['perturbation_'+k]=distribution([r.get('perturbation',{}).get(k) for r in valid if isinstance(r.get('perturbation'),dict)])
                    groups.append(dict(route=route,alpha=alpha,control=control,dose=dose,planned_rows=2,distinct_source_n=len({r['source_id'] for r in g}),complete_distinct_source_n=len({r['source_id'] for r in valid}),complete_rows=len(valid),missing_or_failed_rows=2-len(valid),quality_all_three_n=sum(quality_pass(r['quality_vs_source']) for r in valid),states=states,metrics=metrics))
    gates=[]
    for route in ROUTES:
        for alpha in ALPHAS:
            g=[r for r in rows if r['route']==route and r['alpha']==alpha];complete=len(g)==8 and all(r['complete'] for r in g)
            eligible=complete and provenance_ok
            clean=[r for r in g if r['control']=='C1' and r['dose']=='clean'];vae=[r for r in g if r['control']=='C1' and r['dose']=='vae_cycle']
            quality=all(quality_pass(r['quality_vs_source']) for r in clean) if eligible else None
            both=all(r['owner_decisions'][OWNERS[0]]['state']=='both_match' for r in clean) if eligible else None
            semantic=all(r['owner_decisions'][OWNERS[0]]['flags']['s'] is True for r in vae) if eligible else None
            negatives=all(finite(d[k]) and d[k]<4 for r in g for o,d in r['owner_decisions'].items() if r['control']=='C0' or o!=OWNERS[0] for k in ('s','i')) if eligible else None
            gates.append(dict(route=route,alpha=alpha,planned_rows=8,distinct_source_n=2,complete_rows=sum(r['complete'] for r in g),provenance_ok=provenance_ok,clean_quality=quality,clean_both_match=both,vae_semantic=semantic,c0_and_wrong_below_both=negatives,passes=all((quality,both,semantic,negatives)) if eligible else None))
    hybrid=[g for g in gates if g['route']=='hybrid'];selection_complete=provenance_ok and len(rows)==48 and all(r['complete'] for r in rows) and all(g['passes'] is not None for g in hybrid)
    selected=next((g['alpha'] for g in hybrid if g['passes']),None) if selection_complete else None
    return dict(groups=groups,queries=queries,gates=gates,selection=dict(rule='smallest passing hybrid alpha; no pure substitution',complete=selection_complete,selected_alpha=selected,outcome=('selected' if selected is not None else 'no_dose_passed') if selection_complete else 'incomplete'),planned_rows=48,planned_queries=192,distinct_source_clusters=2)

def load(directory):
    directory=Path(directory).resolve();errors=[];receipts=[]
    def read(name,default):
        path=directory/name
        try:
            receipts.append(dict(path=str(path),sha256=sha(path),size_bytes=path.stat().st_size));return json.loads(path.read_text(encoding='utf-8'))
        except Exception as e:errors.append(name+': '+repr(e));return default
    run=read('run.json',{});manifest=read('manifest.json',{});conditions=read('conditions.json',[])
    expected=json.loads((ROOT/'research/m1-blind-noise-dev.json').read_text())
    if manifest!=expected or run.get('config')!=expected or run.get('data_split')!='development':errors.append('frozen manifest/config/split differs')
    if manifest and run.get('manifest_sha256')!=sha(directory/'manifest.json'):errors.append('manifest hash differs')
    if run.get('conditions')!=conditions:errors.append('run/conditions snapshots differ')
    if run.get('outcome')!='completed':errors.append('source run not completed: '+str(run.get('outcome')))
    hashes=run.get('output_hashes',{})
    if not isinstance(hashes,dict):hashes={};errors.append('invalid output hash map')
    files={p.name for p in directory.iterdir() if p.is_file() and p.name!='run.json'}
    if set(hashes)!=files:errors.append('output hash inventory differs')
    for name,digest in hashes.items():
        try:
            if Path(name).name!=name or sha(directory/name)!=digest:raise ValueError('output hash/path differs')
        except Exception as e:errors.append(name+': '+repr(e))
    for case in expected['cases']:
        try:
            if sha(case['path'])!=case['sha256']:raise ValueError('raw reserved source hash differs')
            receipts.append(dict(path=case['path'],sha256=case['sha256']))
        except Exception as e:errors.append('source '+str(case['id'])+': '+repr(e))
    code=run.get('committed_files',{})
    if not isinstance(code,dict) or not code:errors.append('missing code provenance');code={}
    if not REQUIRED_CODE.issubset(code):errors.append('mandatory scientific code/config receipts missing')
    for name,receipt in code.items():
        try:
            path=(ROOT/name).resolve()
            if not path.is_relative_to(ROOT):raise ValueError('code path escapes workspace')
            if sha(path)!=receipt['working_sha256']:raise ValueError('retained code hash differs')
            blob=subprocess.check_output(['git','rev-parse',run['commit']+':'+name],cwd=ROOT,text=True,stderr=subprocess.DEVNULL).strip()
            if blob!=receipt['git_blob_oid']:raise ValueError('commit/blob provenance differs')
        except Exception as e:errors.append('code '+name+': '+repr(e))
    if run.get('nfe_total')!=500:errors.append('whole-run NFE differs/missing')
    normalized,unexpected=normalize(conditions if isinstance(conditions,list) else [])
    if unexpected:errors.append('unexpected condition rows retained')
    cache={}
    for row in normalized:
        if not row['complete']:continue
        try:
            for key in ('image','source'):
                rec=row[key];path=Path(rec['path']).resolve()
                if path.parent!=directory or path.suffix.lower()!='.png':raise ValueError('PNG path differs')
                suffix='clean' if row['dose']=='clean' else 'vae'
                image_name=(f"{row['source_id']}-{row['route']}-C0-{suffix}.png" if row['control']=='C0' else f"{row['source_id']}-{row['alpha']}-{row['route']}-C1-{suffix}.png")
                if path.name!=(image_name if key=='image' else f"{row['source_id']}-source.png"):raise ValueError('PNG identity/path membership differs')
                if path not in cache:
                    from PIL import Image
                    if rec['sha256']!=hashes.get(path.name) or sha(path)!=rec['sha256']:raise ValueError('PNG receipt hash differs')
                    with Image.open(path) as image:
                        if image.mode!='RGB' or image.size!=(512,512):raise ValueError('PNG RGB512 differs')
                        cache[path]=(rec['sha256'],hashlib.sha256(image.tobytes()).hexdigest())
                if cache[path]!=(rec['sha256'],rec['rgb8_sha256']):raise ValueError('PNG/RGB8 receipt mismatch')
            forward=row['forward'];fp=Path(forward['float_path']).resolve()
            expected_float=f"{row['source_id']}-D0.npy" if row['control']=='C0' else f"{row['source_id']}-{row['alpha']}-Da.npy"
            if fp.parent!=directory or fp.name!=expected_float or hashes.get(fp.name)!=forward['float_sha256']:raise ValueError('forward float receipt differs')
        except Exception as e:row.update(complete=False);row['errors_analysis'].append('artifact: '+repr(e))
    events=run.get('case_events',[])
    if not isinstance(events,list) or len(events)!=2 or {e.get('source_id') for e in events if isinstance(e,dict)}!=set(IDS):errors.append('source event roster differs')
    else:
        for event in events:
            if event.get('outcome')!='completed' or event.get('inverse_nfe')!=50 or not finite(event.get('inverse_seconds')):errors.append('incomplete/malformed source event '+str(event.get('source_id')))
    pairs=run.get('source_pair_projection',{})
    if not isinstance(pairs,dict):pairs={}
    if set(pairs)!=set(OWNERS) or any(projection_errors(pairs.get(o)) for o in OWNERS):errors.append('source pair projection missing/malformed')
    return run,normalized,unexpected,errors,receipts

def flatten(value,prefix=''):
    value=sanitized(value)
    out={}
    for k,v in value.items():
        key=prefix+k
        if isinstance(v,dict):out.update(flatten(v,key+'_'))
        elif isinstance(v,list):out[key]=json.dumps(v,allow_nan=False)
        else:out[key]=v
    return out

def table(path,rows):
    rows=[flatten(r) for r in rows];fields=sorted({k for r in rows for k in r})
    with Path(path).open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)

def analyze(input_dir,output_dir):
    output=Path(output_dir).resolve()
    if not output.is_relative_to((MAIN/'.thesis-build/dev-runs').resolve()):raise ValueError('fresh MAIN dev-runs output required')
    output.mkdir(parents=True,exist_ok=False);started=time.monotonic()
    record=dict(schema=VERSION,command=sys.argv,data_split='development',seeds=[0],config=dict(threshold_s=4.,threshold_i=4.,quality=dict(psnr_gt=35,ssim_gt=.9,lpips_lt=.1)),outcome='started',commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),script_sha256=sha(__file__))
    write(output/'run.json',record)
    try:
        source,rows,unexpected,errors,receipts=load(input_dir)
        summary=summarize(rows,not errors)
        analysis=dict(**summary,rows=rows,unexpected_rows=unexpected,errors=errors,source_outcome=source.get('outcome'),source_commit=source.get('commit'),source_pair_projection=source.get('source_pair_projection'),source_case_events=source.get('case_events'),timing_caveat='owner queries share cached suspect observations; C0 artifacts repeat across amplitudes; timings are not independent standalone detector measurements',human_visual_verdict=None,label='exploratory two-source pilot; no threat/security/global acceptance verdict')
        write(output/'analysis.json',analysis);table(output/'conditions.csv',rows);table(output/'queries.csv',summary['queries']);table(output/'groups.csv',summary['groups']);table(output/'gates.csv',summary['gates'])
        record.update(outcome='completed_descriptive_analysis' if not errors and all(r['complete'] for r in rows) else 'incomplete_descriptive_analysis',input_receipts=receipts,source_commit=source.get('commit'),source_outcome=source.get('outcome'),errors=errors,selection=summary['selection'])
    except (Exception,KeyboardInterrupt) as e:
        rows,_=normalize([]);write(output/'analysis.json',dict(rows=rows,planned_rows=48,planned_queries=192,errors=[repr(e)],selection=dict(complete=False,selected_alpha=None,outcome='incomplete')));record.update(outcome='failed',error=repr(e))
    finally:
        record.update(duration_seconds=time.monotonic()-started,output_hashes={p.name:sha(p) for p in output.iterdir() if p.is_file() and p.name!='run.json'});write(output/'run.json',record)
    return 0 if record['outcome']=='completed_descriptive_analysis' else 1

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--input-dir',type=Path,required=True);parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args();raise SystemExit(analyze(args.input_dir,args.output_dir))
