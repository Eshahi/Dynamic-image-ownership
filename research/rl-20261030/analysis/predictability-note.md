# WP3 predictability: numeric features before regeneration

**MEASURED, post-hoc descriptive development analysis.** All numbers below are reproduced by `predictability.py` from `dev-records.jsonl`; full metrics, missingness, individual-feature fits and margin associations are in `predictability-results.json`. No held-out journals, images or new watermark executions were used.

## Fixed analysis and interpretation

The primary model is ridge regression with lambda=1 on the sum of squared residuals, unpenalized intercept, training-fold mean imputation and training-fold population standardization. Each arm/cell/cohort has its own model. A held-out source contributes no labels from any seed or cell to fitting; each source is one row with three-seed majority (>=2) or success fraction (successes/3). No feature selection, model tuning, seed-wise splitting or policy deployment is performed. Every individual feature is also fit with the same fixed ridge penalty as a descriptive diagnostic; these are not selected winners.

The constant comparator is the training-fold outcome mean. Its Brier/RMSE is valid, but its AUC is deliberately suppressed: leave-one-out fold prevalence changes would mechanically reverse-order binary labels. Ridge AUC uses unrounded, unclipped predictions; Brier and RMSE clip predictions to [0,1]. Metrics are not reported for constant labels because predictive skill is not assessable there. AUC is mathematically undefined for such labels; Brier/RMSE could be computed and a trivial constant prediction would give zero. There are no calibrated survival probabilities here.

Clean margins are separate decoded and recomputed scores minus their own thresholds, for semantic and instance readers. F5 adds embedding margin minimum/median and negative-chip count; all arms use PSNR, SSIM and LPIPS. External arms use clean presence margin, and their outcomes are P (message presence), not C (content-compatible detection). These predictors exist only after paying to write and clean-read that arm; they cannot be treated as free inputs to a pre-mark selector. Regenerated C0/f0 features are excluded.

Stage2 and Phase A are reported separately. Phase A explicitly reuses Stage2 clean features for the same 60 sources. This is repeated development data under different conditions, not fresh-source validation or evidence that a policy transfers to new sources.

Missing outcomes are failures in the conservative primary analysis (fraction denominator 3). Complete-source sensitivity drops any source with one missing seed. Counts of ambiguous majorities are in JSON. No missing numerical score is replaced by a fabricated score. Continuous soft-margin associations use only sources with three observed scores.

## Primary majority results

