# WIND — V2 refresh

- Authors: Kasra Arabi; Benjamin Feuer; R. Teal Witter; Chinmay Hegde; Niv Cohen.
- Title: *Hidden in the Noise: Two-Stage Robust Watermarking for Images*. ICLR 2025; arXiv 2412.04653v5.
- Primary: https://arxiv.org/html/2412.04653v5 ; https://proceedings.iclr.cc/paper_files/paper/2025/file/999fcab97007ebef0cda9949550b4a9e-Paper-Conference.pdf . DOI: 10.48550/arXiv.2412.04653. Access: 2026-10-18.
- Mechanism/side information: secret seeded initial-noise bank plus Fourier group identifier; diffusion inversion and group/full-bank similarity search. SD2, 50 generation/inversion steps.
- Payload/data/count: noise identity, not arbitrary payload. Appendix D.3/Table 7 searches 10,000 candidates after repeated regeneration; reports 100% identification at 10–50 iterations, specific to that experiment.
- Natural-photo evidence: §4.3 inpainting; Appendix D.2/Table 6 uses 100 noises. Appendix D.4/Table 10 reports SSIM .768/PSNR 26.806 dB, below the thesis strict fidelity gate.
- Threat/limits: full fallback costs linear bank search; private-model/inversion assumptions are acknowledged limitations. §6 proposes a database of generations storing prompts/seeds to investigate content edits preserving watermark.
- Relevance/inspection: natural-photo applicability and generic registry ideas already exist; this is not lightweight extraction. Fresh §§3–6, Appendix C/D.2–D.4; prior `research/literature/m1-latent-survey/cards/wind.md`. V2, no reproduction.
