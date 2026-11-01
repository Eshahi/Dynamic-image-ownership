"""Bounded CPU reader-only T2/T3 on allowlisted saved development PNGs.

No embedding, attack, diffusion, or training call exists here. Inventory and
each numbered batch are separate invocations; partial batches stay recorded.
"""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import runpy
import subprocess
import sys
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
RD = ROOT/'research/f5-components-20261101'
MAIN = Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5')
DEV = MAIN/'.thesis-build/dev-runs'
ASSETS = MAIN/'.thesis-build/assets/a6'
OUT = RD/'results/wp4-pixels'
API = runpy.run_path(str(Path(__file__).with_name('account_saved_development.py')))
RADII = (0,1,2,3,4,6)
CELLS = ('clean','D1','D3','X1','X2','R0-0.2','R1-0.2','R3-0.2',
         'R1-mode-0.2','R1-smooth-0.2','R1-rinse-0.1')
T4DIR = DEV/'20261005-0700-f5r2-t4'
GATEDIR = DEV/'20261005-0640-f5-gate-soft-views7'
T5JSON = DEV/'20261005-0700-f5r2-t5/run.json'
V5DIR = MAIN/'.thesis-build/v5-study-runs/C4-v5-two-tier-development/c4-v5-two-tier-dev-001'

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def write(path,obj):
    path.write_text(json.dumps(obj,indent=2)+'\n',encoding='utf-8')

def header(start):
    return dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                command=[sys.executable,*sys.argv],seconds=time.monotonic()-start,
                cuda_visible_devices=os.environ.get('CUDA_VISIBLE_DEVICES'),phase_b_journals='off',
                script_sha256=digest(__file__),plan_sha256=digest(Path(__file__).with_name('WP4-TEST-PLAN.md')))

def cellof(r):return r['channel'] if r['strength'] is None else f"{r['channel']}-{r['strength']}"

