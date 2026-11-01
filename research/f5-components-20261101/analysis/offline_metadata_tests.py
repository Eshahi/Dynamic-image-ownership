"""Prospectively specified T1/T4 reductions of allowed development journals only."""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import runpy
import statistics as st
import subprocess
import sys
import time

sys.dont_write_bytecode = True
API = runpy.run_path(str(Path(__file__).with_name('account_saved_development.py')))
RD, ROOT = API['RD'], API['ROOT']
START = time.monotonic()
NATIVE = ('R0-0.1','R0-0.2','R0-0.4','R1-0.1','R1-0.2','R1-0.4','R3-0.2')

def threshold(alpha, patterns):
    lo, hi = 0., 64.
    for _ in range(200):
        mid = (lo+hi)/2
        if patterns*math.erfc(mid/math.sqrt(2))/(4*math.erfc(1)) > alpha: lo=mid
        else: hi=mid
    return hi

def get_calls():
    data, inputs = {}, {}
    for key in API['INPUTS']:
        data[key], inputs[key] = API['load'](key)
    sources = sorted({r['source_id'] for _,r in data['stage2'].values() if r['channel']=='clean'})
    assert len(sources)==60
    split = {s:('DESIGN' if i%2==0 else 'EVALUATE') for i,s in enumerate(sources)}
    calls = []
    def add(study,cell,arm,source,seed,role,line,row,call,status):
        ok = status=='ok' and call and call.get('status')=='ok'
        calls.append(dict(study=study,cell=cell,arm=arm,source=source,seed=seed,role=role,
                          split=split[source],location=line,status=status,ok=bool(ok),
                          raw=call['raw'] if ok else None,ep=call['endpoints'] if ok else None))
    index={}
    for line,r in data['stage2'].values():
        k=(r['channel'],r['strength'],r['arm'],r['source_id'],r['seed'])
        assert k not in index
        index[k]=(line,r)
    for chan,strength in sorted({(r['channel'],r['strength']) for _,r in data['stage2'].values()},key=str):
        cell=chan if strength is None else f'{chan}-{strength}'
        for arm in API['ARMS']:
            for source in sources:
                for seed in ((None,) if strength is None else API['SEEDS']):
                    for role in ('marked','C0','wrong_owner'):
                        line,r=index.get((chan,strength,'unmarked' if role=='C0' else arm,source,seed),(None,{}))
                        owner=API['BETA'] if role=='wrong_owner' else API['ALPHA']
                        call=r.get('detections',{}).get(arm,{}).get(owner)
                        add('stage2-union',cell,arm,source,seed,role,f'stage2:{line}',r,call,r.get('status','absent'))
    cells=sorted({r['cell'] for _,r in data['native'].values() if r['kind']=='native'})
    for cell in cells+['ctrlB-codec']:
        for arm in API['ARMS']:
            for source in sources:
                for seed in ((None,) if cell=='ctrlB-codec' else API['SEEDS']):
                    for role in ('marked','C0','wrong_owner'):
                        ia='unmarked' if role=='C0' else arm
                        item=f'ctrlB-codec:{source}:{ia}' if seed is None else f'native:{cell}:{source}:{seed}:{ia}'
                        line,r=data['detect'].get(f'det:{arm}:{item}',(None,{}))
                        owner=API['BETA'] if role=='wrong_owner' else API['ALPHA']
                        add('phase-a',cell,arm,source,seed,role,f'detect:{line}',r,r.get('calls',{}).get(owner),r.get('status','absent'))
    return calls,sources,split,data,inputs

