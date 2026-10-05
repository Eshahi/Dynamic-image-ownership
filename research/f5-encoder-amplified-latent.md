# Family 5: encoder-amplified latent carrier (development, 2026-10-05)

Designed, implemented and tested by Claude (Anthropic) after the user asked for an idea that changes the game. Exploratory development evidence on the twelve development sources only; no held-out data. Human visual verdicts: none. Threat scope T3, T4, T5 (`AGENTS.md`).

## Idea

The regeneration removal theorem (Zhao et al., arXiv 2306.01953, Theorem 4.3) bounds any detector after x' = A(phi(x_w) + N(0, sigma^2 I)) by f(e1) = Phi(Phi^-1(1 - e1) - L Delta / sigma), where Delta = ||x_w - x|| and L is a *local, watermark-specific* Lipschitz constant of the embedding phi, ||phi(x_w) - phi(x)|| <= L ||x_w - x||. For SD1.5 img2img, phi is the VAE encoder and the noise is added in its latent. An invisible mark is safe only if L is small. The SD VAE encoder is not robust: PhotoGuard's encoder attack (Salman et al., arXiv 2302.06588) solves argmin over ||delta||_inf <= 16/255 of ||E(x + delta) - z_targ||^2 to steer img2img edits.

So: choose the mark direction to make L large on purpose. Write the robust tier with a pixel change found by gradient ascent through the attacker's own encoder, aimed at a keyed latent pattern in the band the denoiser keeps. The attack then carries the mark through its own first stage, and the removal bound becomes vacuous for this mark. Prior work used encoder sensitivity destructively (immunization); FreqMark (arXiv 2410.20824) optimizes the latent spectrum but writes through the decoder and reads with DINOv2. A-C wrote through the decoder (`D(u) - D(u0)`) and spread its template over all 16,384 latent coordinates, mostly high latent frequencies the denoiser removes. A quick search found no keyed, detectable carrier built on encoder gain; this is not a novelty claim.

## Probe (`scripts/f5_encoder_gain_probe.py`)

Fixed keyed unit latent pattern per band (radial cycles/image on the 64x64 latent, four channels). Same-PSNR comparison of the decoder rendering of the pattern (natural, A-C style) with a pixel change from 100 steps of projected gradient ascent through the fp32 encoder. Pinned img2img, seed 0, same seed for x and x+d. Medians over the twelve sources (eleven completed at each strength; 6012 safety blocks).

| Budget | Variant | LPIPS median (max) | Clean latent signal | Kept at .4 | Score after .4, informed (min) | Blind |
|---|---|---|---|---|---|---|
| 46 dB | natural, 8-16 c/i | .0014 (.0019) | 1.3 | .34 | 0.9 (0.6) | 0.5 |
| 46 dB | encoder, 8-16 c/i | .020 (.068) | 26.5 | .57 | 37.4 (25.1) | 20.2 |
| 52 dB | natural, 8-16 c/i | .0003 (.0005) | 0.6 | .34 | 0.5 (0.2) | 0.2 |
| 52 dB | encoder, 8-16 c/i | .0054 (.015) | 15.9 | .51 | 18.8 (12.5) | 10.3 |

At equal PSNR the encoder route moves the latent pattern 20 to 27 times further, and img2img keeps a larger fraction of it. Runs: `.thesis-build/dev-runs/20261005-0300-f5-encoder-gain-smoke`, `20261005-0310-f5-encoder-gain-psnr46`, `20261005-0310-f5-encoder-gain-psnr52`.

## Codec (`scripts/f5_latent_codec.py`)

v5 r3 unchanged except the robust tier. Semantic code q (CLIP), Ws tables, fragile luminance instance tier (47 dB), perceptual hash H, key test, Bentkus-Dzindzalieta thresholds and decision table are v5's, with v5's study profile, so q and H are identical to v5's. Robust tier: posterior-mode latent of the suspect (pinned SD1.5 VAE, fp32), orthonormal DCT per channel, coefficients with index radius 4 to 32 (about 2-16 cycles/image), public weight radius/4, 3,272 slots spread over the 320 chips with keyed signs by v4's carrier. The weights do not depend on the key, so the null statistic is still a weighted sum of independent random signs. Embedding: 150 steps of normalized-gradient descent on a squared hinge of the chip margins through the encoder, L2 ball at the PSNR budget, [0,1] box; RGB8 rounding; fragile tier on the luminance of that image; one short refinement and a final fragile pass. About 37 s per image on the RTX 5070 Ti. Detector side information: public OwnerID, profile, pinned CLIP, pinned SD1.5 VAE encoder.

