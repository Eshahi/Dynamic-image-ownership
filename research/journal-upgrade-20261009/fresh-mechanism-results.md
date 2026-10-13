# H1 chip-versus-symbol objective: result

2026-10-13. Decision: **H1 not supported on this fixed development panel**. Chipwise constraints reduce the prespecified within-symbol variation statistic on all six images, but do not improve checked semantic recovery or the primary stress-channel raw-error median. This is a valid negative screen, not evidence of universal objective equivalence or a reason to search for a favorable severity.

Run: MAIN `.thesis-build/dev-runs/20261013-1741-fresh-symbol-objective/run.json`; code `a2e3fa1`; completed in 708.515 seconds, exit 0. All 162 planned records are observed: 18 clean observations, 36 deterministic VAE reconstructions, and 108 T3 transformations. No execution failure, safety block, missing row, retry or source replacement. Sources 30,72,73,89,127,165 and seeds9/10/11 were fixed prospectively. Local USD 0. [Compact evidence](fresh-mechanism-summary.json) retains endpoints, controls and failures.

## Prerequisites and outcomes

Both C (chipwise) and S (length-weighted symbol-mean) pass strict clean quality, exact q/h and full clean acceptance on 6/6 images after energy matching. Maximum relative saved-RGB energy discrepancy is .000102344 (about .01024%); maximum pairwise LPIPS and SSIM differences are .002712 and .000236. All are within the unchanged tolerances. Both methods have VAE J6/6 for SD1.5 and6/6 for SDXL. There are no adverse C-negative/S-positive VAE identities.

| Endpoint | C at .2 | S at .2 | C at .4 | S at .4 |
|---|---:|---:|---:|---:|
| Exact readable semantic payload Q, seed identities | 18/18 | 18/18 | 18/18 | 18/18 |
| Checked recovery J, seed identities | 18/18 | 18/18 | 16/18 | 16/18 |
| Majority J, source groups | 6/6 | 6/6 | 6/6 | 6/6 |
| Exact instance H, seed identities | 0/18 | 0/18 | 0/18 | 0/18 |
| Full acceptance F, seed identities | 0/18 | 0/18 | 0/18 | 0/18 |

The paired majority-J difference is exactly zero at both strengths, with no missing-outcome interval. It fails the required two-source advantage at .4. Both arms lose J on the same identities: source72/strength.4/seed9 and source165/strength.4/seed10. These have exact decoded q but fail the existing content-agreement predicate. They are not payload-erasure failures. Human assessment is absent, so they cannot be labelled false rejections of semantically equivalent images.

Every planned negative call is available with zero observed A: each clean/SD1.5-VAE/SDXL-VAE negative family has0/6, and each T3 family has0/36. Four families are C0 alpha, C0 beta, C beta and S beta. These are correlated calls on six selected source groups, not216 independent negative trials or a calibrated FPR result.

## Mechanism interpretation

Clean within-symbol H is lower for C on6/6 pairs, meeting that necessary shaping prediction. However, median raw coded errors at .4 is0 for both arms, and checked recovery ties. Across the36 T3 identities per arm, raw coded-error histograms are C:{0:27,1:8,2:1}, S:{0:28,1:6,2:1,3:1}. Nonzero codeword errors are visible even though the decoder returns exact q on every attack. Do not transfer the old easy-panel no-rescue finding into a universal BCH-redundancy claim; raw systematic-message versus codeword correction are different diagnostics.

The [geometry note](chip-symbol-geometry-note.md) explains why lowering within-symbol variation can raise a normalized score without changing symbol signs. Here neither the primary recovery separation nor lower stress median occurs. The scientific prediction fails despite a functioning intervention and adequate clean distortion control. An easy-channel ceiling remains a limitation; it does not justify a post hoc strength sweep to make H1 win. The .4 panel is exploratory with metric-only admissibility proxies, not a validated realistic-attack or unseen-model claim.

Retain full E3 as the existing method. No new candidate, binding result, proposal alignment, external superiority or journal readiness follows. Complete the already bounded closest-baseline feasibility check, then reassess the one remaining mechanism-hypothesis allowance against prior art and these results. Any H2 needs a distinct question and prospective protocol; the existing H1 thresholds and outcomes stay unchanged.
