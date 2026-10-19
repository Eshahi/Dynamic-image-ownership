# AquaLoRA — V2 new inspection

- Authors: Weitao Feng; Wenbo Zhou; Jiyan He; Jie Zhang; Tianyi Wei; Guanlin Li; Tianwei Zhang; Weiming Zhang; Nenghai Yu.
- Title: *AquaLoRA: Toward White-box Protection for Customized Stable Diffusion Models via Watermark LoRA*. ICML 2024, PMLR 235:13423–13444; arXiv 2405.11135v1.
- Primary: https://arxiv.org/html/2405.11135v1 ; https://proceedings.mlr.press/v235/feng24k.html . DOI: 10.48550/arXiv.2405.11135. Access: 2026-10-18.
- Mechanism/access: stage 1 adds learned message residual to an existing image's VAE latent and decodes it; stage 2 learns rank-320 U-Net LoRA reproducing latent watermarking during generation.
- Side information/cost: learned EfficientNet-B1 RGB extractor, message; no inversion. Requires trained modules/model access; 40-epoch pretraining/30-epoch PPFT.
- Payload/data: 48 bits; stage 1 uses 10,000 COCO2017 training images; comparator evaluation 1,000 marked images.
- Threat/numbers: Table 2 TPR .780/.754 for SD1.5 strength .1/SD2.1 strength .2 (Appendix C.2), at nominal FPR 1e-6 based on binomial-null threshold (Appendix F).
- Limits/relevance: directly relevant latent-insertion architecture, but LPIPS compares against VAE reconstruction, not original photo; no demonstrated thesis strict-photo guarantee.
- Inspection: §§4.2–4.3, 5.1–5.3/Table 2, Appendices B/C.2/F. V2, no reproduction.
