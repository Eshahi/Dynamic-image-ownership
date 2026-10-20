# DeepFloyd IF native primary model evidence

Rechecked 2026-10-20 UTC for BRIEF §1b. Evidence: **NATIVE PRIMARY MODEL/CODE — explicitly not paper V2**. Floor count: **NO; supporting variant/encoder, native-card evidence or incomplete evaluation lead**.

## Inspected primary method and evaluation

Locators: Official IF modelcard architecture/training/evaluation/usage; IF repository resource notes; native img2img source.

**Method evidence (direct source account):** Three pixel diffusion stages64→256→1024, T5 text encoder, no AE in IF stages. Common example substitutes SDx4 latent upscaler for stage3, so that example is not fully pixel-space.

**Quantitative evaluation and conditions (direct source account):** Primary card reports COCO30K FID6.66, StageI2.42M training steps at64 and1000-step cosine noise schedule. No paper V2 claim; native card is substantively inspected but not counted among18 paper families.

## Lineage, representation and implementation

**Training lineage assessment (agent inference constrained by the cited account):** Against SD1/SDXL: no AE in true IF stages; substituted SD upscaler changes that conclusion.

**Official code and img2img:** deepfloyd_if/pipeline_if_img2img.py accepts image+strength, adds pixel noise. StageI operates64, then cascades; not a single native1024 source-preserving denoiser.

Diffusers source inspection pin: `e04f0c5f24392fcd34b32d18d0ce03668f9bcd50` unless this card explicitly names `v0.36.0`. This is source inspection, not installation, import, GPU validation or an amendment of the frozen runtime. Source URLs and hashes appear below. Absence of `strength` means the native interface does not expose the frozen partial-noise corruption; image conditioning alone is insufficient.

| Official model/revision URL | Exact revision | Declared model license | Actual access observation |
|---|---|---|---|
| [DeepFloyd/IF-I-XL-v1.0](https://huggingface.co/DeepFloyd/IF-I-XL-v1.0/tree/c03d510e9b75bce9f9db5bb85148c1402ad7e694) | c03d510e9b75bce9f9db5bb85148c1402ad7e694 | deepfloyd-if-license | auto gated |

Licenses in this table concern the named model package; dependency caveats below remain separate. An ungated metadata snapshot does not prove every dependency is ungated. No model weights were downloaded.

## 1024 memory/time and design consequence

Modelcard CPU-offload14GB and repo16GB stages1/2,24GB mixed full pipeline reports use different configurations. StageI4.3B floor8.6GB BF16 plus T5/superresolution. Matched fully pixel1024 img2img time/peak unknown.

Any parameter-memory figure is a lower bound or explicitly conditional estimate: decimal GB, two bytes per BF16 parameter, inference only, no optimizer. It excludes activations, attention/KV buffers, extra encoders, CFG duplication, allocator workspace and loading peaks. It is not a measured fit or wall-clock prediction.

**Design implication (agent inference):** Pixel mechanism example with native img2img, but gate/noncommercial terms and low-resolution cascade weaken feasibility.

**Limits/open assumptions:** Auto-gated custom DeepFloyd research license, not permissive/ungated. Do not describe substituted SD upscaler example as no-AE.

No evaluation above measures this thesis’s mark survival, false positives or fixed decision rule. Paper outcomes remain author-reported literature evidence, not development outcomes.

## Inspectable source receipts

| Exact source URL | Local cached text | SHA-256 |
|---|---|---|
| https://huggingface.co/api/models/DeepFloyd/IF-I-XL-v1.0?blobs=true | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-DeepFloyd--IF-I-XL-v1.0-api.json | ca81b413993d45a9f1d1405c7cb7bf426e4fa735e32b3e75e622d6e5a4c1c496 |
| https://huggingface.co/DeepFloyd/IF-I-XL-v1.0/resolve/c03d510e9b75bce9f9db5bb85148c1402ad7e694/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-DeepFloyd--IF-I-XL-v1.0-README.md | 3894749f2a584954759728d1e8c25900e3a5d048537dadca08239a0e91a978a1 |
| https://huggingface.co/api/models/DeepFloyd/IF-I-XL-v1.0?blobs=true | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\if-api.txt | 98f56c3df5026fbfaa6d35c5322c5dc9175cc6c0a07c9ab75e22f7c00a3e6731 |
| https://huggingface.co/DeepFloyd/IF-I-XL-v1.0/resolve/c03d510e9b75bce9f9db5bb85148c1402ad7e694/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\DeepFloyd--IF-I-XL-v1.0--README.md.txt | 3894749f2a584954759728d1e8c25900e3a5d048537dadca08239a0e91a978a1 |
| https://api.github.com/repos/huggingface/diffusers/contents/src/diffusers/pipelines/deepfloyd_if/pipeline_if_img2img.py?ref=e04f0c5f24392fcd34b32d18d0ce03668f9bcd50 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\code-deepfloyd_if--pipeline_if_img2img.py-api.txt | d36bdd9b7598ba6183f49f59e94f1b62c6c3342dc11770d7a838b85b02183070 |
| https://api.github.com/repos/huggingface/diffusers/contents/src/diffusers/pipelines/deepfloyd_if/pipeline_if_img2img.py?ref=e04f0c5f24392fcd34b32d18d0ce03668f9bcd50 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\code-deepfloyd_if--pipeline_if_img2img.py-api.decoded.txt | 7badedd113d2f5a08dc266480c54641d9751bb6bfac7fac7793f3412e6f278fc |
| https://api.github.com/repos/deep-floyd/IF/contents/README.md?ref=ffc8163891682beaca0c5eb6b9077860a3bc6509 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\if-repo-readme.decoded.txt | 7c1ef2bb84dcc428e47097023ba6af9c75996272d1f10f5b74260ad44c3d2a17 |
