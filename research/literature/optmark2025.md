# OptMark — Robust Multi-bit Diffusion Watermarking via Inference Time Optimization (arXiv:2508.21727, 2025-08-29)

Source: https://arxiv.org/abs/2508.21727 — fetched 2026-10-05 (abstract-level). Authors: inference-time optimization watermark.

## Claim
Multi-bit watermarking (needed for large-scale user tracking) can be made robust to regeneration by embedding at inference time into intermediate diffusion latents, with O(1) memory via adjoint gradients. Dual-watermark design resists both generative and valuemetric attacks.

## Mechanism
- **Embedding locus:** intermediate latents of the diffusion denoising trajectory, not just initial noise. Optimized at inference time (per image) rather than trained encoder.
- **Dual watermark:**
  - *Structural watermark* inserted early in denoising (coarse structure latents) — survives generative/regeneration attacks that preserve structure but change texture.
  - *Detail watermark* inserted late in denoising (fine-detail latents) — survives valuemetric/geometric transforms (crop, JPEG, noise) that preserve details.
- **Optimization:** per-image gradient optimization through the denoising steps; adjoint method reduces memory from O(N) to O(1) in number of steps, making multi-step optimization feasible.
- **Regularization:** tailored terms to keep image quality (imperceptibility) while maximizing decodability.

## Threat model
Multi-bit payload (tens of bits) must survive: valuemetric transforms, geometric transforms, editing, and regeneration attacks. Claims comprehensive robustness — broader than F5's T3 (regeneration only) but includes it.

## Numbers
- Abstract claims "robust resilience" across all four families; no per-threat breakdown on the landing page.
- Requires PDF for exact BER/TPR, payload size, PSNR/LPIPS, and regeneration strength ablations.
- Memory claim: O(N) -> O(1) enables scaling to full denoising trajectories.

## Limits
- Abstract-only inspection; detailed ablations (payload vs robustness vs quality Pareto) unverified.
- Inference-time optimization is per-image cost similar to F5's PGD but through more steps (full denoising chain); wall-clock vs F5's ~37s (VAE-only PGD) unknown.
- No semantic binding component; orthogonal to F5's binding bottleneck.

## Relevance to F5
- **Transferable idea — dual-locus embedding:** F5 embeds 320 chips into a single DCT band (radius 4-32) of the VAE latent via PGD. OptMark suggests splitting payload across coarse vs fine loci (early vs late latents, or equivalently low-DCT vs high-DCT bands) with unequal error protection. For F5, this maps to: protect a small subset of chips in the most regeneration-robust sub-band (lower DCT radii 4-12) with higher margin/weight, and use remaining chips for capacity. This is a reweighting, not a new encoder.
- Closest to F5 among 2025 papers in being *optimization-based at embed time* rather than trained encoder — so its dual-watermark trick ports directly to F5's PGD.
- Trade-off: dual-locus adds complexity; benefit only matters if F5's uniform weighting is the limiter, which current stress grid (carrier zero failures) suggests it is not — binding is the bottleneck.
