# FreqMark: Invisible Image Watermarking via Frequency Based Optimization in Latent Space

- Citekey: `Guo2024FreqMark`
- Authors: Yiyang Guo; Ruizhe Li; Mude Hui; Hanzhong Guo; Chen Zhang; Chuangjian Cai; Le Wan; Shangfei Wang.
- Year / venue: 2024; NeurIPS 2024.
- Version: v1 (2024-10-28); proceedings metadata verified.
- Primary source: [paper](https://arxiv.org/html/2410.20824v1); arXiv: 2410.20824; DOI: 10.52202/079017-3564.
- Access / inspection date: 2026-10-18.
- Verification: V2 — method and experiment sections inspected in this session; version-specific, not a quality endorsement.
- Exact inspection locators: Sections 4.1–4.4, 5.1 experimental setup and robustness analysis.
- Artifact: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/C1/freqmark.html`; SHA-256: `00a18323cf1145838bc421c097ec59e6094571dcdd4636e0021383b79020aa99`.
- Setting: Post-hoc images reconstructed from optimized latent frequencies.
- Detector side information: Fixed DINOv2-small feature extractor and message directions; no original or diffusion inversion.
- Threat: VAE compression and diffusion regeneration plus conventional attacks.

**Mechanism/payload.** Optimize a perturbation to the FFT of an encoded VAE latent, reconstruct the image, and enforce signs along fixed image-feature directions. All networks remain frozen; default payload is 48 bits.

**Evidence.** Evaluation uses 500 ImageNet validation images and 500 generated images from DiffusionDB prompts. Regeneration includes two CompressAI autoencoder variants at quality 3 and a diffusion attack with 60 denoising steps. The paper reports bit accuracy; this must not be converted into calibrated ownership-attribution probability. A 2,000-clean-image feature-bit correlation check does not establish statistical independence.

**Access/limits.** Embedding requires iterative optimization and an autoencoder decoder. Feature-direction access and adaptive forgery differ from ordinary removal robustness. Image reconstruction constrains fidelity.

**Thesis inference.** Frozen-model, per-image optimization and frequency/semantic-feature robustness are established. The narrow F5 distinction is the optimized variable being pixels and the carrier being measured after the encoder, followed by a separately declared trusted record check.

