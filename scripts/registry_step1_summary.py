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
    """Fixed three-seed endpoint: only at least two observed True values pass."""
    return sum(v is True for v in values) >= 2


def majority_unknown(values):
    """Supplemental optimistic bounds; not the primary attempted-source endpoint."""
    if sum(v is True for v in values) >= 2:
        return True
    if sum(v is False for v in values) >= 2:
        return False
    return None


def summarize(record, rows):
    ids = [s['source_id'] for s in record['sources']]
    if len(ids) != 24 or len(set(ids)) != 24:
        raise ValueError('The fixed step-1 source denominator is 24')
    def observation(model, sid, strength, seed, method, control='C1', owner=ALPHA, rule='C'):
        arm = 'C0' if control == 'C0' else method
        row = rows.get(f'{model}:{sid}:{strength}:{seed}:{arm}', {})
        if row.get('status') != 'ok':
            return None
        return row.get('readouts', {}).get(method, {}).get('endpoints', {}).get(owner, {}).get(rule)
    def source_values(model, strength, method, rule='C'):
        return [majority([observation(model, sid, strength, seed, method, rule=rule) for seed in SEEDS]) for sid in ids]
    def source_bounds(model, strength, method, rule='C'):
        return [majority_unknown([observation(model, sid, strength, seed, method, rule=rule) for seed in SEEDS]) for sid in ids]
    result = dict(denominator=len(ids), outcome=record['outcome'], clean={}, cells={}, comparisons={},
                  quality_matching=False, evidence='exploratory development; no held-out execution; human judgments missing',
                  missing_policy='Primary source majority and paired tests use all 24 attempted sources: at least two observed True seeds pass; unavailable/safety-blocked/missing positive slots are non-successes. This does not assert observed detector rejection. Seed availability and optimistic source bounds remain supplemental; negative calls retain unresolved status.',
                  interpretation='A nonsignificant paired sign test does not establish equality or equivalence. No formal equivalence test or margin was preregistered.',
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
                    supplemental_source_majority_unknown_bounds={rule:availability(source_bounds(model,strength,method,rule), independent=True) for rule in RULES},
                    C_per_source=dict(zip(map(str, ids), source_values(model,strength,method))),
                    c0_A_clustered=clustered_negative([[observation(model,sid,strength,seed,method,'C0',ALPHA,'A') for seed in SEEDS] for sid in ids]),
                    wrong_owner_A_clustered=clustered_negative([[observation(model,sid,strength,seed,method,'C1',BETA,'A') for seed in SEEDS] for sid in ids]))
            for left,right in (('e3-s1','f5-r2'),('e3-s1','v5-r3'),('f5-r2','v5-r3')):
                a,b = source_values(model,strength,left),source_values(model,strength,right)
                test = paired(a,b)
                aa,bb = source_bounds(model,strength,left),source_bounds(model,strength,right)
                test.update(left=left,right=right,planned_pairs=len(ids),unresolved_pairs=0,
                            supplemental_pairs_with_unresolved_seed_majority=sum(x is None or y is None for x,y in zip(aa,bb)),
                            test='one-sided exact paired sign test, left > right; fixed 24 attempted-source Boolean endpoints',
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
            primary_a,primary_b = source_values('sd15',strength,method),source_values('sd21',strength,method)
            a,b = source_bounds('sd15',strength,method),source_bounds('sd21',strength,method)
            lo = sum(v is True for v in a)-sum(v is not False for v in b)
            hi = sum(v is not False for v in a)-sum(v is True for v in b)
            drop = sum(primary_a)-sum(primary_b)
            result['transfer_drop_source_majority_C'][f'{strength}/{method}'] = dict(count=drop, rate=drop/24,
                supplemental_unknown_count_bounds=[lo,hi], supplemental_unknown_rate_bounds=[lo/24,hi/24])
    primary_a,primary_b = source_values('sd21',.2,'e3-s1'),source_values('sd21',.2,'f5-r2')
    difference = sum(primary_a)-sum(primary_b)
    a,b = source_bounds('sd21',.2,'e3-s1'),source_bounds('sd21',.2,'f5-r2')
    lo = sum(v is True for v in a)-sum(v is not False for v in b)
    hi = sum(v is not False for v in a)-sum(v is True for v in b)
    incomplete = []
    for sid in ids:
        for seed in SEEDS:
            for method in ('e3-s1','f5-r2'):
                rid = f'sd21:{sid}:0.2:{seed}:{method}'
                row = rows.get(rid,{})
                if row.get('status') not in ('ok','safety_blocked') or (
                    row.get('status') == 'ok' and not isinstance(observation('sd21',sid,.2,seed,method),bool)):
                    incomplete.append(rid)
    result['method_choice'] = dict(primary='SD2.1 strength .2 source-majority C', denominator=24,
        e3_success=sum(primary_a), f5_success=sum(primary_b), difference=difference,
        supplemental_unknown_difference_bounds=[lo,hi], incomplete_execution_ids=incomplete,
        threshold=3, choice='unresolved' if incomplete else 'e3-s1' if difference >= 3 else 'f5-r2',
        rule='Retain E3 only at fixed-denominator E3-minus-F5 >= 3/24; otherwise choose F5. Completed safety-policy blocks are non-successes. Genuine missing/error execution leaves the method choice unresolved.')
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
