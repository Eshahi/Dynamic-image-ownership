"""DESIGN-half exploration of the decoded-word rule that keeps the production corrected distance.

Rule: accept a tier when its decoded word scores at least t and its corrected Hamming distance to the
suspect's own code is at most 6, the frozen limit. Only t changes. The acceptance set for a score of
at least t sits inside the Hamming ball of radius floor(32e + 6(1-2e)), so the ball sets the budget.
EVALUATE is not read here.
"""
import itertools
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

RD = Path(r"C:\Users\Soroush\.codex\worktrees\codex-f5-components\research\f5-components-20261101")
sys.path.insert(0, str(RD / "judge"))
from loss_budget import CELLS, OWNER, load  # noqa: E402

WRONG = "qim-pilot-owner-beta"
LIMIT = 6


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


def r_eff(s, limit=LIMIT):
    e = err(s)
    return 32 * e + limit * (1 - 2 * e)


def corrected(d, s):
    e = err(s)
    return min(32.0, max(0.0, (d - 32 * e) / (1 - 2 * e)))


def ball(r):
    return sum(math.comb(32, j) for j in range(r + 1))


def fixed_point(alpha):
    t = 8.3
    for cand in [x / 1000 for x in range(6000, 8500)]:
        if thr(ball(int(r_eff(cand))), alpha) <= cand:
            return cand, int(r_eff(cand)), thr(ball(int(r_eff(cand))), alpha)
    return t, None, None


T1, R1, B1 = fixed_point(1e-6)
T2, R2, B2 = fixed_point(5e-7)
T3, R3, B3 = fixed_point(1e-6 / 3)
print(f"fixed point alpha      t*={T1:.3f} ball r={R1} ball threshold {B1:.4f}")
print(f"fixed point alpha/2    t*={T2:.3f} ball r={R2} ball threshold {B2:.4f}")
print(f"fixed point alpha/3    t*={T3:.3f} ball r={R3} ball threshold {B3:.4f}; decoded 2^32 at alpha/3 {thr(2**32, 1e-6/3):.4f}")
T = T2


def ham(a, b):
    return bin(int(a, 16) ^ int(b, 16)).count("1")


def bd(res, own, t=T):
    d = ham(res["decoded_code"], own)
    return res["decoded_score"] >= t and corrected(d, res["decoded_score"]) <= LIMIT


rows = load()
sources = sorted({x["source_id"] for x in rows.values() if x.get("channel") == "clean"})
design = {s for j, s in enumerate(sources) if j % 2 == 0}


def calls(arm, chan, strength, role):
    for x in rows.values():
        if x.get("channel") != chan or x.get("strength") != strength or x.get("status") != "ok" or x["source_id"] not in design:
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


ALL_CELLS = list(CELLS)
for arm in ("f5-r2", "v5-r3"):
    print(f"\n=== {arm}, DESIGN /30 source majority, t={T:.3f} (alpha/2 per tier), corrected distance <= {LIMIT}")
    print("cell     |  C | BDs | C or BDs | BDi | BDs or BDi | C or BDs or BDi | C-sources lost by BDs|BDi")
    for chan, strength in ALL_CELLS:
        c = defaultdict(Counter)
        for x, call in calls(arm, chan, strength, "marked"):
            raw, e = call["raw"], call["endpoints"]
            s, i = raw["semantic"], raw["instance"]
            src = x["source_id"]
            C = bool(e.get("C"))
            a, b = bd(s, raw["semantic_code"]), bd(i, raw["perceptual_hash"])
            c["C"][src] += C
            c["BDs"][src] += a
            c["BDi"][src] += b
            c["C|BDs"][src] += C or a
            c["BD"][src] += a or b
            c["ALL"][src] += C or a or b
        n = {k: {s for s, v in c[k].items() if v >= 2} for k in c}
        g = lambda k: len(n.get(k, ()))
        print(f"{chan}-{strength:<4}| {g('C'):2d} | {g('BDs'):3d} | {g('C|BDs'):8d} | {g('BDi'):3d} | {g('BD'):10d} | {g('ALL'):15d} | {len(n.get('C', set()) - n.get('BD', set())):2d}")
    neg = Counter()
    for chan, strength in ALL_CELLS:
        for role in ("C0", "wrong"):
            for x, call in calls(arm, chan, strength, role):
                raw = call["raw"]
                neg[role, "calls"] += 1
                neg[role, "BDs"] += bd(raw["semantic"], raw["semantic_code"])
                neg[role, "BDi"] += bd(raw["instance"], raw["perceptual_hash"])
    print("negatives:", {f"{a}|{b}": v for (a, b), v in sorted(neg.items())})

print("\n=== T4 pixel panel, DESIGN recipients")
for method in ("f5-r2", "v5-r3"):
    tally = Counter()
    for path in sorted((RD / "results/wp4-pixels").glob(f"{method}-*.jsonl")):
        for line in open(path, encoding="utf-8"):
            row = json.loads(line)
            if row.get("panel") != "T4" or row.get("result_status") != "ok" or row["split"] != "DESIGN":
                continue
            for call in row["calls"]:
                raw = call.get("raw") or {}
                if not raw:
                    continue
                k = (call["role"],)
                tally[k + ("calls",)] += 1
                a = bd(raw["semantic"], raw["semantic_code"])
                b = bd(raw["instance"], raw["perceptual_hash"])
                tally[k + ("BDs",)] += a
                tally[k + ("BDi",)] += b
                tally[k + ("frozen C-like both read",)] += bool(raw["semantic"].get("content_match") and raw["semantic"].get("read"))
                if a or b:
                    print("   accept", method, row["id"], call["role"], "s", round(raw["semantic"]["decoded_score"], 2), "i", round(raw["instance"]["decoded_score"], 2))
    print(" ", method, {"|".join(k): v for k, v in sorted(tally.items())})

print("\n=== collision floor from saved clean codes, ordered pairs of DESIGN sources")
codes = {}
for x in rows.values():
    if x.get("channel") == "clean" and x.get("arm") == "unmarked" and x.get("status") == "ok" and x["source_id"] in design:
        call = x["detections"].get("f5-r2", {}).get(OWNER)
        if call and call.get("status") == "ok":
            codes[x["source_id"]] = (call["raw"]["semantic_code"], call["raw"]["perceptual_hash"])
print("  sources with clean codes", len(codes))
pairs = list(itertools.combinations(sorted(codes), 2))
for name, idx in (("q", 0), ("h", 1)):
    ds = [ham(codes[a][idx], codes[b][idx]) for a, b in pairs]
    print(f"  {name}: pairs {len(ds)} mean {sum(ds) / len(ds):.2f} min {min(ds)}", {f"<={r}": sum(d <= r for d in ds) for r in (4, 6, 8, 9, 10, 12)})
print("  uniform 32-bit share", {f"<={r}": round(ball(r) / 2**32, 6) for r in (4, 6, 8, 9, 10, 12)})
