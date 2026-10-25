"""Post-hoc source-cluster analysis of saved JSONL, stdlib only.

No image, model, detector, metric or experiment execution. Hypotheses commit
5cc20912a7120544e5ec4ece3d4a04bc5b4c9921 predates journal inspection.
"""
import collections
import csv
import hashlib
import json
import math
import random
import statistics as st
from pathlib import Path

MAIN = Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5')
INPUT = MAIN / '.thesis-build/dev-runs/20261025-0128-encoder-transfer-stage2b/results/stage2b-full/rows.jsonl'
OUT = Path(__file__).resolve().parent
FIG = OUT.parent / 'figures'
FIG.mkdir(exist_ok=True)
RIGHT = 'qim-pilot-owner-alpha'
WRONG = 'qim-pilot-owner-beta'
INTERNAL = ('f5-r2', 'v5-r3')
ARMS = INTERNAL + ('wam', 'vine-r', 'trustmark-q', 'pixelseal')
CELL_ORDER = ['clean','R0@0.1','R0@0.2','R0@0.4','R1@0.1','R1@0.2','R1@0.4',
              'R1-rinse@0.1','R1-smooth@0.2','R1-mode@0.2','R3@0.2','D1','D3','X1','X2']

def finite(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)

def quantile(a, p):
    if not a:
        return None
    a = sorted(a)
    x = (len(a)-1)*p
    lo, hi = math.floor(x), math.ceil(x)
    return a[lo]*(hi-x)+a[hi]*(x-lo) if lo != hi else a[lo]

def summary(a):
    a = [float(x) for x in a if finite(x)]
    return {'n': len(a), 'mean': st.mean(a) if a else None,
            'median': st.median(a) if a else None,
            'sd': st.stdev(a) if len(a)>1 else None,
            'min': min(a) if a else None, 'q25':quantile(a,.25),
            'q75':quantile(a,.75), 'max':max(a) if a else None}

def cell(r):
    return r['channel'] + (('@'+str(r['strength'])) if r['strength'] is not None else '')

def expected_seeds(c):
    return [112,113,114] if c.startswith('R1-rinse') else ([12,13,14] if c.startswith('R') else [None])

def detection(r, method, owner=RIGHT):
    if not r or r.get('status') != 'ok':
        return None
    d = r.get('detections',{}).get(method,{}).get(owner)
    return d if isinstance(d,dict) and d.get('status') == 'ok' else None

def state(r, method, tier='semantic'):
    d = detection(r,method)
    if d is None:
        return 'missing_call'
    q = d.get('raw',{}).get(tier)
    if not isinstance(q,dict) or not all(k in q for k in ('read','content_match','found')):
        return 'raw_unavailable'
    if q['read'] and q['content_match']:
        return 'C_success' if tier=='semantic' else 'read_content_match'
    if q['read']:
        return 'read_content_mismatch'
    if q['found']:
        return 'found_not_read'
    return 'not_found'

def pearson(x, y):
    if len(x)<3:
        return None
    mx,my=st.mean(x),st.mean(y)
    xx=sum((v-mx)**2 for v in x); yy=sum((v-my)**2 for v in y)
    return sum((a-mx)*(b-my) for a,b in zip(x,y))/math.sqrt(xx*yy) if xx*yy>0 else None

def ranks(x):
    out=[0.0]*len(x); order=sorted(range(len(x)),key=lambda i:x[i]); i=0
    while i<len(order):
        j=i+1
        while j<len(order) and x[order[j]]==x[order[i]]:
            j+=1
        for k in range(i,j): out[order[k]]=(i+j-1)/2+1
        i=j
    return out

def correlation(pairs):
    pairs=[(x,y) for x,y in pairs if finite(x) and finite(y)]
    x=[a for a,b in pairs]; y=[b for a,b in pairs]
    return {'n':len(pairs),'pearson':pearson(x,y),'spearman':pearson(ranks(x),ranks(y))}

def bootstrap_mean(a, seed=20261025, draws=1000):
    if len(a)<5: return None
    rng=random.Random(seed)
    vals=[st.mean(rng.choices(a,k=len(a))) for _ in range(draws)]
    return {'mean':st.mean(a),'low':quantile(vals,.025),'high':quantile(vals,.975),'n':len(a),'draws':draws}

rows={}; history=collections.Counter(); sha=hashlib.sha256(); transitions=collections.Counter(); count=0
with INPUT.open('rb') as f:
    for line in f:
        sha.update(line)
        if not line.strip(): continue
        r=json.loads(line); count+=1; history[str(r.get('status'))]+=1
        if r['id'] in rows: transitions[(str(rows[r['id']].get('status')),str(r.get('status')))]+=1
        rows[r['id']]=r
