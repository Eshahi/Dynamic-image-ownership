# Robust Watermarking Using Generative Priors Against Image Editing: From Benchmarking to Advances

Stable ID: t7_vine. Citation key: T7_vine_2025. ICLR 2025; eligible top-venue evaluation. Accessed 2026-10-20. DOI: null (not verified). Authors: Lu, Shilin; Zhou, Zihan; Lu, Jiayou; Zhu, Yuanzhi; Kong, Adams.

Canonical venue: https://proceedings.iclr.cc/paper_files/paper/2025/hash/d077bc9ea82a2998ca6b2d0158b5ac6e-Abstract-Conference.html
Full text actually inspected: https://arxiv.org/html/2410.18775v2
Revision: arXiv 2410.18775v2 (official PDF transport failure). Official venue identity was separately read and verified.

Verification: V2, method and evaluation sections read; documentary evidence, not reproduction. Primary artifact: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T7-1b\vine-reused.html`; SHA-256 `f6fb25d7b27ec0e95f883674e2e08a41a9075f5929e76287f02330e339e049dd`. Extracted text: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T7-1b\vine-reused.txt`; SHA-256 `46787d558a32df39faa09346ec501f618c75cbb7b080743b1e96bcbf45b2844e`.

Method locator: arXiv 2410.18775v2 §3.2–3.3, Appendix D and F. Evaluation locator: §4.2–4.3, Table 1, Figure 5, Appendix C and G.2. Personal reinspection windows (cached text, 1-based lines): [(411, 487), (513, 592), (745, 780)].

## Mechanism and threat model

[direct-evidence] VINE conditions an SDXL-Turbo generative prior on image plus message, adds VAE skip connections, and decodes 100 bits with ConvNeXt-B. VINE-R further tunes VINE-B through partial InstructPix2Pix differentiation.

## Evaluation practice rechecked for T7

[direct-evidence] Image counts and units: Unresolved within-paper denominator conflict: §4.2 partitions10,000 UltraEdit instances into1,000 stochastic regeneration,1,000 deterministic regeneration,1,000 global editing,5×1,000 local-edit mask strata,1,000 image-to-video and1,000 conventional distortion; §4.3 says m×1,000 outputs over m difficulty levels. Table1 caption instead says TPR for each specific editing method is averaged over5,000 images. Quality uses10,000 pairs. Do not reconstruct one unified denominator from these conflicting statements.

[direct-evidence] Metrics: TPR@0.1% and 1% FPR, AUROC and raw bit accuracy without BCH; PSNR/SSIM/LPIPS/FID; editing-quality CLIP measures in Appendix G.

[direct-evidence] FPR operating point: Original and marked images both enter decoders for empirical operating-point evaluation. Appendix C's Bernoulli bit-null discussion is distinct; its displayed >= decision and > tail notation also require explicit endpoint conventions when implementing.

[direct-evidence] Quality practice: Official released checkpoints; common 512×512 evaluation via resolution scaling; native payloads and quality differ. Figures vary editing difficulty, not per-source equal-quality optimization.

[direct-evidence] Baselines: MBRS, CIN, PIMoG, RivaGAN, SepMark, TrustMark, DWTDCT, DWTDCTSVD, SSL, StegaStamp, EditGuard.

[direct-evidence] Conditional numbers: Eleven baseline methods. The text reports SSL unmarked-image bit agreement can exceed 0.7, explaining why higher bit accuracy/AUROC need not imply higher low-FPR TPR; this is not a universal SSL threshold.

## Interpretation and limits

[agent-inference] Preserve native 100-bit VINE-R, raw agreement and exact recovery; add empirical ROC with honest finite-negative resolution. Do not force its payload or native quality to equal F5. This is a reporting choice for the present consulted development cohort, assuming native endpoint definitions and the fixed protocol remain unchanged. It is not a new baseline recommendation.

Limitations: Inspected arXiv v2 full text; official proceedings PDF retrieval failed. Venue is ICLR2025, notICCV. The §4.2/§4.3 versusTable1caption image-count conflict remains unresolved and is preserved. No universal released VINE-R native presence cutoff is established by this paper. SDXL-Turbo ancestry must remain visible when comparing SDXL transfer.

What was rechecked beyond inherited dossier material: the method's actual detection task, source versus repeated-output denominator, numerical operating point or its absence, native quality/capacity differences, and the evaluation table context. An NR field means not stated in the inspected window; it does not prove absence everywhere in the paper, repository, or supplement.
