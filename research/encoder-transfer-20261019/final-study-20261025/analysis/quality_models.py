"""Frozen WP2 descriptive quality models. Standard library only; never opens images.

Usage: python -I quality_models.py PATH/TO/rows.jsonl
The provided journal must be the stage2b union journal. Outputs sit beside this file.
"""
import csv
import hashlib
import json
import math
import random
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
OWNER = 'qim-pilot-owner-alpha'
ARMS = ('f5-r2', 'v5-r3')
STRENGTHS = (0.1, 0.2, 0.4)
MODELS = ('D0', 'D1', 'D2', 'D3')
TOL = 1e-8
MAX_ITER = 2000


def fold(sid):
    digest = hashlib.sha256(('et-final-wp2-v1/' + str(sid)).encode()).digest()
    return int.from_bytes(digest, 'big') % 5


def logsnr(strength):
    start = {0.1: 51, 0.2: 151, 0.4: 351}[strength]
    abar = 1.0
    for i in range(start + 1):
        beta = (math.sqrt(0.00085) +
                (math.sqrt(0.012) - math.sqrt(0.00085)) * i / 999) ** 2
        abar *= 1 - beta
    return math.log(abar / (1 - abar))


def read_rows(path):
    final = {}
    total = overwritten = 0
    transitions = Counter()
    with open(path, encoding='utf-8') as f:
        for line in f:
            total += 1
            r = json.loads(line)
            key = r['id']
            if key in final:
                overwritten += 1
                transitions[(final[key].get('status'), r.get('status'))] += 1
            final[key] = r
    return final, {'journal_lines': total, 'unique_ids': len(final),
                   'overwritten_rows': overwritten,
                   'status_transitions': {str(k): v for k, v in transitions.items()}}


def finite(x):
    return isinstance(x, (float, int)) and not isinstance(x, bool) and math.isfinite(x)


def collect(rows):
    out = {a: [] for a in ARMS}
    coverage = Counter()
    for r in rows.values():
        arm = r.get('arm')
        ch = r.get('channel')
        st = r.get('strength')
        if arm not in ARMS or ch not in ('R0', 'R1') or st not in STRENGTHS or r.get('control') != 'C1':
            continue
        key = (arm, ch, str(st))
        coverage[key + ('scheduled',)] += 1
        det = r.get('detections', {}).get(arm, {}).get(OWNER, {})
        y = det.get('endpoints', {}).get('C')
        q = r.get('distortion', {})
        vals = [q.get(k) for k in ('lpips', 'psnr_db', 'ssim_rgb')]
        if (r.get('status') != 'ok' or det.get('status') != 'ok' or
                q.get('status') != 'ok' or not isinstance(y, bool) or
                not all(finite(v) for v in vals)):
            coverage[key + ('unusable', str(r.get('status')), str(det.get('status')), str(q.get('status')))] += 1
            continue
        coverage[key + ('completed',)] += 1
        out[arm].append({'id': r['id'], 'source_id': int(r['source_id']),
                         'channel': ch, 'strength': st, 'seed': r.get('seed'),
                         'cell': ch + ' ' + str(st), 'y': int(y),
                         'features': [float(vals[0]), float(vals[1]), float(vals[2]),
                                      float(ch == 'R1'), logsnr(st)],
                         'fold': fold(int(r['source_id']))})
    for arm in ARMS:
        cells = Counter((r['source_id'], r['cell']) for r in out[arm])
        for r in out[arm]:
            r['weight'] = 1.0 / cells[(r['source_id'], r['cell'])]
    return out, {':'.join(k): v for k, v in sorted(coverage.items())}


def sigmoid(z):
    if z >= 0:
        e = math.exp(-z)
        return 1 / (1 + e)
    e = math.exp(z)
    return e / (1 + e)


