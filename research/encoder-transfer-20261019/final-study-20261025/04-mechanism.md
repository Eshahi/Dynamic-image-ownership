# Mechanism dossier: readable transport, not encoder gain alone

Status: WP2 descriptive development analysis and prospective model design, 2026-10-25. No new images, model passes, metrics or experiments were run. The original **FAILS, ROUTE C** decision is unchanged. Hypotheses were committed as `5cc20912a7120544e5ec4ece3d4a04bc5b4c9921` before raw-journal inspection, but aggregate outcomes were already known; this is not a blind preregistration.

## What the evidence now supports

The striking result is not simply that a foreign encoder erases F5. Foreign autoencoder round trips retain semantic C on 55/60 sources, with strong continuous margins and strong source-rank preservation. Full foreign regeneration then loses most or all semantic C. A useful explanation must therefore describe the **entire readable response**, including encoding, noising, reverse dynamics, decoding, the original reader and content binding. The existing pipelines change several components together, so these data do not identify a causal effect of encoder training independence.

The saved results do permit a stronger distortion statement. On all 58 F5 sources with complete quality triples, SDXL .1 is less damaging than SD1.5 .2 in LPIPS, PSNR and SSIM, source by source. Yet 56 of those 58 retain C under SD1.5 .2 and lose it under SDXL .1. This is true using either the marked input or the original image as the quality reference. It contradicts a deterministic monotone account based only on those three recorded quality numbers on these sources. It does not establish a matched-quality causal comparison: the frozen caliper grid still contains only **two** F5 matched sources.

The proposed law is an untested, expensive scientific forecast with original-image and target-model access. It cannot yet be fitted: the journals lack the latent displacements, continuous chip vectors and target-trajectory tangents it requires. A family regression is not a substitute for those measurements.

## Evidence and reproducibility

The authoritative input is the retained stage2b union journal:

`W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/20261025-0128-encoder-transfer-stage2b/results/stage2b-full/rows.jsonl`.

Last row per ID yields 11,040 units from 39,896 lines: 11,017 final `ok`, 23 final safety blocks, 60 sources. The log contains 28,856 generated-state records and 11,017 generated-to-ok transitions; repeated journal states are not repeated experiments. The input SHA256 and complete extraction contract are in [journal-analysis.json](analysis/journal-analysis.json).

The isolated stdlib scripts [journal_analysis.py](analysis/journal_analysis.py), [quality_models.py](analysis/quality_models.py), [state_and_quality.py](analysis/state_and_quality.py) and [schedule_bounds.py](analysis/schedule_bounds.py) read existing JSON/JSONL or compute analytical bounds. They never import experiment code or scientific libraries. Saved attack quality is read, not recomputed. Complete-source medians require every scheduled seed value; missing continuous values are never set to zero. Positive majority is at least two of three planned seed attempts, with missing/blocked attempts counted as failures.

Two analysis implementation errors were caught and repaired before this report. [attempt-01/ERRORS.md](analysis/attempt-01/ERRORS.md) preserves the incorrect rinse seed join and caliper matching attempt. [quality-attempt-01/ERROR.md](analysis/quality-attempt-01/ERROR.md) preserves a diagnostic regression that used linear instead of scaled-linear beta coefficients. Corrected analyses retain the precommitted model forms. The original hypothesis shorthand “rinse 112/113/114” refers to second-pass internal RNG; journal identity uses base seeds 12/13/14.

## The operational reader, exactly enough to explain its failure

The source-text audit is [reader-contract.md](analysis/reader-contract.md). For F5/v5, `C = semantic.read AND semantic.content_match`; `S = semantic.found AND semantic.content_match`; `A = semantic.found OR instance.found`. A is **any carrier**, not an instance-only endpoint. In these journals read-without-found occurs zero times, consistent with the code. Exact semantic/instance words and tolerant content binding are different endpoints: F5 clean C is 60/60, exact semantic Q is 52/60 and exact instance H is 34/60. Do not relabel clean C as exact payload recovery.

The semantic reader forms 320 DCT-derived chip projections p. For a candidate sign word w,

`score(w,p) = (w^T p)/||p|| = sqrt(320) cos(angle(w,p))`.

Thus multiplying all projections by a positive constant leaves the score unchanged. Total latent energy or projection amplitude alone cannot explain detection. A change in alignment, competing background energy, decoded word or content binding can. The decoded branch maximizes segmentwise over candidate bits; its score is not the fixed original-word score. The selected persisted score switches branches, so the analysis stores decoded and recomputed scores/thresholds separately. The table below uses `(decoded_score - decoded_threshold)/decoded_threshold`. It is a useful continuous diagnostic, not a sufficient statistic for C.

