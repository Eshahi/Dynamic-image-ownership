# Round 3 distortion-budget bounds

Author assistance, 2026-10-29. This is a source inspection and scalar derivation, not an independent review, scientific result, gate amendment, or proposed variant. No image, encoder, gradient, metric, or scientific module was run or imported. Numerical constants below were evaluated with isolated stdlib Python only.

## What each budget centers on

Let RMS denote the Euclidean norm divided by the square root of the number of RGB components. Express RMS in byte levels, so source-relative PSNR is `20 log10(255 / RMS)`; the strict PSNR > 35 condition means RMS < 4.53461250.

The actual sequence is source RGB8 -> robust float write -> RGB8 -> first fragile write -> RGB8 -> refinement float write -> RGB8 -> second fragile write -> RGB8. The source is required to be 512 x 512 x 3 RGB8. The robust stage is centered on the source; the refinement is centered on the already rounded, robust-plus-first-fragile image. There is **no final source-centered projection**. See `scripts/tifs_writer.py:344-380` and `:400-421`.

For robust target P, the ideal-arithmetic robust radius in normalized RGB is `sqrt(N) 10^(-P/20)`, where N = 3 x 512 x 512. Each update clips into [0,1], then projects the actual displacement into that L2 ball. The corresponding byte RMS limit is `r(P) = 255 10^(-P/20)`. Refinement uses 50 steps and 58 dB, hence `r_ref = 0.32102598` byte RMS, relative to its own input. These are maximum radii, not requirements to exhaust energy or achieve an exact PSNR.

The same geometry applies to `f5-budget`, which calls retained `robust_pgd` directly (`tifs_writer.py:347-350`; `scripts/f5_latent_codec.py:175-215`). Equality to the retained F5-r2 optimization calls is at P = 52, where retained F5's refinement also equals 58. At other P, this new control retains the explicitly fixed refinement58; it is not the unchanged F5 embedder parameterized by P, whose refinement formula is `max(P+6,50)` (`f5_latent_codec.py:246-250`).

## Fragile budget: a deterministic bound is possible

The inherited profile has instance PSNR 47, noise standard deviation 8, and three passes (`experiments/c4-v5-two-tier-regeneration-v1/profile.json:31-33`). Its luma is `0.299R + 0.587G + 0.114B` without linearizing sRGB (`scripts/revised_watermark_v4.py:1193-1198`). F6's fragile body uses `quantize=False, reserve_rounding=True`, then copies the luma change equally into all three RGB channels before RGB8 conversion (`tifs_writer.py:382-398`). The profile's proportional-color mode and robust PSNR35.5 setting do not impose a final RGB limit on this copied F5 body.

Let M = H x W, K = 320, and let y be the luma vector at the start of one fragile call. For the actual unique DCT frequencies and normalized, disjoint chip assignments, write U for the K x M orthonormal-row projection matrix. Thus `UU^T = I`. This follows from the orthonormal DCT construction (`revised_watermark_v4.py:162-186`), block analysis (`:385-403`), balanced disjoint carrier assignment and square-root-count norms (`:679-700`), and fragile synthesis (`revised_watermark_v5.py:825-839`, `:862-869`). The instance pattern w has entries +1 or -1 (`revised_watermark_v5.py:352-360`).

The reserved scalar design budget is

`T = max(255^2 10^(-47/10) - 1/12, 0.25 x 255^2 10^(-47/10)) = 1.214085987` byte-luma squared.

Here `1/12` is the code's rounding allowance, not a worst-case rounding guarantee (`revised_watermark_v4.py:86`; `revised_watermark_v5.py:848-850`). Put h = Uy and S = ||h||^2/K. The retained host-rejection search chooses lambda and amplitude a satisfying

`a^2 + lambda^2 S = TM/K`.

See `revised_watermark_v4.py:762-780`. The code itself describes this as a cost averaged over a key pattern. For a realized image and pattern the target displacement is `d = -lambda h + a w`, so

`||d||^2 = TM - 2 lambda a <h,w>`.

Neither the sign nor the value of this cross term is fixed. In particular, nominal instance PSNR47 is not a realized deterministic limit of 47 dB. Cauchy-Schwarz gives the source-independent bound

`||d|| <= lambda ||h|| + a sqrt(K) <= sqrt(2TM)`.

This requires no independence or random-image assumption; even a content-dependent w obeys it. The retained noise parameter affects lambda and a, but not this upper bound.

The three passes target the same t = h+d, recomputing the current projection after each clipped pass (`revised_watermark_v5.py:853-880`). Each is exactly, in ideal arithmetic,

`y_(j+1) = projection_[0,255]^M (y_j - U^T(U y_j - t))`.

To handle clipping without assuming it disappears, let `f(y) = 0.5 ||Uy-t||^2`. Its gradient has Lipschitz constant one. The projection inequality and the quadratic upper bound give

