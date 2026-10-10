"""Differentiable reproduction of the pinned SD1.5 DDIM img2img channel.

The raw tensor is an internal differentiation value, never an accepted image.
Acceptance always calls the existing safety checker through ``checked``.
Only RGB8 rounding uses a straight-through gradient; diffusion does not.
"""
from __future__ import annotations

from dataclasses import dataclass
import torch
from torch.utils.checkpoint import checkpoint


def rgb8_ste(x):
    x = x.clamp(0, 1)
    return x + (torch.round(x * 255) / 255 - x).detach()


@dataclass
class DDIMResult:
    raw: torch.Tensor
    continuous: torch.Tensor
    image: torch.Tensor
    timesteps: list[int]
    posterior_noise: torch.Tensor
    scheduler_noise: torch.Tensor


class DifferentiableDDIM:
    """Batch-one, empty-prompt, CFG-off, eta-zero, 20-step pinned channel."""
    def __init__(self, pipe):
        from three_threat_models import DDIM_CONFIG
        from diffusers import DDIMScheduler
        if not isinstance(pipe.scheduler, DDIMScheduler):
            raise ValueError("Pinned DDIM scheduler required")
        for k, v in DDIM_CONFIG.items():
            if getattr(pipe.scheduler.config, k) != v:
                raise ValueError("DDIM configuration mismatch: " + k)
        if pipe.safety_checker is None or pipe.feature_extractor is None:
            raise ValueError("Required safety components missing")
        if pipe.unet.config.time_cond_proj_dim is not None:
            raise ValueError("Unexpected time conditioning")
        self.pipe = pipe
        self.device = pipe._execution_device
        for model in (pipe.vae, pipe.unet, pipe.text_encoder, pipe.safety_checker):
            model.eval().requires_grad_(False)
        pipe.vae.enable_gradient_checkpointing()
        pipe.unet.enable_gradient_checkpointing()
        # no_grad, not inference_mode: UNet backward may save these constants.
        with torch.no_grad():
            self.prompt, _ = pipe.encode_prompt("", self.device, 1, False, negative_prompt="")
        if self.prompt.dtype != torch.float16 or pipe.vae.dtype != torch.float16:
            raise ValueError("Pinned float16 preparation required")
        self.diagnostic = False

    def set_precision(self, dtype, *, diagnostic=False):
        """Temporary fp32 graph diagnostic; native attack remains fp16.

        The diagnostic promotes the pinned half weights losslessly, rather than
        loading a different checkpoint. Restoring half is exact for these frozen
        parameters. Prompt values are promoted too; text encoding is unchanged.
        """
        if dtype not in (torch.float16, torch.float32) or (dtype == torch.float32 and not diagnostic):
            raise ValueError("Float32 is permitted only as an explicit diagnostic")
        self.pipe.vae.to(dtype=dtype)
        self.pipe.unet.to(dtype=dtype)
        self.prompt = self.prompt.to(dtype=dtype)
        self.diagnostic = diagnostic

    @staticmethod
    def _call(fn, x):
        if torch.is_grad_enabled() and x.requires_grad:
            return checkpoint(fn, x, use_reentrant=False)
        return fn(x)

    def forward(self, x, strength, seed, *, quantize_input=True, quantize_output=True):
        from diffusers.models.autoencoders.vae import DiagonalGaussianDistribution
        from diffusers.utils.torch_utils import randn_tensor
        if x.shape != (1, 3, 512, 512) or x.dtype != torch.float32:
            raise ValueError("Requires one float32 RGB 512x512 input")
        if strength not in (.1, .2) or type(seed) is not int:
            raise ValueError("Feasibility channel permits strengths .1/.2 and integer seeds")
        p = self.pipe
        generator = torch.Generator(device=self.device).manual_seed(seed)
        image = rgb8_ste(x) if quantize_input else x.clamp(0, 1)
        # Same float32 RGB mapping as image_processor.preprocess(PIL), then cast.
        image = (image * 2 - 1).to(device=self.device, dtype=self.prompt.dtype)
        p.scheduler.set_timesteps(20, device=self.device)
        ts, _ = p.get_timesteps(20, strength, self.device)
        if len(ts) != {0.1: 2, 0.2: 4}[strength]:
            raise ValueError("Unexpected executed DDIM timestep count")
        # Checkpoint parameters, sample OUTSIDE checkpoint so generator is used
        # exactly twice overall and recomputation never advances it.
        params = self._call(lambda a: p.vae.encode(a).latent_dist.parameters, image)
        posterior = DiagonalGaussianDistribution(params)
        eps_p = randn_tensor(posterior.mean.shape, generator=generator,
                            device=posterior.mean.device, dtype=posterior.mean.dtype)
        latents = p.vae.config.scaling_factor * (posterior.mean + posterior.std * eps_p)
        latents = torch.cat([latents], dim=0)
        noise = randn_tensor(latents.shape, generator=generator, device=self.device, dtype=self.prompt.dtype)
        latents = p.scheduler.add_noise(latents, noise, ts[:1])
        extra = p.prepare_extra_step_kwargs(generator, 0.)
        for t in ts:
            a = p.scheduler.scale_model_input(latents, t)
            # Bind each timestep at definition: checkpoint backward cannot see
            # the loop's final timestep through a late-bound closure.
            def denoise(z, timestep=t):
                return p.unet(z, timestep, encoder_hidden_states=self.prompt,
                              timestep_cond=None, cross_attention_kwargs=None,
                              added_cond_kwargs=None, return_dict=False)[0]
            pred = self._call(denoise, a)
            latents = p.scheduler.step(pred, t, latents, **extra, return_dict=False)[0]
        raw = self._call(lambda a: p.vae.decode(a, return_dict=False)[0],
                         latents / p.vae.config.scaling_factor)
        # Preserve pinned fp16 denormalization before conversion to reader fp32.
        continuous = (raw / 2 + .5).clamp(0, 1).float()
        image = rgb8_ste(continuous) if quantize_output else continuous
        return DDIMResult(raw, continuous, image, [int(t) for t in ts], eps_p, noise)

    def checked(self, result, output_type="np"):
        if self.diagnostic:
            raise ValueError("Float32 graph diagnostics are not accepted attack outputs")
        with torch.no_grad():
            image, flags = self.pipe.run_safety_checker(result.raw.detach().clone(),
                                                       self.device, self.prompt.dtype)
            if flags is None or len(flags) != 1 or bool(flags[0]):
                raise RuntimeError("Missing or blocked safety verdict")
            accepted = self.pipe.image_processor.postprocess(
                image, output_type=output_type, do_denormalize=[True])
        return accepted, [bool(f) for f in flags]


