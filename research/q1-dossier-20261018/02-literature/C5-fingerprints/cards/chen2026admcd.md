# chen2026admcd — V2

Yunzhuo Chen, Jordan Vice, Naveed Akhtar, Nur Al Hasan Haldar, Ajmal Mian. *Mitigating Memorization in Text-to-Image Diffusion via Region-Aware Prompt Augmentation and Multimodal Copy Detection*. arXiv 2603.13070v1 (2026-03-13); preprint, venue/DOI not verified. Accessed 2026-10-18. [Primary full text](https://arxiv.org/html/2603.13070v1).

**Mechanism / access.** ADMCD fuses ViT patch, CLIP semantic and CNN texture streams with a transformer, then thresholds reference/query similarity and copy type. Reference gallery, extractors and calibrated thresholds are side information; no watermark payload. Training-time RAPTA is separate.

**Evidence.** Read §III-B, §§IV-A–E/Tables I–IV and Appendix A-A. §IV-A describes 1,200 pairs with roughly 25 exact/retrieve positives, 200 style positives and 1,000 class-consistent random negatives; §IV-B instead says 200 copied plus 1,000 noncopied pairs. Robustness tables describe one fixed pair.

**Boundary / relevance.** Threshold selection is described on an in-house test set despite earlier held-out language. No same-shot negatives or diffusion-regeneration grid establish specificity. Its SSCD bibliography misidentifies authors/title. Generic feature fusion is existing prior art; reported claims require these qualification gaps, not adoption as a proven solution.
