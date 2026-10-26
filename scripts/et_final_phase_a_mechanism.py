"""Final-study Phase A, mechanism module (descriptive): twelve development sources, analysis/mechanism-server-spec.md §6.

Written by Claude (Opus 5.5) on 2026-10-26 under the user's Phase-A approval (option (a) kernels throughout).

For the first twelve development sources (protocol SHA-256 order) and the four marked arms:
  1. Directions: the actual residual delta = (mark - source)/255 and four differential controls (two Gaussian,
     two Fourier-phase; per-channel AC energy / Fourier magnitude matched, DC retained; seeds from SHA-256 of
     'et-final-mechanism-v1|source|arm|kind|replicate', PCG64, float64). No clipping.
  2. Encoder gains ||J_E u|| / ||u|| for SD1.5 (512, native fp16), SDXL (1024 via the Lanczos matrix, fp32) and
     Kandinsky 3 MoVQ (1024, fp16), plus the exact finite gain ||E(mark) - E(source)|| / ||delta||.
  3. Stage outputs at .2 for C0 and the four marks: mode codec, sampled codec (SD), noise-only direct decode,
     mode + noise + native reverse (SD), and the native K3 path (R0/R1 .2 natives come from stage 1), with C0's
     captured draws. Measured: pixel and F5-reader-latent residual energy against C0, and for F5 the chip change and
     its signed alignment with e = w(original q)/sqrt(320).
  4. F5-only differential full-chain tangents at .2: the encoder JVP of each direction, propagated as the law does;
     reported ||v||, e'v and e'v/||u||.
Everything is descriptive and paired within source; no setting is chosen from it.

Usage: python scripts/et_final_phase_a_mechanism.py --assets ... --images ... --out ... [--families R0,R1,K3]
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import math
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import encoder_transfer_runtime as rt  # noqa: E402
import et_final_pilot as pilot  # noqa: E402
import et_final_phase_a as pa  # noqa: E402
from encoder_transfer_test import ALPHA, ROOT  # noqa: E402

MARKS = ["f5-r2", "v5-r3", "wam", "vine-r"]
SEEDS = (12, 13, 14)


def directions(delta, source, arm):
    """delta (512,512,3) float64 -> dict kind -> direction (actual, gauss1, gauss2, phase1, phase2)."""
    import numpy as np
    mu = delta.mean(axis=(0, 1), keepdims=True)
    r = delta - mu
    out = {"actual": delta}

    def rng(kind, rep):
        seed = int.from_bytes(hashlib.sha256(f"et-final-mechanism-v1|{source}|{arm}|{kind}|{rep}".encode()).digest()[:8], "little")
        return np.random.Generator(np.random.PCG64(seed))
    for rep in (1, 2):
        g = rng("gaussian", rep).standard_normal(r.shape)
        g -= g.mean(axis=(0, 1), keepdims=True)
        target = np.linalg.norm(r.reshape(-1, 3), axis=0)
        have = np.linalg.norm(g.reshape(-1, 3), axis=0)
        out[f"gauss{rep}"] = mu + g * np.where(have > 0, target / np.maximum(have, 1e-300), 0)
    h, w = r.shape[:2]
    kk, ll = np.meshgrid(np.arange(h), np.arange(w), indexing="ij")
    mk, ml = (-kk) % h, (-ll) % w
    canon = (kk * w + ll) < (mk * w + ml)
    selfc = (kk == mk) & (ll == ml)
    for rep in (1, 2):
        gen = rng("phase", rep)
        f = np.fft.fft2(r, axes=(0, 1), norm="ortho")
        mag = np.abs(f)
        ph = np.zeros(r.shape)
        draw = gen.uniform(0, 2 * np.pi, size=r.shape)
        sign = np.where(gen.random(r.shape) < .5, 0.0, np.pi)
        for c in range(3):
            pc = np.zeros((h, w))
            pc[canon] = draw[..., c][canon]
            pc[mk[canon], ml[canon]] = -draw[..., c][canon]
            pc[selfc] = sign[..., c][selfc]
            ph[..., c] = pc
        g = mag * np.exp(1j * ph)
        g[0, 0, :] = 0
        out[f"phase{rep}"] = mu + np.real(np.fft.ifft2(g, axes=(0, 1), norm="ortho"))
    return out


class Encoders:
    """Native mode encoders on native preprocessing; differentiable in the direction (unit-norm trick)."""

    def __init__(self, fam, regen, resize_up):
        self.fam, self.regen, self.up = fam, regen, resize_up

    def tensor(self, rgb01):  # (512,512,3) float -> native preprocessed (1,3,H,W) in [-1,1]
        import torch
        x = torch.from_numpy(rgb01.astype("float32")).permute(2, 0, 1)[None].cuda()
        if self.fam in ("R1", "K3"):
            x = (self.up @ x @ self.up.T)  # Lanczos 512 -> 1024 as a linear map
        return x * 2 - 1

    def encode(self, x):
        import torch
        pipe = self.regen.pipe
        if self.fam == "K3":
            return pipe.movq.encode(x.to(pipe.movq.dtype))["latents"]
        vae = pipe.vae
        if self.fam == "R1":
            return vae.encode(x.float()).latent_dist.mode() * vae.config.scaling_factor
        return vae.encode(x.to(vae.dtype)).latent_dist.mode() * vae.config.scaling_factor

    @contextlib.contextmanager
    def fp32(self):
        """The official SDXL VAE encodes only in fp32 (the regenerator's checked encode); restore fp16 afterwards."""
        import torch
        if self.fam != "R1":
            yield
            return
        self.regen.pipe.vae.to(dtype=torch.float32)
        try:
            yield
        finally:
            self.regen.pipe.vae.to(dtype=torch.float16)

    def gain(self, rgb01, u):
        import torch
        from torch.func import jvp
        from torch.nn.attention import SDPBackend, sdpa_kernel
        x = self.tensor(rgb01)
        du = self.tensor(u + .5) - self.tensor(.5 + 0 * u)  # the linear map applied to u (offsets cancel)
        unit = (du.float() / du.float().norm()).to(x.dtype)
        with sdpa_kernel([SDPBackend.MATH]), torch.no_grad():
            _, zt = jvp(self.encode, (x,), (unit,))
        return float(zt.float().norm() * du.float().norm() / float(math.sqrt((u ** 2).sum())))


def e_vector(internal, source_rgb, profile):
    """e = w(original q)/sqrt(320): the semantic key chips selected by the original image's q (owner alpha)."""
    import numpy as np
    import f5_latent_codec as f5
    import revised_watermark_v5 as v5
    checked, key, config = v5._resolve(profile, None)
    q = v5._semantic(None, checked, key, config, internal.features(source_rgb, 7), binding=True)
    table = v5._semantic_table(v5.canonical_owner(ALPHA), key, config)
    w = [chip for segment in range(v5.CODE_BITS) for chip in table[segment][v5._bit(q, segment)]]
    return np.asarray(w, float) / math.sqrt(len(w))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--assets", type=Path, required=True)
    parser.add_argument("--images", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--families", default="R0,R1,K3")
    parser.add_argument("--limit-sources", type=int, default=12)
    parser.add_argument("--retry-errors", action="store_true", help="redo encoder-gain rows whose latest status is error_terminal")
    args = parser.parse_args()
    import numpy as np
    import torch
    import f5_latent_codec as f5
    import revised_watermark_v5 as v5
    (args.out / "mechanism").mkdir(parents=True, exist_ok=True)
    journal = pa.Journal(args.out / "mechanism.jsonl")
    native = pa.Journal(args.out / "native.jsonl")
    config, specs = pilot.channel_specs()
    profile = pilot.read(ROOT / config["profile_file"])
    order = pa.development_order()[:args.limit_sources]
    rgb = {(s, a): rt.load_rgb(args.images / f"clean_{s}_{a}_None_None.png") for s in order for a in ["unmarked", *MARKS]}
    checked, key, cfg = v5._resolve(profile, None)
    layout = f5.Layout(checked, key, cfg, v5.canonical_owner(ALPHA))
    reader = f5.Reader(args.assets / "a6", device="cuda")
    resize = pilot.Resize(1024, 512, torch)
    up = torch.from_numpy(pilot.lanczos_matrix(512, 1024)).float().cuda()
    # e vectors need the pinned CLIP features of the originals (CPU), computed once.
    e_path = args.out / "mechanism-e.json"
    if e_path.exists():
        evec = {int(k): np.asarray(v) for k, v in json.loads(e_path.read_text()).items()}
    else:
        internal = rt.Internal(args.assets, config)
        evec = {s: e_vector(internal, rt.load_rgb(args.assets / "sources" / f"{s}.png"), profile) for s in order}
        e_path.write_text(json.dumps({str(k): v.tolist() for k, v in evec.items()}))
        internal = None
        rt.release()

    def chips(img):
        return np.asarray(layout.projections(reader.latent(img)))

    clean_e = {}
    for s in order:
        clean_e[s] = float(evec[s] @ (chips(rgb[(s, "f5-r2")]) - chips(rgb[(s, "unmarked")])))
    journal.append(dict(id="clean-e", kind="clean_e", status="ok", values={str(k): v for k, v in clean_e.items()}))

    for fam in [x for x in args.families.split(",") if x]:
        regen = rt.Regenerator(args.assets, specs[fam])
        pipe = regen.pipe
        modules = [pipe.unet, pipe.movq if fam == "K3" else pipe.vae]
        enc = Encoders(fam, regen, up)
        with pilot.ClassicAttention(*modules):
            # 2. Encoder gains (720 over all families).
            for s in order:
                x01 = rgb[(s, "unmarked")].astype("float64") / 255
                for arm in MARKS:
                    uid = f"gain:{fam}:{s}:{arm}"
                    if journal.done(uid) and not (args.retry_errors and journal.latest[uid]["status"] == "error_terminal"):
                        continue
                    row = dict(id=uid, kind="gain", family=fam, source=s, arm=arm)
                    try:
                        delta = (rgb[(s, arm)].astype("float64") - rgb[(s, "unmarked")].astype("float64")) / 255
                        dirs = directions(delta, s, arm)
                        with enc.fp32():
                            row["gains"] = {k: enc.gain(x01, u) for k, u in dirs.items()}
                        with torch.no_grad(), enc.fp32():
                            z0 = enc.encode(enc.tensor(x01)).float()
                            z1 = enc.encode(enc.tensor(rgb[(s, arm)].astype("float64") / 255)).float()
                        row["finite_gain_actual"] = float((z1 - z0).norm() / math.sqrt((delta ** 2).sum()))
                        row["out_of_range_fraction"] = {k: float(((x01 + u < 0) | (x01 + u > 1)).mean()) for k, u in dirs.items()}
                        row["status"] = "ok"
                    except Exception:
                        row.update(status="error_terminal", error=traceback.format_exc()[-1500:])
                    journal.append(row)
            print(f"[{time.strftime('%H:%M:%S')}] {fam} gains done", flush=True)
            # 3 and 4. Stage outputs and differential chain tangents at .2, per source and seed.
            for s in order:
                for seed in SEEDS:
                    uid = f"stage:{fam}:{s}:{seed}"
                    if journal.done(uid):
                        continue
                    row = dict(id=uid, kind="stage", family=fam, source=s, seed=seed, stages={}, tangents={})
                    tick = time.monotonic()
                    try:
                        tape, hooks = pilot.Tape(), pilot.Hooks(pipe)
                        c0_native = pa.run_native(fam, regen, rgb[(s, "unmarked")], .2, seed, tape.record(), hooks)
                        calls = [(pilot.detach_tree(a), pilot.detach_tree(k)) for a, k in hooks.calls]
                        states, draws = hooks.states, tape.draws
                        t0 = int(calls[0][0][1])
                        sched = pipe.scheduler
                        outs = {}
                        for arm in ["unmarked", *MARKS]:
                            inp = pilot.native_input(fam, rgb[(s, arm)])
                            stage = {}
                            with torch.no_grad():
                                if fam == "K3":
                                    z = pilot.encode_terms(fam, regen, inp)["z"]
                                    dec = lambda zz: (pipe.movq.decode(zz, force_not_quantize=True)["sample"].float() * .5 + .5).clamp(0, 1)
                                    if seed == SEEDS[0]:  # deterministic: one output per input
                                        stage["mode_codec"] = dec(z)
                                    stage["noise_only"] = dec(sched.add_noise(z, draws[0].to(z.dtype), torch.tensor([t0], device="cuda")))
                                else:
                                    terms = pilot.encode_terms(fam, regen, inp)
                                    sf = pipe.vae.config.scaling_factor
                                    vae = pipe.vae
                                    if fam == "R1":
                                        vae.to(dtype=torch.float32)
                                    def dec(zz):
                                        dz = zz.float() if fam == "R1" else zz.to(vae.dtype)
                                        return (vae.decode(dz / sf, return_dict=False)[0].float() / 2 + .5).clamp(0, 1)
                                    zmode = sf * terms["mean"].to(torch.float16)
                                    zsamp = sf * (terms["mean"] + terms["std"] * draws[0]).to(torch.float16)
                                    if seed == SEEDS[0]:  # deterministic: one output per input
                                        stage["mode_codec"] = dec(zmode)
                                    stage["sampled_codec"] = dec(zsamp)
                                    stage["noise_only"] = dec(sched.add_noise(zsamp, draws[1].to(zsamp.dtype), torch.tensor([t0], device="cuda")))
                                    zz = sched.add_noise(zmode, draws[1].to(zmode.dtype), torch.tensor([t0], device="cuda"))
                                    for (a, kw), t in zip(calls, [int(c[0][1]) for c in calls]):
                                        pred = pipe.unet.forward(sched.scale_model_input(zz, t), t, **kw)
                                        pred = pred[0] if isinstance(pred, tuple) else pred.sample
                                        zz = sched.step(pred, t, zz, return_dict=False, eta=0., generator=None)[0]
                                    stage["mode_reverse"] = dec(zz)
                                    if fam == "R1":
                                        vae.to(dtype=torch.float16)
                            imgs = {}
                            for k, img in stage.items():
                                img = resize(img) if img.shape[-1] != 512 else img
                                imgs[k] = (img[0].permute(1, 2, 0).double().cpu().numpy() * 255).round().clip(0, 255).astype("uint8")
                            if fam == "K3":
                                imgs["native"] = c0_native if arm == "unmarked" else pa.run_native(fam, regen, rgb[(s, arm)], .2, seed + 1000, tape.replay())
                            else:
                                n = native.latest.get(f"native:{fam}-0.2:{s}:{seed}:{arm}")
                                if n and n.get("status") == "ok":
                                    imgs["native"] = rt.load_rgb(n["output"]["path"])
                            outs[arm] = imgs
                        for k in outs["unmarked"]:
                            c0 = outs["unmarked"][k]
                            c0_chips = chips(c0)
                            entry = {}
                            for arm in MARKS:
                                if k not in outs[arm]:
                                    continue
                                y = outs[arm][k]
                                rt.save_rgb(args.out / "mechanism" / f"{fam}_{k}_{s}_{arm}_{seed}.png", y)
                                e = dict(pixel_residual_rms=float(np.sqrt((((y.astype(float) - c0.astype(float)) / 255) ** 2).mean())),
                                         reader_latent_residual=float(np.linalg.norm(reader.latent(y) - reader.latent(c0))))
                                if arm == "f5-r2":
                                    dp = chips(y) - c0_chips
                                    e.update(chip_change_norm=float(np.linalg.norm(dp)), signed_transport=float(evec[s] @ dp),
                                             retention_vs_clean=float(evec[s] @ dp) / clean_e[s] if clean_e[s] else None)
                                entry[arm] = e
                            rt.save_rgb(args.out / "mechanism" / f"{fam}_{k}_{s}_unmarked_{seed}.png", c0)
                            row["stages"][k] = entry
                        # 4. F5 differential chain tangents along the five directions.
                        delta = (rgb[(s, "f5-r2")].astype("float64") - rgb[(s, "unmarked")].astype("float64")) / 255
                        x01 = rgb[(s, "unmarked")].astype("float64") / 255
                        for kind, u in directions(delta, s, "f5-r2").items():
                            from torch.func import jvp
                            from torch.nn.attention import SDPBackend, sdpa_kernel
                            x = enc.tensor(x01)
                            du = enc.tensor(u + .5) - enc.tensor(.5 + 0 * u)
                            scale = du.float().norm()
                            unit = (du.float() / scale)
                            if fam == "K3":
                                f = lambda xx: pipe.movq.encode(xx.to(pipe.movq.dtype))["latents"].float()
                                xin = x
                            else:
                                vae = pipe.vae
                                sf = vae.config.scaling_factor
                                eta = draws[0]
                                if fam == "R1":
                                    vae.to(dtype=torch.float32)
                                def f(xx, vae=vae, sf=sf, eta=eta):
                                    post = vae.encode(xx.to(vae.dtype)).latent_dist
                                    return (sf * (post.mean + post.std * eta.to(post.mean.dtype))).float()
                                xin = x
                            dt = torch.float32 if fam == "R1" else (pipe.movq.dtype if fam == "K3" else pipe.vae.dtype)
                            with sdpa_kernel([SDPBackend.MATH]), torch.no_grad():
                                _, dz = jvp(f, (xin.to(dt),), (unit.to(dt),))
                            if fam == "R1":
                                pipe.vae.to(dtype=torch.float16)
                            dz = dz.float() * scale
                            v, diag = pa.law_tangent(fam, regen, reader, layout, resize, calls, states, draws,
                                                     pilot.native_input(fam, rgb[(s, "unmarked")]), None, d_override=dz)
                            un = float(math.sqrt((u ** 2).sum()))
                            row["tangents"][kind] = dict(v_norm=float(np.linalg.norm(v)), e_v=float(evec[s] @ v), e_v_per_u=float(evec[s] @ v) / un,
                                                         latent_displacement_norm=float(dz.norm()), u_norm=un,
                                                         max_primal_err=max(diag["step_primal_rel_err"]))
                        row["status"] = "ok"
                    except Exception:
                        row.update(status="error_terminal", error=traceback.format_exc()[-2500:])
                    row["seconds"] = time.monotonic() - tick
                    journal.append(row)
                    print(f"[{time.strftime('%H:%M:%S')}] {uid} {row['status']} {row['seconds']:.1f}s", flush=True)
                    rt.release()
        regen = None
        rt.release()


if __name__ == "__main__":
    main()
