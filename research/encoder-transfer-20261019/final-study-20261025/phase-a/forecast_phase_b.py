"""Revised Phase-B resource forecast from Phase-A measured timers (07-final-experiment.md section 4 freeze item).

Written by Claude (Opus 5.5) on 2026-10-26. Measured inputs: the Phase-A journals (native.jsonl law rows time one
complete unit = C0 + four marked native outputs + the F5 full-chain JVP; mechanism.jsonl K3 stage rows; detect.jsonl;
attacks.jsonl ctrlB-codec). Clean embedding and per-output quality metrics are not re-measured in Phase A and come from
the stage-2 cost ledger (analysis/cost-analysis.json). Per-unit times use the 90th percentile; a 30% margin is applied
to compute, as in the pilot projection. Phase-A runs shared the GPU between processes, so these times are conservative.

Usage: python -I forecast_phase_b.py RUN_FOLDER COST_ANALYSIS_JSON PILOT_PROJECTION_JSON > phase-b-forecast.json
"""
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

MARGIN = 1.3
N, SEEDS = 200, 3


def rows(path):
    out = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            out[r["id"]] = r
    return out.values()


def p90(xs):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(round(.9 * (len(xs) - 1))))]


def stats(xs):
    return dict(n=len(xs), median=statistics.median(xs), p90=p90(xs), max=max(xs)) if xs else None


def main():
    run, cost = Path(sys.argv[1]), json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    pilot = json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))
    unit = defaultdict(list)
    for r in rows(run / "native.jsonl"):
        if r["kind"] == "law" and r.get("status") == "ok":
            unit[r["cell"]].append(r["seconds"])
    k3 = [r["seconds"] for r in rows(run / "mechanism.jsonl") if r.get("kind") == "stage" and r["family"] == "K3" and r.get("status") == "ok"]
    det = defaultdict(list)
    for r in rows(run / "detect.jsonl"):
        if r.get("status") == "ok":
            det[(r["method"], r["control"])].append(r["seconds"])
    # Control rows carry no timer; use the spacing of their journal timestamps (one process, sequential writes).
    import calendar, time
    stamps = sorted(calendar.timegm(time.strptime(r["utc"], "%Y-%m-%dT%H:%M:%SZ")) for r in rows(run / "attacks.jsonl")
                    if r["kind"] == "ctrlB-codec" and r.get("status") == "ok")
    codec = [(stamps[-1] - stamps[0]) / (len(stamps) - 1)] if len(stamps) > 1 else []
    measured = dict(unit_seconds={c: stats(v) for c, v in sorted(unit.items())},
                    k3_mechanism_stage_row_seconds=stats(k3),
                    detector_seconds={f"{m}:{c}": stats(v) for (m, c), v in sorted(det.items())},
                    b_codec_seconds=stats(codec))
    hours = {}
    # Native grid with law JVPs: 600 units per cell (200 sources x 3 seeds), six R0/R1 cells measured directly.
    hours["native_and_law_R0_R1"] = sum(N * SEEDS * stats(v)["p90"] for v in unit.values()) / 3600
    # K3 .2: no main-law K3 unit ran in Phase A; the mechanism stage row (five native outputs, stage decodes and five
    # differential chain tangents) is an upper bound for one law unit (five native outputs and one tangent).
    k3_unit = pilot["cell_full_chain_jvp_seconds"]["K3 0.2"] + 5 * cost["generation"]["R3:0.2"]["p90"]
    hours["native_and_law_K3"] = N * SEEDS * k3_unit / 3600
    upper_k3 = N * SEEDS * p90(k3) / 3600 if k3 else None
    # Detector rows: per native cell 600 x (4 own-arm + 4 C0 reads); clean and B-codec 200 x (4 + 4) each.
    per_c1 = sum(p90(det[(m, "C1")]) for m in ("f5-r2", "v5-r3", "wam", "vine-r"))
    per_c0 = sum(p90(det[(m, "C0")]) for m in ("f5-r2", "v5-r3", "wam", "vine-r"))
    hours["detection"] = (7 * N * SEEDS + 2 * N) * (per_c1 + per_c0) / 3600
    # Attacks A and B are INACTIVE_QUALITY_INELIGIBLE (attack-freeze.json); only the selection-free B-codec control runs.
    hours["b_codec_control"] = 5 * N * p90(codec) / 3600 if codec else None
    hours["clean_embedding_historical"] = cost["forecast"]["phase_b_clean_embedding_hours"]
    outputs = 7 * N * SEEDS * 5 + 5 * N + 5 * N
    hours["quality_metrics_historical"] = outputs * cost["metrics"]["p90"] / 3600
    compute = sum(v for v in hours.values() if v)
    fixed = dict(setup_acquisition_loading=1.5, retrieval=round(outputs * .41 / .85 / 3600, 2))
    out = dict(measured=measured, phase_b_hours=hours, outputs=outputs, compute=compute, with_margin=compute * MARGIN,
               fixed=fixed, total=compute * MARGIN + sum(fixed.values()), margin=MARGIN,
               k3_estimate=dict(unit_seconds=k3_unit, rule="pilot K3 chain JVP + 5 x historical K3 .2 native p90",
                                upper_bound_hours=upper_k3, upper_bound_rule="Phase-A K3 mechanism stage row p90"),
               notes=["retrieval at the measured 0.85 MB/s home download rate and 0.41 MB per saved output",
                      "attacks inactive: no A, A-first, B or B-fidelity outputs; their four H5 slots stay at p=1",
                      "law JVPs are part of the measured unit times; no separate JVP allowance is added"])
    json.dump(out, sys.stdout, indent=1)


if __name__ == "__main__":
    main()