| Cohort | Arm / endpoint | Cell | Success / 60 | Missing seeds | Constant Brier | Ridge Brier | Ridge AUC | Complete n / ridge Brier |
|---|---|---|---:|---:|---:|---:|---:|---|
| phase_a | f5-r2 / C | R0-0.1 | 60 | 1 | not reported | not reported | not reported | 59 / not reported |
| phase_a | f5-r2 / C | R0-0.2 | 57 | 2 | 0.049 | 0.055 | 0.614 | 58 / 0.040 |
| phase_a | f5-r2 / C | R0-0.4 | 39 | 2 | 0.235 | 0.153 | 0.811 | 58 / 0.136 |
| phase_a | f5-r2 / C | R1-0.1 | 0 | 0 | not reported | not reported | not reported | 60 / not reported |
| phase_a | f5-r2 / C | R1-0.2 | 0 | 0 | not reported | not reported | not reported | 60 / not reported |
| phase_a | f5-r2 / C | R1-0.4 | 0 | 0 | not reported | not reported | not reported | 60 / not reported |
| phase_a | v5-r3 / C | R0-0.1 | 47 | 0 | 0.176 | 0.098 | 0.928 | 60 / 0.098 |
| phase_a | v5-r3 / C | R0-0.2 | 27 | 1 | 0.256 | 0.134 | 0.881 | 59 / 0.133 |
| phase_a | v5-r3 / C | R0-0.4 | 3 | 2 | 0.049 | 0.048 | 0.772 | 58 / 0.049 |
| phase_a | v5-r3 / C | R1-0.1 | 50 | 0 | 0.144 | 0.127 | 0.766 | 60 / 0.127 |
| phase_a | v5-r3 / C | R1-0.2 | 11 | 0 | 0.155 | 0.129 | 0.809 | 60 / 0.129 |
| phase_a | v5-r3 / C | R1-0.4 | 0 | 0 | not reported | not reported | not reported | 60 / not reported |
| phase_a | vine-r / P | R0-0.1 | 60 | 1 | not reported | not reported | not reported | 59 / not reported |
| phase_a | vine-r / P | R0-0.2 | 60 | 2 | not reported | not reported | not reported | 58 / not reported |
| phase_a | vine-r / P | R0-0.4 | 47 | 1 | 0.176 | 0.171 | 0.592 | 59 / 0.174 |
| phase_a | vine-r / P | R1-0.1 | 60 | 0 | not reported | not reported | not reported | 60 / not reported |
| phase_a | vine-r / P | R1-0.2 | 60 | 0 | not reported | not reported | not reported | 60 / not reported |
| phase_a | vine-r / P | R1-0.4 | 45 | 0 | 0.194 | 0.133 | 0.784 | 60 / 0.133 |
| phase_a | wam / P | R0-0.1 | 42 | 0 | 0.217 | 0.196 | 0.661 | 60 / 0.196 |
| phase_a | wam / P | R0-0.2 | 18 | 2 | 0.217 | 0.197 | 0.701 | 59 / 0.200 |
| phase_a | wam / P | R0-0.4 | 1 | 2 | 0.017 | 0.021 | 0.559 | 59 / 0.021 |
| phase_a | wam / P | R1-0.1 | 49 | 0 | 0.155 | 0.152 | 0.568 | 60 / 0.152 |
| phase_a | wam / P | R1-0.2 | 2 | 0 | 0.033 | 0.027 | 0.957 | 60 / 0.027 |
| phase_a | wam / P | R1-0.4 | 0 | 0 | not reported | not reported | not reported | 60 / not reported |
| stage2_union | f5-r2 / C | R0-0.1 | 60 | 1 | not reported | not reported | not reported | 59 / not reported |
| stage2_union | f5-r2 / C | R0-0.2 | 57 | 3 | 0.049 | 0.055 | 0.614 | 58 / 0.040 |
| stage2_union | f5-r2 / C | R0-0.4 | 39 | 2 | 0.235 | 0.153 | 0.811 | 58 / 0.136 |
| stage2_union | f5-r2 / C | R1-0.1 | 0 | 0 | not reported | not reported | not reported | 60 / not reported |
| stage2_union | f5-r2 / C | R1-0.2 | 0 | 0 | not reported | not reported | not reported | 60 / not reported |
| stage2_union | f5-r2 / C | R1-0.4 | 0 | 0 | not reported | not reported | not reported | 60 / not reported |
| stage2_union | f5-r2 / C | R1-mode-0.2 | 0 | 0 | not reported | not reported | not reported | 60 / not reported |
| stage2_union | f5-r2 / C | R1-rinse-0.1 | 0 | 0 | not reported | not reported | not reported | 60 / not reported |
| stage2_union | f5-r2 / C | R1-smooth-0.2 | 0 | 0 | not reported | not reported | not reported | 60 / not reported |
| stage2_union | f5-r2 / C | R3-0.2 | 5 | 0 | 0.079 | 0.061 | 0.884 | 60 / 0.061 |
| stage2_union | v5-r3 / C | R0-0.1 | 47 | 0 | 0.176 | 0.098 | 0.928 | 60 / 0.098 |
| stage2_union | v5-r3 / C | R0-0.2 | 27 | 1 | 0.256 | 0.134 | 0.881 | 59 / 0.133 |
| stage2_union | v5-r3 / C | R0-0.4 | 3 | 2 | 0.049 | 0.048 | 0.772 | 58 / 0.049 |
| stage2_union | v5-r3 / C | R1-0.1 | 50 | 0 | 0.144 | 0.127 | 0.766 | 60 / 0.127 |
| stage2_union | v5-r3 / C | R1-0.2 | 12 | 0 | 0.165 | 0.131 | 0.845 | 60 / 0.131 |
| stage2_union | v5-r3 / C | R1-0.4 | 0 | 0 | not reported | not reported | not reported | 60 / not reported |
| stage2_union | v5-r3 / C | R1-mode-0.2 | 6 | 0 | 0.093 | 0.091 | 0.691 | 60 / 0.091 |
| stage2_union | v5-r3 / C | R1-rinse-0.1 | 4 | 0 | 0.064 | 0.068 | 0.460 | 60 / 0.068 |
| stage2_union | v5-r3 / C | R1-smooth-0.2 | 4 | 0 | 0.064 | 0.065 | 0.634 | 60 / 0.065 |
| stage2_union | v5-r3 / C | R3-0.2 | 57 | 0 | 0.049 | 0.052 | 0.450 | 60 / 0.052 |
| stage2_union | vine-r / P | R0-0.1 | 60 | 0 | not reported | not reported | not reported | 60 / not reported |
| stage2_union | vine-r / P | R0-0.2 | 60 | 2 | not reported | not reported | not reported | 58 / not reported |
| stage2_union | vine-r / P | R0-0.4 | 47 | 1 | 0.176 | 0.171 | 0.592 | 59 / 0.174 |
| stage2_union | vine-r / P | R1-0.1 | 60 | 0 | not reported | not reported | not reported | 60 / not reported |
| stage2_union | vine-r / P | R1-0.2 | 60 | 0 | not reported | not reported | not reported | 60 / not reported |
| stage2_union | vine-r / P | R1-0.4 | 45 | 0 | 0.194 | 0.133 | 0.784 | 60 / 0.133 |
| stage2_union | vine-r / P | R1-mode-0.2 | 60 | 0 | not reported | not reported | not reported | 60 / not reported |
| stage2_union | vine-r / P | R1-rinse-0.1 | 59 | 0 | 0.017 | 0.017 | 0.169 | 60 / 0.017 |
| stage2_union | vine-r / P | R1-smooth-0.2 | 60 | 0 | not reported | not reported | not reported | 60 / not reported |
| stage2_union | vine-r / P | R3-0.2 | 60 | 0 | not reported | not reported | not reported | 60 / not reported |
| stage2_union | wam / P | R0-0.1 | 42 | 1 | 0.217 | 0.196 | 0.661 | 59 / 0.199 |
| stage2_union | wam / P | R0-0.2 | 18 | 2 | 0.217 | 0.197 | 0.701 | 59 / 0.200 |
| stage2_union | wam / P | R0-0.4 | 1 | 2 | 0.017 | 0.021 | 0.559 | 59 / 0.021 |
| stage2_union | wam / P | R1-0.1 | 48 | 0 | 0.165 | 0.160 | 0.602 | 60 / 0.160 |
| stage2_union | wam / P | R1-0.2 | 2 | 0 | 0.033 | 0.027 | 0.957 | 60 / 0.027 |
| stage2_union | wam / P | R1-0.4 | 0 | 0 | not reported | not reported | not reported | 60 / not reported |
| stage2_union | wam / P | R1-mode-0.2 | 2 | 0 | 0.033 | 0.027 | 0.957 | 60 / 0.027 |
| stage2_union | wam / P | R1-rinse-0.1 | 21 | 0 | 0.235 | 0.170 | 0.833 | 60 / 0.170 |
| stage2_union | wam / P | R1-smooth-0.2 | 0 | 0 | not reported | not reported | not reported | 60 / not reported |
| stage2_union | wam / P | R3-0.2 | 44 | 0 | 0.202 | 0.161 | 0.788 | 60 / 0.161 |

