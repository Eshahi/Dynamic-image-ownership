"""Descriptive tables for the final-study Phase A run (development sources only).

Written by Claude (Opus 5.5) on 2026-10-26. Reads the retrieved run folder (native.jsonl, attacks.jsonl, detect.jsonl,
mechanism.jsonl, attack-freeze.json, phase-a-fit.json) and writes phase-a-tables.md. Nothing here feeds back into the
freeze: kappa, q90, the comparator and the attack choice are read from the files the frozen stages wrote.

Usage: python summarize_phase_a.py RUN_FOLDER OUTPUT_MD
"""
from __future__ import annotations

import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts"))
from encoder_transfer_test import ALPHA, BETA  # noqa: E402

MARKS = ["f5-r2", "v5-r3", "wam", "vine-r"]
CELLS = ["R0-0.1", "R0-0.2", "R0-0.4", "R1-0.1", "R1-0.2", "R1-0.4"]
SEEDS = [12, 13, 14]


def journal(path):
    rows = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                rows[r["id"]] = r
    return rows


def call(row, owner=ALPHA):
    """Decision of one detector call: frozen C for the internal marks, binomial presence for WAM/VINE-R; None if missing."""
    if not row or row.get("status") != "ok":
        return None
    c = row["calls"].get(owner)
    if not c or c.get("status") != "ok":
        return None
    if row["method"] in ("f5-r2", "v5-r3"):
        return bool(c["endpoints"]["C"])
    return bool(c["presence"]["present"])


def wrong(row):
    """Wrong-owner (internal marks) or wrong-message (WAM/VINE-R) positive on a C1 item."""
    if not row or row.get("status") != "ok":
        return None
    if row["method"] in ("f5-r2", "v5-r3"):
        return call(row, BETA)
    p = row["calls"][ALPHA].get("wrong_message_presence")
    return None if p is None else bool(p["present"])


def majority(values):
    return sum(v is True for v in values) >= 2


