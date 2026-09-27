"""Offline refined-target scientific worker; exact official approval required."""
import argparse
import gc
import importlib.metadata
import os
import platform
import shutil
import socket
import sys
import time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.embedding import refinement_package as package
from src.embedding import quality_package as custody
from scripts.c4_saved_pair import fresh, failed_cells
STABLE = Path("/mnt/w/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5")
STATE_QUOTA = 64*1024**2
JOURNAL_QUOTA = 8*1024**2


def cells():
    return {**{stage+":"+arm: "pending" for stage in ("render", "safety", "lpips", "codes")
               for arm in package.ARMS}, "codes:source": "pending"}


def persist_state(directory, counter, arm, row, state, record):
    """Exclusive generated-tensor safetensors, fixed quota, durable hash record."""
    if arm not in (*package.ARMS, "shared_encoded") or counter[0] >= 1024:
        raise ValueError("state name/count exceeds fixed inventory")
    from safetensors.torch import save
    raw = save({"latent": state.detach().cpu().contiguous()})
    if len(raw) > 4*1024**2 or counter[1]+len(raw) > STATE_QUOTA:
        raise ValueError("state storage quota exceeded; no deletion or retry")
    name = f"{counter[0]:06d}-{arm}.safetensors"
    target = custody.unlinked(directory/name)
    with target.open("xb") as stream:
        stream.write(raw); stream.flush(); os.fsync(stream.fileno())
    counter[0] += 1; counter[1] += len(raw)
    record("latent_state_saved", arm=arm, row=row, state_path="checkpoints/refinement-states/"+name,
           state_sha256=custody.sha(raw), size_bytes=len(raw), total_state_bytes=counter[1])


