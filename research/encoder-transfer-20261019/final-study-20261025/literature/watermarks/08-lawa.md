# LaWa — V2 primary-source card

Source: Ahmad Rezaei, Mohammad Akbari, Saeed Ranjbar Alvar, Arezou Fatemi and Yong Zhang, *LaWa: Using Latent Space for In-Generation Image Watermarking*, arXiv:2408.05868v3, 30 May 2025. [Inspected version](https://arxiv.org/html/2408.05868v3). Inspected 25 October 2026. Artifact/hash: manifest key `lawa`.

**Direct evidence — mechanism (§3).** Learned message-conditioned residual modules inject information at several VAE-decoder upsampling stages. A trained image extractor recovers bits. The base decoder is frozen while embedding modules learn its latent-to-RGB mapping. Detection needs the extractor/message, not generator inversion. Arbitrary images can enter via encoding.

**Direct evidence — experiments (§4, Table 1).** For the 48-bit version, reported PSNR/SSIM/LPIPS are 33.52/.86/.04, with bit accuracy 1 clean and .94 combined. Section 4.7/Figure 7 directly studies learned compression, KL-VAE and VQ-VAE removal. Under the same KL-f8 autoencoder used for generation, LaWa retains 85% bit accuracy versus 55% for Stable Signature. The authors calculate attack PSNR against the marked image, unlike the cited Stable Signature comparison.

**Limits / transfer.** This is actual cross-autoencoder reconstruction-attack evidence, but not a matched independent-SDXL encoder-only experiment. Appendix A.4 trains separately for different autoencoders. Appendix A.5's empirical FPR denominator/exponent wording is inconsistent; no tiny-FPR claim is adopted here.

**Agent inference for F5.** Same-autoencoder vulnerability is method dependent; decoder modules can differ from decoder fine-tuning and encoder-directed residual writing.
