"""Round 3: defined look-alikes and two-factor rule with plain-image fallback.

Protocol: research/claude-round3-protocol-20261017.md. CPU only, USD 0.
  --mode calibrate  fits and freezes (tau1, tau2, tauF, PSNR cutoff) on already-consulted step-2b data.
  --mode evaluate   applies the frozen values to a new cohort laid out exactly like step 2b.
"""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import glob
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
import claude_two_factor_instance as tf  # noqa: E402  (Features, siblings helpers, paths)
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402

D1_ONLY_TAU = 0.586548254817741
ROUND2 = (0.0594367, 0.98)
MODELS, STRENGTHS, SEEDS = ("sd15", "sd21"), (0.1, 0.2, 0.4), (12, 13, 14)


def latest(pattern):
    hits = sorted(glob.glob(str(pattern)), key=lambda p: int(re.search(r"attempt(\d+)", p).group(1)) if "attempt" in p else 0)
    return hits[-1] if hits else None


class Cohort:
    def __init__(self, fresh, canon, sids, near, t4, sib_seeds, seeds=SEEDS):
        self.fresh, self.canon, self.sids, self.near, self.t4, self.sib_seeds = Path(fresh), Path(canon), sids, near, t4, sib_seeds
        self.seeds = tuple(seeds)

    def record(self, sid):
        return latest(self.fresh / str(sid) / "supplier-attempt*" / "F5-bootstrap.png")

    def suspects(self, sid):
        out = [("clean", None, None, "C0", str(self.canon / f"coco-{sid}-rgb512.png")), ("clean", None, None, "C1", self.record(sid))]
        for m in MODELS:
            for s in STRENGTHS:
                for seed in self.seeds:
                    for arm, tag in (("C1", "f5-r2"), ("C0", "C0")):
                        out.append((m, s, seed, arm, latest(self.fresh / f"{m}-{sid}-{s}-{seed}-{tag}-attempt*.png")))
        return out


def grey(path_or_img):
    im = path_or_img if isinstance(path_or_img, Image.Image) else Image.open(path_or_img)
    return np.asarray(im.convert("L"), dtype=np.float64)


def psnr(a, b):
    mse = float(np.mean((grey(a) - grey(b)) ** 2))
    return float("inf") if mse == 0 else 10 * np.log10(255.0 ** 2 / mse)


def feats(F, key, image=None):
    return F.get(key, image) if image is not None else F.get(key)


def score(F, q, r, qi=None, ri=None):
    x, y = feats(F, q, qi), feats(F, r, ri)
    return dict(d1=tf.cos(x["D1"], y["D1"]), b1=tf.cos(x["B1"], y["B1"]))


def rule(p, t1, t2, tF):
    if p.get("missing") or p.get("b1") is None:
        return False
    if p.get("d1") is None:
        return tF is not None and p["b1"] >= tF
    return p["d1"] >= t1 and p["b1"] >= t2


def build(F, C):
    pos, neg, near = [], [], []
    for sid in C.sids:
        rec = C.record(sid)
        for (m, s, seed, arm, p) in C.suspects(sid):
            row = dict(source=sid, model=m, strength=s, seed=seed, arm=arm, path=p)
            row.update(score(F, p, rec) if p and rec else dict(missing=True))
            if p and rec and arm == "C1" and m != "clean":
                row["psnr"] = psnr(p, rec)
            pos.append(row)
    for j in C.sids:
        for (m, s, seed, arm, p) in C.suspects(j):
            for i in C.sids:
                if i != j:
                    rec = C.record(i)
                    neg.append(dict(family="wrong_source", cluster=f"source:{j}", **(score(F, p, rec) if p and rec else dict(missing=True))))
    for (p, donor) in C.t4:
        rec = C.record(donor)
        neg.append(dict(family="T4", cluster=f"source:{donor}", path=p, **(score(F, p, rec) if rec else dict(missing=True))))
    for nid in C.near:
        a, b = C.canon / f"{nid}-0-rgb512.png", C.canon / f"{nid}-1-rgb512.png"
        if a.exists() and b.exists():
            near.append(dict(family="look_alike", cluster=f"near:{nid}", id=nid, psnr=psnr(b, a), **score(F, str(b), str(a))))
        else:
            near.append(dict(family="look_alike", cluster=f"near:{nid}", id=nid, missing=True))
    for seed in C.sib_seeds:
        ims = [Image.fromarray(np.clip(np.asarray(tf.scene(seed, 512, 512, 12.0, d)), 0, 255).astype(np.uint8)).convert("RGB") for d in (11, 12)]
        neg.append(dict(family="synthetic_sibling", cluster=f"sib:{seed}", psnr=psnr(ims[1], ims[0]),
                        **score(F, f"sib{seed}-12", f"sib{seed}-11", ims[1], ims[0])))
    return pos, neg, near