def run(manifest_path, output):
    started = time.monotonic()
    manifest, snapshots, pins = package.inputs(custody.read(manifest_path), ROOT)
    custody.unlinked(output)
    if not all((output/name).is_dir() for name in ("outputs", "logs", "checkpoints")):
        raise ValueError("official artifact directories required")
    inventory = cells(); current = {"phase": "worker_started"}
    result = {"run_id": package.RUN, "experiment_id": package.EXPERIMENT,
        "git_commit": manifest["git_commit"], "manifest_sha256": custody.sha(custody.canonical(manifest)),
        "input_sha256": pins, "cell_inventory": inventory, "arms": {}, "codes": {}, "drift": {},
        "scope": "one-source-exploratory-refined-target-no-watermark-or-blind-detection",
        "scientific_acceptance": False, "blind_detection": "NOT_RUN"}
    with custody.unlinked(output/"logs/refinement-progress.jsonl").open("xb") as journal:
        def record(phase, **values):
            if "cell" in values:
                cell, status = values["cell"], values["cell_status"]
                allowed = {"pending": "running", "running": "completed"}
                if cell not in inventory or (status != "failed" and allowed.get(inventory[cell]) != status):
                    raise ValueError("invalid fixed cell transition")
                inventory[cell] = status
            payload = custody.canonical({"phase": phase, "elapsed_seconds": time.monotonic()-started, **values})+b"\n"
            # Reserve room for bounded failure/cell records when the normal
            # trajectory hits its quota; do not recursively fail the failure log.
            ceiling = JOURNAL_QUOTA if phase in {"failed", "cell_failed"} else JOURNAL_QUOTA-64*1024
            if journal.tell()+len(payload) > ceiling:
                raise ValueError("journal quota exceeded")
            journal.write(payload); journal.flush(); os.fsync(journal.fileno())
            current["phase"] = phase
        record("worker_started", expected_cells=dict(inventory),
               missing_terminal_report="interrupted-incomplete-never-completed")
        try:
            for name in ("HF_HUB_OFFLINE", "TRANSFORMERS_OFFLINE", "DIFFUSERS_OFFLINE"):
                if os.environ.get(name) != "1": raise ValueError("offline flags absent")
            if os.environ.get("CUBLAS_WORKSPACE_CONFIG") != ":4096:8": raise ValueError("determinism flag absent")
            def blocked(*args, **kwargs): raise RuntimeError("network prohibited")
            socket.socket.connect = blocked; socket.socket.connect_ex = blocked; socket.create_connection = blocked
            actual = {"python": platform.python_version(), "versions": sorted(
                (distribution.metadata["Name"], distribution.version) for distribution in importlib.metadata.distributions())}
            if custody.canonical(actual) != custody.canonical(custody.strict_json_bytes(snapshots[custody.ENV])):
                raise ValueError("pinned scientific environment changed")
            result["environment"] = actual
            from src.embedding.validation_bridge import consume_validation_receipt
            loaded = consume_validation_receipt(manifest_path, output/"checkpoints", root=ROOT)
            raw_images, enrollment = custody.retained(STABLE)
            import torch
            from src.data.preprocess import load_config, decode_source, pixel_sha, normalized, encode_output
            from src.embedding.local_assets import plan_assets, snapshot_assets, load_snapshot
            from src.embedding.residency import PhaseResidency
            from src.embedding.proposed import latent_streams, padded_source
            from src.embedding.refinement_comparison import comparison
            from src.embedding.quality import classical, load_lpips, lpips_distance, target_checks, drift
            from src.signatures.semantic import PinnedClipEncoder, derive_ws
            from src.signatures.instance import bind_canonical_image
            config, _ = load_config(ROOT/"configs/data.json")
            source = decode_source(raw_images["source"], config)[0]
            if source.shape != (333, 500, 3) or pixel_sha(source) != custody.PIXELS["source"]:
                raise ValueError("retained source canonical identity changed")
            if not torch.cuda.is_available(): raise ValueError("CUDA unavailable")
            free, total = torch.cuda.mem_get_info(); limit = package.RESOURCES["vram_mib"]*1024**2
            available = int(next(line.split()[1] for line in Path("/proc/meminfo").read_text().splitlines()
                                 if line.startswith("MemAvailable:")))*1024
            disk = shutil.disk_usage(output).free
            result["resources_initial"] = {"free_vram_bytes": free, "total_vram_bytes": total,
                "torch_limit_bytes": limit, "available_ram_bytes": available, "free_disk_bytes": disk,
                "gpu": torch.cuda.get_device_name(), "cuda": torch.version.cuda}
            record("resource_headroom_measured", resources=result["resources_initial"])
            if free < limit+1024**3 or available < 13*1024**3 or disk < 4*1024**3:
                raise ValueError("fixed resource headroom unavailable")
            torch.cuda.set_per_process_memory_fraction(limit/total); torch.cuda.reset_peak_memory_stats()
            torch.use_deterministic_algorithms(True); torch.backends.cuda.matmul.allow_tf32 = False
            torch.backends.cudnn.allow_tf32 = False; torch.backends.cudnn.benchmark = False; torch.manual_seed(0)
            plan = plan_assets(ROOT/"research/a6-candidate-model-assets.json")
            snapshot = snapshot_assets(STABLE/custody.ASSETS, output/"checkpoints", plan)
            record("sd_load_started")
            models = load_snapshot(loaded, plan, snapshot, device="cuda", progress=lambda row: record(**row),
                                   activation_checkpointing=True)
            result["model_identity"] = models.identity; record("sd_load_completed", identity=models.identity)
            residency = PhaseResidency(models, progress=lambda row: record(**row)); residency.park_idle()
            tensor = torch.from_numpy(normalized(source).transpose(2, 0, 1).copy()).unsqueeze(0).to("cuda")
            padded = padded_source(tensor, models.components.settings.maximum_side)
            base, semantic_carrier, instance_carrier = latent_streams(0, bytes.fromhex(custody.FILES["source"][2]),
                bytes.fromhex(enrollment["Ws"]), bytes.fromhex(enrollment["Wi"]),
                bytes.fromhex(loaded.value["dct"]["config_id"]), padded.shape[-2]//8, padded.shape[-1]//8, tensor.device)
            del semantic_carrier, instance_carrier
            pixels = {}; states = [0, 0]
            state_dir = custody.unlinked(output/"checkpoints/refinement-states"); state_dir.mkdir()
            def progress(row):
                phase = row["phase"]
                if phase == "refinement_comparison_arm_started":
                    record(phase, arm=row["arm"], cell="render:"+row["arm"], cell_status="running")
                elif phase == "refinement_comparison_arm_saved":
                    record(phase, arm=row["arm"], component_outcome=row["outcome"],
                           cell="render:"+row["arm"], cell_status="completed")
                elif phase == "refinement_comparison_arm_failed":
                    result["arms"][row["arm"]] = {"component_outcome": row["outcome"], "png_status": "NOT_RENDERED"}
                    record(phase, arm=row["arm"], outcome=result["arms"][row["arm"]],
                           cell="render:"+row["arm"], cell_status="failed")
                else: record(**row)
            def save_arm(arm, image, metadata):
                native = image[0].permute(1, 2, 0).detach().cpu().numpy()
                raw, decoded = encode_output(native)
                path = custody.unlinked(output/"outputs"/(arm+".png"))
                with path.open("xb") as stream: stream.write(raw); stream.flush(); os.fsync(stream.fileno())
                pixels[arm] = decoded
                result["arms"][arm] = {"png_sha256": custody.sha(raw), "pixel_sha256": pixel_sha(decoded),
                    "native_hwc": list(decoded.shape), "quality_source": classical(source, decoded),
                    "component_outcome": metadata, "safety_status": "NOT_RUN"}
                record("saved_arm_partial", arm=arm, outcome=result["arms"][arm])
            outcome = comparison(models.components, tensor, base, package.policy(snapshots[package.POLICY]),
                progress=progress, save_arm=save_arm,
                save_state=lambda arm, row, state: persist_state(state_dir, states, arm, row, state, record))
            # A terminal-named journal row is not completion: only normal return,
            # consistent final report and official runner outcome count.
            result["composition"] = outcome
            result["matched_control_pixel_replay"] = result["arms"]["ddim_fixed_base_noise"]["pixel_sha256"] == custody.PIXELS["control"]
            record("matched_control_replay", passed=result["matched_control_pixel_replay"])
            if not result["matched_control_pixel_replay"]: raise ValueError("historical control replay differs; no relabel")
            residency.prepare_safety()
            for arm in package.ARMS:
                if arm not in pixels: continue
                record("safety_started", cell="safety:"+arm, cell_status="running")
                flag = models.check_saved_pixels(pixels[arm])
                result["arms"][arm].update(safety_flagged=flag, safety_status="flagged" if flag else "unflagged")
                record("safety_observed", arm=arm, flagged=flag)
                if flag: raise ValueError("diagnostic safety flagged; restricted outputs retained")
                record("safety_completed", cell="safety:"+arm, cell_status="completed")
            del models, residency, tensor, padded, base; gc.collect(); torch.cuda.empty_cache()
            record("clip_load_started")
            encoder = PinnedClipEncoder.from_checkpoint(STABLE/custody.ASSETS/"clip/ViT-B-32.pt", device="cuda")
            result["clip_identity"] = encoder.identity; record("clip_load_completed")
            for name, image in (("source", source), *[(arm, pixels[arm]) for arm in package.ARMS if arm in pixels]):
                record("codes_started", cell="codes:"+name, cell_status="running")
                features = encoder.extract_features(image)
                code, ws = derive_ws(features, bytes(32), custody.OWNER)
                phash, keys = bind_canonical_image(image.tobytes(), 500, 333, code.packed, custody.OWNER)
                observed = {"q": code.packed.hex(), "h": phash.packed.hex(), "Ws": ws.hex(),
                    "Wi": keys.instance.hex(), "OwnerID": keys.owner_id,
                    "semantic_projections": list(code.projections), "phash_minimum_margin": phash.minimum_selected_margin}
                result["codes"][name] = observed
                if name == "source" and any(observed[k] != value for k, value in enrollment.items()):
                    raise ValueError("source enrollment replay differs; no relabel")
                if name != "source": result["drift"][name] = drift(bytes.fromhex(enrollment["q"]),
                    bytes.fromhex(enrollment["h"]), code.packed, phash.packed)
                record("codes_completed", cell="codes:"+name, cell_status="completed", observed=observed,
                       drift=result["drift"].get(name))
            del encoder, features; gc.collect(); torch.cuda.empty_cache()
            record("lpips_load_started")
            metric = load_lpips(STABLE/custody.ASSETS/"alexnet/alexnet-owt-7be5be79.pth", "cuda")
            record("lpips_load_completed")
            for arm in package.ARMS:
                if arm not in pixels: continue
                record("lpips_started", cell="lpips:"+arm, cell_status="running")
                metrics = result["arms"][arm]["quality_source"]
                metrics["lpips_alex_v01"] = lpips_distance(metric, source, pixels[arm])
                metrics["target_diagnostics"] = target_checks(metrics)
                record("lpips_completed", cell="lpips:"+arm, cell_status="completed", metrics=metrics)
            torch.cuda.synchronize()
            if outcome["failed_arms"]: raise ValueError("retained nonconverged inverse arms; package incomplete")
            if any(status != "completed" for status in inventory.values()): raise ValueError("incomplete fixed cells")
            result["status"] = "completed_refined_target_diagnostic_only"; code = 0
            record("completed_refined_target_diagnostic_only")
        except Exception as error:
            result.update(status="failed_retained_partial", error_type=type(error).__name__,
                          error_message=str(error)[:512], failure_phase=current["phase"]); code = 1
            for cell in failed_cells(inventory):
                record("cell_failed", cell=cell, cell_status="failed", error_type=type(error).__name__)
            record("failed", error_type=type(error).__name__, failure_phase=result["failure_phase"])
        try:
            if "torch" in locals() and torch.cuda.is_initialized():
                result["resources_final"] = {"peak_torch_allocated_bytes": torch.cuda.max_memory_allocated(),
                    "peak_torch_reserved_bytes": torch.cuda.max_memory_reserved(),
                    "peak_worker_rss_bytes": __import__("resource").getrusage(__import__("resource").RUSAGE_SELF).ru_maxrss*1024}
        except Exception as error: result["resource_read_error"] = type(error).__name__
        result["elapsed_seconds"] = time.monotonic()-started
        fresh(output/"outputs/refinement.json", result)
        return code


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path); parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args(); raise SystemExit(run(args.manifest, args.output_dir))
