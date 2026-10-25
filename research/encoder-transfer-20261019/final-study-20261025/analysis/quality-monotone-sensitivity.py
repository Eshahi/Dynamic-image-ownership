"""Post-hoc D3M sensitivity: D3 features with D2 monotone quality signs.

Uses only the frozen stage2b union rows.jsonl and the original WP2 code. It does
not modify the D0-D3 files. Standard library only.
"""
import importlib.util
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('wp2_quality_models', HERE/'quality_models.py')
qm = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(qm)
TOL = qm.TOL
MAX_ITER = qm.MAX_ITER


def fit_d3m(train):
    X, _, moments = qm.design(train, [], 'D3')
    beta = [0.0] * len(X[0])
    bounds = {1: (None, 0.0), 2: (0.0, None), 3: (0.0, None)}
    history = []
    converged = False
    for it in range(MAX_ITER):
        before = qm.objective(beta, X, train)
        for j in range(len(beta)):
            g = beta[j] if j else 0.0
            h = 1.0 if j else 0.0
            for x, r in zip(X, train):
                p = qm.sigmoid(sum(a*b for a, b in zip(x, beta)))
                g += r['weight'] * (p-r['y']) * x[j]
                h += r['weight'] * p * (1-p) * x[j]**2
            if h <= 0 or not math.isfinite(h):
                return {'ok': False, 'error': 'nonfinite Hessian', 'iteration': it+1}
            target = beta[j] - g/h
            lo, hi = bounds.get(j, (None, None))
            if lo is not None: target = max(lo, target)
            if hi is not None: target = min(hi, target)
            old = beta[j]
            old_obj = qm.objective(beta, X, train)
            trial = target
            while True:
                beta[j] = trial
                new_obj = qm.objective(beta, X, train)
                if math.isfinite(new_obj) and new_obj <= old_obj + 1e-10:
                    break
                trial = (trial+old)/2
                if abs(trial-old) < 1e-14:
                    beta[j] = old
                    break
        g = qm.gradient(beta, X, train)
        residual = []
        for j, v in enumerate(g):
            lo, hi = bounds.get(j, (None, None))
            if lo is not None and beta[j] <= lo+1e-12: v = min(v,0.0)
            if hi is not None and beta[j] >= hi-1e-12: v = max(v,0.0)
            residual.append(abs(v))
        kkt = max(residual)
        after = qm.objective(beta, X, train)
        if it in (0,9,99) or kkt<TOL or it==MAX_ITER-1:
            history.append({'iteration':it+1,'objective':after,'kkt_max':kkt})
        if not math.isfinite(after) or after>before+1e-8:
            return {'ok':False,'error':'nonfinite/increased objective','iteration':it+1,'history':history}
        if kkt<TOL:
            converged=True
            break
    return {'ok':converged,'beta':beta,'moments':moments,'iterations':it+1,
            'objective':qm.objective(beta,X,train),'kkt_max':kkt,
            'history':history,'error':None if converged else 'iteration limit'}


def evaluate(rows, split):
    groups = range(5) if split=='cv' else qm.STRENGTHS
    predictions=[]; fits=[]
    for group in groups:
        get_group = (lambda r:r['fold']) if split=='cv' else (lambda r:r['strength'])
        train=[r for r in rows if get_group(r)!=group]
        test=[r for r in rows if get_group(r)==group]
        if not train or not test or len({r['y'] for r in train})<2:
            fits.append({'group':group,'ok':False,'error':'empty or single-class training set'})
            continue
        fitted=fit_d3m(train)
        fits.append({'group':group,**fitted,'train_calls':len(train),'test_calls':len(test)})
        if 'beta' in fitted:
            predictions.extend([{**r,'p':p,'holdout_group':group} for r,p in zip(test,qm.predict(fitted,test,'D3'))])
    bycell=defaultdict(list)
    for r in predictions: bycell[r['cell']].append(r)
    return {'overall':qm.metrics(predictions),
            'cells':{c:qm.metrics(rr) for c,rr in sorted(bycell.items())},
            'fits':fits}


def main(path):
    if path.name!='rows.jsonl' or 'stage2b-full' not in str(path):
        raise SystemExit('Expected stage2b-full/rows.jsonl union journal')
    prior=json.loads((HERE/'quality-model-results.json').read_text(encoding='utf-8'))
    rows,journal=qm.read_rows(path)
    arms,coverage=qm.collect(rows)
    if journal!=prior['journal'] or coverage!=prior['coverage']:
        raise ValueError('Primary D0-D3 input state changed')
    result={'label':'Post-hoc D3M sensitivity, not a frozen primary model',
            'objective':prior['contract']['objective'],
            'features':'D2 LPIPS, PSNR, SSIM plus R1 family indicator and DDIM scaled_linear logSNR',
            'constraints':'LPIPS<=0, PSNR>=0, SSIM>=0; family and logSNR unrestricted',
            'folds':prior['contract']['fold'],
            'optimizer':'same cyclic coordinate Newton/backtracking as primary; KKT 1e-8, 2000 passes',
            'journal':journal,'arms':{}}
    for arm,data in arms.items():
        result['arms'][arm]={'cv':evaluate(data,'cv'),'loso':evaluate(data,'loso')}
    (HERE/'quality-monotone-sensitivity.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    lines=['# Post-hoc monotone D3 sensitivity','',
           'D3 in the primary analysis augments D2 with family and logSNR **and relaxes** the '
           'LPIPS/PSNR/SSIM sign constraints. Thus its gain over D2 cannot be attributed solely '
           'to family/schedule. D3M is a separate sensitivity using the same completed calls, '
           'source-cell weights, five source-disjoint folds, train-only scaling, L2=1, and '
           'coordinate Newton solver. It adds family/logSNR while retaining LPIPS ≤ 0, PSNR '
           'and SSIM ≥ 0. Family and logSNR remain unrestricted. This sensitivity was specified '
           'after inspecting D0-D3 results and is descriptive.', '',
           '| Arm | Model | CV Brier | CV log loss | LOSO Brier | LOSO log loss | Convergence |',
           '|---|---|---:|---:|---:|---:|---|']
    for arm in qm.ARMS:
        for model in ('D2','D3M','D3'):
            entry=result['arms'][arm] if model=='D3M' else prior['arms'][arm]
            block=entry if model=='D3M' else {'cv':entry['cv'][model],'loso':entry['loso'][model]}
            c=block['cv']['overall']; l=block['loso']['overall']
            fits=[f for s in ('cv','loso') for f in block[s]['fits']]
            passes=sum(f['ok'] for f in fits)
            lines.append(f"| {arm} | {model} | {c['weighted_brier']:.6f} | {c['weighted_logloss']:.6f} | {l['weighted_brier']:.6f} | {l['weighted_logloss']:.6f} | {passes}/{len(fits)} |")
    lines += ['', 'D3M is still an in-family development-population diagnostic. A lower D3M loss '
              'than D2 limits this specified monotone quality-only form; it does not isolate '
              'a causal encoder effect or rule out other distortion models. Leave-one-strength-out '
              'still uses only R0/R1 and should not be read as family transfer.', '']
    (HERE/'quality-monotone-sensitivity.md').write_text('\n'.join(lines),encoding='utf-8')
    print('D3M complete', {a:result['arms'][a]['cv']['overall']['weighted_brier'] for a in qm.ARMS})


if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit('usage: python -I quality-monotone-sensitivity.py stage2b-full/rows.jsonl')
    main(Path(sys.argv[1]))
