# PECCVAI: Overcoming the Brittleness of AI Image Watermarking Under Visual Paraphrasing Attacks

ID: `peccvai`. Verification: **V2, own T1 method and evaluation recheck**. Conservative direct floor: **supplemental only**.

Authors: Shreyas Dixit; Ashhar Aziz; Shashwat Bajpai; Vasu Sharma; Aman Chadha; Vinija Jain; Amitava Das. Version/date: CVPR 2026 final paper; proceedings pp. 24471--24480. Venue: CVPR 2026; official CVF final paper artifact. DOI: not independently verified. Citation key: `T1_peccvai`. Accessed 2026-10-20.

Primary: [https://openaccess.thecvf.com/content/CVPR2026/html/Dixit_PECCVAI_Overcoming_the_Brittleness_of_AI_Image_Watermarking_Under_Visual_CVPR_2026_paper.html](https://openaccess.thecvf.com/content/CVPR2026/html/Dixit_PECCVAI_Overcoming_the_Brittleness_of_AI_Image_Watermarking_Under_Visual_CVPR_2026_paper.html); [inspected full text](https://openaccess.thecvf.com/content/CVPR2026/papers/Dixit_PECCVAI_Overcoming_the_Brittleness_of_AI_Image_Watermarking_Under_Visual_CVPR_2026_paper.pdf).

Inspected artifact source: [official CVF PDF](https://openaccess.thecvf.com/content/CVPR2026/papers/Dixit_PECCVAI_Overcoming_the_Brittleness_of_AI_Image_Watermarking_Under_Visual_CVPR_2026_paper.pdf).

Cache: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T7-1b\peccvai-paper.pdf` (1208686 bytes). SHA-256: `1fd41b97fe1c3aef51c5507654127b9419e540e75760dfced7654dc5cc3334a6`. Derived text: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T7-1b\peccvai-paper.txt`; SHA-256 `f25b61edff5a18630a754fed6c2dc472f098dd0792f61a9add9b301682c32283`.

Inspected: Own T1 recheck: Section 2.1 visual paraphraser; Sections 3.1--3.3 and 4.1--4.4; Tables 1--3. Cached method lines 216--445 and evaluation lines 570--697. Official CVF PDF reused and independently read; live web re-open returned 403, retained as an access event rather than substituted for cached full text.

## Mechanism and attacker access

New visual-paraphrasing benchmark plus defense. Image and caption enter img2img. Defense finds stable salient patches across five paraphrases, embeds latent Fourier rings and scans patches/channels for maximum confidence.

## Models

NMP uses SD2.1-base; the attack uses SDXL. Table 1 compares DwtDctSvd, Stable Signature, WAM, ZoDiac, Tree-Ring, Gaussian Shading and PECCAVI.

## Strength / noise

Attack paraphrase strengths .1/.2; Table 3 uses learned compression quality 3.

## Sampler / steps

Defense uses DDIM inversion. Attack scheduler, steps and exact SDXL revision NR in inspected main paper; supplementary implementation not inspected.

## Prompt / guidance

Existing COCO captions, rather than tested captioner outputs; numeric attack CFG NR here.

## Resolution

Table 3 explicitly states 512 x 512; general Table 1 paraphrase resolution NR in inspected main paper.

## Image counts and units

500 randomly sampled COCO images; repeated configurations reuse sources. Per-condition processed/failure denominators NR here.

## Metrics

WDP means bit accuracy for payload schemes and detector confidence for zero-bit schemes; the proposed detector takes a maximum over patches/channels. Embedding PSNR, SSIM and FID. Calibrated image-level FPR NR.

## Conditioned numerical results

Table 1 at strengths .1/.2: WAM WDP .63/.56; Stable Signature .59/.51; ZoDiac .81/.70; XRAI Top-30 PECCAVI .92/.87, with embedding PSNR 29.56 dB and SSIM .93. These are native mean WDPs, not calibrated TPRs.

## Limits and conflicts

Adjunct despite a genuine new benchmark: WDP combines bit accuracy and confidence across methods; maximum search needs image-level null calibration. No matched attack-quality operating points are established. Main embedding quality is not attack fidelity. The title spells PECCVAI and the body PECCAVI. Appendix human MOS was not read or borrowed.

## Consequence for this study

Include new benchmark coverage; record caption-conditioned transfer as outside our fixed empty-prompt study. Native confidence cannot replace the frozen binary endpoint.

The settings and numbers above are direct evidence from the named locators; the consequence is agent inference. Native claims of semantic preservation, distribution preservation or general robustness retain the stated assumptions and were not reproduced. No outcome from our study exists.
