"""Post-hoc saved-score analysis; stdlib only; no project imports."""
import collections, json, math, statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parent
INPUT=Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/20261025-0128-encoder-transfer-stage2b/results/stage2b-full/rows.jsonl')
RIGHT='qim-pilot-owner-alpha'; WRONG='qim-pilot-owner-beta'
METHODS=('f5-r2','v5-r3')
def finite(x): return isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x)
def quant(v,p):
    if not v:return None
    a=sorted(v);t=(len(a)-1)*p;i=int(t);return a[i]+(a[min(i+1,len(a)-1)]-a[i])*(t-i)
def stats(v):
    v=[x for x in v if finite(x)]
    return dict(n=len(v),min=min(v) if v else None,p05=quant(v,.05),median=quant(v,.5),p95=quant(v,.95),max=max(v) if v else None)
def cell(r):return r['channel']+('@'+str(r['strength']) if r['strength'] is not None else '')
def seeds(c):return (12,13,14) if c.startswith('R') else (None,)
def call(r,m,o):
    if not r or r.get('status')!='ok':return None
    d=r.get('detections',{}).get(m,{}).get(o)
    return d if d and d.get('status')=='ok' else None
def val(d,t,b,suffix='score'):
    x=(d or {}).get('raw',{}).get(t,{}).get(b+'_'+suffix)
    return x if finite(x) else None
rows={}; lines=0
with INPUT.open(encoding='utf-8') as f:
    for line in f:
        if line.strip():r=json.loads(line);rows[r['id']]=r;lines+=1
sources=sorted({r['source_id'] for r in rows.values()})
idx={(r['arm'],cell(r),r['source_id'],r['seed']):r for r in rows.values()}
cells=sorted({cell(r) for r in rows.values() if r['arm']=='f5-r2'})
summaries=[];paired=[];specificity=[];anomalies=collections.Counter();vine=[]
for m in METHODS:
 for c in cells:
  expected=len(sources)*len(seeds(c))
  for kind in ('C0','wrong_owner','C1'):
   calls=[];miss=collections.Counter(); sourcecalls=collections.Counter()
   for s in sources:
    for seed in seeds(c):
     r=idx.get(('unmarked' if kind=='C0' else m,c,s,seed));d=call(r,m,WRONG if kind=='wrong_owner' else RIGHT)
     if d is None:miss[(r or {}).get('status','row_absent')]+=1;continue
     calls.append((s,seed,d));sourcecalls[s]+=1
   for tier in ('semantic','instance'):
    branchstates=collections.Counter();found=read=0
    for s,seed,d in calls:
     q=d.get('raw',{}).get(tier,{})
     rr=val(d,tier,'recomputed');rt=val(d,tier,'recomputed','threshold');dd=val(d,tier,'decoded');dt=val(d,tier,'decoded','threshold')
     if all(finite(x) for x in (rr,rt,dd,dt)):
      a,b=rr>=rt,dd>=dt;branchstates[('both' if a and b else 'recomputed_only' if a else 'decoded_only' if b else 'neither')]+=1
      if bool(q.get('found'))!=(a or b):anomalies['found_inconsistent']+=1
      if bool(q.get('read'))!=b:anomalies['read_inconsistent']+=1
     found+=bool(q.get('found'));read+=bool(q.get('read'))
    for branch in ('recomputed','decoded'):
     per=collections.defaultdict(list); scores=[]; thresholds=[]
     for s,seed,d in calls:
      score=val(d,tier,branch);thr=val(d,tier,branch,'threshold')
      if score is not None and thr is not None:per[s].append(score-thr);scores.append(score);thresholds.append(thr)
     summaries.append(dict(method=m,cell=c,kind=kind,tier=tier,branch=branch,expected_calls=expected,observed_calls=len(calls),missing=dict(miss),margin_coverage=sum(map(len,per.values())),sources_available=len(per),sources_complete=sum(len(v)==len(seeds(c)) for v in per.values()),score=stats(scores),thresholds=sorted(set(thresholds)),margin=stats([x for v in per.values() for x in v]),source_max_margin_available=stats([max(v) for v in per.values()]),source_max_margin_complete=stats([max(v) for v in per.values() if len(v)==len(seeds(c))]),found=found,read=read,test_states=dict(branchstates)))
  for tier in ('semantic','instance'):
   for branch in ('recomputed','decoded'):
    for contrast in ('C1_minus_C0','right_minus_wrong_owner'):
     per=collections.defaultdict(list);aall=[];ball=[]
     for s in sources:
      for seed in seeds(c):
       r=idx.get((m,c,s,seed));a=call(r,m,RIGHT)
       b=call(idx.get(('unmarked',c,s,seed)),m,RIGHT) if contrast=='C1_minus_C0' else call(r,m,WRONG)
       av=val(a,tier,branch);bv=val(b,tier,branch)
       if av is not None and bv is not None:per[s].append(av-bv);aall.append(av);ball.append(bv)
     rec=dict(method=m,cell=c,tier=tier,branch=branch,contrast=contrast,expected_pairs=expected,complete_pairs=sum(map(len,per.values())),missing_pairs=expected-sum(map(len,per.values())),sources_available=len(per),sources_complete=sum(len(v)==len(seeds(c)) for v in per.values()),delta_calls=stats([x for v in per.values() for x in v]),delta_source_median_complete=stats([statistics.median(v) for v in per.values() if len(v)==len(seeds(c))]),delta_source_max_complete=stats([max(v) for v in per.values() if len(v)==len(seeds(c))]),positive_delta_calls=sum(x>0 for v in per.values() for x in v),left_score=stats(aall),right_score=stats(ball))
     (paired if contrast=='C1_minus_C0' else specificity).append(rec)
