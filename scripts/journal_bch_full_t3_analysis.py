"""Final-run-only, standard-library descriptive analysis of E3 full T3."""
from __future__ import annotations

import argparse
from collections import Counter
import json
import math
from pathlib import Path
import subprocess

from journal_bch_analysis import ALPHA, BETA, endpoint, read_json, read_rows

IDS = (1675, 4795, 6012, 25394, 80932, 109798, 134882, 147498,
       177015, 190676, 468505, 499768)
STRENGTHS = (.1, .2)
METRICS = ('S', 'Q', 'J')


def identity(row):
    return int(row['source_id']), float(row['strength']), int(row['seed'])


def label(key):
    return f'{key[0]}|{key[1]}|{key[2]}'


def quality(metrics):
    def finite(value):
        return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
    return bool(metrics and (metrics.get('psnr_infinite') is True or
        finite(metrics.get('psnr_db')) and metrics['psnr_db'] > 35) and
        finite(metrics.get('ssim_rgb')) and metrics['ssim_rgb'] > .9 and
        finite(metrics.get('lpips')) and metrics['lpips'] < .1)


def histogram(values):
    values = list(values)
    return dict(observed=sum(v is not None for v in values), null=sum(v is None for v in values),
                frequencies=dict(sorted(Counter(str(v) for v in values if v is not None).items())))


