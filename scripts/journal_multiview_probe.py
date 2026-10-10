"""Bounded fixed-all-twelve cached clean/VAE prerequisite screen for V1."""
from __future__ import annotations
import time
BOOT_STARTED = time.monotonic()  # Includes heavy imports and model loading.
import argparse
import json
from pathlib import Path
import subprocess
import sys
import traceback
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]
import numpy as np
from scripts import journal_multiview_readout as readout
from scripts.journal_vae_probe import Evaluator
from f5_gate import OWNERS
from f4_transfer_probe import MAIN, SOURCES
CONDITIONS = ("clean", "sd15_vae", "sdxl_vae")
CACHE = MAIN / ".thesis-build/dev-runs/20261010-1212-native-writer/rows.jsonl"
SECONDS = 300.0
CUDA_BYTES = 10 * 1024 ** 3


def write(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def strict(quality):
    return bool((quality.get("psnr_infinite") or (quality["psnr_db"] is not None and quality["psnr_db"] > 35))
                and quality["ssim_rgb"] > .9 and quality["lpips"] < .1)


def checked(call):
    return bool(call["semantic"]["found"] and call["semantic"]["read"] and call["semantic"]["content_match"])


def summarize(rows, originals):
    result = {"method": "V1", "candidate": "D2-V1", "planned_images": 72, "planned_calls": 108, "completed_images": len(rows),
              "failed_images": sum(r["status"] != "ok" for r in rows), "conditions": {}}
    old = {r["source_id"]: r for r in originals}
    for condition in CONDITIONS:
        group = [r for r in rows if r["condition"] == condition]
        positives = [r for r in group if r["control"] == "C1" and r["status"] == "ok"]
        alpha = [(r, r["calls"][OWNERS[0]]) for r in positives]
        joint = [r["source_id"] for r, c in alpha if checked(c) and c["semantic"]["decoded_code"] == old[r["source_id"]]["payload"]["q"]]
        old_joint = [sid for sid, r in old.items() if r["conditions"][condition]["joint_fixed_q"]]
        result["conditions"][condition] = {
            "completed_c1": len(positives), "semantic_checked": sum(checked(c) for _, c in alpha),
            "exact_checked_q": len(joint), "joint_source_ids": joint,
            "old_joint_source_ids": old_joint, "lost_old_joint": sorted(set(old_joint) - set(joint)),
            "both_match": sum(c["outcome"] == "both_match" for _, c in alpha),
            "exact_read_h": sum(bool(c["instance"]["read"] and c["instance"]["decoded_code"] == old[r["source_id"]]["payload"]["h"]) for r, c in alpha),
            "c0_any": sum(bool(r["calls"][OWNERS[0]]["watermark_found"]) for r in group if r["control"] == "C0" and r["status"] == "ok"),
            "wrong_owner_any": sum(bool(r["calls"][OWNERS[1]]["watermark_found"]) for r in positives),
            "completed_c0": sum(r["control"] == "C0" and r["status"] == "ok" for r in group)}
    result["strict_clean_quality"] = sum(strict(r["conditions"]["clean"]["quality_source"]) for r in originals)
    conditions = result["conditions"]
    result["prerequisite_eligible"] = bool(len(rows) == 72 and not result["failed_images"]
        and result["strict_clean_quality"] == 12
        and conditions["clean"]["exact_checked_q"] == 12 and conditions["clean"]["exact_read_h"] == 12
        and conditions["clean"]["both_match"] == 12 and conditions["sd15_vae"]["exact_checked_q"] == 12
        and conditions["sdxl_vae"]["exact_checked_q"] >= 11 and not conditions["sdxl_vae"]["lost_old_joint"] and not conditions["sd15_vae"]["lost_old_joint"]
        and all(c["c0_any"] == c["wrong_owner_any"] == 0 for c in conditions.values()))
    result["scope"] = "Exploratory cached development prerequisite only; legacy BER/FPR unvalidated; no T3 or milestone passage"
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=False)
    originals = [json.loads(line) for line in CACHE.read_text(encoding="utf-8").splitlines() if line.strip()]
    originals.sort(key=lambda r: r["source_id"])
    if len(originals) != 12 or [r["source_id"] for r in originals] != sorted(SOURCES) or any(r["config"] != "D2" or r["status"] != "ok" for r in originals):
        raise ValueError("Expected fixed twelve successful D2 development sources")
    inventory = [{"source_id": r["source_id"], "condition": condition, "control": control,
                  "image": r["conditions"][condition]["image" if control == "C1" else "c0_image"],
                  "owners": list(OWNERS[:2] if control == "C1" else OWNERS[:1])}
                 for r in originals for condition in CONDITIONS for control in ("C1", "C0")]
    write(args.output_dir / "planned-inventory.json", inventory)
    record = {"commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
              "command": sys.argv, "config": {"method": "V1", "cached_writer": str(CACHE),
              "conditions": list(CONDITIONS), "views": "original RGB8 and two SD15 posterior-mode decode RGB8 cycles",
              "precision": "float32", "clip_views": 7, "clip_device": "cpu", "roster_size": 1,
              "read_threshold": readout.READ_THRESHOLD, "presence_threshold": readout.PRESENCE_THRESHOLD,
              "max_elapsed_seconds_including_imports": SECONDS, "max_cuda_allocated_bytes": CUDA_BYTES},
              "seeds": [], "data_split": "development", "sources": sorted(SOURCES), "cost_usd": 0,
              "outcome": "running", "duration_seconds": None, "cpu_self_checks": readout.self_check()}
    write(args.output_dir / "run.json", record)
    rows, ev = [], None
    def limits():
        if time.monotonic() - BOOT_STARTED > SECONDS:
            raise RuntimeError("Fixed inclusive 300-second screen cap exceeded; no fresh retry")
        if ev is not None and ev.torch.cuda.max_memory_allocated() > CUDA_BYTES:
            raise RuntimeError("Fixed 10-GiB CUDA allocation cap exceeded")
    try:
        limits()
        import torch
        total = torch.cuda.get_device_properties(0).total_memory
        torch.cuda.set_per_process_memory_fraction(min(1.0, CUDA_BYTES / total))
        torch.cuda.reset_peak_memory_stats()
        ev = Evaluator()
        limits()
        from PIL import Image
        for item in inventory:
            row = {**item, "method": "V1", "status": "running"}
            row_started = time.monotonic()
            try:
                limits()
                rgb = np.asarray(Image.open(item["image"]).convert("RGB"), np.uint8)
                features = ev.features(rgb, 7)
                latents, timings = readout.extract_views(ev.reader, rgb, return_timings=True)
                row["calls"] = {}
                for owner in item["owners"]:
                    row["calls"][owner] = readout.detect_rgb(rgb, latents, owner, ev.profile, features,
                        binding_mode="combined", binding="soft", roster_size=1)
                    row["calls"][owner]["view_preprocessing_seconds"] = timings
                if item["control"] == "C1":
                    source = next(r for r in originals if r["source_id"] == item["source_id"])
                    row["payload_for_analysis_only"] = {"q": source["payload"]["q"], "h": source["payload"]["h"]}
                    row["retained_quality_source"] = source["conditions"][item["condition"]]["quality_source"]
                limits()
                row["status"] = "ok"
            except Exception:
                row.update(status="failed", error=traceback.format_exc())
            row["elapsed_seconds"] = time.monotonic() - row_started
            rows.append(row)
            with (args.output_dir / "rows.jsonl").open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(row, allow_nan=False) + "\n")
            print(json.dumps({k: row[k] for k in ("source_id", "condition", "control", "status", "elapsed_seconds")}), flush=True)
            limits()
        record["outcome"] = "completed" if all(r["status"] == "ok" for r in rows) else "completed_with_failures"
    except Exception:
        record.update(outcome="failed", error=traceback.format_exc())
    finally:
        summary = summarize(rows, originals)
        if ev is not None:
            record["cuda_peak_allocated_bytes"] = ev.torch.cuda.max_memory_allocated()
            record["cuda_peak_reserved_bytes"] = ev.torch.cuda.max_memory_reserved()
        write(args.output_dir / "summary.json", summary)
        record["duration_seconds"] = time.monotonic() - BOOT_STARTED
        record["completed_images"] = len(rows)
        record["budget_pass"] = record["duration_seconds"] <= SECONDS and record.get("cuda_peak_allocated_bytes", 0) <= CUDA_BYTES
        summary["resource_budget_pass"] = record["budget_pass"]
        summary["prerequisite_eligible"] = bool(summary["prerequisite_eligible"] and record["budget_pass"] and record["outcome"] == "completed")
        write(args.output_dir / "summary.json", summary)
        record["summary"] = summary
        write(args.output_dir / "run.json", record)
        final_elapsed = time.monotonic() - BOOT_STARTED
        if final_elapsed > SECONDS:
            record["duration_seconds"] = final_elapsed
            record["budget_pass"] = False
            record["outcome"] = "failed"
            record["error"] = "Fixed inclusive 300-second cap exceeded during final summaries"
            summary["resource_budget_pass"] = False
            summary["prerequisite_eligible"] = False
            write(args.output_dir / "summary.json", summary)
            write(args.output_dir / "run.json", record)
    return 0 if record["outcome"] == "completed" and record["budget_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
