# HiDream-I1 / O1 successor (one conservative family)

Rechecked 2026-10-20 UTC for BRIEF §1b. Evidence: **V2 — primary paper method and evaluation inspected**. Floor count: **YES; one distinct family in the conservative floor**.

## Inspected primary method and evaluation

Locators: MoE/training methods; benchmark tables; official README lines105/109 and VAE config; paired O1 methods/evaluation.

Primary paper: [2505.22705v1](https://arxiv.org/html/2505.22705v1). Cached original SHA-256 `2d2ea0614b4b9a1c5e2a3cd019e99d18a6d32fe197a7c69e3ea8e26d42863ac4` at `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\hidream-paper.txt`. “V2” is the inspection tier, not the arXiv revision.

**Method evidence (direct source account):** I1 uses a 17B sparse-MoE DiT, four text encoders and FLUX1 VAE, C=16/f=8. O1 is native RGB3/f1 unified pixel diffusion; its separate card is conservatively grouped under this one family.

**Quantitative evaluation and conditions (direct source account):** I1 reports GenEval .83, DPG85.89 and HPSv2.1 mean33.82. Paper 50/28/14-step variants differ from the native Fast16 example; preserve revisions. Sample count/resolution are incomplete in the table. O1 GenEval .90 and DPG89.83 support pixel generation potential, not corruption equivalence.

## Lineage, representation and implementation

**Training lineage assessment (agent inference constrained by the cited account):** I1 ancestry against SD1/SDXL is UNKNOWN through FLUX. README names FLUX.1-schnell while config _name_or_path is ../checkpoints/flux-dev: both support FLUX1 family reuse, not byte identity. O1 has no AE, so encoder independence is not applicable. Qwen3-VL denoiser initialization is not AE initialization.

**Official code and img2img:** hidream_image/pipeline_hidream_image.py is I1 T2I only. O1 custom inference.py accepts reference images for editing/subject conditioning, but is not native Diffusers strength-controlled img2img; see its separate card.

Diffusers source inspection pin: `e04f0c5f24392fcd34b32d18d0ce03668f9bcd50` unless this card explicitly names `v0.36.0`. This is source inspection, not installation, import, GPU validation or an amendment of the frozen runtime. Source URLs and hashes appear below. Absence of `strength` means the native interface does not expose the frozen partial-noise corruption; image conditioning alone is insufficient.

| Official model/revision URL | Exact revision | Declared model license | Actual access observation |
|---|---|---|---|
| [HiDream-ai/HiDream-I1-Full](https://huggingface.co/HiDream-ai/HiDream-I1-Full/tree/8ccbbfb270ccdae26d6bb0081df67dc81e4033bf) | 8ccbbfb270ccdae26d6bb0081df67dc81e4033bf | mit | ungated API snapshot |
| [HiDream-ai/HiDream-O1-Image](https://huggingface.co/HiDream-ai/HiDream-O1-Image/tree/0b0901d99f200389e138c61946af1185f5f49a13) | 0b0901d99f200389e138c61946af1185f5f49a13 | mit | ungated API snapshot |

Licenses in this table concern the named model package; dependency caveats below remain separate. An ungated metadata snapshot does not prove every dependency is ungated. No model weights were downloaded.

## 1024 memory/time and design consequence

I1 denoiser alone requires at least34GB BF16 before T5/Llama8B/CLIP/VAE. O1 index reports8,804,887,792 parameters:17.609775584GB BF16 parameter floor, excluding activations/KV. Eight official files total35.219643552GB on disk. Added to20.206GB core gives55.425643552GB before packages/images, below the future authorized80GB cap but not an execution authorization. Target1024 peak/runtime unknown; current O1 interface snaps square requests to2048.

Any parameter-memory figure is a lower bound or explicitly conditional estimate: decimal GB, two bytes per BF16 parameter, inference only, no optimizer. It excludes activations, attention/KV buffers, extra encoders, CFG duplication, allocator workspace and loading peaks. It is not a measured fit or wall-clock prediction.

**Design implication (agent inference):** I1 adds no encoder lineage. O1 leads a high-resolution pixel-method research proposal because methods/evaluations are substantive; PRX remains the more direct native1024 interface candidate. Neither is ready for the frozen strength-controlled experiment.

**Limits/open assumptions:** MIT ungated model packages. I1 external Llama3.1 is gated. O1 optional Gemma prompt refiner is gated; plain inference loads the local bundled model/processor, not a required external text encoder. No runtime validation.

No evaluation above measures this thesis’s mark survival, false positives or fixed decision rule. Paper outcomes remain author-reported literature evidence, not development outcomes.

## Inspectable source receipts

| Exact source URL | Local cached text | SHA-256 |
|---|---|---|
| https://huggingface.co/api/models/HiDream-ai/HiDream-I1-Full?blobs=true | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\hidream-api.txt | d3d790f16d486f398db9f1873d6a1938c0b58008cf36e44b6f325df4ac7a3b56 |
| https://arxiv.org/html/2505.22705v1 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\hidream-paper.txt | 2d2ea0614b4b9a1c5e2a3cd019e99d18a6d32fe197a7c69e3ea8e26d42863ac4 |
| https://huggingface.co/HiDream-ai/HiDream-I1-Full/resolve/8ccbbfb270ccdae26d6bb0081df67dc81e4033bf/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\HiDream-ai--HiDream-I1-Full--README.md.txt | 02e2e1b845f6fa3b61fe0a2e9b8f8d89559877e943e1a74a5c49217958116665 |
| https://huggingface.co/HiDream-ai/HiDream-I1-Full/resolve/8ccbbfb270ccdae26d6bb0081df67dc81e4033bf/vae/config.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\HiDream-ai--HiDream-I1-Full--vae--config.json.txt | ad6f0acb584ceb3d136d1e32b684dec65db24bffe9223df2bac0b45539d4e6b5 |
| https://huggingface.co/HiDream-ai/HiDream-I1-Full/resolve/8ccbbfb270ccdae26d6bb0081df67dc81e4033bf/model_index.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\HiDream-ai--HiDream-I1-Full--model_index.json.txt | 17cc70f9342a20adb25c4a48db64ec0cd5991ca4c92ba71200a294b39ae04748 |
| https://api.github.com/repos/huggingface/diffusers/contents/src/diffusers/pipelines/hidream_image/pipeline_hidream_image.py?ref=e04f0c5f24392fcd34b32d18d0ce03668f9bcd50 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\code-hidream_image--pipeline_hidream_image.py-api.txt | 64d76e225a83d72b97c593db10e9aa4250032d27c498d652bd02a7700b1b403a |
| https://api.github.com/repos/huggingface/diffusers/contents/src/diffusers/pipelines/hidream_image/pipeline_hidream_image.py?ref=e04f0c5f24392fcd34b32d18d0ce03668f9bcd50 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\code-hidream_image--pipeline_hidream_image.py-api.decoded.txt | 42d5d89b89b9b16eeaef4a73351eb2789efae1ac3aa06e470e2dc8a9591418f6 |
| https://huggingface.co/api/models/HiDream-ai/HiDream-O1-Image?blobs=true | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\hidream-o1-api.txt | b3a2437f618392b845e4c8f2739e0f5dbc77f51fa94d1b7ffb9fe80c34c6b68e |
| https://huggingface.co/HiDream-ai/HiDream-O1-Image/resolve/0b0901d99f200389e138c61946af1185f5f49a13/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\hidream-o1-card.txt | 901f12f248a2e43a7ac6092d2a6de9f68f444c83e8ba4a53d55eb3069240e7b7 |
| https://huggingface.co/HiDream-ai/HiDream-O1-Image/resolve/0b0901d99f200389e138c61946af1185f5f49a13/config.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\hidream-o1-config.txt | 5cd452860dc1e9c29dd71cc3cef7f39b338b7a40793f7a260655c2d3568f3661 |
| https://huggingface.co/HiDream-ai/HiDream-O1-Image/resolve/0b0901d99f200389e138c61946af1185f5f49a13/model.safetensors.index.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\hidream-o1-index.txt | 33865f9d84679a850080795107f049c3fac81c78d343322f66a36163b9ab53c9 |
| https://arxiv.org/html/2505.22705v1 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\hidream-paper.read.txt | 5ad2e77e22e3dbd34ca033be3f2974b494a4725f5449f8e9d366a7910cb64bcb |
