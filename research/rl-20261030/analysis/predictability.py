"""Post-hoc source-LOO prediction from saved numeric development records; stdlib only.

Fixed before this analysis executes: ridge sum-squared-error penalty lambda=1,
unpenalized intercept, within-training-fold mean imputation and standardization,
all-feature primary model and every individual feature as descriptive diagnostics.
No hyperparameter/model/feature selection, seed-wise CV, image reads or ML imports.
"""
import collections
import hashlib
import json
import math
from pathlib import Path
import statistics

HERE = Path(__file__).resolve().parent
INPUT = HERE / 'dev-records.jsonl'
INTERNAL = ('f5-r2', 'v5-r3')
QUALITY = ('quality.psnr_db', 'quality.ssim_rgb', 'quality.lpips')
READER = tuple(f'{c}_{p}_margin' for c in ('semantic', 'instance')
               for p in ('decoded', 'recomputed'))
EMBED = tuple('embedding_features.' + x for x in ('margin_min', 'margin_median', 'negative_chips'))


def numeric(value):
    return float(value) if isinstance(value, (int, float)) and math.isfinite(value) else None


def get(row, name):
    value = row
    for part in name.split('.'):
        value = value.get(part) if isinstance(value, dict) else None
    return numeric(value)


def solve(a, b):
    """Partial-pivot Gaussian elimination; positive ridge makes matrix nonsingular."""
    n = len(b)
    a = [list(row) + [v] for row, v in zip(a, b)]
    for k in range(n):
        pivot = max(range(k, n), key=lambda i: abs(a[i][k]))
        a[k], a[pivot] = a[pivot], a[k]
        assert abs(a[k][k]) > 1e-12
        scale = a[k][k]
        a[k] = [x / scale for x in a[k]]
        for i in range(n):
            if i != k:
                scale = a[i][k]
                a[i] = [x - scale * y for x, y in zip(a[i], a[k])]
    return [row[-1] for row in a]


def predict(train_x, train_y, test_x):
    n, d = len(train_x), len(test_x)
    means, scales = [], []
    for j in range(d):
        values = [x[j] for x in train_x if x[j] is not None]
        mean = statistics.mean(values) if values else 0.0
        # Imputed entries equal the training mean and contribute zero deviation.
        scale = math.sqrt(sum((v - mean) ** 2 for v in values) / n)
        means.append(mean)
        scales.append(scale if scale > 1e-12 else 1.0)
    def transform(x):
        return [(0 if v is None else (v - m) / s) for v, m, s in zip(x, means, scales)]
    x = [transform(row) for row in train_x]
    z = transform(test_x)
    ymean = statistics.mean(train_y)
    gram = [[sum(row[j] * row[k] for row in x) + float(j == k)
             for k in range(d)] for j in range(d)]
    rhs = [sum(row[j] * (y - ymean) for row, y in zip(x, train_y)) for j in range(d)]
    coef = solve(gram, rhs)
    return ymean + sum(c * v for c, v in zip(coef, z))


def ranks(values):
    ordered = sorted(range(len(values)), key=lambda i: values[i])
    result = [0.0] * len(values)
    j = 0
    while j < len(values):
        k = j + 1
        while k < len(values) and values[ordered[k]] == values[ordered[j]]:
            k += 1
        for i in ordered[j:k]:
            result[i] = (j + k - 1) / 2 + 1
        j = k
    return result


def correlation(x, y):
    if len(x) < 3 or len(set(x)) < 2 or len(set(y)) < 2:
        return None
    mx, my = statistics.mean(x), statistics.mean(y)
    return sum((a-mx)*(b-my) for a,b in zip(x,y)) / math.sqrt(
        sum((a-mx)**2 for a in x) * sum((b-my)**2 for b in y))


def auc(y, score):
    positives = [s for s, v in zip(score, y) if v == 1]
    negatives = [s for s, v in zip(score, y) if v == 0]
    if not positives or not negatives:
        return None
    return sum(float(a>b) + .5*float(a==b) for a in positives for b in negatives) / (len(positives)*len(negatives))


def metrics(y, raw, target, baseline=False):
    if len(set(y)) < 2:
        return {'brier': None, 'rmse': None, 'rank_auc': None, 'spearman': None,
                'reason': 'constant outcomes; predictive skill not assessable'}
    bounded = [min(1.0, max(0.0, p)) for p in raw]
    mse = statistics.mean((p-v)**2 for p,v in zip(bounded,y))
    return {'brier': mse if target == 'majority' else None, 'rmse': math.sqrt(mse),
            'rank_auc': auc(y,raw) if target == 'majority' and not baseline else None,
            'spearman': correlation(ranks(y),ranks(raw)) if not baseline else None,
            'clipped_predictions': sum(a != b for a,b in zip(raw,bounded))}


