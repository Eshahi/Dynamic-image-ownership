# Black-Box Forgery Attacks on Semantic Watermarks for Diffusion Models

- Citation key: `muller2025forgery`
- Authors: Andreas Müller; Denis Lukovnikov; Jonas Thietke; Asja Fischer; Erwin Quiring.
- Year / venue: 2025; CVPR 2025, pp. 20937–20946.
- Version: arXiv 2412.03283v3, 2025-06-07; venue metadata verified; CVPR PDF cached but text fetch failed.
- Primary source: [full text / repository](https://arxiv.org/html/2412.03283v3).
- DOI: Not primary-verified; omitted.
- arXiv / identifier note: 2412.03283v3; venue DOI omitted because only secondary metadata confirmed it.
- Access date: 2026-10-18.
- Verification: **V2**. Current primary arXiv full-text method and experiments inspected. V2 attaches to v3, not an asserted read of inaccessible venue PDF.
- Inspection locators: v3 §§3.1–3.3, 4.1–4.6, Tables 1–3 and PSNR correction footnote.
- Cached artifact: `muller-v3.html`, under MAIN cache directory recorded in `search-log.md`; SHA-256 in `cache-manifest.csv`.

## Evidence extraction

- Setting: Generation-time semantic watermarks attacked through existing-image imprinting or new generation.
- Mechanism: Move a cover's proxy inversion toward reference noise, or reuse recovered noise under a new prompt.
- Threat and attacker access: Victim watermark impersonation, reprompting and removal. Victim inversion model and watermark secrets; attacker needs one marked reference plus an unrelated proxy diffusion model.
- Detector side information: Victim inversion model and watermark secrets; attacker needs one marked reference plus an unrelated proxy diffusion model.
- Payload / capacity: Tree-Ring/Gaussian Shading capacities inherited; Gaussian Shading attribution evaluated with 100,000 users.
- Datasets and counts: 100 image pairs for imprinting; basic reprompting uses 1,000 references. Augmented reprompting uses 100 references with multiple candidates.
- Attacks / regenerators: SD2.1 proxy; target Anime, SDXL, PixArt-Sigma, FLUX.1; cross-model study.
- Conditional results: Table 1, SDXL Gaussian Shading, 50 inversion steps: detection/attribution 1.00, PSNR 21.86, LPIPS .168. FPR: GS 10^-6; TR .01.
- Limits: v3 corrects previous PSNR calculation. Multi-candidate success is not one-attempt success. Proxy transfer is empirical, not universal.

## Thesis relevance and inference

Direct active-forgery threat; it does not test attacker record enrollment. Avoid citing stale v1 quality values.

No new run, pixel inspection, or empirical verification was performed. Literature results remain distinct from thesis evidence.

