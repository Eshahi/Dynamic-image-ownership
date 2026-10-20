# Exploring Weaknesses of Generative Image Watermarks against Latent Frequency Masking

ID: `masking`. Verification: **V2, method and evaluation read**. Conservative direct floor: **included**.

Authors: Kirill Aistov; Khaled Abud; Irina Serzhenko; Egor Kovalev; Aleksey Yakushev; Aleksandr Akimenkov; Dmitry Obydenkov; Yury Markin; Sergey Lavrushkin; Dmitriy Vatolin; Anastasia Antsiferova
Version/date: 2610.02010v1 [cs.CV] 01 Oct 2026. Venue: arXiv preprint version verified from full-text header; final venue not independently verified in this card.
Primary: [https://arxiv.org/abs/2610.02010v1](https://arxiv.org/abs/2610.02010v1); [inspected full text](https://arxiv.org/html/2610.02010v1). Accessed 2026-10-20.

Cache: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1b-masking.html`. SHA-256: `0e4c5f212b8bce8fea276fe19611688591f071c5d678a533168c7a8b696c6856` (239925 bytes).
Inspected: SectionIII cached91-170; SectionIV setup271-313; SectionV/TableI415-481; final full-text/appendix search for resolution, sampler, steps, prompts and implementation settings checked; fields explicitly absent remain unknown.

## Mechanism and attacker access

Latent Frequency Masking replaces selected Fourier coefficients using Gaussian or regenerated latents;20 candidate masks are selected with target-verifier feedback.

## Models

Compatible SD2.1 VAE; FLUX regenerated replacement (exact version unspecified)

## Strength / noise

Radius10/15;4single+6paired channels; beta0,.2,.4,.6,.8; mainGaussian.4/diffusion0

## Sampler / steps / optimizer

20mask candidates; FLUX sampler/steps unspecified

## Prompt / guidance

Original generation prompt unavailable to attacker

## Resolution

Exact evaluation resolution not specified in inspected setup/full-text settings search

## Image counts and units

100 DiffDB calibration disjoint from1,000DiffDB+1,000COCO;6watermarks

## Metrics

TPR@1%; PSNR,SSIM,LPIPS and runtime

## Conditioned numerical results

Diffusion replacement meanTPR.44 on each dataset; DiffDBPSNR28.4/SSIM.897/LPIPS.043; COCO28.9/.908/.045; Tree-Ring VAE-onlyTPR1.0/PSNR33.1

## Limits and unresolved conflicts

Target-compatible encoder and verifier queries violate our independent-query-free threat. Does not establish that latent sampling is truly in-distribution from marginal Gaussianity.

## Consequence for this design

Useful mechanistic counterexample for spectral localization; do not add query-based mask selection or substitute its VAE ancestry.
