"""CPU-only independent descriptive analysis of the finalized E2 cached screen.

Reads recorded detector calls; never imports science code, executes a detector,
fits thresholds, inspects pixels or promotes an official lifecycle gate.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess
import sys

from journal_bch_analysis import ALPHA, BETA, CONDITIONS, encode, endpoint, read_json, strict_quality

IDS = (147498, 6012, 1675, 4795, 25394, 80932, 109798, 134882,
       177015, 190676, 468505, 499768)
ROOT = Path(__file__).resolve().parents[1]


def rows_at(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8-sig').splitlines()
            if line.strip()] if path.exists() else []


def analyze(run_dir):
    run = read_json(run_dir / 'run.json')
    if (not run or run.get('outcome') == 'running' or
            run.get('qualification') in (None, 'pending', 'pending_finalization')):
        raise ValueError('Analysis requires finalized E2 run.json')
    if run.get('schema') != 'journal-e2-bch-attenuation-stage-a-v1':
        raise ValueError('Expected E2 attenuation cached-screen schema')
    rows = rows_at(run_dir / 'rows.jsonl')
    ancestry = run.get('ancestry', {})
    parent_path = Path(ancestry['stage_b_run_json']) if ancestry.get('stage_b_run_json') else None
    parent_rows_path = Path(ancestry['stage_b_rows_jsonl']) if ancestry.get('stage_b_rows_jsonl') else None
    parent = read_json(parent_path, {}) if parent_path else {}
    parent_rows = rows_at(parent_rows_path) if parent_rows_path else []
    issues, discrepancies, sources, calls, comparison = [], [], [], [], []

    def checked(call, payload, label, required=True):
        if call is None:
            if required:
                issues.append(label + ': missing full call')
            return None
        try:
            return endpoint(call, payload)
        except (KeyError, TypeError, ValueError) as error:
            issues.append(label + ': invalid full call: ' + str(error))
            return None

    def compare_value(label, saved, actual):
        if saved != actual:
            discrepancies.append(dict(identity=label, recorded=saved, recomputed=actual))

    for sid in IDS:
        matching = [r for r in rows if r.get('source_id') == sid]
        if len(matching) != 1:
            issues.append(f'Source {sid}: expected one row, observed {len(matching)}')
        row = matching[0] if len(matching) == 1 else {}
        payload = row.get('payload', {})
        if not all(isinstance(payload.get(k), str) and payload[k] for k in ('q', 'h')):
            issues.append(f'Source {sid}: missing fixed q/h targets')
        source = dict(source_id=sid, status=row.get('status', 'missing'),
            error=row.get('error', row.get('reason')), payload=payload,
            source_image=row.get('source_image'), start_image=row.get('start_image'),
            final_state_image=row.get('final_state_image'), writer_ancestry=row.get('writer_ancestry'),
            timings={k: row.get(k) for k in ('construction_seconds', 'vae_negative_seconds', 'duration_seconds')},
            conditions={})
        old_rows = [r for r in parent_rows if r.get('source_id') == sid]
        old = old_rows[0] if len(old_rows) == 1 else {}
        if len(old_rows) != 1 or old.get('status') != 'ok':
            issues.append(f'E1 B source {sid}: missing, duplicate or failed comparator')
        if payload != old.get('payload'):
            issues.append(f'Source {sid}: E1 fixed target payload mismatch')
        source_comparison = dict(source_id=sid, conditions={})
        for condition in CONDITIONS:
            cell = row.get('conditions', {}).get(condition, {})
            label = f'{sid}/{condition}'
            if set(cell.get('calls', {})) - {ALPHA, BETA}:
                issues.append(label + ': unexpected detector owners')
            endpoints = {}
            for arm, owner, call in (
                    ('C1', ALPHA, cell.get('calls', {}).get(ALPHA)),
                    ('wrong_owner', BETA, cell.get('calls', {}).get(BETA)),
                    ('C0', ALPHA, cell.get('c0_call'))):
                e = checked(call, payload if arm == 'C1' else None, label + '/' + arm)
                endpoints[arm] = e
                if e is not None:
                    calls.append(dict(source_id=sid, condition=condition, arm=arm, endpoints=e))
                    compare_value(label + '/' + arm + '/watermark_found', call.get('watermark_found'), e['A'])
            e = endpoints['C1']
            if e is not None:
                delivery = cell.get('delivery', {})
                for field, actual in dict(semantic_exact=e['Q'], both_exact=bool(e['Q'] and e['H']),
                        q_bit_errors=e['q_bit_errors'], h_bit_errors=e['h_bit_errors']).items():
                    compare_value(label + '/delivery/' + field, delivery.get(field), actual)
                compare_value(label + '/joint_fixed_q', cell.get('joint_fixed_q'), bool(e['J'] and e['S']))
                diagnostic = cell.get('coded_diagnostics', {})
                for field, actual in dict(raw_coded_errors=e['raw_coded_bit_errors'],
                        decoded_q_errors=e['q_bit_errors'], raw_coded_word=e['raw_coded_word'],
                        decoded_q_available=e['decoded_q_available'], semantic_read=e['R']).items():
                    compare_value(label + '/coded_diagnostics/' + field, diagnostic.get(field), actual)
                if payload.get('q'):
                    compare_value(label + '/intended_coded_word', diagnostic.get('intended_coded_word'),
                                  f"{encode(payload['q']):015x}")
            value = dict(status=cell.get('status', 'missing'), error=cell.get('error', cell.get('reason')),
                image=cell.get('image'), c0_image=cell.get('c0_image'), endpoints=e,
                negative_endpoints={arm: None if endpoints[arm] is None else
                    {k: endpoints[arm][k] for k in ('A', 'S', 'R', 'F', 'outcome')}
                    for arm in ('C0', 'wrong_owner')},
                full_calls_complete=all(v is not None for v in endpoints.values()),
                quality_source=cell.get('quality_source'), quality_input=cell.get('quality_input'),
                strict_quality=strict_quality(cell.get('quality_source')))
            source['conditions'][condition] = value
            old_cell = old.get('conditions', {}).get(condition, {})
            oe = checked(old_cell.get('calls', {}).get(ALPHA), old.get('payload', {}),
                         'E1 B/' + label)
            oj = bool(oe and oe['J'] and oe['S']) if oe is not None else None
            nj = bool(e and e['J'] and e['S']) if e is not None else None
            source_comparison['conditions'][condition] = dict(e1_J=oj, e2_J=nj,
                lost_e1_J=bool(oj and not nj), gained_J=bool(oj is False and nj),
                e1_quality=old_cell.get('quality_source'), e2_quality=value['quality_source'],
                e1_strict_quality=strict_quality(old_cell.get('quality_source')),
                e2_strict_quality=value['strict_quality'],
                metric_delta={k: (value['quality_source'][k] - old_cell['quality_source'][k])
                    if isinstance((value['quality_source'] or {}).get(k), (int, float)) and
                       isinstance((old_cell.get('quality_source') or {}).get(k), (int, float)) else None
                    for k in ('psnr_db', 'ssim_rgb', 'lpips')})
        source['complete'] = bool(source['status'] == 'ok' and
            set(row.get('conditions', {})) == set(CONDITIONS) and
            all(c['status'] == 'ok' and c['full_calls_complete'] for c in source['conditions'].values()))
        sources.append(source)
        comparison.append(source_comparison)

    extra = [r.get('source_id') for r in rows if r.get('source_id') not in IDS]
    if extra:
        issues.append(f'Unexpected source rows: {extra}')
    if [r.get('source_id') for r in rows] != list(IDS):
        issues.append('Recorded rows differ from frozen twelve-source order/inventory')
    parent_complete = bool(parent.get('schema') == 'journal-e1-bch-stage-b-v1' and
        parent.get('outcome') == 'completed' and len(parent_rows) == 12 and
        {r.get('source_id') for r in parent_rows} == set(IDS))
    if not parent_complete:
        issues.append('E1 B comparator inventory is not complete finalized development evidence')
    targets = [c for c in calls if c['arm'] == 'C1']
    negatives = [c for c in calls if c['arm'] != 'C1']
    clean = [s['conditions']['clean'] for s in sources]
    counts = dict(planned_sources=12, completed=sum(s['complete'] for s in sources),
        missing_or_failed=sum(not s['complete'] for s in sources),
        planned_condition_cells=36,
        completed_condition_cells=sum(c['status'] == 'ok' and c['full_calls_complete']
            for s in sources for c in s['conditions'].values()),
        strict_clean_quality=sum(c['strict_quality'] for c in clean),
        clean_exact_q=sum(bool(c['endpoints'] and c['endpoints']['Q']) for c in clean),
        clean_exact_h=sum(bool(c['endpoints'] and c['endpoints']['H']) for c in clean),
        clean_exact_q_h_both_match=sum(bool(c['endpoints'] and c['endpoints']['Q'] and
            c['endpoints']['H'] and c['endpoints']['F']) for c in clean),
        planned_full_calls=108, completed_full_calls=len(calls),
        planned_negative_calls=72, completed_negative_calls=len(negatives))
    counts['all_source_cells_complete'] = len(rows) == 12 and counts['completed'] == 12 and not extra
    counts['endpoints_by_condition'] = {b: {k: sum(bool(c['endpoints'][k]) for c in targets
        if c['condition'] == b) for k in ('S', 'Q', 'J', 'H', 'F')} for b in CONDITIONS}
    counts['joint_fixed_q'] = {b: sum(bool(c['endpoints']['J'] and c['endpoints']['S'])
        for c in targets if c['condition'] == b) for b in CONDITIONS}
    counts['negative_by_arm'] = {arm: dict(planned=36, completed=sum(c['arm'] == arm for c in negatives),
        any_detections=sum(c['endpoints']['A'] for c in negatives if c['arm'] == arm))
        for arm in ('C0', 'wrong_owner')}
    counts['c0_any'] = counts['negative_by_arm']['C0']['any_detections']
    counts['wrong_owner_any'] = counts['negative_by_arm']['wrong_owner']['any_detections']
    histograms = {}
    for condition in CONDITIONS:
        es = [c['endpoints'] for c in targets if c['condition'] == condition]
        histograms[condition] = {k: dict(histogram=dict(sorted(Counter(str(e[k])
            for e in es if e[k] is not None).items())), available=sum(e[k] is not None for e in es),
            unknown_or_missing=12-sum(e[k] is not None for e in es))
            for k in ('raw_coded_bit_errors', 'q_bit_errors', 'h_bit_errors')}
        histograms[condition]['valid_exact_code_corrections'] = sum(bool(
            e['bch_success'] and e['q_bit_errors'] == 0 and e['raw_coded_bit_errors'] is not None
            and 0 < e['raw_coded_bit_errors'] <= 5) for e in es)
        histograms[condition]['exact_read_q_corrections'] = sum(bool(e['Q'] and
            e['bch_success'] and e['raw_coded_bit_errors'] is not None and
            0 < e['raw_coded_bit_errors'] <= 5) for e in es)
    lost = [dict(source_id=s['source_id'], condition=b) for s in comparison
        for b, c in s['conditions'].items() if c['lost_e1_J']]
    old_positive = sum(c['e1_J'] is True for s in comparison for c in s['conditions'].values())
    comparison_available = sum(c['e1_J'] is not None for s in comparison for c in s['conditions'].values())
    preservation = dict(planned=36, comparator_available=comparison_available,
        e1_positive_count=old_positive, lost=lost, all_e1_J_preserved=
        bool(parent_complete and comparison_available == 36 and not lost), sources=comparison)
    screen = bool(not issues and not discrepancies and counts['all_source_cells_complete'] and
        all(counts[k] == 12 for k in ('strict_clean_quality', 'clean_exact_q', 'clean_exact_h',
                                    'clean_exact_q_h_both_match')) and
        counts['joint_fixed_q']['sd15_vae'] == counts['joint_fixed_q']['sdxl_vae'] == 12 and
        len(calls) == 108 and len(negatives) == 72 and not counts['c0_any'] and not counts['wrong_owner_any'])
    wall = read_json(run_dir / 'parent-wall.json', {})
    duration, inclusive = run.get('duration_seconds'), wall.get('duration_seconds')
    peak = run.get('peak_allocated_bytes')
    memory_ok = isinstance(peak, (int, float)) and 0 < peak <= 10 * 1024**3
    cap_ok = isinstance(inclusive, (int, float)) and 0 <= inclusive <= 300
    process_cap_ok = isinstance(duration, (int, float)) and 0 <= duration <= 300
    if inclusive is None:
        issues.append('Missing finalized parent-wall.json inclusive duration; cap unknown')
    stage_pass = bool(screen and run.get('outcome') == 'completed' and cap_ok and process_cap_ok and
        memory_ok and wall.get('exit_code') == 0 and not run.get('budget_overrun', False))
    saved = run.get('summary', {})
    compare_value('summary.json versus run.json summary', read_json(run_dir / 'summary.json'), saved)
    for key, actual in counts.items():
        if key in saved:
            compare_value('summary/' + key, saved[key], actual)
    compare_value('summary/screen_pass', saved.get('screen_pass'), screen)
    compare_value('summary/stage_a_pass', saved.get('stage_a_pass'), stage_pass)
    return dict(schema='journal-e2-bch-attenuation-analysis-v1',
        provenance=dict(run_dir=str(run_dir), run_json=str(run_dir / 'run.json'),
            rows_jsonl=str(run_dir / 'rows.jsonl'), parent_wall_json=str(run_dir / 'parent-wall.json'),
            summary_json=str(run_dir / 'summary.json'), analysis_command=sys.argv,
            run_commit=run.get('commit'), analysis_commit=subprocess.check_output(
                ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            analysis_script=str(Path(__file__).resolve()), command=run.get('command'),
            e1_run_json=str(parent_path) if parent_path else None,
            e1_rows_jsonl=str(parent_rows_path) if parent_rows_path else None,
            e1_commit=parent.get('commit'), config=run.get('config'),
            data_split=run.get('data_split'), usd=run.get('usd')),
        outcome=run.get('outcome'), qualification=run.get('qualification'), sources=sources,
        screen_counts=counts, screen_pass_recomputed=screen, stage_a_pass_recomputed=stage_pass,
        e1_preservation=preservation, error_histograms=histograms,
        timing=dict(duration_seconds=duration, parent_inclusive_seconds=inclusive,
            parent_exit_code=wall.get('exit_code'),
            cap_seconds=300, parent_cap_pass=cap_ok, process_cap_pass=process_cap_ok,
            peak_allocated_bytes=peak, peak_cap_bytes=10 * 1024**3, memory_cap_pass=memory_ok),
        recorded_summary=saved, discrepancies=discrepancies, issues=issues,
        interpretation='Exploratory same-twelve image-domain cached clean/VAE screen. '
            'No initializer qualification or feasible-ball requirement applies to E2. '
            'Exact q compares with original recorded q; exact h with frozen operational E1 h. '
            'Missing/failed slots remain in all planned denominators; unknown errors remain null. '
            'Fresh 36 C0 and 36 wrong-owner calls reuse the twelve sources and retained matched C0 pixels; '
            'zero observations do not calibrate population FPR. No T3 generalization, M1a, M1b, '
            'T4/T5 preservation, independent design-family passage or latent-method claim follows.')


def report(stats):
    counts, timing, provenance = stats['screen_counts'], stats['timing'], stats['provenance']
    lines = ['# E2 fixed attenuation cached-screen analysis', '',
        f"Outcome {stats['outcome']}; recorded qualification {stats['qualification']}.",
        f"Recomputed scientific screen {stats['screen_pass_recomputed']}; inclusive Stage A {stats['stage_a_pass_recomputed']}.",
        f"Complete sources {counts['completed']}/12; complete condition cells {counts['completed_condition_cells']}/36; "
        f"full calls {counts['completed_full_calls']}/108.",
        f"Strict clean quality {counts['strict_clean_quality']}/12; exact clean q {counts['clean_exact_q']}/12; "
        f"exact operational h {counts['clean_exact_h']}/12; exact q/h/both_match {counts['clean_exact_q_h_both_match']}/12.",
        f"Joint fixed-q/content/read/found counts: {counts['joint_fixed_q']}; each denominator is 12.",
        f"Separate intended-owner endpoint counts S/Q/J/H/full: {counts['endpoints_by_condition']}.",
        f"Negative calls {counts['completed_negative_calls']}/72: {counts['negative_by_arm']}.", '',
        '| Source | Status | Condition | S | Q | J | H | Full | Raw 59 errors | q errors | h errors |',
        '|---|---|---|---|---|---|---|---|---|---|---|']
    for source in stats['sources']:
        for condition, cell in source['conditions'].items():
            e = cell['endpoints'] or {}
            lines.append(f"| {source['source_id']} | {cell['status']} | {condition} | " +
                ' | '.join(str(e.get(k)) for k in ('S', 'Q', 'J', 'H', 'F',
                    'raw_coded_bit_errors', 'q_bit_errors', 'h_bit_errors')) + ' |')
    lines += ['', '| Source | E1 strict clean | E2 strict clean | E1 LPIPS | E2 LPIPS | E2 PSNR | E2 SSIM |',
        '|---|---|---|---|---|---|---|']
    for source in stats['e1_preservation']['sources']:
        c = source['conditions']['clean']
        old, new = c['e1_quality'] or {}, c['e2_quality'] or {}
        lines.append(f"| {source['source_id']} | {c['e1_strict_quality']} | {c['e2_strict_quality']} | "
            f"{old.get('lpips')} | {new.get('lpips')} | {new.get('psnr_db')} | {new.get('ssim_rgb')} |")
    p = stats['e1_preservation']
    lines += ['', f"E1 J comparator available {p['comparator_available']}/36; E1 positives {p['e1_positive_count']}; "
        f"all preserved {p['all_e1_J_preserved']}; lost identities {p['lost']}.",
        f"Process duration {timing['duration_seconds']} s; parent inclusive duration {timing['parent_inclusive_seconds']} s; "
        f"300 s cap passes: parent {timing['parent_cap_pass']}, process {timing['process_cap_pass']}.",
        f"Peak allocated GPU {timing['peak_allocated_bytes']} bytes; 10 GiB cap pass {timing['memory_cap_pass']}.", '',
        'Raw/decoded error histograms (unknown/missing slots explicitly counted):']
    for condition, histogram in stats['error_histograms'].items():
        lines.append(f'{condition}: {json.dumps(histogram, sort_keys=True)}')
    lines += ['', stats['interpretation'], '',
        f"Run code commit: {provenance['run_commit']}; analysis code commit: {provenance['analysis_commit']}.",
        f"E1 B code commit: {provenance['e1_commit']}.",
        f"Raw run: {provenance['run_json']}", f"Raw calls: {provenance['rows_jsonl']}",
        f"Inclusive wall: {provenance['parent_wall_json']}",
        f"E1 raw run: {provenance['e1_run_json']}", f"E1 raw calls: {provenance['e1_rows_jsonl']}",
        'Source image paths, fixed targets, errors, endpoint scalars, condition quality metrics, '
        'source-level E1 comparison and discrepancy details are in stats.json.',
        f"Issues: {json.dumps(stats['issues'])}", f"Discrepancies: {json.dumps(stats['discrepancies'])}"]
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
