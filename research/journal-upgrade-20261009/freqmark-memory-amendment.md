# FreqMark serial-backprop feasibility amendment

2026-10-13. Independent method-amendment decision. No execution is asserted here.

## Decision: one new bounded attempt

**Yes**, test `FM-R48-Eq10-SD2community-serial` once. The retained [result](freqmark-reconstruction-results.md) stopped before any update when the second VAE decode overlapped the clean graph: 8.62 GiB allocated, another 256 MiB requested, within a fixed 9 GiB allowance. This identifies a specific implementation obstacle with a mathematically justified remedy. Cached assets remove the previous acquisition cost. A working implementation would enable later comparison design; uncertain native fidelity does not make this small feasibility question meaningless.

This is a new attempt, not continuation or reinterpretation of the terminal `878a736` run. Preserve every old receipt/output and its 580.234-second outcome. The [original protocol](freqmark-reconstruction-protocol.md), [reproduction limits](freqmark-reproduction-check.md), and [article decision](h2-article-viability-decision.md) otherwise stand. Do not spend H2, alter E3, run attacks, adapt capacity, or claim Q1 readiness.

## Sole implementation amendment

For fixed step parameters theta=(a,b) and one presampled latent/pixel noise pair, write the existing objective as:

`L = [h(clean) - .05*PSNR(clean,source) + .25*LPIPS(clean,source)] + h(latent_noisy) + h(pixel_noisy)`.

Its gradient is the sum of those three branch gradients. Zero gradients once. Recompute the FFT-to-latent path for each branch; backward the clean/quality branch, free its graph, backward the latent-noise branch, free its graph, then recompute clean and backward the pixel-noise branch. Accumulate into the same leaf `a.grad/b.grad`; perform exactly one Adam update afterward. Keep parameters unchanged until then. Detach logged scalars; retain no graph between branches. In particular, pixel-noise gradients must flow through its recomputed clean decode, not a detached image.

Presample noise once per step in the original latent-then-pixel order using the unchanged generator. No branch averaging, scaling, clipping, intermediate optimizer update, mixed precision, altered losses or checkpoint selection. Networks remain frozen/eval, with deterministic fp32 execution and TF32 disabled, identically for reference and serial paths. Record execution flags; unsupported deterministic execution ends the attempt. Algebraic equivalence does not imply bitwise or long-trajectory equivalence; test it before real-source optimization.

## Frozen numerical gate

Use the actual pinned VAE, DINO, LPIPS, FFT, clamps and preprocessing, with a **128-square** synthetic RGB input; DINO still resizes to 256/crops 224. This smaller graph is solely an implementation test, never a performance source. Fix RGB values with NumPy PCG64 seed 2026101301, uniform [.1,.9], saved before model calls. Encode once using the unchanged posterior mode. Use alternating 48 target signs and a separate torch noise generator seeded 2026101302.

Compare joint-backward reference versus serial at two initializations: all-zero a/b; and `a[k]=.1*sin(k)`, `b[k]=.1*cos(k)` for flattened integer k starting at zero, calculated once and cloned. For each initialization compare one fresh-Adam update and one update with its populated moments. Before each comparison clone identical parameters and optimizer state from the reference; presample and share exactly the same noise tensors. Do not let trajectory drift contaminate this local equivalence check. Free each reference graph before serial execution. No resize fallback after failure.

All four comparisons must have finite components, nonzero total gradient, actual parameter movement, and pass every following fixed tolerance:

- Each hinge, PSNR, LPIPS and total loss: absolute difference <= `1e-5 + 1e-5*abs(reference)`.
- Concatenated a/b gradient: relative L2 error <= `1e-4`; maximum absolute error <= `1e-9 + 5e-4*max(abs(reference_gradient))`. Use `max(reference_L2,1e-12)` as the relative denominator. Record both norms and cosine similarity as diagnostics.
- Concatenated Adam parameter-update vector: relative L2 error <= `1e-4` and maximum absolute error <= `1e-3`. Compare updates, not only post-update parameter norms; record optimizer state and differences.

Save all residuals and verdicts. These are prospective engineering tolerances, not measured guarantees. A missing, ambiguous or failed comparison stops execution; do not relax tolerances, adjust the fixture or tune a recipe to pass. Passing validates this scheduling implementation locally, not author equivalence.

## Fixed real-source test and envelope

After passing, run only canonical **512-square sources 30 then 72**, the same predetermined 48 bits, seeds, 400 updates and final PNG scoring as the original protocol. Verify reservation IDs/hashes and absence from held-out assignments using existing receipts; check cached asset hashes/configs against recorded acquisitions. No new sources, downloads or infrastructure. Preserve exact recovery, Hamming count, per-source PSNR/SSIM/LPIPS, tensor/PNG disagreement and separate useful-feasibility/strict-budget verdicts.

One **1,800-second inclusive new execution envelope** starts before prerequisite/model setup and includes numerical validation, failed execution, both sources, serialization and scoring. Retain 9 GiB allocated GPU, 10 GiB process RSS, at least 3 GiB available RAM, one science GPU process, USD 0. Reuse existing guards and the observed Windows desktop-PID exclusion mechanism. After ten real-source steps use measured latency to forecast all remaining updates plus 120 seconds for scoring; stop if they cannot fit.

Any numerical/resource failure or deadline ends this amendment: no second launch, recipe sensitivity, precision reduction, cap extension or paid GPU. Commit implementation/config before execution; one ordinary new development run.json and dev-log entry preserve commit, command, inputs, validation and incomplete sources. Native equivalence, competitiveness and ownership security remain unknown even if both images succeed. A further external-comparison design requires a separate evidence-based decision.
