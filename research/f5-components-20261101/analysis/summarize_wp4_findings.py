"""Reporting reduction of fixed WP4 outcomes, not another tuned experiment."""
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3]
RD=ROOT/'research/f5-components-20261101'
MAIN=Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5')

def main():
    start=time.monotonic();ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);args=ap.parse_args()
    out=RD/'results'/args.out
    assert out.resolve().parent==(RD/'results').resolve() and not out.exists()
    src=RD/'results/wp4-pixel-summary';inputs={}
    def read(name):
        p=src/name;inputs[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
        with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
    calls=read('T2-calls.csv');cells=read('T2-cells.csv');negative=read('negative-calls.csv');t5=read('T5-pairs.csv');response=read('T3-cell-responses.csv')
    groups=defaultdict(Counter)
    for r in negative:
        k='|'.join(r[x] for x in ('method','panel','split','role'));groups[k]['calls']+=1
        for m in ('C','O','O_U','r3','r3_extra_over_lower'):groups[k][m]+=r[m]=='True'
    pairgroups=defaultdict(Counter)
    for r in t5:
        k='|'.join(r[x] for x in ('method','pair_split','category'));pairgroups[k]['pairs']+=1
        for m in ('accept','extra'):pairgroups[k][m]+=r.get(m)=='True'
        pairgroups[k]['missing']+=r['status']!='ok'
    gains=[]
    for method in ('f5-r2','v5-r3'):
        rr=[r for r in calls if r['method']==method and r['radius']=='3' and r['split']=='EVALUATE' and r['panel']=='stage2' and r['role']=='marked']
        cc=[r for r in cells if r['method']==method and r['radius']=='3' and r['split']=='EVALUATE' and r['panel']=='stage2' and r['role']=='marked']
        gains.append(dict(method=method,evaluation_marked_calls=len(rr),extra_calls=sum(r['extra_accept']=='True' for r in rr),
                          extra_source_cells=sum(int(r['new_exact_sources']) for r in cc),
                          rule='KILL_NO_EXTRA_EVALUATION_RECOVERY' if not any(r['extra_accept']=='True' for r in rr) else 'CHECK_NEGATIVES'))
    f5events=[r for r in negative if r['method']=='f5-r2' and r['panel']=='T4' and r['split']=='EVALUATE' and r['role']=='marked' and r['O_U']=='True' and r['C']=='False']
    old=MAIN/'.thesis-build/dev-runs/20261005-0700-f5r2-t4/run.json'
    inputs[str(old)]=hashlib.sha256(old.read_bytes()).hexdigest();historical=json.loads(old.read_text())
    eventdetails=[]
    for e in f5events:
        scale=float(e['cell'].split('-')[-1]);r=next(x for x in historical['rows'] if x['donor_id']==int(e['donor']) and x['recipient_id']==int(e['source']) and x['scale']==scale)
        eventdetails.append(e|{'saved_recipient_psnr_db':r['recipient_psnr_db'],'saved_recipient_ssim':r['recipient_ssim'],
                             'LPIPS':'MISSING in saved attack row','human_visibility':'MISSING','historical_combined':r['calls']['combined']})
    summary=dict(T2_evaluation_gains=gains,negative_counts=dict(groups),T5_reference_assisted_counts=dict(pairgroups),
                 replication_status=dict(Counter(r['replication_valid'] or 'NO_MATCHED_REFERENCE' for r in calls if r['radius']=='3')),
                 F5_union_negative_events=eventdetails,
                 F5_union_disposition='KILL_PROMOTION_NEW_EVALUATE_T4_ACCEPT' if eventdetails else 'NO_NEW_SAVED_T4_EVENT',
                 T3_evaluation=[r for r in response if r['split']=='EVALUATE'],
                 limitations=['Old T4 donors can cross halves; recipient defines report half; this is reused dependent development evidence.',
                              'T5 pairs change the content center using an external reference, not native blind verification.',
                              'No matched reference means historical score replication unavailable, not passed or failed.',
                              'T3 retention is matched C1-C0 alignment normalized to clean; nonlinear host interactions remain.'])
    out.mkdir();(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    meta=dict(command=[sys.executable,'-I',*sys.argv],commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
              seconds=time.monotonic()-start,script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),inputs=inputs,
              output_sha256=hashlib.sha256((out/'summary.json').read_bytes()).hexdigest())
    (out/'provenance.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'T2':gains,'F5_union':summary['F5_union_disposition'],'replication':summary['replication_status']}))

if __name__=='__main__':main()
