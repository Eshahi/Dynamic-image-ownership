"""Judge's independent recheck of Codex's Gate 1 claims, from the raw development journal.

Written without reusing Codex's scripts. Standard library only.
"""
import json
import math
import statistics as st
from collections import Counter, defaultdict
from math import comb
from pathlib import Path

from loss_budget import CELLS, OWNER, load

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
    probe = next(r for r in rows.values() if r.get("arm") == "f5-r2" and r.get("channel") == "R1" and r.get("status") == "ok")
    raw = probe["detections"]["f5-r2"][OWNER]["raw"]
    print("raw keys:", sorted(raw))
    print("semantic.candidate value:", repr(raw["semantic"].get("candidate")), "| raw.semantic_code:", repr(raw.get("semantic_code")),
          "| semantic.decoded_code:", repr(raw["semantic"].get("decoded_code")))
    print("instance keys:", sorted(raw["instance"]))
    cand = Counter(str(r["detections"][a][OWNER]["raw"]["semantic"].get("candidate"))
                   for r in rows.values() for a in ("f5-r2", "v5-r3")
                   if r.get("arm") == a and r.get("status") == "ok" and r["detections"].get(a, {}).get(OWNER, {}).get("status") == "ok")
    print("candidate values:", cand.most_common(6))

    radii = [0, 1, 2, 3, 4, 6]
    thr = {r: threshold(sum(comb(32, i) for i in range(r + 1))) for r in radii}
    print("\n== corrected two-candidate ball bound, source majority /60")
    print("arm cell              " + " ".join(f"r={r:<3}" for r in radii))
    for arm in ("f5-r2", "v5-r3"):
        for chan, strength in CELLS + [("R1-mode", 0.2)]:
            hit = {r: defaultdict(int) for r in radii}
            for x in rows.values():
                if x.get("arm") != arm or x.get("channel") != chan or x.get("strength") != strength or x.get("status") != "ok":
                    continue
                call = x["detections"].get(arm, {}).get(OWNER)
                if not call or call.get("status") != "ok":
                    continue
                r0 = call["raw"]
                s = r0["semantic"]
                dec, rec = s.get("decoded_score"), s.get("recomputed_score")
                center, code = r0.get("semantic_code"), s.get("decoded_code")
                dist = None
                if center is not None and code is not None:
                    dist = bin(int(str(center), 16) ^ int(str(code), 16)).count("1")
                for r in radii:
                    ok = rec is not None and rec >= thr[r]
                    if dec is not None and dist is not None and dist <= r and dec >= thr[r]:
                        ok = True
                    hit[r][x["source_id"]] += int(ok)
            print(f"{arm:6} {chan}-{strength:<8} " + " ".join(f"{sum(1 for v in hit[r].values() if v >= 2):5d}" for r in radii))

    print("\n== fragile (instance) tier versus semantic tier, F5 and v5, source majority /60")
    print("arm cell        sem found  sem read   C   J | inst found  inst read   H   F")
    for arm in ("f5-r2", "v5-r3"):
        for chan, strength in [("clean", None)] + CELLS:
            c = defaultdict(lambda: defaultdict(int))
            for x in rows.values():
                if x.get("arm") != arm or x.get("channel") != chan or x.get("strength") != strength or x.get("status") != "ok":
                    continue
                call = x["detections"].get(arm, {}).get(OWNER)
                if not call or call.get("status") != "ok":
                    continue
                s, i, e = call["raw"]["semantic"], call["raw"]["instance"], call["endpoints"]
                src = x["source_id"]
                c["sf"][src] += int(bool(s.get("found")))
                c["sr"][src] += int(bool(s.get("read")))
                c["C"][src] += int(bool(e.get("C")))
                c["J"][src] += int(bool(e.get("J")))
                c["if"][src] += int(bool(i.get("found")))
                c["ir"][src] += int(bool(i.get("read")))
                c["H"][src] += int(bool(e.get("H")))
                c["F"][src] += int(bool(e.get("F")))
            need = 1 if chan == "clean" else 2
            v = {k: sum(1 for n in c[k].values() if n >= need) for k in ("sf", "sr", "C", "J", "if", "ir", "H", "F")}
            print(f"{arm:6} {str(chan):3}-{str(strength):<5} {v['sf']:9d} {v['sr']:9d} {v['C']:3d} {v['J']:3d} | {v['if']:10d} {v['ir']:10d} {v['H']:3d} {v['F']:3d}")

    print("\n== F5 clean writer margins from embedding reports")
    meds, mins, negs, tgt = [], [], [], set()
    for x in rows.values():
        if x.get("arm") == "f5-r2" and x.get("channel") == "clean" and x.get("status") == "ok":
            rep = x["embedding_report"]
            meds.append(rep["margin_median"])
            mins.append(rep["margin_min"])
            negs.append(rep["negative_chips"])
            tgt.add(rep["target_margin"])
    print(f"n {len(meds)}, target {tgt}, median of margin_median {st.median(meds):.3f}, max {max(meds):.3f}; "
          f"sources with any negative chip {sum(1 for n in negs if n > 0)}, median negative chips {st.median(negs)}, of 320")
    print(f"sources with median margin below target {sum(1 for m in meds if m < 4.0)}")

    print("\n== normalized-score effect of a larger amplitude, noise-dominated model")
    for score in (4.31,):
        n = math.sqrt(320)
        rho = score / math.sqrt(320 - score ** 2)
        for a in (1.0, 1.5, 2.0, 2.25, 3.0):
            print(f"  amplitude x{a}: linear {score * a:.2f}, normalized {n * a * rho / math.sqrt(1 + (a * rho) ** 2):.2f}  (threshold 8.26)")


if __name__ == "__main__":
    main()
