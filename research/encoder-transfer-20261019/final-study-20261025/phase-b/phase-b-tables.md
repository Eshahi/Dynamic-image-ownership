# Phase B results (amendment B1)

Sources 200 of 200 planned.

## Confirmatory family (Holm, alpha .05)

| Slot | Count | p | Holm rank | threshold | adjusted | status |
|---|---|---|---|---|---|---|
| H1 | k+ R1 .1 19, R1 .2 0 | 0.466 | 4 | 0.005 | 1 | INCONCLUSIVE_SUPPORT |
| H2 | 182/200 | 1.81e-05 | 1 | 0.003846 | 0.000236 | SUPPORTED |
| H3 | 163/200 | 0.335 | 3 | 0.004545 | 1 | INCONCLUSIVE_SUPPORT |
| H4 | – | 1 | 5 | 0.005556 | 1 | UNEVALUATED_PREREQUISITE_FAILURE (comparator BASELINE_UNAVAILABLE) |
| H5-A-f5-r2 | – | 1 | 6 | 0.00625 | 1 | UNAVAILABLE_ATTACK_INACTIVE (quality-ineligible) |
| H5-A-v5-r3 | – | 1 | 7 | 0.007143 | 1 | UNAVAILABLE_ATTACK_INACTIVE (quality-ineligible) |
| H5-A-wam | – | 1 | 9 | 0.01 | 1 | UNAVAILABLE_ATTACK_INACTIVE (quality-ineligible) |
| H5-A-vine-r | – | 1 | 8 | 0.008333 | 1 | UNAVAILABLE_ATTACK_INACTIVE (quality-ineligible) |
| H5-B-f5-r2 | – | 1 | 10 | 0.0125 | 1 | UNAVAILABLE_ATTACK_INACTIVE (quality-ineligible) |
| H5-B-v5-r3 | – | 1 | 11 | 0.01667 | 1 | UNAVAILABLE_ATTACK_INACTIVE (quality-ineligible) |
| H5-B-wam | – | 1 | 13 | 0.05 | 1 | UNAVAILABLE_ATTACK_INACTIVE (quality-ineligible) |
| H5-B-vine-r | – | 1 | 12 | 0.025 | 1 | UNAVAILABLE_ATTACK_INACTIVE (quality-ineligible) |
| H6 | R0-0.2 194, R1-0.1 200, R1-0.2 200 | 0.000148 | 2 | 0.004167 | 0.00178 | SUPPORTED |

## Source majorities by cell and arm (Y all-attempt / Y+ possible-majority)

| Cell | f5-r2 | v5-r3 | wam | vine-r |
|---|---|---|---|---|
| R0-0.1 | 186 / 190 | 163 / 166 | 120 / 123 | 195 / 200 |
| R0-0.2 | 182 / 186 | 122 / 124 | 51 / 54 | 194 / 198 |
| R0-0.4 | 140 / 142 | 28 / 30 | 7 / 8 | 158 / 161 |
| R1-0.1 | 19 / 19 | 173 / 173 | 136 / 136 | 200 / 200 |
| R1-0.2 | 0 / 0 | 47 / 47 | 20 / 20 | 200 / 200 |
| R1-0.4 | 0 / 0 | 0 / 0 | 0 / 0 | 174 / 174 |
| K3-0.2 | 61 / 61 | 189 / 189 | 132 / 132 | 200 / 200 |
| clean | 196 | 199 | 200 | 200 |
| B-codec | 194 | 194 | 167 | 200 |

## Negative gates (source-any events over the executed battery)

| Stratum | events | unresolved sources | passed | 95% CP upper | Bonferroni-8 upper |
|---|---|---|---|---|---|
| f5-r2|C0 | 0 | 4 | False | 0.0149 | 0.0251 |
| f5-r2|wrong | 0 | 8 | False | 0.0149 | 0.0251 |
| v5-r3|C0 | 0 | 4 | False | 0.0149 | 0.0251 |
| v5-r3|wrong | 0 | 6 | False | 0.0149 | 0.0251 |
| wam|C0 | 0 | 4 | False | 0.0149 | 0.0251 |
| wam|wrong | 0 | 5 | False | 0.0149 | 0.0251 |
| vine-r|C0 | 0 | 4 | False | 0.0149 | 0.0251 |
| vine-r|wrong | 1 | 8 | False | 0.0235 | 0.0353 |

