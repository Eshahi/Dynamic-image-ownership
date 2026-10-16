# DinoHash and fingerprint registry

Inspected primary source 2026-10-16: https://arxiv.org/html/2503.11195v1, sections3.1 and4.1-4.2. Singhi et al., arXiv2503.11195v1.

Mechanism: DINOv2 ViT-B/14 with registers, PCA768->96, sign hash, registry Hamming search; encrypted registry is a separate component. Tests use1M DiffusionDB images, screenshot-style crops/JPEG and four additional transformations. Claimed rare FPR is binomial-model extrapolation, not observed rare errors. These sections do not establish diffusion-regeneration robustness or competing-owner enrollment resolution. Our continuous DINOv2-small and native fine-feature fingerprint ablation is not a DinoHash reproduction or external superiority comparison. It isolates the added value of our pointer versus descriptor lookup on the same local panel.