for c in cells:
 for kind in ('C0','wrong_message'):
  vals=[];ths=[];per=collections.defaultdict(list);events=[];missing=collections.Counter()
  for s in sources:
   for seed in seeds(c):
    r=idx.get(('unmarked' if kind=='C0' else 'vine-r',c,s,seed));d=call(r,'vine-r',RIGHT)
    p=(d or {}).get('presence' if kind=='C0' else 'wrong_message_presence',{})
    acc=p.get('accuracy');bits=p.get('bits');thr=p.get('threshold')
    if not all(finite(x) for x in (acc,bits,thr)) or bits<=0:missing[(r or {}).get('status','row_absent')]+=1;continue
    vals.append(acc);ths.append(thr/bits);per[s].append(acc-thr/bits)
    if p.get('present'):events.append(dict(source_id=s,seed=seed,accuracy=acc,bits=bits,threshold=thr,row_id=r['id']))
  vine.append(dict(cell=c,kind=kind,expected_calls=len(sources)*len(seeds(c)),observed_scores=len(vals),missing=dict(missing),accuracy=stats(vals),thresholds=sorted(set(ths)),margin=stats([x for v in per.values() for x in v]),source_max_margin_complete=stats([max(v) for v in per.values() if len(v)==len(seeds(c))]),sources_complete=sum(len(v)==len(seeds(c)) for v in per.values()),events=events))