def main():
    records = [json.loads(line) for line in INPUT.open(encoding='utf-8')]
    clean = {(r['arm'],r['source']): r for r in records if r['cell']=='clean' and r['cohort']=='stage2_union'}
    groups = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in records:
        if r['cell'] != 'clean':
            groups[(r['cohort'],r['arm'],r['cell'])][r['source']].append(r)
    feature_inventory = {}
    results = []
    soft = []
    for arm in sorted({a for a,s in clean}):
        names = list(QUALITY + (READER if arm in INTERNAL else ('presence_margin',))
                     + (EMBED if arm=='f5-r2' else ()))
        features = [clean[a,s] for a,s in clean if a==arm]
        feature_inventory[arm] = {
            name: {'missing': sum(get(r,name) is None for r in features),
                   'unique': len({get(r,name) for r in features if get(r,name) is not None}),
                   'min': min((get(r,name) for r in features if get(r,name) is not None),default=None),
                   'max': max((get(r,name) for r in features if get(r,name) is not None),default=None)}
            for name in names}
    for (cohort,arm,cell), source_rows in sorted(groups.items()):
        names = list(feature_inventory[arm])
        sources = sorted(source_rows)
        assert len(sources)==60
        for source in sources:
            assert len(source_rows[source])==3
            assert len({r['seed'] for r in source_rows[source]})==3
            assert (arm,source) in clean
        missing_seed = sum(r['success'] is None for rs in source_rows.values() for r in rs)
        incomplete_sources = [s for s in sources if any(r['success'] is None for r in source_rows[s])]
        ambiguous_majorities = sum(sum(r['success'] is True for r in rs)<2 <=
                                  sum(r['success'] is not False for r in rs) for rs in source_rows.values())
        for sensitivity in ('conservative','complete'):
            ss = [s for s in sources if sensitivity=='conservative' or s not in incomplete_sources]
            x = [[get(clean[arm,s],f) for f in names] for s in ss]
            for target in ('majority','fraction'):
                counts = [sum(r['success'] is True for r in source_rows[s]) for s in ss]
                y = [float(c>=2) if target=='majority' else c/3 for c in counts]
                degenerate = len(set(y)) < 2
                result = {'cohort':cohort,'arm':arm,'cell':cell,'endpoint':'C' if arm in INTERNAL else 'P',
                          'sensitivity':sensitivity,'target':target,'n':len(ss),'mean':statistics.mean(y),
                          'positive_sources':sum(y) if target=='majority' else None,
                          'missing_seed_outcomes':missing_seed,'incomplete_sources':len(incomplete_sources),
                          'majority_ambiguities_due_to_missing':ambiguous_majorities,
                          'outcome_status':('all_zero' if y[0]==0 else 'all_one' if y[0]==1 else 'constant_fraction') if degenerate else 'nonconstant',
                          'models':{}}
                specs = {'constant_training_mean': [],'ridge_all':list(range(len(names)))}
                specs.update({'single:'+name:[j] for j,name in enumerate(names)})
                for model,indices in specs.items():
                    predictions = []
                    if not degenerate:
                        for i,s in enumerate(ss):
                            train = [j for j,t in enumerate(ss) if t != s]
                            assert len(train)==len(ss)-1 and all(ss[j]!=s for j in train)
                            train_y = [y[j] for j in train]
                            predictions.append(predict([[x[j][k] for k in indices] for j in train],train_y,
                                                       [x[i][k] for k in indices]) if indices else statistics.mean(train_y))
                    result['models'][model] = metrics(y,predictions,target,baseline=not indices)
                results.append(result)
        # Observed numeric margins: descriptive feature association, not extra CV targets.
        for name in names:
            pairs=[]
            for s in sources:
                values=[r['margin'] for r in source_rows[s] if r['margin'] is not None]
                f=get(clean[arm,s],name)
                if len(values)==3 and f is not None:
                    pairs.append((f,statistics.mean(values)))
            soft.append({'cohort':cohort,'arm':arm,'cell':cell,'feature':name,'complete_source_n':len(pairs),
                         'spearman_with_mean_regenerated_margin':correlation(ranks([a for a,b in pairs]),ranks([b for a,b in pairs])),
                         'margin_type':'semantic decoded' if arm in INTERNAL else 'presence matching bits'})
    output={'input_sha256':hashlib.sha256(INPUT.read_bytes()).hexdigest(),
            'protocol':'fixed ridge lambda=1 on summed squared error; source LOSO separately per cohort/arm/cell; training-only imputation and scaling',
            'feature_timing':'after paid writing and clean reading, before regeneration; never free pre-mark context',
            'phase_a_reuse':'same 60 sources; stage2 clean feature reuse; not new-source external validation',
            'auc':'raw ridge ranking; undefined for degenerate labels; constant baseline ranking suppressed because fold prevalence shifts create spurious reverse ordering',
            'brier_rmse':'clipped [0,1] predictions; binary Brier, binary/fraction RMSE; all null for constant outcomes',
            'feature_inventory':feature_inventory,'results':results,'soft_margin_associations':soft}
    (HERE/'predictability-results.json').write_text(json.dumps(output,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    write_note(output)
    print(json.dumps({'records':len(results),'nonconstant_majority_conservative':sum(r['target']=='majority' and r['sensitivity']=='conservative' and r['outcome_status']=='nonconstant' for r in results)}))


def fmt(value):
    return 'not reported' if value is None else f'{value:.3f}'


def write_note(out):
    lines=['# WP3 predictability: numeric features before regeneration','',
           '**MEASURED, post-hoc descriptive development analysis.** All numbers below are reproduced by `predictability.py` from `dev-records.jsonl`; full metrics, missingness, individual-feature fits and margin associations are in `predictability-results.json`. No held-out journals, images or new watermark executions were used.','',
           '## Fixed analysis and interpretation','',
           'The primary model is ridge regression with lambda=1 on the sum of squared residuals, unpenalized intercept, training-fold mean imputation and training-fold population standardization. Each arm/cell/cohort has its own model. A held-out source contributes no labels from any seed or cell to fitting; each source is one row with three-seed majority (>=2) or success fraction (successes/3). No feature selection, model tuning, seed-wise splitting or policy deployment is performed. Every individual feature is also fit with the same fixed ridge penalty as a descriptive diagnostic; these are not selected winners.','',
           'The constant comparator is the training-fold outcome mean. Its Brier/RMSE is valid, but its AUC is deliberately suppressed: leave-one-out fold prevalence changes would mechanically reverse-order binary labels. Ridge AUC uses unrounded, unclipped predictions; Brier and RMSE clip predictions to [0,1]. Metrics are not reported for constant labels because predictive skill is not assessable there. AUC is mathematically undefined for such labels; Brier/RMSE could be computed and a trivial constant prediction would give zero. There are no calibrated survival probabilities here.','',
           'Clean margins are separate decoded and recomputed scores minus their own thresholds, for semantic and instance readers. F5 adds embedding margin minimum/median and negative-chip count; all arms use PSNR, SSIM and LPIPS. External arms use clean presence margin, and their outcomes are P (message presence), not C (content-compatible detection). These predictors exist only after paying to write and clean-read that arm; they cannot be treated as free inputs to a pre-mark selector. Regenerated C0/f0 features are excluded.','',
           'Stage2 and Phase A are reported separately. Phase A explicitly reuses Stage2 clean features for the same 60 sources. This is repeated development data under different conditions, not fresh-source validation or evidence that a policy transfers to new sources.','',
           'Missing outcomes are failures in the conservative primary analysis (fraction denominator 3). Complete-source sensitivity drops any source with one missing seed. Counts of ambiguous majorities are in JSON. No missing numerical score is replaced by a fabricated score. Continuous soft-margin associations use only sources with three observed scores.','',
           '## Primary majority results','',
           '| Cohort | Arm / endpoint | Cell | Success / 60 | Missing seeds | Constant Brier | Ridge Brier | Ridge AUC | Complete n / ridge Brier |',
           '|---|---|---|---:|---:|---:|---:|---:|---|']
    rows=out['results']
    lookup={(r['cohort'],r['arm'],r['cell'],r['target'],r['sensitivity']):r for r in rows}
    for r in rows:
        if r['target']!='majority' or r['sensitivity']!='conservative':
            continue
        c=lookup[r['cohort'],r['arm'],r['cell'],'majority','complete']
        m=r['models']['ridge_all']; b=r['models']['constant_training_mean']
        lines.append(f"| {r['cohort']} | {r['arm']} / {r['endpoint']} | {r['cell']} | {r['positive_sources']:.0f} | {r['missing_seed_outcomes']} | {fmt(b['brier'])} | {fmt(m['brier'])} | {fmt(m['rank_auc'])} | {c['n']} / {fmt(c['models']['ridge_all']['brier'])} |")
    lines += ['','## Fraction outcome summary','',
              'Unweighted macro summaries below include only nonconstant fraction cells. Cells are correlated because they reuse sources; these are descriptive summaries, not independent replications.','',
              '| Cohort | Arm | Nonconstant fraction cells | Mean constant RMSE | Mean ridge RMSE | Cells ridge RMSE lower |',
              '|---|---|---:|---:|---:|---:|']
    for cohort in ('stage2_union','phase_a'):
        for arm in sorted(out['feature_inventory']):
            rr=[r for r in rows if r['cohort']==cohort and r['arm']==arm and r['sensitivity']=='conservative' and r['target']=='fraction' and r['outcome_status']=='nonconstant']
            bm=[r['models']['constant_training_mean']['rmse'] for r in rr]
            rm=[r['models']['ridge_all']['rmse'] for r in rr]
            lines.append(f"| {cohort} | {arm} | {len(rr)} | {fmt(statistics.mean(bm) if bm else None)} | {fmt(statistics.mean(rm) if rm else None)} | {sum(a<b for a,b in zip(rm,bm))} |")
    lines += ['','## Reading the pattern','',
              'MEASURED: F5 R0 .4 has 39/60 source-majority successes; all-feature ridge improves Brier from 0.235 to 0.153 with AUC 0.811. This survives complete-source sensitivity (58 sources, ridge Brier 0.136). F5 R0 .2 has only three majority failures, and ridge worsens Brier from 0.049 to 0.055. F5 R1 cells all have zero majority successes: no binary ranking claim is available there. F5 R3 .2 has only five successes; its AUC 0.884 is particularly sample-sensitive.','',
              'MEASURED: v5 R0 .1/.2 shows a stronger prediction signal (AUC 0.928/0.881, Brier 0.176/0.256 reduced to 0.098/0.134). This does not generalize to every cell: at R1-rinse .1, R1-smooth .2 and R3 .2 ridge Brier is worse than the constant baseline. VINE-R P at R1 .4 improves Brier from 0.194 to 0.133 (AUC 0.784), while its several all-success cells cannot test ranking. WAM R1 .2 AUC 0.957 depends on just two positive sources and must not be portrayed as a validated high-accuracy model.','',
              'MEASURED: F5 clean semantic decoded margin correlates with mean regenerated decoded margin at R0 .4 (Spearman 0.977, 58 complete sources) and R1 .1 (0.546, 60 sources). The latter association coexists with zero majority C successes. Continuous numerical signal therefore does not itself establish room to cross the decision boundary. These correlations are descriptive in-sample associations, not cross-validated predictions.','',
              'JUDGMENT: The logs contain some rankable source information, strongest in several nondegenerate R0 cells, but do not support a generic claim that clean features rescue F5 under R1. The learned outcome prediction is not an estimate of the effect of changing any action.','',
              '## Feature availability and limits','']
    for arm,features in out['feature_inventory'].items():
        constant=[name for name,v in features.items() if v['unique']<=1]
        missing=sum(v['missing'] for v in features.values())
        lines.append(f"- {arm}: {len(features)} features; {missing} missing feature entries among 60 clean sources; constant features: {', '.join(constant) or 'none'}.")
    lines += ['','VINE-R clean presence margin has only two values (30 and 31 matching bits above threshold); WAM clean presence margin is constant. External-arm prediction therefore largely concerns quality features rather than a broadly varying clean detection score.','',
              'JUDGMENT: Predictability can identify numerical association worth a prospective test, but it does not establish a causal action, the benefit of changing a writer, the superiority of RL, or a deployable calibrated learner. Small n, many correlated cells/features, ceiling/floor outcomes, and repeated-source reuse limit interpretation. Individual-feature tables and soft-margin correlations are exploratory diagnostics without multiplicity-adjusted claims.','',
              'Validation: analytical two-variable linear-system solution, one-feature ridge solution (including a missing training value), tied-score AUC and constant-label AUC checks passed using only the permitted stdlib interpreter. Runtime assertions check exactly three distinct seeds per source/cell, exactly 60 sources, matching clean records and source-disjoint training folds.','']
    (HERE/'predictability-note.md').write_text('\n'.join(lines),encoding='utf-8')


if __name__=='__main__':
    main()
