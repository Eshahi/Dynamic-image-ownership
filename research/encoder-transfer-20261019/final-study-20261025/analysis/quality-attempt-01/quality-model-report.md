# Quality-only diagnostic models

Development-only descriptive fits on the last record per ID in the stage2b union journal. No marked-output reader score or target detector state enters the predictors.

The weighted objective is the **sum**, not mean, of Bernoulli negative log likelihood with each completed source-cell totaling weight 1, plus 0.5 times the squared standardized nonintercept coefficients (L2=1). Training-fold weighted moments standardize features. D1/D2 enforce LPIPS ≤ 0 and PSNR/SSIM ≥ 0; D3 is unconstrained. Cyclic coordinate Newton uses backtracking and a 1e-8 KKT tolerance, at most 2000 passes. All fit diagnostics, including failures, are in the JSON. A finite-difference gradient and positive directional-curvature check passed for the convex objective.

Journal: 39896 lines, 11040 final IDs, 28856 overwritten states.
Five source-disjoint folds use the frozen SHA256 assignment. Completed quality calls alone enter fitting; incomplete outputs remain in the JSON coverage table. Training within R0/R1 tests in-family source generalization; leave-one-strength-out tests strength extrapolation inside those two families. Neither is independent-family confirmation.

## f5-r2

Completed: 1074 calls, 60 sources. Fold source counts: {'1': 9, '2': 11, '0': 16, '4': 11, '3': 13}.

| Model | CV Brier | CV log loss | LOSO Brier | LOSO log loss |
|---|---:|---:|---:|---:|
| D0 | 0.2459 | 0.6850 | 0.2530 | 0.6992 |
| D1 | 0.2459 | 0.6850 | 0.2530 | 0.6992 |
| D2 | 0.2459 | 0.6850 | 0.2530 | 0.6992 |
| D3 | 0.0433 | 0.1491 | 0.0621 | 0.2237 |

| Cell | Completed | Observed C | D2 predicted | D3 predicted |
|---|---:|---:|---:|---:|
| R0 0.1 | 179 | 1.000 | 0.433 | 0.974 |
| R0 0.2 | 177 | 0.950 | 0.433 | 0.911 |
| R0 0.4 | 178 | 0.653 | 0.433 | 0.665 |
| R1 0.1 | 180 | 0.000 | 0.433 | 0.032 |
| R1 0.2 | 180 | 0.000 | 0.433 | 0.008 |
| R1 0.4 | 180 | 0.000 | 0.433 | 0.001 |

Paired source-cluster bootstrap, D3−D2 held-out CV Brier: -0.2026; 95% percentile interval [-0.2151, -0.1889] (1,000 draws, seed 20261025).

A lower loss for D3 limits these specified quality-only logistic forms; it cannot rule out arbitrary distortion functionals or isolate an encoder mechanism. Family and schedule labels are diagnostics, not a transfer law.

## v5-r3

Completed: 1077 calls, 60 sources. Fold source counts: {'1': 9, '2': 11, '0': 16, '4': 11, '3': 13}.

| Model | CV Brier | CV log loss | LOSO Brier | LOSO log loss |
|---|---:|---:|---:|---:|
| D0 | 0.2373 | 0.6676 | 0.3605 | 0.9583 |
| D1 | 0.1850 | 0.5416 | 0.2749 | 0.7597 |
| D2 | 0.1876 | 0.5481 | 0.2831 | 0.7776 |
| D3 | 0.1326 | 0.4121 | 0.1384 | 0.4373 |

| Cell | Completed | Observed C | D2 predicted | D3 predicted |
|---|---:|---:|---:|---:|
| R0 0.1 | 180 | 0.800 | 0.553 | 0.843 |
| R0 0.2 | 179 | 0.458 | 0.368 | 0.379 |
| R0 0.4 | 178 | 0.039 | 0.125 | 0.058 |
| R1 0.1 | 180 | 0.778 | 0.622 | 0.739 |
| R1 0.2 | 180 | 0.211 | 0.425 | 0.227 |
| R1 0.4 | 180 | 0.000 | 0.183 | 0.025 |

Paired source-cluster bootstrap, D3−D2 held-out CV Brier: -0.0550; 95% percentile interval [-0.0741, -0.0382] (1,000 draws, seed 20261025).

A lower loss for D3 limits these specified quality-only logistic forms; it cannot rule out arbitrary distortion functionals or isolate an encoder mechanism. Family and schedule labels are diagnostics, not a transfer law.

## Coverage and scope

Scheduled calls: 180 per arm/family/strength cell. F5 completed R0 .1/.2/.4: 179/177/178; R1: 180/180/180. v5 completed R0: 180/179/178; R1: 180/180/180. Nine R0 calls were safety blocked (six F5, three v5). Details are in the JSON. 
The hypothesis document asks for a “frozen caliper overlap count” but defines no caliper width or metric, so a caliper count is not computed or retrospectively selected. The model comparison spans observed R0/R1 quality support; it is not a matched-caliper analysis.

Failed or missing outputs have no fabricated quality values. All endpoint counts including failed calls belong in the companion descriptive WP2 report. This statistical comparison uses a reused development population, so its intervals describe source resampling conditional on that population and fitted predictions, not confirmatory uncertainty.
