# RingID — V2 refresh

- Authors: Hai Ci; Pei Yang; Yiren Song; Mike Zheng Shou.
- Title: *RingID: Rethinking Tree-Ring Watermarking for Enhanced Multi-Key Identification*. ECCV 2024; method/evaluation inspected in arXiv 2404.14055v3 (2024-07-18).
- Primary: https://arxiv.org/html/2404.14055v3 ; final venue PDF title/authors checked: https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/04104.pdf . DOI: 10.48550/arXiv.2404.14055. Access: 2026-10-18.
- Mechanism/setting: heterogeneous initial-noise channels combine a Fourier-ring channel and noise-pattern channel for key discrimination.
- Side information/cost: diffusion model, key bank, channel-normalized distance; DDIM inversion, 50 steps in reported setup.
- Payload/data/count: identification among 32/128/2,048 keys; ROC evaluation uses 1,000 marked and 1,000 unmarked images. COCO-derived prompts; quality set separately uses 5,000 generations.
- Threat/evidence: §6.1/Table 2 at 2,048 keys reports clean identification 1.000 but crop-and-scale .080; averages are attack/identity-specific.
- Limits/relevance: binary presence ROC can benefit from distribution shift without resolving identity. Key attribution does not bind content; existing natural photographs require a separate insertion procedure.
- Inspection: fresh method §§3–5 and §6.1/Tables 1–2; prior `research/literature/m1-latent-survey/cards/ringid.md` inspected v2. V2, no reproduction.
