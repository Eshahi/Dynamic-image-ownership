# EditGuard: Versatile Image Watermarking for Tamper Localization and Copyright Protection

Stable ID: t7_editguard. Citation key: T7_editguard_2024. CVPR 2024; eligible top-venue evaluation. Accessed 2026-10-20. DOI: null (not verified). Authors: Zhang, Xuanyu; Li, Runyi; Yu, Jiwen; Xu, Youmin; Li, Weiqi; Zhang, Jian.

Canonical venue: https://openaccess.thecvf.com/content/CVPR2024/html/Zhang_EditGuard_Versatile_Image_Watermarking_for_Tamper_Localization_and_Copyright_Protection_CVPR_2024_paper.html
Full text actually inspected: https://openaccess.thecvf.com/content/CVPR2024/papers/Zhang_EditGuard_Versatile_Image_Watermarking_for_Tamper_Localization_and_Copyright_Protection_CVPR_2024_paper.pdf
Revision: CVPR 2024 final PDF. Official venue identity was separately read and verified.

Verification: V2, method and evaluation sections read; documentary evidence, not reproduction. Primary artifact: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T7-1b\editguard-paper.pdf`; SHA-256 `7e092c780e106a49f9bb532ea11a03f80cb67d32e627c4b39d4179f4794b4c18`. Extracted text: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T7-1b\editguard-paper.txt`; SHA-256 `637954ed12799de0a78110fd1f41bf33e943cf03e5410d11059da124fc1fec00`.

Method locator: Final CVPR PDF §§3–4.5. Evaluation locator: §§5.1–5.4, Tables1–3. Personal reinspection windows (cached text, 1-based lines): [(261, 325), (598, 687)].

## Mechanism and threat model

[direct-evidence] Sequential robust copyright-bit and semi-fragile image-localization watermarks via united image-bit steganography; compare recovered localization image with a predefined localization watermark.

## Evaluation practice rechecked for T7

[direct-evidence] Image counts and units: Watermark comparison1,000 COCO test images; AGE-Set-C30,000 training/1,200 testing images; four classical localization benchmarks have per-benchmark n not stated in inspected main table.

[direct-evidence] Metrics: Copyright bit accuracy; localization F1/AUC/IoU; PSNR/SSIM/NIQE.

[direct-evidence] FPR operating point: No fixed image-presence FPR in inspected main evaluation; localization AUC is pixel/tamper discrimination and does not calibrate copyright-presence FPR.

[direct-evidence] Quality practice: Retrains proposed method to128×128/30 bits for comparison, alongside native512×512/64-bit dual watermark. Quality and bit accuracy shown separately; not exact quality matching.

[direct-evidence] Baselines: Watermark:MBRS,CIN,PIMoG,SepMark; localization:ManTraNet,SPAN,CAT-Net,OSN,MVSS-Net,PSCC-Net,TruFor and AIGC-localization extensions.

[direct-evidence] Conditional numbers: Table2 EditGuard128/30-bit PSNR36.93 SSIM.944 bit99.89%;512/64-bit PSNR37.77 SSIM.949 bit99.95%. Table3 SDXL localization F1.965/AUC.989/IoU.936, bit99.96%; these are local-edit settings, not full img2img regeneration.

## Interpretation and limits

[agent-inference] Report side information and endpoint units; native task differences must remain visible even if some benchmark comparisons standardize payload/resolution. This is a reporting choice for the present consulted development cohort, assuming native endpoint definitions and the fixed protocol remain unchanged. It is not a new baseline recommendation.

Limitations: Extra predefined localization image is detector side information; dual localization/copyright tasks differ from arbitrary payload recovery and semantic binding. Bit and localization results cannot be collapsed into one detection rate.

What was rechecked beyond inherited dossier material: the method's actual detection task, source versus repeated-output denominator, numerical operating point or its absence, native quality/capacity differences, and the evaluation table context. An NR field means not stated in the inspected window; it does not prove absence everywhere in the paper, repository, or supplement.
