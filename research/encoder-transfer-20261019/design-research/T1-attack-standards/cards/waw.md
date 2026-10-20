# Watermarks Attack Watermarks: Re-Watermarking as a Generic Removal Strategy

ID: `waw`. Verification: **V2, method and evaluation read**. Conservative direct floor: **included**.

Authors: Maria Bulychev; Neil G. Marchant; Benjamin I. P. Rubinstein
Version/date: 2605.16796v1 [cs.CR] 16 May 2026. Venue: arXiv preprint version verified from full-text header; final venue not independently verified in this card.
Primary: [https://arxiv.org/abs/2605.16796v1](https://arxiv.org/abs/2605.16796v1); [inspected full text](https://arxiv.org/html/2605.16796v1). Accessed 2026-10-20.

Cache: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1-waw.html`. SHA-256: `724af9ff339bf2afbf1388166bedb0449fa927657f56de1255ca880df92ddb99` (375545 bytes).
Inspected: Method cached442-533,814-836; evaluation/Table4 944-1017; AppendixC2199-2262; final full-text/appendix search for resolution, sampler, steps, prompts and implementation settings checked; fields explicitly absent remain unknown.

## Mechanism and attacker access

Re-watermarking with off-the-shelf encoders can overwrite another watermark. Beige-box knows victim family; black-box classifier predicts family from public training examples.

## Models

Watermark encoders; classifierConvNeXtV2Large; SD1.4 regeneration baseline

## Strength / noise

Regen t40-200; VAEq1-7; rinse2x20/60/100 and4x10-50

## Sampler / steps / optimizer

Baseline exact scheduler/inference count not independently established here

## Prompt / guidance

Original generation prompts for regeneration comparisons

## Resolution

512x512

## Image counts and units

Top500 aesthetic images each COCO/DiffDB; classifier500/class for8 schemes+clean,80/10/10split

## Metrics

BA,TPR and normalized quality degradation(NQD)

## Conditioned numerical results

COCO PixelSeal Table4: cleanBA.999; re-watermark BA.514/TPR.029; Regen100 .524/.08; VAEq2 .554/.312; rinse2x20 .542/.204;4x20 .512/.028; N500

## Limits and unresolved conflicts

Four-pass rinse exceeds the matched NQD threshold in this table. Failure of original payload is not proof of no remaining watermark. Re-watermarking introduces another payload and possible forgery.

## Consequence for this design

Separate presence and original-owner decoding; no re-watermarking execution in current T3 transfer test.