def analyze(folder):
    run = read_json(folder / 'run.json')
    if (not run or run.get('outcome') not in ('completed', 'failed') or
        run.get('qualification') in (None, 'pending', 'pending_finalization') or
        run.get('schema') != 'journal-e3-bch-quality-select-stage-b-v1'):
        raise ValueError('Requires final E3 Stage B run.json; no running-run analysis')
    saved = read_json(folder / 'summary.json')
    if not saved or saved != run.get('summary'):
        raise ValueError('Final run and summary records differ')
    issues, metadata_issues = [], []
    if run.get('method') != 'E3-BCH59-Q080':
        metadata_issues.append('Scientific CLI comparator loop overwrote method label: ' + str(run.get('method')))
    if (run.get('config', {}).get('quality_rule') != 'retain_if_strict_else_contract_once' or
        run.get('config', {}).get('factor') != .8 or run.get('detector') != 'E1-BCH59-A' or
        run.get('inherited_full_calls') != 0 or run.get('inherited_image_rows') != 0):
        issues.append('E3 candidate configuration or fresh-call declaration differs')
    plan = [(sid, s, seed) for sid in IDS for s in STRENGTHS for seed in range(3)]
    expected = {(arm, k) for arm in ('candidate_C1', 'shared_C0') for k in plan}
    rows = read_rows(folder / 'rows.jsonl')
    actual = [(r['arm'], identity(r)) for r in rows]
    complete = len(actual) == 144 and set(actual) == expected
    if not complete:
        issues.append('Missing, extra or duplicate planned image identities')
    candidates, negatives, unavailable, operational, mismatches = {}, [], [], [], []
    calls = 0
    negative_by_arm = {}
    for row in rows:
        key, arm = identity(row), row['arm']
        owners = {ALPHA, BETA} if arm == 'candidate_C1' else {ALPHA}
        row_calls = row.get('calls', {})
        if row['status'] != 'ok':
            unavailable.append(dict(arm=arm, identity=label(key), status=row['status'], error=row.get('error')))
            if row['status'] != 'safety_blocked' or row_calls:
                operational.append(dict(arm=arm, identity=label(key), reason=row['status']))
        elif set(row_calls) != owners:
            operational.append(dict(arm=arm, identity=label(key), reason='missing or extra full calls'))
        for owner, call in row_calls.items():
            calls += 1
            target = row.get('payload') if arm == 'candidate_C1' and owner == ALPHA else None
            e = endpoint(call, target)
            if arm == 'candidate_C1' and owner == ALPHA:
                if row['status'] == 'ok':
                    candidates[key] = e
                if call.get('method') != 'E1-BCH59-A' or row.get('inherited_provenance'):
                    issues.append('Candidate decoder or fresh C1 provenance differs: '+label(key))
                for field, value in row.get('endpoints', {}).items():
                    if field not in e or e[field] != value:
                        mismatches.append(dict(identity=label(key), field=field, recorded=value, recomputed=e.get(field)))
            elif owner == (BETA if arm == 'candidate_C1' else ALPHA):
                negatives.append(dict(arm=arm, identity=label(key), any_detection=e['A']))
    for arm in ('shared_C0', 'candidate_C1'):
        observed = [n for n in negatives if n['arm'] == arm]
        negative_by_arm[arm] = dict(planned=72, observed=len(observed),
            detections=sum(n['any_detection'] for n in observed),
            unavailable=72-len(observed), safety_blocked=sum(r['arm'] == arm and
                r['status'] == 'safety_blocked' for r in rows))
    if mismatches:
        issues.append('Recorded candidate endpoint disagreement')
    comparisons = {}
    for item in saved.get('comparisons', []):
        fields = item['identity'].split('|')
        key = int(fields[0]), float(fields[1]), int(fields[2])
        if key in comparisons:
            issues.append('Duplicate frozen comparison identity')
        comparisons[key] = item
    if set(comparisons) != set(plan):
        issues.append('Incomplete frozen comparator dictionaries')
    strengths = {}
    for strength, minimum, fixed_n, v5_n in ((.1, 36, 29, 27), (.2, 31, 28, 18)):
        keys = [k for k in plan if k[1] == strength]
        counts = {m:sum(bool(candidates.get(k, {}).get(m)) for k in keys) for m in METRICS}
        retention = {}
        for method in ('D2', 'frozen_F5', 'E1_A'):
            known = [k for k in keys if method in comparisons.get(k, {})]
            expected_n = 6 if method == 'E1_A' else 36
            if len(known) != expected_n:
                issues.append(f'{strength} {method}: expected {expected_n} comparator entries')
            retention[method] = {}
            for metric in METRICS:
                old = [k for k in known if comparisons[k][method].get(metric)]
                retention[method][metric] = dict(old_positive=len(old),
                    lost=[label(k) for k in old if not candidates.get(k, {}).get(metric)],
                    gained=[label(k) for k in known if not comparisons[k][method].get(metric)
                            and candidates.get(k, {}).get(metric)])
        fixed = [tuple(k) for k in run.get('comparison_sets', {}).get(str(strength), {}).get('I', [])]
        fixed_valid = len(fixed) == len(set(fixed)) == fixed_n and set(fixed) <= set(keys)
        if not fixed_valid:
            issues.append(f'{strength}: invalid fixed v5 intersection')
        intersection = dict(fixed_identities=len(fixed), identities=[label(k) for k in fixed],
            candidate_S=sum(bool(candidates.get(k, {}).get('S')) for k in fixed),
            v5_S=v5_n, frozen_F5_S=fixed_n,
            baseline_scope='Frozen scientific-script fixed comparison; v5 27/29 and 18/28')
        per_source = {str(sid):{m:sum(bool(candidates.get((sid, strength, seed), {}).get(m))
            for seed in range(3)) for m in METRICS} for sid in IDS}
        values = [candidates[k] for k in keys if k in candidates]
        score_fields = sorted({field for e in values for field in e['channel_scalars']['semantic']
                               if 'score' in field or 'correlation' in field})
        scores = {}
        for field in score_fields:
            nums = [e['channel_scalars']['semantic'].get(field) for e in values]
            valid = [v for v in nums if isinstance(v, (float, int)) and not isinstance(v, bool) and math.isfinite(v)]
            scores[field] = dict(observed=len(valid), null_or_invalid=len(nums)-len(valid),
                                minimum=min(valid) if valid else None, maximum=max(valid) if valid else None)
        strengths[str(strength)] = dict(planned=36, observed=len(values), successes=counts,
            unavailable_candidate_slots=[dict(identity=label(k),
                reason=next((r['status'] for r in rows if r['arm'] == 'candidate_C1' and identity(r) == k), 'missing'),
                interpretation='Unsuccessful planned slot; not an observed decoding/content failure')
                for k in keys if k not in candidates],
            count_pass=counts['Q'] >= minimum and counts['J'] >= minimum,
            preservation_pass=all(not r['lost'] for m in retention.values() for r in m.values()),
            retention=retention, intersection=intersection,
            fixed_I_pass=fixed_valid and intersection['candidate_S'] == fixed_n,
            source_seed_successes=per_source,
            source_majority_descriptive={m:sum(v[m] >= 2 for v in per_source.values()) for m in METRICS},
            histograms={field:histogram(e[field] for e in values) for field in ('raw_coded_bit_errors', 'q_bit_errors')},
            algebraic_success=histogram(e['bch_success'] for e in values),
            algebraic_reasons=histogram(e['bch_reason'] for e in values), scores=scores,
            content_failures=[label(k) for k in keys if k in candidates and not candidates[k]['semantic_content_match']],
            failed_joint=[dict(identity=label(k), Q=candidates[k]['Q'], S=candidates[k]['S'],
                raw_errors=candidates[k]['raw_coded_bit_errors'], q_errors=candidates[k]['q_bit_errors'],
                bch_reason=candidates[k]['bch_reason'], semantic=candidates[k]['channel_scalars']['semantic'])
                for k in keys if k in candidates and not candidates[k]['J']])
        # All original aggregate endpoints are checked against full-call recomputation.
        recorded = saved.get('strengths', {}).get(str(strength), {})
        for field in ('successes', 'retention', 'count_pass', 'preservation_pass', 'fixed_I_pass'):
            if recorded.get(field) != strengths[str(strength)][field]:
                issues.append(f'{strength}: recorded {field} differs')
        for field in ('fixed_identities', 'identities', 'candidate_S', 'v5_S', 'frozen_F5_S'):
            if recorded.get('intersection', {}).get(field) != intersection[field]:
                issues.append(f'{strength}: recorded intersection {field} differs')
    stage_a_dir = Path(run['e3_stage_a_dir'])
    selection = read_json(stage_a_dir/'run.json', {})
    selected = read_rows(stage_a_dir/'rows.jsonl')
    selection_counts = dict(planned=12, observed=len(selected), strict_quality=0, clean_q_h_both=0,
                           sd15_vae_J=0, sdxl_vae_J=0, inherited_calls=0, negative_calls=0, negative_detections=0)
    for row in selected:
        for condition, c in row.get('conditions', {}).items():
            e = endpoint(c['calls'][ALPHA], row['payload'])
            selection_counts['inherited_calls'] += len(c['calls']) + bool(c.get('c0_call'))
            if condition == 'clean':
                selection_counts['strict_quality'] += quality(c.get('quality_source'))
                selection_counts['clean_q_h_both'] += bool(e['Q'] and e['H'] and e['F'])
            else:
                selection_counts[condition+'_J'] += bool(e['J'])
            for call in (c['calls'][BETA], c.get('c0_call')):
                if call:
                    selection_counts['negative_calls'] += 1
                    selection_counts['negative_detections'] += endpoint(call)['A']
    selected_pass = bool(len(selected) == 12 and {r['source_id'] for r in selected} == set(IDS)
        and all(selection_counts[k] == 12 for k in ('strict_quality', 'clean_q_h_both', 'sd15_vae_J', 'sdxl_vae_J'))
        and selection_counts['inherited_calls'] == 108 and selection_counts['negative_calls'] == 72
        and not selection_counts['negative_detections'] and selection.get('qualification') == 'stage_a_pass')
    wall = read_json(folder/'parent-wall.json', {})
    inclusive = wall.get('duration_seconds')
    timing = dict(process_seconds=run.get('duration_seconds'), parent_inclusive_seconds=inclusive,
        peak_allocated_bytes=run.get('peak_allocated_bytes'), cap_seconds=900, gpu_cap_bytes=10*1024**3,
        cached_composition_seconds=selection.get('duration_seconds'), fresh_writer_seconds=None,
        ancestry='Selected cached E1 A/B marks and one E2 contraction; inherited timings are not fresh E3 writer cost')
    cap_pass = bool(isinstance(inclusive, (int, float)) and 0 < inclusive <= 900 and
        0 < (run.get('peak_allocated_bytes') or 0) <= 10*1024**3 and
        not run.get('budget_overrun') and not run.get('gpu_budget_overrun'))
    negative_detections = sum(n['any_detection'] for n in negatives)
    blocked = sum(r['status'] == 'safety_blocked' for r in rows)
    expected_calls = 216 - sum((2 if r['arm'] == 'candidate_C1' else 1)
                             for r in rows if r['status'] == 'safety_blocked')
    negative_accounted = len(negatives) + blocked == 144
    passed = bool(selected_pass and complete and not operational and not issues and not saved.get('error')
        and run['outcome'] == 'completed' and cap_pass and calls == expected_calls and negative_accounted
        and not negative_detections and all(v['count_pass'] and v['preservation_pass'] and v['fixed_I_pass']
                                         for v in strengths.values()))
    aggregate = dict(recorded_image_rows=len(rows), observed_full_calls=calls,
        observed_negative_calls=len(negatives), negative_any_detections=negative_detections, complete=complete)
    for key, value in aggregate.items():
        if saved.get(key) != value:
            issues.append('Recorded aggregate differs: '+key)
    raw_hist = dict(Counter(str(e['raw_coded_bit_errors']) for e in candidates.values()))
    if saved.get('raw_59_bit_error_histogram') != raw_hist:
        issues.append('Recorded raw coded error histogram differs')
    recorded_negatives = {(n['arm'], n['identity'], n['owner']):n['any_detection']
                          for n in saved.get('negative_calls', [])}
    computed_negatives = {(n['arm'], n['identity'], BETA if n['arm'] == 'candidate_C1' else ALPHA):n['any_detection']
                          for n in negatives}
    if (recorded_negatives != computed_negatives or
        len(saved.get('negative_calls', [])) != len(negatives)):
        issues.append('Recorded negative-call endpoints differ')
    if issues:
        passed = False
    return dict(schema='journal-e3-full-t3-descriptive-v1', run_dir=str(folder), commit=run['commit'],
        method='E3-BCH59-Q080', raw_method=run.get('method'), raw_summary_method=saved.get('method'),
        outcome=run['outcome'], qualification=run['qualification'],
        planned_image_rows=144, planned_full_calls=216, planned_negative_calls=144,
        **aggregate, negative_by_arm=negative_by_arm, negative_accounted=negative_accounted,
        unavailable_rows=unavailable, operational_failures=operational, strengths=strengths,
        selection=dict(run_dir=str(stage_a_dir), counts=selection_counts, pass_recomputed=selected_pass,
            branch_counts=dict(Counter(r['selection_provenance']['branch'] for r in selected)),
            selected_lineage=[dict(source_id=r['source_id'], **r['selection_provenance']) for r in selected],
            new_calls=0, e1_stage_b_dir=run.get('e1_stage_b_dir'), e2_stage_a_dir=run.get('e2_stage_a_dir')),
        timing=timing, cap_pass=cap_pass, stage_b_pass_recomputed=passed,
        recorded_stage_b_pass=saved.get('stage_b_pass'), verdict_agrees=passed == saved.get('stage_b_pass'),
        recorded_endpoint_mismatches=mismatches, issues=issues, metadata_issues=metadata_issues,
        interpretation='Adaptive exploratory in-sample image-domain BCH selection. All 72 C1 generations are fresh; '
        'retained C0 pixels receive fresh calls when available. E1 ancestry optimized these same six seeds. '
        'Safety blocks remain unsuccessful planned slots, with unobserved negatives unresolved. '
        'Source majority is descriptive across twelve reused sources. No population FPR, generalization, '
        'T4/T5 preservation, M1a passage, human admissibility or latent-method claim follows.')


