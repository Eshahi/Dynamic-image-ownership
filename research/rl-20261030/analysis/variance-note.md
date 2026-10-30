# WP3 source/seed variance and conditional sample cost

**Status:** descriptive analysis of saved development numbers only. `PHASE_B_JOURNALS=off`. No images, original journals, F6 outcomes, or held-out per-source records were opened. No policy was fit or evaluated.

## Evidence and meanings

- **MEASURED:** `dev-records.jsonl`, SHA-256 `61cd39060c8ffc70c2f7d13fd1a3289b25c7ad1a3d4d473e8a0453f2bcfcab55`; 11760 rows. Extraction provenance and missing statuses are in `data-inventory.json`.
- **SOURCE:** `../context/wp1-reader-semantics.md`: internal margin is decoded normalized correlation minus decoded threshold; external margin is matching bits minus its threshold. The generic branch-selected margin is not substituted. Binary success is content-compatible C for F5/v5 and message presence for WAM/VINE-R; these endpoints differ.
- **SOURCE:** `../BRIEF.md`, WP3 and compute anchors at lines 97-102. Cost figures below reuse those supplied measurements and unmeasured F6 anchors; they are not new timing observations.
- The cohorts reuse the same 60 development sources under different kernels/conditions and are analyzed separately. Clean rows have no seed replication and are excluded from the two-way decomposition.

## Decomposition

**DERIVED:** with N complete sources and r=3 seeds, SS_source=r sum_i(mean_i-grand)^2; SS_seed=N sum_j(mean_j-grand)^2; SS_residual=sum_ij(y_ij-mean_i-mean_j+grand)^2. The sum equals total SS. Degrees of freedom are N-1, 2 and 2(N-1). Random-component method-of-moments estimates are (MS_source-MS_residual)/3, (MS_seed-MS_residual)/N and MS_residual. Their random-effects interpretation requires independent exchangeable source/seed effects and homogeneous residual variance. The JSON retains negative estimates and separately clips them to zero for descriptive fractions; clipping does not create an unbiased estimator.

The table shows fixed SS fractions, not population variance fractions. Residual includes source-by-seed interaction and noise: one observation per source/seed cannot separate them. Pooled within-source variance is sum_i,j(y_ij-mean_i)^2/[N(3-1)] = (SS_seed+SS_residual)/[2N]. No p-values are warranted from three fixed seeds alone.

