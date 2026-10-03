"""Exploratory diagnostics of retained dev-001 JSON; no model, image decode or threshold tuning."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import statistics

OWNER = 'qim-pilot-owner-alpha'

def h(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def detection(row):
    found=[d['result'] for d in row['detections'] if d['claimed_owner']==OWNER and d['binding_mode']=='combined']
    if len(found)>1:
        raise ValueError('duplicate claimed-owner combined call')
    return found[0] if found else None

def distance(a,b):
    return (int(a,16)^int(b,16)).bit_count()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('results',type=Path); p.add_argument('--expected-sha256',required=True)
    p.add_argument('--out',type=Path,required=True); args=p.parse_args()
    digest=h(args.results)
    if digest!=args.expected_sha256:
        raise ValueError('retained result digest mismatch')
    d=json.loads(args.results.read_text()); rows=d['rows']; index={r['id']:r for r in rows}
    if d['run_id']!='c4-v5-two-tier-dev-001' or len(rows)!=617 or len(index)!=617:
        raise ValueError('unexpected inventory')
    strata=defaultdict(list)
    for r in rows:
        if r['axis']=='T3' and r['control'] in ('C1','C2'):
            key=r['control']+'/'+('vae_mode' if r['dose']=='vae_mode' else str(r['strength']))
            result=detection(r)
            entry={'id':r['id'],'source_id':r['source_id'],'seed':r['seed'],'status':r['status']}
            if result is None:
                entry.update(category='missing',errors=r.get('errors',[]))
            else:
                sem=result['semantic']; clean=detection(index[f'clean-{r["source_id"]}-{r["control"]}'])
                entry.update(category='semantic_match' if sem['found'] and sem['content_match'] else
                    'semantic_found_without_content_match' if sem['found'] else 'below_both_semantic_thresholds',
                    outcome=result['outcome'], semantic_content_status=sem['content_status'],
                    recomputed_margin=sem['recomputed_score']-sem['recomputed_threshold'],
                    decoded_margin=sem['decoded_score']-sem['decoded_threshold'],
                    q_drift_from_marked=distance(result['semantic_code'],clean['semantic_code']),
                    clip_source_cosine=r.get('clip_source_cosine'))
                expected=bool(entry['recomputed_margin']>=0 or entry['decoded_margin']>=0)
                if expected!=sem['found']:
                    raise ValueError('saved semantic threshold decision inconsistent')
            strata[key].append(entry)
    t3={}
    for key, rr in sorted(strata.items()):
        vals=[r['q_drift_from_marked'] for r in rr if 'q_drift_from_marked' in r]
        t3[key]={'counts':dict(Counter(r['category'] for r in rr)), 'planned_rows':len(rr),
            'q_drift':{'n':len(vals),'mean':statistics.mean(vals),'median':statistics.median(vals),
                'sd':statistics.stdev(vals),'min':min(vals),'max':max(vals)},'rows':rr}
    t4=[]
    for r in rows:
        if r['axis']!='T4': continue
        q=r.get('quality')
        if q is None: raise ValueError('T4 quality missing')
        reasons=[]
        if not(q.get('zero_error') or q['psnr_db']>35): reasons.append('PSNR<=35')
        if not q['ssim_rgb']>.9: reasons.append('SSIM<=0.9')
        if not q['lpips']['value']<.1: reasons.append('LPIPS>=0.1')
        if reasons:t4.append({'id':r['id'],'recipient_id':r['recipient_id'],'reasons':reasons,'quality':q})
    t5=[]
    for r in rows:
        if r['axis']!='T5' or r['semantic_label']!='same':continue
        t5.append({'id':r['id'],'C0':r['distances_C0'],'C1':r['distances_C1'],
            'qualifying_C0':r['distances_C0']['semantic']<=6 and r['distances_C0']['instance']>6,
            'qualifying_C1':r['distances_C1']['semantic']<=6 and r['distances_C1']['instance']>6})
    result={'analysis_type':'post-outcome exploratory saved-output diagnostic','run_id':d['run_id'],
        'results_sha256':digest,'script_sha256':h(Path(__file__)),'T3':t3,'T4_inadmissible':t4,'T5_same_pairs':t5,
        'limits':'Operational classification, not causal isolation. No criterion/threshold changes, exclusions, new images, GPU calls or inferential statistics. Human visual assessments remain missing.'}
    args.out.mkdir(parents=True,exist_ok=False)
    (args.out/'diagnostic.json').write_text(json.dumps(result,indent=2)+'\n')
    lines=['# Retained v5 dev-001: failure-mode diagnostic','',
        'Issue #18. Post-outcome exploratory analysis dated 2026-10-03; this is not a new scientific run or retrospective preregistration. All original rows, thresholds and missing outputs remain unchanged. No GPU/model call or source-image access is needed.','',
        '## Regeneration: recorded semantic decision paths','',
        '| Arm / dose | Planned | Semantic match | Found, content not matched | Below both thresholds | Missing | q-drift mean / median / SD / range |',
        '| --- | --- | --- | --- | --- | --- | --- |']
    for k,v in t3.items():
        c=v['counts'];s=v['q_drift']
        lines.append(f'| {k} | {v["planned_rows"]} | {c.get("semantic_match",0)} | {c.get("semantic_found_without_content_match",0)} | {c.get("below_both_semantic_thresholds",0)} | {c.get("missing",0)} | {s["mean"]:.2f} / {s["median"]:.1f} / {s["sd"]:.2f} / {s["min"]}–{s["max"]} |')
    lines+=['','q-drift is Hamming distance between the suspect-recomputed semantic code and that of its clean marked source; summaries use only available outputs and do not erase the missing count. Rows and seeds are correlated; these summaries are descriptive. Below both thresholds means neither saved semantic score meets its own unchanged threshold. It does not isolate whether channel distortion, code drift, or both caused the loss. Content mismatch/uncertainty is reported separately from signal absence.','',
        '## Copy-paste: quality failures','', '| Row | Recipient | Failed numerical thresholds |','| --- | --- | --- |']
    for r in t4:lines.append(f'| {r["id"]} | {r["recipient_id"]} | {", ".join(r["reasons"])} |')
    lines+=['','These quality failures explain which attempted transfers cannot contribute to recipient coverage; changing a deadline cannot make them admissible. They remain in the original denominators.','',
        '## Semantic collision: before and after marking','', '| Frozen same pair | C0 q / H | C1 q / H | Qualifies C0 | Qualifies C1 |','| --- | --- | --- | --- | --- |']
    for r in t5:lines.append(f'| {r["id"]} | {r["C0"]["semantic"]} / {r["C0"]["instance"]} | {r["C1"]["semantic"]} / {r["C1"]["instance"]} | {r["qualifying_C0"]} | {r["qualifying_C1"]} |')
    lines+=['',f'Qualifying same pairs: {sum(r["qualifying_C0"] for r in t5)}/7 before marking and {sum(r["qualifying_C1"] for r in t5)}/7 after marking, against the fixed minimum of five. This is a comparison of saved feature distances, not proof of a causal mechanism or justification for relabeling pairs.','',
        '## Next-experiment decision','',
        'Do not repeat the unchanged deterministic batch merely to consume the new 45-minute allowance. It already terminated without a time-limit failure; safety-blocked outputs, low detection scores and insufficient pair/recipient coverage would not be repaired by waiting longer. Do not disable the safety checker or replace failed sources. A subsequent scientific experiment should test a prospectively specified method/coverage hypothesis with fresh exact provenance and retain this baseline. Independent human visual assessment remains outstanding. This diagnostic itself makes no new acceptance claim.','',
        '## Provenance','',f'- Results SHA256: `{digest}`.',f'- Diagnostic script SHA256: `{result["script_sha256"]}`.',
        '- Script: `scripts/analyze_v5_failure_modes.py`; input: MAIN `.thesis-build/v5-study-runs/C4-v5-two-tier-development/c4-v5-two-tier-dev-001/outputs/results.json`.',
        '- Derived rows: MAIN `.thesis-build/v5-dev001-diagnostic-20261003/diagnostic.json`. Reproduce with the script, the exact result path, `--expected-sha256` above and a fresh `--out` directory.',
        '- Original result report: `experiments/c4-v5-two-tier-regeneration-v1/results-dev-001.md`.']
    (args.out/'diagnostic.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'T3':{k:v['counts'] for k,v in t3.items()},'T4_inadmissible':len(t4),
        'T5_qualifying_C0':sum(r['qualifying_C0'] for r in t5),'T5_qualifying_C1':sum(r['qualifying_C1'] for r in t5)}))

if __name__=='__main__':main()
