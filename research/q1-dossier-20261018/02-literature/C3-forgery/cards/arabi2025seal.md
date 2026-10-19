# SEAL: Semantic Aware Image Watermarking

- Citation key: `arabi2025seal`
- Authors: Kasra Arabi; R. Teal Witter; Chinmay Hegde; Niv Cohen.
- Year / venue: 2025; ICCV 2025; substantive evidence here from updated arXiv version.
- Version: 2503.12172v4, 2026-05-18 (initial preprint 2025).
- Primary source: [full text / repository](https://arxiv.org/html/2503.12172v4).
- DOI: 10.48550/arXiv.2503.12172.
- arXiv / identifier note: 2503.12172v4.
- Access date: 2026-10-18.
- Verification: **V2**. Updated primary full-text method, conditional analysis and main experiment sections inspected.
- Inspection locators: Sections 3.1–3.3, 4; Algorithms 1–3; Tables 1–2; Assumption 3.1.
- Cached artifact: `seal-v4.html`, under MAIN cache directory recorded in `search-log.md`; SHA-256 in `cache-manifest.csv`.

## Evidence extraction

- Setting: Generation-time watermark bound to semantics and spatial tampering.
- Mechanism: Caption embedding drives patchwise SimHash seeds with secret salt; detection compares regenerated expected patches with inverted noise.
- Threat and attacker access: Noise reuse with unrelated prompt; object pasting and removal. Private user salt, caption/embedding models and diffusion inversion; no stored original image.
- Detector side information: Private user salt, caption/embedding models and diffusion inversion; no stored original image.
- Payload / capacity: 1,024 noise patches, seven hash-input bits per patch; not 7,168 independent authenticated payload bits.
- Datasets and counts: SD-v2, Gustavosta prompts, 50 generation/inversion steps; 10,000 caption pairs for embedding tuning; main attack sample count not recovered.
- Attacks / regenerators: Private-model inversion/reprompting; pasted objects span 30–60% of image dimensions.
- Conditional results: Table 2 private-model forgery-rejection AUC .708; Table 1 pasted-object detection AUC .982 with spatial test.
- Limits: Formal result assumes patch-distance separation; semantic binding does not guarantee unique instance ownership.

## Thesis relevance and inference

§3.1 explicitly discusses comparing suspects with a database of past generations. Registry verification as a generic idea is therefore not new.

No new run, pixel inspection, or empirical verification was performed. Literature results remain distinct from thesis evidence.