| Cohort | Cell | Arm | Complete / total | Missing | Mean margin | Source SS % | Seed SS % | Residual SS % | Within-source variance |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| phase_a | R0-0.1 | f5-r2 | 59/60 | 1 | 5.7944 | 99.7 | 0.1 | 0.2 | 0.0177 |
| phase_a | R0-0.1 | v5-r3 | 60/60 | 0 | 2.7550 | 98.6 | 0.1 | 1.3 | 0.1418 |
| phase_a | R0-0.1 | vine-r | 59/60 | 1 | 25.6949 | 89.8 | 0.1 | 10.1 | 3.3616 |
| phase_a | R0-0.1 | wam | 51/60 | 14 | 1.2288 | 86.7 | 0.3 | 13.1 | 1.7843 |
| phase_a | R0-0.2 | f5-r2 | 58/60 | 2 | 4.7441 | 99.2 | 0.3 | 0.6 | 0.0628 |
| phase_a | R0-0.2 | v5-r3 | 59/60 | 1 | 0.2852 | 96.2 | 0.3 | 3.4 | 0.3008 |
| phase_a | R0-0.2 | vine-r | 58/60 | 2 | 18.1839 | 83.8 | 0.5 | 15.7 | 11.3506 |
| phase_a | R0-0.2 | wam | 30/60 | 59 | -0.4000 | 66.5 | 0.4 | 33.1 | 5.6889 |
| phase_a | R0-0.4 | f5-r2 | 58/60 | 2 | 2.1363 | 97.0 | 0.9 | 2.1 | 0.2282 |
| phase_a | R0-0.4 | v5-r3 | 58/60 | 2 | -2.4876 | 80.2 | 9.1 | 10.7 | 0.5578 |
| phase_a | R0-0.4 | vine-r | 59/60 | 1 | 4.0791 | 71.2 | 3.8 | 24.9 | 18.1864 |
| phase_a | R0-0.4 | wam | 2/60 | 146 | -6.0000 | 96.6 | 1.4 | 1.9 | 2.3333 |
| phase_a | R1-0.1 | f5-r2 | 60/60 | 0 | -2.7537 | 91.9 | 1.6 | 6.5 | 0.1367 |
| phase_a | R1-0.1 | v5-r3 | 60/60 | 0 | 1.5833 | 95.1 | 1.1 | 3.8 | 0.1804 |
| phase_a | R1-0.1 | vine-r | 60/60 | 0 | 27.7333 | 85.1 | 0.0 | 14.9 | 2.9278 |
| phase_a | R1-0.1 | wam | 54/60 | 12 | 2.7716 | 83.7 | 0.3 | 15.9 | 1.9938 |
| phase_a | R1-0.2 | f5-r2 | 60/60 | 0 | -3.9090 | 86.2 | 3.1 | 10.7 | 0.1560 |
| phase_a | R1-0.2 | v5-r3 | 60/60 | 0 | -1.0586 | 86.4 | 2.7 | 10.9 | 0.3034 |
| phase_a | R1-0.2 | vine-r | 60/60 | 0 | 19.7222 | 91.2 | 0.2 | 8.6 | 7.4778 |
| phase_a | R1-0.2 | wam | 3/60 | 136 | -0.8889 | 66.2 | 27.6 | 6.2 | 4.6667 |
| phase_a | R1-0.4 | f5-r2 | 60/60 | 0 | -4.4127 | 81.1 | 1.9 | 17.0 | 0.1825 |
| phase_a | R1-0.4 | v5-r3 | 60/60 | 0 | -3.0774 | 57.2 | 14.9 | 27.9 | 0.4265 |
| phase_a | R1-0.4 | vine-r | 60/60 | 0 | 4.2444 | 75.9 | 0.0 | 24.1 | 21.9167 |
| phase_a | R1-0.4 | wam | 1/60 | 166 | NA | NA | NA | NA | NA |
| stage2_union | R0-0.1 | f5-r2 | 59/60 | 1 | 5.7944 | 99.7 | 0.1 | 0.2 | 0.0178 |
| stage2_union | R0-0.1 | v5-r3 | 60/60 | 0 | 2.7563 | 98.6 | 0.1 | 1.3 | 0.1417 |
| stage2_union | R0-0.1 | vine-r | 60/60 | 0 | 25.7833 | 89.5 | 0.1 | 10.4 | 3.4389 |
| stage2_union | R0-0.1 | wam | 50/60 | 15 | 1.1667 | 86.6 | 0.3 | 13.1 | 1.8267 |
| stage2_union | R0-0.2 | f5-r2 | 58/60 | 3 | 4.7447 | 99.2 | 0.3 | 0.6 | 0.0624 |
| stage2_union | R0-0.2 | v5-r3 | 59/60 | 1 | 0.2851 | 96.2 | 0.3 | 3.5 | 0.3025 |
| stage2_union | R0-0.2 | vine-r | 58/60 | 2 | 18.2011 | 84.4 | 0.5 | 15.1 | 10.7816 |
| stage2_union | R0-0.2 | wam | 30/60 | 60 | -0.4000 | 64.4 | 0.5 | 35.1 | 5.8778 |
| stage2_union | R0-0.4 | f5-r2 | 58/60 | 2 | 2.1367 | 97.0 | 0.9 | 2.1 | 0.2281 |
| stage2_union | R0-0.4 | v5-r3 | 58/60 | 2 | -2.4868 | 80.1 | 9.1 | 10.7 | 0.5579 |
| stage2_union | R0-0.4 | vine-r | 59/60 | 1 | 4.0452 | 70.7 | 3.6 | 25.8 | 19.1299 |
| stage2_union | R0-0.4 | wam | 2/60 | 145 | -6.0000 | 96.6 | 1.4 | 1.9 | 2.3333 |
| stage2_union | R1-0.1 | f5-r2 | 60/60 | 0 | -2.7531 | 92.0 | 1.6 | 6.4 | 0.1355 |
| stage2_union | R1-0.1 | v5-r3 | 60/60 | 0 | 1.5845 | 95.1 | 1.1 | 3.8 | 0.1796 |
| stage2_union | R1-0.1 | vine-r | 60/60 | 0 | 27.7000 | 84.8 | 0.1 | 15.2 | 3.0167 |
| stage2_union | R1-0.1 | wam | 54/60 | 11 | 2.7716 | 85.5 | 0.3 | 14.2 | 1.8395 |
| stage2_union | R1-0.2 | f5-r2 | 60/60 | 0 | -3.9109 | 86.3 | 3.2 | 10.6 | 0.1567 |
| stage2_union | R1-0.2 | v5-r3 | 60/60 | 0 | -1.0658 | 86.1 | 2.7 | 11.2 | 0.3110 |
| stage2_union | R1-0.2 | vine-r | 60/60 | 0 | 19.7111 | 90.8 | 0.1 | 9.1 | 7.8222 |
| stage2_union | R1-0.2 | wam | 3/60 | 136 | -1.1111 | 82.2 | 9.5 | 8.4 | 3.0000 |
| stage2_union | R1-0.4 | f5-r2 | 60/60 | 0 | -4.4112 | 81.8 | 1.8 | 16.5 | 0.1779 |
| stage2_union | R1-0.4 | v5-r3 | 60/60 | 0 | -3.0786 | 56.7 | 15.1 | 28.2 | 0.4324 |
| stage2_union | R1-0.4 | vine-r | 60/60 | 0 | 4.1333 | 77.0 | 0.0 | 23.0 | 20.8889 |
| stage2_union | R1-0.4 | wam | 1/60 | 166 | NA | NA | NA | NA | NA |
| stage2_union | R1-mode-0.2 | f5-r2 | 60/60 | 0 | -3.9179 | 82.5 | 2.9 | 14.6 | 0.1764 |
| stage2_union | R1-mode-0.2 | v5-r3 | 60/60 | 0 | -1.1935 | 75.5 | 11.9 | 12.6 | 0.5290 |
| stage2_union | R1-mode-0.2 | vine-r | 60/60 | 0 | 20.1333 | 88.6 | 1.5 | 10.0 | 9.0778 |
| stage2_union | R1-mode-0.2 | wam | 4/60 | 138 | -2.0833 | 78.3 | 7.3 | 14.4 | 8.5833 |
| stage2_union | R1-rinse-0.1 | f5-r2 | 60/60 | 0 | -4.1550 | 88.0 | 0.8 | 11.2 | 0.1285 |
| stage2_union | R1-rinse-0.1 | v5-r3 | 60/60 | 0 | -1.8235 | 87.2 | 2.9 | 9.9 | 0.3224 |
| stage2_union | R1-rinse-0.1 | vine-r | 60/60 | 0 | 21.4778 | 92.9 | 0.7 | 6.5 | 6.9222 |
| stage2_union | R1-rinse-0.1 | wam | 20/60 | 96 | 2.2667 | 68.5 | 2.2 | 29.3 | 3.0667 |
| stage2_union | R1-smooth-0.2 | f5-r2 | 60/60 | 0 | -4.1681 | 83.4 | 1.3 | 15.3 | 0.1739 |
| stage2_union | R1-smooth-0.2 | v5-r3 | 60/60 | 0 | -1.4004 | 73.7 | 12.4 | 13.9 | 0.5699 |
| stage2_union | R1-smooth-0.2 | vine-r | 60/60 | 0 | 19.9000 | 86.7 | 0.7 | 12.7 | 9.4944 |
| stage2_union | R1-smooth-0.2 | wam | 1/60 | 155 | NA | NA | NA | NA | NA |
| stage2_union | R3-0.2 | f5-r2 | 60/60 | 0 | -2.0495 | 96.5 | 0.3 | 3.3 | 0.1488 |
| stage2_union | R3-0.2 | v5-r3 | 60/60 | 0 | 4.0194 | 98.3 | 0.5 | 1.3 | 0.1387 |
| stage2_union | R3-0.2 | vine-r | 60/60 | 0 | 29.2222 | 66.9 | 1.2 | 31.9 | 1.5167 |
| stage2_union | R3-0.2 | wam | 53/60 | 14 | 2.6352 | 82.3 | 0.1 | 17.6 | 2.3962 |

