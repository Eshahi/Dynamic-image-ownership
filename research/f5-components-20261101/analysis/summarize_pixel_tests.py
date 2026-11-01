"""Read-only reduction of committed-plan CPU reader batches; no models or images."""
from __future__ import annotations
from collections import defaultdict, Counter
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import runpy
import statistics as st
import subprocess
import sys
import time

sys.dont_write_bytecode = True
ROOT=Path(__file__).resolve().parents[3]
RD=ROOT/'research/f5-components-20261101'
PIX=RD/'results/wp4-pixels'
API=runpy.run_path(str(Path(__file__).with_name('offline_pixel_tests.py')))
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
from scripts import revised_watermark_v5 as v5

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def savecsv(out,name,rows):
    if not rows:return
    fields=list(dict.fromkeys(k for r in rows for k in r))
    with (out/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def mean(x):return st.mean(x) if x else None
def median(x):return st.median(x) if x else None
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def norm(a):return math.sqrt(dot(a,a))

def main():
    start=time.monotonic()
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args()
    out=RD/'results'/a.out
    assert out.resolve().parent==(RD/'results').resolve() and not out.exists()
    inv=json.loads((PIX/'inventory.json').read_text(encoding='utf-8'))
    rows={};failures=[];runmeta=[];inputhashes={}
    for f in sorted(PIX.glob('*.jsonl')):
        inputhashes[f.name]=sha(f)
        meta=json.loads(f.with_name(f.stem+'-run.json').read_text(encoding='utf-8'))
        assert meta['output_sha256']==sha(f)
        assert meta['seconds']<540
        runmeta.append(dict(file=f.name,**{k:meta[k] for k in ('commit','seconds','status','completed','selected','total_items')}))
        for line in f.read_text(encoding='utf-8').splitlines():
            r=json.loads(line);key=(r['method'],r['id'])
            if r['result_status']=='error':failures.append(dict(file=f.name,**r));continue
            if key in rows:
                # A repeated success is not extra evidence. Require numeric identity.
                old={k:v for k,v in rows[key].items() if k!='seconds'}
                new={k:v for k,v in r.items() if k!='seconds'}
                assert old==new,key
            rows[key]=r
    expected=[]
    for item in inv['items']:
        for method in item.get('methods',('v5-r3','f5-r2') if item['arm']=='unmarked' else (item['arm'],)):
            key=method,item['id'];r=rows.get(key)
            expected.append(dict(method=method,id=item['id'],panel=item['panel'],split=item['split'],
                                 status=r['result_status'] if r else 'unprocessed',exists=item.get('exists',False)))
    detail=[];responses=[];negatives=[]
    checked,key,config=v5._resolve(inv['profile'],None)
    owner=v5.canonical_owner(API['API']['ALPHA'])
    for r in rows.values():
        if r['result_status']!='ok':continue
        for c in r['calls']:
            if c['status']!='ok':continue
            raw=c['raw'];s,i=raw['semantic'],raw['instance']
            tu=API['API']['threshold'](4*2**32);tr=API['API']['threshold'](4)
            oldC=bool(s['read'] and s['content_match'])
            O=oldC or bool(i['found'] and i['content_match'])
            OU=(s['decoded_score']>=tu and bool(s['content_match'])) or (
                (i['decoded_score']>=tu or i['recomputed_score']>=tr) and bool(i['content_match']))
            base={k:r[k] for k in ('id','panel','source','split','donor','donor_split','cell','seed','arm','method')}
            base.update(role=c['role'],replication_valid=c['replication_valid'],C=oldC,O=O,O_U=OU)
            for radius,z in c['radii'].items():
                detail.append(base|{'radius':int(radius),**{k:z[k] for k in ('score','lower','threshold','exact_accept','lower_accept','score_gain')},
                                    'extra_accept':z['exact_accept'] and not z['lower_accept'],
                                    'new_vs_C':z['exact_accept'] and not oldC})
            if c['role']!='marked' or r['panel']=='T4':
                negatives.append(base|{'r3':c['radii']['3']['exact_accept'],'r3_extra_over_lower':c['radii']['3']['exact_accept'] and not c['radii']['3']['lower_accept']})
            if c['role'] in ('marked','C0') and r['panel']=='stage2':responses.append((r,c))
    groups=defaultdict(list)
    for r in detail:
        k=tuple(r[k] for k in ('method','panel','cell','role','split','radius'));groups[k].append(r)
    cells=[]
    for k,rr in sorted(groups.items()):
        ss=defaultdict(list)
        for r in rr:ss[r['source']].append(r)
        req=2 if k[1]=='stage2' and rr[0]['seed'] is not None else 1
        cells.append(dict(zip(('method','panel','cell','role','split','radius'),k))|{'observed_calls':len(rr),
            'observed_sources':len(ss),'required_calls_per_source':req,'unvalidated_calls':sum(r['replication_valid'] is False for r in rr),
            **{m+'_calls':sum(bool(r[m]) for r in rr) for m in ('C','O','O_U','exact_accept','lower_accept','extra_accept','new_vs_C')},
            **{m+'_sources':sum(sum(bool(r[m]) for r in rs)>=req for rs in ss.values()) for m in ('C','O','O_U','exact_accept','lower_accept')},
            'new_exact_sources':sum(sum(r['exact_accept'] for r in rs)>=req and sum(r['lower_accept'] for r in rs)<req for rs in ss.values())})
    # Wrong-content center diagnostic, same fixed owner and actual stored scores.
    oldclean={(r['method'],r['source'],r['arm']):r for r in rows.values() if r['panel']=='T5' and r['result_status']=='ok'}
    t5=[]
    for pair in inv['t5_pairs']:
        for left,right in ((pair['left'],pair['right']),(pair['right'],pair['left'])):
            for method in ('v5-r3','f5-r2'):
                marked=oldclean.get((method,left,method));reference=oldclean.get((method,right,'unmarked'))
                ls,rs=inv['old_split'][str(left)],inv['old_split'][str(right)]
                z=dict(method=method,source=left,reference=right,pair_split=ls if ls==rs else 'CROSS',
                       category=pair['semantic_label'])
                # Pair schema is retained verbatim so category mapping is auditable.
                z['pair_record']=json.dumps(pair,sort_keys=True)
                if not marked or not reference:z['status']='missing';t5.append(z);continue
                mc=next(c for c in marked['calls'] if c.get('role')=='marked')
                rc=next(c for c in reference['calls'] if c.get('role')=='C0')
                center=int(rc['center'],16);score,code=API['ball'](mc['segment_scores'],center,3)
                lower=API['ball'](mc['segment_scores'],center,0)[0]
                if (int(mc['decoded_code'],16)^center).bit_count()<=3:lower=max(lower,mc['decoded'])
                z.update(status='ok',center=f'{center:08x}',score=score,lower=lower,threshold=API['bound_threshold'](3),
                         accept=score>=API['bound_threshold'](3),extra=score>=API['bound_threshold'](3)>lower)
                t5.append(z)
    # Matched physical responses. The F5 h target is the clean decoded proxy.
    ri={(r['method'],r['cell'],r['source'],r['seed'],c['role']):(r,c) for r,c in responses}
    paired=[]
    for (method,cell,src,seed,role),(r,c) in sorted(ri.items(),key=lambda x:str(x[0])):
        if role!='marked':continue
        control=ri.get((method,cell,src,seed,'C0'))
        if not control:continue
        cr,cc=control;payload=c['response']['clean_payload']
        if not payload:continue
        ws,wi=v5.derive_keys(int(payload['q'],16),int(payload['h'],16),owner,key,config)
        z=dict(method=method,cell=cell,source=src,seed=seed,split=r['split'],h_target_basis=payload.get('h_target_basis','intended/exported'))
        for kind,pattern in (('robust',ws),('instance',wi)):
            x=c['response'][kind+'_projection'];n=cc['response'][kind+'_projection'];delta=[a-b for a,b in zip(x,n)]
            z.update({kind+'_marked_alignment':dot(x,pattern)/math.sqrt(len(pattern)),
                      kind+'_C0_alignment':dot(n,pattern)/math.sqrt(len(pattern)),
                      kind+'_delta_alignment':dot(delta,pattern)/math.sqrt(len(pattern)),
                      kind+'_marked_norm':norm(x),kind+'_C0_norm':norm(n),kind+'_delta_norm':norm(delta),
                      kind+'_delta_cosine':dot(delta,pattern)/(norm(delta)*math.sqrt(len(pattern))) if norm(delta)>0 else None})
        for metric in ('pixel_robust_band_mean_square','latent_band_mean_square'):
            if metric in c['response']:z[metric+'_marked']=c['response'][metric];z[metric+'_C0']=cc['response'][metric]
        for j,position in enumerate(c['response']['second_positions']):
            name='second_'+str(position[0])+str(position[1])
            z[name+'_marked']=c['response']['second_positions_mean_square'][j]
            z[name+'_C0']=cc['response']['second_positions_mean_square'][j]
        paired.append(z)
    clean={(r['method'],r['source']):r for r in paired if r['cell']=='clean'}
    for r in paired:
        baseline=clean.get((r['method'],r['source']))
        for tier in ('robust','instance'):
            d=baseline[tier+'_delta_alignment'] if baseline else None
            r[tier+'_alignment_retention']=r[tier+'_delta_alignment']/d if d is not None and abs(d)>1e-9 else None
    # Seeds averaged within source, then equal source median; no pseudoreplication.
    pg=defaultdict(list)
    for r in paired:pg[(r['method'],r['cell'],r['split'],r['source'])].append(r)
    source_response=[]
    for k,rr in sorted(pg.items()):
        metrics=[m for m in rr[0] if isinstance(rr[0][m],(int,float)) and m not in ('source','seed')]
        source_response.append(dict(zip(('method','cell','split','source'),k))|{'observed_pairs':len(rr),
            **{m:mean([r[m] for r in rr if r.get(m) is not None]) for m in metrics}})
    cg=defaultdict(list)
    for r in source_response:cg[(r['method'],r['cell'],r['split'])].append(r)
    response_cells=[]
    for k,rr in sorted(cg.items()):
        metrics=[m for m in rr[0] if isinstance(rr[0][m],(int,float)) and m not in ('source','observed_pairs')]
        response_cells.append(dict(zip(('method','cell','split'),k))|{'sources':len(rr),
             **{m+'_median':median([r[m] for r in rr if r.get(m) is not None]) for m in metrics}})
    order=[]
    for method in ('v5-r3','f5-r2'):
        for split in ('DESIGN','EVALUATE'):
            ix={r['cell']:r for r in response_cells if r['method']==method and r['split']==split}
            a,b=ix.get('R0-0.2'),ix.get('R1-0.2')
            valid=a is not None and b is not None and a['sources']==b['sources']==4
            yes=valid and a['robust_alignment_retention_median']>b['robust_alignment_retention_median'] and b['instance_alignment_retention_median']>a['instance_alignment_retention_median']
            order.append(dict(method=method,split=split,matched=valid,rule='ORDER_COMPATIBLE_CAUSE_UNIDENTIFIED' if yes else 'KILL_SIMPLE_RESPONSE_ORDER' if valid else 'MISSING'))
    out.mkdir()
    for name,rs in [('inventory-status.csv',expected),('T2-calls.csv',detail),('T2-cells.csv',cells),('negative-calls.csv',negatives),('T5-pairs.csv',t5),('T3-pairs.csv',paired),('T3-source-responses.csv',source_response),('T3-cell-responses.csv',response_cells),('batch-runs.csv',runmeta)]:savecsv(out,name,rs)
    (out/'failures.json').write_text(json.dumps(failures,indent=2)+'\n',encoding='utf-8')
    summary={'inventory':dict(Counter(r['status'] for r in expected)), 'error_attempts':len(failures),'T3_order':order,
             'T2_rule':'Read EVALUATE radius3 gains and all negative panels; reference-assisted T5 is separate from blind verification.',
             'T3_causality':'Family and working resolution are aliased. No causal scale fraction is identifiable.',
             'runtime':{'batches':len(runmeta),'total_seconds':sum(r['seconds'] for r in runmeta),'max_seconds':max((r['seconds'] for r in runmeta),default=0)}}
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    meta={'command':[sys.executable,'-I',*sys.argv],'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
          'seconds':time.monotonic()-start,'inputs':inputhashes,'inventory_sha256':sha(PIX/'inventory.json'),'script_sha256':sha(Path(__file__)),
          'plan_sha256':sha(Path(__file__).with_name('WP4-TEST-PLAN.md')),'outputs':{p.name:sha(p) for p in out.iterdir()}}
    assert meta['seconds']<540
    (out/'provenance.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary))

if __name__=='__main__':main()