The semantic target is 32 bits distributed over 320 chips. The fixed recomputed and decoded thresholds in these calls are approximately 4.9820 and 8.2593. These analytic thresholds do not establish an empirical natural-image false-positive rate of 1e-6. Their null assumptions and roster/word search correction must not be confused with observed negative-control coverage.

F5 is optimized through the SD1.5 posterior-mode encoder, with a signed per-chip hinge objective and bounded image perturbation. Its gradient selects directions useful to that reader, not necessarily the leading singular direction of the encoder. Final quantization, the fragile image tier and refinement alter the final stored residual; all mechanistic measurements must use that residual. This remains an image-domain encoder-directed writer, not the proposal's latent insertion method or lightweight extractor.

## Continuous results across all fifteen cells

All detection counts below have denominator 60. Semantic/instance margins are medians of complete-source medians; R0 F5 coverage is 59/58/58 at .1/.2/.4, otherwise 60. WAM/VINE values are native known-message presence, not content-binding C and not an equal-FPR comparison. Full arm/margin/coverage tables are in [journal-analysis.md](analysis/journal-analysis.md).

| Cell | F5 C | v5 C | WAM | VINE-R | F5 semantic margin | F5 instance margin | Interpretation and next falsifier |
|---|---:|---:|---:|---:|---:|---:|---|
| Clean | 60 | 60 | 60 | 60 | .8515 | 1.1349 | Optimizer creates a readable direction; measure final stored residual, not its target. |
| R0 .1 | 60 | 47 | 42 | 60 | .7544 | −.5984 | Semantic signal survives while fragile instance signal is lost. Full-chain direction matters. |
| R0 .2 | 57 | 27 | 18 | 60 | .6194 | −.6114 | Semantic rank remains strong; some binding/reading failures begin. |
| R0 .4 | 39 | 3 | 1 | 47 | .2457 | −.6087 | Carrier, decoding and binding losses coexist; a one-threshold explanation is incomplete. |
| R1 .1 | 0 | 50 | 48 | 60 | −.3231 | .1127 | Semantic collapse with substantial surviving instance signal; not universal image destruction. |
| R1 .2 | 0 | 12 | 2 | 60 | −.4708 | −.1378 | C floor hides further margin loss; measure response instead of counting another zero. |
| R1 .4 | 0 | 0 | 0 | 45 | −.5321 | −.3747 | VINE remains a positive comparator, with different clean quality and a known negative-gate failure. |
| R1 rinse .1→.1 | 0 | 4 | 21 | 59 | −.5117 | −.0579 | Extra reconstruction reduces margins; no independent-pass retention product is justified. |
| R1 smooth .2 | 0 | 4 | 0 | 60 | −.5016 | −.2171 | Compare with mode; C floor cannot establish an F5 semantic benefit. |
| R1 mode .2 | 0 | 6 | 2 | 60 | −.4773 | −.1219 | Matched smoothing control; sampled R1 also differs in precision/RNG consumption. |
| R3 .2 | 5 | 57 | 44 | 60 | −.2741 | −.2967 | Native MoVQ/cosine-DDPM path differs from both SD chains. |
| D1 SDXL round trip | 55 | 60 | 60 | 60 | .5685 | .6256 | Foreign codec alone does not explain full SDXL failure. |
| D3 MoVQ round trip | 55 | 60 | 60 | 60 | .6372 | .6993 | Same challenge to an encoder-only account; runtime quantization/precision must be matched prospectively. |
| X1 resize once | 60 | 60 | 60 | 60 | .7621 | 1.1165 | Resizing alone is insufficient to explain the regeneration contrast. |
| X2 resize twice | 60 | 60 | 60 | 60 | .6894 | 1.1111 | Some continuous attenuation without C failure; no universal monotonic rule follows. |

The standalone [source-detection.svg](figures/source-detection.svg) displays the same counts. The arms have unequal clean quality: strict clean quality passes on 60/60 F5 and 31/60 VINE-R in the retained report. The figure is therefore a response map, not a method ranking.

### Failure-state decomposition

At F5 R0 .4, 178 completed calls comprise 117 C successes, 26 found-but-not-read, 25 read-with-content-mismatch and 10 not-found. Two more scheduled calls are blocked. Source-majority carrier A remains 58/60 while C is 39/60. This directly supports M4 as one observed pathway, without identifying causal mediation.

At F5 R1 .1, all 180 calls complete: 154 not-found, 23 found-but-not-read and three read-with-content-mismatch, with zero C successes. Source-majority semantic found is 7/60 and semantic read 1/60, while instance found is 52/60. At R1 .2/.4 all 180 semantic calls are not-found, but instance found remains 30/60 and 5/60 respectively. The two tiers fail differently, so A must not be substituted for semantic C.

