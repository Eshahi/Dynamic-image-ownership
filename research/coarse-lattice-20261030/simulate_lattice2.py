"""Second screen: pessimistic mark gains, overdrive, per-image step, wrong-key control.

Gain sources: measured VINE-R, measured v5, or a fixed value. The real gain of a
lattice nudge is unknown until a real regeneration test, so the honest question
here is how much gain the method needs in order to work.
"""
import argparse
import json
from pathlib import Path

import numpy as np

from simulate_lattice import LOW, PRIMARY, THRESHOLDS, gains, load


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--keys", type=int, default=2)
    ap.add_argument("--min-gain", type=float, default=0.7)
    args = ap.parse_args()
    run = Path(args.run)
    meta, bands, clean, regen = load(run)
    edges = np.array(meta["edges"])
    sources = meta["sources"]
    design, evaluate = sources[0::2], sources[1::2]
    cells, seeds = meta["cells"], meta["seeds"]
    host_gain, vine_gain = gains(meta, bands, "vine-r")
    _, v5_gain = gains(meta, bands, "v5-r3")
    labels = [f"{int(edges[i])}-{int(edges[i + 1])}" for i in range(len(edges) - 1)]

    print("== measured gain by band at the primary cells, per colour channel")
    for ch, name in enumerate(["luma", "red-green", "blue-yellow"]):
        print(name)
        print("  band      " + " ".join(f"{b:>8}" for b in labels[3:13]))
        for c in PRIMARY:
            print(f"  host {c:7}" + " ".join(f"{host_gain[c][ch, b]:8.2f}" for b in range(3, 13)))
            print(f"  vine {c:7}" + " ".join(f"{vine_gain[c][ch, b]:8.2f}" for b in range(3, 13)))
            print(f"  v5   {c:7}" + " ".join(f"{v5_gain[c][ch, b]:8.2f}" for b in range(3, 13)))

    v, u = np.meshgrid(np.arange(LOW), np.arange(LOW), indexing="ij")
    band = np.digitize(np.hypot(u, v), edges) - 1
    sig2 = {}
    for c in cells:
        acc = np.zeros((3, LOW, LOW))
        n = 0
        for s in design:
            for seed in seeds:
                if (s, c, seed) in regen:
                    acc += (regen[(s, c, seed)].astype(np.float64) - clean[s]) ** 2
                    n += 1
        sig2[c] = acc / n
    worst = np.max([sig2[c] for c in PRIMARY], axis=0)
    min_gain = np.min([host_gain[c] for c in PRIMARY], axis=0)
    eligible = np.stack([min_gain[ch][band] >= args.min_gain for ch in range(3)])
    eligible[:, band == 0] = False
    allidx = np.argwhere(eligible)
    order = allidx[np.argsort(worst[eligible])]

    # How much of the noise is image dependent, on the coefficients actually used.
    idx = order[:1024]
    ch, vv, uu = idx[:, 0], idx[:, 1], idx[:, 2]
    print("\n== per-image noise on the 1024 quietest coefficients, relative to the design average")
    for c in PRIMARY:
        ratios = []
        for s in sources:
            vals = [((regen[(s, c, sd)][ch, vv, uu].astype(np.float64) - clean[s][ch, vv, uu]) ** 2).mean()
                    for sd in seeds if (s, c, sd) in regen]
            ratios.append(np.sqrt(np.mean(vals) / worst[ch, vv, uu].mean()))
        ratios = np.array(ratios)
        print(f"  {c:7} p10 {np.percentile(ratios, 10):.2f}  median {np.median(ratios):.2f}  p90 {np.percentile(ratios, 90):.2f}  max {ratios.max():.2f}")

    def run_config(k, m, rho, beta, gain_mode, adaptive, floor=None):
        need = k * m
        idx = order[:need]
        ch, vv, uu = idx[:, 0], idx[:, 1], idx[:, 2]
        if gain_mode == "vine":
            hmap = {c: np.clip(vine_gain[c][ch, band[vv, uu]], 0.0, 1.2) for c in cells}
        elif gain_mode == "v5":
            hmap = {c: np.clip(v5_gain[c][ch, band[vv, uu]], 0.0, 1.2) for c in cells}
        else:
            hmap = {c: np.full(need, float(gain_mode)) for c in cells}
        sel = {s: clean[s][ch, vv, uu].astype(np.float64) for s in sources}
        psnr = {}
        hits = {c: {s: [] for s in sources} for c in cells}
        clean_z = []
        wrong = []
        unmarked = []
        tries = len(MULTS) if adaptive else 1
        for key in range(args.keys):
            rng = np.random.default_rng(90210 + key)
            perm = rng.permutation(need)
            signs = rng.choice([-1.0, 1.0], size=need)
            groups = perm.reshape(k, m)
            wg = signs[groups] / np.sqrt(m)
            sigma = np.sqrt(worst[ch[groups], vv[groups], uu[groups]].mean(axis=1))
            d0 = rng.uniform(0, 1, size=k)
            d1 = rng.uniform(0, 1, size=k)
            for s in sources:
                mult = 1.0
                if adaptive:
                    # The writer calibrates with one regeneration per primary family, seed 12.
                    est = []
                    for c in ("R0-0.2", "R1-0.2", "R3-0.2"):
                        y = regen.get((s, c, 12))
                        if y is not None:
                            est.append(((y[ch, vv, uu].astype(np.float64) - sel[s]) ** 2).mean())
                    ratio = np.sqrt(np.max(est) / worst[ch, vv, uu].mean()) if est else 1.0
                    mult = min(MULTS, key=lambda q: abs(np.log(q / max(ratio, 1e-3))))
                step = rho * sigma * mult
                dither = d0 * step
                p = (sel[s][groups] * wg).sum(axis=1)
                r = np.mod(p - dither + step / 2, step) - step / 2
                delta = -beta * r
                e = (delta ** 2).sum()
                ps = 10 * np.log10(255 ** 2 * 3 * 512 ** 2 / max(e, 1e-9))
                if floor is not None and ps < floor:
                    # Shrink the nudge so that this image still meets the quality floor.
                    delta *= np.sqrt(3 * 512 ** 2 * 255 ** 2 * 10 ** (-floor / 10) / e)
                    e = (delta ** 2).sum()
                    ps = floor
                psnr[(s, key)] = ps
                clean_z.append(np.cos(2 * np.pi * (p + delta - dither) / step).sum() / np.sqrt(k))
                for c in cells:
                    gm = (hmap[c][groups] * wg ** 2).sum(axis=1)
                    zs = []
                    for seed in seeds:
                        y = regen.get((s, c, seed))
                        if y is None:
                            zs.append(-99.0)
                            continue
                        yp = (y[ch, vv, uu].astype(np.float64)[groups] * wg).sum(axis=1)
                        best = -99.0
                        for q in (MULTS if adaptive else [1.0]):
                            st = rho * sigma * q
                            best = max(best, np.cos(2 * np.pi * (yp + gm * delta - d0 * st) / st).sum() / np.sqrt(k))
                        zs.append(best)
                        un = max(np.cos(2 * np.pi * (yp - d0 * (rho * sigma * q)) / (rho * sigma * q)).sum() / np.sqrt(k)
                                 for q in (MULTS if adaptive else [1.0]))
                        unmarked.append(un)
                        st = rho * sigma * mult
                        wrong.append(np.cos(2 * np.pi * (yp + gm * delta - d1 * st) / st).sum() / np.sqrt(k))
                    hits[c][s].append(zs)
        ps = np.array(list(psnr.values()))
        row = {"k": k, "m": m, "rho": round(float(rho), 2), "beta": beta, "gain": gain_mode, "adaptive": adaptive,
               "floor": floor, "psnr_median": float(np.median(ps)), "psnr_min": float(ps.min()),
               "clean_z_min": float(np.min(clean_z)), "clean_z_median": float(np.median(clean_z)),
               "unmarked_z_max": float(np.max(unmarked)), "wrong_key_z_max": float(np.max(wrong)),
               "tries": tries}
        for split, group in (("design", design), ("eval", evaluate)):
            for name, tau in THRESHOLDS.items():
                for c in cells:
                    counts = []
                    for key in range(args.keys):
                        counts.append(sum(int((np.array(hits[c][s][key]) >= tau).sum() >= 2) for s in group))
                    row[f"{split}:{name}:{c}"] = float(np.mean(counts)) / len(group)
        return row

    MULTS = [0.5, 0.71, 1.0, 1.41, 2.0, 2.83]
    out = []
    print("\n== sensitivity to the mark gain (k=1024, rho=2pi, beta=1 unless shown), evaluation half, z>=4.98")
    print(" gain    beta adapt  floor PSNRmed PSNRmin cleanmin unmarkedmax wrongmax | " + " ".join(f"{c:>7}" for c in cells))
    configs = []
    for g in ("vine", "v5", "1.0", "0.7", "0.5", "0.3"):
        configs.append((1024, 1, 2 * np.pi, 1.0, g, False, None))
    for g, b in (("0.5", 1.5), ("0.5", 2.0), ("0.3", 2.0), ("0.3", 3.0)):
        configs.append((1024, 1, 2 * np.pi, b, g, False, None))
    for g in ("vine", "v5", "0.5"):
        for floor in (38, 40):
            configs.append((1024, 1, 2 * np.pi, 1.0, g, True, floor))
            configs.append((2048, 1, 5.0, 1.0, g, True, floor))
    for cfg in configs:
        row = run_config(*cfg)
        out.append(row)
        print(f" {row['gain']:6} {row['beta']:4.1f} {str(row['adaptive'])[0]:>5} {str(row['floor']):>6} {row['psnr_median']:7.1f} {row['psnr_min']:7.1f} "
              f"{row['clean_z_min']:8.1f} {row['unmarked_z_max']:11.2f} {row['wrong_key_z_max']:8.2f} | "
              + " ".join(f"{row[f'eval:z4.98:{c}']:7.2f}" for c in cells)
              + f"  k={row['k']}")
    (run / "lattice-sensitivity.json").write_text(json.dumps(out, indent=0), encoding="utf-8")


if __name__ == "__main__":
    main()
