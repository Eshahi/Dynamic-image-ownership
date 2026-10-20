# Hidden in the Noise: Two-Stage Robust Watermarking for Images

Stable ID: t7_wind. Citation key: T7_wind_2025. ICLR 2025; eligible top-venue evaluation. Accessed 2026-10-20. DOI: null (not verified). Authors: Arabi, Kasra; Feuer, Benjamin; Witter, R. Teal; Hegde, Chinmay; Cohen, Niv.

Canonical venue: https://proceedings.iclr.cc/paper_files/paper/2025/hash/999fcab97007ebef0cda9949550b4a9e-Abstract-Conference.html
Full text actually inspected: https://proceedings.iclr.cc/paper_files/paper/2025/file/999fcab97007ebef0cda9949550b4a9e-Paper-Conference.pdf
Revision: ICLR 2025 final PDF. Official venue identity was separately read and verified.

Verification: V2, method and evaluation sections read; documentary evidence, not reproduction. Primary artifact: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T7-1b\wind-paper.pdf`; SHA-256 `628e6b51865c25ef88d9d49b34b7e7f7d5af731b1e14d82dce851a06e9cafcfc`. Extracted text: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T7-1b\wind-paper.txt`; SHA-256 `b2e07e80944c08501568430880876e1ae54c30931b921e5d416076717b26f430`.

Method locator: Final ICLR PDF §§3–4.1 and AppendixH. Evaluation locator: §5.1, Tables1–3; final-PDF AppendixD.1–D.9 (pp20–24), G/H (pp25–26), Table11 (p23). Personal reinspection windows (cached text, 1-based lines): [(255, 301), (347, 401), (780, 898), (976, 1004)].

## Mechanism and threat model

[direct-evidence] Dictionary of initial Gaussian noises; Fourier group identifiers narrow candidate search, then noise similarity validates a match. WINDfull searches all candidates if group search fails; inversion/rotation/crop search is part of detection.

## Evaluation practice rechecked for T7

[direct-evidence] Image counts and units: Main robustness/quality evaluation-image n remains NR after searching the full available final PDF and reading AppendixD.1–D.9/G/H. N=100,000 in main variants and runtime is dictionary noise/key count; D.1 N=10,000 noises and D.2 N=100 initial noises are likewise not stated as evaluation-image denominators. No count is inferred from decimal accuracy increments.

[direct-evidence] Metrics: Correct watermark/key detection accuracy, cosine similarity, FID; appendix AUC and TPR@1% FPR; PSNR/SSIM for inpainted natural images.

[direct-evidence] FPR operating point: AppendixD.6/Table11 reports AUC.971 and TP@1%1.000; main key-identification table has a different endpoint. Negative sample count and selected raw similarity cutoff are not explicit in inspected sections.

[direct-evidence] Quality practice: Same SDv2 and50 generation/inversion steps; FID for generated images, PSNR/SSIM for natural-image inpainting; no exact paired matched-quality comparison.

[direct-evidence] Baselines: Tree-Ring,RingID main;DwtDctSvd,RivaGAN also in FID table;additional methods in appendices.

[direct-evidence] Conditional numbers: Table1 WINDfull with2048 groups/100000 keys: average accuracy.969, crop&scale.930; WINDfast corresponding crop&scale.060. Table9 natural-image inpainting PSNR26.806/SSIM.768, distinct from generation FID24.33.

## Interpretation and limits

[agent-inference] List detector access/search cost and native mode; do not equate different identification and detection operating points or infer independent samples from key count. This is a reporting choice for the present consulted development cohort, assuming native endpoint definitions and the fixed protocol remain unchanged. It is not a new baseline recommendation.

Limitations: Dictionary size is side information and not payload-bit count or evaluation n. Full versus fast search and generated versus inpainted modes differ materially. Main-image n remains NR rather than guessed from decimal steps. Unresolved internal inconsistency: final Table11 reports AUC .971 and TP@1% 1.000. If both summarize the same standard monotone ROC, TPR=1 at FPR=.01 implies AUC>=.99. Neither rounding nor column extraction resolves this gap; no distinct aggregation explanation was found in inspected AppendixD.6. Preserve both as reported, not coherent calibration evidence. The parent agent rendered and visually inspected final-PDF page 23 on 2026-10-20; cache wind-render/page-023.png confirms the headers and ordering. This is attributed visual verification, not a claim that the T7 author performed that rendering.

What was rechecked beyond inherited dossier material: the method's actual detection task, source versus repeated-output denominator, numerical operating point or its absence, native quality/capacity differences, and the evaluation table context. An NR field means not stated in the inspected window; it does not prove absence everywhere in the paper, repository, or supplement.