sources=sorted({r['source_id'] for r in rows.values()})
index={(r['arm'],cell(r),r['source_id'],r['seed']):r for r in rows.values()}
observed=sorted({(r['arm'],cell(r)) for r in rows.values() if r['arm']!='unmarked'},
                key=lambda ac:(ARMS.index(ac[0]),CELL_ORDER.index(ac[1])))
calls=[]; source_rows=[]; cell_summaries=[]; call_states=[]; transition_tables=[]

for arm,c in observed:
    group=[]; call_counts=collections.Counter(); seed_counts=collections.Counter()
    for sid in sources:
        seedset=expected_seeds(c); sr={'arm':arm,'cell':c,'source_id':sid,'expected':len(seedset)}
        values=collections.defaultdict(list); flags=collections.Counter(); local_states=[]
        for seed in seedset:
            r=index.get((arm,c,sid,seed)); d=detection(r,arm)
            out={'arm':arm,'cell':c,'source_id':sid,'seed':seed,'row_status':r.get('status') if r else 'missing',
                 'call_ok':d is not None,'carrier_state':state(r,arm) if arm in INTERNAL else None}
            if d is not None:
                flags['call_ok']+=1
                flags['positive']+=int(d.get('endpoints',{}).get('C',False) if arm in INTERNAL else d.get('presence',{}).get('present',False))
                out['positive']=bool(d.get('endpoints',{}).get('C',False) if arm in INTERNAL else d.get('presence',{}).get('present',False))
                if arm in INTERNAL:
                    for ep in ('S','C','Q','J','H','D','F','A'):
                        flags[ep]+=int(d.get('endpoints',{}).get(ep,False));out[ep]=bool(d.get('endpoints',{}).get(ep,False))
                    for tier in ('semantic','instance'):
                        q=d.get('raw',{}).get(tier,{})
                        for flag in ('found','read','content_match'):
                            flags[tier+'_'+flag]+=int(q.get(flag,False));out[tier+'_'+flag]=bool(q.get(flag,False))
                        flags[tier+'_read_without_found']+=int(q.get('read',False) and not q.get('found',False))
                        for branch in ('selected','recomputed','decoded'):
                            sk='score' if branch=='selected' else branch+'_score'
                            tk='threshold' if branch=='selected' else branch+'_threshold'
                            score,thr=q.get(sk),q.get(tk);prefix=tier+'_'+branch
                            for name,val in ((prefix+'_score',score),(prefix+'_threshold',thr)):
                                if finite(val):values[name].append(val);out[name]=val
                            if finite(score) and finite(thr):
                                margin=score-thr
                                values[prefix+'_margin'].append(margin);out[prefix+'_margin']=margin
                                norm=margin/max(abs(thr),1e-12)
                                values[prefix+'_normalized'].append(norm);out[prefix+'_normalized']=norm
                        for name in ('code_distance','corrected_distance','decoding_error_rate','soft_distance'):
                            val=q.get(name)
                            if finite(val): values[tier+'_'+name].append(val);out[tier+'_'+name]=val
                else:
                    presence=d.get('presence',{});acc=presence.get('accuracy');bits=presence.get('bits');thr=presence.get('threshold')
                    if finite(acc): values['bit_accuracy'].append(acc);out['bit_accuracy']=acc
                    if finite(acc) and finite(bits) and finite(thr) and bits>0:
                        values['bit_margin'].append(acc-thr/bits);out['bit_margin']=acc-thr/bits
                    out['native_present']=d.get('native',{}).get('present')
                    flags['native_present']+=int(bool(out['native_present']))
            else: out['positive']=False
            for scope,key in (('attack','distortion'),('total','total_distortion'),('incremental','incremental_distortion')):
                q=(r or {}).get(key,{})
                for metric in ('lpips','psnr_db','ssim_rgb'):
                    val=q.get(metric);name=scope+'_'+metric
                    if finite(val):values[name].append(val);out[name]=val
            if arm in INTERNAL:
                s=state(r,arm);local_states.append(s);call_counts[s]+=1
                clean=index.get((arm,'clean',sid,None));transition_tables.append({'arm':arm,'cell':c,'source_id':sid,'seed':seed,'from':state(clean,arm),'to':s})
            calls.append(out)
            seed_counts[(str(seed),'attempts')]+=1;seed_counts[(str(seed),'positive')]+=int(out['positive'])
        for name,n in flags.items():sr[name+'_calls']=n
        sr['complete_calls']=flags['call_ok']==len(seedset)
        required=2 if len(seedset)==3 else 1
        sr['positive_majority']=flags['positive']>=required
        for ep in ('S','C','Q','J','H','D','F','A','semantic_found','semantic_read','semantic_content_match','instance_found','instance_read','instance_content_match','native_present'):
            sr[ep+'_majority']=flags[ep]>=required
        for name,v in values.items():
            sr[name+'_coverage']=len(v)
            sr[name+'_available_median']=st.median(v)
            sr[name+'_median']=st.median(v) if len(v)==len(seedset) else None
            sr[name+'_seed_range']=max(v)-min(v) if len(v)==len(seedset) else None
        if local_states:
            counts=collections.Counter(local_states)
            sr['carrier_majority_state']=next((k for k,v in counts.items() if v>=required),'mixed')
        group.append(sr);source_rows.append(sr)
    fields=sorted({k for sr in group for k in sr if k.endswith('_median') and not k.endswith('_available_median')})
    cs={'arm':arm,'cell':c,'n_sources':len(group),'positive_majority':sum(r['positive_majority'] for r in group),
        'complete_sources':sum(r['complete_calls'] for r in group),
        'call_states':dict(call_counts), 'source_states':dict(collections.Counter(r.get('carrier_majority_state') for r in group)),
        'seed_counts':{k:{v:n for (s,v),n in seed_counts.items() if s==k} for k in sorted({s for s,v in seed_counts})},
        'continuous':{k:summary([r.get(k) for r in group]) for k in fields},
        'seed_range':{k:summary([r.get(k) for r in group]) for k in sorted({q for sr in group for q in sr if q.endswith('_seed_range')})}}
    for ep in ('S','C','Q','J','H','D','F','A','semantic_found','semantic_read','instance_found','instance_read'):
        cs[ep+'_majority']=sum(r[ep+'_majority'] for r in group)
    cs['read_without_found_calls']=sum(r.get('semantic_read_without_found_calls',0)+r.get('instance_read_without_found_calls',0) for r in group)
    cell_summaries.append(cs)

