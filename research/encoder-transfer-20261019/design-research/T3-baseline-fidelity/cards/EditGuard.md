# EditGuard: inspected method and evaluation

Evidence level **V2**. Inspected 2026-10-20; post-hoc eligibility is established in the method below. This is literature evidence, not a local outcome or execution approval.

## Source identity and inspected sections

Exact title: **EditGuard: Versatile Image Watermarking for Tamper Localization and Copyright Protection**. Version/date: arXiv:2312.08883v1 [cs.CV] 12 Dec 2023. Venue: CVPR 2024, pp. 11964–11974; numerics below refer to inspected arXiv v1, not an assumed identical final PDF.

Authors: Xuanyu Zhang; Runyi Li; Jiwen Yu; Youmin Xu; Weiqi Li; Jian Zhang. Year: 2023. DOI: not established for this inspected version.

Stable ID: `arxiv:2312.08883v1`. Citekey: `T3EditGuard2312`. Canonical URL: https://arxiv.org/abs/2312.08883v1

Primary full text: https://arxiv.org/html/2312.08883v1

Cached text: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T3b/editguard-latest.txt`
SHA-256: `c2bceb9b4b2c093789ca5779038e660462d65c2f1dcbb68a8ce66cc52fe2770e`

Actually inspected: Sections 3.1–3.3, 4.1–4.5, 5.1–5.4; Equation 7; Tables 2–4; Appendix A and network details; official repository README and license metadata.

Full source and official-code cache hashes/URLs are in [deepening-manifest.json](../deepening-manifest.json); earlier release/weight metadata is retained in [manifest.json](../manifest.json). A cached abstract or repository listing alone does not establish V2.

## Mechanism and post-hoc applicability

An invertible image-hiding/revealing network and bit embedding/recovery network jointly insert a localization image and a robust message. Wavelet coupling blocks and degradation-conditioned posterior estimation support image recovery. It marks an existing image without retraining its generator.

## Native operating point and detector side information

Native 512×512 evaluation embeds 64 bits plus an RGB localization watermark, commonly a pure blue image. A separate comparison retrains at 128 pixels and 30 bits. The localization reference must be shared between encoder and decoder; this is additional detector side information. Equation 7 uses maximum channel difference >=.2 for the pixel tamper mask. README clean/degraded pipelines use mask thresholds .2/.4 respectively; neither is an image watermark-presence cutoff. No calibrated bit-presence FPR or ECC is established. Exact release normalization, resize and quantization remain unverified.

## Code, weights, pinned release and licenses

xuanyuzhang21/EditGuard@174778fb371640bb31b32fcb9f7bfd440c88766b. README provides clean.pth and degrade.pth checkpoint links and test/train scripts. The inspected root has no LICENSE and official API license is null, so code/model permission is unverified. Artifact SHA-256 and immutable checkpoint versions are unresolved. README explicitly limits trained copyright robustness to Gaussian noise, JPEG and Poisson noise.

## Published evaluation and regeneration conditions

Original Table 2 uses 1,000 COCO test images with SD inpainting: native 512/64-bit PSNR 37.77, SSIM .949, NIQE 4.257 and bit accuracy 99.95%; the 128/30-bit variant is 36.93/.944/5.567 and 99.89%. These are local edits, not fully specified global regeneration. Appendix AGE-Set-C construction uses over 30,000 512-pixel COCO/CelebA images with several editing tools; it is not a 30,000-image calibrated detection trial. Third-party OmniGuard Table 3 evaluates 1,000 512-pixel UltraEdit images: EditGuard bit-only SD Inpaint* regeneration BA .623 (quality 42.15/.986), dual-watermark BA .617 (37.53/.936). Exact attack model revision, strength, sampler, steps and prompt strings are not supplied; paired dataset prompts are used. No TPR/FPR calibration is established.

## Cost and uncertainty

Original training is 250,000 Adam iterations at batch size 4. No sufficiently conditioned inference timing or peak VRAM was found. A full dual-watermark inference path includes extra invertible/localization modules beyond the bit decoder; training cost is not inference cost.

## Limitation and design implication

A legitimate post-hoc comparator previously missed, but its primary scope is local tamper localization. Side information, weaker global regeneration evidence and unresolved licensing keep it outside the current proposal set.

Disposition: **Literature coverage; excluded**
