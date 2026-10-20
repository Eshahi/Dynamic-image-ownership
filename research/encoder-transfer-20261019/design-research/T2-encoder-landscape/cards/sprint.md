# SANA-Sprint supporting distillation evidence

Rechecked 2026-10-20 UTC for BRIEF §1b. Evidence: **V2 — primary paper method and evaluation inspected**. Floor count: **NO; supporting variant/encoder, native-card evidence or incomplete evaluation lead**.

## Inspected primary method and evaluation

Locators: §3 flow-to-TrigFlow/self-consistency/adversarial distillation; §4.1/4.2 benchmarks and latency.

Primary paper: [2503.09641v1](https://arxiv.org/html/2503.09641v1). Cached original SHA-256 `4201d344a00121f4b154bb2717b72ceadbc634d6e81f46e93f610282580877c0` at `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-sprint-paper.txt`. “V2” is the inspection tier, not the arXiv revision.

**Method evidence (direct source account):** Same DC-AE C32/f32; SANA denoiser distilled to1–4 steps. Conversion rescales time, SNR and model output between flow matching and TrigFlow.

**Quantitative evaluation and conditions (direct source account):** MJHQ30K FID/CLIP and GenEval comparisons: headline one-step FID7.59/GenEval.74; four-step table FID6.48/GenEval.76. Faster sampling is not evidence of matched source corruption.

## Lineage, representation and implementation

**Training lineage assessment (agent inference constrained by the cited account):** Same DC-AE encoder as SANA, not an additional independently trained AE. Against SD1/SDXL use the qualified training evidence in dcae.md.

**Official code and img2img:** sana/pipeline_sana_sprint_img2img.py exposes image+strength, default2 steps, TrigFlow-specific time bounds. Small-step integer truncation can empty the core .1/.2/.4 schedule.

Diffusers source inspection pin: `e04f0c5f24392fcd34b32d18d0ce03668f9bcd50` unless this card explicitly names `v0.36.0`. This is source inspection, not installation, import, GPU validation or an amendment of the frozen runtime. Source URLs and hashes appear below. Absence of `strength` means the native interface does not expose the frozen partial-noise corruption; image conditioning alone is insufficient.

| Official model/revision URL | Exact revision | Declared model license | Actual access observation |
|---|---|---|---|
| [Efficient-Large-Model/Sana_Sprint_1.6B_1024px_diffusers](https://huggingface.co/Efficient-Large-Model/Sana_Sprint_1.6B_1024px_diffusers/tree/19683c58b7ea290e55cedd8950ae1d86ada7ef96) | 19683c58b7ea290e55cedd8950ae1d86ada7ef96 | apache-2.0 | ungated API snapshot |

Licenses in this table concern the named model package; dependency caveats below remain separate. An ungated metadata snapshot does not prove every dependency is ungated. No model weights were downloaded.

## 1024 memory/time and design consequence

Headline1024 one-step .1s H100/.31s RTX4090 uses optimized conditions. Another table gives .21s for600M one-step and .32s four-step: different configurations must not be merged. Our img2img time/peak unknown;1.6B denoiser BF16 floor3.2GB plus text/AE.

Any parameter-memory figure is a lower bound or explicitly conditional estimate: decimal GB, two bytes per BF16 parameter, inference only, no optimizer. It excludes activations, attention/KV buffers, extra encoders, CFG duplication, allocator workspace and loading peaks. It is not a measured fit or wall-clock prediction.

**Design implication (agent inference):** Cheap generation candidate after a separate schedule design, or DC-AE-only diagnostic now as a proposal. No silent schedule amendment.

**Limits/open assumptions:** Distilled speed claims do not justify assuming strength labels have the same meaning as DDIM.

No evaluation above measures this thesis’s mark survival, false positives or fixed decision rule. Paper outcomes remain author-reported literature evidence, not development outcomes.

## Inspectable source receipts

| Exact source URL | Local cached text | SHA-256 |
|---|---|---|
| https://arxiv.org/html/2503.09641v1 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-sprint-paper.txt | 4201d344a00121f4b154bb2717b72ceadbc634d6e81f46e93f610282580877c0 |
| https://raw.githubusercontent.com/huggingface/diffusers/v0.36.0/src/diffusers/pipelines/sana/pipeline_sana_sprint_img2img.py | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-sprint-pipeline-v036.txt | 0bb391f36d098ff53a912bcde721855a86397bddfb20789978a585990a0f52bb |
| https://huggingface.co/api/models/Efficient-Large-Model/Sana_Sprint_1.6B_1024px_diffusers?blobs=true | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-Efficient-Large-Model--Sana_Sprint_1.6B_1024px_diffusers-api.txt | 901bcfdbd332e9d683a0088c01d0441cbeef23469c3297a740b1b306c62bdf6e |
| https://huggingface.co/Efficient-Large-Model/Sana_Sprint_1.6B_1024px_diffusers/resolve/19683c58b7ea290e55cedd8950ae1d86ada7ef96/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-Efficient-Large-Model--Sana_Sprint_1.6B_1024px_diffusers-README.md.txt | d4c7975b684d492b80d6103cfb35117e91d8dfab14cff1c2bcc415e391fc28b7 |
| https://huggingface.co/Efficient-Large-Model/Sana_Sprint_1.6B_1024px_diffusers/resolve/19683c58b7ea290e55cedd8950ae1d86ada7ef96/vae/config.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-Efficient-Large-Model--Sana_Sprint_1.6B_1024px_diffusers-vae--config.json.txt | ba6f3d3e44d75d44fdd3760097c069173b5b925e6d14604d5d3582628d09cca6 |
| https://huggingface.co/Efficient-Large-Model/Sana_Sprint_1.6B_1024px_diffusers/resolve/19683c58b7ea290e55cedd8950ae1d86ada7ef96/scheduler/scheduler_config.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-Efficient-Large-Model--Sana_Sprint_1.6B_1024px_diffusers-scheduler--scheduler_config.json.txt | 9a2c56f902710bfde73c81045c7fb99902ab3ead525fa201b58a35817995173b |
| https://huggingface.co/Efficient-Large-Model/Sana_Sprint_1.6B_1024px_diffusers/resolve/19683c58b7ea290e55cedd8950ae1d86ada7ef96/model_index.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-Efficient-Large-Model--Sana_Sprint_1.6B_1024px_diffusers-model_index.json.txt | e3294833370d55fe1d568ab6f9b24df46c4270403d24daffd594eb01927e3fca |
| https://huggingface.co/Efficient-Large-Model/Sana_Sprint_1.6B_1024px_diffusers/resolve/19683c58b7ea290e55cedd8950ae1d86ada7ef96/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\Efficient-Large-Model--Sana_Sprint_1.6B_1024px_diffusers--README.md.txt | d4c7975b684d492b80d6103cfb35117e91d8dfab14cff1c2bcc415e391fc28b7 |
| https://huggingface.co/Efficient-Large-Model/Sana_Sprint_1.6B_1024px_diffusers/resolve/19683c58b7ea290e55cedd8950ae1d86ada7ef96/vae/config.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\Efficient-Large-Model--Sana_Sprint_1.6B_1024px_diffusers--vae--config.json.txt | ba6f3d3e44d75d44fdd3760097c069173b5b925e6d14604d5d3582628d09cca6 |
| https://huggingface.co/Efficient-Large-Model/Sana_Sprint_1.6B_1024px_diffusers/resolve/19683c58b7ea290e55cedd8950ae1d86ada7ef96/model_index.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\Efficient-Large-Model--Sana_Sprint_1.6B_1024px_diffusers--model_index.json.txt | e3294833370d55fe1d568ab6f9b24df46c4270403d24daffd594eb01927e3fca |
| https://github.com/huggingface/diffusers/blob/e04f0c5f24392fcd34b32d18d0ce03668f9bcd50/src/diffusers/pipelines/sana/pipeline_sana_sprint_img2img.py | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\code-sana--pipeline_sana_sprint_img2img.py-html.txt | bae53b5bf394322b83ef26343e5d785229a96952d8a23305db90e1be81ddaa1d |
| https://github.com/huggingface/diffusers/blob/e04f0c5f24392fcd34b32d18d0ce03668f9bcd50/src/diffusers/pipelines/sana/pipeline_sana_sprint_img2img.py | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\code-sana--pipeline_sana_sprint_img2img.py-html.decoded.txt | e25c4fe7a72c9766b047f2774df51fdc970818e5f6f555241ac765f339616a0c |
| https://arxiv.org/html/2503.09641v1 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\T2-sprint-paper.read.txt | 896bb3604fee7cd47d83c1fb76470d18531ea3f95f692661a64b12258183322e |
