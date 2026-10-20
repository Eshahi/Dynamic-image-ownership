# Diffusion Models for Adversarial Purification

ID: `diffpure`. Verification: **V2, method and evaluation read**. Conservative direct floor: **excluded; supplemental or critical coverage**.

Authors: Weili Nie; Brandon Guo; Yujia Huang; Chaowei Xiao; Arash Vahdat; Anima Anandkumar
Version/date: 2205.07460v1 [cs.LG] 16 May 2022. Venue: arXiv preprint version verified from full-text header; final venue not independently verified in this card.
Primary: [https://arxiv.org/abs/2205.07460v1](https://arxiv.org/abs/2205.07460v1); [inspected full text](https://arxiv.org/html/2205.07460v1). Accessed 2026-10-20.

Cache: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1-diffpure.html`. SHA-256: `17ab7e23ca7f120a85150c9f929b50882cc324f4d2fa753da05741bec0ba75b7` (590120 bytes).
Inspected: Section3 cached508-560; Section5.1 setup759-800; Table3; AppendixB2778-2794.

## Mechanism and attacker access

Forward diffusion and reverse SDE purification remove adversarial classifier perturbations; this original paper does not evaluate watermarks.

## Models

CIFARScoreSDE; ImageNet unconditional GuidedDiffusion256; CelebA DDPM

## Strength / noise

Typicalt*.1/.15; Linf8/255 adversarial attack,EOT20

## Sampler / steps / optimizer

Euler-Maruyama dt.001,about100/150reverseupdates

## Prompt / guidance

Unconditional

## Resolution

ImageNet256x256; nativeCIFAR/CelebA settings

## Image counts and units

Typically512 adversarial test examples; clean accuracy uses full test set

## Metrics

Classifier clean/robust accuracy; watermarkTPR N/A

## Conditioned numerical results

Table3 ImageNetResNet50 cleanaccuracy67.79 plus/minus.43%,robust40.93 plus/minus1.96%; no watermark baseline result in this source

## Limits and unresolved conflicts

Foundation only; must not count as direct watermark benchmark or attribute later watermark attack claims to it.

## Consequence for this design

Pixel-space purification is a distinct untested threat; no core addition.
