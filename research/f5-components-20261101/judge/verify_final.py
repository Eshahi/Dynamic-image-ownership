"""Judge's final recheck of G2-A, G2-B and G2-C, written independently of gate2_reader.py.

Standard library only. Reads the raw Stage 2 journal and the raw G2-B reader rows. No pixels, no models.
"""
import itertools
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

RD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RD / "judge"))
from loss_budget import CELLS, OWNER, load  # noqa: E402

T = 7.779133080172838
LIMIT = 6


def expected_best(m):
    return m * 0.5 * (1 + math.erf(m / 2)) + math.exp(-m * m / 4) / math.sqrt(math.pi)


def err(s):
    t = s / math.sqrt(32)
    if t <= expected_best(0):
        return .5
    if t >= math.sqrt(10):
        return 0.0
    lo, hi = 0.0, 1e6
    for _ in range(80):
        mid = (lo + hi) / 2
        if expected_best(mid) / math.sqrt(1 + mid * mid / 10) < t:
            lo = mid
        else:
            hi = mid
    return .5 * math.erfc(lo / 2)


def ham(a, b):
    return bin(int(a, 16) ^ int(b, 16)).count("1")


def tier(res, own):
    s = res["decoded_score"]
    e = err(s)
    d = ham(res["decoded_code"], own)
    return s >= T and min(32.0, max(0.0, (d - 32 * e) / (1 - 2 * e))) <= LIMIT


def endpoint(raw):
    s, i = raw["semantic"], raw["instance"]
    a = tier(s, raw["semantic_code"])
    b = tier(i, raw["perceptual_hash"])
    veto = bool(s.get("read")) and not bool(s.get("content_match"))
    return a, b, veto, a or (b and not veto)


rows = load()
sources = sorted({x["source_id"] for x in rows.values() if x.get("channel") == "clean"})
half = {s: "DESIGN" if j % 2 == 0 else "EVALUATE" for j, s in enumerate(sources)}

print("== G2-A, Stage 2, EVALUATE /30, my implementation")
for arm in ("f5-r2", "v5-r3"):
    print(" ", arm, "cell: C | Bs | Bi | B | C or B | C sources lost")
    for chan, strength in CELLS:
        t = defaultdict(Counter)
        for x in rows.values():
            if x.get("arm") != arm or x.get("channel") != chan or x.get("strength") != strength or x.get("status") != "ok":
                continue
            if half[x["source_id"]] != "EVALUATE":
                continue
            call = x["detections"].get(arm, {}).get(OWNER)
            if not call or call.get("status") != "ok":
                continue
            a, b, veto, B = endpoint(call["raw"])
            C = bool(call["endpoints"].get("C"))
            sid = x["source_id"]
            t["C"][sid] += C
            t["Bs"][sid] += a
            t["Bi"][sid] += b and not veto
            t["B"][sid] += B
            t["CB"][sid] += C or B
        n = {k: {q for q, v in t[k].items() if v >= 2} for k in t}
        lost = sorted(n["C"] - n["B"])
        print(f"    {chan}-{strength:<4} {len(n['C']):2d} | {len(n['Bs']):2d} | {len(n['Bi']):2d} | {len(n['B']):2d} | {len(n['CB']):2d} | {lost}")

print("\n== G2-B, raw rows")
counts = Counter()
per_pair = Counter()
bad = []
routes = Counter()
minq = None
for path in sorted((RD / "results/g2-b-transfer").glob("batch-*.jsonl")):
    for line in open(path, encoding="utf-8"):
        row = json.loads(line)
        counts["rows"] += 1
        if row.get("status") != "ok" and not row.get("raw"):
            counts["not ok"] += 1
            continue
        raw = row["raw"]
        s, i = raw["semantic"], raw["instance"]
        a, b, veto, B = endpoint(raw)
        C = bool(s.get("read")) and bool(s.get("content_match"))
        O = C or (bool(i.get("found")) and bool(i.get("content_match")))
        counts["C"] += C
        counts["O"] += O
        counts["Bs"] += a
        counts["Bi"] += b and not veto
        counts["B"] += B
        if O and not C:
            routes["read" if i.get("read") else "recomputed only"] += 1
        q = row.get("quality") or {}
        counts["strict"] += q.get("psnr_db", 0) > 35 and q.get("ssim_rgb", 0) > .9
        rec = row.get("endpoints") or {}
        if rec and bool(rec.get("B")) != bool(B):
            bad.append(row.get("id"))
        if B:
            print("   B accept", row.get("id"), "inst dec", round(i["decoded_score"], 4), "d_i", ham(i["decoded_code"], raw["perceptual_hash"]), "quality", {k: round(v, 4) for k, v in q.items() if isinstance(v, float)})
print("  ", dict(counts))
print("   O beyond C, by instance route:", dict(routes))
print("   rows where my B disagrees with the recorded B:", bad)

print("\n== G2-C, clean codes, pairs inside EVALUATE and all pairs")
codes = {}
for x in rows.values():
    if x.get("channel") == "clean" and x.get("arm") == "unmarked" and x.get("status") == "ok":
        call = x["detections"].get("f5-r2", {}).get(OWNER)
        if call and call.get("status") == "ok":
            codes[x["source_id"]] = (call["raw"]["semantic_code"], call["raw"]["perceptual_hash"])
print("   sources", len(codes))
for label, subset in (("EVALUATE", [s for s in codes if half[s] == "EVALUATE"]), ("ALL", list(codes))):
    pairs = list(itertools.combinations(sorted(subset), 2))
    for name, idx in (("q", 0), ("h", 1)):
        ds = [ham(codes[a][idx], codes[b][idx]) for a, b in pairs]
        print(f"   {label} {name}: pairs {len(ds)} mean {sum(ds) / len(ds):.5f} min {min(ds)}", {f"<={r}": sum(d <= r for d in ds) for r in (6, 8, 9)})