def design(train, test, model):
    columns = {'D0': [], 'D1': [0], 'D2': [0, 1, 2],
               'D3': [0, 1, 2, 3, 4]}[model]
    moments = []
    for col in columns:
        wsum = sum(r['weight'] for r in train)
        mean = sum(r['weight'] * r['features'][col] for r in train) / wsum
        var = sum(r['weight'] * (r['features'][col] - mean) ** 2 for r in train) / wsum
        std = math.sqrt(var) if var > 1e-24 else 1.0
        moments.append((mean, std))
    def build(rows):
        return [[1.0] + [(r['features'][j] - mean) / std
                         for j, (mean, std) in zip(columns, moments)] for r in rows]
    return build(train), build(test), moments


def objective(beta, X, rows):
    total = 0.5 * sum(b * b for b in beta[1:])
    for x, r in zip(X, rows):
        z = sum(a*b for a, b in zip(x, beta))
        total += r['weight'] * (max(z, 0) + math.log1p(math.exp(-abs(z))) - r['y'] * z)
    return total


def gradient(beta, X, rows):
    g = [0.0] + beta[1:]
    for x, r in zip(X, rows):
        d = r['weight'] * (sigmoid(sum(a*b for a, b in zip(x, beta))) - r['y'])
        for j, v in enumerate(x):
            g[j] += d*v
    return g


def fit(train, model):
    X, _, moments = design(train, [], model)
    beta = [0.0] * len(X[0])
    # Cyclic exact-coordinate Newton with backtracking. Each one-dimensional
    # subproblem is convex; D1/D2 constraints are projected onto their bounds.
    bounds = {1: (None, 0.0), 2: (0.0, None), 3: (0.0, None)} if model == 'D2' else (
        {1: (None, 0.0)} if model == 'D1' else {})
    converged = False
    history = []
    for it in range(MAX_ITER):
        before = objective(beta, X, train)
        for j in range(len(beta)):
            g = beta[j] if j else 0.0
            h = 1.0 if j else 0.0
            for x, r in zip(X, train):
                p = sigmoid(sum(a*b for a, b in zip(x, beta)))
                g += r['weight'] * (p-r['y']) * x[j]
                h += r['weight'] * p * (1-p) * x[j]**2
            if h <= 0 or not math.isfinite(h):
                return {'ok': False, 'error': 'nonfinite Hessian', 'iteration': it}
            target = beta[j] - g/h
            lo, hi = bounds.get(j, (None, None))
            if lo is not None: target = max(lo, target)
            if hi is not None: target = min(hi, target)
            old = beta[j]
            trial = target
            old_obj = objective(beta, X, train)
            while True:
                beta[j] = trial
                new_obj = objective(beta, X, train)
                if math.isfinite(new_obj) and new_obj <= old_obj + 1e-10:
                    break
                trial = (trial + old)/2
                if abs(trial-old) < 1e-14:
                    beta[j] = old
                    break
        g = gradient(beta, X, train)
        residual = []
        for j, v in enumerate(g):
            lo, hi = bounds.get(j, (None, None))
            if lo is not None and beta[j] <= lo+1e-12: v = min(v, 0.0)
            if hi is not None and beta[j] >= hi-1e-12: v = max(v, 0.0)
            residual.append(abs(v))
        kkt = max(residual)
        after = objective(beta, X, train)
        if it in (0, 9, 99) or kkt < TOL or it == MAX_ITER-1:
            history.append({'iteration': it+1, 'objective': after, 'kkt_max': kkt})
        if not math.isfinite(after) or after > before + 1e-8:
            return {'ok': False, 'error': 'nonfinite/increased objective', 'iteration': it+1,
                    'history': history}
        if kkt < TOL:
            converged = True
            break
    return {'ok': converged, 'beta': beta, 'moments': moments, 'iterations': it+1,
            'objective': objective(beta, X, train), 'kkt_max': kkt,
            'history': history, 'error': None if converged else 'iteration limit'}


