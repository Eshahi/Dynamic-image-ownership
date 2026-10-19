# Rethinking Forgery Attacks on Semantic Watermarks in Black-Box Settings: A Geometric Distortion Perspective

- Citation key: `lee2026geometric`
- Authors: Cheng-Yi Lee; Yichi Zhang; Yuchen Yang; Chun-Shien Lu; Jun-Cheng Chen.
- Year / venue: 2026; arXiv; abstract page reports ICML 2026 acceptance (proceedings not independently checked).
- Version: 2606.29807v1, 2026-06-29.
- Primary source: [full text / repository](https://arxiv.org/html/2606.29807v1).
- DOI: 10.48550/arXiv.2606.29807.
- arXiv / identifier note: 2606.29807v1.
- Access date: 2026-10-18.
- Verification: **V2**. Primary full-text geometric argument, attack setup and defense experiments inspected.
- Inspection locators: Sections 4.1–4.3.4, 5.1–5.4, 6.3–6.4; Tables 3–4.
- Cached artifact: `geometric-v1.html`, under MAIN cache directory recorded in `search-log.md`; SHA-256 in `cache-manifest.csv`.

## Evidence extraction

- Setting: Generation-time latent watermark defense.
- Mechanism: Analyze proxy mismatch through rate-distortion geometry; detect angular/local covariance deviations using G-Cos and L-SPD.
- Threat and attacker access: Cross-model optimization and reprompting forgery. Victim inversion model and reference watermarked latent for geometry comparisons; claimed zero-storage implementation needs scheme-specific reference reconstruction clarification.
- Detector side information: Victim inversion model and reference watermarked latent for geometry comparisons; claimed zero-storage implementation needs scheme-specific reference reconstruction clarification.
- Payload / capacity: Six underlying watermark schemes, no new payload capacity.
- Datasets and counts: 1,000 guidance-reprompt samples; 100 COCO covers for optimization attacks.
- Attacks / regenerators: SD2.1/SD3 proxies; SD2.1, SDXL, PixArt-Sigma, FLUX.1, SD3 targets; six schemes including TR and GS.
- Conditional results: Table 4, SD2.1 Tree-Ring, 100-step row: G-Cos AUC .978, L-SPD .905. AUC is not an operating-point false-acceptance guarantee.
- Limits: Gaussian/shared-covariance abstraction and proxy mismatch assumptions; §4.3.4 permits overlap. Do not infer same-model/key-exposed security.

## Thesis relevance and inference

Current defense benchmark idea, not a proof that registry verification is secure. Resolve detector reference availability before adopting.

No new run, pixel inspection, or empirical verification was performed. Literature results remain distinct from thesis evidence.

