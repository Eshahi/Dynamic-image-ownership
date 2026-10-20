# DRIFT: Removing Diffusion Watermarks by Deflecting the Generative Trajectory

ID: `drift`. Verification: **V2, method and evaluation read**. Conservative direct floor: **included**.

Authors: Rui Bao; Zheng Gao; Xiaoyu Li; Xiaoyan Feng; Yang Song; Jiaojiao Jiang
Version/date: 2609.08213v1 [cs.CR] 08 Sep 2026. Venue: arXiv preprint version verified from full-text header; final venue not independently verified in this card.
Primary: [https://arxiv.org/abs/2609.08213v1](https://arxiv.org/abs/2609.08213v1); [inspected full text](https://arxiv.org/html/2609.08213v1). Accessed 2026-10-20.

Cache: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1-drift.html`. SHA-256: `efcba5e4b246aed6503d397929e5555487bd14f0fdf322f877a5de066df4da97` (565321 bytes).
Inspected: Method cached385-426,620-678; Section4/Table1 984-1149,1153,1329,1399-1403; AppendixE2775,3063; final full-text/appendix search for resolution, sampler, steps, prompts and implementation settings checked; fields explicitly absent remain unknown.

## Mechanism and attacker access

Partial diffusion with stochastic reverse solvers deflects trajectories; fixed query-free attack differs from verifier-dependent adaptive ladder and DPPO refinement.

## Models

Public SD2.1 across9 watermark families

## Strength / noise

Lambda0-.70; fixed.70 versus adaptive settings

## Sampler / steps / optimizer

DDIM,DPM++,Euler versus DDPM ancestral,Euler ancestral,SDE-DPM++; exact update count not established

## Prompt / guidance

Global source-independent conditioning; empty prompt in baseline

## Resolution

512x512 illustrated; universal evaluation resolution not established

## Image counts and units

100 images/family controlled sampler/quality cells;300/family adaptive success comparisons

## Metrics

ASR (detector rejection),PSNR,SSIM,LPIPS,FID,CLIP

## Conditioned numerical results

Table1b fixed.70 ASR100%,PSNR14.31,SSIM.401,LPIPS.528; adaptive99.7%,23.72,.697,.168; full100%,24.01,.713,.154. QualityN100/family; do not apply300 denominator to every metric

## Limits and unresolved conflicts

Adaptive success uses verifier access; aggressive fixed setting destroys more content. These are external author results, not a predicted F5 outcome.

## Consequence for this design

Freeze sampler and access policy; report quality of failures as well as survivors; no adaptive attack selection.
