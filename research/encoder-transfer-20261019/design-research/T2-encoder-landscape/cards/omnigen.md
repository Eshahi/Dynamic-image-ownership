# OmniGen v1

Rechecked 2026-10-20 UTC for BRIEF §1b. Evidence: **V2 — primary paper method and evaluation inspected**. Floor count: **YES; one distinct family in the conservative floor**.

## Inspected primary method and evaluation

Locators: §2/3 architecture/training; Table2 and editing evaluation; official docs/inference.md memory/time table.

Primary paper: [2409.11340v2](https://arxiv.org/html/2409.11340v2). Cached original SHA-256 `e4671ad968d012e2abe3fb7245371f14d8879c3f9a74d76625e148f434783c42` at `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\omnigen-paper.txt`. “V2” is the inspection tier, not the arXiv revision.

**Method evidence (direct source account):** 3.8B Phi3-initialized multimodal rectified flow with frozen SDXL VAE, C=4/f=8. Input images are instruction/context tokens, not necessarily source latents initialized with partial noise.

**Quantitative evaluation and conditions (direct source account):** Table2 GenEval overall .70 versus SD3 .68; task tests include EmuEdit and DreamBench. Editing capability does not validate matched-strength regeneration. Resource measurements show an offload latency tradeoff.

## Lineage, representation and implementation

**Training lineage assessment (agent inference constrained by the cited account):** Against SD1: inherits SDXL separately trained ancestry. Against SDXL: SAME frozen encoder.

**Official code and img2img:** omnigen/pipeline_omnigen.py accepts input_images and img_guidance_scale, but no strength. Native editing is not demonstrated SDEdit.

Diffusers source inspection pin: `e04f0c5f24392fcd34b32d18d0ce03668f9bcd50` unless this card explicitly names `v0.36.0`. This is source inspection, not installation, import, GPU validation or an amendment of the frozen runtime. Source URLs and hashes appear below. Absence of `strength` means the native interface does not expose the frozen partial-noise corruption; image conditioning alone is insufficient.

| Official model/revision URL | Exact revision | Declared model license | Actual access observation |
|---|---|---|---|
| [Shitao/OmniGen-v1](https://huggingface.co/Shitao/OmniGen-v1/tree/58e249c7c7634423c0ba41c34a774af79aa87889) | 58e249c7c7634423c0ba41c34a774af79aa87889 | mit | ungated API snapshot |

Licenses in this table concern the named model package; dependency caveats below remain separate. An ungated metadata snapshot does not prove every dependency is ungated. No model weights were downloaded.

## 1024 memory/time and design consequence

Official repo d4752019ae16741dc3801fd4989432aad4c81a4f reports1024: A800 text9GB31s/single image12GB66s/two images13GB80s; RTX3090 text9GB77s/single12GB166s/two13GB203s. KV caching/offload and separate CFG are enabled, model offload false. With model offload,3090 single image5GB469s. Precision/steps are incompletely specified; these are author reports, not our measurements.

Any parameter-memory figure is a lower bound or explicitly conditional estimate: decimal GB, two bytes per BF16 parameter, inference only, no optimizer. It excludes activations, attention/KV buffers, extra encoders, CFG duplication, allocator workspace and loading peaks. It is not a measured fit or wall-clock prediction.

**Design implication (agent inference):** No encoder diversity. It demonstrates why fitting 24 GB and fitting 15 hours are different constraints.

**Limits/open assumptions:** MIT ungated model. Resource table uses official custom code; current Diffusers may differ, so reported seconds cannot be transferred blindly.

No evaluation above measures this thesis’s mark survival, false positives or fixed decision rule. Paper outcomes remain author-reported literature evidence, not development outcomes.

## Inspectable source receipts

| Exact source URL | Local cached text | SHA-256 |
|---|---|---|
| https://huggingface.co/api/models/Shitao/OmniGen-v1?blobs=true | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\omnigen-api.txt | 37a5ec4398091ff5e2c0e2d4f31dd8ecd2ca4a84b9e1e02265b861f0f874d015 |
| https://arxiv.org/html/2409.11340v2 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\omnigen-paper.txt | e4671ad968d012e2abe3fb7245371f14d8879c3f9a74d76625e148f434783c42 |
| https://huggingface.co/Shitao/OmniGen-v1/resolve/58e249c7c7634423c0ba41c34a774af79aa87889/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\Shitao--OmniGen-v1--README.md.txt | 30f0ef613b9fb6b13d5b07352e593db963132191952c082e638aba390f10fada |
| https://huggingface.co/Shitao/OmniGen-v1/resolve/58e249c7c7634423c0ba41c34a774af79aa87889/vae/config.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\Shitao--OmniGen-v1--vae--config.json.txt | 1ab8e39aeac945453e4c4bd1dd4d0953c566cb9eb9291f87cd316e75c61073cf |
| https://api.github.com/repos/huggingface/diffusers/contents/src/diffusers/pipelines/omnigen/pipeline_omnigen.py?ref=e04f0c5f24392fcd34b32d18d0ce03668f9bcd50 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\code-omnigen--pipeline_omnigen.py-api.txt | b93ab853df080058a601e98ba6e18edfe77d0cc066a6d42ddcc67e078889ed13 |
| https://api.github.com/repos/huggingface/diffusers/contents/src/diffusers/pipelines/omnigen/pipeline_omnigen.py?ref=e04f0c5f24392fcd34b32d18d0ce03668f9bcd50 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\code-omnigen--pipeline_omnigen.py-api.decoded.txt | fbdb7e4b4e797bd793f5128e107313acca72ea2d8d593b55961b3cff9683c9d1 |
| https://github.com/VectorSpaceLab/OmniGen/blob/d4752019ae16741dc3801fd4989432aad4c81a4f/docs/inference.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\omnigen-resource-pinned.txt | 2baaadd69824e9f4ae366b67fcc5d465ff56ef6d301d99a925eb4e26a44b198a |
| https://arxiv.org/html/2409.11340v2 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\omnigen-paper.read.txt | 180f3c6db92c4703db6092917fc76eb68856a99394e7684ec91f2b0b5948d3c0 |
| https://github.com/VectorSpaceLab/OmniGen/blob/main/docs/inference.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\omnigen-resource-html.decoded.txt | 907ee901399d2ec29ee4ba91b40b18af49b4ec6d277a60869c0885d5540cdbff |
