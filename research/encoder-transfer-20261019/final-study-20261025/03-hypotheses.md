# Hypotheses and model forms before journal reanalysis

WP2 opened at 2026-10-25T05:35:54.8132878-08:00 (13:35:54 UTC). This file is committed **before root or the WP2 contributors open/aggregate the saved journals**. Aggregate findings in the study reports and MAIN STATE are already known. Therefore the hypotheses and all analyses below are **post-hoc, descriptive development analyses**, not blinded preregistration. The future server confirmation will be prospectively frozen separately.

## Mechanisms and falsifiers

| ID | Candidate explanation | Prediction | What would contradict or limit it |
|---|---|---|---|
| M1 | Writer-encoder gain alone determines survival | F5 has larger normalized residual gain in SD1.5 than foreign encoders; low foreign gain predicts loss | High foreign gain with loss, low gain with retention, or retained foreign round-trip C despite full-pipeline loss rejects sufficiency. Existing round-trip counts already challenge a simple version. |
| M2 | Signed readable transport, not total latent energy, controls the continuous carrier | The complete local encoder–noise–denoiser–decoder–reader directional response predicts signed margin better than latent norm alone | Energy preserved but signed response lost supports this distinction; no out-of-source/family predictive improvement rejects the proposed law. A measured marked-output score is an outcome, never an allowed predictor of itself. |
| M3 | Nominal strength masks actual noise differences | Within one fixed pipeline higher injected noise generally weakens readable signal; actual alpha/sigma explains more than strength alone | Nonmonotone denoiser transport is possible; an alpha-only model failing at equal schedule is evidence against sufficiency, not against the correct schedule calculation. |
| M4 | Final C loss is partly content-binding or decoding failure | Some calls retain a carrier/read but fail content match; semantic and instance tiers can diverge | If every failed C call is unequivocally carrier absent with no alternative state, this pathway has no observed support. Persisted C is read AND content_match and does not require found. |
| M5 | Pixel distortion alone explains the pipeline contrast | A monotone quality-only model predicts outcomes as well as added family/schedule diagnostics | Better predictive fit after family/schedule, or consistent within-source quality dominance with opposite C, limits the declared quality-only models. It does not disprove every possible distortion functional. |
| M6 | Repeated reconstruction compounds a single-stage effect | Two-pass outputs lose more signed margin than first-pass outputs at the cost of additional distortion | No extra loss, recovery, or gain reversal contradicts a simple monotone/product account. Do not assume independent passes or multiply retention rates. |
| M7 | Smoothing suppresses locally unstable encoder directions | Matched R1-smooth versus R1-mode changes continuous margins/tier states even when C is at floor | An unchanged response or increased retention falsifies the directional prediction for that arm; sampled R1 versus mode is a compound precision/posterior contrast. |

## Conditional transport model family

Let x be an unmarked image, x+delta the frozen marked image, E_j the scaled encoder representation, D_j the decoder, and F_jt the native reverse trajectory. Use the actual pipeline preprocessing P_j, latent scaling and posterior convention. The first-order mark is d_j = J_(E_j P_j)(x) delta. A deterministic linearization is a conditional approximation, not a theorem about the quantized/clipped writer.

For a variance-preserving corruption, z_t = a_t z_0 + s_t epsilon, with a_t=sqrt(alpha_bar_t), s_t=sqrt(1-alpha_bar_t). The latent norm ratio is rho_E = a_t^2 ||d_j||^2 / (s_t^2 d_latent), where the denominator is total isotropic injected-noise energy. Also report the directional ratio a_t^2 ||d_j||^2/s_t^2 for a unit direction aligned with d_j. They answer different questions and neither is detector SNR. A flow schedule requires its actual affine coefficients and scaling, not an invented alpha_bar.

For a fixed semantic query/readout score r, the local readable increment is approximately a_t * grad(r)^T J_D J_F d_j. The background score displacement and propagated-noise variance must also be included. Norms cannot recover the sign or orientation. A content-derived query can change after regeneration, invalidating the fixed-query approximation; evaluate fixed-query diagnostic margins separately from the unchanged operational reader.

