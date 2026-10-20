# PECCVAI: Overcoming the Brittleness of AI Image Watermarking Under Visual Paraphrasing Attacks

Stable ID: t7_peccvai. Citation key: T7_peccvai_2026. CVPR 2026; eligible top-venue evaluation. Accessed 2026-10-20. DOI: null (not verified). Authors: Dixit, Shreyas; Aziz, Ashhar; Bajpai, Shashwat; Sharma, Vasu; Chadha, Aman; Jain, Vinija; Das, Amitava.

Canonical venue: https://openaccess.thecvf.com/content/CVPR2026/html/Dixit_PECCVAI_Overcoming_the_Brittleness_of_AI_Image_Watermarking_Under_Visual_CVPR_2026_paper.html
Full text actually inspected: https://openaccess.thecvf.com/content/CVPR2026/papers/Dixit_PECCVAI_Overcoming_the_Brittleness_of_AI_Image_Watermarking_Under_Visual_CVPR_2026_paper.pdf
Revision: CVPR 2026 final PDF. Official venue identity was separately read and verified.

Verification: V2, method and evaluation sections read; documentary evidence, not reproduction. Primary artifact: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T7-1b\peccvai-paper.pdf`; SHA-256 `1fd41b97fe1c3aef51c5507654127b9419e540e75760dfced7654dc5cc3334a6`. Extracted text: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T7-1b\peccvai-paper.txt`; SHA-256 `f25b61edff5a18630a754fed6c2dc472f098dd0792f61a9add9b301682c32283`.

Method locator: Final CVPR2026 PDF §§3.1–3.2, Figure4. Evaluation locator: §§4.1–4.3 and Table1. Personal reinspection windows (cached text, 1-based lines): [(281, 380), (571, 670)].

## Mechanism and threat model

[direct-evidence] Find non-mutable patches through repeated paraphrases and saliency/stability, then embed Fourier patterns in selected patches/channels with strength depending on region consistency.

## Evaluation practice rechecked for T7

[direct-evidence] Image counts and units: 500 randomly sampled COCO images using supplied COCO captions; region selection uses SD2.1-base and visual paraphrasing usesSDXL. Five paraphrases for non-mutable patch consistency are part of method selection, not5 independent evaluation cohorts.

[direct-evidence] Metrics: Watermark Detection Probability(WDP), PSNR/SSIM/FID in main table; CLIP/MOS semantic preservation referred to appendix, not independently verified here.

[direct-evidence] FPR operating point: No numerical image-FPR operating point or negative-image denominator in inspected main§4/Table1. WDP is not automatically TPR at matchedFPR.

[direct-evidence] Quality practice: Reports different saliency methods/top30/40/50 choices, native quality and paraphrase strengths. Native PSNR differs substantially across baselines; no per-source matched-distortion comparison.

[direct-evidence] Baselines: DwtDctSVD,Stable Signature,WAM,ZoDiac,Tree-Ring,Gaussian Shading and proposed saliency variants.

[direct-evidence] Conditional numbers: Table1 WAM PSNR46.05/SSIM1.000 and WDP.63/.56 at paraphrase strengths.1/.2; ZoDiac PSNR28.47/SSIM.920 WDP.81/.70; MSI-Net top50 PSNR30.71/SSIM.94 WDP.87/.83. Unequal quality and unspecified imageFPR prevent a fair direct superiority conclusion.

## Interpretation and limits

[agent-inference] Recent independently trained encoder transfer remains a live evaluation theme; insist on quality and image-FPR qualifiers before interpreting a leaderboard, while keeping the present preregistered grid frozen. This is a reporting choice for the present consulted development cohort, assuming native endpoint definitions and the fixed protocol remain unchanged. It is not a new baseline recommendation.

Limitations: Official CVF title spellsPECCVAI; paper body spellsPECCAVI. Final venue is verifiedCVPR2026, not inferred from the2025 preprint. Appendix MOS was not read and is not borrowed as a human verdict. Architectural separation alone is not a universal robustness proof.

What was rechecked beyond inherited dossier material: the method's actual detection task, source versus repeated-output denominator, numerical operating point or its absence, native quality/capacity differences, and the evaluation table context. An NR field means not stated in the inspected window; it does not prove absence everywhere in the paper, repository, or supplement.
