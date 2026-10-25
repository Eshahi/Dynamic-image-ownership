# H4 prediction and scoring contract: preserve the two-quantity law

Status: mathematical design refinement, 2026-10-25. This note resolves an incompatibility between the prospective H4 promise in `03-hypotheses.md` and the proposed margin criteria in `analysis/theory-design.md`. It does not amend either file or claim an approved protocol. The author read the authoritative MAIN STATE once, the two named design files, and no new result journals. No experiment, model, metric, interpreter or server was run.

## 1. Decision: a deterministic forecast is the minimal defensible primary law

Retain the 320-chip law `p_hat = b + kappa v`, the exact frozen detector mapping, and the unmarked-output semantic proxy. Fit only the one global transport gain kappa on the 30 designated fit sources. Retain the one global q90 margin-calibration radius from the separate 30 calibration sources. These are the two learned quantities of the primary law. No family, strength, seed, source or descriptor-reliability coefficient is added.

For source i, validation cell c and scheduled seed s, form:

- `a_ics = C_frozen(p_hat_ics, f0_ics)` in {0,1}, including every native decoding and soft-binding rule;
- `a_ic = 1[sum_s a_ics >= 2]` for the fixed three-seed design;
- `y_ic = 1[sum_s C_actual_ics >= 2]` for the corresponding observed source-majority endpoint.

For a deterministic single-output control, use its single predicted and actual C directly. Such controls must not be added to the main H4 weights after outcomes are seen.

The primary predictive value for Brier scoring is **a_ic itself, either zero or one**. It is a deterministic class forecast, equivalently a degenerate predictive distribution, not an estimated calibrated conditional probability. Its Brier loss is exactly `(a_ic-y_ic)^2 = 1[a_ic != y_ic]`. This choice is deliberately unforgiving: confidently wrong forecasts receive loss one. Do not describe its scores as evidence of probabilistic calibration. The rate criterion tests calibration in the large at each cell, not reliability of a probability model.

This resolves the missing probability law without inventing a noise distribution, exceeding the two-quantity budget, or using confirmation residuals. It does not guarantee that H4 will pass. The continuous margin and q90 interval remain useful companion diagnostics; they cannot replace either promised C criterion.

## 2. Why q90 cannot supply the missing probabilities

The calibration statistic in the theory note is one sourcewise maximum absolute **decoded-score** residual over a finite grid. Its 28th order statistic among 30 complete calibration sources is a radius, not a standard deviation, a signed-error distribution, or a conditional probability. In particular:

1. Many residual distributions have the same absolute 90th percentile and arbitrarily different probabilities of crossing a particular signed read threshold. A Gaussian conversion such as `Phi(M_hat/q90)` assumes information never fitted or justified.
2. A decoded score does not identify the decoded word or the semantic-binding state. Even a valid read-margin probability would not be a probability for compound C.
3. Joint residuals across chip coordinates, seeds and binding variables determine the source-majority event. One marginal radius contains none of this dependence.
4. Same-distribution sourcewise interval coverage does not imply conditional coverage for every source or any coverage guarantee on a withheld family.

A stochastic alternative would have to predeclare a full joint residual-and-descriptor-error distribution and its scaling before Phase A, then integrate the entire frozen detector and majority event under that distribution. A covariance matrix, empirical residual library, copula, chip noise model or probability calibrator is additional learned structure even if labelled a single object. A scalar Gaussian added only to D does not solve C. Such alternatives are separate model proposals, not innocuous ways of interpreting q90. The deterministic contract is preferable for the already promised primary law.

## 3. What information is available, and when

The forecast is explicitly a privileged scientific measurement. It uses the original unmarked source x, its final marked INPUT x+delta, target model internals, the frozen reader, exact paired noise tensors, and an UNMARKED target trajectory for each scheduled seed. It is not a blind operational detector, a model-name-only forecast or a cheap attack predictor.

From that C0 trajectory obtain background chips b, the floating-path tangent v, and the unchanged seven-view semantic descriptor f0. The source/marked INPUT pair may supply the exact target-encoder displacement. A derivative may be evaluated along C0; it may not be evaluated at the marked target output. C0 itself may be generated during confirmation because it is declared predictor information, not the marked outcome.

Freeze all target-source/cell/seed predictions, quality-comparator forecasts, identities and validity flags before generating or releasing any target marked-output detection result. This order is stronger and easier to audit than merely promising not to use a detector field. No target marked-output pixel, LPIPS, chip, decoded word, semantic descriptor, derivative, error rate or C status may enter its own predictor. Do not use marked-output finite differences as a tangent substitute.

After forecast release, the actual marked output and metrics may be read for evaluation and the previously specified semantic-proxy diagnostic. None may update kappa, q90, baseline coefficients, cell weights, thresholds or the declared model form.

## 4. Use a quality-only comparator that can actually forecast

