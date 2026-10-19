# Watermark Anything with Localized Messages

- Citekey: `Sander2025WAM`
- Authors: Tom Sander; Pierre Fernandez; Alain Durmus; Teddy Furon; Matthijs Douze.
- Year / venue: 2025; ICLR 2025.
- Version: v2 (2025-07-22).
- Primary source: [paper](https://arxiv.org/html/2411.07231v2); arXiv: 2411.07231; DOI: 10.48550/arXiv.2411.07231.
- Access / inspection date: 2026-10-18.
- Verification: V2 — method and experiment sections inspected in this session; version-specific, not a quality endorsement.
- Exact inspection locators: Sections 3–4, 5 evaluation; Appendix G.3 Table 9; Appendix D.
- Artifact: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/C1/wam.html`; SHA-256: `3ca12cea768aa10c8eda2e351a88c3e85790e69db64e60cad747771897c9c6aa`.
- Setting: Post-hoc localized and multi-message image watermarking.
- Detector side information: Learned ViT/pixel decoder and clustering; no original or diffusion inversion.
- Threat: T4 splicing/local editing; conventional attacks; regeneration appendix.

**Mechanism/payload.** An autoencoder/message lookup produces an additive residual, modulated by a JND map. A ViT pixel decoder predicts detection and 32 message bits at each pixel; DBSCAN separates messages.

**Evidence.** Training uses COCO's 118,000 images. Experiments include 256-image sets and disjoint marked regions. Appendix G.3 Table 9 reports DiffPure bit accuracies 100/99.4/71.3/49.1% at respective PSNR 30.1/28.4/27.0/24.9 dB. The progressive loss is more informative than a single robustness label; local-message success is conditional on region geometry and discovered clusters.

**Access/limits.** A public learned detector replaces original-image comparison. Pixel detection thresholds use held-out clean pixels; that calibration is not automatically an image-level or registry-wide false-positive bound. Localization of copied marked content does not prove legitimate ownership.

**Thesis inference.** T4 requires a different question from recovering the owner bits. WAM supplies a principled local baseline, but its ordinary splicing capability must not be described as blanket resilience to full regeneration.

