# Prospective training and calibration missingness rule

**Root decision during WP5, before any new experiment:** adopt sections 1–6 in 07-final-experiment.md and the named baseline/statistical contracts. Section 6 is the selected prospective amendment. Full numerical delivery remains a separate flag, and structurally unavailable paths cannot be rescued. The earlier strict complete-grid vetoes are superseded only as explicitly integrated in those final contracts.

Design recommendation, 2026-10-25. This is a bounded method-design note, not an independent review, executed fit or approval. MAIN STATE was read once. The inputs were `07-final-experiment.md`, `analysis/theory-design.md`, `analysis/quality-baseline-contract.md` and `analysis/confirmatory-statistics.md`. Nothing scientific was run. The parent supplied the historical count of six blocked F5 R0/R1 calls among 1,080; this note does not independently recompute that count. The new explicit-noise trajectories may have different failures.

## Decision

Replace the absolute complete-training-grid requirement with a **prospectively fixed, coverage-qualified observed-data fit**. Keep every planned training identity and its original weight in the ledger. Do not fill in missing chips, invent quality features, replace a source/seed, refit alternatives, or bypass safety. Keep the entire 30-source calibration denominator and assign an incomplete source's calibration score positive infinity. The radius is still exactly the 28th order statistic of 30 source scores.

Crucially, **an infinite q90 does not by itself invalidate the frozen point predictor or prevent testing H4**. The authoritative H4 is compound-C rate error <=.10 in every cell and >=20% family-balanced Brier improvement; it does not use q90 to form probabilities or decide C. An infinite radius makes the margin-interval diagnostic uninformative. It does not pass a useful margin-prediction claim, excuse missing Phase-B forecasts or relax either H4 criterion. Earlier proposed q90<=1/85%-coverage margin gates in the theory note are research history, not the current primary H4.

This change must be adopted before the new Phase-A outcomes and masks exist. Do not choose between strict and observed-data fitting after looking at their performance. If it is not adopted prospectively, keep the existing strict rule. No historical endpoint can be reclassified by this amendment.

## 1. Immutable attempts, admissibility and ordering

Attempt all 30 fit sources x six native cells x three seeds under the fixed retry policy; apply the same rule to the 30 calibration sources. A safety block is terminal for that request. Only already permitted transient infrastructure retries may repeat an identical request. A missing artifact is not permission to change precision, seeds, prompts, safety settings, cells or numerical path. Repairing a genuine implementation defect requires a documented prospective repair consistent with the parent protocol; it cannot be used to select favorable scientific outcomes.

Determine admissibility from completed artifacts, finite required quantities, valid provenance and execution status. Never exclude a finite pair because its error, leverage, decoded score, quality, class or effect on kappa is inconvenient. No robust trimming, winsorization, influence cutoff or residual-based deletion is added. Preserve the planned identity and reason for every unavailable observation. The availability mask can itself depend on image content and on the generated trajectory: this is an acknowledged selection mechanism, not an assumption of missing-at-random.

Freeze fit coefficients before examining calibration residuals. Freeze the final radius after all calibration attempts reach their permitted terminal status, regardless of whether it is finite. Phase B remains a separate user decision and uses the unchanged prediction-before-outcome release order.

## 2. Kappa: one observed-data scalar, with coverage qualification

For fit source i, cell c and seed s let A_ics=1 only if the paired C0 background b, full-chain tangent v, actual marked-output chip vector p1 and required identities are present and finite. Missing chips are missing measurements, **not zero chips**, even when the operational positive endpoint is zero. Keep one all-or-none mask per complete 320-chip vector; do not fit on a selected subset of chips.

Use w_ics=1/18 exactly as planned, and fit

`kappa = sum[A*w*<v,p1-b>] / sum[A*w*||v||^2]`.

The sums range over all 540 planned trajectory identities. An unavailable vector contributes no observed squared-error term; its missing objective weight is reported. Do not increase a surviving row's weight to make an incomplete source or cell sum to its nominal total. This is the minimizer of the available-data objective, not a recovery of the hypothetical complete-grid minimizer. Multiplying the whole unpenalized objective by one common constant would leave kappa unchanged, but no such rescaling is needed.

