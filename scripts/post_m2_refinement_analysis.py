"""Descriptive, source-clustered analysis of the fixed post-M2 paired probe.

No scientific imports, tuning, image access, or held-out observations.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import statistics

ALPHA = 'qim-pilot-owner-alpha'
BETA = 'qim-pilot-owner-beta'
IDS = (1675, 4795, 6012, 25394, 80932, 109798, 134882, 147498,
       177015, 190676, 468505, 499768)
SEEDS = (6, 7, 8)


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def strict(m):
    return bool(m and (m.get('psnr_infinite') is True or
        (m.get('psnr_db') is not None and m['psnr_db'] > 35)) and
        m.get('ssim_rgb', 0) > .9 and m.get('lpips', 1) < .1)


def describe(values):
    v = [float(x) for x in values if x is not None]
    return dict(n=len(v), min=min(v) if v else None,
        median=statistics.median(v) if v else None, max=max(v) if v else None,
        mean=statistics.mean(v) if v else None)


def analyze(run, rows):
    lookup = {}
    for r in rows:
        key = (r['source_id'], r['arm'], r['condition'], r.get('strength'), r.get('seed'))
        if key in lookup:
            raise ValueError(f'Duplicate logical row: {key}')
        lookup[key] = r
    expected = {(sid, arm, 'clean', None, None) for sid in IDS for arm in ('I', 'E', 'C0')}
    expected |= {(sid, arm, 't3', strength, seed) for sid in IDS
        for arm in ('I', 'E', 'C0') for strength in (.1, .2) for seed in SEEDS}
    if set(lookup) != expected:
        raise ValueError('Full preallocated fixed inventory required')

    def row(sid, arm, strength=None, seed=None):
        return lookup[(sid, arm, 'clean' if strength is None else 't3', strength, seed)]

    def ep(r, owner=ALPHA):
        return r.get('endpoints', {}).get(owner)

    def majority(sid, arm, strength, endpoint):
        e = [ep(row(sid, arm, strength, seed)) for seed in SEEDS]
        available = [x for x in e if x is not None]
        successes = sum(bool(x[endpoint]) for x in available)
        missing = 3-len(available)
        return dict(successes=successes, missing=missing,
            lower=int(successes >= 2), upper=int(successes + missing >= 2))

    result = dict(schema='post-m2-refinement-analysis-v1', exploratory=True,
        independent_unit='source; three seeds are repeated measurements',
        source_count=12, inventory=dict(planned=len(expected), observed=len(rows),
            statuses=dict(Counter(r['status'] for r in rows)),
            reused_rows=sum(bool(r.get('reuse_of')) for r in rows)),
        run_outcome=run['outcome'], clean={}, comparisons={}, negatives={})
    eligibility = {}
    for arm in ('I', 'E'):
        clean = [row(sid, arm) for sid in IDS]
        eligibility[arm] = {sid: bool(ep(row(sid, arm)) and
            all(ep(row(sid, arm))[k] for k in ('Q', 'H', 'F')) and
            strict(row(sid, arm).get('quality_source'))) for sid in IDS}
        result['clean'][arm] = dict(
            strict_quality=sum(strict(r.get('quality_source')) for r in clean),
            exact_Q_H_F=sum(bool(ep(r) and all(ep(r)[k] for k in ('Q','H','F'))) for r in clean),
            jointly_eligible=sum(eligibility[arm].values()),
            quality={metric: describe([r.get('quality_source',{}).get(metric) for r in clean])
                     for metric in ('psnr_db','ssim_rgb','lpips')})
    for strength in (.1, .2):
        comparison = dict(endpoints={}, per_seed={}, sources=[], quality={})
        for endpoint in ('J', 'Q', 'S', 'H', 'F'):
            pairs = [(majority(sid,'I',strength,endpoint), majority(sid,'E',strength,endpoint)) for sid in IDS]
            counts = Counter()
            for i,e in pairs:
                if i['missing'] or e['missing']:
                    counts['unresolved_pair'] += 1
                else:
                    counts['both' if i['lower'] and e['lower'] else
                           'I_only' if i['lower'] else 'E_only' if e['lower'] else 'neither'] += 1
            comparison['endpoints'][endpoint] = dict(
                I_majority_lower=sum(i['lower'] for i,e in pairs),
                I_majority_upper=sum(i['upper'] for i,e in pairs),
                E_majority_lower=sum(e['lower'] for i,e in pairs),
                E_majority_upper=sum(e['upper'] for i,e in pairs),
                difference_lower=sum(e['lower']-i['upper'] for i,e in pairs),
                difference_upper=sum(e['upper']-i['lower'] for i,e in pairs),
                complete_pairs=dict(counts),
                I_seed_successes=sum(i['successes'] for i,e in pairs),
                E_seed_successes=sum(e['successes'] for i,e in pairs),
                I_unavailable_seeds=sum(i['missing'] for i,e in pairs),
                E_unavailable_seeds=sum(e['missing'] for i,e in pairs))
        common = [sid for sid in IDS if eligibility['I'][sid] and eligibility['E'][sid]]
        comparison['common_clean_diagnostic'] = dict(n=len(common),
            I_J_majority=sum(majority(s,'I',strength,'J')['lower'] for s in common),
            E_J_majority=sum(majority(s,'E',strength,'J')['lower'] for s in common))
        comparison['joint_clean_eligible_J'] = {arm:sum(eligibility[arm][sid] *
            majority(sid,arm,strength,'J')['lower'] for sid in IDS) for arm in ('I','E')}
        for seed in SEEDS:
            comparison['per_seed'][str(seed)] = {arm:dict(
                available=sum(ep(row(sid,arm,strength,seed)) is not None for sid in IDS),
                J=sum(bool(ep(row(sid,arm,strength,seed)) and
                           ep(row(sid,arm,strength,seed))['J']) for sid in IDS)) for arm in ('I','E')}
        for sid in IDS:
            comparison['sources'].append(dict(source_id=sid,
                I=majority(sid,'I',strength,'J'), E=majority(sid,'E',strength,'J')))
        for arm in ('I','E','C0'):
            group = [row(sid,arm,strength,seed) for sid in IDS for seed in SEEDS]
            comparison['quality'][arm] = {base:{metric:describe([
                r.get(base,{}).get(metric) for r in group]) for metric in ('psnr_db','ssim_rgb','lpips')}
                for base in ('quality_source','quality_marked')}
            comparison['quality'][arm]['lpips_proxy_coverage'] = {
                str(cap):dict(eligible=sum(r.get('quality_marked',{}).get('lpips',float('inf')) <= cap for r in group),
                    assessed=sum('lpips' in r.get('quality_marked',{}) for r in group),planned=36)
                for cap in (.2,.3)}
            comparison['quality'][arm]['raw_coded_errors'] = describe([
                ep(r).get('raw_coded_bit_errors') if ep(r) else None for r in group])
        result['comparisons'][str(strength)] = comparison
    for condition in ('clean', '.1', '.2'):
        strength = None if condition == 'clean' else float(condition)
        for arm,owner in (('C0',ALPHA),('C0',BETA),('I',BETA),('E',BETA)):
            families = []
            for sid in IDS:
                rr = [row(sid,arm)] if strength is None else [row(sid,arm,strength,s) for s in SEEDS]
                observed = [ep(r,owner) for r in rr if ep(r,owner) is not None]
                event = any(e['A'] for e in observed)
                missing = len(rr)-len(observed)
                families.append(dict(source_id=sid,event=event,unresolved=bool(missing and not event),
                    observed_calls=len(observed),unavailable_calls=missing))
            events=sum(x['event'] for x in families)
            unresolved=sum(x['unresolved'] for x in families)
            result['negatives'][f'{condition}/{arm}/{owner}'] = dict(
                source_events=events,unresolved_sources=unresolved,
                fixed_cohort_rate_bracket=[events/12,(events+unresolved)/12],
                observed_calls=sum(x['observed_calls'] for x in families),
                unavailable_calls=sum(x['unavailable_calls'] for x in families), sources=families)
    j1=result['comparisons']['0.1']['endpoints']['J']
    j2=result['comparisons']['0.2']['endpoints']['J']
    criteria = dict(complete_run=run['outcome']=='completed',
        E_clean_quality_and_QHF_all=result['clean']['E']['jointly_eligible']==12,
        no_observed_negative_event=all(x['source_events']==0 for x in result['negatives'].values()),
        J_point_majority_gain_at_least_two_at_02=j2['E_majority_lower']-j2['I_majority_lower']>=2,
        J_point_majority_nondecreasing_at_01=j1['E_majority_lower']>=j1['I_majority_lower'],
        J_net_seed_positive_at_02=j2['E_seed_successes']>j2['I_seed_successes'],
        J_net_seed_nondecreasing_at_01=j1['E_seed_successes']>=j1['I_seed_successes'],
        J_majority_gain_survives_adverse_missingness_at_02=j2['difference_lower']>0)
    result['decision'] = dict(criteria=criteria, useful_screen=all(criteria.values()),
        outcome='useful_screen_requires_fresh_equal_distortion_study' if all(criteria.values()) else
        'incomplete_no_advancement_claim' if run['outcome']!='completed' else 'no_decisive_added_value',
        human_admissibility='unassessed', population_claim=False)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run-dir',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    run=read(args.run_dir/'run.json')
    rows=[json.loads(x) for x in (args.run_dir/'rows.jsonl').read_text().splitlines() if x.strip()]
    result=analyze(run,rows)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps(result['decision']))


if __name__=='__main__':
    main()
