# WARP: A Unified Benchmark for Invisible Image Watermarking — Robustness and Protection Against Attacks

ID: `warp`. Verification: **V2, method and evaluation read**. Conservative direct floor: **included**.

Authors: Khaled Abud; Aleksey Yakushev; Aleksandr Akimenkov; Irina Serzhenko; Kirill Aistov; Egor Kovalev; Dmitry Obydenkov; Sergey Lavrushkin; Anastasia Antsiferova; Dmitriy Vatolin; Yury Markin; Kirill Lukianov
Version/date: 2609.40031v1 [cs.CV] 30 Sep 2026. Venue: arXiv header names ACM MM 2026, November 10-14; scheduled venue label is not independent proof of publication.
Primary: [https://arxiv.org/abs/2609.40031v1](https://arxiv.org/abs/2609.40031v1); [inspected full text](https://arxiv.org/html/2609.40031v1). Accessed 2026-10-20.

Cache: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T1b-warp.html`. SHA-256: `0e87fbcc8839ce6bd3e89c649a3f7fbfcf2cc0f3f09f510a339d02f6df2ad1ab` (410398 bytes).
Inspected: Benchmark method cached226-243; evaluation249-266; AppendixB850-854 and C1392-1398; AppendixTable4 cached1491-1645 read; no forensic experiment present.

## Mechanism and attacker access

Unified watermark robustness benchmark spanning distortions, regeneration, purification and dedicated erasure, with watermark detection/decoding and image-quality evaluation. No forensic detector evaluation is established by this paper.

## Models

32 methods(26post-hoc,6generative); FLUX regeneration/rinse and other reconstructors

## Strength / noise

Main34 attacks/40 configurations; AppendixC resolution study39 attacks. Table4 does not state FLUX noise strengths or rinse count; retain scope difference.

## Sampler / steps / optimizer

Appendix Table4 names FLUX regeneration/rinse/VAE but supplies descriptions rather than exact sampler or step counts

## Prompt / guidance

Per-model prompt policy not established in inspected paper

## Resolution

Native resolution with residual scaling; NIPS299x299 versus DIV2K mean2040x1300

## Image counts and units

1kCOCO+1kDiffDB+400each NIPS/KoNIQ/DIV2K;2.8M transformed outputs are not independent images

## Metrics

BER,TPR@.01%FPR,PSNR,SSIM,LPIPS and quality-robustness summaries

## Conditioned numerical results

Across24 post-hoc methods and39 attacks, NIPSmeanTPR.590/BER.208 versusDIV2K.725/.147; regeneration BER.371 versus.306. Denominators400 source images/dataset, reused across configurations

## Limits and unresolved conflicts

Content and resolution vary jointly; no causal resolution claim. Theoretical binomial calibration is not empirical .01% FPR validation. Venue date is prospective relative to retrieval.

## Consequence for this design

Retain paired resizing controls and source-level denominators; do not promote transformation totals to sample size.
