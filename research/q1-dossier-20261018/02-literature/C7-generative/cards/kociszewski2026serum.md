# SERUM — V2 new inspection

- Authors: Jan Kociszewski; Hubert Jastrzębski; Tymoteusz Stępkowski; Filip Manijak; Krzysztof Rojek; Franziska Boenisch; Adam Dziedzic.
- Title: *SERUM: Simple, Efficient, Robust, and Unifying Marking for Diffusion-based Image Generation*. ICLR 2026 Poster reported by arXiv author metadata; OpenReview access challenge prevented venue-page inspection. arXiv 2603.13396v1.
- Primary: https://arxiv.org/html/2603.13396v1 . DOI: 10.48550/arXiv.2603.13396. Access: 2026-10-18. Discovery: https://sprintml.com/blog/2026-04-25-serum/ .
- Mechanism/access: mix a normalized Gaussian watermark pattern into initial noise; unchanged generator; detector uses VAE encoder plus learned CNN, no diffusion inversion.
- Side information/payload/data: learned detector/fixed pattern, binary detection; 40,000 training prompts, disjoint 5,000 positive/5,000 negative test images; SD1.4/2.0/2.1.
- Evidence: §4.3/Table 2 TPR@1%FPR is 88.50% for Regen30 and 58.20% for image-to-video. Appendix C uses 256-pixel unconditional Guided Diffusion regeneration, not SD img2img strength .3.
- Limits/cost: thresholds calibrated separately per perturbation (§4.1). Appendix G reports 9.48h training including data/augmentations, A100. Natural COCO/LAION are FPR negatives, not watermarked-photo evidence.
- Relevance/inspection: strong prior against generic VAE-encoder/lightweight-detector novelty; insertion still requires generation-noise control. Fresh §§3, 4.1–4.3/Table 2, Appendices C/G/J. V2, no reproduction.
