# Z-Image

Rechecked 2026-10-20 UTC for BRIEF §1b. Evidence: **V2 — primary paper method and evaluation inspected**. Floor count: **YES; one distinct family in the conservative floor**.

## Inspected primary method and evaluation

Locators: S3-DiT and distillation methods; §5.2.1/Table9; official speed claim and VAE metadata.

Primary paper: [2511.22699v1](https://arxiv.org/html/2511.22699v1). Cached original SHA-256 `3f9f86f6f2c25a6d1a66ab78873d7f1ddde3c52661a11f15cf3b617c9481371a` at `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-zimage-paper.txt`. “V2” is the inspection tier, not the arXiv revision.

**Method evidence (direct source account):** 6B single-stream S3-DiT with Qwen3-4B conditioning; frozen FLUX1 VAE, C=16/f=8. Turbo uses 8 NFE.

**Quantitative evaluation and conditions (direct source account):** Table9 reports GenEval .84 for base and .82 for Turbo. Speed depends on NFE and specialized optimization; quality scores do not isolate the encoder. Prompt rewriting and distillation can affect outcomes.

## Lineage, representation and implementation

**Training lineage assessment (agent inference constrained by the cited account):** Against SD1 and SDXL: UNKNOWN through FLUX initialization. The advertised VAE LFS SHA f5b59a26…604d40a3 matches FLUX1 and Chroma; this is encoder reuse, not new training.

**Official code and img2img:** z_image/pipeline_z_image_img2img.py native image+strength, VAEshift/scale/flow. Currentpin; frozen v0.35.1 compatibility not established.

Diffusers source inspection pin: `e04f0c5f24392fcd34b32d18d0ce03668f9bcd50` unless this card explicitly names `v0.36.0`. This is source inspection, not installation, import, GPU validation or an amendment of the frozen runtime. Source URLs and hashes appear below. Absence of `strength` means the native interface does not expose the frozen partial-noise corruption; image conditioning alone is insufficient.

| Official model/revision URL | Exact revision | Declared model license | Actual access observation |
|---|---|---|---|
| [Tongyi-MAI/Z-Image-Turbo](https://huggingface.co/Tongyi-MAI/Z-Image-Turbo/tree/f332072aa78be7aecdf3ee76d5c247082da564a6) | f332072aa78be7aecdf3ee76d5c247082da564a6 | apache-2.0 | ungated API snapshot |

Licenses in this table concern the named model package; dependency caveats below remain separate. An ungated metadata snapshot does not prove every dependency is ungated. No model weights were downloaded.

## 1024 memory/time and design consequence

The 6B denoiser alone requires at least 12 GB BF16 weights, plus about 8 GB for the 4B text encoder and additional VAE/activations. Primary subsecond speed uses H800, FlashAttention3 and compilation. The modelcard 16 GB claim does not prove a fully resident BF16 pipeline. Our 1024 peak and runtime remain unknown.

Any parameter-memory figure is a lower bound or explicitly conditional estimate: decimal GB, two bytes per BF16 parameter, inference only, no optimizer. It excludes activations, attention/KV buffers, extra encoders, CFG duplication, allocator workspace and loading peaks. It is not a measured fit or wall-clock prediction.

**Design implication (agent inference):** An accessible modern FLUX-family contrast, but not a proven freshly initialized AE. Replacing gated FLUX with Z-Image would not establish independent-encoder transfer.

**Limits/open assumptions:** Apache2 and ungated model package. Published object hashes are metadata evidence; no weights or outcomes were generated.

No evaluation above measures this thesis’s mark survival, false positives or fixed decision rule. Paper outcomes remain author-reported literature evidence, not development outcomes.

## Inspectable source receipts

| Exact source URL | Local cached text | SHA-256 |
|---|---|---|
| https://huggingface.co/api/models/Tongyi-MAI/Z-Image-Turbo?blobs=true | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-Tongyi-MAI--Z-Image-Turbo-api.json | 4489484514a5facd650bb2a6b28ead62b1612f5429658a1b005c7901f4424532 |
| https://huggingface.co/Tongyi-MAI/Z-Image-Turbo/resolve/f332072aa78be7aecdf3ee76d5c247082da564a6/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-Tongyi-MAI--Z-Image-Turbo-README.md | 87af5e1d7933dbfe091c4048a20805541130690ee813b8039b7f396b47e64338 |
| https://huggingface.co/Tongyi-MAI/Z-Image-Turbo/resolve/f332072aa78be7aecdf3ee76d5c247082da564a6/vae/config.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-Tongyi-MAI--Z-Image-Turbo-vae--config.json | e80af1e64a71883a9d10c3159d2e493e5934508da57852f6a180ae6ae63b14bd |
| https://huggingface.co/Tongyi-MAI/Z-Image-Turbo/resolve/f332072aa78be7aecdf3ee76d5c247082da564a6/model_index.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-Tongyi-MAI--Z-Image-Turbo-model_index.json | 18a90e1bc117a29a8b7961bb200c86ff0b9704609e87c7171511dc724fcdc9d3 |
| https://arxiv.org/html/2511.22699v1 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-zimage-paper.txt | 3f9f86f6f2c25a6d1a66ab78873d7f1ddde3c52661a11f15cf3b617c9481371a |
| https://huggingface.co/Tongyi-MAI/Z-Image-Turbo/resolve/f332072aa78be7aecdf3ee76d5c247082da564a6/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\Tongyi-MAI--Z-Image-Turbo--README.md.txt | 87af5e1d7933dbfe091c4048a20805541130690ee813b8039b7f396b47e64338 |
| https://huggingface.co/Tongyi-MAI/Z-Image-Turbo/resolve/f332072aa78be7aecdf3ee76d5c247082da564a6/vae/config.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\Tongyi-MAI--Z-Image-Turbo--vae--config.json.txt | e80af1e64a71883a9d10c3159d2e493e5934508da57852f6a180ae6ae63b14bd |
| https://huggingface.co/Tongyi-MAI/Z-Image-Turbo/resolve/f332072aa78be7aecdf3ee76d5c247082da564a6/model_index.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\Tongyi-MAI--Z-Image-Turbo--model_index.json.txt | 18a90e1bc117a29a8b7961bb200c86ff0b9704609e87c7171511dc724fcdc9d3 |
| https://api.github.com/repos/huggingface/diffusers/contents/src/diffusers/pipelines/z_image/pipeline_z_image_img2img.py?ref=e04f0c5f24392fcd34b32d18d0ce03668f9bcd50 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\code-z_image--pipeline_z_image_img2img.py-api.txt | de27ec009173f07051fb88c6642486f91b3740ccfa15f19ee8946c2b646f4ae0 |
| https://api.github.com/repos/huggingface/diffusers/contents/src/diffusers/pipelines/z_image/pipeline_z_image_img2img.py?ref=e04f0c5f24392fcd34b32d18d0ce03668f9bcd50 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\code-z_image--pipeline_z_image_img2img.py-api.decoded.txt | ff2ab85bfdedbe1e84c5e42a21882b6c31cf31dff906f4cc1efa9b2497c20111 |
| https://arxiv.org/html/2511.22699v1 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\T2-zimage-paper.read.txt | 3aa44df46348c07dc1bc54929150ac22d2192fe156b76b794362ebdc99b94759 |
