# WMCopier: Forging Invisible Image Watermarks on Arbitrary Images

- Citation key: `dong2025wmcopier`
- Authors: Ziping Dong; Chao Shuai; Zhongjie Ba; Peng Cheng; Zhan Qin; Qinglong Wang; Kui Ren.
- Year / venue: 2025; NeurIPS 2025 acceptance reported on arXiv; substantive evidence from v3.
- Version: 2503.22330v3, 2025-10-24; earlier title differs.
- Primary source: [full text / repository](https://arxiv.org/html/2503.22330v3).
- DOI: 10.48550/arXiv.2503.22330.
- arXiv / identifier note: 2503.22330v3.
- Access date: 2026-10-18.
- Verification: **V2**. Primary current-version method and experiments inspected.
- Inspection locators: Sections 3–5, especially threat model, shallow inversion/refinement and Table 1.
- Cached artifact: `wmcopier-v3.html`, under MAIN cache directory recorded in `search-log.md`; SHA-256 in `cache-manifest.csv`.

## Evidence extraction

- Setting: Post-hoc static-message image watermark forgery.
- Mechanism: Train diffusion model on marked distribution, then shallow-invert and denoise a cover with iterative refinement.
- Threat and attacker access: Victim-message copying onto arbitrary covers. Victim decoder/key; attacker collects 5,000 images bearing the same target message, with no embedder/detector interface.
- Detector side information: Victim decoder/key; attacker collects 5,000 images bearing the same target message, with no embedder/detector interface.
- Payload / capacity: Default capacities of DWT-DCT, HiDDeN, RivaGAN and Stable Signature; no new common payload.
- Datasets and counts: COCO, ImageNet, CelebA-HQ, DiffusionDB; training count 5,000; per-cell test denominator not independently recovered.
- Attacks / regenerators: Trained diffusion copying; also evaluated a commercial watermark service historically.
- Conditional results: Table 1, Stable Signature/COCO: reported acceptance .946 and PSNR 31.29. Do not transplant its threshold or rate to F5.
- Limits: Repeated-message data requirement is strong; not one-shot. Contemporary vendor performance cannot be inferred.

## Thesis relevance and inference

Threat to generic post-hoc forgery-resistance claims; distinguish data-rich copying from passive enrollment.

No new run, pixel inspection, or empirical verification was performed. Literature results remain distinct from thesis evidence.

