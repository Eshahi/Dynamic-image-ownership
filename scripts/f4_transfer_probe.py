"""Family 4, step 1: measure what SD1.5 img2img regeneration keeps, per spatial band and colour channel.

For each development source x, band b and colour axis c, a fixed random pattern
d limited to that band and axis is added at a small fixed RMS.  The pinned
img2img attack A is run on x and on x+d with the same seed, so A(x+d)-A(x)
isolates what survives of d.  Per (strength, band, axis) the probe reports

* gain     g = <A(x+d)-A(x), d> / <d, d>         (fraction of the pattern kept)
* host     h = mean power per orthonormal FFT coefficient of A(x) in the band
* score    s = g * sqrt(E) / sqrt(h)              (normalized correlation a
  matched detector would see after the attack if the whole 35.5 dB budget E
  were spent in that cell; host not cancelled)

Exploratory development measurement on the twelve development sources; no
detector, threshold or held-out data is involved.
"""
from __future__ import annotations

import argparse, json, math, subprocess, sys, time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
MAIN = Path("W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5")
ASSETS = MAIN / ".thesis-build/assets/a6"
DEV = MAIN / ".thesis-build/dev-runs"
SOURCES = {
    1675: DEV / "20261004-1102-e2e-1675/1675-C0-clean.png",
    4795: DEV / "20261004-1122-e2e-4795/4795-C0-clean.png",
    6012: DEV / "20261004-1142-e2e-6012/6012-C0-clean.png",
    **{i: DEV / f"20261004-1207-e2e-expansion-queue/e2e-{i}/{i}-C0-clean.png"
       for i in (25394, 80932, 109798, 134882, 147498, 177015, 190676, 468505, 499768)},
}
BANDS = ((1, 2), (2, 4), (4, 8), (8, 16), (16, 32), (32, 64), (64, 128), (128, 256))
AXES = {  # orthonormal colour basis in RGB
    "lum": np.array([1, 1, 1]) / math.sqrt(3),
    "rg": np.array([1, -1, 0]) / math.sqrt(2),
    "by": np.array([1, 1, -2]) / math.sqrt(6),
}
PROBE_PSNR = 38.0
BUDGET_PSNR = 35.5
SIDE = 512


def radius():
    f = np.fft.fftfreq(SIDE) * SIDE
    return np.hypot(f[:, None], f[None, :])


def pattern(band, axis, rms):
    lo, hi = band
    rng = np.random.default_rng(1000 * BANDS.index(band) + list(AXES).index(axis))
    spec = np.fft.fft2(rng.standard_normal((SIDE, SIDE)))
    r = radius()
    spec[(r < lo) | (r >= hi)] = 0
    plane = np.real(np.fft.ifft2(spec))
    plane /= np.sqrt(np.mean(plane ** 2))
    # rms is per RGB sample: total energy = rms^2 * 3 * SIDE^2, all of it on one colour axis.
    return plane[..., None] * AXES[axis][None, None, :] * rms * math.sqrt(3)


def band_power(rgb, band, axis):
    plane = rgb @ AXES[axis]
    spec = np.fft.fft2(plane, norm="ortho")
    r = radius()
    mask = (r >= band[0]) & (r < band[1])
    return float(np.mean(np.abs(spec[mask]) ** 2))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--strengths", type=float, nargs="+", default=[0.1, 0.2, 0.4])
    p.add_argument("--seed", type=int, default=0)
    a = p.parse_args()
    import torch
    from PIL import Image
    import three_threat_models as models

    a.output_dir.mkdir(parents=True, exist_ok=False)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    pipe = models.load_regenerator(ASSETS)
    rms = 10 ** (-PROBE_PSNR / 20)
    budget_energy = 3 * SIDE * SIDE * 10 ** (-BUDGET_PSNR / 10)

    def attack(rgb01, strength):
        img = Image.fromarray(np.clip(np.rint(rgb01 * 255), 0, 255).astype(np.uint8))
        with torch.inference_mode():
            out = pipe(prompt="", negative_prompt="", image=img, strength=strength, num_inference_steps=20,
                       eta=0.0, guidance_scale=1.0, generator=torch.Generator(device="cuda").manual_seed(a.seed),
                       num_images_per_prompt=1, output_type="pil", return_dict=True)
        return np.asarray(models.validate_generated(out), np.float64) / 255

    patterns = {(b, c): pattern(b, c, rms) for b in BANDS for c in AXES}
    rows, tick = [], time.monotonic()
    with (a.output_dir / "rows.jsonl").open("w", encoding="utf-8") as log:
        for sid, path in SOURCES.items():
            x = np.asarray(Image.open(path).convert("RGB"), np.float64) / 255
            for strength in a.strengths:
                try:
                    base = attack(x, strength)
                except RuntimeError as error:
                    row = dict(source=sid, strength=strength, outcome=str(error))
                    rows.append(row); log.write(json.dumps(row) + "\n"); continue
                for (band, axis), d in patterns.items():
                    try:
                        marked = attack(np.clip(x + d, 0, 1), strength)
                    except RuntimeError as error:
                        row = dict(source=sid, strength=strength, band=band, axis=axis, outcome=str(error))
                    else:
                        applied = np.clip(x + d, 0, 1) - x
                        diff = marked - base
                        gain = float(np.sum(diff * applied) / np.sum(applied * applied))
                        host_after = band_power(base, band, axis)
                        host_before = band_power(x, band, axis)
                        row = dict(source=sid, strength=strength, band=band, axis=axis, outcome="completed",
                                   gain=gain, host_after=host_after, host_before=host_before,
                                   attack_power=band_power(base - x, band, axis),
                                   score_at_budget=gain * math.sqrt(budget_energy / host_after))
                    rows.append(row); log.write(json.dumps(row) + "\n"); log.flush()
            print(f"source {sid} done, {time.monotonic() - tick:.0f}s", flush=True)
    summary = {}
    for strength in a.strengths:
        for band in BANDS:
            for axis in AXES:
                got = [r for r in rows if r.get("outcome") == "completed" and r["strength"] == strength
                       and tuple(r["band"]) == band and r["axis"] == axis]
                if got:
                    summary[f"{strength}|{band[0]}-{band[1]}|{axis}"] = dict(
                        n=len(got), gain_median=float(np.median([r["gain"] for r in got])),
                        score_median=float(np.median([r["score_at_budget"] for r in got])),
                        score_min=float(np.min([r["score_at_budget"] for r in got])),
                        host_after_median=float(np.median([r["host_after"] for r in got])))
    run = dict(schema="f4-transfer-probe-v1", data_split="development", commit=commit,
               command=sys.argv, seed=a.seed, strengths=a.strengths, probe_psnr_db=PROBE_PSNR,
               budget_psnr_db=BUDGET_PSNR, bands=BANDS, axes=list(AXES), sources=list(SOURCES),
               attack="pinned SD1.5 DDIM img2img, 20 steps, empty prompt, CFG 1, eta 0, same seed for x and x+d",
               duration_seconds=time.monotonic() - tick, outcome="completed", summary=summary)
    (a.output_dir / "run.json").write_text(json.dumps(run, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