def predict(fitted, test, model):
    columns = {'D0': [], 'D1': [0], 'D2': [0, 1, 2], 'D3': [0, 1, 2, 3, 4]}[model]
    b = fitted['beta']
    return [sigmoid(b[0] + sum(b[k+1] * (r['features'][j]-m)/s
                               for k, (j, (m, s)) in enumerate(zip(columns, fitted['moments']))))
            for r in test]


def metrics(items):
    if not items: return None
    w = sum(r['weight'] for r in items)
    return {'n_calls': len(items), 'n_sources': len({r['source_id'] for r in items}),
            'weighted_brier': sum(r['weight']*(r['p']-r['y'])**2 for r in items)/w,
            'weighted_logloss': sum(r['weight']*(-r['y']*math.log(max(1e-8,min(1-1e-8,r['p'])))
                -(1-r['y'])*math.log(max(1e-8,min(1-1e-8,1-r['p'])))) for r in items)/w,
            'weighted_observed': sum(r['weight']*r['y'] for r in items)/w,
            'weighted_predicted': sum(r['weight']*r['p'] for r in items)/w}


def evaluate(rows, split):
    result = {}
    for model in MODELS:
        predictions = []
        fits = []
        groups = range(5) if split == 'fold' else STRENGTHS
        for group in groups:
            train = [r for r in rows if (r['fold'] if split == 'fold' else r['strength']) != group]
            test = [r for r in rows if (r['fold'] if split == 'fold' else r['strength']) == group]
            if not train or not test or len({r['y'] for r in train}) < 2:
                fits.append({'group': group, 'ok': False, 'error': 'empty or single-class training set'})
                continue
            fitted = fit(train, model)
            fits.append({'group': group, **fitted, 'train_calls': len(train), 'test_calls': len(test)})
            if 'beta' in fitted:
                predictions.extend([{**r, 'p': p, 'model': model, 'split': split,
                                     'holdout_group': group} for r, p in zip(test, predict(fitted,test,model))])
        bycell = defaultdict(list)
        for r in predictions: bycell[r['cell']].append(r)
        result[model] = {'overall': metrics(predictions),
                         'cells': {cell: metrics(rr) for cell, rr in sorted(bycell.items())},
                         'fits': fits, 'predictions': predictions}
    return result


def bootstrap_diff(left, right):
    a = {r['id']: r for r in left}
    b = {r['id']: r for r in right}
    common = sorted(set(a) & set(b))
    sources = sorted({a[k]['source_id'] for k in common})
    grouped = defaultdict(list)
    for k in common:
        grouped[a[k]['source_id']].append((a[k], b[k]))
    def brier_diff(selection):
        pairs = [pair for sid in selection for pair in grouped[sid]]
        w = sum(u['weight'] for u,v in pairs)
        return sum(u['weight']*((v['p']-v['y'])**2-(u['p']-u['y'])**2) for u,v in pairs)/w
    rng = random.Random(20261025)
    draws = sorted(brier_diff([rng.choice(sources) for _ in sources]) for _ in range(1000))
    return {'difference': 'right minus left weighted Brier', 'left': 'D2', 'right': 'D3',
            'point': brier_diff(sources), 'percentile_95': [draws[24], draws[974]],
            'draws': 1000, 'seed': 20261025, 'paired_sources': len(sources)}


def numerical_self_check():
    # Finite-difference gradient and strictly positive directional curvature
    # for a tiny synthetic convex objective; no journal-derived parameter fit.
    X = [[1.0, -0.4, 0.8], [1.0, 1.2, -0.3], [1.0, 0.1, 0.5]]
    rows = [{'weight': 1.0, 'y': y} for y in (0, 1, 0)]
    b = [0.2, -0.3, 0.4]
    g = gradient(b, X, rows)
    errors = []
    for j in range(len(b)):
        a, c = b[:], b[:]
        a[j] += 1e-6; c[j] -= 1e-6
        errors.append(abs(g[j] - (objective(a, X, rows)-objective(c, X, rows))/2e-6))
    direction = [0.6, -0.5, 0.3]
    curvature = sum(r['weight']*sigmoid(sum(t*u for t,u in zip(x,b))) *
                    (1-sigmoid(sum(t*u for t,u in zip(x,b)))) *
                    sum(t*u for t,u in zip(x,direction))**2 for x,r in zip(X, rows))
    curvature += sum(v*v for v in direction[1:])
    if max(errors)>1e-7 or curvature<=0: raise ArithmeticError('objective self-check failed')
    return {'finite_difference_gradient_max_abs_error': max(errors),
            'directional_hessian_quadratic': curvature, 'pass': True}