For primary qualification require **at least two available paired vectors in every one of the 180 source-cell triplets, and at least 81 of the 90 planned vectors in each of the six cells**. Thus every source/cell remains represented, every cell retains >=90% of its intended observations, and overall available weight is >=90% of the planned total. These are prospective coverage tolerances, not a theorem, a missingness correction or a power guarantee. The two-of-three requirement retains direct representation of each planned source-cell under the existing three-seed design; it is not an assertion that two seeds determine the third chip vector. The 90% floor deliberately limits the allowed departure from the intended fit and must not be reduced after outcomes.

Also require a finite strictly positive denominator and finite kappa. Publish denominator and per-source/cell contributions as diagnostics; an unusually small but positive denominator does not authorize a newly selected cutoff or shrinkage. Zero denominator means unidentifiable; nonfinite quantities mean numerical failure. Neither receives a replacement coefficient.

If coverage passes with any missing vectors, label the result `FIT_QUALIFIED_INCOMPLETE`, retaining the number and weight missing. A complete qualified fit is `FIT_COMPLETE`. Failure of coverage or identifiability is `FIT_UNAVAILABLE`; a descriptive available-data coefficient may be shown separately but cannot become the primary H4 predictor.

## 3. Quality comparator: preserve its strength and objective

The comparator uses the same fixed 30 training source IDs and six cells, but its admissibility mask is determined by its own required information. A marked-output safety block does not by itself invalidate this row: the operational all-attempt source-majority Y is still defined after all planned attempts have terminal statuses. In contrast, any missing/nonfinite C0 seed quality or input quality makes the row unavailable; do not use the median of only two C0 seeds, infer quality from a law measurement, or impute a probability.

Require **at least five of six feature-complete source-cell rows per source, and at least 27 of 30 feature-complete rows in every cell**. This preserves all 30 sources, represents every cell on >=90% of sources and retains >=90% of total planned comparator weight. These are fixed design tolerances, not evidence that selection bias is small. Do not impose the chip mask on comparator rows whose legitimate features are available; artificially discarding usable comparator training information could weaken it. Conversely do not discard usable chip pairs solely to equalize row counts. Publish both masks and their overlap.

Each available comparator row retains weight 1/6. Compute training means and variances using the available rows with these weights: a weighted mean necessarily divides its numerator by the sum of **available** weights. This ordinary definition of a weighted moment does not restore missing objective weight. Do not rescale the loss to 30 source-units or to an average loss. Optimize exactly `sum_available[(1/6)*binary_NLL] + .5*sum(beta_j^2)`, with the unchanged intercept, solver, zero-variance-feature rule and convergence criteria. With missing rows the fixed penalty is somewhat stronger relative to total observed loss; disclose that consequence rather than retune lambda.

Both target classes must occur in the observed training rows, and the existing finite/converged-fit conditions must pass. Identical targets, unavailable coverage or solver failure give `BASELINE_UNAVAILABLE`; do not cap the intercept, change the penalty or substitute a weaker sensitivity comparator. Record complete versus qualified-incomplete status just as for kappa. An unavailable primary baseline prevents primary H4 evaluation.

## 4. q90: keep 30 scores and the fixed rank

For calibration source i, if every one of its 18 native trajectory predictions and actual decoded margins is finite and available, compute

`R_i = max_(c,s) abs(M_actual_ics - M_hat_ics)`

in the unchanged native score units. If **any** required value is unavailable or nonfinite, set `R_i = +infinity`. Use no observed-only maximum for an incomplete source. Then sort all 30 extended-real scores, including infinities, and set `q90=R_(28)`.

There are three explicit statuses:

- `RADIUS_COMPLETE_FINITE`: all 30 source maxima observed; q90 finite.
- `RADIUS_CONSERVATIVE_FINITE`: 28 or 29 complete sources; incomplete-source scores are infinity; q90 finite.
- `RADIUS_UNINFORMATIVE_INFINITE`: at most 27 complete sources; q90 infinite.

With 28 complete sources q90 is the largest finite source maximum; with 29 it is the second largest; with 30 it is the third largest. Thus this is **not** recalibration on a reduced denominator and is not a more permissive quantile. Serialize infinity explicitly, for example `{"kind":"positive_infinity","value":null}`, rather than a nonstandard JSON numeric literal or a large finite stand-in. Publish all 30 statuses and scores.

Why this is conservative: whenever hypothetical complete finite residuals are meaningful, replacing any unknown source maximum by infinity can only increase the 28th order statistic. This is a deterministic order-statistic fact, requiring no missing-at-random assumption. When safety has prevented a legitimate output, its counterfactual physical margin need not be defined; the infinity score instead records failure to measure that source's entire finite grid. Do not interpret it as a measured infinite prediction error.

