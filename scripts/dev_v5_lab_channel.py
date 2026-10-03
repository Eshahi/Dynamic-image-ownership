"""Development lab: what the channel keeps of the robust-tier mark, per frequency and per block texture.

Development tooling (see ``dev_v5_lab``).  Reads the cached lab outputs of one
variant (marked C1, unmarked C0 and their channel outputs) and reports, in the
normalised coefficient domain the detector reads:

* retention ``r``: regression slope of the change that survives
  (channel(C1) - channel(C0)) on the change that was made (C1 - C0);
* noise ``s``: RMS of what the channel does to the unmarked host
  (channel(C0) - C0);
* mark ``a``: RMS of the change made;

per robust position and per quartile of block texture, pooled over the hosts.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import dev_v5_lab as lab  # noqa: E402
from scripts import dev_v5_lab_run as run  # noqa: E402


def load(path: Path):
    from PIL import Image

    return np.asarray(Image.open(path).convert("RGB")) if path.exists() else None


def normalised(rgb, variant, reference):
    """Coefficients of ``rgb`` divided by the normalisers of ``reference`` (whitened)."""
    c = lab.coefficients(lab.coarse(lab.luma(rgb)))
    return c * reference.w / reference.n[:, None]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", default="equal")
    parser.add_argument("--hosts", default="dev")
    parser.add_argument("--channels", default="vae,sd0.05-0,sd0.1-0,sd0.2-0")
    args = parser.parse_args()
    variant = dict(lab.DEFAULT)
    keys = lab.Keys()
    root = lab.LAB / args.hosts
    pooled = {channel: {"made": [], "kept": [], "noise": [], "texture": []} for channel in args.channels.split(",")}
    per_host = []
    for name, rgb in run.dev_hosts(args.hosts):
        marked = load(root / args.variant / f"{name}-C1.png")
        if marked is None:
            continue
        reference = lab.Analysis(lab.luma(rgb), keys, variant)
        texture = np.repeat(reference.mask[:, None], lab.COUNT, axis=1)
        host = normalised(rgb, variant, reference)
        made = normalised(marked, variant, reference) - host
        line = [name]
        for channel in pooled:
            c1 = load(root / args.variant / f"{name}-{channel}.png")
            c0 = load(root / "C0" / f"{name}-{channel}.png")
            if c1 is None or c0 is None:
                continue
            kept = normalised(c1, variant, reference) - normalised(c0, variant, reference)
            noise = normalised(c0, variant, reference) - host
            pooled[channel]["made"].append(made)
            pooled[channel]["kept"].append(kept)
            pooled[channel]["noise"].append(noise)
            pooled[channel]["texture"].append(texture)
            r = float((kept * made).sum() / (made * made).sum())
            line.append(f"{channel}: r {r:.2f} a {np.sqrt((made**2).mean()):.3f} s {np.sqrt((noise**2).mean()):.3f}")
        per_host.append(line)
    for line in per_host:
        print(" | ".join(line))
    for channel, data in pooled.items():
        if not data["made"]:
            continue
        made, kept, noise, texture = (np.concatenate(data[key], axis=0) for key in ("made", "kept", "noise", "texture"))
        print(f"\n== {channel}: per position (u,v): retention r, mark rms a, noise rms s, r*a/s")
        for index, (u, v) in enumerate(lab.POSITIONS):
            m, k, n = made[:, index], kept[:, index], noise[:, index]
            r = float((k * m).sum() / (m * m).sum())
            a, s = float(np.sqrt((m * m).mean())), float(np.sqrt((n * n).mean()))
            print(f"  ({u},{v}) r {r:5.2f}  a {a:.3f}  s {s:.3f}  r*a/s {r * a / s:.3f}")
        print(f"== {channel}: per texture quartile of the block mask")
        edges = np.quantile(texture[:, 0], [0.25, 0.5, 0.75])
        bins = np.digitize(texture[:, 0], edges)
        for b in range(4):
            sel = bins == b
            m, k, n = made[sel], kept[sel], noise[sel]
            r = float((k * m).sum() / (m * m).sum())
            print(
                f"  quartile {b}: mask {texture[sel, 0].mean():.2f}  r {r:5.2f}  a {np.sqrt((m * m).mean()):.3f}  s {np.sqrt((n * n).mean()):.3f}"
                f"  share of mark energy {float((m * m).sum() / (made * made).sum()):.2f}"
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