def main(path):
    if not path.name == 'rows.jsonl' or 'stage2b-full' not in str(path):
        raise SystemExit('Expected stage2b-full/rows.jsonl union journal')
    rows, journal = read_rows(path)
    arms, coverage = collect(rows)
    output = {'self_check': numerical_self_check(),
             'contract': {'fold': "SHA256('et-final-wp2-v1/'+str(source_id)) mod 5",
             'weight': 'each completed source-cell sums to one',
             'objective': 'SUM of source-cell-weighted negative Bernoulli log likelihood + 0.5 SUM squared standardized nonintercept coefficients',
             'constraint': 'D1/D2 LPIPS<=0; D2 PSNR,SSIM>=0; D3 unrestricted',
             'optimizer': 'cyclic coordinate Newton with backtracking, KKT tolerance 1e-8, maximum 2000 passes',
             'logsnr': 'DDIM 1000 scaled_linear betas .00085 to .012, inclusive product through start 51/151/351'},
             'journal': journal, 'coverage': coverage, 'logsnr_values': {str(s): logsnr(s) for s in STRENGTHS},
             'arms': {}}
    csvrows = []
    for arm, data in arms.items():
        cv = evaluate(data, 'fold')
        loso = evaluate(data, 'strength')
        output['arms'][arm] = {'n_complete_calls': len(data),
             'n_sources': len({r['source_id'] for r in data}),
             'fold_source_counts': dict(Counter(str(fold(s)) for s in {r['source_id'] for r in data})),
             'cv': {m: {k:v for k,v in cv[m].items() if k!='predictions'} for m in MODELS},
             'loso': {m: {k:v for k,v in loso[m].items() if k!='predictions'} for m in MODELS}}
        output['arms'][arm]['bootstrap_D3_minus_D2'] = bootstrap_diff(cv['D2']['predictions'],cv['D3']['predictions'])
        for block in (cv, loso):
            for m in MODELS:
                for r in block[m]['predictions']:
                    csvrows.append({k:r[k] for k in ('id','source_id','channel','strength','seed','cell','y','weight','fold','p','model','split','holdout_group') } | {'arm':arm})
    with open(HERE/'quality-model-predictions.csv','w',newline='',encoding='utf-8') as f:
        fields = ['arm','id','source_id','channel','strength','seed','cell','y','weight','fold','p','model','split','holdout_group']
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(csvrows)
    (HERE/'quality-model-results.json').write_text(json.dumps(output,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    lines = ['# Quality-only diagnostic models', '',
      'Development-only descriptive fits on the last record per ID in the stage2b union journal. '
      'No marked-output reader score or target detector state enters the predictors.', '',
      'The weighted objective is the **sum**, not mean, of Bernoulli negative log likelihood '
      'with each completed source-cell totaling weight 1, plus 0.5 times the squared '
      'standardized nonintercept coefficients (L2=1). Training-fold weighted moments '
      'standardize features. D1/D2 enforce LPIPS ≤ 0 and PSNR/SSIM ≥ 0; D3 is unconstrained. '
      'Cyclic coordinate Newton uses backtracking and a 1e-8 KKT tolerance, at most 2000 passes. '
      'All fit diagnostics, including failures, are in the JSON. A finite-difference gradient '
      'and positive directional-curvature check passed for the convex objective.', '',
      f"Journal: {journal['journal_lines']} lines, {journal['unique_ids']} final IDs, {journal['overwritten_rows']} overwritten states.",
      'Five source-disjoint folds use the frozen SHA256 assignment. Completed quality calls alone '
      'enter fitting; incomplete outputs remain in the JSON coverage table. Training within R0/R1 '
      'tests in-family source generalization; leave-one-strength-out tests strength extrapolation '
      'inside those two families. Neither is independent-family confirmation.', '']
    for arm in ARMS:
        block=output['arms'][arm]
        lines += [f"## {arm}", '', f"Completed: {block['n_complete_calls']} calls, {block['n_sources']} sources. Fold source counts: {block['fold_source_counts']}.", '',
                  '| Model | CV Brier | CV log loss | LOSO Brier | LOSO log loss |',
                  '|---|---:|---:|---:|---:|']
        for m in MODELS:
            c=block['cv'][m]['overall']; l=block['loso'][m]['overall']
            fmt=lambda d,k: f"{d[k]:.4f}" if d else 'NA'
            lines.append(f"| {m} | {fmt(c,'weighted_brier')} | {fmt(c,'weighted_logloss')} | {fmt(l,'weighted_brier')} | {fmt(l,'weighted_logloss')} |")
        lines += ['', '| Cell | Completed | Observed C | D2 predicted | D3 predicted |',
                  '|---|---:|---:|---:|---:|']
        for cell in sorted(block['cv']['D3']['cells']):
            actual = block['cv']['D3']['cells'][cell]
            d2 = block['cv']['D2']['cells'][cell]
            d3 = block['cv']['D3']['cells'][cell]
            lines.append(f"| {cell} | {actual['n_calls']} | {actual['weighted_observed']:.3f} | {d2['weighted_predicted']:.3f} | {d3['weighted_predicted']:.3f} |")
        bs=block['bootstrap_D3_minus_D2']
        lines += ['', f"Paired source-cluster bootstrap, D3−D2 held-out CV Brier: {bs['point']:.4f}; 95% percentile interval [{bs['percentile_95'][0]:.4f}, {bs['percentile_95'][1]:.4f}] (1,000 draws, seed 20261025).", '',
                  'A lower loss for D3 limits these specified quality-only logistic forms; it cannot rule out arbitrary '
                  'distortion functionals or isolate an encoder mechanism. Family and schedule labels are diagnostics, '
                  'not a transfer law.', '']
    lines += ['## Coverage and scope', '',
              'Scheduled calls: 180 per arm/family/strength cell. F5 completed R0 .1/.2/.4: 179/177/178; '
              'R1: 180/180/180. v5 completed R0: 180/179/178; R1: 180/180/180. '
              'Nine R0 calls were safety blocked (six F5, three v5). Details are in the JSON. ',
              'The frozen T7 bin/caliper overlap analysis is reported in the companion WP2 journal analysis: '
              'F5 2, v5 0, WAM 1 and VINE-R 3 unique sources across bins. '
              'These logistic models use all completed R0/R1 C1 calls and are not matched-caliper fits. '
              'The overlap counts limit direct matched-distortion comparisons.', '',
              'Failed or missing outputs have no fabricated quality values. '
              'All endpoint counts including failed calls belong in the companion descriptive WP2 report. '
              'This statistical comparison uses a reused development population, so its intervals describe '
              'source resampling conditional on that population and fitted predictions, not confirmatory uncertainty.', '']
    (HERE/'quality-model-report.md').write_text('\n'.join(lines),encoding='utf-8')
    print('wrote outputs:', {a: output['arms'][a]['n_complete_calls'] for a in ARMS})


if __name__ == '__main__':
    if len(sys.argv)!=2: raise SystemExit('usage: python -I quality_models.py stage2b-full/rows.jsonl')
    main(Path(sys.argv[1]))
