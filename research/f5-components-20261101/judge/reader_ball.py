"""Counterfactual on saved numbers: search only the codes the content check could accept.

The frozen reader searches all 2^32 codes, so its threshold is 8.26, then rejects any
code outside the content radius. Testing only codes within Hamming radius r of the
code recomputed from the suspect spends the false-positive budget only on acceptable
codes. A row counts if the decoded code lies inside the ball and clears the lower
threshold, or if the recomputed code itself clears it. This is a lower bound: the best
code inside the ball may score higher than the row's saved scores show.

Exploratory, development journal only, no writer change. T4 and T5 effects are not
measured here and would need a real run. Also reports the fragile tier's share of F5's
distortion from saved embedding reports.
"""
import json
import math
import statistics as st
from collections import defaultdict
from math import comb
from pathlib import Path

from loss_budget import ARMS, CELLS, OWNER, load

TAIL = 1 / (2 * math.erfc(1))


def threshold(n, target=1e-6):
    lo, hi = 0.0, 40.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if TAIL * n * 0.5 * math.erfc(mid / math.sqrt(2)) <= target:
            hi = mid
        else:
            lo = mid
    return hi


def main():
    rows = load()
    radii = [0, 1, 2, 3, 4, 6]
    thresholds = {r: threshold(sum(comb(32, i) for i in range(r + 1))) for r in radii}
    print("frozen thresholds:", round(threshold(1), 3), round(threshold(2 ** 32), 3))
    print("ball thresholds:", {r: round(t, 3) for r, t in thresholds.items()})
    out = {}
    for arm in ARMS:
        print(f"\n== {arm}: source-majority count, /60")
        print("cell      frozen C | " + " ".join(f"r={r:<3}" for r in radii))
        for chan, strength in CELLS:
            frozen = defaultdict(int)
            hit = {r: defaultdict(int) for r in radii}
            for x in rows.values():
                if x.get("arm") != arm or x.get("channel") != chan or x.get("strength") != strength or x.get("status") != "ok":
                    continue
                call = x["detections"].get(arm, {}).get(OWNER)
                if not call or call.get("status") != "ok":
                    continue
                s = call["raw"]["semantic"]
                src = x["source_id"]
                if call["endpoints"].get("C"):
                    frozen[src] += 1
                dec, rec = s.get("decoded_score"), s.get("recomputed_score")
                code, cand = s.get("decoded_code"), s.get("candidate")
                dist = None
                if code is not None and cand is not None:
                    try:
                        dist = bin(int(str(code), 16) ^ int(str(cand), 16)).count("1")
                    except ValueError:
                        dist = None
                for r in radii:
                    t = thresholds[r]
                    ok = rec is not None and rec >= t
                    if dec is not None and dist is not None and dist <= r and dec >= t:
                        ok = True
                    if ok:
                        hit[r][src] += 1
            line = [sum(1 for v in hit[r].values() if v >= 2) for r in radii]
            c = sum(1 for v in frozen.values() if v >= 2)
            print(f"{chan}-{strength:<4} {c:8d} | " + " ".join(f"{v:5d}" for v in line))
            out[f"{arm}|{chan}-{strength}"] = {"frozen": c, **{f"r{r}": v for r, v in zip(radii, line)}}
    Path(__file__).with_name("reader-ball.json").write_text(json.dumps({"thresholds": thresholds, "counts": out}, indent=1), encoding="utf-8")

    print("\n== F5 embedding reports, clean rows")
    psnr, frag = [], []
    sample = None
    for x in rows.values():
        if x.get("arm") == "f5-r2" and x.get("channel") == "clean" and x.get("status") == "ok":
            rep = x.get("embedding_report") or {}
            sample = rep if sample is None else sample
            if rep.get("rgb_psnr_db"):
                psnr.append(rep["rgb_psnr_db"])
            ic = rep.get("instance_channel") or {}
            for key in ("psnr_db", "tier_psnr_db", "achieved_psnr_db", "luma_psnr_db", "rgb_psnr_db"):
                if ic.get(key):
                    frag.append(ic[key])
                    break
    print("report keys:", sorted(sample) if sample else None)
    print("instance_channel keys:", sorted((sample or {}).get("instance_channel") or {}))
    print("instance_channel sample:", json.dumps((sample or {}).get("instance_channel"))[:500])
    if psnr:
        print("median total RGB PSNR", round(st.median(psnr), 2))
    if frag:
        print("median fragile tier PSNR", round(st.median(frag), 2))


if __name__ == "__main__":
    main()