At D1 and D3 the five failed C sources are found-but-not-read; semantic found and tolerant semantic S are 60/60. The retained codec signal is therefore more than a binary accident, but the full-vector measurements needed to explain its subsequent loss remain absent.

Rinse sends all 26 non-absent F5 semantic calls from first-pass R1 .1 to not-found. For v5, 140 first-pass C successes become 15 successes, 54 found-but-not-read, 69 not-found and two read-with-content-mismatch. WAM goes from 144 present calls to 58, VINE-R from 180 to 176. These paired transitions, kept in [state-and-quality.json](analysis/state-and-quality.json), are descriptive repeated-seed observations; their denominator is not 180 independent sources.

### Dependence, margins and source uncertainty

F5 clean-to-regenerated semantic-margin Pearson correlations are .993/.983/.937 for R0 .1/.2/.4, with 59/58/58 complete sources. They are .520/.176/.054 for R1, .973 for D1 and .982 for D3 (60 each). Corresponding Spearman correlations are .994/.988/.972, .550/.194/.066, .981 and .981. The original source ordering survives the codecs and same-family chain far better than full SDXL. This is consistent with a changed downstream readable response; it is not a measured Jacobian or proof of cause.

The pooled R0/R1 correlation between semantic margin and LPIPS is only −.049 (355 source-cell summaries), while within R0 .4 it is −.550 (58 sources). Pooling families can hide their distinct response geometry. No test treats the 355 rows as independent images.

At R0 .4, F5 seed-specific C counts are 35/60, 46/60 and 36/60. The median within-source normalized-margin range rises from .021 at R0 .1 to .087 at .4. Three seed repetitions are informative about sensitivity, not a tripling of sample size. Across models, equal integer seeds do not mean equal noise tensors.

The paired F5 C difference R1 .1 minus R0 .2 is −.950, with descriptive 95% source-bootstrap interval [−1.000, −.883]. The complete-source mean normalized-margin difference is −.913 [−.966, −.852], n=58. Rinse minus first pass changes F5 margin by −.167 [−.185, −.147], n=60, despite C being zero in both. Smooth minus mode changes it by −.0281 [−.0368, −.0191], while source-majority any-carrier A falls 32→16. These intervals resample sources 1,000 times with seed20261025; they describe this reused development population and do not confer confirmatory status.

### Quality-only explanations and their limits

Five source-disjoint folds use the precommitted SHA256 assignment. Training-fold scaling and a fixed L2 penalty avoid validation-chosen preprocessing. D1 uses LPIPS, D2 uses LPIPS/PSNR/SSIM with monotone quality signs, and D3 adds family and actual log schedule SNR. The implemented D3 also relaxes quality signs; therefore it is an augmented-and-relaxed diagnostic, not a pure test of adding family alone. A separately labelled D3M sensitivity retains the monotone quality signs.

| Arm | Intercept CV Brier | LPIPS CV Brier | Three-quality CV Brier | D3 augmented/relaxed CV Brier |
|---|---:|---:|---:|---:|
| F5 | .2459 | .2459 | .2459 | .0433 |
| v5 | .2373 | .1850 | .1876 | .1326 |

F5's quality coefficients collapse to the constraint boundary under pooled-family inversion. D3−D2 Brier is −.2026 [−.2151, −.1889] for F5 and −.0550 [−.0741, −.0382] for v5 under a paired source bootstrap. All 64 declared original fits converge. This limits these finite logistic forms, not all possible distortion functionals. D3 evaluates new sources within already fitted families; it is not out-of-family prediction and its family label is not a mechanism. See [quality-model-report.md](analysis/quality-model-report.md) and the separate sensitivity files.

The post-hoc [D3M sensitivity](analysis/quality-monotone-sensitivity.md) gives CV Brier .04319 for F5 and .13409 for v5 while retaining the quality signs; all 16 additional fits converge with no sign violations. The gain therefore largely remains without relaxing quality monotonicity. The sensitivity addresses that implementation ambiguity; it does not upgrade reused-data fit into causal or confirmatory evidence.

The realized marked-output quality in these regressions is available only after regeneration. It is a valid explanatory covariate here, but cannot silently become a pre-output benchmark for a future transfer forecast. WP5 must freeze a quality-only comparator computed from the same permissible C0 trajectory as the law, plus stronger separately reported diagnostic comparators. The prospective comparator's exact feature set and regularization must be frozen before Phase A rather than selected for ease of beating it.