## Fraction outcome summary

Unweighted macro summaries below include only nonconstant fraction cells. Cells are correlated because they reuse sources; these are descriptive summaries, not independent replications.

| Cohort | Arm | Nonconstant fraction cells | Mean constant RMSE | Mean ridge RMSE | Cells ridge RMSE lower |
|---|---|---:|---:|---:|---:|
| stage2_union | f5-r2 | 4 | 0.224 | 0.199 | 2 |
| stage2_union | v5-r3 | 9 | 0.295 | 0.260 | 7 |
| stage2_union | vine-r | 6 | 0.169 | 0.153 | 2 |
| stage2_union | wam | 8 | 0.301 | 0.273 | 7 |
| phase_a | f5-r2 | 3 | 0.214 | 0.195 | 1 |
| phase_a | v5-r3 | 5 | 0.333 | 0.274 | 5 |
| phase_a | vine-r | 5 | 0.176 | 0.157 | 2 |
| phase_a | wam | 5 | 0.282 | 0.264 | 4 |

## Reading the pattern

MEASURED: F5 R0 .4 has 39/60 source-majority successes; all-feature ridge improves Brier from 0.235 to 0.153 with AUC 0.811. This survives complete-source sensitivity (58 sources, ridge Brier 0.136). F5 R0 .2 has only three majority failures, and ridge worsens Brier from 0.049 to 0.055. F5 R1 cells all have zero majority successes: no binary ranking claim is available there. F5 R3 .2 has only five successes; its AUC 0.884 is particularly sample-sensitive.

