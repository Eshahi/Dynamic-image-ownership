"""Descriptive decomposition of the frozen pooled kappa by family and cell, on the 30 FIT sources only.

Written by Claude (Opus 5.5) on 2026-10-26 after the Phase-A freeze. It changes nothing in the freeze: kappa, q90 and
the comparator stay as phase-a-fit.json records them. Calibration-source rows are not read, so they stay unused by any
later declared amendment. The weights are the frozen 1/18 per seed vector.

Usage: python -I kappa_decomposition.py RUN_FOLDER > kappa-decomposition.json
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np


def main():
    num, den, cos, ratio = defaultdict(float), defaultdict(float), defaultdict(list), defaultdict(list)
    latest = {}
    for line in (Path(sys.argv[1]) / "native.jsonl").read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        if r["kind"] == "law":
            latest[r["id"]] = r
    for r in latest.values():
        if r.get("status") != "ok" or r["split"] != "fit":
            continue
        v, d = np.asarray(r["v"]), np.asarray(r["p1"]) - np.asarray(r["b"])
        for key in ("pooled", r["family"], r["cell"]):
            num[key] += float(v @ d) / 18
            den[key] += float(v @ v) / 18
        cos[r["cell"]].append(float(v @ d / np.linalg.norm(v) / np.linalg.norm(d)))
        ratio[r["cell"]].append(float(np.linalg.norm(v) / np.linalg.norm(d)))
    out = dict(split="fit (30 sources)", pooled_kappa=num["pooled"] / den["pooled"],
               family={f: dict(kappa=num[f] / den[f], denominator_share=den[f] / den["pooled"]) for f in ("R0", "R1")},
               cell={c: dict(kappa=num[c] / den[c], n=len(cos[c]), median_cos_v_actual=float(np.median(cos[c])),
                             median_norm_ratio_v_over_actual=float(np.median(ratio[c]))) for c in sorted(cos)})
    json.dump(out, sys.stdout, indent=1)


if __name__ == "__main__":
    main()