# Every C0/wrong-owner scheduled call is counted; missing calls do not become negatives.
negatives=[]
for arm,c in observed:
    for kind in ('C0','wrong_owner'):
        events=[];complete=[];positive_calls=0;missing_calls=0;total_calls=0;event_ids=[]
        for sid in sources:
            sf=[];valid=[]
            for seed in expected_seeds(c):
                r=index.get(('unmarked' if kind=='C0' else arm,c,sid,seed))
                d=detection(r,arm,RIGHT if kind=='C0' or arm not in INTERNAL else WRONG)
                total_calls+=1
                if d is None:missing_calls+=1;valid.append(False);continue
                if arm in INTERNAL: event=bool(d.get('endpoints',{}).get('A',False))
                else:
                    p=d.get('presence' if kind=='C0' else 'wrong_message_presence')
                    if not isinstance(p,dict):missing_calls+=1;valid.append(False);continue
                    event=bool(p.get('present',False))
                valid.append(True);sf.append(event);positive_calls+=int(event)
                if event:event_ids.append(r['id'])
            events.append(any(sf));complete.append(all(valid) and len(valid)==len(expected_seeds(c)))
        k=sum(events);n=len(sources)
        negatives.append({'arm':arm,'cell':c,'kind':kind,'source_events':k,'sources':n,'complete_sources':sum(complete),
                          'calls':total_calls,'positive_calls':positive_calls,'missing_calls':missing_calls,
                          'zero_event_gate':'pass' if k==0 and all(complete) else ('fail' if k else 'unresolved'),
                          'one_sided_95_upper_if_zero':1-.05**(1/n) if k==0 and all(complete) else None,
                          'event_ids':event_ids})

sr_index={(r['arm'],r['cell'],r['source_id']):r for r in source_rows}
correlations=[]
for arm in INTERNAL:
    cells=[c for a,c in observed if a==arm]
    for tier in ('semantic','instance'):
        field=tier+'_decoded_normalized_median'
        for i,c1 in enumerate(cells):
            for c2 in cells[i+1:]:
                pairs=[(sr_index[(arm,c1,s)].get(field),sr_index[(arm,c2,s)].get(field)) for s in sources]
                correlations.append({'arm':arm,'kind':'cross_cell','tier':tier,'left':c1,'right':c2,**correlation(pairs)})
        for c in cells+['pooled_R0_R1']:
            selected=[r for r in source_rows if r['arm']==arm and (r['cell']==c if c!='pooled_R0_R1' else r['cell'].startswith(('R0@','R1@')))]
            for metric in ('attack_lpips_median','attack_psnr_db_median','attack_ssim_rgb_median'):
                correlations.append({'arm':arm,'kind':'quality','tier':tier,'left':c,'right':metric,**correlation([(r.get(field),r.get(metric)) for r in selected])})