**MEASURED missingness:** WAM margins are absent on 166/180 rows at R1 .4 in each cohort and 155/180 rows at stage2 R1-smooth .2; each has only one complete source and is not decomposed. Numeric margin availability is therefore not the same as successful row status. WAM presence can remain defined when a matched-bit score is absent. Other incomplete sources and their numeric missing counts appear in the table and JSON.

**MEASURED:** across the normalized WAM rows, 1,460 absent numeric margins coexist with an observed presence=False; nine further absent margins accompany unresolved calls. Thus no numeric score is not the same as no binary outcome. **SOURCE, reported by the integration lead after its code inspection:** `scripts/encoder_transfer_test.py:62-65` maps decoded=None to matches=None and present=False, and `scripts/journal_wam_probe.py:90` produces decoded=None for an empty positive mask. This agent did not separately open those code files. There is no justified arbitrary numeric floor to impute for this structural case; complete-case margin summaries select the subset with a decoded score.

**JUDGMENT:** large source SS shows heterogeneity of retained outcomes, not that a feature available before marking predicts it, not that the best action changes by source, and not that a new policy can improve it. Large residual need not be pure seed noise. Missing outcomes are excluded only by complete-source restriction and are counted; no failure was silently converted to a numeric margin. Complete-case statistics can be biased if missingness depends on difficulty.

