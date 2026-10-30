# What the saved development results allow a policy to learn

**Status: WP3 complete. PHASE_B_JOURNALS=off.** All numerical findings below are retrospective, descriptive MEASURED or DERIVED results from saved development numbers. No new watermark, attack, detector, metric, model or policy experiment ran. The F6 outcome remains unseen. The central result is that source heterogeneity and predictable survival exist, but the observed fixed-arm set offers almost no source-personalization gain once the regeneration cell is known. A new action space could behave differently; these logs cannot estimate that effect.

## Provenance and endpoints

[Data inventory](analysis/data-inventory.json) records exact input paths, hashes and status counts. Stage2b is the union containing Stage2a: it is counted once, with 11,040 final IDs, including 23 safety blocks. Phase A native/detect journals form a separate cohort. Normalization retains 11,760 numeric records: 7,440 Stage2 union and 4,320 Phase A; 60 identical development sources, seeds 12/13/14, four arms. Cohorts use different kernels/conditions and are not independent replications. The normalized gzip snapshot, scripts and [reproduction guide](analysis/README.md) permit checking calculations without opening images or held-out journals. Its decompressed SHA-256 is `61cd39060c8ffc70c2f7d13fd1a3289b25c7ad1a3d4d473e8a0453f2bcfcab55`.

SOURCE: [reader semantics](context/wp1-reader-semantics.md), established from code before analysis. Internal decoded margin is normalized correlation minus 8.259326826136963. Generic `score-threshold` switches between decoded and recomputed branches: a positive generic margin does **not** imply content-compatible detection. C requires decoded read and content match; J additionally requires exact original q, not exact fragile h. Recomputed presence and generic carrier detection are reported separately. External WAM/VINE-R margins are matching bits minus threshold (27/32 and 69/100), and their endpoint P is message presence, not content binding. Units and tasks are never pooled into a security-efficacy claim.

Primary source majority means at least two successes among three planned seeds. Missing endpoints count as non-success in the conservative analysis; optimistic and complete-source alternatives are retained. There are 17 unresolved Stage2 and 16 unresolved Phase A calls in the normalized selection. Structural numeric missingness is different: WAM has 1,460 observed P=false calls with no numeric margin, and nine unresolved calls with no margin. SOURCE: `scripts/journal_wam_probe.py:90` returns no decoded message for an empty positive mask; `scripts/encoder_transfer_test.py:62-65` consequently reports no matches and P=false. No arbitrary numeric floor was imputed. Complete-case WAM margin statistics can therefore be strongly selected.

## 1. Reward signal: continuous variation can coexist with a binary floor

[All 68 arm/cell/cohort summaries](analysis/reward-tables.md) and [machine-readable results](analysis/reward-results.json) give decoded, recomputed, generic, instance and external margins, quantiles, observed calls, seed-success counts, source majorities and mixed-seed sources. Representative Stage2 values follow; mixed sources have both success and failure among observed seeds. Thus the last column directly measures non-saturated binary variation within sources, not a population probability.

| Arm / cell | Median decoded or matched-bit margin | Successful / observed seed calls | C or P majority /60 | Mixed-seed sources /60 |
|---|---:|---:|---:|---:|
| F5 R0 .2 | 5.150 | 170/177 | 57 C | 2 |
| F5 R0 .4 | 2.271 | 117/178 | 39 C | 18 |
| F5 R1 .1 | -2.749 | 0/180 | 0 C | 0 |
| F5 R1 .2 | -3.946 | 0/180 | 0 C | 0 |
| F5 R1 .4 | -4.342 | 0/180 | 0 C | 0 |
| F5 K3 .2 | -2.212 | 16/180 | 5 C | 7 |
| v5 R0 .2 | 0.003 | 82/179 | 27 C | 9 |
| v5 R1 .1 | 1.589 | 140/180 | 50 C | 16 |
| v5 R1 .2 | -1.079 | 38/180 | 12 C | 14 |
| VINE-R R0 .4 | 4 bits | 136/179 | 47 P | 20 |
| VINE-R R1 .4 | 4.5 bits | 128/180 | 45 P | 17 |
| WAM R1 .4 | -11 bits, only 14 numeric rows | 0/180 | 0 P | 0 |

