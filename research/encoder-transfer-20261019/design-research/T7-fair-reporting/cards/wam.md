# Watermark Anything With Localized Messages

Stable ID: t7_wam. Citation key: T7_wam_2025. ICLR 2025; eligible top-venue evaluation. Accessed 2026-10-20. DOI: null (not verified). Authors: Sander, Tom; Fernandez, Pierre; Oliviero Durmus, Alain; Furon, Teddy; Douze, Matthijs.

Canonical venue: https://proceedings.iclr.cc/paper_files/paper/2025/hash/c5ee1911dffe4886367eee7fca314235-Abstract-Conference.html
Full text actually inspected: https://proceedings.iclr.cc/paper_files/paper/2025/file/c5ee1911dffe4886367eee7fca314235-Paper-Conference.pdf
Revision: ICLR 2025 final PDF. Official venue identity was separately read and verified.

Verification: V2, method and evaluation sections read; documentary evidence, not reproduction. Primary artifact: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T7-1b\wam-paper.pdf`; SHA-256 `2ee08bf693643a35156733082235ff4bd850533c535e7d4517a9704ad5723f94`. Extracted text: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T7-1b\wam-paper.txt`; SHA-256 `01193fc381cdb9adfb96aee29600cfb7b0fe906fdb22b8f27349138add34b4f0`.

Method locator: Final ICLR PDF §§3–4, Eqs.1–2. Evaluation locator: §§5.1–5.5, Tables 1–2, Appendix D.3 and G.1–G.2. Personal reinspection windows (cached text, 1-based lines): [(196, 275), (351, 490)].

## Mechanism and threat model

[direct-evidence] Joint embedder and segmentation extractor return pixel-level presence probabilities plus 32 message-bit maps. Single-message decoding averages soft bit predictions over pixels whose presence exceeds a threshold; presence and payload extraction are separate tasks.

## Evaluation practice rechecked for T7

[direct-evidence] Image counts and units: First 10,000 COCO validation images and 100 DIV2K validation images; multiple-message experiments first resize images to 256. Training's 118,000 COCO images are not evaluation sources.

[direct-evidence] Metrics: Image TPR/FPR, bit accuracy, pixel localization mIoU; PSNR/SSIM/LPIPS. Multiple-message bit accuracy is conditional on discovered DBSCAN clusters.

[direct-evidence] FPR operating point: s_det>0.07; §5.3 says approximately similar COCO FPR to 16-bit detection reserve allowing <=1 error (nominal 2.6e-4). Table2a actually reports WAM FPR 0.04% and TrustMark 2.88%; DIV2K reports FP counts (WAM 0, TrustMark 5), not a finely estimated rate.

[direct-evidence] Quality practice: §5.2 explicitly adapts methods for comparable imperceptibility; original-resolution embedding/extraction with JND attenuation. Appendix G discusses perceptibility–robustness operating points. This does not calibrate the different SA-1B MIT release.

[direct-evidence] Baselines: DCTDWT, HiDDeN, TrustMark, SSL, FNNS; EditGuard for localization; generation-time comparisons in appendix.

[direct-evidence] Conditional numbers: Table2a COCO WAM: inpainting TPR97.9%, bit99.2%; splicing TPR100%, bit95.3%. These specific local-edit averages do not establish SDXL regeneration survival. All experiments use32 bits; native masks and common known-message detection are different endpoints.

## Interpretation and limits

[agent-inference] Report native zero-bit mask endpoint, common known-message endpoint, exact recovery and abstentions separately; never call theoretical bit tails measured image FPR. This is a reporting choice for the present consulted development cohort, assuming native endpoint definitions and the fixed protocol remain unchanged. It is not a new baseline recommendation.

Limitations: Paper COCO training/calibration differs from frozen MIT SA-1B release. Native mask calibration does not transfer automatically. DBSCAN-conditioned recovery must not silently omit undiscovered messages.

What was rechecked beyond inherited dossier material: the method's actual detection task, source versus repeated-output denominator, numerical operating point or its absence, native quality/capacity differences, and the evaluation table context. An NR field means not stated in the inspected window; it does not prove absence everywhere in the paper, repository, or supplement.