## Simultaneous ranking plans

**DERIVED, conditional guarantee:** assume K fixed options, independently sampled rounds, rewards each having range width at most B, and minimum true gap Delta. For best-option identification M=K-1; for all ranks M=K(K-1)/2. For each required pair, differences lie in a range of width at most 2B; Hoeffding plus a union bound gives n >= 2 B^2 log(M/0.05)/Delta^2 rounds per option. Total reward evaluations = K*n. This is a 95% simultaneous probability-of-error bound under those assumptions; it does not need the measured variance. The internal conservative range is 2 sqrt(320), binary range1, external matched-bit range equal to payload length. Threshold shifts do not change width when fixed per option.

**DERIVED, plug-in approximation only:** n >= z_(1-0.05/M)^2 Var(D)/Delta^2. Independent equal-variance future options are illustrated with Var(D)=2v using each retained arm/cell within-source variance v. The normal approximation, fixed-arm-to-new-option transfer, seed exchangeability and ignoring variance uncertainty are substantive assumptions. With three seeds, rare binary failures or a small mean gap make this especially fragile; zero empirical variance is no certificate of a constant future reward. Gap sensitivity and full ordering are in the JSON: internal margins .25/.5/1, binary .02/.05/.1, external matching bits 1/2/5.

All table n below identify the best option, at nominal 95% simultaneous confidence. Every rollout/cost table is **per one source**, using pooled within-source variance only as a homogeneous-variance approximation. A full 60-source design multiplies those totals by 60, with 60*K candidate marks when marks are cached. These totals do not estimate fresh-source generalization. Reusing the three saved seeds does not provide additional independent rounds.

