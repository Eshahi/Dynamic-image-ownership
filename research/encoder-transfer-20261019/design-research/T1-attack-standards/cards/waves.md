# WAVES: Benchmarking the Robustness of Image Watermarks

ID: `waves`. Verification: **V2, method and evaluation read**. Conservative direct floor: **included**.

Authors: Bang An; Mucong Ding; Tahseen Rabbani; Aakriti Agrawal; Yuancheng Xu; Chenghao Deng; Sicheng Zhu; Abdirisak Mohamed; Yuxin Wen; Tom Goldstein; Furong Huang
Version/date: 2401.08573v3 [cs.CV] 07 Jun 2024. Venue: arXiv preprint version verified from full-text header; final venue not independently verified in this card.
Primary: [https://arxiv.org/abs/2401.08573v3](https://arxiv.org/abs/2401.08573v3); [inspected full text](https://arxiv.org/html/2401.08573v3). Accessed 2026-10-20.

Cache: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1-waves.html`. SHA-256: `238ffa869b2b8424a92aeeef27e39d7b7909b33ed487a3d4e794e7e6f67e7a08` (466453 bytes).
Inspected: Sections 3-4 cached699-929; Table3 1176-1193; AppendixE2546 and F3103-3246; official regen.py.

## Mechanism and attacker access

Benchmark uses single regeneration, VAE reconstruction and two/four-pass rinsing, with optional original-generation prompts as a separate access condition.

## Models

Attack SD1.4 against generated SD2.1 targets; compression VAE

## Strength / noise

Single t40-200; two-pass t20-100/pass; four-pass t10-50/pass; VAE quality1-7

## Sampler / steps / optimizer

Official helper schedules50; scheduler class not fixed in helper; partial noising start

## Prompt / guidance

Paper distinguishes empty vs original prompt; inspected helper appends empty captions

## Resolution

512x512 code path

## Image counts and units

5,000 reference images each COCO,DiffusionDB,DALL-E3; repeated attacks share sources

## Metrics

TPR@.1%FPR; eight quality metrics; normalized Q and aggregate performance P

## Conditioned numerical results

Table3 Regen-Diff aggregate P: Tree-Ring.612, Stable Signature.001, StegaStamp.943 across severity settings; not a single operating point or raw count

## Limits and unresolved conflicts

Q normalization depends on dataset and metric distribution. Helper RNG handling does not establish identical pass noise. Mixed VAE/diffusion rinsing is discussed as further exploration.

## Consequence for this design

Retain frozen .1+.1 rinse; label SDXL adaptation, not WAVES reproduction, and record both pass seeds.