## Exploratory B1 law (outside Holm)

| Cell | identified | law positive | actual positive | rate error | worst mismatch | Brier | margin coverage (q90_R0) |
|---|---|---|---|---|---|---|---|
| R0-0.1 | 197 | 166 | 186 | -0.102 | 27 | 0.122 | 0.974 (588) |
| R0-0.2 | 198 | 139 | 182 | -0.217 | 50 | 0.237 | 0.964 (588) |
| R0-0.4 | 198 | 38 | 140 | -0.515 | 110 | 0.545 | 0.973 (592) |

## H3 components

- R1 lost (Y+=0): 181
- R0 retained (Y=1): 182
- qualities complete: 195
- strictly milder all three: 193

## Quality medians (attack d(y,u) / total d(y,x)): LPIPS, PSNR, SSIM

| Cell | arm | n | attack | total |
|---|---|---|---|---|
| R0-0.1 | unmarked | 591 | 0.105, 24.38, 0.728 | 0.105, 24.38, 0.728 |
| R0-0.1 | f5-r2 | 588 | 0.132, 24.29, 0.691 | 0.161, 24.30, 0.696 |
| R0-0.1 | v5-r3 | 592 | 0.114, 24.24, 0.705 | 0.119, 24.30, 0.715 |
| R0-0.1 | wam | 591 | 0.121, 24.24, 0.709 | 0.128, 24.31, 0.703 |
| R0-0.1 | vine-r | 585 | 0.109, 24.09, 0.718 | 0.116, 24.07, 0.719 |
| R0-0.2 | unmarked | 593 | 0.154, 22.98, 0.680 | 0.154, 22.98, 0.680 |
| R0-0.2 | f5-r2 | 588 | 0.187, 22.86, 0.638 | 0.214, 22.87, 0.638 |
| R0-0.2 | v5-r3 | 593 | 0.164, 22.82, 0.656 | 0.167, 22.91, 0.658 |
| R0-0.2 | wam | 592 | 0.172, 22.88, 0.651 | 0.172, 22.96, 0.654 |
| R0-0.2 | vine-r | 587 | 0.159, 22.74, 0.661 | 0.166, 22.80, 0.663 |
| R0-0.4 | unmarked | 596 | 0.254, 20.54, 0.593 | 0.254, 20.54, 0.593 |
| R0-0.4 | f5-r2 | 592 | 0.299, 20.40, 0.559 | 0.319, 20.41, 0.564 |
| R0-0.4 | v5-r3 | 593 | 0.265, 20.40, 0.571 | 0.269, 20.46, 0.583 |
| R0-0.4 | wam | 594 | 0.274, 20.46, 0.584 | 0.262, 20.53, 0.579 |
| R0-0.4 | vine-r | 591 | 0.260, 20.29, 0.584 | 0.262, 20.40, 0.576 |
| R1-0.1 | unmarked | 600 | 0.092, 27.51, 0.820 | 0.092, 27.51, 0.820 |
| R1-0.1 | f5-r2 | 600 | 0.104, 27.37, 0.803 | 0.123, 27.37, 0.803 |
| R1-0.1 | v5-r3 | 600 | 0.101, 27.29, 0.804 | 0.115, 27.29, 0.803 |
| R1-0.1 | wam | 600 | 0.098, 27.20, 0.808 | 0.108, 27.33, 0.807 |
| R1-0.1 | vine-r | 600 | 0.092, 27.37, 0.820 | 0.104, 26.73, 0.816 |
| R1-0.2 | unmarked | 600 | 0.140, 25.21, 0.751 | 0.140, 25.21, 0.751 |
| R1-0.2 | f5-r2 | 600 | 0.159, 25.10, 0.730 | 0.166, 25.12, 0.731 |
| R1-0.2 | v5-r3 | 600 | 0.155, 25.02, 0.732 | 0.158, 25.06, 0.733 |
| R1-0.2 | wam | 600 | 0.147, 25.02, 0.736 | 0.145, 25.15, 0.740 |
| R1-0.2 | vine-r | 600 | 0.141, 24.95, 0.750 | 0.150, 24.79, 0.745 |
| R1-0.4 | unmarked | 600 | 0.216, 22.50, 0.663 | 0.216, 22.50, 0.663 |
| R1-0.4 | f5-r2 | 600 | 0.246, 22.45, 0.645 | 0.239, 22.45, 0.641 |
| R1-0.4 | v5-r3 | 600 | 0.237, 22.36, 0.646 | 0.235, 22.46, 0.645 |
| R1-0.4 | wam | 600 | 0.224, 22.37, 0.654 | 0.219, 22.47, 0.650 |
| R1-0.4 | vine-r | 600 | 0.220, 22.31, 0.661 | 0.226, 22.42, 0.653 |
| K3-0.2 | unmarked | 600 | 0.102, 26.16, 0.819 | 0.102, 26.16, 0.819 |
| K3-0.2 | f5-r2 | 600 | 0.117, 26.01, 0.798 | 0.122, 26.03, 0.807 |
| K3-0.2 | v5-r3 | 600 | 0.116, 25.91, 0.800 | 0.114, 25.93, 0.808 |
| K3-0.2 | wam | 600 | 0.116, 25.92, 0.804 | 0.116, 26.04, 0.799 |
| K3-0.2 | vine-r | 600 | 0.104, 25.96, 0.814 | 0.113, 25.58, 0.813 |
| ctrlB-codec | unmarked | 200 | 0.063, 25.82, 0.770 | 0.063, 25.82, 0.770 |
| ctrlB-codec | f5-r2 | 200 | 0.092, 25.73, 0.737 | 0.123, 25.73, 0.742 |
| ctrlB-codec | v5-r3 | 200 | 0.070, 25.66, 0.749 | 0.088, 25.65, 0.755 |
| ctrlB-codec | wam | 200 | 0.079, 25.54, 0.745 | 0.095, 25.61, 0.750 |
| ctrlB-codec | vine-r | 200 | 0.066, 25.64, 0.766 | 0.079, 25.47, 0.764 |

