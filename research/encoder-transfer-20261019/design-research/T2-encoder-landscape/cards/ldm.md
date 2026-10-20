# Latent Diffusion / Stable Diffusion 1.x–2.x

Rechecked 2026-10-20 UTC for BRIEF §1b. Evidence: **V2 — primary paper method and evaluation inspected**. Floor count: **YES; one distinct family in the conservative floor**.

## Inspected primary method and evaluation

Locators: §3.1 perceptual compression; §3.2 latent diffusion; §4.1/Fig.7 compression evaluation; official sd-vae-ft-mse Training/Evaluation; SD1.5 VAE config.

Primary paper: [2112.10752v2](https://arxiv.org/html/2112.10752v2). Cached original SHA-256 `bc27be0c28b03fbd9e444e31224035d38d3f6622c59e45e49ef37ed927dcd5ea` at `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-ldm-paper.txt`. “V2” is the inspection tier, not the arXiv revision.

**Method evidence (direct source account):** KL-regularized convolutional perceptual autoencoder with adversarial/perceptual reconstruction; latent C=4, spatial f=8 in SD1.5 (1024→128²×4). Cross-attention U-Net diffusion. LDM also studies VQ and other compression factors; these are not all SD1.5 configurations.

**Quantitative evaluation and conditions (direct source account):** Fig.7 compares f=1,2,4,8,16,32, 5K samples,500K CelebA-HQ or2M ImageNet updates, A100 and DDIM step sweeps; f4/8 balances speed and quality. Official decoder-ft card: COCO2017-val5K at256, original PSNR23.4±3.8dB/SSIM.69/rFID4.99 versus ft-MSE24.5±3.7/.71/4.70. Its PSIM column is not our LPIPS assessor.

## Lineage, representation and implementation

**Training lineage assessment (agent inference constrained by the cited account):** vs SD1: SAME anchor. vs SDXL: DISTINCT because SDXL explicitly retrains its AE from scratch. SD2 is not evidence of a fresh encoder: official ft-EMA/ft-MSE describes decoder-only fine-tuning, and SDXL §2.4 identifies the SD2 decoder change. Exact identity of every SD2 release is not established by this family description.

**Official code and img2img:** stable_diffusion/pipeline_stable_diffusion_img2img.py: get_timesteps, prepare_latents, __call__; native image+strength, floor(N×strength), encode then scheduler noise; VAE scaling. SD1.5 DDIM identity remains the anchor.

Diffusers source inspection pin: `e04f0c5f24392fcd34b32d18d0ce03668f9bcd50` unless this card explicitly names `v0.36.0`. This is source inspection, not installation, import, GPU validation or an amendment of the frozen runtime. Source URLs and hashes appear below. Absence of `strength` means the native interface does not expose the frozen partial-noise corruption; image conditioning alone is insufficient.

| Official model/revision URL | Exact revision | Declared model license | Actual access observation |
|---|---|---|---|
| [stable-diffusion-v1-5/stable-diffusion-v1-5](https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5/tree/451f4fe16113bff5a5d2269ed5ad43b0592e9a14) | 451f4fe16113bff5a5d2269ed5ad43b0592e9a14 | creativeml-openrail-m | ungated API snapshot |
| [CompVis/stable-diffusion-v1-4](https://huggingface.co/CompVis/stable-diffusion-v1-4/tree/133a221b8aa7292a167afc5127cb63fb5005638b) | 133a221b8aa7292a167afc5127cb63fb5005638b | creativeml-openrail-m | ungated API snapshot |
| [stabilityai/sd-vae-ft-mse](https://huggingface.co/stabilityai/sd-vae-ft-mse/tree/31f26fdeee1355a5c34592e401dd41e45d25a493) | 31f26fdeee1355a5c34592e401dd41e45d25a493 | mit | ungated API snapshot |

Licenses in this table concern the named model package; dependency caveats below remain separate. An ungated metadata snapshot does not prove every dependency is ungated. No model weights were downloaded.

## 1024 memory/time and design consequence

No primary 1024 batch-one peak/time found. SD1.5 ≈0.86B U-Net implies ≈1.72 GB BF16 parameters alone (2 bytes/parameter); CLIP, VAE, activations, CFG and allocator add memory. Native training was512, so1024 is an extrapolation, not equivalent native-resolution quality. Frozen runtime remains unmeasured.

Any parameter-memory figure is a lower bound or explicitly conditional estimate: decimal GB, two bytes per BF16 parameter, inference only, no optimizer. It excludes activations, attention/KV buffers, extra encoders, CFG duplication, allocator workspace and loading peaks. It is not a measured fit or wall-clock prediction.

**Design implication (agent inference):** Retain SD1.5; do not count SD2.1 as independent-encoder transfer. The relevant mechanism is encoder initialization, not decoder fine-tuning or changed text encoders.

**Limits/open assumptions:** Generation/reconstruction metrics do not evaluate watermark survival. Official SD2 metadata endpoint was inaccessible; no new SD2 revision or gate status is invented.

No evaluation above measures this thesis’s mark survival, false positives or fixed decision rule. Paper outcomes remain author-reported literature evidence, not development outcomes.

## Inspectable source receipts

| Exact source URL | Local cached text | SHA-256 |
|---|---|---|
| https://arxiv.org/html/2112.10752v2 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-ldm-paper.txt | bc27be0c28b03fbd9e444e31224035d38d3f6622c59e45e49ef37ed927dcd5ea |
| https://huggingface.co/api/models/CompVis/stable-diffusion-v1-4?blobs=true | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\sd14-api.txt | d722b1db8aa70260cd73948e8284c65ce3fb82900217716b10b2d7a6c004deaf |
| https://huggingface.co/api/models/stabilityai/sd-vae-ft-mse?blobs=true | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\sd-vae-mse-api.txt | 3ed58c8267ef15dfa7ed930f36dab0ea62f812511e6cc8417fc64471eb38f30a |
| https://api.github.com/repos/huggingface/diffusers/contents/src/diffusers/pipelines/stable_diffusion/pipeline_stable_diffusion_img2img.py?ref=e04f0c5f24392fcd34b32d18d0ce03668f9bcd50 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\code-stable_diffusion--pipeline_stable_diffusion_img2img.py-api.txt | 9b26f9e5ce9e818e833a6e2043cd6c4c2b3b485dfc9678119046e344b9bc3d14 |
| https://huggingface.co/CompVis/stable-diffusion-v1-4/resolve/133a221b8aa7292a167afc5127cb63fb5005638b/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\sd14-card.txt | 4eb72f9e6bdbfcf359ad66cdd7e26984449f47692069f81205f2217c9a821ba2 |
| https://huggingface.co/stabilityai/sd-vae-ft-mse/resolve/31f26fdeee1355a5c34592e401dd41e45d25a493/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\sd-vae-mse-card.txt | 8ac69483c18a45d0fee531e08b6ede97ee9b4c79e875659c1b0e6a5903ca3400 |
| https://api.github.com/repos/huggingface/diffusers/contents/src/diffusers/pipelines/stable_diffusion/pipeline_stable_diffusion_img2img.py?ref=e04f0c5f24392fcd34b32d18d0ce03668f9bcd50 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\code-stable_diffusion--pipeline_stable_diffusion_img2img.py-api.decoded.txt | 240baf929b2fcb2422a2cdc553ff388600fa390f3892c90e4aee492ff5080d93 |
| https://huggingface.co/api/models/stable-diffusion-v1-5/stable-diffusion-v1-5?blobs=true | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\sd15-api.txt | 54c44f8db561f88591def735264ce3521d907edc42aef2a2db4fa97c743e1c7d |
| https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5/resolve/451f4fe16113bff5a5d2269ed5ad43b0592e9a14/vae/config.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\sd15-config.txt | 786a7d21647ddea6a04b9675c03d3cb45e90a2f3c6da5fbda2c54ade040036de |
| https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5/resolve/451f4fe16113bff5a5d2269ed5ad43b0592e9a14/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\sd15-card.txt | 2079161f9df7524bd9eca5e53ff5911271b8551e0f868b7b5a92b84776df28a3 |
| https://arxiv.org/html/2112.10752v2 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\T2-ldm-paper.read.txt | a314a7eedbb58467c33245d56c31104e4f37219d06255ad118f69c2478e4715c |
