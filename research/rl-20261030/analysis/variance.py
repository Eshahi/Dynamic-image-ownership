"""WP3 saved-number variance and conditional planning; Python stdlib only.

Reads only the normalized development JSONL and its extraction inventory.
Does not open original journals, images, model code, or held-out outcomes.
"""
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from statistics import NormalDist, mean, median
import hashlib
import json
import math

BASE = Path(__file__).resolve().parent
INPUT = BASE / 'dev-records.jsonl'
SEEDS = (12, 13, 14)
INTERNAL = ('f5-r2', 'v5-r3')
DELTA = 0.05
KS = (8, 64, 1024)
RATE = 0.551


def finite(x):
    return isinstance(x, (int, float)) and math.isfinite(x)


def decompose(records, metric):
    """Balanced two-factor decomposition with one observation per source/seed."""
    cells = defaultdict(dict)
    for row in records:
        assert row['seed'] in SEEDS
        assert row['seed'] not in cells[row['source']]
        cells[row['source']][row['seed']] = row.get(metric)
    usable = {s: [float(v[k]) for k in SEEDS] for s, v in cells.items()
              if all(k in v and finite(v[k]) for k in SEEDS)}
    n, r = len(usable), len(SEEDS)
    result = {'sources_total': len(cells), 'sources_complete': n,
              'sources_excluded_incomplete': len(cells)-n,
              'rows_total': len(records),
              'missing_rows_or_values': len(cells)*r-sum(finite(v) for c in cells.values() for v in c.values()),
              'expected_seeds': list(SEEDS)}
    if n < 2:
        return result | {'status': 'insufficient_complete_sources'}
    values = list(usable.values())
    grand = mean(x for row in values for x in row)
    source_means = [mean(row) for row in values]
    seed_means = [mean(row[j] for row in values) for j in range(r)]
    ss_source = r*sum((x-grand)**2 for x in source_means)
    ss_seed = n*sum((x-grand)**2 for x in seed_means)
    ss_residual = sum((values[i][j]-source_means[i]-seed_means[j]+grand)**2
                      for i in range(n) for j in range(r))
    ss_total = sum((x-grand)**2 for row in values for x in row)
    assert math.isclose(ss_total, ss_source+ss_seed+ss_residual, rel_tol=1e-9, abs_tol=1e-9)
    df = {'source': n-1, 'seed': r-1, 'residual': (n-1)*(r-1), 'total': n*r-1}
    ss = {'source': ss_source, 'seed': ss_seed, 'residual': ss_residual, 'total': ss_total}
    ms = {k: ss[k]/df[k] for k in ('source', 'seed', 'residual')}
    components = {'source': (ms['source']-ms['residual'])/r,
                  'seed': (ms['seed']-ms['residual'])/n,
                  'residual_interaction_plus_noise': ms['residual']}
    clipped = {k: max(0.0, v) for k, v in components.items()}
    clipped_sum = sum(clipped.values())
    within = sum((row[j]-source_means[i])**2 for i, row in enumerate(values) for j in range(r))/(n*(r-1))
    assert math.isclose(within, (ss_seed+ss_residual)/(n*(r-1)), rel_tol=1e-9, abs_tol=1e-9)
    result.update({'status': 'ok', 'mean': grand,
                   'minimum': min(x for row in values for x in row),
                   'maximum': max(x for row in values for x in row),
                   'seed_means': dict(zip(map(str, SEEDS), seed_means)),
                   'fixed_ss': ss, 'fixed_ss_fraction': {k: ss[k]/ss_total if ss_total else None for k in ('source', 'seed', 'residual')},
                   'df': df, 'ms': ms, 'random_components_raw': components,
                   'random_components_clipped': clipped,
                   'random_component_fraction_clipped': {k: v/clipped_sum if clipped_sum else None for k, v in clipped.items()},
                   'empirical_pooled_within_source_variance': within,
                   'empirical_overall_sample_variance': ss_total/(n*r-1),
                   'source_mean_sample_variance': sum((x-grand)**2 for x in source_means)/(n-1),
                   'sources_varying_across_seeds': sum(len(set(row)) > 1 for row in values)})
    return result


