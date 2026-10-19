# PRC image watermark — V2 refresh

- Authors: Sam Gunn; Xuandong Zhao; Dawn Song.
- Title: *An Undetectable Watermark for Generative Image Models*. ICLR 2025; arXiv 2410.07369v4 (2025-04-21); legacy citekey retains 2024.
- Primary: https://arxiv.org/html/2410.07369v4 . DOI: 10.48550/arXiv.2410.07369. Access: 2026-10-18.
- Mechanism/setting: PRC-coded Gaussian signs with half-normal magnitudes in initial generation noise.
- Side information/access/cost: secret PRC key/parity checks and diffusion model; 50-step exact inversion, belief-propagation decoding. SD2.1, DPM generation, guidance 3.
- Payload/data: detection and message decoding are distinct; reported 512-bit decoding is weaker than detection. Evaluation includes generated-image attack curves; attack-specific count not re-extracted here.
- Evidence: §4.3 reports high detection over its tested quality/attack range; it does not prove arbitrary regeneration survival. Theorem 2 fixes the image/key-independent input and randomizes the key.
- Limits: finite implementation parameters do not inherit an unrestricted asymptotic guarantee. Appendix Figure 8 discusses adversarially robust/private VAEs as possible embedding-attack mitigations; it is **not** evidence of an experimentally evaluated robustified regenerator.
- Relevance/inspection: initial-noise cryptographic precedent, not existing-photo insertion. Fresh §§3, 4.1–4.3, Appendix/Figure 8; prior `research/literature/m1-latent-survey/cards/prc-image.md` was v2. V2, no reproduction.
