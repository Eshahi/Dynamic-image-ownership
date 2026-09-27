"""Offline retained run003 metrics worker: official exact-approved runner only."""
import argparse
import gc
import importlib.metadata
import io
import json
import os
import platform
import shutil
import socket
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.embedding import quality_package as package

STABLE = Path("/mnt/w/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5")


def fresh(path, value):
    package.unlinked(path)
    with path.open("xb") as stream:
        stream.write(package.canonical(value)); stream.flush(); os.fsync(stream.fileno())


def append_progress(journal, started, phase, **values):
    """Durable values, not just labels, survive missing terminal report."""
    journal.write(package.canonical({"phase": phase, "elapsed_seconds": time.monotonic()-started,
                                    **values}) + b"\n")
    journal.flush(); os.fsync(journal.fileno())


def run(manifest_path, output):
    started = time.monotonic()
    manifest, snapshots, pins = package.inputs(package.read(manifest_path), ROOT)
    package.unlinked(output)
    if not all((output/name).is_dir() for name in ("outputs", "logs", "checkpoints")):
        raise ValueError("existing official output directories required")
    progress = output/"logs/saved-pair-progress.jsonl"
    package.unlinked(progress)
    with progress.open("xb") as journal:
        current = {"phase": "worker_started"}
        comparisons = ["control_source", "candidate_source", "candidate_control"]
        images_expected = ["source", "control", "candidate"]
        inventory = {stage+":"+name: "pending" for stage, names in
                     (("classical", comparisons), ("codes", images_expected), ("lpips", comparisons))
                     for name in names}
        def record(phase, **values):
            if "cell" in values:
                cell, status = values["cell"], values["cell_status"]
                if cell not in inventory or status not in ("running", "completed", "failed"):
                    raise ValueError("unknown outcome cell/status")
                inventory[cell] = status
            append_progress(journal, started, phase, **values)
            current["phase"] = phase
        record("worker_started", manifest_sha256=package.sha(package.canonical(manifest)),
               expected_cells=inventory, scientific_acceptance=False,
               missing_terminal_report="interrupted-or-incomplete-never-completed")
        result = {"run_id": package.RUN, "experiment_id": package.EXPERIMENT,
                  "manifest_sha256": package.sha(package.canonical(manifest)),
                  "git_commit": manifest["git_commit"], "input_sha256": pins,
                  "quality": {}, "codes": {}, "drift": {}, "blind_detection": "NOT_RUN",
                  "cell_inventory": inventory,
                  "scientific_acceptance": False, "scope": "one-source-exploratory-local-only"}
        try:
            def blocked(*args, **kwargs): raise RuntimeError("network prohibited")
            socket.socket.connect = blocked; socket.socket.connect_ex = blocked
            socket.create_connection = blocked
            expected_env = json.loads(snapshots[package.ENV])
            actual_env = {"python": platform.python_version(),
                "versions": sorted((d.metadata["Name"], d.version) for d in importlib.metadata.distributions())}
            if package.canonical(expected_env) != package.canonical(actual_env):
                raise ValueError("exact scientific environment changed")
            result["environment"] = actual_env
            raw_images, source_enrollment = package.retained(STABLE)
            record("retained_bytes_verified", images=3)
            import numpy as np
            from PIL import Image
            import torch
            import psutil
            from src.data.preprocess import load_config, decode_source, pixel_sha, check_output_chunks
            from src.embedding.quality import classical, load_lpips, lpips_distance, target_checks, drift, PAIRS
            from src.signatures.semantic import PinnedClipEncoder, derive_ws
            from src.signatures.instance import bind_canonical_image
            config, _ = load_config(ROOT/"configs/data.json")
            images = {"source": decode_source(raw_images["source"], config)[0]}
            for name in ("control", "candidate"):
                check_output_chunks(raw_images[name])
                with Image.open(io.BytesIO(raw_images[name])) as image:
                    if image.mode != "RGB" or image.size != (500, 333) or image.format != "PNG":
                        raise ValueError("retained saved PNG profile mismatch")
                    image.load(); images[name] = np.array(image, dtype=np.uint8, copy=True)
            if any(image.shape != (333, 500, 3) or pixel_sha(image) != package.PIXELS[name]
                   for name, image in images.items()):
                raise ValueError("canonical retained pixel identity mismatch")
            record("pixels_verified", width=500, height=333)
            if not torch.cuda.is_available(): raise ValueError("CUDA unavailable")
            free, total = torch.cuda.mem_get_info()
            limit = package.RESOURCES["vram_mib"]*1024**2
            available_ram = int(next(line.split()[1] for line in Path("/proc/meminfo").read_text().splitlines()
                                     if line.startswith("MemAvailable:")))*1024
            disk = shutil.disk_usage(output).free
            if free < limit+1024*1024**2 or available_ram < 7*1024**3 or disk < 1024**3:
                raise ValueError("fixed resource headroom unavailable")
            torch.cuda.set_per_process_memory_fraction(limit/total)
            torch.cuda.reset_peak_memory_stats()
            torch.manual_seed(0)
            result["resources_initial"] = {"free_vram_bytes": free, "total_vram_bytes": total,
                "torch_limit_bytes": limit, "available_ram_bytes": available_ram,
                "free_disk_bytes": disk, "gpu": torch.cuda.get_device_name(), "cuda": torch.version.cuda}
            for label, reference, candidate in PAIRS:
                record("classical_started", comparison=label, cell="classical:"+label, cell_status="running")
                result["quality"][label] = classical(images[reference], images[candidate])
                record("classical_complete", comparison=label, metrics=result["quality"][label],
                       cell="classical:"+label, cell_status="completed")
            # Sequential models keep the frozen 4GiB estimate conservative.
            record("clip_load_started")
            encoder = PinnedClipEncoder.from_checkpoint(STABLE/package.ASSETS/"clip/ViT-B-32.pt", device="cuda")
            result["clip_identity"] = encoder.identity
            record("clip_load_completed")
            for name in ("source", "control", "candidate"):
                record("clip_phash_started", image=name, cell="codes:"+name, cell_status="running")
                features = encoder.extract_features(images[name])
                code, ws = derive_ws(features, bytes(32), package.OWNER)
                phash, keys = bind_canonical_image(images[name].tobytes(), 500, 333, code.packed, package.OWNER)
                observed = {"q": code.packed.hex(), "h": phash.packed.hex(), "Ws": ws.hex(),
                            "Wi": keys.instance.hex(), "OwnerID": keys.owner_id,
                            "semantic_projections": list(code.projections),
                            "phash_minimum_margin": phash.minimum_selected_margin}
                result["codes"][name] = observed
                if name == "source" and any(observed[k] != v for k, v in source_enrollment.items()):
                    record("source_replay_failed", image=name, observed=observed,
                           cell="codes:"+name, cell_status="failed")
                    raise ValueError("source enrollment replay failed; no relabeling")
                if name != "source":
                    result["drift"][name] = drift(bytes.fromhex(source_enrollment["q"]),
                        bytes.fromhex(source_enrollment["h"]), code.packed, phash.packed)
                record("clip_phash_complete", image=name, observed=observed,
                       drift=result["drift"].get(name), source_replay_passed=name == "source",
                       cell="codes:"+name, cell_status="completed")
            del encoder, features; gc.collect(); torch.cuda.empty_cache()
            record("lpips_load_started")
            metric = load_lpips(STABLE/package.ASSETS/"alexnet/alexnet-owt-7be5be79.pth", "cuda")
            record("lpips_load_completed")
            for label, reference, candidate in PAIRS:
                record("lpips_started", comparison=label, cell="lpips:"+label, cell_status="running")
                metrics = result["quality"][label]
                metrics["lpips_alex_v01"] = lpips_distance(metric, images[reference], images[candidate])
                metrics["target_diagnostics"] = target_checks(metrics)
                record("lpips_complete", comparison=label, metrics=metrics,
                       cell="lpips:"+label, cell_status="completed")
            torch.cuda.synchronize()
            if any(status != "completed" for status in inventory.values()):
                raise ValueError("incomplete fixed outcome inventory")
            result["status"] = "completed_diagnostic_only"
            result["resources_final"] = {"peak_torch_allocated_bytes": torch.cuda.max_memory_allocated(),
                "peak_torch_reserved_bytes": torch.cuda.max_memory_reserved(),
                "peak_worker_rss_bytes": psutil.Process().memory_info().peak_wset if sys.platform == "win32"
                   else __import__("resource").getrusage(__import__("resource").RUSAGE_SELF).ru_maxrss*1024}
            record("completed_diagnostic_only")
            code = 0
        except Exception as error:
            result["status"] = "failed_retained_partial"
            result["error_type"] = type(error).__name__
            result["failure_phase"] = current["phase"]
            result["error_message"] = str(error)[:512]
            try:
                if "torch" in locals() and torch.cuda.is_initialized():
                    result["resources_failure"] = {
                        "peak_torch_allocated_bytes": torch.cuda.max_memory_allocated(),
                        "peak_torch_reserved_bytes": torch.cuda.max_memory_reserved()}
            except Exception as resource_error:
                result["failure_resource_read_error"] = type(resource_error).__name__
            record("failed", error_type=type(error).__name__, failure_phase=result["failure_phase"],
                   error_message=result["error_message"], resources=result.get("resources_failure"))
            code = 1
        result["elapsed_seconds"] = time.monotonic()-started
        fresh(output/"outputs/saved-pair-quality.json", result)
        return code


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    raise SystemExit(run(args.manifest, args.output_dir))
