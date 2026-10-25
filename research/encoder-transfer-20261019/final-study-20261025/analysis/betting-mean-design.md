# Prospective bounded-mean design: fixed betting mixture for H4

2026-10-25. This is one bounded statistical design contribution, not an independent review, an experiment result, an execution authorization or an amendment to the primary protocol. The authoritative MAIN STATE was read once. Only this file and the accompanying [analytical calculation](betting-mean-bounds.py) and [output](betting-mean-bounds.json) were written. No images, models, retained experimental outcomes, scientific libraries or new experimental data were used. The root researcher decides adoption; independent review remains separate.

**Recommendation: adopt the uniform six-bet mixture below as H4's sole primary paired-risk certificate, prospectively before new Phase A/B measurements, and retain the existing Maurer–Pontil empirical-Bernstein (EB) calculation as a named secondary sensitivity.** The mixture is finite-sample valid for the existing composite mean null and substantially improves the specified analytical power scenarios. It does not change n=200, .10 rate tolerance, 20% risk improvement, source/family weights, the 13 Holm slots, the forecast/outcome masks or prerequisites. It does not guarantee adequate power against every strong comparator. Root's explicit design decision is to retain the uniform weights; the alternative calculation in section 7 is not adopted.

## 1. Fixed prescription and direct finite-sample proof

Write Z_i=t_lower,i for the existing robust source-level loss contrast, with Z_i in [-1,.8]. Conditional on the qualified, fitted and frozen Phase-A procedure, assume the 200 Phase-B source vectors are iid from the declared population. The null is H_B: E[Z_i] <= 0. The source vector includes its within-source cells, seeds, forecasts, outcomes and availability states. Nothing here makes those within-source quantities independent.

Freeze the six bets and their weights before Phase A:

`Lambda={1/16,1/8,1/4,1/2,3/4,1}; w_lambda=1/6.`

For each lambda define `K_lambda=product_(i=1)^200 (1+lambda*Z_i)` and define `E_mix=(1/6)*sum_lambda K_lambda`. The primary mean-component p-value is

`p_bet=min(1,1/E_mix)`, with `p_bet=1` if `E_mix=0`.

For every distribution in H_B, each factor is nonnegative because Z_i>=-1 and 0<=lambda<=1. Moreover `E[1+lambda*Z_i]=1+lambda*E[Z_i]<=1`. Conditional independence gives

`E[K_lambda]=product_i E[1+lambda*Z_i]<=1`.

Linearity gives `E[E_mix]<=1`. Thus, for any alpha in (0,1), Markov's inequality yields `P(p_bet<=alpha)=P(E_mix>=1/alpha)<=alpha`. This proves a valid conservative p-value for the entire composite null, including its boundary. It is not an exact nominal-size p-value, a likelihood fitted to outcomes, a normal approximation or a resampling test. No extra factor of two belongs in this one-sided test. At the first Holm threshold .05/13=1/260, reject this component exactly when `E_mix>=260`.

The same proof can be written by conditional expectations for a supermartingale under `E[Z_i | previous source vectors, Phase A]<=0`; iid under the stated null suffices. This stronger mathematical fact does not authorize optional sampling or change the protocol: the proposed test uses exactly the scheduled n=200 sources and the final mixture only. With fixed bets it is also invariant to source order.

The six products must be **averaged**, not maximized. Maximizing over them and taking the reciprocal without correction is invalid. In particular, do not optimize lambda on the Phase-B losses or choose whichever mixture, EB result or missingness treatment gives the smallest p-value. The grid includes several scales and the maximal legal positive bet as a simple, fixed distribution-free diversification. It is not claimed to be optimal.

## 2. Robust completion, Phase A and H4 composition

The frozen A/Q/S sets and original family weights define, for every feasible numerical completion C,

`Z_i=sum_c w_c min_(a,q,y in A_ic x Q_ic x S_ic)[.8*(q-y)^2-(a-y)^2] <= t_i(C)`.

This inequality is pointwise; no missing-at-random assumption or invented probability distribution over completions is required. For any completion whose population risk target fails, `E[t_i(C)]<=0`, hence `E[Z_i]<=0`. Therefore rejection of H_B provides a conservative certificate of **more than** 20% population Brier improvement for every feasible completion. As before, strict improvement implies positive baseline population risk. The existing robust sample point criteria, including B_Q,min>0 and the per-cell .10 bias bounds, remain required rather than being replaced by this test.

The incomplete procedure must still be described as a guarantee over numerical completions, not as complete forecast delivery or a measured physical outcome for an unavailable image. It does not show that the actual unobserved completion fails when this certificate is inconclusive.

Let `p_cal,c` be the unchanged exact worst-mismatch certificate for every required cell. Set

`p4=max(p_bet, all p_cal,c)`

