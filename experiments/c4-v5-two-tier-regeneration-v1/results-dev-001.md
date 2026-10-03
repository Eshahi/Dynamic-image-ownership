# v5 revision-3 development run 001: retained results

Issue #18; draft PR #67. Analyzed 2026-10-03 against the frozen acceptance criteria at `baeb21852b2eef21187a0e6732237c42090389a9`. This report records observations and unmet criteria; it does not accept a technical gate, the method, or the thesis.

**Joint preliminary support is not established.** Clean numerical prerequisites pass. VAE and diffusion strength 0.05 meet the numerical regeneration criterion, but the required independent human assessments are missing. Higher strengths fall below the 9/10 source-group threshold and have incomplete C0 controls. T4 residual scale 0.5 meets its numerical arm criterion; the other active T4 arms have only nine qualifying recipients. T5 component coverage is insufficient (one qualifying same-semantic pair, minimum five).

## Execution and completeness

The authenticated user first approved the exact package, then instructed Codex "خودت اجرا کن" ("Run it yourself"). The latter changes only the launch actor. The original approval and a separate launch addendum remain in MAIN. Codex supervised the official local dispatcher until it exited; there was no rerun, tuning, download, paid/remote compute, or push.

- Run: `c4-v5-two-tier-dev-001`; local NVIDIA GeForce RTX 5070 Ti Laptop GPU; USD 0.
- Runner: 2026-10-03 17:51:29–18:06:48 UTC; exit 1, status `failed`. Worker duration: 895.158 seconds.
- Inventory: 617/617 planned row identities retained; 531 `metrics_complete`, 66 `complete_component_diagnostic`, 20 `failed`; 2124/2204 detector calls. No stage-wide failures.
- Every failed row is a `safety_checker_blocked_output` for source 6012: C0 nine, C1 five, C2 six. No black replacement is counted as an attack success; all missing calls remain in denominators.
- All three runner-declared output hashes and all 531 saved PNG byte hashes match. The 60 completeness audit entries are three flags for each of the 20 blocked rows; no identity/duplicate-call/suspect-provenance discrepancy was found elsewhere.
- The generic preregistered batch helper retains the single batch as failed (zero completed batches), with no significance or superiority conclusion. Its derived completion indicator is 0; this is separate from axis-level descriptive evidence.
- Two independent human assessments of clean quality and regenerated content are **MISSING**. CLIP similarity is not a substitute. No scientific support decision is fabricated.

| Strength | Blocked C0 / 30 | Blocked C1 / 30 | Blocked C2 / 30 |
| --- | --- | --- | --- |
| 0.05 | 0 | 0 | 0 |
| 0.1 | 3 | 1 | 1 |
| 0.2 | 3 | 2 | 2 |
| 0.4 | 3 | 2 | 3 |

All VAE rows completed. Log warnings and failed rows are preserved. The worker log does not retain all expected stage/completion messages; final completeness is established from the runner record and hashed final JSON, not from an assumed log success marker.

## Clean prerequisites

All 12 C1 images changed, returned authoritative saved-suspect `both_match`, and met PSNR > 35, SSIM > 0.9 and LPIPS < 0.1. All 48 clean C0 owner calls and 36 wrong-owner C1 calls completed with `neither_match`; both per-channel found counts are zero. These small controls do not estimate a population FPR. Human visual quality remains unevaluated.

| Source | PSNR dB | SSIM | LPIPS | C1 outcome |
| --- | --- | --- | --- | --- |
| 1675 | 38.3186 | 0.980225 | 0.017020 | both_match |
| 4795 | 37.0054 | 0.981696 | 0.015803 | both_match |
| 6012 | 35.2519 | 0.978623 | 0.010721 | both_match |
| 25394 | 38.9328 | 0.979576 | 0.011275 | both_match |
| 80932 | 36.3399 | 0.973957 | 0.025894 | both_match |
| 109798 | 35.9588 | 0.971902 | 0.018856 | both_match |
| 134882 | 35.2569 | 0.975710 | 0.016566 | both_match |
| 147498 | 40.7105 | 0.979078 | 0.038330 | both_match |
| 177015 | 38.3907 | 0.983337 | 0.013343 | both_match |
| 190676 | 36.9545 | 0.979736 | 0.014486 | both_match |
| 468505 | 37.0336 | 0.980182 | 0.015362 | both_match |
| 499768 | 35.2501 | 0.984228 | 0.013797 | both_match |

| Metric (12 sources) | Mean | Median | Sample SD | Range |
| --- | --- | --- | --- | --- |
| psnr | 37.116965 | 36.979945 | 1.697375 | 35.250062–40.710485 |
| ssim | 0.979021 | 0.979656 | 0.003618 | 0.971902–0.984228 |
| lpips | 0.017621 | 0.015583 | 0.007624 | 0.010721–0.038330 |

## T3 regeneration: primary C1

