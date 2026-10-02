# Evidence criteria for the small v5 two-tier study

Fixed on 2026-10-02 before any photograph was processed with v5. The clean, T3, T5 and joint criteria are those of `experiments/c4-v4r2-three-threat-small-v1/acceptance-criteria.md`, unchanged. The T4 criteria are the same rule applied to this study's arms. `content_uncertain` and `not_detected` are reported as their own states; they are never counted as `content_match` or as `watermark_found` unless the codec's own `watermark_found` field says so.

All counts retain planned failures and missing controls. No criterion changes after study outcomes.

## Clean prerequisites

All 12 C1 images must have non-zero changes, authoritative saved-suspect `both_match` and RGB PSNR > 35, SSIM > 0.9, LPIPS < 0.1. All 12 C0 images and all 36 wrong-owner C1 calls must complete without `watermark_found`; report `both_match` and per-channel events separately. These small development controls cannot establish a population FPR. Any failed source prevents joint support.

Two independent human assessments of the 12 marked images against their sources are required, with attention to flat regions, because the robust tier changes low frequencies. Until they exist the quality prerequisite is numeric only.

## T3 regeneration

At each of the four diffusion strengths, preliminary owner-semantic survival requires at least 9 of 10 source groups to meet CLIP >= 0.90, two-reviewer content retention and `semantic.found` with `content_match` on all 3 fixed C1 seeds. All 30 paired C0 rows must complete with zero `watermark_found`. The VAE-mode round trip is a separate 10-group stratum with at least 9 of 10 C1 successes and all 10 C0 negative. Missing C0 or visual evidence prevents support; invalid semantics cannot be counted as a successful removal attack. Report `both_match` and `semantic_only` separately and all strength curves; never select a favourable dose. Any content-retained C1 with no `watermark_found` is a counterexample to blanket survival, but rate support also requires complete controls.

**Mechanism observation (weaker than support, stated separately).** If at least 5 of the 10 VAE-mode C1 rows read `semantic.found` with `content_match`, with all VAE-mode C0 rows negative, the run shows that the robust tier does what it was built for on these photographs, where revision 2 had 0 of 10. This is an observation about a mechanism on ten images, not survival support, and it must be worded so.

**Outcome label.** The amendment reads `semantic_only` as the proposal's "regenerated" state. Report, per stratum, how many surviving C1 rows read `semantic_only` and how many read anything else (`both_match`, `content_uncertain`, `content_mismatch`). A regenerated genuine image that reads `content_mismatch` is a false copy-paste label and is reported as such.

## Secondary arm C2 (strong profile; descriptive, no pass rule)

The ten C2 images are marked with a larger robust-tier budget and are expected to miss PSNR > 35. Report, per image, quality and the clean outcome, and per T3 stratum the same counts as for C1 against the same C0 rows. An inadmissible marked image cannot support survival, whatever its detection outcome. The arm is reported next to the C1 arm as a second point of the quality-robustness trade-off; it is never pooled with C1 and never substituted for it. Any C2 clean image that does meet all three admissibility thresholds is named, and its T3 rows are still reported under this section only.

## T1s ordinary processing (supplementary, no pass rule)

Report the outcome counts of the 10 C1 and the `watermark_found` counts of the 40 C0 calls per operation. These rows cannot substitute for T3, T4 or T5.

## T4 copy paste

For each arm separately (clean-donor residual at 0.5 and at 1, public projection, unmarked projection sham), count attempts, admissible outputs, delivery (`none`-mode `watermark_found`), donor attribution (`combined` `both_match`), and `content_mismatch` given delivery. Preliminary binding support requires complete calls and admissible delivered examples spanning at least 10 distinct recipients, complete no-transfer C0 negatives and negative shams. Any content-admissible distinct-recipient `combined` `both_match` is a false-attribution counterexample. Zero acceptance without delivery or admissibility is inconclusive, not security success. Never pool the arms.

## T5 semantic collision

Component support requires at least 5 same pairs with q-distance <= 6 and H-distance > 6, at least 5 different pairs, all 12 same-instance q and H distances <= 6 and no joint near-collision among the same pairs. Fewer semantic-near pairs is inconclusive; frozen uncertain labels stay separate. With this cohort the revision-2 run found 3 such pairs, so this component is expected to be inconclusive again; the cohort is not expanded here.

End-to-end support additionally needs at least 5 same-semantic admissible delivered projection transfers and no `combined` `both_match` on them, with complete C0 and binding-mode controls. `semantic_only` ablation acceptance is a diagnostic, not a required favourable outcome.

## Joint interpretation

Clean prerequisites and all three primary axes need complete evidence for joint preliminary support. Failure, insufficient delivery or coverage, missing metrics or missing independent visual assessment prevents that claim. A computationally complete batch may give negative or inconclusive scientific results. No conclusion validates latent embedding, native 2K behaviour, all 6,900 sources, other regeneration models, legal ownership or publication readiness.
