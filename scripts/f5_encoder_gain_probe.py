"""Family 5 probe: can the attacker's own VAE encoder amplify an invisible mark?

Regeneration removal bounds (Zhao et al. 2023) are stated where the noise is
added: in SD's VAE latent.  They assume an invisible pixel change makes a small
latent change.  The SD VAE encoder is not robust (PhotoGuard's encoder attack
moves the latent far with a small pixel change), so that premise can fail.

For each development source x and each latent band b (radial cycles/image on
the 64x64 latent, all four channels), a fixed keyed unit latent pattern P is
chosen and two pixel changes with the same PSNR are built:

* natural: the decoder rendering D(z+aP)-D(z), scaled to the PSNR (A-C style);
* encoder: projected gradient ascent on <E(x+d), P> through the frozen fp32
  encoder, under the same L2 budget and the [0,1] box.

Both are rounded to RGB8.  Reported per source, band and variant: the clean
latent signal s0 = <z(x+d)-z(x), P> read with the attack's own fp16 encoder;
after the pinned img2img (strengths .1/.2/.4, seed 0, same seed for x and x+d)
the kept signal s = <z(A(x+d))-z(A(x)), P>; the attack-induced noise sigma_a
(std of <z(A(x))-z(x), Q> over 64 null patterns Q of the band) and the host
spread sigma_h (std of <z(A(x)), Q>).  s/sigma_a is what an informed embedder
could reach, s/sigma_h what a blind reader sees without host cancellation.
LPIPS of each marked image to x is reported.  Exploratory development
measurement; no detector, threshold or held-out data.
"""
from __future__ import annotations

import argparse, json, math, subprocess, sys, time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from f4_transfer_probe import SOURCES, ASSETS  # noqa: E402

LATENT = 64
SCALE = 0.18215
BANDS = ((2, 8), (8, 16), (16, 32))
NULLS = 64