The primary small law predicts the **continuous 320-chip vector**, not an invented scalar sufficient statistic. For a known clean source and its frozen marked INPUT, measure the exact attack-encoder displacement. Along the corresponding UNMARKED target trajectory, propagate that displacement through a floating-path tangent of denoiser, decoder and fixed reader. Predicted chips equal the C0 chip background plus one global calibrated transport-gain coefficient times this tangent, with one global residual-scale coefficient for uncertainty. These are at most two fitted coefficients and no family intercepts. This requires original-source/control-trajectory/target-model derivative access as explicit privileged scientific measurement information; it is not a cheap operational detector or a blind forecast from the model name. RGB8, casts and clipping make literal end-to-end derivatives discontinuous; the floating-path approximation and its error must be tested.

For compound C, the UNMARKED target output's semantic descriptor may be used as a predeclared proxy for the unknown marked target descriptor, with the unchanged reader rules applied to predicted chips. This approximation must be reported and tested separately. **No target marked-output score, decoded word, semantic descriptor or derivative evaluated at that output may enter its own prediction.** Finite differences that generate the target marked output and call its reader are forbidden prediction features. If exact C is not predictable from these allowed quantities, that is a failed C prediction; a useful fixed-query margin prediction is a separately labelled result, not a replacement H4 endpoint.

An explicitly secondary scalar surrogate may use a standardized signed transport predictor Z and semantic-content drift Q: sigmoid(beta0 + beta1 Z - beta2 Q), beta1,beta2>=0, no more than three global coefficients. Q must come from an unmarked control or Phase-A-frozen measurement, not marked target outputs. This surrogate cannot replace the vector law after seeing confirmation. Norm-only SNR is a reduced explanatory comparator, not a sufficient survival law.

The derivation contributor may sharpen observable definitions before Phase A. Every refinement must be labelled as a design refinement; numerical forms fitted to existing journals remain exactly those below. Missing mechanistic quantities will **not** be imputed from a family label or inferred from a binary endpoint. No genuine transfer-law fit is possible unless the saved outputs contain the necessary observables, which is not currently expected.

## Predictions for all fifteen existing cells

The qualitative ordering below was selected knowing aggregate development counts. It is a falsifiable explanation to test with new measurements, not an independent prediction of those counts.

| Cell | Pre-analysis mechanism prediction and silence |
|---|---|
| Clean | Positive semantic margin and consistent content are expected from the optimizer; measured final quantization/auxiliary tier can violate the target. |
| R0 .1 | High retention if the writer-selected directions retain signed response under the native denoiser; gain alone is insufficient. |
| R0 .2 | Less latent signal/noise than .1; continuous margins should weaken on average, not necessarily for every source/seed. |
| R0 .4 | Further reduction is expected conditionally on comparable denoiser transport; semantic drift/abstention may add failures. |
| R1 .1 | Encoder-only loss is not predicted from the round-trip counts; an additional reverse-trajectory/readout/background effect is required to explain the known floor. |
| R1 .2 | Lower a/s than .1, but C at floor cannot identify an additional mechanism; use continuous margins and states. |
| R1 .4 | Same floor limitation; quality and raw margins remain informative. No claim of a stronger causal encoder effect. |
| R1-rinse | Expected extra margin loss for arms with first-pass signal; F5 C floor is uninformative. No independent-pass product law. |
| R1-smooth | Relative to mode, expect attenuation of unstable local directions; sign and arm ranking remain testable, not guaranteed. |
| R1-mode | Cleaner posterior convention; difference from sampled R1 cannot alone identify posterior sampling because precision/RNG paths also differ. |
| R3 .2 | Native cosine schedule and MoVQ/denoiser/readout chain differ; a/s alone need not rank it against R0 or R1. |
| D1 | No diffusion noise; foreign codec may retain enough signed signal despite a changed residual. This is the key counterexample to encoder-gain sufficiency. |
| D3 | Same logic for MoVQ; architecture difference does not imply unreadability. |
| X1 | One resize cycle tests preprocessing attenuation; should not mimic a learned denoising effect if signed margin remains. |
| X2 | Two resize cycles test compounded resampling; no exact monotonicity claim under clipping/quantization. |

## Fixed descriptive analysis contract

**Inputs.** Only MAIN stage2a and union stage2b `rows.jsonl` and their declared study documents. The union is authoritative for the final state: last row per id wins; retain counts of overwritten states and status transitions. No image folders, embeddings, model passes or scientific packages. Never modify retained outputs. All scripts and new output files stay under this final-study directory.

