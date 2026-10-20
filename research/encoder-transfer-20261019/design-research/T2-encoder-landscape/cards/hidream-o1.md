# HiDream-O1 native pixel model and P7 recommendation

Rechecked 2026-10-20 UTC for BRIEF §1b. Evidence: **V2 — primary paper method and evaluation inspected**. Floor count: **NO; supporting variant/encoder, native-card evidence or incomplete evaluation lead**.

## Inspected primary method and evaluation

Locators: §3.2–3.4 unified pixel transformer/losses; §4 progressive training; §5 distillation/evaluation; official inference/pipeline/utils/index.

Primary paper: [2605.11061v1](https://arxiv.org/html/2605.11061v1). Cached original SHA-256 `a1f32df6e2e2032508a5c21470733be424a21cd7538b549508a20f81eecee4db` at `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\hidream-o1-paper.txt`. “V2” is the inspection tier, not the arXiv revision.

**Method evidence (direct source account):** Raw RGB C3/f1, no external VAE or disjoint text encoder; single shared text/image token system. Pixel patches32×32 are tokenization, not a learned AE compression. Qwen3-VL-8B initialization, clean-image prediction, LPIPS/perceptualDINO and flow conversion; distillation uses distribution matching/adversarial training.

**Quantitative evaluation and conditions (direct source account):** §5/table1 8B GenEval.90, Pro.92; DPG8B89.83. Full50/Dev28-step protocols and multiple text/editing benchmarks provide substantive evaluation. Sampling resolution/sample counts are not fully specified for every table; leaderboard images are not independent measurements.

## Lineage, representation and implementation

**Training lineage assessment (agent inference constrained by the cited account):** Against SD1/SDXL: NOT APPLICABLE, no AE. The integrated vision tower for reference conditioning is not a source-image latent bottleneck for target generation.

**Official code and img2img:** Official repo2c2d29ff729e48f33e41f49edfdbd81d5ac103b4: inference.py loads local model_path processor/model in BF16 CUDA. generate_image(ref_image_paths,height,width,steps,...) has no strength; target initializes Gaussian RGB noise, references provide context. Full50 steps/CFG5/shift3; Dev28 steps/CFG0/shift1, flow_match editing versus flash elsewhere. No native Diffusers O1 class verified.

Diffusers source inspection pin: `e04f0c5f24392fcd34b32d18d0ce03668f9bcd50` unless this card explicitly names `v0.36.0`. This is source inspection, not installation, import, GPU validation or an amendment of the frozen runtime. Source URLs and hashes appear below. Absence of `strength` means the native interface does not expose the frozen partial-noise corruption; image conditioning alone is insufficient.

| Official model/revision URL | Exact revision | Declared model license | Actual access observation |
|---|---|---|---|
| [HiDream-ai/HiDream-O1-Image](https://huggingface.co/HiDream-ai/HiDream-O1-Image/tree/0b0901d99f200389e138c61946af1185f5f49a13) | 0b0901d99f200389e138c61946af1185f5f49a13 | mit | ungated API snapshot |

Licenses in this table concern the named model package; dependency caveats below remain separate. An ungated metadata snapshot does not prove every dependency is ungated. No model weights were downloaded.

## 1024 memory/time and design consequence

Official index:8,804,887,792 parameters →17.609775584GB BF16 weight floor, excluding KV/activations/reference tokens. Tensor metadata35.219551168GB; eight files35.219643552GB. With20.206GB core,55.425643552GB before packages/images, below future80GB cap but not authorized now. No primary1024 peak/time. Crucially utils PREDEFINED_RESOLUTIONS includes2048² and~4MP rectangles, not1024; requested1024² snaps to2048². keep_original_aspect rescales toward2048² area, not a1024 bypass.

Any parameter-memory figure is a lower bound or explicitly conditional estimate: decimal GB, two bytes per BF16 parameter, inference only, no optimizer. It excludes activations, attention/KV buffers, extra encoders, CFG duplication, allocator workspace and loading peaks. It is not a measured fit or wall-clock prediction.

**Design implication (agent inference):** P7: replace DDPM as lead high-resolution pixel research direction with O1, but retain PRX as the direct1024-interface lead. O1 is NOT a drop-in frozen1024 regenerator: no strength, resolution snapping, runtime unmeasured and new dependency stack. Any1024 adaptation or native instruction-editing scenario needs explicit proposal/design approval and separate interpretation.

**Limits/open assumptions:** MIT code/models, HF ungated. Plain inference uses bundled local weights/tokenizer/processor; optional Gemma4-31B prompt agent requires gate acceptance, optional API can cost money. Neither optional reasoner is required for plain generation or authorized here. PyTorch≥2.10/Transformers4.57.1 and optional FlashAttention differ from frozen stack.

No evaluation above measures this thesis’s mark survival, false positives or fixed decision rule. Paper outcomes remain author-reported literature evidence, not development outcomes.

## Inspectable source receipts

| Exact source URL | Local cached text | SHA-256 |
|---|---|---|
| https://arxiv.org/html/2605.11061v1 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\hidream-o1-paper.txt | a1f32df6e2e2032508a5c21470733be424a21cd7538b549508a20f81eecee4db |
| https://huggingface.co/api/models/HiDream-ai/HiDream-O1-Image?blobs=true | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\hidream-o1-api.txt | b3a2437f618392b845e4c8f2739e0f5dbc77f51fa94d1b7ffb9fe80c34c6b68e |
| https://huggingface.co/HiDream-ai/HiDream-O1-Image/resolve/0b0901d99f200389e138c61946af1185f5f49a13/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\hidream-o1-card.txt | 901f12f248a2e43a7ac6092d2a6de9f68f444c83e8ba4a53d55eb3069240e7b7 |
| https://huggingface.co/HiDream-ai/HiDream-O1-Image/resolve/0b0901d99f200389e138c61946af1185f5f49a13/config.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\hidream-o1-config.txt | 5cd452860dc1e9c29dd71cc3cef7f39b338b7a40793f7a260655c2d3568f3661 |
| https://github.com/HiDream-ai/HiDream-O1-Image/blob/2c2d29ff729e48f33e41f49edfdbd81d5ac103b4/inference.py | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\hidream-o1-inference.py.decoded.txt | e0ed5b516a35cb83cabf673d1cd7ddff14453e94b1fbfcc6ea8af1c61d02d90d |
| https://github.com/HiDream-ai/HiDream-O1-Image/blob/2c2d29ff729e48f33e41f49edfdbd81d5ac103b4/LICENSE | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\hidream-o1-LICENSE.decoded.txt | 6ea70e9e57680db2d91b8a8f0a54f565d36fe1e118e383f468bae913a8a95aa5 |
| https://github.com/HiDream-ai/HiDream-O1-Image/blob/2c2d29ff729e48f33e41f49edfdbd81d5ac103b4/models/pipeline.py | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\hidream-o1-models--pipeline.py.decoded.txt | d458e88ea9d77c305b6b333c2b7739914d788392313c2874c04d83d14d67c50a |
| https://github.com/HiDream-ai/HiDream-O1-Image/blob/2c2d29ff729e48f33e41f49edfdbd81d5ac103b4/requirements.txt | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\hidream-o1-requirements.txt.decoded.txt | b449b3ef2b1e7727f1c21aa4f65c585e3ca86d0bb13656889f42d5a17854bc2a |
| https://huggingface.co/HiDream-ai/HiDream-O1-Image/resolve/0b0901d99f200389e138c61946af1185f5f49a13/model.safetensors.index.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\hidream-o1-index.txt | 33865f9d84679a850080795107f049c3fac81c78d343322f66a36163b9ab53c9 |
| https://arxiv.org/html/2605.11061v1 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\hidream-o1-paper.read.txt | c2766216cb3358dad5a9056efcb6d17f85409d0c6810038f5a3151b8c79e0e3b |
| https://github.com/HiDream-ai/HiDream-O1-Image/blob/2c2d29ff729e48f33e41f49edfdbd81d5ac103b4/models/utils.py | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\hidream-o1-utils.decoded.txt | f6681b0813a8cbf3f6e9be4506791ef573ccecb3c703ce20e16f7a7ae1b419a6 |
