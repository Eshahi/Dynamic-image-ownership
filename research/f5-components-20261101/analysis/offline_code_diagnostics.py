"""T0: saved semantic drift versus transport; deterministic public codebook audit."""
from __future__ import annotations
from collections import defaultdict, Counter
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import statistics as st
import subprocess
import sys
import time
sys.dont_write_bytecode=True
API=runpy.run_path(str(Path(__file__).with_name('offline_metadata_tests.py')))
ROOT,RD=API['ROOT'],API['RD']
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
from scripts import revised_watermark_v5 as v5

def main():
    start=time.monotonic()
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args()
    out=RD/'results'/a.out
    assert out.resolve().parent==(RD/'results').resolve() and not out.exists()
    calls,sources,split,data,inputs=API['get_calls']()
    truth={(r['arm'],r['source_id']):r['payload'] for _,r in data['stage2'].values() if r['status']=='ok' and r['channel']=='clean' and r['arm'] in API['API']['ARMS']}
    rows=[]
    for c in calls:
        if c['role']!='marked':continue
        z={k:c[k] for k in ('study','cell','arm','source','seed','split','location')}
        z.update(missing=not c['ok'],C=False,read=False,found=False,Q=False)
        if c['ok']:
            raw=c['raw'];s=raw['semantic'];q=int(truth[c['arm'],c['source']]['q'],16)
            z.update(C=c['ep']['C'],Q=c['ep']['Q'],read=s['read'],found=s['found'],
                     semantic_drift_bits=(int(raw['semantic_code'],16)^q).bit_count(),
                     transport_error_bits=(int(s['decoded_code'],16)^q).bit_count(),
                     decoded_to_suspect_bits=(int(s['decoded_code'],16)^int(raw['semantic_code'],16)).bit_count(),
                     soft_distance=s.get('soft_distance'))
        rows.append(z)
    groups=defaultdict(list)
    for r in rows:groups[tuple(r[k] for k in ('study','cell','arm','split'))].append(r)
    cells=[]
    for k,rr in sorted(groups.items()):
        ss=defaultdict(list)
        for r in rr:ss[r['source']].append(r)
        req=1 if rr[0]['seed'] is None else 2
        z=dict(zip(('study','cell','arm','split'),k))|{'expected_calls':len(rr),'missing':sum(r['missing'] for r in rr),'sources':len(ss)}
        for metric in ('C','Q','read','found'):z[metric+'_sources']=sum(sum(r[metric] for r in rs)>=req for rs in ss.values())
        z['binding_only_headroom']=z['read_sources']-z['C_sources']
        for metric in ('semantic_drift_bits','transport_error_bits','decoded_to_suspect_bits'):
            vals=[r[metric] for r in rr if not r['missing']]
            z[metric+'_median']=st.median(vals) if vals else None
            z[metric+'_mean']=st.mean(vals) if vals else None
        cells.append(z)
    decisions={}
    for arm in API['API']['ARMS']:
        rr=[r for r in cells if r['arm']==arm and r['split']=='EVALUATE' and r['cell'] in API['NATIVE'][3:]]
        gain=sum(r['binding_only_headroom'] for r in rr);loss=sum(r['sources']-r['C_sources'] for r in rr)
        decisions[arm]={'foreign_source_cell_headroom':gain,'foreign_source_cell_losses':loss,'ratio':gain/loss if loss else None,
                        'rule':'KILL_PRIMARY_BINDING_ONLY_ACCOUNT' if loss and gain/loss<.1 else 'RETAIN_RANKING_LEAD',
                        'qualification':'Overlapping Stage2 and PhaseA source-cells are descriptive, not independent trials.'}
    profile=json.loads((ROOT/'experiments/c4-v5-two-tier-regeneration-v1/profile.json').read_text(encoding='utf-8'))
    checked,key,config=v5._resolve(profile,None)
    codebook=[]
    for own in (API['API']['ALPHA'],API['API']['BETA']):
        table=v5._semantic_table(v5.canonical_owner(own),key,config)
        for j,(left,right) in enumerate(table):
            distance=sum(a!=b for a,b in zip(left,right))
            codebook.append({'owner':own,'segment':j,'distance':distance,'identical':distance==0,'guaranteed_correctable_chips':(distance-1)//2})
    out.mkdir()
    API['csvwrite'](out,'calls.csv',rows);API['csvwrite'](out,'cells.csv',cells);API['csvwrite'](out,'codebook.csv',codebook)
    summary={'decisions':decisions,'codebook_distance_histogram':dict(Counter(r['distance'] for r in codebook)),
             'one_chip_guarantee':'KILL' if min(r['distance'] for r in codebook)<3 else 'NOT_FALSIFIED_FOR_TWO_FIXED_OWNER_TABLES',
             'codebook_scope':'Public deterministic two-owner audit; no ECC transport experiment and no adaptive security guarantee.'}
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    meta={'command':[sys.executable,'-I',*sys.argv],'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
          'seconds':time.monotonic()-start,'inputs':inputs,'script_sha256':sha(Path(__file__)),'plan_sha256':sha(Path(__file__).with_name('WP4-TEST-PLAN.md')),
          'outputs':{p.name:sha(p) for p in out.iterdir()}}
    assert meta['seconds']<540
    (out/'provenance.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary))

if __name__=='__main__':main()
