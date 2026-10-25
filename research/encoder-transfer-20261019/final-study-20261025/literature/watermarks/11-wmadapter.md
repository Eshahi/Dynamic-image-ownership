# WMAdapter — V2 primary-source card

Source: Hai Ci, Yiren Song, Pei Yang, Jinheng Xie and Mike Zheng Shou, *WMAdapter: Adding WaterMark Control to Latent Diffusion Models*, arXiv:2406.08337v1, 12 June 2024. [Inspected version](https://arxiv.org/html/2406.08337v1). Inspected 25 October 2026. Artifact/hash: manifest key `wmadapter`.

**Direct evidence — mechanism (§3).** Contextual message/feature fusers form a 1.3M-parameter VAE-decoder plugin. Initial training freezes the VAE and pretrained HiDDeN extractor. Hybrid fine-tuning updates adapter and decoder jointly, then deploys the trained adapter with the original decoder. Detection uses the image extractor and expected 48-bit message, without inversion.

**Direct evidence — experiments (§4, Table 2).** Adapter-I yields PSNR 34.8 dB, SSIM .96 and FID 2.5 on the stated COCO evaluation. Appendix A.4/Table 6 separately trains adapters for SD1.5, SD2.1, SDXL and DiT: all give .99 bit accuracy, with PSNR 32.1/32.8/31.2/32.4 dB. The appendix additionally applies the SD2.1 adapter directly to the SD1.5 VAE, describing little performance loss without a numerical zero-shot table.

**Limits / transfer.** There is actual zero-shot adapter transfer, but only SD2.1→SD1.5 is stated. Separately training an SDXL adapter does not demonstrate zero-shot SDXL transfer or survival under SDXL regeneration. Encoder training independence is not established by model labels.

**Agent inference for F5.** Transfer of a decoder plugin is a different estimand from robustness of a fixed marked image under a new regenerator.
