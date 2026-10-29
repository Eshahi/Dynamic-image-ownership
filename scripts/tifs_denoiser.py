"""R3 native epsilon/x0 helpers. Import and pure-mock tests use stdlib only.

Real tensors, model construction and parity callbacks are SERVER ONLY.
The x0 operator is one conditional denoiser evaluation, not a full attack.
"""
from __future__ import annotations

import hashlib
import json
import math
from types import SimpleNamespace


def native_window(scheduler, pipeline_class, steps, strength):
    """Derive the executed window from the pinned pipeline, never interpolate t."""
    if steps != 20 or scheduler.config.prediction_type != "epsilon":
        raise ValueError("R3 requires native 20-step epsilon DDIM")
    if scheduler.config.clip_sample or scheduler.config.thresholding or scheduler.order != 1:
        raise ValueError("Unsupported native x0 scheduler")
    scheduler.set_timesteps(steps, device="cpu")
    timesteps, executed = pipeline_class.get_timesteps(
        SimpleNamespace(scheduler=scheduler), steps, strength, "cpu")
    if not len(timesteps) or len(timesteps) != executed:
        raise ValueError("Unexpected native DDIM window")
    values = [int(t) for t in timesteps]
    return [dict(timestep=t, alpha_bar=float(scheduler.alphas_cumprod[t]),
                 a=math.sqrt(float(scheduler.alphas_cumprod[t])),
                 b=math.sqrt(1 - float(scheduler.alphas_cumprod[t]))) for t in values]


def sample_window(window, source_id, family, strength, step, stream):
    if not window or stream not in ("optimization", "diagnostic") or family not in ("R0", "R1"):
        raise ValueError("Invalid x0 timestep sampling request")
    value = json.dumps(["f6-x0-timestep-v1", stream, str(source_id), family,
                        float(strength), int(step)], separators=(",", ":"))
    seed = int.from_bytes(hashlib.sha256(value.encode("ascii")).digest()[:8], "big")
    return dict(window[seed % len(window)], window_index=seed % len(window), timestep_seed=seed)


def enable_unet_checkpointing(unet):
    if unet.training or any(p.requires_grad for p in unet.parameters()):
        raise ValueError("Writer UNet must be frozen and eval")
    unet.enable_gradient_checkpointing()
    blocks = [m for m in unet.modules() if hasattr(m, "gradient_checkpointing")]
    if not blocks or not all(m.gradient_checkpointing for m in blocks):
        unet.disable_gradient_checkpointing()
        raise ValueError("Native UNet checkpoint flags incomplete")


def assemble_conditioning(pipe, family, spec, torch, device="cuda"):
    """Mirror native encode_prompt and SDXL added conditioning, batch size one.

    R0/R1 currently have guidance=1, so no negative branch is evaluated. A CFG
    value >1 uses the exact native negative-first, positive-second assembly.
    Distilled time-conditioned models and nonzero guidance rescale are excluded.
    """
    if family not in ("R0", "R1") or pipe.unet.config.time_cond_proj_dim is not None:
        raise ValueError("Unsupported denoiser family or timestep conditioning")
    guidance = float(spec["guidance_scale"])
    cfg = guidance > 1
    kwargs = dict(prompt=spec["prompt"], device=device, num_images_per_prompt=1,
                  do_classifier_free_guidance=cfg, negative_prompt="", clip_skip=None)
    if family == "R1":
        kwargs.update(prompt_2="", negative_prompt_2=None)
    encoded = pipe.encode_prompt(**kwargs)
    positive, negative = encoded[:2]
    hidden = torch.cat([negative, positive], dim=0) if cfg else positive
    added = None
    if family == "R1":
        pooled, negative_pooled = encoded[2:]
        # Same defaults as native __call__: negative sizes inherit positives,
        # aesthetic defaults 6/2.5 (unused for the pinned SDXL base model).
        projection_dim = (pipe.text_encoder_2.config.projection_dim
                          if pipe.text_encoder_2 is not None else int(pooled.shape[-1]))
        pos_ids, neg_ids = pipe._get_add_time_ids(
            (1024, 1024), (0, 0), (1024, 1024), 6.0, 2.5,
            (1024, 1024), (0, 0), (1024, 1024),
            dtype=positive.dtype, text_encoder_projection_dim=projection_dim)
        text = torch.cat([negative_pooled, pooled], dim=0) if cfg else pooled
        ids = torch.cat([neg_ids, pos_ids], dim=0) if cfg else pos_ids
        added = dict(text_embeds=text.to(device), time_ids=ids.to(device))
    return dict(encoder_hidden_states=hidden.to(device), added_cond_kwargs=added,
                guidance_scale=guidance, do_cfg=cfg, family=family)


