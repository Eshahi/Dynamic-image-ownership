# T2 — Independent encoder landscape and implementable panel

Research date: 2026-10-19. Stage 1 only. No weights downloaded, GPU used, development outcomes inspected, or held-out data accessed. This document is the self-contained decision deliverable; `model-metadata.json`, `download-plan.json`, `source-cache-manifest.json`, and `cards/` provide the source inventory and exact file pins. Existing dossier [Q-VAE](../../../q1-dossier-20261018/02-literature/Q-VAE.md) is retained, not superseded.

## Decision

Keep R0 SD1.5 and R1 SDXL as the firm core, n=60 and four watermark arms. Preserve the brief's SDXL strength .2 primary endpoint and decision thresholds unchanged. SDXL is explicitly trained from scratch and answers the independent-of-SD1 encoder question. The official FLUX.1-schnell repository is currently automatically gated, despite its Apache-2.0 license. Anonymous config access returned 401; it fails the brief's ungated condition. Mark R2 and its paired D2 unavailable, with this reason. Do not replace it silently, use a mirror to evade the gate, or seek credentials.

If a separately recorded design amendment is desired before execution, **Kandinsky 3** is the strongest native-1024 alternative: independently trained MoVQ, Apache-2.0, anonymously accessible, and a stable official img2img API. **Kandinsky 2.2** is cheaper to store/load, but has a lower native training resolution and an additional prior. Both are proposals, not amendments enacted here. Their scheduler and noise levels differ from SDXL; equal numeric strength does not imply equal corruption. Keep such an arm secondary and budget-droppable. SDXL reconstruction-only D1 is especially useful because it separates the encoder bottleneck from denoising without another generator download.

## What “independent” means

Here Y means primary sources describe a separately trained image encoder, or directly identify a separately trained ancestor. N means documented reuse/shared ancestry. U means the training initialization is unresolved. Architectural dimensions and different complete-VAE file hashes alone do not establish independence: a decoder can change while its encoder remains frozen. Y is documentary evidence, not a tensor-level forensic audit. The two lineage columns concern independence from the **SD1 image encoder** and from the **SDXL image encoder**, respectively; independence from every other row is not implied.

## Landscape

`C/f` denotes image latent channels/spatial downsampling; packed transformer tokens are distinguished. “Native” means an official image-to-image API that adds noise to an encoded input, not merely an image-edit/reference-image interface. Licenses below are model-card declarations, with dependencies noted; OpenRAIL and custom licenses are not permissive OSI licenses. Gating was checked anonymously through official HF API/config requests. Pipeline availability was checked against official docs and the diffusers tree at `e04f0c5f24392fcd34b32d18d0ce03668f9bcd50`; core/alternative API code was also read at release `v0.36.0`.

