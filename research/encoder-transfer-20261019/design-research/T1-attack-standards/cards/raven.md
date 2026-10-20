# RAVEN : Erasing Invisible Watermarks via Novel View Synthesis

ID: `raven`. Verification: **V2, method and evaluation read**. Conservative direct floor: **included**.

Authors: Fahad Shamshad; Nils Lukas; Karthik Nandakumar
Version/date: 2601.08832v1 [cs.CV] 13 Jan 2026. Venue: arXiv preprint version verified from full-text header; final venue not independently verified in this card.
Primary: [https://arxiv.org/abs/2601.08832v1](https://arxiv.org/abs/2601.08832v1); [inspected full text](https://arxiv.org/html/2601.08832v1). Accessed 2026-10-20.

Cache: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1-raven.html`. SHA-256: `a0bdfdff7e0c81be8ad4d1aa01d1cd29feac57fa34bbc81ebba5ce0cf14635d6` (441566 bytes).
Inspected: Method cached481-505; evaluation/Table2 setup1291-1312 and1429-1474; Appendix DiffusionDB text cached2229 claims1001 prompts, compared with main detectionN1000.

## Mechanism and attacker access

Novel-view synthesis shifts latent content diagonally with cross-frame attention, followed by color matching; inversion and reconstruction use an image-to-image diffusion refiner.

## Models

Stable Diffusion Refiner (exact checkpoint unspecified); SD2.1 generation

## Strength / noise

Attack strength.15; latent translations plus/minus24-32 pixels

## Sampler / steps / optimizer

DDIM inversion50; generationDDIM50; reconstruction exactstep count not separately established

## Prompt / guidance

Empty attack prompt,CFG2.5; generationCFG7.5

## Resolution

512x512 generation

## Image counts and units

1,000 paired images per detection evaluation; available prompt pools5kCOCO,1001DiffDB,8192SDP are not all evaluated N; AppendixTable6 prose separately says1001 DiffusionDB prompts; retain this denominator difference.

## Metrics

TPR at native thresholds; FID,CLIP; paper Table2

## Conditioned numerical results

COCO meanTPR.026 vs UnMarker.078 across benchmark methods; RAVEN FID40.18COCO/49.47SDP/47.11DiffDB; CLIP.328/.364/.350 under stated1k-pair evaluation

## Limits and unresolved conflicts

Method count differs between abstract/setup/table; do not claim a precise universal count. Geometric correspondence and semantic fidelity change the attacked object. Final CVPR version not compared.

## Consequence for this design

Do not add novel-view synthesis to a narrowly fixed same-source regeneration grid; record as untested stronger transformation.
