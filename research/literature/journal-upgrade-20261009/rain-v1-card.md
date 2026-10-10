# RAIN v1: bounded primary-source card

Inspected 2026-10-10: [arXiv HTML v1](https://arxiv.org/html/2609.14856v1), Sections 3–4, Tables 1–4. Zilai Li, September 2026 preprint; bibliography key `Li2026RAINv1`. No code, model or dataset downloaded.

- **Claim/mechanism:** a prompt-free learned anchor–residual estimator recovers Gaussian-Shading decision regions without iterative diffusion inversion. It uses VAE input and NAFNet components, not an image-DCT decoder.
- **Training:** Section 4.1 reports 89,600 image/noise pairs and 15,000 training iterations. Generation uses SD1.5, 512 pixels, 15-step UniPC, guidance 5.5; the SOTA comparison uses SD2.1.
- **Numbers:** Table 3 reports 99.99% bit accuracy and 100% detection on clean VAE round trips. Table 4 reports 15.468 million parameters and 14.394 GFLOPs. Table 2's 2.993–3.085 ms/image uses two RTX Pro 6000 GPUs, batch 10, excluding input transfer, VAE encoding and GS decoding.
- **Threat/limits:** the ten-condition table evaluates ordinary distortions, not this thesis's matched DDIM regeneration, delivered donor binding or distinct-owner collision. Reported target FPR is not local calibration. No reproduction or peer-review status is established.
- **Decision:** retain as recent learned-extractor prior art/comparator. It does not validate the proposal's lightweight image-DCT hypothesis or justify replacing its detector silently. No training run is warranted before a small latent-to-observable channel test.
