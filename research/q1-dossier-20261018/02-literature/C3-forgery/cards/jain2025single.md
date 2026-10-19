# Forging and Removing Latent-Noise Diffusion Watermarks Using a Single Image

- Citation key: `jain2025single`
- Authors: Anubhav Jain; Yuya Kobayashi; Naoki Murata; Yuhta Takida; Takashi Shibuya; Yuki Mitsufuji; Niv Cohen; Nasir Memon; Julian Togelius.
- Year / venue: 2025; arXiv preprint.
- Version: 2504.20111v1, 2025-04-27.
- Primary source: [full text / repository](https://arxiv.org/html/2504.20111v1).
- DOI: 10.48550/arXiv.2504.20111.
- arXiv / identifier note: 2504.20111v1.
- Access date: 2026-10-18.
- Verification: **V2**. Primary full-text method and experimental sections inspected.
- Inspection locators: Sections 3–5, especially §4 attack objective, §5.1 setup and Table 1.
- Cached artifact: `jain-v1.html`, under MAIN cache directory recorded in `search-log.md`; SHA-256 in `cache-manifest.csv`.

## Evidence extraction

- Setting: Generation-time latent-noise marks; forgery applied to an existing cover.
- Mechanism: Optimize image pixels so the proxy VAE encoding approaches the marked reference's encoding, with image-distance regularization.
- Threat and attacker access: Latent-noise watermark impersonation and removal. Victim watermark/inversion machinery; attacker has one marked example and differentiable off-the-shelf VAE, without U-Net or key.
- Detector side information: Victim watermark/inversion machinery; attacker has one marked example and differentiable off-the-shelf VAE, without U-Net or key.
- Payload / capacity: Inherited Tree-Ring, RingID, WIND and Gaussian Shading payloads; no common new capacity.
- Datasets and counts: 200 marked-reference/COCO-2017-validation cover pairs; simpler runway prompts used for attack references.
- Attacks / regenerators: SD1.4 VAE attacks SD1.4/SD2 targets. No tested registry enrollment.
- Conditional results: Table 1 reports attack success and quality jointly across regularization settings. TR/RingID/WIND use p<.05; these results must not be represented as FPR 10^-6 security.
- Limits: Related Stable Diffusion VAEs and prompt selection constrain generalization; successful attacks do not necessarily satisfy strict imperceptibility thresholds.

## Thesis relevance and inference

Particularly relevant to a VAE-gradient image-domain writer: encoder access enables attack optimization too. This is a hypothesis for F5, not a measured F5 failure.

No new run, pixel inspection, or empirical verification was performed. Literature results remain distinct from thesis evidence.