The historical diagnostic regressions use realized `LPIPS(marked target output, marked input)`, and possibly PSNR/SSIM of that pair. Those quantities are unavailable before the marked output exists. Their historical cross-validation is an explanatory diagnostic conditional on realized quality; it does not make them eligible pre-output forecasts. Using them for the prospective 20% benchmark would compare incompatible information sets. Calling this an especially strong oracle benchmark is permissible only as a separately labelled post-output analysis, never as an undisclosed replacement of H4.

**Recommended prospective baseline, to freeze before Phase A:** for each source/cell compute

`Q_ic = mean_s LPIPS(C0_target_ics, marked_input_i)`.

This uses the identical planned seed set and output preprocessing, with the pinned LPIPS implementation. It is a proxy distortion of the unmarked trajectory relative to the published mark; it is not the actual marked-output attack distortion. It is available from the law's allowed information. Do not replace this definition with `LPIPS(C0,x)` after comparing fits.

Fit one pooled source-majority logistic model on the SAME 30 fit sources and SAME R0/R1 training cells:

`q_ic = sigmoid(beta0 + beta1 Q_ic)`, with `beta1 <= 0`.

Minimize the equally source-and-cell-weighted Bernoulli negative log likelihood plus the fixed penalty `0.5*(beta0^2+beta1^2)`. Use raw LPIPS units: no learned standardization, feature selection, family indicator or validation-chosen penalty. Penalizing both coefficients makes even a constant-label training set have a finite unique fit; publish any adverse limitation of this baseline. Freeze numerical tolerances and the solver before Phase A. The baseline's two coefficients are separate from the primary law's kappa/q90 budget, and must be explicitly counted as comparator parameters.

Crucially, fit the baseline directly to y_ic, the majority outcome. Do not fit seed probabilities and then pretend their mean or an independent-binomial majority formula predicts y_ic. The logistic model is a stipulated conditional prediction model; its prospective accuracy, including on the withheld family, is measured rather than assumed.

This gives information-availability parity: both methods may use original/marked inputs and C0 outputs before marked outcomes. It intentionally gives the quality-only comparator only quality features while the law additionally uses mechanistic features. It does not establish identical information content, computational cost, or superiority over every possible quality predictor. Its honest conclusion is relative to this frozen C0-quality baseline. Report the constant training-prevalence forecast as a diagnostic; do not switch the primary comparator to whichever is easiest to beat.

If the baseline is not fitted and frozen, or its required C0 quality is unavailable, the 20% criterion is not evaluable. Do not substitute the historical marked-output-quality regression without a new prospective contract.

## 5. Seed dependence and aggregation

The independent sampling unit is the source (or a larger acquisition group if related sources share one). Keep all cells, all seeds, C0 trajectories, predictions and outcomes together when resampling. The three seed labels are repeated measurements conditional on one source, not three independent images. The primary endpoint is the majority of the three fixed scheduled outcomes; it does not estimate a hypothetical infinite-seed success rate.

Even knowing the three marginal success probabilities does not determine a majority probability. For example, the distribution giving probability 1/4 to each of `111,100,010,001` has each seed marginal 1/2 and majority probability 1/4. Its complemented distribution on `000,011,101,110` has the same marginals and majority probability 3/4. An independent-binomial calculation would give 1/2 and is justified by neither set of marginals.

The deterministic scheme simply applies the actual majority rule to the three jointly computed forecasts. It needs no independence assumption about seeds. The direct majority logistic comparator likewise avoids reconstructing a joint seed distribution from marginals. Future randomized-seed-population claims would need an explicitly sampled seed-block design and remain distinct from this fixed-seed endpoint.

## 6. Exact retained H4 criteria and fixed weights

Choose the validation cells before Phase A, including development-supported high- and low-retention challenges and a family excluded from fitting/calibration. Historical knowledge of that family's aggregate behavior must be disclosed; it is family-held-out relative to model fitting, not a previously unknown model. Never replace a failed or inconvenient challenge after observing confirmation.

Let n be the fixed number of fresh independent source units, m the fixed number of validation cells and w_c their frozen weights. Recommended weights are equal across predeclared family blocks and equal across cells within each block, so a family with many floor-strength cells cannot dominate. Freeze the exact list and numerical weights; require `sum_c w_c=1`. The calibration criterion remains unweighted and mandatory for EVERY designated cell.

Define

`d_c = (1/n) sum_i (a_ic-y_ic)`;

`B_L = (1/n) sum_i sum_c w_c (a_ic-y_ic)^2`;

`B_Q = (1/n) sum_i sum_c w_c (q_ic-y_ic)^2`;

`T = 0.8 B_Q - B_L`.

A numerical H4 pass requires **all** `abs(d_c) <= 0.10` and **T >= 0**, with `B_Q > 0`. T >= 0 is exactly at least 20% lower Brier error. If B_Q=0, positive relative improvement is undefined/unattainable; two perfect predictors do not establish a 20% improvement. No division-by-small-B_Q workaround is permitted. Report per-cell Brier scores and paired loss differences as well as the aggregate.