def sample_n(vdiff, width, gap, k, full_order=False):
    """K means ordered by a minimum gap, at simultaneous error delta=.05.

    Hoeffding uses differences with range length 2*width; Gaussian uses a
    plug-in difference variance and no estimation-uncertainty correction.
    """
    comparisons = k*(k-1)//2 if full_order else k-1
    z = NormalDist().inv_cdf(1-DELTA/comparisons)
    return {'comparisons': comparisons, 'gaussian_z': z,
            'hoeffding_n_per_option': math.ceil(2*width**2*math.log(comparisons/DELTA)/gap**2),
            'gaussian_plugin_n_per_option': max(1, math.ceil(vdiff*z*z/gap**2)),
            'gaussian_zero_observed_variance': vdiff == 0}


def cost(total_rollouts, cached_marks=None):
    # Every row includes one reader and one quality check; fixed writing is excluded.
    cell_seconds = {'R0-0.2': 0.54+1.4+0.25, 'R1-0.1': 0.99+1.4+0.25,
                    'R1-0.2': 1.24+1.4+0.25, 'R3-0.2': 1.98+1.4+0.25}
    result = {}
    for mode, rewrite in [('existing_carrier', 0), ('f5_rewrite_device_equivalent', 122),
                          ('f6_rewrite_unmeasured_low', 361), ('f6_rewrite_unmeasured_high', 723)]:
        seconds_low, seconds_high = min(cell_seconds.values())+rewrite, max(cell_seconds.values())+rewrite
        result[mode] = {'device_hours_low': total_rollouts*seconds_low/3600,
                        'device_hours_high': total_rollouts*seconds_high/3600,
                        'usd_low': total_rollouts*seconds_low*RATE/3600,
                        'usd_high': total_rollouts*seconds_high*RATE/3600}
    if cached_marks is not None:
        for mode, writing in [('f5_candidates_written_once_per_source', 122),
                              ('f6_candidates_written_once_unmeasured_low', 361),
                              ('f6_candidates_written_once_unmeasured_high', 723)]:
            seconds_low = total_rollouts*min(cell_seconds.values())+cached_marks*writing
            seconds_high = total_rollouts*max(cell_seconds.values())+cached_marks*writing
            result[mode] = {'marks_written': cached_marks,
                            'device_hours_low': seconds_low/3600, 'device_hours_high': seconds_high/3600,
                            'usd_low': seconds_low*RATE/3600, 'usd_high': seconds_high*RATE/3600}
    return result


def fmt(x, digits=4):
    return 'NA' if x is None else f'{x:.{digits}f}'


raw = INPUT.read_bytes()
rows = [json.loads(line) for line in raw.splitlines()]
inventory = json.loads((BASE/'data-inventory.json').read_text(encoding='utf-8'))
assert len(rows) == inventory['output']['records']
assert len({(r['cohort'], r['cell'], r['arm'], r['source'], r['seed']) for r in rows}) == len(rows)
grouped = defaultdict(list)
for row in rows:
    grouped[(row['cohort'], row['cell'], row['arm'])].append(row)
results = []
clean = []
planning = []
for (cohort, cell, arm), records in sorted(grouped.items()):
    bits = sorted({r['payload_bits'] for r in records if r['payload_bits'] is not None})
    units = sorted({r['margin_units'] for r in records})
    assert len(units) == 1
    if cell == 'clean':
        clean.append({'cohort': cohort, 'cell': cell, 'arm': arm, 'rows': len(records),
                      'missing_margin': sum(not finite(r['margin']) for r in records),
                      'status': 'no_seed_replicates; excluded from source_seed_decomposition'})
        continue
    for metric in ('margin', 'success'):
        d = decompose(records, metric)
        d.update({'cohort': cohort, 'cell': cell, 'arm': arm, 'metric': metric,
                  'units': units[0] if metric == 'margin' else records[0]['endpoint_label'],
                  'payload_bits_observed': bits})
        results.append(d)
        if d['status'] != 'ok':
            continue
        if metric == 'success':
            width, gaps = 1.0, (0.02, 0.05, 0.1)
        elif arm in INTERNAL:
            # Conservative absolute correlation bound, not observed sample range.
            width, gaps = 2*math.sqrt(320), (0.25, 0.5, 1.0)
        else:
            assert len(bits) == 1
            width, gaps = float(bits[0]), (1.0, 2.0, 5.0)
        for gap in gaps:
            for k in KS:
                v = d['empirical_pooled_within_source_variance']
                planning.append({'cohort': cohort, 'cell': cell, 'arm': arm, 'metric': metric,
                                 'reward_range_width_bound': width, 'gap': gap, 'K': k,
                                 'variance_per_option_plugin': v,
                                 'difference_variance_independent_options_plugin': 2*v,
                                 'best_identification': sample_n(2*v, width, gap, k),
                                 'full_ordering': sample_n(2*v, width, gap, k, True)})

