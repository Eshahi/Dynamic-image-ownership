# Diffusion-Based Image Editing for Breaking Robust Watermarks

ID: `editing`. Verification: **V2, method and evaluation read**. Conservative direct floor: **excluded; supplemental or critical coverage**.

Authors: Yunyi Ni; Finn Carter; Ze Niu; Emily Davis; Bo Zhang
Version/date: 2510.05978v1; 07 Oct 2025. Venue: Verified arXiv preprint version; final venue not verified.
Primary: [https://arxiv.org/abs/2510.05978v1](https://arxiv.org/abs/2510.05978v1); [inspected full text](https://arxiv.org/html/2510.05978v1). Accessed 2026-10-20.

Cache: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1-editing.html`. SHA-256: `6241712daa1dee469a12b70d270a296bc9f484fc907fdea72c7ce2fe9dba10a4` (180416 bytes).
Inspected: Sections4,6; web137-172,211-240;Table1.

## Mechanism and attacker access

Unguided latent regeneration and decoder-gradient guidance; latter requires white-box watermark decoder.

## Models

SD1.5; StegaStamp,TrustMark,VINE

## Strength / noise

Approximately.3T or30-40% forward-noise timeline; guidance coefficient not specified

## Sampler / steps / optimizer

DDIM50 steps

## Prompt / guidance

Not specified in evaluation

## Resolution

Not specified in evaluation

## Image counts and units

500COCO+200ImageNet=700; random payload per image

## Metrics

Exact-message recovery called detection;PSNR vsunmarked original;SSIM

## Conditioned numerical results

Table1 VINE18%unguided/0%guided recovery,PSNR29.4/26.0;Stega5%/1%,31.0/28.0.

## Limits and unresolved conflicts

No FPR calibration; payload/model descriptions not independently reconciled; approximate strength; guidance objective sign ambiguity.

## Consequence for this design

Critical coverage only: zero exact payloads does not imply absent native watermark.
