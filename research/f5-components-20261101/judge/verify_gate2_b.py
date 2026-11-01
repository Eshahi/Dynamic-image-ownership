"""Judge exploration on the DESIGN half only: which route carries the second-tier gain, and does a
decoded-word-in-ball rule keep binding? EVALUATE is left for a kill rule written first."""
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median

RD = Path(r"C:\Users\Soroush\.codex\worktrees\codex-f5-components\research\f5-components-20261101")
sys.path.insert(0, str(RD / "judge"))
from loss_budget import CELLS, OWNER, load  # noqa: E402

WRONG = "qim-pilot-owner-beta"


def phi_bar(z):
    return 0.5 * math.erfc(z / math.sqrt(2))


def thr(mult, alpha=1e-6, c=3.1787):
    lo, hi = 0.0, 40.0
    for _ in range(200):
        m = (lo + hi) / 2
        if c * mult * phi_bar(m) > alpha:
            lo = m
        else:
            hi = m
    return hi


def ball_t(r):
    return thr(sum(math.comb(32, j) for j in range(r + 1)))


def ham(a, b):
    return bin(int(a, 16) ^ int(b, 16)).count("1")


rows = load()
sources = sorted({x["source_id"] for x in rows.values() if x.get("channel") == "clean"})
assert len(sources) == 60
design = {s for j, s in enumerate(sources) if j % 2 == 0}
RADII = (6, 8, 10, 12)
T = {r: ball_t(r) for r in RADII}
print("ball thresholds", {r: round(v, 4) for r, v in T.items()})


def calls(arm, chan, strength, role):
    for x in rows.values():
        if x.get("channel") != chan or x.get("strength") != strength or x.get("status") != "ok":
            continue
        if x["source_id"] not in design:
            continue
        if role == "marked" and x.get("arm") == arm:
            call = x["detections"].get(arm, {}).get(OWNER)
        elif role == "wrong" and x.get("arm") == arm:
            call = x["detections"].get(arm, {}).get(WRONG)
        elif role == "C0" and x.get("arm") == "unmarked":
            call = x["detections"].get(arm, {}).get(OWNER)
        else:
            continue
        if call and call.get("status") == "ok":
            yield x, call


for arm in ("f5-r2", "v5-r3"):
    print(f"\n=== {arm}, DESIGN /30 source majority")
    print("cell | C | inst read+ok | inst recomputed-only ok | C or inst read+ok | BDs r6 r8 r10 r12 | C or BDs r6 r8 r10 r12 | BDi r6 r8 r10 r12 | C or BDs10 or BDi10 | med d_s(all/near thr) med d_i")
    for chan, strength in CELLS:
        c = defaultdict(Counter)
        ds, di = [], []
        for x, call in calls(arm, chan, strength, "marked"):
            raw, e = call["raw"], call["endpoints"]
            s, i = raw["semantic"], raw["instance"]
            src = x["source_id"]
            C = bool(e.get("C"))
            ok = bool(i.get("found")) and bool(i.get("content_match"))
            iread = ok and bool(i.get("read"))
            irec = ok and not bool(i.get("read"))
            d_s = ham(s["decoded_code"], raw["semantic_code"])
            d_i = ham(i["decoded_code"], raw["perceptual_hash"])
            ds.append(d_s)
            di.append(d_i)
            c["C"][src] += C
            c["iread"][src] += iread
            c["irec"][src] += irec
            c["C|iread"][src] += C or iread
            for r in RADII:
                bs = s["decoded_score"] >= T[r] and d_s <= r
                bi = i["decoded_score"] >= T[r] and d_i <= r
                c[f"bs{r}"][src] += bs
                c[f"C|bs{r}"][src] += C or bs
                c[f"bi{r}"][src] += bi
            c["C|bs10|bi10"][src] += C or (s["decoded_score"] >= T[10] and d_s <= 10) or (i["decoded_score"] >= T[10] and d_i <= 10)
        n = {k: sum(v >= 2 for v in c[k].values()) for k in c}
        g = lambda k: n.get(k, 0)
        print(f"{chan}-{strength:<4}| {g('C'):2d} | {g('iread'):2d} | {g('irec'):2d} | {g('C|iread'):2d} | "
              f"{g('bs6'):2d} {g('bs8'):2d} {g('bs10'):2d} {g('bs12'):2d} | {g('C|bs6'):2d} {g('C|bs8'):2d} {g('C|bs10'):2d} {g('C|bs12'):2d} | "
              f"{g('bi6'):2d} {g('bi8'):2d} {g('bi10'):2d} {g('bi12'):2d} | {g('C|bs10|bi10'):2d} | {median(ds) if ds else None} {median(di) if di else None}")
    neg = Counter()
    for chan, strength in CELLS:
        for role in ("C0", "wrong"):
            for x, call in calls(arm, chan, strength, role):
                raw = call["raw"]
                s, i = raw["semantic"], raw["instance"]
                d_s = ham(s["decoded_code"], raw["semantic_code"])
                d_i = ham(i["decoded_code"], raw["perceptual_hash"])
                neg[role, "calls"] += 1
                for r in RADII:
                    neg[role, f"bs{r}"] += s["decoded_score"] >= T[r] and d_s <= r
                    neg[role, f"bi{r}"] += i["decoded_score"] >= T[r] and d_i <= r
    print("negatives DESIGN:", {f"{a}|{b}": v for (a, b), v in sorted(neg.items())})

