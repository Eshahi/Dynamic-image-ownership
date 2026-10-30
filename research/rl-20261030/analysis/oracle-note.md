# Retrospective arm-selection ceilings

DERIVED from `dev-records.jsonl` (hash in `oracle-results.json`); script `oracle.py`. Numeric development analysis only. No new policy tested.

## Definition and limitations

- One success is source majority: at least two of seeds 12/13/14. Conservative missing endpoints count as non-success; optimistic assigns them success; complete-case removes a source from the whole suite when any selected arm/cell/seed endpoint is missing. Complete-case denominators are displayed and differ by endpoint pool.
- Per-cell fixed arm and per-source oracle both know the cell. The unknown-cell average oracle selects one arm per source to maximize total successes across all cells. The unknown-cell worst-family oracle selects one arm per source to maximize the minimum aggregate family success fraction, using exact integer-vector Pareto dynamic programming; average is the tie-break. These are retrospective portfolios, not trainable effects. No arm changes after the unknown cell is revealed. The clairvoyant oracle may change arm for every source and cell.
- Native R0/R1 each have three strengths; R3 has one. Average weights cells equally; minimax weights family rates equally. Each additional T3 variant is a distinct group for the additional-only minimax, not an independently trained encoder family. Phase A has only six native cells; R3 and additional T3 are absent. Stage2 union already contains Stage2a and is not duplicated. Both cohorts reuse the same 60 sources and are not independent replications.
- C/J compare only F5/v5. P compares WAM/VINE message presence, not content binding. The heterogeneous C-or-P ceiling mixes different tasks and is explicitly non-comparable as security performance. F5/v5 carry q32+h32; WAM carries 32 bits and VINE 100 bits with different readers. J tests exact original q and content compatibility, not h recovery. Payload lengths do not imply equal usable capacity.
- Strict clean quality is PSNR >35, SSIM >0.9, LPIPS <0.1. Stage2 clean pass counts: F5 60/60, v5 60/60, WAM 58/60, VINE 31/60. Phase A borrows these checks from the same marked inputs; it has no independently measured clean quality in this normalized file. A quality-constrained source oracle can use only that source’s eligible arms; a fixed arm must pass on all 60 sources. Thus external-only P has no globally eligible fixed arm, not a zero-success fixed arm. Sources with no eligible arm stay in the denominator and yield zero.
- These are optimistic selection ceilings for the finite observed arm set and observed cells, not bounds over unseen methods/encoders. Outcomes were not randomized for a policy comparison. Clean margins, embedding reports and quality require producing/reading each candidate and incur compute; no equal-budget or free-feature claim is made. Missing/failure records remain in the input and primary denominator.

## Main implications

DERIVED: In Stage2 native6+R3, internal C is 196/420 for the best single fixed arm (v5), 209/420 for an average-optimized per-source portfolio chosen before the cell is known, and 276/420 for the source-and-cell clairvoyant oracle. A simpler cell-known fixed-arm selector already achieves 275/420. The within-cell personalization headroom is therefore only one source majority (R0 .2: 57 to 58); most clairvoyant improvement is knowing the regenerator, not identifying special sources. C worst-family performance stays 62/180 = 0.344444 even for the exact minimax source portfolio.

DERIVED: Internal J in the same seven cells is 93/420 fixed, 108/420 for the unknown-cell average portfolio and 132/420 clairvoyant; the cell-known fixed-arm baseline is 130/420. Worst-family J remains 6/180 = 0.033333. Additional T3 has C 14/180 and J 0/180 with no source-oracle improvement. These findings do not establish that a policy can learn the retrospective arm allocation.

DERIVED: WAM/VINE P has no unconstrained source-oracle gain beyond VINE: 392/420 on the seven native cells. Its quality-constrained source oracle is 262/420; neither external arm meets strict clean quality on all 60 sources, so there is no globally eligible fixed P comparator. Combining external P with internal C produces a different, heterogeneous task and cannot support a content-binding claim.

## Per-cell conservative counts

All denominators are 60; F5/v5 columns are C or J, WAM/VINE columns are P. Quality oracle uses per-source eligibility. `none` means no globally eligible fixed arm.

