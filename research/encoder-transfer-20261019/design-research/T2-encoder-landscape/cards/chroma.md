# Chroma1-HD / Radiance leads

Rechecked 2026-10-20 UTC for BRIEF §1b. Evidence: **NATIVE PRIMARY MODEL/CODE — explicitly not paper V2**. Floor count: **NO; supporting variant/encoder, native-card evidence or incomplete evaluation lead**.

## Inspected primary method and evaluation

Locators: Official cards/config/LFS metadata; Chroma native img2img source.

**Method evidence (direct source account):** HD8.9B derived from FLUX1-schnell, VAE C16/f8 with same advertised FLUX object. Radiance card is a short WIP pixel-model announcement; architecture was not sufficiently documented to assert an exact bottleneck.

**Quantitative evaluation and conditions (direct source account):** No sufficiently specified quantitative evaluation in inspected native cards. Radiance describes hourly checkpoints/history replacement; this is not stable evaluated release evidence.

## Lineage, representation and implementation

**Training lineage assessment (agent inference constrained by the cited account):** HD againstSD1/SDXL UNKNOWN throughFLUX; no new encoder. Radiance no verified ancestry conclusion.

**Official code and img2img:** chroma/pipeline_chroma_img2img.py supports HD image+strength. Radiance native source-noise support not established by its short card.

Diffusers source inspection pin: `e04f0c5f24392fcd34b32d18d0ce03668f9bcd50` unless this card explicitly names `v0.36.0`. This is source inspection, not installation, import, GPU validation or an amendment of the frozen runtime. Source URLs and hashes appear below. Absence of `strength` means the native interface does not expose the frozen partial-noise corruption; image conditioning alone is insufficient.

