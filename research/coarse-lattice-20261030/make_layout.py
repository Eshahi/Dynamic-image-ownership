"""Build a frozen coefficient layout from the design half only."""
import argparse
from pathlib import Path

import numpy as np

from coarse_lattice import Lattice
from simulate_lattice import LOW, PRIMARY, gains, load


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--channels", default="0")
    ap.add_argument("--rmin", type=float, default=32)
    ap.add_argument("--rmax", type=float, default=128)
    ap.add_argument("--k", type=int, default=512)
    ap.add_argument("--rho", type=float, default=5.0)
    ap.add_argument("--beta", type=float, default=1.0)
    ap.add_argument("--min-gain", type=float, default=0.6)
    args = ap.parse_args()
    run = Path(args.run)
    meta, bands, clean, regen = load(run)
    edges = np.array(meta["edges"])
    design = meta["sources"][0::2]
    host_gain, _ = gains(meta, bands, "vine-r")
    v, u = np.meshgrid(np.arange(LOW), np.arange(LOW), indexing="ij")
    radius = np.hypot(u, v)
    band = np.digitize(radius, edges) - 1
    sig2 = []
    for c in PRIMARY:
        acc, n = np.zeros((3, LOW, LOW)), 0
        for s in design:
            for seed in meta["seeds"]:
                if (s, c, seed) in regen:
                    acc += (regen[(s, c, seed)].astype(np.float64) - clean[s]) ** 2
                    n += 1
        sig2.append(acc / n)
    worst = np.max(sig2, axis=0)
    min_gain = np.min([host_gain[c] for c in PRIMARY], axis=0)
    channels = [int(c) for c in args.channels.split(",")]
    ok = np.zeros((3, LOW, LOW), dtype=bool)
    for ch in channels:
        ok[ch] = (min_gain[ch][band] >= args.min_gain) & (radius >= args.rmin) & (radius < args.rmax)
    idx = np.argwhere(ok)
    order = idx[np.argsort(worst[ok])][: args.k]
    ch, vv, uu = order[:, 0], order[:, 1], order[:, 2]
    lat = Lattice(ch, vv, uu, np.sqrt(worst[ch, vv, uu]), args.rho, args.beta)
    lat.save(run / args.out)
    print(f"{args.out}: k={lat.k}, eligible {len(idx)}, rms noise {np.sqrt((lat.sigma ** 2).mean()):.1f}, radius {np.hypot(vv, uu).min():.0f}-{np.hypot(vv, uu).max():.0f}, channels {sorted(set(ch.tolist()))}")


if __name__ == "__main__":
    main()
