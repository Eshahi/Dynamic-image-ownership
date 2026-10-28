# Stage C foreign-family feasibility audit

Research-only inspection, 2026-10-28. This is a recommendation to the lead researcher, not a frozen family selection or execution authorization. No models, datasets, images, packages or repositories were downloaded and no pipeline was executed. The authoritative MAIN STATE was read once; the session brief and the earlier `third-family-alternatives.md` audit were inspected.

## Recommendation and the precise claim it supports

**Prefer SD3.5 Medium as the conditional Stage C family**, subject to the user's own gated-access action, a committed model revision/file manifest, and a server-only operational preflight. It offers an official full image-to-image interface, a useful many-step severity grid, and a substantially smaller denoiser than FLUX.1-schnell. Keep every SD3/SD3.5 model and its VAE out of Stage S writer construction, predictor fitting, threshold calibration and method selection. A family can be prospectively excluded from scientific design even though its public interface was researched here; disclose that distinction.

**Do not certify strict independently initialized VAE weights.** The SD3 paper §5.2.1/Table 3 establishes an f8 representation with 16 latent channels and experimentally compares 4/8/16-channel autoencoders. Its 16-channel reconstruction PSNR/SSIM are 28.62/.86. It does not trace the exact released SD3.5 Medium VAE to a from-scratch initialization or prove that no SD1.5 layers were adapted. Architecture incompatibility with the SD1.5 four-channel latent interface supports a foreign-codec challenge; it does not prove that stronger training-history claim. [SD3 paper, §5.2.1/Table 3](https://arxiv.org/html/2403.03206v1#S5.SS2.SSS1)

Thus the supportable prospective claim is **generalization to a regenerator/codec family excluded from design**, not a causal effect of independent encoder training. The full chain also changes the denoiser, scheduler, conditioning and potentially resolution. Retain an AE-only round trip and preprocessing-only control as diagnostic cells; neither identifies encoder causality for full regeneration.

If strict released-weight initialization independence is indispensable to the primary hypothesis, this audit does not clear any candidate. Record that as an unresolved evidence condition rather than replacing it with an architectural argument. Sana/DC-AE is a stronger architectural departure, but its native few-step img2img severity is less suitable and its exact released AE provenance still needs qualification.

## Official SD3.5-compatible img2img interface

Use Diffusers **v0.35.1**, `StableDiffusion3Img2ImgPipeline`, with the official `stabilityai/stable-diffusion-3.5-medium` components. The pinned implementation registers `SD3Transformer2DModel`, `AutoencoderKL` and `FlowMatchEulerDiscreteScheduler`; its call accepts `image`, `height`, `width`, `strength`, `num_inference_steps`, `guidance_scale`, `generator` and `max_sequence_length`. It samples the VAE posterior, applies the released shift/scale, and corrupts encoded image latents with `scheduler.scale_noise`. Source locators: constructor lines 193–220; preparation 609–662; call 757–789. [Pinned official source](https://raw.githubusercontent.com/huggingface/diffusers/v0.35.1/src/diffusers/pipelines/stable_diffusion_3/pipeline_stable_diffusion_3_img2img.py)

Two short exact source excerpts:

```python
init_timestep = min(num_inference_steps * strength, num_inference_steps)
t_start = int(max(num_inference_steps - init_timestep, 0))
```

The resulting suffix has 4/8/16 denoising steps at N=40 and strengths .1/.2/.4. Preserve the actual timestep/sigma arrays, initial corruption coefficient, scheduler config, posterior RNG and noise RNG in the run record. Nominal strength does not equate flow noise to DDIM noise. Do not substitute a DDIM scheduler or manually inject SD1.5 latents.

**Proposed configuration for freezing:** BF16, batch one, 1024×1024, N=40, CFG=4.5, strengths .1/.2/.4, max sequence length 256, all three released text encoders, fixed declared prompt policy, native released scheduler/config. The official Medium card demonstrates N=40 and CFG=4.5; its training description includes resolutions 256–1440. This is an experiment proposal extrapolating the card's text-to-image settings to the official img2img class, not measured regeneration quality. The card's 4-bit example is an optional deployment variant, not evidence that quantization preserves this study's outputs. [Official Medium card, Implementation Details and Using with Diffusers](https://huggingface.co/stabilityai/stable-diffusion-3.5-medium)

For existing 512-pixel marked inputs, preregister one interpolation/resize path and a resize-only round trip to detector resolution. Do not quietly compare 1024-pixel regeneration against a different-resolution unregenerated control. A 512-pixel SD3.5 variant could be a declared budget fallback, but cannot be selected after inspecting held-out watermark survival. Prompt content must be fixed without held-out detector outputs.

## 24 GB deployment feasibility

Use native BF16 with `enable_model_cpu_offload()` first, before moving the whole pipeline to CUDA. Release all previous family pipelines and metric models. The official SD3 documentation explicitly supports component CPU offload, dropping T5, and T5 quantization; it states the optimizations apply to SD3.5. Dropping T5 or quantizing components changes the scientific configuration, so choose these only as separately preregistered fallbacks, not automatic retries after a held-out failure. [Diffusers v0.35.1 SD3 memory documentation](https://huggingface.co/docs/diffusers/v0.35.1/en/api/pipelines/stable_diffusion/stable_diffusion_3#memory-optimisations-for-sd3)

This is plausible on one RTX4090, **not verified peak VRAM, latency, host RAM, or an SLA**. Budget ample host RAM (planning preference: at least 32 GB, preferably 64 GB) because offload trades VRAM for host residency. Exact peak memory and throughput belong to a server-only, detector-sealed development preflight using the fixed operational configuration. Do not use the fresh Stage C images to tune severity or decide which codec passes. If Stage C claims depend on a family never tested scientifically, distinguish an interface-only preflight from any development quality screen, and disclose whichever is used.

## Model pin, selected files and disk accounting

SD3.5 Medium **exact repository SHA: UNRESOLVED** in this unauthenticated audit. Its public tree is visible but file content is gated; the model API and commit-history requests failed. No mutable `main` string should pass a final execution-manifest check. After the user accepts access, resolve its full commit SHA and selected LFS file sizes/hashes on the server, commit the manifest before scientific outputs, and use that SHA in every component load. A missing pin is a blocking execution condition, not a reason to invent one. [Public gated tree](https://huggingface.co/stabilityai/stable-diffusion-3.5-medium/tree/main)

| Selected component | Rounded public size | Source |
|---|---:|---|
| Transformer | 4.94 GB | [official transformer tree](https://huggingface.co/stabilityai/stable-diffusion-3.5-medium/tree/main/transformer) |
| VAE | .168 GB | [official VAE tree](https://huggingface.co/stabilityai/stable-diffusion-3.5-medium/tree/main/vae) |
| CLIP-L | .247 GB | [official text encoder tree](https://huggingface.co/stabilityai/stable-diffusion-3.5-medium/tree/main/text_encoder) |
| CLIP-G | 1.39 GB | [official second text encoder tree](https://huggingface.co/stabilityai/stable-diffusion-3.5-medium/tree/main/text_encoder_2) |
| One T5 shard set | 4.99 + 4.53 = 9.52 GB | [official third text encoder tree](https://huggingface.co/stabilityai/stable-diffusion-3.5-medium/tree/main/text_encoder_3) |
| Sum before small configs/tokenizers | **16.265 GB** | Arithmetic of rounded sizes, not exact `totalbytes` |

Download only one coherent Diffusers component set. Do not also fetch the root 5.11 GB single-file checkpoint, alternate T5 precision shards or Comfy text-encoder copies. Exact selected-file bytes remain unresolved. Reserve **at least 20 GB incremental model space**, plus independently calculated outputs, dependency caches and filesystem margin; 25 GB incremental free space is a conservative model/setup-only planning threshold. This is not a complete Stage C disk budget.

The old server has **76 GB total**, not 76 GB free. The preceding audit estimated roughly 48.6 GB of old core assets, leaving at most 27.4 GB before outputs, dependencies and filesystem overhead. Adding the selected Medium set would consume about 64.9 GB in models alone. Consequently do not promise reuse of the old disk: inspect free bytes before provisioning and plan a larger volume or a user-approved, backed-up model-cache cleanup. Retained outputs are not disposable. No cleanup is authorized by this document.

## Access and safety behavior

Both Medium and schnell visibly require a personal Hugging Face login and agreement to share account information. SD3.5 uses the Stability Community License; the current card describes research/noncommercial permissions and revenue-dependent commercial conditions. The user must review/accept the actual terms and provide approved server authentication personally; this audit accepts nothing. The SD3.5 gate explicitly collects affiliation and intended-use fields. [Official SD3.5 gate metadata](https://huggingface.co/stabilityai/stable-diffusion-3.5-medium/resolve/main/README.md), [official schnell card/gate](https://huggingface.co/black-forest-labs/FLUX.1-schnell)

The pinned SD3 img2img constructor has **no integrated safety-checker module**, and its output dataclass exposes images without an NSFW flag. This differs from the retained SD1.5 pipeline. Report `native_safety_checker=absent`, not `safety_passed`, and never pass `safety_checker=None` as a supposed optimization. Native absence is not an intervention or a certification of safe output. Any external screen must be fixed before outputs, separately versioned, and its blocks/missingness retained without seed substitution. [Pinned SD3 output definition](https://raw.githubusercontent.com/huggingface/diffusers/v0.35.1/src/diffusers/pipelines/stable_diffusion_3/pipeline_output.py), [pinned SD3 constructor](https://github.com/huggingface/diffusers/blob/v0.35.1/src/diffusers/pipelines/stable_diffusion_3/pipeline_stable_diffusion_3_img2img.py#L193)

## Why not automatically choose FLUX or Sana?

**FLUX.1-schnell** is a viable reserve foreign-family challenge. The official API resolves repository revision **`741f7c3ce8b383c54771c7003378a50191e9efe9`** and identifies an automatic gate. Its repository-wide `usedStorage=58051892060` includes duplicate formats and is not the selected pipeline's `totalbytes`. [Official Hub API](https://huggingface.co/api/models/black-forest-labs/FLUX.1-schnell)

Its selected transformer shards are approximately 9.96+9.95+3.87=23.78 GB; T5 adds 9.52 GB, VAE .168 GB and CLIP about .247 GB: roughly **33.72 GB** before tokenizers/configs. The transformer alone is about 22.15 GiB of stored BF16 weights, leaving little activation margin on a 24 GiB GPU. Whole-component offload does not subdivide that component; stronger sequential/group offload or a frozen quantized transformer may be needed. These are planning inferences from file sizes, not measured OOMs. [Pinned transformer tree](https://huggingface.co/black-forest-labs/FLUX.1-schnell/tree/741f7c3ce8b383c54771c7003378a50191e9efe9/transformer), [T5](https://huggingface.co/black-forest-labs/FLUX.1-schnell/tree/741f7c3ce8b383c54771c7003378a50191e9efe9/text_encoder_2), [VAE](https://huggingface.co/black-forest-labs/FLUX.1-schnell/tree/741f7c3ce8b383c54771c7003378a50191e9efe9/vae)

Official `FluxImg2ImgPipeline` supports schnell. At N=4, the same suffix rule makes strengths .1 and .2 identical one-step conditions, with .4 selecting two steps. Do not call that three severities or raise N to 40 merely to manufacture resolution in a timestep-distilled sampler. Native preparation samples/normalizes the VAE and injects flow noise; no integrated safety checker is registered in its constructor. [Pinned Flux img2img source, lines 53–71, 179–205, 417–439](https://raw.githubusercontent.com/huggingface/diffusers/v0.35.1/src/diffusers/pipelines/flux/pipeline_flux_img2img.py)

The supported schnell regime is CFG=0, maximum sequence length 256 and few steps; the card demonstrates CPU model offload. A fixed one/two/three/four-step challenge could be useful, but is a distinct severity design and requires quality validation. The model card establishes a 12B distilled flow model, not the exact VAE's independent initialization history. [Official versioned Flux documentation](https://huggingface.co/docs/diffusers/v0.35.1/en/api/pipelines/flux#timestep-distilled)

**Sana-Sprint 0.6B** has the official `SanaSprintImg2ImgPipeline` in v0.35.1 and a public Apache-2.0-labelled checkpoint. Its card separately points to Gemma terms; it is not safe to infer all component permissions from the top-level licence. [Official Sprint card](https://huggingface.co/Efficient-Large-Model/Sana_Sprint_0.6B_1024px_diffusers)

The existing October 25 audit identifies a roughly 7.7 GB self-contained release, `AutoencoderDC`, a concrete DC-AE checkpoint lead and an SCM trigonometric schedule. At default N=2, .1/.2/.4 collapse to the same selected step. This makes it a cheap reserve with a difficult severity preflight, not a drop-in .1/.2/.4 replacement. The current audit re-opened the native source and confirmed the distinct Sprint class; the earlier SCM/config derivation is retained evidence rather than a fresh runtime verification. Ordinary Sana weights must not be silently loaded into the Sprint sampler. [Pinned native Sprint implementation](https://raw.githubusercontent.com/huggingface/diffusers/v0.35.1/src/diffusers/pipelines/sana/pipeline_sana_sprint_img2img.py), [earlier detailed local audit](../../encoder-transfer-20261019/final-study-20261025/analysis/third-family-alternatives.md)

## Conditions before a Stage C freeze

1. State the claim as prospective family exclusion; retain `strict_AE_initialization_independence=unverified` unless new primary evidence resolves it.
2. User accepts the selected gate/licence; authenticate only through the approved server arrangement.
3. Resolve exact Medium revision and selected-file byte/hash manifest; pin software and scheduler config. No `main` fallback.
4. Freeze resolution, preprocessing, prompts, RNG behavior, steps, strengths, CPU offload, safety policy, output/missingness rules and any fallback before scientific outcomes.
5. Establish server-only operational feasibility within Stage C's 50-hour ceiling and disk envelope. No timing claim follows from this source audit. If preflight changes the family or numerical pipeline, update and commit the protocol before held-out use.
6. Never replace a failed held-out family with the reserve after seeing detection results. A predeclared feasibility-only substitution rule must trigger before detector release and be reported.

**Verdict:** SD3.5 Medium is the strongest practical candidate for a fresh foreign-family challenge; it remains conditional, and it does not currently satisfy a stronger claim of proven independently initialized released VAE weights.
