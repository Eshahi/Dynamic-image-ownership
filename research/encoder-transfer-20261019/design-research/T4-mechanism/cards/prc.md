# PRC image watermark — V2 refresh

Gunn, Zhao and Song, *An Undetectable Watermark for Generative Image Models*, ICLR2025, arXiv 2410.07369v4. [Primary](https://arxiv.org/html/2410.07369v4). Reuses dossier `C7-generative/cards/gunn2024prcimage.md`. Inspected §§3–4 and Appendix Figure 8 on 2026-10-19.

PRC encodes initial Gaussian signs; detection requires model inversion and secret code information. Main SD2.1 experiment uses 512-pixel output, 50 generation/inversion steps and guidance 3. Detection differs from message decoding. Figure 8 proposes robust/private VAEs to mitigate embedding attacks; it does not evaluate a trained robustified attack encoder. That distinction prevents importing an unmeasured defense into our adaptive-regenerator claim. The key-independent-input qualification of its false-positive theorem also prevents treating it as security against arbitrary key-aware forgery. Artifact/hash in manifest. No reproduction.
