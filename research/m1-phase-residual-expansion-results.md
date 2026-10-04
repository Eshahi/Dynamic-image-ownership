# Frozen IPS residual expansion: development results

The frozen quality-cap IPS amendment satisfies the clean numerical quality conjunction on all 12 development sources. Correct-owner presence is 9/12 clean and 9/12 after a VAE cycle, but only 8/12 sources pass both. No C0 or wrong-owner query is positive. Thus the expanded carrier gate fails; the successful two-source pilot did not generalize to every retained development source. This is a source-bypass residual operator, not a pure decoder or initial-noise result, and it does not yet implement dual-key content binding or three decision states.

## Receipts and verification

- Expansion: MAIN `.thesis-build/dev-runs/20261004-0057-phase-residual-expansion`, commit `e56ef8c4c06a3490f156983eb3950d8fef80f65e`, duration 57.406 s, completed. Run SHA-256 `5d898e461f73980ded6f477636449a1a067c23e0ec58f6748c018825be053d1f`; manifest SHA-256 `3a08bbf9d04343aa577e46ad28c0faa4d103b7ffb7ce322f6d10ec08caa2dcc1`; conditions SHA-256 `c624271019e0f0fcc485f95a60f68d0e0b12e734754eb3fa5c80773616c1f61b`.
- Retained pilot: MAIN `.thesis-build/dev-runs/20261004-0030-phase-residual`, commit `eca1a533a852d988b213ca47ab24f94dcda5b1f0`, duration 35.657 s, completed. Run SHA-256 `08c97137492d9807ee4ae4962eef689bb0098f21eccd0036cef1d29e96a12615`. Only its preregistered IPS/quality-cap slice joins the expansion; APM/full results remain retained separately.
- Combined analysis: MAIN `.thesis-build/dev-runs/20261004-0059-phase-residual-combined-analysis`, commit `9267e6e4879c7f9101dee9ca75ecc49195b6aa94`, duration 0.281 s. Run SHA-256 `7725dd17dbe020eaf1d3285942fc1f30644aa681bdaf0fc31d150271eaba42fa`. Its family receipts report no errors; `incomplete=false`.

This report independently checked all recorded analysis input-file hashes and all 87 output-artifact hashes across the two source runs, and recomputed every selected owner match count from the recorded extracted bits and frozen payloads. Presence remains exactly `matches >= 82` of 128; no threshold or scientific code was changed. Cap SSE/MSE and clean PSNR were independently recomputed from the recorded integer SSE. No GPU, tensor loading, image inspection, or new experiment was needed.

There are 12 distinct source clusters, 48 distinct image conditions (C0/C1 × clean/VAE), and 192 owner queries (alpha plus beta/gamma/delta). The expansion contributes ten new sources, 40 conditions and 160 queries. The original two pilot sources remain explicit; these 12 selected development sources are not an independent confirmatory sample. Repeated conditions and owner queries do not increase the independent source count. All planned sources are present; none were excluded for a failed readout.

## Per-source clean quality and readout

Quality is against the saved canonical 512×512 RGB8 source. All rows satisfy PSNR >35 dB, SSIM >0.9 and LPIPS <0.1. Lambda is determined solely by the frozen 35.2 dB integer-pixel cap. Counts are correct-owner matches out of 128; signed differences are C1 minus the corresponding C0. Values below 82 fail presence.

| Source | Lambda | Clean PSNR dB | Clean SSIM | Clean LPIPS | Clean C0→C1 | Δ matches | VAE C0→C1 | Δ matches |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1675 (pilot) | 0.427460414 | 35.200011764 | 0.979243759 | 0.016821936 | 66→89 | +23 | 61→90 | +29 |
| 4795 (pilot) | 0.471749898 | 35.200001358 | 0.965493987 | 0.027796268 | 67→99 | +32 | 63→90 | +27 |
| 6012 | 0.415063907 | 35.200009514 | 0.978341614 | 0.010436660 | 72→101 | +29 | 70→88 | +18 |
| 25394 | 0.381271539 | 35.200001640 | 0.974383998 | 0.016930118 | 68→89 | +21 | 58→86 | +28 |
| 80932 | 0.504732261 | 35.200012888 | 0.962834005 | 0.027274977 | 68→115 | +47 | 64→107 | +43 |
| 109798 | 0.339971275 | 35.200002202 | 0.984696770 | 0.009929756 | 64→84 | +20 | 63→82 | +19 |
| 134882 | 0.438043773 | 35.200013451 | 0.970775969 | 0.022475906 | 56→91 | +35 | 61→99 | +38 |
| 147498 | 0.478940834 | 35.200002765 | 0.976335094 | 0.019128267 | 60→97 | +37 | 56→95 | +39 |
| 177015 | 0.396723609 | 35.200002765 | 0.966580315 | 0.018932860 | 64→79 | +15 | 66→80 | +14 |
| 190676 | 0.316038758 | 35.200003046 | 0.982419250 | 0.011546007 | 59→80 | +21 | 63→87 | +24 |
| 468505 | 0.282047859 | 35.200010920 | 0.984829000 | 0.011228321 | 61→85 | +24 | 55→72 | +17 |
| 499768 | 0.210740745 | 35.200002202 | 0.987533400 | 0.009896317 | 62→75 | +13 | 65→75 | +10 |

The ten-source expansion alone gives 7/10 clean and 7/10 VAE positives; six sources pass both. Across all 12, clean failures are 177015, 190676 and 499768. VAE failures are 177015, 468505 and 499768. VAE recovers 190676 (+7 matches versus its clean C1), but loses 468505 (−13). Source 109798 is exactly at the VAE presence boundary (82), not above it.

