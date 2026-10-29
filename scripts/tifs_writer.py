"""SERVER ONLY: F6 fixed-reader pixel writers for the frozen Stage-S screen.

Importing this module imports only the standard library. Constructing F6Writer,
embedding, and validate_rehearsal require the authorized GPU server. No CLI is
provided deliberately. Retained F5/v5 sources are never modified or patched.
"""
from __future__ import annotations

import gc
from functools import wraps
import hashlib
import json
import math
from pathlib import Path
import sys
import time
from types import SimpleNamespace


VARIANTS = ("f6-noise", "f6-codec", "f6-generic")
CYCLE = (("R0", .2), ("R1", .1), ("R1", .2))
EXPECTED_F5 = dict(psnr_db=52.0, steps=150, target_margin=4.0,
                   mask_power=0.0, band=[4, 32], whitening=1.0,
                   refine_rounds=1, binding="soft", semantic_views=7)
EXPECTED_WRITER = dict(EXPECTED_F5, refine_steps=50, refine_psnr_db=58.0,
    posterior="mode", cycle=[dict(family=f, strength=s) for f, s in CYCLE],
    generic_cycle=[dict(kind="gaussian_blur", sigma=1.5, kernel_size=11, padding="reflect"),
        dict(kind="bilinear_resize", sizes=[512, 256, 512], antialias=True, align_corners=False),
        dict(kind="gaussian_noise", sigma=.02, clip=[0, 1])],
    reader_gradient_evaluations=350, codec_gradient_evaluations=150, fragile_writes=2)


def enable_writer_checkpointing(vae):
    """SERVER ONLY with real VAEs; pure mocks can test this control logic.

    diffusers 0.35.1 checkpoints Encoder/Decoder in eval when grad is enabled.
    Its default non-reentrant checkpoint supports our autograd.grad calls.
    """
    if vae.training or any(p.requires_grad for p in vae.parameters()):
        raise ValueError("Writer checkpointing requires frozen eval VAE")
    vae.enable_gradient_checkpointing()
    if not all(getattr(getattr(vae, name), "gradient_checkpointing", False)
               for name in ("encoder", "decoder")):
        vae.disable_gradient_checkpointing()
        raise ValueError("Writer encoder and decoder checkpointing required")


def writer_gradient_scope(function):
    """Keep checkpoint flags through backward; clear even after writer closes."""
    @wraps(function)
    def scoped(self, *args, **kwargs):
        if getattr(self, "_checkpoint_vaes", None) is not None:
            raise RuntimeError("Nested writer gradient scope")
        vaes = self._checkpoint_vaes = []
        try:
            self._checkpoint_vae(self.reader.vae)
            if self.sdxl is not None:
                self._checkpoint_vae(self.sdxl)
            return function(self, *args, **kwargs)
        finally:
            # Local references survive close() clearing self.reader/self.sdxl.
            for vae in vaes:
                vae.disable_gradient_checkpointing()
            self._checkpoint_vaes = None
    return scoped


def validate_writer_config(base_config, frozen_config):
    """Standard-library preflight; permits additional descriptive config keys."""
    if base_config.get("f5") != EXPECTED_F5:
        raise ValueError("F6 requires the exact retained F5-r2 configuration")
    writer = frozen_config.get("writer", {})
    for name, value in EXPECTED_WRITER.items():
        if writer.get(name) != value:
            raise ValueError("F6 frozen writer mismatch: " + name)


def draw_seed(source_id, variant, step, stream="optimization"):
    """Domain-separated, process-independent seed; never use Python hash()."""
    if stream not in ("optimization", "diagnostic") or variant not in VARIANTS:
        raise ValueError("Unknown random stream or writer")
    value = json.dumps(["f6-stage-s-v1", stream, str(source_id), variant, int(step)],
                       ensure_ascii=True, separators=(",", ":"))
    return int.from_bytes(hashlib.sha256(value.encode("ascii")).digest()[:8], "big") & ((1 << 63) - 1)


