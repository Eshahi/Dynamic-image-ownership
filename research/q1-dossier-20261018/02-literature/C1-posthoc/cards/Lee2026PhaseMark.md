# PhaseMark: A Post-hoc, Optimization-Free Watermarking of AI-generated Images in the Latent Frequency Domain

- Citekey: `Lee2026PhaseMark`
- Authors: Sung Ju Lee; Nam Ik Cho.
- Year / venue: 2026; arXiv preprint.
- Version: v1 (2026-01-19).
- Primary source: [paper](https://arxiv.org/html/2601.13128v1); arXiv: 2601.13128; DOI: not verified for this inspected version (omitted from BibTeX).
- Access / inspection date: 2026-10-18.
- Verification: V2 — method and experiment sections inspected in this session; version-specific, not a quality endorsement.
- Exact inspection locators: Sections 2–3; Tables 1–3.
- Artifact: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/C1/phase.html`; SHA-256: `903c711eacb06288a39471fa6f7947eb9fa1d05b620003c57662d26071e41009`.
- Setting: Post-hoc bitmap input; evaluated on generated images.
- Detector side information: VAE encoder, frequency locations and phase rule; no original or inversion.
- Threat: VAE and diffusion regeneration plus image distortions.

**Mechanism/payload.** Encode the VAE posterior mean, crop a central 44×44 latent region, transform it, and modulate mid-band 2×2 phases under four variants while preserving Hermitian symmetry. Decode to an image. Extraction uses VAE encoding and phase tests without iterative optimization. Payload: 128 bits across four latent channels.

**Evidence.** The paper evaluates 1,000 SD2.1-generated images per prompt collection (COCO2017, SD prompts, DiffusionDB). APM reports TPR at 1% FPR of 0.996/0.997 under two VAE regenerators and 1.000 for its 60-step diffusion condition. PCQ's 34.156 dB PSNR is below the reconstruction-only 36.4193 dB in the reported setting. These values do not establish performance on natural photographs.

**Access/limits.** Detection probabilities invoke binomial/Bonferroni assumptions; they are not an ownership guarantee. Autoencoder reconstruction changes the input even before watermarking.

**Thesis inference.** Post-hoc, inversion-free, latent-frequency watermarking is already explicit prior art. The remaining question concerns pixel-variable optimization and content-specific verification under declared side information.

