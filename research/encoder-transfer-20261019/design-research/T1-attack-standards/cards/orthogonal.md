# The Orthogonal Vulnerabilities of Generative AI Watermarks: A Comparative Empirical Benchmark of Spatial and Latent Provenance

ID: `orthogonal`. Verification: **V2, method and evaluation read**. Conservative direct floor: **excluded; supplemental or critical coverage**.

Authors: Jesse Yu; Nicholas Wei
Version/date: 2603.10323v1; 11 Mar 2026. Venue: Verified arXiv preprint version; final venue not verified.
Primary: [https://arxiv.org/abs/2603.10323v1](https://arxiv.org/abs/2603.10323v1); [inspected full text](https://arxiv.org/pdf/2603.10323v1). Accessed 2026-10-20.

Cache: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1b-orthogonal.pdf`. SHA-256: `3d352ecd2863889032f2960d9fbc574b8eb414f2e81c165fe03982ff8ae3ca79` (607989 bytes).
Inspected: PDF Sections3-4 pp3-6; Table1; full PDF resolution search.

## Mechanism and attacker access

Empirical spatial/latent benchmark; regeneration/inpainting/crop/brightness; AER combines provenance and CLIP thresholds.

## Models

SD1.5; RivaGAN; Tree-Ring; OpenCLIP ViT-B-32

## Strength / noise

Img2img.01-.95 over30 intensity intervals; inpaint5-60% area; crop5-90%; brightness1-3

## Sampler / steps / optimizer

DDIM15; inpainting15

## Prompt / guidance

DiffusionDB2M-first-1k generation prompts; attack prompt policy not specified

## Resolution

Not reported in inspected experimental design or full-PDF resolution search

## Image counts and units

4,000 images:2,000 Tree-Ring and2,000 RivaGAN; exact per-intensity denominator not supplied

## Metrics

AER requires provenance<.20 and CLIP>75; provenance is byte accuracy vs transformed MSE

## Conditioned numerical results

Img2img AER67.47% RivaGAN/17.73% Tree-Ring; crop22.67%/43.20%, aggregate across intensity conditions.

## Limits and unresolved conflicts

No common calibrated FPR; unlike provenance scales, unclear aggregation denominator and stronger interpretation than measurements warrant.

## Consequence for this design

Include as benchmark coverage but not evidence of calibrated removal superiority.