and retain all existing p4=1 structural, fit, freeze and robust-point-criterion gates. Under H4's union null, at least one component p-value is valid for a true component null. The event p4<=alpha implies that true component p<=alpha, so p4 is valid without within-H4 Bonferroni correction and regardless of dependence among its components. Setting p4=1 for a failed gate can only remove rejections. Enter this p4 into the unchanged 13-slot Holm procedure, which controls FWER under arbitrary dependence. No separate confirmatory discovery is assigned to the mean component alone.

The validity is conditional on the actual frozen Phase-A fit and calibration procedure, provided Phase B is independent and satisfies the declared sampling assumptions. It gives predictive-risk inference for that procedure, not uncertainty over hypothetical refits or a population of encoder families. Do not condition this proof on the entire realized Phase-B forecast/covariate array: the iid guarantee is over source vectors, not an assertion that every realized source has conditional mean <=0. No Phase-B fitting, feature normalization, choice of grid, weighting or subset selection is permitted.

A shared outage, acquisition grouping, outcome-dependent availability or dataset-wide adaptive processing must not silently be assumed to yield iid source vectors. Arbitrary **within-source** missingness is allowed; arbitrary **between-source** dependence is not justified by this proof. The existing declared source-population assumptions remain essential. Likewise, a random sample without replacement from one fixed finite list requires a separately specified without-replacement method; this document does not supply it.

## 3. Numerical prescription

For each lambda use `ell_lambda=sum_i log1p(lambda*Z_i)`. If any factor is exactly zero (possible at lambda=1 and Z_i=-1), set that component's ell to negative infinity; its product contributes zero. Do not replace a zero by an epsilon or drop it while retaining the remaining factors. If a calculated factor is negative or a Z_i is nonfinite/outside the proven range, resolve the upstream error; do not silently clamp favorable values.

Compute `m=max_lambda ell_lambda` and, if m is finite,

`logE=m+log(sum_lambda exp(ell_lambda-m))-log(6)`.

If all components are negative infinity, E=0 and p=1. Otherwise `logp=min(0,-logE)`; report p by exponentiating only for display, and use logs for small values and threshold comparisons. Use compensated or accurately rounded summation. The mixture weights remain exactly one sixth even if one component is zero. With legal inputs the five bets below one remain positive; thus all components cannot actually die under this particular grid, but the general implementation branch is harmless.

Floating-point logsumexp alone is a stability technique, not a proof of conservative rounding. For decisions, specify a certified lower bound on E (equivalently an upper bound on p), or an exact rational boundary check. The persisted comparator probabilities may be treated as exact binary or decimal rational predictions; the minima of their squared losses, binary law/outcome states and rational family weights then make every Z_i rational. Computing these contrasts and the six finite products with exact rational arithmetic gives an exact E and exact threshold comparison for the defined numerical forecasts. If instead upstream calculations provide interval enclosures, use the lower enclosure for each Z_i: every factor, product and mixture is nondecreasing in each Z_i, so that E_lower<=E_true and `min(1,1/E_lower)` is conservative. Do not assume that an undocumented fixed epsilon bounds all accumulated errors. The separate calibration tails and Holm ordering also need their existing full-precision/conservative handling.

The accompanying script uses exact `fractions.Fraction` arithmetic for all scenario rejection comparisons, binomial sums and minimum-n searches. It uses float logsumexp only as a checked illustration and float conversion only to print the final exact-rational probabilities. It is an analytical design calculator, not an authorized server implementation.

## 4. Exact analytical scenario power at n=200

Use the existing illustrative scenario: q=.5 in every source/cell; a Bernoulli worst-error event with probability e is shared across all cells of a source and independent across sources. It represents either a known wrong law prediction or the specified law/target majority ambiguity. Then Z_i=.2-error_i, and for k errors,

`E_mix(k)=(1/6)*sum_lambda (1+.2*lambda)^(200-k)*(1-.8*lambda)^k`.

The mean component passes at error counts **0 through 20**, inclusive; its p-values at k=20 and 21 are .0029279430 and .0062828325. The unchanged per-cell mismatch component passes only **0 through 9** at the first Holm threshold. Every cell shares the same error count here, so the full H4 conjunction passes exactly 0 through 9; no independence across cells or multiplication of component powers is used. At k=9, p_bet is about 7.65e-9 while p_cal is .0035285655. The original EB conjunction passed 0 through 5.

| Source error probability e | Uniform betting H4 power | Prior EB H4 power |
|---|---:|---:|
| .01 | .99995986 | .98397709 |
| .02 | .99252071 | .78672247 |
| .03 | .91922064 | .44322921 |
| .04 | .71920000 | .18564969 |
| .05 | .45470981 | .06234250 |
| .075 | .06251224 | .00211971 |

These are exact finite binomial-sum scenario powers, conditional on that stipulated distribution, not estimated empirical powers or predictions about the final study. The binomial CDF at 9 is the betting joint power. Actual Holm rejection can occur at a less demanding later rank. Different error concentration, within-source cell correlation, comparator performance and missing comparator probabilities change the result; unavailable Q is not represented by this scenario.

## 5. Perfect-law constant-baseline limits