**Setting fixed before the gate.** Band 4-32 and whitening 1 were in the committed codec before any gate result. The budget was declared by quality only: robust PSNR 50 dB, raised to 52 dB if clean LPIPS exceeded v5's mean (.0176) or maximum (.038). A two-source smoke run at 50 dB (`20261005-0400-f5-gate-smoke`) had LPIPS mean .021, so the full gate ran once at 52 dB. No other setting was tried on the gate.

## M1a gate (`scripts/f5_gate.py`, run `.thesis-build/dev-runs/20261005-0420-f5-gate-psnr52`)

| | F5 | v5 r3 (dev-001) |
|---|---|---|
| Clean PSNR mean (min) | 44.7 (43.3) | 37.1 (35.3) |
| Clean SSIM min | .975 | |
| Clean LPIPS mean (max) | .0172 (.051, source 147498) | .0176 (.038) |
| Clean both_match | 12/12 | 12/12 |
| VAE posterior mode, C1 semantic | 12/12 | 10/10 |
| Paired C1 semantic, img2img .05 | 30/30 | 30/30 |
| .1 | **29**/29 | 27/29 |
| .2 | **25**/28 | 18/28 |
| .4 | **21**/28 | 2/28 |
| C0 and wrong-owner detections | 0 of 159 C0 rows x 4 owners, 0 wrong-owner | 0 |

Paired identities are source/strength/seed triples completed on both sides; safety blocks are excluded. Gate status: **passes M1a as written**, on the first full run at the pre-declared setting. Only one quality number is worse than v5: the LPIPS maximum (.051 on the sky image 147498), inside the gate's .1 limit.

## Why it still fails sometimes: carrier versus binding (`scripts/f5_binding_diagnostic.py`, run `20261005-0500-f5-binding`)

Every completed C1 row is classed as success, binding failure (key found, content check not matched) or carrier failure (key not found), and split by the T3 protocol's content-retention line (CLIP cosine to the source >= .90).

| Strength | F5 | v5 r3 |
|---|---|---|
| .2 | 30 success; 5 binding failures (1 not retained); **0 carrier** | 18 success; 9 carrier; 1 binding |
| .4 | 25 success; 9 binding failures (6 not retained); **0 carrier** | 2 success; 26 carrier (12 not retained) |

F5's mark was found on every attacked marked image at every strength. Scores at .2 range from 8.9 to 16.4 (median 13.3; decoded-code threshold 8.26). At .4 they range from 5.0 to 14.8 (median 10.4), so a few rows pass only by the recomputed-pattern threshold of 4.98, with no margin. Unmarked C0 calls score at most 2.6. All remaining failures are semantic-code drift: the CLIP code q recomputed from the regenerated image moved by more than the semantic radius of 6 bits from the code the mark carries. Of the 9 failures at .4, 6 are outputs whose content is not retained by the thesis's own criterion. The bottleneck has moved from the carrier to the semantic binding.

## T4 and T5

