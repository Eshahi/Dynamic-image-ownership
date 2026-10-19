# ao2026awpd — V2

Xiang Ao, Yilin Du, Zidan Wang, Mengru Chen, Siyang Lu. AWPD: Frequency Shield Network for Agnostic Watermark Presence Detection. arXiv:2603.06723v3 (2026-04-17), inspected 2026-10-19. [Primary text](https://arxiv.org/html/2603.06723v3); cache/hash in `../source-artifacts.json`.

**Citation edge:** Reference 10 identifies SynthID-Image, arXiv:2510.09263. Earlier v2 was also read; v3 governs this card.

**Direct evidence:** Sections 3–5 formulate watermark-presence classification without decoding information. FSNet combines learnable DCT gates, a ResNet-50 backbone, spectral attention and extremum pooling. Section 4/Appendix A.3 describe 190,000 images (94,000 marked, 96,000 unmarked) despite the UniFreq-100K name. Sections 4.2/6.1 use balanced leave-one-algorithm-out evaluation. Table 1 gives SynthID accuracy .894/F1 .886, versus accuracy .594 for LSB and .587 for Patchwork. Appendix A.2.3 obtains 2,000 SynthID samples from Imagen's generation API.

**Author interpretation:** Generalization to unseen watermark algorithms.

**Our inference/limits:** Presence classification does not recover an owner, payload or registered record. Dataset balancing does not independently establish a paired causal watermark-only comparison; generation traces may contribute. It supplies no evidence for the thesis's incremental q/content gate.
