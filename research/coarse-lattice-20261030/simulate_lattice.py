"""Offline screen of a coarse-lattice mark on measured regeneration noise.

Idea: instead of adding a pattern, nudge secret projections of the image's own
coarse content onto a secret lattice. The reader needs no reference: it checks
whether the projections sit on the lattice, with an analytic false-positive bound.

This is a simulation with one stated assumption. Regeneration of the marked image
is approximated by: real regeneration of the unmarked image, plus the mark times a
measured band gain. A real regeneration test must confirm it.
Design and evaluation use separate halves of the 60 development sources.
"""
import argparse
import itertools
import json
from pathlib import Path

import numpy as np

PRIMARY = ["R0-0.2", "R1-0.1", "R1-0.2", "R3-0.2"]
THRESHOLDS = {"z4.98": 4.98, "z8.26": 8.26}
LOW = 128


def load(run):
    meta = json.loads((run / "meta.json").read_text(encoding="utf-8"))
    bands = list(np.load(run / "bands.npy", allow_pickle=True))
    z = np.load(run / "low.npz")
    clean = {s: z[f"{s}:clean"] for s in meta["sources"]}
    regen = {}
    for s in meta["sources"]:
        for c in meta["cells"]:
            for seed in meta["seeds"]:
                key = f"{s}:{c}:{seed}"
                if key in z.files:
                    regen[(s, c, seed)] = z[key]
    return meta, bands, clean, regen


