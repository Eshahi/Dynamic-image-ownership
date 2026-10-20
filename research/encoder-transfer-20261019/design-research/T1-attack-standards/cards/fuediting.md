# Diffusion-Based Image Editing: An Unforeseen Adversary to Robust Invisible Watermarks

ID: `fuediting`. Verification: **V2, method and evaluation read**. Conservative direct floor: **excluded; supplemental or critical coverage**.

Authors: Wenkai Fu; Finn Carter; Yue Wang; Emily Davis; Bo Zhang
Version/date: 2511.05598v1; 05 Nov 2025. Venue: Verified arXiv preprint version; final venue not verified.
Primary: [https://arxiv.org/abs/2511.05598v1](https://arxiv.org/abs/2511.05598v1); [inspected full text](https://arxiv.org/html/2511.05598v1). Accessed 2026-10-20.

Cache: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1b-fuediting.html`. SHA-256: `1f679e146b624435c911c9d812f5e8a4dbf0f9495f8fc9bf49aff5ff4958f3b0` (239153 bytes).
Inspected: Sections3,5,6 Tables1-2;web104-166,179-269.

## Mechanism and attacker access

Latent regeneration with optional white-box decoder guidance eta.1 at each reverse step.

## Models

SD1.5; five posthoc watermark methods

## Strength / noise

About.5 noise timeline

## Sampler / steps / optimizer

50 forward+50 reverse; DDIM inversion/PLMS mentioned without fixing evaluated selector

## Prompt / guidance

Null text

## Resolution

512x512; watermark methods cropped/padded256 as needed

## Image counts and units

500COCO+500ImageNet=1000

## Metrics

Exact-message recovery;PSNR/SSIM/LPIPS

## Conditioned numerical results

VINE12%unguided/0%guided;Stega4%/0%;Trust2%/0%. Trust quality40.5/.992/.010 unguided and39.1/.981/.015 guided.

## Limits and unresolved conflicts

Payload32/64 descriptions conflict with known implementations; quality reference says marked but identity PSNR45.7 finite. No calibrated TPR; unreconciled source claims.

## Consequence for this design

Quarantine quantitative comparisons; no reason to alter F5 thresholds.
