# T4-04: Robust Watermarks Meet Backdoored Models: Evading Diffusion Semantic Watermarks via Stealthy Backdoor

- **Primary source:** [2608.00543v1](https://arxiv.org/html/2608.00543v1); authors: Jinyuan Liu; Tianshuo Cong; Pei Li; Tianrui Wang; Xinlei He; Anyu Wang; Xiaoyun Wang.
- **Inspected:** 2026-10-20; V2, method and evaluation read; no reproduction. Prior T4 source explicitly rechecked for this mechanism topic; the body records the new assumption/endpoint checks.
- **Method locators:** cached `ghostvae.txt` lines 230-274; 321-346. **Evaluation locators:** 391-483. Lines refer to the saved HTML-to-text extraction, not PDF pages.
- **Document license:** CC BY 4.0, as stated in the inspected arXiv HTML; not a model/code license.
- **Cache:** `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T4-1b/ghostvae.html`. **HTML SHA-256:** `7d35917e8ee69c665473d8e9c68e0bb5fbdbedc5a4ec2cc6971a08cb51e95a8a`. Text hash and byte counts are in `source-manifest.json`.

## Claim and mechanism

GhostVAE trains a backdoored verification encoder so that a small trigger drives an otherwise valid image toward watermark-negative latent evidence. Its two stages learn a spectrally structured trigger and modify encoder behavior while preserving ordinary reconstruction. It attacks the model-supply trust boundary: the verifier must load the attacker's encoder. This differs from regenerating an image while the legitimate verifier retains its pinned SD1.5 encoder.

The paper shows why latent evidence depends on actual encoder weights, not merely the name of a generator family. Its lineage table motivates checking training history. Fine-tuned/shared encoders cannot be declared independent because the UNet or checkpoint name changes. It does not establish numerical independence of feature Jacobians across separately trained encoders.

## Evaluation actually inspected

The experimental section tests Tree-Ring, Gaussian Shading and PRCMark on Stable Diffusion/FLUX families, measuring TPR/FPR, triggered evasion and image quality. Images are 512 pixels. Stage 2 fine-tunes for four epochs; the authors report an eight-A800 server and list per-family watermark settings. These are reported backdoor-experiment properties, not local measurements or a P8 cost estimate. No training or model download was performed here.

## T4 interpretation and disconfirmation

Core R1/D1 use official SDXL weights while F5 verification retains its pinned reader. They test an honest attack encoder, not a malicious verifier. Failure after substituting an arbitrary reader would not answer the core question; good transfer would not defend against a malicious reader.

Strong R1/D1 retention would weaken an explanation requiring the original attack encoder but say nothing about backdoor resistance. This source supports a limitation and lineage check, not a new core attack or permission to train models. Its CC BY 4.0 paper license is not a model/code license. No venue acceptance is needed for this card's V2 reading qualification.
