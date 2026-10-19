# BiSLW — V2 new primary inspection

Aryan Pandit, *BiSLW: Bi-Spectral Latent Watermarking for Generative Diffusion Models*, arXiv 2607.02643v1 (2026-07-02). [Primary](https://arxiv.org/html/2607.02643v1), [official repository](https://github.com/OVER-CODER/BiSLW). Read §§3.1–3.7, §§4.1–4.3/Table 2, 2026-10-19. Repository claims ECCV2026; venue not independently checked.

Learned watermark-conditioned residuals occupy complementary DCT bands before VAE decoding. Extraction encodes the suspect and uses learned band decoders. Training includes regeneration. The paper reports 100,000 MIRFLICKR images, 40 epochs, 32/48-bit settings, 37.40dB/0.91 on generated-image quality and .96 bit accuracy at regeneration timestep 250. Bit accuracy is not presence at our fixed FPR. No F5 or matched independent-encoder result is established by these numbers.

This directly pre-empts a broad VAE-DCT-carrier novelty claim. F5's narrower distinction is per-image pixel-gradient writing through a frozen encoder with its fixed keyed chip statistic. Released checkpoint/license fidelity and exact attack settings require T3 review before any baseline proposal; no asset downloaded.
