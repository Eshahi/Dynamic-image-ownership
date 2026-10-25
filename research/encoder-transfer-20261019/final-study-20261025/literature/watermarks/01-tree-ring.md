# Tree-Ring — V2 primary-source card

Source: Wen, Kirchenbauer, Geiping and Goldstein, *Tree-Ring Watermarks: Fingerprints for Diffusion Images that are Invisible and Robust*, arXiv:2305.20030v2, 1 June 2023. [Inspected version](https://arxiv.org/html/2305.20030v2). Inspected 25 October 2026. Artifact and SHA-256: `source-manifest.json`, key `tree-ring`.

**Direct evidence — mechanism (§§3.1–3.4).** Fourier-domain patterns replace components of the initial Gaussian noise before diffusion generation. Detection uses the generating model's image encoder and denoiser for DDIM inversion, then compares recovered Fourier coefficients with a reference pattern. The image's original prompt and original pixels are unnecessary; model access and the watermark key/pattern are necessary.

**Direct evidence — experiments (§§4.1–4.4, Table 1).** Stable Diffusion v2 and an ImageNet pixel-space diffusion model are evaluated, with 50 generation/inversion steps and 1,000 marked/1,000 unmarked images per run, repeated five times. For SD, ring patterns achieve clean AUC/TPR@1% FPR of 1/1; the attack-averaged values are .975/.694. FID is 25.93 versus 25.29 without watermarking. Attacks include rotation, crop-scale, JPEG, blur, noise and color changes.

**Limits / transfer.** These experiments instantiate the scheme on different generators; they do not freeze a writer and isolate regeneration through independently trained autoencoders. Inversion and its errors are part of the detector (§5).

**Agent inference for F5.** This is generative initial-noise watermarking, not an image-domain residual optimized through an encoder. Its robustness cannot establish an F5 encoder-transfer mechanism.
