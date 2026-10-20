# Gaussian Shading: Provable Performance-Lossless Image Watermarking for Diffusion Models

Stable ID: t7_gs. Citation key: T7_gs_2024. CVPR 2024; eligible top-venue evaluation. Accessed 2026-10-20. DOI: null (not verified). Authors: Yang, Zijin; Zeng, Kai; Chen, Kejiang; Fang, Han; Zhang, Weiming; Yu, Nenghai.

Canonical venue: https://openaccess.thecvf.com/content/CVPR2024/html/Yang_Gaussian_Shading_Provable_Performance-Lossless_Image_Watermarking_for_Diffusion_Models_CVPR_2024_paper.html
Full text actually inspected: https://openaccess.thecvf.com/content/CVPR2024/papers/Yang_Gaussian_Shading_Provable_Performance-Lossless_Image_Watermarking_for_Diffusion_Models_CVPR_2024_paper.pdf
Revision: CVPR 2024 final PDF. Official venue identity was separately read and verified.

Verification: V2, method and evaluation sections read; documentary evidence, not reproduction. Primary artifact: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T7-1b\gs-paper.pdf`; SHA-256 `fe4d7935082b80fc8be8fe8b1c167e8c8901e130ee9cf3642c25038af5cef9ae`. Extracted text: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T7-1b\gs-paper.txt`; SHA-256 `643e7ca6bc2319e71777764935e271b66143374cca5d82c700bb3cf77eda84ac`.

Method locator: Final CVPR PDF §3, Figure3. Evaluation locator: §§4.1–4.3, Figure5 and Table1. Personal reinspection windows (cached text, 1-based lines): [(251, 315), (511, 610), (604, 688)].

## Mechanism and threat model

[direct-evidence] Repeat and randomize message bits then sample initial latent coordinates from Gaussian quantile bins; preserve marginal noise distribution. Detect by DDIM inversion, de-randomization and repetition recovery.

## Evaluation practice rechecked for T7

[direct-evidence] Image counts and units: Detection: 1,000 positive images per watermark trial, repeated for five watermark trials. Traceability: 1,000 users × 10 images = 10,000 outputs. Quality uses 10 batches; batch size is not stated in the inspected main section. Repeated trials are not automatically independent source images.

[direct-evidence] Metrics: TPR at specified FPR, bit accuracy, FID/CLIP score over batches and t-values for generation-quality comparison.

[direct-evidence] FPR operating point: Table1 FPR1e-6; Figure5 thresholds derived for nominal approximate FPR1 down to1e-13, with empirical TPR. This does not represent1e13 independent negative trials.

[direct-evidence] Quality practice: Same SD1.4/2.0/2.1,512 image size,50 generation/inversion steps; distribution-preserving theory and FID/CLIP comparisons rather than per-source equal PSNR/SSIM/LPIPS.

[direct-evidence] Baselines: DwtDct, DwtDctSvd, RivaGAN, Stable Signature, Tree-Ring.

[direct-evidence] Conditional numbers: Default fc1/fhw8/l1 yields256 bits. Table1 adverse-noise mean TPR.997/.998/.996 for SD1.4/2.0/2.1 at nominal1e-6; corresponding bit accuracies.9753/.9749/.9724. These are the listed noise averages, not SDXL regeneration results.

## Interpretation and limits

[agent-inference] Distinguish mathematical/random-message operating points from image-level calibration; use paired fidelity for the present fixed-source study, without adding the paper's t-tests. This is a reporting choice for the present consulted development cohort, assuming native endpoint definitions and the fixed protocol remain unchanged. It is not a new baseline recommendation.

Limitations: Distributional quality theorem is not image-by-image equality. The paper's inference about performance-losslessness from low t-values is author interpretation; non-rejection is not an equivalence proof.

What was rechecked beyond inherited dossier material: the method's actual detection task, source versus repeated-output denominator, numerical operating point or its absence, native quality/capacity differences, and the evaluation table context. An NR field means not stated in the inspected window; it does not prove absence everywhere in the paper, repository, or supplement.
