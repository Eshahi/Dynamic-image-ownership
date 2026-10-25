# FLUX.1-schnell feasibility audit

Research-only source inspection, 2026-10-25 UTC. Author: delegated Codex WP4 auditor. No checkpoint, code, image or dataset downloaded; no inference, library import, account action or server action performed. Read the authoritative MAIN STATE once and the supplied WP4 brief and encoder matrix. This is a conditional implementation recommendation, not an executed feasibility test.

## Recommendation

Prefer **FLUX.1-schnell as a conditional new independent-family challenge**, using BF16 on a rented 48 GB GPU, after access, storage and a development-only feasibility gate. Its family-level autoencoder independence evidence is stronger than an architectural difference alone. Do not promise that the exact released schnell AE is byte-identical to the AE evaluated in the Kontext paper: gated files prevent closing that identity audit here.

Fallback: retain the already established Kandinsky 3/Sber-MoVQGAN family as the third independent representation alongside SD1.5 and SDXL; report that FLUX was unavailable, rather than quietly substituting an unverified SD3.5 AE lineage. If a genuinely new family is mandatory, SD3.5 Medium is a separate conditional option requiring its own lineage, license, scheduler and resource gate. Neither fallback upgrades an observational full-pipeline difference into an AE-only causal result.

## Evidence and unresolved identity

