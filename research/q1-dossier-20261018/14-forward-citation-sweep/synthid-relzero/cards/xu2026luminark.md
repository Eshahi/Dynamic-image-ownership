# xu2026luminark — V2

Jiayi Xu et al. Luminark: Training-free, Probabilistically-Certified Watermarking for General Vision Generative Models. arXiv:2601.01085v1 (2026-01-03), inspected 2026-10-19. [Primary text](https://arxiv.org/html/2601.01085v1); cache/hash in `../source-artifacts.json`.

**Citation edge:** References, Gowal et al. (2025), exact SynthID-Image title and arXiv:2510.09263.

**Direct evidence:** Sections 3.1–3.3 define secret binary patch patterns and luminance thresholds. Generation guidance and repeated sampling encourage matching; detection uses patch luminance, without inversion. Proposition 1 bounds false matches over independent random key sampling for a fixed image. Section 4.1 evaluates nine generators, 1,000 marked and 1,000 unmarked examples per method, conventional transforms and 20 seeds. Table 1 reports EDM2-L mean detection accuracy 95.49%; this is not TPR at a fixed FPR. Section 4.2 uses distribution-level FID; Section 5 discusses generation overhead.

**Author interpretation:** A general, probabilistically certified watermark detector.

**Our inference/limits:** Random-key certification does not itself establish adaptive-forgery resistance or arbitrary-distribution FPR for one fixed key. The inspected evaluation does not establish registered-image attribution or regeneration robustness. FID does not measure paired content identity. No thesis experiment or new-baseline authorization follows.