print("\n=== T4 mechanism, DESIGN recipients only, F5: recomputed/decoded vs share of shared segments")
for path in sorted((RD / "results/wp4-pixels").glob("f5-r2-*.jsonl")):
    for line in open(path, encoding="utf-8"):
        row = json.loads(line)
        if row.get("panel") != "T4" or row.get("result_status") != "ok" or row["split"] != "DESIGN":
            continue
        for call in row["calls"]:
            if call["role"] != "marked":
                continue
            raw = call["raw"]
            i, s = raw["instance"], raw["semantic"]
            d_i = ham(i["decoded_code"], raw["perceptual_hash"])
            d_s = ham(s["decoded_code"], raw["semantic_code"])
            bi10 = i["decoded_score"] >= T[10] and d_i <= 10
            bs10 = s["decoded_score"] >= T[10] and d_s <= 10
            print(f"  {row['id']:34} inst dec {i['decoded_score']:6.2f} rec {i['recomputed_score']:5.2f} ratio {i['recomputed_score'] / max(i['decoded_score'], 1e-9):5.2f} d_i {d_i:2d} expected {(32 - 2 * d_i * 0.5) / 32:4.2f} | sem dec {s['decoded_score']:5.2f} rec {s['recomputed_score']:5.2f} d_s {d_s:2d} | O {raw['outcome']:17} BDi10 {bi10} BDs10 {bs10}")

print("\n=== decoding error rate model at scores")
def expected_best(m):
    return m * 0.5 * (1 + math.erf(m / 2)) + math.exp(-m * m / 4) / math.sqrt(math.pi)
def err(s):
    t = s / math.sqrt(32)
    if t <= expected_best(0):
        return .5
    lo, hi = 0.0, 1e6
    for _ in range(80):
        mid = (lo + hi) / 2
        if expected_best(mid) / math.sqrt(1 + mid * mid / 10) < t:
            lo = mid
        else:
            hi = mid
    return .5 * math.erfc(lo / 2)
for s in (6.5, 7.0, 7.21, 7.5, 7.81, 8.26, 9, 10, 12):
    print(f"  score {s:5.2f} e={err(s):.3f} expected wrong bits {32 * err(s):4.1f}  hamming at corrected 6: {32 * err(s) + 6 * (1 - 2 * err(s)):4.1f}")
