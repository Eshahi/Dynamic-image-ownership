# E3 and WAM common-message development comparison

2026-10-14. Fixed native operating points; previously consulted development images. This is a common exact-payload task, not matched-FPR, matched-distortion or ownership benchmarking.

## Execution and eligibility

Clean receipt: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\dev-runs\20261014-e3-wam-common-clean/run.json`, code `9fb10cb5ca72f9b26e24d41a585e5c478b8c4ad5`, 37.906 s. T3 receipt: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\dev-runs\20261014-e3-wam-common-t3/run.json`, code `e0a9d5b9fd259df75056a2cb169a72d047021f89`, 151.406 s.

Clean eligibility **PASS**: 36/36 reader calls and 30 image-family records. E3 q, WAM q, WAM complement and WAM hash each pass strict clean quality and readable exact assigned-message recovery on 6/6. Native WAM tensor parity, empty-mask/serialization tests and retained E3 classification checks pass. All tested C0 own/complement/cyclic targets and primary C1 wrong-message counts are zero. Control-message successes are not pooled with the common-q endpoint.

T3 contains 108 unique image attempts and 144 unique planned reads. Image statuses: {'ok': 108}; reader statuses: {'ok': 144}. No missing, duplicate or extra identities. Shared C0 images are read by both methods and are not duplicate independent sources.

The six ascending reserved IDs are 30, 72, 73, 89, 127, 165. Both primary methods embed the same frozen source-derived 32-bit q. WAM additionally embeds complementary and fixed source-ID-hash controls at the same native w=2. Neither reader receives expected q, source ID or original pixels; equality is evaluator-only. E3 Q requires semantic.read, so recomputed-only matches and below-threshold BCH candidates never count. WAM uses predicted masks and native semihard raw-logit means >.5; an empty mask is unavailable.

## Clean quality and control messages

| Source | Method / message | PSNR dB | SSIM | LPIPS | Exact | Strict |
|---:|---|---:|---:|---:|---:|---:|
| 30 | E3 / q | 43.4352 | 0.972770 | 0.088671 | 1 | 1 |
| 30 | WAM / q | 40.8139 | 0.988911 | 0.018738 | 1 | 1 |
| 30 | WAM / complement | 40.8169 | 0.989168 | 0.018188 | 1 | 1 |
| 30 | WAM / hash | 40.8076 | 0.988995 | 0.018706 | 1 | 1 |
| 72 | E3 / q | 40.3687 | 0.987148 | 0.017819 | 1 | 1 |
| 72 | WAM / q | 36.1750 | 0.988047 | 0.051444 | 1 | 1 |
| 72 | WAM / complement | 36.1506 | 0.988176 | 0.047423 | 1 | 1 |
| 72 | WAM / hash | 36.2153 | 0.987909 | 0.051296 | 1 | 1 |
| 73 | E3 / q | 40.0690 | 0.987311 | 0.020286 | 1 | 1 |
| 73 | WAM / q | 36.1551 | 0.992872 | 0.049508 | 1 | 1 |
| 73 | WAM / complement | 36.1141 | 0.992981 | 0.050615 | 1 | 1 |
| 73 | WAM / hash | 36.1090 | 0.993139 | 0.047617 | 1 | 1 |
| 89 | E3 / q | 41.6931 | 0.966148 | 0.037913 | 1 | 1 |
| 89 | WAM / q | 38.8051 | 0.968608 | 0.034157 | 1 | 1 |
| 89 | WAM / complement | 38.7620 | 0.968852 | 0.032528 | 1 | 1 |
| 89 | WAM / hash | 38.7276 | 0.968578 | 0.030795 | 1 | 1 |
| 127 | E3 / q | 40.4217 | 0.960903 | 0.031903 | 1 | 1 |
| 127 | WAM / q | 36.7235 | 0.952896 | 0.041718 | 1 | 1 |
| 127 | WAM / complement | 36.7317 | 0.953496 | 0.039793 | 1 | 1 |
| 127 | WAM / hash | 36.7655 | 0.953425 | 0.043675 | 1 | 1 |
| 165 | E3 / q | 40.7891 | 0.955932 | 0.040602 | 1 | 1 |
| 165 | WAM / q | 37.6129 | 0.965673 | 0.024703 | 1 | 1 |
| 165 | WAM / complement | 37.6131 | 0.966148 | 0.024816 | 1 | 1 |
| 165 | WAM / hash | 37.5859 | 0.966029 | 0.023471 | 1 | 1 |

Strict means PSNR>35 dB, SSIM>.9, LPIPS<.1, each against the same canonical source. These are ceilings, not equal distortion. All delivered pixels and failed outcomes are retained.

Assigned-q bit-one counts across six images: `[5, 1, 3, 4, 6, 3, 4, 3, 5, 6, 0, 3, 1, 3, 0, 0, 6, 0, 2, 4, 0, 6, 2, 3, 0, 1, 5, 4, 4, 4, 1, 0]`. Pairwise distances range 5–15 bits; hash-control schedule collisions: []. There are no repeated q words. Six structured messages do not establish uniformity or 32 bits of entropy.

## Regeneration outcomes

