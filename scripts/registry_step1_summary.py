"""Frozen-predicate analysis of the step-1 journal; no image/model access."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import median

from m1b_e3_s1_analysis import availability, clustered_negative, holm, paired
from registry_step1_transfer import ALPHA, BETA, METHODS, SEEDS, STRENGTHS, journal, read, write

RULES = ('S', 'C', 'Q', 'J', 'H', 'F', 'A')
MODELS = ('sd15', 'sd21')


def majority(values):
    """At least two seeds, with explicit unresolved rather than adverse imputation."""
    if sum(v is True for v in values) >= 2:
        return True
    if sum(v is False for v in values) >= 2:
        return False
    return None


def summarize(record, rows):
    ids = [s['source_id'] for s in record['sources']]
    def observation(model, sid, strength, seed, method, control='C1', owner=ALPHA, rule='C'):
        arm = 'C0' if control == 'C0' else method
        row = rows.get(f'{model}:{sid}:{strength}:{seed}:{arm}', {})
        if row.get('status') != 'ok':
            return None
        return row.get('readouts', {}).get(method, {}).get('endpoints', {}).get(owner, {}).get(rule)
    def source_values(model, strength, method, rule='C'):
        return [majority([observation(model, sid, strength, seed, method, rule=rule) for seed in SEEDS]) for sid in ids]
    result = dict(denominator=len(ids), outcome=record['outcome'], clean={}, cells={}, comparisons={},
                  quality_matching=False, evidence='exploratory development; no held-out execution; human judgments missing',
                  missing_policy='Unresolved shown with fixed-denominator bounds. Missing is never an observed failure.',
                  exact_H_note='F5 h uses operational bootstrap decoded h, E3 uses its supplied h, v5 uses native intended h; these exact-H targets differ.')
    for method in METHODS:
        clean = [rows.get(f'clean:{sid}:{method}:C1', {}) for sid in ids]
        ok = [r for r in clean if r.get('status') == 'ok']
        metrics = [r['quality'] for r in ok]
        result['clean'][method] = dict(planned=len(ids), observed=len(ok), strict_quality=sum(r['strict_quality'] for r in ok),
            psnr_min=min((r['psnr_db'] for r in metrics if not r.get('psnr_infinite')), default=None),
            ssim_min=min((r['ssim_rgb'] for r in metrics), default=None), lpips_max=max((r['lpips'] for r in metrics), default=None),
            lpips_median=median([r['lpips'] for r in metrics]) if metrics else None,
            embedding_seconds_median=median([r['embedding_seconds'] for r in ok]) if ok else None,
            per_source=[dict(source_id=r.get('source_id'), quality=r.get('quality'), embedding_seconds=r.get('embedding_seconds'),
                             embedding_time_basis=r.get('embedding_time_basis'), endpoints=r.get('endpoints')) for r in clean],
            endpoint_counts={rule:availability([r.get('endpoints', {}).get(ALPHA, {}).get(rule) if r.get('status') == 'ok' else None for r in clean]) for rule in RULES})
    tests = []
    for model in MODELS:
        for strength in STRENGTHS:
            key = f'{model}/{strength}'
            cell = result['cells'][key] = {}
            for method in METHODS:
                cell[method] = dict(
                    seeds={rule:availability([observation(model,sid,strength,seed,method,rule=rule) for sid in ids for seed in SEEDS]) for rule in RULES},
                    source_majority={rule:availability(source_values(model,strength,method,rule), independent=True) for rule in RULES},
                    C_per_source=dict(zip(map(str, ids), source_values(model,strength,method))),
                    c0_A_clustered=clustered_negative([[observation(model,sid,strength,seed,method,'C0',ALPHA,'A') for seed in SEEDS] for sid in ids]),
                    wrong_owner_A_clustered=clustered_negative([[observation(model,sid,strength,seed,method,'C1',BETA,'A') for seed in SEEDS] for sid in ids]))
            for left,right in (('e3-s1','f5-r2'),('e3-s1','v5-r3'),('f5-r2','v5-r3')):
                a,b = source_values(model,strength,left),source_values(model,strength,right)
                # A paired sign test needs both observations. Keep denominator 24 explicit.
                observed = [(x,y) for x,y in zip(a,b) if x is not None and y is not None]
                test = paired([v[0] for v in observed],[v[1] for v in observed])
                test.update(left=left,right=right,planned_pairs=len(ids),unresolved_pairs=len(ids)-len(observed),
                            test='one-sided exact paired sign test, left > right; available pairs only',
                            left_success=test.pop('e3_success'),right_success=test.pop('v5_success'),
                            left_only=test.pop('e3_only'),right_only=test.pop('v5_only'),
                            left_interval=test.pop('e3_interval'),right_interval=test.pop('v5_interval'))
                result['comparisons'][f'{key}/{left}:{right}'] = test
                tests.append(test)
    adjusted = holm([t['exact_mcnemar_one_sided_p'] for t in tests])
    for test,p in zip(tests,adjusted):
        test['holm_p_18_tests'] = p
    result['transfer_drop_source_majority_C'] = {}
    for strength in STRENGTHS:
        for method in METHODS:
            a,b = source_values('sd15',strength,method),source_values('sd21',strength,method)
            lo = sum(v is True for v in a)-sum(v is not False for v in b)
            hi = sum(v is not False for v in a)-sum(v is True for v in b)
            result['transfer_drop_source_majority_C'][f'{strength}/{method}'] = dict(count_bounds=[lo,hi], rate_bounds=[lo/len(ids),hi/len(ids)])
    a,b = source_values('sd21',.2,'e3-s1'),source_values('sd21',.2,'f5-r2')
    lo = sum(v is True for v in a)-sum(v is not False for v in b)
    hi = sum(v is not False for v in a)-sum(v is True for v in b)
    result['method_choice'] = dict(primary='SD2.1 strength .2 source-majority C', difference_bounds=[lo,hi],
        threshold=3, choice='e3-s1' if lo >= 3 else 'f5-r2' if hi < 3 else 'unresolved',
        rule='Retain E3 only at E3-minus-F5 >= 3/24; otherwise choose F5. Unresolved evidence cannot be silently imputed.')
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run-dir', type=Path, required=True)
    p.add_argument('--output', type=Path)
    args = p.parse_args()
    result = summarize(read(args.run_dir/'run.json'),journal(args.run_dir/'rows.jsonl'))
    write(args.output or args.run_dir/'summary.json',result)
    print(json.dumps(result['method_choice']))


if __name__ == '__main__':
    main()
