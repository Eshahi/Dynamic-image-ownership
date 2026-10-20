# AuraFlow v0.3 lead

Rechecked 2026-10-20 UTC for BRIEF §1b. Evidence: **NATIVE PRIMARY MODEL/CODE — explicitly not paper V2**. Floor count: **NO; supporting variant/encoder, native-card evidence or incomplete evaluation lead**.

## Inspected primary method and evaluation

Locators: Official modelcard Usage/Limitations; VAE config and advertised LFS hash; native pipeline signature.

**Method evidence (direct source account):** Flow transformer with C4/f8 VAE; advertised VAE object matches SDXL. Card describes beta v0.3 and1536/multiaspect generation.

**Quantitative evaluation and conditions (direct source account):** No reproducible quantitative benchmark protocol in inspected card. This is a model/code lead, not a qualifying evaluated family.

## Lineage, representation and implementation

**Training lineage assessment (agent inference constrained by the cited account):** Against SD1 inheritsSDXL ancestry; againstSDXL SAME published VAE object. Different generator does not add encoder diversity.

**Official code and img2img:** auraflow/pipeline_aura_flow.py T2I only at inspected code;50-step/CFG3.5 example, no image+strength.

Diffusers source inspection pin: `e04f0c5f24392fcd34b32d18d0ce03668f9bcd50` unless this card explicitly names `v0.36.0`. This is source inspection, not installation, import, GPU validation or an amendment of the frozen runtime. Source URLs and hashes appear below. Absence of `strength` means the native interface does not expose the frozen partial-noise corruption; image conditioning alone is insufficient.

| Official model/revision URL | Exact revision | Declared model license | Actual access observation |
|---|---|---|---|
| [fal/AuraFlow-v0.3](https://huggingface.co/fal/AuraFlow-v0.3/tree/2cd8588f04c886002be4571697d84654a50e3af3) | 2cd8588f04c886002be4571697d84654a50e3af3 | apache-2.0 | ungated API snapshot |

Licenses in this table concern the named model package; dependency caveats below remain separate. An ungated metadata snapshot does not prove every dependency is ungated. No model weights were downloaded.

## 1024 memory/time and design consequence

No primary1024 peak/time. Model family roughly6.8B implies≥13.6GB BF16 weights if that nominal count is used; exact component count not independently checked, so treat this as conditional estimate, not guaranteed floor.

Any parameter-memory figure is a lower bound or explicitly conditional estimate: decimal GB, two bytes per BF16 parameter, inference only, no optimizer. It excludes activations, attention/KV buffers, extra encoders, CFG duplication, allocator workspace and loading peaks. It is not a measured fit or wall-clock prediction.

**Design implication (agent inference):** Exclude from independent-encoder expansion and conservative floor.

**Limits/open assumptions:** Apache ungated metadata; evidence insufficient for generation-quality ranking.

No evaluation above measures this thesis’s mark survival, false positives or fixed decision rule. Paper outcomes remain author-reported literature evidence, not development outcomes.

## Inspectable source receipts

| Exact source URL | Local cached text | SHA-256 |
|---|---|---|
| https://huggingface.co/api/models/fal/AuraFlow-v0.3?blobs=true | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-fal--AuraFlow-v0.3-api.json | 52a371c422b083ab012d8d09e210e834b4196df01797636e5a2260e22a2deeec |
| https://huggingface.co/fal/AuraFlow-v0.3/resolve/2cd8588f04c886002be4571697d84654a50e3af3/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-fal--AuraFlow-v0.3-README.md | 4b06a70c7afb2f2a3ab7fbc043373c37c291c5a348a63000e47fde18d5609e11 |
| https://huggingface.co/fal/AuraFlow-v0.3/resolve/2cd8588f04c886002be4571697d84654a50e3af3/vae/config.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-fal--AuraFlow-v0.3-vae--config.json | bf2daa82c70fb8437853a3e9cd901c775a3f7a9af9b49227663ad86e93be3bc7 |
| https://huggingface.co/fal/AuraFlow-v0.3/resolve/2cd8588f04c886002be4571697d84654a50e3af3/model_index.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-fal--AuraFlow-v0.3-model_index.json | 7ffee10ae3277f136a341bac357405d615961f7c949f7c2e231075f8c7d18541 |
| https://huggingface.co/api/models/fal/AuraFlow-v0.3?blobs=true | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\auraflow-api.txt | 81b4efb96ebfb36e9dbe106f22c763e4786d4fe2d7cc03738d111a21821c6614 |
| https://huggingface.co/fal/AuraFlow-v0.3/resolve/2cd8588f04c886002be4571697d84654a50e3af3/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\fal--AuraFlow-v0.3--README.md.txt | 4b06a70c7afb2f2a3ab7fbc043373c37c291c5a348a63000e47fde18d5609e11 |
| https://huggingface.co/fal/AuraFlow-v0.3/resolve/2cd8588f04c886002be4571697d84654a50e3af3/vae/config.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\fal--AuraFlow-v0.3--vae--config.json.txt | bf2daa82c70fb8437853a3e9cd901c775a3f7a9af9b49227663ad86e93be3bc7 |
| https://huggingface.co/fal/AuraFlow-v0.3/resolve/2cd8588f04c886002be4571697d84654a50e3af3/model_index.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\fal--AuraFlow-v0.3--model_index.json.txt | 7ffee10ae3277f136a341bac357405d615961f7c949f7c2e231075f8c7d18541 |
| https://api.github.com/repos/huggingface/diffusers/contents/src/diffusers/pipelines/aura_flow/pipeline_aura_flow.py?ref=e04f0c5f24392fcd34b32d18d0ce03668f9bcd50 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\code-aura-api.decoded.txt | ba8da80cbc0e3074598eb0d1d5cc861bb55a03fde35b8fb64143f4102cdcb1e5 |
