"""Development probe: does a carrier without block borders survive regeneration better?

Development tooling, synthetic hosts only (outputs under
``.thesis-build/rehearsal/v5-lab/carrier``).  Adds two kinds of random luminance
pattern at the same RMS to the development hosts and measures, through the VAE
round trip and img2img, the retention of the pattern (regression slope of what
survives on what was added, on the 128x128 average) and the channel noise along
it (projection of what the channel does to the unmarked host), hence the score
one unit of RMS buys:

* ``block``: the robust tier's carrier, independent random coefficients of the
  8x8 block DCT of the 128x128 average at the 24 robust positions, rendered
  block by block (smooth inside a block, discontinuous across borders);
* ``smooth``: a random field with no block structure, global 2D DCT
  coefficients of the 128x128 grid with frequency indices from ``low`` to 64
  (periods of 16 to 1024 / low pixels at 512x512), rendered continuously.

``weighting`` gives the coefficient amplitude as a power of the frequency.

    .thesis-build/a6-science-venv/Scripts/python.exe scripts/dev_v5_carrier_probe.py
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import dev_v5_channel_probe as probe  # noqa: E402
from scripts import dev_v5_lab as lab  # noqa: E402
from scripts import dev_v5_lab_run as run  # noqa: E402

OUT = lab.LAB / "carrier"


def block_pattern(rng: np.random.Generator, size: int, weighting: float) -> np.ndarray:
    weights = np.array([math.hypot(u, v) ** weighting for u, v in lab.POSITIONS])
    coefficients = rng.choice((-1.0, 1.0), size=(lab.BLOCKS * lab.BLOCKS, lab.COUNT)) * weights
    gains = lab.averaging_gains(size, size)
    return lab.render(size, size, coefficients * gains, gains)


def smooth_pattern(rng: np.random.Generator, size: int, weighting: float, low: int, high: int = 64) -> np.ndarray:
    side = lab.SIDE
    coordinate = (np.arange(size) + 0.5) * side / size - 0.5  # fine pixel centres in grid units
    frequencies = np.arange(high + 1)
    basis = np.cos(np.pi * (2 * coordinate[:, None] + 1) * frequencies[None, :] / (2 * side)) * math.sqrt(2.0 / side)
    basis[:, 0] /= math.sqrt(2.0)
    u, v = np.meshgrid(frequencies, frequencies, indexing="ij")
    radius = np.hypot(u, v)
    band = (radius >= low) & (radius <= high)
    coefficients = np.where(band, rng.normal(size=radius.shape) * np.maximum(radius, 1.0) ** weighting, 0.0)
    return basis @ coefficients @ basis.T


def coarse(image: np.ndarray) -> np.ndarray:
    return lab.coarse(lab.luma(image))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rms", type=float, default=3.0)
    parser.add_argument("--hosts", type=int, default=16)
    parser.add_argument("--patterns", default="block:1,smooth:1:8,smooth:1:16,smooth:0:8")
    parser.add_argument("--channels", default="vae,sd0.1-0,sd0.2-0")
    parser.add_argument("--keys", type=int, default=64, help="random patterns for the noise estimate")
    args = parser.parse_args()
    probe.offline()
    _text, pipe = probe.load()
    hosts = run.dev_hosts("dev")[: args.hosts]
    channels = args.channels.split(",")
    report = {"label": "synthetic development probe; not study evidence", "rms": args.rms, "patterns": {}}
    for spec in args.patterns.split(","):
        kind, *rest = spec.split(":")
        weighting = float(rest[0])
        if kind == "block":
            make = lambda rng: block_pattern(rng, 512, weighting)  # noqa: E731
        else:
            make = lambda rng, low=int(rest[1]), high=int(rest[2]) if len(rest) > 2 else 64: smooth_pattern(rng, 512, weighting, low, high)  # noqa: E731
        rows = []
        for index, (name, rgb) in enumerate(hosts):
            rng = np.random.default_rng(1000 + index)
            pattern = make(rng)
            pattern *= args.rms / math.sqrt(float((pattern**2).mean()))
            marked = np.clip(np.floor(rgb.astype(np.float64) + pattern[..., None] + 0.5), 0, 255).astype(np.uint8)
            made = coarse(marked) - coarse(rgb)
            unit = made / math.sqrt(float((made**2).sum()))
            # noise: projections of the channel's change to the unmarked host on independent patterns of the same kind
            probes = []
            for k in range(args.keys):
                other = make(np.random.default_rng(50000 + 97 * index + k))
                small = lab.coarse(other)
                probes.append(small / math.sqrt(float((small**2).sum())))
            row = {"host": name}
            for channel in channels:
                c0 = run.cached(lab.LAB / "dev" / "C0" / f"{name}-{channel}.png", lambda: None)
                if channel == "vae":
                    c1 = probe.vae_round_trip(pipe, marked)
                else:
                    strength, seed = channel[2:].split("-")
                    c1 = probe.regenerate(pipe, marked, float(strength), int(seed))
                if c0 is None or c1 is None:
                    continue
                kept = coarse(c1) - coarse(c0)
                retention = float((kept * made).sum() / (made * made).sum())
                change = coarse(c0) - coarse(rgb)
                noise = float(np.std([(change * p).sum() for p in probes]))
                amplitude = math.sqrt(float((made**2).sum()))
                row[channel] = {"r": retention, "noise": noise, "snr": retention * amplitude / noise}
            rows.append(row)
        report["patterns"][spec] = rows
        line = []
        for channel in channels:
            values = [row[channel] for row in rows if channel in row]
            line.append(f"{channel}: r {np.median([v['r'] for v in values]):.2f} snr {np.median([v['snr'] for v in values]):.2f}")
        print(f"{spec:16s} " + " | ".join(line), flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "carrier-probe.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
