"""Fixed G2-A and G2-C reductions; never executes a pixel reader."""
from __future__ import annotations
import argparse
from collections import defaultdict, Counter
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gate2_reader as B
import offline_metadata_tests as M

RD = M.RD
PIX = RD/'results/wp4-pixels'
METRICS = ('C','J','Bs','Bi','B','C_or_B')

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p, obj): p.write_text(json.dumps(obj, indent=2)+'\n', encoding='utf-8')

def provenance(out, start, inputs):
    write(out/'provenance.json',dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        command=[sys.executable,*sys.argv],seconds=time.monotonic()-start,inputs=inputs,
        scripts={p.name:digest(p) for p in (Path(__file__),Path(B.__file__),Path(M.__file__))},
        plan_sha256=digest(RD/'analysis/GATE2-TEST-PLAN.md'),phase_b_journals='off',
        cuda_visible_devices=os.environ.get('CUDA_VISIBLE_DEVICES'),outputs={p.name:digest(p) for p in out.iterdir()}))
    assert time.monotonic()-start < 540

def pixel_rows():
    rows={}; hashes={}
    for p in sorted(PIX.glob('*.jsonl')):
        hashes[str(p)]=digest(p)
        for line in p.read_text(encoding='utf-8').splitlines():
            r=json.loads(line)
            key=(r['method'],r['id'])
            assert key not in rows
            rows[key]=r
    return rows, hashes