The theory note's proposed 85% agreement, 20% margin-error improvement, 85% interval coverage and q90<=1 criteria are distinct proposed diagnostics/additional tests. None supersedes the already promised .10/20% C criteria. A scalar margin law cannot be promoted to a successful C law after the proxy fails.

Constant-floor forecasts must be explicitly scored as a diagnostic on the identical grid. If all actual validation cells collapse to floor despite the planned high/low design, disclose the loss of discrimination; a nominal H4 numerical pass then supplies no persuasive evidence for a nontrivial survival mechanism. Do not repair that failure by changing the cell weights or selecting new cells after outcomes.

## 7. Source uncertainty: numerical success versus supported success

The existing promise requires a source-level uncertainty assessment but does not fix whether confidence bounds themselves must meet the tolerances. WP5 must decide this before execution. Record these as different conclusions, not silently interchangeable gates:

- **Numerical pass:** the exact point criteria in section 6 pass.
- **Statistically supported pass:** simultaneous uncertainty bounds also establish every .10 tolerance and the 20% improvement.
- **Inconclusive support:** point criteria pass but uncertainty reaches a failure region. This is not permission to claim a securely established law.

A rigorously conservative, distribution-free supported-pass rule is available without any fitted probability model. Conditional on the frozen Phase-A models, assume independent identically sampled fresh source units from the declared target population. Define source contributions `t_i = sum_c w_c[0.8(q_ic-y_ic)^2-(a_ic-y_ic)^2]`, which lie in [-1,0.8]. Each calibration difference lies in [-1,1]. With `alpha_cal=alpha_B=0.025`, simultaneous Hoeffding bounds are

`r_cal = sqrt(2 log(2m/alpha_cal)/n)`;

`r_B = 1.8 sqrt(log(1/alpha_B)/(2n))`.

With probability at least .95, all population cell differences lie within `d_c +/- r_cal` and the population improvement contrast is at least `T-r_B`. A supported pass therefore requires `abs(d_c)+r_cal <= .10` for every cell and `T-r_B >= 0`, as well as the defined positive-baseline condition. Dependence between cells and seeds is unrestricted; independence is required only between the sampled source units. These are bounds on performance of the fitted, frozen predictors, not uncertainty over repeated Phase-A refitting or an unobserved population of model families.

This conservative rule may make the server sample infeasible. Even with zero observed calibration error, it requires `n >= 200 log(2m/.025)` merely to allow a .10 bound; for m=7 this is about 1,266 independent source units. A small study cannot honestly promise that distribution-free certificate. Finite-population sampling or related-source designs require their own design-specific inference; do not call sources independent by filename alone.

For a more informative but approximate uncertainty assessment, predeclare a paired source-cluster bootstrap (e.g. 10,000 fixed-seed resamples), preserving each source's full vector of cells and both predictors. Report an interval for T rather than relying only on an unstable relative ratio. For simultaneous calibration, bootstrap the maximum absolute centered cell error across all m cells. Bootstrap intervals are approximate, can be degenerate for all-zero errors, and do not resolve unknown family shifts or missing-data bias. Do not replace a preregistered confidence gate with a bootstrap gate after seeing its width. A feasible small protocol may retain point criteria plus explicitly approximate uncertainty and call uncertain results inconclusive; it must not advertise the conservative certificate.

## 8. Invalidity, missingness and honest failure

Every scheduled marked attempt remains in the endpoint: failed/missing attempts count as C=false under the frozen intention-to-attempt convention. This outcome rule does not make missing predictor values zero. Missing C0, tangent, descriptor or baseline quality means a missing forecast. Retain the source in accounting; for the primary complete-grid H4 claim, any unresolved required forecast makes the claim not fully evaluable. Do not remove the source or impute a convenient forecast. An available-forecast analysis is secondary and must show its denominator.

A dataset where most attack attempts fail can also be easy to predict as C=false. Report execution-failure and successful-output strata descriptively, preserving the primary denominator, so infrastructure failure is not sold as a survival law.

H4 fails, or remains untested as appropriate, if: kappa cannot be estimated; the required tangent cannot be obtained without marked-output leakage; the frozen proxy mispredicts content binding; any cell misses .10; the aggregate misses 20%; the comparator is unavailable; or the family challenge cannot be executed under the frozen design. Insufficient precision is inconclusive support rather than a positive mechanism result. No extra family fit, learned residual library, confirmation recalibration, post-hoc cell omission or substitution of the continuous-margin endpoint rescues it.

The useful result even after failure is sharply bounded: report whether the vector transport forecast predicts continuous chips/margins, whether C0 semantic features approximate marked features, and exactly where compound majority C prediction breaks. Those are separate scientific findings, not a retrospective pass of H4.
