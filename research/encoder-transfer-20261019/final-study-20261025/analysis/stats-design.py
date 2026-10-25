"""Analytical sample-size/power calculations only; Python standard library.

No project imports, data files, model/image operations, or stochastic simulation.
Run with the approved stdlib interpreter and -I. Output is sibling JSON.
"""
import json
import math
from itertools import product
from pathlib import Path


def pmf(n, p):
    return [math.comb(n, k) * p**k * (1-p)**(n-k) for k in range(n+1)]


def cdf(n, p, k):
    return math.fsum(pmf(n, p)[:k+1]) if k >= 0 else 0.0


def sf(n, p, k):
    return math.fsum(pmf(n, p)[k:]) if k <= n else 0.0


def upper_cp(n, k, alpha):
    if k == n:
        return 1.0
    lo, hi = 0.0, 1.0
    for _ in range(90):
        mid = (lo+hi)/2
        if cdf(n, mid, k) > alpha:
            lo = mid
        else:
            hi = mid
    return (lo+hi)/2


def lower_cp(n, k, alpha):
    if k == 0:
        return 0.0
    lo, hi = 0.0, 1.0
    for _ in range(90):
        mid = (lo+hi)/2
        if sf(n, mid, k) < alpha:
            lo = mid
        else:
            hi = mid
    return (lo+hi)/2


def lower_critical(n, p0, alpha):
    return max((k for k in range(n+1) if cdf(n, p0, k) <= alpha), default=-1)


def upper_critical(n, p0, alpha):
    return min((k for k in range(n+1) if sf(n, p0, k) <= alpha), default=n+1)


def eb_radius(n, variance, alpha):
    logterm = math.log(2/alpha)
    return math.sqrt(2*variance*logterm/n) + 7*1.8*logterm/(3*(n-1))


def eb_pvalue(n, mean, variance):
    if mean <= 0:
        return 1.0
    a = math.sqrt(2*variance/n)
    c = 7*1.8/(3*(n-1))
    root = 2*mean / (math.sqrt(a*a+4*c*mean)+a)
    return min(1.0, 2*math.exp(-root*root))


def verify_completion_bounds():
    """Finite binary arithmetic only; no sampled or observed study outcomes."""
    checks = 0
    patterns = 0
    examples = []
    for states in product((0, 1, None), repeat=3):
        positives = sum(v == 1 for v in states)
        unresolved = sum(v is None for v in states)
        lo = int(positives >= 2)
        hi = int(positives + unresolved >= 2)
        feasible = tuple(range(lo, hi+1))
        completions = product(*[(0, 1) if v is None else (v,) for v in states])
        actual_majorities = {int(sum(values) >= 2) for values in completions}
        assert set(feasible) == actual_majorities
        patterns += 1
        for a in (0, 1):
            for q in (0.0, .1, .5, .9, 1.0):
                upper_mismatch = max(int(a != y) for y in feasible)
                lower_t = min(.8*(q-y)**2 - (a-y)**2 for y in feasible)
                min_baseline = min((q-y)**2 for y in feasible)
                for y in actual_majorities:
                    assert a-hi <= a-y <= a-lo
                    assert int(a != y) <= upper_mismatch
                    assert lower_t <= .8*(q-y)**2 - (a-y)**2 + 1e-14
                    assert min_baseline <= (q-y)**2 + 1e-14
                    checks += 1
                assert -1-1e-14 <= lower_t <= .8+1e-14
                if len(feasible) == 2:
                    assert upper_mismatch == 1
                    assert abs(lower_t-(.8*(q-(1-a))**2-1)) < 1e-14
        if states in [(0, 0, None), (1, 1, None), (1, 0, None), (None, None, None)]:
            a, q = 0, .5
            examples.append({"scheduled_call_states":states, "feasible_majorities":feasible,
                             "forecast_a":a, "baseline_q":q,
                             "bias_interval":[a-hi,a-lo],
                             "worst_mismatch":max(int(a!=y) for y in feasible),
                             "lower_loss_contrast":min(.8*(q-y)**2-(a-y)**2 for y in feasible)})
    return {"abstract_status_patterns":patterns, "bound_checks":checks,
            "all_bounds_valid":True, "examples":examples,
            "scope":"finite algebra checks, not experiment/detector/image data"}


