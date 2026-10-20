# Pixel-space DDPM

Rechecked 2026-10-20 UTC for BRIEF §1b. Evidence: **V2 — primary paper method and evaluation inspected**. Floor count: **YES; one distinct family in the conservative floor**.

## Inspected primary method and evaluation

Locators: §3 forward/reverse process and objective; §4/Table1; AppendixB architecture and sampling cost.

Primary paper: [2006.11239v2](https://arxiv.org/html/2006.11239v2). Cached original SHA-256 `889bf6b3d1e18930447c30ab2c32c4c9b6134777502794e2f09aa7fd4506aef5` at `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\ddpm-paper.txt`. “V2” is the inspection tier, not the arXiv revision.

**Method evidence (direct source account):** RGB C=3/f=1, no AE. U-Net predicts noise with group normalization and attention at16². Training uses1000 steps and beta1e-4→.02.

**Quantitative evaluation and conditions (direct source account):** Table1 CIFAR train-reference FID3.17 (test-reference5.24), IS9.46. LSUNChurch256 FID7.89 and Bedroom4.90. These unconditional domain metrics do not validate general-photo regeneration.

## Lineage, representation and implementation

**Training lineage assessment (agent inference constrained by the cited account):** Against SD1 and SDXL: NOT APPLICABLE, no AE. This tests regeneration without an AE bottleneck, not another independently trained encoder.

**Official code and img2img:** ddpm/pipeline_ddpm.py accepts batch_size and num_inference_steps, not image/strength. Pixel SDEdit requires forward-noising and correct scheduler truncation; not implemented or authorized.

Diffusers source inspection pin: `e04f0c5f24392fcd34b32d18d0ce03668f9bcd50` unless this card explicitly names `v0.36.0`. This is source inspection, not installation, import, GPU validation or an amendment of the frozen runtime. Source URLs and hashes appear below. Absence of `strength` means the native interface does not expose the frozen partial-noise corruption; image conditioning alone is insufficient.

| Official model/revision URL | Exact revision | Declared model license | Actual access observation |
|---|---|---|---|
| [google/ddpm-celebahq-256](https://huggingface.co/google/ddpm-celebahq-256/tree/cd5c944777ea2668051904ead6cc120739b86c4d) | cd5c944777ea2668051904ead6cc120739b86c4d | apache-2.0 | ungated API snapshot |

Licenses in this table concern the named model package; dependency caveats below remain separate. An ungated metadata snapshot does not prove every dependency is ungated. No model weights were downloaded.

## 1024 memory/time and design consequence

The114M model requires at least .228GB BF16 parameters. Paper sampling on TPUv3-8 takes300s for batch128 at256; not GPU batch-one or1024. Official face checkpoint supports256; no validated1024 setting, peak or latency.

Any parameter-memory figure is a lower bound or explicitly conditional estimate: decimal GB, two bytes per BF16 parameter, inference only, no optimizer. It excludes activations, attention/KV buffers, extra encoders, CFG duplication, allocator workspace and loading peaks. It is not a measured fit or wall-clock prediction.

**Design implication (agent inference):** Feasible permissive ungated small mechanism control, but demoted from the lead pixel proposal because high-resolution pixel alternatives exist. It cannot stand in for general-photo1024 regeneration.

**Limits/open assumptions:** Apache2 model and permissive diffusion code. An adapter would be new scientific work;256 feasibility does not establish1024 feasibility.

No evaluation above measures this thesis’s mark survival, false positives or fixed decision rule. Paper outcomes remain author-reported literature evidence, not development outcomes.

## Inspectable source receipts

| Exact source URL | Local cached text | SHA-256 |
|---|---|---|
| https://huggingface.co/api/models/google/ddpm-celebahq-256?blobs=true | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-google--ddpm-celebahq-256-api.json | 3a29527a29b3ae2bca9eb22fff595f30e015959ec0c578b443c4b895f574a04e |
| https://huggingface.co/google/ddpm-celebahq-256/resolve/cd5c944777ea2668051904ead6cc120739b86c4d/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-google--ddpm-celebahq-256-README.md | 8c5543f321d69e4974766eefc80dd1e4b280d5c8c90b2d7b7db2becee5e26c00 |
| https://huggingface.co/google/ddpm-celebahq-256/resolve/cd5c944777ea2668051904ead6cc120739b86c4d/model_index.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-google--ddpm-celebahq-256-model_index.json | c6a0e54d1d235280bce7e40abae49b73c4de0011ddbf09d817ce39e848cc2fa7 |
| https://huggingface.co/api/models/google/ddpm-celebahq-256?blobs=true | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\ddpm-api.txt | 8692164d77f6a11ed95dd0d64dfaa1c6b1f4971ef4d3a4329ad977b4ea0f9d2d |
| https://arxiv.org/html/2006.11239v2 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\ddpm-paper.txt | 889bf6b3d1e18930447c30ab2c32c4c9b6134777502794e2f09aa7fd4506aef5 |
| https://huggingface.co/google/ddpm-celebahq-256/resolve/cd5c944777ea2668051904ead6cc120739b86c4d/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\google--ddpm-celebahq-256--README.md.txt | 8c5543f321d69e4974766eefc80dd1e4b280d5c8c90b2d7b7db2becee5e26c00 |
| https://huggingface.co/google/ddpm-celebahq-256/resolve/cd5c944777ea2668051904ead6cc120739b86c4d/model_index.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\google--ddpm-celebahq-256--model_index.json.txt | c6a0e54d1d235280bce7e40abae49b73c4de0011ddbf09d817ce39e848cc2fa7 |
| https://api.github.com/repos/huggingface/diffusers/contents/src/diffusers/pipelines/ddpm/pipeline_ddpm.py?ref=e04f0c5f24392fcd34b32d18d0ce03668f9bcd50 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\code-ddpm--pipeline_ddpm.py-api.txt | da260d873e7c56c8f9a7fb89ceb820e68e0c329a36f40f6e6d79381261c18c14 |
| https://api.github.com/repos/huggingface/diffusers/contents/src/diffusers/pipelines/ddpm/pipeline_ddpm.py?ref=e04f0c5f24392fcd34b32d18d0ce03668f9bcd50 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\code-ddpm--pipeline_ddpm.py-api.decoded.txt | 43e5b6747abd6ebb832e2f7d40f5339dcdfca60691512ca44f026e2d171c0b90 |
| https://arxiv.org/html/2006.11239v2 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\ddpm-paper.read.txt | 8f355b9155b4d2eacec443e08f4eb64d8f16040bb0f97f431c9f82d835260873 |
