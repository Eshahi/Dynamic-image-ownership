# Vanishing Watermarks: Diffusion-Based Image Editing Undermines Robust Invisible Watermarking

ID: `vanishing`. Verification: **V2, method and evaluation read**. Conservative direct floor: **excluded; supplemental or critical coverage**.

Authors: Fan Guo; Jiyu Kang; Qi Ming; Emily Davis; Finn Carter
Version/date: 2602.20680v1; 24 Feb 2026. Venue: Verified arXiv preprint version; final venue not verified.
Primary: [https://arxiv.org/abs/2602.20680v1](https://arxiv.org/abs/2602.20680v1); [inspected full text](https://arxiv.org/html/2602.20680v1). Accessed 2026-10-20.

Cache: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1b-vanishing.html`. SHA-256: `3e0347b58ba9e1fc81bf927f7d8c9efb73cc880a6ff63de5506556184a813732` (213810 bytes).
Inspected: Sections3-4;Table1;web105-188.

## Mechanism and attacker access

SD regeneration; optional decoder null-message MSE gradient,lambda.5 one late/final step.

## Models

SD1.5; StegaStamp/TrustMark/VINE

## Strength / noise

Approximately30%noise timeline

## Sampler / steps / optimizer

Sampler/inference step count absent from inspected Section4

## Prompt / guidance

Null text; optional caption-edit variant

## Resolution

512x512

## Image counts and units

500 COCO

## Metrics

Mixed Stega bit accuracy vsTrust/VINE ECC exact-message recovery;quality afteralignment

## Conditioned numerical results

Table1 Stega7.4%regen/0%guided;Trust12.8/0;VINE24.5/1.6. Quality31.8dB/.95/.03 vs30.5/.93/.05.

## Limits and unresolved conflicts

Source calls7.4%bitaccuracy chance and0correctbits removal: neither is valid binary-chance reasoning. Mixed endpoints and payload/ECC assumptions unresolved.

## Consequence for this design

Critical coverage; reject its inference of universal absence from these endpoints.
