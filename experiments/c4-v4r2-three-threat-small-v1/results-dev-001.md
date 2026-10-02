# Results of `c4-v4r2-three-threat-dev-001` (v4 revision 2, three threats)

Exploratory development evidence for an image-domain pixel comparator. It is not evidence about the proposal's latent method (RQ-02/HYP-02 stay open), legal ownership, a population FPR or native 2K behaviour. Criteria are those of `acceptance-criteria.md`, fixed before the run.

## Run record

| Item | Value |
| --- | --- |
| Commit | `13df481` on `claude/v4r2-three-threat-study` (local, not pushed) |
| Manifest | `.thesis-build/v4r2-three-threat-final-20261002.json`, sha256 `42d7a978e4f238dd121be6dfe7f616092a5883314b144c5a557fa1539016cf1d` |
| Approval | `.thesis-build/v4r2-three-threat-user-decision-20261002.json` and `...-execution-authorization-20261002.json`: a delegated chat approval, given before the manifest existed and not shown the hash; it needs the user's confirmation |
| Runner | official dispatcher, `--execute`, local RTX 5070 Ti, USD 0, no downloads |
| Output | `.thesis-build/v4r2-three-threat-runs/C4-v4r2-three-threat-development/c4-v4r2-three-threat-dev-001/` |
| Analysis | `scripts/analyze_v4r2_study.py` writes `.thesis-build/v4r2-three-threat-analysis-001/analysis.json` |
| Wall time | 751 s worker (embedding and transfers 170 s, regeneration 126 s, CLIP and detection 304 s, LPIPS 151 s) |
| Completion | 1,812 of 1,884 detector calls; 0 stage failures; 18 rows `safety_checker_blocked_output` (9 T3 C1 and 9 T3 C0 outputs at strengths .1/.2/.4, three per strength and control) |

The runner records the run as `failed` because the worker exits non-zero whenever a planned row is missing. The only missing rows are the 18 safety-checker blocks; they stay in the denominator as the plan requires. No retry was made.

Mean costs: embedding 1.02 s, suspect CLIP 0.09 s, one detector call 0.125 s (CLIP not included), SD img2img plus save 0.44 s.

## Clean prerequisites: met (numerically)

All 12 marked images (C1) have non-zero changes and `both_match` on the saved, reopened suspect, with RGB PSNR 41.8 to 42.3 dB, SSIM 0.958 to 0.984 and LPIPS 0.005 to 0.091 (worst 147498 at 0.091). All 48 unmarked C0 calls and all 36 wrong-owner C1 calls returned no `watermark_found`. Clean C1 scores are about 11.2 against thresholds of about 5.5; C0 scores average 0.5 to 0.9. Independent visual review was not done.

## T3 regeneration: v4 r2 does not survive, even with no diffusion at all

| Stratum | C1 rows detected | C1 `watermark_found` | Groups with CLIP >= .90 on all seeds | C0 `watermark_found` |
| --- | ---: | ---: | ---: | ---: |
| VAE mode round trip | 10/10 | 0 | 10/10 | 0 |
| strength .05 | 30/30 | 0 | 10/10 | 0 |
| strength .10 | 27/30 | 0 | 9/10 | 0 |
| strength .20 | 27/30 | 0 | 8/10 | 0 |
| strength .40 | 27/30 | 0 | 3/10 | 0 |

All 121 detected C1 outputs are `neither_match` for the true owner. Mean semantic-channel scores of C1 (0.47 to 1.20) are in the range of their paired C0 controls (0.41 to 0.82), against a threshold of 5.64, so the mark is gone, not weakened. The deterministic VAE round trip alone (output PSNR about 25 dB against its input) removes it. This is the outcome the plan named as the expected failure mode of a hand-crafted image-domain mark. It is a counterexample to survival at every dose; the survival criterion fails at every dose regardless of the missing visual assessments. `semantic_only` never occurs after regeneration.

## T4 copy-paste: binding holds where marks are delivered, but the patch arms are inconclusive

| Arm | Attempts | Admissible (PSNR>35, SSIM>.9, LPIPS<.1) | Delivered (`none` mode found) | `combined` `both_match` | `content_mismatch` given delivery |
| --- | ---: | ---: | ---: | ---: | ---: |
| public patch 128 / 256 | 20 / 20 | 0 / 0 | 0 / 0 | 0 | - |
| unmarked patch sham 128 / 256 | 20 / 20 | 0 / 0 | 0 / 0 | 0 | - |
| clean-donor residual .5 | 20 | 20 | 0 | 0 | - |
| clean-donor residual 1.0 | 20 | 20 | 9 (6 recipients) | 0 | 9 |
| public band | 20 | 0 | 20 | 0 | 20 |
| unmarked band sham | 20 | 0 | 0 | 0 | - |
| public projection | 20 | 20 | 20 (10 recipients) | 0 | 20 |

- Public projection, the strongest method-aware transplant, delivers the donor's key into all 20 recipients at admissible quality, and the content binding rejects all 20 as `content_mismatch` under `combined`. No false attribution. With 10 distinct recipients this meets the preliminary binding criterion for this regime.
- Clean-donor residual at scale 1 delivers 9 marks (6 recipients), all rejected as `content_mismatch`. Below the 10-recipient requirement, so preliminary only.
- Patch arms and the band arm never produce an admissible output, so they cannot show binding resistance (inconclusive, not success). The patches also never deliver a detectable key.
- Binding ablations: with `none` every delivered mark is accepted (expected); with `perceptual_only` all are rejected; with `semantic_only` 1 of 20 projection and 3 of 20 band transfers are accepted, the rest are `content_mismatch` or `content_uncertain`. The semantic channel alone is a weak binding, consistent with the known limit in `research/method-amendment-v4.md`.
- Shams and every C0 produced no detections.

## T5 semantic collision: component criterion not met (insufficient near-semantic coverage)

- Same-semantic pairs: 7. Only 3 have q-distance <= 6 (all 3 with H-distance > 6). The criterion needs at least 5, so the component test is inconclusive by its own pre-registered rule; the cohort was not expanded.
- Different pairs: 57. 5 have q-distance <= 6 (semantic near-collisions), all separated by H (> 6). No exact q or H collision, no joint near-collision in any label group.
- Same instance (C0 against C1, 12 sources): q and H both within 6 for all 12, so embedding does not move the codes.
- End-to-end: 7 same-semantic public-projection transfers, all admissible and delivered, all rejected under `combined` (`content_mismatch`); `semantic_only` accepted 3 of 7. Seven delivered transfers meets the "at least 5" count, but the support also requires the component criterion, which is inconclusive.

## Joint reading

Joint preliminary support is not reached. Clean prerequisites pass numerically; regeneration is a clear negative (complete removal from the VAE stage on); copy-paste binding is supported only for the public-projection regime; semantic collision is inconclusive because of coverage. Independent visual assessments (two humans) are missing for every axis, which by itself blocks any support claim.

## Comparison with revision 1

Revision 1 never produced evaluated attack results (run 001 stopped after the clean axis, 12/12 `both_match`). Revision 2 matches it on the clean axis. Nothing else can be compared.

## Deviations and open items for the user

1. Approval was delegated in chat before the manifest existed; the user should confirm or reject the run on return.
2. No independent reviewer checked the package; it was written and run by the same agent.
3. Worker bookkeeping differs from revision 1 (throttled writes); no scientific step changed.
4. Visual principal-content assessments are still needed for clean, T3 (CLIP-retained outputs) and admissible T4/T5 outputs.