def majority(rows, ok):
    by = defaultdict(list)
    for r in rows:
        by[r["source"]].append(bool(ok(r)))
    return sum(sum(v) >= 2 for v in by.values()), len(by)


def cell_rows(pos, m, s):
    return [r for r in pos if r["arm"] == "C1" and r["model"] == m and r["strength"] == s]


def classify(near, cut):
    return [dict(r, different=(not r.get("missing")) and r["psnr"] < cut) for r in near]


def fit(pos, neg, near_cls):
    negs = neg + [r for r in near_cls if r["different"]]
    grid = [round(0.50 + 0.01 * k, 3) for k in range(30)] + [round(0.80 + 0.005 * k, 3) for k in range(40)]
    best = None
    for t2 in grid:
        passing = [r["d1"] for r in negs if not r.get("missing") and r.get("d1") is not None and r["b1"] is not None and r["b1"] >= t2]
        t1 = max(float(np.nextafter(max(passing), np.inf)) if passing else tf.SCREEN_TAU, tf.SCREEN_TAU)
        abst = [r["b1"] for r in negs if not r.get("missing") and r.get("d1") is None and r.get("b1") is not None]
        tF = max(t2, float(np.nextafter(max(abst), np.inf)) if abst else t2)
        ok = lambda r: rule(r, t1, t2, tF)
        s2 = sum(majority(cell_rows(pos, m, 0.2), ok)[0] for m in MODELS)
        s4 = sum(majority(cell_rows(pos, m, 0.4), ok)[0] for m in MODELS)
        key = (s2, s4, t2)
        if best is None or key > best[0]:
            best = (key, t1, t2, tF)
    # Calibration amendment (before any round-3 evaluation image existed): the fallback has no D1 check,
    # so give it the largest margin that keeps the maximal strength-.2 calibration acceptance.
    (key, t1, t2, tF) = best
    for cand in sorted(x for x in grid if x > tF):
        ok = lambda r, c=cand: rule(r, t1, t2, c)
        if sum(majority(cell_rows(pos, m, 0.2), ok)[0] for m in MODELS) == key[0] and not any(ok(r) for r in negs):
            tF = cand
        else:
            break
    s4 = sum(majority(cell_rows(pos, m, 0.4), lambda r: rule(r, t1, t2, tF))[0] for m in MODELS)
    return ((key[0], s4, t2), t1, t2, tF)


