# PRX Pixel native1024 candidate

Rechecked 2026-10-20 UTC for BRIEF §1b. Evidence: **NATIVE PRIMARY MODEL/CODE — explicitly not paper V2**. Floor count: **NO; supporting variant/encoder, native-card evidence or incomplete evaluation lead**.

## Inspected primary method and evaluation

Locators: Official modelcard architecture/usage; native prx pipeline signature and pixel noise path.

**Method evidence (direct source account):** 7B pixel transformer, rawRGB C3/f1 and no VAE; Qwen3-VL text conditioning, FlowMatchEuler,28-step example at1024.

**Quantitative evaluation and conditions (direct source account):** Card lacks a reproducible quantitative comparison protocol. Therefore nonqualifying for18-paper floor, despite useful official architecture/code evidence.

## Lineage, representation and implementation

**Training lineage assessment (agent inference constrained by the cited account):** AgainstSD1/SDXL NOT APPLICABLE, no AE. Pixel denoising still may remove marks.

**Official code and img2img:** prx/pipeline_prx_pixel.py exists at pinned current Diffusers main, despite card saying branch support; no image/strength. DefaultCFG4 in source versus5 in card is a configuration discrepancy. Requires a new pixel-noise adapter for SDEdit.

Diffusers source inspection pin: `e04f0c5f24392fcd34b32d18d0ce03668f9bcd50` unless this card explicitly names `v0.36.0`. This is source inspection, not installation, import, GPU validation or an amendment of the frozen runtime. Source URLs and hashes appear below. Absence of `strength` means the native interface does not expose the frozen partial-noise corruption; image conditioning alone is insufficient.

| Official model/revision URL | Exact revision | Declared model license | Actual access observation |
|---|---|---|---|
| [Photoroom/prxpixel-t2i](https://huggingface.co/Photoroom/prxpixel-t2i/tree/bcd5e63f072257a220c5d0ba039c97657398b1c2) | bcd5e63f072257a220c5d0ba039c97657398b1c2 | apache-2.0 | ungated API snapshot |

Licenses in this table concern the named model package; dependency caveats below remain separate. An ungated metadata snapshot does not prove every dependency is ungated. No model weights were downloaded.

## 1024 memory/time and design consequence

Nominal7B denoiser≥14GB BF16 plus text/activations. No primary1024 batch-one peak/time found;24GB fit is unproved. Native1024 usage is clearer than current O1 source, which snaps to2048.

Any parameter-memory figure is a lower bound or explicitly conditional estimate: decimal GB, two bytes per BF16 parameter, inference only, no optimizer. It excludes activations, attention/KV buffers, extra encoders, CFG duplication, allocator workspace and loading peaks. It is not a measured fit or wall-clock prediction.

**Design implication (agent inference):** Retain as direct1024-interface P7 candidate; O1 leads substantive high-resolution pixel-method evidence. Neither is a frozen regenerator, and no adapter was implemented.

**Limits/open assumptions:** Apache ungated model metadata; dependency access must be checked for the exact execution package. Current code support does not imply compatibility with frozen v0.35.1.

No evaluation above measures this thesis’s mark survival, false positives or fixed decision rule. Paper outcomes remain author-reported literature evidence, not development outcomes.

## Inspectable source receipts

| Exact source URL | Local cached text | SHA-256 |
|---|---|---|
| https://huggingface.co/api/models/Photoroom/prxpixel-t2i?blobs=true | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-Photoroom--prxpixel-t2i-api.txt | 9aadd78d2b36480467432ae544f27a812cfcdbeee1a9c03316239ae62e5809fb |
| https://huggingface.co/api/models/Photoroom/prxpixel-t2i?blobs=true | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\prxpixel-api.txt | a052125d1e350f536c3d4ac36d1e2776e69aad38d109a27f62f44b7e553e7a56 |
| https://huggingface.co/Photoroom/prxpixel-t2i/resolve/bcd5e63f072257a220c5d0ba039c97657398b1c2/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\Photoroom--prxpixel-t2i--README.md.txt | 5927993eb67687cac7aa49dce378c78a656541d1fea4f7f3c94d4a1537396b79 |
| https://huggingface.co/Photoroom/prxpixel-t2i/resolve/bcd5e63f072257a220c5d0ba039c97657398b1c2/model_index.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\Photoroom--prxpixel-t2i--model_index.json.txt | dd47645ed10c9be2c082cf80dff4a7f0763828fd26013025f4316f2db61a5060 |
| https://api.github.com/repos/huggingface/diffusers/contents/src/diffusers/pipelines/prx/pipeline_prx_pixel.py?ref=e04f0c5f24392fcd34b32d18d0ce03668f9bcd50 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\code-prx--pipeline_prx_pixel.py-api.txt | 3b8bda6edb080523f95f0ec5684f586325025391e695a9bfc44a3abbd681fc34 |
| https://api.github.com/repos/huggingface/diffusers/contents/src/diffusers/pipelines/prx/pipeline_prx_pixel.py?ref=e04f0c5f24392fcd34b32d18d0ce03668f9bcd50 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\code-prx--pipeline_prx_pixel.py-api.decoded.txt | 4273257cedc89335dd2a2762fff06122d659f8a44342c6d4f36fd7a1dc707591 |