def run_a(out):
    start=time.monotonic()
    bound=B.validate_bound()
    calls,sources,split,data,inputs=M.get_calls()
    details=[]
    for x in calls:
        r={k:x[k] for k in ('study','cell','arm','source','seed','role','split','location','status')}
        r['missing']=not x['ok']
        r.update({m:False for m in METRICS})
        if x['ok']:r.update(B.endpoints(x['raw'],x['ep']))
        details.append(r)
    groups=defaultdict(list)
    for r in details:
        k=tuple(r[x] for x in ('study','cell','arm','role'))
        groups[k+(r['split'],)].append(r)
        groups[k+('ALL',)].append(r)
    cells=[]; sr=[]
    for key,rr in sorted(groups.items()):
        ss=defaultdict(list)
        for r in rr:ss[r['source']].append(r)
        n=len(next(iter(ss.values()))); req=1 if n==1 else 2
        assert n in (1,3) and all(len(v)==n for v in ss.values())
        z=dict(zip(('study','cell','arm','role','split'),key))
        z.update(sources=len(ss),expected_calls=len(rr),missing_calls=sum(r['missing'] for r in rr))
        for m in METRICS:
            z[m+'_calls']=sum(r[m] for r in rr)
            z[m+'_sources']=sum(sum(r[m] for r in v)>=req for v in ss.values())
            z[m+'_missing_upper']=sum(sum(r[m] or r['missing'] for r in v)>=req for v in ss.values())
        z['gains']=sum(sum(r['B'] for r in v)>=req and sum(r['C'] for r in v)<req for v in ss.values())
        z['losses']=sum(sum(r['B'] for r in v)<req and sum(r['C'] for r in v)>=req for v in ss.values())
        cells.append(z)
        if key[-1]!='ALL':
            for s,v in sorted(ss.items()):
                sr.append(dict(zip(('study','cell','arm','role','split'),key))|dict(source=s,required=req,
                    missing=sum(r['missing'] for r in v),**{m:sum(r[m] for r in v) for m in METRICS}))
    assert len({(r['study'],r['cell']) for r in cells})==22
    old,ih=pixel_rows(); inputs['pixel_batches']=ih
    inv=json.loads((PIX/'inventory.json').read_text(encoding='utf-8'))
    panel=[]; clean={}
    for r in old.values():
        if r['result_status']!='ok':continue
        if r['panel']=='T5' and not r['id'].endswith('-C2'):clean[r['method'],r['source'],r['arm']]=r
        if r['panel'] not in ('T4','T5'):continue
        for c in r['calls']:
            if not c.get('raw'):continue
            panel.append({k:r.get(k) for k in ('id','panel','method','source','split','donor','donor_split')}|
                         dict(role=c['role'],**B.endpoints(c['raw'],c.get('frozen_endpoints'))))
    t5=[]
    for pair in inv['t5_pairs']:
        for left,right in ((pair['left'],pair['right']),(pair['right'],pair['left'])):
            for method in M.API['ARMS']:
                ls,rs=inv['old_split'][str(left)],inv['old_split'][str(right)]
                z=dict(method=method,source=left,reference=right,pair_split=ls if ls==rs else 'CROSS',
                       category=pair['semantic_label'],pair_record=json.dumps(pair,sort_keys=True))
                mr=clean.get((method,left,method)); rr=clean.get((method,right,'unmarked'))
                if not mr or not rr:z['status']='missing';t5.append(z);continue
                raw=next(c['raw'] for c in mr['calls'] if c['role']=='marked')
                ref=next(c['raw'] for c in rr['calls'] if c['role']=='C0')
                a=B.tier(raw['semantic'],ref['semantic_code'])
                af=B.tier(raw['semantic'],ref['semantic_code'],B.FROZEN_STYLE_THRESHOLD)
                b=B.tier(raw['instance'],ref['perceptual_hash'])
                bf=B.tier(raw['instance'],ref['perceptual_hash'],B.FROZEN_STYLE_THRESHOLD)
                veto=raw['semantic']['decoded_score']>=B.FROZEN_STYLE_THRESHOLD and not af['passes']
                accept=a['passes'] or (b['passes'] and not veto)
                frozen=af['passes'] or (bf['passes'] and not veto)
                z.update(status='ok',q_center=ref['semantic_code'],h_center=ref['perceptual_hash'],
                    Bs=a['passes'],Bi=b['passes'],B=accept,frozen_s=af['passes'],frozen_i=bf['passes'],frozen_union=frozen,
                    veto=veto,semantic_extra=a['passes'] and not af['passes'],
                    contributing_instance_extra=b['passes'] and not veto and not bf['passes'],
                    extra=(a['passes'] and not af['passes']) or (b['passes'] and not veto and not bf['passes']),
                    s_distance=a['distance'],s_corrected=a['corrected'],i_distance=b['distance'],i_corrected=b['corrected'])
                t5.append(z)
    ev=[r for r in cells if r['arm']=='f5-r2' and r['split']=='EVALUATE' and r['role']=='marked']
    foreign=[r for r in ev if r['study']=='stage2-union' and r['cell'] in M.NATIVE[3:]]
    assert sum(r['sources'] for r in foreign)==120
    gain=sum(r['gains'] for r in foreign)
    lowloss=sum(r['losses'] for r in ev if r['cell'] in ('R0-0.1','R0-0.2'))
    neg=[r for r in details if r['role']!='marked' and r['B']]
    pixneg=[r for r in panel if r['role']!='marked' and r['B']]
    t4extra=[r for r in panel if r['method']=='f5-r2' and r['panel']=='T4' and r['split']=='EVALUATE' and r['role']=='marked' and r['B'] and not r['C']]
    categories=Counter(r['category'] for r in t5)
    # Labels are retained from the historical manifest, never inferred from outcomes.
    assert set(categories)<= {'same','different','uncertain'},categories
    t5extra=[r for r in t5 if r['status']=='ok' and r['pair_split']=='EVALUATE' and r['category']=='different' and r['extra']]
    kills=dict(fewer_than_5_F5_foreign_gains=gain<5,any_F5_SD15_low_C_loss=lowloss>0,
               any_saved_negative_accept=bool(neg or pixneg),any_new_F5_T4_EVALUATE=bool(t4extra),
               any_new_different_T5_EVALUATE=bool(t5extra))
    summary=dict(bound=bound,foreign_gains_over_C=gain,foreign_denominator=120,sd15_low_losses=lowloss,
                 negative_accepts=len(neg),pixel_negative_accepts=len(pixneg),new_F5_T4=len(t4extra),
                 new_T5=len(t5extra),T5_category_directions=dict(categories),kills=kills,
                 outcome='KILL' if any(kills.values()) else 'SURVIVES_G2_A_ONLY',
                 T5_scope='reference-assisted fixed-table scores; not operational blind transplantation')
    out.mkdir()
    for name,rows in [('calls.csv',details),('cells.csv',cells),('sources.csv',sr),('old-panels.csv',panel),('T5-directions.csv',t5)]:M.csvwrite(out,name,rows)
    write(out/'summary.json',summary)
    write(out/'counterexamples.json',dict(negative=neg,pixel_negative=pixneg,T4=t4extra,T5=t5extra))
    report=['# G2-A fixed decoded-word reader','','MEASURED: '+json.dumps(summary),'',
        'C/J are frozen. New B is exploratory and hard-distance based; C OR B is separate. Missing calls count as failures; missing upper bounds in cells.csv. Study/source-cell repetitions are not independent. The old T4 event is not fresh evidence for B.','',
        '|Study|Cell|Method|Half|C|J|Bs|Bi|B|C OR B|Missing|','|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|']
    for r in cells:
        if r['role']=='marked':report.append('| '+' | '.join(str(r[k]) for k in ('study','cell','arm','split','C_sources','J_sources','Bs_sources','Bi_sources','B_sources','C_or_B_sources','missing_calls'))+' |')
    report+=['','DERIVED: Conditional-q union bound <=alpha under domain-separated PRF randomness and honest image/null independence. No fixed-public-key adaptive security. C OR B <=2alpha. G2-B is independently required; no promotion follows from G2-A alone.']
    (out/'REPORT.md').write_text('\n'.join(report)+'\n',encoding='utf-8')
    provenance(out,start,inputs)
    print(json.dumps(summary))

