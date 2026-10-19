# Official pipeline contract

Evidence type: code/config inspected, 2026-10-19. Primary source: [diffusers v0.35.1 SDXL img2img](https://github.com/huggingface/diffusers/blob/v0.35.1/src/diffusers/pipelines/stable_diffusion_xl/pipeline_stable_diffusion_xl_img2img.py), [DDIM](https://github.com/huggingface/diffusers/blob/v0.35.1/src/diffusers/schedulers/scheduling_ddim.py), [SDXL official snapshot](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/tree/462165984030d82259a11f4367a4eed129e94a7b). File identities in adjacent manifests.

## Precision correction

The SDXL official VAE config has force_upcast=true, four latent channels, factor8 spatial compression and scaling_factor=.13025. Native img2img `prepare_latents` moves image and whole VAE to fp32 before encoding, samples the posterior with the supplied generator, then restores VAE/latents to prompt dtype. **Default decoder upcast is mixed precision:** `upcast_vae` moves the VAE to fp32 but, with PyTorch2 SDPA or xformers attention, recasts post_quant_conv, decoder.conv_in and decoder.mid_block to their original dtype. The brief's full-fp32 decode therefore requires an explicit minimal subclass override:

```python
class FullFloatSDXLImg2Img(StableDiffusionXLImg2ImgPipeline):
    def upcast_vae(self):
        self.vae.to(dtype=torch.float32)
```

This retains native full-fp32 encode and native sampling/noising. Final decode casts latents to post_quant_conv dtype, now fp32. Native code restores fp16 afterward. Assert `force_upcast is True` and decoder parameter dtypes in a synthetic adapter test; add runtime finite checks. Merely calling `vae.to(float32)` once before a standard pipeline call is insufficient: native encode subsequently restores prompt dtype. Full fp32 arithmetic here uses released fp16 checkpoint values expanded to fp32; it does not recover original unrounded fp32 checkpoint weights. Record that distinction. Loading full-fp32 VAE weights instead would be a separate weight choice, not implied by arithmetic upcast.

Use actual `vae/` at the pinned repo, not `vae_1_0/`, external fp16-fix, refiner, or another decoder. Set `add_watermarker=False` and assert `pipe.watermark is None`, because the default is installation-dependent and can stamp a native SDXL invisible mark onto every C0/C1 output. SDXL pipeline has no safety checker; this differs from R0 and must be reported. No unofficial replacement checker.

## Scheduler and randomness

Instantiate DDIM explicitly, using historical `three_threat_models.DDIM_CONFIG` values for both R0/R1: training1000, scaled_linear betas .00085/.012, trained_betas=None, clip_sample=false, set_alpha_to_one=false, steps_offset=1, prediction_type=epsilon, thresholding=false, timestep_spacing=leading, rescale_betas_zero_snr=false. Also record inactive defaults clip_sample_range=1, sample_max_value=1, dynamic_thresholding_ratio=.995. Avoid relying on an Euler-to-DDIM constructor silently retaining irrelevant Euler configuration.

With 20 requested steps, schedule is [951,901,...,51,1]. Strength truncation uses floor(20*s). Thus .1 retains [51,1], .2 [151,101,51,1], .4 [351,301,251,201,151,101,51,1]. These are 2/4/8 UNet evaluations, not20 evaluations and not timestep100/200/400. Input noising is sqrt(alpha_bar[t])*z + sqrt(1-alpha_bar[t])*epsilon, where alpha_bar is cumulative product of 1-beta. A useful reported effective noise ratio is sqrt((1-alpha_bar[t])/alpha_bar[t]); no Euler sigma argument is supplied. Matching t/beta schedules across R0/R1 still does not equate image distortion or latent signal scale.

Each independent call creates a fresh CUDA torch.Generator seeded12/13/14. It is consumed first by VAE posterior sampling, then by added Gaussian diffusion noise. DDIM eta0 consumes no further stochastic transition noise; it does not make the whole call seed-independent or turn the input posterior into mode. Same seed/input shape pairs noise across arms within one model; same seed across models is not proof of identical perturbation tensors or corruption. Preserve one-image batch size, no latent caching across arms, and no global-RNG reseeding in place of the supplied generator.

## Conditioning and geometry

Pass prompt='', prompt_2='', guidance_scale=1, negative_prompt='', eta=0, num_images_per_prompt=1, clip_skip=None, guidance_rescale=0; no custom timesteps/sigmas, denoising_start/end, LoRA, IP-adapter, latent input or external prompt embeddings. Guidance1 disables CFG; it still conditions on the learned encoding of an empty string. Empty embeddings are **not** zero vectors. SDXL uses both text encoders, concatenated penultimate hidden states plus pooled second-encoder output. Negative prompts are unused when CFG is off.

Use source512 RGB8 -> Pillow Lanczos1024 -> pipeline RGB PIL output1024 -> Pillow Lanczos512 -> lossless RGB PNG -> reopen for detection. Explicit original_size=(1024,1024), target_size=(1024,1024), crops_coords_top_left=(0,0). Size describes the pipeline's 1024 input, not an alternative512 microcondition. The pipeline does not invent missing detail during upsampling; resize is part of the channel and can damage a mark by itself.

D1: same512->1024 preprocess, all VAE fp32, z=encode(x).latent_dist.mode(), decode(z) directly, same postprocess/downsample/save. No RNG and no diffusion scaling are needed: multiplying then dividing by .13025 would cancel but introduce rounding. Temporarily restore VAE fp16 after D1 if reused by R1. No VAE tiling/slicing in the frozen core. Compare with one resize-only512->1024->512 control. For rinse, start pass2 from the **saved512 output** of corresponding R1 .1 seed12/13/14; upscale again, use strength.1 with fresh seeds112/113/114, then downsample/save. This is two passes with intermediate quantization/resampling, not a single strength.2 attack. Include twice-repeated resize-only control.

R0 retains its historical safety components, exact assets and `validate_generated`: a safety-blocked output is missing/blocked, never detection failure on a black placeholder. No dropping blocked source denominators, replacement images or disabling the checker based on results. It remains a newly executed historical-configuration anchor; modern torch/diffusers/hardware may not reproduce old pixels.
