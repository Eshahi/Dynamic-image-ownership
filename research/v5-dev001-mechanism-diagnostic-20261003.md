# Retained v5 dev-001: failure-mode diagnostic

Issue #18. Post-outcome exploratory analysis dated 2026-10-03; this is not a new scientific run or retrospective preregistration. All original rows, thresholds and missing outputs remain unchanged. No GPU/model call or source-image access is needed.

## Regeneration: recorded semantic decision paths

| Arm / dose | Planned | Semantic match | Found, content not matched | Below both thresholds | Missing | q-drift mean / median / SD / range |
| --- | --- | --- | --- | --- | --- | --- |
| C1/0.05 | 30 | 30 | 0 | 0 | 0 | 2.90 / 3.0 / 1.47 / 1–6 |
| C1/0.1 | 30 | 27 | 1 | 1 | 1 | 3.38 / 3.0 / 1.57 / 1–6 |
| C1/0.2 | 30 | 18 | 1 | 9 | 2 | 3.68 / 3.5 / 1.76 / 1–8 |
| C1/0.4 | 30 | 2 | 0 | 26 | 2 | 5.07 / 5.0 / 2.19 / 2–10 |
| C1/vae_mode | 10 | 10 | 0 | 0 | 0 | 2.60 / 2.0 / 1.35 / 1–5 |
| C2/0.05 | 30 | 30 | 0 | 0 | 0 | 3.00 / 3.0 / 1.29 / 1–5 |
| C2/0.1 | 30 | 29 | 0 | 0 | 1 | 3.28 / 3.0 / 1.62 / 0–6 |
| C2/0.2 | 30 | 25 | 2 | 1 | 2 | 4.29 / 4.0 / 1.84 / 0–9 |
| C2/0.4 | 30 | 6 | 1 | 20 | 3 | 5.30 / 5.0 / 1.96 / 1–9 |
| C2/vae_mode | 10 | 10 | 0 | 0 | 0 | 3.10 / 3.0 / 1.37 / 1–5 |

q-drift is Hamming distance between the suspect-recomputed semantic code and that of its clean marked source; summaries use only available outputs and do not erase the missing count. Rows and seeds are correlated; these summaries are descriptive. Below both thresholds means neither saved semantic score meets its own unchanged threshold. It does not isolate whether channel distortion, code drift, or both caused the loss. Content mismatch/uncertainty is reported separately from signal absence.

C2 is a separate descriptive ablation, not pooled with C1. Only 3/10 clean C2 sources (25394, 147498, 177015) meet the numerical quality criteria; the C2 table above includes all planned sources and does not establish quality-admissible robustness.

## Copy-paste: quality failures

| Row | Recipient | Failed numerical thresholds |
| --- | --- | --- |
| t4-residual-6012-147498-0.5 | 147498 | LPIPS>=0.1 |
| t4-residual-6012-147498-1.0 | 147498 | LPIPS>=0.1 |
| t4-residual-80932-109798-1.0 | 109798 | LPIPS>=0.1 |
| t4-residual-134882-147498-1.0 | 147498 | LPIPS>=0.1 |
| t4-public_projection-147498-6012 | 6012 | PSNR<=35, SSIM<=0.9 |
| t4-public_projection-499768-6012 | 6012 | PSNR<=35 |
| t4-unmarked_projection_sham-499768-6012 | 6012 | PSNR<=35 |

These quality failures explain which attempted transfers cannot contribute to recipient coverage; changing a deadline cannot make them admissible. They remain in the original denominators.

## Semantic collision: before and after marking

| Frozen same pair | C0 q / H | C1 q / H | Qualifies C0 | Qualifies C1 |
| --- | --- | --- | --- | --- |
| t5-1675-4795 | 9 / 14 | 11 / 13 | False | False |
| t5-1675-134882 | 12 / 19 | 12 / 19 | False | False |
| t5-1675-177015 | 14 / 17 | 14 / 18 | False | False |
| t5-4795-134882 | 11 / 17 | 11 / 18 | False | False |
| t5-4795-177015 | 5 / 11 | 9 / 11 | True | False |
| t5-80932-468505 | 6 / 14 | 6 / 18 | True | True |
| t5-134882-177015 | 10 / 14 | 12 / 13 | False | False |

Qualifying same pairs: 2/7 before marking and 1/7 after marking, against the fixed minimum of five. This is a comparison of saved feature distances, not proof of a causal mechanism or justification for relabeling pairs.

## Next-experiment decision

Do not repeat the unchanged deterministic batch merely to consume the new 45-minute allowance. It already terminated without a time-limit failure; safety-blocked outputs, low detection scores and insufficient pair/recipient coverage would not be repaired by waiting longer. Do not disable the safety checker or replace failed sources. A subsequent scientific experiment should test a prospectively specified method/coverage hypothesis with fresh exact provenance and retain this baseline. Independent human visual assessment remains outstanding. This diagnostic itself makes no new acceptance claim.

## Provenance

- Results SHA256: `58766c579377f344770887e6cad8bf4ed779ee207c2b6872b4a24ac4a90b9b4d`.
- Diagnostic script SHA256: `ba39f98b5054d52e01572f04cbfa235f7fc1224be04392eba7c6e1c28ab97382`.
- Script: `scripts/analyze_v5_failure_modes.py`; input: MAIN `.thesis-build/v5-study-runs/C4-v5-two-tier-development/c4-v5-two-tier-dev-001/outputs/results.json`.
- Derived rows: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/v5-dev001-diagnostic-20261003-final/diagnostic.json`. Reproduce with the script, the exact result path, `--expected-sha256` above and a fresh `--out` directory.
- Original result report: `experiments/c4-v5-two-tier-regeneration-v1/results-dev-001.md`.
