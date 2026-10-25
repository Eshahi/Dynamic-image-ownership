# Stable Signature — V2 primary-source card

Source: Pierre Fernandez, Guillaume Couairon, Hervé Jégou, Matthijs Douze and Teddy Furon, *The Stable Signature: Rooting Watermarks in Latent Diffusion Models*, arXiv:2303.15435v2, 26 July 2023. [Inspected version](https://arxiv.org/html/2303.15435v2). Inspected 25 October 2026. Artifact/hash: manifest key `stable-signature`.

**Direct evidence — mechanism (§4).** A pretrained image watermark extractor supplies the message objective while the latent diffusion image decoder is fine-tuned for a fixed 48-bit signature. The denoiser remains unchanged. Detection needs the neural image extractor and expected signature, without diffusion inversion or the original image. Training therefore changes the decoder's image mapping; it does not write bits into initial noise.

**Direct evidence — experiments (§§5–6, Table 1).** Text-to-image results report PSNR 30.0 dB, SSIM .89, and bit accuracy .99 clean/.92 under the combined attack. Appendix B discusses whitening and the independent-bit false-positive model.

**Direct evidence — autoencoder attacks (§7.1, Figure 7).** Other autoencoders require PSNR below 26 dB to reduce extraction near chance. The autoencoder used for generation is a stronger attack: watermark removal occurs with PSNR above 29 dB. Thus the same-autoencoder advantage is an attack advantage here.

**Limits / transfer.** This directly compares autoencoder reconstruction attacks, but does not isolate an SD1.5-to-SDXL encoder-only substitution. Model purification and collusion are additional limitations (§7).

**Agent inference for F5.** This counterexample rules out a universal claim that embedding with an autoencoder necessarily protects against that autoencoder. Insertion site and training objective matter.
