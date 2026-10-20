# Kandinsky5 image lineage correction

Rechecked 2026-10-20 UTC for BRIEF §1b. Evidence: **V2 — primary paper method and evaluation inspected**. Floor count: **NO; supporting variant/encoder, native-card evidence or incomplete evaluation lead**.

## Inspected primary method and evaluation

Locators: §5.1–5.3 CrossDiT/encoders; §8.2.8 image-generation/editing SBS; official current Diffusers I2I signature.

Primary paper: [2511.14993v1](https://arxiv.org/html/2511.14993v1). Cached original SHA-256 `8a6039fc9f055662c3c76c9781c012f1d4dbf88242685eb99ecd41b6f31d066f` at `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-kandinsky5-paper.txt`. “V2” is the inspection tier, not the arXiv revision.

**Method evidence (direct source account):** Image Lite6B CrossDiT flow matching; explicitly FLUX.1-dev VAE C16/f8. Video uses HunyuanVideo VAE. The image branch is not MoVQ.

**Quantitative evaluation and conditions (direct source account):** §8.2.8 uses internal SBS prompts expanded from PartiPrompts with GigaMax; expert judges rate prompt following/visual quality against FLUX-dev/Qwen and editing counterparts. Figure win percentages and exact sample count were not extracted; remain unknown. Video2.7× speedup is not image timing.

## Lineage, representation and implementation

**Training lineage assessment (agent inference constrained by the cited account):** Against SD1/SDXL: UNKNOWN through FLUX1. Does not inherit Kandinsky2/3 distinct MoVQ encoder lineage.

**Official code and img2img:** kandinsky5/pipeline_kandinsky_i2i.py accepts image and prompt, default50 steps/CFG3.5, but no strength. Native instruction editing is not the frozen source-noise attack.

Diffusers source inspection pin: `e04f0c5f24392fcd34b32d18d0ce03668f9bcd50` unless this card explicitly names `v0.36.0`. This is source inspection, not installation, import, GPU validation or an amendment of the frozen runtime. Source URLs and hashes appear below. Absence of `strength` means the native interface does not expose the frozen partial-noise corruption; image conditioning alone is insufficient.

| Official model/revision URL | Exact revision | Declared model license | Actual access observation |
|---|---|---|---|
| No verified release revision | UNAVAILABLE | UNVERIFIED | endpoint inaccessible or release not resolved; see limitations |

Licenses in this table concern the named model package; dependency caveats below remain separate. An ungated metadata snapshot does not prove every dependency is ungated. No model weights were downloaded.

## 1024 memory/time and design consequence

6B image denoiser floor12GB BF16 plus Qwen2.5VL7B text conditioning/VAE. No matched primary1024 image peak/time; video acceleration figures cannot be reused.

Any parameter-memory figure is a lower bound or explicitly conditional estimate: decimal GB, two bytes per BF16 parameter, inference only, no optimizer. It excludes activations, attention/KV buffers, extra encoders, CFG duplication, allocator workspace and loading peaks. It is not a measured fit or wall-clock prediction.

**Design implication (agent inference):** Correct the family-level assumption: newer Kandinsky does not automatically provide another independent encoder.

**Limits/open assumptions:** Paper inspected V2, but exact image checkpoint revision/license/gate not resolved in this sweep. Treat those model-release fields unavailable, not inferred from old Apache Kandinsky.

No evaluation above measures this thesis’s mark survival, false positives or fixed decision rule. Paper outcomes remain author-reported literature evidence, not development outcomes.

## Inspectable source receipts

| Exact source URL | Local cached text | SHA-256 |
|---|---|---|
| https://arxiv.org/html/2511.14993v1 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-kandinsky5-paper.txt | 8a6039fc9f055662c3c76c9781c012f1d4dbf88242685eb99ecd41b6f31d066f |
| https://github.com/huggingface/diffusers/blob/e04f0c5f24392fcd34b32d18d0ce03668f9bcd50/src/diffusers/pipelines/kandinsky5/pipeline_kandinsky_i2i.py | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\code-kandinsky5--pipeline_kandinsky_i2i.py-html.txt | a0393d42d00b9405cc455b9aaa3185fd3c18af823accfe0a00ec77f5a98d8acf |
| https://github.com/huggingface/diffusers/blob/e04f0c5f24392fcd34b32d18d0ce03668f9bcd50/src/diffusers/pipelines/kandinsky5/pipeline_kandinsky_i2i.py | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\code-kandinsky5--pipeline_kandinsky_i2i.py-html.decoded.txt | e5dee9921871ba5d1f355868d15d535415480c4abaadebb0c718c9417ff7b18d |
| https://arxiv.org/html/2511.14993v1 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\T2-kandinsky5-paper.read.txt | 06d12869459e9ac042aff57dee5c308c710aa56e52ebb64d32353234a5ec6d0e |
