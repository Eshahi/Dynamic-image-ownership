# T4-08: Image Watermarks are Removable Using Controllable Regeneration from Clean Noise

- **Primary source:** [2410.05470v2](https://arxiv.org/html/2410.05470v2); authors: Yepeng Liu; Yiren Song; Hai Ci; Yu Zhang; Haofan Wang; Mike Zheng Shou; Yuheng Bu.
- **Inspected:** 2026-10-20; V2, method and evaluation read; no reproduction. New Stage1b T4 card, with method and evaluation inspected.
- **Method locators:** cached `ctrlregen.txt` lines 74-120. **Evaluation locators:** 301-315; Section 4 tables. Lines refer to the saved HTML-to-text extraction, not PDF pages.
- **Document license:** CC BY-NC-SA 4.0, as stated in the inspected arXiv HTML; not a model/code license.
- **Cache:** `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T4-1b/ctrlregen.html`. **HTML SHA-256:** `8167b5480d5f4a71a9ec4b298c9c00e26d6b9c9dab98e0935af42a0e071d14df`. Text hash and byte counts are in `source-manifest.json`.

## Claim and mechanism

CtrlRegen starts from clean Gaussian latent noise and reconstructs using semantic image embeddings and spatial edge conditioning. The generator is still latent diffusion. CtrlRegen+ also uses a noised image latent. Removing the marked VAE latent from the start state is different from removing all image-dependent paths or using pixel diffusion. DINOv2 and Canny-derived conditioning can still convey mark-related information.

The method trains image-conditioning and spatial control around SD1.5. It provides a contrast for P6/P7/P8, not a ready robust SDXL encoder. A common-postprocessor theorem cannot ignore a caption/feature vector that changes between clean and marked inputs: include the entire transcript or condition on a genuinely common fixed value.

## Evaluation actually inspected

Evaluation uses 1000 MIRFLICKR images and 1000 DiffusionDB prompts, several post-hoc/generative watermarks at TPR@1% FPR and PSNR/SSIM/LPIPS. Training descriptions include 10 million LAION/COYO image-text pairs for semantic control and 118,000 COCO images for spatial control. Regeneration and two-pass rinse are distinct comparators. Reported examples include StegaStamp TPR 0.94 under rinse versus 0.01 under CtrlRegen and Tree-Ring 0.12 under CtrlRegen. These are the paper's settings, not F5/SDXL predictions.

## T4 implications and falsification

Content preservation can coexist with carrier loss: preserving semantics does not preserve arbitrary watermark bits. An image-dependent caption could preserve content_match and increase C even if carrier evidence drops. P6 needs separate read/content reporting and an explicit caption source. A caption from the clean original shared across marks is privileged side information; captioning each suspect instead makes conditioning vary by arm.

R1's empty prompt/CFG1 avoids that caption channel. Passing R1 does not establish resilience to trained conditional regeneration. CtrlRegen presence at a fixed FPR is not F5 content-bound verification. Its paper license is CC BY-NC-SA4.0; code/model rights and executability are not inferred.
