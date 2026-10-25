"""Post-hoc source-local quality dominance; existing journal, standard library only.

Run only after committing this file. No image, model, or metric computation occurs.
Numeric seed equality is a label pairing, not equality of regeneration randomness.
All source-local pairs share outputs and are not independent observations.
"""
import csv
import hashlib
import itertools
import json
import math
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
INPUT = Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/20261025-0128-encoder-transfer-stage2b/results/stage2b-full/rows.jsonl')
OWNER = 'qim-pilot-owner-alpha'
ARMS = ('f5-r2', 'v5-r3', 'wam', 'vine-r')
SEEDS = (12, 13, 14)
REFERENCES = ('distortion', 'total_distortion')
MODES = ('same_numeric_seed_label', 'all_source_local_pairs')
METRICS = ('lpips', 'psnr_db', 'ssim_rgb')
COUNT_FIELDS = ('scheduled_pairs', 'observed_record_pairs', 'complete_pairs',
                'missing_pairs', 'r1_strictly_milder_pairs',
                'r0_positive_r1_negative_among_r1_milder_pairs',
                'r0_strictly_milder_pairs',
                'r1_positive_r0_negative_among_r0_milder_pairs')


def finite(value):
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value))


def read_journal():
    final = {}
    digest = hashlib.sha256()
    lines = overwritten = 0
    with INPUT.open('rb') as stream:
        for raw in stream:
            digest.update(raw)
            lines += 1
            row = json.loads(raw)
            identity = row['id']
            overwritten += int(identity in final)
            final[identity] = row
    return final, dict(input_path=str(INPUT), input_sha256=digest.hexdigest(),
                       journal_lines=lines, unique_ids=len(final),
                       overwritten_records=overwritten,
                       final_status_counts=dict(sorted(Counter(
                           str(r.get('status')) for r in final.values()).items())))


def usable(row, arm, reference):
    """Return quality and strict Boolean endpoint, or an explicit missing reason."""
    if row is None:
        return None, 'record_absent'
    if row.get('status') != 'ok':
        return None, 'row_status_' + str(row.get('status'))
    quality = row.get(reference)
    if not isinstance(quality, dict) or quality.get('status') != 'ok':
        return None, 'quality_status_not_ok'
    if not all(finite(quality.get(metric)) for metric in METRICS):
        return None, 'quality_nonfinite_or_nonnumeric'
    detection = row.get('detections', {}).get(arm, {}).get(OWNER, {})
    if detection.get('status') != 'ok':
        return None, 'right_owner_detector_status_not_ok'
    if arm in ('f5-r2', 'v5-r3'):
        endpoint = detection.get('endpoints', {}).get('C')
    else:
        endpoint = detection.get('presence', {}).get('present')
    if not isinstance(endpoint, bool):
        return None, 'endpoint_not_boolean'
    return ({metric: quality[metric] for metric in METRICS}, endpoint), None


def milder_gaps(worse, better):
    """Positive values mean better quality in each respective metric."""
    return {'lpips': worse['lpips'] - better['lpips'],
            'psnr_db': better['psnr_db'] - worse['psnr_db'],
            'ssim_rgb': better['ssim_rgb'] - worse['ssim_rgb']}


def bounds(gaps):
    return {metric: {'min': min(g[metric] for g in gaps),
                     'max': max(g[metric] for g in gaps)} if gaps else
            {'min': None, 'max': None} for metric in METRICS}


