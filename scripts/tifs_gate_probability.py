"""Analytical gate sensitivity, not experimental outcomes or fitted power.

Standard library only. No random draws, images, saved run files or model imports.
All probabilities are exact finite sums evaluated in binary floating point.
Run with the approved stdlib interpreter and -I. --self-test checks identities;
--output writes only an explicitly requested analytical JSON artifact.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def probability(p):
    if not math.isfinite(p) or not 0 <= p <= 1:
        raise ValueError("Probability must be finite and in [0,1]")
    return p


def binomial_pmf(n, p):
    probability(p)
    if type(n) is not int or n < 0:
        raise ValueError("n must be a nonnegative integer")
    return [math.comb(n, k) * p**k * (1-p)**(n-k) for k in range(n+1)]


def tail(n, p, threshold):
    return math.fsum(binomial_pmf(n, p)[max(0, threshold):])


def beta_binomial_pmf(n, mean, rho):
    """Exchangeable Bernoulli mixture, rho = intraclass correlation.

    rho=0 is independent Bernoulli; rho=1 is one shared Bernoulli variable.
    For seed counts the latent rate is redrawn independently for every source.
    For source counts this describes a *shared cohort* random effect instead.
    Independent source-specific heterogeneity alone is not this latter model.
    """
    probability(mean)
    probability(rho)
    if rho == 0 or mean in (0, 1):
        return binomial_pmf(n, mean)
    if rho == 1:
        return [1-mean] + [0.] * (n-1) + [mean] if n else [1.]
    concentration = (1-rho)/rho
    a, b = mean*concentration, (1-mean)*concentration
    def rising(x, k):
        return math.prod(x+i for i in range(k))
    den = rising(a+b, n)
    return [math.comb(n, k)*rising(a, k)*rising(b, n-k)/den for k in range(n+1)]


def majority_probability(per_seed, rho=0):
    return math.fsum(beta_binomial_pmf(3, per_seed, rho)[2:])


def joint_success(candidate_p, comparator_p, association=0):
    """Interpolate independence to maximal positive overlap, not Pearson rho.

    association=0 gives P(A=B=1)=pA*pB; 1 gives min(pA,pB).
    This is one admissible sensitivity family, not a fitted correlation model.
    """
    probability(candidate_p)
    probability(comparator_p)
    probability(association)
    return candidate_p*comparator_p + association*(min(candidate_p, comparator_p)-candidate_p*comparator_p)


def comparator_cdf_given_candidate_count(n, x, limit, candidate_p, comparator_p, joint):
    """P(Y<=limit | X=x), for iid paired Bernoulli source outcomes.

    Y = Bin(x, joint/pA) + Bin(n-x, (pB-joint)/(1-pA)).
    Includes exact boundary handling where the conditional group is empty.
    """
    lo, hi = max(0, candidate_p+comparator_p-1), min(candidate_p, comparator_p)
    if not lo-1e-12 <= joint <= hi+1e-12:
        raise ValueError("Invalid joint Bernoulli success probability")
    if limit < 0:
        return 0.
    if limit >= n:
        return 1.
    if (candidate_p == 0 and x != 0) or (candidate_p == 1 and x != n):
        raise ValueError("Conditioning on an impossible candidate count")
    yes = joint/candidate_p if candidate_p else 0.
    no = (comparator_p-joint)/(1-candidate_p) if candidate_p < 1 else 0.
    a, b = binomial_pmf(x, max(0., min(1., yes))), binomial_pmf(n-x, max(0., min(1., no)))
    return math.fsum(av*bv for i, av in enumerate(a) for j, bv in enumerate(b) if i+j <= limit)


def cell_probability(candidate_p, controls=(), absolute=12, n=16):
    """P(X>=absolute and X-Y_i>=gain_i for all supplied comparators).

    A control is {p, gain, association}. Source pairs are iid. Comparator
    outcomes are conditionally independent GIVEN THE CANDIDATE'S SOURCE
    INDICATOR; they are not generally marginally independent. This assumption
    makes the product of conditional CDFs exact for the declared model.
    C and J are treated as coincident in the profile grids, not independent.
    """
    terms = []
    for x, mass in enumerate(binomial_pmf(n, candidate_p)):
        if x < absolute or mass == 0:
            continue
        factors = []
        for ctrl in controls:
            joint = joint_success(candidate_p, ctrl["p"], ctrl.get("association", 0))
            factors.append(comparator_cdf_given_candidate_count(n, x, x-ctrl["gain"], candidate_p, ctrl["p"], joint))
        terms.append(mass*math.prod(factors))
    return math.fsum(terms)


def frechet_intersection(probabilities):
    return dict(lower=max(0., math.fsum(probabilities)-len(probabilities)+1),
                independent=math.prod(probabilities), upper=min(probabilities))


def profile_probability(candidate_p, retained_p, ablation_p, budget_p, association=0):
    """Foreign-cell efficacy only; omitted gates pass identically in this model.

    Equal candidate/control rates across the three foreign cells are a
    sensitivity simplification. Product assumes independent cells. Actual
    shared sources, models and endpoints violate independence in general.
    """
    cells = []
    for cell, gain, ablation_gain in (("R1-0.1", 4, 3), ("R1-0.2", 4, 3), ("K3-0.2", 3, 1)):
        retained = dict(p=retained_p, gain=gain, association=association)
        ablation = dict(p=ablation_p, gain=ablation_gain, association=association)
        budget = dict(p=budget_p, gain=gain, association=association)
        cells.append(dict(cell=cell,
            round1=cell_probability(candidate_p, [retained, ablation, ablation]),
            ablations_secondary_only=cell_probability(candidate_p, [retained]),
            round3_proposed=cell_probability(candidate_p, [retained, budget])))
    return dict(cells=cells, **{profile: frechet_intersection([r[profile] for r in cells])
        for profile in ("round1", "ablations_secondary_only", "round3_proposed")})


def article_comparison_probability(candidate_p, vine_p, association=0):
    """Article comparison block plus foreign absolute bars, C=J toy model.

    Requires independent cells and all quality gates fixed to pass. Does NOT
    include the complete thesis gate or condition the candidate distribution
    on having passed that gate. A quality edge is treated as a fixed branch.
    """
    ni = dict(p=vine_p, gain=-1, association=association)
    edge = dict(p=vine_p, gain=3, association=association)
    r0 = cell_probability(candidate_p, [ni], absolute=0)
    foreign = cell_probability(candidate_p, [ni])
    gain = cell_probability(candidate_p, [edge])
    return dict(if_quality_edge_absent=r0*(foreign**3-(foreign-gain)**3),
                if_quality_edge_present=r0*foreign**3)


def report():
    source_grid = [.30, .40, .50, .60, .65, .70, .75, .80, .85, .90, .95]
    seed_grid = [.50, .60, .65, .70, .75, .80, .85, .90, .95]
    absolute = []
    for p in source_grid:
        rows = {str(k): tail(16, p, k) for k in (10, 11, 12, 13)}
        absolute.append(dict(per_source_majority_p=p, by_required_count=rows,
            three_cells_12=frechet_intersection([rows["12"]]*3)))
    seed = [dict(per_seed_p=p, seed_icc=rho, per_source_majority_p=(q := majority_probability(p, rho)),
                 one_cell_12=tail(16, q, 12), three_independent_cells_12=tail(16, q, 12)**3)
            for p in seed_grid for rho in (0., .2, .5, 1.)]
    across_sources = [dict(per_source_majority_p=p, source_icc=rho,
        one_cell_12=math.fsum(beta_binomial_pmf(16, p, rho)[12:]))
        for p in (.6, .75, .9) for rho in (0., .05, .15, .3)]
    scenarios = []
    # Deliberately hypothetical rates. No rates are estimated from study data.
    for p in (.6, .7, .8, .9, .95):
        for b, a, m in ((.3, .5, .3), (.3, .7, .5), (.5, .8, .7)):
            for association in (0., .5, 1.):
                scenarios.append(dict(candidate_p=p, retained_f5_p=b, each_ablation_p=a,
                    f5_budget_p=m, association=association,
                    foreign_efficacy_other_gates_fixed_pass=profile_probability(p, b, a, m, association)))
    gains = [dict(candidate_p=p, comparator_p=b, gain=g, association=assoc,
        pass_probability=cell_probability(p, [dict(p=b, gain=g, association=assoc)]))
        for p in (.7, .8, .9) for b in (.1, .3, .5, .7, .9) for g in (0, 1, 3, 4) for assoc in (0., 1.)]
    article = [dict(candidate_p=p, vine_p=b, association=assoc,
        comparison_block=article_comparison_probability(p, b, assoc))
        for p in (.7, .8, .9) for b in (.5, .7, .9) for assoc in (0., 1.)]
    auxiliary = [dict(per_source_probability=p, all_16_strict_quality=p**16,
        clean_F_at_least_15=tail(16, p, 15), zero_16_independent_source_any_event_clusters=(1-p)**16)
        for p in (.001, .01, .02, .05, .90, .95, .98, .99, .995)]
    return dict(schema="tifs-r3-analytical-gate-sensitivity-v1", status="ANALYTICAL_ASSUMPTIONS_ONLY_NOT_SCIENTIFIC_OUTPUT",
        experimental_outputs_read=False, random_simulation=False, n_sources=16, seeds_per_source=3,
        note="Finite sums, float arithmetic. No posterior, empirical power or publication probability. Grids are hypothetical.",
        source_rate_grid=absolute, seed_correlation_grid=seed, source_correlation_grid=across_sources,
        profile_scenarios=scenarios, paired_gain_grid=gains, article_comparison_grid=article, auxiliary_gate_grid=auxiliary,
        omissions=["Quality, clean F, negative events, R0 retention and inventory are set to pass deterministically in profile_scenarios; their joint distributions are not inferred.",
                   "C and J coincide in profile_scenarios. Real J implies C, but paired C gains can still fail independently of J gains.",
                   "Across-cell product is a model illustration; Frechet bounds retain arbitrary across-cell dependence.",
                   "Quality and method rates are not known. A unique unconditional whole-gate probability is unidentified."],
        full_gate_identity="P(GO)=P(foreign efficacy)*P(all remaining conditions | foreign efficacy), with exact joint dependence retained.")


def self_test():
    for p in (0., .1, .5, .9, 1.):
        assert math.isclose(math.fsum(binomial_pmf(16, p)), 1., abs_tol=1e-12)
        assert math.isclose(majority_probability(p), 3*p*p-2*p*p*p, abs_tol=1e-12)
        for rho in (0., .2, .5, 1.):
            assert math.isclose(math.fsum(beta_binomial_pmf(16, p, rho)), 1., abs_tol=1e-12)
        assert math.isclose(majority_probability(p, 1.), p, abs_tol=1e-12)
        assert math.isclose(cell_probability(p), tail(16, p, 12), abs_tol=1e-12)
        assert math.isclose(cell_probability(p, [dict(p=p, gain=0, association=1)]), tail(16, p, 12), abs_tol=1e-12)
        assert cell_probability(p, [dict(p=p, gain=1, association=1)]) < 1e-12
    # Independent comparison also has a direct double-binomial finite sum.
    direct = math.fsum(px*py for x,px in enumerate(binomial_pmf(16, .8))
                      for y,py in enumerate(binomial_pmf(16, .3)) if x >= 12 and x-y >= 4)
    assert math.isclose(direct, cell_probability(.8, [dict(p=.3, gain=4)]), abs_tol=1e-12)
    # Verify the paired conditional sum against an independent joint-state DP.
    n, pa, pb, joint = 4, .7, .4, .35
    states = {(0, 0): 1.}
    for _ in range(n):
        nxt = {}
        for (x, y), mass in states.items():
            for dx, dy, pr in ((1,1,joint), (1,0,pa-joint), (0,1,pb-joint), (0,0,1-pa-pb+joint)):
                key = (x+dx, y+dy)
                nxt[key] = nxt.get(key, 0.)+mass*pr
        states = nxt
    expected = math.fsum(v for (x,y),v in states.items() if x >= 2 and x-y >= 1)
    assoc = (joint-pa*pb)/(min(pa,pb)-pa*pb)
    assert math.isclose(expected, cell_probability(pa, [dict(p=pb, gain=1, association=assoc)], absolute=2, n=n), abs_tol=1e-12)
    assert cell_probability(.9, [dict(p=1., gain=1)]) == 0.


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    if args.self_test:
        self_test()
        print("Analytical identities passed; no experiment run.")
    if args.output:
        args.output.write_text(json.dumps(report(), indent=2, allow_nan=False)+"\n", encoding="utf-8")
        print(str(args.output))
    if not args.self_test and not args.output:
        parser.error("Specify --self-test and/or --output")


if __name__ == "__main__":
    main()
