"""TK2: prospective, CPU-only saved-feature calibration diagnostic.

Run only after preregistration and commit. No image/model/held-out access.
One additive bias is fit on DESIGN; all EVALUATE summaries are descriptive.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
MAIN = Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5')
INPUT = MAIN / '.thesis-build/v5-study-runs/C4-v5-two-tier-development/c4-v5-two-tier-dev-001/outputs/results.json'
PROFILE = ROOT / 'experiments/c4-v5-two-tier-regeneration-v1/profile.json'
ALLOWED_OUT = ROOT / 'research/f5-components-20261101'
# Historical design roster; these are protocol constants, not observed outcomes.
T3_SOURCES = (6012, 25394, 80932, 109798, 134882, 147498, 177015, 190676, 468505, 499768)
ALL_SOURCES = tuple(sorted((*T3_SOURCES, 1675, 4795)))
STRENGTHS = (.05, .1, .2, .4)
OWNER = 'qim-pilot-owner-alpha'
LIMIT_SECONDS = 540


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha_bytes(value):
    return hashlib.sha256(value).hexdigest()


def write_json(path, value):
    with path.open('x', encoding='utf-8', newline='\n') as handle:
        json.dump(value, handle, indent=2, allow_nan=False)
        handle.write('\n')


def expected_rows():
    rows = []
    for source in T3_SOURCES:
        rows.append(dict(id=f'vae-{source}-C1', source_id=source, axis='T3',
                         control='C1', dose='vae_mode', seed=None, strength=None))
        for strength in STRENGTHS:
            for seed in range(3):
                rows.append(dict(id=f't3-{source}-{strength}-{seed}-C1', source_id=source,
                                 axis='T3', control='C1', dose='diffusion', seed=seed,
                                 strength=strength))
    return rows


def feature_code(row, profile, codec):
    require(isinstance(row, dict), 'missing saved row')
    feature = row.get('clip') or {}
    values = feature.get('values')
    require(isinstance(values, list) and len(values) == 512, 'missing or invalid 512D feature')
    require(all(type(x) in (float, int) and math.isfinite(x) for x in values),
            'feature contains nonfinite/nonnumeric value')
    norm = math.sqrt(math.fsum(x*x for x in values))
    require(norm > 0, 'zero norm feature')
    code = codec.semantic_code(values, profile=profile)
    require(type(code) is int and 0 <= code < 2**32, 'invalid computed q32')
    saved = [d.get('result', {}).get('semantic_code') for d in row.get('detections', [])
             if d.get('claimed_owner') == OWNER and d.get('binding_mode') == 'combined']
    require(len(saved) <= 1, 'duplicate saved owner combined detection')
    if saved and saved[0] is not None:
        require(int(saved[0], 16) == code, 'computed q32 differs from saved q32')
    return values, norm, code, bool(saved and saved[0] is not None)


def source_weighted(rows, field):
    by_source = defaultdict(list)
    for row in rows:
        if row.get(field) is not None:
            by_source[row['source_id']].append(row[field])
    means = {str(source): statistics.fmean(values) for source, values in sorted(by_source.items())}
    return dict(value=statistics.fmean(means.values()) if means else None,
                n_sources=len(means), n_rows=sum(map(len, by_source.values())), per_source=means)


def summarize(rows, design_sources, evaluation_sources):
    result = {}
    for split, sources in [('DESIGN', design_sources), ('EVALUATE', evaluation_sources)]:
        subset = [r for r in rows if r['split'] == split]
        result[split] = {
            'uncalibrated_mae': source_weighted(subset, 'uncalibrated_absolute_error'),
            'calibrated_mae': source_weighted(subset, 'calibrated_absolute_error'),
            'n_retained_or_missing_units': len(subset),
            'n_unavailable_units': sum(r['availability'] != 'available' for r in subset),
            'assigned_sources': sources,
            'clean_only_not_planned_for_T3': [s for s in sources if s not in T3_SOURCES],
            'planned_T3_sources_with_no_available_rows': [s for s in sources if s in T3_SOURCES
                and not any(r['source_id'] == s and r['availability'] == 'available' for r in subset)]}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True, type=Path, help='New directory within research/f5-components-20261101')
    args = parser.parse_args()
    started = time.perf_counter()
    # Fail closed on an incorrectly prepared execution environment.
    require(os.environ.get('CUDA_VISIBLE_DEVICES') == '-1', 'CUDA_VISIBLE_DEVICES must equal -1')
    require(not sys.flags.optimize, 'do not disable assertions with -O')
    assert INPUT.resolve() == (MAIN / '.thesis-build/v5-study-runs/C4-v5-two-tier-development/c4-v5-two-tier-dev-001/outputs/results.json').resolve()
    assert 'development' in str(INPUT).lower() and not any(s in str(INPUT).lower() for s in ('held-out', 'heldout', 'test-pool'))
    out = args.out.resolve()
    require(out.is_relative_to(ALLOWED_OUT.resolve()) and out != ALLOWED_OUT.resolve(), 'output outside allowed research directory')
    require(not any(part.lower() == 'judge' or 'ruling' in part.lower() for part in out.relative_to(ALLOWED_OUT.resolve()).parts), 'protected output path')
    require(not out.exists(), 'output directory already exists; overwriting forbidden')
    commit = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, check=True,
                            capture_output=True, text=True, timeout=10).stdout.strip()
    script_relative = Path(__file__).resolve().relative_to(ROOT).as_posix()
    tracked = subprocess.run(['git', 'ls-files', '--error-unmatch', '--', script_relative],
                             cwd=ROOT, capture_output=True, timeout=10)
    require(tracked.returncode == 0, 'commit script before execution')
    diff = subprocess.run(['git', 'diff', 'HEAD', '--exit-code', '--', script_relative, PROFILE.relative_to(ROOT).as_posix(),
                           'scripts/revised_watermark_v5.py', 'scripts/revised_watermark_v4.py', 'scripts/revised_watermark_v3.py'],
                          cwd=ROOT, capture_output=True, timeout=10)
    require(diff.returncode == 0, 'script/profile/codec differ from committed versions')
    raw = INPUT.read_bytes()
    profile_raw = PROFILE.read_bytes()
    metadata = dict(schema='TK2-content-calibration-v1', status='running',
                    start_utc=datetime.now(timezone.utc).isoformat(), command=subprocess.list2cmdline([sys.executable, *sys.argv]),
                    argv=[sys.executable, *sys.argv], python=sys.version, git_commit=commit,
                    script=str(Path(__file__).resolve()), script_sha256=sha_bytes(Path(__file__).read_bytes()),
                    input=str(INPUT.resolve()), input_sha256=sha_bytes(raw), profile_sha256=sha_bytes(profile_raw),
                    cuda_visible_devices=os.environ['CUDA_VISIBLE_DEVICES'], maximum_seconds=LIMIT_SECONDS,
                    read_scope='One saved development JSON, existing profile and stdlib codec source; no images or models.')
    out.mkdir(parents=True, exist_ok=False)
    try:
        data = json.loads(raw)
        profile = json.loads(profile_raw)
        require(profile['code_bits'] == 32, 'requires existing q32 profile')
        require(data['run_id'] == 'c4-v5-two-tier-dev-001', 'wrong development run')
        sys.path.insert(0, str(ROOT))
        from scripts import revised_watermark_v5 as codec
        metadata['codec_sha256'] = {name: sha_bytes((ROOT / 'scripts' / name).read_bytes()) for name in
                                   ('revised_watermark_v5.py', 'revised_watermark_v4.py', 'revised_watermark_v3.py')}
        rows = data['rows']
        clean = defaultdict(list)
        observed = defaultdict(list)
        for row in rows:
            if row.get('axis') == 'clean' and row.get('control') == 'C0':
                clean[row['source_id']].append(row)
            if row.get('axis') == 'T3' and row.get('control') == 'C1':
                observed[row['id']].append(row)
        # Fixed 12-source clean cohort: two clean-only sources still determine parity.
        require(not set(clean) - set(ALL_SOURCES), 'unplanned clean source IDs')
        design_sources = list(ALL_SOURCES[::2])
        evaluation_sources = list(ALL_SOURCES[1::2])
        clean_cache = {}
        clean_inventory = []
        for source in ALL_SOURCES:
            record = dict(source_id=source, split='DESIGN' if source in design_sources else 'EVALUATE',
                          planned_for_T3=source in T3_SOURCES, saved_clean_rows=len(clean[source]))
            try:
                require(len(clean[source]) == 1, 'missing or duplicate clean C0 row')
                clean_cache[source] = feature_code(clean[source][0], profile, codec)
                record['availability'] = 'available'
            except (ValueError, TypeError, KeyError) as error:
                record.update(availability='unavailable', reason=str(error))
            clean_inventory.append(record)
        planned = expected_rows()
        planned_ids = {r['id'] for r in planned}
        # Preserve unexpected retained T3 C1 rows too, explicitly outside the fixed endpoint.
        work = [(p, r) for p in planned for r in (observed.get(p['id']) or [None])]
        work.extend((None, r) for key, group in observed.items() if key not in planned_ids for r in group)
        results = []
        for expected, row in work:
            require(time.perf_counter() - started < LIMIT_SECONDS, 'CPU diagnostic exceeded 540 seconds')
            identity = expected or row
            source = identity['source_id']
            result = {key: identity.get(key) for key in ('id', 'source_id', 'dose', 'strength', 'seed')}
            result.update(split='DESIGN' if source in design_sources else 'EVALUATE' if source in evaluation_sources else 'UNASSIGNED',
                          saved_status=row.get('status') if row else None,
                          saved_errors=row.get('errors', []) if row else [],
                          availability='unavailable', reason=None, planned=expected is not None)
            try:
                require(expected is not None, 'unplanned retained row; preserved outside endpoint')
                require(row is not None, 'planned row absent from saved JSON')
                require(len(observed[row['id']]) == 1, 'duplicate saved row identity')
                require(all(row.get(key) == value for key, value in expected.items()), 'row disagrees with planned metadata')
                require(source in clean_cache, 'unavailable clean C0 reference feature/code')
                a, an, aq, a_saved = clean_cache[source]
                b, bn, bq, b_saved = feature_code(row, profile, codec)
                cosine = max(-1., min(1., math.fsum(x*y for x, y in zip(a, b)) / (an*bn)))
                expected_distance = 32 * math.acos(cosine) / math.pi
                observed_distance = (aq ^ bq).bit_count()
                result.update(availability='available', cosine=cosine, source_q32=f'{aq:08x}', suspect_q32=f'{bq:08x}',
                              source_saved_q32_checked=a_saved, suspect_saved_q32_checked=b_saved,
                              observed_hamming=observed_distance, predicted_uncalibrated=expected_distance,
                              residual=observed_distance-expected_distance,
                              uncalibrated_absolute_error=abs(observed_distance-expected_distance))
            except (ValueError, TypeError, KeyError) as error:
                result['reason'] = str(error)
            results.append(result)
        design = [r for r in results if r['split'] == 'DESIGN' and r['planned']]
        bias_summary = source_weighted(design, 'residual')
        bias = bias_summary['value']
        for result in results:
            if result['availability'] == 'available' and bias is not None:
                prediction = min(32., max(0., result['predicted_uncalibrated'] + bias))
                result.update(predicted_calibrated=prediction,
                              calibrated_absolute_error=abs(result['observed_hamming']-prediction))
        endpoint_rows = [r for r in results if r['planned']]
        summary = summarize(endpoint_rows, design_sources, evaluation_sources)
        before = summary['EVALUATE']['uncalibrated_mae']['value']
        after = summary['EVALUATE']['calibrated_mae']['value']
        reduction = (before-after)/before if before is not None and before > 0 and after is not None else None
        verdict = ('UNDEFINED' if reduction is None else 'KILL_CALIBRATION_PRIORITY' if reduction < .10 else 'RETAIN_FOR_FURTHER_RESEARCH')
        cells = {}
        for dose, strength in [('vae_mode', None), *[('diffusion', s) for s in STRENGTHS]]:
            subset = [r for r in endpoint_rows if r['dose'] == dose and r['strength'] == strength]
            cells[f'{dose}:{strength}'] = summarize(subset, design_sources, evaluation_sources)
        limitations = [
            'Exploratory observed-subset necessary screen; no C/J endpoint or detector threshold changes.',
            'Actual q32 is recomputed with the unchanged v5 profile from existing single-view features; this is not an F5 seven-view claim.',
            'The angular prediction is a theoretical random-hyperplane expectation, not an interval for this fixed projection.',
            'Repeated seeds/doses are correlated within source; equal source weights do not make rows independent.',
            'Missing/failed rows remain in rows.json; available vectors are used regardless of saved embedding/detection status.',
            'Means condition on available rows. Missing units can bias this diagnostic and are not performance failures or successes.',
            'The two clean-only sources set split parity but had no planned T3 attempts; they are not fictional failed attempts.',
            'No held-out pixels/journals, regeneration, encoder, new descriptor, writer optimization, training, or uncertainty calibration.']
        report = dict(fit=dict(additive_bias=bias, source_weighted_residual=bias_summary),
                      split=dict(rule='Numeric ascending 12 clean C0 source IDs; zero-based even DESIGN, odd EVALUATE',
                                 DESIGN=design_sources, EVALUATE=evaluation_sources),
                      summary=summary, T3_cells=cells, relative_evaluation_mae_reduction=reduction,
                      proposal=verdict, proposal_scope='OBSERVED_SUBSET_DIAGNOSTIC_ONLY',
                      criterion='KILL calibration priority if EVALUATE relative source-weighted MAE reduction < 0.10',
                      undefined_reason='No available fit/evaluation or zero uncalibrated MAE' if reduction is None else None,
                      clean_source_inventory=clean_inventory, limitations=limitations)
        write_json(out / 'rows.json', results)
        write_json(out / 'summary.json', report)
        metadata.update(status='complete', proposal=verdict,
                        outputs_sha256={name: sha_bytes((out / name).read_bytes()) for name in ('rows.json', 'summary.json')})
    except Exception as error:
        metadata.update(status='failed', error_type=type(error).__name__, error=str(error))
        raise
    finally:
        metadata['duration_seconds'] = time.perf_counter()-started
        metadata['end_utc'] = datetime.now(timezone.utc).isoformat()
        write_json(out / 'run.json', metadata)


if __name__ == '__main__':
    main()
