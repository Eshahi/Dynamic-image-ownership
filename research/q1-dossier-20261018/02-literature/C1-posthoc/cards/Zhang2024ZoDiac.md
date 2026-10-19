# Attack-Resilient Image Watermarking Using Stable Diffusion

- Citekey: `Zhang2024ZoDiac`
- Authors: Lijun Zhang; Xiao Liu; Antoni Viros Martin; Cindy Xiong Bearfield; Yuriy Brun; Hui Guan.
- Year / venue: 2024; arXiv version inspected.
- Version: v2 (2024-10-28).
- Primary source: [paper](https://arxiv.org/html/2401.04247v2); arXiv: 2401.04247; DOI: not verified for this inspected version (omitted from BibTeX).
- Access / inspection date: 2026-10-18.
- Verification: V2 — method and experiment sections inspected in this session; version-specific, not a quality endorsement.
- Exact inspection locators: Sections 3.1–3.3, 4.1 experimental setup and attack evaluation.
- Artifact: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/C1/zodiac.html`; SHA-256: `80f626f4abdaef8a9468497ab5b28bc4e27510aecc4bc365fb3b509a40e72145`.
- Setting: Post-hoc images via diffusion inversion and reconstruction.
- Detector side information: Diffusion model, inversion and keyed ring pattern; no enrolled original needed for presence test.
- Threat: Conventional and diffusion-based removal.

**Mechanism/payload.** DDIM inversion initializes a latent; a Fourier ring watermark is inserted while reconstruction is optimized through frozen Stable Diffusion, followed by image blending. Detection inverts the suspect and tests the ring. The inspected design is principally zero-bit presence detection, not a 32-bit identifier.

**Evidence.** Tests use 500 images each from COCO, DiffusionDB and WikiArt. The setup uses SD2.1-base, 50 diffusion steps and up to 100 optimization iterations; the reported per-image embedding range is 45.4–255.9 seconds. The quality control uses an SSIM target of 0.92, and a detection threshold of 0.9 under its stated statistic. Those thresholds are method-specific.

**Access/limits.** The attacker can apply regeneration without the key; detector-side model/inversion costs remain substantial. Watermark presence is not verification of which enrolled photograph is present.

**Thesis inference.** This blocks a broad claim of first robust post-hoc diffusion watermarking, while leaving a meaningful difference in detector access/cost and image-domain optimization.