| Cohort | Cell | Endpoint pool | Arm counts | Fixed | Oracle | Gain | Quality fixed | Quality oracle |
|---|---|---|---|---:|---:|---:|---:|---:|
| stage2_union | R0-0.1 | C | f5-r2:60, v5-r3:47 | 60 | 60 | 0 | 60 | 60 |
| stage2_union | R0-0.2 | C | f5-r2:57, v5-r3:27 | 57 | 58 | 1 | 57 | 58 |
| stage2_union | R0-0.4 | C | f5-r2:39, v5-r3:3 | 39 | 39 | 0 | 39 | 39 |
| stage2_union | R1-0.1 | C | f5-r2:0, v5-r3:50 | 50 | 50 | 0 | 50 | 50 |
| stage2_union | R1-0.2 | C | f5-r2:0, v5-r3:12 | 12 | 12 | 0 | 12 | 12 |
| stage2_union | R1-0.4 | C | f5-r2:0, v5-r3:0 | 0 | 0 | 0 | 0 | 0 |
| stage2_union | R3-0.2 | C | f5-r2:5, v5-r3:57 | 57 | 57 | 0 | 57 | 57 |
| stage2_union | R0-0.1 | J | f5-r2:41, v5-r3:23 | 41 | 43 | 2 | 41 | 43 |
| stage2_union | R0-0.2 | J | f5-r2:38, v5-r3:6 | 38 | 38 | 0 | 38 | 38 |
| stage2_union | R0-0.4 | J | f5-r2:14, v5-r3:0 | 14 | 14 | 0 | 14 | 14 |
| stage2_union | R1-0.1 | J | f5-r2:0, v5-r3:6 | 6 | 6 | 0 | 6 | 6 |
| stage2_union | R1-0.2 | J | f5-r2:0, v5-r3:0 | 0 | 0 | 0 | 0 | 0 |
| stage2_union | R1-0.4 | J | f5-r2:0, v5-r3:0 | 0 | 0 | 0 | 0 | 0 |
| stage2_union | R3-0.2 | J | f5-r2:0, v5-r3:31 | 31 | 31 | 0 | 31 | 31 |
| stage2_union | R0-0.1 | P | wam:42, vine-r:60 | 60 | 60 | 0 | none | 51 |
| stage2_union | R0-0.2 | P | wam:18, vine-r:60 | 60 | 60 | 0 | none | 41 |
| stage2_union | R0-0.4 | P | wam:1, vine-r:47 | 47 | 47 | 0 | none | 20 |
| stage2_union | R1-0.1 | P | wam:48, vine-r:60 | 60 | 60 | 0 | none | 53 |
| stage2_union | R1-0.2 | P | wam:2, vine-r:60 | 60 | 60 | 0 | none | 32 |
| stage2_union | R1-0.4 | P | wam:0, vine-r:45 | 45 | 45 | 0 | none | 18 |
| stage2_union | R3-0.2 | P | wam:44, vine-r:60 | 60 | 60 | 0 | none | 47 |
| stage2_union | R0-0.1 | heterogeneous_C_or_P | f5-r2:60, v5-r3:47, wam:42, vine-r:60 | 60 | 60 | 0 | 60 | 60 |
| stage2_union | R0-0.2 | heterogeneous_C_or_P | f5-r2:57, v5-r3:27, wam:18, vine-r:60 | 60 | 60 | 0 | 57 | 60 |
| stage2_union | R0-0.4 | heterogeneous_C_or_P | f5-r2:39, v5-r3:3, wam:1, vine-r:47 | 47 | 53 | 6 | 39 | 44 |
| stage2_union | R1-0.1 | heterogeneous_C_or_P | f5-r2:0, v5-r3:50, wam:48, vine-r:60 | 60 | 60 | 0 | 50 | 59 |
| stage2_union | R1-0.2 | heterogeneous_C_or_P | f5-r2:0, v5-r3:12, wam:2, vine-r:60 | 60 | 60 | 0 | 12 | 39 |
| stage2_union | R1-0.4 | heterogeneous_C_or_P | f5-r2:0, v5-r3:0, wam:0, vine-r:45 | 45 | 45 | 0 | 0 | 18 |
| stage2_union | R3-0.2 | heterogeneous_C_or_P | f5-r2:5, v5-r3:57, wam:44, vine-r:60 | 60 | 60 | 0 | 57 | 59 |
| stage2_union | R1-mode-0.2 | C | f5-r2:0, v5-r3:6 | 6 | 6 | 0 | 6 | 6 |
| stage2_union | R1-rinse-0.1 | C | f5-r2:0, v5-r3:4 | 4 | 4 | 0 | 4 | 4 |
| stage2_union | R1-smooth-0.2 | C | f5-r2:0, v5-r3:4 | 4 | 4 | 0 | 4 | 4 |
| stage2_union | R1-mode-0.2 | J | f5-r2:0, v5-r3:0 | 0 | 0 | 0 | 0 | 0 |
| stage2_union | R1-rinse-0.1 | J | f5-r2:0, v5-r3:0 | 0 | 0 | 0 | 0 | 0 |
| stage2_union | R1-smooth-0.2 | J | f5-r2:0, v5-r3:0 | 0 | 0 | 0 | 0 | 0 |
| stage2_union | R1-mode-0.2 | P | wam:2, vine-r:60 | 60 | 60 | 0 | none | 32 |
| stage2_union | R1-rinse-0.1 | P | wam:21, vine-r:59 | 59 | 59 | 0 | none | 41 |
| stage2_union | R1-smooth-0.2 | P | wam:0, vine-r:60 | 60 | 60 | 0 | none | 31 |
| stage2_union | R1-mode-0.2 | heterogeneous_C_or_P | f5-r2:0, v5-r3:6, wam:2, vine-r:60 | 60 | 60 | 0 | 6 | 35 |
| stage2_union | R1-rinse-0.1 | heterogeneous_C_or_P | f5-r2:0, v5-r3:4, wam:21, vine-r:59 | 59 | 59 | 0 | 4 | 42 |
| stage2_union | R1-smooth-0.2 | heterogeneous_C_or_P | f5-r2:0, v5-r3:4, wam:0, vine-r:60 | 60 | 60 | 0 | 4 | 33 |
| phase_a | R0-0.1 | C | f5-r2:60, v5-r3:47 | 60 | 60 | 0 | 60 | 60 |
| phase_a | R0-0.2 | C | f5-r2:57, v5-r3:27 | 57 | 58 | 1 | 57 | 58 |
| phase_a | R0-0.4 | C | f5-r2:39, v5-r3:3 | 39 | 39 | 0 | 39 | 39 |
| phase_a | R1-0.1 | C | f5-r2:0, v5-r3:50 | 50 | 50 | 0 | 50 | 50 |
| phase_a | R1-0.2 | C | f5-r2:0, v5-r3:11 | 11 | 11 | 0 | 11 | 11 |
| phase_a | R1-0.4 | C | f5-r2:0, v5-r3:0 | 0 | 0 | 0 | 0 | 0 |
| phase_a | R0-0.1 | J | f5-r2:41, v5-r3:23 | 41 | 43 | 2 | 41 | 43 |
| phase_a | R0-0.2 | J | f5-r2:38, v5-r3:6 | 38 | 38 | 0 | 38 | 38 |
| phase_a | R0-0.4 | J | f5-r2:14, v5-r3:0 | 14 | 14 | 0 | 14 | 14 |
| phase_a | R1-0.1 | J | f5-r2:0, v5-r3:6 | 6 | 6 | 0 | 6 | 6 |
| phase_a | R1-0.2 | J | f5-r2:0, v5-r3:0 | 0 | 0 | 0 | 0 | 0 |
| phase_a | R1-0.4 | J | f5-r2:0, v5-r3:0 | 0 | 0 | 0 | 0 | 0 |
| phase_a | R0-0.1 | P | wam:42, vine-r:60 | 60 | 60 | 0 | none | 51 |
| phase_a | R0-0.2 | P | wam:18, vine-r:60 | 60 | 60 | 0 | none | 41 |
| phase_a | R0-0.4 | P | wam:1, vine-r:47 | 47 | 47 | 0 | none | 20 |
| phase_a | R1-0.1 | P | wam:49, vine-r:60 | 60 | 60 | 0 | none | 53 |
| phase_a | R1-0.2 | P | wam:2, vine-r:60 | 60 | 60 | 0 | none | 32 |
| phase_a | R1-0.4 | P | wam:0, vine-r:45 | 45 | 45 | 0 | none | 18 |
| phase_a | R0-0.1 | heterogeneous_C_or_P | f5-r2:60, v5-r3:47, wam:42, vine-r:60 | 60 | 60 | 0 | 60 | 60 |
| phase_a | R0-0.2 | heterogeneous_C_or_P | f5-r2:57, v5-r3:27, wam:18, vine-r:60 | 60 | 60 | 0 | 57 | 60 |
| phase_a | R0-0.4 | heterogeneous_C_or_P | f5-r2:39, v5-r3:3, wam:1, vine-r:47 | 47 | 53 | 6 | 39 | 44 |
| phase_a | R1-0.1 | heterogeneous_C_or_P | f5-r2:0, v5-r3:50, wam:49, vine-r:60 | 60 | 60 | 0 | 50 | 59 |
| phase_a | R1-0.2 | heterogeneous_C_or_P | f5-r2:0, v5-r3:11, wam:2, vine-r:60 | 60 | 60 | 0 | 11 | 38 |
| phase_a | R1-0.4 | heterogeneous_C_or_P | f5-r2:0, v5-r3:0, wam:0, vine-r:45 | 45 | 45 | 0 | 0 | 18 |

