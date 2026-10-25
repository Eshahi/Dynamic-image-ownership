# Fixed-renderer capacity and regeneration

- Title: On the Information-Theoretic Limits of Latent-Space Watermarking Through Pretrained Generators
- Authors: Jinwan Jeon; Minju Lee; Sung Hoon Lim. Year: 2026.
- Version: arXiv:2609.24377v1, 21 September 2026. Preprint; submission to IEEE Transactions on Information Theory is not acceptance.
- DOI: 10.48550/arXiv.2609.24377. Key: jeon2026limits.
- [Primary full text](https://arxiv.org/html/2609.24377v1). Access: 2026-10-25.
- Verification: **V2 (theoretical paper)**: formulation II; Gaussian modes V-E/F; regeneration VI-A–F, especially Eqs.51–75 and numerical Figures 3–4. No real-image experiment exists here; not counted toward the empirical-source minimum.

**Direct evidence.** The model imposes exact message-wise, context-conditioned output preservation and a secret key. It derives capacity for a prescribed renderer and scalar Gaussian regeneration. Repeated canonical passes attenuate the original latent contribution geometrically; per-pass and total distortion differ. Figure 4 is a theoretical numerical illustration, not diffusion-model validation.

**Inference / limit.** Useful precedent for treating encoder-to-output transport separately from latent magnitude. Its assumptions do not hold automatically for public-owner, content-derived F5. Neither its capacity nor its asymptotic decay is an F5 performance bound; a new empirical transfer law must be labelled a conditional surrogate.

Cache: MAIN `.thesis-build/cache-et-final/papers/root/jeon2026-limits-v1.html`; SHA256 `a23c0159176067314dd65b9d3d1a17bf292fdd76519054585899b22ca125ad8d`.