class F6Writer:
    """Share an optional rt.Internal reader/CPU CLIP without altering its adapter.

    assets is the retained stage-2 asset root (containing a6/ and sdxl/).
    base_config is unchanged stage2b-config.json. frozen_config is retained in
    reports; only the fixed algorithm below is implemented, with no tuning API.
    internal, when provided, must have reader, profile and features(rgb,views).
    close() offloads the shared reader too: finish using the writer before K3.
    """

    def __init__(self, assets, base_config, frozen_config, internal=None):
        validate_writer_config(base_config, frozen_config)
        # All scientific imports are lazy and this constructor is SERVER ONLY.
        import numpy as np
        import torch
        from diffusers import AutoencoderKL, DDIMScheduler
        from diffusers import StableDiffusionImg2ImgPipeline, StableDiffusionXLImg2ImgPipeline

        script_dir = str(Path(__file__).resolve().parent)
        if script_dir not in sys.path:
            sys.path.insert(0, script_dir)
        import f5_latent_codec as f5
        import et_final_pilot as pilot
        from encoder_transfer_test import ALPHA, ROOT

        self.np, self.torch, self.f5 = np, torch, f5
        self._AutoencoderKL = AutoencoderKL
        self.assets, self.base_config = Path(assets), base_config
        self.frozen_config = json.loads(json.dumps(frozen_config))
        self.owner_id = ALPHA
        self.internal = internal
        self.reader = self.clip = self.sdxl = None
        self._closed = False
        self._owns_reader = internal is None
        self._schedule = {}
        self.resize_up = self.resize_down = None
        try:
            if internal is not None:
                if internal.config["f5"] != EXPECTED_F5:
                    raise ValueError("Shared Internal uses a different reader configuration")
                self.reader, self.profile = internal.reader, internal.profile
                self.features = internal.features
            else:
                # rt.Internal would also load LPIPS on GPU; writing needs none.
                import three_threat_models as models
                from a6_clip_visual import load_visual_encoder
                from f5_gate import semantic_feature
                self.reader = f5.Reader(self.assets / "a6", device="cuda")
                self.clip, transform = load_visual_encoder(self.assets / "a6/clip/ViT-B-32.pt", device="cpu")
                self.clip.eval().requires_grad_(False)
                self.features = lambda rgb, views: semantic_feature(models, self.clip, transform, rgb, views)
                self.profile = json.loads((ROOT / base_config["profile_file"]).read_text(encoding="utf-8"))
            self.reader.vae.eval().requires_grad_(False).to(device="cuda", dtype=torch.float32)
            self.checked, self.key, self.config = f5.v5._resolve(self.profile, None)
            self.owner = f5.v5.canonical_owner(ALPHA)
            self.layout = f5.Layout(self.checked, self.key, self.config, self.owner, [4, 32], 1.0)
            self._make_projection_tensors()
            # Read VAE metadata only. A generic-only call needs no SDXL weights.
            self._sdxl_config = AutoencoderKL.load_config(self.assets / "sdxl/vae", local_files_only=True)
            if not self._sdxl_config["force_upcast"]:
                raise ValueError("Retained SDXL VAE must have force_upcast=True")
            self.resize_up, self.resize_down = pilot.Resize(512, 1024, torch), pilot.Resize(1024, 512, torch)
            specs = {row["id"]: row for row in base_config["channels"]}
            for family, strength in CYCLE:
                spec = specs[family]
                if spec["steps"] != 20:
                    raise ValueError("Frozen native schedule requires 20 steps")
                folder = self.assets / ("a6/sd15-fp16" if family == "R0" else "sdxl")
                sched = DDIMScheduler.from_pretrained(folder, subfolder="scheduler", local_files_only=True,
                                                       **spec["scheduler_overrides"])
                sched.set_timesteps(20, device="cpu")
                # Invoke native get_timesteps without constructing/loading a pipeline.
                cls = StableDiffusionImg2ImgPipeline if family == "R0" else StableDiffusionXLImg2ImgPipeline
                timesteps, executed = cls.get_timesteps(SimpleNamespace(scheduler=sched), 20, strength, "cpu")
                if len(timesteps) != executed or not len(timesteps):
                    raise ValueError("Unexpected native DDIM first timestep")
                first = int(timesteps[0])
                alpha = float(sched.alphas_cumprod[first])
                self._schedule[(family, strength)] = dict(family=family, strength=strength,
                    timestep=first, timesteps=[int(t) for t in timesteps], executed_steps=executed,
                    alpha_bar=alpha, a=math.sqrt(alpha), b=math.sqrt(1 - alpha),
                    scaling_factor=float(self.reader.vae.config.scaling_factor if family == "R0" else self._sdxl_config["scaling_factor"]))
            if abs(float(self.reader.vae.config.scaling_factor) - f5.SCALE) > 1e-12:
                raise ValueError("SD1.5 codec scaling differs from retained F5 reader")
        except BaseException:
            self.close()
            raise

    def _make_projection_tensors(self):
        t, n, l = self.torch, self.np, self.layout
        self.D = t.from_numpy(l.dct.astype(n.float32)).cuda()
        self.ch, self.u, self.v = (t.from_numpy(a).cuda() for a in (l.ch, l.u, l.v))
        self.coeff = t.from_numpy((l.weights * l.signs).astype(n.float32)).cuda()
        self.chip = t.from_numpy(l.chip).cuda()
        self.norms = t.from_numpy(l.norms.astype(n.float32)).cuda()

    def _checkpoint_vae(self, vae):
        if self._checkpoint_vaes is None:
            raise RuntimeError("VAE checkpointing outside writer gradient scope")
        if not any(item is vae for item in self._checkpoint_vaes):
            # Register before enabling, so even a partial failure is cleaned up.
            self._checkpoint_vaes.append(vae)
            enable_writer_checkpointing(vae)

    def _finite(self, value, label):
        if not bool(self.torch.isfinite(value).all()):
            raise FloatingPointError("Nonfinite F6 " + label)
        return value

    def _projections(self, image):
        t = self.torch
        # encode(), unlike latent(), preserves the input graph.
        z = self.reader.encode(image)
        self._finite(z, "reader latent")
        coef = t.einsum("ij,cjk,lk->cil", self.D, z, self.D)
        totals = t.zeros(self.f5.v5.CHANNEL_CHIPS, device=image.device, dtype=image.dtype)
        totals = totals.index_add(0, self.chip, coef[self.ch, self.u, self.v] * self.coeff)
        return self._finite(totals / self.norms, "reader projections")

    def _loss(self, image, w):
        return self.torch.relu(4.0 - w * self._projections(image)).square().mean()

    def _random(self, shape, source_id, variant, step, stream, device):
        t = self.torch
        generator = t.Generator(device=device).manual_seed(draw_seed(source_id, variant, step, stream))
        return t.randn(shape, generator=generator, device=device, dtype=t.float32)

    def _codec(self, image, family, strength, variant, source_id, step, stream):
        t = self.torch
        row = self._schedule[(family, strength)]
        if family == "R1":
            if self.sdxl is None:
                self.sdxl = self._AutoencoderKL.from_pretrained(self.assets / "sdxl/vae", variant="fp16",
                    torch_dtype=t.float32, use_safetensors=True, local_files_only=True).eval().requires_grad_(False)
                self._checkpoint_vae(self.sdxl)
            vae = self.sdxl
            vae.to(device=image.device, dtype=t.float32)
            image = self.resize_up(image)
        else:
            vae = self.reader.vae
        # Native preprocessing normalizes first, then casts R1 through fp16.
        encoded_input = image * 2 - 1
        if family == "R1":
            encoded_input = encoded_input.to(t.float16).to(t.float32)
        z = vae.encode(encoded_input).latent_dist.mode() * row["scaling_factor"]
        self._finite(z, "codec posterior mode")
        if variant == "f6-noise":
            epsilon = self._random(z.shape, source_id, variant, step, stream, z.device)
            z = row["a"] * z + row["b"] * epsilon
        elif variant != "f6-codec":
            raise ValueError(variant)
        # No division by a, latent normalization, denoiser, or RGB8 rounding.
        decoded = vae.decode(z / row["scaling_factor"], return_dict=False)[0]
        self._finite(decoded, "codec decoded output")
        out = (decoded / 2 + .5).clamp(0, 1)
        return self.resize_down(out) if family == "R1" else out

    def _generic(self, image, source_id, step, stream):
        t = self.torch
        functional = t.nn.functional
        if step % 3 == 0:
            grid = t.arange(-5, 6, device=image.device, dtype=t.float32)
            kernel = t.exp(-grid.square() / (2 * 1.5 ** 2))
            kernel = kernel / kernel.sum()
            kernel2d = (kernel[:, None] * kernel[None, :])[None, None].expand(3, 1, 11, 11)
            return functional.conv2d(functional.pad(image, (5, 5, 5, 5), mode="reflect"), kernel2d, groups=3)
        if step % 3 == 1:
            small = functional.interpolate(image, size=(256, 256), mode="bilinear", align_corners=False, antialias=True)
            return functional.interpolate(small, size=(512, 512), mode="bilinear", align_corners=False, antialias=True)
        epsilon = self._random(image.shape, source_id, "f6-generic", step, stream, image.device)
        return (image + .02 * epsilon).clamp(0, 1)

    def _offload_codec(self):
        if self.sdxl is not None:
            self.sdxl.to("cpu")

    def _schedule_receipt(self, variant):
        return [dict(row, applied_a=row["a"] if variant == "f6-noise" else 1.0,
                     applied_b=row["b"] if variant == "f6-noise" else 0.0,
                     codec_used=variant != "f6-generic") for row in self._schedule.values()]

    @writer_gradient_scope
    def _optimize(self, rgb01, w, source_id, variant, *, refine=False):
        t = self.torch
        x = self.reader.tensor(rgb01)
        steps, psnr = (50, 58.0) if refine else (150, 52.0)
        budget = 10 ** (-psnr / 20) * math.sqrt(rgb01.size)
        eta = t.zeros_like(x, requires_grad=True)
        for step in range(steps):
            # Serial graph accumulation: autograd.grad frees the clean graph
            # before constructing the surrogate; only the leaf eta persists.
            clean_loss = self._loss((x + eta).clamp(0, 1), w)
            gradient, = t.autograd.grad(clean_loss, eta)
            del clean_loss
            if not refine:
                family, strength = CYCLE[step % 3]
                image = (x + eta).clamp(0, 1)
                surrogate = (self._generic(image, source_id, step, "optimization") if variant == "f6-generic" else
                             self._codec(image, family, strength, variant, source_id, step, "optimization"))
                surrogate_loss = self._loss(surrogate, w)
                added, = t.autograd.grad(surrogate_loss, eta)
                gradient = gradient + added
                del surrogate_loss, surrogate, image, added
                # No graph remains when offloading the inactive VAE.
                if variant != "f6-generic" and family == "R1":
                    self._offload_codec()
            self._finite(gradient, "input gradient")
            with t.no_grad():
                lr = budget * (.2 if step < steps // 2 else .05)
                eta -= lr * gradient / (gradient.norm() + 1e-12)
                delta = (x + eta).clamp(0, 1) - x
                eta.copy_(delta * (budget / delta.norm().clamp_min(budget)))
            del gradient
        with t.no_grad():
            return self._finite((x + eta).clamp(0, 1), "optimized RGB")[0].permute(1, 2, 0).double().cpu().numpy()

    def _fragile(self, current, q):
        """Bounded copy of the retained F5 embed_rgb fragile body, unchanged."""
        n, v5, base = self.np, self.f5.v5, self.f5.base
        robust_rgb = current.copy()
        before = v5.luminance_from_rgb(robust_rgb.astype(n.uint8).tolist())
        height, width = base._check_image(before, int(self.checked["minimum_side"]))
        marked_luma = [[float(value) for value in row] for row in before]
        fragile = v5._Fragile(self.checked, self.key, self.config, self.owner, height, width)
        means, coefficients = base._analyse(marked_luma, fragile.analysis)
        h = base._perceptual_hash(means, coefficients, self.key, self.config)
        itable = v5._instance_table(self.owner, self.key, self.config)
        wi = [chip for segment in range(v5.CODE_BITS)
              for chip in itable[segment][v5._bit(q, segment)][v5._bit(h, segment)]]
        report = v5._embed_fragile(marked_luma, fragile, wi, self.checked, False, True)
        change = n.asarray(marked_luma) - n.asarray(before)
        current = n.clip(n.rint(robust_rgb + change[..., None]), 0, 255)
        return current, h, report

    def embed(self, rgb, variant, source_id):
        if self._closed or variant not in VARIANTS:
            raise ValueError("Closed writer or unknown variant")
        n, t, f5 = self.np, self.torch, self.f5
        source = n.asarray(rgb)
        if source.dtype != n.uint8 or source.shape != (512, 512, 3):
            raise ValueError("F6 requires native RGB8 512x512 input")
        tick = time.monotonic()
        self.reader.vae.to(device="cuda", dtype=t.float32)
        try:
            # Features are CPU-only; fixed original q is held through all stages.
            features = self.features(source, 7)
            luma = f5.v5.luminance_from_rgb(source.tolist())
            q, ws = f5._semantic_pattern(self.checked, self.key, self.config, self.owner, features, luma)
            w = t.as_tensor(n.asarray(ws, n.float32), device="cuda")
            robust = self._optimize(source.astype(n.float64) / 255, w, source_id, variant)
            current = n.clip(n.rint(robust * 255), 0, 255)
            current, _, _ = self._fragile(current, q)
            refined = self._optimize(current / 255, w, source_id, variant, refine=True)
            current = n.clip(n.rint(refined * 255), 0, 255)
            current, intended_h, fragile_report = self._fragile(current, q)
            output = current.astype(n.uint8)
            # Exactly the fixed F5 reader/profile, seven-view suspect semantics.
            verification = f5.detect_rgb(output, self.reader.latent(output), self.owner_id, self.profile,
                self.features(output, 7), band=[4, 32], whitening=1.0, binding="soft")
            decoded_h = verification["instance"].get("decoded_code")
            payload = dict(q=f"{q:08x}", h=decoded_h,
                h_target_basis="native clean decoded h; intended h exported separately",
                intended_h=f"{intended_h:08x}")
            t.cuda.synchronize()
            report = dict(family="f6-finite-fixed-reader", variant=variant, revision=1,
                source_id=str(source_id), semantic_code=payload["q"], intended_h=payload["intended_h"],
                payload=payload, verification=verification, verified=verification["outcome"] == "both_match",
                instance_channel=fragile_report, seconds=time.monotonic() - tick,
                reader_gradient_evaluations=350, codec_gradient_evaluations=0 if variant == "f6-generic" else 150,
                surrogate_gradient_evaluations=150, robust_updates=150, clean_refinement_updates=50,
                fragile_writes=2, initial_psnr_budget_db=52.0, refinement_psnr_budget_db=58.0,
                target_margin=4.0, mask_power=0.0, reader_dispatch="f5-r2", binding="soft", semantic_views=7,
                schedule=self._schedule_receipt(variant), posterior="mode", denoiser=False,
                preprocessing="differentiable Lanczos float approximation; R1 normalized RGB cast fp16 then fp32",
                quantization="RGB8 only after robust, fragile, refinement, final fragile",
                random_seed_domain="f6-stage-s-v1; optimization distinct from diagnostic",
                gradient_checkpointing="writer VAEs only; diffusers non-reentrant; disabled before native verification",
                frozen_config=self.frozen_config)
            return output, payload, report
        except BaseException:
            # OOM remains an exception for the orchestrator's RESOURCE_STOP.
            self.close()
            raise
        finally:
            self._offload_codec()

    @writer_gradient_scope
    def validate_rehearsal(self, rgb, source_id):
        """SERVER ONLY: graph/parity/finite checks, with no scientific selection.

        Run once on each prespecified rehearsal source before full embedding.
        Returns receipts; fails on zero/nonfinite input gradients or tensor-DCT
        projection disagreement. This is not native pipeline primal parity.
        """
        if self._closed:
            raise ValueError("Closed writer")
        n, t = self.np, self.torch
        source = n.asarray(rgb)
        if source.dtype != n.uint8 or source.shape != (512, 512, 3):
            raise ValueError("Rehearsal requires RGB8 512x512")
        try:
            features = self.features(source, 7)
            q, ws = self.f5._semantic_pattern(self.checked, self.key, self.config, self.owner, features,
                                             self.f5.v5.luminance_from_rgb(source.tolist()))
            x = self.reader.tensor(source.astype(n.float64) / 255).requires_grad_(True)
            w = t.as_tensor(n.asarray(ws, n.float32), device="cuda")
            with t.no_grad():
                actual = self._projections(x).double().cpu().numpy()
            expected = n.asarray(self.layout.projections(self.reader.latent(source)))
            error = float(n.max(n.abs(actual - expected)))
            if not n.allclose(actual, expected, atol=1e-3, rtol=1e-4):
                raise ValueError("Differentiable F5 projection parity failed")
            rows = []
            loss = self._loss(x, w)
            grad, = t.autograd.grad(loss, x)
            self._finite(grad, "rehearsal clean gradient")
            clean_norm = float(grad.norm())
            del loss, grad
            if not clean_norm > 0:
                raise ValueError("Zero clean input gradient")
            for variant in VARIANTS:
                for step, (family, strength) in enumerate(CYCLE):
                    surrogate = (self._generic(x, source_id, step, "diagnostic") if variant == "f6-generic" else
                                 self._codec(x, family, strength, variant, source_id, step, "diagnostic"))
                    loss = self._loss(surrogate, w)
                    grad, = t.autograd.grad(loss, x)
                    self._finite(grad, "rehearsal surrogate gradient")
                    norm, value = float(grad.norm()), float(loss.detach())
                    del loss, surrogate, grad
                    self._offload_codec()
                    if not norm > 0:
                        raise ValueError("Zero surrogate input gradient")
                    rows.append(dict(variant=variant, family=family, strength=strength,
                        generic_operation=step if variant == "f6-generic" else None,
                        loss=value, input_gradient_norm=norm,
                        diagnostic_seed=draw_seed(source_id, variant, step, "diagnostic")))
            if any(p.grad is not None or p.requires_grad for vae in (self.reader.vae, self.sdxl)
                   if vae is not None for p in vae.parameters()):
                raise ValueError("Frozen VAE unexpectedly accumulates parameter gradients")
            return dict(status="ok", source_id=str(source_id), q=f"{q:08x}",
                clean_input_gradient_norm=clean_norm, projection_max_abs_error=error,
                schedule=list(self._schedule.values()), gradient_checks=rows,
                gradient_checkpointing="writer encoder/decoder eval; non-reentrant; scope cleared on return",
                note="No native-noise/primal equality is claimed; mode and float resize are intentional approximations")
        except BaseException:
            self.close()
            raise
        finally:
            self._offload_codec()

    def close(self):
        """Best-effort release, preserving any original OOM; returns cleanup errors."""
        errors = []
        self._closed = True
        if getattr(self, "sdxl", None) is not None:
            try:
                self.sdxl.to("cpu")
            except Exception as exc:
                errors.append("SDXL offload: " + str(exc))
            self.sdxl = None
        if getattr(self, "reader", None) is not None:
            try:
                self.reader.vae.to("cpu")
            except Exception as exc:
                errors.append("F5 reader offload: " + str(exc))
            self.reader = None
        self.clip = self.features = None
        self.resize_up = self.resize_down = None
        for name in ("D", "ch", "u", "v", "coeff", "chip", "norms"):
            if hasattr(self, name):
                setattr(self, name, None)
        gc.collect()
        if hasattr(self, "torch") and self.torch.cuda.is_available():
            try:
                self.torch.cuda.empty_cache()
            except Exception as exc:
                errors.append("CUDA cache release: " + str(exc))
        self.cleanup_errors = errors
        return errors

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
