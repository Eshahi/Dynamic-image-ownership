# T4-12: On the Information-Theoretic Limits of Latent-Space Watermarking Through Pretrained Generators

- **Primary source:** [2609.24377v1](https://arxiv.org/html/2609.24377v1); authors: Jinwan Jeon; Minju Lee; Sung Hoon Lim.
- **Inspected:** 2026-10-20; V2, method and evaluation read; no reproduction. New Stage1b T4 card, with method and evaluation inspected.
- **Method locators:** cached `limits.txt` lines 100-178; 360-494. **Evaluation locators:** 346-359; 495-503. Lines refer to the saved HTML-to-text extraction, not PDF pages.
- **Document license:** arXiv perpetual non-exclusive, as stated in the inspected arXiv HTML; not a model/code license.
- **Cache:** `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T4-1b/limits.html`. **HTML SHA-256:** `a23c0159176067314dd65b9d3d1a17bf292fdd76519054585899b22ca125ad8d`. Text hash and byte counts are in `source-manifest.json`.

## Formal result and assumptions

This theory paper treats a fixed pretrained renderer as a latent-to-released-sample channel. Bounds assume a secret key, independent messages, context and exact messagewise conditional distribution preservation after averaging over keys. General bounds are not universally tight. Gaussian cases expose direction-dependent renderer information and key allocation: an isotropic latent prior does not imply equal information capacity along every direction.

The repeated-regeneration calculation is for a canonical scalar Gaussian channel. Original latent contribution attenuates as beta(D)^L; capacity is nonincreasing in round count for that family. The authors explicitly exclude a minimax claim over arbitrary multiround attacks. Per-pass distortion differs from end-to-end distortion. Two DDIM strength 0.1 passes therefore are not theoretically equivalent to strength 0.2, and measured per-image C need not be monotone.

## Evaluation actually inspected

This is a theory source with numerical evaluation, not an empirical image benchmark. Figure 3 compares isotropic/anisotropic Gaussian mode profiles at matched aggregate SNR. Figure 4 numerically plots canonical capacity versus round count using specified scalar variances and key rate. Method, formal assumptions/statements, numerical setup and interpretation were read. No SDXL/F5 detection rate is reported by this card.

## T4 use, falsifiability and limits

The direction-dependent renderer insight complements the Jacobian derivation: a large writer-encoder change can be invisible to the final reader if regeneration suppresses its direction. The repeated-channel calculation motivates lower carrier retention under R1-rinse, with X2 checking extra resampling costs. Equal/higher rinse C at comparable utility weakens simple attenuation as an explanation here; it does not falsify a Gaussian theorem whose assumptions were not established.

F5 is a post-hoc, content-bound, publicly parameterized perturbation. Random-looking chips do not satisfy this paper's exact preservation/secret-key assumptions. No capacity, payload optimum, public-key security or finite-sample detection bound is claimed for F5. The source distinguishes latent dimension, recoverable message information and observed presence; it gives no numerical capacity for this planned experiment.
