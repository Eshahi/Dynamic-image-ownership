# OmniGuard: Hybrid Manipulation Localization via Augmented Versatile Deep Image Watermarking

Stable ID: t7_omniguard. Citation key: T7_omniguard_2025. CVPR 2025; eligible top-venue evaluation. Accessed 2026-10-20. DOI: null (not verified). Authors: Zhang, Xuanyu; Tang, Zecheng; Xu, Zhipei; Li, Runyi; Xu, Youmin; Chen, Bin; Gao, Feng; Zhang, Jian.

Canonical venue: https://openaccess.thecvf.com/content/CVPR2025/html/Zhang_OmniGuard_Hybrid_Manipulation_Localization_via_Augmented_Versatile_Deep_Image_Watermarking_CVPR_2025_paper.html
Full text actually inspected: https://openaccess.thecvf.com/content/CVPR2025/papers/Zhang_OmniGuard_Hybrid_Manipulation_Localization_via_Augmented_Versatile_Deep_Image_Watermarking_CVPR_2025_paper.pdf
Revision: CVPR 2025 final PDF. Official venue identity was separately read and verified.

Verification: V2, method and evaluation sections read; documentary evidence, not reproduction. Primary artifact: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T7-1b\omniguard-paper.pdf`; SHA-256 `4e8a7cf6f4b7c8350ce1651bbb5c5c02739fcb3b15be5b76b9bb2f0f32ca50e5`. Extracted text: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T7-1b\omniguard-paper.txt`; SHA-256 `65c2958d813865d27000bb7bb0de7c9abb1558dad4e2798017be92c144112659`.

Method locator: Final CVPR PDF §3, Figure4. Evaluation locator: §§4.1–4.3, Table3. Personal reinspection windows (cached text, 1-based lines): [(281, 345), (561, 660)].

## Mechanism and threat model

[direct-evidence] Proactive dual watermark augmented with VAE-based AIGC simulation and degradation-aware passive tamper extraction; robust copyright retrieval is distinct from localization.

## Evaluation practice rechecked for T7

[direct-evidence] Image counts and units: Localization:1,000 COCO test samples; watermark/fidelity comparison:1,000 UltraEdit512×512 images with paired prompts (§4.3). Tamper extractor20,000 constructed pairs are training data.

[direct-evidence] Metrics: Localization F1/AUC; copyright bit recovery; PSNR/SSIM.

[direct-evidence] FPR operating point: No fixed numerical image-presence FPR in inspected evaluation. Localization AUC and copyright bit accuracy are different metrics.

[direct-evidence] Quality practice: Table3 native30/64/100-bit methods with/without extra localization watermark; reports paired quality and recovery, no equal-quality tuning or per-source caliper.

[direct-evidence] Baselines: PIMoG,SepMark,TrustMark,EditGuard,Robust-Wide for watermarking;PSCC-Net,MVSS-Net,CAT-Net,HiFi-Net,IML-ViT,EditGuard for localization.

[direct-evidence] Conditional numbers: Table3 OmniGuard100-bit copyright-only PSNR42.33 SSIM.992 and InstructPix2Pix bit.981; dual watermark PSNR41.78 SSIM.989 bit.979. SD Inpaint* (regenerating outside original content) and strictly local SD Inpaint are explicitly distinct columns.

## Interpretation and limits

[agent-inference] Separate native single-/dual-task arms and attack definitions; captions must name whether unedited pixels were restored. This is a reporting choice for the present consulted development cohort, assuming native endpoint definitions and the fixed protocol remain unchanged. It is not a new baseline recommendation.

Limitations: Table header labels bit accuracy (%) but entries are fractions such as.981; preserve raw scale and explain as98.1% only when converting. Local edits that retain unedited pixels do not measure full-image independent-encoder regeneration.

What was rechecked beyond inherited dossier material: the method's actual detection task, source versus repeated-output denominator, numerical operating point or its absence, native quality/capacity differences, and the evaluation table context. An NR field means not stated in the inspected window; it does not prove absence everywhere in the paper, repository, or supplement.
