"""Two-factor instance check (fine-detail D1 AND aligned layout B1) for the registry route.

Protocol: research/claude-two-factor-instance-protocol-20261017.md. CPU only.
  --calibrate  sets and freezes (tau1, tau2) from the calibration split only.
  --evaluate   applies the frozen thresholds to the untouched evaluation split.
"""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import glob
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import time

os.environ["CUDA_VISIBLE_DEVICES"] = ""
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]

import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity

from scripts import journal_fine_gaussian_instance as fine
from scripts import revised_watermark_v5 as v5
from scripts.watermark_synthetic import scene

BUILD = Path("W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build")
FRESH = BUILD / "dev-runs/20261016-registry-step2-fresh"
AN1 = BUILD / "dev-runs/20261016-registry-step2-fresh-analysis"
AN2 = BUILD / "dev-runs/20261016-registry-step2-fresh-analysis-r2"
CANON = BUILD / "assets/registry-fresh-20261016/canonical"
PROFILE_RUN = BUILD / "dev-runs/20261013-1636-fresh-e3-simplification/run.json"
SCREEN_TAU = 0.0594367
STRENGTHS = (0.1, 0.2, 0.4)
MODELS = ("sd15", "sd21")


def norm(v):
    v = np.asarray(v, dtype=np.float64)
    n = np.linalg.norm(v)
    return v / n if np.isfinite(n) and n > 0 and np.all(np.isfinite(v)) else None


class Features:
    def __init__(self, index_paths):
        self.cache = {}
        for p in index_paths:
            if Path(p).exists():
                for path, meta in json.loads(Path(p).read_text()).items():
                    self.cache[os.path.normcase(os.path.normpath(path))] = meta["cache"]
        _, self.key, self.config = v5._resolve(json.loads(PROFILE_RUN.read_text())["config"]["profile"], None)
        self.memo, self.computed_d1 = {}, 0

    def d1(self, path, image):
        hit = self.cache.get(os.path.normcase(os.path.normpath(str(path))))
        if hit:
            return norm(np.load(hit)["D1"])
        self.computed_d1 += 1
        f = fine.descriptor(v5.luminance_from_rgb(np.asarray(image).tolist()), self.key, self.config)
        return norm(f["vector"]) if f["vector"] is not None else None

    def get(self, path, image=None):
        k = str(path)
        if k not in self.memo:
            im = image if image is not None else Image.open(path).convert("RGB")
            g = im.convert("L")
            b1 = np.asarray(g.resize((32, 32), Image.BOX), dtype=np.float64).ravel()
            self.memo[k] = dict(D1=self.d1(path, im), B1=norm(b1 - b1.mean()),
                                g64=np.asarray(g.resize((64, 64), Image.BOX), dtype=np.float64))
        return self.memo[k]


def cos(a, b):
    return None if a is None or b is None else float(a @ b)


def pair(F, q, r):
    x, y = F.get(q[0], q[1]) if isinstance(q, tuple) else F.get(q), F.get(r[0], r[1]) if isinstance(r, tuple) else F.get(r)
    return dict(d1=cos(x["D1"], y["D1"]), b1=cos(x["B1"], y["B1"]),
                b2=float(structural_similarity(x["g64"], y["g64"], data_range=255)))


def accept(p, t1, t2):
    return p["d1"] is not None and p["b1"] is not None and p["d1"] >= t1 and p["b1"] >= t2


def siblings():
    out = []
    for seed in range(1, 7):
        ims = [Image.fromarray(np.clip(np.asarray(scene(seed, 512, 512, 12.0, d)), 0, 255).astype(np.uint8)).convert("RGB") for d in (11, 12)]
        out.append(((f"sib{seed}-11", ims[0]), (f"sib{seed}-12", ims[1])))
    return out


def latest(pattern):
    hits = sorted(glob.glob(str(pattern)), key=lambda p: int(re.search(r"attempt(\d+)", p).group(1)) if "attempt" in p else 0)
    return hits[-1] if hits else None


def record(sid):
    return latest(FRESH / str(sid) / "supplier-attempt*" / "F5-bootstrap.png")


