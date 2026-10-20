# Removing the Watermark Is Not Enough: Forensic Stealth in Generative-AI Watermark Removal

ID: `forensicstealth`. Verification: **V2, method and evaluation read**. Conservative direct floor: **excluded; supplemental or critical coverage**.

Authors: Yevin Nikhel Goonatilake; Giuseppe Ateniese
Version/date: 2605.09203v2 [cs.CR] 28 Aug 2026. Venue: arXiv preprint version verified from full-text header; final venue not independently verified in this card.
Primary: [https://arxiv.org/abs/2605.09203v2](https://arxiv.org/abs/2605.09203v2); [inspected full text](https://arxiv.org/html/2605.09203v2). Accessed 2026-10-20.

Cache: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1b-forensicstealth.html`. SHA-256: `4b5e15a753222b55c0b58fa3b415b561b1213cfcec1ee072853f839a913a15a0` (457493 bytes).
Inspected: Method cached379-448; evaluation529-550; AppendixA1752-1809.

## Mechanism and attacker access

Attack-specific forensic classifiers and pooled probes evaluate whether watermark removal leaves recognizable traces; evaluates existing removers, not a new query-free regeneration setting.

## Models

Six attack-specific forensic detectors; NFPA,Boundary,WiTS among datasets

## Strength / noise

Per-remover noise/strength not established in inspected summary

## Sampler / steps / optimizer

Per-remover sampler/steps not established

## Prompt / guidance

Per-remover prompt policy unspecified

## Resolution

512x512

## Image counts and units

157,984source pool;197,984 after tamper expansion;NFPA69,992,Boundary22,993,WiTS32,136;pairedLPIPS100/attack;three-way5x150 cohorts

## Metrics

AUROC;TPR at validation-target1%FPR; balanced accuracy;LPIPS

## Conditioned numerical results

PooledAUROC.9976 andTPR97.62% at validation-target1%FPR; held-out20,577 probe examples BA.971 versus ImageNet.600 baseline

## Limits and unresolved conflicts

These are external dataset test partitions, not accessed project held-out pixels. Attack dataset separability is not generic removal/ownership recovery. Excluded from strict direct-removal floor.

## Consequence for this design

Keep forensic distinguishability separate from original-owner detection claims.