The source is the all-seed grouping unit. A joint numerical success requires semantic found/content match and CLIP >= 0.90 on every planned seed (one for VAE, three for each diffusion dose). The table uses their intersection, not two separate marginal counts. Missing outputs never become successes. Required human retention is missing for every stratum.

| Stratum | Semantic successes / planned C1 | Semantic all-seed groups / 10 | Joint numerical groups / 10 | C0 alpha complete / planned | C0 found (all owners) |
| --- | --- | --- | --- | --- | --- |
| vae_mode | 10/10 | 10 | 10 | 10/10 | 0 |
| strength_0.05 | 30/30 | 10 | 10 | 30/30 | 0 |
| strength_0.1 | 27/30 | 7 | 7 | 27/30 | 0 |
| strength_0.2 | 18/30 | 3 | 3 | 27/30 | 0 |
| strength_0.4 | 2/30 | 0 | 0 | 27/30 | 0 |

| Stratum | both_match | semantic_only | content_uncertain | content_mismatch | neither_match | Missing C1 |
| --- | --- | --- | --- | --- | --- | --- |
| vae_mode | 0 | 10 | 0 | 0 | 0 | 0 |
| strength_0.05 | 0 | 30 | 0 | 0 | 0 | 0 |
| strength_0.1 | 0 | 27 | 1 | 0 | 1 | 1 |
| strength_0.2 | 0 | 18 | 1 | 0 | 9 | 2 |
| strength_0.4 | 0 | 2 | 0 | 0 | 26 | 2 |

The weaker preregistered **VAE mechanism observation is met**: 10/10 semantic found/content match with all ten paired C0 negative (40/40 owner calls negative). This is an observation on these photographs, not survival support. VAE and 0.05 satisfy the numerical 9/10 rule and complete negatives, with visual evidence still missing. Strengths 0.1, 0.2 and 0.4 fail the numerical group threshold and cannot support a rate claim with their incomplete controls.

C1 rows with CLIP >= 0.90 but no watermark are respectively 0, 0, 1, 9 and 14 for the table strata. These are numerical removal candidates; human-confirmed content retention is not available. No evaluated genuine regenerated C1 is labeled `content_mismatch` (zero observed false copy-paste labels); blocked rows are not evaluated. No favourable dose is selected or pooled.

## Secondary C2 quality–robustness trade-off

All ten C2 clean images returned `both_match`; wrong-owner calls found zero marks. Only sources 25394, 147498 and 177015 meet all three numerical quality thresholds. The seven inadmissible images cannot support survival. C2 remains descriptive and is never substituted for C1.

| Source | PSNR dB | SSIM | LPIPS | Admissible | Outcome |
| --- | --- | --- | --- | --- | --- |
| 6012 | 32.8866 | 0.966442 | 0.019893 | False | both_match |
| 25394 | 35.7998 | 0.966603 | 0.021748 | True | both_match |
| 80932 | 33.0281 | 0.952771 | 0.061312 | False | both_match |
| 109798 | 32.9266 | 0.954803 | 0.034214 | False | both_match |
| 134882 | 32.8974 | 0.964281 | 0.032848 | False | both_match |
| 147498 | 37.7606 | 0.969862 | 0.052009 | True | both_match |
| 177015 | 35.2395 | 0.971514 | 0.031533 | True | both_match |
| 190676 | 33.7406 | 0.967948 | 0.028121 | False | both_match |
| 468505 | 33.8519 | 0.969443 | 0.026249 | False | both_match |
| 499768 | 32.8976 | 0.975299 | 0.026607 | False | both_match |

| Stratum | Semantic successes / planned | Joint groups / 10 | semantic_only | uncertain | neither | Missing |
| --- | --- | --- | --- | --- | --- | --- |
| vae_mode | 10/10 | 10 | 10 | 0 | 0 | 0 |
| strength_0.05 | 30/30 | 10 | 30 | 0 | 0 | 0 |
| strength_0.1 | 29/30 | 9 | 29 | 0 | 0 | 1 |
| strength_0.2 | 25/30 | 6 | 25 | 2 | 1 | 2 |
| strength_0.4 | 6/30 | 0 | 6 | 1 | 20 | 3 |

C2 has zero observed `both_match` or `content_mismatch` after regeneration; paired C0 counts are the same as the C1 table. Human retention remains missing, and the same missing-control caveats apply.

## T4 copy-paste, each arm separately

| Arm | Attempts | Admissible | Delivered | Admissible delivered | Distinct qualifying recipients | Combined both_match | Mismatch given delivery |
| --- | --- | --- | --- | --- | --- | --- | --- |
| clean_donor_residual_0.5 | 20 | 19 | 18 | 17 | 10 | 0 | 14 |
| clean_donor_residual_1.0 | 20 | 17 | 20 | 17 | 9 | 0 | 20 |
| public_projection | 20 | 18 | 20 | 18 | 9 | 0 | 20 |
| unmarked_projection_sham | 20 | 19 | 0 | 0 | 0 | 0 | 0 |

