# SDXL

Rechecked 2026-10-20 UTC for BRIEF §1b. Evidence: **V2 — primary paper method and evaluation inspected**. Floor count: **YES; one distinct family in the conservative floor**.

## Inspected primary method and evaluation

Locators: §2.1 architecture; §2.4 improved autoencoder; Table3 reconstruction; official VAE config and img2img prepare_latents.

Primary paper: [2307.01952v1](https://arxiv.org/html/2307.01952v1). Cached original SHA-256 `f50bf5a2c55213b90feb5c37d3059ea60d7509ed181ce78ef496df3753082efd` at `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-sdxl-paper.txt`. “V2” is the inspection tier, not the arXiv revision.

**Method evidence (direct source account):** KL AutoencoderKL,C=4,f=8; same architecture class as SD1, separately trained. SDXL U-Net≈2.6B, dual CLIP conditioning; native1024. Optional refiner excluded from core.

**Quantitative evaluation and conditions (direct source account):** Table3 COCO2017-val256: SDXL PSNR24.7/SSIM.73/LPIPS.88/rFID4.4; SD1 23.4/.69/.96/5.0; SD2 24.5/.71/.92/4.7. Preserve paper metric convention rather than treating these LPIPS values as the thesis assessor. Generation preferences can include refiner and cannot be assigned to base-only img2img.

## Lineage, representation and implementation

**Training lineage assessment (agent inference constrained by the cited account):** vs SD1: YES, explicit from-scratch AE training in §2.4,batch256 versus9,EMA. vs SDXL: SELF anchor. Similar architecture does not imply weight ancestry.

**Official code and img2img:** stable_diffusion_xl/pipeline_stable_diffusion_xl_img2img.py: native image+strength and get_timesteps/prepare_latents. The frozen protocol executes the pinned official fp16 checkpoint values in full fp32 VAE arithmetic; it does not replace the artifact with the separate fp32 file or an external fp16-fix model.

Diffusers source inspection pin: `e04f0c5f24392fcd34b32d18d0ce03668f9bcd50` unless this card explicitly names `v0.36.0`. This is source inspection, not installation, import, GPU validation or an amendment of the frozen runtime. Source URLs and hashes appear below. Absence of `strength` means the native interface does not expose the frozen partial-noise corruption; image conditioning alone is insufficient.

| Official model/revision URL | Exact revision | Declared model license | Actual access observation |
|---|---|---|---|
| [stabilityai/stable-diffusion-xl-base-1.0](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/tree/462165984030d82259a11f4367a4eed129e94a7b) | 462165984030d82259a11f4367a4eed129e94a7b | openrail++ | ungated API snapshot |

Licenses in this table concern the named model package; dependency caveats below remain separate. An ungated metadata snapshot does not prove every dependency is ungated. No model weights were downloaded.

## 1024 memory/time and design consequence

No matched primary batch-one1024 peak/time. The roughly2.6B U-Net implies at least5.2GB BF16 parameters plus dual CLIP and fp32 VAE execution/activations. Frozen stage2 selected SDXL assets total6.941187536GB. Earlier7.105319356GB estimate used a different selection and is superseded, not an amendment of the asset plan. Official fp16 VAE is167,335,342 bytes versus separate fp32 artifact334,643,268 bytes; file precision differs from execution precision. Core10–14h is a project estimate, not a primary measurement.

Any parameter-memory figure is a lower bound or explicitly conditional estimate: decimal GB, two bytes per BF16 parameter, inference only, no optimizer. It excludes activations, attention/KV buffers, extra encoders, CFG duplication, allocator workspace and loading peaks. It is not a measured fit or wall-clock prediction.

**Design implication (agent inference):** Retain R1 as the strongest documented independent-encoder anchor, with full fp32 VAE execution of the pinned official checkpoint and deterministic posterior-mode D1.

**Limits/open assumptions:** Reconstruction at256 does not predict1024 survival. From-scratch training is an author statement, not independent initialization forensics.

No evaluation above measures this thesis’s mark survival, false positives or fixed decision rule. Paper outcomes remain author-reported literature evidence, not development outcomes.

## Inspectable source receipts

| Exact source URL | Local cached text | SHA-256 |
|---|---|---|
| https://huggingface.co/api/models/stabilityai/stable-diffusion-xl-base-1.0?blobs=true | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-stabilityai--stable-diffusion-xl-base-1.0-api.json | 8f247aefb53bf24324f3469565d9e93ba5d552a99719e81ff16f9f6c7ce72600 |
| https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/462165984030d82259a11f4367a4eed129e94a7b/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-stabilityai--stable-diffusion-xl-base-1.0-README.md | 40d263065b8a3e9a41996c257e11463fd97ae956ebf4e3f8b9625e0d78183893 |
| https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/462165984030d82259a11f4367a4eed129e94a7b/vae/config.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-stabilityai--stable-diffusion-xl-base-1.0-vae--config.json | 0b331c8ac22ded5f9997a144a575c1d113d6169aff262c353f39015bd24a6264 |
| https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/462165984030d82259a11f4367a4eed129e94a7b/model_index.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-stabilityai--stable-diffusion-xl-base-1.0-model_index.json | 6d7b93508390ab91ac5bfbe4aeb4dc2d83f7bb1b05fb069d714b5b0c75f70d44 |
| https://arxiv.org/html/2307.01952v1 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-sdxl-paper.txt | f50bf5a2c55213b90feb5c37d3059ea60d7509ed181ce78ef496df3753082efd |
| https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/462165984030d82259a11f4367a4eed129e94a7b/README.md | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\stabilityai--stable-diffusion-xl-base-1.0--README.md.txt | 40d263065b8a3e9a41996c257e11463fd97ae956ebf4e3f8b9625e0d78183893 |
| https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/462165984030d82259a11f4367a4eed129e94a7b/vae/config.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\stabilityai--stable-diffusion-xl-base-1.0--vae--config.json.txt | 0b331c8ac22ded5f9997a144a575c1d113d6169aff262c353f39015bd24a6264 |
| https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/462165984030d82259a11f4367a4eed129e94a7b/model_index.json | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\stabilityai--stable-diffusion-xl-base-1.0--model_index.json.txt | 6d7b93508390ab91ac5bfbe4aeb4dc2d83f7bb1b05fb069d714b5b0c75f70d44 |
| https://api.github.com/repos/huggingface/diffusers/contents/src/diffusers/pipelines/stable_diffusion_xl/pipeline_stable_diffusion_xl_img2img.py?ref=e04f0c5f24392fcd34b32d18d0ce03668f9bcd50 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\code-stable_diffusion_xl--pipeline_stable_diffusion_xl_img2img.py-api.txt | 53c4b787ac15e9f30d060902586236ff34b4abb8268d22e97b25d6cab296a426 |
| https://api.github.com/repos/huggingface/diffusers/contents/src/diffusers/pipelines/stable_diffusion_xl/pipeline_stable_diffusion_xl_img2img.py?ref=e04f0c5f24392fcd34b32d18d0ce03668f9bcd50 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\code-stable_diffusion_xl--pipeline_stable_diffusion_xl_img2img.py-api.decoded.txt | 0833c640ae91f8afdc548b511f4172db60a0f6dc7ee6373596343f2faf239907 |
| https://arxiv.org/html/2307.01952v1 | W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\q1-research-20261018\cache\T2-1b\T2-sdxl-paper.read.txt | 60a25194dd0df46b806d281520c1fed12a95bf8ed762e8fe5adbb129e47a93ea |
