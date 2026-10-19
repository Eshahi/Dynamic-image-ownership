# InvisMark: Invisible and Robust Watermarking for AI-generated Image Provenance

- Citekey: `Xu2024InvisMark`
- Authors: Rui Xu; Mengya Hu; Deren Lei; Yaxi Li; David Lowe; Alex Gorevski; Mingyu Wang; Emily Ching; Alex Deng.
- Year / venue: 2024; arXiv preprint.
- Version: v2 (2024-11-19).
- Primary source: [paper](https://arxiv.org/html/2411.07795v2); arXiv: 2411.07795; DOI: 10.48550/arXiv.2411.07795.
- Access / inspection date: 2026-10-18.
- Verification: V2 — method and experiment sections inspected in this session; version-specific, not a quality endorsement.
- Exact inspection locators: Sections 2.1–2.4.1, 3 experimental setup, 3.3–3.5.
- Artifact: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/C1/invis.html`; SHA-256: `a4851485a056418c41ad65d605b783a0c626d805f759622d5e978b2a02405343`.
- Setting: Post-hoc images; training emphasizes generated high-resolution images.
- Detector side information: Learned ConvNeXt-base message decoder; no original or inversion.
- Threat: Conventional distortions; SD2.1 regeneration; residual-transfer forgery discussion.

**Mechanism/payload.** MUNIT residual encoder with 1×1 processing, ConvNeXt-base decoder, resolution-aware training and robust optimization. Main evaluation uses 100 bits; a 256-bit configuration is discussed.

**Evidence.** Training uses 100,000 non-public DALL·E 3 images. Tests include 900 DIV2K and 900 public DALL·E 3 images. Section 3.3's SD2.1 regeneration study uses only ten images and timesteps 1, 3, 5, 10, 20, 60 and 100; decoding approaches chance at roughly 25 dB PSNR. This is a small, severity-conditioned observation, not a universal cutoff.

**Access/limits.** A public encoder enables residual-transfer forgery in the paper's discussion. Dataset availability limits independent reproduction. Pixel Seal later flags a released-checkpoint effective-payload issue; that later observation is not silently substituted for this paper's declared payload.

**Thesis inference.** High clean fidelity and robustness to ordinary distortions do not settle T3. A pointer copied into another image requires record verification beyond message extraction. No final conference venue was verified, so this card retains the preprint citation.