## Across-cell portfolios, conservative

Each average entry is successful source-cell majorities / total source-cell pairs. Each worst-family entry is a fraction. Fixed average and fixed worst-family may select different arms; separate unknown-cell portfolios optimize the two objectives.

| Cohort/suite | Pool | Quality | Best fixed average | Unknown-cell average oracle | Clairvoyant average oracle | Best fixed worst-family | Unknown-cell minimax | Clairvoyant worst-family |
|---|---|---|---|---|---|---|---|---|
| stage2_union/native6 | C | unconstrained | f5-r2: 156/360 | 175/360 | 219/360 | v5-r3: 0.344444 | 0.344444 | 0.344444 |
| stage2_union/native6 | C | quality | f5-r2: 156/360 | 175/360 | 219/360 | v5-r3: 0.344444 | 0.344444 | 0.344444 |
| stage2_union/native6 | J | unconstrained | f5-r2: 93/360 | 98/360 | 101/360 | v5-r3: 0.033333 | 0.033333 | 0.033333 |
| stage2_union/native6 | J | quality | f5-r2: 93/360 | 98/360 | 101/360 | v5-r3: 0.033333 | 0.033333 | 0.033333 |
| stage2_union/native6 | P | unconstrained | vine-r: 332/360 | 332/360 | 332/360 | vine-r: 0.916667 | 0.916667 | 0.916667 |
| stage2_union/native6 | P | quality | none | 215/360 | 215/360 | none | 0.572222 | 0.572222 |
| stage2_union/native6 | heterogeneous_C_or_P | unconstrained | vine-r: 332/360 | 332/360 | 338/360 | vine-r: 0.916667 | 0.916667 | 0.916667 |
| stage2_union/native6 | heterogeneous_C_or_P | quality | f5-r2: 156/360 | 253/360 | 280/360 | v5-r3: 0.344444 | 0.644444 | 0.644444 |
| stage2_union/native6_plus_R3 | C | unconstrained | v5-r3: 196/420 | 209/420 | 276/420 | v5-r3: 0.344444 | 0.344444 | 0.344444 |
| stage2_union/native6_plus_R3 | C | quality | v5-r3: 196/420 | 209/420 | 276/420 | v5-r3: 0.344444 | 0.344444 | 0.344444 |
| stage2_union/native6_plus_R3 | J | unconstrained | f5-r2: 93/420 | 108/420 | 132/420 | v5-r3: 0.033333 | 0.033333 | 0.033333 |
| stage2_union/native6_plus_R3 | J | quality | f5-r2: 93/420 | 108/420 | 132/420 | v5-r3: 0.033333 | 0.033333 | 0.033333 |
| stage2_union/native6_plus_R3 | P | unconstrained | vine-r: 392/420 | 392/420 | 392/420 | vine-r: 0.916667 | 0.916667 | 0.916667 |
| stage2_union/native6_plus_R3 | P | quality | none | 262/420 | 262/420 | none | 0.572222 | 0.572222 |
| stage2_union/native6_plus_R3 | heterogeneous_C_or_P | unconstrained | vine-r: 392/420 | 392/420 | 398/420 | vine-r: 0.916667 | 0.916667 | 0.916667 |
| stage2_union/native6_plus_R3 | heterogeneous_C_or_P | quality | v5-r3: 196/420 | 304/420 | 339/420 | v5-r3: 0.344444 | 0.644444 | 0.644444 |
| stage2_union/additionalT3 | C | unconstrained | v5-r3: 14/180 | 14/180 | 14/180 | v5-r3: 0.066667 | 0.066667 | 0.066667 |
| stage2_union/additionalT3 | C | quality | v5-r3: 14/180 | 14/180 | 14/180 | v5-r3: 0.066667 | 0.066667 | 0.066667 |
| stage2_union/additionalT3 | J | unconstrained | f5-r2: 0/180 | 0/180 | 0/180 | f5-r2: 0.000000 | 0.000000 | 0.000000 |
| stage2_union/additionalT3 | J | quality | f5-r2: 0/180 | 0/180 | 0/180 | f5-r2: 0.000000 | 0.000000 | 0.000000 |
| stage2_union/additionalT3 | P | unconstrained | vine-r: 179/180 | 179/180 | 179/180 | vine-r: 0.983333 | 0.983333 | 0.983333 |
| stage2_union/additionalT3 | P | quality | none | 104/180 | 104/180 | none | 0.516667 | 0.516667 |
| stage2_union/additionalT3 | heterogeneous_C_or_P | unconstrained | vine-r: 179/180 | 179/180 | 179/180 | vine-r: 0.983333 | 0.983333 | 0.983333 |
| stage2_union/additionalT3 | heterogeneous_C_or_P | quality | v5-r3: 14/180 | 110/180 | 110/180 | v5-r3: 0.066667 | 0.550000 | 0.550000 |
| phase_a/native6 | C | unconstrained | f5-r2: 156/360 | 174/360 | 218/360 | v5-r3: 0.338889 | 0.338889 | 0.338889 |
| phase_a/native6 | C | quality | f5-r2: 156/360 | 174/360 | 218/360 | v5-r3: 0.338889 | 0.338889 | 0.338889 |
| phase_a/native6 | J | unconstrained | f5-r2: 93/360 | 98/360 | 101/360 | v5-r3: 0.033333 | 0.033333 | 0.033333 |
| phase_a/native6 | J | quality | f5-r2: 93/360 | 98/360 | 101/360 | v5-r3: 0.033333 | 0.033333 | 0.033333 |
| phase_a/native6 | P | unconstrained | vine-r: 332/360 | 332/360 | 332/360 | vine-r: 0.916667 | 0.916667 | 0.916667 |
| phase_a/native6 | P | quality | none | 215/360 | 215/360 | none | 0.572222 | 0.572222 |
| phase_a/native6 | heterogeneous_C_or_P | unconstrained | vine-r: 332/360 | 332/360 | 338/360 | vine-r: 0.916667 | 0.916667 | 0.916667 |
| phase_a/native6 | heterogeneous_C_or_P | quality | f5-r2: 156/360 | 252/360 | 279/360 | v5-r3: 0.338889 | 0.638889 | 0.638889 |