| Cohort | Cell | Arm | Reward / gap | K | Gaussian n/option | Hoeffding n/option | Gaussian total rollouts | Existing carrier hours / USD | F5 candidates cached hours / USD |
|---|---|---|---|---:|---:|---:|---:|---|---|
| phase_a | R1-0.2 | f5-r2 | margin / 0.5 | 8 | 8 | 50603 | 64 | 0.04–0.06 / $0.02–0.04 | 0.31–0.34 / $0.17–0.18 |
| phase_a | R1-0.2 | f5-r2 | margin / 0.5 | 64 | 13 | 73102 | 832 | 0.51–0.84 / $0.28–0.46 | 2.68–3.01 / $1.47–1.66 |
| phase_a | R1-0.2 | f5-r2 | margin / 0.5 | 1024 | 19 | 101645 | 19456 | 11.84–19.62 / $6.52–10.81 | 46.54–54.32 / $25.64–29.93 |
| phase_a | R1-0.2 | f5-r2 | success / 0.05 | 8 | 1 [zero variance] | 3954 | 8 | 0.00–0.01 / $0.00–0.00 | 0.28–0.28 / $0.15–0.15 |
| phase_a | R1-0.2 | f5-r2 | success / 0.05 | 64 | 1 [zero variance] | 5712 | 64 | 0.04–0.06 / $0.02–0.04 | 2.21–2.23 / $1.22–1.23 |
| phase_a | R1-0.2 | f5-r2 | success / 0.05 | 1024 | 1 [zero variance] | 7941 | 1024 | 0.62–1.03 / $0.34–0.57 | 35.33–35.73 / $19.46–19.69 |
| stage2_union | R0-0.2 | f5-r2 | margin / 0.5 | 8 | 3 | 50603 | 24 | 0.01–0.02 / $0.01–0.01 | 0.29–0.30 / $0.16–0.16 |
| stage2_union | R0-0.2 | f5-r2 | margin / 0.5 | 64 | 5 | 73102 | 320 | 0.19–0.32 / $0.11–0.18 | 2.36–2.49 / $1.30–1.37 |
| stage2_union | R0-0.2 | f5-r2 | margin / 0.5 | 1024 | 8 | 101645 | 8192 | 4.98–8.26 / $2.75–4.55 | 39.69–42.96 / $21.87–23.67 |
| stage2_union | R0-0.2 | f5-r2 | success / 0.05 | 8 | 56 | 3954 | 448 | 0.27–0.45 / $0.15–0.25 | 0.54–0.72 / $0.30–0.40 |
| stage2_union | R0-0.2 | f5-r2 | success / 0.05 | 64 | 92 | 5712 | 5888 | 3.58–5.94 / $1.97–3.27 | 5.75–8.11 / $3.17–4.47 |
| stage2_union | R0-0.2 | f5-r2 | success / 0.05 | 1024 | 140 | 7941 | 143360 | 87.21–144.55 / $48.05–79.65 | 121.91–179.26 / $67.17–98.77 |
| stage2_union | R1-0.2 | f5-r2 | margin / 0.5 | 8 | 8 | 50603 | 64 | 0.04–0.06 / $0.02–0.04 | 0.31–0.34 / $0.17–0.18 |
| stage2_union | R1-0.2 | f5-r2 | margin / 0.5 | 64 | 13 | 73102 | 832 | 0.51–0.84 / $0.28–0.46 | 2.68–3.01 / $1.47–1.66 |
| stage2_union | R1-0.2 | f5-r2 | margin / 0.5 | 1024 | 20 | 101645 | 20480 | 12.46–20.65 / $6.86–11.38 | 47.16–55.35 / $25.99–30.50 |
| stage2_union | R1-0.2 | f5-r2 | success / 0.05 | 8 | 1 [zero variance] | 3954 | 8 | 0.00–0.01 / $0.00–0.00 | 0.28–0.28 / $0.15–0.15 |
| stage2_union | R1-0.2 | f5-r2 | success / 0.05 | 64 | 1 [zero variance] | 5712 | 64 | 0.04–0.06 / $0.02–0.04 | 2.21–2.23 / $1.22–1.23 |
| stage2_union | R1-0.2 | f5-r2 | success / 0.05 | 1024 | 1 [zero variance] | 7941 | 1024 | 0.62–1.03 / $0.34–0.57 | 35.33–35.73 / $19.46–19.69 |

Costs use 2.19–3.63 seconds per regeneration/reader/quality rollout, 124.19–125.63 seconds if each rollout rewrites an F5 mark, and $0.551/device-hour. The 732-second F5 mark figure is observed shard latency with six simultaneous shards; 122 seconds is its approximate device-equivalent amortization, not serial mark latency. Throughput and per-request latency are distinct. Reader/quality overheads and native regeneration timers may have different concurrency scopes; additive costs are planning approximations.

