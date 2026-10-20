# Hide&Seek: Remove Image Watermarks with Negligible Cost via Pixel-wise Reconstruction

ID: `hideseek`. Verification: **V2, method and evaluation read**. Conservative direct floor: **excluded; supplemental or critical coverage**.

Authors: Huajie Chen; Tianqing Zhu; Hailin Yang; Yuchen Zhong; Yang Zhang; Hui Sun; Heng Xu; Zuobin Ying; Lihua Yin; Wanlei Zhou
Version/date: 2603.01067v1; 01 Mar 2026. Venue: arXivpreprint; source conference/DOI fields are unresolved template placeholders.
Primary: [https://arxiv.org/abs/2603.01067v1](https://arxiv.org/abs/2603.01067v1); [inspected full text](https://arxiv.org/html/2603.01067v1). Accessed 2026-10-20.

Cache: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1b-hideseek.html`. SHA-256: `fc71e2c81cc9c43cc9701e27c66eb9f71b733790bbc624a9135814fbd7db5342` (351096 bytes).
Inspected: Sections3-4;Section6/Table2-4;AppendixA;web130-156,175-353,386-450,535-540.

## Mechanism and attacker access

Detector-free masking followed by MAE or vulnerability-ranked pixelwise fractal reconstruction; clean auxiliary training.

## Models

HSN MAE-ViT;HS+UNet mask andFractal GenerativeModel

## Strength / noise

HSN mask.60/.65/.70/.75/.80;HS+mask probabilitythreshold.5

## Sampler / steps / optimizer

HS+one steppermaskedpixel;training optimizer/schedule not specified in AppendixA

## Prompt / guidance

N/A

## Resolution

Method-specific;StegaStamp400x400;other exactresolutions not stated in AppendixA

## Image counts and units

100randomimages perdefense;datasetsLAION/CelebA/FFHQ/COCO/CelebA-HQ;timing100images repeated10times

## Metrics

DR,BA,TR inverse-distance;PSNR,SSIM,LPIPS

## Conditioned numerical results

Section6.2 HS+HiDDeN DR0,StableSignature.03;allreportedPSNR>30/SSIM>.85. StegaStampTable4 originalorder BA.63/DR.52,31.49/.89/.14.

## Limits and unresolved conflicts

Equation4.7 vsAlgorithm2 mask-area loss sign/form conflict; placeholder venue/DOI not publication evidence; DR not uniformly FPR calibrated.

## Consequence for this design

Include mask reconstruction threat; not a cost estimate forourserver or reason to addtraining.
