# Image Watermarks are Removable Using Controllable Regeneration from Clean Noise

ID: `ctrlregen`. Verification: **V2, method and evaluation read**. Conservative direct floor: **included**.

Authors: Yepeng Liu; Yiren Song; Hai Ci; Yu Zhang; Haofan Wang; Mike Zheng Shou; Yuheng Bu
Version/date: 2410.05470v2 [cs.CR] 02 Mar 2025. Venue: arXiv preprint version verified from full-text header; final venue not independently verified in this card.
Primary: [https://arxiv.org/abs/2410.05470v2](https://arxiv.org/abs/2410.05470v2); [inspected full text](https://arxiv.org/html/2410.05470v2). Accessed 2026-10-20.

Cache: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1-ctrlregen.html`. SHA-256: `bcf6954245a45313525b56acbb9eccf31a59cf3671cb8db9f24d0562d9f39dfe` (261501 bytes).
Inspected: Method cached350-529; Section4/Table1 setup760-811 and AppendixA; final full-text/appendix search for resolution, sampler, steps, prompts and implementation settings checked; fields explicitly absent remain unknown.

## Mechanism and attacker access

Clean-noise generation is guided by DINOv2 semantic and Canny spatial controllers; CtrlRegen+ also permits a noised input. Training uses10M semantic and118k spatial examples.

## Models

SD1.5 backbone; DINOv2-giant and Canny ControlNet

## Strength / noise

Weak-mark t20:20:140; strong100,200,300,400,500,1000; baselines Regen70/Rinse2x70; AppendixA SSL20/60/100/140/180/220/260/300/340; RivaGAN/StableSignature20:20:140.

## Sampler / steps / optimizer

Exact inference sampler/update count not specified in inspected main/appendix settings

## Prompt / guidance

Empty text conditioning

## Resolution

Not specified in inspected main/appendix settings

## Image counts and units

1,000 MIRFLICKR photos and1,000 DiffusionDB prompts for generated methods

## Metrics

TPR@1%FPR; BA; PSNR,CLIP-FID,Q-Align,LIQE

## Conditioned numerical results

Table1 StegaStamp TPR: Regen.99,Rinse.94,CtrlRegen.01; respective PSNR22.34,21.31,19.10dB on the stated1k-image evaluation; Tree-Ring CtrlRegenTPR.12

## Limits and unresolved conflicts

Fresh noise with trained semantic/spatial conditioning is not ordinary img2img strength1. Major training/data costs and changed semantics prevent a cheap drop-in standard.

## Consequence for this design

Consider as an untested stronger conditioned threat; no core expansion or training recommended.
