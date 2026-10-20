# MarkNull : Model-Agnostic Watermark Removal in AI-Generated Images via On-Manifold Latent Manipulation

ID: `marknull`. Verification: **V2, method and evaluation read**. Conservative direct floor: **included**.

Authors: Jie Cao; Qi Li; Zelin Zhang; Xiaodong Wu; Lingshuang Liu; Xiangman Li; Jianbing Ni
Version/date: 2608.10166v1 [cs.CR] 10 Aug 2026. Venue: USENIX Security 2026 official publication metadata verified separately; inspected text is arXiv v1.
Primary: [https://arxiv.org/abs/2608.10166v1](https://arxiv.org/abs/2608.10166v1); [inspected full text](https://arxiv.org/html/2608.10166v1). Accessed 2026-10-20.

Cache: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1-marknull.html`. SHA-256: `522723a9664b1226762fda200c4b758a2b16476f6552d27c1e081b124bf1ff32` (617482 bytes).
Inspected: Method cached722-765; setup1236-1280; evaluation2430-2475; AppendixB3836-3892; final full-text/appendix search for resolution, sampler, steps, prompts and implementation settings checked; fields explicitly absent remain unknown.

## Mechanism and attacker access

Proxy-model latent optimization uses orthogonality and perceptual constraints; MarkNull-A amortizes removal. No target decoder gradient is required.

## Models

SD1.5 proxy; SD2.1 watermark generation; SDXL covers for post-hoc marks

## Strength / noise

Latent constraint epsilon1; objective weights1/20/1.5/3

## Sampler / steps / optimizer

Adam50 iterations,lr.05; generation50 diffusion steps; attack inversion schedule not established

## Prompt / guidance

Attack text not specified in inspected setup

## Resolution

512x512

## Image counts and units

100 images/method; nine evaluated methods (eight multibit plus Tree-Ring)

## Metrics

BA; Tree-RingTPR@1%; PSNR,SSIM,LPIPS,FID,BRISQUE; composite CQS

## Conditioned numerical results

MarkNull average multibit BA53.14%; VAE baseline80.17%,UnMarker91.81%; Tree-Ring TPR43% MarkNull and63% amortized on100 images

## Limits and unresolved conflicts

BA near.5 does not by itself establish detector rejection. VINE method categorization in this source needs caution. Composite quality score is not the thesis quality criterion.

## Consequence for this design

Marks tied to a surrogate latent representation may fail transfer; keep independently trained encoder test and explicit native detection metrics.