| Quantity, n=12 source values | Mean | Median | Sample SD | Range |
|---|---:|---:|---:|---:|
| Lambda | 0.388565406 | 0.405893758 | 0.087362399 | 0.210740745–0.504732261 |
| Clean PSNR dB | 35.200006209 | 35.200002905 | 0.000004966 | 35.200001358–35.200013451 |
| Clean SSIM | 0.976122264 | 0.977338354 | 0.008235739 | 0.962834005–0.987533400 |
| Clean LPIPS | 0.016866449 | 0.016876027 | 0.006514282 | 0.009896317–0.027796268 |
| C0 clean matches | 63.916667 | 64 | 4.541893 | 56–72 |
| C1 clean matches | 90.333333 | 89 | 11.219572 | 75–115 |
| C0 VAE matches | 62.083333 | 63 | 4.252450 | 55–70 |
| C1 VAE matches | 87.583333 | 87.5 | 9.848473 | 72–107 |

Mean signed C1−C0 match gain is +26.416667 clean and +25.5 after VAE. Every source has a positive gain, including the presence failures. In each dose there are 48 C0 queries and 36 C1 wrong-owner queries: 0/84 positive clean (matches 53–77), 0/84 positive VAE (49–77). Those 168 null queries share images, payloads and sources; zero observed positives is descriptive and is not a calibrated global false-positive rate.

## Cheap failure diagnosis

The cap arithmetic is consistent on all 12 sources: budget MSE is `65025 * 10**(-35.2/10) = 19.63723606191409` RGB8 units; actual MSE equals integer SSE /786432, ranges 19.63717524210612–19.637229919433594, and never exceeds the budget. Each saved lambda equals the feasible lower bracket endpoint and each upper-minus-lower interval is exactly `2**-36`. The almost identical PSNR values follow from the cap, not from uniformly easy sources. There is no evidence of a reversed bracket, MSE normalization error or cap violation.

Clean failures have mean lambda 0.307834371 versus 0.415475751 for successes; VAE failures have mean 0.296504071 versus 0.419252518. Source 499768 requires the largest unscaled decoded residual norm (73.423452), hence the smallest weight (0.210741), and has the weakest payload-aligned mean score. Source 468505 also has a large residual norm (54.840922), low weight (0.282048), and loses presence after VAE. However, 177015 fails at weight 0.396724 while 109798 succeeds at 0.339971; lambda alone does not determine success. The clean failure 499768 has the highest clean SSIM and lowest LPIPS, so failing clean quality is not the explanation.

The following additional readout diagnostic uses `mean((2*payload_bit−1)*extracted_score)` over all 128 blocks. It is computed from frozen scores, not a fitted detector. Every C1 score shifts toward the payload relative to C0, but attenuation and source-dependent encode/decode behavior leave some counts below the fixed boundary.

| Source | Residual L2 before lambda | Clean aligned score C0→C1 | VAE aligned score C0→C1 |
|---:|---:|---:|---:|
| 1675 | 36.143869 | −0.023295→0.626711 | −0.072860→0.515626 |
| 4795 | 32.623883 | −0.005637→0.706970 | −0.004562→0.621876 |
| 6012 | 37.092086 | 0.168921→0.670202 | 0.179631→0.564559 |
| 25394 | 40.432176 | 0.033459→0.519028 | −0.001701→0.416519 |
| 80932 | 30.467339 | 0.085261→0.973749 | 0.052738→0.925399 |
| 109798 | 45.504346 | 0.014297→0.441802 | 0.042837→0.375362 |
| 134882 | 35.156445 | −0.122912→0.655628 | −0.034116→0.653340 |
| 147498 | 32.251531 | −0.190218→0.665985 | −0.185839→0.623736 |
| 177015 | 38.831136 | −0.018244→0.456427 | 0.003560→0.404309 |
| 190676 | 48.873532 | −0.093211→0.346113 | −0.102705→0.369365 |
| 468505 | 54.840922 | 0.032574→0.311107 | −0.014231→0.197582 |
| 499768 | 73.423452 | 0.015401→0.190449 | −0.020958→0.177829 |

All ten newly enrolled latents have recorded direct latent readout equal to the complete correct 128-bit payload, with zero zero-magnitude block counts. Thus their failures appear after decoded residual composition and suspect VAE re-encoding, rather than failed phase insertion in the saved marked latent. This check uses saved metadata and does not establish which of decoding, attenuation, pixel quantization or re-encoding contributes how much. The earlier pilot does not expose the same embedding metadata in its residual run, so no new direct-latent claim is made for those two sources.

Clean admissibility must not be extended to attacked source fidelity: C1 VAE images have source PSNR mean 24.935507 dB (19.611582–26.903354), SSIM mean 0.687599 (0.491553–0.802939), LPIPS mean 0.077303 (0.057259–0.127480), and source quality conjunction 0/12. Same-arm CLIP retention is 0.962644–0.989169 on all 12; this numerical semantic proxy does not restore source quality or supply a human visual verdict. In particular, 499768 also has the lowest VAE source PSNR/SSIM and highest LPIPS, consistent with a difficult source-dependent VAE channel. This is a descriptive association, not a causal attribution or a reason to remove it.

The next method decision should account for this quality/carrier tradeoff and the different clean/VAE failure sets. No stronger diffusion-regeneration survival, T4/T5 resistance, content authentication, human imperceptibility or family exhaustion follows from this expansion. Human judgments remain missing; all negatives remain in the denominator.
