# FreqMark — Invisible Image Watermarking via Frequency Based Optimization in Latent Space (arXiv 2410.20824)

- Authors: Yu et al. (Monash/CSIRO). v1 2024-10-28.
- URL: https://arxiv.org/abs/2410.20824
- Access: arXiv landing page + abstract, 2026-10-05. No full-PDF table extraction.
- Status: preprint.

## Claim
Optimizing the latent frequency space (after VAE encoding) gives a flexible quality-vs-robustness tradeoff and resists regeneration attacks.

## Mechanism
1. Encode image to VAE latent. 2. Unconstrained optimization over latent frequency representation. 3. Decode; extraction via pre-trained image encoder. 4. Flexible bit length (reports 48 bits).

## Threat model
Post-hoc watermark on existing images; regeneration attacks are the stated weakness of prior work. Abstract says various attacks.

## Numbers
Bit accuracy >90% for 48-bit message under various attacks (landing page). No PSNR/SSIM/TPR at fixed FPR quoted on landing page.

## Limits
Abstract/HTML only here; no Pareto. Detector is learned encoder (model-dependent). No pinned SD1.5 VAE transfer shown.

## Relevance to F5
Direct precedent for frequency-shaped latent optimization. F5 already does PGD through SD1.5 VAE encoder into DCT band 4-32 with keyed spreading and encoder gain. FreqMark suggests weighting inside band and unconstrained vs box-constrained optimization.