`f(y_(j+1)) <= f(y_j) - 0.5 ||y_(j+1)-y_j||^2`.

Consequently, over p passes, the sum of squared increments is at most `2f(y_0) = ||d||^2`. Cauchy-Schwarz over increments then gives

`||y_p-y_0|| <= sqrt(p) ||d|| <= sqrt(2pTM)`.

For p = 3, the total luma RMS of one fragile call is at most `sqrt(6T) = 2.69898424` byte levels. This is a conservative finite-pass bound, not a statement that three passes generally add that much error. If clipping never activates, the first pass reaches t and subsequent passes add zero in exact arithmetic; its bound then improves to `sqrt(2T)`.

Adding an identical luma change to R,G,B preserves this RMS before RGB clipping. Clipping each channel into [0,255] cannot increase its displacement from the input RGB8 image, which already lies in that box. Rounding adds at most 0.5 byte per component. Thus each entire fragile call, including the subsequent RGB8 conversion, has byte RGB RMS at most `sqrt(6T) + 0.5`.

## Source-relative conservative bound

All four RGB8 conversions have an individual rounding error of at most 0.5 byte per component. This is a worst-case magnitude statement, not the stochastic 1/12 MSE approximation. By the triangle inequality, the full writer therefore has the ideal-arithmetic source-relative bound

`RMS_final <= B(P) = r(P) + r_ref + 2 sqrt(6T) + 4 x 0.5`.

Equivalently, `||final-source||_2 <= sqrt(N) B(P)` and `PSNR_final >= 20 log10(255/B(P))`. In a general inherited profile with p passes and instance target I, replace T by `max(255^2 10^(-I/10)-1/12, 0.25 x 255^2 10^(-I/10))` and replace 6 by 2p. A trivial bound of 255 RMS also holds from the RGB range.

| Robust target P | Robust radius, byte RMS | Robust energy capacity versus 52 | Full conservative RMS upper bound | Implied PSNR lower bound, dB |
| --- | ---: | ---: | ---: | ---: |
| 52 | 0.640531 | 1.0000x | 8.359525 | 29.6872 |
| 46 | 1.278027 | 3.9811x | 8.997022 | 29.0488 |
| 42 | 2.025537 | 10.0000x | 9.744531 | 28.3556 |
| 38 | 3.210260 | 25.1189x | 10.929254 | 27.3590 |

These intentionally loose bounds do not predict failures. They show that **the inspected budget structure alone does not certify final PSNR > 35**, even at 52. Actual displacements may cancel, leave much of a budget unused, undergo little clipping, and have much smaller cross terms. Conversely, adding nominal MSEs without their cross terms is not a deterministic proof.

The derivation above treats DCT orthogonality, norms, clipping and arithmetic mathematically. Actual PGD uses float32 (`f5_latent_codec.py:98-99`); source/input casting alone can add up to about 255 x 2^-25 byte RMS per conversion into float32. Projection arithmetic and finite-precision DCT synthesis also have numerical residuals. No machine-arithmetic error certificate was derived. Strictly for the implementation, write the displayed bound as `B(P) + E_numeric`, with E_numeric the unbounded-here accumulated numerical error. The table is the proved scalar model's result, not a bit-exact runtime guarantee. Ordinary rounding to RGB8 is already explicitly included and is not part of E_numeric.

## What 38 dB plausibly buys, and what it does not

At P = 38, the robust-stage radius is 3.210260 versus the source-relative PSNR35 limit of 4.534612. Its nominal 3 dB gap is about a factor of two in MSE. Refinement consumes up to another 0.321026 RMS relative to its own center; under worst-case alignment that leaves 1.003327 RMS for everything else, before any rounding or fragile writes. This is not enough to absorb their conservative bounds.

For scale only, suppose both optimizers use their full radii, fragile calls behave like one unclipped write with mean-square T, all stage changes have zero pairwise cross terms, and the four rounding errors each have independent uniform variance 1/12. The illustrative total would be

`RMS^2 = r(P)^2 + r_ref^2 + 2T + 4/12`.

That arithmetic gives 36.9348 dB at P = 38. It establishes that plausible low-correlation behavior could leave headroom; it is **not an expected value established for this writer**, a probability of passing, a measured PSNR, or a guarantee. The second fragile write reuses structure and follows refinement, so the independence assumption is especially unverified. No outputs were inspected or generated to support it.

Finally, equal nominal budgets across F6 and `f5-budget` constrain the same maximum robust displacement radius. They do not force equal realized RMS, equal final PSNR, equal spatial or frequency structure, or equal perceptual quality. The objectives can use different directions and different amounts of the available energy; the subsequent source-dependent fragile writes differ too. Nothing in these scalar L2 calculations establishes SSIM, LPIPS, human acceptability, mark readability, or regeneration survival. Those remain unmeasured here. No gate, variant, or experiment is changed by this note.
