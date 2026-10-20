# Attack-Resilient Image Watermarking Using Stable Diffusion

Stable ID: t7_zodiac. Citation key: T7_zodiac_2024. NeurIPS 2024; eligible top-venue evaluation. Accessed 2026-10-20. DOI: null (not verified). Authors: Zhang, Lijun; Liu, Xiao; Martin, Antoni V.; Bearfield, Cindy X.; Brun, Yuriy; Guan, Hui.

Canonical venue: https://proceedings.neurips.cc/paper_files/paper/2024/hash/43d33182360378d5c8e69dd706c24f2f-Abstract.html
Full text actually inspected: https://proceedings.neurips.cc/paper_files/paper/2024/file/43d33182360378d5c8e69dd706c24f2f-Paper-Conference.pdf
Revision: NeurIPS 2024 final PDF. Official venue identity was separately read and verified.

Verification: V2, method and evaluation sections read; documentary evidence, not reproduction. Primary artifact: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T7-1b\zodiac-paper.pdf`; SHA-256 `3f4e0a431674cfdfb1aac89b0c37c48209f36cd6d3789477eec37cb361b51a4a`. Extracted text: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T7-1b\zodiac-paper.txt`; SHA-256 `6ce8fcaed7dea3f5fc34697a20882692ef98159cee18468abc63875e40749387`.

Method locator: Final NeurIPS PDF §§3.1–3.3, Algorithm1 andEq.9. Evaluation locator: §§4.1–4.4, Tables1–3 and Figure3. Personal reinspection windows (cached text, 1-based lines): [(282, 377), (378, 477), (491, 560)].

## Mechanism and threat model

[direct-evidence] Optimize an inverted initial latent containing a Fourier watermark through frozen Stable Diffusion, then adaptively blend with original image for SSIM. Detection inverts the suspect and applies a noncentral-chi-square distance test.

## Evaluation practice rechecked for T7

[direct-evidence] Image counts and units: 500 images each from MS-COCO,DiffusionDB,WikiArt (1,500 distinct source images across domains), evaluated across attacks/settings; primary SD2.1-base50 steps, maximum100 optimization iterations.

[direct-evidence] Metrics: Watermark Detection Rate(WDR=TPR), empirical FPR, PSNR/SSIM/LPIPS; WDR-versus-native-SSIM trade-offs.

[direct-evidence] FPR operating point: Table3 COCO: p_star.90/.95/.99 yields measuredFPR.062/.030/.004 and Zhao23WDR.988/.974/.938. Baselines use nominal p<.01 with24/32 or61/96 matching bits. These empiricalFPRs are not equal merely because p-value tests were used.

[direct-evidence] Quality practice: Adaptive image enhancement and SSIM threshold sweep. Figure3 s_star.8–.98 in.03 increments compares robustness versus native watermark quality; no three-metric per-source caliper match.

[direct-evidence] Baselines: DwtDct,DwtDctSvd,RivaGAN,SSL,CIN,StegaStamp;32-bit messages except96-bitStegaStamp.

[direct-evidence] Conditional numbers: At p_star.99 Table3 cleanWDR.992, Zhao23.938, All-without-rotation.166, FPR.004. At.90 Zhao23.988 comes withFPR.062; quoting.988 without that false-positive condition is misleading.

## Interpretation and limits

[agent-inference] Preserve native-quality sensitivity as descriptive and show measuredFPR next to every WDR; nominal significance levels across different tests do not guarantee fair actual operating points. This is a reporting choice for the present consulted development cohort, assuming native endpoint definitions and the fixed protocol remain unchanged. It is not a new baseline recommendation.

Limitations: Official venue isNeurIPS2024, neitherECCV norACMMM. Default writer SD2.1 model differs from an independent-encoder regeneration claim. Native-quality enhancement can reduce robustness and cannot be treated as free equalization.

What was rechecked beyond inherited dossier material: the method's actual detection task, source versus repeated-output denominator, numerical operating point or its absence, native quality/capacity differences, and the evaluation table context. An NR field means not stated in the inspected window; it does not prove absence everywhere in the paper, repository, or supplement.
