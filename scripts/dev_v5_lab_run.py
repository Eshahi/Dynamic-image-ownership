"""Development lab runner: mark the synthetic hosts with robust-tier variants, attack, score.

Development tooling (see ``dev_v5_lab``).  Synthetic hosts only; outputs under
``.thesis-build/rehearsal/v5-lab/``.  Each variant is marked with the numpy
model of the robust tier (no fragile tier), put through the VAE round trip and
img2img, and read with its own detector weighting.  Unmarked hosts are put
through the same channel once and read with every variant.

    .thesis-build/a6-science-venv/Scripts/python.exe scripts/dev_v5_lab_run.py --variants lab-variants.json --tag lab1
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import dev_v5_channel_probe as probe  # noqa: E402
from scripts import dev_v5_lab as lab  # noqa: E402

SINGLE_HOEFFDING = math.sqrt(2.0 * math.log(1e6))


def tight_threshold(target: float, patterns: int) -> float:
    """Score t with 3.178 * patterns * P(Z >= t) = target (Bentkus and Dzindzalieta 2015)."""
    constant = 1.0 / (4.0 * 0.5 * math.erfc(math.sqrt(2.0) / math.sqrt(2.0)))
    low, high = 0.0, 40.0
    for _ in range(200):
        middle = (low + high) / 2.0
        if constant * patterns * 0.5 * math.erfc(middle / math.sqrt(2.0)) > target:
            low = middle
        else:
            high = middle
    return high


SINGLE = tight_threshold(1e-6, 1)
SEARCHED = tight_threshold(1e-6, 1 << 32)


def dev_hosts(which: str) -> list[tuple[str, np.ndarray]]:
    from PIL import Image

    if which == "dev":
        out = [(f"procedural-{index}", probe.procedural(100 + index)) for index in range(4)]
        for path in sorted((probe.OUTPUT / "hosts").glob("generated-*.png")):
            out.append((path.stem, np.asarray(Image.open(path).convert("RGB"))))
        return out
    directory = probe.OUTPUT / which
    return [(path.stem, np.asarray(Image.open(path).convert("RGB"))) for path in sorted(directory.glob("*.png"))]


def cached(path: Path, make):
    from PIL import Image

    if path.exists():
        return np.asarray(Image.open(path).convert("RGB"))
    image = make()
    if image is None:
        return None
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(image).save(path)
    return image


def attacks(pipe, image: np.ndarray, directory: Path, name: str, strengths, seeds) -> dict[str, np.ndarray | None]:
    out = {"clean": image, "vae": cached(directory / f"{name}-vae.png", lambda: probe.vae_round_trip(pipe, image))}
    for strength in strengths:
        for seed in seeds:
            out[f"sd{strength}-{seed}"] = cached(directory / f"{name}-sd{strength}-{seed}.png", lambda: probe.regenerate(pipe, image, strength, seed))
    return out


def read(image, keys, variant):
    if image is None:
        return None
    y = lab.luma(image)
    recomputed, decoded, code = lab.score(lab.Analysis(y, keys, variant), keys.q(y))
    return {"r": round(recomputed, 3), "d": round(decoded, 3), "found": recomputed >= SINGLE or decoded >= SEARCHED}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--variants", required=True, help="JSON file: {name: overrides of dev_v5_lab.DEFAULT}")
    parser.add_argument("--tag", required=True)
    parser.add_argument("--hosts", default="dev")
    parser.add_argument("--strengths", default="0.05,0.1,0.2")
    parser.add_argument("--seeds", default="0")
    parser.add_argument("--only", default="", help="comma-separated variant names")
    args = parser.parse_args()
    probe.offline()
    variants = json.loads(Path(args.variants).read_text(encoding="utf-8"))
    if args.only:
        variants = {name: variants[name] for name in args.only.split(",")}
    strengths = tuple(float(s) for s in args.strengths.split(","))
    seeds = tuple(int(s) for s in args.seeds.split(","))
    _text, pipe = probe.load()
    from skimage.metrics import structural_similarity

    from scripts import dev_v5_regeneration_check as check

    metric = check.load_lpips()
    keys = lab.Keys()
    hosts = dev_hosts(args.hosts)
    root = lab.LAB / args.hosts
    report = {"label": "synthetic development lab; not study evidence", "hosts": args.hosts, "strengths": strengths, "seeds": seeds, "variants": {}}
    started = time.time()
    c0 = {name: attacks(pipe, rgb, root / "C0", name, strengths, seeds) for name, rgb in hosts}
    for vname, overrides in variants.items():
        variant = {**lab.DEFAULT, **overrides}
        rows = []
        for name, rgb in hosts:
            directory = root / vname
            path = directory / f"{name}-C1.png"
            if path.exists():
                from PIL import Image

                marked = np.asarray(Image.open(path).convert("RGB"))
                info = json.loads((directory / f"{name}-C1.json").read_text(encoding="utf-8"))
            else:
                marked, info = lab.mark(rgb, keys, variant)
                directory.mkdir(parents=True, exist_ok=True)
                from PIL import Image

                Image.fromarray(marked).save(path)
                (directory / f"{name}-C1.json").write_text(json.dumps(info), encoding="utf-8")
            if "lpips" not in info:
                info["ssim"] = float(structural_similarity(rgb, marked, channel_axis=2, data_range=255))
                info["lpips"] = check.lpips_score(metric, rgb, marked)
                (directory / f"{name}-C1.json").write_text(json.dumps(info), encoding="utf-8")
            outputs = attacks(pipe, marked, directory, name, strengths, seeds)
            row = {"host": name, "info": info, "C1": {k: read(v, keys, variant) for k, v in outputs.items()}, "C0": {k: read(v, keys, variant) for k, v in c0[name].items()}}
            rows.append(row)
        report["variants"][vname] = {"variant": variant, "rows": rows}
        summary(vname, rows, strengths, seeds)
        print(f"  [{time.time() - started:.0f}s]", flush=True)
    out = root / f"report-{args.tag}.json"
    out.write_text(json.dumps(report, indent=1), encoding="utf-8")
    print("wrote", out)
    return 0


def summary(vname, rows, strengths, seeds):
    psnr = [row["info"]["rgb_psnr"] for row in rows]
    worst = [row["info"]["worst_block_rms"] for row in rows]
    keys = ["clean", "vae"] + [f"sd{s}-{seed}" for s in strengths for seed in seeds]
    line = []
    for key in keys:
        c1 = [row["C1"][key] for row in rows]
        c0 = [row["C0"][key] for row in rows]
        kept = sum(bool(r and r["found"]) for r in c1)
        hoeffding = sum(bool(r and r["r"] >= SINGLE_HOEFFDING) for r in c1)
        false = sum(bool(r and r["found"]) for r in c0)
        med = np.median([r["r"] for r in c1 if r])
        line.append(f"{key} {kept}/{len(c1)} [H {hoeffding}] (med {med:.2f}, C0 {false})")
    lp = [row["info"].get("lpips", float("nan")) for row in rows]
    ss = [row["info"].get("ssim", float("nan")) for row in rows]
    print(
        f"{vname}: psnr med {np.median(psnr):.1f} min {min(psnr):.1f} max {max(psnr):.1f}, ssim min {min(ss):.3f}, lpips max {max(lp):.3f},"
        f" worst block {max(worst):.1f} | " + "; ".join(line),
        flush=True,
    )
    print("   vae scores:", " ".join(f"{row['C1']['vae']['r']:.1f}" for row in rows), flush=True)
    print("   psnr:      ", " ".join(f"{row['info']['rgb_psnr']:.1f}" for row in rows), flush=True)


if __name__ == "__main__":
    sys.exit(main())