def band_pattern(band, seed):
    rng = np.random.default_rng(seed)
    f = np.fft.fftfreq(LATENT) * LATENT
    r = np.hypot(f[:, None], f[None, :])
    keep = (r >= band[0]) & (r < band[1])
    out = np.stack([np.real(np.fft.ifft2(np.fft.fft2(rng.standard_normal((LATENT, LATENT))) * keep)) for _ in range(4)])
    return out / np.linalg.norm(out)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--sources", type=int, nargs="*", default=None)
    p.add_argument("--psnr", type=float, default=40.0)
    p.add_argument("--steps", type=int, default=100)
    p.add_argument("--strengths", type=float, nargs="+", default=[0.1, 0.2, 0.4])
    a = p.parse_args()
    import torch
    from PIL import Image
    from diffusers import AutoencoderKL
    import three_threat_models as models

    a.output_dir.mkdir(parents=True, exist_ok=False)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    pipe = models.load_regenerator(ASSETS)
    vae32 = AutoencoderKL.from_pretrained(ASSETS / "sd15-fp16/vae", variant="fp16", use_safetensors=True,
                                          local_files_only=True, torch_dtype=torch.float32).eval().requires_grad_(False).to("cuda")
    import importlib.metadata
    from m1_latent_reconstruction import quality
    metric = models.load_lpips(ASSETS, Path(importlib.metadata.distribution("lpips").locate_file("lpips")))

    keys = {band: band_pattern(band, 7000 + i) for i, band in enumerate(BANDS)}
    nulls = {band: [band_pattern(band, 9000 + 100 * i + j) for j in range(NULLS)] for i, band in enumerate(BANDS)}
    n_pix = 3 * 512 * 512
    budget = 10 ** (-a.psnr / 20) * math.sqrt(n_pix)  # L2 norm in [0,1] units

    def to_t(rgb01):
        return torch.from_numpy(np.ascontiguousarray(rgb01.transpose(2, 0, 1)))[None].float().cuda() * 2 - 1

    def z16(rgb01):
        with torch.inference_mode():
            t = to_t(rgb01).half()
            return (pipe.vae.encode(t).latent_dist.mode()[0].float() * SCALE).cpu().numpy().astype(np.float64)

    def attack(rgb01, strength):
        img = Image.fromarray(np.clip(np.rint(rgb01 * 255), 0, 255).astype(np.uint8))
        with torch.inference_mode():
            out = pipe(prompt="", negative_prompt="", image=img, strength=strength, num_inference_steps=20,
                       eta=0.0, guidance_scale=1.0, generator=torch.Generator(device="cuda").manual_seed(0),
                       num_images_per_prompt=1, output_type="pil", return_dict=True)
        return np.asarray(models.validate_generated(out), np.float64) / 255

    def rgb8(x):
        return np.clip(np.rint(x * 255), 0, 255) / 255

    def natural(x, band):
        with torch.no_grad():
            u0 = vae32.encode(to_t(x)).latent_dist.mode()
            P = torch.from_numpy(keys[band])[None].float().cuda()
            d0 = (vae32.decode(u0).sample + 1) / 2
            d1 = (vae32.decode(u0 + P / SCALE).sample + 1) / 2
        r = (d1 - d0)[0].permute(1, 2, 0).double().cpu().numpy()
        r *= budget / np.linalg.norm(r)
        return rgb8(np.clip(x + r, 0, 1))

    def encoder_attack(x, band):
        xt = torch.from_numpy(np.ascontiguousarray(x.transpose(2, 0, 1)))[None].float().cuda()
        P = torch.from_numpy(keys[band])[None].float().cuda()
        delta = torch.zeros_like(xt, requires_grad=True)
        for step in range(a.steps):
            lr = budget * (0.25 if step < a.steps // 2 else 0.08)
            z = vae32.encode((xt + delta) * 2 - 1).latent_dist.mode() * SCALE
            obj = (z * P).sum()
            g, = torch.autograd.grad(obj, delta)
            with torch.no_grad():
                delta += lr * g / (g.norm() + 1e-12)
                delta.copy_((xt + delta).clamp(0, 1) - xt)
                n = delta.norm()
                if n > budget:
                    delta *= budget / n
        out = (xt + delta.detach())[0].permute(1, 2, 0).double().cpu().numpy()
        return rgb8(out)

    def proj(z, pattern):
        return float(np.sum(z * pattern))

    rows, tick = [], time.monotonic()
    sources = {k: v for k, v in SOURCES.items() if a.sources is None or k in a.sources}
    with (a.output_dir / "rows.jsonl").open("w", encoding="utf-8") as log:
        for sid, path in sources.items():
            x = np.asarray(Image.open(path).convert("RGB"), np.float64) / 255
            zx = z16(x)
            variants = {}
            for band in BANDS:
                variants[f"natural|{band[0]}-{band[1]}"] = (band, natural(x, band))
                variants[f"encoder|{band[0]}-{band[1]}"] = (band, encoder_attack(x, band))
            base = {}
            for s in a.strengths:
                try:
                    base[s] = attack(x, s)
                except RuntimeError as error:
                    base[s] = str(error)
            for name, (band, xw) in variants.items():
                mse = float(np.mean((xw - x) ** 2))
                x8, w8 = np.rint(x * 255).astype(np.uint8), np.rint(xw * 255).astype(np.uint8)
                s0 = proj(z16(xw) - zx, keys[band])
                row = dict(source=sid, variant=name, band=band, psnr_db=10 * math.log10(1 / mse),
                           lpips=float(models.lpips_score(metric, x8, w8)), ssim=quality(x8, w8)["ssim_rgb"],
                           clean_signal=s0, after={})
                for s in a.strengths:
                    if isinstance(base[s], str):
                        row["after"][str(s)] = dict(outcome=base[s]); continue
                    try:
                        out = attack(xw, s)
                    except RuntimeError as error:
                        row["after"][str(s)] = dict(outcome=str(error)); continue
                    zb, zo = z16(base[s]), z16(out)
                    kept = proj(zo - zb, keys[band])
                    sig_a = float(np.std([proj(zb - zx, Q) for Q in nulls[band]]))
                    sig_h = float(np.std([proj(zb, Q) for Q in nulls[band]]))
                    row["after"][str(s)] = dict(outcome="completed", kept=kept, gain=kept / s0 if s0 else None,
                                                sigma_attack=sig_a, sigma_host=sig_h,
                                                z_informed=kept / sig_a, z_blind=kept / sig_h)
                rows.append(row); log.write(json.dumps(row) + "\n"); log.flush()
            print(f"source {sid} done, {time.monotonic() - tick:.0f}s", flush=True)

    summary = {}
    for name in sorted({r["variant"] for r in rows}):
        sel = [r for r in rows if r["variant"] == name]
        entry = dict(n=len(sel), psnr_median=float(np.median([r["psnr_db"] for r in sel])),
                     clean_signal_median=float(np.median([r["clean_signal"] for r in sel])))
        entry["lpips_median"] = float(np.median([r["lpips"] for r in sel]))
        entry["lpips_max"] = float(np.max([r["lpips"] for r in sel]))
        for s in a.strengths:
            got = [r["after"][str(s)] for r in sel if r["after"][str(s)].get("outcome") == "completed"]
            if got:
                entry[str(s)] = dict(n=len(got), kept_median=float(np.median([g["kept"] for g in got])),
                                     gain_median=float(np.median([g["gain"] for g in got])),
                                     z_informed_median=float(np.median([g["z_informed"] for g in got])),
                                     z_informed_min=float(np.min([g["z_informed"] for g in got])),
                                     z_blind_median=float(np.median([g["z_blind"] for g in got])))
        summary[name] = entry
    run = dict(schema="f5-encoder-gain-probe-v1", data_split="development", commit=commit, command=sys.argv,
               psnr_db=a.psnr, steps=a.steps, bands=BANDS, strengths=a.strengths, sources=list(sources),
               attack="pinned SD1.5 DDIM img2img, 20 steps, empty prompt, CFG 1, eta 0, seed 0 for x and x+d",
               duration_seconds=time.monotonic() - tick, outcome="completed", summary=summary)
    (a.output_dir / "run.json").write_text(json.dumps(run, indent=1), encoding="utf-8")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