JUDGMENT: F5 SDXL binary reward supplies no observed positive feedback, despite varied continuous margins. Reward shaping might help optimization, but improving decoded margin is not enough if content consistency fails. For example F5 R1 .1 has 26 positive generic-margin calls with C=false; v5 R1 .2 has 78. A policy trained on the generic field could optimize the wrong event. VINE-R has headroom at stronger regeneration, but its presence endpoint and clean-quality allowance differ.

## 2. Source, seed and residual variation

[Variance note](analysis/variance-note.md) supplies 128 balanced decompositions, formulas, random-component estimates, missingness and 112 paired comparisons. Fixed source/seed/residual sums of squares are distinguished from population variance components. With one observation per source/seed, the residual includes interaction and noise; three seeds do not identify a stable population seed distribution.

MEASURED/DERIVED: F5 R1 .2 mean decoded margin is -3.9109. Source, seed and residual account for 86.3%, 3.2% and 10.6% of fixed total SS, respectively (rounding). Method-of-moments random components are 0.62619, 0.03431 and 0.12243 correlation-units squared; pooled within-source variance is 0.15674. This is source-dominated heterogeneity of an unsuccessful fixed writer, **not** evidence that a pre-mark feature predicts a beneficial action. WAM R1 .4 in each cohort and Stage2 R1-smooth .2 each have only one complete numeric source, so margin decomposition is unavailable there.

Shared source/seed pairing is not automatically a variance reduction technique: the F5-minus-v5 margin variance divided by the sum of individual variances is 0.812 at R0 .2 but 1.054 at R1 .2. Common seed labels need not create the desired covariance for new actions or different models.

## 3. Personalization ceiling and its information price

[Oracle note](analysis/oracle-note.md) defines four distinct selection problems, covers 96 analyses and retains missingness/quality sensitivities. C/J compare only F5 and v5 (q32+h32); external P compares WAM32 and VINE100 with different readers. Both internal methods meet strict clean quality on 60/60 sources; WAM does on 58/60 and VINE on 31/60. Strict means PSNR>35, SSIM>.9 and LPIPS<.1. External P has no fixed arm eligible on all 60 sources; this means unavailable under that constraint, not zero efficacy.

| Stage2 seven native cells, 420 source-cell opportunities | C | J |
|---|---:|---:|
| Best single fixed arm | 196 (v5) | 93 (F5) |
| Hindsight per-source arm, chosen before unknown cell, average objective | 209 | 108 |
| Cell-known fixed-arm selector | 275 | 130 |
| Clairvoyant source-and-cell selector | 276 | 132 |

DERIVED: most apparent oracle improvement is information about the regenerator. Within-cell C personalization adds only one source majority (R0 .2, 57 to 58); J adds two (R0 .1, 41 to 43). Exact minimax selection over one arm per source leaves worst-family C at 62/180 and J at 6/180. WAM/VINE unconstrained P fixed and oracle both reach 392/420. Its source-wise quality-constrained oracle reaches 262/420, without an all-source quality-eligible fixed external arm.

Missingness does not overturn the C ceiling: conservative clairvoyant C is 276/420, optimistic 278/420, and complete-source 270/406 (58 sources). J is 132/420, 133/420 and 129/406. These are ceilings only for the finite observed arms/cells and chosen aggregate objective, not bounds on new writers. Hindsight choices are unlearned and do not establish equal-budget gains. Producing multiple candidate marks to observe their clean features has a cost.

## 4. Predictability before regeneration

[Predictability note](analysis/predictability-note.md) and its script use whole-source leave-one-out ridge regression, fixed lambda=1, training-fold imputation/standardization and a training-fold constant-mean comparator. No hyperparameter or feature-set winner is selected. Inputs are numeric clean quality, clean reader margins and F5 embedding summaries; post-regeneration descriptors are excluded. These features exist only after candidate writing/reading, so they do not establish free P1 information. Phase A borrows clean features from the same Stage2 marked sources, explicitly.

MEASURED/DESCRIPTIVE: on F5 R0 .4, C majority Brier improves from .235 to .153 and AUC is .811; on R0 .2, Brier worsens from .049 to .055. All F5 SDXL majority labels are zero, so ranking skill is unassessable. v5 R0 .1/.2 Brier improves from .176/.256 to .098/.134, AUC .928/.881; several other cells worsen. VINE-R P at R1 .4 improves from .194 to .133, AUC .784. WAM R1 .2 AUC .957 is based on only two positive sources and is not a validated predictor. Constant-label metrics are suppressed: AUC is undefined, whereas trivial constant Brier could be zero.

