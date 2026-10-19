# Stable Signature — V2 refresh

- Authors: Pierre Fernandez; Guillaume Couairon; Hervé Jégou; Matthijs Douze; Teddy Furon.
- Title: *The Stable Signature: Rooting Watermarks in Latent Diffusion Models*. ICCV 2023; arXiv 2303.15435v2.
- Primary: https://arxiv.org/html/2303.15435v2 ; https://openaccess.thecvf.com/content/ICCV2023/papers/Fernandez_The_Stable_Signature_Rooting_Watermarks_in_Latent_Diffusion_Models_ICCV_2023_paper.pdf . DOI: 10.48550/arXiv.2303.15435. Access: 2026-10-18.
- Mechanism/setting: pretrain and whiten a HiDDeN-style RGB extractor; fine-tune a generator's VAE decoder to a fixed signature.
- Side information/access/cost: learned extractor and reference bit string; no diffusion inversion. Model-owner decoder access; reported tuning 100 iterations, batch 4, per signature.
- Payload/data/count: 48 bits; COCO-image/prompt evaluation, §7 uses 5,000 generations. Table 1 text-to-image paired PSNR 30/SSIM .89 measures changed generator outputs, not strict preservation of an existing photograph.
- Threat/evidence: §§5–6 test transformations/detection/attribution; §7.1/Figure 7 reports removal by original-VAE recompression and adversarial attacks when extractor leaks.
- Limits/relevance: inversion-free learned extraction predates the thesis; generator-decoder fine-tuning differs from F5's RGB optimization through an encoder.
- Inspection: fresh §§3–7.1/Table 1/Figure 7; prior `research/literature/m1-primary-extension/cards-additional.md` Stable Signature entry. V2, no reproduction.
