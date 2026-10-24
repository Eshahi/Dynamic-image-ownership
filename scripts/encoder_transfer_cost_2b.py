"""Project the stage-2b cost from the timings measured in the stage-2a run. Stdlib only; reads no score.

Written by Claude (Opus 5.5) on 2026-10-24 for amendment 2b. Per new unit, time = generation + quality
metrics + detector reads, using the stage-2a mean of the same arm in the nearest measured cell:
- R0 and R1 at .1 and .4 reuse their .2 cell; generation at .4 is doubled (8 executed steps instead
  of 4), and .1 keeps the .2 time;
- the rinse is one more R1 .1 pass, plus one more distortion measurement (the incremental one);
- R3 (full Kandinsky 3) has no measurement yet, so it is bracketed at 2-8 s per output;
- P5 adds 8 (smoothing) or 1 (control) fp32 SDXL encodes per marked input, shared by its three seeds,
  at the D1 encode-and-decode time as an upper bound; its img2img pass costs R1's generation.
Setup, smoke and the return of the results are bracketed separately. The runner's smoke projection on
the new server replaces the compute numbers before the run.

Usage: python scripts/encoder_transfer_cost_2b.py --run <stage2a-full dir>
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
import statistics
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import encoder_transfer_test as et  # noqa: E402
import encoder_transfer_amend_2b as amend  # noqa: E402

# Hours, (low, high).
OVERHEAD = dict(environment_and_packages=(0.15, 0.3), downloads_and_hashing_50GB=(0.15, 0.4),
                upload_stage2a_inputs_180MB=(0.05, 0.2), adapter_check=(0.05, 0.1),
                smoke_368_units=(0.35, 0.5), model_loads=(0.15, 0.25), return_of_results_3GB=(0.5, 1.3))


def measured(rows):
    gen, read = defaultdict(list), defaultdict(list)
    for row in rows.values():
        if row.get("status") != "ok":
            continue
        key = (row["channel"], row["arm"])
        gen[key].append(row.get("generation_seconds") or 0)
        read[key].append((row.get("metrics_seconds") or 0) + sum((row.get("detection_seconds") or {}).values()))
    return {k: statistics.mean(v) for k, v in gen.items()}, {k: statistics.mean(v) for k, v in read.items()}


def project(config, sources, rows, k3_seconds):
    gen, read = measured(rows)
    inherited = {tuple(c) for c in config["inherited_cells"]}
    counts = Counter((u["channel"], u["strength"], u["arm"]) for u in et.plan(config, sources)
                     if (u["channel"], u["strength"], u["arm"]) not in inherited)
    encode = gen[("D1", "unmarked")]
    metric = statistics.mean(r.get("metrics_seconds") or 0 for r in rows.values() if r.get("channel") == "R1" and r.get("status") == "ok")
    cells = []
    for (cid, strength, arm), n in sorted(counts.items(), key=str):
        g, r = gen[("R0" if cid == "R0" else "R1", arm)], read[("R0" if cid == "R0" else "R1", arm)]
        if cid in ("R0", "R1") and strength == .4:
            g *= 2
        elif cid == "R1-rinse":
            r += metric
        elif cid == "R3":
            g = k3_seconds
        elif cid == "R1-smooth":
            g += 8 * encode / 3
        elif cid == "R1-mode":
            g += encode / 3
        cells.append(dict(channel=cid, strength=strength, arm=arm, units=n, generation_s=g, reads_s=r, hours=n * (g + r) / 3600))
    return cells


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--hourly", type=float, nargs=2, default=(0.45, 0.65))
    args = parser.parse_args()
    config = amend.build_config("0" * 64, {"sentencepiece": "X", "protobuf": "Y"}, 25.9, 14.48, None)
    _, sources = et.load_contract(amend.STUDY / "stage2a-config.json")
    rows = {}
    with open(args.run / "rows.jsonl", encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            rows[row["id"]] = row
    result = dict(new_units=sum(c["units"] for c in project(config, sources, rows, 5.)))
    for label, k3, side in (("low", 2., 0), ("high", 8., 1)):
        cells = project(config, sources, rows, k3)
        raw = sum(c["hours"] for c in cells)
        runner = 1.3 * raw + 900 / 3600  # the runner's own allowance: +30% and a 900 s loading reserve
        overhead = sum(v[side] for v in OVERHEAD.values())
        result[label] = dict(raw_compute_hours=round(raw, 2), runner_projection_hours=round(runner, 2),
                             overhead_hours=round(overhead, 2), instance_hours=round(runner + overhead, 2),
                             usd_at=dict((f"{p:.2f}/h", round((runner + overhead) * p, 2)) for p in args.hourly))
    by = defaultdict(float)
    for c in project(config, sources, rows, 5.):
        by[f"{c['channel']} {c['strength']}"] += c["hours"]
    result["raw_compute_hours_by_cell_with_k3_at_5s"] = {k: round(v, 2) for k, v in sorted(by.items())}
    result["overhead_hours_low_high"] = OVERHEAD
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
