"""Real writer and reader on saved development images: T4, T5, quality, simulated T3.

T4 and T5 here are real pixel operations with no modelling assumption.
T3 stays a simulation until a real regeneration test: saved unmarked regeneration
plus the mark times an assumed gain. The writer calibrates on one seed (12) of SD1.5
only and T3 is scored on seeds 13 and 14, so calibration does not touch the test.
"""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image

from coarse_lattice import MULTS, Lattice, embed, from_coefs, psnr, read, score_values, threshold, to_coefs
from measure_channel import DIRS
from simulate_lattice import LOW, PRIMARY, gains, load


def img(name):
    for d in DIRS:
        p = d / name
        if p.exists():
            return np.asarray(Image.open(p).convert("RGB"))
    raise FileNotFoundError(name)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--k", type=int, default=2048)
    ap.add_argument("--rho", type=float, default=5.0)
    ap.add_argument("--beta", type=float, default=1.0)
    ap.add_argument("--floor", type=float, default=38.0)
    ap.add_argument("--min-gain", type=float, default=0.7)
    ap.add_argument("--keys", type=int, default=3)
    ap.add_argument("--samples", default="")
    args = ap.parse_args()
    run = Path(args.run)
    meta, bands, clean, regen = load(run)
    edges = np.array(meta["edges"])
    sources = meta["sources"]
    design, evaluate = sources[0::2], sources[1::2]
    cells = meta["cells"]
    host_gain, vine_gain = gains(meta, bands, "vine-r")
    _, v5_gain = gains(meta, bands, "v5-r3")

    v, u = np.meshgrid(np.arange(LOW), np.arange(LOW), indexing="ij")
    band = np.digitize(np.hypot(u, v), edges) - 1
    sig2 = {}
    for c in cells:
        acc, n = np.zeros((3, LOW, LOW)), 0
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
    allidx = np.argwhere(eligible)
    order = allidx[np.argsort(worst[eligible])][: args.k]
    ch, vv, uu = order[:, 0], order[:, 1], order[:, 2]
    lat = Lattice(ch, vv, uu, np.sqrt(worst[ch, vv, uu]), args.rho, args.beta)
    lat.save(run / "lattice-layout.json")
    tau = threshold(1e-6)
    print(f"layout k={lat.k}, rho={lat.rho}, floor={args.floor} dB; threshold at 1e-6 per claim with {len(MULTS)} step tries: {tau:.2f}")

    def choose_mult(s):
        y = regen.get((s, "R0-0.2", 12))
        if y is None:
            return 1.0
        ratio = np.sqrt(((y[ch, vv, uu].astype(np.float64) - clean[s][ch, vv, uu]) ** 2).mean() / worst[ch, vv, uu].mean())
        return min(MULTS, key=lambda q: abs(np.log(q / max(ratio, 1e-3))))

    pix = {s: img(f"clean_{s}_unmarked_None_None.png") for s in sources}
    marked = {}
    rows = {"psnr": [], "clean_z": [], "unmarked_clean_z": [], "wrong_key_clean_z": [], "mult": []}
    moves = {}
    for key_i in range(args.keys):
        key = f"owner-{key_i}"
        for s in sources:
            mult = choose_mult(s)
            out, move = embed(pix[s], lat, key, mult, args.floor)
            marked[(s, key_i)] = out
            moves[(s, key_i)] = move
            rows["psnr"].append(psnr(out, pix[s]))
            rows["mult"].append(mult)
            rows["clean_z"].append(read(out, lat, key))
            rows["unmarked_clean_z"].append(read(pix[s], lat, key))
            rows["wrong_key_clean_z"].append(read(out, lat, f"other-{key_i}"))
    p = np.array(rows["psnr"])
    print(f"quality: PSNR median {np.median(p):.2f}, min {p.min():.2f}, strict>35 on {(p > 35).mean():.3f} of marks; step multipliers used {sorted(set(rows['mult']))}")
    print(f"clean read: min z {np.min(rows['clean_z']):.1f}, median {np.median(rows['clean_z']):.1f}")
    print(f"unmarked clean: max z {np.max(rows['unmarked_clean_z']):.2f}; marked with wrong key: max z {np.max(rows['wrong_key_clean_z']):.2f}; threshold {tau:.2f}")

    print("\nT4 copy-paste and residual copy, real pixels, claimed owner = donor's owner")
    pairs = [(evaluate[i], evaluate[(i + j) % len(evaluate)]) for i in range(len(evaluate)) for j in (1, 2, 3, 5, 7)]
    t4 = {f"patch{sz}": [] for sz in (64, 128, 256, 384)}
    t4["residual"] = []
    t4["recipient_alone"] = []
    for key_i in range(args.keys):
        key = f"owner-{key_i}"
        for donor, target in pairs:
            d = marked[(donor, key_i)]
            t = pix[target]
            t4["recipient_alone"].append(read(t, lat, key))
            for sz in (64, 128, 256, 384):
                y = t.copy()
                a = (512 - sz) // 2
                y[a:a + sz, a:a + sz] = d[a:a + sz, a:a + sz]
                t4[f"patch{sz}"].append(read(y, lat, key))
            res = d.astype(np.float64) - pix[donor]
            t4["residual"].append(read(np.clip(np.rint(t + res), 0, 255), lat, key))
    for name, vals in t4.items():
        vals = np.array(vals)
        print(f"  {name:16} trials {len(vals):4d}  accepted {int((vals >= tau).sum()):4d}  max z {vals.max():6.2f}")

    print("\nT5 look-alike proxy, regenerated copies of the never-marked image (same content, no mark), all cells")
    un = [score_values(lat, regen[k][ch, vv, uu].astype(np.float64), f"owner-{ki}")
          for k in regen for ki in range(args.keys)]
    un = np.array(un)
    print(f"  trials {len(un)}  accepted {int((un >= tau).sum())}  max z {un.max():.2f}")

    print("\nT3 simulated, evaluation half, seeds 13 and 14 only, per-image detection rate at 1e-6")
    print("  gain scenario " + " ".join(f"{c:>7}" for c in cells))
    scen = {"v5 measured": v5_gain, "VINE measured": vine_gain, "fixed 0.7": 0.7, "fixed 0.5": 0.5, "fixed 0.3": 0.3, "fixed 0.2": 0.2}
    table = {}
    for name, g in scen.items():
        line = {}
        for c in cells:
            hs = np.full(lat.k, float(g)) if isinstance(g, float) else np.clip(g[c][ch, band[vv, uu]], 0, 1.2)
            ok, tot = 0, 0
            for key_i in range(args.keys):
                key = f"owner-{key_i}"
                for s in evaluate:
                    for seed in (13, 14):
                        y = regen.get((s, c, seed))
                        tot += 1
                        if y is None:
                            continue
                        vals = y[ch, vv, uu].astype(np.float64) + hs * moves[(s, key_i)]
                        ok += int(score_values(lat, vals, key) >= tau)
            line[c] = ok / tot
        table[name] = line
        print(f"  {name:13} " + " ".join(f"{line[c]:7.2f}" for c in cells))
    (run / "offline-safety.json").write_text(json.dumps({
        "k": lat.k, "rho": lat.rho, "floor": args.floor, "tau": tau,
        "psnr_median": float(np.median(p)), "psnr_min": float(p.min()),
        "t4": {k: {"n": len(v), "accepted": int((np.array(v) >= tau).sum()), "max": float(np.max(v))} for k, v in t4.items()},
        "t5_proxy": {"n": len(un), "accepted": int((un >= tau).sum()), "max": float(un.max())},
        "t3_sim": table,
    }, indent=1), encoding="utf-8")

    if args.samples:
        out = run / "samples"
        out.mkdir(exist_ok=True)
        for s in [int(i) for i in args.samples.split(",")]:
            Image.fromarray(pix[s]).save(out / f"{s}-original.png")
            Image.fromarray(marked[(s, 0)]).save(out / f"{s}-marked.png")
            diff = np.clip(128 + 12 * (marked[(s, 0)].astype(np.float64) - pix[s]), 0, 255).astype(np.uint8)
            Image.fromarray(diff).save(out / f"{s}-difference-x12.png")
            print(s, "PSNR", round(psnr(marked[(s, 0)], pix[s]), 2))


if __name__ == "__main__":
    main()
