# Qwen-Image / newer Qwen variants

Rechecked 2026-10-20 UTC for BRIEF §1b. Evidence: **V2 — primary paper method and evaluation inspected**. Floor count: **YES; one distinct family in the conservative floor**.

## Inspected primary method and evaluation

Locators: §2.3 image VAE: frozen Wan encoder and decoder-only fine-tuning; Table2 reconstruction; architecture discussion and official configs/native img2img.

Primary paper: [2508.02324v1](https://arxiv.org/html/2508.02324v1). Cached original SHA-256 `7e32948c2c21b304ada3b58aab2cd58079eb35c0885dc747d21d681580710c97` at `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-qwen-paper.txt`. “V2” is the inspection tier, not the arXiv revision.

**Method evidence (direct source account):** 20B MMDiT/Qwen2.5VL, Wan2.1 VAE C16/spatial8/temporal4. Image encoder frozen, decoder fine-tuned. Qwen2.1 instead RGBA4 input/output,z64,spatial16/temporal8; no inheritedWan assumption.

**Quantitative evaluation and conditions (direct source account):** Table2 ImageNet-val256FP32 PSNR33.42/SSIM.9159 versusWan31.29/.887; in-house text-rich25636.63/.9839 versus26.77/.9386. Effective image encoder19M/decoder25M. Decoder improvement does not prove new encoder.

## Lineage, representation and implementation

**Training lineage assessment (agent inference constrained by the cited account):** Original vs SD1/SDXL: qualified distinctWan training lineage, not newly trainedQwen encoder. Qwen2.1 vsboth UNKNOWN. Qwen-VAE2 from-scratch ablations do not establish mapping to released2.1.

**Official code and img2img:** qwenimage/pipeline_qwenimage_img2img.py native image+strength, mean/std normalization/flow truncation. qwenimage21/pipeline_qwenimage21.py image conditioning but no strength; not interchangeable.

Diffusers source inspection pin: `e04f0c5f24392fcd34b32d18d0ce03668f9bcd50` unless this card explicitly names `v0.36.0`. This is source inspection, not installation, import, GPU validation or an amendment of the frozen runtime. Source URLs and hashes appear below. Absence of `strength` means the native interface does not expose the frozen partial-noise corruption; image conditioning alone is insufficient.

| Official model/revision URL | Exact revision | Declared model license | Actual access observation |
|---|---|---|---|
| [Qwen/Qwen-Image](https://huggingface.co/Qwen/Qwen-Image/tree/75e0b4be04f60ec59a75f475837eced720f823b6) | 75e0b4be04f60ec59a75f475837eced720f823b6 | apache-2.0 | ungated API snapshot |
| [Qwen/Qwen-Image-2512](https://huggingface.co/Qwen/Qwen-Image-2512/tree/25468b98e3276ca6700de15c6628e51b7de54a26) | 25468b98e3276ca6700de15c6628e51b7de54a26 | apache-2.0 | ungated API snapshot |
| [Qwen/Qwen-Image-2.1](https://huggingface.co/Qwen/Qwen-Image-2.1/tree/d26bb61231c349cf6b7896fa83353113880e1ba3) | d26bb61231c349cf6b7896fa83353113880e1ba3 | other | ungated API snapshot |

Licenses in this table concern the named model package; dependency caveats below remain separate. An ungated metadata snapshot does not prove every dependency is ungated. No model weights were downloaded.

## 1024 memory/time and design consequence

The20B denoiser requires at least40GB BF16 parameters, plus about14GB for the7B text encoder, VAE and activations. A fully resident24GB pipeline is impossible under these assumptions. Offload/quantization changes runtime; no matched primary1024 peak/time found. Wan video8.19GB is not a Qwen1024 image measurement.

Any parameter-memory figure is a lower bound or explicitly conditional estimate: decimal GB, two bytes per BF16 parameter, inference only, no optimizer. It excludes activations, attention/KV buffers, extra encoders, CFG duplication, allocator workspace and loading peaks. It is not a measured fit or wall-clock prediction.

**Design implication (agent inference):** Wan/Qwen AE-only distinct-lineage diagnostic useful; fullregeneration costly. Treat2.1 as unresolved new config.

**Limits/open assumptions:** Qwen-Image/2512 are Apache and ungated. Qwen2.1 uses ungated Qwen Research terms, not Apache. The original paper cannot establish successor initialization.

No evaluation above measures this thesis’s mark survival, false positives or fixed decision rule. Paper outcomes remain author-reported literature evidence, not development outcomes.

## Inspectable source receipts

| Exact source URL | Local cached text | SHA-256 |
|---|---|---|
| https://huggingface.co/api/models/Qwen/Qwen-Image?blobs=true | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-Qwen--Qwen-Image-api.json | d2c677db9546812baab2d09e422768c36053d9e94597867815d05efc1c0a2167 |
| https://huggingface.co/Qwen/Qwen-Image/resolve/75e0b4be04f60ec59a75f475837eced720f823b6/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-Qwen--Qwen-Image-README.md | c70f9851b364e5d6209305d6f07e065086126132ecc24805c652de45d3d92ca8 |
| https://huggingface.co/Qwen/Qwen-Image/resolve/75e0b4be04f60ec59a75f475837eced720f823b6/vae/config.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-Qwen--Qwen-Image-vae--config.json | e4e61b7553f930e9eabf8935f0a77e6d004cc3ee67a601a56ef03cc41ccada68 |
| https://huggingface.co/Qwen/Qwen-Image/resolve/75e0b4be04f60ec59a75f475837eced720f823b6/model_index.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-Qwen--Qwen-Image-model_index.json | 9fb9557c1e5bafb3a582af8407b5a7ad8a8bcbdb20dde4d248bbb4718e1654bd |
| https://arxiv.org/html/2508.02324v1 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-qwen-paper.txt | 7e32948c2c21b304ada3b58aab2cd58079eb35c0885dc747d21d681580710c97 |
| https://huggingface.co/api/models/Qwen/Qwen-Image-2512?blobs=true | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-Qwen--Qwen-Image-2512-api.txt | aaf97aa2a37d7d819db99a81856286b193d29a2ebcccbe9059210c50f6a95a01 |
| https://huggingface.co/Qwen/Qwen-Image-2512/resolve/25468b98e3276ca6700de15c6628e51b7de54a26/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-Qwen--Qwen-Image-2512-README.md.txt | db371596007403d9588e0d78d9798ecafa59bf7772fbdc12952e581b1562920b |
| https://huggingface.co/Qwen/Qwen-Image-2512/resolve/25468b98e3276ca6700de15c6628e51b7de54a26/vae/config.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-Qwen--Qwen-Image-2512-vae--config.json.txt | c448160dba5ce79c965cb075ee02e18d1c42eb6424f787e5869790d577b56a65 |
| https://huggingface.co/Qwen/Qwen-Image-2512/resolve/25468b98e3276ca6700de15c6628e51b7de54a26/scheduler/scheduler_config.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-Qwen--Qwen-Image-2512-scheduler--scheduler_config.json.txt | 7ee767e37bae4af31d4eb935e125bb20a2237eeecafd22af6610093865c6f587 |
| https://huggingface.co/Qwen/Qwen-Image-2512/resolve/25468b98e3276ca6700de15c6628e51b7de54a26/model_index.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-Qwen--Qwen-Image-2512-model_index.json.txt | caf5f49ee3d897fff6a8e8d6353b084c8d1da3e40ba2f32e9bc554eb0ee4b4e9 |
| https://huggingface.co/api/models/Qwen/Qwen-Image-2.1?blobs=true | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-Qwen--Qwen-Image-2.1-api.txt | 7e57a4bc1b61eb2974a8fea1d2af2aac1b798bbbf83ae41b096969bf7a16257d |
| https://huggingface.co/Qwen/Qwen-Image-2.1/resolve/d26bb61231c349cf6b7896fa83353113880e1ba3/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-Qwen--Qwen-Image-2.1-README.md.txt | d4aee8d372df2a890b6283e7d1885e3f68b57190c7d3f4b9466a61beffc16016 |
| https://huggingface.co/api/models/Qwen/Qwen-Image-2.1?blobs=true | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\qwen21-api.txt | 892e9cdc72d06205c9ef7ed6a42e6e0ea2f0ca7dcc826b887e1143f606f0eb38 |
| https://huggingface.co/Qwen/Qwen-Image/resolve/75e0b4be04f60ec59a75f475837eced720f823b6/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\Qwen--Qwen-Image--README.md.txt | c70f9851b364e5d6209305d6f07e065086126132ecc24805c652de45d3d92ca8 |
| https://huggingface.co/Qwen/Qwen-Image/resolve/75e0b4be04f60ec59a75f475837eced720f823b6/vae/config.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\Qwen--Qwen-Image--vae--config.json.txt | e4e61b7553f930e9eabf8935f0a77e6d004cc3ee67a601a56ef03cc41ccada68 |
| https://huggingface.co/Qwen/Qwen-Image/resolve/75e0b4be04f60ec59a75f475837eced720f823b6/model_index.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\Qwen--Qwen-Image--model_index.json.txt | 9fb9557c1e5bafb3a582af8407b5a7ad8a8bcbdb20dde4d248bbb4718e1654bd |
| https://huggingface.co/Qwen/Qwen-Image-2512/resolve/25468b98e3276ca6700de15c6628e51b7de54a26/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\Qwen--Qwen-Image-2512--README.md.txt | db371596007403d9588e0d78d9798ecafa59bf7772fbdc12952e581b1562920b |
| https://huggingface.co/Qwen/Qwen-Image-2512/resolve/25468b98e3276ca6700de15c6628e51b7de54a26/vae/config.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\Qwen--Qwen-Image-2512--vae--config.json.txt | c448160dba5ce79c965cb075ee02e18d1c42eb6424f787e5869790d577b56a65 |
| https://huggingface.co/Qwen/Qwen-Image-2512/resolve/25468b98e3276ca6700de15c6628e51b7de54a26/model_index.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\Qwen--Qwen-Image-2512--model_index.json.txt | caf5f49ee3d897fff6a8e8d6353b084c8d1da3e40ba2f32e9bc554eb0ee4b4e9 |
| https://huggingface.co/Qwen/Qwen-Image-2.1/resolve/d26bb61231c349cf6b7896fa83353113880e1ba3/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\Qwen--Qwen-Image-2.1--README.md.txt | d4aee8d372df2a890b6283e7d1885e3f68b57190c7d3f4b9466a61beffc16016 |
| https://huggingface.co/Qwen/Qwen-Image-2.1/resolve/d26bb61231c349cf6b7896fa83353113880e1ba3/vae/config.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\Qwen--Qwen-Image-2.1--vae--config.json.txt | 9785d527b278cb8b210e9f48a8028d92a4190968ce7e24c8fc85d9d1b82f6ba2 |
| https://huggingface.co/Qwen/Qwen-Image-2.1/resolve/d26bb61231c349cf6b7896fa83353113880e1ba3/model_index.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\Qwen--Qwen-Image-2.1--model_index.json.txt | cf1ecd104ea090855d60d8cec0895c1e9d6ee41b2f87e231b678beecd1cf7809 |
| https://api.github.com/repos/huggingface/diffusers/contents/src/diffusers/pipelines/qwenimage/pipeline_qwenimage_img2img.py?ref=e04f0c5f24392fcd34b32d18d0ce03668f9bcd50 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\code-qwenimage--pipeline_qwenimage_img2img.py-api.txt | b67a9c4a2dc16bd310a06ec722c696040140e0a7652fecbe8911443665f403d0 |
| https://api.github.com/repos/huggingface/diffusers/contents/src/diffusers/pipelines/qwenimage/pipeline_qwenimage_img2img.py?ref=e04f0c5f24392fcd34b32d18d0ce03668f9bcd50 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\code-qwenimage--pipeline_qwenimage_img2img.py-api.decoded.txt | abc01f2e3482898fe4d6bad1b8559478a095c82ea9cdafd165a56c8392e4b14f |
| https://github.com/huggingface/diffusers/blob/e04f0c5f24392fcd34b32d18d0ce03668f9bcd50/src/diffusers/pipelines/qwenimage21/pipeline_qwenimage21.py | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\code-qwenimage21--pipeline_qwenimage21.py-html.txt | 341dfdb6a89cecb1bd2fde22d27745a29e083546664ac53d7ba1e04a35d12e72 |
| https://github.com/huggingface/diffusers/blob/e04f0c5f24392fcd34b32d18d0ce03668f9bcd50/src/diffusers/pipelines/qwenimage21/pipeline_qwenimage21.py | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\code-qwenimage21--pipeline_qwenimage21.py-html.decoded.txt | ef0acd8349473ee1af668745f2a7483f83c65bd0efc9c9d6ba4bccdcb5e1dbd3 |
| https://arxiv.org/html/2508.02324v1 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\T2-qwen-paper.read.txt | c8b7142f6403e4981dbe2e987cfc74320a2769144d4e9c39ccffd713e972f938 |