def split_rows(sids, near_ids, t4_dir, t4_prefix):
    """Positive and negative pair lists for a split, built from files only."""
    pos, suspects = [], defaultdict(list)
    for sid in sids:
        suspects[sid] += [("clean", None, None, "C0", str(CANON / f"coco-{sid}-rgb512.png")), ("clean", None, None, "C1", record(sid))]
        for m in MODELS:
            for s in STRENGTHS:
                for seed in (12, 13, 14):
                    for arm, tag in (("C1", "f5-r2"), ("C0", "C0")):
                        p = latest(FRESH / f"{m}-{sid}-{s}-{seed}-{tag}-attempt*.png")
                        suspects[sid].append((m, s, seed, arm, p))
    for sid, rows in suspects.items():
        for (m, s, seed, arm, p) in rows:
            pos.append(dict(source=sid, model=m, strength=s, seed=seed, arm=arm, path=p))
    neg = []
    for j, rows in suspects.items():
        for (m, s, seed, arm, p) in rows:
            for i in sids:
                if i != j:
                    neg.append(dict(family="wrong_source", cluster=f"source:{j}", suspect=p, target=i, model=m, strength=s))
    for p in sorted(glob.glob(str(t4_dir / f"{t4_prefix}-*.png"))):
        d, r, scale = re.search(rf"{t4_prefix}-(\d+)-(\d+)-([0-9.]+)\.png$", p).groups()
        if int(d) in sids:
            neg.append(dict(family="T4", cluster=f"source:{d}", suspect=p, target=int(d), scale=scale))
    for nid in near_ids:
        neg.append(dict(family="real_near_duplicate", cluster=f"near:{nid}", suspect=str(CANON / f"{nid}-1-rgb512.png"),
                        target_path=str(CANON / f"{nid}-0-rgb512.png")))
    return pos, neg


def score_split(F, sids, near_ids, t4_dir, t4_prefix):
    pos, neg = split_rows(sids, near_ids, t4_dir, t4_prefix)
    for r in pos:
        r.update(pair(F, r["path"], record(r["source"])) if r["path"] else dict(d1=None, b1=None, b2=None, missing=True))
    for r in neg:
        tgt = r.get("target_path") or record(r["target"])
        r.update(pair(F, r["suspect"], tgt) if r["suspect"] else dict(d1=None, b1=None, b2=None, missing=True))
    for (a, b) in siblings():
        neg.append(dict(family="synthetic_sibling", cluster=a[0], **pair(F, b, a)))
    return pos, neg


def majority(rows, rule):
    by = defaultdict(list)
    for r in rows:
        by[r["source"]].append(rule(r))
    return sum(sum(v) >= 2 for v in by.values()), len(by)