def predict_epsilon(unet, scheduler, noisy, timestep, conditioning, torch):
    """Native fp16 UNet, explicit casts; gradient remains through the cast.

    No autocast promotion policy is relied upon. The caller disables autocast.
    The returned epsilon stays fp16 until x0 arithmetic explicitly promotes it.
    """
    latent = noisy.to(dtype=unet.dtype)
    if conditioning["do_cfg"]:
        latent = torch.cat([latent, latent], dim=0)
    latent = scheduler.scale_model_input(latent, timestep)
    pred = unet(latent, timestep,
        encoder_hidden_states=conditioning["encoder_hidden_states"],
        timestep_cond=None, cross_attention_kwargs=None,
        added_cond_kwargs=conditioning["added_cond_kwargs"], return_dict=False)[0]
    if conditioning["do_cfg"]:
        negative, positive = pred.chunk(2)
        pred = negative + conditioning["guidance_scale"] * (positive - negative)
    return pred


def x0_from_epsilon(noisy, epsilon, alpha_bar):
    if not 0 < float(alpha_bar) <= 1:
        raise ValueError("Invalid alpha-bar")
    # Inputs are float32 in the writer; pure scalar mocks exercise the formula.
    return (noisy - math.sqrt(1 - float(alpha_bar)) * epsilon) / math.sqrt(float(alpha_bar))


def load_native_denoiser(assets, family, spec, vae, torch):
    """SERVER ONLY. Load pinned local weights; never call a pipeline forward.

    Text encoders move to CUDA only to cache native conditioning and are then
    released. UNet lives on CPU between gradient graphs. The supplied fp32 VAE
    is shared, never cast by a pipeline-wide .to().
    """
    from diffusers import DDIMScheduler, StableDiffusionImg2ImgPipeline, StableDiffusionXLImg2ImgPipeline
    import et_final_pilot as pilot
    cls = StableDiffusionImg2ImgPipeline if family == "R0" else StableDiffusionXLImg2ImgPipeline
    folder = assets / ("a6/sd15-fp16" if family == "R0" else "sdxl")
    extra = (dict(safety_checker=None, feature_extractor=None, requires_safety_checker=False)
             if family == "R0" else dict(add_watermarker=False))
    pipe = cls.from_pretrained(folder, vae=vae, variant="fp16", torch_dtype=torch.float16,
        use_safetensors=True, local_files_only=True, **extra)
    pipe.unet.eval().requires_grad_(False)
    encoders = [getattr(pipe, name, None) for name in ("text_encoder", "text_encoder_2")]
    try:
        for encoder in encoders:
            if encoder is not None:
                encoder.eval().requires_grad_(False).to("cuda")
        with torch.no_grad(), torch.autocast(device_type="cuda", enabled=False):
            cond = assemble_conditioning(pipe, family, spec, torch)
    finally:
        for encoder in encoders:
            if encoder is not None:
                encoder.to("cpu")
    scheduler = DDIMScheduler.from_config(pipe.scheduler.config, **spec["scheduler_overrides"])
    scheduler.set_timesteps(spec["steps"], device="cpu")
    attention = pilot.ClassicAttention(pipe.unet)
    attention.__enter__()  # Stage-S native() uses this exact processor/LN scope.
    return SimpleNamespace(unet=pipe.unet, conditioning=cond, scheduler=scheduler,
                           attention_scope=attention)