- T4 (`scripts/f5_t4.py`, run `20261005-0500-f5-t4`, v5's twenty donor/recipient pairs): combined both_match on recipients 0/20 at residual scale .5 and 1 (v5 0/20). The copied residual barely carries the robust key at all: semantic key delivered (binding none) 0/20 at .5 and 1/20 at 1, against v5's 18/20 and 20/20. The pixel change only works through the encoder at the donor's own pixels, so copy-paste fails at the carrier, before binding is needed. Combined outcomes at .5: neither 17, content_mismatch 3; at 1: content_mismatch 14, neither 6.
- T5 (`scripts/f4_t5.py`, run `20261005-0500-f5-t5`): joint near collisions of distinct marked images 0/66 (v5 0/66); C0 codes identical to v5's on all 66 pairs (same profile); same image C0 to C1 within 6 on both codes 12/12.

T4 and T5 are not worse than v5.

## Visual

`20261005-0420-f5-gate-psnr52/compare-source-v5-f5.png`: crops (2x) where F5's change is largest, for 147498 (sky, the worst LPIPS), 1675 and 468505: source, v5, F5, F5 change x20. The change is a fine, grid-like texture with small coloured clusters. Claude's observation: in the sky crop v5's blotchy grain is more visible than F5's change.

**Human visual verdict (the user, 2026-10-05, after viewing this comparison):** "کیفیت بصری قبوله" ("the visual quality is acceptable"). It applies to the F5 images of run `20261005-0420-f5-gate-psnr52` (52 dB robust budget); later runs at the same budget change only which key pattern is written.

## Limits

- Exploratory development counts on twelve sources, dependent seeds; held-out confirmation is required before any claim.
- The gain is a property of the pinned SD1.5 VAE encoder, which is the T3 threat model's pinned regeneration family. Out of scope and untested, one line: a different regenerator's encoder, or a pixel pre-filter applied before encoding (a T2 composition), may not see the gain.
- Detector side information now includes the public SD1.5 VAE encoder, as in A-C's reader; it must be accepted explicitly at M1.
- LPIPS maximum .051 on one flat sky image; a perceptual mask (`mask_power` in the codec, untested) is the first thing to try if the human visual check objects.
- Next research target, in scope: the semantic binding under regeneration (q drift at .2 and .4), now the only cause of T3 failures.

## Revision 2: semantic binding (user request, 2026-10-05: "آزمایش پیوند معنایی رو هم انجام بده")

After revision 1 every T3 failure was a binding failure. The code bits are signs of 32 keyed Rademacher projections p_j of the unit CLIP vector, and the detector sees p_j itself, so a disagreement on a bit whose projection is near zero is expected under small drift. Two changes were tested, with v5's own angles (match at most 6 pi/32, mismatch at least 10 pi/32; nothing tuned):

- **Soft binding:** maximum-likelihood angle from P(c_j | p_j, t) = Phi(c_j p_j cot t), mixed with the decoder's error rate, instead of pi * Hamming / 32. On synthetic pairs at t = .45 its spread is .136 rad against .194 for the Hamming estimate.
- **Seven-view CLIP:** the semantic vector E is the re-normalized mean over the image, its mirror, four corner crops and the centre crop at 7/8 size; this changes the code the mark carries, so it needs re-embedding.

Selection rule, declared before the run (`scripts/f5_binding_experiment.py`): a variant replaces hard binding with one view only if it raises T3 matches at .2 and .4, does not raise semantic matches on different-label donor/recipient pairs, and keeps T5 joint collisions at zero.

Offline screen on the revision-1 images (`20261005-0600-f5-binding-experiment`; carried code taken as exact):

| Rule | T3 match .2 (of 35) | .4 (of 34) | Different-label semantic matches (of 114 ordered pairs) | T5 joint collisions |
|---|---|---|---|---|
| hard, 1 view (rev. 1) | 31 | 28 | 2 | 0 |
| soft, 1 view | 35 | 28 | 0 | 0 |
| hard, 7 views | 35 | 29 | 6 (fails the rule) | 0 |
| soft, 7 views | 35 | 31 | 2 | 0 |

Real runs (all CLIP, latent and decision steps as in deployment):

| | Rev. 1 (hard, 1 view) | Soft, 1 view (re-read of the same images, `20261005-0630-f5-reread-soft`) | **Rev. 2: soft, 7 views (re-embedded, `20261005-0640-f5-gate-soft-views7`)** | v5 r3 |
|---|---|---|---|---|
| Paired C1 semantic .1 | 29/29 | 29/29 | **29/29** | 27 |
| .2 | 25/28 | 26/28 | **28/28** | 18 |
| .4 | 21/28 | 21/28 | **23/28** | 2 |
| All C1 rows .2 / .4 | 30/35, 25/34 | 33/35, 26/34 | **35/35, 29/34** | |
| Clean PSNR mean, LPIPS mean (max) | 44.7, .0172 (.051) | same images | 44.7, .0173 (.050) | 37.1, .0176 (.038) |
| Clean both_match; C0 and wrong-owner detections | 12/12; 0 | 12/12; 0 | 12/12; 0 | 12/12; 0 |

Revision 2 checks (runs `20261005-0700-f5r2-*`):

- T4: combined both_match 0/20 at residual scale .5 and 1 (v5 0/20); semantic key delivered 0/20 and 1/20. Outcomes at .5: neither 18, content_mismatch 1, instance_only 1 (pair 177015 to 25394, where v5 says content_mismatch). `instance_only` is the abstention state "unclassified", not an attribution. It comes from v5's unchanged rule that an instance key found only by its recomputed pattern counts as distance 0. At 1: content_mismatch 16, neither 4.
- T5: joint near collisions 0/66 under the soft seven-view rule; 4 pairs match semantically, all with perceptual-hash distance at least 11. Donor code against other recipients: 2 different-label semantic matches of 114 (as revision 1).
- Diagnostic: at .2 all 35 succeed. At .4, 29 of 34 succeed. Of the 5 failures, 2 have content not retained (CLIP cosine below .90), 2 are binding failures on retained content and 1 is the first carrier failure, a retained output. On content-retained outputs: .2 34/34, .4 14/17.

Decision under the declared rule: **revision 2 (soft binding, seven-view CLIP) is adopted.** Cost: seven CLIP passes per detection instead of one. The user's visual verdict was given on revision-1 images at the same 52 dB budget.