The frozen same-LPIPS-bin calipers require absolute differences ≤.02 LPIPS, ≤1 dB PSNR and ≤.02 SSIM, then choose minimum squared normalized distance with fixed ties. Matched unique sources are F5=2, v5=0, WAM=1 and VINE-R=3 across bins; bins must not be pooled into a fictitious larger matched sample. A successful within-source quality-dominance analysis and a nearly empty equal-distortion analysis answer different questions.

WAM bit accuracy is missing when its native mask/presence path supplies no bit estimate. At R1 .2 only three sources have all three seed accuracies, versus 54 at .1. The rising conditional median cannot be interpreted as recovery. VINE-R provides all 60 source medians at R1: .98/.90/.73 for .1/.2/.4; its native threshold and known-message advantage remain explicit.

## A conditional derivation with measurable terms

The full derivation, assumptions, reader mapping and fifteen-cell predictions are in [theory-design.md](analysis/theory-design.md). Let x be the clean original, x+δ the final stored mark, and let E_c include native preprocessing, scaling and posterior convention. With a shared explicit posterior noise tensor η,

`d_c = E_c(x+δ;η) - E_c(x;η)`.

For a variance-preserving noising step, `z_t = a_c z_0 + b_c ε`. Shared explicit ε cancels in the paired latent difference, but remains in the background trajectory and downstream response. Let F_c be the complete native reverse path, V_c its decoder and R_0 the original reader encoder/chip transform. Along the **unmarked** trajectory,

`p_mark = p_C0 + v_c + remainder`,

`v_c = J_(R_0) J_(V_c) J_(F_c) a_c d_c`.

This is a local approximation to a floating computation path. The literal RGB8 derivative is zero almost everywhere; output rounding, clipping, finite displacements, precision casts and posterior differences contribute approximation error. One must measure that error rather than claim an exact derivative of the complete discrete pipeline.

A useful factorization of a fixed signed read increment is

`a ||δ|| × encoder directional gain × downstream gain × signed alignment`.

The first factor alone is not a detector SNR. High norm can accompany negative alignment or a large off-pattern denominator. The conditional Gaussian input-channel ratio `a²||d||²/b²` also differs from the dimension-normalized latent energy ratio `a²||d||²/(b² d_latent)`. Neither by itself determines the nonlinear decoded word and content state.

For equal-covariance Gaussian location shifts only, the optimal level-α detector has TPR `Phi(mu - Phi^-1(1-α))`, where μ is Mahalanobis displacement. A downstream detector cannot improve this bound without additional information under those assumptions. At α=1e-6, 90% TPR requires μ≥6.035; this is an analytical conditional requirement, not a measured F5 quantity. Sampled posteriors can change covariance, public content-dependent marks violate generic random-secret-code assumptions, and a fixed clean-source conditional comparison is not automatically the operational natural-image null. The [Zhao paper card](literature/attacks/zhao-provable.md) records the theorem's actual scope.

