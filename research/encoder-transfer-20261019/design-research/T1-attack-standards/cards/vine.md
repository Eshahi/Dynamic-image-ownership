# Robust Watermarking Using Generative Priors Against Image Editing: From Benchmarking to Advances

ID: `vine`. Verification: **V2, method and evaluation read**. Conservative direct floor: **included**.

Authors: Shilin Lu; Zihan Zhou; Jiayou Lu; Yuanzhi Zhu; Adams Wai-Kin Kong
Version/date: 2410.18775v2 [cs.CV] 15 Mar 2025. Venue: arXiv preprint version verified from full-text header; final venue not independently verified in this card.
Primary: [https://arxiv.org/abs/2410.18775v2](https://arxiv.org/abs/2410.18775v2); [inspected full text](https://arxiv.org/html/2410.18775v2). Accessed 2026-10-20.

Cache: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1-vine.html`. SHA-256: `f6fb25d7b27ec0e95f883674e2e08a41a9075f5929e76287f02330e339e049dd` (362103 bytes).
Inspected: Method Sections 3-4 and cached text lines 375-485; W-Bench settings 493-513; evaluation/Table 1 730-793; official stochastic and deterministic source text; caption cached517, Sections4.2-4.3 cached758-776; released vine/src/vine_turbo.py lines47,77,85,114,138-139 read directly.

## Mechanism and attacker access

W-Bench separates stochastic regeneration, deterministic inversion, global/local editing and video; VINE uses a generative-prior encoder with editing augmentation. Evaluation has no adaptive detector-query attack.

## Models

W-Bench stochastic SD2.1 non-base; deterministic SD2.1-base. Paper describes VINE encoder as SDXL-Turbo; released constructor uses stabilityai/sd-turbo (revision d72f11a93f8de9bc45ef61202b9c8dda2a70cc77). These are not interchangeable lineage claims.

## Strength / noise

VP times 60:20:240; deterministic 15/25/35/45 inversion steps

## Sampler / steps / optimizer

DDIM scheduled50, actual3-12 updates; DPM order2 for deterministic branch

## Prompt / guidance

Empty stochastic captions; CFG7.5; eta0

## Resolution

512x512 residual application

## Image counts and units

Unresolved source conflict: Section4.2 gives 10,000 UltraEdit sources partitioned 1k stochastic,1k deterministic,1k global,5k local,1k video,1k distortion; Section4.3 averages m x 1,000 regeneration outputs. Table1 caption instead states 5,000 images per edit, quality over10,000. Retain both, no reconstructed denominator.

## Metrics

TPR at .1%/1% FPR; BA/AUROC; PSNR,SSIM,LPIPS,FID

## Conditioned numerical results

Table1 VINE-R clean PSNR37.34dB/SSIM.9934/LPIPS.0063; stochastic TPR@.1%FPR99.66%, deterministic99.98%. Severity-averaged; denominator conflict between caption5,000 and Sections4.2-4.3 1,000 remains unresolved.

## Limits and unresolved conflicts

Averages over m x 1k outputs do not create m x 1k independent sources. Original benchmark combines stronger semantic edits with regeneration; no guarantee for F5. Paper/model release discrepancy prevents using paper SDXL-Turbo description as proof of released VINE independent-encoder lineage.

## Consequence for this design

Keep VAE/resize diagnostics and report executed timesteps rather than equating pipeline strength with VP time.
