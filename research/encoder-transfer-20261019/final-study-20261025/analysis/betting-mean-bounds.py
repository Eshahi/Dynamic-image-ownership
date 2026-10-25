"""Prospective exact-rational scenario arithmetic; no experiment or data input."""
from fractions import Fraction as F
import json
import math
from pathlib import Path

GRID = (F(1, 16), F(1, 8), F(1, 4), F(1, 2), F(3, 4), F(1))
ALPHA = F(1, 260)
N = 200


def e_two_point(n, k, high=F(1, 5), low=F(-4, 5), weights=None):
    weights = weights or (F(1,6),)*6
    return sum((w * (1 + lam * high) ** (n-k) * (1 + lam * low) ** k
                for lam, w in zip(GRID, weights)), F(0))


def binom_prob(n, p, counts):
    return sum((math.comb(n, k) * p**k * (1-p)**(n-k)
                for k in counts), F(0))


def min_n_constant(t, weights=None):
    weights = weights or (F(1,6),)*6
    def passed(n):
        return sum((w*(1+lam*t)**n for lam,w in zip(GRID,weights)), F(0)) >= 260
    hi = 1
    while not passed(hi):
        hi *= 2
    lo = 0
    while hi-lo > 1:
        mid = (lo+hi)//2
        if passed(mid):
            hi = mid
        else:
            lo = mid
    assert passed(hi) and not passed(hi-1)
    return hi


def log_e_float(values):
    logs = []
    for lam in GRID:
        lf = float(lam)
        if any(1+lf*t == 0 for t in values):
            logs.append(-math.inf)
        else:
            logs.append(math.fsum(math.log1p(lf*t) for t in values))
    m = max(logs)
    if m == -math.inf:
        return -math.inf
    return m + math.log(math.fsum(math.exp(v-m) for v in logs)) - math.log(len(GRID))


def main():
    mean_counts = [k for k in range(N+1) if e_two_point(N, k) >= 1/ALPHA]
    calibration_counts = [k for k in range(N+1)
                          if binom_prob(N, F(1, 10), range(k+1)) <= ALPHA]
    joint_counts = sorted(set(mean_counts) & set(calibration_counts))
    rates = [F(0), F(1, 200), F(1, 100), F(1, 50), F(3, 100),
             F(1, 25), F(1, 20), F(3, 40)]
    out = {
        "purpose": "prospective exact-rational analytical scenario, no experimental data",
        "grid": [str(v) for v in GRID], "weights": "1/6 each",
        "n": N, "local_alpha": str(ALPHA), "e_rejection_threshold": 260,
        "scenario": "q=.5; shared iid Bernoulli source error; t=.2-error",
        "mean_only_passing_error_counts": mean_counts,
        "calibration_passing_error_counts": calibration_counts,
        "joint_passing_error_counts": joint_counts,
        "scenario_power": {
            str(float(p)): {
                "betting_mean": float(binom_prob(N, p, mean_counts)),
                "betting_joint_H4": float(binom_prob(N, p, joint_counts)),
                "prior_EB_joint_H4": float(binom_prob(N, p, range(6)))
            } for p in rates
        },
        "p_values_at_counts": {
            str(k): {
                "p_betting": float(min(F(1), 1/e_two_point(N, k))),
                "p_calibration": float(binom_prob(N, F(1, 10), range(k+1)))
            } for k in [0, 5, 9, 10, max(mean_counts), max(mean_counts)+1]
        },
        "perfect_law_constant_baseline": {
            str(float(b)): {
                "t": float(F(4, 5)*b),
                "minimum_n_betting_mean": min_n_constant(F(4, 5)*b),
                "p_betting_at_200": float(min(F(1), 1/e_two_point(N, 0, F(4,5)*b)))
            } for b in [F(1,4), F(1,10), F(1,25), F(1,100)]
        },
    }
    # A null distribution at the support endpoints has E[t]=0. Each bet,
    # and hence the fixed mixture, has expectation exactly one.
    endpoint_high_p = F(5,9)
    for lam in GRID:
        factor_mean = endpoint_high_p*(1+lam*F(4,5)) + (1-endpoint_high_p)*(1-lam)
        assert factor_mean == 1
    # Zero factors: a lambda=1 component dies; the others still contribute.
    assert math.isfinite(log_e_float([-1.0] + [.2]*199))
    assert abs(log_e_float([.2]*191+[-.8]*9) - math.log(float(e_two_point(200,9)))) < 1e-12
    # A positive-mean alternative at which all fixed positive bets have
    # negative log growth; documents lack of universal consistency.
    tiny_mean_p = float((1+F(1,1000))/F(9,5))
    drifts = {str(lam): (tiny_mean_p*math.log1p(float(lam)*.8)
                          +(1-tiny_mean_p)*math.log1p(-float(lam)))
              for lam in GRID if lam < 1}
    assert all(v < 0 for v in drifts.values())
    out["no_universal_dominance_example"] = {
        "distribution": "t=.8 with p=(1+.001)/1.8, otherwise t=-1; mean=.001",
        "log_growth": drifts, "lambda_1": "bankrupts at first -1",
        "scope": "asymptotic counterexample to universal dominance, not Phase-B forecast"
    }
    out["checks"] = "exact rational rejection comparisons; null factor identity; zero-factor log handling; float log agrees with rational value"
    half_weights = (F(1,10),)*5 + (F(1,2),)
    half_counts = [k for k in range(N+1) if e_two_point(N,k,weights=half_weights) >= 260]
    out["prospective_half_max_alternative"] = {
        "weights_in_grid_order": [str(w) for w in half_weights],
        "mean_passing_error_counts": half_counts,
        "joint_passing_error_counts": sorted(set(half_counts)&set(calibration_counts)),
        "perfect_law_constant_baseline": {
            str(float(b)): {
                "minimum_n": min_n_constant(F(4,5)*b,half_weights),
                "p_at_200": float(min(F(1),1/e_two_point(N,0,F(4,5)*b,weights=half_weights)))
            } for b in [F(1,4), F(1,10), F(1,25), F(1,100)]
        },
        "identity": "E_half=.6*E_uniform+.4*K_lambda1; therefore E_half>=.6*E_uniform pointwise"
    }
    path = Path(__file__).with_suffix('.json')
    path.write_text(json.dumps(out, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
