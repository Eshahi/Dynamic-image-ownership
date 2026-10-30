# Coarse-lattice mark: a proposal and its first offline evidence

2026-10-30. Exploratory development work on the 60 Stage 2 development sources. CPU only, no model run for T3, no held-out data. Design and evaluation use separate halves of the sources. The approved F6 package is unchanged. Under the project's rules this is an image-domain comparator, not the proposal's latent method.

## The idea

Earlier marks add a pattern and then try to carry it through regeneration. This one adds no fixed pattern. It moves secret DCT coefficients of the image's own content onto a secret lattice.

1. **Measure the channel first.** Treat each regenerator like a lens under test: gain and new noise per frequency band, per colour channel, black-box.
2. **Write.** Move the chosen coefficients to the nearest lattice point. Closed form, no model.
3. **Read with no reference.** Score how close the coefficients sit to the lattice. No model, no stored descriptor.
4. **Bind without payload.** The lattice is derived from the owner key and a 16-bit coarse sketch of the image, read from luma coefficients the mark never touches. No content bits are transmitted. The reader tries every sketch within Hamming radius 2 and every step size, and pays for those tries in its threshold.

For any image that does not depend on the key, each reader term is an independent bounded symmetric variable over the random dither. The project's Bentkus-Dzindzalieta bound therefore applies per image, with no model of image statistics. Threshold at 1e-6 per claim: z = 6.15 for 137 sketches and 6 step sizes.

## Measured from saved images

Root mean noise per DCT coefficient, 0-255 scale, band 32-48:

| Channel | SD1.5 .2 | SDXL .2 | Kandinsky 3 .2 |
|---|---:|---:|---:|
| Luma | 132 | 98 | 78 |
| Red-green | 33 | 28 | 25 |
| Blue-yellow | 43 | 38 | 32 |

Gain of a change depends on what it looks like, luma band 64-96:

| At | Image content | VINE-R | v5 | F5 |
|---|---:|---:|---:|---:|
| SD1.5 .2 | .74 | .44 | .29 | 1.76 |
| SDXL .2 | .82 | .62 | .33 | .35 |
| Kandinsky 3 .2 | .87 | .74 | .48 | .60 |

F5 is amplified about 1.8 times by the encoder it was written against and attenuated to about a third by SDXL. A change that does not look like image content is attenuated more than image content is.

## Results with real pixels, no simulation

Claimed owner is the donor's owner. Threshold z = 6.15.

| Test | Chroma layout, k=2048 | Luma layout, k=512 |
|---|---:|---:|
| 128×128 patch copied | 0/300 | 0/150 |
| 256×256 patch copied | 0/300 | 0/150 |
| 384×384 patch copied (56% of the image) | 2/300 | 2/150 |
| Exact residual copied (stronger attacker with the unmarked donor) | 0/300, was 73/450 before binding | 0/150 |
| Regenerated copies of the never-marked image | 0/180 | 0/180 |
| PSNR, median / minimum | 39.86 / 37.97 | 42.16 / 38.01 |
| SSIM, median / minimum | .994 / .918 | .983 / .947 |
| LPIPS, median / maximum | .028 / .071 | .016 / .172 |

Real look-alike pairs were not run. For an unmarked look-alike the bound above applies directly.

## Simulated T3

T3 is not measured yet. Simulation: real regeneration of the unmarked image, plus the mark times an assumed gain. Evaluation half, seeds 13 and 14, per-image rate at 1e-6, sketch misses counted as failures. Calibration uses SD1.5 seed 12 only.

| Layout and assumed gain | SD1.5 .1 | .2 | .4 | SDXL .1 | .2 | .4 | K3 .2 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Chroma, gain as measured for v5 | 1.00 | .77 | .00 | 1.00 | .93 | .00 | 1.00 |
| Chroma, gain as measured for VINE-R | .97 | .28 | .00 | 1.00 | .54 | .00 | .96 |
| Chroma, fixed gain .5 | 1.00 | .97 | .42 | 1.00 | 1.00 | .86 | 1.00 |
| Chroma, fixed gain .3 | .98 | .76 | .06 | 1.00 | .88 | .25 | .97 |
| Luma, gain as measured for VINE-R | .92 | .12 | .00 | 1.00 | .97 | .00 | 1.00 |
| Luma, gain as measured for v5 | .25 | .00 | .00 | .97 | .18 | .00 | .97 |

Real comparators, source majority on the same 60 sources:

| Method | SD1.5 .1 | .2 | .4 | SDXL .1 | .2 | .4 | K3 .2 | Median PSNR | Strict quality |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| F5 r2 (C) | 1.00 | .95 | .65 | .00 | .00 | .00 | .08 | 44.96 | 60/60 |
| v5 r3 (C) | .78 | .45 | .05 | .83 | .20 | .00 | .95 | 36.85 | 60/60 |
| VINE-R (presence, no content binding) | 1.00 | 1.00 | .78 | 1.00 | 1.00 | .75 | 1.00 | 35.14 | 31/60 |

## Known problems

1. **The real gain of a lattice nudge is unknown.** It decides everything. The method needs roughly .3 to .5 or more. Measured gains of other marks in the chosen bands run from about .2 to .55.
2. **Visible flaw.** At 3x zoom the chroma layout shows pink and green blotches on flat areas despite passing PSNR, SSIM and LPIPS. The luma layout shows a ripple on the dark flat image and passes LPIPS on 59/60 only. A visibility-weighted writer is required before any quality claim. Candidate: minimum weighted-norm moves that hit the same lattice targets while placing energy where a spatial mask allows it.
3. **Strength .4** is not reached under measured gains.
4. **A secret owner key is required.** The proposal's public-derived profile cannot use this. It must be declared under `research/threat-model.md`.
5. **Prior art is only lightly checked,** about ten searches. No result combined a content-derived lattice with regeneration, which is not evidence of novelty.
6. Unweighted, per the scope rule: a grayscale conversion would remove the chroma layout.

## Decisive next test

One real regeneration grid on the rented server, development sources only, no held-out data. Layouts compared inside one run: chroma, luma, mixed, lower-band. 30 design sources, the seven cells above, seeds 12-14. About 1 hour, under USD 1 at the historical rate. It measures the real gain per band. The chosen layout is then scored on the 30 evaluation sources.

Kill rule, fixed now: stop this line if no layout reaches at least 50% real detection on every .2 cell at the 1e-6 threshold with strict quality on every mark. Passing this rule does not establish the visual quality; the visibility-weighted writer and a human verdict are separate gates.
