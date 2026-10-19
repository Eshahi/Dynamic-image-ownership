# APT: Anchor-aligned Perturbations for Tamper Localization in Fully Regenerated Images

- Citekey: `Ha2026APT`
- Authors: Suhyeon Ha; Woo Jae Kim; Joonsung Jeon; Sooel Son; Sung-eui Yoon.
- Year / venue: 2026; arXiv preprint.
- Version: v1 (2026-08-31).
- Primary source: [paper](https://arxiv.org/html/2608.30656v1); arXiv: 2608.30656; DOI: not verified for this inspected version (omitted from BibTeX).
- Access / inspection date: 2026-10-18.
- Verification: V2 — method and experiment sections inspected in this session; version-specific, not a quality endorsement.
- Exact inspection locators: Sections 3.2, 4.1–4.3, 5.1–5.2; Table 1; Appendix D.
- Artifact: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/C1/apt.html`; SHA-256: `a90a8c7c571d713fec754bf6a8436ab43d83dc621f612443b3de1116ea88d51a`.
- Setting: Post-hoc latent perturbation for tamper localization.
- Detector side information: DINOv3 ConvNeXt-small features and secret server-side anchors; no original image.
- Threat: Regeneration after localized inpainting; copy-move and re-marking limits.

**Mechanism/payload.** Optimize a latent perturbation so shallow DINOv3 features align with secret Rademacher anchors, with noisy and hard-negative branches; decode and clip the result. No UNet participates. This is a localization signal, not a multi-bit ownership payload.

**Evidence.** Experiments use the first 100 COCO validation images with expanded object masks and Stable Diffusion inpainting. Table 1 reports APT at PSNR 32.80 dB, AUROC 0.97 and IoU 0.90; a shallow-decoder variant reaches IoU 0.92 under that protocol. The stated implementation uses 150 Adam steps, averaging 42.52 seconds on RTX4090 for 100 images.

**Access/limits.** Anchors are assumed secret and server-side. Same-image copy-move can evade localization, and malicious re-marking is a separate threat. These caveats restrict transfer to public watermark encoders.

**Thesis inference.** Semantic anchors and VAE-aware per-image optimization substantially narrow novelty. F5's pointer plus continuous enrolled descriptors is a different decision problem, not evidence of superiority over APT's localization task.

