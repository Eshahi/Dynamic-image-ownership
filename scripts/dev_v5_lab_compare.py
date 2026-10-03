"""Development lab: compare variants host by host from the lab reports.

Development tooling (see ``dev_v5_lab``).  Prints, per variant and channel, the
number of hosts whose key was found, the median, the geometric mean and the
lowest recomputed score, and the score of every host.

    python scripts/dev_v5_lab_compare.py --reports lab8,lab9 --variants r3-base,r3-mp0
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import dev_v5_lab as lab  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reports", required=True, help="comma-separated report tags")
    parser.add_argument("--variants", default="", help="comma-separated variant names (default: all)")
    parser.add_argument("--hosts", default="dev")
    parser.add_argument("--per-host", action="store_true")
    args = parser.parse_args()
    found = {}
    for tag in args.reports.split(","):
        report = json.loads((lab.LAB / args.hosts / f"report-{tag}.json").read_text(encoding="utf-8"))
        for name, data in report["variants"].items():
            found[name] = data["rows"]
    names = args.variants.split(",") if args.variants else list(found)
    for name in names:
        rows = found[name]
        channels = [key for key in rows[0]["C1"] if key != "clean"]
        psnr = [row["info"]["rgb_psnr"] for row in rows]
        parts = []
        for channel in channels:
            scores = np.array([row["C1"][channel]["r"] if row["C1"][channel] else 0.0 for row in rows])
            kept = sum(bool(row["C1"][channel] and row["C1"][channel]["found"]) for row in rows)
            false = sum(bool(row["C0"][channel] and row["C0"][channel]["found"]) for row in rows)
            geo = float(np.exp(np.log(np.maximum(scores, 0.1)).mean()))
            parts.append(f"{channel} {kept}/{len(rows)} med {np.median(scores):.2f} geo {geo:.2f} min {scores.min():.2f}" + (f" C0 {false}" if false else ""))
        print(f"{name:22s} psnr {min(psnr):.1f}-{max(psnr):.1f} | " + " | ".join(parts))
        strengths = sorted({channel.split("-")[0] for channel in channels if channel.startswith("sd")})
        every = []
        for strength in strengths:
            seeds = [channel for channel in channels if channel.split("-")[0] == strength]
            hosts = sum(all(row["C1"][seed] and row["C1"][seed]["found"] for seed in seeds) for row in rows)
            every.append(f"{strength} {hosts}/{len(rows)} on all {len(seeds)} seeds")
        print(f"{'':22s} " + " | ".join(every))
        if args.per_host:
            for channel in channels:
                print(f"   {channel:9s}", " ".join(f"{row['C1'][channel]['r'] if row['C1'][channel] else float('nan'):5.1f}" for row in rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
