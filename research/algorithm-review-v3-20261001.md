# Review of the v3 candidate (`scripts/revised_watermark_v3.py`)

Date: 2026-10-01. Requested by the user in the Claude Code session recorded in [method-amendment-decision-20261001.md](method-amendment-decision-20261001.md). This review adds to [algorithm-audit-20260930.md](algorithm-audit-20260930.md); it does not replace or edit it.

## How the review was done

Four reviewers worked independently and read-only: code and security, empirical robustness, proposal conformance and academic rigour, and literature. A fifth reviewer then tried to refute every critical and high finding with its own probes. All five were Claude subagents (model `claude-opus-5-5`); none wrote v3 or v4. Probes used procedurally generated images only. No study image was processed, no model weight was loaded and nothing was downloaded into the repository. The retained v2 run output was read, not rerun.

The verifier judged 24 findings: 20 confirmed and 4 partially confirmed with corrections. None was refuted. Structured findings, the verifier's corrected statements and the probe scripts are in [`audits/v3-algorithm-review-20261001/`](../audits/v3-algorithm-review-20261001/README.md).

Every rate below comes from synthetic images. v3 has never been run on a real image.

## What is sound in v3

The DCT and inverse DCT, the SECDED(8,4) code, the margin index mapping, bit packing, CRC8 and interleaver coverage are correct. A clean embed, rounded to bytes, verifies at about 50.4 dB, including sizes that are not multiples of eight and hosts with large saturated regions. A fresh mark for a victim's OwnerID cannot be made without the key, except through the tag-threshold weakness below.

## Verified findings

| ID | Severity | Finding (as corrected by the verifier) | Verdict |
| --- | --- | --- | --- |
| SEC-1, R2, F01 | critical | A keyless attacker who knows the public method reads the donor payload, shifts the DC of the publicly indexed blocks of an unrelated recipient until its binding equals the donor's, and re-embeds. `detect()` returned `present=True` in 44/44 synthetic pairs for the verifier (26/30, 8/8 and 11/11 for the three reviewers). At 512x512 the forgery stays at 40-49 dB PSNR against the recipient. Keying the carrier alone would not stop it. | confirmed |
| BUG-1, R4, F02 | high | The tag is recomputed from the binding of the suspect image, so one flipped binding bit rejects a genuine mark. Byte rounding alone rejects about 2-3% of clean marked images (14/600 at 160 px, 5/240 at 256 px, 2/60 at 512 px). The instance threshold can never be the deciding gate for an honest input. This is the avalanche that amendment v2 said it had removed. | confirmed |
| SEC-2 | high | Accepting 48 of 64 tag bits gives a per-trial acceptance probability of 3.87e-5 once any v3 mark is present, because the version, ECC and CRC gates are public. A competing (owner, key) pair for an unmodified marked image was found in about 2.6e4 HMAC evaluations. With `owner_accuracy` exposed, 66 queries produced a valid tag for an unmarked image. | confirmed |
| SEC-3 | high | Only the tag is keyed. Reading, erasing and overwriting the payload need no key and cost 49-51 dB. These are the declared T2/T6 limits; the wording "keyed candidate" overstates what is keyed. | confirmed |
| R1 | critical | Hard-decision QIM at step 4 fails between noise sigma 1.4 and 2 (attack PSNR 45-42 dB) and between JPEG quality 90 and 85. A v3 regeneration run should be expected to repeat v2's null result; that is an analytic prediction, not a run. | partially confirmed (see corrections) |
| R3 | high | The 0.65 "confidence" gate rejects payloads that decoded without error. At 512x512 the payload decodes cleanly up to noise sigma 2.2 but acceptance stops at about sigma 1.4, the same as at 256x256, so the repetition gain is cancelled. | confirmed |
| R5 | high | The reliability weights are computed from the attacked image and favour the less reliable slots; the weighted vote was never better than the unweighted one. | confirmed |
| R6, F18, BUG-2 | high | `embed()` accepts smooth hosts that `detect()` then always rejects as `inadmissible_dynamic_range`, although the dynamic range is fine and the payload decodes perfectly. Eligibility depends on per-block variance and therefore on image size. | confirmed |
| R11, F03, F04, F05, F08 | high | v3 has no semantic input, no DCT pHash (the binding reads 63 block means, 1.54% of a 512x512 image), no second key or channel, and a boolean decision. "Semantic key only" cannot occur, and "present but bound to other content" is indistinguishable from a wrong owner, a wrong key or benign drift. | confirmed |
| F06 | high | v3 keeps the v2 carrier and can only be the pixel comparator arm. HYP-02 and RQ-02 stay open. | confirmed |
| F09 | high | The thresholds 0.75 / 0.75 / 0.65 are uncalibrated smoke values with no stated false-positive rate. | partially confirmed: the confidence threshold is the operative gate for genuine marks under mild noise, and the owner threshold for adversarial acceptance; only the instance threshold is inert. |
| F11 | high | No statistic with a known null distribution is returned. | confirmed |
| F13 | high | No output is the decision statistic. ACC can be computed from `present`; an AUC from `confidence` would be uninformative because that field is 1.0 for genuine marks and for adaptive forgeries alike. | partially confirmed |
| F22 | high | v3 is keyed-only and has no amendment, decision record, threat-model row or wrong-secret control. | partially confirmed: the public-derived profile still exists in the untouched v2 file. |
| F24, F25 | high | The closure map and the scope-guard constraints the next revision must respect. | confirmed as consistent with the documents |

