"""Stdlib descriptive WAM T3 analysis; no calibrated presence or gate verdict."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path

MAIN = Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5')
ROOT = Path(__file__).resolve().parents[1]
FROZEN = MAIN / '.thesis-build/dev-runs/20261010-1051-rc3-t3'
CLEAN = MAIN / '.thesis-build/dev-runs/20261010-0948-wam-vae'
IDS = (1675, 4795, 6012, 25394, 80932, 109798, 134882, 147498,
       177015, 190676, 468505, 499768)
ARMS = ('native_w2', 'quality_w0p5', 'shared_C0')
STRENGTHS, SEEDS = (.1, .2), (0, 1, 2)
ALPHA = 'qim-pilot-owner-alpha'


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def rows(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def identity(row):
    return int(row['source_id']), float(row['strength']), int(row['seed'])


def label(key):
    return '|'.join(map(str, key))


def message(sid):
    digest = hashlib.sha256(f'journal-wam-dev-v1:{sid}'.encode()).digest()[:4]
    return [(byte >> shift) & 1 for byte in digest for shift in range(7, -1, -1)]


def describe(values):
    finite = sorted(float(v) for v in values if v is not None and math.isfinite(v))
    n = len(finite)
    return dict(n=n, unavailable_or_nonfinite=len(values)-n,
                minimum=finite[0] if n else None, maximum=finite[-1] if n else None,
                mean=sum(finite)/n if n else None,
                median=(finite[(n-1)//2]+finite[n//2])/2 if n else None)


def inventory(data, expected, key):
    counts = Counter(key(r) for r in data)
    inv = dict(planned=len(expected), recorded=len(data), unique=len(counts),
               missing=[label(k) for k in sorted(expected-counts.keys())],
               extra=[label(k) for k in sorted(counts.keys()-expected)],
               duplicates=[dict(identity=label(k), count=n) for k, n in sorted(counts.items()) if n > 1],
               statuses=dict(Counter(r.get('status', 'missing_status') for r in data)))
    inv['complete_unique_inventory'] = not any(inv[x] for x in ('missing', 'extra', 'duplicates'))
    # Ambiguous repeated identities have no aggregate score; do not choose a favorable row.
    unique = {key(r): r for r in data if key(r) in expected and counts[key(r)] == 1}
    return inv, unique


def decode(row):
    """Recompute from native decoded bits, never from stored success summaries."""
    target = message(int(row['source_id']))
    if row.get('message') != target:
        raise ValueError('Row target differs from frozen public source-ID schedule')
    d = row['detection']
    positive, pixels = d['native_mask_positive_pixels'], d['native_mask_pixels']
    if not isinstance(positive, int) or not isinstance(pixels, int) or not 0 <= positive <= pixels or pixels <= 0:
        raise ValueError('Invalid native mask pixel counts')
    bits = d['decoded_message']
    if bits is not None and (not isinstance(bits, list) or len(bits) != 32 or any(b not in (0, 1) for b in bits)):
        raise ValueError('Invalid decoded 32-bit payload')
    if (positive > 0) != (bits is not None):
        raise ValueError('Empty-mask/decoded-message contract differs')
    accuracy = sum(a == b for a, b in zip(bits, target))/32 if bits is not None else None
    result = dict(exact=bits == target, complement_exact=bits == [1-b for b in target],
                  bit_accuracy=accuracy, complement_bit_accuracy=1-accuracy if accuracy is not None else None,
                  empty=positive == 0, mask_fraction=positive/pixels, mask_mean=d['native_mask_mean'])
    result['stored_field_disagreements'] = [field for field, value in (
        ('exact_message_match', result['exact']), ('wrong_message_exact_match', result['complement_exact']),
        ('bit_accuracy', accuracy), ('wrong_message_bit_accuracy', result['complement_bit_accuracy']),
        ('native_mask_nonempty_diagnostic', not result['empty']),
        ('native_mask_fraction', result['mask_fraction'])) if d.get(field) != value]
    return result


def quality(data):
    return {field: {metric: describe([r.get(field, {}).get(metric) for r in data])
                    for metric in ('psnr_db', 'ssim_rgb', 'lpips')}
            for field in ('quality_source', 'quality_input')}


def comparator(path, arm, field):
    record = load(path/'run.json')
    if record.get('outcome') == 'running':
        raise ValueError('Comparator run is still active')
    if (record.get('schema') != 'journal-rc-t3-v1' or record.get('data_split') != 'development'
            or record.get('usd') != 0 or record.get('seeds') != list(SEEDS)
            or (arm == 'candidate_C1' and record.get('config', {}).get('candidate') != 'D2')):
        raise ValueError('Unexpected comparator protocol or optional D2 candidate')
    selected = [r for r in rows(path/'rows.jsonl') if r.get('arm') == arm]
    expected = {(sid, s, seed) for sid in IDS for s in STRENGTHS for seed in SEEDS}
    inv, unique = inventory(selected, expected, identity)
    ep, errors = {}, []
    for k, r in unique.items():
        if r.get('status') != 'ok':
            continue
        try:
            call = r[field][ALPHA]['semantic']
            q = r['payload']['q']
            exact = bool(call['read'] and int(call['decoded_code'], 16) == int(q, 16))
            ep[k] = dict(Q=exact, J=bool(exact and call['content_match']))
        except (KeyError, TypeError, ValueError) as error:
            errors.append(dict(identity=label(k), error=str(error)))
    return dict(path=str(path), commit=record.get('commit'), inventory=inv, call_errors=errors,
                endpoint_definitions='Q: semantic.read and decoded q equals recorded target; J: Q and semantic.content_match'), ep, unique


def clean_snapshot():
    record = load(CLEAN/'run.json')
    selected = [r for r in rows(CLEAN/'rows.jsonl') if r.get('control') == 'C1' and r.get('condition') == 'clean']
    expected = {(arm, sid) for arm in ARMS[:2] for sid in IDS}
    inv, unique = inventory(selected, expected, lambda r: (r['arm'], int(r['source_id'])))
    result = dict(path=str(CLEAN), commit=record.get('commit'), inventory=inv, arms={})
    for arm in ARMS[:2]:
        group = [r for (a, sid), r in unique.items() if a == arm and r.get('status') == 'ok']
        strict = sum((q.get('psnr_infinite') or q.get('psnr_db') is not None and q['psnr_db'] > 35)
                     and q.get('ssim_rgb', 0) > .9 and q.get('lpips', 1) < .1
                     for q in (r['quality_source'] for r in group))
        result['arms'][arm] = dict(planned=12, completed=len(group),
            exact=sum(decode(r)['exact'] for r in group), strict_quality=strict, quality=quality(group))
    return result


def analyze(path, d2_path=None):
    record = load(path/'run.json')
    if record.get('outcome') == 'running':
        raise ValueError('WAM probe is still active; no final analysis of partial active output')
    if (record.get('schema') != 'journal-wam-t3-v1' or record.get('data_split') != 'development'
            or record.get('usd') != 0 or record.get('sources') != list(IDS)
            or record.get('seeds') != list(SEEDS) or record.get('strengths') != list(STRENGTHS)
            or record.get('config', {}).get('arms') != {'native_w2': 2.0, 'quality_w0p5': .5}):
        raise ValueError('Unexpected fixed WAM protocol configuration')
    data = rows(path/'rows.jsonl')
    expected = {(a, sid, s, seed) for a in ARMS for sid in IDS for s in STRENGTHS for seed in SEEDS}
    inv, unique = inventory(data, expected, lambda r: (r['arm'], *identity(r)))
    calls, errors, discrepancies = {}, [], []
    for k, r in unique.items():
        if 'detection' not in r:
            if r.get('status') == 'ok':
                errors.append(dict(identity=label(k), error='ok row lacks detection'))
            continue
        try:
            calls[k] = decode(r)
            if calls[k]['stored_field_disagreements']:
                discrepancies.append(dict(identity=label(k), fields=calls[k]['stored_field_disagreements']))
        except (KeyError, TypeError, ValueError) as error:
            errors.append(dict(identity=label(k), error=str(error)))
    cells = {}
    for a in ARMS:
        for s in STRENGTHS:
            planned = [(a, sid, s, seed) for sid in IDS for seed in SEEDS]
            group = [unique[k] for k in planned if k in unique]
            good = [k for k in planned if k in calls and unique[k].get('status') == 'ok']
            observed = [k for k in planned if k in calls]
            readable = [k for k in good if calls[k]['bit_accuracy'] is not None]
            exact = sum(calls[k]['exact'] for k in good)
            cells[f'{a}/{s}'] = dict(planned=36, recorded_unique=len(group),
                statuses=dict(Counter(r.get('status', 'missing_status') for r in group)),
                missing_or_duplicate=36-len(group), completed_status_ok=sum(r.get('status') == 'ok' for r in group),
                completed_valid_calls=len(good), observed_calls_any_status=len(observed),
                exact_recovery=exact, exact_rate_all_planned=exact/36,
                exact_rate_completed=exact/len(good) if good else None,
                bit_accuracy_observed_nonempty=describe([calls[k]['bit_accuracy'] for k in readable]),
                bit_accuracy_all_planned_zero_stress=sum(calls[k]['bit_accuracy'] or 0 for k in good)/36,
                complement_bit_accuracy_observed_nonempty=describe([calls[k]['complement_bit_accuracy'] for k in readable]),
                empty_masks_completed=sum(calls[k]['empty'] for k in good),
                complement_exact_completed=sum(calls[k]['complement_exact'] for k in good),
                exact_any_observed_status=sum(calls[k]['exact'] for k in observed),
                complement_exact_any_observed_status=sum(calls[k]['complement_exact'] for k in observed),
                empty_masks_any_observed_status=sum(calls[k]['empty'] for k in observed),
                source_majority=dict(successes=sum(sum((a, sid, s, seed) in good and
                    calls[(a, sid, s, seed)]['exact'] for seed in SEEDS) >= 2 for sid in IDS), planned_sources=12),
                masks={field: describe([calls[k][field] for k in good]) for field in ('mask_fraction', 'mask_mean')},
                quality=quality([unique[k] for k in good]))
    comparisons, paired = {}, {}
    specifications = [('frozen_F5_native', FROZEN, 'frozen_C1_enrichment', 'native_calls')]
    if d2_path is not None:
        specifications.append(('D2_RC', d2_path, 'candidate_C1', 'calls'))
    for name, location, a, field in specifications:
        metadata, ep, lookup = comparator(location, a, field)
        comparisons[name] = metadata
        for arm in ARMS[:2]:
            for s in STRENGTHS:
                grid = [(sid, s, seed) for sid in IDS for seed in SEEDS]
                entries = []
                for k in grid:
                    wk = (arm, *k)
                    w = calls.get(wk) if unique.get(wk, {}).get('status') == 'ok' else None
                    entries.append(dict(identity=label(k), wam_status=unique.get(wk, {}).get('status', 'missing_or_duplicate'),
                        wam_exact=w['exact'] if w is not None else None,
                        comparator_status=lookup.get(k, {}).get('status', 'missing_or_duplicate'), comparator=ep.get(k)))
                common = [r for r in entries if r['wam_exact'] is not None and r['comparator'] is not None]
                paired[f'{arm}/{s}/{name}'] = dict(planned=36, common_observed=len(common),
                    wam_valid=sum(r['wam_exact'] is not None for r in entries), comparator_valid=sum(k in ep for k in grid),
                    endpoints={e: dict(wam_on_planned=sum(r['wam_exact'] is True for r in entries),
                        comparator_on_planned=sum(k in ep and ep[k][e] for k in grid),
                        wam_on_common=sum(r['wam_exact'] for r in common), comparator_on_common=sum(r['comparator'][e] for r in common),
                        wam_only_on_common=sum(r['wam_exact'] and not r['comparator'][e] for r in common),
                        comparator_only_on_common=sum(not r['wam_exact'] and r['comparator'][e] for r in common)) for e in ('Q', 'J')},
                    identities=entries)
    return dict(schema='journal-wam-t3-analysis-v1', input=dict(path=str(path.resolve()),
        commit=record.get('commit'), outcome=record.get('outcome'), command=record.get('command')),
        inventory=inv, call_errors=errors, stored_field_disagreements=discrepancies,
        operationally_complete=inv['complete_unique_inventory'] and not errors and
            all(r.get('status') in ('ok', 'safety_blocked') for r in unique.values()),
        budget=dict(cap_seconds=900, duration_seconds=record.get('duration_seconds'),
            overrun_measured=record.get('duration_seconds') is not None and record['duration_seconds'] > 900,
            overrun_recorded=record.get('budget_overrun')),
        cells=cells, clean_snapshot=clean_snapshot(), comparators=comparisons, paired=paired,
        limits=['Exploratory twelve-source development sample; no significance test or population inference.',
            'No matched-FPR superiority: native WAM mask/bit decoder has no separately calibrated image presence endpoint.',
            'WAM public 32-bit source-ID message differs from F5 q/h construction and content binding; complement is not wrong-owner authentication.',
            'Q is exact semantic-code recovery; J adds semantic content_match, not full q/h acceptance.',
            'Shared C0 pixels/calls and repeated source seeds are shared evidence, not independent replicates.',
            'Zero-scored unavailable/empty all-planned bit accuracy is a stress score, not measured accuracy for unavailable outputs.',
            'Quality distributions are descriptive, no quality filtering; human admissibility remains missing.',
            'MIT SA-1B checkpoint is not the paper COCO checkpoint; no held-out or lifecycle gate verdict.'])


def report(d):
    lines = ['# Exploratory WAM matched T3', '',
        f"Inventory: {d['inventory']['recorded']}/216 recorded; unique complete: {d['inventory']['complete_unique_inventory']}; operational complete: {d['operationally_complete']}. "
        f"Call errors: {len(d['call_errors'])}; stored-field disagreements: {len(d['stored_field_disagreements'])}.", '',
        '| Arm / strength | Exact / planned | Valid / planned | Nonempty bit accuracy (n) | All-planned zero stress | Empty | Complement exact | Source majority |',
        '|---|---:|---:|---:|---:|---:|---:|---:|']
    for name, c in d['cells'].items():
        acc = c['bit_accuracy_observed_nonempty']
        lines.append(f"| {name} | {c['exact_recovery']}/36 | {c['completed_valid_calls']}/36 | {acc['mean']} ({acc['n']}) | {c['bit_accuracy_all_planned_zero_stress']:.4f} | {c['empty_masks_completed']} | {c['complement_exact_completed']} | {c['source_majority']['successes']}/12 |")
    lines += ['', 'Each marked arm has 72 planned attempts. Shared C0 has 72 total attempts, decoded once and shared across arms. Source majority requires exact recovery on at least two of three planned seeds; unavailable seeds count as no success.', '']
    for name, c in d['cells'].items():
        lines.append(f"- {name}: statuses {c['statuses']}; missing/duplicate {c['missing_or_duplicate']}; observed calls across all statuses {c['observed_calls_any_status']}.")
    lines += ['', '## Matched identities', '', '| Arm / strength / comparator / endpoint | WAM / 36 | Comparator / 36 | Common observed | WAM / common | Comparator / common | WAM only / comparator only |', '|---|---:|---:|---:|---:|---:|---:|']
    for name, p in d['paired'].items():
        for e, c in p['endpoints'].items():
            lines.append(f"| {name}/{e} | {c['wam_on_planned']}/36 | {c['comparator_on_planned']}/36 | {p['common_observed']}/36 | {c['wam_on_common']}/{p['common_observed']} | {c['comparator_on_common']}/{p['common_observed']} | {c['wam_only_on_common']} / {c['comparator_only_on_common']} |")
    lines += ['', 'All planned comparison counts retain blocked/failed/missing identities; common-observed rows are descriptive paired availability subsets. Their endpoints differ and do not establish superiority.', '', '## Clean quality and attack distortion', '']
    for arm, c in d['clean_snapshot']['arms'].items():
        lines.append(f"- Prior clean {arm}: exact {c['exact']}/12; strict PSNR >35, SSIM >.9, LPIPS <.1: {c['strict_quality']}/12; completed {c['completed']}/12.")
    for name, c in d['cells'].items():
        for field, metrics in c['quality'].items():
            lines.append(f"- {name}, {field}: " + '; '.join(f"{m} n={v['n']}, mean={v['mean']}, range={v['minimum']}..{v['maximum']}" for m, v in metrics.items()) + '.')
    lines += ['', f"Fresh budget: {d['budget']['duration_seconds']} s / 900 s; measured overrun {d['budget']['overrun_measured']}.", '', '## Limits', '']
    lines.extend('- '+limit for limit in d['limits'])
    lines += ['', 'Statistics JSON retains all inventory discrepancies, quality distributions, paired identities and endpoint denominators. No probe summary was used for counts.', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', required=True, type=Path)
    parser.add_argument('--output-dir', required=True, type=Path)
    parser.add_argument('--d2-run', type=Path)
    args = parser.parse_args()
    if args.output_dir.resolve() in {p.resolve() for p in (args.run, FROZEN, CLEAN, args.d2_run) if p is not None}:
        raise ValueError('Analysis output directory must differ from raw run directories')
    d = analyze(args.run, args.d2_run)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir/'wam-t3-statistics.json').write_text(json.dumps(d, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    (args.output_dir/'wam-t3-results.md').write_text(report(d), encoding='utf-8')
    print(json.dumps(dict(operationally_complete=d['operationally_complete'],
        exact={name: c['exact_recovery'] for name, c in d['cells'].items()})))


if __name__ == '__main__':
    main()
