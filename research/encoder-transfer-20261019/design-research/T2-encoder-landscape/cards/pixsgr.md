# PixSGR

Rechecked 2026-10-20 UTC for BRIEF §1b. Evidence: **V2 — primary paper method and evaluation inspected**. Floor count: **YES; one distinct family in the conservative floor**.

## Inspected primary method and evaluation

Locators: §3.1 low-channel bottleneck; §3.2 sparse global refinement; ImageNet protocol/tables; official release inventory.

Primary paper: [2609.00798v1](https://arxiv.org/html/2609.00798v1). Cached original SHA-256 `1fa6bce6d006efb68ca048ca89845bbc3a3a68a6305776335eefa57df193e214` at `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\pixsgr-paper.txt`. “V2” is the inspection tier, not the arXiv revision.

**Method evidence (direct source account):** Pixel diffusion with learned low-channel bottleneck and sparse global refinement inside the denoiser. RGB3/f1 output, no external pretrained AE.

**Quantitative evaluation and conditions (direct source account):** ImageNet256,50K samples,320 epochs,875M model: FID1.51, IS311, precision.78, recall.65. CFG3 over[.2,.98], interval guidance.04 over[.2,.7]. These are evaluation settings, not .2 img2img strength. No general T2I1024 result established.

## Lineage, representation and implementation

**Training lineage assessment (agent inference constrained by the cited account):** Against SD1/SDXL: NOT APPLICABLE. Internal representation learning can still remove marks; pixel space does not guarantee retention.

**Official code and img2img:** CVL-UESTC/PixSGR repo1f08f332fb469c893cfa8992ad269d8588173c5a exposes README/assets, no runnable sampler inspected. HF contains only .gitattributes and no released weights. Native Diffusers support unverified.

Diffusers source inspection pin: `e04f0c5f24392fcd34b32d18d0ce03668f9bcd50` unless this card explicitly names `v0.36.0`. This is source inspection, not installation, import, GPU validation or an amendment of the frozen runtime. Source URLs and hashes appear below. Absence of `strength` means the native interface does not expose the frozen partial-noise corruption; image conditioning alone is insufficient.

| Official model/revision URL | Exact revision | Declared model license | Actual access observation |
|---|---|---|---|
| [CVLUESTC/PixSGR](https://huggingface.co/CVLUESTC/PixSGR/tree/ad6d1c3fcd616abb39e1dedcf43face1f7ab810a) | ad6d1c3fcd616abb39e1dedcf43face1f7ab810a | not declared | ungated API snapshot |

Licenses in this table concern the named model package; dependency caveats below remain separate. An ungated metadata snapshot does not prove every dependency is ungated. No model weights were downloaded.

## 1024 memory/time and design consequence

875M parameters imply at least1.75GB BF16 weights. Evaluation at256/512; no supported1024 model or primary1024 peak/time. Availability gap blocks an executable cost plan.

Any parameter-memory figure is a lower bound or explicitly conditional estimate: decimal GB, two bytes per BF16 parameter, inference only, no optimizer. It excludes activations, attention/KV buffers, extra encoders, CFG duplication, allocator workspace and loading peaks. It is not a measured fit or wall-clock prediction.

**Design implication (agent inference):** Qualifies as substantively inspected distinct research, not an executable candidate. Paper evidence and released-model availability are separate.

**Limits/open assumptions:** Ungated but empty HF repository; license/code/weights unavailable rather than gated.

No evaluation above measures this thesis’s mark survival, false positives or fixed decision rule. Paper outcomes remain author-reported literature evidence, not development outcomes.

## Inspectable source receipts

| Exact source URL | Local cached text | SHA-256 |
|---|---|---|
| https://arxiv.org/html/2609.00798v1 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\pixsgr-paper.txt | 1fa6bce6d006efb68ca048ca89845bbc3a3a68a6305776335eefa57df193e214 |
| https://api.github.com/search/repositories?q=PixSGR | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\pixsgr-repo-discovery.txt | 3289c9f9b7b6b32b84c76389791b6eea19be5f5512cf25aa3790bdf8e4d57099 |
| https://huggingface.co/api/models/CVLUESTC/PixSGR?blobs=true | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\pixsgr-api.txt | 4e2244de12a266693f850da272a7d82cb3e3825ec9624ec3d43ee6804774ad09 |
| https://github.com/CVL-UESTC/PixSGR/tree/1f08f332fb469c893cfa8992ad269d8588173c5a | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\pixsgr-readme-pinned.txt | 42e5e9ae00a8b0ff76455092c4e88914a55564ff689de39e02732c115fdcac49 |
| https://github.com/CVL-UESTC/PixSGR/tree/1f08f332fb469c893cfa8992ad269d8588173c5a | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\pixsgr-readme-pinned.decoded.txt | 161b6c1a1eabba929603ba0549a550735264d672e298c74b8c0a608d171b6c5d |
| https://arxiv.org/html/2609.00798v1 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\pixsgr-paper.read.txt | 392ca63953ca25009d581014d0ac3f095b44bd62f830d3437782f5639258aec7 |
