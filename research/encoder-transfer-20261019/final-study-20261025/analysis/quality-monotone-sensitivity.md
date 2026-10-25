# Post-hoc monotone D3 sensitivity

D3 in the primary analysis augments D2 with family and logSNR **and relaxes** the LPIPS/PSNR/SSIM sign constraints. Thus its gain over D2 cannot be attributed solely to family/schedule. D3M is a separate sensitivity using the same completed calls, source-cell weights, five source-disjoint folds, train-only scaling, L2=1, and coordinate Newton solver. It adds family/logSNR while retaining LPIPS ≤ 0, PSNR and SSIM ≥ 0. Family and logSNR remain unrestricted. This sensitivity was specified after inspecting D0-D3 results and is descriptive.

| Arm | Model | CV Brier | CV log loss | LOSO Brier | LOSO log loss | Convergence |
|---|---|---:|---:|---:|---:|---|
| f5-r2 | D2 | 0.245931 | 0.684994 | 0.252957 | 0.699242 | 8/8 |
| f5-r2 | D3M | 0.043188 | 0.148910 | 0.058012 | 0.199571 | 8/8 |
| f5-r2 | D3 | 0.043292 | 0.149105 | 0.062232 | 0.224188 | 8/8 |
| v5-r3 | D2 | 0.187621 | 0.548082 | 0.283100 | 0.777573 | 8/8 |
| v5-r3 | D3M | 0.134090 | 0.413653 | 0.135407 | 0.420991 | 8/8 |
| v5-r3 | D3 | 0.132625 | 0.412261 | 0.138628 | 0.438387 | 8/8 |

D3M is still an in-family development-population diagnostic. A lower D3M loss than D2 limits this specified monotone quality-only form; it does not isolate a causal encoder effect or rule out other distortion models. Leave-one-strength-out still uses only R0/R1 and should not be read as family transfer.
