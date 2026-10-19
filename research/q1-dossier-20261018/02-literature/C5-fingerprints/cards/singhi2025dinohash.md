# singhi2025dinohash — V2

Shree Singhi, Aayan Yadav, Aayush Gupta, Shariar Ebrahimi, Parisa Hassanizadeh. *Provenance Detection for AI-Generated Images: Combining Perceptual Hashing, Homomorphic Encryption, and AI Detection Models*. arXiv 2503.11195v1 (2025-03-14); preprint, venue/DOI not verified. Accessed 2026-10-18. [Primary full text](https://arxiv.org/html/2503.11195v1).

**Mechanism / access.** DINOv2 ViT-B/14-register features are reduced from 768 to 96 dimensions by PCA and binarized; encrypted Hamming comparison searches signed registered hashes. Fallback AI classification is separate from attribution. Registered fingerprints, PCA parameters and encryption/signature infrastructure are side information; no embedded image payload.

**Evidence.** Read §§3.1–3.3 and 4.1–4.2. Evaluation uses one million DiffusionDB images with common transformations/screenshots. TPR is empirical, while reported FPR is approximated by an independent fair-bit binomial model (Eq. 2).

**Boundary / relevance.** Generated source images do not make these transformation tests diffusion-regeneration tests. PCA decorrelation does not establish independent bits or same-shot collision rates. Registry fingerprint provenance is prior art; its analytic random-pair model cannot certify the thesis's hard-negative specificity.