def med(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else None


def fmt(x, d=3):
    return "–" if x is None else f"{x:.{d}f}" if isinstance(x, float) else str(x)


def table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    out += ["| " + " | ".join(fmt(c) for c in r) + " |" for r in rows]
    return out


def main():
    run, target = Path(sys.argv[1]), Path(sys.argv[2])
    native, attacks, det = journal(run / "native.jsonl"), journal(run / "attacks.jsonl"), journal(run / "detect.jsonl")
    mech = journal(run / "mechanism.jsonl")
    freeze = json.loads((run / "attack-freeze.json").read_text(encoding="utf-8")) if (run / "attack-freeze.json").exists() else {}
    fit = json.loads((run / "phase-a-fit.json").read_text(encoding="utf-8")) if (run / "phase-a-fit.json").exists() else {}
    sources = sorted({r["source"] for r in native.values() if r["kind"] == "native"})
    md = ["# Phase A tables (development sources; descriptive)", "",
          f"Generated from `{run.name}`: {len(native)} stage-1 rows, {len(attacks)} attack rows, {len(det)} detector rows, "
          f"{len(mech)} mechanism rows, {len(sources)} sources.", ""]

    # 1. Stage-1 coverage and numerical diagnostics.
    md += ["## 1. Native grid and law tangents", ""]
    rows = []
    for cell in CELLS:
        nat = [r for r in native.values() if r["kind"] == "native" and r["cell"] == cell]
        law = [r for r in native.values() if r["kind"] == "law" and r["cell"] == cell]
        st = Counter(r["status"] for r in nat)
        ok = [r for r in law if r.get("status") == "ok"]
        rows.append([cell, st.get("ok", 0), st.get("safety_blocked", 0), st.get("error_terminal", 0), len(ok), len(law) - len(ok),
                     max((max(r["step_primal_rel_err"]) for r in ok), default=None),
                     med([r.get("chips_float_vs_b_rel") for r in ok]), med([r.get("seconds") for r in law])])
    md += table(["cell", "native ok", "safety", "error", "law ok", "law unavailable", "max primal err", "median chip float rel", "median s/unit"], rows)
    md += [""]

    # 2. Native detection: each mark with its own detector, C0 with all four.
    md += ["## 2. Native outputs: detection by arm", "",
           "Attempt rate over all scheduled seeds (missing counts as a failure); source rate = majority of three seeds.", ""]
    rows = []
    for cell in CELLS:
        for m in MARKS:
            att, src, c0f, wr = [], 0, [], []
            for s in sources:
                vals = [call(det.get(f"det:{m}:native:{cell}:{s}:{seed}:{m}")) for seed in SEEDS]
                att += vals
                src += majority(vals)
                c0f += [call(det.get(f"det:{m}:native:{cell}:{s}:{seed}:unmarked")) for seed in SEEDS]
                wr += [wrong(det.get(f"det:{m}:native:{cell}:{s}:{seed}:{m}")) for seed in SEEDS]
            rows.append([cell, m, f"{sum(v is True for v in att)}/{len(att)}", f"{src}/{len(sources)}",
                         f"{sum(v is True for v in c0f)}/{sum(v is not None for v in c0f)}",
                         f"{sum(v is True for v in wr)}/{sum(v is not None for v in wr)}"])
    md += table(["cell", "arm", "C attempts", "C sources", "C0 false", "wrong owner/message"], rows)
    md += [""]

    # 3. Attack freeze.
    md += ["## 3. Attack selection freeze (quality only)", ""]
    for name in ("A", "B"):
        f = freeze.get(name) or {}
        md += [f"**Attack {name}:** {f.get('status')} — selected {f.get('selected')}; grid rows {f.get('observed_grid_rows')}/"
               f"{f.get('planned_grid_rows')}.", ""]
        rows = []
        for c in f.get("candidates", []):
            rows.append([str(c["theta"]), "yes" if c["eligible"] else "no", c["score"],
                         *[f"{c['arms'][m]['passing_sources']}/{c['arms'][m]['passing_outputs']}" for m in MARKS]])
        md += table(["theta", "eligible", "score", *[f"{m} src/out" for m in MARKS]], rows) + [""]
    qrows = []
    for kind in ("gridA", "gridB"):
        groups = defaultdict(list)
        for r in attacks.values():
            if r["kind"] == kind and r.get("status") == "ok":
                key = r["strength"] if kind == "gridA" else (r["epsilon"], r["lam"])
                groups[(str(key), r["arm"])].append(r["quality"])
        for (key, arm), qs in sorted(groups.items()):
            qrows.append([kind, key, arm, len(qs), med([q.get("lpips") for q in qs]), med([q.get("psnr_db") for q in qs]),
                          med([q.get("ssim_rgb") for q in qs])])
    md += ["Median attack quality against the attacked input (all grid outputs):", ""]
    md += table(["grid", "theta", "arm", "n", "LPIPS", "PSNR", "SSIM"], qrows) + [""]

    # 4. Detection after the frozen attacks and controls.
    md += ["## 4. Frozen attacks and controls: detection", ""]
    rows = []
    a_sel, b_sel = (freeze.get("A") or {}).get("selected"), (freeze.get("B") or {}).get("selected")
    for label, kind, theta in (("A selected", "gridA", a_sel), ("A first pass", "gridA-first", a_sel), ("A on C0", "ctrlA", a_sel),
                               ("B selected", "gridB", b_sel), ("B on C0", "ctrlB-selected", b_sel),
                               ("B fidelity only", "ctrlB-fidelity", b_sel), ("B codec", "ctrlB-codec", None)):
        if theta is None and kind != "ctrlB-codec":
            continue
        for m in MARKS:
            vals = []
            for s in sources:
                if kind.startswith("gridA") or kind == "ctrlA":
                    arm = "unmarked" if kind == "ctrlA" else m
                    base = "ctrlA" if kind == "ctrlA" else "gridA"
                    suffix = ":first" if kind == "gridA-first" else ""
                    vals.append([call(det.get(f"det:{m}:{base}:{theta[0]}:{s}:{arm}:{seed}{suffix}")) for seed in SEEDS])
                elif kind == "gridB":
                    vals.append([call(det.get(f"det:{m}:gridB:{theta[0]}:{theta[1]}:{s}:{m}"))])
                elif kind == "ctrlB-selected":
                    vals.append([call(det.get(f"det:{m}:ctrlB-selected:{s}:unmarked"))])
                else:
                    vals.append([call(det.get(f"det:{m}:{kind}:{s}:{m}")), call(det.get(f"det:{m}:{kind}:{s}:unmarked"))])
            if kind in ("ctrlB-fidelity", "ctrlB-codec"):
                rows.append([label, m, f"{sum(v[0] is True for v in vals)}/{len(vals)}", f"C0 false {sum(v[1] is True for v in vals)}"])
            elif len(vals[0]) == 3:
                rows.append([label, m, f"{sum(majority(v) for v in vals)}/{len(vals)} sources",
                             f"{sum(x is True for v in vals for x in v)}/{3 * len(vals)} attempts"])
            else:
                rows.append([label, m, f"{sum(v[0] is True for v in vals)}/{len(vals)}", ""])
    md += table(["item", "detector", "positives", "note"], rows) + [""]

    # 5. Fit and freeze values.
    md += ["## 5. Law fit, radius and comparator", ""]
    if fit:
        k, q, b = fit["kappa"], fit["q90"], fit["quality_comparator"]
        md += [f"- kappa = {fmt(k['value'], 5)} ({k['status']}); vectors per cell {k['vectors_per_cell']}.",
               f"- q90 = {fmt(q['value'], 5)} ({q['status']}; {q['complete_sources']}/30 complete calibration sources; {q['units']}).",
               f"- Quality comparator: {b['status']}; {b['rows']} rows, {b['positives']} positives; diagnostics {b['diagnostics']}.",
               f"- Coefficients (intercept first; standardized {', '.join(b['features'])}): "
               f"{[round(c, 4) for c in b['coefficients']] if b['coefficients'] else None}.", ""]
        rows = [[c, *(fit["development_diagnostics"]["by_cell"][c].get(k) for k in
                      ("actual_rate", "law_rate", "law_brier", "quality_brier", "law_available", "quality_available"))] for c in CELLS]
        md += ["Development diagnostics (reused development data; not an H4 test):", ""]
        md += table(["cell", "actual F5 rate", "law rate", "law Brier", "comparator Brier", "law n", "comparator n"], rows) + [""]
        import numpy as np
        rows = []
        for cell in CELLS:
            cos, res = [], []
            for r in native.values():
                if r["kind"] == "law" and r["cell"] == cell and r.get("status") == "ok" and k["value"] is not None:
                    v, d = np.asarray(r["v"]), np.asarray(r["p1"]) - np.asarray(r["b"])
                    if np.linalg.norm(v) > 0 and np.linalg.norm(d) > 0:
                        cos.append(float(v @ d / np.linalg.norm(v) / np.linalg.norm(d)))
                        res.append(float(np.linalg.norm(d - k["value"] * v) / np.linalg.norm(d)))
            rows.append([cell, len(cos), med(cos), med(res)])
        md += ["Chip-space agreement of the linear law with the actual F5 output (all sources):", ""]
        md += table(["cell", "n", "median cos(v, p1-b)", "median |p1-b-kappa v|/|p1-b|"], rows) + [""]
    else:
        md += ["phase-a-fit.json not present.", ""]

    # 6. Mechanism module.
    md += ["## 6. Mechanism module (descriptive)", ""]
    rows = []
    for fam in ("R0", "R1", "K3"):
        g = [r for r in mech.values() if r.get("kind") == "gain" and r["family"] == fam and r.get("status") == "ok"]
        for arm in MARKS:
            ga = [r["gains"] for r in g if r["arm"] == arm]
            if ga:
                rows.append([fam, arm, len(ga), *[med([x.get(k) for x in ga]) for k in ("actual", "gauss1", "gauss2", "phase1", "phase2")],
                             med([r["finite_gain_actual"] for r in g if r["arm"] == arm])])
    md += ["Encoder gain (latent norm per unit pixel norm), median over sources:", ""]
    md += table(["family", "arm", "n", "actual", "gauss1", "gauss2", "phase1", "phase2", "finite actual"], rows) + [""]
    rows = []
    for fam in ("R0", "R1", "K3"):
        st = [r for r in mech.values() if r.get("kind") == "stage" and r["family"] == fam and r.get("status") == "ok"]
        if not st:
            continue
        for stage in ("mode_codec", "sampled_codec", "noise_only", "mode_reverse", "native"):
            vals = [r["stages"][stage]["f5-r2"] for r in st if stage in r["stages"] and "f5-r2" in r["stages"][stage]]
            if vals:
                rows.append([fam, stage, len(vals), med([v.get("retention_vs_clean") for v in vals]), med([v["pixel_residual_rms"] for v in vals]),
                             med([v["reader_latent_residual"] for v in vals])])
    md += ["F5 transport through the regeneration stages at strength .2 (retention = e·Δchips / clean e·Δchips):", ""]
    md += table(["family", "stage", "n", "median retention", "median pixel RMS", "median reader-latent residual"], rows) + [""]
    rows = []
    for fam in ("R0", "R1", "K3"):
        st = [r for r in mech.values() if r.get("kind") == "stage" and r["family"] == fam and r.get("status") == "ok"]
        for kind in ("actual", "gauss1", "gauss2", "phase1", "phase2"):
            t = [r["tangents"][kind] for r in st if kind in r.get("tangents", {})]
            if t:
                rows.append([fam, kind, len(t), med([x["e_v"] for x in t]), med([x["v_norm"] for x in t]), max(x["max_primal_err"] for x in t)])
    md += ["F5 differential chain tangents (e·v along each direction, scaled to the direction's size):", ""]
    md += table(["family", "direction", "n", "median e·v", "median |v|", "max primal err"], rows) + [""]
    target.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"wrote {target}")


if __name__ == "__main__":
    main()
