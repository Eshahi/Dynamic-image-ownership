# Diffusion-generated watermarking taxonomy and bounded case studies

Lee and Cho, [arXiv:2610.09755v1](https://arxiv.org/html/2610.09755v1), 2026-10-07; English translation/reorganization of their Korean journal article. Inspected 2026-10-10: sections 2–7, tables 2, 4–6. Bibliography: `Lee2026TwoAxisTaxonomy`.

**Mechanism and claim:** separate insertion procedure from signal-bearing representation; distinguish verification from enrolled-key identification. Their editing discussion treats semantic imprinting as an unlocalized hypothesis, recommending paired pre/post detection and conditional retention.

**Numbers:** the PhaseMark case study reports .998 mean regeneration verification at 1% FPR, .14-second insertion and .05-second detection. Its APM quality is PSNR 31.715/LPIPS .129; PCQ is 34.156/.037. Numbers reuse earlier protocols, not our 512-square strict-quality grid.

**Limits and consequence:** neither quality operating point meets our PSNR >35 requirement; averaged regeneration detection cannot substitute for exact payload recovery. The article does not isolate the causal carrier, and its tables do not form one universal ranking. It reinforces reporting D2's original-positive retention and distinguishing latent observation from image-domain optimization. PhaseMark remains existing prior art, not a newly demonstrated local baseline or proof that our failed latent constructions exhaust the family.