# Pair identical source/seed observations only within each cohort and cell.
# Only F5-v5 margins are comparable units. Presence versus C remains different.
pairs = []
for cohort, cell in sorted({(r['cohort'], r['cell']) for r in rows if r['cell'] != 'clean'}):
    arms = sorted({r['arm'] for r in rows if r['cohort'] == cohort and r['cell'] == cell})
    for a, b in combinations(arms, 2):
        by_a = {(r['source'], r['seed']): r for r in grouped[(cohort, cell, a)]}
        by_b = {(r['source'], r['seed']): r for r in grouped[(cohort, cell, b)]}
        metrics = ['success'] + (['margin'] if a in INTERNAL and b in INTERNAL else [])
        for metric in metrics:
            keys = sorted(set(by_a) | set(by_b))
            diff_rows = []
            for source, seed in keys:
                va, vb = by_a.get((source, seed), {}).get(metric), by_b.get((source, seed), {}).get(metric)
                diff_rows.append({'source': source, 'seed': seed,
                                  'value': float(va)-float(vb) if finite(va) and finite(vb) else None})
            d = decompose(diff_rows, 'value')
            d.update({'cohort': cohort, 'cell': cell, 'arm_a': a, 'arm_b': b, 'metric': metric,
                      'endpoint_comparability': 'same C endpoint' if a in INTERNAL and b in INTERNAL else
                      'heterogeneous C/presence or different presence payload; not ownership efficacy ranking'})
            if d['status'] == 'ok':
                complete_sources = {s for s in {r['source'] for r in diff_rows}
                                    if all(any(r['source'] == s and r['seed'] == seed and finite(r['value'])
                                               for r in diff_rows) for seed in SEEDS)}
                da = decompose([r for r in by_a.values() if r['source'] in complete_sources], metric)
                db = decompose([r for r in by_b.values() if r['source'] in complete_sources], metric)
                independent_v = da['empirical_pooled_within_source_variance']+db['empirical_pooled_within_source_variance']
                paired_v = d['empirical_pooled_within_source_variance']
                d['independent_difference_variance_matched_sources'] = independent_v
                d['paired_to_independent_variance_ratio'] = paired_v/independent_v if independent_v else None
                gap = 0.5 if metric == 'margin' else 0.05
                width = 2*math.sqrt(320) if metric == 'margin' else 1
                d['paired_planning_at_gap'] = {'gap': gap, 'K_illustrations': [
                    {'K': k, **sample_n(paired_v, width, gap, k)} for k in KS]}
            pairs.append(d)

anchors = [('stage2_union', 'R0-0.2', 'f5-r2'), ('stage2_union', 'R1-0.2', 'f5-r2'),
           ('phase_a', 'R1-0.2', 'f5-r2'), ('stage2_union', 'R1-0.2', 'vine-r')]
cost_examples = []
gradient_examples = []
for item in planning:
    if (item['cohort'], item['cell'], item['arm']) not in anchors:
        continue
    gap = 0.5 if item['metric'] == 'margin' and item['arm'] in INTERNAL else 2.0 if item['metric'] == 'margin' else 0.05
    if item['gap'] != gap:
        continue
    for method in ('gaussian_plugin', 'hoeffding'):
        n = item['best_identification'][method+'_n_per_option']
        cost_examples.append({**{k: item[k] for k in ('cohort', 'cell', 'arm', 'metric', 'K', 'gap')},
                              'method': method, 'n_per_option': n, 'total_rollouts': n*item['K'],
                              'scope': 'one-source homogeneous seed-variance illustration; multiply by 60 for all 60 sources',
                              'cost': cost(n*item['K'], cached_marks=item['K'])})
