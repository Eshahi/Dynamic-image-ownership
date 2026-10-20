# What Breaks Local Watermarks? A Robustness Benchmark for Local Invisible Image Watermarking

ID: `local`. Verification: **V2, method and evaluation read**. Conservative direct floor: **included**.

Authors: Kai Yao; Bence Szilágyi; Sebestyén Kamp; Máté Poór; Máté Szilveszter; Matyas K. Zsoldos; Marc Juarez
Version/date: 2609.16832v1 [cs.CV] 15 Sep 2026. Venue: arXiv preprint version verified from full-text header; final venue not independently verified in this card.
Primary: [https://arxiv.org/abs/2609.16832v1](https://arxiv.org/abs/2609.16832v1); [inspected full text](https://arxiv.org/html/2609.16832v1). Accessed 2026-10-20.

Cache: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1b-local.html`. SHA-256: `58a071e8937f10827491f86c8cde4dd23181b3940891e4cd1e1dfc57f0ea13ba` (336526 bytes).
Inspected: Method cached180-220; evaluation232-280; AppendixA610-623; Table4 858-884; final full-text/appendix search for resolution, sampler, steps, prompts and implementation settings checked; fields explicitly absent remain unknown.

## Mechanism and attacker access

Local-watermark benchmark tests55 transformations with SyncSeal alignment on/off and controlled inpainting, measuring both localization and decoding.

## Models

WAM,MaskWM,PixelSeal,TrustMark,OmniGuard; inpainting checkpoint not established

## Strength / noise

Inpaint rectangle area .05-.15/.35/.50; local watermark masks fixed by dataset policy

## Sampler / steps / optimizer

Single fixed transform seed; inpainting sampler/steps not established

## Prompt / guidance

Inpainting prompt policy not established

## Resolution

512x512

## Image counts and units

800 sources/method:200 each COCO,SA1B,DIV2K,MIR; COCO masks>=2%, other masks4-14%

## Metrics

BA,IoU,F1 and quality, with means across datasets

## Conditioned numerical results

Clean WAM BA.702 plus/minus.033 andIoU.293 versus MaskWM BA.973 plus/minus.018 andIoU.902; deviations are SD of four dataset means, not800 independent errorbars

## Limits and unresolved conflicts

Local adapters and masks differ from whole-image WAM use. Outside-mask restoration changes the quality test; local results cannot condemn global decoding.

## Consequence for this design

Name whole-image versus region-adapted baseline; current whole-image WAM comparator and resize controls remain fixed.
