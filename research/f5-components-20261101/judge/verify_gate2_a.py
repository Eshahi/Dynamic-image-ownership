"""Independent Gate 2 checks from raw files, written without importing Codex's reducers."""
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median

RD = Path(r"C:\Users\Soroush\.codex\worktrees\codex-f5-components\research\f5-components-20261101")


def phi_bar(z):
    return 0.5 * math.erfc(z / math.sqrt(2))


def threshold(mult, alpha=1e-6, c=3.1787):
    lo, hi = 0.0, 40.0
    for _ in range(300):
        m = (lo + hi) / 2
        if c * mult * phi_bar(m) > alpha:
            lo = m
        else:
            hi = m
    return hi


print("== thresholds, BD constant 3.1787")
for name, mult, a in [
    ("decoded 2^32 a", 2**32, 1e-6), ("recomputed 1 a", 1, 1e-6),
    ("O_U decoded 2^32 a/4", 2**32, 2.5e-7), ("O_U recomputed a/4", 1, 2.5e-7),
    ("O_Q decoded 2^64 a/4", 2**64, 2.5e-7), ("O_Q recomputed 2^32 a/4", 2**32, 2.5e-7),
]:
    print(f"  {name:28} {threshold(mult, a):.6f}")
for r in (0, 1, 2, 3, 4, 6, 8, 10):
    size = sum(math.comb(32, j) for j in range(r + 1))
    print(f"  ball r={r:<2} size {size:>12} t={threshold(size):.4f}")

print("\n== T1 calls.csv: recount source-majority O_U, EVALUATE, F5, stage2-union")
rows = list(csv.DictReader(open(RD / "results/wp4-t1/calls.csv", encoding="utf-8", newline="")))
print("  rows", len(rows), "cells", len({(r['study'], r['cell']) for r in rows}))
agg = defaultdict(lambda: defaultdict(Counter))
for r in rows:
    if r["study"] != "stage2-union" or r["role"] != "marked":
        continue
    for ep in ("C", "J", "O", "O_U", "O_Q", "if", "io", "sf"):
        agg[(r["arm"], r["cell"], r["split"])][ep][r["source"]] += r[ep] == "True"
for arm in ("f5-r2", "v5-r3"):
    for cell in ("R0-0.1", "R0-0.2", "R0-0.4", "R1-0.1", "R1-0.2", "R1-0.4", "R3-0.2"):
        for split in ("DESIGN", "EVALUATE"):
            a = agg[(arm, cell, split)]
            line = {ep: sum(v >= 2 for v in a[ep].values()) for ep in ("C", "J", "O", "O_U", "O_Q", "sf", "if", "io")}
            print(f"  {arm} {cell:7} {split:8}", line)

print("\n== T1 negatives in calls.csv")
neg = Counter()
for r in rows:
    if r["role"] != "marked":
        for ep in ("C", "O", "O_U", "O_Q", "either"):
            neg[(r["arm"], r["role"], ep)] += r[ep] == "True"
        neg[(r["arm"], r["role"], "calls")] += 1
for k in sorted(neg):
    print(" ", k, neg[k])

print("\n== F5 T4 pixel events, raw jsonl")
events = []
for path in sorted((RD / "results/wp4-pixels").glob("f5-r2-*.jsonl")):
    for line in open(path, encoding="utf-8"):
        row = json.loads(line)
        if row.get("panel") != "T4" or row.get("result_status") != "ok":
            continue
        for call in row["calls"]:
            raw = call.get("raw") or {}
            sem, ins = raw.get("semantic") or {}, raw.get("instance") or {}
            events.append((row["id"], row["split"], row.get("donor_split"), call["owner"][:8], call["role"], raw.get("outcome"),
                           sem.get("found"), sem.get("read"), sem.get("content_match"), round(sem.get("decoded_score", 0), 3), round(sem.get("recomputed_score", 0), 3),
                           ins.get("found"), ins.get("read"), ins.get("content_match"), ins.get("candidate"), round(ins.get("decoded_score", 0), 3), round(ins.get("recomputed_score", 0), 3),
                           ins.get("corrected_hamming_distance", ins.get("content_distance")), ins.get("error_rate")))
print("  T4 calls", len(events))
print("  fields: id split donor_split owner role outcome | sem found read content dec rec | inst found read content cand dec rec dist err")
for e in events:
    if e[11] or e[6]:
        print("  ", e)

print("\n== raw keys of one F5 T4 call")
for path in sorted((RD / "results/wp4-pixels").glob("f5-r2-*.jsonl")):
    for line in open(path, encoding="utf-8"):
        row = json.loads(line)
        if row.get("panel") == "T4" and row.get("result_status") == "ok":
            raw = row["calls"][0]["raw"]
            print(json.dumps({k: (v if not isinstance(v, (list, dict)) else "...") for k, v in raw.items()}))
            print("semantic", json.dumps(raw["semantic"])[:900])
            print("instance", json.dumps(raw["instance"])[:900])
            raise SystemExit
