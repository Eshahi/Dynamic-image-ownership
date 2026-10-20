# Microsoft Lens

Rechecked 2026-10-20 UTC for BRIEF §1b. Evidence: **V2 — primary paper method and evaluation inspected**. Floor count: **YES; one distinct family in the conservative floor**.

## Inspected primary method and evaluation

Locators: §2.2 FLUX2 VAE and architecture; §2.5 acceleration; §3/Table2 and protocols; official README.

Primary paper: [2605.21573v1](https://arxiv.org/html/2605.21573v1). Cached original SHA-256 `a489c0e453326f60ce67312c753649d1bca1544bb964550edf71876ca55ce414` at `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-lens-paper.txt`. “V2” is the inspection tier, not the arXiv revision.

**Method evidence (direct source account):** 3.8B48-block MMDiT with frozen FLUX2 VAE, C=32/f=8;2×2 packing gives128 channels/f16 token grid. GPT-OSS20B total/about3B active text encoder.

**Quantitative evaluation and conditions (direct source account):** Table2: Lens20-step GenEval.930 and Turbo4-step.914; OneIG EN/ZH are separate columns (.557/.525 for Lens), not two GenEval settings. Protocols include OneIG1,120 prompts, GenEval553 as this paper states and LongText160. Default inference refines prompts with a reasoner, uses20 steps/CFG5, while Turbo4-step uses no CFG. Prompt rewriting and system-prompt search therefore limit comparison with frozen unrewritten prompts. The H100 .84s/3.15s speed reports are primary author measurements, not our replication.

## Lineage, representation and implementation

**Training lineage assessment (agent inference constrained by the cited account):** Against SD1/SDXL: UNKNOWN through FLUX2 initialization. Explicit reuse means a freshly trained Lens denoiser is not a fresh AE.

**Official code and img2img:** Official microsoft/Lens repo5bf0f0cea2f4bc32ebb2b7ed2ef96d5e88b701e0 has a custom pipeline. No Lens native Diffusers class in inspected tree, nor verified source-noise image+strength interface.

Diffusers source inspection pin: `e04f0c5f24392fcd34b32d18d0ce03668f9bcd50` unless this card explicitly names `v0.36.0`. This is source inspection, not installation, import, GPU validation or an amendment of the frozen runtime. Source URLs and hashes appear below. Absence of `strength` means the native interface does not expose the frozen partial-noise corruption; image conditioning alone is insufficient.

| Official model/revision URL | Exact revision | Declared model license | Actual access observation |
|---|---|---|---|
| No verified release revision | UNAVAILABLE | UNVERIFIED | endpoint inaccessible or release not resolved; see limitations |

Licenses in this table concern the named model package; dependency caveats below remain separate. An ungated metadata snapshot does not prove every dependency is ungated. No model weights were downloaded.

## 1024 memory/time and design consequence

§2.5 reports1024 on H100:20 steps3.15s and4-step Turbo.84s. Denoiser floor7.6GB BF16; dequantized GPT-OSS20B on A100 adds about40GB, unlike Hopper MXFP4. Target peak/runtime unknown; reasoner cost is not assumed included.

Any parameter-memory figure is a lower bound or explicitly conditional estimate: decimal GB, two bytes per BF16 parameter, inference only, no optimizer. It excludes activations, attention/KV buffers, extra encoders, CFG duplication, allocator workspace and loading peaks. It is not a measured fit or wall-clock prediction.

**Design implication (agent inference):** Current efficiency lead but no new encoder lineage. Advertised model API401 and empty owner search mean access unavailable, not proof of nonexistence.

**Limits/open assumptions:** Code MIT. Actual model revision/license unverified at inaccessible endpoint. GPU-specific quantization undermines a blanket small-VRAM claim.

No evaluation above measures this thesis’s mark survival, false positives or fixed decision rule. Paper outcomes remain author-reported literature evidence, not development outcomes.

## Inspectable source receipts

| Exact source URL | Local cached text | SHA-256 |
|---|---|---|
| https://arxiv.org/html/2605.21573v1 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-lens-paper.txt | a489c0e453326f60ce67312c753649d1bca1544bb964550edf71876ca55ce414 |
| https://api.github.com/repos/microsoft/Lens/commits/main | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\lens-repo.txt | 5ac184b1a647583921240aec2fdf0672f21faed50a4bd5ac8e6894ea88f67d9a |
| https://huggingface.co/api/models?author=microsoft&search=Lens&limit=30 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\lens-hub-discovery.txt | 4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945 |
| https://github.com/microsoft/Lens/blob/5bf0f0cea2f4bc32ebb2b7ed2ef96d5e88b701e0/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\lens-readme-html.decoded.txt | 49a1095ce4c661c422196ac3fa0a194ca174fda2cee1186c3a7141347dedac4d |
| https://arxiv.org/html/2605.21573v1 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\T2-lens-paper.read.txt | 98da439c2e32e9496a6ce2216f80f88e6a05b450007eec9b25fa673b9294eaf5 |