All 320 T4 calls completed across all four binding modes. No-transfer C0 controls are complete and negative; all 80 sham calls across the four modes are negative. Delivery means `none`-mode watermark found; admissibility uses recipient quality. Residual scale 0.5 reaches ten distinct admissible delivered recipients, zero false attribution and complete controls, so its frozen numerical arm rule is met. Residual scale 1 and public projection each reach only nine recipients and remain insufficient for their arm-level support rule. The negative sham is a control, not a delivered attack. All distinct-recipient admissible combined false-attribution counts are zero; this is not a general security guarantee.

## T5 semantic collision

| Frozen label | Pairs / distances available | q <= 6 and H > 6 | Joint near collision | q range | H range |
| --- | --- | --- | --- | --- | --- |
| same | 7/7 | 1 | 0 | 6–14 | 11–19 |
| different | 57/57 | 0 | 0 | 7–17 | 9–22 |
| uncertain | 2/2 | 0 | 0 | 8–8 | 12–16 |

All 66 C0 and C1 pair-distance records exist. All 12 same-instance controls have both distances <= 6. Only 1/7 frozen same-semantic pairs meets q <= 6 and H > 6; minimum five is unmet. Thus component evidence is **inconclusive for insufficient semantic-near coverage**, despite no observed joint near collision. The two uncertain pairs remain separate.

All seven same-semantic projection transfers are admissible and delivered, with 28/28 binding-mode calls complete: combined `content_mismatch` 7/7, combined `both_match` 0/7; semantic-only ablation gives one `both_match`, four mismatches and two uncertain. The transfer subcondition reaches at least five examples, but the failed component-coverage condition prevents T5 end-to-end support. Four distinct recipients do not represent seven independent sources. No cohort expansion or pair replacement was performed.

## Supplementary T1 ordinary processing

| Operation | C1 outcomes (10) | C0 calls | C0 watermark found |
| --- | --- | --- | --- |
| down384 | {"semantic_only": 10} | 40 | 0 |
| jpeg75 | {"both_match": 9, "content_uncertain": 1} | 40 | 0 |

These supplementary rows cannot replace Regeneration, Copy-Paste or Semantic Collision evidence.

## Reproducibility and interpretation limits

Run artifacts and analyses are local in MAIN; paths below are relative to MAIN unless stated otherwise. Original run files remain unchanged. The full descriptive JSON includes n, mean, median, sample SD and range for the available continuous metrics; absent/blocked outputs are recorded separately, not imputed. Repeated seeds and overlapping image pairs are correlated; no inferential confidence interval, significance claim, population FPR or superiority claim is made.

- Run directory: `.thesis-build/v5-study-runs/C4-v5-two-tier-development/c4-v5-two-tier-dev-001/`.
- Analyses: `.thesis-build/v5-study-analysis-dev-001/{descriptive-analysis.json,joint-completeness-audit.json,provenance.json,batch-metrics.json,batch-analysis/}`.
- Reproduce descriptive analysis with WT `scripts/analyze_v5_study.py RESULTS --out FRESH_ANALYSIS.json`; the additional raw-row audit is MAIN `.thesis-build/audit-v5-dev-001.py`. It writes only derived analysis files, never run outputs; choose fresh output paths for any reanalysis.
- Original approval: `.thesis-build/v5-study-execution-authorization-20261003.json`; launch override: `.thesis-build/v5-study-agent-launch-authorization-20261003.json`; final execution receipt: `.thesis-build/v5-study-execution-receipt-20261003.json`.
- Manifest SHA256: `0a9a071eaa15dbaab5907947812c2725e7d55da3621a4ba0feb5f9a7dbea87cd`. Review-computed conservative all-input scientific core: `ac2cac2e1b78182441b2078671c5c9330672a7afae81215df0dc3284e4d9f6cd`; no native harness/rerun delegation.

| Artifact | SHA256 |
| --- | --- |
| results.json | 58766c579377f344770887e6cad8bf4ed779ee207c2b6872b4a24ac4a90b9b4d |
| runtime.json | 5cf73605d4eaaf64d19cd50203d0a34c1a3559410aecc6d00b0af94d2fcc4af9 |
| audit-v5-dev-001.py | 0fd68d7dca6f3ac854d31fd9e7cb77db05e6b9f15b35f442599fec48a413468b |
| descriptive-analysis.json | 2e19e266e749a0a7f90242cd4b41ffe37779e43f0ac7a98e1a61b46e64f3066b |
| joint-completeness-audit.json | 8cd95075849da9f66d6658fd9e739e824aabf3918d6d32ce51bee8ffa7ab575b |

This is an exploratory image-domain comparator on known development photographs. It does not validate latent embedding, native 2K operation, all 6,900 sources, unseen models/data, legal ownership or publication readiness. Missing visual assessments and the unmet numerical/coverage criteria prevent joint preliminary support. Spec Kit remains paused; no gate or issue is closed.
