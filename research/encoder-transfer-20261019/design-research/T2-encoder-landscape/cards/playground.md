# Playground v2.5

Rechecked 2026-10-20 UTC for BRIEF §1b. Evidence: **V2 — primary paper method and evaluation inspected**. Floor count: **YES; one distinct family in the conservative floor**.

## Inspected primary method and evaluation

Locators: §2 EDM/noise/resolution buckets; §3/Table1 MJHQ/preference; official VAE config/LFS metadata.

Primary paper: [2402.17245v1](https://arxiv.org/html/2402.17245v1). Cached original SHA-256 `d18793404f00870bc71976147fede04facbf7b0dea79fd29406b2bc445f9a6ad` at `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-playground-paper.txt`. “V2” is the inspection tier, not the arXiv revision.

**Method evidence (direct source account):** SDXL-like U-Net with EDM and balanced resolution buckets; C4/f8 SDXL VAE.

**Quantitative evaluation and conditions (direct source account):** MJHQ30K1024 FID4.48 versusSDXL+refiner9.55; private1K-prompt aesthetic preference4.8×ratio. Settings mix model/sampler/training differences, not AE isolation.

## Lineage, representation and implementation

**Training lineage assessment (agent inference constrained by the cited account):** vs SD1: inherits SDXL ancestry. vs SDXL: SAME. Advertised fp16VAE LFS SHA matches officialSDXL (bcb60880…c6161e68); metadata identity without downloading weights.

**Official code and img2img:** stable_diffusion_xl/pipeline_stable_diffusion_xl_img2img.py supports architecture; EDM scheduler/config compatibility remains a condition, not tested runtime.

Diffusers source inspection pin: `e04f0c5f24392fcd34b32d18d0ce03668f9bcd50` unless this card explicitly names `v0.36.0`. This is source inspection, not installation, import, GPU validation or an amendment of the frozen runtime. Source URLs and hashes appear below. Absence of `strength` means the native interface does not expose the frozen partial-noise corruption; image conditioning alone is insufficient.

| Official model/revision URL | Exact revision | Declared model license | Actual access observation |
|---|---|---|---|
| [playgroundai/playground-v2.5-1024px-aesthetic](https://huggingface.co/playgroundai/playground-v2.5-1024px-aesthetic/tree/1e032f13f2fe6db2dc49947dbdbd196e753de573) | 1e032f13f2fe6db2dc49947dbdbd196e753de573 | other | ungated API snapshot |

Licenses in this table concern the named model package; dependency caveats below remain separate. An ungated metadata snapshot does not prove every dependency is ungated. No model weights were downloaded.

## 1024 memory/time and design consequence

≈2.6B denoiser≥5.2GB BF16 plustext/VAE/activations. No matched primary1024 peak/time. Similar parameter count does not justify copying latency across schedulers.

Any parameter-memory figure is a lower bound or explicitly conditional estimate: decimal GB, two bytes per BF16 parameter, inference only, no optimizer. It excludes activations, attention/KV buffers, extra encoders, CFG duplication, allocator workspace and loading peaks. It is not a measured fit or wall-clock prediction.

**Design implication (agent inference):** Exclude from encoder-diversity expansion; at most a separate denoiser/scheduler control.

**Limits/open assumptions:** Custom Playground Community license, ungated. AdvertisedVAE hash is metadata evidence, not locally verified weights.

No evaluation above measures this thesis’s mark survival, false positives or fixed decision rule. Paper outcomes remain author-reported literature evidence, not development outcomes.

## Inspectable source receipts

| Exact source URL | Local cached text | SHA-256 |
|---|---|---|
| https://huggingface.co/api/models/playgroundai/playground-v2.5-1024px-aesthetic?blobs=true | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-playgroundai--playground-v2.5-1024px-aesthetic-api.json | b191d4ae0ed0234410d7737e97f5dd106551ac2d270357504e7e52322f8669b9 |
| https://huggingface.co/playgroundai/playground-v2.5-1024px-aesthetic/resolve/1e032f13f2fe6db2dc49947dbdbd196e753de573/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-playgroundai--playground-v2.5-1024px-aesthetic-README.md | c6660ae40bb2bd3a3c932072f16de46efff8ac95e22048c5f90f41540a7a85c0 |
| https://huggingface.co/playgroundai/playground-v2.5-1024px-aesthetic/resolve/1e032f13f2fe6db2dc49947dbdbd196e753de573/vae/config.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-playgroundai--playground-v2.5-1024px-aesthetic-vae--config.json | 900dba765a6f61896ed12fa863b951a7053e9d13c8d249aa9ff757721fcf86ee |
| https://huggingface.co/playgroundai/playground-v2.5-1024px-aesthetic/resolve/1e032f13f2fe6db2dc49947dbdbd196e753de573/model_index.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-playgroundai--playground-v2.5-1024px-aesthetic-model_index.json | e69bc6c32f552e1a967c4c4c706f6ce264dc31f3d34e8972a107ee89b585da8a |
| https://arxiv.org/html/2402.17245v1 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-playground-paper.txt | d18793404f00870bc71976147fede04facbf7b0dea79fd29406b2bc445f9a6ad |
| https://huggingface.co/playgroundai/playground-v2.5-1024px-aesthetic/resolve/1e032f13f2fe6db2dc49947dbdbd196e753de573/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\playgroundai--playground-v2.5-1024px-aesthetic--README.md.txt | c6660ae40bb2bd3a3c932072f16de46efff8ac95e22048c5f90f41540a7a85c0 |
| https://huggingface.co/playgroundai/playground-v2.5-1024px-aesthetic/resolve/1e032f13f2fe6db2dc49947dbdbd196e753de573/vae/config.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\playgroundai--playground-v2.5-1024px-aesthetic--vae--config.json.txt | 900dba765a6f61896ed12fa863b951a7053e9d13c8d249aa9ff757721fcf86ee |
| https://huggingface.co/playgroundai/playground-v2.5-1024px-aesthetic/resolve/1e032f13f2fe6db2dc49947dbdbd196e753de573/model_index.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\playgroundai--playground-v2.5-1024px-aesthetic--model_index.json.txt | e69bc6c32f552e1a967c4c4c706f6ce264dc31f3d34e8972a107ee89b585da8a |
| https://api.github.com/repos/huggingface/diffusers/contents/src/diffusers/pipelines/stable_diffusion_xl/pipeline_stable_diffusion_xl_img2img.py?ref=e04f0c5f24392fcd34b32d18d0ce03668f9bcd50 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\code-stable_diffusion_xl--pipeline_stable_diffusion_xl_img2img.py-api.txt | 53c4b787ac15e9f30d060902586236ff34b4abb8268d22e97b25d6cab296a426 |
| https://api.github.com/repos/huggingface/diffusers/contents/src/diffusers/pipelines/stable_diffusion_xl/pipeline_stable_diffusion_xl_img2img.py?ref=e04f0c5f24392fcd34b32d18d0ce03668f9bcd50 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\code-stable_diffusion_xl--pipeline_stable_diffusion_xl_img2img.py-api.decoded.txt | 0833c640ae91f8afdc548b511f4172db60a0f6dc7ee6373596343f2faf239907 |
| https://arxiv.org/html/2402.17245v1 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\T2-playground-paper.read.txt | 7d97fb281ae670c5a6f019b8772cde456dcc32b4ec58c6ef47c2adf5c88e4d84 |
