"""Last Gate 2 rechecks: T3 medians, T2/T5 counts, T0 headroom, and the design-half rule with the production veto."""
import csv
import importlib.util
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, median

RD = Path(r"C:\Users\Soroush\.codex\worktrees\codex-f5-components\research\f5-components-20261101")
sys.path.insert(0, str(RD / "judge"))
from loss_budget import CELLS, OWNER, load  # noqa: E402

spec = importlib.util.spec_from_file_location("g2c", Path(__file__).with_name("verify_gate2_c.py"))

print("== T3 medians from T3-pairs.csv, EVALUATE (seed mean per source, then median)")
tp = list(csv.DictReader(open(RD / "results/wp4-pixel-summary/T3-pairs.csv", encoding="utf-8", newline="")))
for method, cell in [("f5-r2", "R0-0.2"), ("f5-r2", "R1-0.2"), ("f5-r2", "R3-0.2"), ("v5-r3", "R0-0.2"), ("v5-r3", "R1-0.2"), ("v5-r3", "R3-0.2"), ("f5-r2", "X1"), ("f5-r2", "X2")]:
    by = defaultdict(list)
    for r in tp:
        if r["method"] == method and r["cell"] == cell and r["split"] == "EVALUATE" and r["robust_alignment_retention"]:
            by[r["source"]].append((float(r["robust_alignment_retention"]), float(r["instance_alignment_retention"])))
    rob = median(mean(v[0] for v in vs) for vs in by.values())
    ins = median(mean(v[1] for v in vs) for vs in by.values())
    print(f"  {method} {cell:7} sources {len(by)} robust {rob:.6f} second {ins:.6f}")

print("\n== negative-calls.csv recount")
neg = list(csv.DictReader(open(RD / "results/wp4-pixel-summary/negative-calls.csv", encoding="utf-8", newline="")))
c = Counter()
for r in neg:
    k = (r["method"], r["panel"], r["split"], r["role"])
    c[k + ("calls",)] += 1
    for m in ("C", "O_U", "r3"):
        c[k + (m,)] += r[m] == "True"
for k in sorted({x[:4] for x in c}):
    if k[1] == "T4":
        print("  ", k, {m: c[k + (m,)] for m in ("calls", "C", "O_U", "r3")})

print("\n== T5-pairs.csv recount, different content")
t5 = list(csv.DictReader(open(RD / "results/wp4-pixel-summary/T5-pairs.csv", encoding="utf-8", newline="")))
print("  columns", list(t5[0].keys())[:16])
g = Counter()
for r in t5:
    k = (r["method"], r["pair_split"], r["category"])
    g[k + ("n",)] += 1
    g[k + ("accept",)] += r.get("accept") == "True"
    g[k + ("lower",)] += r.get("lower_accept") == "True"
    g[k + ("extra",)] += r.get("extra") == "True"
for k in sorted({x[:3] for x in g}):
    print("  ", k, {m: g[k + (m,)] for m in ("n", "accept", "lower", "extra")})

print("\n== T0 headroom from wp4-t0/cells.csv")
t0 = list(csv.DictReader(open(RD / "results/wp4-t0/cells.csv", encoding="utf-8", newline="")))
print("  columns", list(t0[0].keys())[:16])

print("\n== design half, B with production veto: instance pass void when semantic is read and frozen status is not match")
src = Path(__file__).with_name("verify_gate2_c.py").read_text(encoding="utf-8").split('rows = load()')[0]
ns = {"__file__": str(Path(__file__).with_name("verify_gate2_c.py")), "__name__": "g2c"}
exec(src, ns)
bd = ns["bd"]
rows = load()
sources = sorted({x["source_id"] for x in rows.values() if x.get("channel") == "clean"})
design = {s for j, s in enumerate(sources) if j % 2 == 0}
for arm in ("f5-r2", "v5-r3"):
    print(" ", arm, "cell: C | Bs | Bi no veto | Bi veto | B | C or B | C lost by B")
    for chan, strength in CELLS:
        t = defaultdict(Counter)
        for x in rows.values():
            if x.get("arm") != arm or x.get("channel") != chan or x.get("strength") != strength or x.get("status") != "ok" or x["source_id"] not in design:
                continue
            call = x["detections"].get(arm, {}).get(OWNER)
            if not call or call.get("status") != "ok":
                continue
            raw = call["raw"]
            s, i = raw["semantic"], raw["instance"]
            a = bd(s, raw["semantic_code"])
            b = bd(i, raw["perceptual_hash"])
            veto = bool(s.get("read")) and not bool(s.get("content_match"))
            sid = x["source_id"]
            C = bool(call["endpoints"].get("C"))
            t["C"][sid] += C
            t["Bs"][sid] += a
            t["Bi"][sid] += b
            t["Biv"][sid] += b and not veto
            t["B"][sid] += a or (b and not veto)
            t["CB"][sid] += C or a or (b and not veto)
        n = {k: {q for q, v in t[k].items() if v >= 2} for k in t}
        print(f"    {chan}-{strength:<4} {len(n['C']):2d} | {len(n['Bs']):2d} | {len(n['Bi']):2d} | {len(n['Biv']):2d} | {len(n['B']):2d} | {len(n['CB']):2d} | {len(n['C'] - n['B'])}")