def inventory():
    start=time.monotonic()
    if OUT.exists():raise FileExistsError(OUT)
    data,provenance=API['load']('stage2')
    rows=[r for _,r in data.values()]
    sources=sorted({r['source_id'] for r in rows if r['channel']=='clean'})
    assert len(sources)==60
    split={s:'DESIGN' if j%2==0 else 'EVALUATE' for j,s in enumerate(sources)}
    chosen=sources[:8] # first four positions of each half; pre-outcome rule
    index={(cellof(r),r['source_id'],r['arm'],r['seed']):r for r in rows}
    clean={(r['source_id'],r['arm']):r for r in rows if r['channel']=='clean' and r['status']=='ok'}
    items=[]
    for cell in CELLS:
        for s in chosen:
            for seed in ((None,) if cell in ('clean','D1','D3','X1','X2') else API['SEEDS']):
                for arm in ('v5-r3','f5-r2','unmarked'):
                    r=index.get((cell,s,arm,seed))
                    z=dict(id=f'{cell}:{s}:{arm}:{seed}',panel='stage2',source=s,split=split[s],cell=cell,seed=seed,arm=arm,
                           status=r['status'] if r else 'absent',path=None,calls={},payloads={})
                    if r and r['status']=='ok':
                        remote=r['output']['path'];prefix='stage2a' if '/stage2a-full/' in remote else 'stage2b'
                        base=DEV/('20261024-1431-encoder-transfer-stage2a' if prefix=='stage2a' else '20261025-0128-encoder-transfer-stage2b')/'results'/f'{prefix}-full/images'
                        p=base/Path(remote).name
                        z.update(path=str(p),expected_sha256=r['output']['sha256'],exists=p.is_file(),calls=r['detections'])
                        for method in ('v5-r3','f5-r2'):
                            if (s,method) in clean:z['payloads'][method]=clean[s,method]['payload']
                    items.append(z)
    # Explicit earlier development manifests, not an unrestricted pixel search.
    gate=json.loads((GATEDIR/'run.json').read_text(encoding='utf-8'))
    assert gate.get('data_split')=='development'
    t4=json.loads((T4DIR/'run.json').read_text(encoding='utf-8'))
    assert t4.get('data_split')=='development'
    t5=json.loads(T5JSON.read_text(encoding='utf-8'))
    oldsources=sorted({r['donor_id'] for r in t4['rows']}|{r['recipient_id'] for r in t4['rows']}|
                      {r['left'] for r in t5['rows']}|{r['right'] for r in t5['rows']})
    oldsplit={s:'DESIGN' if j%2==0 else 'EVALUATE' for j,s in enumerate(oldsources)}
    for r in t4['rows']:
        p=T4DIR/f"t4-residual-{r['donor_id']}-{r['recipient_id']}-{r['scale']}.png"
        items.append(dict(id=p.stem,panel='T4',source=r['recipient_id'],donor=r['donor_id'],
                          split=oldsplit[r['recipient_id']],donor_split=oldsplit[r['donor_id']],cell=f"T4-{r['scale']}",
                          seed=None,arm='f5-r2',status='ok',exists=p.is_file(),path=str(p),calls={},payloads={}))
    for s in oldsources:
        for control in ('C0','C1'):
            p=GATEDIR/'images'/f'clean-{s}-{control}.png'
            items.append(dict(id=f'T5-clean-{s}-{control}',panel='T5',source=s,split=oldsplit[s],cell='clean',seed=None,
                              arm='unmarked' if control=='C0' else 'f5-r2',methods=['f5-r2'],status='ok',exists=p.is_file(),
                              path=str(p),calls={},payloads={}))
    v5path=V5DIR/'outputs/results.json'
    v5old=json.loads(v5path.read_text(encoding='utf-8'))
    for r in v5old['rows']:
        if r.get('axis')!='T4' and not r['id'].startswith('clean-'):continue
        panel='T4' if r.get('axis')=='T4' else 'T5'
        s=r['recipient_id'] if panel=='T4' else r['source_id']
        if s not in oldsplit:continue
        p=V5DIR/r['image']['path']
        assert p.resolve().is_relative_to(V5DIR.resolve())
        items.append(dict(id='v5-old:'+r['id'],panel=panel,source=s,split=oldsplit[s],donor=r.get('donor_id'),
                          donor_split=oldsplit.get(r.get('donor_id')),cell=f"T4-{r['arm']}-{r.get('scale')}" if panel=='T4' else 'clean',
                          seed=None,arm='unmarked' if r.get('control')=='C0' else 'v5-r3',methods=['v5-r3'],status='ok',
                          exists=p.is_file(),path=str(p),expected_sha256=r['image']['sha256'],calls={},payloads={},
                          saved_features=r['clip']['values'],historical_roster=4))
    OUT.mkdir()
    write(OUT/'inventory.json',dict(items=items,chosen_stage2=chosen,split=split,old_split=oldsplit,
                                  cells=CELLS,profile=gate['profile'],stage2_input=provenance,
                                  panel_manifests={str(p):digest(p) for p in (GATEDIR/'run.json',T4DIR/'run.json',T5JSON,v5path)},
                                  t5_pairs=t5['rows']))
    write(OUT/'inventory-provenance.json',header(start))
    print(json.dumps(dict(items=len(items),existing=sum(x.get('exists',False) for x in items),selected_sources=chosen)))

def ball(scores,center,r):
    """Exact separable score maximum with at most r flips; scores normalized."""
    n=len(scores);bits=[(center>>(n-1-j))&1 for j in range(n)]
    fixed=sum(s[b] for s,b in zip(scores,bits))
    gains=sorted(((s[1-b]-s[b],j) for j,(s,b) in enumerate(zip(scores,bits))),key=lambda x:(-x[0],x[1]))
    code=center;best=fixed
    for gain,j in gains[:r]:
        if gain>0:best+=gain;code^=1<<(n-1-j)
    return best,code

def synthetic_check():
    import random
    rng=random.Random(20261101);checks=0
    for n in range(1,9):
        for _ in range(20):
            scores=[(rng.choice([-2.,-1.,0.,1.,2.]),rng.choice([-2.,-1.,0.,1.,2.])) for j in range(n)]
            center=rng.randrange(1<<n)
            for r in range(n+1):
                best,code=ball(scores,center,r)
                truth=max(sum(s[(c>>(n-1-j))&1] for j,s in enumerate(scores)) for c in range(1<<n) if (c^center).bit_count()<=r)
                assert best==truth and (code^center).bit_count()<=r
                checks+=1
    return checks

def bound_threshold(r):return API['THRESHOLDS'][r]