def summarize(pos, neg, t1, t2, pointer=None):
    out = {}
    rules = {"two_factor": lambda r: accept(r, t1, t2), "d1_only_587": lambda r: r["d1"] is not None and r["d1"] >= 0.586548254817741}
    for name, rule in rules.items():
        cells = {}
        for m in MODELS:
            for s in STRENGTHS:
                rows = [r for r in pos if r["arm"] == "C1" and r["model"] == m and r["strength"] == s]
                k, n = majority(rows, rule)
                cell = dict(seed_accept=sum(rule(r) for r in rows), seeds=len(rows), source_majority=k, sources=n)
                if pointer is not None:
                    jr = lambda r: rule(r) and pointer.get((r["source"], m, s, r["seed"]), False)
                    cell["F_R_source_majority"] = majority(rows, jr)[0]
                    cell["F_R_seed"] = sum(jr(r) for r in rows)
                cells[f"{m}/{s}"] = cell
        fam = defaultdict(lambda: dict(n=0, false_accepts=0, clusters_with_fa=set(), missing_image=0, d1_abstain=0, max_d1=None, max_b1=None))
        for r in neg:
            f = fam[r["family"]]
            f["n"] += 1
            if r.get("missing"):
                f["missing_image"] += 1
            elif r.get("d1") is None:
                f["d1_abstain"] += 1
            if rule(r):
                f["false_accepts"] += 1; f["clusters_with_fa"].add(r["cluster"])
            for key, val in (("max_d1", r.get("d1")), ("max_b1", r.get("b1"))):
                if val is not None and (f[key] is None or val > f[key]):
                    f[key] = val
        out[name] = dict(cells=cells, negatives={k: {**v, "clusters_with_fa": sorted(v["clusters_with_fa"])} for k, v in fam.items()})
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode", choices=("calibrate", "evaluate"), required=True)
    ap.add_argument("--thresholds", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    a = ap.parse_args()
    a.output_dir.mkdir(parents=True, exist_ok=False)
    tick = time.monotonic()
    cal = json.loads((AN2 / "calibration-thresholds.json").read_text())
    cal_ids, cal_near = [int(x) for x in cal["source_ids"]], cal["near_duplicate_ids"]
    all_ids = sorted(int(p.name) for p in FRESH.iterdir() if p.is_dir() and p.name.isdigit())
    all_near = sorted({m.group(1) for m in (re.match(r"(tos-[0-9a-z_]+)-[01]-rgb512\.png$", p.name) for p in CANON.iterdir()) if m})
    F = Features([AN2 / "descriptor-index-calibration.json"] + ([AN2 / "descriptor-index-evaluation.json"] if a.mode == "evaluate" else []))
    result = dict(commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(), command=sys.argv,
                  started_at_utc=datetime.now(timezone.utc).isoformat(), mode=a.mode, usd=0, device="cpu",
                  data_split="development (registry fresh cohort)", protocol="research/claude-two-factor-instance-protocol-20261017.md")
    if a.mode == "calibrate":
        pos, neg = score_split(F, cal_ids, cal_near, AN1 / "images", "T4-calibration")
        best = None
        for t2 in [round(0.50 + 0.01 * k, 2) for k in range(50)]:
            passing = [r["d1"] for r in neg if r.get("b1") is not None and r["b1"] >= t2 and r.get("d1") is not None]
            t1 = max(float(np.nextafter(max(passing), np.inf)) if passing else SCREEN_TAU, SCREEN_TAU)
            s2 = sum(majority([r for r in pos if r["arm"] == "C1" and r["model"] == m and r["strength"] == 0.2], lambda r: accept(r, t1, t2))[0] for m in MODELS)
            s4 = sum(majority([r for r in pos if r["arm"] == "C1" and r["model"] == m and r["strength"] == 0.4], lambda r: accept(r, t1, t2))[0] for m in MODELS)
            key = (s2, s4, t2)
            if best is None or key > best[0]:
                best = (key, t1, t2)
        (_, t1, t2) = best
        frozen = dict(tau1_d1=t1, tau2_b1=t2, calibration_score_02=best[0][0], calibration_score_04=best[0][1],
                      calibration_sources=cal_ids, calibration_near_duplicates=cal_near, rule="D1>=tau1 and B1>=tau2")
        a.thresholds.write_text(json.dumps(frozen, indent=2) + "\n")
        result.update(frozen=frozen, summary=summarize(pos, neg, t1, t2), d1_computed_locally=F.computed_d1)
    else:
        fr = json.loads(a.thresholds.read_text())
        t1, t2 = fr["tau1_d1"], fr["tau2_b1"]
        ev_ids = [i for i in all_ids if i not in cal_ids]
        ev_near = [n for n in all_near if n not in cal_near]
        pos, neg = score_split(F, ev_ids, ev_near, AN2 / "images", "T4-evaluation")
        # Pointer outcomes (owner found, q read, record candidate) come from Codex's own evaluation scoring,
        # which is independent of this descriptor rule and is read only after the thresholds are frozen.
        pointer = {}
        ev_scores = AN2 / "evaluation-D1-scores.json"
        if ev_scores.exists():
            for c in json.loads(ev_scores.read_text()).get("positives_and_C0", []):
                m = re.match(r"(sd15|sd21):(\d+):([0-9.]+):(\d+):f5-r2$", str(c.get("id", "")))
                if m and isinstance(c.get("pointer"), dict):
                    pointer[(int(m.group(2)), m.group(1), float(m.group(3)), int(m.group(4)))] = bool(c["pointer"].get("recovered"))
        result.update(thresholds=fr, evaluation_sources=ev_ids, evaluation_near_duplicates=ev_near, pointer_rows=len(pointer),
                      summary=summarize(pos, neg, t1, t2, pointer if pointer else None), d1_computed_locally=F.computed_d1)
    result["duration_seconds"] = time.monotonic() - tick
    result["outcome"] = "completed"
    (a.output_dir / "run.json").write_text(json.dumps(result, indent=2, default=list) + "\n")
    print(json.dumps({k: result[k] for k in ("mode", "duration_seconds", "d1_computed_locally")}, indent=1))
    if a.mode == "calibrate":
        print("FROZEN", json.dumps(result["frozen"]))
    for name, s in result["summary"].items():
        print(f"\n== {name}")
        for c, v in s["cells"].items():
            print(f"  {c}: {v}")
        for f, v in s["negatives"].items():
            print(f"  NEG {f}: n={v['n']} FA={v['false_accepts']} clusters={v['clusters_with_fa'][:5]} maxD1={v['max_d1']} maxB1={v['max_b1']}")


if __name__ == "__main__":
    main()
