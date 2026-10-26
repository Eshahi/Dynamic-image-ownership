"""Amendment B1 values: the SD1.5-only exploratory law, frozen from Phase-A development data before Phase B.

Written by Claude (Opus 5.5) on 2026-10-26 after the user chose, for Phase B, "law derivatives only for SD1.5" (a
declared exploratory amendment outside the 13-slot Holm family). The estimator, weights, coverage rule and radius rule
are the frozen ones of training-missingness-design.md, restricted to the three R0 cells: kappa_R0 on the 30 fit sources,
then q90_R0 on the 30 calibration sources (nine R0 trajectories per source; an incomplete source is +infinity; 28th
order statistic of 30). The pooled Phase-A freeze is not changed.

Usage: python -I amendment_b1.py PHASE_A_RUN_FOLDER > amendment-b1.json
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))
import et_final_phase_a_fit as fitmod  # noqa: E402
import et_final_pilot as pilot  # noqa: E402
from encoder_transfer_test import ALPHA  # noqa: E402

CELLS = ["R0-0.1", "R0-0.2", "R0-0.4"]
SEEDS = (12, 13, 14)


def journal(path):
    rows = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            rows[r["id"]] = r
    return rows


def main():
    run = Path(sys.argv[1])
    native, det = journal(run / "native.jsonl"), journal(run / "detect.jsonl")
    fit = json.loads((run / "phase-a-fit.json").read_text(encoding="utf-8"))
    fit_ids, cal_ids = fit["fit_sources"], fit["calibration_sources"]
    config, _ = pilot.channel_specs()
    profile = pilot.read(ROOT / config["profile_file"])
    num = den = 0.0
    avail = {}
    for cell in CELLS:
        for s in fit_ids:
            avail[(cell, s)] = 0
            for seed in SEEDS:
                law = native.get(f"law:{cell}:{s}:{seed}")
                if law and law.get("status") == "ok":
                    v, b, p1 = (np.asarray(law[k]) for k in ("v", "b", "p1"))
                    num += float(v @ (p1 - b)) / 18
                    den += float(v @ v) / 18
                    avail[(cell, s)] += 1
    per_cell = {c: sum(avail[(c, s)] for s in fit_ids) for c in CELLS}
    triplets_ok = all(n >= 2 for n in avail.values())
    kappa = num / den if den > 0 else None
    status = "FIT_UNAVAILABLE" if not (triplets_ok and all(n >= 81 for n in per_cell.values()) and kappa and math.isfinite(kappa)) else \
        ("FIT_COMPLETE" if all(n == 90 for n in per_cell.values()) else "FIT_QUALIFIED_INCOMPLETE")

    def margins(cell, s, seed):
        law = native.get(f"law:{cell}:{s}:{seed}")
        d = det.get(f"det:f5-r2:native:{cell}:{s}:{seed}:f5-r2")
        f0 = (det.get(f"det:f5-r2:native:{cell}:{s}:{seed}:unmarked") or {}).get("f0")
        if not law or law.get("status") != "ok" or f0 is None or not d or d.get("status") != "ok":
            return None
        sem = d["calls"][ALPHA]["raw"]["semantic"]
        pred = fitmod.semantic_predict(np.asarray(law["b"]) + kappa * np.asarray(law["v"]), f0, profile)
        actual_c = bool(d["calls"][ALPHA]["endpoints"]["C"])
        m_act = float(sem["decoded_score"]) - float(sem["decoded_threshold"])
        if pred["margin"] is None or not math.isfinite(m_act):
            return None
        return dict(err=abs(m_act - pred["margin"]), pred_c=pred["C"], actual_c=actual_c)

    scores, diag = [], {c: dict(fit=[0, 0, 0], calibration=[0, 0, 0]) for c in CELLS}  # [sources, law majority, actual majority]
    for s in fit_ids + cal_ids:
        split = "fit" if s in fit_ids else "calibration"
        worst, complete = 0.0, True
        for cell in CELLS:
            m = [margins(cell, s, seed) for seed in SEEDS]
            for x in m:
                if x is None:
                    complete = False
                else:
                    worst = max(worst, x["err"])
            law_major = sum(x is not None and x["pred_c"] for x in m) >= 2
            act_major = sum(x is not None and x["actual_c"] for x in m) >= 2
            d = diag[cell][split]
            d[0] += 1
            d[1] += law_major
            d[2] += act_major
        if split == "calibration":
            scores.append(dict(source=s, complete=complete, score=worst if complete else {"kind": "positive_infinity", "value": None}))
    finite = sorted(x["score"] for x in scores if x["complete"])
    ranked = finite + [math.inf] * (30 - len(finite))
    q90 = ranked[27]
    out = dict(amendment="B1", kappa_R0=dict(value=kappa, status=status, numerator=num, denominator=den, vectors_per_cell=per_cell,
                                              triplets_with_two_or_more=triplets_ok),
               q90_R0=dict(value=None if math.isinf(q90) else q90, infinite=math.isinf(q90), complete_sources=len(finite),
                           status="RADIUS_COMPLETE_FINITE" if len(finite) == 30 else "RADIUS_CONSERVATIVE_FINITE" if len(finite) >= 28 else "RADIUS_UNINFORMATIVE_INFINITE",
                           units="native decoded score units", source_scores=scores),
               development_majorities={c: {k: dict(sources=v[0], law_positive=v[1], actual_positive=v[2]) for k, v in d.items()} for c, d in diag.items()},
               note="descriptive development agreement; the amended law is exploratory and outside the Holm family")
    json.dump(out, sys.stdout, indent=1, default=str)


if __name__ == "__main__":
    main()
