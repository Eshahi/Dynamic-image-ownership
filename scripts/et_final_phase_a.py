"""Final-study Phase A, stage 1: native paired grid and F5 transfer-law tangents (option (a) kernels).

Written by Claude (Opus 5.5) on 2026-10-26. The user approved, verbatim: "Approved: Phase A with option (a), total cap
22 instance-hours (about $10). Keep the instance on for development and testing, and stop it when Phase A ends."

Option (a) (pilot report, research/encoder-transfer-20261019/final-study-20261025/pilot/PILOT-REPORT.md): the new
study's native trajectories use the same deterministic attention (diffusers classic AttnProcessor) and explicit
fp32-internal LayerNorm as the derivative path, so the law's primal trajectory is the native one by construction.
Recorded here as a pre-outcome technical amendment; the detectors and the F5 reader stay unchanged.

For each development source (fixed SHA-256 order), R0/R1 cell (.1/.2/.4) and seed (12/13/14):
  - C0 native output with every random draw captured (and the UNet calls and scheduler states traced);
  - the four marked inputs' native outputs replaying C0's draws (paired coupling);
  - the F5 full-chain tangent v around the C0 trajectory (exact paired encoder displacement), and the chip
    vectors b (C0 output, RGB8 reader) and p1 (F5 output, RGB8 reader) that the kappa fit needs.
No detector endpoint is computed here. Journal: append-only JSONL, last row per id; resumable.

Usage: python scripts/et_final_phase_a.py --assets /workspace/assets --images /workspace/runs/stage2a-full/images \
           --out /workspace/runs/et-phase-a [--families R0,R1] [--limit-sources N]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import encoder_transfer_runtime as rt  # noqa: E402
import et_final_pilot as pilot  # noqa: E402
from encoder_transfer_test import ALPHA, ROOT  # noqa: E402

STUDY = ROOT / "research/encoder-transfer-20261019"
ARMS = ["unmarked", "f5-r2", "v5-r3", "wam", "vine-r"]
CELLS = [("R0", .1), ("R0", .2), ("R0", .4), ("R1", .1), ("R1", .2), ("R1", .4)]
SEEDS = (12, 13, 14)


def development_order():
    """All 60 development sources in the protocol's SHA-256 order; first 30 fit, last 30 calibration."""
    ids = [s["source_id"] for s in pilot.read(STUDY / "source-list.json")["sources"]]
    return sorted(ids, key=lambda i: (hashlib.sha256(f"{pilot.SPLIT_TAG}{i}".encode()).hexdigest(), int(i)))