def report(pos, neg, near_cls, rules, pointer):
    out = {}
    for name, ok in rules.items():
        cells = {}
        for m in MODELS:
            for s in STRENGTHS:
                rows = cell_rows(pos, m, s)
                c = dict(seed_accept=sum(ok(r) for r in rows), seeds=len(rows), source_majority=majority(rows, ok)[0],
                         sources=majority(rows, ok)[1], d1_abstain_seeds=sum(r.get("d1") is None and not r.get("missing") for r in rows),
                         missing=sum(bool(r.get("missing")) for r in rows))
                if pointer is not None:
                    j = lambda r: ok(r) and pointer.get((r["source"], m, s, r["seed"]), False)
                    c.update(F_R_seed=sum(j(r) for r in rows), F_R_source_majority=majority(rows, j)[0],
                             pointer_unknown=sum((r["source"], m, s, r["seed"]) not in pointer for r in rows))
                cells[f"{m}/{s}"] = c
        fam = {}
        for r in neg + near_cls:
            f = r["family"] if r["family"] != "look_alike" else ("look_alike_different" if r.get("different") else "look_alike_ambiguous")
            e = fam.setdefault(f, dict(n=0, missing=0, d1_abstain=0, accepts=0, accepted_clusters=[]))
            e["n"] += 1
            e["missing"] += bool(r.get("missing"))
            e["d1_abstain"] += (not r.get("missing")) and r.get("d1") is None
            if ok(r):
                e["accepts"] += 1
                e["accepted_clusters"].append(r["cluster"])
        out[name] = dict(cells=cells, negatives=fam)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode", choices=("calibrate", "evaluate"), required=True)
    ap.add_argument("--frozen", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--fresh-dir", type=Path)
    ap.add_argument("--canonical-dir", type=Path)
    ap.add_argument("--t4-glob", action="append", default=[])
    ap.add_argument("--index", type=Path, action="append", default=[])
    ap.add_argument("--pointer-scores", type=Path)
    ap.add_argument("--sources", type=int, nargs="*")
    ap.add_argument("--near", nargs="*")
    # Defaults reproduce round 3 exactly; the approved held-out plan passes --seeds 15 16 17 --sibling-seeds 21..32.
    ap.add_argument("--seeds", type=int, nargs=3, default=list(SEEDS))
    ap.add_argument("--sibling-seeds", type=int, nargs="+", default=None)
    a = ap.parse_args()
    a.output_dir.mkdir(parents=True, exist_ok=False)
    tick = time.monotonic()
    res = dict(commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=tf.ROOT, text=True).strip(), command=sys.argv,
               started_at_utc=datetime.now(timezone.utc).isoformat(), mode=a.mode, usd=0, device="cpu",
               protocol="research/claude-round3-protocol-20261017.md")

    def t4_list(globs):
        out = []
        for g in globs:
            for p in sorted(glob.glob(g)):
                mm = re.search(r"T4-[a-z]+-(\d+)-(\d+)-([0-9.]+)\.png$", p)
                if mm:
                    out.append((p, int(mm.group(1))))
        return out

    if a.mode == "calibrate":
        sids = sorted(int(p.name) for p in tf.FRESH.iterdir() if p.is_dir() and p.name.isdigit())
        near = sorted({mm.group(1) for mm in (re.match(r"(tos-[0-9a-z_]+)-[01]-rgb512\.png$", p.name) for p in tf.CANON.iterdir()) if mm})
        C = Cohort(tf.FRESH, tf.CANON, sids, near,
                   t4_list([str(tf.AN1 / "images" / "T4-calibration-*.png"), str(tf.AN2 / "images" / "T4-evaluation-*.png")]), range(1, 7))
        F = tf.Features([tf.AN2 / "descriptor-index-calibration.json", tf.AN2 / "descriptor-index-evaluation.json"])
        pos, neg, near_rows = build(F, C)
        p2 = [r["psnr"] for r in pos if r["arm"] == "C1" and r["strength"] == 0.2 and "psnr" in r]
        p4 = [r["psnr"] for r in pos if r["arm"] == "C1" and r["strength"] == 0.4 and "psnr" in r]
        cut, cut_med = float(np.percentile(p2, 5)), float(np.median(p2))
        near_cls = classify(near_rows, cut)
        (key, t1, t2, tF) = fit(pos, neg, near_cls)
        frozen = dict(tau1_d1=t1, tau2_b1=t2, tauF_b1_fallback=t2 if tF is None else tF, psnr_cutoff_primary=cut,
                      psnr_cutoff_secondary_median=cut_med, psnr_04_p5=float(np.percentile(p4, 5)),
                      calibration_score_02=key[0], calibration_score_04=key[1], calibration_sources=sids, calibration_look_alikes=near,
                      look_alikes_different=[r["id"] for r in near_cls if r["different"]],
                      look_alikes_ambiguous=[r["id"] for r in near_cls if not r["different"]])
        a.frozen.write_text(json.dumps(frozen, indent=2) + "\n")
        rules = {"round3": lambda r: rule(r, t1, t2, tF), "round2_no_fallback": lambda r: rule(r, *ROUND2, None),
                 "d1_only_587": lambda r: rule(r, D1_ONLY_TAU, -2.0, None)}
        res.update(frozen=frozen, summary=report(pos, neg, near_cls, rules, None),
                   look_alike_psnr={r["id"]: r.get("psnr") for r in near_cls})
    else:
        fr = json.loads(a.frozen.read_text())
        t1, t2, tF = fr["tau1_d1"], fr["tau2_b1"], fr["tauF_b1_fallback"]
        C = Cohort(a.fresh_dir, a.canonical_dir, a.sources, a.near, t4_list(a.t4_glob),
                   a.sibling_seeds if a.sibling_seeds is not None else range(7, 13), seeds=a.seeds)
        res.update(regeneration_seeds=list(a.seeds), sibling_seeds=list(C.sib_seeds))
        F = tf.Features(a.index)
        pos, neg, near_rows = build(F, C)
        near_cls = classify(near_rows, fr["psnr_cutoff_primary"])
        near_sec = classify(near_rows, fr["psnr_cutoff_secondary_median"])
        pointer = None
        if a.pointer_scores and a.pointer_scores.exists():
            pointer = {}
            for c in json.loads(a.pointer_scores.read_text()).get("positives_and_C0", []):
                mm = re.match(r"(sd15|sd21):(\d+):([0-9.]+):(\d+):f5-r2$", str(c.get("id", "")))
                if mm and isinstance(c.get("pointer"), dict):
                    pointer[(int(mm.group(2)), mm.group(1), float(mm.group(3)), int(mm.group(4)))] = bool(c["pointer"].get("recovered"))
        rules = {"round3": lambda r: rule(r, t1, t2, tF), "round2_no_fallback": lambda r: rule(r, *ROUND2, None),
                 "d1_only_587": lambda r: rule(r, D1_ONLY_TAU, -2.0, None)}
        summ = report(pos, neg, near_cls, rules, pointer)
        r3 = summ["round3"]
        fa = sum(v["accepts"] for k, v in r3["negatives"].items() if k != "look_alike_ambiguous")
        key = "F_R_source_majority" if pointer is not None else "source_majority"
        passed = all(r3["cells"][f"{m}/0.2"][key] >= int(np.ceil(0.9 * len(a.sources))) for m in MODELS) and fa == 0
        # Approved held-out plan view (user decision 2026-10-17): the distance definition applies to synthetic
        # look-alikes too; ambiguous pairs (real or synthetic) are reported, never scored. E1 uses the one-sided
        # 95% Clopper-Pearson lower bound >= .85 at strength .2 on each regenerator; E2 needs zero false accepts
        # on non-ambiguous negatives. E3 (attribution scenario) is computed by the enrollment analysis.
        from scipy.stats import beta as _beta
        cut = fr["psnr_cutoff_primary"]
        neg_plan = [dict(r, family=("synthetic_different" if r["psnr"] < cut else "synthetic_ambiguous"))
                    if r["family"] == "synthetic_sibling" else r for r in neg]
        plan = report(pos, neg_plan, near_cls, {"round3": rules["round3"]}, pointer)["round3"]
        n = len(a.sources)
        e1 = {}
        for m in MODELS:
            k = plan["cells"][f"{m}/0.2"][key]
            lb = float(_beta.ppf(0.05, k, n - k + 1)) if k > 0 else 0.0
            e1[m] = dict(successes=k, n=n, clopper_pearson_lower_95=lb, pass_=lb >= 0.85)
        e2 = {f: v["accepts"] for f, v in plan["negatives"].items() if not f.endswith("_ambiguous")}
        res.update(plan_view=dict(negatives=plan["negatives"], E1=e1, E2_false_accepts_by_family=e2,
                                  E2_total=sum(e2.values()), E1_E2_pass=all(v["pass_"] for v in e1.values()) and sum(e2.values()) == 0,
                                  synthetic_psnr={r["cluster"]: r["psnr"] for r in neg if r["family"] == "synthetic_sibling"}))
        res.update(frozen=fr, evaluation_sources=a.sources, evaluation_look_alikes=a.near, pointer_rows=None if pointer is None else len(pointer),
                   summary=summ, secondary_definition=report(pos, neg, near_sec, {"round3": rules["round3"]}, pointer),
                   look_alike_psnr={r["id"]: r.get("psnr") for r in near_cls},
                   development_pass=passed, pass_basis=key, round3_false_accepts_excluding_ambiguous=fa)
    res["d1_computed_locally"] = F.computed_d1
    res["duration_seconds"] = time.monotonic() - tick
    res["outcome"] = "completed"
    (a.output_dir / "run.json").write_text(json.dumps(res, indent=2, default=list) + "\n")
    print(json.dumps({k: res[k] for k in res if k in ("mode", "duration_seconds", "development_pass", "pass_basis",
                                                      "round3_false_accepts_excluding_ambiguous", "d1_computed_locally")}, indent=1))
    if a.mode == "calibrate":
        print("FROZEN", json.dumps({k: v for k, v in res["frozen"].items() if not isinstance(v, list)}))
        print("different:", res["frozen"]["look_alikes_different"]); print("ambiguous:", res["frozen"]["look_alikes_ambiguous"])
    for name, s in res["summary"].items():
        print(f"\n== {name}")
        for c, v in s["cells"].items():
            print(f"  {c}: {v}")
        for f, v in s["negatives"].items():
            print(f"  NEG {f}: n={v['n']} accepts={v['accepts']} missing={v['missing']} d1_abstain={v['d1_abstain']} {v['accepted_clusters'][:6]}")


if __name__ == "__main__":
    main()
