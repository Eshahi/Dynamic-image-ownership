"""Add content binding at no payload cost: the lattice itself depends on the image.

The first check showed a residual copy can pass when host coefficients are small
compared with the lattice step. Fix under test: derive the secret lattice from the
owner key and a coarse content sketch, read from luma coefficients the mark never
touches. The reader tries every sketch within a small Hamming ball, and pays for
those tries in its threshold, so no bits are transmitted and the false-positive
bound stays analytic.
"""
import argparse
import json
from itertools import combinations
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import uniform_filter

from coarse_lattice import MULTS, Lattice, embed, psnr, score_values, threshold, to_coefs
from measure_channel import DIRS
from simulate_lattice import PRIMARY, gains, load
from visual_check import ssim


def img(name):
    for d in DIRS:
        p = d / name
        if p.exists():
            return np.asarray(Image.open(p).convert("RGB"))
    raise FileNotFoundError(name)


def ball(value, bits, radius):
    out = [value]
    for r in range(1, radius + 1):
        for pos in combinations(range(bits), r):
            flip = 0
            for b in pos:
                flip |= 1 << b
            out.append(value ^ flip)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--bits", type=int, default=16)
    ap.add_argument("--radius", type=int, default=2)
    ap.add_argument("--floor", type=float, default=38.0)
    ap.add_argument("--keys", type=int, default=2)
    ap.add_argument("--samples", default="30,1180,1786")
    ap.add_argument("--layout", default="lattice-layout.json")
    ap.add_argument("--tag", default="")
    args = ap.parse_args()
    run = Path(args.run)
    meta, bands, clean, regen = load(run)
    sources = meta["sources"]
    design, evaluate = sources[0::2], sources[1::2]
    cells, seeds = meta["cells"], meta["seeds"]
    edges = np.array(meta["edges"])
    _, vine_gain = gains(meta, bands, "vine-r")
    _, v5_gain = gains(meta, bands, "v5-r3")
    lat = Lattice.load(run / args.layout)
    ch, vv, uu = lat.ch, lat.vv, lat.uu
    v, u = np.meshgrid(np.arange(128), np.arange(128), indexing="ij")
    band = np.digitize(np.hypot(u, v), edges) - 1

    # Sketch coefficients: luma, low band, large compared with regeneration noise. Chosen on the design half.
    host = np.median([np.abs(clean[s][0, :24, :24]) for s in design], axis=0)
    noise = np.zeros((24, 24))
    for c in PRIMARY:
        acc, n = np.zeros((24, 24)), 0
        for s in design:
            for sd in seeds:
                if (s, c, sd) in regen:
                    acc += (regen[(s, c, sd)][0, :24, :24].astype(np.float64) - clean[s][0, :24, :24]) ** 2
                    n += 1
        noise = np.maximum(noise, acc / n)
    ratio = host / np.sqrt(noise)
    ratio[0, 0] = 0
    picks = np.argsort(ratio.ravel())[::-1][: args.bits]
    sv, su = np.unravel_index(picks, ratio.shape)
    print("sketch coefficients (v,u):", list(zip(sv.tolist(), su.tolist())), "median host/noise", np.round(ratio.ravel()[picks], 1).tolist())

    def sketch(lowluma):
        bitsv = (lowluma[sv, su] >= 0).astype(int)
        return int((bitsv << np.arange(args.bits)).sum())

    print("\nsketch stability under regeneration (all 60 sources): share of regenerated images within Hamming radius")
    print("  cell     mean-flips " + " ".join(f"r<={r}" for r in range(5)))
    stable = {}
    for c in cells:
        dist = []
        for s in sources:
            sx = sketch(clean[s][0])
            for sd in seeds:
                if (s, c, sd) in regen:
                    dist.append(bin(sx ^ sketch(regen[(s, c, sd)][0])).count("1"))
        dist = np.array(dist)
        stable[c] = dist
        print(f"  {c:8} {dist.mean():6.2f}     " + " ".join(f"{(dist <= r).mean():4.2f}" for r in range(5)))

    candidates = len(ball(0, args.bits, args.radius))
    tau = threshold(1e-6, tries=candidates * len(MULTS))
    print(f"\nball radius {args.radius}: {candidates} sketches x {len(MULTS)} steps; threshold at 1e-6 per claim = {tau:.2f}")

    worst = np.max([[((regen[(s, c, sd)][ch, vv, uu].astype(np.float64) - clean[s][ch, vv, uu]) ** 2).mean()
                     for c in ("R0-0.2",) for sd in (12,) if (s, c, sd) in regen] or [lat.sigma.__pow__(2).mean()] for s in sources], axis=1)
    base = (lat.sigma ** 2).mean()
    mult_of = {s: min(MULTS, key=lambda q: abs(np.log(q / max(np.sqrt(w / base), 1e-3)))) for s, w in zip(sources, worst)}

    def key_for(owner, sk):
        return f"{owner}|{sk}"

    def read_ball(coefs, owner):
        best = -99.0
        sk = sketch(coefs[0, :24, :24])
        vals = lat.values(coefs)
        for cand in ball(sk, args.bits, args.radius):
            best = max(best, score_values(lat, vals, key_for(owner, cand)))
        return best

    pix = {s: img(f"clean_{s}_unmarked_None_None.png") for s in sources}
    marked, moves, ps = {}, {}, []
    for ki in range(args.keys):
        owner = f"owner-{ki}"
        for s in sources:
            sk = sketch(to_coefs(pix[s])[0, :24, :24])
            out, move = embed(pix[s], lat, key_for(owner, sk), mult_of[s], args.floor)
            marked[(s, ki)] = out
            moves[(s, ki)] = (move, sk)
            ps.append(psnr(out, pix[s]))
    ps = np.array(ps)
    clean_scores = [read_ball(to_coefs(marked[(s, 0)]), "owner-0") for s in sources]
    print(f"quality: PSNR median {np.median(ps):.2f}, min {ps.min():.2f}; clean read min z {min(clean_scores):.1f}, threshold {tau:.2f}")

    print("\nT4, real pixels, claimed owner = donor's owner, with binding")
    pairs = [(evaluate[i], evaluate[(i + j) % len(evaluate)]) for i in range(len(evaluate)) for j in (1, 2, 3, 5, 7)]
    t4 = {f"patch{sz}": [] for sz in (128, 256, 384)}
    t4["residual"] = []
    for ki in range(args.keys):
        owner = f"owner-{ki}"
        for donor, target in pairs:
            d, t = marked[(donor, ki)], pix[target]
            for sz in (128, 256, 384):
                y = t.copy()
                a = (512 - sz) // 2
                y[a:a + sz, a:a + sz] = d[a:a + sz, a:a + sz]
                t4[f"patch{sz}"].append(read_ball(to_coefs(y), owner))
            res = d.astype(np.float64) - pix[donor]
            t4["residual"].append(read_ball(to_coefs(np.clip(np.rint(t + res), 0, 255)), owner))
    for name, vals in t4.items():
        vals = np.array(vals)
        print(f"  {name:10} trials {len(vals):4d}  accepted {int((vals >= tau).sum()):4d}  max z {vals.max():6.2f}")

    print("\nT5 proxy, never-marked regenerated copies of the same content, with binding")
    keys = sorted(regen)[::7]
    un = np.array([read_ball(np.concatenate([regen[k], np.zeros((3, 128, 128))], axis=0)[:3], "owner-0") for k in keys])
    print(f"  trials {len(un)}  accepted {int((un >= tau).sum())}  max z {un.max():.2f}")

    print("\nT3 simulated, evaluation half, seeds 13 and 14, detection rate at 1e-6 with binding (sketch misses count as failures)")
    print("  gain scenario " + " ".join(f"{c:>7}" for c in cells))
    table = {}
    for name, g in {"v5 measured": v5_gain, "VINE measured": vine_gain, "fixed 0.7": 0.7, "fixed 0.5": 0.5, "fixed 0.3": 0.3}.items():
        line = {}
        for c in cells:
            hs = np.full(lat.k, float(g)) if isinstance(g, float) else np.clip(g[c][ch, band[vv, uu]], 0, 1.2)
            ok, tot = 0, 0
            for ki in range(args.keys):
                owner = f"owner-{ki}"
                for s in evaluate:
                    move, sk = moves[(s, ki)]
                    for sd in (13, 14):
                        tot += 1
                        y = regen.get((s, c, sd))
                        if y is None:
                            continue
                        if bin(sk ^ sketch(y[0, :24, :24])).count("1") > args.radius:
                            continue
                        vals = y[ch, vv, uu].astype(np.float64) + hs * move
                        ok += int(score_values(lat, vals, key_for(owner, sk)) >= tau)
            line[c] = ok / tot
        table[name] = line
        print(f"  {name:13} " + " ".join(f"{line[c]:7.2f}" for c in cells))
    (run / f"offline-binding{args.tag}.json").write_text(json.dumps({
        "bits": args.bits, "radius": args.radius, "tau": tau,
        "psnr_median": float(np.median(ps)), "psnr_min": float(ps.min()),
        "t4": {k: {"n": len(v), "accepted": int((np.array(v) >= tau).sum()), "max": float(np.max(v))} for k, v in t4.items()},
        "t5_proxy": {"n": len(un), "accepted": int((un >= tau).sum()), "max": float(un.max())},
        "sketch_within_radius": {c: float((stable[c] <= args.radius).mean()) for c in cells},
        "t3_sim": table,
    }, indent=1), encoding="utf-8")

    out = run / "samples"
    out.mkdir(exist_ok=True)
    for s in [int(i) for i in args.samples.split(",")]:
        Image.fromarray(pix[s]).save(out / f"{s}-original.png")
        Image.fromarray(marked[(s, 0)]).save(out / f"{s}-marked{args.tag}.png")
        diff = np.clip(128 + 12 * (marked[(s, 0)].astype(np.float64) - pix[s]), 0, 255).astype(np.uint8)
        Image.fromarray(diff).save(out / f"{s}-difference-x12{args.tag}.png")
        gray = pix[s].mean(axis=2)
        var = uniform_filter(gray ** 2, 180) - uniform_filter(gray, 180) ** 2
        inner = var[90:-90, 90:-90]
        yy, xx = np.unravel_index(np.argmin(inner), inner.shape)
        a, b = pix[s][yy:yy + 180, xx:xx + 180], marked[(s, 0)][yy:yy + 180, xx:xx + 180]
        pair = np.concatenate([a, np.full((180, 6, 3), 255, dtype=np.uint8), b], axis=1)
        Image.fromarray(pair).resize((pair.shape[1] * 3, 540), Image.NEAREST).save(out / f"{s}-flat-crop{args.tag}.png")
    ssims = [ssim(marked[(s, 0)], pix[s]) for s in sources]
    print(f"\nSSIM median {np.median(ssims):.4f}, min {np.min(ssims):.4f}")

    try:
        import lpips
        import torch
        net = lpips.LPIPS(net="alex", verbose=False).eval()
        vals = []
        for s in sources:
            a = torch.tensor(pix[s] / 127.5 - 1).permute(2, 0, 1)[None].float()
            b = torch.tensor(marked[(s, 0)] / 127.5 - 1).permute(2, 0, 1)[None].float()
            with torch.no_grad():
                vals.append(float(net(a, b)))
        print(f"\nLPIPS on CPU: median {np.median(vals):.4f}, max {np.max(vals):.4f}, strict <.1 on {(np.array(vals) < .1).mean():.3f}")
    except Exception as exc:
        print("\nLPIPS not measured here:", type(exc).__name__, str(exc)[:120])


if __name__ == "__main__":
    main()
