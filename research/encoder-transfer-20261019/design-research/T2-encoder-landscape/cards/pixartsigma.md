# PixArt-α / PixArt-Σ

Rechecked 2026-10-20 UTC for BRIEF §1b. Evidence: **V2 — primary paper method and evaluation inspected**. Floor count: **YES; one distinct family in the conservative floor**.

## Inspected primary method and evaluation

Locators: §3.2 KV compression; §3.3 VAE adaptation; §4.1/4.2 evaluation; paired α methods/evaluation.

Primary paper: [2403.04692v1](https://arxiv.org/html/2403.04692v1). Cached original SHA-256 `fae501058e9f5b60b203577b4aaaacbaac06a8af2004a1e76eecd76ae655d775` at `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-pixartsigma-paper.txt`. “V2” is the inspection tier, not the arXiv revision.

**Method evidence (direct source account):** 0.6B DiT/T5, KL VAE C4/f8. α uses pretrained LDM VAE; Σ explicitly replaces with SDXL VAE and adapts denoiser2K updates. α paper does not establish exactSD1.5 versusSD2 checkpoint.

**Quantitative evaluation and conditions (direct source account):** Σ evaluates30K curated high-quality examples and300-caption human/GPT4V preference subset. α COCO30K FID7.32. α753 A100GPU-days partly converts V100 by2.2×; training estimate, not inference cost.

## Lineage, representation and implementation

**Training lineage assessment (agent inference constrained by the cited account):** α vs SD1: shared pretrainedLDM lineage, not proven new. Σ vs SD1: inherits SDXL distinct ancestry; Σ vs SDXL: SAME. No new encoder diversity.

**Official code and img2img:** pixart_alpha/pipeline_pixart_sigma.py T2I signature; no image/strength. Community adapter is not native support in inspected official class.

Diffusers source inspection pin: `e04f0c5f24392fcd34b32d18d0ce03668f9bcd50` unless this card explicitly names `v0.36.0`. This is source inspection, not installation, import, GPU validation or an amendment of the frozen runtime. Source URLs and hashes appear below. Absence of `strength` means the native interface does not expose the frozen partial-noise corruption; image conditioning alone is insufficient.

| Official model/revision URL | Exact revision | Declared model license | Actual access observation |
|---|---|---|---|
| [PixArt-alpha/PixArt-XL-2-1024-MS](https://huggingface.co/PixArt-alpha/PixArt-XL-2-1024-MS/tree/b89adadeccd9ead2adcb9fa2825d3fabec48d404) | b89adadeccd9ead2adcb9fa2825d3fabec48d404 | openrail++ | ungated API snapshot |
| [PixArt-alpha/PixArt-Sigma-XL-2-1024-MS](https://huggingface.co/PixArt-alpha/PixArt-Sigma-XL-2-1024-MS/tree/e102b3591cc82e97071b8b4cb90d834d0c487207) | e102b3591cc82e97071b8b4cb90d834d0c487207 | openrail++ | ungated API snapshot |

Licenses in this table concern the named model package; dependency caveats below remain separate. An ungated metadata snapshot does not prove every dependency is ungated. No model weights were downloaded.

## 1024 memory/time and design consequence

Denoiser≥1.2GB BF16 plusT5/VAE. No matched1024 batch-one peak/seconds. ≈34% KV compression relative high-resolution speed improvement is not a portable absolute1024 measurement.

Any parameter-memory figure is a lower bound or explicitly conditional estimate: decimal GB, two bytes per BF16 parameter, inference only, no optimizer. It excludes activations, attention/KV buffers, extra encoders, CFG duplication, allocator workspace and loading peaks. It is not a measured fit or wall-clock prediction.

**Design implication (agent inference):** Useful denoiser control holding SDXL encoder fixed, low priority for encoder diversity.

**Limits/open assumptions:** Ungated OpenRAIL++ packages, not Apache/MIT permissiveness. Private evaluation/evaluator differences prevent direct score ranking.

No evaluation above measures this thesis’s mark survival, false positives or fixed decision rule. Paper outcomes remain author-reported literature evidence, not development outcomes.

## Inspectable source receipts

| Exact source URL | Local cached text | SHA-256 |
|---|---|---|
| https://huggingface.co/api/models/PixArt-alpha/PixArt-XL-2-1024-MS?blobs=true | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-PixArt-alpha--PixArt-XL-2-1024-MS-api.json | 8102336364865258e60e768f7539cde4d7545d0a38ba90db26eed5672af78008 |
| https://huggingface.co/PixArt-alpha/PixArt-XL-2-1024-MS/resolve/b89adadeccd9ead2adcb9fa2825d3fabec48d404/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-PixArt-alpha--PixArt-XL-2-1024-MS-README.md | bdd17f61f9a9dbfec90efb0344c092466bff4c251f8e022782ac07f09c4ca04e |
| https://huggingface.co/PixArt-alpha/PixArt-XL-2-1024-MS/resolve/b89adadeccd9ead2adcb9fa2825d3fabec48d404/vae/config.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-PixArt-alpha--PixArt-XL-2-1024-MS-vae--config.json | 9d90ec977f9742aa150fa8c771f74e333e87142bcd927e295c5d43d24fc4661d |
| https://huggingface.co/PixArt-alpha/PixArt-XL-2-1024-MS/resolve/b89adadeccd9ead2adcb9fa2825d3fabec48d404/model_index.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-PixArt-alpha--PixArt-XL-2-1024-MS-model_index.json | e56aa549036ba94ed16747379e8a2c84b77612b298090fbcdfc2ded43d0e20a6 |
| https://huggingface.co/api/models/PixArt-alpha/PixArt-Sigma-XL-2-1024-MS?blobs=true | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-PixArt-alpha--PixArt-Sigma-XL-2-1024-MS-api.json | cddec51b01a6043814ba437402ddc1a11b2f78c27570621bc1ba5517890f6a4f |
| https://huggingface.co/PixArt-alpha/PixArt-Sigma-XL-2-1024-MS/resolve/e102b3591cc82e97071b8b4cb90d834d0c487207/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-PixArt-alpha--PixArt-Sigma-XL-2-1024-MS-README.md | 0f44a27ede142b5ef109c5112c4604c3cb60e869356684cbc1c66f0cb9f98a23 |
| https://huggingface.co/PixArt-alpha/PixArt-Sigma-XL-2-1024-MS/resolve/e102b3591cc82e97071b8b4cb90d834d0c487207/vae/config.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-PixArt-alpha--PixArt-Sigma-XL-2-1024-MS-vae--config.json | f18b16fa4381c90ab44a3d7abd2e90afd05a2c31b8ca69998bc93c6453aeb7b7 |
| https://huggingface.co/PixArt-alpha/PixArt-Sigma-XL-2-1024-MS/resolve/e102b3591cc82e97071b8b4cb90d834d0c487207/model_index.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-PixArt-alpha--PixArt-Sigma-XL-2-1024-MS-model_index.json | 48717b6754c57ffc40baafd747dafaa3ddfbc4b4c6b7932ab7f472c88665cd06 |
| https://arxiv.org/html/2403.04692v1 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-pixartsigma-paper.txt | fae501058e9f5b60b203577b4aaaacbaac06a8af2004a1e76eecd76ae655d775 |
| https://arxiv.org/html/2310.00426v3 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\pixartalpha-paper.txt | 95091dce9425eb889ae81ee14812a08dcb64bb7bcc8ffcc2c0984bd9aeb0734f |
| https://huggingface.co/PixArt-alpha/PixArt-XL-2-1024-MS/resolve/b89adadeccd9ead2adcb9fa2825d3fabec48d404/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\PixArt-alpha--PixArt-XL-2-1024-MS--README.md.txt | bdd17f61f9a9dbfec90efb0344c092466bff4c251f8e022782ac07f09c4ca04e |
| https://huggingface.co/PixArt-alpha/PixArt-XL-2-1024-MS/resolve/b89adadeccd9ead2adcb9fa2825d3fabec48d404/vae/config.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\PixArt-alpha--PixArt-XL-2-1024-MS--vae--config.json.txt | 9d90ec977f9742aa150fa8c771f74e333e87142bcd927e295c5d43d24fc4661d |
| https://huggingface.co/PixArt-alpha/PixArt-XL-2-1024-MS/resolve/b89adadeccd9ead2adcb9fa2825d3fabec48d404/model_index.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\PixArt-alpha--PixArt-XL-2-1024-MS--model_index.json.txt | e56aa549036ba94ed16747379e8a2c84b77612b298090fbcdfc2ded43d0e20a6 |
| https://huggingface.co/PixArt-alpha/PixArt-Sigma-XL-2-1024-MS/resolve/e102b3591cc82e97071b8b4cb90d834d0c487207/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\PixArt-alpha--PixArt-Sigma-XL-2-1024-MS--README.md.txt | 0f44a27ede142b5ef109c5112c4604c3cb60e869356684cbc1c66f0cb9f98a23 |
| https://huggingface.co/PixArt-alpha/PixArt-Sigma-XL-2-1024-MS/resolve/e102b3591cc82e97071b8b4cb90d834d0c487207/vae/config.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\PixArt-alpha--PixArt-Sigma-XL-2-1024-MS--vae--config.json.txt | f18b16fa4381c90ab44a3d7abd2e90afd05a2c31b8ca69998bc93c6453aeb7b7 |
| https://huggingface.co/PixArt-alpha/PixArt-Sigma-XL-2-1024-MS/resolve/e102b3591cc82e97071b8b4cb90d834d0c487207/model_index.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\PixArt-alpha--PixArt-Sigma-XL-2-1024-MS--model_index.json.txt | 48717b6754c57ffc40baafd747dafaa3ddfbc4b4c6b7932ab7f472c88665cd06 |
| https://github.com/huggingface/diffusers/blob/e04f0c5f24392fcd34b32d18d0ce03668f9bcd50/src/diffusers/pipelines/pixart_alpha/pipeline_pixart_sigma.py | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\code-pixart_alpha--pipeline_pixart_sigma.py-html.txt | 56b2740fee1c499faf633f725ca119fc0a431aea3237aef3104d10ca1b9b9536 |
| https://github.com/huggingface/diffusers/blob/e04f0c5f24392fcd34b32d18d0ce03668f9bcd50/src/diffusers/pipelines/pixart_alpha/pipeline_pixart_sigma.py | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\code-pixart_alpha--pipeline_pixart_sigma.py-html.decoded.txt | 4925177d9296871764dd7e53fdccfeab844ad4c5a0a8ea7ed924a79525a3229e |
| https://arxiv.org/html/2310.00426v3 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\pixartalpha-paper.read.txt | 2db77f3b15311e1a296474233da0e33d2c93b4efeb78db6bd7a56ff46ef4cecb |
| https://arxiv.org/html/2403.04692v1 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\T2-pixartsigma-paper.read.txt | 19062934e1dfbe921e2181dc92e4398c04607dc113433949d87b452d1bdfab25 |