## Missingness sensitivity

Every endpoint, quality setting, suite, per-cell count, portfolio and selected-arm count is provided for conservative, optimistic and complete-case modes in `oracle-results.json`. Table below summarizes the unconstrained aggregate oracle sensitivity; missing is seed endpoints across the pool, not missing sources.

| Cohort/suite | Pool | Missing | Conservative clairvoyant | Optimistic clairvoyant | Complete sources | Complete clairvoyant |
|---|---|---:|---|---|---:|---|
| stage2_union/native6 | C | 9 | 219/360 | 221/360 | 58 | 215/348 |
| stage2_union/native6 | J | 9 | 101/360 | 102/360 | 58 | 99/348 |
| stage2_union/native6 | P | 8 | 332/360 | 332/360 | 55 | 302/330 |
| stage2_union/native6 | heterogeneous_C_or_P | 17 | 338/360 | 338/360 | 55 | 308/330 |
| stage2_union/native6_plus_R3 | C | 9 | 276/420 | 278/420 | 58 | 270/406 |
| stage2_union/native6_plus_R3 | J | 9 | 132/420 | 133/420 | 58 | 129/406 |
| stage2_union/native6_plus_R3 | P | 8 | 392/420 | 392/420 | 55 | 357/385 |
| stage2_union/native6_plus_R3 | heterogeneous_C_or_P | 17 | 398/420 | 398/420 | 55 | 363/385 |
| stage2_union/additionalT3 | C | 0 | 14/180 | 14/180 | 60 | 14/180 |
| stage2_union/additionalT3 | J | 0 | 0/180 | 0/180 | 60 | 0/180 |
| stage2_union/additionalT3 | P | 0 | 179/180 | 179/180 | 60 | 179/180 |
| stage2_union/additionalT3 | heterogeneous_C_or_P | 0 | 179/180 | 179/180 | 60 | 179/180 |
| phase_a/native6 | C | 8 | 218/360 | 220/360 | 58 | 214/348 |
| phase_a/native6 | J | 8 | 101/360 | 102/360 | 58 | 99/348 |
| phase_a/native6 | P | 8 | 332/360 | 332/360 | 55 | 302/330 |
| phase_a/native6 | heterogeneous_C_or_P | 16 | 338/360 | 338/360 | 55 | 308/330 |