**Units.** Source is the independent sampling unit. The three seeds are repeated observations. For positive C use the frozen majority >=2/3, counting failed/missing scheduled attempts as failures. Deterministic clean/D/X controls have one scheduled output. For continuous source summaries report the finite median only when all scheduled seed values exist, plus a separately labelled available-value sensitivity and coverage. Do not turn a missing score into zero. Preserve read-without-found and malformed-raw categories.

**Margins.** Extract semantic/instance score and their corresponding persisted thresholds. Report raw score-minus-threshold and normalized margin (score-threshold)/max(abs(threshold),1e-12), only where score and threshold are numeric and semantically matched. Decoded fields, bit errors and other readout criteria are separate. Carrier-state transition tables compare clean to each cell and R1 .1 to rinse; final C remains the persisted endpoint. If fields do not mean a common score/threshold pair, document that and withhold the invalid normalization.

**Correlations.** Pearson and rank-Spearman of source median margins across cells; within each family/strength and pooled across families, relate margin to LPIPS, PSNR and SSIM. Show coverage and constant-response cases. The cross-family pooled correlation is explicitly ecological/confounded. Separate seeds 12/13/14 (rinse 112/113/114), report paired source distributions and within-source seed spread, not 180 independent-image tests. Seed effects are descriptive, with no claim that seed labels correspond to common latent noise across models.

**Baselines.** Report WAM and VINE-R bit accuracy continuously, their native threshold-relative distance, and source-majority detection. Do not convert them into content-binding C or compare their probability to F5's under a common nominal random-bit null. Preserve the observed VINE negative and its exact threshold tie.

**Quality-only model comparison.** Use individual completed R0/R1 seed calls with paired recorded attack-to-mark quality, source weights ensuring each source-cell totals one. Failed outputs stay in the main endpoint tables but are not given invented quality. Fit four nested diagnostic logistic regressions separately for F5 and v5 operational C: D0 intercept; D1 intercept plus LPIPS; D2 LPIPS, PSNR, SSIM; D3 D2 plus family indicator and log(alpha_bar/(1-alpha_bar)). D1/D2 have physically monotone coefficient constraints (LPIPS nonpositive, PSNR/SSIM nonnegative). D3 permits unconstrained family/schedule effects. Standardize using training-fold moments only; use fixed L2 penalty 1 on standardized nonintercept coefficients. Numerical optimizer tolerance and maximum iterations are recorded, not tuned for a preferred result. If separation or convergence fails, report it and use a declared stable regularized fit; retain failed fits.

Use five source-disjoint folds given by SHA256('et-final-wp2-v1/'+source_id) modulo 5. Evaluate Brier score, log loss (probabilities clipped only for numerical reporting at 1e-8), and per-cell calibration on held-out source folds. This is in-family prediction on a reused development population, not confirmation or out-of-family prediction. Also report leave-one-strength-out diagnostics where trainable; no broad extrapolation claim. Compare quality-only models only within observed support and report the frozen caliper overlap count. Any arbitrary nonlinear distortion-only model remains outside this finite comparison.

**Uncertainty.** Descriptive 95% source-cluster bootstrap intervals (1,000 draws, seed20261025) may be used for selected paired differences; record the exact endpoints. No uncorrected hypothesis-test claims will be made from this package. Negative rates use source-any-event counts with exact one-sided binomial upper bounds, conditional on independent source sampling. Any missing negative call makes the zero-event gate unresolved. Correlated channel/seed calls are not extra independent negative images.

## Prospective prediction criterion carried to WP5

The future H4 must require calibration and useful error reduction on untouched sources, separately for a held-out family if available. Planned thresholds: absolute source-majority rate error <=0.10 in each designated validation cell; at least 20% lower aggregate Brier error than the frozen quality-only comparator, with a source-level uncertainty assessment; and no refit or threshold change after confirmation begins. A floor-only constant predictor must not pass by dominating the cell weights. Include both high-retention and low-retention cells, plus the independent family challenge. WP5 will make the inferential decision rule, multiplicity, minimum sample and fallback conditions exact; these thresholds cannot be relaxed because development fitting is inconvenient.

No parameter estimate, carrier-state count, correlation, scheduler value or new journal-derived number has been computed before this file's first commit.
