# ZoDiac — V2 primary-source card

Source: Lijun Zhang, Xiao Liu, Antoni Viros Martin, Cindy Xiong Bearfield, Yuriy Brun and Hui Guan, *Attack-Resilient Image Watermarking Using Stable Diffusion*, arXiv:2401.04247v2, 28 October 2024. [Inspected version](https://arxiv.org/html/2401.04247v2). Inspected 25 October 2026. Artifact/hash: manifest key `zodiac`.

**Direct evidence — mechanism (§3).** An arbitrary image is DDIM-inverted; a Fourier ring is imposed in the latent. The latent is optimized through a frozen diffusion generator for reconstruction, followed by adaptive blending with the original image to satisfy an SSIM target. Detection uses diffusion inversion and the reference ring. This is post-hoc latent optimization through the generator/VAE, not just image-space optimization through an encoder.

**Direct evidence — experiments (§4).** Each of COCO, DiffusionDB and WikiArt contributes 500 images. Table 3's COCO threshold sweep shows the tradeoff: at threshold .90, empirical FPR is .062 and Zhao23 regeneration WDR .988; at .99, FPR is .004 and regeneration WDR .938. Rotation WDR falls from .538 to .106. Thus high regeneration detection is not evidence of negligible false positives.

**Limits / transfer.** Figure 4 repeats embedding with SD2.1, SD1.4 and SDXL backbones. This is not a frozen SD1.5 writer attacked by independent SDXL autoencoding; backbone dependence and detector inversion remain coupled.

**Agent inference for F5.** Closely relevant optimization precedent, but its writer and detector are materially heavier and observe different information.