For K fixed candidate marks reused over n seeds, the per-source cost is **K*w + K*n*feedback**, with w approximately122 device-equivalent seconds for F5. Across 60 sources it is 60 times that quantity. If each continuous action changes the mark, the per-source cost instead becomes K*n*(w+feedback) (or total policy rollouts times w+feedback); that is a separate rewrite-every-rollout scenario in the JSON. Existing-carrier scenarios exclude already-paid writing entirely. F6 writing is unmeasured: conditional costs use w=361–723 seconds; rewriting every rollout gives 363.19–726.63 seconds total. No observed F6 cost or result is claimed. JSON provides cached-mark and rewrite-every-rollout scenarios for every selected planning example.

## Paired common-random-number comparisons

**MEASURED/DESCRIPTIVE:** pair the retained arms on the same source and prescribed seed within each cohort; recompute complete-source differences and the within-source variance of those differences. The JSON contains every pair and the ratio to Var(A)+Var(B) on exactly the same retained complete sources. Ratio below one suggests variance reduction for these particular paired outcomes; ratio above one suggests an increase. Same numeric seeds alone do not establish identical random draws across models or this benefit for new actions. F5/v5 C and normalized-correlation margins can be compared; C-versus-presence and different external payloads cannot be called an ownership-efficacy ranking.

| Cohort | Cell | Pair | Metric | Paired variance | Independent variance | Ratio |
|---|---|---|---|---:|---:|---:|
| phase_a | R0-0.2 | F5 − v5 | success | 0.0575 | 0.0575 | 1.0000 |
| phase_a | R0-0.2 | F5 − v5 | margin | 0.2973 | 0.3665 | 0.8111 |
| phase_a | R1-0.2 | F5 − v5 | success | 0.0778 | 0.0778 | 1.0000 |
| phase_a | R1-0.2 | F5 − v5 | margin | 0.4804 | 0.4595 | 1.0457 |
| stage2_union | R0-0.2 | F5 − v5 | success | 0.0575 | 0.0575 | 1.0000 |
| stage2_union | R0-0.2 | F5 − v5 | margin | 0.2987 | 0.3679 | 0.8117 |
| stage2_union | R1-0.2 | F5 − v5 | success | 0.0778 | 0.0778 | 1.0000 |
| stage2_union | R1-0.2 | F5 − v5 | margin | 0.4931 | 0.4677 | 1.0542 |

## Continuous-policy score-function gradients

**Unidentified from these logs:** Var[(R-b) grad_theta log pi(a|x)] requires sampled actions, their policy probabilities/log gradients, their association with rewards and the baseline. Fixed-arm outcomes supply none of these, so there is no measured policy-gradient variance, return estimate, sample complexity or improvement probability.

**DERIVED scale-conditional illustration:** let a=theta+sigma*z, z~N(0,I_d). Suppose an oracle baseline removes the mean and the remaining additive reward noise epsilon is independent of z, with variance v equal to a retained fixed-arm within-source variance. For g=epsilon*z/sigma, trace Cov(mean_n g)=d*v/(n*sigma^2), hence noise-only trace RMS <=tau requires n >= d*v/(sigma^2*tau^2). This is neither the complete gradient variance nor the gradient signal, and ignores action-dependent reward, nonlinear parameterization, correlated trajectory credit, baseline-estimation error and all learning iterations. Changing parameter/action units changes sigma and tau. Under a general policy the corresponding independent-noise term is v*trace(Fisher information)/n.

The JSON illustrates d=8/64/1024, sigma=.1/1, and tau=.1 correlation-gradient units or .01 binary-gradient units, for F5 R0 .2 and R1 .2. Each entry is labelled noise-only conditional and converted with the same costs. In particular a binary floor can yield v=0 and a useless zero-noise expression while also supplying no usable gradient signal.

## Reproduction and checks

Exact command (PowerShell, from the worktree):

```powershell
& 'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/venv/Scripts/python.exe' -I 'research/rl-20261030/analysis/variance.py'
```

The script asserts normalized-record count/unique source-cell-seed-arm keys, three-seed design, SS additivity and equivalence of the two within-source-variance calculations. The script writes only `variance-results.json` and this note. No dependency outside Python stdlib is imported.
