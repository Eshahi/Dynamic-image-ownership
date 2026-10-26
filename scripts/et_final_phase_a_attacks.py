"""Final-study Phase A, stage 2: informed attacks A and B, quality-only grids, selection freeze and controls.

Written by Claude (Opus 5.5) on 2026-10-26 under the user's Phase-A approval (option (a)). Implements
research/encoder-transfer-20261019/final-study-20261025/05-informed-attacks.md exactly:
  A(u, s, seed) = pinned R0 SD1.5 img2img(saved 512 RGB8 of pinned R1 SDXL img2img(u, s, seed), s, seed + 100),
     s in {.05, .1, .15, .2}, seeds 12/13/14; native kernels of the new study (option (a));
  B(u, epsilon, lambda): SD1.5 fp32 posterior-mode latent, cached 20-step DDIM inversion with the explicit inverse
     scheduler, 20 normalized-gradient steps on .5*(LPIPS/.15 + MSE/10^-2.5) + lambda*cos(z, n)^2 inside an
     epsilon box; epsilon in {.025, .075, .225}, lambda in {.1, 1, 10}.
Quality is against the published input u only (LPIPS/PSNR/SSIM with the pinned helpers; LPIPS evaluated on the GPU
with the pinned weights). Selection uses only quality: eligibility (A: >=48/60 passing sources and >=144/180 passing
outputs per arm; B: >=48/60 per arm), score = min over arms of the mean min(LPIPS/.15, 1) with missing = 0, highest
score rounded to 6 decimals, ties by lower call cost then ascending parameters. No detector is loaded in this stage.

Usage: python scripts/et_final_phase_a_attacks.py --stage grid|select|controls --assets ... --images ... --out ...
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import encoder_transfer_runtime as rt  # noqa: E402
import et_final_pilot as pilot  # noqa: E402
import et_final_phase_a as pa  # noqa: E402

MARKS = ["f5-r2", "v5-r3", "wam", "vine-r"]
A_GRID = (.05, .1, .15, .2)
B_GRID = [(e, l) for e in (.025, .075, .225) for l in (.1, 1.0, 10.0)]
SEEDS = (12, 13, 14)


class Quality:
    def __init__(self, assets):
        import importlib.metadata
        import three_threat_models as models
        from m1_latent_reconstruction import quality
        self.quality = quality
        self.metric = models.load_lpips(assets / "a6", Path(importlib.metadata.distribution("lpips").locate_file("lpips"))).cuda().eval()

    def lpips(self, a, b):
        import torch
        def tensor(rgb):  # three_threat_models.lpips_score conversion, on the GPU
            return torch.from_numpy(rgb.copy()).permute(2, 0, 1).unsqueeze(0).float().cuda() / 255 * 2 - 1
        with torch.inference_mode():
            score = self.metric(tensor(a), tensor(b), normalize=False)
        if score.numel() != 1 or not bool(torch.isfinite(score).all()):
            raise RuntimeError("invalid LPIPS score")
        return float(score.item())

    def __call__(self, reference, rgb):
        q = dict(self.quality(reference, rgb))
        q["lpips"] = self.lpips(reference, rgb)
        return q


def passes(q):
    return q is not None and q.get("lpips") is not None and q["lpips"] <= .15 and \
        (q.get("psnr_infinite") is True or (q.get("psnr_db") or 0) >= 25) and (q.get("ssim_rgb") or 0) >= .75


class AttackB:
    def __init__(self, assets, r0):
        import importlib.metadata
        import torch
        import three_threat_models as models
        from diffusers import AutoencoderKL, DDIMInverseScheduler
        self.torch = torch
        self.pipe = r0.pipe
        self.vae = AutoencoderKL.from_pretrained(assets / "a6/sd15-fp16/vae", variant="fp16", use_safetensors=True,
                                                 local_files_only=True, torch_dtype=torch.float32).eval().requires_grad_(False).cuda()
        self.lp = models.load_lpips(assets / "a6", Path(importlib.metadata.distribution("lpips").locate_file("lpips"))).cuda().eval()
        for p in self.lp.parameters():
            p.requires_grad_(False)
        self.sf = self.pipe.vae.config.scaling_factor
        with torch.no_grad():
            self.embeds = self.pipe.encode_prompt("", "cuda", 1, False)[0]
        self.inverse = DDIMInverseScheduler(num_train_timesteps=1000, beta_start=.00085, beta_end=.012, beta_schedule="scaled_linear",
                                            prediction_type="epsilon", clip_sample=False, set_alpha_to_one=True, steps_offset=1,
                                            timestep_spacing="leading", rescale_betas_zero_snr=False)
        self.cache = {}

    def encode(self, u):
        with self.torch.no_grad():
            return self.vae.encode(u * 2 - 1).latent_dist.mode() * self.sf

    def decode(self, z):
        return (self.vae.decode(z / self.sf).sample / 2 + .5).clamp(0, 1)

    def invert(self, key, z0):
        if key in self.cache:
            return self.cache[key]
        t = self.torch
        self.inverse.set_timesteps(20, device="cuda")
        z = z0.float()
        with t.no_grad():
            for step in self.inverse.timesteps:
                e = self.pipe.unet(self.inverse.scale_model_input(z, step).half(), step, encoder_hidden_states=self.embeds).sample.float()
                z = self.inverse.step(e, step, z).prev_sample
        self.cache[key] = z.detach()
        return self.cache[key]

    def __call__(self, key, rgb8, epsilon, lam, invert=True):
        t = self.torch
        u = t.from_numpy(rgb8.astype("float32") / 255).permute(2, 0, 1)[None].cuda()
        z0 = self.encode(u)
        n = self.invert(key, z0) if invert else None
        if not (t.isfinite(z0).all() and z0.norm() > 0) or (n is not None and not (t.isfinite(n).all() and n.norm() > 0)):
            raise FloatingPointError("zero or nonfinite reference norm")

        def cosine(a, b):
            return ((a * b).sum() / (a.norm().clamp_min(1e-12) * b.norm().clamp_min(1e-12))).clamp(-1, 1)

        z = z0.clone()
        step = epsilon / 10
        log = dict(initial_cosine=None if n is None else float(cosine(z0, n)))
        for _ in range(20):
            z = z.detach().requires_grad_(True)
            v = self.decode(z)
            loss = .5 * (self.lp(v * 2 - 1, u * 2 - 1, normalize=False).sum() / .15 + ((v - u) ** 2).mean() / 10 ** -2.5)
            if n is not None and lam:
                loss = loss + lam * cosine(z, n) ** 2
            g, = t.autograd.grad(loss, z)
            if not (t.isfinite(loss) and t.isfinite(g).all()):
                raise FloatingPointError("nonfinite attack B step")
            with t.no_grad():
                z = z - step * g / (g.pow(2).mean().sqrt() + 1e-12)
                z = z0 + (z - z0).clamp(-epsilon, epsilon)
        with t.no_grad():
            out = (self.decode(z) * 255 + .5).floor().clamp(0, 255)[0].permute(1, 2, 0).to("cpu", t.uint8).numpy().copy()
            log.update(final_cosine=None if n is None else float(cosine(z, n)), final_loss=float(loss),
                       box_fraction=float(((z - z0).abs() >= epsilon * (1 - 1e-6)).float().mean()))
        return out, log

    def codec(self, rgb8):
        t = self.torch
        u = t.from_numpy(rgb8.astype("float32") / 255).permute(2, 0, 1)[None].cuda()
        with t.no_grad():
            return (self.decode(self.encode(u)) * 255 + .5).floor().clamp(0, 255)[0].permute(1, 2, 0).to("cpu", t.uint8).numpy().copy()


def attack_a(regens, rgb, s, seed):
    first = pa.run_native("R1", regens["R1"], rgb, s, seed)
    final = pa.run_native("R0", regens["R0"], first, s, seed + 100)
    return first, final


def load_regens(assets, specs):
    regens = {fam: rt.Regenerator(assets, specs[fam]) for fam in ("R0", "R1")}
    contexts = [pilot.ClassicAttention(regens["R0"].pipe.unet, regens["R0"].pipe.vae),
                pilot.ClassicAttention(regens["R1"].pipe.unet, regens["R1"].pipe.vae)]
    return regens, contexts


def grid(args, journal, order, rgb, specs, which):
    qual = Quality(args.assets)
    regens, contexts = load_regens(args.assets, specs)
    for c in contexts:
        c.__enter__()
    try:
        if "A" in which:
            for s in A_GRID:
                for source in order:
                    for arm in MARKS:
                        for seed in SEEDS:
                            uid = f"gridA:{s}:{source}:{arm}:{seed}"
                            if journal.done(uid):
                                continue
                            row = dict(id=uid, kind="gridA", strength=s, source=source, arm=arm, seed=seed)
                            tick = time.monotonic()
                            try:
                                first, final = attack_a(regens, rgb[(source, arm)], s, seed)
                                row["first"] = rt.save_rgb(args.out / "attacks" / f"A1_{s}_{source}_{arm}_{seed}.png", first)
                                row["output"] = rt.save_rgb(args.out / "attacks" / f"A_{s}_{source}_{arm}_{seed}.png", final)
                                row["quality"] = qual(rgb[(source, arm)], final)
                                row["status"] = "ok"
                            except Exception as exc:
                                row["status"] = "safety_blocked" if "safety" in str(exc).lower() or "nsfw" in str(exc).lower() else "error_terminal"
                                row["error"] = traceback.format_exc()[-1500:]
                            row["seconds"] = time.monotonic() - tick
                            journal.append(row)
                print(f"[{time.strftime('%H:%M:%S')}] A grid s={s} done", flush=True)
        if "B" in which:
            attack = AttackB(args.assets, regens["R0"])
            for eps, lam in B_GRID:
                for source in order:
                    for arm in MARKS:
                        uid = f"gridB:{eps}:{lam}:{source}:{arm}"
                        if journal.done(uid):
                            continue
                        row = dict(id=uid, kind="gridB", epsilon=eps, lam=lam, source=source, arm=arm)
                        tick = time.monotonic()
                        try:
                            out, log = attack(f"{source}:{arm}", rgb[(source, arm)], eps, lam)
                            row["output"] = rt.save_rgb(args.out / "attacks" / f"B_{eps}_{lam}_{source}_{arm}.png", out)
                            row["quality"] = qual(rgb[(source, arm)], out)
                            row["log"] = log
                            row["status"] = "ok"
                        except Exception:
                            row["status"] = "error_terminal"
                            row["error"] = traceback.format_exc()[-1500:]
                        row["seconds"] = time.monotonic() - tick
                        journal.append(row)
                print(f"[{time.strftime('%H:%M:%S')}] B grid {eps},{lam} done", flush=True)
    finally:
        for c in reversed(contexts):
            c.__exit__(None, None, None)


def select(journal, order):
    rows = [r for r in journal.latest.values() if r["kind"] in ("gridA", "gridB")]
    result = {}
    for attack, params in (("A", [(s,) for s in A_GRID]), ("B", B_GRID)):
        table = []
        for theta in params:
            arms = {}
            for arm in MARKS:
                outputs, sources_pass, budget = 0, 0, []
                for source in order:
                    if attack == "A":
                        rs = [journal.latest.get(f"gridA:{theta[0]}:{source}:{arm}:{seed}") for seed in SEEDS]
                    else:
                        rs = [journal.latest.get(f"gridB:{theta[0]}:{theta[1]}:{source}:{arm}")]
                    ok = [r is not None and r.get("status") == "ok" and passes(r.get("quality")) for r in rs]
                    outputs += sum(ok)
                    sources_pass += int(sum(ok) >= (2 if attack == "A" else 1))
                    for r in rs:
                        q = (r or {}).get("quality") if (r or {}).get("status") == "ok" else None
                        budget.append(min(q["lpips"] / .15, 1.0) if q and q.get("lpips") is not None else 0.0)
                arms[arm] = dict(passing_sources=sources_pass, passing_outputs=outputs, scheduled_outputs=len(budget),
                                 mean_budget_use=sum(budget) / len(budget))
            eligible = all(a["passing_sources"] >= 48 and (attack == "B" or a["passing_outputs"] >= 144) for a in arms.values())
            score = min(a["mean_budget_use"] for a in arms.values())
            cost = theta[0] if attack == "A" else 0.0  # A: more updates per pass at higher strength; B: equal cost
            table.append(dict(theta=list(theta), eligible=eligible, score=round(score, 6), cost=cost, arms=arms))
        eligible = [t for t in table if t["eligible"]]
        chosen = sorted(eligible, key=lambda t: (-t["score"], t["cost"], t["theta"]))[0] if eligible else None
        result[attack] = dict(status="SELECTED" if chosen else "INACTIVE_QUALITY_INELIGIBLE",
                              selected=chosen["theta"] if chosen else None, candidates=table,
                              planned_grid_rows=len(params) * len(order) * len(MARKS) * (3 if attack == "A" else 1),
                              observed_grid_rows=sum(1 for r in rows if r["kind"] == f"grid{attack}"))
    return result


def controls(args, journal, order, rgb, specs, freeze):
    """After the selection freeze: selected attacks on C0, B-fidelity and B-codec on all five inputs (A-first is retained
    from the grid at the selected strength)."""
    qual = Quality(args.assets)
    regens, contexts = load_regens(args.assets, specs)
    for c in contexts:
        c.__enter__()
    try:
        a_sel, b_sel = freeze["A"]["selected"], freeze["B"]["selected"]
        if a_sel:
            s = a_sel[0]
            for source in order:
                for seed in SEEDS:
                    uid = f"ctrlA:{s}:{source}:unmarked:{seed}"
                    if journal.done(uid):
                        continue
                    row = dict(id=uid, kind="ctrlA", strength=s, source=source, arm="unmarked", seed=seed)
                    try:
                        first, final = attack_a(regens, rgb[(source, "unmarked")], s, seed)
                        row["first"] = rt.save_rgb(args.out / "attacks" / f"A1_{s}_{source}_unmarked_{seed}.png", first)
                        row["output"] = rt.save_rgb(args.out / "attacks" / f"A_{s}_{source}_unmarked_{seed}.png", final)
                        row["quality"] = qual(rgb[(source, "unmarked")], final)
                        row["status"] = "ok"
                    except Exception as exc:
                        row["status"] = "safety_blocked" if "safety" in str(exc).lower() or "nsfw" in str(exc).lower() else "error_terminal"
                        row["error"] = traceback.format_exc()[-1500:]
                    journal.append(row)
        attack = AttackB(args.assets, regens["R0"])
        for source in order:
            for arm in ["unmarked", *MARKS]:
                jobs = [("codec", None)]
                if b_sel:
                    jobs.append(("fidelity", (b_sel[0], 0.0)))
                    if arm == "unmarked":
                        jobs.append(("selected", tuple(b_sel)))
                for kind, theta in jobs:
                    uid = f"ctrlB-{kind}:{source}:{arm}"
                    if journal.done(uid):
                        continue
                    row = dict(id=uid, kind=f"ctrlB-{kind}", theta=theta, source=source, arm=arm)
                    try:
                        if kind == "codec":
                            out, log = attack.codec(rgb[(source, arm)]), {}
                        else:
                            out, log = attack(f"{source}:{arm}", rgb[(source, arm)], theta[0], theta[1], invert=(kind == "selected"))
                        row["output"] = rt.save_rgb(args.out / "attacks" / f"B{kind}_{source}_{arm}.png", out)
                        row["quality"] = qual(rgb[(source, arm)], out)
                        row["log"] = log
                        row["status"] = "ok"
                    except Exception:
                        row["status"] = "error_terminal"
                        row["error"] = traceback.format_exc()[-1500:]
                    journal.append(row)
    finally:
        for c in reversed(contexts):
            c.__exit__(None, None, None)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--stage", choices=("grid", "select", "controls"), required=True)
    parser.add_argument("--attacks", default="A,B")
    parser.add_argument("--assets", type=Path, required=True)
    parser.add_argument("--images", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--limit-sources", type=int, default=60)
    args = parser.parse_args()
    (args.out / "attacks").mkdir(parents=True, exist_ok=True)
    journal = pa.Journal(args.out / "attacks.jsonl")
    order = pa.development_order()[:args.limit_sources]
    rgb = {(s, a): rt.load_rgb(args.images / f"clean_{s}_{a}_None_None.png") for s in order for a in ["unmarked", *MARKS]}
    _, specs = pilot.channel_specs()
    freeze_path = args.out / "attack-freeze.json"
    if args.stage == "grid":
        grid(args, journal, order, rgb, specs, args.attacks.split(","))
    elif args.stage == "select":
        if freeze_path.exists():
            raise SystemExit("attack freeze already exists; it is immutable")
        result = select(journal, order)
        result["frozen_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        result["rule"] = "05-informed-attacks.md: quality-only eligibility and budget-use score; no detector output exists at freeze"
        pa.Journal  # noqa: B018
        freeze_path.write_text(json.dumps(result, indent=1), encoding="utf-8")
        print(json.dumps({k: (v["status"], v["selected"]) for k, v in result.items() if isinstance(v, dict) and "status" in v}))
    else:
        controls(args, journal, order, rgb, specs, json.loads(freeze_path.read_text(encoding="utf-8")))


if __name__ == "__main__":
    main()