def native_first_step_parity(pipe, family, spec, run_native):
    """SERVER ONLY. Wrap one existing native call; return (its result, receipt).

    Capture actual first UNet + DDIM step, independently rebuild conditioning,
    and replay the epsilon/x0 operator on the captured noisy latent. This does
    not claim posterior-mode/float-resize equality with sampled RGB8 attacks.
    Invoke inside the runtime's ClassicAttention scope. Hooks always restore.
    """
    import torch
    if family not in ("R0", "R1"):
        raise ValueError("Only optimized families have x0 parity")
    if any(getattr(m, "gradient_checkpointing", False) for m in pipe.unet.modules()):
        raise ValueError("Native parity must run outside writer checkpoint scope")
    captured = {}
    original_forward, original_step = pipe.unet.forward, pipe.scheduler.step
    def forward(*args, **kwargs):
        value = original_forward(*args, **kwargs)
        if "unet" not in captured:
            captured["unet"] = (args, kwargs, value[0].detach().clone())
        return value
    def step(model_output, timestep, sample, *args, **kwargs):
        value = original_step(model_output, timestep, sample, *args, **kwargs)
        if "sample" not in captured:
            pred = value[1] if isinstance(value, tuple) else value.pred_original_sample
            captured.update(sample=sample.detach().clone(), timestep=timestep,
                epsilon=model_output.detach().clone(), native_x0=pred.detach().clone())
        return value
    pipe.unet.forward, pipe.scheduler.step = forward, step
    try:
        result = run_native()
    finally:
        pipe.unet.forward, pipe.scheduler.step = original_forward, original_step
    if "sample" not in captured or "unet" not in captured:
        raise ValueError("Native first step was not observed")
    with torch.no_grad(), torch.autocast(device_type="cuda", enabled=False):
        cond = assemble_conditioning(pipe, family, spec, torch)
        _, actual_kwargs, _ = captured["unet"]
        if not torch.equal(cond["encoder_hidden_states"], actual_kwargs["encoder_hidden_states"]):
            raise ValueError("Native prompt-conditioning parity failed")
        if family == "R1":
            for key in ("text_embeds", "time_ids"):
                if not torch.equal(cond["added_cond_kwargs"][key], actual_kwargs["added_cond_kwargs"][key]):
                    raise ValueError("Native SDXL added-conditioning parity failed: " + key)
        pred = predict_epsilon(pipe.unet, pipe.scheduler, captured["sample"],
                               captured["timestep"], cond, torch)
        if not torch.allclose(pred, captured["epsilon"], atol=1e-3, rtol=1e-3):
            raise ValueError("Native first epsilon parity failed")
        alpha = float(pipe.scheduler.alphas_cumprod[int(captured["timestep"])])
        x0 = x0_from_epsilon(captured["sample"].float(), pred.float(), alpha)
        # Native DDIM arithmetic is fp16. Bound rounding relative to the two
        # operands before subtraction, avoiding a near-zero cancellation ratio.
        scale = ((captured["sample"].float().abs() + math.sqrt(1-alpha)*pred.float().abs())
                 / math.sqrt(alpha))
        bound = 16 * (2 ** -11) * scale + 1e-5
        error = (x0 - captured["native_x0"].float()).abs()
        if not torch.isfinite(x0).all() or not bool((error <= bound).all()):
            raise ValueError("Native first x0 arithmetic parity failed")
        return result, dict(status="ok", family=family, timestep=int(captured["timestep"]),
            alpha_bar=alpha, exact_conditioning=True,
            epsilon_max_abs_error=float((pred-captured["epsilon"]).abs().max()),
            x0_max_abs_error=float(error.max()), x0_rounding_bound_max=float(bound.max()),
            epsilon_atol=1e-3, epsilon_rtol=1e-3, x0_bound="16 fp16 unit-roundoffs times operand magnitude + 1e-5",
            scope="native captured first noisy latent; no image/preprocessing parity claim")
