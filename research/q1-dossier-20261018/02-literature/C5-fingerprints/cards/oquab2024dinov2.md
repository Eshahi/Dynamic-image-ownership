# oquab2024dinov2 — V2

Maxime Oquab et al. *DINOv2: Learning Robust Visual Features without Supervision*. Inspected arXiv 2304.07193v2 (2024-02-02); venue metadata not independently verified here. DOI: not verified. Accessed 2026-10-18. [Primary full text](https://arxiv.org/html/2304.07193v2).

**Mechanism / access.** Frozen image and patch representations learned by image/patch self-distillation, curated data and feature regularization. Public feature extractor; retrieval needs stored reference embeddings. No watermark payload or registry authentication.

**Evidence.** Read §§3–4, §7.3/Table 9 and patch-matching discussion in §7.5. Cosine instance retrieval covers Oxford, Paris, Met and AmsterTime. Table 9 reports Oxford Hard mAP 54.0 for DINOv2 ViT-L/14 and 19.7 for OpenCLIP ViT-G/14. Different architectures/training prevent attributing the difference solely to the learning objective.

**Boundary / relevance.** Landmark retrieval permits different photographs of one object; patch correspondence can align semantically similar objects. Neither constitutes exact-frame rejection. Global DINOv2 or CLIP is useful context, but higher semantic invariance does not establish separation of adjacent frames under regeneration.
