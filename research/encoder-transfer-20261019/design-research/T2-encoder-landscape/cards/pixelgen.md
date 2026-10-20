# PixelGen

Rechecked 2026-10-20 UTC for BRIEF §1b. Evidence: **V2 — primary paper method and evaluation inspected**. Floor count: **YES; one distinct family in the conservative floor**.

## Inspected primary method and evaluation

Locators: §3.1–3.4 pixel prediction/perceptual losses; ImageNet/T2I evaluations; official PixelAE/config/actual sampler.

Primary paper: [2602.02493v1](https://arxiv.org/html/2602.02493v1). Cached original SHA-256 `3f9e6de030cf7982515d06c6f52363fd9fd51f8cdcd0a46ce76670009ef099cc` at `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\pixelgen-paper.txt`. “V2” is the inspection tier, not the arXiv revision.

**Method evidence (direct source account):** RGB C=3/f=1 with affine identity PixelAE: encode x/scale+shift, inverse decode. Clean-image prediction converts to flow. LPIPS, perceptual DINO and REPA losses train the model; no compression AE.

**Quantitative evaluation and conditions (direct source account):** ImageNet256,80 epochs without CFG: FID5.11;160 epochs with CFG and50 Heun steps: FID1.83. T2I5121.1B GenEval.79. Paper title “Pixel Diffusion Beats Latent Diffusion with Perceptual Loss” differs from repository “Improving Pixel Diffusion with Perceptual Loss”; retain version distinction.

## Lineage, representation and implementation

**Training lineage assessment (agent inference constrained by the cited account):** Against SD1/SDXL: NOT APPLICABLE, no AE. Training perceptual networks are not inference compressors.

**Official code and img2img:** Official repo7b94115d6f14d1c4ce0fe7a17a06351934ef2d4a: T2I config uses adam_sampling.AdamLMSamplerJiT and PixelAE. Sampler starts from noise; no verified image+strength adapter. Generic sampling.py is not the configured sampler. No official native Diffusers support verified.

Diffusers source inspection pin: `e04f0c5f24392fcd34b32d18d0ce03668f9bcd50` unless this card explicitly names `v0.36.0`. This is source inspection, not installation, import, GPU validation or an amendment of the frozen runtime. Source URLs and hashes appear below. Absence of `strength` means the native interface does not expose the frozen partial-noise corruption; image conditioning alone is insufficient.

| Official model/revision URL | Exact revision | Declared model license | Actual access observation |
|---|---|---|---|
| [zehongma/PixelGen](https://huggingface.co/zehongma/PixelGen/tree/3e55c85aa4b78bc576d4370fa5daaa2770081d4d) | 3e55c85aa4b78bc576d4370fa5daaa2770081d4d | apache-2.0 | ungated API snapshot |

Licenses in this table concern the named model package; dependency caveats below remain separate. An ungated metadata snapshot does not prove every dependency is ungated. No model weights were downloaded.

## 1024 memory/time and design consequence

ImageNet676M model floor1.352GB BF16; T2I1.1B floor2.2GB plus text/activations. Native T2I512; no1024 peak/time. Token/attention scaling is not captured by parameter memory.

Any parameter-memory figure is a lower bound or explicitly conditional estimate: decimal GB, two bytes per BF16 parameter, inference only, no optimizer. It excludes activations, attention/KV buffers, extra encoders, CFG duplication, allocator workspace and loading peaks. It is not a measured fit or wall-clock prediction.

**Design implication (agent inference):** Modern pixel-method evidence and lower model size, but native512 and code-license gap put it behind HiDream-O1 for P7.

**Limits/open assumptions:** Official HF weights Apache2 and ungated. Repository tree lacks LICENSE; do not infer code permission from weight terms. Community Diffusers mirror is not official support.

No evaluation above measures this thesis’s mark survival, false positives or fixed decision rule. Paper outcomes remain author-reported literature evidence, not development outcomes.

## Inspectable source receipts

| Exact source URL | Local cached text | SHA-256 |
|---|---|---|
| https://arxiv.org/html/2602.02493v1 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\pixelgen-paper.txt | 3f9e6de030cf7982515d06c6f52363fd9fd51f8cdcd0a46ce76670009ef099cc |
| https://api.github.com/repos/Zehong-Ma/PixelGen/git/trees/7b94115d6f14d1c4ce0fe7a17a06351934ef2d4a?recursive=1 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\pixelgen-repo-tree.txt | c80588fa16f3b28d880f9cf0c303ec60b5788f1fc96d30a4146386123b76b6d1 |
| https://huggingface.co/api/models/zehongma/PixelGen?blobs=true | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\pixelgen-api.txt | 5916dcfa44c794dc70c11ecb57bd76608d1e22a50febf17d8368d2dc40c05310 |
| https://huggingface.co/zehongma/PixelGen/resolve/3e55c85aa4b78bc576d4370fa5daaa2770081d4d/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\pixelgen-card.txt | 4bcf87ecfbbb8e07a01b21415a970c8b53a5283bf6872b657040d3f45c9241f7 |
| https://github.com/Zehong-Ma/PixelGen/blob/7b94115d6f14d1c4ce0fe7a17a06351934ef2d4a/src/models/autoencoder/pixel.py | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\pixelgen-ae.decoded.txt | ef68aaa0aaabd09007d9610a0d75d8621b494352099dde43d2f4f43a8f3eb524 |
| https://github.com/Zehong-Ma/PixelGen/blob/7b94115d6f14d1c4ce0fe7a17a06351934ef2d4a/src/diffusion/flow_matching/adam_sampling.py | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\pixelgen-adam-sampler.decoded.txt | 473aaa8291e31eed8ff5e9b876662d5c6a0fa39ac886fddcdc8ecab3203ea850 |
| https://github.com/Zehong-Ma/PixelGen/blob/7b94115d6f14d1c4ce0fe7a17a06351934ef2d4a/configs_t2i/sft_res512.yaml | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\pixelgen-config-html.decoded.txt | a29e91d33a241585138bcd33fac63e3dd74cf43dd71a68643d09249b569e5ba6 |
| https://arxiv.org/html/2602.02493v1 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\pixelgen-paper.read.txt | e157273844b9662266db495043e0144a11ba7bd5539410d21b1b21a4d7787d87 |