For a perfect law and constant source-level baseline Brier loss b>0, every Z_i=.8b and the mixture is `(1/6)*sum_lambda(1+.8b*lambda)^n`. The following are the minimum sample sizes for the **mean component** at alpha=1/260. They are analytical sensitivity values, not proposed new sample sizes. n remains 200. A full H4 claim also needs every other gate; for example even perfect calibration requires enough zero-error sources for its own certificate.

| Constant baseline Brier b | Prior EB minimum n | Uniform betting minimum n | Uniform betting p at n=200 |
|---|---:|---:|---:|
| .25 | 133 | 40 | 8.7461e-16 |
| .10 | 330 | 94 | 1.2105e-6 |
| .04 | 822 | 228 | .00867311 |
| .01 | 3,285 | 900 | .42047783 |

Thus the new certificate removes the EB zero-variance radius floor as the practical blocker for the b=.10 example. It still does **not** guarantee first-Holm support at b=.04, even with a perfect law. Its .00867311 p-value could pass at rank 9 or later if all earlier Holm comparisons pass; it cannot be assumed to reach that rank. At b=.01 the mean p exceeds .05. A statistically stronger method does not cure the limited information against a near-perfect comparator, and the comparator must not be weakened to make this table look better.

## 6. Limitations and failure modes

The uniform grid is not universally superior to EB. For example, let Z=.8 with probability (1+.001)/1.8 and Z=-1 otherwise. Its mean is .001>0. For the five bets below one, expected log factors are respectively approximately -.001515, -.006270, -.026308, -.120564 and -.353986. The lambda=1 product becomes zero at the first -1. Therefore this fixed finite mixture tends to zero almost surely as n grows, whereas the EB lower bound eventually becomes positive. This is an explicit counterexample to universal consistency/dominance, not a prediction about n=200 or the Phase-B distribution. An infinite grid or predictable strategy could address that separate asymptotic issue; adding it here is unnecessary design complexity.

Other failure modes are using individual seeds/cells as independent factors; pooling an unweighted loss after freezing family weights; choosing bets or weights from the final losses; forgetting the mixture penalty; using worst mismatch for calibration but favorable completions for risk; refitting after seeing Phase B; treating a late missing required family as harmless sporadic missingness; or presenting non-rejection as proof the law fails. The new test changes none of these restrictions. If loss observations are not the specified bounded lower contrasts, the proof is inapplicable.

Keep `p_EB`, its lower bound and the earlier power calculations under an explicit secondary/sensitivity label. Do not take `min(p_bet,p_EB)` or choose the reported primary test after outcomes. Any future confirmatory combination would need its own prospectively valid construction; it is not part of this recommendation.

## 7. Unadopted analytical alternative, preserved for transparency

One additional fixed mixture was calculated before outcomes: weight 1/2 at lambda=1 and 1/10 at each of the other five bets. Root explicitly declined it and selected the uniform grid, avoiding further weight optimization around one hypothetical comparator value. The alternative remains only in the calculator/output as an unadopted design check. Its constant-b minima are 34/81/197/779 for .25/.10/.04/.01, while its q=.5 mean-component cutoff is 19 errors instead of 20; its joint cutoff remains 9. Neither these weights nor a favorable choice between mixtures may be selected after measurements. Algebraically `E_half=.6*E_uniform+.4*K_1`; the alternative is valid but is not the adopted prescription.

## 8. Primary source inspection and reproducibility

The foundational statistical mechanism was checked in Waudby-Smith and Ramdas, *Estimating means of bounded random variables by betting*: [arXiv:2010.09686v7, submitted revision 25 August 2022](https://arxiv.org/pdf/2010.09686v7), Section 4 and Appendix A.3–A.4, printed pp.32–33. The inspected proof takes the conditional expectation of a nonnegative product, and explains the analogous supermartingale construction. The [RSS discussion-paper version](https://rss.org.uk/RSS/media/File-library/Events/Discussion%20meetings/Estimating-means-of-bounded-random-variables-by-betting.pdf), Section 4, Propositions 2–3 and Section 2.1, was also opened. The published bibliographic identity is JRSS B 86(1), 2024, pp.1–27, [DOI 10.1093/jrsssb/qkad009](https://doi.org/10.1093/jrsssb/qkad009); the publisher full-text fetch failed, so the proof-reading claim is specifically for the opened preprint, not the final journal supplement. This document's six-point uniform test and proof are a simple fixed-mixture specialization derived above, not a claim to implement that paper's optimized hedged confidence interval.

Access date: 2026-10-25. Search query: `Waudby-Smith Ramdas Estimating means of bounded random variables by betting JRSSB 2024 pdf`. No paper/code/package was downloaded to the workspace. The isolated approved stdlib interpreter ran the final calculator in approximately 1.1 seconds. It checks exact null factor expectations, scenario cutoff comparisons, exact binomial powers, minimum-n boundaries, zero-factor handling and agreement of illustrative logsumexp with exact rational arithmetic. No primary-protocol, review or shared-log file was edited and no commit was made by this contributor.
