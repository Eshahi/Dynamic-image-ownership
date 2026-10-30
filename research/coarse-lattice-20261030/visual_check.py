"""SSIM on all development marks, and flat-region crops for human viewing."""
import argparse
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, uniform_filter

from coarse_lattice import MULTS, Lattice, embed, psnr, to_coefs
from measure_channel import DIRS

SKETCH = [(1, 0), (2, 0), (0, 2), (0, 1), (1, 1), (0, 3), (2, 1), (3, 2), (4, 0), (5, 0), (0, 4), (3, 0), (1, 3), (7, 0), (4, 1), (2, 8)]


def img(name):
    for d in DIRS:
        p = d / name
        if p.exists():
            return np.asarray(Image.open(p).convert("RGB"))
    raise FileNotFoundError(name)


def ssim(a, b):
    a, b = a.astype(np.float64), b.astype(np.float64)
    c1, c2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2
    vals = []
    for c in range(3):
        x, y = a[..., c], b[..., c]
        mx, my = gaussian_filter(x, 1.5), gaussian_filter(y, 1.5)
        sxx = gaussian_filter(x * x, 1.5) - mx * mx
        syy = gaussian_filter(y * y, 1.5) - my * my
        sxy = gaussian_filter(x * y, 1.5) - mx * my
        vals.append(((2 * mx * my + c1) * (2 * sxy + c2) / ((mx * mx + my * my + c1) * (sxx + syy + c2))).mean())
    return float(np.mean(vals))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    args = ap.parse_args()
    run = Path(args.run)
    lat = Lattice.load(run / "lattice-layout.json")
    z = np.load(run / "low.npz")
    sources = sorted({int(k.split(":")[0]) for k in z.files})
    base = (lat.sigma ** 2).mean()
    rows = []
    out = run / "samples"
    out.mkdir(exist_ok=True)
    for s in sources:
        x = img(f"clean_{s}_unmarked_None_None.png")
        key = f"R{0}"
        name = f"{s}:R0-0.2:12"
        mult = 1.0
        if name in z.files:
            r = z[name][lat.ch, lat.vv, lat.uu].astype(np.float64) - z[f"{s}:clean"][lat.ch, lat.vv, lat.uu]
            mult = min(MULTS, key=lambda q: abs(np.log(q / max(np.sqrt((r ** 2).mean() / base), 1e-3))))
        low = to_coefs(x)[0]
        bits = np.array([low[v, u] >= 0 for v, u in SKETCH], dtype=int)
        sk = int((bits << np.arange(len(SKETCH))).sum())
        marked, _ = embed(x, lat, f"owner-0|{sk}", mult, 38.0)
        rows.append((s, psnr(marked, x), ssim(marked, x), mult))
        if s in (1180, 1786, 30, 72, 165):
            gray = x.mean(axis=2)
            var = uniform_filter(gray ** 2, 180) - uniform_filter(gray, 180) ** 2
            margin = 90
            inner = var[margin:-margin, margin:-margin]
            yy, xx = np.unravel_index(np.argmin(inner), inner.shape)
            yy, xx = yy + margin - 90, xx + margin - 90
            a = x[yy:yy + 180, xx:xx + 180]
            b = marked[yy:yy + 180, xx:xx + 180]
            gap = np.full((180, 6, 3), 255, dtype=np.uint8)
            pair = np.concatenate([a, gap, b], axis=1)
            Image.fromarray(pair).resize((pair.shape[1] * 3, pair.shape[0] * 3), Image.NEAREST).save(out / f"{s}-flat-crop-original-left-marked-right.png")
    arr = np.array([(p, q) for _, p, q, _ in rows])
    print(f"PSNR median {np.median(arr[:, 0]):.2f} min {arr[:, 0].min():.2f}; SSIM median {np.median(arr[:, 1]):.4f} min {arr[:, 1].min():.4f}; strict SSIM>.9 on {(arr[:, 1] > .9).mean():.3f}")


if __name__ == "__main__":
    main()
