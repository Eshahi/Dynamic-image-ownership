# Guidance Watermarking — V2 primary-source card

Source: Enoal Gesny, Eva Giboulot, Teddy Furon and Vivien Chappelier, *Guidance Watermarking for Diffusion Models*, arXiv:2509.22126v2, 7 May 2026. [Inspected version](https://arxiv.org/html/2509.22126v2). Inspected 25 October 2026. Artifact/hash: manifest key `guidance`.

**Direct evidence — mechanism (§4, Eqs.5–7).** Gradients through the VAE and a pretrained differentiable image watermark extractor guide diffusion updates toward the desired feature direction/message. Multiple image transformations and gradient conflict handling improve robustness. Generation/extractor weights are not retrained. Detection needs the pretrained extractor and reference feature/message, not inverse diffusion. Its false-alarm formula assumes isotropic null features (§4.1, Appendix C).

**Direct evidence — experiments (§5).** The method is instantiated on SD2, FLUX.1-dev and SANA with 1,000 prompts. Table 1 reports G-SSig PSNR/LPIPS 25.4/.07 on FLUX and 28.6/.02 on SANA. Section 5.3/Figure 4 tests same-model VAE purification, latent-noise regeneration and adversarial removal; regeneration uses 500 images and 2–10 diffusion steps. Appendix C examines calibration pitfalls in competing p-values.

**Limits / transfer.** Multi-generator applicability is not transfer of one frozen marked residual across independently trained attack autoencoders. Purification uses each model's original VAE. Analytic feature assumptions require empirical checking on the deployment null.

**Agent inference for F5.** This recent precedent prevents equating all frozen-VAE gradient watermarking with initial-noise methods. F5 still differs by optimizing an image-domain writer through an encoder.
