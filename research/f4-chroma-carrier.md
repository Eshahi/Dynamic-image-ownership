# Family 4: chroma-channel carrier (development, 2026-10-04/05)

Designed, implemented and tested by Claude (Anthropic) at the user's request ("find the fourth family idea yourself and test it"). Exploratory development evidence on the twelve development sources only; no held-out data. Human visual verdicts: none.

## Idea: measure the attack's transfer function first

Regeneration removes what the denoiser treats as noise. Which part of an added pattern survives therefore depends on spatial frequency and colour, and the score a blind correlation detector sees after the attack scales with *gain / sqrt(host power)* in the band it reads: gain from the attack, host power from the photograph itself. Both can be measured.

`scripts/f4_transfer_probe.py` (run `.thesis-build/dev-runs/20261004-2130-f4-transfer-probe`, 792 of 795 attacks completed, 3 safety blocks) added fixed random patterns limited to one radial band and one colour axis (luma; red-green; blue-yellow) at 38 dB to each development source, ran the pinned SD1.5 img2img with the same seed on x and x+d, and measured the kept fraction and the host power. Median over the twelve sources at strength .2, score at a 35.5 dB budget (minimum over sources):

| Band, cycles/image | Luminance (v5's channel) | Red-green | Blue-yellow |
|---|---|---|---|
| 8-16 | 1.7 (1.0) | 15.6 (5.9) | 7.8 (4.8) |
| 16-32 | 3.5 (2.7) | 22.5 (7.2) | 16.9 (7.5) |
| 32-64 | 6.8 (5.2) | 6.3 (1.1) | 7.7 (2.4) |

Photographs carry one to three orders of magnitude less chroma than luminance power at 8-32 cycles/image, and img2img keeps chroma there about as well as luminance (median gain .46 and .28 at .2), so per unit of mean squared error the chroma channel is six to nine times better. Above 32 cycles/image img2img keeps almost no chroma (gain .02).

## Design

`scripts/f4_chroma_codec.py` keeps v5 r3 unchanged except for one thing: the robust (semantic key) tier reads and writes the isoluminant Cr plane (BT.601 full range; RGB direction (1.402, -0.714, 0) leaves Y and Cb unchanged) instead of luminance. Keys, carriers, key test, Bentkus-Dzindzalieta threshold, decision table, fragile instance tier and perceptual hash are v5's. Options: both chroma planes with independent carriers (pooled chip totals, so the null stays a weighted sum of random signs), and an embedder-side Gaussian smoothing of the chroma change (v5 renders each 32x32 coarse block separately, which leaves edges at block borders that regeneration does not keep and that are visible). Profiles in `experiments/f4-chroma-carrier/`. Image-domain comparator, like v5; not the proposal's latent method.

## Results (M1a gate, `scripts/f4_gate.py`, paired with v5 dev-001 by source/strength/seed)

v5 r3 reference quality on the same sources: PSNR mean 37.1 dB (min 35.3), LPIPS mean .0176 (max .0383).

| Variant | PSNR mean | LPIPS mean (max) | .1 F4/v5 | .2 F4/v5 | .4 F4/v5 | Gate |
|---|---|---|---|---|---|---|
| r1 v5 profile in Cr | 44.2 | .013 (.040) | 7/26 | 2/18 | 0/2 | fail |
| r2 band <= 32 c/i, chroma mask 1.0 | 41.0 | .032 (.069) | 24/26 | 18/18 | 5/2 | fail |
| r2 mask 1.5 | 38.5 | .059 (.116) | 27/25 | 21/18 | 13/2 | robustness passes, LPIPS fails on 1/12 |
| r3 Cr+Cb, mask 1.0 | 38.0 | .050 (.105) | 27/26 | 23/17 | 5/2 | robustness passes, LPIPS fails on 1/12 |
| r4 mask 1.5, smoothing 4 px | 44.6 | .013 (.042) | 13/25 | 5/17 | 0/2 | fail |
| **r4 mask 2.0, smoothing 4 px (selected by the quality-only rule)** | 43.4 | .017 (.048) | 25/25 | 13/17 | 2/2 | **fail** |
| r5 mask 2.5, smoothing 3 px (post-hoc frontier point) | 40.3 | .041 (.083) | 27/26 | 23/17 | 6/2 | **passes as written**, post-hoc |

Paired identities are 27 or 28 per strength (ten sources with v5 T3 rows, three seeds, safety blocks on source 6012 excluded where either side is missing). Across all variants: unmarked C0 and wrong-owner calls were never detected; clean C1 was both_match on 12/12; after any regeneration the instance tier is gone (semantic_only), as in v5.

**Selection rule.** Before the r4 attack results were read, the final setting was fixed by quality alone: the most robust-tier energy with worst-case LPIPS <= .05 and mean LPIPS about v5's (quality sweep on CPU over mask 1.5-3.0 and smoothing 2-4 px). Only mask 2.0 with 4 px smoothing met it, and it fails the gate. r5 was added afterwards to map the frontier at the gate's own LPIPS limit and is reported as post-hoc.

## Copy-paste (T4) and colour attacks

- `scripts/f4_t4.py` on r2 mask 1.5 (v5's twenty donor/recipient pairs, residual transfer .5 and 1): combined both_match on recipients 0/20 at both scales (v5 0/20); the mark was delivered in 20/20 (binding none). Combined outcomes at .5: content_mismatch 13, content_uncertain 4, semantic_only 3 (v5: 14, 3, 1 and 2 neither). Public-projection arm not reproduced.
- Same check on r5: combined both_match 0/20 at both scales, delivered 20/20. Combined outcomes at .5: content_mismatch 8, content_uncertain 10, semantic_only 2 (v5 14, 3, 1, 2 neither); at 1: 18 and 2 (v5 20 mismatch). Equal on false attribution, less decisive than v5 at scale .5. T5 (same-topic pairs) was not rerun: the semantic codes come from CLIP and the perceptual hash from luminance, which the chroma tier does not change.
- `scripts/f4_colour_attacks.py` on r2 mask 1.5 and on r5 (same counts): saturation x0.5, hue 10 degrees and JPEG q75 4:2:0 keep 12/12; **grayscale removes the mark on 12/12** while CLIP cosine to the source stays .87. A luminance mark (v5) is unaffected by grayscale. This is a cheap removal attack (T2 class), visible as loss of colour.

## Conclusion

0. **Gate status.** r5 meets M1a as written: strict clean quality on all twelve (PSNR >= 40.1, SSIM >= .967, LPIPS <= .083), clean both_match 12/12, zero detections on 1,113+ negative calls, more paired detections than v5 at .1 (27 vs 26, a one-identity margin) and .2 (23 vs 17), and no T4 false attribution. It is a provisional pass, not an acceptance: it was the seventh variant and chosen after seeing earlier results, the pre-declared quality-matched pick (r4 mask 2.0) failed, its mean LPIPS is 2.3 times v5's, grayscale removes it, and the counts are small dependent development counts. It needs a human visual comparison with v5 and the held-out confirmatory test before any claim.
1. The physical finding is solid and reusable: against SD1.5 img2img, mid-band chroma (8-32 cycles/image) is a far better channel per unit of mean squared error than luminance, and high-band chroma is useless.
2. As a watermark, the chroma carrier does **not** beat v5 at equal perceptual distance: LPIPS penalises chroma noise more than PSNR does. Every variant that beats v5 at .1 and .2 has about three times v5's mean LPIPS; at v5's LPIPS it ties at .1 and loses at .2. Family 4 fails M1a under the pre-declared quality-matched selection.
3. Grayscale conversion removes it completely.
4. Worth trying next, as a new hypothesis rather than a rescue: pooling a luminance robust tier with the chroma tier in one statistic (graceful under grayscale), and a perceptual (CIELAB/CSF-weighted) mask instead of block caps, so the energy goes where chroma change is least visible. Human visual assessment is needed to decide whether r2/r3-level chroma visibility is acceptable at all.