For the pinned scaled-linear SD schedule, strengths .1/.2/.4 execute 2/4/8 updates starting at timesteps51/151/351. The analytical a/b ratios are 4.383/2.182/1.010. Native Kandinsky3 .2 has cosine-schedule a/b≈3.932. Thus nominal .2 does not even match the forward-noise ratio across these chains. It still cannot rank readability, because d_c, scaling, posterior covariance and reverse response differ. Values and precision limits are in [schedule-bounds.md](analysis/schedule-bounds.md), derived from pinned [DDIM source](https://raw.githubusercontent.com/huggingface/diffusers/v0.35.1/src/diffusers/schedulers/scheduling_ddim.py), [DDPM source](https://raw.githubusercontent.com/huggingface/diffusers/v0.35.1/src/diffusers/schedulers/scheduling_ddpm.py) and [img2img timestep slicing](https://raw.githubusercontent.com/huggingface/diffusers/v0.35.1/src/diffusers/pipelines/stable_diffusion/pipeline_stable_diffusion_img2img.py).

For deterministic DDIM, each reverse-step Jacobian contains a multiple of the identity plus a coefficient times the denoiser Jacobian; their ordered product may rotate, amplify or suppress the mark. Eta0 does not remove posterior sampling or initial noise. This follows the [DDIM update](https://arxiv.org/html/2010.02502v4), not an assumption that every denoiser contracts every direction. Likewise antithetic averaging can reduce average directional variation but Jensen's inequality does not say its norm is below the unsmoothed center's response. Both claims require measurement.

## The small law and the information boundary

The primary candidate is `p_hat = p_C0 + κ v`, with one pooled scalar κ fitted on 30 designated development sources. A second global quantity q90 is the 28th order statistic of 30 separate sourcewise maximum absolute decoded-score errors over the frozen calibration grid. It is a margin radius, not a noise standard deviation or a probability model. No family intercept, learned covariance or confirmation residual library is hidden inside these two quantities.

Use predicted chips plus the unmarked target output's seven-view semantic descriptor as a declared proxy, then apply the unchanged reader and binding code. The forecasted source endpoint is the majority of the three predicted binary C values. Score it as deterministic 0/1 Brier loss; do not invent an independent-seed majority probability. The [prediction contract](analysis/prediction-contract.md) gives a simple counterexample showing that identical seed marginals can have different majority probabilities.

Allowed prediction information is substantial: the original source, marked input, target model internals, explicit paired noise, C0 output/background and derivatives evaluated along C0. It is not lightweight extraction or an attacker's detector-free knowledge. Forbidden predictors are the target marked output's pixels, chip vector, score, word, descriptor, derivative or quality. A marked-output finite difference would evaluate the very result being forecast and is not an acceptable shortcut. Freeze all predictions before releasing marked target outcomes.

The prospective C criterion from 03 remains unchanged: ≤.10 absolute source-majority rate error in **every** validation cell and ≥20% aggregate Brier improvement over a frozen permissible quality-only comparator, with source uncertainty. Include high- and low-retention cells and a family excluded from fitting/calibration. A margin fit, an interval that contains everything, a family-label fit or a floor-only predictor cannot replace this requirement. q90 coverage and continuous-margin improvement are companion diagnostics. If the proxy predicts margins but fails C, report that precise failure.

Theoretical distribution-free simultaneous rate-error bounds are expensive: a simple Hoeffding construction can need over 1,200 sources for seven cells even at zero observed bias. That is a conservative sufficient requirement, not a lower bound on all inference methods. WP5 must choose feasible source-level inference before outcomes, distinguish point success from statistically supported success, and retain inconclusive outcomes. Approximate bootstrap intervals alone must not be sold as exact certification.

## Minimal server measurements that distinguish the hypotheses

Preserve the frozen writer and reader. For selected development sources, obtain exact final residuals; native mode and sampled encoder displacements; signal norm, noise scale and signed reader response; C0/C1 chip vectors and all branch scores; actual timestep coefficients; and the full-chain tangent along C0. Use explicit common random tensors for the clean/marked pair, not merely identical seed integers. A single JVP can propagate the 320-dimensional output direction; 320 separate passes are unnecessary, but its runtime and support are unmeasured and must be budgeted on the server.

Matched stage controls are: preprocessing only, mode codec round trip, sampled codec round trip, mode-plus-noise direct decode, and the same mode-plus-noise-plus-native-reverse path. Directly decoding a noisy latent can be out of distribution and is a mechanism diagnostic, not a fair attack. Match precision and decode options where the comparison is intended to isolate the reverse path. Native pipelines remain the external-validity attacks. Blindly swapping a foreign encoder into an incompatible denoiser would introduce another confound.

Norm-matched random and spectrum-matched residual directions can test whether F5 occupies unusually readable directions. These are bounded scientific controls, not new writer variants or claimed practical watermarks. Do not tune F5 against the new family. Predeclare the controls and random seeds in Phase A and keep the family challenge excluded from law fitting.

The decisive falsifiers are: encoder norm fails to predict signed transport; the tangent remainder is too large; content-proxy error dominates; the global κ fails on a new family; or the C forecast loses to the frozen quality comparator. Any of these produces a useful negative mechanism result without rescuing the old transfer verdict.

## Negative controls and claim ceiling

F5 has no observed A event in the tested C0/wrong-owner calls. The R1 primary scope has 540 calls per negative kind, but only 60 independent source clusters. Zero source-any events gives a one-sided 95% upper bound of **4.8703%**, conditional on independent source sampling. It does not establish a 1e-6 operational FPR. Missing negative calls leave the corresponding gate unresolved; the 23 safety blocks are retained in coverage.

VINE-R has one unmarked R1 .1 detection, source1295 seed14, exactly at its 69/100 threshold. Its zero-event gate fails. Its excellent positive retention remains a measured positive-control result with this qualification and unmatched clean quality. No threshold is changed after observing the tie.

The evidence supports pipeline-specific semantic retention failure, stage-resolved descriptive response, rejection of specified monotone quality-only explanations, and a falsifiable proposal for a richer forecast. It does not yet support a general encoder-transfer law, an independent-encoder causal theorem, a universal attack, ownership authenticity, T4/T5 robustness, a Q1-readiness claim or confirmation on fresh data.
