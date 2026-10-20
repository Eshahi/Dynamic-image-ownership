# Lumina-Image 2.0

Rechecked 2026-10-20 UTC for BRIEF §1b. Evidence: **V2 — primary paper method and evaluation inspected**. Floor count: **YES; one distinct family in the conservative floor**.

## Inspected primary method and evaluation

Locators: UnifiedNextDiT architecture; official README VAE statement; §5.4/Table8; Fig11 efficiency protocol.

Primary paper: [2503.21758v1](https://arxiv.org/html/2503.21758v1). Cached original SHA-256 `0d145a61994b9054cc1c0e90b865262e0ece4bc2b298704af34476ba31ae8275` at `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\lumina-paper.txt`. “V2” is the inspection tier, not the arXiv revision.

**Method evidence (direct source account):** 2.6B UnifiedNextDiT with Gemma2-2B and FLUX VAE, C=16/f=8. Progressive multiresolution training, RoPE and CFG normalization improve the denoiser.

**Quantitative evaluation and conditions (direct source account):** Table8: low-resolution DPG84.5/GenEval.63 → high-resolution85.7/.67 → high-quality5K updates87.2/.73 →11K updates87.6/.72. Nonmonotonic GenEval requires retaining training-stage context. FDPM/TeaCache speed choices trade stability or blur.

## Lineage, representation and implementation

**Training lineage assessment (agent inference constrained by the cited account):** Against SD1 and SDXL: UNKNOWN through FLUX. The VAE is reused, not separately trained for Lumina.

**Official code and img2img:** lumina2/pipeline_lumina2.py: T2I only, default 30 steps, no image/strength parameter.

Diffusers source inspection pin: `e04f0c5f24392fcd34b32d18d0ce03668f9bcd50` unless this card explicitly names `v0.36.0`. This is source inspection, not installation, import, GPU validation or an amendment of the frozen runtime. Source URLs and hashes appear below. Absence of `strength` means the native interface does not expose the frozen partial-noise corruption; image conditioning alone is insufficient.

| Official model/revision URL | Exact revision | Declared model license | Actual access observation |
|---|---|---|---|
| [Alpha-VLLM/Lumina-Image-2.0](https://huggingface.co/Alpha-VLLM/Lumina-Image-2.0/tree/53504abd8178b30685b6c4c7a4cd181ff78b73e9) | 53504abd8178b30685b6c4c7a4cd181ff78b73e9 | apache-2.0 | ungated API snapshot |

Licenses in this table concern the named model package; dependency caveats below remain separate. An ungated metadata snapshot does not prove every dependency is ungated. No model weights were downloaded.

## 1024 memory/time and design consequence

Denoiser weights alone are at least 5.2 GB BF16, plus about 4 GB Gemma and VAE/activations. Fig11 compares A100 batch-one 1024 latency graphically; exact seconds were not reliably extracted. Target-device peak/runtime remain unknown.

Any parameter-memory figure is a lower bound or explicitly conditional estimate: decimal GB, two bytes per BF16 parameter, inference only, no optimizer. It excludes activations, attention/KV buffers, extra encoders, CFG duplication, allocator workspace and loading peaks. It is not a measured fit or wall-clock prediction.

**Design implication (agent inference):** A further FLUX reuse example, low priority for an independent-encoder panel.

**Limits/open assumptions:** Apache ungated package; upstream Gemma license/access remain separate dependencies. No native strength interface is assumed.

No evaluation above measures this thesis’s mark survival, false positives or fixed decision rule. Paper outcomes remain author-reported literature evidence, not development outcomes.

## Inspectable source receipts

| Exact source URL | Local cached text | SHA-256 |
|---|---|---|
| https://huggingface.co/api/models/Alpha-VLLM/Lumina-Image-2.0?blobs=true | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-Alpha-VLLM--Lumina-Image-2.0-api.json | 77dc33b44630cbdbbe27013b354b661c314d9b2c2b8c65b5f1c1d0bac2204e97 |
| https://huggingface.co/Alpha-VLLM/Lumina-Image-2.0/resolve/53504abd8178b30685b6c4c7a4cd181ff78b73e9/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-Alpha-VLLM--Lumina-Image-2.0-README.md | 028997c0841a44c282f53786c955f8bedd6b829fba36351a3ab473f5a404d6e5 |
| https://huggingface.co/Alpha-VLLM/Lumina-Image-2.0/resolve/53504abd8178b30685b6c4c7a4cd181ff78b73e9/vae/config.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-Alpha-VLLM--Lumina-Image-2.0-vae--config.json | 80c5ed836c7171f6817a8addb910cdd32d30ca65549ba13b75e097c0c30fb326 |
| https://huggingface.co/Alpha-VLLM/Lumina-Image-2.0/resolve/53504abd8178b30685b6c4c7a4cd181ff78b73e9/model_index.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-Alpha-VLLM--Lumina-Image-2.0-model_index.json | 1590e95ac1235820a3151bd6dfbed840a025ddedddcf67af5a8a304a2d2be426 |
| https://huggingface.co/api/models/Alpha-VLLM/Lumina-Image-2.0?blobs=true | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\lumina2-api.txt | e5e0b965ae60303ceec1a09e2cdc42b2d664125a87fa7a6f4347989d8938ff87 |
| https://arxiv.org/html/2503.21758v1 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\lumina-paper.txt | 0d145a61994b9054cc1c0e90b865262e0ece4bc2b298704af34476ba31ae8275 |
| https://huggingface.co/Alpha-VLLM/Lumina-Image-2.0/resolve/53504abd8178b30685b6c4c7a4cd181ff78b73e9/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\Alpha-VLLM--Lumina-Image-2.0--README.md.txt | 028997c0841a44c282f53786c955f8bedd6b829fba36351a3ab473f5a404d6e5 |
| https://huggingface.co/Alpha-VLLM/Lumina-Image-2.0/resolve/53504abd8178b30685b6c4c7a4cd181ff78b73e9/vae/config.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\Alpha-VLLM--Lumina-Image-2.0--vae--config.json.txt | 80c5ed836c7171f6817a8addb910cdd32d30ca65549ba13b75e097c0c30fb326 |
| https://huggingface.co/Alpha-VLLM/Lumina-Image-2.0/resolve/53504abd8178b30685b6c4c7a4cd181ff78b73e9/model_index.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\Alpha-VLLM--Lumina-Image-2.0--model_index.json.txt | 1590e95ac1235820a3151bd6dfbed840a025ddedddcf67af5a8a304a2d2be426 |
| https://api.github.com/repos/huggingface/diffusers/contents/src/diffusers/pipelines/lumina2/pipeline_lumina2.py?ref=e04f0c5f24392fcd34b32d18d0ce03668f9bcd50 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\code-lumina2--pipeline_lumina2.py-api.txt | 57f36dd5c100384a571253dd2c88f150577b855623efd6bccab8e4a67af52cb2 |
| https://api.github.com/repos/huggingface/diffusers/contents/src/diffusers/pipelines/lumina2/pipeline_lumina2.py?ref=e04f0c5f24392fcd34b32d18d0ce03668f9bcd50 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\code-lumina2--pipeline_lumina2.py-api.decoded.txt | e2e25bc37c944fe71943d34356f26cdc9670bf12db82dc8412fb864f8f612505 |
| https://arxiv.org/html/2503.21758v1 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\lumina-paper.read.txt | 8a660ca30cb70ff3ae579469ba40bd48fb23b9e5b9cee5b8183e69d9df418bdb |