paired=[]
for arm in INTERNAL+('wam','vine-r'):
    for c1,c2 in [('R0@0.2','R1@0.1'),('R0@0.4','R1@0.1'),('R1@0.1','R1-rinse@0.1'),('R1-mode@0.2','R1-smooth@0.2'),('D1','R1-mode@0.2'),('D3','R3@0.2')]:
        pairs=[(sr_index[(arm,c1,s)],sr_index[(arm,c2,s)]) for s in sources]
        quality_complete=[(a,b) for a,b in pairs if all(finite(r.get(m)) for r in (a,b) for m in ('attack_lpips_median','attack_psnr_db_median','attack_ssim_rgb_median'))]
        dominant=[(a,b) for a,b in quality_complete if b['attack_lpips_median']<a['attack_lpips_median'] and b['attack_psnr_db_median']>a['attack_psnr_db_median'] and b['attack_ssim_rgb_median']>a['attack_ssim_rgb_median']]
        row={'arm':arm,'left':c1,'right':c2,'n_sources':len(pairs),'quality_complete':len(quality_complete),
             'right_strictly_milder_all3':len(dominant),'left_positive_right_negative_among_dominant':sum(a['positive_majority'] and not b['positive_majority'] for a,b in dominant),
             'positive_paired_difference_right_minus_left':bootstrap_mean([int(b['positive_majority'])-int(a['positive_majority']) for a,b in pairs])}
        field='semantic_decoded_normalized_median' if arm in INTERNAL else 'bit_accuracy_median'
        delta=[b[field]-a[field] for a,b in pairs if finite(a.get(field)) and finite(b.get(field))]
        row['continuous_field']=field;row['continuous_paired_difference']=bootstrap_mean(delta)
        paired.append(row)

# Fixed finite-grid caliper overlap: one best eligible cross-family pair per source.
overlap=[]
for arm in INTERNAL+('wam','vine-r'):
    matched=[]
    for sid in sources:
        eligible=[]
        for s0 in (.1,.2,.4):
            for s1 in (.1,.2,.4):
                a=sr_index[(arm,'R0@'+str(s0),sid)];b=sr_index[(arm,'R1@'+str(s1),sid)]
                fields=('attack_lpips_median','attack_psnr_db_median','attack_ssim_rgb_median')
                if not all(finite(r.get(m)) for r in (a,b) for m in fields):continue
                ds=[abs(a[m]-b[m]) for m in fields]
                if all(d<=limit for d,limit in zip(ds,(.02,1.0,.02))):
                    eligible.append((sum(d/limit for d,limit in zip(ds,(.02,1.0,.02))),s0,s1))
        if eligible:matched.append({'source_id':sid,'pair':min(eligible)})
    overlap.append({'arm':arm,'matched_sources':len(matched),'sources':len(sources),'matches':matched})

# Retained timings are read, never benchmarked locally. Sum each final unit's existing components.
timings=[]
for arm,c in observed+[('unmarked',c) for c in CELL_ORDER]:
    rr=[r for r in rows.values() if r['arm']==arm and cell(r)==c]
    if not rr:continue
    ts=[]
    for r in rr:
        det=r.get('detection_seconds',{})
        if isinstance(det,dict):det=sum(v for v in det.values() if finite(v))
        total=sum(v for v in (r.get('generation_seconds'),det,r.get('metrics_seconds')) if finite(v))
        ts.append(total)
    timings.append({'arm':arm,'cell':c,'n':len(rr),'sum_seconds':sum(ts),'components_total':summary(ts),
                    'generation':summary([r.get('generation_seconds') for r in rr])})

result={'input':str(INPUT),'input_sha256':sha.hexdigest(),'hypotheses_commit':'5cc20912a7120544e5ec4ece3d4a04bc5b4c9921',
        'lines':count,'unique_ids':len(rows),'source_ids':sources,'history_status':dict(history),
        'history_transitions':{' -> '.join(k):v for k,v in transitions.items()},
        'final_status':dict(collections.Counter(r['status'] for r in rows.values())),
        'cell_summaries':cell_summaries,'negative_gates':negatives,'correlations':correlations,
        'paired_comparisons':paired,'fixed_caliper_overlap':overlap,'timings':timings,
        'mechanistic_parameters':'NOT ESTIMABLE: no target encoder residuals, latent chips or derivative transport in saved journals'}
