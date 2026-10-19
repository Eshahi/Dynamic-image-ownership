# Gaussian Shading — V2 refresh

- Authors: Zijin Yang; Kai Zeng; Kejiang Chen; Han Fang; Weiming Zhang; Nenghai Yu.
- Title: *Gaussian Shading: Provable Performance-Lossless Image Watermarking for Diffusion Models*. CVPR 2024; inspected arXiv 2404.04956v3.
- Primary: https://arxiv.org/html/2404.04956v3 ; https://openaccess.thecvf.com/content/CVPR2024/html/Yang_Gaussian_Shading_Provable_Performance-Lossless_Image_Watermarking_for_Diffusion_Models_CVPR_2024_paper.html . DOI: 10.48550/arXiv.2404.04956. Access: 2026-10-18.
- Mechanism/access: encrypted/repeated message determines Gaussian quantile sampling in initial noise; requires control before diffusion generation.
- Side information/cost: secret stream-cipher parameters and layout; empty-prompt diffusion inversion, 50 steps in reported SD setup. Not a lightweight RGB detector.
- Payload/data: 256 payload bits repeated 64 times in the stated configuration; SD-generated evaluation. Per-attack sample count not re-extracted here.
- Threat/evidence: main robustness table concerns transformations; §4.5 discusses prompt-change forgery. Figure 7(c)'s 0.4 is a latent sign-flip rate, not img2img strength.
- Limits/relevance: marginal Gaussian distribution preservation does not establish content binding or natural-photo post-hoc insertion; distribution/security claims retain key assumptions.
- Inspection: fresh §§3.2–3.4, 4.1/Table 1, 4.5–5; prior `research/literature/m1-latent-survey/cards/gaussian-shading.md` inspected v1, now refreshed to v3. V2, no reproduction.
