# Qwen-VAE2 supporting newer AE research

Rechecked 2026-10-20 UTC for BRIEF §1b. Evidence: **V2 — primary paper method and evaluation inspected**. Floor count: **NO; supporting variant/encoder, native-card evidence or incomplete evaluation lead**.

## Inspected primary method and evaluation

Locators: §2 global shortcut/semantic alignment; §3 training; §6.1.1/6.1.3 reconstruction and SiT evaluations.

Primary paper: [2605.13565v1](https://arxiv.org/html/2605.13565v1). Cached original SHA-256 `5cdd7618ba73f3526154a8e2f16dafa0d46206848eb6a20975f47818fdfaa67b` at `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\qwen-vae2-paper.txt`. “V2” is the inspection tier, not the arXiv revision.

**Method evidence (direct source account):** Global space-to-channel shortcut plus semantic DINO alignment; studies f16/c64 and f16/c128 image AEs. These are not automatically the released Qwen2.1 RGBA z64/f16 checkpoint.

**Quantitative evaluation and conditions (direct source account):** ImageNet256 and FFHQ1024 reconstruction; OmniDoc roughly3K images at256, f16/c128 PSNR30.45/SSIM.9706/NED.9617 versus FLUX1 NED.9546. SiT80-epoch no-CFG comparisons change patch rates. NED convention and OCR quality matter; not our mark detector.

## Lineage, representation and implementation

**Training lineage assessment (agent inference constrained by the cited account):** Paper includes from-scratch f16/c64 ablation. Independence of that experiment is evidence; mapping it to the newer released model remains UNKNOWN.

**Official code and img2img:** qwenimage21/pipeline_qwenimage21.py is conditional generation/editing without strength. No verified released checkpoint mapping to the paper AE configurations.

Diffusers source inspection pin: `e04f0c5f24392fcd34b32d18d0ce03668f9bcd50` unless this card explicitly names `v0.36.0`. This is source inspection, not installation, import, GPU validation or an amendment of the frozen runtime. Source URLs and hashes appear below. Absence of `strength` means the native interface does not expose the frozen partial-noise corruption; image conditioning alone is insufficient.

| Official model/revision URL | Exact revision | Declared model license | Actual access observation |
|---|---|---|---|
| [Qwen/Qwen-Image-2.1](https://huggingface.co/Qwen/Qwen-Image-2.1/tree/d26bb61231c349cf6b7896fa83353113880e1ba3) | d26bb61231c349cf6b7896fa83353113880e1ba3 | other | ungated API snapshot |

Licenses in this table concern the named model package; dependency caveats below remain separate. An ungated metadata snapshot does not prove every dependency is ungated. No model weights were downloaded.

## 1024 memory/time and design consequence

No matched1024 peak/time. Higher latent channel count does not alone determine peak memory; DINO loss is a training component, not necessarily inference residency.

Any parameter-memory figure is a lower bound or explicitly conditional estimate: decimal GB, two bytes per BF16 parameter, inference only, no optimizer. It excludes activations, attention/KV buffers, extra encoders, CFG duplication, allocator workspace and loading peaks. It is not a measured fit or wall-clock prediction.

**Design implication (agent inference):** Potential additional encoder lineage for future work, conditional on exact release provenance; no automatic independent status for Qwen2.1.

**Limits/open assumptions:** Supplement only, not an additional model family in the floor.

No evaluation above measures this thesis’s mark survival, false positives or fixed decision rule. Paper outcomes remain author-reported literature evidence, not development outcomes.

## Inspectable source receipts

| Exact source URL | Local cached text | SHA-256 |
|---|---|---|
| https://huggingface.co/api/models/Qwen/Qwen-Image-2.1?blobs=true | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-Qwen--Qwen-Image-2.1-api.txt | 7e57a4bc1b61eb2974a8fea1d2af2aac1b798bbbf83ae41b096969bf7a16257d |
| https://huggingface.co/Qwen/Qwen-Image-2.1/resolve/d26bb61231c349cf6b7896fa83353113880e1ba3/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-Qwen--Qwen-Image-2.1-README.md.txt | d4aee8d372df2a890b6283e7d1885e3f68b57190c7d3f4b9466a61beffc16016 |
| https://arxiv.org/html/2605.13565v1 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\qwen-vae2-paper.txt | 5cdd7618ba73f3526154a8e2f16dafa0d46206848eb6a20975f47818fdfaa67b |
| https://huggingface.co/api/models/Qwen/Qwen-Image-2.1?blobs=true | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\qwen21-api.txt | 892e9cdc72d06205c9ef7ed6a42e6e0ea2f0ca7dcc826b887e1143f606f0eb38 |
| https://huggingface.co/Qwen/Qwen-Image-2.1/resolve/d26bb61231c349cf6b7896fa83353113880e1ba3/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\Qwen--Qwen-Image-2.1--README.md.txt | d4aee8d372df2a890b6283e7d1885e3f68b57190c7d3f4b9466a61beffc16016 |
| https://huggingface.co/Qwen/Qwen-Image-2.1/resolve/d26bb61231c349cf6b7896fa83353113880e1ba3/vae/config.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\Qwen--Qwen-Image-2.1--vae--config.json.txt | 9785d527b278cb8b210e9f48a8028d92a4190968ce7e24c8fc85d9d1b82f6ba2 |
| https://huggingface.co/Qwen/Qwen-Image-2.1/resolve/d26bb61231c349cf6b7896fa83353113880e1ba3/model_index.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\Qwen--Qwen-Image-2.1--model_index.json.txt | cf1ecd104ea090855d60d8cec0895c1e9d6ee41b2f87e231b678beecd1cf7809 |
| https://github.com/huggingface/diffusers/blob/e04f0c5f24392fcd34b32d18d0ce03668f9bcd50/src/diffusers/pipelines/qwenimage21/pipeline_qwenimage21.py | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\code-qwenimage21--pipeline_qwenimage21.py-html.txt | 341dfdb6a89cecb1bd2fde22d27745a29e083546664ac53d7ba1e04a35d12e72 |
| https://github.com/huggingface/diffusers/blob/e04f0c5f24392fcd34b32d18d0ce03668f9bcd50/src/diffusers/pipelines/qwenimage21/pipeline_qwenimage21.py | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\code-qwenimage21--pipeline_qwenimage21.py-html.decoded.txt | ef0acd8349473ee1af668745f2a7483f83c65bd0efc9c9d6ba4bccdcb5e1dbd3 |
| https://arxiv.org/html/2605.13565v1 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\qwen-vae2-paper.read.txt | d6db0076b75b3b4a06c7aa7df12819247550ac96e29fe329b206ef421309865c |