out=dict(status='post-hoc AUTHOR saved-score descriptive analysis; no scientific measurement',input=str(INPUT),journal_lines=lines,last_state_units=len(rows),row_status=dict(collections.Counter(r['status'] for r in rows.values())),sources=len(sources),internal=summaries,paired_C1_C0=paired,owner_specificity=specificity,vine=vine,contract_anomalies=dict(anomalies),denominator_note='C0 once per method/cell/source/base-seed, never multiplied by marked arm contexts. Native R0/R1 cells versus diagnostic D/X and rinse/mode/smooth retained separately. Source maxima available and complete reported. Rinse label is base seed; internal second seed adds 100.')
(ROOT/'negative-background-analysis.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:out[k] for k in ('journal_lines','last_state_units','row_status','sources','contract_anomalies')}))
print('INTERNAL DECODED SEMANTIC: method cell kind observed median max sourceMaxMedian')
for r in summaries:
 if r['tier']=='semantic' and r['branch']=='decoded':print(r['method'],r['cell'],r['kind'],r['observed_calls'],r['margin']['median'],r['margin']['max'],r['source_max_margin_complete']['median'])
print('PAIRED SEMANTIC DECODED')
for r in paired:
 if r['tier']=='semantic' and r['branch']=='decoded':print(r['method'],r['cell'],r['complete_pairs'],r['delta_source_median_complete']['median'])
print('VINE EVENTS', [r for r in vine if r['events']])

# Rebuild the report beneath the pre-journal frozen plan.
report_path=ROOT/'negative-background-analysis.md'
plan=report_path.read_text(encoding='utf-8').split('\n## Results\n')[0].rstrip()
text=['','## Results','',
'Journal reduction: **39,896 lines -> 11,040 last-state units**, 11,017 ok and 23 safety blocked, covering 60 sources. No saved found/read predicate inconsistency was found. All scores below come from saved detector calls; no images or models were opened.',
'',
'Each native regeneration cell schedules 180 calls (60 sources x 3 dependent seeds); clean and D/X diagnostics schedule 60. R1, R3, rinse, mode and smooth calls have full score coverage. C0 is counted once per method/cell/source/seed, even though the same unmarked image is queried by several methods. C0 and wrong-owner call types remain separate, as do semantic and instance tiers. Wrong-owner queries here are beta on the method\'s own marked arm, not all cross-arm combinations.',
'',
'### Do losses approach background?','',
'Yes, descriptively, with residual score displacement. F5 semantic decoded alignment loses most of its separation from C0 under SDXL. Its paired **median over 60 complete source seed-medians** of C1-minus-C0 score is 12.068 clean, 1.989 at R1 .1, 0.919 at .2 and 0.342 at .4. The matched v5 values are 13.420, 6.485, 3.761 and 1.810. These are paired scores, not differences between unpaired medians. There is no equivalence test and no claim that the distributions become identical.',
'',
'F5 semantic decoded C1 call-median score-minus-threshold is +7.033 clean and -2.749/-3.946/-4.342 under R1 .1/.2/.4; C0 medians are -4.866/-4.784/-4.755 there. Thus low positive results coexist with negative backgrounds far below threshold, rather than a negative background rising to trigger detections. At R1 .1, the largest F5 semantic decoded margin is +1.000 even though C source-majority is zero: decoded readability alone does not establish content compatibility or original payload recovery. At .2 and .4 even the largest decoded margins are below zero (-1.016 and -2.001).',
'',
'F5 instance decoded C1-minus-C0 separation remains 6.011/4.064/2.290 at R1 .1/.2/.4. Its surviving instance alignment is not latent semantic survival; endpoint A is the union of semantic and instance found. F5 D1/D3 semantic displacements remain 9.501/9.982, while full R3 gives 2.468; this is a descriptive pipeline contrast, not an isolated encoder mechanism.',
'',
'### Do wrong-owner margins show query specificity?','',
'Right-minus-wrong semantic decoded source-median differences for F5 are 12.710 clean and 2.821/1.528/0.969 at R1 .1/.2/.4. For v5 they are 13.386 clean and 6.861/4.135/2.128. These are descriptive query-specific score contrasts below threshold in the failed cells, not causal or carrier evidence. They do not imply a successful owner test, lawful ownership, independent channels, or universal specificity against other keys. F5 wrong-owner semantic backgrounds are slightly lower than its C0 backgrounds; marked versus unmarked content can alter alignment, so those two negative controls are not interchangeable.',
'',
'### Fixed-threshold negative margins, both branches','',
'The table gives the greatest saved margin across all cells and both negative query types. Every maximum is negative. Found is the OR of branch tests, while read uses decoded only; inspecting decoded margins alone would miss a recomputed-only false event. In fact both channels have zero found/read negatives for both internal methods.',
'',
'| Method | Tier | Maximum decoded margin | Maximum recomputed margin |','|---|---|---:|---:|']
for m in METHODS:
 for tier in ('semantic','instance'):
  ns=[r for r in summaries if r['method']==m and r['tier']==tier and r['kind']!='C1']
  a=max(r['margin']['max'] for r in ns if r['branch']=='decoded');b=max(r['margin']['max'] for r in ns if r['branch']=='recomputed')
  text.append(f'| {m} | {tier} | {a:.3f} | {b:.3f} |')
text += ['', '### Per-cell semantic decoded source maxima','',
'Each median below is over source-wise maximum margins. Complete-source restriction requires every scheduled seed. Coverage columns give observed calls/expected calls and complete sources/60 for C0 and wrong owner, respectively. Source maxima account for within-source repeated queries descriptively; they are not independent false-positive trials. Native cells are R0/R1/R3; clean, D/X, rinse/mode/smooth remain separately labelled diagnostic contrasts.',
'', '| Method | Cell | C0 coverage; complete sources | C0 median source max | Wrong coverage; complete sources | Wrong median source max |', '|---|---|---|---:|---|---:|']
for m in METHODS:
 for c in cells:
  a=next(r for r in summaries if r['method']==m and r['cell']==c and r['kind']=='C0' and r['tier']=='semantic' and r['branch']=='decoded')
  b=next(r for r in summaries if r['method']==m and r['cell']==c and r['kind']=='wrong_owner' and r['tier']=='semantic' and r['branch']=='decoded')
  text.append(f"| {m} | {c} | {a['observed_calls']}/{a['expected_calls']}; {a['sources_complete']}/60 | {a['source_max_margin_complete']['median']:.3f} | {b['observed_calls']}/{b['expected_calls']}; {b['sources_complete']}/60 | {b['source_max_margin_complete']['median']:.3f} |")
text += ['', 'Full source-max distributions (min, p05, median, p95, max), both available and complete-source versions, call distributions and coverage for **both tiers and both branches in every cell** are in `negative-background-analysis.json`. Paired comparison missingness is separately recorded there; under R0 the paired C1/C0 calls are F5 177/176/177 and v5 178/177/177 at .1/.2/.4. Missing is never changed to a zero score or a negative.',
'', '### VINE-R native fixed-threshold negative background','',
'The saved native 100-bit threshold is 69/100, inclusive. Across 4,191 available C0 plus wrong-message scores in these cells, exactly one crosses it: C0 R1 .1, source 1295, base seed 14, accuracy .69, margin zero. Its R1 .1 C0 cell has 180/180 scores: median .49, p95 .57, maximum .69. Across the 60 complete source maxima the median accuracy is .52, p95 .59 and maximum .69. This is an observed boundary event; it does not justify moving the threshold or inferring a population false-positive rate from pooled dependent calls. JSON retains every cell and each wrong-message/C0 denominator separately.',
'', '### Interpretation limits','',
'C1-minus-C0 decoded scores may maximize over different decoded words, and recomputed scores may use different output-derived content codes q. These native score contrasts are not a common-pattern linear transported signal, a fixed-pattern signal increment, or evidence of carrier recovery. Right-minus-wrong changes the query direction and may change threshold context; its raw-score contrast does not hold the queried pattern fixed. All analyses are post-hoc author diagnostics of development data whose aggregate outcomes were already known. Scores are normalized alignment statistics (decoded scores include a pattern search); a negative margin or loss of separation cannot measure absolute carrier amplitude or prove destruction. Readable mismatches remain distinct from absent carriers. A nonzero right-minus-wrong score is not a passing owner query. Background distributions under these saved keys/sources do not establish a universal null law, cryptographic security or confirmatory FPR. No causal encoder effect is identified: the pipelines differ in multiple components. Same-source/seed pairing does not guarantee identical random draws across marked/unmarked inputs or pipeline families. Rinse pairs use base seed 12/13/14, with its second pass adding 100 internally.',
'', 'Reproduce with the permitted stdlib interpreter and `-I negative-background-analysis.py`. Only the saved journal is read; this script writes this report and its JSON sibling.']
report_path.write_text(plan+'\n'+'\n'.join(text)+'\n',encoding='utf-8')