Medium and low findings that were not separately verified (SECDED gives no gain over plain repetition on the same slots; partial edge blocks carry unreadable slots; profile validation accepts booleans and thresholds of 0.5; any crop or one-pixel shift fails; the unit tests use one texture and never round to bytes) are listed in `findings.json`.

## Issues the reviewers missed, found by the verifier

1. **A plain copy is accepted when two images share coarse layout.** The binding bit is biased towards zero on flat regions. Among 150 synthetic "object on flat background" images, 0.19% of distinct pairs at 256 px had an identical 32-bit binding, against an ideal of 2^-32; in same-composition families the rate was 0.7% to 6.7%. In every colliding pair tested a keyless payload copy with no binding forcing was accepted at about 50 dB.
2. **The commonly proposed fix is not sufficient by itself.** Verifying the tag against the decoded binding and then applying a Hamming tolerance makes transfer easier with the current descriptor: at a tolerance of 8 of 32 bits, 54% to 100% of distinct pairs in the tested families fall inside it. The method-spec pHash with point-sampled bilinear resizing reads 1.56% of the pixels of a 512x512 image and was forced onto every recipient at a median of 43.6 dB. The descriptor needs anti-aliased downsampling, key-dependent projections in the keyed profile, a calibrated tolerance, and T4 reported as attack cost per access arm. A public unkeyed descriptor remains forceable.
3. **Plain additive spread spectrum is host-limited.** A correlation score fell from 71 on a smooth host to 3.8 on a high-texture host at the same 42 dB. A replacement needs host rejection or declared embedding failures.
4. **The hard-decision decoder discards margin.** A soft correlation against the known payload still gives a score of 13 at noise sigma 3 on a 512x512 image where `detect()` rejects. The carrier is dead from about sigma 4, so this does not rescue regeneration.

## Corrections to how the retained v2 run is summarised

The run itself is unchanged and must not be replayed or overwritten.

- **Regeneration survival is 0/54, not 0/108.** There are 54 completed marked (C1) rows, 27 per strength, with nine of ten sources; source 6012 is missing for all seeds. The other 54 rows are unmarked controls with 0/54 false positives. Content retention by the plan's CLIP criterion held for 27/27 marked rows at strength 0.2 and 14/27 at 0.4, and the two-reviewer check is unreviewed on every row.
- **"0/120 accepted" in T4 does not test content binding.** The public-patch arms had 0/40 admissible attempts (12-23 dB against the recipient). The residual arm was admissible but did not deliver the mark. The 21 rows with a valid CRC are 20 complete payload copies with owner accuracy 1.0, rejected only by the 12-bit binding (five of them by one bit), plus one unmarked sham patch that passed CRC8 by chance. No admissible attempt carried a decodable mark, so the result is inconclusive for HYP-04.
- The plan text still describes ten sources while the executed manifest used twelve on the clean and T5 axes.

## What the literature review adds

The pixel-arm regeneration failure agrees with published results: Zhao et al. and the W-Bench benchmark report classical transform-domain marks at about 40 dB removed almost completely by diffusion regeneration, and report that editing removes mid and high frequencies while leaving low frequencies relatively intact. No fetched source shows a hand-crafted block-DCT mark at 35 dB or better surviving diffusion regeneration, and no source shows a latent-embedded mark read by a blind 8x8 image-DCT correlation. The thesis should report the pixel-arm outcome as the pixel side of HYP-02, not as a defect to tune away. Source-by-source verification status is in `findings.json`.

## Consequence

The v4 candidate ([method-amendment-v4.md](method-amendment-v4.md)) was written against these findings: verification through codes carried in the mark with a Hamming tolerance, a key-dependent image-wide descriptor, a keyed carrier, host-rejecting spread spectrum with declared embedding failures, a correlation statistic with a stated false-positive bound, and the proposal's decision states. Whether v4 meets them is for its own independent review, not for this document.
