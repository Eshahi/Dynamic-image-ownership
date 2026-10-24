"""Seed the stage-2b full-run journal with the verified stage-2a rows (amendment 2b). Stdlib only.

Written by Claude (Opus 5.5), 2026-10-24. Stage 2b inherits every stage-2a cell instead of rerunning
it: the stage-2a `rows.jsonl` is copied byte for byte, and every clean image that a stage-2b unit
reads is checked against the SHA-256 its row recorded. Nothing is regenerated, reread or rescored.
The stage-2b smoke starts empty, because the stage-2a smoke images were not kept; it reruns the
two reserved smoke sources only, for timing and pipeline checks.

Usage: python scripts/encoder_transfer_seed_2b.py --manifest <stage2b-config.json> --from <stage2a-full> --to <stage2b-full>
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import encoder_transfer_test as et  # noqa: E402


def seed(manifest, source_dir, target_dir):
    config, sources = et.load_contract(manifest)
    inherited = {tuple(cell) for cell in config["inherited_cells"]}
    source_rows = Path(source_dir) / "rows.jsonl"
    rows = et.Journal(source_rows).latest
    units = list(et.plan(config, sources))
    missing = [u["id"] for u in units if (u["channel"], u["strength"], u["arm"]) in inherited and not
               (u["id"] in rows and rows[u["id"]].get("status") in ("ok", "error", "safety_blocked", "input_missing"))]
    if missing:
        raise ValueError(f"Stage-2a journal lacks {len(missing)} inherited units, e.g. {missing[0]}")
    if set(rows) - {u["id"] for u in units}:
        raise ValueError("Stage-2a journal holds rows outside the stage-2b schedule")
    # Every clean output a new stage-2b unit depends on must exist with its recorded hash.
    needed = {et.unit_id(u["source_id"], "clean", None, None, u["arm"]) for u in units
              if (u["channel"], u["strength"], u["arm"]) not in inherited and u["channel"] != "R1-rinse"}
    for rid in sorted(needed):
        output = rows[rid].get("output")
        if not output or et.digest(output["path"]) != output["sha256"]:
            raise ValueError(f"Inherited input image missing or changed: {rid}")
    target = Path(target_dir)
    target.mkdir(parents=True, exist_ok=True)
    destination = target / "rows.jsonl"
    raw = source_rows.read_bytes()
    if destination.exists():
        if not destination.read_bytes().startswith(raw):
            raise ValueError("Stage-2b journal exists and does not begin with the stage-2a journal")
    else:
        destination.write_bytes(raw)
    receipt = dict(source=str(source_rows), source_sha256=et.digest(source_rows), inherited_units=len(units) - sum(
        1 for u in units if (u["channel"], u["strength"], u["arm"]) not in inherited), checked_inputs=len(needed),
        new_units=sum(1 for u in units if (u["channel"], u["strength"], u["arm"]) not in inherited))
    et.write(target / "seeded-from.json", receipt)
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--from", dest="source", type=Path, required=True)
    parser.add_argument("--to", dest="target", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(seed(args.manifest, args.source, args.target)))


if __name__ == "__main__":
    main()
