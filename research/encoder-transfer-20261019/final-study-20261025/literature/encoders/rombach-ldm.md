# Rombach et al. 2022 — latent diffusion (V2)

- **Exact source:** Robin Rombach, Andreas Blattmann, Dominik Lorenz, Patrick Esser, Björn Ommer, *High-Resolution Image Synthesis with Latent Diffusion Models*, arXiv:2112.10752v2, 2022. https://arxiv.org/html/2112.10752v2. Accessed 2026-10-25 UTC.
- **Method inspected:** §3.1–3.2, Appendix G. Encoder E maps RGB to spatially compressed continuous or quantized latent; decoder D reconstructs. First stage uses perceptual plus patch-adversarial objectives, then is frozen for latent diffusion. The paper compares spatial factors and code types.
- **Experiment inspected:** §4.1, Appendix D.2/Table 8. The autoencoder zoo was trained on OpenImages and evaluated on ImageNet validation; f8 KL has 4 channels in Table 8. The table evaluates reconstruction, not watermark survival or cross-encoder transfer.
- **Direct evidence:** SD1-family LDM's first-stage representation is trained separately from the diffusion denoiser. This source alone does not identify the exact SD1.5 checkpoint bytes or rule out training overlap with later AEs.
- **Inference for this study:** A mark optimized through a particular E can depend on its Jacobian, but paper does not establish that dependence or predict transfer loss.
- **Limits:** The selected SD1.5 implementation and scaling factor must be verified from its specific checkpoint/config; do not equate all LDM first-stage models. No regeneration-watermark measurements.
- **Cached artifact:** `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/cache-et-final/papers/enc-ldm-v2.html`; SHA-256 `F0D19A78867A200210C492226E59E85AA85BB5795B4FABC4FF4EEF50BEEC3D27`.
