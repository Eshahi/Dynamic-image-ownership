# SEAL: Semantic Aware Image Watermarking

Stable ID: t7_seal. Citation key: T7_seal_2025. ICCV 2025; eligible top-venue evaluation. Accessed 2026-10-20. DOI: null (not verified). Authors: Arabi, Kasra; Witter, R. Teal; Hegde, Chinmay; Cohen, Niv.

Canonical venue: https://openaccess.thecvf.com/content/ICCV2025/html/Arabi_SEAL_Semantic_Aware_Image_Watermarking_ICCV_2025_paper.html
Full text actually inspected: https://openaccess.thecvf.com/content/ICCV2025/papers/Arabi_SEAL_Semantic_Aware_Image_Watermarking_ICCV_2025_paper.pdf
Revision: ICCV 2025 final PDF. Official venue identity was separately read and verified.

Verification: V2, method and evaluation sections read; documentary evidence, not reproduction. Primary artifact: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T7-1b\seal-paper.pdf`; SHA-256 `28e1ab0517cf6ac501a9f1b218d0f05117229fd88ad782c7c70a289b02daf2e0`. Extracted text: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T7-1b\seal-paper.txt`; SHA-256 `21d0a869f5b59940de004503efb8523645610a328a9082f219b0f7df0019f2a5`.

Method locator: Final ICCV PDF §3.2, Algorithms1–2. Evaluation locator: Final main §4, Tables1–2; separate official supplement §§9–13, Tables3–7 (five pages). Personal reinspection windows (cached text, 1-based lines): [(238, 307), (553, 642)].

## Mechanism and threat model

[direct-evidence] Semantic embedding feeds locality-sensitive hashing to derive Gaussian-noise patches; detection compares semantically reconstructed patches with inverted noise, optionally adding a local spatial consistency test.

## Evaluation practice rechecked for T7

[direct-evidence] Image counts and units: Main removal/CatAttack evaluation-image n remains NR after reading main evaluation and the full available five-page official supplement. Supplement §11 explicitly reports 100 images for latent-forgery attacks only. Supplement §9.4 has 10,000 caption pairs for embedding fine-tuning (training), not test images. n/k=1024 denotes noise patches and b=7 denotes hash bits per patch, not image n.

[direct-evidence] Metrics: ROC-AUC for semantic forgery/CatAttack, removal detection accuracy, steganalysis AUC, and CLIP score before/after watermarking. Different tasks have different denominators.

[direct-evidence] FPR operating point: Main Tables1–2 report ROC-AUC, not a numerical low-FPR TPR operating point. Supplement §13.3 reports regeneration accuracy, without a numeric FPR/negative denominator. The 100-image latent-forgery experiment does not calibrate rare-image FPR.

[direct-evidence] Quality practice: Same SDv2/50-step generation+inversion for methods; distribution-free semantic-noise design and attack comparison. No per-source PSNR/SSIM/LPIPS matching in inspected main evaluation.

[direct-evidence] Baselines: Main: WIND, Tree-Ring, Gaussian Shading. Supplement Table6 regeneration: HiDDeN, Stable Signature, TrustMark, WOUAF.

[direct-evidence] Conditional numbers: Main CatAttack (object dimension30–60% of image): AUC .551 basicSEAL, .982 with spatial test; private-model forgery AUC .708 versus0 for listed baselines. Supplement §11 latent-forgery: complete robustness on100images (author report). Supplement §13.3 Table6 regeneration detection accuracy: SEAL98%, HiDDeN47%, StableSig41%, TrustMark5%, WOUAF51%; image n and FPR are not stated there. Do not combine these tasks into one TPR claim.

## Interpretation and limits

[agent-inference] Report content-binding misuse and presence removal separately, and state detector semantic side information; do not treat patch count as statistical sample size. This is a reporting choice for the present consulted development cohort, assuming native endpoint definitions and the fixed protocol remain unchanged. It is not a new baseline recommendation.

Limitations: Uses a semantic model and diffusion inversion; semantic binding differs from F5 content-match read endpoint. All five official supplement pages were text-inspected on2026-10-20, including explicit100-image latent-forgery experiment, but main removal/CatAttack n remainsNR. Extraction emitted wrong-pointing-object warnings; relevant prose/tables are coherent, without inferring unavailable figure details. AUC and robustness claims do not supply low-FPR calibration.

What was rechecked beyond inherited dossier material: the method's actual detection task, source versus repeated-output denominator, numerical operating point or its absence, native quality/capacity differences, and the evaluation table context. An NR field means not stated in the inspected window; it does not prove absence everywhere in the paper, repository, or supplement.

Official supplement inspected: https://openaccess.thecvf.com/content/ICCV2025/supplemental/Arabi_SEAL_Semantic_Aware_ICCV_2025_supplemental.pdf
Artifact: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T7-1b\seal-supplement.pdf`; SHA-256 `f09db824dd4b2ba008b5db42580a60f2014344492d54d669b04ae517779f5e28`. Derived text: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T7-1b\seal-supplement.txt`; SHA-256 `2b9b1bf82c85cc91ce5ddde5d5ecd05d11fd86eca3a3cf4e0b50c26c5b7a81f4`. All five pages' text was read; no experimental/source images were opened. Relevant locators §§9–13, especially §11 and §13.3.
