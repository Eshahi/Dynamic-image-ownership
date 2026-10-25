"""Additional descriptive state/quality summaries from existing JSONL only."""
import collections
import json
import statistics
from pathlib import Path

HERE=Path(__file__).resolve().parent
INPUT=Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/20261025-0128-encoder-transfer-stage2b/results/stage2b-full/rows.jsonl')
RIGHT='qim-pilot-owner-alpha'
rows={}
with INPUT.open(encoding='utf-8') as f:
    for line in f:
        r=json.loads(line);rows[r['id']]=r
idx={(r['arm'],r['channel'],r['strength'],r['source_id'],r['seed']):r for r in rows.values()}
sources=sorted({r['source_id'] for r in rows.values()})

def det(r,arm):
    if not r or r.get('status')!='ok':return None
    q=r.get('detections',{}).get(arm,{}).get(RIGHT)
    return q if q and q.get('status')=='ok' else None

def state(r,arm):
    q=det(r,arm)
    if q is None:return 'missing'
    if arm in ('wam','vine-r'):
        return 'present' if q.get('presence',{}).get('present') else 'absent'
    s=q['raw']['semantic']
    if s['read'] and s['content_match']:return 'C_success'
    if s['read']:return 'read_content_mismatch'
    if s['found']:return 'found_not_read'
    return 'not_found'

trans=[]
for arm in ('f5-r2','v5-r3','wam','vine-r'):
    counts=collections.Counter()
    for sid in sources:
        for seed in (12,13,14):
            a=idx.get((arm,'R1',.1,sid,seed)); b=idx.get((arm,'R1-rinse',.1,sid,seed))
            counts[(state(a,arm),state(b,arm))]+=1
    trans.append(dict(arm=arm,unit='paired source/base-seed calls, descriptive; not independent trials',
                      transitions=[dict(before=a,after=b,calls=n) for (a,b),n in sorted(counts.items())]))

contrasts=[]
for arm in ('f5-r2','v5-r3','wam','vine-r'):
    for left_strength in (.2,.4):
        for scope in ('distortion','total_distortion'):
            valid=dominant=opposite=0
            deltas=collections.defaultdict(list)
            for sid in sources:
                aa=[idx.get((arm,'R0',left_strength,sid,s)) for s in (12,13,14)]
                bb=[idx.get((arm,'R1',.1,sid,s)) for s in (12,13,14)]
                metrics=('lpips','psnr_db','ssim_rgb')
                if any(not r or r.get('status')!='ok' or any(not isinstance(r.get(scope,{}).get(k),(int,float)) for k in metrics) for r in aa+bb):continue
                a={k:statistics.median(r[scope][k] for r in aa) for k in metrics}
                b={k:statistics.median(r[scope][k] for r in bb) for k in metrics}
                valid+=1
                for k in metrics:deltas[k].append(b[k]-a[k])
                dom=b['lpips']<a['lpips'] and b['psnr_db']>a['psnr_db'] and b['ssim_rgb']>a['ssim_rgb']
                dominant+=int(dom)
                yes='C_success' if arm.startswith(('f5','v5')) else 'present'
                posa=sum(state(r,arm)==yes for r in aa)>=2
                posb=sum(state(r,arm)==yes for r in bb)>=2
                opposite+=int(dom and posa and not posb)
            contrasts.append(dict(arm=arm,left=f'R0@{left_strength}',right='R1@0.1',quality_reference=scope,
                                  complete_sources=valid,right_milder_all_three=dominant,left_positive_right_negative_among_milder=opposite,
                                  median_paired_difference_right_minus_left={k:statistics.median(v) for k,v in deltas.items()}))

out=dict(rinse_state_transitions=trans,paired_quality_reference_sensitivity=contrasts,
         status='Additional post-hoc descriptive sensitivity; not a new confirmatory hypothesis. No metrics recomputed.')
(HERE/'state-and-quality.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'f5_quality':[r for r in contrasts if r['arm']=='f5-r2'],'rinse':trans},indent=2))