MEASURED: v5 R0 .1/.2 shows a stronger prediction signal (AUC 0.928/0.881, Brier 0.176/0.256 reduced to 0.098/0.134). This does not generalize to every cell: at R1-rinse .1, R1-smooth .2 and R3 .2 ridge Brier is worse than the constant baseline. VINE-R P at R1 .4 improves Brier from 0.194 to 0.133 (AUC 0.784), while its several all-success cells cannot test ranking. WAM R1 .2 AUC 0.957 depends on just two positive sources and must not be portrayed as a validated high-accuracy model.

MEASURED: F5 clean semantic decoded margin correlates with mean regenerated decoded margin at R0 .4 (Spearman 0.977, 58 complete sources) and R1 .1 (0.546, 60 sources). The latter association coexists with zero majority C successes. Continuous numerical signal therefore does not itself establish room to cross the decision boundary. These correlations are descriptive in-sample associations, not cross-validated predictions.

JUDGMENT: The logs contain some rankable source information, strongest in several nondegenerate R0 cells, but do not support a generic claim that clean features rescue F5 under R1. The learned outcome prediction is not an estimate of the effect of changing any action.

## Feature availability and limits

- f5-r2: 10 features; 0 missing feature entries among 60 clean sources; constant features: none.
- v5-r3: 7 features; 0 missing feature entries among 60 clean sources; constant features: none.
- vine-r: 4 features; 0 missing feature entries among 60 clean sources; constant features: none.
- wam: 4 features; 0 missing feature entries among 60 clean sources; constant features: presence_margin.

VINE-R clean presence margin has only two values (30 and 31 matching bits above threshold); WAM clean presence margin is constant. External-arm prediction therefore largely concerns quality features rather than a broadly varying clean detection score.

JUDGMENT: Predictability can identify numerical association worth a prospective test, but it does not establish a causal action, the benefit of changing a writer, the superiority of RL, or a deployable calibrated learner. Small n, many correlated cells/features, ceiling/floor outcomes, and repeated-source reuse limit interpretation. Individual-feature tables and soft-margin correlations are exploratory diagnostics without multiplicity-adjusted claims.

Validation: analytical two-variable linear-system solution, one-feature ridge solution (including a missing training value), tied-score AUC and constant-label AUC checks passed using only the permitted stdlib interpreter. Runtime assertions check exactly three distinct seeds per source/cell, exactly 60 sources, matching clean records and source-disjoint training folds.