The name q90 retains its fixed rank meaning. Under a genuinely exchangeable same-distribution calibration/test-score model, the usual rank logic for 30 calibration scores at rank 28 concerns at least 28/31 marginal coverage, including any infinity mass. That logic supplies no family-shift guarantee and no coverage conditional on successful generation or on q90 being finite. These reused development sources are not a new exchangeable sample from the fresh POTD population, so **report this radius descriptively**, as the current protocol already requires. No conformal guarantee is claimed here.

An infinite interval has no useful width and must not be advertised as successful uncertainty prediction because all finite residuals fall inside it. Report its width as infinite, its informativeness as failed/uninformative and any mechanical finite-margin coverage only alongside that statement. Missing Phase-B margins remain missing; an infinite radius does not make them observed. A finite censored radius also does not prove that missing calibration sources would be ordinary or that their residuals are bounded by it.

## 5. Primary status and interpretation

If the scalar fit and primary comparator both qualify, their parameters can freeze and proceed to the separately approved Phase B, whether the radius is finite or infinite. Kappa and q90 remain the law's only two learned quantities; an extended-real order statistic adds no parameter, model choice or tuning degree of freedom. The comparator retains its separately declared seven coefficients and preprocessing constants. No additional classifier of safety failure is learned.

If either required fit is unavailable, mark H4 `UNEVALUATED_TRAINING_UNAVAILABLE`, retain its multiplicity slot at p=1, and continue reporting the other prespecified hypotheses as feasible. A radius alone cannot repair an unavailable scalar fit. Do not silently run a zero-kappa, prevalence-only or historical fit as the primary predictor. The other hypotheses need not be canceled merely because the proposed law failed to qualify.

The adopted Phase-B rules distinguish complete delivery from robust support: unavailable forecasts prevent a complete-delivery claim, while section 6 extends the worst-feasible-completion certificate to sporadic forecast abstentions as well as unresolved marked outcomes. Training missingness does not authorize available-case confirmation, source replacement or relaxed .10/20% criteria. A numerical H4 failure remains failure; an insufficient inferential certificate remains inconclusive.

The scientific limitation is substantive. Safety/technical availability may select easier images, channels or particular residual directions. OLS on observed chips can therefore estimate a different scalar from complete-grid OLS; the quality comparator may learn operational failures as negatives and has a different missingness mask. Coverage floors do not remove these biases. A subsequent complete, frozen fresh-source predictive test still honestly measures the resulting fixed procedures, conditional on their Phase-A training realization; it does not validate an unbiased physical transport coefficient, safety-invariant mechanism or universal law. Report the missing-fit qualification wherever interpreting kappa or model superiority.

## 6. Adopted prospective rule: sporadically unavailable Phase-B forecasts

**The parent adopted this amendment before any new Phase-A/B measurement.** The previous any-unavailable-forecast veto is honest if the claim is delivery of a complete numerical forecast grid. It is also brittle: if each of 1,400 source-cell forecasts independently had unavailability probability r, the probability of at least one failure would be `1-(1-r)^1400`. Independence and r are illustrative assumptions, not estimates from the historical six marked-output blocks. C0 safety and derivative failures could make a complete-grid certificate hard even with a useful partial predictor.

Recommendation: before execution, permit a **worst-completion H4 certificate for sporadic execution unavailability**, and retain a separate explicit complete-measurement flag. Do not encode abstention as probability zero or score it as a correct negative. The tradeoff is a changed claim about a partial procedure with bounded missing forecasts: it can support .10/20% robust to every missing-forecast completion, but it cannot establish that every planned numerical forecast was actually delivered or that missing derivatives were measured. If the authors require the latter full-delivery claim, keep the strict veto and accept the likely operational limitation.

An exact extension of the existing bounds is available without inventing a single prediction. For each source-cell define:

- `A_ic`: feasible law source-majority predictions from the available per-seed forecast bits, with each unavailable bit ranging independently over {0,1}. If two observed bits already agree, A is that singleton despite the missing third seed; otherwise A may be {0,1}. This does not claim the absent chip vector or margin exists.
- `Q_ic`: singleton {q_ic} when all frozen comparator inputs exist; otherwise [0,1]. Never replace its three-seed medians by available-seed medians.
- `S_ic`: the existing feasible marked-outcome-majority set, unchanged.

