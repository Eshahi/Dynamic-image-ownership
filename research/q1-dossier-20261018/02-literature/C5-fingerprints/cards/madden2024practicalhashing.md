# madden2024practicalhashing — V2

Jordan Madden, Moxanki Bhavsar, Lhamo Dorje, Xiaohua Li. *Robustness of Practical Perceptual Hashing Algorithms to Hash-Evasion and Hash-Inversion Attacks*. NeurIPS 2024 AdvML Frontiers workshop (author publication list); inspected arXiv 2406.00918v2 (2024-12-05). DOI not verified. Accessed 2026-10-18. [Primary full text](https://arxiv.org/html/2406.00918v2); [workshop paper](https://openreview.net/pdf?id=hraOxsleRl).

**Mechanism / access.** A black-box hash oracle supports soft-label initialization followed by hard-label optimization; no weights or embedded payload. Read §§3.1–3.3, §§4.1–4.2/Table 2, Appendices A.3–A.4.

**Evidence.** On 100 random ImageNet validation images with reported L2 distortion below 0.1, 5,000-query budget and normalized untargeted Hamming-distance goal 0.3, maximum reported success is PDQ 1%, NeuralHash 28%, PhotoDNA 92% (Table 2; attacks/configurations differ).

**Boundary / relevance.** This is counterevidence to claiming every practical fingerprint is easily broken under every threat model. A query-limited distant-hash evasion goal differs from white-box targeted collision and natural cohort collisions. It offers no diffusion or same-shot specificity result and no assurance for the thesis verifier.