| Family / released examples | C/f; lineage from SD1 / SDXL | Official img2img | License / gate; decision |
|---|---|---|---|
| SD1.x KL-f8; SD2/2.1 | 4/8; N / Y | StableDiffusionImg2ImgPipeline | OpenRAIL variants; historical R0 only. SD2 decoder changes are not an independent encoder test. |
| SDXL base1.0 | 4/8; Y / N | StableDiffusionXLImg2ImgPipeline | OpenRAIL++, ungated; primary R1. Paper §2.4 explicitly from-scratch AE. |
| SD3 / SD3.5 | 16/8; U / U | StableDiffusion3Img2ImgPipeline | Stability custom/community terms, auto-gated. Paper trains/evaluates expanded latent AEs but no inspected explicit SD1/XL initialization exclusion; not eligible core. |
| FLUX.1 schnell / dev | 16/8; U / U | FluxImg2ImgPipeline | Schnell Apache-2.0, dev noncommercial; both auto-gated. Same published VAE file. No affirmative no-SD-initialization claim established. |
| FLUX.2 dev / klein4B / klein9B | 32/8; 2x2 packing produces128 channels at /16; U / U | Reference-image editing, no inspected standard strength img2img class | 4B Apache-2.0 ungated; dev/9B custom gated. New dimensions alone insufficient lineage evidence. |
| FLUX.3 Image Klein, Oct2026 | AutoencoderKLFlux2; U / U | Modular reference editing, no established classic img2img | Kommunity/custom, auto-gated. Very recent; main-branch API, not v0.36.0. |
| Kandinsky2.1/2.2 MoVQ | 4/8; Y / Y | KandinskyV22Img2ImgPipeline plus prior | Apache-2.0, ungated. MoVQ trained on LAION HighRes, 67M AE; optional lower-cost alternative. |
| Kandinsky3 MoVQ | 4/8; Y / Y | Kandinsky3Img2ImgPipeline | Apache-2.0, ungated; FLAN-UL2 dependency Apache-2.0. 270M AE, native1024; preferred alternative. Same broad MoVQ family as KD2, not two unrelated families. |
| SANA600M/1.6B DC-AE | 32/32; Y / Y | No native base-SANA img2img verified | Model Apache-2.0 ungated; bundled Gemma text encoder has Gemma terms. Independent residual/DC-AE training. |
| SANA Sprint1.6B DC-AE1.1 | 32/32; Y / Y | SanaSprintImg2ImgPipeline, v0.36.0 | Apache model/Gemma dependency; native2-step strengths .1/.2/.4 all yield one step. Different SCM semantics; proposal only. |
| PixArt-alpha | 4/8; N / Y | No native strength img2img class verified | OpenRAIL++, ungated; inherits SD2 VAE. Not new encoder evidence. |
| PixArt-Sigma | 4/8; Y / N | No native strength img2img class verified | OpenRAIL++, ungated; paper §3.3 uses frozen SDXL VAE. |
| Playground2.5 | 4/8; Y / N | SDXL-compatible img2img; EDM schedule | Custom Playground community license, ungated; published fp16 VAE SHA equals SDXL. Different normalization is not a new encoder. |
| Hunyuan-DiT v1.2 | 4/8; Y / N | No native strength img2img class verified | Tencent custom, ungated; uses SDXL VAE. |
| Qwen-Image / 2512 | 16/8 spatial, /4 temporal; Y / Y | QwenImageImg2ImgPipeline | Apache-2.0 ungated; Wan2.1 encoder frozen, decoder tuned. Same VAE in Qwen/2512. New relative to SD, not to Wan. |
| Qwen-Image2.1 | U; U / U | Unified generation/edit API; classic strength API unverified | qwen-research custom, ungated. New7B architecture; do not inherit prior Qwen lineage by name. |
| Z-Image Turbo | 16/8; U / U | ZImageImg2ImgPipeline in current tree | Apache-2.0 ungated; FLUX VAE reused, identical file SHA. Not a new family relative to FLUX. |
| Lumina2 | 16/8; U / U | No native strength img2img verified | Apache-2.0 ungated; explicit FLUX.1-dev VAE path. |
| Chroma1-HD | 16/8; U / U | ChromaImg2ImgPipeline in current tree | Apache-2.0 ungated; FLUX VAE identical file SHA. |
| AuraFlow0.3 | 4/8; Y / N | No native strength img2img verified | Apache-2.0 ungated; SDXL VAE files identical. |
| HunyuanImage3 | Unresolved; U / U | No native strength img2img verified | Tencent custom ungated; ~168GB listed weights, outside cap. Not Hunyuan-DiT. |
| Kandinsky5 / Lens | Training/initialization incompletely resolved; U / U | No native strength img2img verified in screened tree | 2025/2026 paper screening only; not promoted to independent-encoder candidates. |
| DeepFloyd IF | Pixel stages64/256, no image AE there | IFImg2ImgPipeline exists | IF custom license, gated. Final1024 upsampler may reintroduce a VAE; not eligible. |
| Google DDPM CelebA-HQ256 | RGB3/1; no AE | DDPMPipeline only, no turnkey img2img | Apache-2.0 ungated; face-specific256 and custom noising adapter needed. Poor1024 general-image comparator. |
| Chroma Radiance | RGB3/1; no AE | No official diffusers/native img2img found | Apache-2.0 ungated, ~19GB denoiser plus text encoder; WIP release. Bespoke adapter needed. |
| PRX Pixel, 2026 | RGB3/1; no AE | Official PRXPixelPipeline is text-to-image only | Apache-2.0 ungated, ~7B denoiser, Qwen3-VL text;1024. Strong future pixel-space candidate, no native input-image/strength parameter. |

