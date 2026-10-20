# T4-11: Exploring Weaknesses of Generative Image Watermarks against Latent Frequency Masking

- **Primary source:** [2610.02010v1](https://arxiv.org/html/2610.02010v1); authors: Kirill Aistov; Khaled Abud; Irina Serzhenko; Egor Kovalev; Aleksey Yakushev; Aleksandr Akimenkov; Dmitry Obydenkov; Yury Markin; Sergey Lavrushkin; Dmitriy Vatolin; Anastasia Antsiferova.
- **Inspected:** 2026-10-20; V2, method and evaluation read; no reproduction. New Stage1b T4 card, with method and evaluation inspected.
- **Method locators:** cached `lfm.txt` lines 90-242. **Evaluation locators:** 258-287; 327-346; 433-481. Lines refer to the saved HTML-to-text extraction, not PDF pages.
- **Document license:** arXiv perpetual non-exclusive, as stated in the inspected arXiv HTML; not a model/code license.
- **Cache:** `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T4-1b/lfm.html`. **HTML SHA-256:** `0e4c5f212b8bce8fea276fe19611688591f071c5d678a533168c7a8b696c6856`. Text hash and byte counts are in `source-manifest.json`.

## Claim and mechanism

LFM replaces selected Fourier coefficients of a marked image's VAE latent with Gaussian or diffusion-regenerated values and decodes. It assumes a compatible autoencoder and public-verifier access. A separate 100-image calibration set searches 20 mask configurations over channel subsets and radii using TPR@1% FPR. This is not a detector-free fixed-mask theorem. Its distortion bound combines VAE reconstruction error and a decoder-Lipschitz term; it does not prove erasure.

## Evaluation actually inspected

Setup generates 1000 DiffusionDB and 1000 COCO-prompt images with SD2.1 and evaluates Stable Signature, Tree-Ring, RingID, Gaussian Shading, MaXsive and METR. Gaussian Shading resists partial masks more effectively, consistent with distributed evidence. The Tree-Ring ablation gives TPR 1.0 for VAE-only versus 0.001 for full Gaussian LFM, but PSNR 19.4; diffusion replacement gives TPR 0.385 with PSNR 28.7. Those costs prevent treating lowest TPR as a universal useful attack. Speed excludes one-time mask search.

## T4 implications and limits

F5 exposes its DCT band and chip construction. Fourier masking is not identical to removing DCT chips, but localized public spectral evidence is a plausible weakness. Independent-encoder transfer does not address an attack aimed at the public carrier using the original SD1.5 autoencoder. Even a core pass cannot support general regeneration robustness.

A future spectral-replacement study needs calibration/query permissions, quality controls and a budget amendment. It is not inserted into core or numbered as an approved P1-P10 proposal here. The falsifiable lead is reduced F5 readable carrier while scene identity persists; survival, or erasure only at unusable quality, weakens practical exploitability. Mixed success across schemes contradicts a universal spectral-watermark failure claim. FreqMark/BiSLW remain prior mechanisms, not authorized executions. IEEE-style front matter is not used as evidence of venue acceptance.
