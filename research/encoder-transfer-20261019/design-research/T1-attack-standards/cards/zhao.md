# Invisible Image Watermarks Are Provably Removable Using Generative AI

ID: `zhao`. Verification: **V2, method and evaluation read**. Conservative direct floor: **included**.

Authors: Xuandong Zhao; Kexun Zhang; Zihao Su; Saastha Vasan; Ilya Grishchenko; Christopher Kruegel; Giovanni Vigna; Yu-Xiang Wang; Lei Li
Version/date: 2306.01953v3 [cs.CR] 31 Oct 2024. Venue: arXiv preprint version verified from full-text header; final venue not independently verified in this card.
Primary: [https://arxiv.org/abs/2306.01953v3](https://arxiv.org/abs/2306.01953v3); [inspected full text](https://arxiv.org/html/2306.01953v3). Accessed 2026-10-20.

Cache: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1-zhao.html`. SHA-256: `41861c3d032d039a001feb23c58c8a322b0e38c27ad70b382acfc84d96423582` (352470 bytes).
Inspected: Method/theory cached494-646; Section5/Table1/Figures4,7 cached790-986; final full-text/appendix search for resolution, sampler, steps, prompts and implementation settings checked; fields explicitly absent remain unknown.

## Mechanism and attacker access

Bounded invisible perturbations can be suppressed by adding sufficient noise and reconstructing with a generative model. Theory is conditional on feature perturbation and reconstruction assumptions.

## Models

SD2.1-base; Bmshj2018 and Cheng2020 compression

## Strength / noise

t10/30/50/100/150/200; sigma.10/.17/.23/.34/.46/.57; compression quality1-6

## Sampler / steps / optimizer

PNDM; exact inference-step grid not specified in inspected evaluation/full-text settings search

## Prompt / guidance

Not reported in inspected evaluation

## Resolution

Not specified in inspected evaluation/full-text settings search

## Image counts and units

500 COCO +500 SD-prompt generated images per evaluated watermark

## Metrics

TPR@1%FPR; PSNR,SSIM,FID

## Conditioned numerical results

Table1 clean COCO StegaStamp TPR1.000,PSNR28.50dB,SSIM.911 (500 images); generated pool28.28dB/.900; attack curves not digitized

## Limits and unresolved conflicts

The greater-than99% removal statement is condition-specific, not universal. Payload-length notation is inconsistent for SSL; do not transplant its threshold. Clean-quality differences materially affect comparisons.

## Consequence for this design

Preserve fixed decoder thresholds and quality reports; independent encoders test transfer, not this theorem universally.
