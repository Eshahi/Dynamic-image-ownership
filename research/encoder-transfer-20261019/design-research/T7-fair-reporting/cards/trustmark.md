# TrustMark: Robust Watermarking and Watermark Removal for Arbitrary Resolution Images

Stable ID: t7_trustmark. Citation key: T7_trustmark_2025. ICCV 2025; eligible top-venue evaluation. Accessed 2026-10-20. DOI: null (not verified). Authors: Bui, Tu; Agarwal, Shruti; Collomosse, John.

Canonical venue: https://openaccess.thecvf.com/content/ICCV2025/html/Bui_TrustMark_Robust_Watermarking_and_Watermark_Removal_for_Arbitrary_Resolution_Images_ICCV_2025_paper.html
Full text actually inspected: https://openaccess.thecvf.com/content/ICCV2025/papers/Bui_TrustMark_Robust_Watermarking_and_Watermark_Removal_for_Arbitrary_Resolution_Images_ICCV_2025_paper.pdf
Revision: ICCV 2025 final PDF. Official venue identity was separately read and verified.

Verification: V2, method and evaluation sections read; documentary evidence, not reproduction. Primary artifact: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T7-1b\trustmark-paper.pdf`; SHA-256 `94be2a50e08356b321c4f64a56579eeb63ea4676634ac9c019e3c76f6c5726f5`. Extracted text: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T7-1b\trustmark-paper.txt`; SHA-256 `aeb6cb1769f7c1c3cee2203d3614efa2a0bb851388d4d7fb3dee7083a1d6d871`.

Method locator: Final ICCV PDF §3.1 and Algorithm1. Evaluation locator: §§4.1–4.3, Tables1–2 and Figure3. Personal reinspection windows (cached text, 1-based lines): [(181, 265), (361, 480)].

## Mechanism and threat model

[direct-evidence] MUNIT-style image/message embedder and ResNet50 extractor, trained with noise simulation and quality/recovery losses; resolution scaling adds an upsampled residual with controllable factor lambda. ReMark is a separate removal network.

## Evaluation practice rechecked for T7

[direct-evidence] Image counts and units: CLIC, MetFace and DIV2K (both training and validation images used for evaluation because DIV2K test is not public). Exact evaluated counts are not stated in inspected §4.1/Table1; 100K train+1K validation MIRFlickR is training provenance, not test n.

[direct-evidence] Metrics: Original-resolution PSNR and bit accuracy after random noises; §4.1 deliberately omits saturated SSIM/SFID and clean bit accuracy.

[direct-evidence] FPR operating point: No fixed numerical image-FPR operating point or measured image-FPR denominator in inspected §§4.1–4.3; bit accuracy is not an FPR estimate.

[direct-evidence] Quality practice: Default lambda=1 applied to proposed method and baselines, resolution scaling except native-resolution RivaGAN/shallow methods; baseline retraining with same noises if helpful. Figure3 varies training alpha and inference residual scale. No per-source equal-distortion matching is claimed.

[direct-evidence] Baselines: RoSteALS, RivaGAN, SSL, StegaStamp, dwtDctSvd; paper also discusses WAM/OmniGuard numbers on distinct COCO subsets.

[direct-evidence] Conditional numbers: Table1 alpha_max27.5: DIV2K PSNR42.39±1.46, noised bit accuracy0.95±0.09; Table2 different ImageNet-C/CLIC setting uses alpha_max15 and PSNR38.87±1.42, bit0.95±0.08. Neither number is matched to the other row's setting.

## Interpretation and limits

[agent-inference] Show fixed native quality as measured and distinguish training/release settings; a displayed strength frontier in another paper does not authorize retuning frozen baselines. This is a reporting choice for the present consulted development cohort, assuming native endpoint definitions and the fixed protocol remain unchanged. It is not a new baseline recommendation.

Limitations: Final ICCV2025 paper adds material beyond 2023 arXiv TrustMark. Do not transfer release checkpoint behavior, bit length or FPR from older versions. Exact evaluation n remains NR rather than inferred from dataset convention.

What was rechecked beyond inherited dossier material: the method's actual detection task, source versus repeated-output denominator, numerical operating point or its absence, native quality/capacity differences, and the evaluation table context. An NR field means not stated in the inspected window; it does not prove absence everywhere in the paper, repository, or supplement.