def decode(projections,table,center,v5):
    norm=math.sqrt(sum(v*v for v in projections))
    scores=[[sum(sign*v for sign,v in zip(table[j][b],projections[j*10:(j+1)*10]))/norm if norm>1e-12 else 0. for b in (0,1)] for j in range(32)]
    ref=v5._key_test(projections,table,center)
    distance=(int(ref['code'])^center).bit_count()
    radii={}
    for r in RADII:
        exact,code=ball(scores,center,r)
        lower=max(ref['recomputed'],ref['decoded'] if distance<=r else -math.inf)
        assert lower-1e-9<=exact<=ref['decoded']+1e-9
        t=bound_threshold(r)
        radii[str(r)]=dict(score=exact,code=f'{code:08x}',lower=lower,threshold=t,exact_accept=exact>=t,
                           lower_accept=lower>=t,unconstrained_upper=ref['decoded']>=t,
                           score_gain=exact-lower)
    return dict(norm=norm,recomputed=ref['recomputed'],decoded=ref['decoded'],decoded_code=f"{int(ref['code']):08x}",
                center=f'{center:08x}',distance=distance,radii=radii,segment_scores=scores)

def run_batch(method,start_index,count):
    start=time.monotonic()
    assert 1<=count<=12
    name=f'{method}-{start_index:04d}-{count:02d}'
    target=OUT/f'{name}.jsonl'
    if target.exists():raise FileExistsError(target)
    inv=json.loads((OUT/'inventory.json').read_text(encoding='utf-8'))
    def relevant(x):
        return method in x.get('methods', ('v5-r3','f5-r2') if x['arm']=='unmarked' else (x['arm'],))
    items=[x for x in inv['items'] if relevant(x)]
    batch=items[start_index:start_index+count]
    assert batch
    for var in ('HF_HUB_OFFLINE','TRANSFORMERS_OFFLINE','DIFFUSERS_OFFLINE','HF_HUB_DISABLE_TELEMETRY'):os.environ[var]='1'
    sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
    import numpy as np
    import torch
    from PIL import Image
    from scripts import revised_watermark_v5 as v5
    torch.set_num_threads(4);torch.set_num_interop_threads(1)
    assert not torch.cuda.is_available()
    profile=json.loads((ROOT/'experiments/c4-v5-two-tier-regeneration-v1/profile.json').read_text(encoding='utf-8'))
    assert v5.validate_profile(profile)==v5.validate_profile(inv['profile'])
    checked,key,config=v5._resolve(profile,None)
    f5=reader=None
    if method=='f5-r2':
        from scripts import f5_latent_codec as f5
        reader=f5.Reader(ASSETS,device='cpu')
    clip=transform=models=feature=None
    if any(x['panel']!='stage2' and x.get('exists') and not x.get('saved_features') for x in batch):
        import three_threat_models as models
        from a6_clip_visual import load_visual_encoder
        from f5_gate import semantic_feature as feature
        clip,transform=load_visual_encoder(ASSETS/'clip/ViT-B-32.pt',device='cpu')
    checked_cases=synthetic_check()
    completed=0;status='complete';failure=None
    with target.open('x',encoding='utf-8') as handle:
        for item in batch:
            if time.monotonic()-start>440:
                status='partial-time-budget';break
            tick=time.monotonic()
            row={k:item.get(k) for k in ('id','panel','source','split','donor','donor_split','cell','seed','arm','status','path')}
            row['method']=method
            if item['status']!='ok' or not item.get('exists'):
                row['result_status']='missing-image-or-terminal';handle.write(json.dumps(row)+'\n');handle.flush();completed+=1;continue
            try:
                p=Path(item['path']);sha=digest(p)
                if item.get('expected_sha256'):assert sha==item['expected_sha256'],str(p)
                rgb=np.asarray(Image.open(p).convert('RGB'),np.uint8)
                assert rgb.shape==(512,512,3),rgb.shape
                luma=v5.luminance_from_rgb(rgb.tolist())
                z=reader.latent(rgb) if reader else None
                features=item.get('saved_features')
                if features is None and item['panel']!='stage2':
                    features=feature(models,clip,transform,rgb,7 if method=='f5-r2' else 1)
                qnew=v5.semantic_code(features,profile=profile) if features is not None else None
                calls=[]
                for owner in ((API['ALPHA'],API['BETA']) if item['arm']!='unmarked' else (API['ALPHA'],)):
                    own=v5.canonical_owner(owner)
                    original=item['calls'].get(method,{}).get(owner)
                    if item['panel']=='stage2' and (not original or original.get('status')!='ok'):
                        calls.append(dict(owner=owner,status='missing-saved-call'));continue
                    raw=original['raw'] if original else None
                    q=int(raw['semantic_code'],16) if raw else int(qnew)
                    assert not raw or raw['detector_config_id']==config.hex()
                    robust=v5._Robust(v5._coarse(luma),luma,checked,v5._robust_carrier(key,config,own,len(checked['robust_frequencies'])))
                    proj=f5.Layout(checked,key,config,own).projections(z) if reader else robust.projections
                    result=decode(proj,v5._semantic_table(own,key,config),q,v5)
                    result.update(owner=owner,status='ok',role='C0' if item['arm']=='unmarked' else 'marked' if owner==API['ALPHA'] else 'wrong_owner')
                    if raw:
                        result['saved_score_difference']={k:result[k]-raw['semantic'][k+'_score'] for k in ('decoded','recomputed')}
                        result['replication_valid']=all(abs(d)<=(.05 if reader else .001) for d in result['saved_score_difference'].values())
                        result['frozen_endpoints']=original['endpoints'];result['raw']=raw
                    else:
                        # Reader calls only, with freshly recomputed permitted CPU CLIP features.
                        result['raw']=f5.detect_rgb(rgb,z,owner,profile,features,binding='soft') if reader else v5.detect(luma,owner,profile=profile,semantic_features=features)
                        result['replication_valid']=None
                    if owner==API['ALPHA']:
                        fragile=v5._Fragile(checked,key,config,own,512,512)
                        means,coeff=v5.base._analyse(luma,fragile.analysis)
                        instance_proj=fragile.projections(coeff)
                        positions=[c[fragile.skip:] for c in coeff]
                        result['response']=dict(robust_projection=proj,instance_projection=instance_proj,
                            pixel_robust_band_mean_square=float(np.mean(np.asarray(robust.coefficients)**2)),
                            second_positions_mean_square=np.mean(np.asarray(positions)**2,axis=0).tolist(),
                            second_positions=[list(x) for x in fragile.positions],
                            instance_projection_norm=float(np.linalg.norm(instance_proj)),
                            clean_payload=item['payloads'].get(method))
                        if z is not None:
                            layout=f5.Layout(checked,key,config,own)
                            coef=np.einsum('ij,cjk,lk->cil',layout.dct,z,layout.dct)
                            band=coef[layout.ch,layout.u,layout.v]
                            result['response']['latent_band_mean_square']=float(np.mean(band**2))
                    calls.append(result)
                row.update(result_status='ok',image_sha256=sha,calls=calls,seconds=time.monotonic()-tick)
            except Exception as exc:
                import traceback
                row.update(result_status='error',error=repr(exc),traceback=traceback.format_exc(),seconds=time.monotonic()-tick)
                status='failed';failure=repr(exc)
            handle.write(json.dumps(row)+'\n');handle.flush();completed+=1
            if failure:break
    meta=header(start)|dict(method=method,inventory_sha256=digest(OUT/'inventory.json'),selected=len(batch),completed=completed,
                           total_items=len(items),status=status,failure=failure,synthetic_checks=checked_cases,
                           output_sha256=digest(target),threads=4,workers=1)
    write(OUT/f'{name}-run.json',meta)
    print(json.dumps({k:meta[k] for k in ('method','selected','completed','total_items','status','failure','seconds')}))
    assert meta['seconds']<540, 'Run exceeded conservative budget'
    if failure:raise RuntimeError(failure)

def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1'
    p=argparse.ArgumentParser();p.add_argument('action',choices=('inventory','batch','self-test'))
    p.add_argument('--method',choices=('v5-r3','f5-r2'));p.add_argument('--start',type=int,default=0);p.add_argument('--count',type=int,default=1)
    a=p.parse_args()
    if a.action=='inventory':inventory()
    elif a.action=='self-test':print(json.dumps(dict(exhaustive_checks=synthetic_check())))
    else:run_batch(a.method,a.start,a.count)

if __name__=='__main__':main()