Primary paper links and inspected locators are in the cards. Exact model IDs/revisions/configs and file hashes are in the metadata. For reuse evidence, the identical SHA of SDXL/Playground/AuraFlow fp16 VAE is `bcb60880a46b63dea58e9bc591abe15f8350bde47b405f9c38f4be70c6161e68`; the FLUX.1/Z-Image/Chroma VAE SHA is `f5b59a26851551b67ae1fe58d32e76486e1e812def4696a4bea97f16604d40a3`. These identify released files; they do not resolve the original FLUX encoder initialization.

## Exact implementation contract: optional Kandinsky3

This is a static API specification, not executed code. Verified official source: [v0.36.0 pipeline](https://github.com/huggingface/diffusers/blob/v0.36.0/src/diffusers/pipelines/kandinsky3/pipeline_kandinsky3_img2img.py) and [VQModel](https://github.com/huggingface/diffusers/blob/v0.36.0/src/diffusers/models/autoencoders/vq_model.py). The official [Kandinsky3 documentation](https://huggingface.co/docs/diffusers/api/pipelines/kandinsky3) confirms both the API and external embeddings/masks. Runtime dependency compatibility still requires ordinary installation/smoke verification after stage1; no claim that this environment was executed.

```python
pipe = Kandinsky3Img2ImgPipeline.from_pretrained(
    "kandinsky-community/kandinsky-3",
    revision="bf79e6c219da8a94abb50235fdc4567eb8fb4632",
    variant="fp16", torch_dtype=torch.float16,
)
# Input already resized512->1024 using the brief's Lanczos rule.
out = pipe(prompt="", image=image1024, strength=s,
           num_inference_steps=20, guidance_scale=1.0,
           generator=generator).images[0]
# Downsample1024->512 using the same locked Lanczos rule.
```

Img2img takes input resolution; do not pass unsupported height/width arguments. Keep its shipped `DDPMScheduler`: 1000 training steps, epsilon prediction, `squaredcos_cap_v2`, `fixed_small` variance, `clip_sample=true`, `steps_offset=1`. Do not substitute DDIM or pass eta. The implementation uses floor(N*strength), hence2/4/8 denoising steps at20 and .1/.2/.4. `guidance_scale=1` disables classifier-free guidance. Reuse empty prompt embeddings **and their attention mask** to avoid repeated FLAN-UL2 work. The published API supports these inputs; the loader must manage text encoder/offload phases without changing numerics or quantizing.

Paired deterministic diagnostic, if this proposal is adopted:

```python
x = pipe.image_processor.preprocess(image1024).to(device=device, dtype=dtype)
z = pipe.movq.encode(x).latents
y = pipe.movq.decode(z, force_not_quantize=True).sample
image1024_recon = pipe.image_processor.postprocess(y, output_type="pil")[0]
```

Then perform the same locked1024->512 downsample. MoVQ has no posterior `.mode()`/`.sample()` here. Use raw continuous latents and `force_not_quantize=True`, matching the native diffusion path; do not add SD scaling or codebook quantization. Although a dormant generic `prepare_latents` branch mentions a posterior, the actual call first encodes to four-channel latents and bypasses that branch. D2 must be named “continuous MoVQ roundtrip,” not VQ codebook reconstruction. KD2.2 uses the same continuous-latent convention, but needs the official prior outputs `image_embeds` and `negative_image_embeds` passed to `KandinskyV22Img2ImgPipeline`.

SANA details: base `Efficient-Large-Model/Sana_600M_1024px_diffusers` bundles DC-AE1.0; Sprint `Efficient-Large-Model/Sana_Sprint_1.6B_1024px_diffusers` bundles DC-AE1.1. Their C32/f32 codec is not a KL-f8 substitute. Sprint uses SCMScheduler/trigflow, sigma_data=.5, `max_timesteps=1.57080`, intermediate_timestep1.3. Its native2-step truncation uses ceil(N*s), so the brief's three strengths collapse to one retained step. Increasing the step count just to manufacture three severities would be a new, unvalidated protocol. The often cited SANA subsecond4090 number is for an optimized quantized engine, not this official diffusers img2img path.

## Download pins and cap

No model files were downloaded. Sizes below are HF LFS metadata, decimal GB; selected weight hashes and every filename are in `download-plan.json`. That file is an allowlist specification, not a command. Download only relevant configs/tokenizers/indexes and selected weights; avoid root monoliths and duplicate precision formats.

| Model | Immutable revision | Selected weights GB |
|---|---|---:|
| SDXL base1.0 | `462165984030d82259a11f4367a4eed129e94a7b` | 7.105319356 |
| Kandinsky3 | `bf79e6c219da8a94abb50235fdc4567eb8fb4632` | 28.390829958 |
| Kandinsky2.2 decoder | `9ae140d347fed8ce6e8bb3005dcc1f48543bb8e3` | 5.283689948 |
| Kandinsky2.2 prior | `9fc51ad5732afc5d031724219d22e6c42179c5a8` | 10.573556608 |

SDXL selection: `text_encoder/model.fp16.safetensors`246,144,152 bytes; `text_encoder_2/model.fp16.safetensors`1,389,382,176; `unet/diffusion_pytorch_model.fp16.safetensors`5,135,149,760; **official fp32** `vae/diffusion_pytorch_model.safetensors`334,643,268. Explicitly load this VAE in fp32 with its shipped `force_upcast=true`; no madebyollin fp16-fix. Its hash is `1598f3d24932bcfe6634e8b618ea1e30ab1d57f5aad13a6d2de446d2199f2341`. Loading a globally fp16 pipeline and later upcasting does not recover weights already rounded on load, so load the official VAE separately as fp32.

KD3 selected files: `movq/diffusion_pytorch_model.fp16.safetensors`, `unet/diffusion_pytorch_model.fp16.safetensors`, and `text_encoder/model.fp16-00001-of-00005.safetensors` through `00005-of-00005`, with matching fp16 index. The text encoder accounts for21.739GB; UNet6.111GB; MoVQ0.541GB. All-resident execution cannot fit24GB. Model CPU offload or separate text encoding is required; reserve at least64GB host RAM as an assumption, then verify actual loading peak.

Planning reserve:20GB for R0, watermark baselines and their dependencies +7.106GB SDXL +28.391GB KD3 +1GB configs/tokenizers =56.497GB. KD2.2 instead gives44GB rounded. Even both alternatives give72.354GB before remaining extras; do **not** download both simply because this nominal sum fits. The20GB baseline reserve is not a measured baseline inventory; parent must reconcile it against the complete manifest before authorizing downloads. R0's existing historical revision remains the brief's lock; this topic does not replace it with a new SD1 mirror.

## Memory and time: assumptions, not benchmark evidence

No primary measured timing was found matching our1024, empty prompt, guidance1, batch1, precision, scheduler and strength grid. The following are deliberately broad planning ranges for a4090-class24GB GPU with cached prompt, efficient attention, serial model phases and adequate host RAM. They are neither results nor throughput guarantees. Seconds are per regenerated image, averaged over .1/.2/.4 at20 base steps where meaningful, including encode/decode but excluding initial model download/load. A model requiring offload can be much slower. No current rental price is asserted.

| Candidate | Approx active VRAM / seconds at1024 | Implication |
|---|---|---|
| SD1/2 | 6–12GB /2–8s | Historical R0 remains512; planning R0 average2s at512. |
| SDXL | 10–18GB /4–12s | Plan6s average; protect its allocation. |
| SD3 medium /3.5medium | 12–24GB with text offload /5–20s | Gate and lineage uncertainty dominate. Large3.5 >24GB all-resident. |
| FLUX1 schnell/dev | 20–30GB denoiser+AE, text offload /5–25s | 10-step schnell cannot be treated as normal20-step diffusion; not eligible. |
| FLUX2klein4B /9B | 12–24GB /5–25s;24–40GB /10–40s | Reference-edit interface; not a matched noising channel. |
| FLUX2dev /FLUX3 | >24GB or uncertain /not budgeted | Published optimized FLUX3 timings do not transfer to this task. |
| KD2.2 | 10–18GB phased /4–12s | Plan6s;1024 extrapolates training resolution. |
| KD3 | 12–22GB denoising phase /6–20s; text phase may approach24GB | Plan8s; loading/offload is material. |
| SANA base /Sprint | 8–16GB /2–8s;1–4s native short Sprint | No base official img2img; Sprint severity collapse. |
| PixArt /Playground /HunyuanDiT /AuraFlow | 10–24GB phased /4–20s | Shared encoder or unsupported API; no additional lineage test. |
| QwenImage/2512 | >40GB denoiser alone;24GB sequential offload /30–120s | ~57.7GB weights; poor budget fit. |
| ZImage /Lumina2 /Chroma | 16–30GB phased /4–25s | Shared FLUX AE; cannot count as independent families. |
| Qwen2.1 /HunyuanImage3 /Kandinsky5 /Lens | Not estimated reliably | Do not use unverified dimensional/latency claims for budget. |
| Pixel DDPM256 /IF | Native resolution mismatch; no valid1024 estimate | Not a general1024 ungated channel. |
| ChromaRadiance /PRXPixel | 20–32GB phased /10–60s (speculative) | Extra adapter validation, no native img2img; proposals only. |

Cost calculation is explicit: outputs per regenerator = n*4 arms*3 strengths*3 seeds =36n (2160 at60;4320 at120). At n60, R0 mean2s +SDXL6s costs4.8 GPU-hours of regeneration. Reserve4.2 instance-hours for setup/download/loading, watermark generation, diagnostics/detection, transfer and contingency: **9.0 instance-hours**. At price p USD/hour cost is9p. The binding cap is min(15,15/p) hours including overhead, not15 GPU-hours plus uncounted setup. A real host must satisfy both time and dollar caps.

| Proposal | n | Planned total instance-hours | Cost at hypothetical p=$1/h |
|---|---:|---:|---:|
| Firm R0/R1 +D1 |60|9.0|$9.0|
| Add KD2.2 full grid,6s plus0.5h loading |60|13.1|$13.1|
| Add KD3 full grid,8s plus0.7h loading |60|14.5|$14.5|
| R0/R1 only, doubled outputs +5h overhead |120|14.6|$14.6|
| R0/R1 +KD3, doubled outputs +6h overhead |120|25.2|$25.2; larger-budget proposal only|
| n60 plus Qwen .2 only,720 outputs at60s +1h loading |60|22.0|$22.0; larger-budget proposal only|

These projections are sensitive: KD3 at20s would add12h, exceeding the cap. Therefore neither optional model belongs in an assured15h core. Before any optional execution, extrapolate a few already authorized development setup calls, including preprocessing/offload and I/O, without examining detection success to decide inclusion. Reserve completion time for R0/R1 .2/.4 first; apply the brief's drop order. Never reduce n, choose sources, or change thresholds based on measured watermark performance. n120 is also too close to the cap to promise before timing. Default n60.

## Pixel-space result and coverage limits

There are permissive ungated1024 pixel-space generators: **PRX Pixel** and **Chroma Radiance**. No inspected official implementation provides a ready, standard input-image-strength regeneration interface. Passing hand-built noisy pixels as `latents` would require a newly specified noising schedule and validation; it is not established native img2img. Thus **no fully qualified low-complexity pixel-space regenerator was identified for this core**, not “none exists.” PRX Pixel is the best wider-panel lead because its current official API/docs explicitly describe RGB prediction and1024; the model card warns its pipeline was not yet in a released diffusers version. Its revision is `bcd5e63f072257a220c5d0ba039c97657398b1c2`.

Coverage includes all requested families and representative2025–2026 releases, including FLUX2, FLUX3 announced2026-10-15, Qwen2512/2.1, ZImage, Chroma, HunyuanImage3, PRXPixel and screening of Kandinsky5/Lens. It is not a census of all fine-tunes, private APIs, or every current diffusers sidebar entry. A distinct generator brand is not another independent encoder. Inaccessible gated config bodies are recorded as unresolved, not inferred from snippets. Some main-branch APIs postdate the pinned stable core API. No commercial closed model is recommended because encoder lineage and reproducible corruption cannot be verified.

Primary access limitations: some license filename guesses returned404, Gemma terms failed through urllib but were readable through the browser, and BFL pages had intermittent DNS failures in the cache client. These failures remain in the manifest. FLUX gate evidence is corroborated by API `gated=auto` and401 pinned config requests; a failed guessed repository name alone is not gating evidence. FLUX3's correct lower-case repository was subsequently resolved and verified auto-gated. “V2” cards require method and evaluation sections actually read; lightly screened new papers remain partial. No claim of exhaustive absence or runtime validation follows from this research.