Pinned SD1.5 DDIM20, strengths .1/.2, seeds 9/10/11, empty prompts, guidance=1, eta=0, native safety checks, same fresh generator seed for each matched identity. Native sampler FP16; readers FP32. Each delivered primary mark and shared C0 is regenerated afresh, saved and reopened. All 18 planned C1 attempts per method/strength remain in the denominator; source N=6.

| Strength | Method | Available / 18 | Readable / 18 | Exact Q / 18 | Source majority Q / 6 | Zero-filled bit score |
|---:|---|---:|---:|---:|---:|---:|
| 0.1 | E3 | 18 | 18 | 18 | 6 | 1.000000 |
| 0.1 | WAM | 18 | 17 | 3 | 1 | 0.866319 |
| 0.2 | E3 | 18 | 18 | 18 | 6 | 1.000000 |
| 0.2 | WAM | 18 | 13 | 0 | 0 | 0.548611 |

The zero-filled bit score assigns zero to unreadable/unavailable calls; it is not measured BER. At least two of three planned seeds define a source majority. No seed-level independence or significance test is asserted.

| Source | .1 E3 Q / 3 | .1 WAM Q / 3 | Paired difference | .2 E3 Q / 3 | .2 WAM Q / 3 | Paired difference |
|---:|---:|---:|---:|---:|---:|---:|
| 30 | 3 | 0 | +1.000 | 3 | 0 | +1.000 |
| 72 | 3 | 0 | +1.000 | 3 | 0 | +1.000 |
| 73 | 3 | 2 | +0.333 | 3 | 0 | +1.000 |
| 89 | 3 | 0 | +1.000 | 3 | 0 | +1.000 |
| 127 | 3 | 1 | +0.667 | 3 | 0 | +1.000 |
| 165 | 3 | 0 | +1.000 | 3 | 0 | +1.000 |

| Strength | E3 S | E3 J | E3 H | E3 F |
|---:|---:|---:|---:|---:|
| 0.1 | 18/18 | 18/18 | 0/18 | 0/18 |
| 0.2 | 18/18 | 18/18 | 0/18 | 0/18 |

E3 content checks are system-specific secondary endpoints; WAM has no equivalent full ownership decision. Their absence is not a WAM failure. Neither a wrong-message control nor E3 public-owner routing establishes cryptographic security.

| Strength | Method | C0 available / 18 | C0 readable / 18 | C0 own / complement / cyclic matches | C1 complement / cyclic matches | Attack-input LPIPS median / max | Canonical LPIPS median / max |
|---:|---|---:|---:|---|---|---|---|
| 0.1 | E3 | 18 | 0 | 0 / 0 / 0 | 0 / 0 | 0.161594 / 0.217553 | 0.182218 / 0.288327 |
| 0.1 | WAM | 18 | 0 | 0 / 0 / 0 | 0 / 0 | 0.110235 / 0.213582 | 0.108831 / 0.202676 |
| 0.2 | E3 | 18 | 0 | 0 / 0 / 0 | 0 / 0 | 0.221219 / 0.282217 | 0.240423 / 0.337503 |
| 0.2 | WAM | 18 | 0 | 0 / 0 / 0 | 0 / 0 | 0.162689 / 0.278868 | 0.155355 / 0.259152 |

Distortion is descriptive; no attack was removed by a quality filter. Human admissibility remains missing. Native WAM readable-mask counts are diagnostics, not a calibrated image-presence FPR. Zero observed exact negative matches on six source clusters does not certify a rare-event rate.

## Interpretation and next allocation

This establishes a usable shared payload-recovery implementation and a bounded native-setting comparison. It does not establish matched-FPR superiority, equal distortion, arbitrary-message advantage, added binding value or journal readiness. E3 has BCH(59,32), 320 semantic carrier chips plus a separate h tier; WAM is an arbitrary 32-bit image watermark. The payload source, total coding budget, models used at extraction, and writer effort differ. E3 construction explicitly optimized this SD1.5 DDIM .1/.2 channel with seeds 0–2; these new seeds are not a new diffusion backbone. The published WAM SA-1B MIT checkpoint is not the paper’s COCO model.

The fixed comparison is complete, including unfavorable results. Do not tune amplitude, message, seed or threshold on these six sources. Retain native tables and carry the comparison forward only through a separately frozen distortion/FPR calibration and independent-transfer design. Use new development source groups for calibration and evaluation, with ID/hash exclusion of protected held-out assignments. No large construction run or acquisition is launched by this report; the protocol describes its feasibility and resource requirements.

Peak process RAM: clean 2.810 GiB, T3 3.172 GiB. Peak CUDA allocations: 1.328 / 3.903 GiB. USD 0 rental/API; electricity unmetered. No downloads, paid computation, held-out inspection or protected edits. E3 marks were reused from the retained construction run; fresh WAM embedding time versus cached E3 access is not a fair construction-speed comparison.

Reproduce this report from receipts with `scripts/analyze_e3_wam_common.py --clean <clean-dir> --t3 <t3-dir> --output <report.md>`. The four interface regression tests are `tests/test_e3_wam_common.py`. Independent review is recorded separately.
