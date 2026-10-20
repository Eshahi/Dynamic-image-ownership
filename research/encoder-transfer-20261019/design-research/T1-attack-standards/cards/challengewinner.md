# First-Place Solution to NeurIPS 2024 Invisible Watermark Removal Challenge

ID: `challengewinner`. Verification: **V2, method and evaluation read**. Conservative direct floor: **included**.

Authors: Fahad Shamshad; Tameem Bakr; Yahia Shaaban; Noor Hussein; Karthik Nandakumar; Nils Lukas
Version/date: 2508.21072v1 [cs.CV] 28 Aug 2025. Venue: arXiv preprint version verified from full-text header; final venue not independently verified in this card.
Primary: [https://arxiv.org/abs/2508.21072v1](https://arxiv.org/abs/2508.21072v1); [inspected full text](https://arxiv.org/html/2508.21072v1). Accessed 2026-10-20.

Cache: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1-challengewinner.html`. SHA-256: `62c448a0a6c79e6097ff01305bc0238c52cdf53e1ef2eaa0f1e13ea404d32d51` (260338 bytes).
Inspected: Method cached409-455,878-942,1000-1029; evaluation297-375,1215-1231.

## Mechanism and attacker access

Winning competition uses VAE fine-tuning against known StegaStamp and artifact-cluster-specific regeneration for black-box tracks; leaderboard feedback supports iterative adaptation.

## Models

SD2.1 paired training covers; SDXL refiner preferred for regeneration

## Strength / noise

Strength.04/.16 plus7-pixel shift for square artifacts

## Sampler / steps / optimizer

500 refiner steps,CFG1; VAE training uses1,000 generated pairs

## Prompt / guidance

ChatGPT-generated image captions

## Resolution

Resolution varies by challenge track; exact common resolution not established

## Image counts and units

300 competition images per track;1,000 paired SD2.1 images for VAE fine-tuning

## Metrics

Challenge detection/quality/combined scores, not raw accuracy

## Conditioned numerical results

Leaderboard: black-box detection score.043,quality.136,total.143; beige-box.037/.153/.157 on300-image tracks; these are competition scores and cannot be interpreted as rates without scoring formula

## Limits and unresolved conflicts

Five leaderboard queries/day and manual clustering are stronger access than fixed query-free evaluation. Percentile notation is ambiguous in text; do not import nominal FPR.

## Consequence for this design

Version and disclose attack adaptation; do not introduce caption optimization or learned removal into fixed core.
