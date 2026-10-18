"""Independent check of the held-out registry run (Claude, 2026-10-18). Reads only frozen outputs; writes nothing there."""
import json, sys, math
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
from PIL import Image

RUN = Path(r"W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\registry-package\artifacts\M1b-test\registry-div2k300-confirm-01")
OUT = Path(sys.argv[1])
rows = {}
for line in (RUN / "outputs/journal.jsonl").read_text(encoding="utf-8").splitlines():
    if line.strip():
        r = json.loads(line); rows[r["id"]] = r
ep = json.loads((RUN / "metrics/endpoints.json").read_text())
sc = json.loads(next((RUN / "metrics").glob("frozen-scorer-*/scoring/run.json")).read_text())
fr = sc["frozen"]; t1, t2, tF, cut = fr["tau1_d1"], fr["tau2_b1"], fr["tauF_b1_fallback"], fr["psnr_cutoff_primary"]
ALPHA, BETA = "qim-pilot-owner-alpha", "qim-pilot-owner-beta"
lines = []
P = lambda *a: lines.append(" ".join(str(x) for x in a))
P("frozen", dict(t1=t1, t2=t2, tF=tF, cut=cut))
P("journal rows", len(rows), "outcomes", dict(Counter(r.get("outcome") for r in rows.values())))

def unit_ok(u): return rows.get(u, {}).get("outcome") == "completed"
memo = {}
def feat(u):
    if u in memo: return memo[u]
    res = None
    r, d = rows.get(u, {}), rows.get("descriptor:" + u, {})
    if r.get("outcome") == "completed" and r.get("image") and d.get("outcome") == "completed" and d.get("cache"):
        im = Image.open(r["image"]).convert("RGB"); g = im.convert("L")
        b1 = np.asarray(g.resize((32, 32), Image.BOX), dtype=np.float64).ravel(); b1 = b1 - b1.mean(); b1 /= np.linalg.norm(b1)
        with np.load(d["cache"], allow_pickle=False) as z: D = np.asarray(z["D1"], dtype=np.float64)
        n = np.linalg.norm(D) if D.size else 0
        res = dict(D1=(D / n) if (D.size and np.isfinite(n) and n > 0) else None, B1=b1, grey=np.asarray(g, dtype=np.float64))
    memo[u] = res
    return res
def pair(q, r):
    a, b = feat(q), feat(r)
    if a is None or b is None: return None
    return dict(d1=None if a["D1"] is None or b["D1"] is None else float(a["D1"] @ b["D1"]), b1=float(a["B1"] @ b["B1"]))
def rule(p):
    if p is None: return False
    if p["d1"] is None: return p["b1"] >= tF
    return p["d1"] >= t1 and p["b1"] >= t2
def psnr(u, v):
    mse = float(np.mean((feat(u)["grey"] - feat(v)["grey"]) ** 2)); return 10 * math.log10(255 ** 2 / mse)

sids = sorted({r["source_id"] for k, r in rows.items() if k.startswith("canon:")})
P("sources", len(sids))
# ---- E1 independent
from scipy.stats import beta
for m in ("sd15", "sd21"):
    k = 0; gap = 0; fails = []
    for sid in sids:
        ok = 0
        for seed in (15, 16, 17):
            u = f"t3:{m}:{sid}:0.2:{seed}:C1"
            ptr = rows.get(f"native:{u}:{ALPHA}", {}).get("pointer_recovered") is True
            ok += bool(ptr and rule(pair(u, f"embed:{sid}")))
        k += ok >= 2
        if ok < 2: fails.append(sid)
    lb = beta.ppf(0.05, k, len(sids) - k + 1)
    P(f"E1 {m}: {k}/{len(sids)} CP95 lower {lb:.4f} pass={lb >= .85} | frozen {ep['E1'][m]['successes']} | misses {fails}")
# ---- look-alikes
near = sorted({k.split(":")[1] for k in rows if k.startswith("near:")})
P("\nlook-alike pairs", len(near))
la = []
for pid in near:
    a, b = f"near:{pid}:0", f"near:{pid}:1"
    p = pair(b, a)
    if p is None: la.append((pid, None, None, None, None)); continue
    la.append((pid, psnr(b, a), p["d1"], p["b1"], rule(p)))
for pid, ps, d1, b1, acc in sorted(la, key=lambda x: (x[1] is None, x[1])):
    tag = "DIFFERENT" if ps is not None and ps < cut else "ambiguous"
    P(f"  {pid:22s} psnr={ps if ps is None else round(ps,3)} d1={d1 if d1 is None else round(d1,4)} b1={b1 if b1 is None else round(b1,4)} {tag} {'ACCEPT' if acc else ''}")
dif = [x for x in la if x[1] is not None and x[1] < cut]
P(f"different n={len(dif)} accepts={sum(x[4] for x in dif)}; ambiguous n={len(la)-len(dif)} accepts={sum(bool(x[4]) for x in la if x not in dif)}")
P("frozen look_alike_psnr agree:", all(abs((sc['look_alike_psnr'].get(pid) or 0) - (ps or 0)) < 1e-6 for pid, ps, *_ in la if ps is not None))
# ---- E3 complete-case
P("\nE3 row example:", json.dumps(ep["E3"]["rows"][0])[:900])
def evaluable(e):
    sid, (model, strength, kind) = e["source_id"], e["cell"].split("/")
    q = f"t3:{model}:{sid}:{strength}:15:C1" if kind == "exact_copy" else f"scenario:{model}:{sid}:{strength}"
    beta_unit = f"t3:{model}:{sid}:{strength}:15:C1"
    causes = []
    if feat(q) is None or not all(unit_ok(f"native:{q}:{o}") for o in (ALPHA, BETA)): causes.append("query missing")
    if feat(f"embed:{sid}") is None or (rows.get(f"embed:{sid}", {}).get("payload") or {}).get("q") is None: causes.append("owner record missing (F5 could not mark)")
    nb = rows.get(f"native:{beta_unit}:{BETA}", {})
    if feat(beta_unit) is None or nb.get("outcome") != "completed" or (nb.get("detection") or {}).get("semantic_code") is None: causes.append("attacker record missing")
    return not causes, causes
tot = Counter(); wrong = Counter(); attr = defaultdict(Counter); fp = defaultdict(Counter); cause = Counter(); wrong_rows = []
for e in ep["E3"]["rows"]:
    ok, cs = evaluable(e)
    c = e["cell"]; tot[(c, ok)] += 1
    if not ok:
        cause[(c, "; ".join(cs))] += 1; continue
    pr = e["arms"]["pointer_registry"]
    attr[c][str(pr.get("attribution"))] += 1
    fp[c][str(e["arms"]["fingerprint_only"].get("attribution"))] += 1
    if pr.get("wrong_owner_present"): wrong[c] += 1; wrong_rows.append((c, e["source_id"], pr))
for c in sorted({e["cell"] for e in ep["E3"]["rows"]}):
    P(f"E3 {c}: evaluable {tot[(c, True)]}/{tot[(c, True)] + tot[(c, False)]} wrong-owner {wrong[c]} | pointer arm {dict(attr[c])} | fingerprint-only {dict(fp[c])}")
for (c, cs), n in sorted(cause.items()): P(f"   not evaluable {c}: {n} x {cs}")
P("E3 wrong-owner total among evaluable:", sum(wrong.values()))
for w in wrong_rows[:10]: P("   WRONG", w)
OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