Freeze the forecast identities, available values and A/Q sets for the entire required grid before generating or releasing any Phase-B marked target outcome. Subsequent S sets come from the prescribed outcome-status ledger. Expand the existing statistics to:

`b_lo,c = mean_i[min A_ic - max S_ic]`;

`b_hi,c = mean_i[max A_ic - min S_ic]`;

`M_upper,ic = max_(a in A_ic,y in S_ic) 1[a!=y]`;

`t_lower,i = sum_c w_c * min_(a in A_ic,q in Q_ic,y in S_ic) [.8*(q-y)^2-(a-y)^2]`;

`B_Q,min = mean_i sum_c w_c * min_(q in Q_ic,y in S_ic) (q-y)^2`.

These are observed set bounds, not imputations. If Q=[0,1], its minimizing q for any binary y is y, giving zero comparator loss; the missing comparator is granted perfect prediction for this bound, so its failure never makes the law look better. If A={0,1}, the law can be wrong for either y, receiving worst-case loss one. Thus missing information is penalized against the claimed law advantage. The objective has no new fitted parameter, and the known range of t_lower stays [-1,.8].

For every possible completion a*,q*,Y* consistent with the observed values, the bias is inside [b_lo,b_hi], its mismatch is <=M_upper, and its paired loss advantage is >=t_lower. Apply **the same** robust point criteria, CP mismatch tails, empirical-Bernstein bound, IUT and 13-slot Holm rule to these expanded observed bounds. The .10 tolerance, .8 relative-risk factor, source/cell weights, n=200 and uncertainty assumptions stay unchanged. The deterministic proof is the same pointwise inequality already used for missing target outcomes. No missing-at-random assumption is introduced. The source-level observed bounds still need the existing iid/exchangeability assumption for population inference.

With a non-singleton A, M_upper is one, even if the observed target is negative; missing law majority therefore consumes the finite mismatch budget. At the first Holm threshold, ten such source-cells in one native cell already prevent the existing <=9/200 sufficient certificate, even with no other mismatch. A single missing seed need not consume this budget if the other two predicted bits agree; its margin/derivative completeness flag remains false. This is a principled consequence of majority identification, not completion of an absent measurement.

Where A or Q is not a singleton, conventional full-grid point losses and rate bias depending on that set are **not identified**; report their intervals/bounds, not one fabricated point estimate. Use the authoritative status `ROBUSTLY_SUPPORTED_WITH_ABSTENTIONS`, accompanied by missing-forecast counts and `forecast_measurement_grid_complete=false`. This status must not be printed as a complete-forecast-grid pass. If the bounds do not certify the claim, distinguish failed worst-case point criteria from inferentially inconclusive bounds and show the observed coverage. Complete cases alone cannot become the primary estimand.

**Systematically unsupported families remain a hard prerequisite failure.** The fixed six-source pilot must establish the required native adapter, derivative and comparator measurement paths for every required family before fit/freeze. A fundamentally unsupported JVP/adapter, a missing required model or a family-wide undefined feature is `UNEVALUATED_REQUIRED_PATH_UNAVAILABLE`, p4=1; it is not sporadic abstention to be hidden in pooled loss. If a required family becomes globally unavailable later, preserve that status and its planned weight. Sporadic request-specific safety/technical failures after a functioning frozen path qualifies may use the set certificate. Predeclare these structural versus request-level status reasons; do not classify them by whether their p-value would pass. Even without this structural guard, a family with no law forecasts gives M_upper=1 for every source and necessarily fails the per-cell certificate.

No route permits safety bypass, pre-filter black output, hidden marked-output finite differences or a completed-derivative claim for absent records. The proposed certificate addresses statistical robustness to absent values, not recovery of those values. Parent integration would need to revise the strict forecast prerequisite in statistics section 5 and the H4 status wording explicitly, keeping both the availability-aware certificate and the full-measurement flag visible.

## Parent integration checklist

Adopt this as one prospective amendment across protocol section 4, the baseline contract and statistics sections 1/4; remove their contradictory complete-grid vetoes. Preserve their Phase-B missingness rules. Distinguish finite-radius qualification from primary H4 eligibility in the Phase-A freeze receipt. Add tests later for 0/1/2/3 incomplete calibration sources, infinite serialization, exact original weights, coverage boundaries, terminal-status operational labels, distinct fit masks and unavailable-model p=1. No local implementation or rehearsal is requested by this note.
