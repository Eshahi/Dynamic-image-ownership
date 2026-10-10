"""Complete only L1's twelve pre-generation unlisted-strength cells; USD 0."""
from __future__ import annotations
import time
STARTED = time.monotonic()
import argparse
import json
from pathlib import Path
import subprocess
import sys
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]
ORIGINAL = Path("W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/20261010-1309-latent-tangent")
ORIGINAL_COMMIT = "019031ada4d2a869dc02e559c061354be6297776"
VRAM = 10 * 1024**3


def original_plan(path):
    """Validate a technical repair; no completed or scientifically failed cells."""
    run = json.loads((path / "run.json").read_text(encoding="utf-8"))
    expected = {f"T3-{sid}-0.1-{seed}-{arm}" for sid in (1675, 468505) for seed in range(3) for arm in ("C0", "P")}
    if run["commit"] != ORIGINAL_COMMIT or run["method"] != "L1-image-DCT":
        raise ValueError("Unexpected retained L1 run")
    if run["frozen_selection"] != {"1675/L": None, "1675/P": 1., "468505/L": None, "468505/P": .75}:
        raise ValueError("Frozen selection differs")
    rows = run["rows"]
    if len(rows) != 96 or len({r["id"] for r in rows}) != 96:
        raise ValueError("Require complete retained 96-cell inventory")
    failed = [r for r in rows if r["status"] in ("failed", "missing")]
    if {r["id"] for r in failed} != expected or len(failed) != 12 or set(run["failed_or_missing"]) != expected:
        raise ValueError("Only the twelve specified unlisted-strength cells may be completed")
    for r in failed:
        if (r["status"] != "failed" or r["phase"] != "T3" or r["strength"] != .1 or
                "ValueError: unlisted regeneration strength" not in r.get("error", "") or
                "regeneration_kwargs" not in r["error"] or r.get("image") or r.get("calls")):
            raise ValueError("Cell did not fail before generation for the specified technical reason")
    completed = [r for r in rows if r["phase"] == "T3" and r["strength"] == .2 and r["control"] in ("C0", "C1") and r.get("arm") != "L"]
    if len(completed) != 12 or any(r["status"] != "ok" for r in completed):
        raise ValueError("Existing .2 cells must stay completed")
    plan = [{k: r[k] for k in ("id", "phase", "source_id", "strength", "seed", "control", "arm") if k in r} for r in failed]
    if not 0 < float(run["duration_seconds"]) < 600:
        raise ValueError("Original screen exhausted shared budget")
    return run, plan


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--original-run", type=Path, default=ORIGINAL)
    args = parser.parse_args()
    old, plan = original_plan(args.original_run)
    prior = float(old["duration_seconds"])
    args.output_dir.mkdir(parents=True, exist_ok=False)
    (args.output_dir / "images").mkdir()
    rows, torch = [], None
    record = dict(schema="journal-l1-t3-completion-v1", method="L1-image-DCT", command=sys.argv,
                  commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                  original_commit=old["commit"], original_run=str(args.original_run), original_outcome=old["outcome"],
                  data_split=old["data_split"], sources=old["sources"], seeds=[0, 1, 2], usd=0,
                  profile=old["profile"], frozen_selection=old["frozen_selection"], prior_duration_seconds=prior,
                  config=dict(strengths=[.1], steps=20, cfg=1., eta=0., precision="official fp16 regenerator",
                              semantic_views=7, binding="soft", roster_size=1, h_embedded=False,
                              shared_seconds_cap=600., remaining_seconds_cap=600.-prior,
                              allocated_vram_cap_bytes=VRAM, safety_checker="required",
                              repair="register frozen .1 strength before existing official kwargs adapter",
                              no_selection_or_completed_cell_rerun=True),
                  inventory=plan, outcome="running", rows=[])

    def guard():
        if prior + time.monotonic()-STARTED >= 600:
            raise TimeoutError("Original plus completion 600-second inclusive cap exhausted")
        if torch is not None and torch.cuda.max_memory_allocated() > VRAM:
            raise TimeoutError("10 GiB allocated VRAM cap exceeded")

    def write():
        record["rows"] = rows
        record["duration_seconds"] = time.monotonic()-STARTED
        record["shared_duration_seconds"] = prior + record["duration_seconds"]
        (args.output_dir/"run.json").write_text(json.dumps(record, indent=2, allow_nan=False)+"\n", encoding="utf-8")

    def emit(item, **fields):
        row = dict(item, **fields, elapsed_seconds=time.monotonic()-STARTED)
        rows.append(row)
        with (args.output_dir/"rows.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, allow_nan=False)+"\n")
        print(json.dumps({k: row[k] for k in ("id", "status")}), flush=True)
        write()

    write()
    try:
        guard()
        import numpy as np
        import torch
        from PIL import Image
        from journal_vae_probe import Evaluator
        from journal_latent_tangent_probe import detect_rgb, native_projection, exact_checked
        from journal_readability_probe import projection_stats
        from f4_transfer_probe import ASSETS
        from f5_gate import OWNERS
        from scripts import revised_watermark_v5 as v5
        import three_threat_models as models
        torch.set_num_threads(4)
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        torch.cuda.set_per_process_memory_fraction(min(1., VRAM/torch.cuda.get_device_properties(0).total_memory))
        torch.cuda.reset_peak_memory_stats()
        models.block_network()
        # The official adapter's default strengths omitted the already frozen .1.
        models.REGEN_SETTINGS = {**models.REGEN_SETTINGS, "strengths": [.1, .2]}
        guard()
        ev = Evaluator()
        ev.reader.vae.to("cpu")  # No VAE reader participates in these calls.
        ev.lpips.to("cpu")
        guard()
        pipe = models.load_regenerator(ASSETS)
        guard()
        cached, targets, baselines, templates, source_paths, selected_paths = {}, {}, {}, {}, {}, {}

        def load(path):
            with Image.open(path) as im:
                value = np.asarray(im.convert("RGB"), np.uint8).copy()
            if value.shape != (512, 512, 3):
                raise ValueError("Retained image geometry differs")
            return value

        for sid in (1675, 468505):
            fraction = old["frozen_selection"][f"{sid}/P"]
            baseline = next(r for r in old["rows"] if r["id"] == f"baseline-{sid}-clean")
            selected = next(r for r in old["rows"] if r["id"] == f"screen-{sid}-P-{fraction}-clean")
            if baseline["status"] != "ok" or selected["status"] != "ok" or not selected["exact_checked_q"]:
                raise ValueError("Retained fixed pixels lack qualifying original records")
            source_paths[sid], selected_paths[sid] = baseline["image"], selected["image"]
            cached[sid, "C0"], cached[sid, "P"] = load(baseline["image"]), load(selected["image"])
            targets[sid] = int(selected["analysis_only"]["intended_q"], 16)
            baselines[sid] = np.asarray(native_projection(cached[sid, "C0"], OWNERS[0], old["profile"]).projections)
            checked, key, config = v5._resolve(old["profile"], None)
            table = np.asarray(v5._semantic_table(v5.canonical_owner(OWNERS[0]), key, config))
            bits = np.array([v5._bit(targets[sid], j) for j in range(32)])
            templates[sid] = table[np.arange(32), bits].reshape(-1), table[np.arange(32), bits]-table[np.arange(32), 1-bits]
        for item in plan:
            tick = time.monotonic()
            try:
                guard()
                sid, arm = item["source_id"], item.get("arm", "C0")
                rgb = cached[sid, arm]
                kwargs = models.regeneration_kwargs(.1, item["seed"], Image.fromarray(rgb), torch.Generator)
                with torch.inference_mode():
                    generated = pipe(**kwargs)
                guard()
                generated = models.validate_generated(generated)
                path = args.output_dir/"images"/f"{item['id']}.png"
                generated.save(path)
                suspect = load(path)
                features = ev.features(suspect, 7)
                calls = {o: detect_rgb(suspect, o, old["profile"], features) for o in (OWNERS[:2] if arm == "P" else OWNERS[:1])}
                fields = dict(image=str(path), source_image=source_paths[sid],
                              input_image=selected_paths[sid] if arm == "P" else source_paths[sid],
                              calls=calls, quality_source=ev.metrics(cached[sid, "C0"], suspect),
                              selected_fraction=old["frozen_selection"][f"{sid}/P"] if arm == "P" else None,
                              safety_checker_passed=True)
                if arm == "P":
                    fields["exact_checked_q"] = exact_checked(calls[OWNERS[0]], targets[sid])
                    p = np.asarray(native_projection(suspect, OWNERS[0], old["profile"]).projections)
                    w, gaps = templates[sid]
                    fields["analysis_only"] = dict(projection_stats(p, w, gaps), intended_q=f"{targets[sid]:08x}",
                        signed_chip_displacement=float(w @ (p-baselines[sid])/320),
                        projection_displacement=(p-baselines[sid]).tolist())
                guard()
                emit(item, status="ok", duration_seconds=time.monotonic()-tick, **fields)
            except (TimeoutError, torch.OutOfMemoryError):
                raise
            except Exception:
                emit(item, status="failed", error=traceback.format_exc(), duration_seconds=time.monotonic()-tick)
        record["outcome"] = "completed" if all(r["status"] == "ok" for r in rows) else "completed_with_failures"
    except Exception:
        record.update(outcome="failed", error=traceback.format_exc())
    finally:
        done = {r["id"] for r in rows}
        for item in plan:
            if item["id"] not in done:
                emit(item, status="missing", error="Not reached; budget/setup/fatal failure; see run.json")
        record["full_inventory"] = [dict(item, status=next(r["status"] for r in rows if r["id"] == item["id"])) for item in plan]
        record["failed_or_missing"] = [r["id"] for r in rows if r["status"] != "ok"]
        record["budget_overrun"] = prior + time.monotonic()-STARTED > 600
        if torch is not None and torch.cuda.is_available():
            record["gpu_peak_allocated_bytes"] = torch.cuda.max_memory_allocated()
            record["gpu_peak_reserved_bytes"] = torch.cuda.max_memory_reserved()
        if record["budget_overrun"] or record.get("gpu_peak_allocated_bytes", 0) > VRAM:
            record["outcome"] = "failed_budget"
        record["scientific_scope"] = "Technical missing-cell completion; L remains unqualified; P descriptive only; no new candidate"
        write()
    return 0 if record["outcome"] == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
