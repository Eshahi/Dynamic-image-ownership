# SemBind: Binding Diffusion Watermarks to Semantics Against Black-Box Forgery Attacks

- Citation key: `zhang2026sembind`
- Authors: Xin Zhang; Zijin Yang; Kejiang Chen; Linfeng Ma; Weiming Zhang; Nenghai Yu.
- Year / venue: 2026; arXiv preprint.
- Version: 2601.20310v1, 2026-01-28.
- Primary source: [full text / repository](https://arxiv.org/html/2601.20310v1).
- DOI: 10.48550/arXiv.2601.20310.
- arXiv / identifier note: 2601.20310v1.
- Access date: 2026-10-18.
- Verification: **V2**. Primary full-text construction and main experimental sections inspected; adaptive appendix not exhaustively audited.
- Inspection locators: Sections 2.3, 3.1–3.3, 4.1–4.4; Tables 2 and 4.
- Cached artifact: `sembind-v1.html`, under MAIN cache directory recorded in `search-log.md`; SHA-256 in `cache-manifest.csv`.

## Evidence extraction

- Setting: Generation-time semantic binding.
- Mechanism: Derive a semantic code from a preliminary image and use it to mask watermark noise; detector recomputes the code to unmask.
- Threat and attacker access: Imprinting and reprompting of victim watermarks. Private trained DINOv2-based semantic masker, secret permutation, watermark keys and inversion model; no per-image registry.
- Detector side information: Private trained DINOv2-based semantic masker, secret permutation, watermark keys and inversion model; no per-image registry.
- Payload / capacity: Underlying TR/GS/PRC/GS++ capacities inherited; semantic code is not an independent ownership payload.
- Datasets and counts: SemCon3M training; quality on 5,000 COCO prompts and 1,000 SDP prompts; attack denominator not independently recovered here.
- Attacks / regenerators: SD2.1-base 512px, 50-step DPM-Solver generation/inversion; imprinting and reprompting comparisons.
- Conditional results: Table 4, SDP/SD2.1 reprompting: GS-S acceptance .60 versus GS 1.00, theoretical FPR 10^-6. This is substantial residual forgery.
- Limits: Semantic similarity differs from instance identity. Private masker assumptions differ from public owner-conditioned pointers.

## Thesis relevance and inference

Preempts generic semantic-binding novelty; motivates explicit same-semantics adversaries and separation of key secrecy from public identifiers.

No new run, pixel inspection, or empirical verification was performed. Literature results remain distinct from thesis evidence.