class Journal:
    def __init__(self, path):
        self.path = Path(path)
        self.latest = {}
        if self.path.exists():
            with open(self.path, encoding="utf-8") as handle:
                for line in handle:
                    try:
                        row = json.loads(line)
                    except json.JSONDecodeError:
                        continue  # torn tail of an interrupted write; the identity is redone
                    self.latest[row["id"]] = row

    def done(self, uid):
        return self.latest.get(uid, {}).get("status") in ("ok", "safety_blocked", "error_terminal")

    def append(self, row):
        row["utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with open(self.path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, default=str) + "\n")
        self.latest[row["id"]] = row


def run_native(fam, regen, rgb512, strength, seed, tape=None, hooks=None):
    """Regenerator.__call__ semantics (same kwargs, safety handling and RGB8 quantization), but under no_grad so the
    C0 trace can be used for derivatives, and inside the option-(a) kernel context set by the caller."""
    import numpy as np
    import torch
    pipe = regen.pipe
    generator = torch.Generator(device="cuda").manual_seed(seed)
    kwargs = pilot.pipe_kwargs(regen, pilot.native_input(fam, rgb512), strength, generator)
    contexts = [c for c in (tape, hooks) if c is not None]
    with torch.no_grad():
        for c in contexts:
            c.__enter__()
        try:
            if fam == "K3":
                result = pipe(output_type="np", **kwargs)
                image = result.images[0]
                if not np.isfinite(image).all():
                    raise FloatingPointError("Kandinsky 3 decoded output contains non-finite values")
                out = (image * 255).round().astype("uint8")
            else:
                result = pipe(output_type="pil", **kwargs)
                if regen.spec["family"] == "sd15":
                    from three_threat_models import validate_generated
                    out = validate_generated(result)
                else:
                    out = result.images[0]
                out = np.asarray(out, dtype=np.uint8).copy()
        finally:
            for c in reversed(contexts):
                c.__exit__(None, None, None)
    return rt.resize_rgb(out, 512) if fam in ("R1", "K3") else out


def law_tangent(fam, regen, reader, layout, resize, calls, states, draws, in0, in1):
    """F5 full-chain tangent around the traced C0 trajectory (pilot check_jvp_chain without its own capture)."""
    import numpy as np
    import torch
    from torch.func import jvp
    from torch.nn.attention import SDPBackend, sdpa_kernel
    pipe = regen.pipe
    sched = pipe.scheduler
    if any(len(a) != 2 for a, _ in calls):
        raise RuntimeError("unexpected UNet call signature")
    timesteps = [int(a[1]) for a, _ in calls]
    if fam == "K3":
        t0 = pilot.encode_terms(fam, regen, in0)["z"]
        z0, d = t0, pilot.encode_terms(fam, regen, in1)["z"] - t0
        eps, step_draws = draws[0], draws[1:]
    else:
        e0, e1 = pilot.encode_terms(fam, regen, in0), pilot.encode_terms(fam, regen, in1)
        eta, eps, step_draws = draws[0], draws[1], draws[2:]
        sf = pipe.vae.config.scaling_factor
        z0 = sf * (e0["mean"] + e0["std"] * eta).to(torch.float16)
        d = sf * ((e1["mean"] - e0["mean"]) + (e1["std"] - e0["std"]) * eta).float()
    first = calls[0][0][0]
    state = sched.add_noise(z0.to(first.dtype), eps.to(first.dtype), torch.tensor([timesteps[0]], device="cuda"))
    start_err = pilot.rel_err(state, first)
    tangent32 = (float(sched.alphas_cumprod[timesteps[0]] ** .5) * d).float()
    tape_step = pilot.Tape()
    tape_step.draws = step_draws
    errors, precisions = [], []
    for k, ((a, kw), t) in enumerate(zip(calls, timesteps)):
        cond = dict(kw)
        extra = {} if fam == "K3" else dict(eta=0., generator=None)

        def f(z, t=t, cond=cond, extra=extra):
            m = sched.scale_model_input(z, t)
            pred = pipe.unet.forward(m, t, **cond)
            pred = pred[0] if isinstance(pred, tuple) else pred.sample
            return sched.step(pred, t, z, return_dict=False, **extra)[0]

        scale_k = tangent32.norm().clamp_min(1e-30)
        unit = (tangent32 / scale_k).to(state.dtype)
        precision = "native"
        with sdpa_kernel([SDPBackend.MATH]), torch.no_grad(), tape_step.replay(start=k if fam == "K3" else 0,
                                                                                stop=(k + 1) if fam == "K3" else 0):
            nxt, out = jvp(f, (state,), (unit,))
            if not bool(torch.isfinite(out).all()):
                precision = "fp32_surrogate_after_nonfinite_native"
                pipe.unet.to(dtype=torch.float32)
                try:
                    tape_step.replay(start=k if fam == "K3" else 0, stop=(k + 1) if fam == "K3" else 0)
                    _, out = jvp(lambda z: f(z, t, pilot.cast_floats(cond, torch.float32), extra), (state.float(),), (unit.float(),))
                finally:
                    pipe.unet.to(dtype=torch.float16)
        tangent32 = out.float() * scale_k
        errors.append(pilot.rel_err(nxt, states[k]))
        precisions.append(precision)
        state = nxt
    if fam == "K3":
        def decode(z):
            return (pipe.movq.decode(z, force_not_quantize=True)["sample"].float() * .5 + .5).clamp(0, 1)
        dec_module = pipe.movq
    else:
        vae = pipe.vae
        sf = vae.config.scaling_factor
        dec_module = vae

        def decode(z):
            dz = z.float() if fam == "R1" else z.to(vae.dtype)
            return (vae.decode(dz / sf, return_dict=False)[0].float() / 2 + .5).clamp(0, 1)
    if fam == "R1":
        vae.to(dtype=torch.float32)

    def chain(z):
        img = decode(z)
        return reader.encode(resize(img) if img.shape[-1] != 512 else img)

    scale = tangent32.norm().clamp_min(1e-30)
    unit = (tangent32 / scale).to(state.dtype)
    decode_precision = "native"
    try:
        with pilot.ClassicAttention(reader.vae), sdpa_kernel([SDPBackend.MATH]), torch.no_grad():
            zr, zr_t = jvp(chain, (state,), (unit,))
            if not bool(torch.isfinite(zr_t).all()) and fam != "R1":
                decode_precision = "fp32_surrogate_after_nonfinite_native"
                dec_module.to(dtype=torch.float32)
                try:
                    zr, zr_t = jvp(chain, (state.float(),), (unit.float(),))
                finally:
                    dec_module.to(dtype=torch.float16)
    finally:
        if fam == "R1":
            vae.to(dtype=torch.float16)
    zr_t = zr_t.float() * scale
    v = np.asarray(layout.projections(zr_t.double().cpu().numpy()))
    chips_float = np.asarray(layout.projections(zr.double().cpu().numpy()))
    return v, dict(timesteps=timesteps, start_state_rel_err=start_err, step_primal_rel_err=errors, step_precision=precisions,
                   decode_precision=decode_precision, displacement_norm=float(d.float().norm()), chips_float=chips_float)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--assets", type=Path, required=True)
    parser.add_argument("--images", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--families", default="R0,R1")
    parser.add_argument("--limit-sources", type=int, default=60)
    parser.add_argument("--deadline-utc", default="", help="stop starting new units after this UTC time (YYYY-mm-ddTHH:MM)")
    args = parser.parse_args()
    import numpy as np
    import torch
    import f5_latent_codec as f5
    import revised_watermark_v5 as v5
    out = args.out
    (out / "images").mkdir(parents=True, exist_ok=True)
    journal = Journal(out / "native.jsonl")
    config, specs = pilot.channel_specs()
    order = development_order()[:args.limit_sources]
    split = {s: ("fit" if i < 30 else "calibration") for i, s in enumerate(development_order())}
    rgb = {(s, a): rt.load_rgb(args.images / f"clean_{s}_{a}_None_None.png") for s in order for a in ARMS}
    profile = pilot.read(ROOT / config["profile_file"])
    checked, key, cfg = v5._resolve(profile, None)
    layout = f5.Layout(checked, key, cfg, v5.canonical_owner(ALPHA))
    reader = f5.Reader(args.assets / "a6", device="cuda")
    resize = pilot.Resize(1024, 512, torch)
    import calendar
    deadline = calendar.timegm(time.strptime(args.deadline_utc, "%Y-%m-%dT%H:%M")) if args.deadline_utc else None
    for fam in [x for x in args.families.split(",") if x]:
        regen = rt.Regenerator(args.assets, specs[fam])
        modules = [regen.pipe.unet, regen.pipe.movq if fam == "K3" else regen.pipe.vae]
        with pilot.ClassicAttention(*modules):  # option (a): native trajectories use the derivative path's kernels
            for strength in [s for f, s in CELLS if f == fam]:
                cell = f"{fam}-{strength}"
                for source in order:
                    for seed in SEEDS:
                        law_id = f"law:{cell}:{source}:{seed}"
                        if journal.done(law_id):
                            continue
                        if deadline and time.time() > deadline:
                            print("deadline reached", flush=True)
                            return
                        tick = time.monotonic()
                        tape, hooks = pilot.Tape(), pilot.Hooks(regen.pipe)
                        outputs = {}
                        c0_status, c0_error = "ok", None
                        try:
                            outputs["unmarked"] = run_native(fam, regen, rgb[(source, "unmarked")], strength, seed, tape.record(), hooks)
                        except Exception as exc:
                            c0_status = "safety_blocked" if "safety" in str(exc).lower() or "nsfw" in str(exc).lower() else "error_terminal"
                            c0_error = traceback.format_exc()[-1500:]
                        receipt = tape.receipt()
                        calls = [(pilot.detach_tree(a), pilot.detach_tree(k)) for a, k in hooks.calls]
                        states = hooks.states
                        native_rows = {}
                        for arm in ARMS:
                            uid = f"native:{cell}:{source}:{seed}:{arm}"
                            row = dict(id=uid, kind="native", cell=cell, family=fam, strength=strength, source=source, seed=seed,
                                       arm=arm, split=split[source], draws=receipt)
                            try:
                                if arm == "unmarked":
                                    if c0_status != "ok":
                                        raise RuntimeError(c0_error)
                                    img = outputs["unmarked"]
                                else:
                                    if not tape.draws:
                                        raise RuntimeError("no captured C0 draws to replay")
                                    img = run_native(fam, regen, rgb[(source, arm)], strength, seed + 1000, tape.replay())
                                    if tape.cursor != len(tape.draws):
                                        raise RuntimeError(f"replay consumed {tape.cursor} of {len(tape.draws)} draws")
                                    outputs[arm] = img
                                path = out / "images" / f"{cell}_{source}_{arm}_{seed}.png"
                                row["output"] = rt.save_rgb(path, img)
                                row["status"] = "ok"
                            except Exception as exc:
                                row["status"] = "safety_blocked" if "safety" in str(exc).lower() or "nsfw" in str(exc).lower() else "error_terminal"
                                row["error"] = str(exc)[-1500:]
                            native_rows[arm] = row
                            journal.append(row)
                        law = dict(id=law_id, kind="law", cell=cell, family=fam, strength=strength, source=source, seed=seed,
                                   split=split[source])
                        try:
                            if "unmarked" not in outputs or "f5-r2" not in outputs:
                                raise RuntimeError("C0 or F5 native output unavailable")
                            v, diag = law_tangent(fam, regen, reader, layout, resize, calls, states, tape.draws,
                                                  pilot.native_input(fam, rgb[(source, "unmarked")]), pilot.native_input(fam, rgb[(source, "f5-r2")]))
                            b = np.asarray(layout.projections(reader.latent(outputs["unmarked"])))
                            p1 = np.asarray(layout.projections(reader.latent(outputs["f5-r2"])))
                            if not (np.isfinite(v).all() and np.isfinite(b).all() and np.isfinite(p1).all()):
                                raise FloatingPointError("nonfinite law vector")
                            cf = diag.pop("chips_float")
                            law.update(status="ok", v=v.tolist(), b=b.tolist(), p1=p1.tolist(),
                                       chips_float_vs_b_rel=float(np.linalg.norm(cf - b) / max(np.linalg.norm(b), 1e-12)), **diag)
                        except Exception as exc:
                            law.update(status="unavailable", error=traceback.format_exc()[-2000:])
                        law["seconds"] = time.monotonic() - tick
                        journal.append(law)
                        print(f"[{law['utc']}] {law_id} {law['status']} {law['seconds']:.1f}s "
                              f"err={max(law.get('step_primal_rel_err') or [0]):.1e}", flush=True)
                        del calls, states, tape, hooks
                        rt.release()
        regen = None
        rt.release()


if __name__ == "__main__":
    main()
