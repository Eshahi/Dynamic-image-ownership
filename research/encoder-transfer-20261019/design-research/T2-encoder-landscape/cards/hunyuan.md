# Hunyuan-DiT

Rechecked 2026-10-20 UTC for BRIEF §1b. Evidence: **V2 — primary paper method and evaluation inspected**. Floor count: **YES; one distinct family in the conservative floor**.

## Inspected primary method and evaluation

Locators: §2.1 VAE/text/DiT; §4 evaluation/ablations; official cards/config.

Primary paper: [2405.08748v1](https://arxiv.org/html/2405.08748v1). Cached original SHA-256 `69373dd3134bbf703b6acca804648b24cdb7d156296eb5ab7392f14b29f1607a` at `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-hunyuan-paper.txt`. “V2” is the inspection tier, not the arXiv revision.

**Method evidence (direct source account):** ≈1.5B transformer with bilingualCLIP/T5; C4/f8 VAE explicitly fromSDXL.

**Quantitative evaluation and conditions (direct source account):** §4 >3,000 prompts,>50 professional raters,four dimensions,30–50 prompts/subcategory. Smaller.7B ablations COCO30K256. Do not assign those conditions to1024 full-model reconstruction/survival.

## Lineage, representation and implementation

**Training lineage assessment (agent inference constrained by the cited account):** vs SD1: inheritsSDXL ancestry. vs SDXL: SAME. Hunyuan text callsSDXL fine-tunedSD1.5, conflicting with creatorSDXL§2.4; prefer original from-scratch account and preserve conflict.

**Official code and img2img:** hunyuandit/pipeline_hunyuandit.py T2I-only, no source image/strength. HunyuanImage3 is separate80B-MoE generation; no inherited VAE-lineage assertion.

Diffusers source inspection pin: `e04f0c5f24392fcd34b32d18d0ce03668f9bcd50` unless this card explicitly names `v0.36.0`. This is source inspection, not installation, import, GPU validation or an amendment of the frozen runtime. Source URLs and hashes appear below. Absence of `strength` means the native interface does not expose the frozen partial-noise corruption; image conditioning alone is insufficient.

| Official model/revision URL | Exact revision | Declared model license | Actual access observation |
|---|---|---|---|
| [Tencent-Hunyuan/HunyuanDiT-v1.2-Diffusers](https://huggingface.co/Tencent-Hunyuan/HunyuanDiT-v1.2-Diffusers/tree/5e96094e0ad19e7f475de8711f03634ca0ccc40c) | 5e96094e0ad19e7f475de8711f03634ca0ccc40c | other | ungated API snapshot |
| [tencent/HunyuanImage-3.0](https://huggingface.co/tencent/HunyuanImage-3.0/tree/36f21fe74b65614451cc50ffd8a35a5f662dac70) | 36f21fe74b65614451cc50ffd8a35a5f662dac70 | other | ungated API snapshot |

Licenses in this table concern the named model package; dependency caveats below remain separate. An ungated metadata snapshot does not prove every dependency is ungated. No model weights were downloaded.

## 1024 memory/time and design consequence

1.5B denoiser≥3GB BF16 plustext/VAE; matched1024 peak/time unknown. HunyuanImage3 advertised weights≈168GB; activeMoE parameters do not equal resident memory.

Any parameter-memory figure is a lower bound or explicitly conditional estimate: decimal GB, two bytes per BF16 parameter, inference only, no optimizer. It excludes activations, attention/KV buffers, extra encoders, CFG duplication, allocator workspace and loading peaks. It is not a measured fit or wall-clock prediction.

**Design implication (agent inference):** DiT adds no encoder diversity. Image3 remains current lead with unresolved AE ancestry and huge resident footprint.

**Limits/open assumptions:** Tencent custom terms, ungated hub; availability is not permissiveness. Native strength wrapper not verified.

No evaluation above measures this thesis’s mark survival, false positives or fixed decision rule. Paper outcomes remain author-reported literature evidence, not development outcomes.

## Inspectable source receipts

| Exact source URL | Local cached text | SHA-256 |
|---|---|---|
| https://huggingface.co/api/models/Tencent-Hunyuan/HunyuanDiT-v1.2-Diffusers?blobs=true | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-Tencent-Hunyuan--HunyuanDiT-v1.2-Diffusers-api.json | 27db7e4bdb8908924e00f790c81246c8b848451e868c828dddff60e63b0970dc |
| https://huggingface.co/Tencent-Hunyuan/HunyuanDiT-v1.2-Diffusers/resolve/5e96094e0ad19e7f475de8711f03634ca0ccc40c/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-Tencent-Hunyuan--HunyuanDiT-v1.2-Diffusers-README.md | ec53e969b5e79e898499d77135032401df181c69d03dbabac2bb32e304966655 |
| https://huggingface.co/Tencent-Hunyuan/HunyuanDiT-v1.2-Diffusers/resolve/5e96094e0ad19e7f475de8711f03634ca0ccc40c/vae/config.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-Tencent-Hunyuan--HunyuanDiT-v1.2-Diffusers-vae--config.json | d59730ff7b5f2f4f5abd2f9572727d60ac1f8d3288e77554b10b998c606f9b12 |
| https://huggingface.co/Tencent-Hunyuan/HunyuanDiT-v1.2-Diffusers/resolve/5e96094e0ad19e7f475de8711f03634ca0ccc40c/model_index.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-Tencent-Hunyuan--HunyuanDiT-v1.2-Diffusers-model_index.json | 2efa723f3c6d0d3417cdaae521007ab606d20c5f8436183eaf37f10169f9e0a5 |
| https://arxiv.org/html/2405.08748v1 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-hunyuan-paper.txt | 69373dd3134bbf703b6acca804648b24cdb7d156296eb5ab7392f14b29f1607a |
| https://huggingface.co/api/models/tencent/HunyuanImage-3.0?blobs=true | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-tencent--HunyuanImage-3.0-api.txt | 87e1c74738f023fe9aaf8f9794d164dedfd506aca2c985eba17e903d194ba844 |
| https://huggingface.co/tencent/HunyuanImage-3.0/resolve/36f21fe74b65614451cc50ffd8a35a5f662dac70/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-tencent--HunyuanImage-3.0-README.md.txt | 28e098542099baac5a958457dad024c63c4c0f66daa7f2cec80c4dd33e7e6b06 |
| https://huggingface.co/Tencent-Hunyuan/HunyuanDiT-v1.2-Diffusers/resolve/5e96094e0ad19e7f475de8711f03634ca0ccc40c/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\Tencent-Hunyuan--HunyuanDiT-v1.2-Diffusers--README.md.txt | ec53e969b5e79e898499d77135032401df181c69d03dbabac2bb32e304966655 |
| https://huggingface.co/Tencent-Hunyuan/HunyuanDiT-v1.2-Diffusers/resolve/5e96094e0ad19e7f475de8711f03634ca0ccc40c/vae/config.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\Tencent-Hunyuan--HunyuanDiT-v1.2-Diffusers--vae--config.json.txt | d59730ff7b5f2f4f5abd2f9572727d60ac1f8d3288e77554b10b998c606f9b12 |
| https://huggingface.co/Tencent-Hunyuan/HunyuanDiT-v1.2-Diffusers/resolve/5e96094e0ad19e7f475de8711f03634ca0ccc40c/model_index.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\Tencent-Hunyuan--HunyuanDiT-v1.2-Diffusers--model_index.json.txt | 2efa723f3c6d0d3417cdaae521007ab606d20c5f8436183eaf37f10169f9e0a5 |
| https://huggingface.co/tencent/HunyuanImage-3.0/resolve/36f21fe74b65614451cc50ffd8a35a5f662dac70/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\tencent--HunyuanImage-3.0--README.md.txt | 28e098542099baac5a958457dad024c63c4c0f66daa7f2cec80c4dd33e7e6b06 |
| https://github.com/huggingface/diffusers/blob/e04f0c5f24392fcd34b32d18d0ce03668f9bcd50/src/diffusers/pipelines/hunyuandit/pipeline_hunyuandit.py | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\code-hunyuandit--pipeline_hunyuandit.py-html.txt | bde2042cb24159e09051642330580d6e922051b901b2b02a5b16481e37e63320 |
| https://github.com/huggingface/diffusers/blob/e04f0c5f24392fcd34b32d18d0ce03668f9bcd50/src/diffusers/pipelines/hunyuandit/pipeline_hunyuandit.py | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\code-hunyuandit--pipeline_hunyuandit.py-html.decoded.txt | 176b6b5f48511c1da12811d4ea8ffe7b364c17564a05d798e141673df4a7a1f6 |
| https://arxiv.org/html/2405.08748v1 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\T2-hunyuan-paper.read.txt | 72d66de585ec241e636d484fbf28a47dd971f1b69cdee6f4bc498de6403b71c0 |
