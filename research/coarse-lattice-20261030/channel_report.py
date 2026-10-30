"""Turn the channel measurement into gain, noise and capacity tables."""
import argparse
import json
from pathlib import Path

import numpy as np

CHANNELS = ["luma", "red-green", "blue-yellow"]
PRIMARY = ["R0-0.2", "R1-0.1", "R1-0.2", "R3-0.2"]


def water_fill(count, ratio, energy):
    """Maximise sum count*0.5*log2(1 + P/ratio) with sum count*P = energy."""
    order = np.argsort(ratio)
    r, c = ratio[order], count[order]
    used = 0.0
    level = None
    for i in range(len(r)):
        used += c[i] * r[i]
        cand = (energy + used) / c[: i + 1].sum()
        if i + 1 == len(r) or cand <= r[i + 1]:
            level = cand
            break
    power = np.maximum(level - ratio, 0)
    bits = (count * 0.5 * np.log2(1 + power / ratio)).sum()
    return bits, power


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    args = ap.parse_args()
    run = Path(args.run)
    meta = json.loads((run / "meta.json").read_text(encoding="utf-8"))
    rows = list(np.load(run / "bands.npy", allow_pickle=True))
    edges = meta["edges"]
    labels = [f"{int(edges[i])}-{int(edges[i + 1])}" for i in range(len(edges) - 1)]
    count = rows[0]["count"]
    nb = len(count)
    shape = meta["shape"]
    px = shape[1] * shape[2]
    print("sources", len(rows), "image", shape, "coefs per band", count.astype(int).tolist())

    host = np.mean([r["host"] for r in rows], axis=0) / count
    lines = {}
    print("\n== root mean noise per DCT coefficient, luma, 0-255 scale (all regeneration change)")
    print("band      host_rms " + " ".join(f"{c:>9}" for c in meta["cells"]))
    noise = {}
    seedv = {}
    gain = {}
    for cell in meta["cells"]:
        have = [r for r in rows if cell in r]
        noise[cell] = np.mean([r[cell]["noise"] for r in have], axis=0) / count
        seedv[cell] = np.mean([r[cell]["seed_var"] for r in have if "seed_var" in r[cell]], axis=0) / count
        cross = np.sum([r[cell]["host_cross"] for r in have], axis=0)
        hh = np.sum([r["host"] for r in have], axis=0)
        gain[cell] = cross / hh
    for b in range(nb):
        print(f"{labels[b]:>9} {np.sqrt(host[0, b]):9.1f} " + " ".join(f"{np.sqrt(noise[c][0, b]):9.2f}" for c in meta["cells"]))
    print("\n== share of that noise that changes between seeds (rest repeats for this image), luma")
    for b in range(nb):
        print(f"{labels[b]:>9}           " + " ".join(f"{seedv[c][0, b] / noise[c][0, b]:9.2f}" for c in meta["cells"]))
    print("\n== host gain in each band, luma (regenerated vs clean projection)")
    for b in range(nb):
        print(f"{labels[b]:>9}           " + " ".join(f"{gain[c][0, b]:9.3f}" for c in meta["cells"]))
    print("\n== root mean noise, chroma channels, at the primary cells")
    for ch in (1, 2):
        print(CHANNELS[ch])
        for b in range(0, nb):
            print(f"{labels[b]:>9} {np.sqrt(host[ch, b]):9.1f} " + " ".join(f"{np.sqrt(noise[c][ch, b]):9.2f}" for c in meta["cells"]))

    print("\n== mark response: share of each existing mark's energy that survives regeneration, luma")
    resp_gain = {}
    for arm in meta["arms"]:
        energy = np.mean([r["mark_energy"][arm] for r in rows if arm in r["mark_energy"]], axis=0) / count
        psnr_rows = [r["mark_energy"][arm].sum() / (3 * px) for r in rows if arm in r["mark_energy"]]
        print(f"{arm}: median clean PSNR {np.median([10 * np.log10(255 ** 2 / m) for m in psnr_rows]):.2f}")
        tot = energy * count
        share = tot[0] / tot.sum()
        print("  energy share by band: " + " ".join(f"{labels[b]}:{share[b]:.2f}" for b in range(nb) if share[b] > 0.02))
        for cell in meta["cells"]:
            wd = np.zeros((3, nb))
            ww = np.zeros((3, nb))
            dd = np.zeros((3, nb))
            for r in rows:
                if cell in r and arm in r[cell]["resp"]:
                    wd += r[cell]["resp"][arm]["wd"]
                    ww += r[cell]["resp"][arm]["ww"]
                    dd += r[cell]["resp"][arm]["dd"]
            with np.errstate(divide="ignore", invalid="ignore"):
                h = wd / ww
                coh = wd ** 2 / (ww * dd)
            resp_gain[(arm, cell)] = (h, coh, ww)
            print(f"  {cell:7} gain " + " ".join(f"{h[0, b]:6.2f}" for b in range(nb)))
    print("  bands   " + " ".join(f"{labels[b]:>6}" for b in range(nb)))

    print("\n== dirty-paper capacity in bits, with reverse water-filling over all channels and bands")
    print("   writer knows the image, not the regeneration noise; gain from the best available mark response")
    budgets = [35, 38, 40, 42, 45, 48, 52]
    print("cell     " + " ".join(f"{b:>7}dB" for b in budgets))
    results = {}
    for cell in meta["cells"] + ["worst-of-primary"]:
        cap = []
        for psnr in budgets:
            energy = 3 * px * 255 ** 2 * 10 ** (-psnr / 10)
            cells = PRIMARY if cell == "worst-of-primary" else [cell]
            ratio = np.zeros((3, nb))
            for c in cells:
                g = np.clip(gain[c], 0.05, 1.0)
                ratio = np.maximum(ratio, noise[c] / g ** 2)
            bits, _ = water_fill(np.tile(count, 3), ratio.ravel(), energy)
            cap.append(float(bits))
        results[cell] = cap
        print(f"{cell:16} " + " ".join(f"{v:9.0f}" for v in cap))
    (run / "capacity.json").write_text(json.dumps({"budgets_db": budgets, "bits": results}, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
