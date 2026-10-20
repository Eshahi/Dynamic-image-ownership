# Würstchen / Stable Cascade

Rechecked 2026-10-20 UTC for BRIEF §1b. Evidence: **V2 — primary paper method and evaluation inspected**. Floor count: **YES; one distinct family in the conservative floor**.

## Inspected primary method and evaluation

Locators: §3 three-stage compression; §4.1 COCO/PickScore; §4.2/Table2; Fig4; successor modelcard.

Primary paper: [2306.00637v2](https://arxiv.org/html/2306.00637v2). Cached original SHA-256 `785b933d564d2ebd751d2fe8fa7e550702dd1751566164e06bcaf1286d8186ca` at `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\cascade-paper.txt`. “V2” is the inspection tier, not the arXiv revision.

**Method evidence (direct source account):** Stage A VQ reconstruction uses spatial f=4; Stage B reconstructs its latent; Stage C uses a semantic EfficientNetV2-S compressor with16 channels and about24×24 tokens for1024, effective f≈42.7. This is not a single f8 VAE. Stable Cascade successor sizes differ from the paper.

**Quantitative evaluation and conditions (direct source account):** COCO30K generated at1024, downsampled to256 for FID. Table2 Würstchen FID23.6/IS40.9; Stage C60 steps, Stage B12 steps, CFG4. PickScore also uses LocalNarratives5K and PartiPrompts. These are not measurements of the Stable Cascade3.6B release.

## Lineage, representation and implementation

**Training lineage assessment (agent inference constrained by the cited account):** Against SD1/SDXL: qualified YES for a distinct documented semantic compressor, ImageNet pretraining and stage training. This does not prove disjoint training data.

**Official code and img2img:** stable_cascade/pipeline_stable_cascade_prior.py allows images to condition the prior, but no strength. It does not expose source-latent partial denoising.

Diffusers source inspection pin: `e04f0c5f24392fcd34b32d18d0ce03668f9bcd50` unless this card explicitly names `v0.36.0`. This is source inspection, not installation, import, GPU validation or an amendment of the frozen runtime. Source URLs and hashes appear below. Absence of `strength` means the native interface does not expose the frozen partial-noise corruption; image conditioning alone is insufficient.

| Official model/revision URL | Exact revision | Declared model license | Actual access observation |
|---|---|---|---|
| [stabilityai/stable-cascade](https://huggingface.co/stabilityai/stable-cascade/tree/a89f66d459ae653e3b4d4f992a7c3789d0dc4d16) | a89f66d459ae653e3b4d4f992a7c3789d0dc4d16 | other | ungated API snapshot |

Licenses in this table concern the named model package; dependency caveats below remain separate. An ungated metadata snapshot does not prove every dependency is ungated. No model weights were downloaded.

## 1024 memory/time and design consequence

Paper Fig4 A1001024 shows more than2× SDXL relative speed; exact portable peak/seconds unavailable. Stable Cascade3.6B prior alone requires at least7.2GB BF16 plus decoder/text/VQ. Sequential offload changes time; matched release1024 runtime unknown.

Any parameter-memory figure is a lower bound or explicitly conditional estimate: decimal GB, two bytes per BF16 parameter, inference only, no optimizer. It excludes activations, attention/KV buffers, extra encoders, CFG duplication, allocator workspace and loading peaks. It is not a measured fit or wall-clock prediction.

**Design implication (agent inference):** A distinct semantic compression route, but noncommercial terms and non-equivalent conditioning reduce immediate feasibility.

**Limits/open assumptions:** Ungated custom noncommercial model license. Successor weights and stages prevent direct reuse of paper timing or scores.

No evaluation above measures this thesis’s mark survival, false positives or fixed decision rule. Paper outcomes remain author-reported literature evidence, not development outcomes.

## Inspectable source receipts

| Exact source URL | Local cached text | SHA-256 |
|---|---|---|
| https://huggingface.co/api/models/stabilityai/stable-cascade?blobs=true | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\cascade-api.txt | 15b08077a2fbde3f638df3c4ae998a2b80fb7b54bdd0e092848edbdc21cfcdbd |
| https://arxiv.org/html/2306.00637v2 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\cascade-paper.txt | 785b933d564d2ebd751d2fe8fa7e550702dd1751566164e06bcaf1286d8186ca |
| https://huggingface.co/stabilityai/stable-cascade/resolve/a89f66d459ae653e3b4d4f992a7c3789d0dc4d16/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\stabilityai--stable-cascade--README.md.txt | fac1ea38330cb92617d4e46f2ddc8e117fb4db45b74786d89da40a34c91c0569 |
| https://huggingface.co/stabilityai/stable-cascade/resolve/a89f66d459ae653e3b4d4f992a7c3789d0dc4d16/model_index.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\stabilityai--stable-cascade--model_index.json.txt | 0c8c28b033d3f7462c7b63ba0e891efad044766a147f5fdee8257e03aaa749f9 |
| https://api.github.com/repos/huggingface/diffusers/contents/src/diffusers/pipelines/stable_cascade/pipeline_stable_cascade_prior.py?ref=e04f0c5f24392fcd34b32d18d0ce03668f9bcd50 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\code-stable_cascade--pipeline_stable_cascade_prior.py-api.txt | e58f4919d400b2879a1b594204e698a717bd97fbc840fcb2671eb0b761d7c2fa |
| https://api.github.com/repos/huggingface/diffusers/contents/src/diffusers/pipelines/stable_cascade/pipeline_stable_cascade_prior.py?ref=e04f0c5f24392fcd34b32d18d0ce03668f9bcd50 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\code-stable_cascade--pipeline_stable_cascade_prior.py-api.decoded.txt | 5bce912ffeec386c534dc4c9aab0386cdd32eaf067f86ad8005d0a7c09ba9d9f |
| https://arxiv.org/abs/2306.00637 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\cascade-bibliographic-metadata.txt | 2837feea4ae2e219b599a8df27241ef4db41a0645bb8a9b123390c242d76b029 |
| https://arxiv.org/html/2306.00637v2 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\cascade-paper.read.txt | c3082420c24969ca1f61b5a736fc03e1fb05122b721588aeae4723f1e2bbbc69 |
