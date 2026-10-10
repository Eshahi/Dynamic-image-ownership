# Certifiably Robust Image Watermark

Jiang, Guo, Hu, Jia and Gong; ECCV 2024. Inspected 2026-10-10: [primary conference PDF](https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/09971.pdf), sections 3–5, especially 4.2–4.4 and 5.1. Bibliography: `Jiang2024CertifiedWatermark`.

**Mechanism:** smooth a watermark decoder with Gaussian input noise; compare bitwise voting, multilabel aggregation and regression over message accuracy. Certification bounds apply to additive perturbations within a specified L2 radius. Detection uses a known reference message.

**Numbers and scope:** HiDDeN experiments use 128-square images, 30 message bits and threshold .83; 10,000 samples for certification, 100 for empirical attacks. Standard/adversarial training mean SSIM is .943/.941. These are author-reported settings, not local replications or matched regeneration results.

**Implication:** aggregating several decoder observations is established prior art. Our three deterministic VAE cycles are correlated observations, not Gaussian randomized smoothing; their majority vote inherits neither this certificate nor independent-trial confidence. Original-carrier verification and separate negative controls remain necessary. This paper does not establish source-blind content binding or our T3/T4/T5 performance.