| Official model/revision URL | Exact revision | Declared model license | Actual access observation |
|---|---|---|---|
| [lodestones/Chroma1-HD](https://huggingface.co/lodestones/Chroma1-HD/tree/0e0c60ece1e82b17cb7f77342d765ba5024c40c0) | 0e0c60ece1e82b17cb7f77342d765ba5024c40c0 | apache-2.0 | ungated API snapshot |
| [lodestones/Chroma1-Radiance](https://huggingface.co/lodestones/Chroma1-Radiance/tree/a696c3104a7215de599c72bff72d32a96fb53914) | a696c3104a7215de599c72bff72d32a96fb53914 | apache-2.0 | ungated API snapshot |

Licenses in this table concern the named model package; dependency caveats below remain separate. An ungated metadata snapshot does not prove every dependency is ungated. No model weights were downloaded.

## 1024 memory/time and design consequence

HD denoiser≥17.8GB BF16 plus text/VAE/activations; no primary matched1024 peak/time. Radiance footprint/runtime unknown.

Any parameter-memory figure is a lower bound or explicitly conditional estimate: decimal GB, two bytes per BF16 parameter, inference only, no optimizer. It excludes activations, attention/KV buffers, extra encoders, CFG duplication, allocator workspace and loading peaks. It is not a measured fit or wall-clock prediction.

**Design implication (agent inference):** Record current leads without counting them as evaluated families or independent encoders.

**Limits/open assumptions:** Apache ungated metadata. WIP announcement does not establish production or experiment readiness.

No evaluation above measures this thesis’s mark survival, false positives or fixed decision rule. Paper outcomes remain author-reported literature evidence, not development outcomes.

## Inspectable source receipts

| Exact source URL | Local cached text | SHA-256 |
|---|---|---|
| https://huggingface.co/api/models/lodestones/Chroma1-HD?blobs=true | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-lodestones--Chroma1-HD-api.txt | ce4dab89114fe6a9980c137cf66387d2ea096e1d9de30e6297886e1fdfa4a216 |
| https://huggingface.co/lodestones/Chroma1-HD/resolve/0e0c60ece1e82b17cb7f77342d765ba5024c40c0/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-lodestones--Chroma1-HD-README.md.txt | 7fb4b45c76fd5e2028d540dd76b59491eb547edd6271f88769a513c4ac1336be |
| https://huggingface.co/lodestones/Chroma1-HD/resolve/0e0c60ece1e82b17cb7f77342d765ba5024c40c0/vae/config.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-lodestones--Chroma1-HD-vae--config.json.txt | e423b4a9e49572574de14faf263494416bc757e1bdd62645cfade7284a912565 |
| https://huggingface.co/lodestones/Chroma1-HD/resolve/0e0c60ece1e82b17cb7f77342d765ba5024c40c0/scheduler/scheduler_config.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-lodestones--Chroma1-HD-scheduler--scheduler_config.json.txt | 5420bd572b9a520774c50d79a8bb511f73bf58e691c2a38e4763435625cea197 |
| https://huggingface.co/lodestones/Chroma1-HD/resolve/0e0c60ece1e82b17cb7f77342d765ba5024c40c0/model_index.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-lodestones--Chroma1-HD-model_index.json.txt | cf83237e214327ef542d8b139cade5537fb44b8eb3aa33911ad6a5f8b4356202 |
| https://huggingface.co/api/models/lodestones/Chroma1-Radiance?blobs=true | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-lodestones--Chroma1-Radiance-api.txt | 8c337b7c7403e90283179e9603f7adee47e520aed583d6681bfd5fc853605039 |
| https://huggingface.co/lodestones/Chroma1-Radiance/resolve/a696c3104a7215de599c72bff72d32a96fb53914/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-lodestones--Chroma1-Radiance-README.md.txt | d278779c5fe7b0e1860dd3b78d64c3a2abcbd454c8beae0877963c7bb6469da0 |
| https://huggingface.co/lodestones/Chroma1-Radiance/resolve/a696c3104a7215de599c72bff72d32a96fb53914/config_radiance.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-lodestones--Chroma1-Radiance-config_radiance.json.txt | a69d9a4e01ad49f2bb39c2e5dfb313cda2da14ad5438d557ddb80e12d6b79573 |
| https://huggingface.co/lodestones/Chroma1-HD/resolve/0e0c60ece1e82b17cb7f77342d765ba5024c40c0/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\lodestones--Chroma1-HD--README.md.txt | 7fb4b45c76fd5e2028d540dd76b59491eb547edd6271f88769a513c4ac1336be |
| https://huggingface.co/lodestones/Chroma1-HD/resolve/0e0c60ece1e82b17cb7f77342d765ba5024c40c0/vae/config.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\lodestones--Chroma1-HD--vae--config.json.txt | e423b4a9e49572574de14faf263494416bc757e1bdd62645cfade7284a912565 |
| https://huggingface.co/lodestones/Chroma1-HD/resolve/0e0c60ece1e82b17cb7f77342d765ba5024c40c0/model_index.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\lodestones--Chroma1-HD--model_index.json.txt | cf83237e214327ef542d8b139cade5537fb44b8eb3aa33911ad6a5f8b4356202 |
| https://huggingface.co/lodestones/Chroma1-Radiance/resolve/a696c3104a7215de599c72bff72d32a96fb53914/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\lodestones--Chroma1-Radiance--README.md.txt | d278779c5fe7b0e1860dd3b78d64c3a2abcbd454c8beae0877963c7bb6469da0 |
| https://api.github.com/repos/huggingface/diffusers/contents/src/diffusers/pipelines/chroma/pipeline_chroma_img2img.py?ref=e04f0c5f24392fcd34b32d18d0ce03668f9bcd50 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\code-chroma--pipeline_chroma_img2img.py-api.txt | a82c778ccea3759efb5b79c5d25cb2dd61dce4f0b27c82e3825521f8040b551e |
| https://api.github.com/repos/huggingface/diffusers/contents/src/diffusers/pipelines/chroma/pipeline_chroma_img2img.py?ref=e04f0c5f24392fcd34b32d18d0ce03668f9bcd50 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\code-chroma--pipeline_chroma_img2img.py-api.decoded.txt | af14d8c4ce8e0527b0d1f755f826edbe1081994709624416a3a6c334d19db9d2 |