def official_parity(channel, rgb, base, strength, seed):
    """Observe, without changing, official RNG draws and pre-checker pixels.

    Checker verdicts are recorded even when blocked. Pre-checker equality only
    validates the mathematical adapter; it never changes that verdict.
    """
    import numpy as np
    from PIL import Image
    from unittest.mock import patch
    from diffusers.models.autoencoders import vae as vae_module
    from diffusers.pipelines.stable_diffusion import pipeline_stable_diffusion_img2img as pipeline_module
    if channel.diagnostic or channel.prompt.dtype != torch.float16:
        raise ValueError("Official parity requires the native fp16 operator")
    p = channel.pipe
    captured = {"posterior": [], "noise": [], "raw": []}
    original_p, original_n, original_checker = vae_module.randn_tensor, pipeline_module.randn_tensor, p.run_safety_checker
    def posterior_draw(*args, **kwargs):
        value = original_p(*args, **kwargs)
        captured["posterior"].append(value.detach().clone())
        return value
    def initial_draw(*args, **kwargs):
        value = original_n(*args, **kwargs)
        captured["noise"].append(value.detach().clone())
        return value
    def observe_checker(raw, *args, **kwargs):
        captured["raw"].append(raw.detach().clone())
        return original_checker(raw, *args, **kwargs)
    with torch.no_grad(), patch.object(vae_module, "randn_tensor", posterior_draw), \
            patch.object(pipeline_module, "randn_tensor", initial_draw), \
            patch.object(p, "run_safety_checker", observe_checker):
        official = p(prompt="", negative_prompt="", image=Image.fromarray(rgb),
            strength=strength, num_inference_steps=20, guidance_scale=1., eta=0.,
            generator=torch.Generator(device=channel.device).manual_seed(seed), output_type="pil")
        official_ts, _ = p.get_timesteps(20, strength, channel.device)
    if any(len(captured[k]) != 1 for k in captured):
        raise ValueError("Unexpected official RNG/checker call inventory")
    with torch.no_grad():
        own = channel.forward(base, strength, seed)
        reference8 = p.image_processor.postprocess(captured["raw"][0], output_type="pil", do_denormalize=[True])[0]
        own8 = torch.round(own.image[0].permute(1, 2, 0) * 255).byte().cpu().numpy()
        mismatches = int(np.count_nonzero(own8 != np.asarray(reference8)))
        checks = dict(posterior_equal=bool(torch.equal(own.posterior_noise, captured["posterior"][0])),
            noise_equal=bool(torch.equal(own.scheduler_noise, captured["noise"][0])),
            timesteps_equal=own.timesteps == [int(t) for t in official_ts], rgb8_equal=mismatches == 0)
        result = dict(**checks, parity_pass=all(checks.values()),
            rgb8_mismatched_components=mismatches,
            raw_max_abs=float((own.raw-captured["raw"][0]).abs().max()),
            timesteps=own.timesteps, official_safety_flags=official.nsfw_content_detected,
            stage_shapes=dict(rgb=list(base.shape), latent_noise=list(own.posterior_noise.shape), raw=list(own.raw.shape)),
            stage_dtypes=dict(input=str(base.dtype), noise=str(own.posterior_noise.dtype), raw=str(own.raw.dtype)),
            note="Pre-checker parity is internal diagnostic evidence, never attack acceptance")
    return result


def continuous_projection(obj, x):
    """Existing F5 projection math, without RGB8 rounding for derivative probe."""
    z = obj.call(lambda a: obj.reader.vae.encode(a).latent_dist.mode(), x * 2 - 1)[0]
    from scripts import f5_latent_codec as f5
    c = torch.einsum("ij,cjk,lk->cil", obj.D, z * f5.SCALE, obj.D)
    total = torch.zeros(320, device=x.device).index_add(
        0, obj.chip, c[obj.ch, obj.u, obj.v] * obj.coeff)
    return total / obj.norms
