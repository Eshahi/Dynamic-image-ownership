# SpecGuard: Spectral Projection-based Advanced Invisible Watermarking

Stable ID: t7_specguard. Citation key: T7_specguard_2025. ICCV 2025; eligible top-venue evaluation. Accessed 2026-10-20. DOI: null (not verified). Authors: Alam, Inzamamul; Islam, Md Tanvir; Woo, Simon S.; Muhammad, Khan.

Canonical venue: https://openaccess.thecvf.com/content/ICCV2025/html/Alam_SpecGuard_Spectral_Projection-based_Advanced_Invisible_Watermarking_ICCV_2025_paper.html
Full text actually inspected: https://openaccess.thecvf.com/content/ICCV2025/papers/Alam_SpecGuard_Spectral_Projection-based_Advanced_Invisible_Watermarking_ICCV_2025_paper.pdf
Revision: ICCV 2025 final PDF. Official venue identity was separately read and verified.

Verification: V2, method and evaluation sections read; documentary evidence, not reproduction. Primary artifact: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T7-1b\specguard-paper.pdf`; SHA-256 `f23bbfbc1a88d141117b10045539488c687267095928b587d4ff4c07dee6683e`. Extracted text: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T7-1b\specguard-paper.txt`; SHA-256 `9e9480bad7db7383236d67384c24d77dd843b3b494d1f8ba95acc5db09251799`.

Method locator: Final ICCV PDF §3, Figure2, Eqs.6–11. Evaluation locator: §§4.1–4.5, Tables1–3. Personal reinspection windows (cached text, 1-based lines): [(291, 380), (596, 703)].

## Mechanism and threat model

[direct-evidence] Wavelet decomposition plus spectral projection into high-frequency hidden convolution features; strength-controlled embedding and a learned extractor.

## Evaluation practice rechecked for T7

[direct-evidence] Image counts and units: 25K COCO images are training data. Main robustness uses DiffusionDB/COCO/DALL·E3 with inherited WAVES setup but per-dataset evaluated n not explicit in inspected main section. Separate social-media/Photoshop check uses200 COCO images. Quality subsets' n is NR.

[direct-evidence] Metrics: BRA, PSNR/SSIM/FID/MSE, WAVES-style Q@0.95P/Q@0.7P/AvgP/AvgQ.

[direct-evidence] FPR operating point: WAVES setup is cited, but no explicit numerical image-FPR threshold or negative count stated in inspected§4.2/Table3; do not silently import0.1% as verified implementation.

[direct-evidence] Quality practice: Resolution256/512/1024 and payload sweeps; native-quality comparisons and attack-quality summary metrics. No exact cross-method paired caliper matching.

[direct-evidence] Baselines: Tree-Ring,Stable Signature,Gaussian Shading,SleeperMark,HiDDeN,StegaStamp,MBRS,FIN,MuST,EditGuard.

[direct-evidence] Conditional numbers: Table2 clean128-bit SpecGuard PSNR42.89, SSIM.99, FID17.0, BRA.99. Table1 separate30-bit COCO512 quality PSNR44.680/SSIM.9927; the two tables' payloads are not interchangeable.

## Interpretation and limits

[agent-inference] Preserve NR fields rather than backfill convenient inherited settings; include complete denominators and operating points in our own report. This is a reporting choice for the present consulted development cohort, assuming native endpoint definitions and the fixed protocol remain unchanged. It is not a new baseline recommendation.

Limitations: Missing exact n and FPR details limit reproduction; bibliographic eligibility does not make every evaluation setting complete. Some comparisons change payload/resolution. Do not infer a common detection test from BRA alone.

What was rechecked beyond inherited dossier material: the method's actual detection task, source versus repeated-output denominator, numerical operating point or its absence, native quality/capacity differences, and the evaluation table context. An NR field means not stated in the inspected window; it does not prove absence everywhere in the paper, repository, or supplement.