[BFL Kontext v2 §2](https://arxiv.org/html/2506.15742v2) explicitly describes training the FLUX.1 convolutional AE from scratch, with adversarial training and 16 latent channels. Table 1 and Appendix B evaluate reconstruction, not mark retention. This establishes the developer's family-level fresh-training claim, not disjoint training data.

[BFL util.py](https://raw.githubusercontent.com/black-forest-labs/flux/main/src/flux/util.py), inspected lines 333–362 and 554–583, maps schnell and Kontext to their respective repositories' `ae.safetensors`, with identical AE configuration: 16 channels, scale .3611, shift .1159. The loader uses each model's own repository. **Same filename/config does not prove same weight bytes.** This moving-main source has no immutable commit recovered in this audit. Its save helper also adds an invisible watermark; the study should use the pinned Diffusers path and save outputs directly, without importing that helper, to avoid an additional intervention.

[Official HF model metadata](https://huggingface.co/api/models/black-forest-labs/FLUX.1-schnell) exposes revision **741f7c3ce8b383c54771c7003378a50191e9efe9**, last modified 2024-08-16, and `gated: auto`. [The official card](https://huggingface.co/black-forest-labs/FLUX.1-schnell) displays Apache-2.0 and requires agreement to share HF information before accessing files. Public listing is not download access. No evidence about this user's existing account approval was available.

Exact human action for a later authorized server phase: log in to the intended Hugging Face account, open the official schnell card, review its current access conditions, and personally submit the agreement to share the requested account/contact information if willing. Then authorize a read token for that account on the rented server through a private credential mechanism. Do not paste credentials in project files. This audit neither accepts conditions nor assumes consent. The default until that action is **FLUX excluded/pending**, with the fallback explicit.

Before calling the released AE independently audited, archive the pinned `vae/config.json`, model index and documented conversion provenance. Record a checkpoint digest on the server; seek an official reference tying it to the paper's AE. Compare named tensor values after official conversion only if identity remains material: raw and converted checkpoints can differ in serialization/dtype, so unequal file hashes alone do not disprove weight lineage. Lack of exact identity remains a limitation, not a fabricated proof.

## Pinned strength semantics: correction to the earlier card

[Diffusers v0.35.1 FluxImg2Img source](https://raw.githubusercontent.com/huggingface/diffusers/v0.35.1/src/diffusers/pipelines/flux/pipeline_flux_img2img.py), lines 431–439 and 830–852, uses `t_start=int(max(N-N*strength,0))`, not `int(N*strength)`. Therefore effective updates are `N-t_start = ceil(N*strength)` for positive strength, subject to floating-point boundaries. For N=4:

| Nominal strength | Updates | Start index | Raw start sigma |
|---|---:|---:|---:|
| .1, .2, .25 | 1 | 3 | .25 |
| .4, .5 | 2 | 2 | .5 |
| .75 | 3 | 1 | .75 |
| 1 | 4 | 0 | 1 |

Exactly zero yields no updates and raises an error. Thus the earlier card's warning that positive strength below .25 yields zero updates is **incorrect for this pinned version**. The scientific problem is duplicated severity settings and coarse control. The default raw grid is [1,.75,.5,.25]. Image encoding samples the posterior by default; an AE-mode control must be explicit.

## Conditional sigma derivation, not a verified released configuration

Anonymous `blob`, `raw` and `resolve` requests for the pinned released scheduler JSON failed. Consequently **the released scheduler's actual flags are UNVERIFIED here**, and the following grid is conditional.

[Pinned FlowMatchEuler scheduler](https://raw.githubusercontent.com/huggingface/diffusers/v0.35.1/src/diffusers/schedulers/scheduling_flow_match_euler_discrete.py) uses `z_sigma=(1-sigma)z+sigma*epsilon`. For dynamic exponential shifting, sigma becomes `exp(mu)*r/(1+(exp(mu)-1)*r)`. At 1024 square, f8 encoding plus 2×2 packing gives 4096 image tokens; with base/max lengths 256/4096 and shifts .5/1.15, mu=1.15. With no terminal stretch, alternative schedule or inversion:

| Raw r | Dynamic sigma | t if 1000 training steps |
|---:|---:|---:|
| 1 | 1 | 1000 |
| .75 | .90453077 | 904.53077 |
| .5 | .75951092 | 759.51092 |
| .25 | .51284410 | 512.84410 |

If dynamic shifting is false, the rational shift uses configured `shift` instead of exp(mu); at shift=1 the raw grid remains unchanged. A zero terminal sigma is appended. Server implementation must read flags and serialize actual arrays, rather than adopt this conditional table as fact. Numbers above are scalar arithmetic, not an experiment.

## Required download and memory reasoning

At revision 741f7c3ce8b383c54771c7003378a50191e9efe9, the official subtrees list:

| Required Diffusers weights | Listed size | Primary listing |
|---|---:|---|
| Transformer, three shards | 9.96+9.95+3.87 = 23.78 GB | [Transformer](https://huggingface.co/black-forest-labs/FLUX.1-schnell/tree/741f7c3ce8b383c54771c7003378a50191e9efe9/transformer) |
| T5 encoder, two shards | 4.99+4.53 = 9.52 GB | [T5](https://huggingface.co/black-forest-labs/FLUX.1-schnell/tree/741f7c3ce8b383c54771c7003378a50191e9efe9/text_encoder_2) |
| CLIP encoder | .246 GB | [CLIP](https://huggingface.co/black-forest-labs/FLUX.1-schnell/tree/741f7c3ce8b383c54771c7003378a50191e9efe9/text_encoder) |
| Converted VAE | .168 GB | [VAE](https://huggingface.co/black-forest-labs/FLUX.1-schnell/tree/741f7c3ce8b383c54771c7003378a50191e9efe9/vae) |
| Configs, indices, two tokenizers | Additional; exact bytes unverified | [Full file names](https://huggingface.co/api/models/black-forest-labs/FLUX.1-schnell) |

Total displayed weights are about **33.714 decimal GB**, before small files, packages and study outputs. Values are rounded listing values, not an exact manifest. Do not additionally fetch duplicate root `flux1-schnell.safetensors` (23.8 GB), root `ae.safetensors` (.335 GB), or example JPEGs. All files are one chosen format, not a whole-repository snapshot. This alone exceeds the older 30 GB total-download allowance; if that allowance applies to the eventual server phase, the user must amend it explicitly, or FLUX is omitted. No amendment is inferred here.

The following are resource estimates from weight sizes, not observed peaks: 23.78 GB BF16 transformer weights are about 22.15 GiB. A 24 GiB 4090 has under 2 GiB remaining before activations, allocator and other buffers; whole-model CPU offload still moves the full transformer to GPU for its forward pass, so that option alone does not establish fit. Layer/sequential offload or quantization might help but change runtime or numerical conditions and need their own server measurement. No 4090 runtime/fit claim is justified.

The complete listed weights are about 31.4 GiB, making **48 GB VRAM preferable** for BF16 with room to investigate activation headroom. This does not prove all-resident 1024px fit: transformer forward, text encoding and VAE decoding have distinct peaks. Start with batch 1, CPU offload of inactive modules, no quantization, and text embeddings cached on the server. Request ample host RAM (planning preference ≥64 GiB, not a measured minimum) and storage beyond the weight total plus all other study models and outputs. Exact peak host/GPU memory, startup and per-source time remain **unmeasured**. [Pinned Diffusers docs](https://huggingface.co/docs/diffusers/v0.35.1/en/api/pipelines/flux) prescribe schnell guidance 0, maximum text length 256 and demonstrate four steps with model CPU offload; this is an example, not a 4090 benchmark.

## Development-only acceptance and fallback plan

After the user approves the final experiment and rented-server budget, first audit access/revisions and estimate all required storage before fetching weights. Then use a small fixed development subset, batch 1, 1024px, N=4, guidance 0, fixed text policy, posterior/noise seeds, and distinct stock schedule tails (one, two and three updates). Record attempted cells, exceptions/OOMs, actual scheduler config, full timestep/sigma arrays, posterior mode/sample, preprocessing, achieved distortion and observed memory/time. Freeze a resource cutoff in the parent protocol before starting. No discarded failures or locally generated rehearsals.

Keep AE-only posterior-mode reconstruction separate from the native sampled-AE full pipeline. Couple posterior randomness when comparing marked/unmarked versions. Compare severity using the parent's frozen distortion-overlap/caliper rule on development data; the floor at one stock update may be too severe. If no overlap exists, retain an explicitly descriptive challenge result and declare matched-severity inference unavailable. Neither equal nominal strength nor equal latent sigma across different encoders establishes equal image severity. Custom sigma schedules and >4 steps would be a new development amendment with a distilled-model validity check, not an automatic repair. If access, memory, budget or valid severity support fails, activate the stated Kandinsky fallback and record FLUX missing.

## Research query and access log

All web operations used the web tool for source reading; no search-engine query was needed. Access date for this audit: 2026-10-25 UTC. Local reads: authoritative STATE, BRIEF WP4, `bfl-flux-schnell.md`, `literature/encoders/wp4-matrix.md`. The initially requested root `wp4-matrix.md` was absent and located by file-name search.

1. Opened pinned v0.35.1 FluxImg2Img source, official HF model API and scheduler raw-main URL. Source/API readable; scheduler unavailable.
2. Opened pinned scheduler source and BFL util main. Readable. Tried HF pinned scheduler blob and recursive pinned API tree; unavailable.
3. Opened HF main scheduler blob and recursive tree; unavailable. Opened official card; readable gate. Used find for `get_timesteps`, `sigmas = np`, `flux-schnell`, `_time_shift_exponential` in sources.
4. Clicked official Files listing; readable. Tried pinned scheduler resolve; unavailable. Opened Kontext v2 and pinned Flux docs; readable.
5. Tried HF API tree main and scheduler subtree; unavailable. Opened T5 and transformer main subtrees; readable. Used find for AE filename and sequential offload term (latter absent).
6. Opened pinned CLIP/VAE subtrees; readable. Tried GitHub commits/main API to pin BFL source; unavailable. Clicked root AE file; unavailable. Used find for Kontext config and memory-optimization heading (latter absent).
7. Opened scheduler lines 270 onward and pinned transformer/T5 subtrees; readable. Computed four conditional shifted scalars with PowerShell Math.Exp only.

The inaccessible scheduler/config/checkpoint pages remain unresolved evidence. Public metadata and cached listing dates do not imply authenticated access or a server result.
