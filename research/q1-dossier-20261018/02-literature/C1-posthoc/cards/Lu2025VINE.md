# Robust Watermarking Using Generative Priors Against Image Editing: From Benchmarking to Advances

- Citekey: `Lu2025VINE`
- Authors: Shilin Lu; Zihan Zhou; Jiayou Lu; Yuanzhi Zhu; Adams Wai-Kin Kong.
- Year / venue: 2025; ICLR 2025.
- Version: v2 (2025-03-15).
- Primary source: [paper](https://arxiv.org/html/2410.18775v2); arXiv: 2410.18775; DOI: not verified for this inspected version (omitted from BibTeX).
- Access / inspection date: 2026-10-18.
- Verification: V2 — method and experiment sections inspected in this session; version-specific, not a quality endorsement.
- Exact inspection locators: Sections 3.1–3.3, 4.1–4.4; Tables 1–2; Appendix F.
- Artifact: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/C1/vine.html`; SHA-256: `f6fb25d7b27ec0e95f883674e2e08a41a9075f5929e76287f02330e339e049dd`.
- Setting: Post-hoc existing images.
- Detector side information: Trained ConvNeXt-B extractor; candidate message and threshold for verification; no original or inversion.
- Threat: T3 diffusion regeneration and global/local editing.

**Mechanism/payload.** A conditional SDXL-Turbo watermark encoder combines the image and message through an adapter, modified VAE skip connections and staged training. Blur surrogates encourage low-frequency survival; VINE-R additionally uses InstructPix2Pix with a straight-through gradient. Payload: 100 bits.

**Evidence.** W-Bench uses 10,000 UltraEdit-sourced images: 1,000 each for stochastic regeneration, deterministic regeneration, global editing, image-to-video and distortion, plus 5,000 local-editing images. It reports TPR at 0.1%/1% FPR with image quality. Stochastic regeneration varies timesteps 60–240; deterministic editing varies solver steps; global/local editing includes InstructPix2Pix, MagicBrush, UltraEdit and ControlNet. Table 1 aggregates severities; these are not interchangeable with a single SD img2img setting.

**Access/limits.** Training uses differentiable surrogates and an editing model; this is not an adaptive public-key forgery evaluation. VINE is post-hoc despite its generative encoder. No numerical superiority claim is imported here.

**Thesis inference.** Generative-prior and VAE-aware robustness are established territory. F5 needs a narrower image-variable/encoder-gradient distinction and evidence under matched threats, not a broad first diffusion-robust watermark claim.

