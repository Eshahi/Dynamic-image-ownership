# SANA / DC-AE / SANA-Sprint

Rechecked 2026-10-20 UTC for BRIEF §1b. Evidence: **V2 — primary paper method and evaluation inspected**. Floor count: **YES; one distinct family in the conservative floor**.

## Inspected primary method and evaluation

Locators: §2 DC-AE/linearDiT/text; §4 benchmark protocol; Table5 latency/quantization; paired DC-AE/Sprint cards.

Primary paper: [2410.10629v1](https://arxiv.org/html/2410.10629v1). Cached original SHA-256 `8ea6edac419bd04be43aff4fc2b41c4815fed271a217fcd2fd808fd71ba11959` at `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-sana-paper.txt`. “V2” is the inspection tier, not the arXiv revision.

**Method evidence (direct source account):** DC-AE continuous nonvariational C32/f32 (1024→32²×32), residual shortcuts and linear-attention DiT, Gemma2-2B. Sprint is distilled, not another family.

**Quantitative evaluation and conditions (direct source account):** GenEval533 prompts as paper states, DPG1,065,MJHQ30K. Table5 quantization CLIP28.5→28.3 and ImageReward1.03→.96 on statedMJHQ/first1K subsets. DC-AE supplies reconstruction evidence; Sprint few-step gains do not validate equal corruption.

## Lineage, representation and implementation

**Training lineage assessment (agent inference constrained by the cited account):** vs SD1/SDXL: documented separate DC-AE training, qualified YES; no SD checkpoint initialization described. Compression geometry alone would not suffice; DC-AE §3 supplies training evidence.

**Official code and img2img:** sana/pipeline_sana.py T2I-only. sana/pipeline_sana_sprint_img2img.py exposes image+strength with TrigFlow time transform/default2steps; v0.36 also has Sprint img2img. floor(N×strength) can give zero steps for .1/.2/.4 at tinyN; core strengths cannot simply be copied.

Diffusers source inspection pin: `e04f0c5f24392fcd34b32d18d0ce03668f9bcd50` unless this card explicitly names `v0.36.0`. This is source inspection, not installation, import, GPU validation or an amendment of the frozen runtime. Source URLs and hashes appear below. Absence of `strength` means the native interface does not expose the frozen partial-noise corruption; image conditioning alone is insufficient.

| Official model/revision URL | Exact revision | Declared model license | Actual access observation |
|---|---|---|---|
| [Efficient-Large-Model/Sana_600M_1024px_diffusers](https://huggingface.co/Efficient-Large-Model/Sana_600M_1024px_diffusers/tree/28f3af7689de15f3883d5863059a2fca0aa9b829) | 28f3af7689de15f3883d5863059a2fca0aa9b829 | apache-2.0 | ungated API snapshot |
| [Efficient-Large-Model/Sana_Sprint_1.6B_1024px_diffusers](https://huggingface.co/Efficient-Large-Model/Sana_Sprint_1.6B_1024px_diffusers/tree/19683c58b7ea290e55cedd8950ae1d86ada7ef96) | 19683c58b7ea290e55cedd8950ae1d86ada7ef96 | apache-2.0 | ungated API snapshot |

Licenses in this table concern the named model package; dependency caveats below remain separate. An ungated metadata snapshot does not prove every dependency is ungated. No model weights were downloaded.

## 1024 memory/time and design consequence

Table5 RTX4090 1024 FP16 .88s versus optimized W8A8 .37s, with quality changes. Official4bit8GB claim uses Nunchaku. These are optimizedT2I, not frozen img2img measurements. 600M denoiser≥1.2GB BF16 plus≈4GB Gemma/AE/activations; target runtime unknown.

Any parameter-memory figure is a lower bound or explicitly conditional estimate: decimal GB, two bytes per BF16 parameter, inference only, no optimizer. It excludes activations, attention/KV buffers, extra encoders, CFG duplication, allocator workspace and loading peaks. It is not a measured fit or wall-clock prediction.

**Design implication (agent inference):** DC-AE provides large compression change and cheap AE-only contrast. FullSprint needs a defensible corruption schedule and cannot silently replaceR1.

**Limits/open assumptions:** Apache ungated packages; upstreamGemma terms/access remain separate. Packaged weights do not erase upstream terms. Optimized headlines do not establish frozen-stack24GB throughput.

No evaluation above measures this thesis’s mark survival, false positives or fixed decision rule. Paper outcomes remain author-reported literature evidence, not development outcomes.

## Inspectable source receipts

| Exact source URL | Local cached text | SHA-256 |
|---|---|---|
| https://huggingface.co/api/models/Efficient-Large-Model/Sana_600M_1024px_diffusers?blobs=true | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-Efficient-Large-Model--Sana_600M_1024px_diffusers-api.json | 2b939300a75454a6353dc0ae6541f639aba9db79a64c0f8d2ea1d2518a460b8e |
| https://huggingface.co/Efficient-Large-Model/Sana_600M_1024px_diffusers/resolve/28f3af7689de15f3883d5863059a2fca0aa9b829/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-Efficient-Large-Model--Sana_600M_1024px_diffusers-README.md | 956e2d4cc2706eae2a1408349325b0a9786aac24dbaae4d0c9f6c3ada25e229c |
| https://huggingface.co/Efficient-Large-Model/Sana_600M_1024px_diffusers/resolve/28f3af7689de15f3883d5863059a2fca0aa9b829/vae/config.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-Efficient-Large-Model--Sana_600M_1024px_diffusers-vae--config.json | 4e5669aa03caa77615b73b21c9347c384cb11124a9590683e32a510df0176eb4 |
| https://huggingface.co/Efficient-Large-Model/Sana_600M_1024px_diffusers/resolve/28f3af7689de15f3883d5863059a2fca0aa9b829/model_index.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-Efficient-Large-Model--Sana_600M_1024px_diffusers-model_index.json | 5692423f50e7908bec51264ad39e5a9b7566970600f6089a0a40759524f5569b |
| https://arxiv.org/html/2410.10629v1 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-sana-paper.txt | 8ea6edac419bd04be43aff4fc2b41c4815fed271a217fcd2fd808fd71ba11959 |
| https://raw.githubusercontent.com/huggingface/diffusers/v0.36.0/src/diffusers/pipelines/sana/pipeline_sana_sprint_img2img.py | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-sprint-pipeline-v036.txt | 0bb391f36d098ff53a912bcde721855a86397bddfb20789978a585990a0f52bb |
| https://huggingface.co/api/models/Efficient-Large-Model/Sana_Sprint_1.6B_1024px_diffusers?blobs=true | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-Efficient-Large-Model--Sana_Sprint_1.6B_1024px_diffusers-api.txt | 901bcfdbd332e9d683a0088c01d0441cbeef23469c3297a740b1b306c62bdf6e |
| https://huggingface.co/Efficient-Large-Model/Sana_Sprint_1.6B_1024px_diffusers/resolve/19683c58b7ea290e55cedd8950ae1d86ada7ef96/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-Efficient-Large-Model--Sana_Sprint_1.6B_1024px_diffusers-README.md.txt | d4c7975b684d492b80d6103cfb35117e91d8dfab14cff1c2bcc415e391fc28b7 |
| https://huggingface.co/Efficient-Large-Model/Sana_Sprint_1.6B_1024px_diffusers/resolve/19683c58b7ea290e55cedd8950ae1d86ada7ef96/vae/config.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-Efficient-Large-Model--Sana_Sprint_1.6B_1024px_diffusers-vae--config.json.txt | ba6f3d3e44d75d44fdd3760097c069173b5b925e6d14604d5d3582628d09cca6 |
| https://huggingface.co/Efficient-Large-Model/Sana_Sprint_1.6B_1024px_diffusers/resolve/19683c58b7ea290e55cedd8950ae1d86ada7ef96/scheduler/scheduler_config.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-Efficient-Large-Model--Sana_Sprint_1.6B_1024px_diffusers-scheduler--scheduler_config.json.txt | 9a2c56f902710bfde73c81045c7fb99902ab3ead525fa201b58a35817995173b |
| https://huggingface.co/Efficient-Large-Model/Sana_Sprint_1.6B_1024px_diffusers/resolve/19683c58b7ea290e55cedd8950ae1d86ada7ef96/model_index.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-Efficient-Large-Model--Sana_Sprint_1.6B_1024px_diffusers-model_index.json.txt | e3294833370d55fe1d568ab6f9b24df46c4270403d24daffd594eb01927e3fca |
| https://huggingface.co/Efficient-Large-Model/Sana_600M_1024px_diffusers/resolve/28f3af7689de15f3883d5863059a2fca0aa9b829/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\Efficient-Large-Model--Sana_600M_1024px_diffusers--README.md.txt | 956e2d4cc2706eae2a1408349325b0a9786aac24dbaae4d0c9f6c3ada25e229c |
| https://huggingface.co/Efficient-Large-Model/Sana_600M_1024px_diffusers/resolve/28f3af7689de15f3883d5863059a2fca0aa9b829/vae/config.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\Efficient-Large-Model--Sana_600M_1024px_diffusers--vae--config.json.txt | 4e5669aa03caa77615b73b21c9347c384cb11124a9590683e32a510df0176eb4 |
| https://huggingface.co/Efficient-Large-Model/Sana_600M_1024px_diffusers/resolve/28f3af7689de15f3883d5863059a2fca0aa9b829/model_index.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\Efficient-Large-Model--Sana_600M_1024px_diffusers--model_index.json.txt | 5692423f50e7908bec51264ad39e5a9b7566970600f6089a0a40759524f5569b |
| https://huggingface.co/Efficient-Large-Model/Sana_Sprint_1.6B_1024px_diffusers/resolve/19683c58b7ea290e55cedd8950ae1d86ada7ef96/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\Efficient-Large-Model--Sana_Sprint_1.6B_1024px_diffusers--README.md.txt | d4c7975b684d492b80d6103cfb35117e91d8dfab14cff1c2bcc415e391fc28b7 |
| https://huggingface.co/Efficient-Large-Model/Sana_Sprint_1.6B_1024px_diffusers/resolve/19683c58b7ea290e55cedd8950ae1d86ada7ef96/vae/config.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\Efficient-Large-Model--Sana_Sprint_1.6B_1024px_diffusers--vae--config.json.txt | ba6f3d3e44d75d44fdd3760097c069173b5b925e6d14604d5d3582628d09cca6 |
| https://huggingface.co/Efficient-Large-Model/Sana_Sprint_1.6B_1024px_diffusers/resolve/19683c58b7ea290e55cedd8950ae1d86ada7ef96/model_index.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\Efficient-Large-Model--Sana_Sprint_1.6B_1024px_diffusers--model_index.json.txt | e3294833370d55fe1d568ab6f9b24df46c4270403d24daffd594eb01927e3fca |
| https://github.com/huggingface/diffusers/blob/e04f0c5f24392fcd34b32d18d0ce03668f9bcd50/src/diffusers/pipelines/sana/pipeline_sana.py | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\code-sana--pipeline_sana.py-html.txt | b399e717e19a3e060a0a1fc58645461b32eb614864582df217e6debf8eb900d5 |
| https://github.com/huggingface/diffusers/blob/e04f0c5f24392fcd34b32d18d0ce03668f9bcd50/src/diffusers/pipelines/sana/pipeline_sana_sprint_img2img.py | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\code-sana--pipeline_sana_sprint_img2img.py-html.txt | bae53b5bf394322b83ef26343e5d785229a96952d8a23305db90e1be81ddaa1d |
| https://github.com/huggingface/diffusers/blob/e04f0c5f24392fcd34b32d18d0ce03668f9bcd50/src/diffusers/pipelines/sana/pipeline_sana.py | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\code-sana--pipeline_sana.py-html.decoded.txt | ac125de8b005cfa7ec56d0e424850a19c1cba5da4386822deade2ba36aeb0ebe |
| https://github.com/huggingface/diffusers/blob/e04f0c5f24392fcd34b32d18d0ce03668f9bcd50/src/diffusers/pipelines/sana/pipeline_sana_sprint_img2img.py | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\code-sana--pipeline_sana_sprint_img2img.py-html.decoded.txt | e25c4fe7a72c9766b047f2774df51fdc970818e5f6f555241ac765f339616a0c |
| https://arxiv.org/html/2410.10629v1 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\T2-sana-paper.read.txt | 85eb59544231db2358a7085278499503982012375a028829cfa1a05f2b06665c |
