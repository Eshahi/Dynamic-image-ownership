# Fu et al. — Diffusion-Based Image Editing: An Unforeseen Adversary to Robust Invisible Watermarks (arXiv:2511.05598, v1 2025-11-07)

Source: https://arxiv.org/abs/2511.05598 — fetched 2026-10-05 (abstract + page). Full PDF not locally hashed; card from page + WebSearch excerpts. Authors: Wenkai Fu et al.

## Claim
Iterative diffusion noising/denoising erases robust invisible watermarks with near-zero detectable payload while preserving perceptual content. Formal proofs that mutual information I(x_w; m) -> 0 as diffusion steps/strength increases, so any decoder fails. Demonstrated by two attacks.

## Mechanism
- **Theory:** models watermark as signal in image; diffusion forward (add Gaussian) then reverse (learned denoise) is a lossy channel. Under conditions on the diffusion kernel, regenerated image retains vanishing information about embedded payload.
- **Attack 1 — Unguided regeneration:** encode image into diffusion latent, add noise at editing strength, denoise with a pretrained diffusion model (content-preserving regeneration).
- **Attack 2 — Guided removal:** integrates the watermark decoder into the diffusion sampling loop, steering each denoising step away from the watermark decision region (stronger, decoder-aware adversary).

## Threat model
Attacker has a powerful pretrained diffusion model (e.g., SDXL/SD1.5 class) and optionally a watermark decoder (for guided variant). No embedding key needed. Threat is realistic post-deployment editing/regeneration at strengths comparable to T3 .4-.6. Evaluated as image-to-image regeneration, not just valuemetric noise/JPEG.

## Numbers
- Table reported in WebSearch excerpts (needs PDF verification for exact config):
  - StegaStamp, TrustMark: ~100% bit accuracy clean -> ~50% (chance) after guided diffusion editing.
  - VINE-R (Lu et al. 2025, the most robust baseline): 100% no-attack -> 24.5% regeneration (unguided diffusion) -> 1.6% guided removal, while LPIPS/PSNR stays high.
- VINE and TrustMark retain ~12-20% under unguided regeneration in some settings; under medium-high editing strength bit accuracy -> 50% (chance).
- General finding across methods: TPR at fixed low FPR collapses to near chance after diffusion editing.

## Limits
- Abstract-level numbers only on this page fetch; exact datasets, strengths, decoder thresholds, and image quality metrics (PSNR/SSIM/LPIPS) need PDF inspection.
- Theory gives an upper bound on survival (fragility), not a survival guarantee — consistent with Zhao Thm 4.3 framing.
- Guided attack assumes decoder access (stronger than F5's T3 which is unguided SD1.5 img2img). Relevance to T3 is via unguided numbers.

## Relevance to F5
- Direct justification for F5's design: if the diffusion channel erases any signal not amplified in the channel's own Jacobian, only encoder-gain directions survive. F5 explicitly targets L amplification through the SD1.5 VAE encoder, making the bound f(e1)=Phi(Phi^{-1}(1-e1)-L*Delta/sigma) vacuous.
- Fu's guided variant is a stronger adversary than T3; if F5 survives unguided .5/.6 partially, Fu predicts it will still eventually fail at higher strength or with decoder guidance. F5 should not claim beyond unguided img2img at pinned SD1.5.
- Suggests next F5 improvement must increase effective L*Delta/sigma *through the full regeneration* (not just VAE), e.g., by including a differentiable surrogate denoising step in the PGD.