(OUT/'journal-analysis.json').write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8')

def write_csv(name, data):
    fields=list(dict.fromkeys(k for r in data for k in r))
    with (OUT/name).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(data)
write_csv('call-level.csv',calls);write_csv('source-level.csv',source_rows);write_csv('carrier-transitions.csv',transition_tables)

lines=['# Descriptive journal analysis','',f'Final state: {len(rows):,} units from {count:,} journal lines; {len(sources)} sources. No images opened.','',
       'Positive counts use source majority, with missing/blocked calls counted as failures. Continuous values use complete-source medians.','',
       '| Arm | Cell | Positive / 60 | Complete | Semantic decoded normalized margin, median | Instance decoded normalized margin, median | Bit accuracy, median |',
       '|---|---|---:|---:|---:|---:|---:|']
def fmt(v):return 'NA' if v is None else f'{v:.4f}'
for cs in cell_summaries:
    def med(name):return cs['continuous'].get(name,{}).get('median')
    lines.append(f"| {cs['arm']} | {cs['cell']} | {cs['positive_majority']} | {cs['complete_sources']} | {fmt(med('semantic_decoded_normalized_median'))} | {fmt(med('instance_decoded_normalized_median'))} | {fmt(med('bit_accuracy_median'))} |")
lines+=['','No mechanistic gain or full-chain transport parameter can be estimated from these journals. Quality/family regressions are separate diagnostic fits, not the transfer law.','',
        'The selected score/threshold switches branches. Recomputed and decoded branch margins are therefore retained separately in JSON/CSV. The continuous table above uses the decoded branch, not a claim that it alone defines C.','',
        'Negatives, source-paired intervals, complete-case quality dominance, correlations, overlap and retained timing summaries are in journal-analysis.json. Carrier states are preserved at call and source-majority level.']
(OUT/'journal-analysis.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

# Static, standalone scientific SVG with exact source-count labels.
width,height=1120,650
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
     '<rect width="100%" height="100%" fill="white"/>',
     '<style>text{font-family:Arial,sans-serif;fill:#17212b} .lab{font-size:13px}.small{font-size:11px}</style>',
     '<text x="28" y="30" font-size="21">Development source-majority detection across reconstruction stages</text>',
     '<text x="28" y="52" class="lab">60 sources; three repeated seeds for R cells, one output for controls. Native endpoints differ by arm.</text>']
colors={'f5-r2':'#a32c36','v5-r3':'#1f6d8a','wam':'#7365a5','vine-r':'#2f7a54'}
for k,(arm,color) in enumerate(colors.items()):
    svg.append(f'<rect x="{28+k*230}" y="72" width="16" height="12" fill="{color}"/><text x="{50+k*230}" y="83" class="lab">{arm}</text>')
for i,c in enumerate(CELL_ORDER):
    x=95+i*65
    for j,arm in enumerate(colors):
        cs=next(q for q in cell_summaries if q['arm']==arm and q['cell']==c);n=cs['positive_majority'];h=n*6
        svg.append(f'<rect x="{x+j*12}" y="{480-h}" width="10" height="{h}" fill="{colors[arm]}"/>')
        svg.append(f'<text x="{x+j*12+5}" y="{474-h}" text-anchor="middle" class="small">{n}</text>')
    svg.append(f'<text transform="translate({x+25},500) rotate(55)" class="lab">{c}</text>')
for n in (0,15,30,45,60):
    y=480-n*6;svg.append(f'<text x="68" y="{y+4}" text-anchor="end" class="lab">{n}</text>')
svg+=['<text x="28" y="620" class="small">F5/v5: historical semantic C; WAM/VINE-R: known-message presence. No equal-quality or equal-FPR ranking.</text>','</svg>']
(FIG/'source-detection.svg').write_text('\n'.join(svg),encoding='utf-8')
print(json.dumps({'unique_ids':len(rows),'sources':len(sources),'final_status':result['final_status'],
                  'f5_counts':{s['cell']:s['positive_majority'] for s in cell_summaries if s['arm']=='f5-r2'},
                  'caliper_overlap':{s['arm']:s['matched_sources'] for s in overlap}},indent=2))
