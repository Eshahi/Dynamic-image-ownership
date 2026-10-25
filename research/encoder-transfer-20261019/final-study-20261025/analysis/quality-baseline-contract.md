# Prospective pre-output quality comparator

WP5 design refinement, fixed before Phase A and any fresh-source outcome. This replaces the provisional one-/three-feature suggestions in earlier design notes. It does not alter the two-quantity vector law or H4's <=.10 per-cell rate-error and >=20% aggregate Brier-improvement criteria. No model described here has been fitted locally.

## Why a stronger comparator is needed

Realized target marked-output quality is unavailable at prediction time. Substituting it would leak the future output into a purported forecast. Conversely, requiring only a monotone response to one C0 quality measure could make the comparator unnecessarily weak. The primary comparator therefore sees six permissible quality measurements and has unconstrained coefficient signs. It may learn counterintuitive correlations from development data; the mechanism law must beat that fixed comparator, not only a physically monotone straw man.

## Inputs and target

For each source i and native cell c, the target Y_ic is the actual F5 operational source-majority C (>=2/3 scheduled seeds). Use all scheduled attempts, with missing/blocked positives handled as the study contract prescribes; missingness is additionally audited and bounded in confirmatory claims.

The six predictors are:

1. Median over the three scheduled seeds of LPIPS(C0_target_output, original x).
2. The analogous PSNR median.
3. The analogous SSIM median.
4. LPIPS(frozen marked INPUT u, original x).
5. PSNR(u,x).
6. SSIM(u,x).

Only items 1–3 vary by native channel for a given source. All values must be finite. C0 and clean-input quality are permitted information before the marked target trajectory exists; the original source is explicit privileged scientific side information. No target marked-output pixel, quality, chip, score, word, descriptor or derivative enters a feature. Do not add a model-family label, strength, scheduler index, source ID, filename or timestamp. Compute features from the same declared quality implementation/references throughout.

A missing C0 seed quality or missing input quality makes that source-cell forecast **unavailable**. Do not impute a zero-quality or zero-probability prediction. Full numerical delivery is then incomplete. Under the prospective WP5 availability amendment, the [statistical contract](confirmatory-statistics.md) may still certify risk conservatively using Q=[0,1], which grants the missing comparator its best possible value in each loss comparison. Report the distinct robust-completion status and missing-forecast flag; never print an imputed full-grid Brier point estimate.

## Fit and freeze

Use only the 30 designated Phase-A fitting sources and six native R0/R1 cells (.1/.2/.4 in each family). Exclude the 30 calibration sources, Kandinsky and optional FLUX from fitting. Each planned fitting source has total objective weight one: each of its six cells has weight 1/6. Apply the fixed [training-missingness rule](training-missingness-design.md): at least five feature-complete cells per source and at least 27 feature-complete sources in every cell. Unavailable rows retain their missing weight in the ledger; do not redistribute it. A marked-target block alone does not remove a row because the operational all-attempt majority target is still defined. Do not impose the law's chip-availability mask on valid comparator rows. Label a qualifying incomplete fit explicitly; insufficient coverage makes the primary baseline unavailable.

Standardize each feature using admissible training rows and their original weights only. Weighted moments divide by the sum of available weights, while the loss weights remain unrescaled. A zero training variance fixes that feature's standardized value and coefficient to zero; retain the intercept and remaining columns. Fit

`q_ic = sigmoid(beta0 + sum_(j=1..6) beta_j standardized_feature_j)`

by minimizing weighted binary negative log likelihood over available rows plus `0.5 * sum(beta_j^2)`. The intercept is unpenalized and coefficient signs are unrestricted. Thus the fixed L2 coefficient is one under the **summed source-weighted** objective, not an undocumented mean-loss convention. Missing rows make this penalty somewhat stronger relative to the observed loss; disclose that rather than retune it. No cross-validation tuning, feature selection or alternative penalty is selected. Use deterministic convex optimization to a declared convergence tolerance (gradient infinity norm <=1e-8, at most200 Newton iterations with backtracking); preserve failed fits. Both target classes must occur. An all-identical-target training set is degenerate and cannot qualify H4; report inability to fit a useful comparator rather than hide separation in an arbitrary intercept cap.

Archive coefficients, training means/scales, row/source weights, objective, convergence diagnostics, training source IDs and implementation version. Freeze before calibration diagnostics or held-out target outcomes can change any choice. The 30 calibration sources are reserved for the law's q90, not a second chance to tune the quality model.

## Scoring and interpretation

The law predicts a deterministic source-majority bit and therefore has 0/1 Brier loss. The quality model predicts q in [0,1] and receives its ordinary squared-error Brier loss. For each source, use fixed **family-balanced** validation weights: in the seven-cell core, each R0/R1 cell has weight 1/9 and the single Kandinsky cell has weight 1/3; with the preapproved eighth FLUX cell, each R0/R1 cell has weight 1/12 and each Kandinsky/FLUX cell has weight 1/4. Thus every native family receives equal total weight, irrespective of its number of strengths. Freeze the seven- versus eight-cell set before Phase B; missing cells cannot be dropped or reweighted. These validation weights do not change the fitting weights of 1/6 across the six R0/R1 training cells. H4 compares `L_law - .8 L_quality`; negative expectation is the required 20% relative improvement. If the quality model has zero average Brier, the law cannot demonstrate a strict relative improvement; do not divide by zero or call a tie a success. Per-cell errors and family-specific coverage remain mandatory.

The constant training-prevalence forecast, a three-feature C0-only unconstrained logistic model, and a three-feature monotone C0-quality model may be reported as fixed sensitivities using the same training split/penalty. They cannot replace the six-feature primary comparator or rescue a failed H4. Do not select the easiest comparator after seeing any validation result.

The two predictors intentionally use different information: the law also sees latent displacement and target-model derivatives. Better accuracy would support the usefulness of those expensive measurements under the declared protocol, not equal-cost superiority, causal identification, a lightweight extractor, or universal insufficiency of every possible quality model.