def gains(meta, bands, arm):
    """Mark gain and host gain by cell, channel and band."""
    nb = len(bands[0]["count"])
    host, mark = {}, {}
    for c in meta["cells"]:
        rows = [r for r in bands if c in r]
        host[c] = np.sum([r[c]["host_cross"] for r in rows], axis=0) / np.sum([r["host"] for r in rows], axis=0)
        wd = np.zeros((3, nb))
        ww = np.zeros((3, nb))
        for r in rows:
            if arm in r[c]["resp"]:
                wd += r[c]["resp"][arm]["wd"]
                ww += r[c]["resp"][arm]["ww"]
        with np.errstate(divide="ignore", invalid="ignore"):
            mark[c] = np.where(ww > 0, wd / ww, 0.0)
    return host, mark


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--keys", type=int, default=5)
    ap.add_argument("--min-gain", type=float, default=0.7)
    ap.add_argument("--gain-arm", default="vine-r")
    args = ap.parse_args()
    run = Path(args.run)
    meta, bands, clean, regen = load(run)
    edges = np.array(meta["edges"])
    sources = meta["sources"]
    design = sources[0::2]
    evaluate = sources[1::2]
    host_gain, mark_gain = gains(meta, bands, args.gain_arm)

    v, u = np.meshgrid(np.arange(LOW), np.arange(LOW), indexing="ij")
    band = np.digitize(np.hypot(u, v), edges) - 1
    sig2 = {}
    for c in meta["cells"]:
        acc = np.zeros((3, LOW, LOW))
        n = 0
        for s in design:
            for seed in meta["seeds"]:
                if (s, c, seed) in regen:
                    acc += (regen[(s, c, seed)].astype(np.float64) - clean[s]) ** 2
                    n += 1
        sig2[c] = acc / n
    worst = np.max([sig2[c] for c in PRIMARY], axis=0)
    min_gain = np.min([host_gain[c] for c in PRIMARY], axis=0)
    eligible = np.stack([min_gain[ch][band] >= args.min_gain for ch in range(3)])
    eligible[:, band == 0] = False
    order_all = np.argwhere(eligible)
    vals = worst[eligible]
    order = order_all[np.argsort(vals)]
    print("eligible coefficients", len(order), "by channel", [int((order[:, 0] == ch).sum()) for ch in range(3)])
    for top in (64, 128, 256, 512, 1024, 2048, 4096):
        idx = order[:top]
        print(f" top {top:5d}: rms noise {np.sqrt(worst[idx[:, 0], idx[:, 1], idx[:, 2]].mean()):6.1f}, channel shares "
              f"{[round(float((idx[:, 0] == ch).mean()), 2) for ch in range(3)]}, max radius {np.hypot(idx[:, 1], idx[:, 2]).max():.0f}")

    src_index = {s: i for i, s in enumerate(sources)}
    cells = meta["cells"]
    seeds = meta["seeds"]
    results = []
    grid = list(itertools.product([64, 128, 256, 512, 1024], [1, 4], [4.0, 5.0, 2 * np.pi, 8.0, 10.0], [0.7, 0.85, 1.0]))
    for k, m, rho, beta in grid:
        need = k * m
        if need > len(order):
            continue
        idx = order[:need]
        ch, vv, uu = idx[:, 0], idx[:, 1], idx[:, 2]
        hmap = {c: np.clip(mark_gain[c][ch, band[vv, uu]], 0.0, 1.2) for c in cells}
        psnrs = []
        hit = {c: {} for c in cells}
        h0_max = -9.0
        for key in range(args.keys):
            rng = np.random.default_rng(90210 + key)
            perm = rng.permutation(need)
            signs = rng.choice([-1.0, 1.0], size=need)
            groups = perm.reshape(k, m)
            w_group = signs[groups] / np.sqrt(m)
            sigma = np.sqrt(worst[ch[groups], vv[groups], uu[groups]].mean(axis=1))
            step = rho * sigma
            dither = rng.uniform(0, 1, size=k) * step
            for s in sources:
                x = clean[s][ch, vv, uu].astype(np.float64)
                p = (x[groups] * w_group).sum(axis=1)
                r = np.mod(p - dither + step / 2, step) - step / 2
                delta = -beta * r
                energy = (delta ** 2).sum()
                psnrs.append((s, 10 * np.log10(255 ** 2 * 3 * 512 ** 2 / max(energy, 1e-9))))
                for c in cells:
                    gm = (hmap[c][groups] * w_group ** 2).sum(axis=1)
                    zs = []
                    for seed in seeds:
                        y = regen.get((s, c, seed))
                        if y is None:
                            zs.append(-99.0)
                            continue
                        yp = (y[ch, vv, uu].astype(np.float64)[groups] * w_group).sum(axis=1) + gm * delta
                        ang = 2 * np.pi * (yp - dither) / step
                        zs.append(np.cos(ang).sum() / np.sqrt(k))
                        h0 = np.cos(2 * np.pi * ((y[ch, vv, uu].astype(np.float64)[groups] * w_group).sum(axis=1) - dither) / step).sum() / np.sqrt(k)
                        h0_max = max(h0_max, h0)
                    hit[c].setdefault(s, []).append(zs)
        ps = np.array([p for _, p in psnrs])
        row = {"k": k, "m": m, "rho": round(float(rho), 2), "beta": beta,
               "psnr_median": float(np.median(ps)), "psnr_min": float(ps.min()), "h0_max_z": float(h0_max)}
        for split, group in (("design", design), ("eval", evaluate)):
            for name, tau in THRESHOLDS.items():
                for c in cells:
                    counts = []
                    for key in range(args.keys):
                        ok = 0
                        for s in group:
                            zs = np.array(hit[c][s][key])
                            ok += int((zs >= tau).sum() >= 2)
                        counts.append(ok)
                    row[f"{split}:{name}:{c}"] = float(np.mean(counts)) / len(group)
        results.append(row)
    (run / f"lattice-grid-{args.gain_arm}.json").write_text(json.dumps(results, indent=0), encoding="utf-8")

    def primary_min(row, split, name):
        return min(row[f"{split}:{name}:{c}"] for c in PRIMARY)

    for name in THRESHOLDS:
        print(f"\n== {name}: best config per PSNR floor, chosen on the design half, shown on the evaluation half")
        print(" floor   k  m   rho  beta  PSNRmed PSNRmin  h0max | " + " ".join(f"{c:>7}" for c in cells))
        for floor in (35, 38, 40, 42, 45, 48):
            pool = [r for r in results if r["psnr_min"] >= floor]
            if not pool:
                print(f"  {floor}: none")
                continue
            best = max(pool, key=lambda r: (primary_min(r, "design", name), r["psnr_median"]))
            print(f"  {floor:3d} {best['k']:4d} {best['m']:2d} {best['rho']:5.2f} {best['beta']:5.2f} "
                  f"{best['psnr_median']:7.1f} {best['psnr_min']:7.1f} {best['h0_max_z']:6.2f} | "
                  + " ".join(f"{best[f'eval:{name}:{c}']:7.2f}" for c in cells))


if __name__ == "__main__":
    main()
