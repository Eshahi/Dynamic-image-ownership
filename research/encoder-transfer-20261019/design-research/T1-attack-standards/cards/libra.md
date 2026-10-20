# LiBRA: Detection-Aware Image Watermark Removal via Bidirectional Latent Optimization

ID: `libra`. Verification: **V2, method and evaluation read**. Conservative direct floor: **included**.

Authors: Saibo Ye; Huajie Chen; Xin Guo; Le Yang; Chi Liu; Xiangyu Hu; Jingjing Guo; Tianqing Zhu
Version/date: 2610.03166v1 [cs.CR] 02 Oct 2026. Venue: arXiv preprint version verified from full-text header; final venue not independently verified in this card.
Primary: [https://arxiv.org/abs/2610.03166v1](https://arxiv.org/abs/2610.03166v1); [inspected full text](https://arxiv.org/html/2610.03166v1). Accessed 2026-10-20.

Cache: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1b-libra.html`. SHA-256: `34d311de58b23fd2d3daa485e87148620cc8598c059f6498780e295078d02ed1` (533879 bytes).
Inspected: Method cached174-208; evaluation309-359; Table4 360-405.

## Mechanism and attacker access

White-box bidirectional latent optimization targets chance-level bit agreement rather than simple inversion, addressing two-sided detection.

## Models

SD2.1-base VAE; target decoder/key gradients

## Strength / noise

TargetBA.45; latent clamp[-6,6]; high/low mask ratios.3/.5

## Sampler / steps / optimizer

Adam50 iterations,lr.01; diffusion samplerN/A

## Prompt / guidance

N/A

## Resolution

StableSignature512;Yu128;HiDDeN/MBRS256

## Image counts and units

5,000 images/system x4 systems =20k system-images per evaluation configuration

## Metrics

BA; one/two-sided detection(alpha.01); PSNR,SSIM,LPIPS

## Conditioned numerical results

Table4 StableSignature inversionbaselineBA.018 but two-sidedDR1.0; LiBRABA.458,DR.03,PSNR38.0dB,SSIM.970,LPIPS.046;5,000/system

## Limits and unresolved conflicts

White-box key access differs from core. Reporting very low BA as removal can invert rather than erase a mark; two-sided calibration depends on the actual detector.

## Consequence for this design

Report native presence separately from exact payload/owner matches; no threshold changes after outcomes.
