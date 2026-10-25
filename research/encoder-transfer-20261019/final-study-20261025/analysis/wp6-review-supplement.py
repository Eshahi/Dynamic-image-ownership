"""Independent bounded supplementary audit: saved numeric scores only, stdlib."""
import collections
import json
import math
from pathlib import Path
import statistics

HERE = Path(__file__).resolve().parent
RAW = Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/20261025-0128-encoder-transfer-stage2b/results/stage2b-full/rows.jsonl')
latest = {}
with RAW.open(encoding='utf-8') as f:
    for line in f:
        if line.strip():
            r = json.loads(line)
            latest[r['id']] = r
def cell(r):
    return r['channel'] + ('' if r['strength'] is None else '@' + str(r['strength']))
index = {(r['arm'], cell(r), r['source_id'], r['seed']): r for r in latest.values()}
sources = sorted({r['source_id'] for r in latest.values()})
methods = ('f5-r2', 'v5-r3')
right, wrong = 'qim-pilot-owner-alpha', 'qim-pilot-owner-beta'
def call(arm, c, source, seed, method, owner=right):
    r = index.get((arm,c,source,seed), {})
    if r.get('status') != 'ok': return {}
    d = r.get('detections', {}).get(method, {}).get(owner, {})
    return d if d.get('status') == 'ok' else {}
def score(d, tier, branch, suffix='score'):
    x = d.get('raw', {}).get(tier, {}).get(branch + '_' + suffix)
    return x if type(x) in (int,float) and math.isfinite(x) else None
def seeds(c): return (12,13,14) if c.startswith('R') else (None,)
def quantile(x,p):
    a=sorted(x); t=(len(a)-1)*p; i=int(t)
    return a[i] + (a[min(i+1,len(a)-1)]-a[i])*(t-i)

paired=[]
for m in methods:
    for c in ('clean','R1@0.1','R1@0.2','R1@0.4','D1','D3','R3@0.2'):
        for tier in ('semantic','instance'):
            for kind in ('C1_minus_C0','right_minus_wrong_owner'):
                per=[]
                for source in sources:
                    diffs=[]
                    for seed in seeds(c):
                        a=score(call(m,c,source,seed,m),tier,'decoded')
                        b=score(call('unmarked',c,source,seed,m) if kind=='C1_minus_C0' else call(m,c,source,seed,m,wrong),tier,'decoded')
                        if a is not None and b is not None: diffs.append(a-b)
                    if len(diffs)==len(seeds(c)): per.append(statistics.median(diffs))
                paired.append(dict(method=m,cell=c,tier=tier,contrast=kind,n=len(per),median=statistics.median(per)))

maxima={}; violations=[]; vine=[]; vine_cell=[]
for r in latest.values():
    if r.get('status')!='ok': continue
    for m in methods:
        owners=(right,) if r['arm']=='unmarked' else (wrong,) if r['arm']==m else ()
        for owner in owners:
            d=call(r['arm'],cell(r),r['source_id'],r['seed'],m,owner)
            for tier in ('semantic','instance'):
                for branch in ('decoded','recomputed'):
                    s=score(d,tier,branch); t=score(d,tier,branch,'threshold')
                    if s is None or t is None: continue
                    k='|'.join((m,tier,branch))
                    maxima[k]=max(maxima.get(k,-math.inf),s-t)
                    if s>=t: violations.append([r['id'],owner,tier,branch,s,t])
    if r['arm'] not in ('unmarked','vine-r'): continue
    d=call(r['arm'],cell(r),r['source_id'],r['seed'],'vine-r')
    p=d.get('presence' if r['arm']=='unmarked' else 'wrong_message_presence',{})
    if not all(type(p.get(k)) in (int,float) for k in ('accuracy','threshold','bits')): continue
    acc=p['accuracy']; threshold=p['threshold']/p['bits']
    vine.append(dict(cell=cell(r),kind='C0' if r['arm']=='unmarked' else 'wrong_message',source=r['source_id'],seed=r['seed'],accuracy=acc,threshold=threshold,crossing=acc>=threshold))
    if r['arm']=='unmarked' and cell(r)=='R1@0.1': vine_cell.append((r['source_id'],acc))
vs=collections.defaultdict(list)
for s,acc in vine_cell: vs[s].append(acc)
source_max=[max(v) for v in vs.values() if len(v)==3]
result=dict(paired=paired,negative_maxima=maxima,internal_negative_crossings=violations,vine_total=len(vine),vine_events=[x for x in vine if x['crossing']],vine_R1_01=dict(n=len(vine_cell),median=statistics.median(a for s,a in vine_cell),p95=quantile([a for s,a in vine_cell],.95),max=max(a for s,a in vine_cell),source_count=len(source_max),source_max_median=statistics.median(source_max),source_max_p95=quantile(source_max,.95)))
published=json.loads((HERE/'negative-background-analysis.json').read_text())
errors=[]
for r in paired:
    pool=published['paired_C1_C0' if r['contrast']=='C1_minus_C0' else 'owner_specificity']
    p=next(x for x in pool if all(x[k]==r[k] for k in ('method','cell','tier','contrast')) and x['branch']=='decoded')
    if r['n']!=p['sources_complete'] or abs(r['median']-p['delta_source_median_complete']['median'])>1e-12: errors.append(r)
for key,v in maxima.items():
    m,t,b=key.split('|')
    p=max(x['margin']['max'] for x in published['internal'] if x['method']==m and x['tier']==t and x['branch']==b and x['kind']!='C1')
    if abs(v-p)>1e-12: errors.append([key,v,p])
if len(vine)!=sum(x['observed_scores'] for x in published['vine']): errors.append('VINE count')
result['comparison_errors']=errors
(HERE/'wp6-review-supplement.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='paired'},indent=2))
print(json.dumps([r for r in paired if r['tier']=='semantic' and r['contrast']=='C1_minus_C0'],indent=2))
