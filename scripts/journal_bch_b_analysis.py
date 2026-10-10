"""Independent stdlib analysis of finalized E1 Stage B clean/VAE evidence."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess

from journal_bch_analysis import ALPHA, BETA, CONDITIONS, endpoint, read_json, read_rows, strict_quality

IDS = (1675, 4795, 6012, 25394, 80932, 109798, 134882, 147498,
       177015, 190676, 468505, 499768)
INHERITED = (1675, 499768)


def analyze(run_dir):
    run = read_json(run_dir / 'run.json')
    if (not run or run.get('outcome') == 'running' or
            run.get('qualification') in (None, 'pending', 'pending_finalization')):
        raise ValueError('Analysis requires a finalized run.json; run is absent or unfinished')
    if run.get('schema') != 'journal-e1-bch-stage-b-v1' or run.get('stage') != 'B':
        raise ValueError('Expected E1 Stage B schema')
    rows = read_rows(run_dir / 'rows.jsonl')
    issues, sources, calls, negatives = [], [], [], []
    expected_slots = []

    def checked(call, payload, label):
        if call is None:
            issues.append(label + ': missing full call')
            return None
        try:
            return endpoint(call, payload)
        except (KeyError, TypeError, ValueError) as error:
            issues.append(label + ': invalid full call: ' + str(error))
            return None

    for sid in IDS:
        matches = [r for r in rows if r.get('source_id') == sid]
        if len(matches) != 1:
            issues.append(f'Source {sid}: expected one row, observed {len(matches)}')
        r = matches[0] if len(matches) == 1 else {}
        payload = r.get('payload', {})
        if set(payload) < {'q', 'h'} or not all(payload.get(k) for k in ('q', 'h')):
            issues.append(f'Source {sid}: missing target payload')
        s = dict(source_id=sid, status=r.get('status', 'missing'),
                 error=r.get('error', r.get('reason')), inherited='inherited_provenance' in r,
                 inherited_provenance=r.get('inherited_provenance'), conditions={})
        if s['inherited'] != (sid in INHERITED):
            issues.append(f'Source {sid}: inherited provenance mismatch')
        initial = r.get('initial_qualification', {})
        ie = checked(initial.get('call'), payload, f'{sid} initializer')
        s['initializer'] = dict(endpoints=ie, quality=initial.get('metrics'),
            qualified=bool(ie and ie['Q'] and ie['H'] and ie['F'] and
                           strict_quality(initial.get('metrics')) and
                           r.get('initial_balls', {}).get('feasible') is True))
        s['final_feasible'] = r.get('final_balls', {}).get('feasible') is True
        for condition in CONDITIONS:
            c = r.get('conditions', {}).get(condition, {})
            full = {}
            for arm, owner, call in (
                    ('C1', ALPHA, c.get('calls', {}).get(ALPHA)),
                    ('wrong_owner', BETA, c.get('calls', {}).get(BETA)),
                    ('C0', ALPHA, c.get('c0_call'))):
                e = checked(call, payload if arm == 'C1' else None,
                            f'{sid}/{condition}/{arm}')
                slot = dict(source_id=sid, condition=condition, arm=arm,
                            owner=owner, inherited=s['inherited'], available=e is not None,
                            endpoints=e)
                expected_slots.append(slot)
                full[arm] = e
                if e is not None:
                    calls.append(slot)
                    if arm != 'C1':
                        negatives.append(slot)
            s['conditions'][condition] = dict(endpoints=full['C1'],
                full_calls_complete=all(e is not None for e in full.values()),
                quality=c.get('quality_source'), strict_quality=strict_quality(c.get('quality_source')))
        s['complete'] = bool(s['status'] == 'ok' and
            set(r.get('conditions', {})) == set(CONDITIONS) and
            all(c['full_calls_complete'] for c in s['conditions'].values()))
        sources.append(s)
    extras = [r.get('source_id') for r in rows if r.get('source_id') not in IDS]
    if extras:
        issues.append(f'Unexpected source rows: {extras}')
    clean = [s['conditions']['clean'] for s in sources]
    counts = dict(planned_sources=12, completed=sum(s['complete'] for s in sources),
        missing_or_failed=sum(not s['complete'] for s in sources),
        strict_clean_quality=sum(c['strict_quality'] for c in clean),
        clean_exact_q_h_both_match=sum(bool(c['endpoints'] and c['endpoints']['Q'] and
            c['endpoints']['H'] and c['endpoints']['F']) for c in clean),
        valid_initializers=sum(s['initializer']['qualified'] for s in sources),
        final_feasible=sum(s['final_feasible'] for s in sources),
        joint_fixed_q={b:sum(bool(s['conditions'][b]['endpoints'] and
            s['conditions'][b]['endpoints']['J'] and s['conditions'][b]['endpoints']['S'])
            for s in sources) for b in CONDITIONS},
        planned_full_calls=108, completed_full_calls=len(calls),
        planned_negative_calls=72, completed_negative_calls=len(negatives),
        inherited_sources=sum(s['inherited'] for s in sources),
        inherited_full_calls=sum(c['inherited'] for c in calls),
        inherited_negative_calls=sum(c['inherited'] for c in negatives))
    counts['all_source_cells_complete'] = (len(rows) == 12 and counts['completed'] == 12 and not extras)
    counts['negative_by_arm'] = {arm:dict(planned=36,
        completed=sum(c['arm'] == arm for c in negatives),
        any_detections=sum(c['endpoints']['A'] for c in negatives if c['arm'] == arm))
        for arm in ('C0', 'wrong_owner')}
    counts['c0_any'] = counts['negative_by_arm']['C0']['any_detections']
    counts['wrong_owner_any'] = counts['negative_by_arm']['wrong_owner']['any_detections']

    d2_path = Path(run['d2_c0_source']) if run.get('d2_c0_source') else None
    d2_rows = read_rows(d2_path) if d2_path else []
    positives, lost, d2_missing = [], [], []
    for sid in IDS:
        matches = [r for r in d2_rows if r.get('source_id') == sid]
        r = matches[0] if len(matches) == 1 else {}
        if r.get('status') != 'ok' or set(r.get('conditions', {})) != set(CONDITIONS):
            d2_missing.append(dict(source_id=sid, reason='D2 row missing, duplicate, failed or incomplete'))
        for b in ('sd15_vae', 'sdxl_vae'):
            call = r.get('conditions', {}).get(b, {}).get('calls', {}).get(ALPHA)
            try:
                e = endpoint(call, r.get('payload', {})) if call else None
            except (KeyError, TypeError, ValueError):
                e = None
            if e is None or e['Q'] is None:
                d2_missing.append(dict(source_id=sid, condition=b, reason='D2 full target call or payload unavailable'))
            elif e['J'] and e['S']:
                identity = dict(source_id=sid, condition=b)
                positives.append(identity)
                target = next(s for s in sources if s['source_id'] == sid)['conditions'][b]['endpoints']
                if not (target and target['J'] and target['S']):
                    lost.append(identity)
    d2_complete = bool(len(d2_rows) == 12 and {r.get('source_id') for r in d2_rows} == set(IDS) and not d2_missing)
    counts.update(d2_vae_comparison_complete=d2_complete, d2_vae_positive_count=len(positives),
                  lost_d2_positive_vae_identities=lost)
    evidence_pass = bool(not issues and counts['all_source_cells_complete'] and d2_complete and
        all(counts[k] == 12 for k in ('strict_clean_quality', 'clean_exact_q_h_both_match',
                                    'valid_initializers', 'final_feasible')) and
        counts['joint_fixed_q']['sd15_vae'] == 12 and counts['joint_fixed_q']['sdxl_vae'] >= 11 and
        not lost and len(negatives) == 72 and not counts['c0_any'] and not counts['wrong_owner_any'])
    wall = read_json(run_dir / 'parent-wall.json', {})
    inclusive = wall.get('duration_seconds')
    memory = run.get('peak_allocated_bytes')
    memory_ok = isinstance(memory, (int, float)) and 0 < memory <= 10 * 1024**3
    cap_ok = isinstance(inclusive, (int, float)) and 0 <= inclusive <= 3300
    if inclusive is None:
        issues.append('Missing finalized parent-wall duration; inclusive cap is unknown')
    stage_pass = bool(evidence_pass and run.get('outcome') == 'completed' and cap_ok and memory_ok
                      and not run.get('budget_overrun', False))
    histograms = {}
    for b in CONDITIONS:
        target = [c['endpoints'] for c in calls if c['arm'] == 'C1' and c['condition'] == b]
        histograms[b] = {name:dict(histogram=dict(sorted(Counter(str(e[name]) for e in target
            if e[name] is not None).items())), available=sum(e[name] is not None for e in target),
            unknown_or_missing=12-sum(e[name] is not None for e in target))
            for name in ('raw_coded_bit_errors', 'q_bit_errors')}
        histograms[b]['exact_q_corrections'] = sum(bool(e['Q'] and e['raw_coded_bit_errors'] is not None
                                                       and e['raw_coded_bit_errors'] > 0) for e in target)
    ranges = {}
    for b in CONDITIONS:
        ranges[b] = {}
        for metric in ('psnr_db', 'ssim_rgb', 'lpips'):
            values = [s['conditions'][b]['quality'].get(metric) for s in sources
                      if s['conditions'][b]['quality']]
            finite = [v for v in values if isinstance(v, (int, float))]
            ranges[b][metric] = dict(min=min(finite) if finite else None,
                max=max(finite) if finite else None, numeric_count=len(finite),
                unknown_or_nonnumeric=12-len(finite))
        ranges[b]['infinite_psnr_count'] = sum(bool((s['conditions'][b]['quality'] or {}).get('psnr_infinite')) for s in sources)
    saved = run.get('summary', {})
    try:
        analysis_commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'],
            cwd=Path(__file__).resolve().parents[1], text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        analysis_commit = None
    return dict(schema='journal-e1-bch-stage-b-analysis-v1', run_dir=str(run_dir),
        run_commit=run.get('commit'), analysis_commit=analysis_commit, analysis_script=str(Path(__file__).resolve()),
        outcome=run.get('outcome'), qualification=run.get('qualification'), counts=counts,
        sources=sources, calls=calls, unavailable_calls=[c for c in expected_slots if not c['available']],
        d2=dict(path=str(d2_path) if d2_path else None, positives=positives, unavailable=d2_missing),
        timing=dict(run_duration_seconds=run.get('duration_seconds'), parent_inclusive_seconds=inclusive,
                    inclusive_cap_seconds=3300, inclusive_cap_pass=cap_ok,
                    peak_allocated_bytes=memory, memory_cap_bytes=10*1024**3, memory_cap_pass=memory_ok),
        error_histograms=histograms, quality_ranges=ranges, stage_b_evidence_pass_recomputed=evidence_pass,
        stage_b_pass_recomputed=stage_pass, recorded_summary=saved,
        verdict_agrees=dict(evidence=evidence_pass == saved.get('stage_b_evidence_pass'),
                           stage_b=stage_pass == saved.get('stage_b_pass')),
        issues=issues, interpretation='Exploratory twelve-source clean/VAE prerequisite only; '
        'two inherited Stage A sources and ten new sources. Source failures remain in denominators. '
        'B passage requires Stage C and T4/T5 work before M1a; no new T3, M1a, T4 efficacy, '
        'calibrated FPR, latent-method or held-out claim follows. Null decoded words remain unknown.')


def report(stats):
    c = stats['counts']
    lines = ['# E1 Stage B descriptive analysis', '',
        f"Run commit: {stats['run_commit']}. Analysis commit: {stats['analysis_commit']}.", '',
        f"Evidence pass: {stats['stage_b_evidence_pass_recomputed']}; inclusive Stage B pass: "
        f"{stats['stage_b_pass_recomputed']}. Verdict agreement: {stats['verdict_agrees']}.", '',
        f"Complete sources {c['completed']}/12; strict clean quality {c['strict_clean_quality']}/12; "
        f"clean exact q/h/both {c['clean_exact_q_h_both_match']}/12; valid initializers "
        f"{c['valid_initializers']}/12; feasible finals {c['final_feasible']}/12.", '',
        f"Joint exact q: {c['joint_fixed_q']}. D2 positives {c['d2_vae_positive_count']}; "
        f"lost identities {c['lost_d2_positive_vae_identities']}.", '',
        f"Negative calls {c['completed_negative_calls']}/72, including "
        f"{c['inherited_negative_calls']} inherited calls; arms: {c['negative_by_arm']}.", '',
        f"Timing and memory: {stats['timing']}.", '',
        '| Source | Inherited | Status | Strict clean | Q/H/F clean | SD1.5 J/S | SDXL J/S |',
        '|---|---|---|---|---|---|---|']
    for s in stats['sources']:
        es = [s['conditions'][b]['endpoints'] for b in CONDITIONS]
        clean = '/'.join(str(es[0][k]) for k in ('Q', 'H', 'F')) if es[0] else 'unavailable'
        joints = ['/'.join(str(e[k]) for k in ('J', 'S')) if e else 'unavailable' for e in es[1:]]
        lines.append(f"| {s['source_id']} | {s['inherited']} | {s['status']} | "
            f"{s['conditions']['clean']['strict_quality']} | {clean} | {joints[0]} | {joints[1]} |")
    for title, value in [('Quality ranges', stats['quality_ranges']),
                         ('Raw 59-bit and decoded q error histograms by condition', stats['error_histograms']),
                         ('Failed or incomplete sources', [s for s in stats['sources'] if not s['complete']]),
                         ('Unavailable full calls', stats['unavailable_calls']),
                         ('Unavailable D2 evidence', stats['d2']['unavailable']), ('Issues', stats['issues'])]:
        lines += ['', title + ':', '', '```json', json.dumps(value, indent=2), '```']
    return '\n'.join(lines + ['', stats['interpretation'], ''])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    stats = analyze(args.run_dir.resolve())
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / 'stats.json').write_text(json.dumps(stats, indent=2) + '\n', encoding='utf-8')
    (args.output_dir / 'report.md').write_text(report(stats), encoding='utf-8')


if __name__ == '__main__':
    main()
