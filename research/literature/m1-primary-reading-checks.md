# Primary researcher verification, 2026-10-03

These supplementary reading notes are observations by the parent researcher, not a replacement claim ledger or an independent milestone review. Existing paper cards and bibliography preserve the full citation records. No held-out evidence was inspected.

## Regeneration theorem scope

Opened [Zhao et al., v3](https://arxiv.org/html/2306.01953v3), method, theorem statements, Appendix C, proof and Appendix E. The removal bound assumes an additive Gaussian channel with shared variance and a bounded embedding displacement. Its dimensionless separation is displacement divided by noise standard deviation. Some displayed Appendix D normalization equations use sigma squared inconsistently with the theorem; do not propagate that normalization into our derivation. Utility is conditional on successful denoising of the unmarked counterpart. Remark C.6 explicitly excludes an automatic application to ordinary input-dependent VAE noise. Our deterministic posterior-mode round trip is empirical evidence, not that theorem's certified randomized attack. Appendix E uses caption/prompt generation for Tree-Ring; its robustness is not evidence of imperceptible modification of an existing photograph.

## PRC false-positive quantifier

Opened [PRC watermark v2](https://arxiv.org/html/2410.07369v2), Sections 3.1–3.2, Theorem 2 and experimental implementation. The key-independent fixed-image/random-key quantifier matters. A public key derived from the same image is not automatically covered. Our wrong-owner counts cannot inherit that guarantee. The experimental extractor uses diffusion inversion and does not establish a lightweight image-only extractor. Its solver and guidance settings must not be silently equated with the local DDIM adaptation of another baseline.

## Initial-noise carrier and observability

Opened [Tree-Ring v3](https://arxiv.org/html/2305.20030v3), Sections 2.1, 3 and 4.1. The mark lives in Fourier structure of initial noise; detection reconstructs noise using diffusion inversion. The Gaussian null statistic and estimated variance are assumptions of that detector, not an unconditional guarantee for all content-derived image carriers. The local family A terminal-latent optimization and family C VAE extraction are explicitly different observation channels. A Fourier translation phase is frequency dependent; do not interpret a translation as one global phase across all coefficients.
