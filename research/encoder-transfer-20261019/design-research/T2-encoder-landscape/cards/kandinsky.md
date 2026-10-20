# Kandinsky 2.x / MoVQ (3.x/5.x grouped)

Rechecked 2026-10-20 UTC for BRIEF §1b. Evidence: **V2 — primary paper method and evaluation inspected**. Floor count: **YES; one distinct family in the conservative floor**.

## Inspected primary method and evaluation

Locators: §4 components/MoVQ; §5 quantitative/human evaluation; MoVQ configs; KD2.2 encode/decode.

Primary paper: [2310.03502v1](https://arxiv.org/html/2310.03502v1). Cached original SHA-256 `c5a5071a5212155cc6af1d82fe3dad4d002a942e36f964eb7b0be3830ceba72d` at `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-kandinsky-paper.txt`. “V2” is the inspection tier, not the arXiv revision.

**Method evidence (direct source account):** Image-embedding prior, diffusion decoder and MoVQ,C=4/f=8. Kandinsky3 enlarges MoVQ; Kandinsky5 images use FLUX.1-dev VAE, so the brand is not a persistent encoder lineage.

**Quantitative evaluation and conditions (direct source account):** §5 COCO30K256: linear-prior FID8.03; diffusion-prior quantized9.86 versus unquantized9.87. Human DrawBench5,000 votes. These are generation, not native1024 regeneration/watermark metrics.

## Lineage, representation and implementation

**Training lineage assessment (agent inference constrained by the cited account):** vs SD1/SDXL: documented separate MoVQ training, qualified YES. Sber-trained MoVQ on LAION-HighRes67M is training evidence, not an inference from different names or datasets. Initialization is less explicit than SDXL.

**Official code and img2img:** Pinned v0.36.0 kandinsky2_2/pipeline_kandinsky2_2_img2img.py and models/autoencoders/vq_model.py: native image+strength; KD2.2 decode can bypass nearest-codebook quantization with force_not_quantize=True. Paper quantization ablations are not automatically the runtime path.

Diffusers source inspection pin: `e04f0c5f24392fcd34b32d18d0ce03668f9bcd50` unless this card explicitly names `v0.36.0`. This is source inspection, not installation, import, GPU validation or an amendment of the frozen runtime. Source URLs and hashes appear below. Absence of `strength` means the native interface does not expose the frozen partial-noise corruption; image conditioning alone is insufficient.

| Official model/revision URL | Exact revision | Declared model license | Actual access observation |
|---|---|---|---|
| [kandinsky-community/kandinsky-2-2-decoder](https://huggingface.co/kandinsky-community/kandinsky-2-2-decoder/tree/9ae140d347fed8ce6e8bb3005dcc1f48543bb8e3) | 9ae140d347fed8ce6e8bb3005dcc1f48543bb8e3 | apache-2.0 | ungated API snapshot |
| [kandinsky-community/kandinsky-2-2-prior](https://huggingface.co/kandinsky-community/kandinsky-2-2-prior/tree/9fc51ad5732afc5d031724219d22e6c42179c5a8) | 9fc51ad5732afc5d031724219d22e6c42179c5a8 | apache-2.0 | ungated API snapshot |
| [kandinsky-community/kandinsky-3](https://huggingface.co/kandinsky-community/kandinsky-3/tree/bf79e6c219da8a94abb50235fdc4567eb8fb4632) | bf79e6c219da8a94abb50235fdc4567eb8fb4632 | apache-2.0 | ungated API snapshot |

Licenses in this table concern the named model package; dependency caveats below remain separate. An ungated metadata snapshot does not prove every dependency is ungated. No model weights were downloaded.

## 1024 memory/time and design consequence

KD2.2 decoder package≈5.284GB plus prior≈10.574GB on disk, not peakVRAM. KD3 components total28.391GB (text21.739,U-Net6.111,MoVQ.541); phased offload needed on24GB. Matched1024 peak/runtime unknown.

Any parameter-memory figure is a lower bound or explicitly conditional estimate: decimal GB, two bytes per BF16 parameter, inference only, no optimizer. It excludes activations, attention/KV buffers, extra encoders, CFG duplication, allocator workspace and loading peaks. It is not a measured fit or wall-clock prediction.

**Design implication (agent inference):** Highest-priority additional convolutional encoder: native strength API, permissive ungated packages, documented MoVQ training. AE-only diagnostic cheaper than full prior+decoder regeneration.

**Limits/open assumptions:** KD2.2 native resolution lower than1024; KD3 better1024 proposal. Fix quantization mode explicitly. Independence conclusion does not extend toKandinsky5.

No evaluation above measures this thesis’s mark survival, false positives or fixed decision rule. Paper outcomes remain author-reported literature evidence, not development outcomes.

## Inspectable source receipts

| Exact source URL | Local cached text | SHA-256 |
|---|---|---|
| https://huggingface.co/api/models/kandinsky-community/kandinsky-2-2-decoder?blobs=true | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-kandinsky-community--kandinsky-2-2-decoder-api.json | 2fdf28e61979b6ac146b13716ef2f44ffef81fa01105fa6bffff058dff1559c3 |
| https://huggingface.co/kandinsky-community/kandinsky-2-2-decoder/resolve/9ae140d347fed8ce6e8bb3005dcc1f48543bb8e3/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-kandinsky-community--kandinsky-2-2-decoder-README.md | 23e958a88dabb1a9bb6dc525eabcee038311b7a9f21fe6f0eda96af511a61917 |
| https://huggingface.co/kandinsky-community/kandinsky-2-2-decoder/resolve/9ae140d347fed8ce6e8bb3005dcc1f48543bb8e3/movq/config.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-kandinsky-community--kandinsky-2-2-decoder-movq--config.json | b7448f3ea8aecf233629b20c1f606887e22244656edcee1be6a419079717a23e |
| https://huggingface.co/kandinsky-community/kandinsky-2-2-decoder/resolve/9ae140d347fed8ce6e8bb3005dcc1f48543bb8e3/model_index.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-kandinsky-community--kandinsky-2-2-decoder-model_index.json | 5cde694d9f2a436adcdf0874c7f2b863d03bfcf54dbaf98926d2ef55bfe32918 |
| https://huggingface.co/api/models/kandinsky-community/kandinsky-2-2-prior?blobs=true | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-kandinsky-community--kandinsky-2-2-prior-api.json | d114da551dfb0f0ed4934d429958fd7a6f1eab1c664ca0a3599d40a0d6e89e63 |
| https://huggingface.co/kandinsky-community/kandinsky-2-2-prior/resolve/9fc51ad5732afc5d031724219d22e6c42179c5a8/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-kandinsky-community--kandinsky-2-2-prior-README.md | bba4898931a219c1d2f2f832bb8050e205a94ec781e7ebee55eb96c89add286d |
| https://huggingface.co/kandinsky-community/kandinsky-2-2-prior/resolve/9fc51ad5732afc5d031724219d22e6c42179c5a8/model_index.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-kandinsky-community--kandinsky-2-2-prior-model_index.json | 26cba76e560b6da612d65b8e7beac9be04442df8df2e1743b8466454988d1f5e |
| https://arxiv.org/html/2310.03502v1 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-kandinsky-paper.txt | c5a5071a5212155cc6af1d82fe3dad4d002a942e36f964eb7b0be3830ceba72d |
| https://raw.githubusercontent.com/huggingface/diffusers/v0.36.0/src/diffusers/pipelines/kandinsky2_2/pipeline_kandinsky2_2_img2img.py | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-kandinsky-pipeline-v036.txt | f5b968f05494823e12c1530b24ae18b4d3696e986535e26c3458d970af39afaa |
| https://huggingface.co/api/models/kandinsky-community/kandinsky-3?blobs=true | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-kandinsky-community--kandinsky-3-api.txt | b2c4b9353292e03e4db4730ac918b4dd0fb3086081abc7ea2641cf643f0ea13b |
| https://huggingface.co/kandinsky-community/kandinsky-3/resolve/bf79e6c219da8a94abb50235fdc4567eb8fb4632/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-kandinsky-community--kandinsky-3-README.md.txt | b2dc591f2c95099c97f8fd67d41521a8180be696a44297846b49babf23472be7 |
| https://huggingface.co/kandinsky-community/kandinsky-3/resolve/bf79e6c219da8a94abb50235fdc4567eb8fb4632/scheduler/scheduler_config.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-kandinsky-community--kandinsky-3-scheduler--scheduler_config.json.txt | 9e05a641fe4024b17b85cba59f894fc2b5324c148ea31b10c5cb12f3c0cb5471 |
| https://huggingface.co/kandinsky-community/kandinsky-3/resolve/bf79e6c219da8a94abb50235fdc4567eb8fb4632/model_index.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-kandinsky-community--kandinsky-3-model_index.json.txt | 6b437e9e2d1d66fbf9dc99f6871da3705d1ba67591a9298b3b5b4e4ddc050b49 |
| https://raw.githubusercontent.com/huggingface/diffusers/v0.36.0/src/diffusers/models/autoencoders/vq_model.py | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-vq-model-v036.txt | 74276357e1d327324323880d393b5d54a1f6004e9a9ce35e1289adf575b6cb1a |
| https://huggingface.co/kandinsky-community/kandinsky-2-2-decoder/resolve/9ae140d347fed8ce6e8bb3005dcc1f48543bb8e3/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\kandinsky-community--kandinsky-2-2-decoder--README.md.txt | 23e958a88dabb1a9bb6dc525eabcee038311b7a9f21fe6f0eda96af511a61917 |
| https://huggingface.co/kandinsky-community/kandinsky-2-2-decoder/resolve/9ae140d347fed8ce6e8bb3005dcc1f48543bb8e3/model_index.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\kandinsky-community--kandinsky-2-2-decoder--model_index.json.txt | 5cde694d9f2a436adcdf0874c7f2b863d03bfcf54dbaf98926d2ef55bfe32918 |
| https://huggingface.co/kandinsky-community/kandinsky-2-2-prior/resolve/9fc51ad5732afc5d031724219d22e6c42179c5a8/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\kandinsky-community--kandinsky-2-2-prior--README.md.txt | bba4898931a219c1d2f2f832bb8050e205a94ec781e7ebee55eb96c89add286d |
| https://huggingface.co/kandinsky-community/kandinsky-2-2-prior/resolve/9fc51ad5732afc5d031724219d22e6c42179c5a8/model_index.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\kandinsky-community--kandinsky-2-2-prior--model_index.json.txt | 26cba76e560b6da612d65b8e7beac9be04442df8df2e1743b8466454988d1f5e |
| https://huggingface.co/kandinsky-community/kandinsky-3/resolve/bf79e6c219da8a94abb50235fdc4567eb8fb4632/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\kandinsky-community--kandinsky-3--README.md.txt | b2dc591f2c95099c97f8fd67d41521a8180be696a44297846b49babf23472be7 |
| https://huggingface.co/kandinsky-community/kandinsky-3/resolve/bf79e6c219da8a94abb50235fdc4567eb8fb4632/model_index.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\kandinsky-community--kandinsky-3--model_index.json.txt | 6b437e9e2d1d66fbf9dc99f6871da3705d1ba67591a9298b3b5b4e4ddc050b49 |
| https://arxiv.org/html/2310.03502v1 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\T2-kandinsky-paper.read.txt | b690193e3511e4f83681408f51c7110cd627f765b3f5b8f6882e89e030011e5d |