def main():
    final, journal = read_journal()
    sources = sorted({r['source_id'] for r in final.values()}, key=str)
    if len(sources) != 60:
        raise ValueError('Expected exactly 60 journal source IDs; got ' + str(len(sources)))
    index = {}
    selected_status = Counter()
    for row in final.values():
        if (row.get('control') != 'C1' or row.get('arm') not in ARMS or
                (row.get('channel'), row.get('strength')) not in (('R0', .2), ('R1', .1)) or
                row.get('seed') not in SEEDS):
            continue
        key = (row['arm'], row['channel'], row['strength'], row['source_id'], row['seed'])
        if key in index:
            raise ValueError('Duplicate final scientific key: ' + repr(key))
        index[key] = row
        selected_status[str(row.get('status'))] += 1
    journal['selected_records'] = len(index)
    journal['selected_final_status_counts'] = dict(sorted(selected_status.items()))
    journal['selected_unique_sources'] = len({k[3] for k in index})
    if journal['selected_unique_sources'] != 60:
        raise ValueError('Selected contrast does not cover 60 source IDs')
    per_source = []
    aggregates = []
    missing_reasons = Counter()
    for arm, reference, mode in itertools.product(ARMS, REFERENCES, MODES):
        seed_pairs = ([(s, s) for s in SEEDS] if mode == MODES[0] else
                      list(itertools.product(SEEDS, repeat=2)))
        group = []
        contradictions = []
        reverse_contradictions = []
        complete_six_contradictions = []
        complete_six_reverse = []
        for source in sources:
            raw = {(channel, seed): index.get((arm, channel, strength, source, seed))
                   for channel, strength in (('R0', .2), ('R1', .1)) for seed in SEEDS}
            valid = {}
            for key, row in raw.items():
                value, reason = usable(row, arm, reference)
                valid[key] = value
                # Count each output once per quality reference, not once per pairing mode.
                if reason and mode == MODES[0]:
                    missing_reasons[(arm, reference, reason)] += 1
            six_complete = all(value is not None for value in valid.values())
            result = dict(arm=arm, quality_reference=reference, pairing_mode=mode,
                          source_id=source, complete_six_outputs=int(six_complete),
                          **{field: 0 for field in COUNT_FIELDS})
            result['scheduled_pairs'] = len(seed_pairs)
            local_gaps = []
            local_reverse = []
            for seed0, seed1 in seed_pairs:
                key0, key1 = ('R0', seed0), ('R1', seed1)
                result['observed_record_pairs'] += int(raw[key0] is not None and raw[key1] is not None)
                a, b = valid[key0], valid[key1]
                if a is None or b is None:
                    result['missing_pairs'] += 1
                    continue
                result['complete_pairs'] += 1
                gaps = milder_gaps(a[0], b[0])
                reverse = milder_gaps(b[0], a[0])
                dom = all(gap > 0 for gap in gaps.values())
                rev = all(gap > 0 for gap in reverse.values())
                result['r1_strictly_milder_pairs'] += int(dom)
                result['r0_strictly_milder_pairs'] += int(rev)
                if dom and a[1] and not b[1]:
                    result['r0_positive_r1_negative_among_r1_milder_pairs'] += 1
                    local_gaps.append(gaps)
                if rev and b[1] and not a[1]:
                    result['r1_positive_r0_negative_among_r0_milder_pairs'] += 1
                    local_reverse.append(reverse)
            for direction, entries in (('r1_milder_contradiction', local_gaps),
                                       ('r0_milder_contradiction', local_reverse)):
                for metric, limit in bounds(entries).items():
                    for edge in ('min', 'max'):
                        result[f'{direction}_{metric}_gap_{edge}'] = limit[edge]
            contradictions.extend(local_gaps)
            reverse_contradictions.extend(local_reverse)
            if six_complete:
                complete_six_contradictions.extend(local_gaps)
                complete_six_reverse.extend(local_reverse)
            group.append(result)
        aggregate = dict(arm=arm, quality_reference=reference, pairing_mode=mode,
                         scheduled_sources=60,
                         **{field: sum(r[field] for r in group) for field in COUNT_FIELDS})
        for field in COUNT_FIELDS[2:]:
            aggregate['sources_any_' + field] = sum(r[field] > 0 for r in group)
        subset = [r for r in group if r['complete_six_outputs']]
        aggregate['complete_six_output_subset'] = dict(
            sources=len(subset),
            **{field: sum(r[field] for r in subset) for field in COUNT_FIELDS},
            sources_any_r1_milder_contradiction=sum(r[COUNT_FIELDS[5]] > 0 for r in subset),
            sources_any_r0_milder_contradiction=sum(r[COUNT_FIELDS[7]] > 0 for r in subset),
            r1_milder_contradiction_quality_gap_bounds=bounds(complete_six_contradictions),
            r0_milder_contradiction_quality_gap_bounds=bounds(complete_six_reverse))
        aggregate['r1_milder_contradiction_quality_gap_bounds'] = bounds(contradictions)
        aggregate['r0_milder_contradiction_quality_gap_bounds'] = bounds(reverse_contradictions)
        aggregates.append(aggregate)
        per_source.extend(group)
    if len(aggregates) != 16 or len(per_source) != 960:
        raise AssertionError('Unexpected output dimensions')
    output = dict(
        analysis='Post-hoc descriptive source-local strict all-three-metric dominance',
        contrast={'left': 'C1 R0@0.2', 'right': 'C1 R1@0.1', 'seeds': list(SEEDS),
                  'right_owner': OWNER, 'arms': list(ARMS)},
        interpretation=[
            'No p-values; source-local pairs share outputs and are not independent trials.',
            'Equal numeric seed labels do not assert equal regeneration randomness.',
            'Complete pairs require row, quality and right-owner detector status ok, finite numeric quality and a Boolean endpoint.',
            'Strictly milder means lower LPIPS and higher PSNR and SSIM; ties do not dominate.',
            'Contradictions concern three recorded quality metrics, not all perceptual distortion or a causal encoder effect.',
            'Gap bounds use positive metric improvements toward the strictly milder output, only among contradictions.',
            'Missing pairs include absent records and unusable observations; scheduled pair counts always retain all 60 sources.'
        ], journal=journal,
        unusable_output_counts=[dict(arm=a, quality_reference=q, reason=r, count=n)
                                for (a, q, r), n in sorted(missing_reasons.items())],
        aggregates=aggregates)
    (HERE / 'quality-dominance.json').write_text(
        json.dumps(output, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    with (HERE / 'quality-dominance-sources.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(per_source[0]))
        writer.writeheader()
        writer.writerows(per_source)
    print(json.dumps({'aggregate_rows': len(aggregates), 'source_rows': len(per_source),
                      'journal_lines': journal['journal_lines'], 'unique_ids': journal['unique_ids'],
                      'selected_records': journal['selected_records'],
                      'summary': [{k: r[k] for k in ('arm', 'quality_reference', 'pairing_mode',
                                   'complete_pairs', 'missing_pairs', COUNT_FIELDS[5], COUNT_FIELDS[7])}
                                  for r in aggregates]}, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