def verify_forecast_abstention_bounds():
    """Verify finite A/S sets and exact minimization over singleton/[0,1] Q."""
    checks = 0
    cases = 0
    examples = []
    for aset, sset, q in product(((0,), (1,), (0, 1)),
                                ((0,), (1,), (0, 1)),
                                (0.0, .1, .5, .9, 1.0, None)):
        b_lo = min(aset)-max(sset)
        b_hi = max(aset)-min(sset)
        mismatch = max(int(a != y) for a in aset for y in sset)
        # For missing Q=[0,1] and binary y, q=y is the exact convex minimizer.
        baseline_min = min(0.0 if q is None else (q-y)**2 for y in sset)
        t_lower = min(.8*(0.0 if q is None else (q-y)**2)-(a-y)**2
                      for a in aset for y in sset)
        cases += 1
        q_candidates = [v/20 for v in range(21)] if q is None else [q]
        for a, actual_q, y in product(aset, q_candidates, sset):
            assert b_lo <= a-y <= b_hi
            assert int(a != y) <= mismatch
            assert baseline_min <= (actual_q-y)**2+1e-14
            assert t_lower <= .8*(actual_q-y)**2-(a-y)**2+1e-14
            checks += 1
        assert -1-1e-14 <= t_lower <= .8+1e-14
        if len(aset) == 2 or len(sset) == 2:
            assert mismatch == 1
        if q is None:
            assert baseline_min == 0
            assert abs(t_lower+max((a-y)**2 for a in aset for y in sset)) < 1e-14
        if q in (None, .5) and (aset,sset) in [((0,1),(0,)),((0,),(0,)),((0,),(1,)),((0,1),(0,1))]:
            examples.append({"A":aset,"Q_singleton_or_null_interval":q,"S":sset,
                             "bias_interval":[b_lo,b_hi],"worst_mismatch":mismatch,
                             "lower_loss_contrast":t_lower,"minimum_baseline_loss":baseline_min})
    # Fixed rank check uses abstract ordered values, not calibration observations.
    radius_cases=[]
    for missing in range(4):
        source_scores = list(range(1,31-missing)) + [math.inf]*missing
        radius = sorted(source_scores)[27]
        assert math.isfinite(radius) == (missing <= 2)
        radius_cases.append({"incomplete_sources":missing,"rank":28,"denominator":30,
                             "q90":radius if math.isfinite(radius) else None,
                             "kind":"finite" if math.isfinite(radius) else "positive_infinity"})
    return {"set_configurations":cases,"completion_bound_checks":checks,
            "continuous_Q_minimizer":"q=y for binary y; convex squared loss",
            "all_bounds_valid":True,"examples":examples,"abstract_radius_rank_checks":radius_cases,
            "scope":"abstract arithmetic only; no forecasts or calibration observations"}


def main():
    n, alpha, slots = 200, .05, 13
    first = alpha/slots
    out = {"purpose": "analytical prospective design; no experiments or source outcomes", "n": n,
           "family_alpha": alpha, "holm_slots": slots, "worst_case_local_alpha": first}
    rows = {}
    for name, p0, direction, alternatives in [
        ("H1_or_H4_mismatch", .1, "less", [.0, .01, .02, .03, .04, .05, .075, .1]),
        ("H2_H3_H5_quality", .8, "greater", [.8, .85, .875, .9, .925, .95]),
        ("H6", .9, "greater", [.9, .925, .95, .97, .98, .99, 1.0]),
        ("H5_removal", .5, "greater", [.5, .55, .6, .65, .7, .8]),
    ]:
        critical = lower_critical(n,p0,first) if direction == "less" else upper_critical(n,p0,first)
        power = {}
        for p in alternatives:
            power[str(p)] = cdf(n,p,critical) if direction == "less" else sf(n,p,critical)
        rows[name] = {"null_boundary":p0,"direction":direction,"critical":critical,"power":power,
                      "critical_tail": cdf(n,p0,critical) if direction=="less" else sf(n,p0,critical),
                      "next_failing_tail": cdf(n,p0,critical+1) if direction=="less" else sf(n,p0,critical-1),
                      "confidence_bound_at_critical":upper_cp(n,critical,first) if direction=="less" else lower_cp(n,critical,first)}
    out["exact_binomial"] = rows
    out["negative_bounds"] = {
        "zero_200_marginal_95_upper":1-.05**(1/n),
        "zero_200_eight_bounds_simultaneous_95_upper":1-(.05/8)**(1/n),
        "zero_200_at_Holm_first_alpha_upper":1-first**(1/n),
        "n_zero_needed_for_marginal_95_upper_at_most_1e_6":math.ceil(math.log(.05)/math.log1p(-1e-6)),
    }
    out["h4_eb"] = {
        "range_width":1.8,
        "zero_variance_radius_first_alpha":eb_radius(n,0,first),
        "radii_by_sample_sd":{str(s):eb_radius(n,s*s,first) for s in [0,.05,.1,.2,.3,.5]},
        "hoeffding_radius_first_alpha":1.8*math.sqrt(math.log(1/first)/(2*n)),
    }
    # Exact illustrative power: q=.5 always; the same worst-error indicator
    # (known error or unresolved majority) occurs in every validation cell,
    # independently across sources. Then t_lower=.2-E.
    passing=[]
    for k in range(n+1):
        r=k/n
        variance=n/(n-1)*r*(1-r)
        mean=.2-r
        p=max(cdf(n,.1,k),eb_pvalue(n,mean,variance))
        if p<=first:
            passing.append(k)
    out["h4_illustrative_perfectly_correlated_cells"]={
        "definition":"q=.5; identical Bernoulli worst-error (known error or ambiguous majority) across cells within source; iid sources",
        "passing_error_counts":passing,
        "exact_power":{str(p):math.fsum(pmf(n,p)[k] for k in passing) for p in [.0,.005,.01,.02,.03,.04,.05,.075]},
    }
    out["h4_zero_variance_min_n"]={str(b):math.floor(7*1.8*math.log(2/first)/(3*.8*b))+2 for b in [.25,.1,.04,.01]}
    # Basic identities and the inversion used to turn a bound into a p-value.
    assert abs(math.fsum(pmf(n,.1))-1)<1e-12
    assert abs(cdf(n,.1,10)-sf(n,.9,n-10))<1e-12
    test_mean=eb_radius(n,.02,first)
    assert abs(eb_pvalue(n,test_mean,.02)-first)<1e-12
    out["missingness_completion_bounds"] = verify_completion_bounds()
    out["forecast_abstention_completion_bounds"] = verify_forecast_abstention_bounds()
    Path(__file__).with_name("stats-design.json").write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2))


if __name__=="__main__":
    main()
