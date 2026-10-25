# PRC watermark — V2 primary-source card

Source: Sam Gunn, Xuandong Zhao and Dawn Song, *An undetectable watermark for generative image models*, arXiv:2410.07369v4, 21 April 2025. [Inspected version](https://arxiv.org/html/2410.07369v4). Inspected 25 October 2026. Artifact/hash: manifest key `prc`.

**Direct evidence — mechanism (§3).** A pseudorandom error-correcting code controls Gaussian initial-noise signs. Detection combines recovered-noise soft information with the private code key. The evaluated exact inversion includes decoder inversion and the original diffusion model, so the detector is not a lightweight image-only extractor.

**Direct evidence — experiments (§4).** SD2.1-base generates 512-pixel images with 50 steps; main PRC FPR is set to 1%. Section 4.3/Figure 5 reports TPR .94 under JPEG quality 20, while assessing attack quality with PSNR, SSIM and FID. Section 4.4 reports robust 512-bit message recovery and up to 2,500 bits without removal attacks. Appendix A.1 uses SD2.1 diffusion regeneration and Bmshj2018/Cheng2020 learned compression over strength grids.

**Limits / transfer.** These attacks do not isolate independently trained SDXL/FLUX encoder substitution. Theorem 2's FPR is over random keys for key-independent input, not an unconditional guarantee against adaptive inputs under one fixed disclosed key. Computational undetectability is distinct from measured removal robustness.

**Agent inference for F5.** Separate cryptographic assumptions, error correction, inversion resources and empirical regeneration transfer; success in one category cannot substitute for another.