Clean embedding quality d(u,x) medians: f5-r2 LPIPS 0.034629810601472855, PSNR 45.06434379775574, SSIM 0.9822208878215759 (n 200); v5-r3 LPIPS 0.029733660630881786, PSNR 36.4747030912894, SSIM 0.9760608124425783 (n 200); wam LPIPS 0.032812610268592834, PSNR 38.43948824538688, SSIM 0.9872414408792347 (n 200); vine-r LPIPS 0.007819103309884667, PSNR 34.7113612773453, SSIM 0.9954171016460198 (n 200)

## Accounting

```
{
 "sources": 200,
 "planned": 200,
 "absent_sources": 0,
 "c0": {
  "R0-0.1|ok": 591,
  "R0-0.1|safety_blocked": 9,
  "R0-0.2|ok": 593,
  "R0-0.2|safety_blocked": 7,
  "R0-0.4|ok": 596,
  "R0-0.4|safety_blocked": 4,
  "R1-0.1|ok": 600,
  "R1-0.2|ok": 600,
  "R1-0.4|ok": 600,
  "K3-0.2|ok": 600
 },
 "outcome": {
  "K3-0.2|ok": 2400,
  "R0-0.1|ok": 2356,
  "R0-0.1|safety_blocked": 44,
  "R0-0.2|ok": 2360,
  "R0-0.2|safety_blocked": 40,
  "R0-0.4|ok": 2370,
  "R0-0.4|safety_blocked": 30,
  "R1-0.1|ok": 2400,
  "R1-0.2|ok": 2400,
  "R1-0.4|ok": 2400,
  "ctrlB-codec|ok": 1000
 },
 "detect": {
  "f5-r2|ok": 9148,
  "v5-r3|ok": 9158,
  "wam|ok": 9157,
  "vine-r|ok": 9143
 },
 "quality": {
  "ok": 21866
 },
 "forecasts": {
  "ok": 1780,
  "none": 20
 }
}
```