def report(stats):
    lines = ['# E3 full T3 descriptive analysis', '',
        f"Recomputed Stage B pass: {stats['stage_b_pass_recomputed']}; recorded agreement: {stats['verdict_agrees']}.",
        f"Commit: {stats['commit']}; outcome: {stats['outcome']}.", '',
        f"Image rows {stats['recorded_image_rows']}/144; full calls {stats['observed_full_calls']}/216; "
        f"negative detections {stats['negative_any_detections']} in {stats['observed_negative_calls']}/144 available calls.",
        f"Unavailable rows: {len(stats['unavailable_rows'])}; operational failures: {len(stats['operational_failures'])}.", '',
        '| Strength | S | Exact Q | Joint Q/content | Source-majority S/Q/J (of 12) | Fixed S versus v5 |',
        '|---|---:|---:|---:|---|---|']
    for strength, value in stats['strengths'].items():
        c, i = value['successes'], value['intersection']
        lines.append(f"| {strength} | {c['S']}/36 | {c['Q']}/36 | {c['J']}/36 | "
            f"{value['source_majority_descriptive']} | {i['candidate_S']}/{i['fixed_identities']} versus "
            f"{i['v5_S']}/{i['fixed_identities']} |")
    lines += ['', f"Cached selection: {stats['selection']['counts']}; branches {stats['selection']['branch_counts']}.",
              f"Timing and reused ancestry: {stats['timing']}. Inclusive cost/memory cap pass: {stats['cap_pass']}."]
    for strength, value in stats['strengths'].items():
        lines += ['', f"Strength {strength} raw/decoded error histograms (nulls separate): {value['histograms']}.",
                  f"Unavailable C1 slots: {value['unavailable_candidate_slots']}.",
                  f"Algebraic success/reasons: {value['algebraic_success']}; {value['algebraic_reasons']}.",
                  f"Content failures: {value['content_failures']}; score ranges: {value['scores']}."]
        for method, endpoints in value['retention'].items():
            lines.append(f"{method} retention: {endpoints}.")
    lines += ['', stats['interpretation'],
              'stats.json retains exact lost/gained identities, failed-joint score details and selected lineage; full calls remain in the input record.']
    if stats['issues'] or stats['metadata_issues']:
        lines += ['', 'Record issues: '+str(stats['issues']), 'Metadata issues: '+str(stats['metadata_issues'])]
    return '\n'.join(lines)+'\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    stats = analyze(args.run_dir.resolve())
    stats['analysis_provenance'] = dict(
        script=str(Path(__file__).resolve()),
        commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=Path(__file__).resolve().parent, text=True).strip(),
        raw_records=[str(args.run_dir.resolve()/name) for name in ('run.json', 'rows.jsonl', 'summary.json', 'parent-wall.json')])
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir/'stats.json').write_text(json.dumps(stats, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    (args.output_dir/'report.md').write_text(report(stats), encoding='utf-8')


if __name__ == '__main__':
    main()
