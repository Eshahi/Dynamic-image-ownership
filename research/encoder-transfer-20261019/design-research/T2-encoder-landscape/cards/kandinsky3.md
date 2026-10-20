# Kandinsky3 MoVQ detail

Rechecked 2026-10-20 UTC for BRIEF §1b. Evidence: **V2 — primary paper method and evaluation inspected**. Floor count: **NO; supporting variant/encoder, native-card evidence or incomplete evaluation lead**.

## Inspected primary method and evaluation

Locators: §3.4/Table2 MoVQ sizes/training; evaluation; updated2410.21061 §4 architecture and human protocol.

Primary paper: [2312.03511v1](https://arxiv.org/html/2312.03511v1). Cached original SHA-256 `d40b6bf75f86e7119d97e894e4d9e5c618937bb9a1e62fa4490b38c60e6fff08` at `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-kandinsky3-paper.txt`. “V2” is the inspection tier, not the arXiv revision.

**Method evidence (direct source account):** C4/f8 MoVQ; compares67M,102M,270M and selects270M. Updated model combines roughly3B U-Net and8.6B FLAN-UL2 text encoder.

**Quantitative evaluation and conditions (direct source account):** Table2 ImageNet reconstruction270M FID.686/SSIM.741/PSNR27.04, latent32². Do not invent an image resolution absent from the inspected table caption. Updated report uses human comparisons; these are not watermark outcomes.

## Lineage, representation and implementation

**Training lineage assessment (agent inference constrained by the cited account):** Against SD1/SDXL: qualified separate MoVQ training on LAION-HighRes. No fresh family count beyond Kandinsky2/3 grouping. AE is frozen during generator training.

**Official code and img2img:** v0.36.0 kandinsky3/pipeline_kandinsky3_img2img.py provides image+strength; official native1024 model. Quantization path must be fixed from source, not assumed from the term MoVQ.

Diffusers source inspection pin: `e04f0c5f24392fcd34b32d18d0ce03668f9bcd50` unless this card explicitly names `v0.36.0`. This is source inspection, not installation, import, GPU validation or an amendment of the frozen runtime. Source URLs and hashes appear below. Absence of `strength` means the native interface does not expose the frozen partial-noise corruption; image conditioning alone is insufficient.

| Official model/revision URL | Exact revision | Declared model license | Actual access observation |
|---|---|---|---|
| [kandinsky-community/kandinsky-3](https://huggingface.co/kandinsky-community/kandinsky-3/tree/bf79e6c219da8a94abb50235fdc4567eb8fb4632) | bf79e6c219da8a94abb50235fdc4567eb8fb4632 | apache-2.0 | ungated API snapshot |

Licenses in this table concern the named model package; dependency caveats below remain separate. An ungated metadata snapshot does not prove every dependency is ungated. No model weights were downloaded.

## 1024 memory/time and design consequence

Advertised component bytes: text21.739GB, U-Net6.111GB, MoVQ.541GB, total28.391GB. These are disk/weight amounts, not peak; phase offload needed24GB. Primary matched1024 time/peak unknown.

Any parameter-memory figure is a lower bound or explicitly conditional estimate: decimal GB, two bytes per BF16 parameter, inference only, no optimizer. It excludes activations, attention/KV buffers, extra encoders, CFG duplication, allocator workspace and loading peaks. It is not a measured fit or wall-clock prediction.

**Design implication (agent inference):** Best optional full1024 regenerator among documented independent MoVQ variants, subject to timing and explicit proposal approval.

**Limits/open assumptions:** A larger MoVQ model is not automatically independent of earlier MoVQ training; count the family once.

No evaluation above measures this thesis’s mark survival, false positives or fixed decision rule. Paper outcomes remain author-reported literature evidence, not development outcomes.

## Inspectable source receipts

| Exact source URL | Local cached text | SHA-256 |
|---|---|---|
| https://huggingface.co/api/models/kandinsky-community/kandinsky-3?blobs=true | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-kandinsky-community--kandinsky-3-api.txt | b2c4b9353292e03e4db4730ac918b4dd0fb3086081abc7ea2641cf643f0ea13b |
| https://huggingface.co/kandinsky-community/kandinsky-3/resolve/bf79e6c219da8a94abb50235fdc4567eb8fb4632/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-kandinsky-community--kandinsky-3-README.md.txt | b2dc591f2c95099c97f8fd67d41521a8180be696a44297846b49babf23472be7 |
| https://huggingface.co/kandinsky-community/kandinsky-3/resolve/bf79e6c219da8a94abb50235fdc4567eb8fb4632/scheduler/scheduler_config.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-kandinsky-community--kandinsky-3-scheduler--scheduler_config.json.txt | 9e05a641fe4024b17b85cba59f894fc2b5324c148ea31b10c5cb12f3c0cb5471 |
| https://huggingface.co/kandinsky-community/kandinsky-3/resolve/bf79e6c219da8a94abb50235fdc4567eb8fb4632/model_index.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-kandinsky-community--kandinsky-3-model_index.json.txt | 6b437e9e2d1d66fbf9dc99f6871da3705d1ba67591a9298b3b5b4e4ddc050b49 |
| https://arxiv.org/html/2312.03511v1 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-kandinsky3-paper.txt | d40b6bf75f86e7119d97e894e4d9e5c618937bb9a1e62fa4490b38c60e6fff08 |
| https://raw.githubusercontent.com/huggingface/diffusers/v0.36.0/src/diffusers/pipelines/kandinsky3/pipeline_kandinsky3_img2img.py | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-kandinsky3-pipeline-v036.txt | 2ba7126ca5d46809c87cead3fd42043864241dd42940aeb03e742101903cb311 |
| https://arxiv.org/html/2410.21061v1 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\kd3-updated-paper.txt | 9e407574e39ac284186d9b5abd2bff834c02fa04c9da39657c4ec99a0fae62bc |
| https://huggingface.co/kandinsky-community/kandinsky-3/resolve/bf79e6c219da8a94abb50235fdc4567eb8fb4632/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\kandinsky-community--kandinsky-3--README.md.txt | b2dc591f2c95099c97f8fd67d41521a8180be696a44297846b49babf23472be7 |
| https://huggingface.co/kandinsky-community/kandinsky-3/resolve/bf79e6c219da8a94abb50235fdc4567eb8fb4632/model_index.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\kandinsky-community--kandinsky-3--model_index.json.txt | 6b437e9e2d1d66fbf9dc99f6871da3705d1ba67591a9298b3b5b4e4ddc050b49 |
| https://arxiv.org/html/2410.21061v1 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\kd3-updated-paper.read.txt | a99aac8b07646401389e98da2b76aea35838fafa98d5bf445ed994e753ef8f21 |
| https://arxiv.org/html/2312.03511v1 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\T2-kandinsky3-paper.read.txt | 1da367ff5a464c441348a25bac423844148a067ae847f486821c7e79df827e87 |
