"""CPU-only descriptive analysis of a finished E1 Stage A record.

No detector/scientific imports, re-execution, threshold fitting or gate promotion.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

ALPHA = 'qim-pilot-owner-alpha'
BETA = 'qim-pilot-owner-beta'
IDS = (1675, 499768)
CONDITIONS = ('clean', 'sd15_vae', 'sdxl_vae')


def encode(q):
    """Independent integer polynomial division; no production codec import."""
    shifted = int(q, 16) << 27
    remainder = shifted
    while remainder.bit_length() >= 28:
        remainder ^= 0x086e8113 << (remainder.bit_length() - 28)
    return shifted ^ remainder


def read_json(path, default=None):
    return json.loads(path.read_text(encoding='utf-8-sig')) if path.exists() else default


def read_rows(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()
            if line.strip()] if path.exists() else []


def strict_quality(m):
    return bool(m and (m.get('psnr_infinite') is True or
        (m.get('psnr_db') is not None and m['psnr_db'] > 35)) and
        m.get('ssim_rgb', 0) > .9 and m.get('lpips', 1) < .1)


def distance(value, target):
    return None if value is None or target is None else (int(value, 16) ^ int(target, 16)).bit_count()


def endpoint(call, payload=None):
    """Payload comparison is evaluator-only and only for intended-owner C1."""
    s, i = call['semantic'], call['instance']
    payload = payload or {}
    qe, he = distance(s.get('decoded_code'), payload.get('q')), distance(i.get('decoded_code'), payload.get('h'))
    raw = s.get('raw_coded_word')
    if raw is not None and (not isinstance(raw, str) or len(raw) != 15 or
                            not 0 <= int(raw, 16) < 2**59):
        raise ValueError('Invalid 59-bit raw coded word')
    result = dict(A=bool(s['found'] or i['found']), S=bool(s['found'] and s['content_match']),
        R=bool(s['read']), Q=bool(s['read'] and qe == 0) if 'q' in payload else None,
        J=bool(s['read'] and qe == 0 and s['content_match']) if 'q' in payload else None,
        H=bool(i['read'] and he == 0) if 'h' in payload else None, F=call['outcome'] == 'both_match',
        target_comparison_applicable=bool(payload), q_bit_errors=qe, h_bit_errors=he, decoded_q=s.get('decoded_code'),
        decoded_h=i.get('decoded_code'), raw_coded_word=raw,
        raw_coded_bit_errors=None if raw is None or 'q' not in payload else
            (int(raw, 16) ^ encode(payload['q'])).bit_count(),
        decoded_q_available=s.get('decoded_code') is not None,
        bch_success=s.get('bch_success'), bch_reason=s.get('bch_reason'),
        semantic_content_match=s['content_match'], instance_read=i['read'],
        instance_content_match=i['content_match'], outcome=call['outcome'],
        seconds=call.get('seconds'), routing=call.get('routing'))
    # Preserve every scalar channel field, including thresholds and bound warnings.
    result['channel_scalars'] = {tier: {k: v for k, v in values.items()
        if v is None or isinstance(v, (str, int, float, bool))}
        for tier, values in (('semantic', s), ('instance', i))}
    return result


def analyze(run_dir):
    run = read_json(run_dir / 'run.json')
    if not run or run.get('outcome') == 'running' or run.get('qualification') in ('pending', 'pending_finalization'):
        raise ValueError('Run is absent or unfinished; analysis requires a final run.json')
    rows = read_rows(run_dir / 'rows.jsonl')
    selected = {sid: [r for r in rows if r.get('source_id') == sid] for sid in IDS}
    calls, sources, negatives = [], [], []
    issues = []
    for sid in IDS:
        matches = selected[sid]
        if len(matches) != 1:
            issues.append(f'Source {sid}: expected one row, observed {len(matches)}')
        r = matches[0] if len(matches) == 1 else {}
        payload = r.get('payload', {})
        source = dict(source_id=sid, status=r.get('status', 'missing'), error=r.get('error'),
            update_status=r.get('update_status'), accepted_updates=r.get('accepted_updates'),
            timings={k:r.get(k) for k in ('construction_seconds', 'refinement_seconds',
                'vae_negative_seconds', 'duration_seconds')}, conditions={})
        initial = r.get('initial_qualification', {})
        initial_call = endpoint(initial['call'], payload) if initial.get('call') else None
        source['initializer'] = dict(endpoints=initial_call, quality=initial.get('metrics'),
            strict_quality=strict_quality(initial.get('metrics')),
            feasible=r.get('initial_balls', {}).get('feasible') is True,
            qualified=bool(initial_call and initial_call['Q'] and initial_call['H'] and initial_call['F']
                and strict_quality(initial.get('metrics')) and r.get('initial_balls', {}).get('feasible') is True))
        source['final_feasible'] = r.get('final_balls', {}).get('feasible') is True
        for condition in CONDITIONS:
            c = r.get('conditions', {}).get(condition, {})
            intended = c.get('calls', {}).get(ALPHA)
            e = endpoint(intended, payload) if intended else None
            source['conditions'][condition] = dict(available=e is not None, endpoints=e,
                quality=c.get('quality_source'), strict_quality=strict_quality(c.get('quality_source')))
            for owner, call in c.get('calls', {}).items():
                entry = dict(source_id=sid, condition=condition, arm='C1', owner=owner,
                    endpoints=endpoint(call, payload if owner == ALPHA else None))
                calls.append(entry)
                if owner == BETA:
                    negatives.append(entry)
            if c.get('c0_call'):
                entry = dict(source_id=sid, condition=condition, arm='C0', owner=ALPHA,
                    endpoints=endpoint(c['c0_call']))
                calls.append(entry)
                negatives.append(entry)
        sources.append(source)
    clean = [s['conditions']['clean'] for s in sources]
    counts = dict(completed_sources=sum(s['status'] == 'ok' for s in sources), planned_sources=2,
        strict_clean_quality=sum(c['strict_quality'] for c in clean),
        clean_exact_q_h_both_match=sum(bool(c['endpoints'] and c['endpoints']['Q'] and
            c['endpoints']['H'] and c['endpoints']['F']) for c in clean),
        valid_initializers=sum(s['initializer']['qualified'] for s in sources),
        final_feasible=sum(s['final_feasible'] for s in sources),
        joint_fixed_q={b:sum(bool(s['conditions'][b]['endpoints'] and
            s['conditions'][b]['endpoints']['J'] and s['conditions'][b]['endpoints']['S'])
            for s in sources) for b in CONDITIONS},
        planned_negative_calls=12, completed_negative_calls=len(negatives),
        negative_any_detections=sum(n['endpoints']['A'] for n in negatives))
    counts['negative_by_arm'] = {arm:dict(planned=6,
        completed=sum(n['arm'] == arm for n in negatives),
        any_detections=sum(n['endpoints']['A'] for n in negatives if n['arm'] == arm))
        for arm in ('C0', 'C1')}
    screen = bool(not issues and counts['completed_sources'] == 2 and
        all(counts[k] == 2 for k in ('strict_clean_quality', 'clean_exact_q_h_both_match',
                                  'valid_initializers', 'final_feasible')) and
        counts['joint_fixed_q']['sd15_vae'] == counts['joint_fixed_q']['sdxl_vae'] == 2 and
        len(negatives) == 12 and counts['negative_any_detections'] == 0)
    t3_rows = read_rows(run_dir / 'e1-t3-rows.jsonl')
    t3_saved = read_json(run_dir / 'e1-t3-summary.json', {})
    t3 = dict(status=run.get('conditional_t3', {}).get('status',
        'evaluated' if t3_rows else ('required_missing' if screen else 'not_triggered_screen_failure')),
        planned_image_rows=24, planned_full_calls=36, planned_negative_calls=24,
        observed_image_rows=len(t3_rows), observed_full_calls=0, observed_negative_calls=0,
        negative_any_detections=0, calls=[], strengths={}, unavailable_rows=[], pass_recomputed=False)
    plan = {(arm, sid, strength, seed) for arm in ('shared_C0', 'candidate_C1')
        for sid in IDS for strength in (.1, .2) for seed in range(3)}
    observed, candidates = [], {}
    for r in t3_rows:
        key = (r['arm'], r['source_id'], float(r['strength']), r['seed'])
        observed.append(key)
        if r.get('status') != 'ok':
            t3['unavailable_rows'].append(dict(identity=list(key), status=r.get('status'), error=r.get('error')))
        for owner, call in r.get('calls', {}).items():
            e = endpoint(call, r.get('payload') if r['arm'] == 'candidate_C1' and owner == ALPHA else None)
            t3['calls'].append(dict(identity=list(key), owner=owner, endpoints=e))
            t3['observed_full_calls'] += 1
            if (r['arm'] == 'shared_C0' and owner == ALPHA) or (r['arm'] == 'candidate_C1' and owner == BETA):
                t3['observed_negative_calls'] += 1
                t3['negative_any_detections'] += e['A']
            if r['arm'] == 'candidate_C1' and owner == ALPHA:
                candidates[(r['source_id'], float(r['strength']), r['seed'])] = e
    comparisons = {tuple(map(float, c['identity'].split('|'))):c for c in t3_saved.get('comparisons', [])}
    for strength, minimum in ((.1, 6), (.2, 5)):
        keys = [(sid, strength, seed) for sid in IDS for seed in range(3)]
        successes = {e:sum(candidates.get(k, {}).get(e, False) for k in keys) for e in ('S', 'Q', 'J')}
        retention = {}
        for method in ('D2', 'frozen_F5'):
            retention[method] = {}
            for e in ('S', 'Q', 'J'):
                known = [k for k in keys if method in comparisons.get(k, {})]
                old = [k for k in known if comparisons[k][method][e]]
                retention[method][e] = dict(comparator_available=len(known), old_positive=len(old),
                    lost=[list(k) for k in old if not candidates.get(k, {}).get(e, False)],
                    gained=[list(k) for k in known if not comparisons[k][method][e] and candidates.get(k, {}).get(e, False)])
        t3['strengths'][str(strength)] = dict(planned=6, successes=successes, retention=retention,
            count_pass=successes['Q'] >= minimum and successes['J'] >= minimum,
            preservation_pass=all(v['comparator_available'] == 6 and not v['lost']
                for method in retention.values() for v in method.values()))
    t3['complete'] = len(observed) == 24 and set(observed) == plan and not t3['unavailable_rows']
    t3['pass_recomputed'] = bool(t3['complete'] and t3['observed_full_calls'] == 36 and
        t3['observed_negative_calls'] == 24 and not t3['negative_any_detections'] and
        not t3_saved.get('error') and all(v['count_pass'] and v['preservation_pass'] for v in t3['strengths'].values()))
    timing_values = [s['timings'] for s in sources]
    projection = None
    if (run.get('startup_seconds') is not None and run.get('finalization_seconds') is not None and
            all(all(t.get(k) is not None for k in ('construction_seconds', 'refinement_seconds', 'vae_negative_seconds')) for t in timing_values)):
        projection = run['startup_seconds'] + 15*max(sum(t[k] for k in
            ('construction_seconds', 'refinement_seconds', 'vae_negative_seconds')) for t in timing_values) + run['finalization_seconds']
    duration = run.get('duration_seconds')
    parent_wall = read_json(run_dir / 'parent-wall.json', {})
    inclusive_duration = parent_wall.get('duration_seconds', duration)
    memory_ok = 0 < run.get('peak_allocated_bytes', 0) <= 10 * 1024**3
    cap_ok = (duration is not None and inclusive_duration <= 900 and memory_ok
        and not run.get('budget_overrun', False))
    stage_pass = bool(screen and t3['pass_recomputed'] and projection is not None and projection <= 3300 and cap_ok)
    target_calls = [c['endpoints'] for c in calls if c['arm'] == 'C1' and c['owner'] == ALPHA]
    target_calls += [c['endpoints'] for c in t3['calls'] if c['identity'][0] == 'candidate_C1' and c['owner'] == ALPHA]
    histograms = {name:dict(sorted(Counter(str(e[name]) for e in target_calls if e[name] is not None).items()))
        for name in ('raw_coded_bit_errors', 'q_bit_errors')}
    saved = run.get('summary', {})
    return dict(schema='journal-e1-bch-analysis-v1', run_dir=str(run_dir), commit=run.get('commit'),
        outcome=run.get('outcome'), qualification=run.get('qualification'), sources=sources,
        calls=calls, screen_counts=counts, screen_pass_recomputed=screen, t3=t3,
        error_histograms=histograms, missing_error_values={name:sum(e[name] is None for e in target_calls)
            for name in ('raw_coded_bit_errors', 'q_bit_errors')},
        timing=dict(duration_seconds=duration, parent_inclusive_seconds=inclusive_duration,
            peak_allocated_bytes=run.get('peak_allocated_bytes'), memory_cap_pass=memory_ok,
            startup_seconds=run.get('startup_seconds'),
            finalization_seconds=run.get('finalization_seconds'), cap_seconds=900, cap_pass=cap_ok,
            projected_remaining_recomputed=projection, projection_cap_seconds=3300,
            recorded_projection=run.get('timing_projection')),
        stage_a_pass_recomputed=stage_pass, recorded_summary=saved,
        verdict_agrees=dict(screen=screen == saved.get('screen_pass'),
            stage_a=stage_pass == saved.get('stage_a_pass')),
        issues=issues, interpretation='Exploratory two-source image-domain development selection. '
            'Unavailable slots remain planned failures. BCH availability and semantic read are distinct. '
            'Observed repeated-source negatives do not calibrate FPR. No T4/T5, M1a, M1b, '
            'independent design-family count, held-out claim or latent-method claim follows.')


def report(stats):
    c, t = stats['screen_counts'], stats['timing']
    lines = ['# E1 Stage A descriptive analysis', '',
        f"Run outcome: {stats['outcome']}; qualification: {stats['qualification']}.",
        f"Screen: {stats['screen_pass_recomputed']}; Stage A: {stats['stage_a_pass_recomputed']}.",
        f"Recorded verdict agreement: {stats['verdict_agrees']}.", '',
        f"Sources completed {c['completed_sources']}/2; strict clean quality {c['strict_clean_quality']}/2; "
        f"clean q/h/both {c['clean_exact_q_h_both_match']}/2; initial qualification {c['valid_initializers']}/2.",
        f"Joint fixed q: {c['joint_fixed_q']}. Negatives: {c['negative_any_detections']} detections "
        f"in {c['completed_negative_calls']}/12 completed calls.", '',
        '| Source | Status | Condition | Read | Exact q | Joint q/content | q errors | Raw coded errors |',
        '|---|---|---|---|---|---|---|---|']
    for s in stats['sources']:
        for condition, value in s['conditions'].items():
            e = value['endpoints'] or {}
            lines.append(f"| {s['source_id']} | {s['status']} | {condition} | " +
                ' | '.join(str(e.get(k, 'missing')) for k in ('R', 'Q', 'J', 'q_bit_errors', 'raw_coded_bit_errors')) + ' |')
    lines += ['', f"Official conditional T3: {stats['t3']['status']}; "
        f"{stats['t3']['observed_image_rows']}/24 rows; recomputed pass {stats['t3']['pass_recomputed']}."]
    for strength, value in stats['t3']['strengths'].items():
        lines.append(f"T3 {strength}: S/Q/J {value['successes']}/6; count pass {value['count_pass']}; preservation {value['preservation_pass']}.")
    lines += [f"T3 negatives: {stats['t3']['negative_any_detections']} detections in "
        f"{stats['t3']['observed_negative_calls']}/24 completed calls (conditional plan).", '',
        f"Duration {t['duration_seconds']} s; 900 s cap pass {t['cap_pass']}. "
        f"Projected remaining {t['projected_remaining_recomputed']} s against 3300 s.",
        f"Raw error histogram: {stats['error_histograms']['raw_coded_bit_errors']}; "
        f"decoded q error histogram: {stats['error_histograms']['q_bit_errors']}.", '',
        stats['interpretation'], 'Full call scalar endpoints, partial rows, missing values, comparator lost/gained identities and recorded verdicts are retained in stats.json.']
    if stats['issues']:
        lines += ['', 'Record issues: ' + '; '.join(stats['issues'])]
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', required=True, type=Path)
    parser.add_argument('--output-dir', required=True, type=Path)
    args = parser.parse_args()
    stats = analyze(args.run_dir.resolve())
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / 'stats.json').write_text(json.dumps(stats, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    (args.output_dir / 'report.md').write_text(report(stats), encoding='utf-8')


if __name__ == '__main__':
    main()
