"""Measure regeneration as a channel, from saved development images only.

Treats each regenerator like a lens under test: how much of each spatial
frequency passes (gain), and how much new noise it adds. Uses the 60 Stage 2
development sources, unmarked and marked arms, common regeneration seeds.
No model runs here and no held-out data is read.

Outputs in --out:
  bands.npz    per source, per cell, per channel, per band statistics
  low.npz      low-band DCT coefficients of clean and unmarked regenerated images
"""
import argparse
import json
import os
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import numpy as np
from PIL import Image
from scipy.fft import dctn

RUNS = Path(r"W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs")
DIRS = [
    RUNS / "20261025-0128-encoder-transfer-stage2b/results/stage2b-full/images",
    RUNS / "20261024-1431-encoder-transfer-stage2a/results/stage2a-full/images",
]
ARMS = ["f5-r2", "v5-r3", "vine-r", "wam"]
CELLS = [("R0", 0.1), ("R0", 0.2), ("R0", 0.4), ("R1", 0.1), ("R1", 0.2), ("R1", 0.4), ("R3", 0.2)]
SEEDS = [12, 13, 14]
EDGES = np.array([0, 1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128, 192, 256, 384, 512, 2048], float)
LOW = 128

# Orthonormal colour transform, so energy here equals RGB energy for the PSNR budget.
OPP = np.array([
    [1 / np.sqrt(3), 1 / np.sqrt(3), 1 / np.sqrt(3)],
    [1 / np.sqrt(2), -1 / np.sqrt(2), 0.0],
    [1 / np.sqrt(6), 1 / np.sqrt(6), -2 / np.sqrt(6)],
])


def path_of(name):
    for d in DIRS:
        p = d / name
        if p.exists():
            return p
    return None


def load_dct(name):
    p = path_of(name)
    if p is None:
        return None
    arr = np.asarray(Image.open(p).convert("RGB"), dtype=np.float64)
    opp = np.tensordot(arr, OPP.T, axes=([2], [0]))
    return np.stack([dctn(opp[..., c], norm="ortho") for c in range(3)], axis=0)


def band_index(shape):
    h, w = shape
    v, u = np.meshgrid(np.arange(h), np.arange(w), indexing="ij")
    idx = np.digitize(np.hypot(u, v), EDGES) - 1
    return idx


def by_band(values, idx, n):
    return np.stack([np.bincount(idx.ravel(), weights=values[c].ravel(), minlength=n)[:n] for c in range(3)])


def process(source):
    nb = len(EDGES) - 1
    x = load_dct(f"clean_{source}_unmarked_None_None.png")
    idx = band_index(x.shape[1:])
    count = np.bincount(idx.ravel(), minlength=nb)[:nb].astype(np.float64)
    out = {"source": source, "count": count, "host": by_band(x * x, idx, nb), "shape": x.shape}
    low = {"clean": x[:, :LOW, :LOW].astype(np.float32)}
    marks = {}
    for arm in ARMS:
        xa = load_dct(f"clean_{source}_{arm}_None_None.png")
        if xa is None or xa.shape != x.shape:
            continue
        marks[arm] = xa
    out["mark_energy"] = {arm: by_band((marks[arm] - x) ** 2, idx, nb) for arm in marks}
    for chan, strength in CELLS:
        cell = f"{chan}-{strength}"
        ys = {}
        for seed in SEEDS:
            y = load_dct(f"{chan}_{source}_unmarked_{strength}_{seed}.png")
            if y is not None and y.shape == x.shape:
                ys[seed] = y
        if not ys:
            continue
        stack = np.stack(list(ys.values()))
        res = stack - x
        rec = {
            "n_seeds": len(ys),
            "noise": by_band((res * res).mean(0), idx, nb),
            "host_cross": by_band((x * stack).mean(0), idx, nb),
            "regen_power": by_band((stack * stack).mean(0), idx, nb),
        }
        if len(ys) > 1:
            rec["seed_var"] = by_band(stack.var(0, ddof=1), idx, nb)
        rec["low"] = {s: ys[s][:, :LOW, :LOW].astype(np.float32) for s in ys}
        resp = {}
        for arm, xa in marks.items():
            w = xa - x
            ww = np.zeros((3, nb))
            wd = np.zeros((3, nb))
            dd = np.zeros((3, nb))
            cnt = 0
            for seed, y in ys.items():
                ya = load_dct(f"{chan}_{source}_{arm}_{strength}_{seed}.png")
                if ya is None or ya.shape != x.shape:
                    continue
                d = ya - y
                ww += by_band(w * w, idx, nb)
                wd += by_band(w * d, idx, nb)
                dd += by_band(d * d, idx, nb)
                cnt += 1
            if cnt:
                resp[arm] = {"ww": ww, "wd": wd, "dd": dd, "n": cnt}
        rec["resp"] = resp
        out[cell] = rec
    return out, low


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--sources", default="")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    names = sorted(p.name for p in DIRS[1].glob("clean_*_unmarked_None_None.png"))
    sources = sorted(int(n.split("_")[1]) for n in names)
    if args.sources:
        sources = [int(s) for s in args.sources.split(",")]
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(process, sources))
    np.savez_compressed(out / "low.npz", **{
        f"{r[0]['source']}:clean": r[1]["clean"] for r in results
    }, **{
        f"{r[0]['source']}:{c}:{s}": r[0][c]["low"][s]
        for r in results for c in (f"{a}-{b}" for a, b in CELLS) if c in r[0] for s in r[0][c]["low"]
    })
    for r, _ in results:
        for c in (f"{a}-{b}" for a, b in CELLS):
            if c in r:
                del r[c]["low"]
    np.save(out / "bands.npy", np.array([r for r, _ in results], dtype=object), allow_pickle=True)
    meta = {
        "sources": sources,
        "cells": [f"{a}-{b}" for a, b in CELLS],
        "seeds": SEEDS,
        "arms": ARMS,
        "edges": EDGES.tolist(),
        "shape": list(results[0][0]["shape"]),
        "seconds": time.time() - t0,
    }
    (out / "meta.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    print(json.dumps(meta)[:600])


if __name__ == "__main__":
    main()
