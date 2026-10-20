# Removing Watermarks with Partial Regeneration using Semantic Information

ID: `partial`. Verification: **V2, method and evaluation read**. Conservative direct floor: **included**.

Authors: Krti Tallam; John Kevin Cava; Caleb Geniesse; N. Benjamin Erichson; Michael W. Mahoney
Version/date: 2505.08234v1 [cs.CV] 13 May 2025. Venue: arXiv preprint version verified from full-text header; final venue not independently verified in this card.
Primary: [https://arxiv.org/abs/2505.08234v1](https://arxiv.org/abs/2505.08234v1); [inspected full text](https://arxiv.org/html/2505.08234v1). Accessed 2026-10-20.

Cache: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1-partial.html`. SHA-256: `73271e5b8ee97034e7ca77d509526910b5f19338f157bb30734fc06ed0123d5c` (176126 bytes).
Inspected: SemanticRegen method cached484-598,785-814; evaluation/Table3 1035-1114; Section3.3 cached750-785 and Table3 caption1083; final full-text/appendix search for resolution, sampler, steps, prompts and implementation settings checked; fields explicitly absent remain unknown.

## Mechanism and attacker access

Captioning/segmentation isolate semantically important foreground, then regenerate background with object/background/style prompts, preserving the chosen region.

## Models

BLIP2 VQA, LangSAM mask, MiniChat-MA summary; Stable Diffusion-v2 inpainting (exact repository revision not stated)

## Strength / noise

Background-mask regeneration; numeric noise level not established

## Sampler / steps / optimizer

50 inference steps (Section3.3 cached763-764); sampler family not named in inspected section

## Prompt / guidance

Object,background and style prompts from semantic pipeline

## Resolution

Mask assessment256x256; generation resolution not established

## Image counts and units

Table3 caption:1,000 prompts; successful-output or excluded-image count not supplied

## Metrics

Tree-Ring mean p-value; global and maskedPSNR/SSIM

## Conditioned numerical results

Table3 reports globalSSIM.46/PSNR12.83dB versus maskedSSIM.95/PSNR31.71dB; Tree-Ring meanp=.10 over its evaluated collection

## Limits and unresolved conflicts

Mean p-value above threshold is not an attack success rate. Masked quality excludes changed background and cannot replace full-image fidelity; no claim of all-image invisibility.

## Consequence for this design

Treat semantic conservation as weaker than instance conservation; retain full-image quality and fixed regenerate-and-detect definition.
