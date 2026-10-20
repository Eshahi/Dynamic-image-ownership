# Saliency-Aware Diffusion Reconstruction for Effective Invisible Watermark Removal

ID: `sadre`. Verification: **V2, method and evaluation read**. Conservative direct floor: **excluded; supplemental or critical coverage**.

Authors: Inzamamul Alam; Md Tanvir Islam; Simon S. Woo
Version/date: 2504.12809v1; 17 Apr 2025. Venue: WWW Companion2025; DOI10.1145/3701716.3715519 verified.
Primary: [https://arxiv.org/abs/2504.12809v1](https://arxiv.org/abs/2504.12809v1); [inspected full text](https://arxiv.org/pdf/2504.12809v1). Accessed 2026-10-20.

Cache: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1b-sadre.pdf`. SHA-256: `b2f73e1e2e87023ff260c7905ea590cc98ae33b8ac798b3ece90676b73365ea7` (138478 bytes).
Inspected: PDF method pp2-3; evaluation p4/Table2; arXiv metadata inspected.

## Mechanism and attacker access

Saliency-weighted latent corruption then diffusion reconstruction; adaptive intensity assumes watermark-strength information whose acquisition is unclear.

## Models

Latent diffusion checkpoint not specified in inspected method/setup

## Strength / noise

Laplace/Cauchy .05-.15; Poisson lambda.1

## Sampler / steps / optimizer

50 denoising steps; linear schedule; exact sampler not specified

## Prompt / guidance

Not reported in method/setup

## Resolution

640x480

## Image counts and units

1,000 COCO images

## Metrics

BRA; PSNR; SSIM

## Conditioned numerical results

Table2 StegaStamp BRA.40,PSNR32.15,SSIM.9535; Tree-Ring BRA.47 on stated1000-image benchmark.

## Limits and unresolved conflicts

Tree-Ring zero-bit BRA interpretation and Equation6 reverse direction unresolved; no calibrated FPR.

## Consequence for this design

Do not infer calibrated erasure or adopt saliency/oracle settings.
