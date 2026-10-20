# T4-03: An undetectable watermark for generative image models

- **Primary source:** [2410.07369v4](https://arxiv.org/html/2410.07369v4); authors: Sam Gunn; Xuandong Zhao; Dawn Song.
- **Inspected:** 2026-10-20; V2, method and evaluation read; no reproduction. Prior T4 source explicitly rechecked for this mechanism topic; the body records the new assumption/endpoint checks.
- **Method locators:** cached `prc.txt` lines 165-210; 232-267; 627-659; 906-955. **Evaluation locators:** 268-281; 383-407. Lines refer to the saved HTML-to-text extraction, not PDF pages.
- **Document license:** arXiv perpetual non-exclusive, as stated in the inspected arXiv HTML; not a model/code license.
- **Cache:** `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T4-1b/prc.html`. **HTML SHA-256:** `e7f8017500b50dfcebf62d9899346fbfebff5162dab0b62d132b60b6facb776b`. Text hash and byte counts are in `source-manifest.json`.

## Claim and mechanism

PRC watermarking draws signs of initial Gaussian noise from a pseudorandom error-correcting code. Detection recovers generation randomness using diffusion inversion and applies a keyed detector, with a separate message decoder. Algorithms 7/8 distinguish detection from decoding: decoding is slower and less robust. This is generator-integrated watermarking, unlike post-hoc F5.

Theorem 2 fixes an image generated independently of a newly sampled key and bounds detection or non-null decoding probability **over key generation** by F. It is not a guarantee for an image chosen adaptively after seeing the key. Computational undetectability rests on PRC security assumptions; randomized-looking chip patterns do not inherit that result. Public OwnerID is not a PRC secret. The paper mentions a separate extension for unforgeable public attribution, which does not make F5 unforgeable.

## Evaluation actually inspected

The main setup uses SD2.1-base, 512 pixels, 50 DPMSolver generation steps, CFG3 and 50 exact-inversion steps with inverse order zero. It generates 500 images using COCO or Stable Diffusion Prompts, encodes 512 random bits for the standard PRC arm and reports TPR at 1% FPR. Section 4.4 reports up to 2500 bits on images **without removal attacks**; that is not a 2500-bit robust capacity result. Attack figures evaluate quality and presence, while message recovery is assessed separately.

## T4 use and limits

The embedding-attack discussion suggests a robust or private reader-side VAE might mitigate some attacks. It does not supply a trained SDXL attacker-side encoder that removes F5 while preserving compatibility. It cannot close P8's training, utility and calibration requirements.

A pass on F5 C says readable content-bound information survived the tested channel. It does not demonstrate arbitrary random-message recovery, distributional undetectability, copyright authority or forgery resistance. C can pass without exact Q; report both. Zero C0/wrong-owner detections is a finite development check, not the PRC theorem or a population-wide FPR guarantee. Adaptive forgery needs a separate threat model and evidence, outside this study.
