# Q-VAE: what the SD2.1 transfer result establishes

Inspected 2026-10-18. Research only: configs and retained notes read, two weight files hashed, no model loaded or tensor compared.

## Decision

Call the result **transfer to an unseen diffusion checkpoint**, with shared encoder ancestry a material limitation. Do not call it transfer across independent autoencoders. The standard SD1.x and SD2.x autoencoders differ in their decoder; primary documentation supports retention of the encoder. Exact equality of the two locally pinned encoders after dtype conversion remains unverified. These statements are compatible: model-family provenance is established more strongly than local tensor identity.

## Primary evidence

- Podell et al., *SDXL: Improving Latent Diffusion Models for High-Resolution Image Synthesis*, [arXiv 2307.01952, section 2.4 and Table 3](https://arxiv.org/html/2307.01952#S2.SS4), says SD2.x improves SD1.x's autoencoder through decoder fine-tuning. SDXL's autoencoder is trained from scratch, although it uses the same architecture. This directly supports choosing SDXL as the first independent-encoder family for a future test. It does not establish performance of our method on SDXL.
- The [official Stability AI improved-VAE card](https://huggingface.co/stabilityai/sd-vae-ft-mse), sections Decoder Finetuning and Evaluation, identifies original kl-f8 ancestry and says only the decoder was fine-tuned to preserve compatibility. It distinguishes ft-EMA and ft-MSE. This is documentation of the released family, not a hash mapping to either local file.
- The official SD2.1-base Hugging Face page returned HTTP 401 during this inspection; no gated access or replacement weights were requested. The public SDXL paper is primary evidence from the model authors, not a community inference.

## Local artifacts

All paths below are relative to `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/`.

| Item | SD1.5 writer VAE | SD2.1 regenerator VAE |
|---|---|---|
| Directory | `.thesis-build/assets/a6/sd15-fp16/vae/` | `.thesis-build/assets/registry-sd21-4e63672c/vae/` |
| Weight filename | `diffusion_pytorch_model.fp16.safetensors` | `diffusion_pytorch_model.safetensors` |
| Bytes | 167335342 | 334643276 |
| SHA-256 | `4fbcf0ebe55a0984f5a5e00d8c4521d52359af7229bb4d81890039d2aa16dd7c` | `a1d993488569e928462932c8c38a0760b874d166399b14414135bd9c42df5815` |
| Config class | AutoencoderKL | AutoencoderKL |
| Channels / latent channels | `[128,256,512,512]` / 4 | `[128,256,512,512]` / 4 |
| Layers per block / group norm | 2 / 32 | 2 / 32 |
| Config sample_size | 512 | 768 |
| Config diffusers version | 0.6.0 | 0.10.0.dev0 |

Both configs have three input/output channels, silu activation, four DownEncoderBlock2D and four UpDecoderBlock2D blocks. The serialized files have different precision and byte counts. Unequal file hashes therefore do not establish unequal tensor values after casting, much less unequal encoder ancestry. The `sample_size` metadata difference does not establish a different encoder architecture.

The retained `research/journal-upgrade-20261009/unseen-regenerator-results.md`, lines 200–206, records `equal_after_cast_to_regenerator_dtype: false` for the **full VAE** and explicitly acknowledges that the promised encoder-only comparison was not recorded. A changed decoder is sufficient to produce this result. This session does not repair that gap by loading or comparing models.

## Consequences for the article

1. EV-33/35 and EV-50/51 support the tested checkpoint-specific results, including an unseen diffusion backbone; they do not isolate encoder transfer.
2. The strongest hypothesized failure is that F5 amplifies directions peculiar to the known encoder. Different decoder weights do not test that hypothesis decisively.
3. A future SDXL img2img comparison is the cheapest clearly motivated independent-encoder test from these sources. Pin the encoder identity, publish attack quality versus attribution, and separate VAE-only reconstruction from full regeneration. A VAE-only control cannot substitute for full SDXL regeneration.
4. Broader claims covering SD3 or FLUX would require separately verified encoder provenance and additional tests. Architecture names alone are insufficient. No such test, download or benchmark is run or approved here.

## Search record

Web search, 2026-10-18: `site:huggingface.co stabilityai stable-diffusion-2-1-base same autoencoder VAE 1.5` (no decisive hit); `"stable-diffusion-2" "autoencoder" "same"` (one decisive primary hit: SDXL Table 3; community mirrors not relied on). Direct opens: official SD2.1-base card (401), official improved-VAE card (success), SDXL OpenReview PDF (browser challenge), SDXL arXiv HTML (success). Local SHA-256 obtained using PowerShell Get-FileHash. No weight download.
