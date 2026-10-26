"""Final-study Phase-A feasibility pilot: detector-sealed technical checks on six development sources.

Written by Claude (Opus 5.5) on 2026-10-26. The user approved the pilot, verbatim: "start it, and when it ends, stop
the instance". It implements the pilot of research/encoder-transfer-20261019/final-study-20261025/07-final-experiment.md
section 4 and analysis/mechanism-server-spec.md section 7.

It measures feasibility only:
  - native noise capture and replay (every diffusers randn_tensor draw, in call order) for R0, R1 and K3;
  - the executed schedules for every planned strength;
  - full-chain forward-mode JVPs (denoiser steps, decoder, resize, F5 reader encoder, chip operator) per family;
  - encoder-only JVPs for the mechanism module;
  - the attack A and B adapters;
  - memory, time and storage.
It runs no detector on any marked output, chooses no scientific setting and keeps every failure. C0 (unmarked) chips
are read only to compare the floating reader path with the RGB8 path.

Usage (on the server):
  python scripts/et_final_pilot.py --assets /workspace/assets --images /workspace/runs/stage2a-full/images \
      --out /workspace/runs/et-pilot --minutes 110
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import encoder_transfer_runtime as rt  # noqa: E402
from encoder_transfer_test import ALPHA, ROOT  # noqa: E402

STUDY = ROOT / "research/encoder-transfer-20261019"
ARMS = ["unmarked", "f5-r2", "v5-r3", "wam", "vine-r"]
SPLIT_TAG = "et-final-law-split-v1/"


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def pilot_sources():
    """The first six of the 60 development sources in the fixed SHA-256 order of the final-study protocol."""
    ids = [s["source_id"] for s in read(STUDY / "source-list.json")["sources"]]
    order = sorted(ids, key=lambda i: (hashlib.sha256(f"{SPLIT_TAG}{i}".encode()).hexdigest(), int(i)))
    return order[:6]


def tensor_digest(x):
    return hashlib.sha256(x.detach().contiguous().cpu().numpy().tobytes()).hexdigest()


# ---------------------------------------------------------------- recorder

class Pilot:
    def __init__(self, out, minutes):
        self.out = Path(out)
        self.out.mkdir(parents=True, exist_ok=True)
        self.journal = self.out / "pilot.jsonl"
        self.deadline = time.monotonic() + minutes * 60
        self.started = time.time()

    def write(self, row):
        row["utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with open(self.journal, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, default=str) + "\n")
        print(f"[{row['utc']}] {row['check']} {row.get('status')} {row.get('seconds', 0):.1f}s", flush=True)
        return row

    def run(self, name, fn, **meta):
        import torch
        if time.monotonic() > self.deadline:
            return self.write(dict(check=name, status="skipped_budget", **meta))
        torch.cuda.synchronize()
        torch.cuda.reset_peak_memory_stats()
        tick = time.monotonic()
        row = dict(check=name, **meta)
        try:
            row["details"] = fn() or {}
            row["status"] = "ok"
        except torch.cuda.OutOfMemoryError as exc:
            row["status"] = "oom"
            row["error"] = str(exc)[:3000]
        except Exception:
            row["status"] = "failed"
            row["error"] = traceback.format_exc()[-6000:]
        torch.cuda.synchronize()
        row["seconds"] = time.monotonic() - tick
        row["peak_allocated_bytes"] = torch.cuda.max_memory_allocated()
        row["peak_reserved_bytes"] = torch.cuda.max_memory_reserved()
        rt.release()
        return self.write(row)


# ---------------------------------------------------------------- noise tape

class Tape:
    """Record or replay every diffusers randn_tensor draw, in call order, across all loaded diffusers modules."""

    def __init__(self):
        import diffusers.utils.torch_utils as tu
        self.original = tu.randn_tensor
        self.draws, self.mode, self.cursor, self.stop = [], None, 0, None

    def _fake(self, shape, generator=None, device=None, dtype=None, layout=None):
        if self.mode == "record":
            x = self.original(shape, generator=generator, device=device, dtype=dtype, layout=layout)
            self.draws.append(x.detach().clone())
            return x
        if self.stop is not None and self.cursor >= self.stop:
            raise RuntimeError("replay beyond the allowed draw")
        x = self.draws[self.cursor]
        self.cursor += 1
        if tuple(x.shape) != tuple(shape) or (dtype is not None and x.dtype != dtype):
            raise ValueError(f"replayed draw mismatch: {tuple(x.shape)}/{x.dtype} vs {tuple(shape)}/{dtype}")
        return x.to(device) if device is not None else x

    def __enter__(self):
        self.modules = [m for n, m in list(sys.modules.items())
                        if n.startswith("diffusers") and getattr(m, "randn_tensor", None) is self.original]
        for m in self.modules:
            m.randn_tensor = self._fake
        return self

    def __exit__(self, *exc):
        for m in self.modules:
            m.randn_tensor = self.original

    def record(self):
        self.mode, self.draws, self.cursor, self.stop = "record", [], 0, None
        return self

    def replay(self, start=0, stop=None):
        self.mode, self.cursor, self.stop = "replay", start, stop
        return self

    def receipt(self):
        return [dict(shape=list(d.shape), dtype=str(d.dtype), sha256=tensor_digest(d), bytes=d.numel() * d.element_size())
                for d in self.draws]


# ---------------------------------------------------------------- differentiable Lanczos (PIL-equivalent float weights)

def lanczos_matrix(in_size, out_size):
    """PIL ImagingResample LANCZOS coefficients as a dense float64 (out, in) matrix, without 8-bit fixed point."""
    import numpy as np
    scale = in_size / out_size
    filterscale = max(scale, 1.0)
    support = 3.0 * filterscale

    def lanczos(x):
        if -3.0 <= x < 3.0:
            return (np.sinc(x) * np.sinc(x / 3.0)) if x != 0 else 1.0
        return 0.0

    m = np.zeros((out_size, in_size))
    for i in range(out_size):
        center = (i + 0.5) * scale
        xmin = max(int(center - support + 0.5), 0)
        xmax = min(int(center + support + 0.5), in_size)
        w = np.array([lanczos((j + xmin - center + 0.5) / filterscale) for j in range(xmax - xmin)])
        w = w / w.sum() if w.sum() != 0 else w
        m[i, xmin:xmax] = w
    return m


class Resize:
    def __init__(self, in_size, out_size, torch):
        mat = torch.from_numpy(lanczos_matrix(in_size, out_size)).float().cuda()
        self.mat = mat

    def __call__(self, image):  # (1,3,H,W) float in [0,1] -> (1,3,h,w)
        return (self.mat @ image @ self.mat.T).clamp(0, 1)


# ---------------------------------------------------------------- families

def channel_specs():
    config = read(STUDY / "stage2b-config.json")
    specs = {c["id"]: c for c in config["channels"]}
    return config, dict(R0=specs["R0"], R1=specs["R1"], K3=specs["R3"])


def native_input(family, rgb):
    """The native regenerator input for a saved 512 RGB8 image (R1 and K3 work at 1024, as the stage-2 runner does)."""
    return rt.resize_rgb(rgb, 1024) if family in ("R1", "K3") else rgb


def pipe_kwargs(regen, rgb, strength, generator):
    """The exact keyword arguments of encoder_transfer_runtime.Regenerator.__call__ (no latent input)."""
    from PIL import Image
    spec = regen.spec
    if spec["family"] == "kandinsky3":
        return dict(image=Image.fromarray(rgb), strength=strength, num_inference_steps=spec["steps"],
                    guidance_scale=spec["guidance_scale"], generator=generator, return_dict=True, **regen.prompt)
    kwargs = dict(prompt=spec["prompt"], image=Image.fromarray(rgb), strength=strength, num_inference_steps=spec["steps"],
                  guidance_scale=spec["guidance_scale"], generator=generator, return_dict=True, negative_prompt="", eta=0.)
    if spec["family"] == "sdxl":
        kwargs.update(prompt_2="", original_size=(1024, 1024), target_size=(1024, 1024), crops_coords_top_left=(0, 0), clip_skip=None)
    return kwargs


def native_rgb(family, regen, rgb512, strength, seed, tape=None):
    """Unchanged native call (inference mode) returning the saved 512 RGB8 output, optionally under a noise tape."""
    out = regen(native_input(family, rgb512), strength, seed) if tape is None else None
    if tape is not None:
        with tape:
            out = regen(native_input(family, rgb512), strength, seed)
    return rt.resize_rgb(out, 512) if family in ("R1", "K3") else out


class Hooks:
    """Capture every UNet call (args, kwargs) and every scheduler.step output of one native call."""

    def __init__(self, pipe):
        self.pipe, self.calls, self.states = pipe, [], []

    def __enter__(self):
        unet, sched = self.pipe.unet, self.pipe.scheduler
        self.unet_forward, self.sched_step = unet.forward, sched.step

        def forward(*a, **k):
            self.calls.append((a, k))
            return self.unet_forward(*a, **k)

        def step(*a, **k):
            out = self.sched_step(*a, **k)
            prev = out[0] if isinstance(out, tuple) else out.prev_sample
            self.states.append(prev.detach().clone())
            return out

        unet.forward, sched.step = forward, step
        return self

    def __exit__(self, *exc):
        self.pipe.unet.forward, self.pipe.scheduler.step = self.unet_forward, self.sched_step


def detach_tree(x):
    import torch
    if isinstance(x, torch.Tensor):
        return x.detach().clone()
    if isinstance(x, dict):
        return {k: detach_tree(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return type(x)(detach_tree(v) for v in x)
    return x


class ClassicAttention:
    """Swap every diffusers Attention processor to the classic bmm/softmax AttnProcessor, which supports forward-mode
    AD in fp16 (PyTorch's flash kernel has no forward AD; its math kernel returns fp32 for fp16 inputs under forward AD,
    found in the pilot's first debug run). Native generation keeps its own processors; the JVP path records the
    resulting primal difference instead of hiding it."""

    def __init__(self, *modules):
        self.modules = [m for m in modules if m is not None]

    def __exit__(self, *exc):
        for sub, processor in self.saved:
            sub.set_processor(processor)
        for sub, forward in self.norms:
            sub.forward = forward

    def __enter__(self):
        import torch
        from diffusers.models.attention_processor import Attention, AttnProcessor
        self.saved, self.norms = [], []
        for m in self.modules:
            for sub in m.modules():
                if isinstance(sub, Attention):
                    self.saved.append((sub, sub.processor))
                    sub.set_processor(AttnProcessor())
                elif isinstance(sub, torch.nn.LayerNorm):
                    # fp16 nn.LayerNorm returns an fp32 tangent under forward AD (pilot debug run 2). This explicit
                    # form computes in fp32 and casts back, as the native kernel does internally.
                    def forward(x, sub=sub):
                        dims = tuple(range(-len(sub.normalized_shape), 0))
                        xf = x.float()
                        mu = xf.mean(dims, keepdim=True)
                        var = (xf - mu).pow(2).mean(dims, keepdim=True)
                        y = (xf - mu) * torch.rsqrt(var + sub.eps)
                        if sub.weight is not None:
                            y = y * sub.weight.float()
                        if sub.bias is not None:
                            y = y + sub.bias.float()
                        return y.to(x.dtype)
                    self.norms.append((sub, sub.forward))
                    sub.forward = forward
        return self


def cast_floats(x, dtype):
    import torch
    if isinstance(x, torch.Tensor):
        return x.to(dtype) if x.is_floating_point() else x
    if isinstance(x, dict):
        return {k: cast_floats(v, dtype) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return type(x)(cast_floats(v, dtype) for v in x)
    return x


def rel_err(a, b):
    import torch
    a, b = a.float(), b.float()
    return float((a - b).norm() / b.norm().clamp_min(1e-12))


# ---------------------------------------------------------------- checks

def check_environment(args):
    import torch
    import diffusers
    import transformers
    return dict(torch=torch.__version__, diffusers=diffusers.__version__, transformers=transformers.__version__,
                gpu=torch.cuda.get_device_name(0), total_memory=torch.cuda.get_device_properties(0).total_memory,
                cudnn=torch.backends.cudnn.version(), deterministic_algorithms=torch.are_deterministic_algorithms_enabled(),
                sources=pilot_sources(), commit=os.popen(f"git -C {ROOT} rev-parse HEAD").read().strip())


def check_schedules(regens):
    out = {}
    for fam, regen in regens.items():
        pipe = regen.pipe
        rows = {}
        strengths = [.05, .1, .15, .2, .4] if fam in ("R0", "R1") else [.2]
        for s in strengths:
            pipe.scheduler.set_timesteps(regen.spec["steps"], device="cuda")
            timesteps, n = pipe.get_timesteps(regen.spec["steps"], s, "cuda")
            ts = [int(t) for t in timesteps]
            ab = pipe.scheduler.alphas_cumprod
            rows[str(s)] = dict(executed=n, timesteps=ts, alpha_bar_start=float(ab[ts[0]]) if ts else None)
        out[fam] = dict(scheduler=type(pipe.scheduler).__name__, config={k: v for k, v in pipe.scheduler.config.items()
                                                                          if not k.startswith("_")}, strengths=rows)
    return out


def check_replay(fam, regen, rgb_c0, rgb_f5, strength, seed):
    """Native output against the same call replaying the captured draws; then the F5 input with C0's draws."""
    import numpy as np
    tape = Tape()
    native = native_rgb(fam, regen, rgb_c0, strength, seed, tape.record())
    receipt = tape.receipt()
    replayed = native_rgb(fam, regen, rgb_c0, strength, seed + 1000, tape.replay())  # other seed: draws come from the tape
    consumed = tape.cursor
    coupled = native_rgb(fam, regen, rgb_f5, strength, seed + 2000, tape.replay())  # marked input, C0's draws; not read
    diff = np.abs(native.astype(np.int16) - replayed.astype(np.int16))
    return dict(draws=receipt, draws_consumed=consumed, rgb8_equal=bool((diff == 0).all()), max_abs_diff=int(diff.max()),
                differing_pixels=int((diff > 0).any(axis=2).sum()), coupled_shape=list(coupled.shape),
                note="coupled output (F5 input, C0 draws) is generated but never read by a detector")


def encode_terms(fam, regen, rgb_in, dtype_override=None):
    """Native encoder terms for the img2img input: (mean, std) for SD-family posteriors, latents for MoVQ."""
    import torch
    from PIL import Image
    pipe = regen.pipe
    if fam == "K3":
        x = pipe.image_processor.preprocess(Image.fromarray(rgb_in)) if hasattr(pipe, "image_processor") else None
        if x is None:
            raise RuntimeError("no K3 image processor")
        x = x.to("cuda", dtype=pipe.movq.dtype)
        with torch.no_grad():
            z = pipe.movq.encode(x)["latents"]
        return dict(z=z)
    vae = pipe.vae
    x = pipe.image_processor.preprocess(Image.fromarray(rgb_in)).to("cuda")
    upcast = fam == "R1" and vae.config.force_upcast
    dtype = torch.float32 if upcast else vae.dtype
    if upcast:
        vae.to(dtype=torch.float32)
    with torch.no_grad():
        # Native SDXL img2img casts the preprocessed image to the pipeline dtype (fp16) before upcasting it.
        x = x.to(torch.float16).float() if upcast else x.to(dtype)
        post = vae.encode(x).latent_dist
    terms = dict(mean=post.mean.detach().clone(), std=post.std.detach().clone())
    if upcast:
        vae.to(dtype=torch.float16)
    return terms


def check_jvp_chain(fam, regen, reader, layout, resize, rgb_c0, rgb_f5, strength, seed):
    """One end-to-end F5 tangent around the C0 trajectory: exact encoder displacement, denoiser JVP per step, decode,
    resize, F5 reader encoder, linear chip operator. Primal agreement with the captured native states is recorded."""
    import numpy as np
    import torch
    from torch.func import jvp
    from torch.nn.attention import SDPBackend, sdpa_kernel
    pipe = regen.pipe
    sched = pipe.scheduler
    in0, in1 = native_input(fam, rgb_c0), native_input(fam, rgb_f5)
    # 1. Native C0 call without inference mode, capturing draws, UNet calls and scheduler states.
    tape = Tape()
    generator = torch.Generator(device="cuda").manual_seed(seed)
    kwargs = pipe_kwargs(regen, in0, strength, generator)
    kwargs["output_type"] = "latent"
    tick = time.monotonic()
    with tape.record(), Hooks(pipe) as hooks, torch.no_grad():
        pipe(**kwargs)
    native_seconds = time.monotonic() - tick
    calls = [(detach_tree(a), detach_tree(k)) for a, k in hooks.calls]
    states = hooks.states
    draws = tape.draws
    if any(len(a) != 2 for a, _ in calls):
        raise RuntimeError("unexpected UNet call signature; expected (sample, timestep) positional")
    timesteps = [int(a[1]) for a, _ in calls]
    # 2. Exact paired encoder displacement d and the C0 starting latent.
    if fam == "K3":
        t0 = encode_terms(fam, regen, in0)["z"]
        t1 = encode_terms(fam, regen, in1)["z"]
        z0, d = t0, t1 - t0
        eps, step_draws = draws[0], draws[1:]
    else:
        e0, e1 = encode_terms(fam, regen, in0), encode_terms(fam, regen, in1)
        eta, eps, step_draws = draws[0], draws[1], draws[2:]
        sf = pipe.vae.config.scaling_factor
        # Native order: posterior sample in the encoder dtype, cast to the pipeline dtype, then scaled.
        z0 = sf * (e0["mean"] + e0["std"] * eta).to(torch.float16)
        d = sf * ((e1["mean"] - e0["mean"]) + (e1["std"] - e0["std"]) * eta).float()
    first = calls[0][0][0]
    t_start = torch.tensor(timesteps[0], device="cuda")
    state = sched.add_noise(z0.to(first.dtype), eps.to(first.dtype), t_start.reshape(1))
    a_t = float(sched.alphas_cumprod[timesteps[0]] ** .5)
    tangent = (a_t * d).to(state.dtype)
    start_err = rel_err(state, first)
    # 3. Denoiser steps with forward-mode JVP.
    step_rows = []
    tangent32 = tangent.float()
    tape_step = Tape()
    tape_step.draws = step_draws
    for k, ((a, kw), t) in enumerate(zip(calls, timesteps)):
        cond = dict(kw)
        extra = dict(eta=0.) if fam != "K3" else {}
        if fam != "K3":
            extra["generator"] = None

        def f(z, t=t, cond=cond, extra=extra):
            m = sched.scale_model_input(z, t)
            pred = hooks.unet_forward(m, t, **cond)
            pred = pred[0] if isinstance(pred, tuple) else pred.sample
            return sched.step(pred, t, z, return_dict=False, **extra)[0]

        # Linear in the tangent: propagate a unit-norm fp16 tangent and keep the rescaled tangent in fp32
        # (the first pilot run overflowed the fp16 SDXL UNet tangent at its first step).
        scale_k = tangent32.norm().clamp_min(1e-30)
        unit = (tangent32 / scale_k).to(state.dtype)
        precision = "native"
        tick = time.monotonic()
        with ClassicAttention(pipe.unet), sdpa_kernel([SDPBackend.MATH]), torch.no_grad(), tape_step.replay(start=k if fam == "K3" else 0,
                                                                                stop=(k + 1) if fam == "K3" else 0):
            nxt, out = jvp(f, (state,), (unit,))
            if not bool(torch.isfinite(out).all()):
                # Declared surrogate: this step's tangent in an fp32 denoiser (primal stays the native fp16 result).
                precision = "fp32_surrogate_after_nonfinite_native"
                pipe.unet.to(dtype=torch.float32)
                cond32 = cast_floats(cond, torch.float32)
                try:
                    tape_step.replay(start=k if fam == "K3" else 0, stop=(k + 1) if fam == "K3" else 0)
                    _, out = jvp(lambda z, t=t, cond=cond32, extra=extra: f(z, t, cond, extra),
                                 (state.float(),), (unit.float(),))
                finally:
                    pipe.unet.to(dtype=torch.float16)
        torch.cuda.synchronize()
        tangent32 = out.float() * scale_k
        step_rows.append(dict(t=t, seconds=time.monotonic() - tick, precision=precision, primal_rel_err=rel_err(nxt, states[k]),
                              tangent_norm=float(tangent32.norm()), finite=bool(torch.isfinite(tangent32).all())))
        state = nxt
    tangent = tangent32.to(state.dtype) if bool(torch.isfinite(tangent32).all()) and tangent32.abs().max() < 6e4 else tangent32
    # 4. Decode, resize to 512, F5 reader encoder (fp32 SD1.5 posterior mode), as one JVP.
    if fam == "K3":
        def decode(z):
            img = pipe.movq.decode(z, force_not_quantize=True)["sample"]
            return (img.float() * .5 + .5).clamp(0, 1)
    else:
        vae = pipe.vae
        sf = vae.config.scaling_factor
        upcast = fam == "R1"

        def decode(z):
            dz = z.float() if upcast else z.to(vae.dtype)
            img = vae.decode(dz / sf, return_dict=False)[0]
            return (img.float() / 2 + .5).clamp(0, 1)
    if fam == "R1":
        vae.to(dtype=torch.float32)

    def chain(z):
        img = decode(z)
        if img.shape[-1] != 512:
            img = resize(img)
        return reader.encode(img)

    # The JVP is linear in the tangent: propagate a unit-norm tangent and rescale in fp32, so the fp16 decoder's
    # tangent cannot overflow (pilot debug run 3 gave non-finite chips with the raw tangent).
    scale = tangent.float().norm()
    unit = (tangent.float() / scale.clamp_min(1e-30)).to(state.dtype)
    decode_precision = "native"
    tick = time.monotonic()
    with ClassicAttention(pipe.movq if fam == "K3" else pipe.vae, reader.vae), sdpa_kernel([SDPBackend.MATH]), torch.no_grad():
        zr, zr_t = jvp(chain, (state,), (unit,))
        if not bool(torch.isfinite(zr_t).all()) and fam != "R1":
            # Declared surrogate: fp32 decoder for the tangent only (the native fp16 decode stays the primal reference).
            decode_precision = "fp32_surrogate_after_nonfinite_native"
            dec_module = pipe.movq if fam == "K3" else pipe.vae
            dec_module.to(dtype=torch.float32)
            try:
                if fam == "K3":
                    zr, zr_t = jvp(lambda z: reader.encode(resize((dec_module.decode(z.float(), force_not_quantize=True)["sample"] * .5 + .5).clamp(0, 1))),
                                   (state,), (unit,))
                else:
                    zr, zr_t = jvp(lambda z: reader.encode((dec_module.decode(z.float() / dec_module.config.scaling_factor, return_dict=False)[0] / 2 + .5).clamp(0, 1)),
                                   (state,), (unit,))
            finally:
                dec_module.to(dtype=torch.float16)
    zr_t = zr_t.float() * scale
    torch.cuda.synchronize()
    decode_seconds = time.monotonic() - tick
    if fam == "R1":
        vae.to(dtype=torch.float16)
    v = np.asarray(layout.projections(zr_t.double().cpu().numpy()))
    chips_float = np.asarray(layout.projections(zr.double().cpu().numpy()))
    # 5. C0 native RGB8 chips (unmarked output only) against the floating path.
    native_c0 = native_rgb(fam, regen, rgb_c0, strength, seed)
    chips_rgb8 = np.asarray(layout.projections(reader.latent(native_c0)))
    return dict(family=fam, strength=strength, seed=seed, executed_steps=len(calls), timesteps=timesteps,
                native_latent_call_seconds=native_seconds, start_state_rel_err=start_err, steps=step_rows,
                decode_reader_jvp_seconds=decode_seconds, decode_precision=decode_precision, v_norm=float(np.linalg.norm(v)), v_finite=bool(np.isfinite(v).all()),
                chips_float_vs_rgb8=dict(max_abs=float(np.abs(chips_float - chips_rgb8).max()),
                                         rel=float(np.linalg.norm(chips_float - chips_rgb8) / max(np.linalg.norm(chips_rgb8), 1e-12))),
                displacement_norm=float(d.float().norm()), draws=len(draws),
                stored_bytes_estimate=int(sum(x.numel() * x.element_size() for x in draws) + sum(s.numel() * s.element_size() for s in states)))


def check_encoder_jvp(name, encode, x, direction, module=None):
    import torch
    from torch.func import jvp
    from torch.nn.attention import SDPBackend, sdpa_kernel
    unit = (direction.float() / direction.float().norm().clamp_min(1e-30)).to(direction.dtype)  # gain is scale-free
    tick = time.monotonic()
    with ClassicAttention(module), sdpa_kernel([SDPBackend.MATH]), torch.no_grad():
        z, zt = jvp(encode, (x,), (unit,))
    torch.cuda.synchronize()
    return dict(encoder=name, seconds=time.monotonic() - tick, gain=float(zt.float().norm() / unit.float().norm()),
                finite=bool(torch.isfinite(zt).all()), latent_shape=list(z.shape))


def check_attack_a(regens, rgb_in, seed):
    rows = []
    for s in (.05, .1, .15, .2):
        tick = time.monotonic()
        first = native_rgb("R1", regens["R1"], rgb_in, s, seed)
        mid = time.monotonic()
        second = native_rgb("R0", regens["R0"], first, s, seed + 100)
        rows.append(dict(strength=s, sdxl_seconds=mid - tick, sd15_seconds=time.monotonic() - mid, shape=list(second.shape)))
    return dict(rows=rows, note="outputs are never read by a detector")


def check_attack_b(r0, reader, lpips_metric, rgb_in, epsilon=.075, lam=1.0, steps=20, codec=True):
    import torch
    from diffusers import DDIMInverseScheduler
    pipe = r0.pipe
    vae = reader.vae  # pinned SD1.5 VAE in fp32
    sf = .18215
    u = torch.from_numpy(rgb_in.astype("float32") / 255).permute(2, 0, 1)[None].cuda()
    timing = {}
    tick = time.monotonic()
    with torch.no_grad():
        z0 = vae.encode(u * 2 - 1).latent_dist.mode() * sf
        embeds = pipe.encode_prompt("", "cuda", 1, False)[0]
        inverse = DDIMInverseScheduler(num_train_timesteps=1000, beta_start=.00085, beta_end=.012, beta_schedule="scaled_linear",
                                       prediction_type="epsilon", clip_sample=False, set_alpha_to_one=True, steps_offset=1,
                                       timestep_spacing="leading", rescale_betas_zero_snr=False)
        inverse.set_timesteps(20, device="cuda")
        z = z0.float()
        for t in inverse.timesteps:
            e = pipe.unet(inverse.scale_model_input(z, t).half(), t, encoder_hidden_states=embeds).sample.float()
            z = inverse.step(e, t, z).prev_sample
        n = z.detach()
    timing["inversion_seconds"] = time.monotonic() - tick
    timing["inverse_timesteps"] = [int(t) for t in inverse.timesteps]

    def decode(z):
        return (vae.decode(z / sf).sample / 2 + .5).clamp(0, 1)

    def cosine(a, b):
        return ((a * b).sum() / (a.norm().clamp_min(1e-12) * b.norm().clamp_min(1e-12))).clamp(-1, 1)

    tick = time.monotonic()
    z = z0.clone()
    step = epsilon / 10
    log = []
    for _ in range(steps):
        z = z.detach().requires_grad_(True)
        v = decode(z)
        loss_fid = .5 * (lpips_metric(v * 2 - 1, u * 2 - 1, normalize=False).sum() / .15 + ((v - u) ** 2).mean() / 10 ** -2.5)
        c = cosine(z, n)
        loss = loss_fid + lam * c ** 2
        g, = torch.autograd.grad(loss, z)
        if not (torch.isfinite(loss) and torch.isfinite(g).all()):
            raise FloatingPointError("nonfinite attack B step")
        with torch.no_grad():
            z = z - step * g / (g.pow(2).mean().sqrt() + 1e-12)
            z = z0 + (z - z0).clamp(-epsilon, epsilon)
        log.append(dict(loss=float(loss), cosine=float(c)))
    with torch.no_grad():
        out = (decode(z) * 255 + .5).floor().clamp(0, 255)
    timing["optimization_seconds"] = time.monotonic() - tick
    if codec:
        tick = time.monotonic()
        with torch.no_grad():
            (decode(z0) * 255 + .5).floor()
        timing["codec_seconds"] = time.monotonic() - tick
    return dict(epsilon=epsilon, lam=lam, steps=steps, timing=timing, first=log[0], last=log[-1],
                note="setting fixed for timing only; outputs are never read by a detector")


def gaussian_and_phase_controls(delta, seed_text):
    """Mechanism-module differential directions (spec section 6): two Gaussian and two Fourier-phase controls."""
    import numpy as np
    seed = int.from_bytes(hashlib.sha256(seed_text.encode()).digest()[:8], "little")
    rng = np.random.Generator(np.random.PCG64(seed))
    mu = delta.mean(axis=(0, 1), keepdims=True)
    r = delta - mu
    out = []
    for _ in range(2):
        g = rng.standard_normal(r.shape)
        g -= g.mean(axis=(0, 1), keepdims=True)
        norms = np.linalg.norm(r.reshape(-1, 3), axis=0)
        gn = np.linalg.norm(g.reshape(-1, 3), axis=0)
        out.append(mu + g * np.where(gn > 0, norms / np.maximum(gn, 1e-300), 0))
    for _ in range(2):
        f = np.fft.fft2(r, axes=(0, 1), norm="ortho")
        mag = np.abs(f)
        h, w = r.shape[:2]
        phase = rng.uniform(0, 2 * np.pi, size=(h, w, 3))
        kk, ll = np.meshgrid(np.arange(h), np.arange(w), indexing="ij")
        mate_k, mate_l = (-kk) % h, (-ll) % w
        canon = (kk * w + ll) < (mate_k * w + mate_l)
        selfc = (kk == mate_k) & (ll == mate_l)
        ph = np.zeros_like(phase)
        ph[canon] = phase[canon]
        ph[mate_k[canon], mate_l[canon]] = -phase[canon]
        signs = np.where(rng.random((h, w, 3)) < .5, 0.0, np.pi)
        ph[selfc] = signs[selfc]
        g = mag * np.exp(1j * ph)
        g[0, 0] = 0
        out.append(mu + np.real(np.fft.ifft2(g, axes=(0, 1), norm="ortho")))
    return out


# ---------------------------------------------------------------- main

def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--assets", type=Path, required=True)
    parser.add_argument("--images", type=Path, required=True, help="stage-2a images folder with the clean marks")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--minutes", type=float, default=110)
    parser.add_argument("--only", default="", help="comma-separated families to run (R0,R1,K3); default all")
    args = parser.parse_args()
    import numpy as np
    import torch
    import f5_latent_codec as f5
    import revised_watermark_v5 as v5
    import three_threat_models as models
    import importlib.metadata
    p = Pilot(args.out, args.minutes)
    config, specs = channel_specs()
    sources = pilot_sources()
    rgb = {(s, a): rt.load_rgb(args.images / f"clean_{s}_{a}_None_None.png") for s in sources for a in ARMS}
    p.run("environment", lambda: check_environment(args))
    profile = read(ROOT / config["profile_file"])
    checked, key, cfg = v5._resolve(profile, None)
    layout = f5.Layout(checked, key, cfg, v5.canonical_owner(ALPHA))
    reader = f5.Reader(args.assets / "a6", device="cuda")
    resize = Resize(1024, 512, torch)
    # Lanczos surrogate against PIL on a real C0 R1-sized image (primal only).
    def lanczos_check():
        big = rt.resize_rgb(rgb[(sources[0], "unmarked")], 1024)
        pil = rt.resize_rgb(big, 512).astype("float64") / 255
        x = torch.from_numpy(big.astype("float32") / 255).permute(2, 0, 1)[None].cuda()
        mine = resize(x)[0].permute(1, 2, 0).double().cpu().numpy()
        return dict(max_abs=float(np.abs(mine - pil).max()), mean_abs=float(np.abs(mine - pil).mean()),
                    rgb8_equal_after_rounding=float(((np.floor(mine * 255 + .5) - pil * 255) == 0).mean()))
    p.run("lanczos_surrogate_vs_pil", lanczos_check)
    # Control directions (CPU) for the mechanism module.
    def controls():
        s = sources[0]
        delta = (rgb[(s, "f5-r2")].astype("float64") - rgb[(s, "unmarked")].astype("float64")) / 255
        tick = time.monotonic()
        dirs = gaussian_and_phase_controls(delta, f"et-final-mechanism-v1|{s}|f5-r2|both|1")
        secs = time.monotonic() - tick
        norms = [float(np.linalg.norm(d)) for d in dirs]
        spec = [float(np.abs(np.abs(np.fft.fft2(d - d.mean(axis=(0, 1)), axes=(0, 1))) -
                             np.abs(np.fft.fft2(delta - delta.mean(axis=(0, 1)), axes=(0, 1)))).max()) for d in dirs[2:]]
        return dict(seconds=secs, delta_norm=float(np.linalg.norm(delta)), control_norms=norms, phase_spectrum_max_err=spec,
                    out_of_range_fraction=[float(((rgb[(s, "unmarked")] / 255 + d < 0) | (rgb[(s, "unmarked")] / 255 + d > 1)).mean()) for d in dirs])
    p.run("mechanism_controls_cpu", controls)
    lp = models.load_lpips(args.assets / "a6", Path(importlib.metadata.distribution("lpips").locate_file("lpips"))).cuda().eval()
    only = [x for x in args.only.split(",") if x] or ["R0", "R1", "K3"]
    regens = {}
    for fam in only:
        tick = time.monotonic()
        def load(fam=fam):
            regens[fam] = rt.Regenerator(args.assets, specs[fam])
            return {}
        p.run(f"load_{fam}", load, family=fam)
        if fam not in regens:
            continue
        p.run(f"schedules_{fam}", lambda fam=fam: check_schedules({fam: regens[fam]}), family=fam)
        for s in sources:
            p.run("replay", lambda fam=fam, s=s: check_replay(fam, regens[fam], rgb[(s, "unmarked")], rgb[(s, "f5-r2")], .2, 12),
                  family=fam, source=s, strength=.2, seed=12)
        longest = .2 if fam == "K3" else .4
        for s in sources[:2]:
            p.run("jvp_chain", lambda fam=fam, s=s: check_jvp_chain(fam, regens[fam], reader, layout, resize,
                                                                     rgb[(s, "unmarked")], rgb[(s, "f5-r2")], longest, 12),
                  family=fam, source=s, strength=longest, seed=12)
        if fam == "R1":
            p.run("jvp_chain", lambda s=sources[0]: check_jvp_chain("R1", regens["R1"], reader, layout, resize,
                                                                     rgb[(s, "unmarked")], rgb[(s, "f5-r2")], .1, 13),
                  family=fam, source=sources[0], strength=.1, seed=13)
        if fam == "R0":
            p.run("attack_b", lambda: check_attack_b(regens["R0"], reader, lp, rgb[(sources[0], "f5-r2")]), source=sources[0])
            p.run("attack_b", lambda: check_attack_b(regens["R0"], reader, lp, rgb[(sources[1], "wam")], codec=False), source=sources[1])
        # Encoder-only JVPs for the mechanism module (actual F5 residual direction).
        for s in sources[:3]:
            def enc(fam=fam, s=s):
                import torch as t
                delta = (rgb[(s, "f5-r2")].astype("float32") - rgb[(s, "unmarked")].astype("float32")) / 255
                if fam == "R0":
                    vae = reader.vae
                    x = t.from_numpy(rgb[(s, "unmarked")].astype("float32") / 255).permute(2, 0, 1)[None].cuda() * 2 - 1
                    dvec = t.from_numpy(delta).permute(2, 0, 1)[None].cuda() * 2
                    return check_encoder_jvp("sd15-fp32-512", lambda x: vae.encode(x).latent_dist.mode(), x, dvec, vae)
                if fam == "R1":
                    vae = regens["R1"].pipe.vae
                    vae.to(dtype=t.float32)
                    big = rt.resize_rgb(rgb[(s, "unmarked")], 1024)
                    dbig = rt.resize_rgb(rgb[(s, "f5-r2")], 1024).astype("float32") / 255 - big.astype("float32") / 255
                    x = t.from_numpy(big.astype("float32") / 255).permute(2, 0, 1)[None].cuda() * 2 - 1
                    dvec = t.from_numpy(dbig).permute(2, 0, 1)[None].cuda() * 2
                    try:
                        return check_encoder_jvp("sdxl-fp32-1024", lambda x: vae.encode(x).latent_dist.mode(), x, dvec, vae)
                    finally:
                        vae.to(dtype=t.float16)
                movq = regens["K3"].pipe.movq
                big = rt.resize_rgb(rgb[(s, "unmarked")], 1024)
                dbig = rt.resize_rgb(rgb[(s, "f5-r2")], 1024).astype("float32") / 255 - big.astype("float32") / 255
                x = t.from_numpy(big.astype("float32") / 255).permute(2, 0, 1)[None].cuda().to(movq.dtype) * 2 - 1
                dvec = (t.from_numpy(dbig).permute(2, 0, 1)[None].cuda() * 2).to(movq.dtype)
                return check_encoder_jvp(f"movq-{movq.dtype}-1024", lambda x: movq.encode(x)["latents"], x, dvec, movq)
            p.run("encoder_jvp", enc, family=fam, source=s)
        if fam == "R1" and "R0" in regens:
            p.run("attack_a", lambda: check_attack_a(regens, rgb[(sources[0], "f5-r2")], 12), source=sources[0])
        # SD1.5 stays loaded until attack A has run with SDXL; everything is released before the next family.
        if fam != "R0" or "R1" not in only:
            for key in list(regens):
                regens.pop(key)
            rt.release()
    p.write(dict(check="pilot_end", status="ok", wall_seconds=time.time() - p.started))


if __name__ == "__main__":
    main()
