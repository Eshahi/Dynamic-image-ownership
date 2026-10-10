"""Auxiliary CPU-only clean fragile-channel diagnostic on the fixed development set.

The three q choices condition the existing instance table; they do not change
the native detector, its screen results, or any gate. No neural model is loaded.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import subprocess
import sys
import time
import traceback

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import revised_watermark_v5 as v5

IDS = (1675, 4795, 6012, 25394, 80932, 109798, 134882, 147498,
       177015, 190676, 468505, 499768)
CONFIGS = ("R1", "R2", "R3", "R4")
OWNER = "qim-pilot-owner-alpha"
MAIN = Path("W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5")
FROZEN = MAIN / ".thesis-build/dev-runs/20261005-0640-f5-gate-soft-views7"
CHOICES = ("native_q_bound", "intended_q", "decoded_q")


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def disagreement(a, b):
    mask = a ^ b
    return dict(mask=f"{mask:08x}", count=mask.bit_count(),
                bits_msb_first=[v5._bit(mask, j) for j in range(v5.CODE_BITS)],
                segments=[j for j in range(v5.CODE_BITS) if v5._bit(mask, j)])


def code(value):
    if not isinstance(value, str) or len(value) != 8:
        raise ValueError(f"Expected eight hex digits, got {value!r}")
    result = int(value, 16)
    if not 0 <= result < (1 << 32):
        raise ValueError("Code outside uint32")
    return result


def decode(projections, table, q, target_h, recomputed_h, checked):
    options = [table[j][v5._bit(q, j)] for j in range(v5.CODE_BITS)]
    test = v5._key_test(projections, options, recomputed_h)
    result = v5._channel_result(test, float(checked["decision"]["false_positive_target"]),
                                1, recomputed_h)
    decoded_h = code(result["decoded_code"])
    segment_scores = []
    target_margins = []
    for j in range(v5.CODE_BITS):
        chips = projections[j * v5.SEGMENT_CHIPS:(j + 1) * v5.SEGMENT_CHIPS]
        scores = [sum(s * x for s, x in zip(options[j][b], chips)) for b in (0, 1)]
        segment_scores.append(scores)
        own = v5._bit(target_h, j)
        target_margins.append(scores[own] - scores[1 - own])
    return dict(q=f"{q:08x}", **result,
                exact_h=decoded_h == target_h,
                readable_exact_h=bool(result["read"] and decoded_h == target_h),
                h_disagreement=disagreement(decoded_h, target_h),
                segment_scores_h0_h1=segment_scores,
                target_h_signed_bit_margins=target_margins)


def inspect(image, record, baseline, checked, key, config, table):
    payload = record["payload"]
    if payload["q"] != baseline["payload"]["q"] or payload["h"] != baseline["payload"]["h"]:
        raise ValueError("Screen target differs from the fixed frozen diagnostic target")
    clean = record["conditions"]["clean"]
    native = clean["native"] if "native" in clean else clean["calls"][OWNER]
    if native.get("native_q_bound_rule") != "decoded_q_on_found_content_mismatch_else_suspect_q":
        raise ValueError("Recorded native conditioning rule missing or unexpected")
    expected_q = (native["semantic"]["decoded_code"] if native["semantic"]["found"]
                  and native["semantic"]["content_status"] != "match" else native["semantic_code"])
    if native["native_q_bound"] != expected_q:
        raise ValueError("Recorded native q_bound contradicts its stored native rule")
    qs = dict(native_q_bound=code(native["native_q_bound"]),
              intended_q=code(payload["q"]), decoded_q=code(native["semantic"]["decoded_code"]))
    target_h = code(payload["h"])
    # Match detect_rgb's RGB8 -> Python list -> luminance -> block-DCT path.
    with Image.open(image) as img:
        rgb = img.convert("RGB")
        if rgb.size != (512, 512):
            raise ValueError("Fixed development clean image must be 512x512")
        pixels = list(rgb.getdata())
        rows = [pixels[j * 512:(j + 1) * 512] for j in range(512)]
    luma = v5.luminance_from_rgb(rows)
    height, width = v5.base._check_image(luma, int(checked["minimum_side"]))
    fragile = v5._Fragile(checked, key, config, v5.canonical_owner(OWNER), height, width)
    means, coefficients = v5.base._analyse(luma, fragile.analysis)
    recomputed_h = v5.base._perceptual_hash(means, coefficients, key, config)
    if recomputed_h != code(native["perceptual_hash"]):
        raise ValueError("CPU perceptual hash differs from the stored native hash")
    projections = fragile.projections(coefficients)
    decoded = {name: decode(projections, table, q, target_h, recomputed_h, checked)
               for name, q in qs.items()}
    reproduced = decoded["native_q_bound"]
    stored = native["instance"]
    exact_fields = ("decoded_code", "read", "found", "code_distance", "corrected_distance")
    exact_matches = {field: reproduced[field] == stored[field] for field in exact_fields}
    float_fields = ("score", "threshold", "decoded_score", "decoded_threshold",
                    "recomputed_score", "recomputed_threshold")
    deltas = {field: reproduced[field] - stored[field] for field in float_fields}
    numerical_matches = {field: math.isclose(reproduced[field], stored[field],
                                            rel_tol=1e-12, abs_tol=1e-12)
                         for field in float_fields}
    matched = all(exact_matches.values()) and all(numerical_matches.values())
    return dict(image=str(image), target_q=payload["q"], target_h=payload["h"],
                h_target_basis=payload["h_target_basis"], original_h_known=False,
                stored_native_outcome=native["outcome"],
                stored_native_instance=stored,
                suspect_semantic_code=native["semantic_code"],
                recomputed_h=f"{recomputed_h:08x}",
                q_disagreements={"native_vs_intended": disagreement(qs["native_q_bound"], qs["intended_q"]),
                                 "decoded_vs_intended": disagreement(qs["decoded_q"], qs["intended_q"]),
                                 "native_vs_decoded": disagreement(qs["native_q_bound"], qs["decoded_q"])},
                instance_projections=projections,
                projection_norm=math.sqrt(sum(x * x for x in projections)),
                conditioning=decoded,
                native_reproduction=dict(matched=matched, exact_fields=exact_matches,
                                         numerical_fields=numerical_matches, score_deltas=deltas,
                                         tolerance=dict(relative=1e-12, absolute=1e-12)))


def collect(group, sid, path, image, baseline, checked, key, config, table):
    row = dict(config=group, source_id=sid, condition="clean", control="C1",
               record_path=str(path), image=str(image), status="missing_record")
    if not path.exists():
        row["reason"] = "No completed source record in input snapshot"
        return row
    try:
        record = load_json(path)
        row["screen_status"] = record.get("status", "missing_status")
        if record.get("source_id") != sid or (group != "frozen" and record.get("config") != group):
            raise ValueError("Completed record identity differs from fixed cell")
        if not image.exists():
            row.update(status="missing_image", reason="Final clean image unavailable")
        elif not record.get("conditions", {}).get("clean") or "payload" not in record:
            row.update(status="missing_clean_metadata", reason="Cannot diagnose image without recorded native call and targets")
        elif baseline is None or baseline.get("status") != "ok":
            row.update(status="missing_frozen_target", reason="Definitive frozen diagnostic target unavailable")
        else:
            row.update(inspect(image, record, baseline, checked, key, config, table))
            row["status"] = "ok" if row["native_reproduction"]["matched"] else "native_reproduction_mismatch"
    except Exception:
        row.update(status="failed", error=traceback.format_exc())
    return row


def summarize(rows):
    result = {}
    for group in ("frozen",) + CONFIGS:
        selected = [r for r in rows if r["config"] == group]
        good = [r for r in selected if r["status"] == "ok"]
        result[group] = dict(planned=12, diagnosed=len(good), unresolved=12-len(good),
                            input_ok=sum(r.get("screen_status") == "ok" for r in selected),
                            status_counts={s: sum(r["status"] == s for r in selected)
                                           for s in sorted({r["status"] for r in selected})},
                            native_reproduction_mismatches=sum(r["status"] == "native_reproduction_mismatch" for r in selected),
                            readable_exact_h={choice: sum(r["conditioning"][choice]["readable_exact_h"] for r in good)
                                              for choice in CHOICES},
                            exact_h={choice: sum(r["conditioning"][choice]["exact_h"] for r in good)
                                     for choice in CHOICES},
                            native_intended_q_mismatches=sum(r["q_disagreements"]["native_vs_intended"]["count"] > 0 for r in good))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--screen-dir", required=True, type=Path)
    parser.add_argument("--diagnostic-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    started = time.monotonic()
    screen_run = load_json(args.screen_dir / "run.json")
    diagnostic_run = load_json(args.diagnostic_dir / "run.json")
    if screen_run["profile"] != diagnostic_run["profile"]:
        parser.error("Screen and frozen diagnostic must use the same profile")
    fixed_marks = Path(diagnostic_run["config"]["fixed_marks"]).resolve()
    if fixed_marks != FROZEN.resolve():
        parser.error("Frozen baseline must be the retained fixed-development F5 run")
    checked, key, config = v5._resolve(screen_run["profile"], None)
    table = v5._instance_table(v5.canonical_owner(OWNER), key, config)
    # Refuse overwrites and keep inputs separate from auxiliary output.
    args.output_dir.mkdir(parents=True, exist_ok=False)
    baselines = {}
    for sid in IDS:
        path = args.diagnostic_dir / "completed" / f"diagnostic-{sid}.json"
        try:
            baselines[sid] = load_json(path) if path.exists() else None
        except (OSError, ValueError):
            baselines[sid] = None
    rows = []
    with (args.output_dir / "rows.jsonl").open("w", encoding="utf-8") as handle:
        for group in ("frozen",) + CONFIGS:
            for sid in IDS:
                path = ((args.diagnostic_dir / "completed" / f"diagnostic-{sid}.json") if group == "frozen"
                        else (args.screen_dir / "completed" / f"{group}-{sid}.json"))
                image = ((FROZEN / "images" / f"clean-{sid}-C1.png") if group == "frozen"
                         else (args.screen_dir / "images" / f"{group}-{sid}-C1-clean.png"))
                row = collect(group, sid, path, image, baselines[sid], checked, key, config, table)
                rows.append(row)
                handle.write(json.dumps(row, allow_nan=False) + "\n")
                handle.flush()
                print(f"{group} {sid}: {row['status']}", flush=True)
    summary = summarize(rows)
    record = dict(schema_version="journal-instance-diagnostic-v1", kind="auxiliary_exploratory",
                  timestamp_utc=datetime.now(timezone.utc).isoformat(),
                  commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                  command=[sys.executable] + sys.argv, cpu_only=True, neural_models_loaded=False,
                  data_split="fixed12 development", source_ids=list(IDS),
                  seeds=[], cost_usd=0, screen_planned=48, frozen_planned=12,
                  screen_dir=str(args.screen_dir), diagnostic_dir=str(args.diagnostic_dir),
                  input_commits=dict(screen=screen_run.get("commit"), diagnostic=diagnostic_run.get("commit")),
                  screen_outcome_at_snapshot=screen_run.get("outcome"),
                  diagnostic_outcome_at_snapshot=diagnostic_run.get("outcome"),
                  profile=screen_run["profile"], detector_config_id=config.hex(),
                  conditioning_choices=list(CHOICES), roster_size=1,
                  limitation="Recorded semantic conditioning is reused; no fresh semantic inference. Forced q is auxiliary and cannot rescue the native screen or alter gates.",
                  h_target_basis="Frozen native-decoded operational h; original embedded h is unrecorded",
                  summary=summary, duration_seconds=time.monotonic()-started,
                  outcome="completed" if all(r["status"] == "ok" for r in rows) else "completed_with_unresolved",
                  rows=len(rows))
    write_json(args.output_dir / "run.json", record)
    lines = ["# Auxiliary clean instance diagnostic", "",
             "Fixed screen denominator: 48 (4 configurations × 12 sources); frozen baseline: 12.",
             "Native reproduction is required for diagnostic counts. Missing/failed cells remain unresolved.",
             "Forced intended/decoded q results are auxiliary; they cannot rescue screen results or gates.",
             "The h target is the frozen operational clean decoding, not an original embedded h.", "",
             "| Group | Diagnosed / 12 | Input ok / 12 | Native exact+read | Intended q exact+read | Decoded q exact+read | q mismatch |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    for group, data in summary.items():
        counts = data["readable_exact_h"]
        lines.append(f"| {group} | {data['diagnosed']}/12 | {data['input_ok']}/12 | "
                     f"{counts['native_q_bound']}/12 | {counts['intended_q']}/12 | "
                     f"{counts['decoded_q']}/12 | {data['native_intended_q_mismatches']} |")
    lines += ["", "Unresolved cells:"]
    for row in rows:
        if row["status"] != "ok" or row.get("screen_status") != "ok":
            lines.append(f"- {row['config']} {row['source_id']}: {row['status']}; input status {row.get('screen_status', 'missing')}.")
    if all(r["status"] == "ok" and r.get("screen_status") == "ok" for r in rows):
        lines.append("- None.")
    (args.output_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