def run_c(out):
    start=time.monotonic()
    data,inputs=M.API['load']('stage2')
    sources=sorted({r['source_id'] for _,r in data.values() if r['channel']=='clean'})
    assert len(sources)==60
    split={s:'DESIGN' if j%2==0 else 'EVALUATE' for j,s in enumerate(sources)}
    codes={}
    for _,r in data.values():
        if r['channel']=='clean' and r['arm']=='unmarked' and r['status']=='ok':
            c=r['detections']['f5-r2'][M.API['ALPHA']]
            assert c['status']=='ok'
            codes[r['source_id']]={k:c['raw'][k] for k in ('semantic_code','perceptual_hash')}
    assert set(codes)==set(sources)
    pairs=[]
    for a,b in itertools.combinations(sources,2):
        pairs.append(dict(left=a,right=b,split=split[a] if split[a]==split[b] else 'CROSS',
            q=B.distance(codes[a]['semantic_code'],codes[b]['semantic_code']),
            h=B.distance(codes[a]['perceptual_hash'],codes[b]['perceptual_hash'])))
    sums=[]
    for half in ('DESIGN','EVALUATE','CROSS','ALL'):
        rr=[r for r in pairs if half=='ALL' or r['split']==half]
        for key in ('q','h'):
            ds=[r[key] for r in rr]
            sums.append(dict(split=half,code=key,pairs=len(ds),mean=statistics.mean(ds),minimum=min(ds),
                **{f'le{r}':sum(d<=r for d in ds) for r in (6,8,9)}))
    uniform={str(r):sum(math.comb(32,j) for j in range(r+1))/2**32 for r in (6,8,9)}
    out.mkdir()
    M.csvwrite(out,'pairs.csv',pairs);M.csvwrite(out,'summary.csv',sums)
    write(out/'codes.json',codes);write(out/'summary.json',dict(rows=sums,uniform_share=uniform))
    (out/'REPORT.md').write_text('# G2-C code collision floor\n\nMEASURED: '+json.dumps(sums,indent=2)+'\n\nDERIVED uniform32-bit shares: '+json.dumps(uniform)+
        '\n\nJUDGMENT: No kill. Dependent pair counts describe this development cohort, not population entropy or an adaptive security bound. q collision concentration limits semantic transplant binding; h may discriminate better here, without guaranteeing reader or transplant safety.\n',encoding='utf-8')
    provenance(out,start,inputs);print(json.dumps(dict(rows=sums,uniform_share=uniform)))

if __name__=='__main__':
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1'
    p=argparse.ArgumentParser();p.add_argument('test',choices=('G2-A','G2-C'));a=p.parse_args()
    out=RD/'results'/a.test.lower()
    assert not out.exists()
    (run_a if a.test=='G2-A' else run_c)(out)