for d in results:
    if (d['cohort'], d['cell'], d['arm']) not in anchors[:2]:
        continue
    v = d['empirical_pooled_within_source_variance']
    target = 0.1 if d['metric'] == 'margin' else 0.01
    for dimension in KS:
        for exploration in (0.1, 1.0):
            n = max(1, math.ceil(dimension*v/(exploration**2*target**2)))
            gradient_examples.append({'cohort': d['cohort'], 'cell': d['cell'], 'arm': d['arm'],
                                      'metric': d['metric'], 'measured_fixed_arm_reward_variance': v,
                                      'dimension': dimension, 'exploration_sd': exploration,
                                      'target_trace_rms': target, 'n_noise_only_conditional': n,
                                      'zero_observed_variance_no_information': v == 0, 'cost': cost(n)})

out = {'provenance': {'input': str(INPUT), 'input_sha256': hashlib.sha256(raw).hexdigest(),
                      'records': len(rows), 'PHASE_B_JOURNALS': 'off',
                      'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
       'assumptions': {
           'decomposition': 'Complete-source balanced fixed source x fixed seed SS. Raw ANOVA variance components assume random independent source and seed effects with homoscedastic residual; negative estimates retained and also clipped for descriptive fractions. Residual includes interaction and unexplained noise.',
           'sampling_scope': 'Only three prescribed seeds. Within-source variance is empirical across those seeds, not established variance under new actions, a policy, or fresh sources. Shared sources across cohorts; cohorts never pooled.',
           'hoeffding': 'DERIVED: bounded independent rounds; each option range width <=B; unique best separated by gap or every ordering pair separated by gap. D_ij range width <=2B. n >= 2 B^2 log(M/delta)/gap^2, M=K-1 or K(K-1)/2. Simultaneous error <=delta, conditional on assumptions. K*n reward evaluations.',
           'gaussian': 'DERIVED plug-in only: n >= z_(1-delta/M)^2 * Var(D)/gap^2. Independent equal-variance option approximation Var(D)=2v; measured pairs use empirical Var(D). No finite-sample guarantee, variance uncertainty, or future-option transfer guarantee. Zero observed variance does not imply zero true variance.',
           'reward_bounds': 'Binary width1. Internal normalized-correlation absolute bound sqrt320 yields conservative width2sqrt320 with fixed threshold; this does not rely on observed min/max or assert nonnegative decoded scores. External match count width=payload bits. Margins are not probabilities and are not interchangeable with C/J.',
           'paired_CRN': 'Same source/seed within cohort can provide empirical paired differences. CRN benefit is measured for retained arms only; same numeric seed does not establish identical random streams or positive covariance for new methods. Bounds allow dependence among options within a round, require independence across rounds.',
           'continuous_gradient': 'Not identifiable without actions and score/log-gradient vectors. Conditional toy: Gaussian mean policy a=theta+sigma*z, z~N(0,I_d); zero-mean reward noise epsilon independent of z with Var(epsilon)=v, baseline removes conditional mean. Then trace Cov(mean epsilon*z/sigma)=d*v/(n*sigma^2). This is only an additive noise term, not total policy-gradient variance, learning cost, or a usable policy return estimate.',
           'cost': 'SOURCE BRIEF seconds: regeneration .54/.99/1.24/1.98 + reader1.4 + quality.25; price .551 USD/device-hour. F5 732s shard latency /6 approximately122 device-equivalent seconds. F6 361-723 unmeasured planning seconds per mark. Conversion assumes those timing scopes add and hardware/price stay comparable; no new measurements.'},
       'cost_anchors': {'regeneration_seconds': {'R0-0.2': 0.54, 'R1-0.1': 0.99, 'R1-0.2': 1.24, 'R3-0.2': 1.98},
                        'reader_seconds': 1.4, 'quality_seconds': 0.25, 'usd_per_device_hour': RATE,
                        'f5_shard_wall_latency_seconds': 732, 'f5_approx_device_equivalent_seconds': 122,
                        'f6_unmeasured_seconds_range': [361, 723]},
       'clean_exclusions': clean, 'decomposition': results, 'paired_differences': pairs,
       'ranking_planning': planning, 'ranking_cost_examples': cost_examples,
       'continuous_gradient_noise_only_examples': gradient_examples}
(BASE/'variance-results.json').write_text(json.dumps(out, indent=2, allow_nan=False)+'\n', encoding='utf-8')

lines = ['# WP3 source/seed variance and conditional sample cost', '',
         '**Status:** descriptive analysis of saved development numbers only. `PHASE_B_JOURNALS=off`. No images, original journals, F6 outcomes, or held-out per-source records were opened. No policy was fit or evaluated.', '',
         '## Evidence and meanings', '',
         '- **MEASURED:** `dev-records.jsonl`, SHA-256 `'+out['provenance']['input_sha256']+'`; '+str(len(rows))+' rows. Extraction provenance and missing statuses are in `data-inventory.json`.',
         '- **SOURCE:** `../context/wp1-reader-semantics.md`: internal margin is decoded normalized correlation minus decoded threshold; external margin is matching bits minus its threshold. The generic branch-selected margin is not substituted. Binary success is content-compatible C for F5/v5 and message presence for WAM/VINE-R; these endpoints differ.',
         '- **SOURCE:** `../BRIEF.md`, WP3 and compute anchors at lines 97-102. Cost figures below reuse those supplied measurements and unmeasured F6 anchors; they are not new timing observations.',
         '- The cohorts reuse the same 60 development sources under different kernels/conditions and are analyzed separately. Clean rows have no seed replication and are excluded from the two-way decomposition.', '',
         '## Decomposition', '',
         '**DERIVED:** with N complete sources and r=3 seeds, SS_source=r sum_i(mean_i-grand)^2; SS_seed=N sum_j(mean_j-grand)^2; SS_residual=sum_ij(y_ij-mean_i-mean_j+grand)^2. The sum equals total SS. Degrees of freedom are N-1, 2 and 2(N-1). Random-component method-of-moments estimates are (MS_source-MS_residual)/3, (MS_seed-MS_residual)/N and MS_residual. Their random-effects interpretation requires independent exchangeable source/seed effects and homogeneous residual variance. The JSON retains negative estimates and separately clips them to zero for descriptive fractions; clipping does not create an unbiased estimator.', '',
         'The table shows fixed SS fractions, not population variance fractions. Residual includes source-by-seed interaction and noise: one observation per source/seed cannot separate them. Pooled within-source variance is sum_i,j(y_ij-mean_i)^2/[N(3-1)] = (SS_seed+SS_residual)/[2N]. No p-values are warranted from three fixed seeds alone.', '',
         '| Cohort | Cell | Arm | Complete / total | Missing | Mean margin | Source SS % | Seed SS % | Residual SS % | Within-source variance |',
         '|---|---|---|---:|---:|---:|---:|---:|---:|---:|']
for d in results:
    if d['metric'] != 'margin':
        continue
    if d['status'] != 'ok':
        lines.append('| '+' | '.join([d['cohort'], d['cell'], d['arm'], f"{d['sources_complete']}/{d['sources_total']}",
                                     str(d['missing_rows_or_values']), 'NA', 'NA', 'NA', 'NA', 'NA'])+' |')
        continue
    f = d['fixed_ss_fraction']
    lines.append('| '+ ' | '.join([d['cohort'], d['cell'], d['arm'], f"{d['sources_complete']}/{d['sources_total']}", str(d['missing_rows_or_values']),
                                 fmt(d['mean']), *(fmt(None if f[k] is None else 100*f[k], 1) for k in ('source','seed','residual')),
                                 fmt(d['empirical_pooled_within_source_variance'])])+' |')
lines += ['', '**MEASURED missingness:** WAM margins are absent on 166/180 rows at R1 .4 in each cohort and 155/180 rows at stage2 R1-smooth .2; each has only one complete source and is not decomposed. Numeric margin availability is therefore not the same as successful row status. WAM presence can remain defined when a matched-bit score is absent. Other incomplete sources and their numeric missing counts appear in the table and JSON.', '',
          '**MEASURED:** across the normalized WAM rows, 1,460 absent numeric margins coexist with an observed presence=False; nine further absent margins accompany unresolved calls. Thus no numeric score is not the same as no binary outcome. **SOURCE, reported by the integration lead after its code inspection:** `scripts/encoder_transfer_test.py:62-65` maps decoded=None to matches=None and present=False, and `scripts/journal_wam_probe.py:90` produces decoded=None for an empty positive mask. This agent did not separately open those code files. There is no justified arbitrary numeric floor to impute for this structural case; complete-case margin summaries select the subset with a decoded score.', '',
          '**JUDGMENT:** large source SS shows heterogeneity of retained outcomes, not that a feature available before marking predicts it, not that the best action changes by source, and not that a new policy can improve it. Large residual need not be pure seed noise. Missing outcomes are excluded only by complete-source restriction and are counted; no failure was silently converted to a numeric margin. Complete-case statistics can be biased if missingness depends on difficulty.', '',
          '## Simultaneous ranking plans', '',
          '**DERIVED, conditional guarantee:** assume K fixed options, independently sampled rounds, rewards each having range width at most B, and minimum true gap Delta. For best-option identification M=K-1; for all ranks M=K(K-1)/2. For each required pair, differences lie in a range of width at most 2B; Hoeffding plus a union bound gives n >= 2 B^2 log(M/0.05)/Delta^2 rounds per option. Total reward evaluations = K*n. This is a 95% simultaneous probability-of-error bound under those assumptions; it does not need the measured variance. The internal conservative range is 2 sqrt(320), binary range1, external matched-bit range equal to payload length. Threshold shifts do not change width when fixed per option.', '',
          '**DERIVED, plug-in approximation only:** n >= z_(1-0.05/M)^2 Var(D)/Delta^2. Independent equal-variance future options are illustrated with Var(D)=2v using each retained arm/cell within-source variance v. The normal approximation, fixed-arm-to-new-option transfer, seed exchangeability and ignoring variance uncertainty are substantive assumptions. With three seeds, rare binary failures or a small mean gap make this especially fragile; zero empirical variance is no certificate of a constant future reward. Gap sensitivity and full ordering are in the JSON: internal margins .25/.5/1, binary .02/.05/.1, external matching bits 1/2/5.', '',
          'All table n below identify the best option, at nominal 95% simultaneous confidence. Every rollout/cost table is **per one source**, using pooled within-source variance only as a homogeneous-variance approximation. A full 60-source design multiplies those totals by 60, with 60*K candidate marks when marks are cached. These totals do not estimate fresh-source generalization. Reusing the three saved seeds does not provide additional independent rounds.', '',
          '| Cohort | Cell | Arm | Reward / gap | K | Gaussian n/option | Hoeffding n/option | Gaussian total rollouts | Existing carrier hours / USD | F5 candidates cached hours / USD |',
          '|---|---|---|---|---:|---:|---:|---:|---|---|']
for item in planning:
    if (item['cohort'], item['cell'], item['arm']) not in anchors[:3] or item['gap'] != (0.5 if item['metric'] == 'margin' else 0.05):
        continue
    p = item['best_identification']; n = p['gaussian_plugin_n_per_option']; costs = cost(n*item['K'], cached_marks=item['K'])
    def cost_text(mode):
        c = costs[mode]
        return f"{c['device_hours_low']:.2f}–{c['device_hours_high']:.2f} / ${c['usd_low']:.2f}–{c['usd_high']:.2f}"
    lines.append('| '+' | '.join([item['cohort'], item['cell'], item['arm'], f"{item['metric']} / {item['gap']}", str(item['K']),
                                str(n)+(' [zero variance]' if p['gaussian_zero_observed_variance'] else ''), str(p['hoeffding_n_per_option']), str(n*item['K']),
                                cost_text('existing_carrier'), cost_text('f5_candidates_written_once_per_source')])+' |')
lines += ['', 'Costs use 2.19–3.63 seconds per regeneration/reader/quality rollout, 124.19–125.63 seconds if each rollout rewrites an F5 mark, and $0.551/device-hour. The 732-second F5 mark figure is observed shard latency with six simultaneous shards; 122 seconds is its approximate device-equivalent amortization, not serial mark latency. Throughput and per-request latency are distinct. Reader/quality overheads and native regeneration timers may have different concurrency scopes; additive costs are planning approximations.', '',
          'For K fixed candidate marks reused over n seeds, the per-source cost is **K*w + K*n*feedback**, with w approximately122 device-equivalent seconds for F5. Across 60 sources it is 60 times that quantity. If each continuous action changes the mark, the per-source cost instead becomes K*n*(w+feedback) (or total policy rollouts times w+feedback); that is a separate rewrite-every-rollout scenario in the JSON. Existing-carrier scenarios exclude already-paid writing entirely. F6 writing is unmeasured: conditional costs use w=361–723 seconds; rewriting every rollout gives 363.19–726.63 seconds total. No observed F6 cost or result is claimed. JSON provides cached-mark and rewrite-every-rollout scenarios for every selected planning example.', '',
          '## Paired common-random-number comparisons', '',
          '**MEASURED/DESCRIPTIVE:** pair the retained arms on the same source and prescribed seed within each cohort; recompute complete-source differences and the within-source variance of those differences. The JSON contains every pair and the ratio to Var(A)+Var(B) on exactly the same retained complete sources. Ratio below one suggests variance reduction for these particular paired outcomes; ratio above one suggests an increase. Same numeric seeds alone do not establish identical random draws across models or this benefit for new actions. F5/v5 C and normalized-correlation margins can be compared; C-versus-presence and different external payloads cannot be called an ownership-efficacy ranking.', '',
          '| Cohort | Cell | Pair | Metric | Paired variance | Independent variance | Ratio |',
          '|---|---|---|---|---:|---:|---:|']
for p in pairs:
    if p['arm_a'] == 'f5-r2' and p['arm_b'] == 'v5-r3' and p['cell'] in ('R0-0.2','R1-0.2'):
        lines.append('| '+' | '.join([p['cohort'],p['cell'],'F5 − v5',p['metric'],fmt(p['empirical_pooled_within_source_variance']),
                                    fmt(p['independent_difference_variance_matched_sources']),fmt(p['paired_to_independent_variance_ratio'])])+' |')
lines += ['', '## Continuous-policy score-function gradients', '',
          '**Unidentified from these logs:** Var[(R-b) grad_theta log pi(a|x)] requires sampled actions, their policy probabilities/log gradients, their association with rewards and the baseline. Fixed-arm outcomes supply none of these, so there is no measured policy-gradient variance, return estimate, sample complexity or improvement probability.', '',
          '**DERIVED scale-conditional illustration:** let a=theta+sigma*z, z~N(0,I_d). Suppose an oracle baseline removes the mean and the remaining additive reward noise epsilon is independent of z, with variance v equal to a retained fixed-arm within-source variance. For g=epsilon*z/sigma, trace Cov(mean_n g)=d*v/(n*sigma^2), hence noise-only trace RMS <=tau requires n >= d*v/(sigma^2*tau^2). This is neither the complete gradient variance nor the gradient signal, and ignores action-dependent reward, nonlinear parameterization, correlated trajectory credit, baseline-estimation error and all learning iterations. Changing parameter/action units changes sigma and tau. Under a general policy the corresponding independent-noise term is v*trace(Fisher information)/n.', '',
          'The JSON illustrates d=8/64/1024, sigma=.1/1, and tau=.1 correlation-gradient units or .01 binary-gradient units, for F5 R0 .2 and R1 .2. Each entry is labelled noise-only conditional and converted with the same costs. In particular a binary floor can yield v=0 and a useless zero-noise expression while also supplying no usable gradient signal.', '',
          '## Reproduction and checks', '',
          'Exact command (PowerShell, from the worktree):', '',
          '```powershell',
          "& 'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/venv/Scripts/python.exe' -I 'research/rl-20261030/analysis/variance.py'",
          '```', '',
          'The script asserts normalized-record count/unique source-cell-seed-arm keys, three-seed design, SS additivity and equivalence of the two within-source-variance calculations. The script writes only `variance-results.json` and this note. No dependency outside Python stdlib is imported.']
(BASE/'variance-note.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
print(json.dumps({'records': len(rows), 'decompositions': len(results), 'paired_decompositions': len(pairs),
                  'ranking_plans': len(planning), 'cost_examples': len(cost_examples),
                  'gradient_noise_examples': len(gradient_examples), 'output_bytes': (BASE/'variance-results.json').stat().st_size}))