The clean F5 decoded margin has Spearman correlation .977 with mean R0 .4 regenerated margin (58 complete sources), and .546 with R1 .1 (60), despite zero C in the latter. These are in-sample associations, not cross-validated continuous predictions and not evidence for an action-dependent improvement. Survival prediction and treatment-effect prediction are different tasks.

## 5. Ranking and continuous-policy sample cost

DERIVED, conditional: the variance package computes 1,125 planning cases for K=8/64/1024, gaps, best-option identification versus full ordering, Gaussian plug-in approximations and bounded-reward Hoeffding guarantees. For F5 R1 .2 and a .5 correlation-unit gap, nominal simultaneous 95% best-option Gaussian plans require 8/13/20 fresh seeds per option, or 64/832/20,480 rollouts **per source**. They assume new options share retained fixed-arm noise and ignore its estimation uncertainty. The corresponding distribution-free range bounds are 50,603/73,102/101,645 seeds per option and are conservative. Neither calculation promises a learnable gap. Zero observed binary variance is especially uninformative about discovering a new success.

SOURCE/DERIVED cost: the brief supplies measured regeneration+reader+quality feedback of 2.19–3.63 seconds; F5 shard latency732 seconds corresponds approximately to122 device-equivalent seconds under six-way sharing. At $0.551/hour, the above K plans using an existing carrier cost .04–.06, .51–.84 and12.46–20.65 device-hours per source. Writing each fixed F5 option once and caching it costs .31–.34,2.68–3.01 and47.16–55.35 hours, respectively ($.17–.18,$1.47–1.66,$25.99–30.50). A full60-source design multiplies these totals by60. Serial latency and throughput are different, and additive timer scopes are planning approximations.

The correct cached-candidate formula is `K*w + K*n*feedback`; a continuously changed mark instead pays `N*(w+feedback)`. F6 w=361–723 seconds is an unmeasured planning anchor, never an observed outcome. Costs for both regimes, all K values and F6 sensitivity are retained in JSON.

Policy-gradient variance is **unidentified**: there are no sampled policy actions, probabilities, log gradients or action-reward relationships in these fixed-arm logs. A deliberately conditional Gaussian-action illustration gives noise-only `trace Cov(mean gradient)=d*v/(n*sigma^2)` when additive reward noise is independent of action and an oracle baseline removes the mean. It is not complete gradient variance or learning sample complexity. WP4 develops the comparison with pathwise gradients.

## 6. Attacker room

DERIVED from [reward results](analysis/reward-results.json): without an attack-fidelity constraint, one fixed strong cell already reduces F5/v5/WAM source-majority survival to0/60; per-source choice over the logged menu cannot improve that removal endpoint. For VINE-R, the best fixed cell (R1 .4) leaves45/60, while a clairvoyant per-source cell choice leaves40/60. On57 sources complete across cells it is42 versus37, still five additional removals. This is finite-menu presence removal headroom of8.3 percentage points, not a trained policy result. It may disappear under matched fidelity, query charges or generalization. Attack-output fidelity is separate from strict clean writer quality. T4/T5 policy effects are not identified by this T3 grid.

## Limits and decision implications

No policy allocation was randomized, arms are fixed methods, three seeds are sparse, and source/cell selection is retrospective. Continuous margins have different units across readers. Source heterogeneity does not imply action heterogeneity, and predictability does not establish controllability. The WP3 arithmetic supports investigating a richer action space only after its non-RL baseline and cost are specified; it does not establish RL superiority.

Because PHASE_B_JOURNALS=off, **none of the six per-source/seed questions can be answered for Phase B**: no held-out margin distribution, variance decomposition, oracle, LOSO prediction, seed-based sample-cost estimate or adaptive attacker ceiling is computed. Its committed aggregate summary remains frozen and is used only as prior context, not for tuning. No new source, protected reserve/Stage C identifier, image or F6 output was opened. Later designs must use fresh disjoint sources.

Verification: extraction checks endpoint implications and design keys; oracle arithmetic includes exact minimax dynamic programming and300 tiny brute-force cross-checks; variance asserts SS additivity and equivalent within-source formulas; ridge/AUC checks and source-disjoint folds are recorded in the notes. All runs used only the permitted stdlib interpreter with `-I`, each far below10 minutes. These validate calculations, not a new scientific claim.
