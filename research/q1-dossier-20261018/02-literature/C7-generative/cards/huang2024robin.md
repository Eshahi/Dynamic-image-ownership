# ROBIN — V2 refresh

- Authors: Huayang Huang; Yu Wu; Qian Wang.
- Title: *ROBIN: Robust and Invisible Watermarks for Diffusion Models with Adversarial Optimization*. NeurIPS 2024; arXiv 2411.03862v2.
- Primary: https://arxiv.org/html/2411.03862v2 ; venue: https://proceedings.neurips.cc/paper_files/paper/2024/file/073c8584ef86bee26fe9d639ec648e28-Paper-Conference.pdf . DOI: 10.48550/arXiv.2411.03862. Access: 2026-10-18.
- Mechanism/access: inject a frequency pattern at intermediate diffusion time; optimize a hiding prompt and key. Requires generation control and offline optimization.
- Side information/cost: model, optimized prompt/key; partial diffusion inversion. Stated optimization uses 50 images and 1,000 rounds; faster inference does not remove training cost.
- Payload/data/count: key detection; SDv2 and 256-pixel Guided Diffusion; AUC uses 1,000 marked/1,000 clean images.
- Threat/evidence: §4.1/Table 1 average AUC .983 under its listed ordinary attacks; Table 3 stacked attacks degrade performance. This is not an independent matched T3 regeneration sweep.
- Limits/relevance: partial inversion reduces detector cost but remains diffusion inference. Pixel-diffusion results show broader model setting, not proof that the thesis F5 writer transfers between unrelated autoencoders.
- Inspection: fresh §§3–4.1, Tables 1/3; prior `research/literature/m1-latent-survey/cards/robin.md`. V2, no reproduction.