def csvwrite(out,name,rows):
    if not rows:return
    fields=list(dict.fromkeys(k for row in rows for k in row))
    with (out/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def t1(out,calls,sources,split,data):
    ts=threshold(1e-6/4,1);td=threshold(1e-6/4,2**32)
    # Explicit q-selection envelope, while keeping the fixed h recomputation.
    tiq=threshold(1e-6/4,2**64)
    metrics=('C','J','sf','if','io','either','O','O_U','O_Q','C_U','s_dec','s_rec','s_both','i_dec','i_rec','i_both',
             'io_sem_absent','io_sem_absent_recomputed_only','io_sem_absent_decoded')
    detail=[]
    for x in calls:
        row={k:x[k] for k in ('study','cell','arm','source','seed','role','split','location','status')}
        row['missing']=not x['ok']
        row.update({k:False for k in metrics})
        if x['ok']:
            raw,ep=x['raw'],x['ep']; s,i=raw['semantic'],raw['instance']
            sd=s['decoded_score']>=s['decoded_threshold'];sr=s['recomputed_score']>=s['recomputed_threshold']
            idc=i['decoded_score']>=i['decoded_threshold'];ir=i['recomputed_score']>=i['recomputed_threshold']
            assert bool(s['found'])==(sd or sr) and bool(i['found'])==(idc or ir)
            assert bool(ep['C'])==(sd and bool(s['content_match']))
            io=bool(i['found'] and i['content_match'])
            su=s['decoded_score']>=td and bool(s['content_match'])
            iu=(i['decoded_score']>=td or i['recomputed_score']>=ts) and bool(i['content_match'])
            iq=(i['decoded_score']>=tiq or i['recomputed_score']>=td) and bool(i['content_match'])
            # Comparator with one total alpha spread over the semantic pair.
            cu=s['decoded_score']>=threshold(1e-6/2,2**32) and bool(s['content_match'])
            row.update(C=bool(ep['C']),J=bool(ep['J']),sf=bool(s['found']),**{'if':bool(i['found'])},io=io,
                       either=bool(s['found'] or i['found']),O=bool(ep['C'] or io),O_U=bool(su or iu),O_Q=bool(su or iq),C_U=cu,
                       s_dec=sd,s_rec=sr,s_both=sd and sr,i_dec=idc,i_rec=ir,i_both=idc and ir,
                       io_sem_absent=io and not s['found'],io_sem_absent_recomputed_only=io and not s['found'] and ir and not idc,
                       io_sem_absent_decoded=io and not s['found'] and idc,
                       semantic_status=s.get('content_status'),instance_status=i.get('content_status'),
                       semantic_route=s.get('candidate'),instance_route=i.get('candidate'),
                       instance_q=raw.get('instance_tested_with_semantic_code'),recomputed_q=raw.get('semantic_code'))
        detail.append(row)
    groups=defaultdict(list)
    for r in detail:
        k=tuple(r[k] for k in ('study','cell','arm','role'))
        groups[k+(r['split'],)].append(r);groups[k+('ALL',)].append(r)
    summary=[]
    source_rows=[]
    for key,rows in sorted(groups.items()):
        bysrc=defaultdict(list)
        for r in rows:bysrc[r['source']].append(r)
        nseed=len(next(iter(bysrc.values())));req=1 if nseed==1 else 2
        assert all(len(v)==nseed for v in bysrc.values())
        z=dict(zip(('study','cell','arm','role','split'),key))
        z.update(sources=len(bysrc),expected_calls=len(rows),missing_calls=sum(r['missing'] for r in rows))
        for metric in metrics:
            z[metric+'_calls']=sum(r[metric] for r in rows)
            z[metric+'_sources']=sum(sum(r[metric] for r in rr)>=req for rr in bysrc.values())
        for metric in ('C','J','O','O_U','O_Q'):
            z[metric+'_missing_upper']=sum(sum(r[metric] or r['missing'] for r in rr)>=req for rr in bysrc.values())
        z['O_U_gain_over_C_sources']=sum(sum(r['O_U'] for r in rr)>=req and sum(r['C'] for r in rr)<req for rr in bysrc.values())
        z['O_U_loss_from_C_sources']=sum(sum(r['O_U'] for r in rr)<req and sum(r['C'] for r in rr)>=req for rr in bysrc.values())
        summary.append(z)
        if key[-1]!='ALL':
            for source,rr in sorted(bysrc.items()):
                source_rows.append(dict(zip(('study','cell','arm','role','split'),key))|{'source':source,'required':req,
                    'missing_calls':sum(r['missing'] for r in rr),**{m:sum(r[m] for r in rr) for m in metrics}})
    # Reproduce independent judge numbers, not just our prior reduction.
    expected=json.loads((RD/'judge/two-tiers.json').read_text(encoding='utf-8'))
    checks=[]
    for z in summary:
        name=f"{z['arm']}|{z['cell']}"
        if z['study']=='stage2-union' and z['role']=='marked' and z['split']=='ALL' and name in expected:
            for a,b in [('sf','sf'),('if','if'),('io','io'),('either','any'),('C','C'),('O','CI')]:
                assert z[a+'_sources']==expected[name][b],(name,a,z[a+'_sources'],expected[name][b])
            checks.append(name)
    assert len(checks)==14
    decisions={}
    for arm in API['ARMS']:
        ev=[r for r in summary if r['split']=='EVALUATE' and r['arm']==arm]
        foreign=[r for r in ev if r['role']=='marked' and r['cell'] in NATIVE[3:]]
        gain=sum(r['O_U_gain_over_C_sources'] for r in foreign)
        lost=sum(r['O_U_loss_from_C_sources'] for r in ev if r['role']=='marked' and r['cell'] in ('R0-0.1','R0-0.2'))
        newneg=sum(r['O_U_calls'] for r in ev if r['role']!='marked')
        decisions[arm]={'foreign_source_cell_gains_not_unique_sources':gain,'sd15_low_strength_source_cell_losses':lost,
                        'negative_calls':newneg,'necessary_lead_rule':'RETAIN_LEAD_T4_T5_UNKNOWN' if gain>0 and lost==0 and newneg==0 else 'KILL',
                        'note':'Stage2/PhaseA overlap; aggregate source-cell counts are not independent evidence.'}
    csvwrite(out,'calls.csv',detail);csvwrite(out,'cells.csv',summary);csvwrite(out,'sources.csv',source_rows)
    payload={'nominal_alpha':1e-6,'old_tier_union_upper':2e-6,'old_either_found_union_upper':4e-6,
             'old_O_three_route_union_upper_conditional_q':3e-6,'O_U_three_route_union_upper_conditional_q':.75e-6,
             'four_route_thresholds':{'recomputed':ts,'decoded':td},'instance_q_enumerated_decoded_threshold':tiq,
             'qualification':'Conditional random-sign model; public fixed-key adaptive forgery is not controlled. Q envelope covers q selection, not arbitrary image adaptation.',
             'judge_cells_reproduced':checks,'decisions':decisions}
    (out/'summary.json').write_text(json.dumps(payload,indent=2)+'\n',encoding='utf-8')
    md=['# T1 two-tier endpoint reduction','','MEASURED: Every declared source/seed is retained, including missing calls. EVALUATE is odd sorted-source positions. Frozen C/J and new O/O_U/O_Q are separate. See calls.csv for routes and sources.csv for paired outcomes.','',
        'DERIVED: Either-found uses four routes (union <=4e-6); O uses decoded semantic plus two instance routes (<=3e-6 conditional on valid q selection). O_U allocates alpha/4 to each of its three routes (<=.75e-6, one share unused); O_Q additionally enumerates instance q selections. These are conditional random-sign bounds, not adaptive fixed-public-key security. Frozen content status/q routing is retained.','',
        '| Study | Cell | Arm | Split | C | J | O | O_U | O_Q | second content-ok with semantic absent |',
        '|---|---|---|---|---|---|---|---|---|---|']
    for z in summary:
        if z['role']=='marked':md.append('| '+' | '.join(str(z[k]) for k in ('study','cell','arm','split','C_sources','J_sources','O_sources','O_U_sources','O_Q_sources','io_sem_absent_sources'))+' |')
    md+=['','JUDGMENT: Necessary lead-rule outcomes: '+json.dumps(decisions)+'. No T4/T5 safety conclusion follows.']
    (out/'REPORT.md').write_text('\n'.join(md)+'\n',encoding='utf-8')

def ranks(values):
    order=sorted(range(len(values)),key=values.__getitem__);result=[0.]*len(values);i=0
    while i<len(order):
        j=i+1
        while j<len(order) and values[order[j]]==values[order[i]]:j+=1
        for k in range(i,j):result[order[k]]=(i+j-1)/2+1
        i=j
    return result

def rho(x,y):
    if len(x)<3 or len(set(x))<2 or len(set(y))<2:return None
    x,y=ranks(x),ranks(y);mx,my=st.mean(x),st.mean(y)
    return sum((a-mx)*(b-my) for a,b in zip(x,y))/math.sqrt(sum((a-mx)**2 for a in x)*sum((b-my)**2 for b in y))

def t4(out,calls,sources,split,data):
    metadata={r['source_id']:r['embedding_report'] for _,r in data['stage2'].values() if r['arm']=='f5-r2' and r['channel']=='clean' and r['status']=='ok'}
    assert set(metadata)==set(sources)
    cutoff=st.median(metadata[s]['margin_median'] for s in sources if split[s]=='DESIGN')
    groups=defaultdict(list)
    for r in calls:
        if r['arm']=='f5-r2' and r['role']=='marked':groups[(r['study'],r['cell'],r['source'])].append(r)
    rows=[]
    for (study,cell,source),rr in sorted(groups.items()):
        good=[r for r in rr if r['ok']];req=1 if len(rr)==1 else 2
        m=metadata[source]
        row={'study':study,'cell':cell,'source':source,'split':split[source],'n':len(good),'expected':len(rr),
             **{k:m[k] for k in ('margin_median','margin_min','negative_chips','rgb_psnr_db')},'high_margin':m['margin_median']>=cutoff,
             'decoded_mean':st.mean(r['raw']['semantic']['decoded_score'] for r in good) if good else None,
             'C':sum(bool(r['ep']['C']) for r in good)>=req,'J':sum(bool(r['ep']['J']) for r in good)>=req,
             'found':sum(bool(r['raw']['semantic']['found']) for r in good)>=req,
             'read':sum(bool(r['raw']['semantic']['read']) for r in good)>=req}
        rows.append(row)
    primary=[]
    for s in sources:
        rr=[r for r in rows if r['study']=='stage2-union' and r['source']==s and r['cell'] in ('R1-0.1','R1-0.2','R1-0.4','R3-0.2')]
        # Equal weighting of cells with observed scores; incomplete coverage explicit.
        present=[r for r in rr if r['decoded_mean'] is not None]
        primary.append({'source':s,'split':split[s],'margin_median':metadata[s]['margin_median'],'high_margin':metadata[s]['margin_median']>=cutoff,
                        'foreign_cells':len(present),'foreign_calls':sum(r['n'] for r in rr),
                        'foreign_decoded_mean':st.mean(r['decoded_mean'] for r in present) if present else None})
    assoc=[]
    cells=defaultdict(list)
    for r in rows:
        if r['decoded_mean'] is not None:cells[(r['study'],r['cell'],r['split'])].append(r)
    for key,rr in sorted(cells.items()):
        hi=[r for r in rr if r['high_margin']];lo=[r for r in rr if not r['high_margin']]
        z=dict(zip(('study','cell','split'),key))|{'n':len(rr),'high_n':len(hi),'low_n':len(lo)}
        for pred in ('margin_median','margin_min','negative_chips','rgb_psnr_db'):
            z[pred+'_rho_decoded']=rho([r[pred] for r in rr],[r['decoded_mean'] for r in rr])
        for metric in ('decoded_mean','C','J','found','read'):
            z['high_minus_low_'+metric]=st.mean(r[metric] for r in hi)-st.mean(r[metric] for r in lo) if hi and lo else None
        assoc.append(z)
    result={}
    for subset in ('DESIGN','EVALUATE'):
        rr=[r for r in primary if r['split']==subset and r['foreign_decoded_mean'] is not None]
        hi=[r['foreign_decoded_mean'] for r in rr if r['high_margin']];lo=[r['foreign_decoded_mean'] for r in rr if not r['high_margin']]
        r=rho([x['margin_median'] for x in rr],[x['foreign_decoded_mean'] for x in rr]);gap=st.mean(hi)-st.mean(lo) if hi and lo else None
        result[subset]={'n':len(rr),'rho':r,'high_n':len(hi),'low_n':len(lo),'high_minus_low':gap,
                        'rule':'PREDICTIVE_LEAD_CAUSE_UNKNOWN' if r is not None and r>=.30 and gap is not None and gap>0 else 'KILL_SIMPLE_PREDICTIVE_ACCOUNT'}
    csvwrite(out,'source-cells.csv',rows);csvwrite(out,'associations.csv',assoc);csvwrite(out,'primary.csv',primary)
    summary={'design_median_cutoff':cutoff,'primary':result,'causal_status':'UNKNOWN: final-only reports lack per-stage residuals/margins and robust-only matched-total-quality counterfactual.'}
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    (out/'REPORT.md').write_text('# T4 final-margin association\n\nMEASURED: '+json.dumps(summary,indent=2)+'\n\nJUDGMENT: No causal attribution follows. Missing cells/calls and constant binary outcomes are retained. Q-STAGE is required to separate optimizer, clipping, rounding and second-write interference.\n',encoding='utf-8')

def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == '-1'
    p=argparse.ArgumentParser();p.add_argument('test',choices=('T1','T4'));p.add_argument('--out',required=True);a=p.parse_args()
    out=RD/'results'/a.out
    assert out.resolve().parent==(RD/'results').resolve()
    if out.exists():raise FileExistsError(out)
    calls,sources,split,data,inputs=get_calls();out.mkdir()
    (t1 if a.test=='T1' else t4)(out,calls,sources,split,data)
    seconds=time.monotonic()-START
    assert seconds<540
    meta={'test':a.test,'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
          'command':[sys.executable,'-I',str(Path(__file__).resolve()),*sys.argv[1:]],'inputs':inputs,
          'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'plan_sha256':hashlib.sha256(Path(__file__).with_name('WP4-TEST-PLAN.md').read_bytes()).hexdigest(),
          'phase_b_journals':'off','seconds':seconds,'split':{k:[s for s in sources if split[s]==k] for k in ('DESIGN','EVALUATE')},
          'outputs_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir())}}
    (out/'provenance.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'test':a.test,'seconds':seconds,'output':str(out)}))

if __name__=='__main__':main()
