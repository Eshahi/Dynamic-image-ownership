"""Bounded M1 decoder-fit diagnosis; development metadata selection, no watermark.

Select the declared best/worst step-200 endpoints only when all twelve reserved
development cases are complete. Reset Adam and fit the unchanged, unclamped
RGB-MSE objective for 400 further updates at unscaled-latent learning rate .005.
Import and --preview do not load models, images, or torch. See the method note.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import io
import json
import math
from pathlib import Path
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
MAIN = Path("W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5")
ASSETS = MAIN / ".thesis-build/assets/a6"
for directory in (ROOT, ROOT / "scripts"):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))
from scripts import m1_latent_reconstruction as base

VERSION = "m1-reconstruction-diagnosis-v1"
UNITS = "unscaled VAE posterior mode; decoder receives same units"
CONFIG = {
    "initial_step": 200, "additional_steps": 400,
    "evaluation_total_steps": [200, 300, 400, 600],
    "optimizer": "Adam-reset", "learning_rate": .005,
    "betas": [.9, .999], "epsilon": 1e-8,
    "precision": "float32", "batch_size": 1, "size": [512, 512],
    "objective": "unclamped decoded RGB MSE to canonical source",
    "decoder_checkpoint": True, "snapshot_every": 10, "seed": 0,
    "gpu_budget_bytes": 10 * 1024**3, "run_seconds_cap": 3600,
    "selection": "complete12-step200-PSNR-extrema-ties-numeric-ID",
    "plateau_comparison_steps": [400, 600], "plateau_gain_db_lt": .25,
}


def sha(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024**2), b""):
            result.update(chunk)
    return result.hexdigest()


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def write_json(path, value):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def finite(value):
    return type(value) in (float, int) and math.isfinite(value)


def valid_hash(value):
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def psnr_value(checkpoint):
    flag = checkpoint.get("psnr_infinite", False)
    if type(flag) is not bool:
        raise ValueError("Malformed infinite-PSNR flag")
    if flag is True:
        if checkpoint.get("psnr_db") is not None or not finite(checkpoint.get("mse_rgb8")) or checkpoint["mse_rgb8"] != 0:
            raise ValueError("Inconsistent infinite-PSNR receipt")
        return math.inf
    value = checkpoint.get("psnr_db")
    if not finite(value):
        raise ValueError("Missing or nonfinite step-200 PSNR")
    if "mse_rgb8" in checkpoint and (not finite(checkpoint["mse_rgb8"]) or checkpoint["mse_rgb8"] <= 0):
        raise ValueError("Finite PSNR requires finite positive RGB8 MSE")
    return float(value)


def select_extrema(entries, expected_ids, roles):
    """Pure metadata selection. No truncation to an incomplete observed cohort."""
    if roles not in (["best", "worst"], ["best"], ["worst"]):
        raise ValueError("Explicit best/worst roles required")
    if len(entries) != len(expected_ids) or {e["id"] for e in entries} != set(expected_ids):
        raise ValueError("All twelve reserved cases must have exactly one completed endpoint")
    if len({e["id"] for e in entries}) != len(entries):
        raise ValueError("Duplicate completed endpoint; explicit input provenance must resolve it")
    best = min(entries, key=lambda entry: (-psnr_value(entry["checkpoint"]), entry["id"]))
    worst = min(entries, key=lambda entry: (psnr_value(entry["checkpoint"]), entry["id"]))
    selected = []
    for role in roles:
        entry = best if role == "best" else worst
        same = next((row for row in selected if row["id"] == entry["id"]), None)
        if same is None:
            selected.append({**entry, "selection_roles": [role]})
        else:
            same["selection_roles"].append(role)
    return selected


def validate_manifest(manifest):
    required = {"schema_version", "experiment_id", "data_split", "cohort_manifest",
                "input_runs", "case_roles", "config"}
    if set(manifest) != required or manifest["schema_version"] != VERSION or manifest["data_split"] != "development":
        raise ValueError("Only the exact versioned development manifest is allowed")
    if manifest["config"] != CONFIG:
        raise ValueError("Fixed diagnosis configuration differs")
    if manifest["case_roles"] not in (["best", "worst"], ["best"], ["worst"]):
        raise ValueError("Roles must be best/worst, or one explicit recovery shard")
    cohort = (ROOT / manifest["cohort_manifest"]).resolve()
    if cohort != (ROOT / "research/m1-reconstruction-dev.json").resolve():
        raise ValueError("Only the reserved twelve-source development cohort is allowed")
    cohort_manifest = json.loads(cohort.read_text(encoding="utf-8"))
    if cohort_manifest.get("data_split") != "development":
        raise ValueError("Cohort is not development data")
    cases = base.cases_for(cohort_manifest)
    if {c["id"] for c in cases} != set(base.IDS) or len(cases) != len(base.IDS):
        raise ValueError("Full reserved twelve-source cohort is required for selection")
    paths = [Path(p).resolve() for p in manifest["input_runs"]]
    if not paths or len(set(paths)) != len(paths):
        raise ValueError("Explicit unique source run directories required")
    if any(not p.is_relative_to((MAIN / ".thesis-build/dev-runs").resolve()) for p in paths):
        raise ValueError("Input runs must be retained local development runs")
    return cases, paths, cohort


def collect_inventory(cases, run_snapshots):
    """Combine disjoint completed cases, retaining ignored incomplete receipts.

    run_snapshots is [(absolute_run_directory, parsed_run_json), ...]. The caller
    reads each JSON once and preserves the exact bytes in a new run directory.
    """
    by_id = {c["id"]: c for c in cases}
    entries, ignored = [], []
    for directory, record in run_snapshots:
        directory = Path(directory)
        if (record.get("schema_version") != "m1-development-run-v1"
                or record.get("data_split") != "development"
                or record.get("config") != base.CONFIG or record.get("latent_units") != UNITS):
            raise ValueError("Input run is not the pinned unscaled development reconstruction")
        commit = record.get("commit")
        if not isinstance(commit,str) or len(commit) not in (40,64) or any(c not in "0123456789abcdef" for c in commit):
            raise ValueError("Input run is missing its exact Git commit")
        seen = set()
        for row in record.get("cases", []):
            ident = row.get("id")
            if type(ident) is not int or ident not in by_id or ident in seen:
                raise ValueError("Unreserved or duplicate case in source run")
            seen.add(ident)
            if row.get("outcome") != "completed":
                ignored.append({"id": ident, "run": str(directory), "outcome": row.get("outcome")})
                continue
            points = [p for p in row.get("checkpoints", []) if p.get("step") == CONFIG["initial_step"]]
            if len(points) != 1:
                raise ValueError("Completed source lacks exactly one step-200 endpoint")
            point = points[0]
            psnr_value(point)
            if row.get("raw_sha256") != by_id[ident]["sha256"] or not valid_hash(row.get("source_rgb8_sha256")):
                raise ValueError("Source receipt differs from reserved development identity")
            if not all(valid_hash(point.get(k)) for k in ("latent_sha256", "png_sha256")):
                raise ValueError("Missing endpoint artifact hashes")
            entries.append({"id": ident, "source_case": by_id[ident], "run_directory": str(directory),
                            "input_run_commit": record.get("commit"), "source_rgb8_sha256": row["source_rgb8_sha256"],
                            "input_run_outcome": record.get("outcome"), "checkpoint": point,
                            "latent_path": str(directory / f"{ident}-step200.pt"),
                            "png_path": str(directory / f"{ident}-step200.png")})
    counts = {ident: sum(e["id"] == ident for e in entries) for ident in by_id}
    missing = [ident for ident, count in counts.items() if count == 0]
    duplicate = [ident for ident, count in counts.items() if count > 1]
    if missing or duplicate:
        raise ValueError(f"Inventory not ready: missing={sorted(missing)}, duplicate_completed={sorted(duplicate)}")
    return sorted(entries, key=lambda e: e["id"]), ignored


def load_inventory(manifest):
    cases, paths, cohort = validate_manifest(manifest)
    snapshots = []
    for directory in paths:
        raw = (directory / "run.json").read_bytes()
        record = json.loads(raw)
        snapshots.append({"directory": directory, "raw": raw, "record": record,
                          "sha256": hashlib.sha256(raw).hexdigest()})
    entries, ignored = collect_inventory(cases, [(s["directory"], s["record"]) for s in snapshots])
    selected = select_extrema(entries, [c["id"] for c in cases], manifest["case_roles"])
    return entries, selected, ignored, snapshots, cohort


def verify_artifacts(entries):
    receipts = []
    for entry in entries:
        for kind in ("latent", "png"):
            path = Path(entry[kind + "_path"])
            expected = entry["checkpoint"][kind + "_sha256"]
            if sha(path) != expected:
                raise ValueError(f"Source {kind} artifact hash mismatch: {path}")
            receipts.append({"id": entry["id"], "kind": kind, "path": str(path),
                             "sha256": expected, "size_bytes": path.stat().st_size})
    return receipts


def require_committed(paths):
    result = {}
    for path in paths:
        path = Path(path).resolve()
        relative = path.relative_to(ROOT).as_posix()
        expected = subprocess.check_output(["git", "rev-parse", "HEAD:" + relative], cwd=ROOT, text=True).strip()
        observed = subprocess.check_output(["git", "hash-object", "--path=" + relative, str(path)], cwd=ROOT, text=True).strip()
        if expected != observed:
            raise ValueError("Scientific input differs from HEAD: " + relative)
        result[relative] = {"git_blob_oid": expected, "working_sha256": sha(path)}
    return result


def source_rgb(case):
    import numpy as np
    from PIL import Image, ImageOps, ImageCms
    if sha(case["path"]) != case["sha256"]:
        raise ValueError("Reserved source raw hash mismatch")
    with Image.open(case["path"]) as image:
        if image.mode != "RGB":
            raise ValueError("Only RGB sources allowed")
        image.load()
        icc = image.info.get("icc_profile")
        image = ImageOps.exif_transpose(image)
        if icc:
            image = ImageCms.profileToProfile(image, ImageCms.ImageCmsProfile(io.BytesIO(icc)),
                ImageCms.createProfile("sRGB"), renderingIntent=0, outputMode="RGB", flags=0)
        return np.asarray(image.resize((512, 512), Image.Resampling.BICUBIC), dtype=np.uint8).copy()


def load_start(entry):
    import torch
    if sha(entry["latent_path"]) != entry["checkpoint"]["latent_sha256"]:
        raise ValueError("Selected latent changed after input verification")
    state = torch.load(entry["latent_path"], map_location="cpu", weights_only=True)
    if not isinstance(state, dict):
        raise ValueError("Starting checkpoint must contain a receipt dictionary")
    if state.get("step") != 200 or state.get("latent_units") != UNITS:
        raise ValueError("Latent step/units mismatch")
    z = state.get("z")
    if not isinstance(z, torch.Tensor) or z.dtype != torch.float32 or tuple(z.shape) != (1, 4, 64, 64) or not bool(torch.isfinite(z).all()):
        raise ValueError("Invalid starting latent")
    return z


def cpu_state(value):
    import torch
    if isinstance(value, torch.Tensor):
        return value.detach().cpu().clone()
    if isinstance(value, dict):
        return {key: cpu_state(item) for key, item in value.items()}
    if isinstance(value, list):
        return [cpu_state(item) for item in value]
    if isinstance(value, tuple):
        return tuple(cpu_state(item) for item in value)
    return value


def fit_additional(vae, target, initial, config, event, measure, snapshot, deadline=None):
    """Only z is trainable; mockable CPU kernel, no image/file policy inside it."""
    import torch
    from torch.utils.checkpoint import checkpoint
    vae.eval().requires_grad_(False)
    z = initial.detach().to(target.device).float().clone().requires_grad_(True)
    optimizer = torch.optim.Adam([z], lr=config["learning_rate"], betas=tuple(config["betas"]), eps=config["epsilon"])
    started = time.monotonic()
    def decode(latent):
        return (vae.decode(latent, return_dict=False)[0].float() + 1) / 2
    for offset in range(config["additional_steps"] + 1):
        total_step = config["initial_step"] + offset
        if deadline is not None and time.monotonic() >= deadline:
            raise RuntimeError("Diagnosis wall-time cap reached; prior snapshots retained")
        if total_step in config["evaluation_total_steps"]:
            with torch.no_grad():
                raw = decode(z)
                if not bool(torch.isfinite(raw).all()):
                    raise RuntimeError("Nonfinite decoder measurement")
                measure(total_step, z.detach(), raw, float((raw-target).square().mean()))
                del raw
        if offset == config["additional_steps"]:
            break
        optimizer.zero_grad(set_to_none=True)
        decoded = checkpoint(decode, z, use_reentrant=False) if config["decoder_checkpoint"] else decode(z)
        loss = (decoded-target).square().mean()
        if not bool(torch.isfinite(loss)):
            raise RuntimeError("Nonfinite unclamped reconstruction loss")
        loss.backward()
        if z.grad is None or not bool(torch.isfinite(z.grad).all()):
            raise RuntimeError("Missing/nonfinite reconstruction gradient")
        row = {"phase": "update", "total_step": total_step + 1, "additional_step": offset + 1,
               "loss_before_update": float(loss.detach()), "latent_gradient_l2": float(torch.linalg.vector_norm(z.grad)),
               "seconds": time.monotonic() - started}
        optimizer.step()
        if not bool(torch.isfinite(z).all()):
            raise RuntimeError("Nonfinite updated latent")
        del loss, decoded
        event(row)
        if (offset+1) % config["snapshot_every"] == 0 or offset+1 == config["additional_steps"]:
            snapshot(total_step+1, z.detach(), optimizer)
        if z.device.type == "cuda" and torch.cuda.memory_allocated() > config["gpu_budget_bytes"]:
            raise RuntimeError("GPU allocation cap exceeded")
    return z.detach(), {"additional_updates": config["additional_steps"],
        "total_step": config["initial_step"] + config["additional_steps"],
        "selection": "last-fixed-step", "optimizer_start": "reset-Adam-at-step200",
        "latent_displacement_from_step200_l2": float(torch.linalg.vector_norm(z.detach()-initial.to(z.device))),
        "seconds": time.monotonic() - started}


def comparison(checkpoints):
    by_step = {c["step"]: c for c in checkpoints}
    if any(step not in by_step for step in (200, 400, 600)):
        return {"complete": False, "plateau": None, "interpretation": "incomplete fixed checkpoints"}
    values = {step: psnr_value(by_step[step]) for step in (200, 400, 600)}
    def gain(after, before):
        result = values[after] - values[before]
        return result if math.isfinite(result) else None
    late = gain(600, 400)
    return {"complete": True, "psnr_gain_200_to_600_db": gain(600, 200),
            "psnr_gain_400_to_600_db": late,
            "plateau": late < CONFIG["plateau_gain_db_lt"] if late is not None else None,
            "final_quality_admissible": by_step[600].get("quality_admissible"),
            "interpretation": "finite optimizer endpoint; no certified decoder floor"}


def _run_verified(manifest_path, output):
    started = time.monotonic()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries, selected, ignored, snapshots, cohort = load_inventory(manifest)
    if not output.resolve().is_relative_to((MAIN / ".thesis-build/dev-runs").resolve()):
        raise ValueError("Output must be a new authoritative development run directory")
    dependencies = [Path(__file__), manifest_path, cohort, Path(base.__file__),
        ROOT / "scripts/three_threat_models.py", ROOT / "scripts/three_threat_protocol.py",
        ROOT / "scripts/check_a6_lpips_assets.py", ROOT / "scripts/verify_science_assets.py",
        ROOT / "research/a6-candidate-model-assets.json",
        ROOT / "experiments/c4-qim-rgb-development-v1/cohort.json",
        ROOT / "experiments/c4-three-threat-small-v1/development-expansion.json"]
    committed = require_committed(dependencies)
    artifacts = verify_artifacts(entries)
    (output / "input-snapshots").mkdir()
    source_runs = []
    for index, item in enumerate(snapshots):
        path = output / "input-snapshots" / f"source-run-{index}.json"
        path.write_bytes(item["raw"])
        source_runs.append({"directory": str(item["directory"]), "snapshot_path": str(path), "sha256": item["sha256"]})
    record = {"schema_version": "m1-development-run-v1", "method": VERSION,
        "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "command": sys.argv, "manifest_sha256": sha(manifest_path), "config": CONFIG,
        "config_sha256": canonical_hash(CONFIG), "seeds": [CONFIG["seed"]], "data_split": "development",
        "committed_files": committed, "input_runs": source_runs, "input_artifacts": artifacts,
        "selection_inventory": entries, "selected": selected, "ignored_incomplete_receipts": ignored,
        "duration_seconds": 0, "outcome": "started", "cases": [], "environment": {"python": sys.version},
        "latent_units": UNITS, "label": "Adaptive development extremum diagnosis; no watermark or global floor claim"}
    write_json(output / "run.json", record)
    def event(value):
        with (output / "journal.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(value, allow_nan=False) + "\n")
    try:
        from scripts.three_threat_models import block_network, load_lpips, lpips_score
        from scripts.check_a6_lpips_assets import verify_package
        block_network()
        import numpy as np
        import torch
        from diffusers import AutoencoderKL
        from PIL import Image
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA unavailable; no silent CPU scientific run")
        torch.manual_seed(CONFIG["seed"])
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        torch.backends.cudnn.benchmark = False
        torch.cuda.set_per_process_memory_fraction(min(1, CONFIG["gpu_budget_bytes"] / torch.cuda.get_device_properties(0).total_memory))
        record["environment"].update({p: importlib.metadata.version(p) for p in ("torch", "numpy", "scipy", "Pillow", "diffusers", "lpips")})
        record["environment"]["gpu"] = torch.cuda.get_device_name(0)
        lock = json.loads((ROOT / "research/a6-candidate-model-assets.json").read_text())
        assets = [item for item in lock["files"] if item["path"].startswith(("sd15-fp16/vae/", "alexnet/"))]
        for item in assets:
            path = ASSETS / item["path"]
            if path.stat().st_size != item["size_bytes"] or sha(path) != item["sha256"]:
                raise ValueError("Model asset mismatch: " + item["path"])
        record["asset_files"] = assets
        package = Path(importlib.metadata.distribution("lpips").locate_file("lpips"))
        verify_package(package)
        metric = load_lpips(ASSETS, package)
        record["lpips_learned_sha256"] = sha(package / "weights/v0.1/alex.pth")
        vae = AutoencoderKL.from_pretrained(ASSETS / "sd15-fp16/vae", variant="fp16", use_safetensors=True,
            local_files_only=True, torch_dtype=torch.float32).eval().requires_grad_(False).to("cuda")
        record["vae_scaling_factor"] = float(vae.config.scaling_factor)
        for entry in selected:
            ident = entry["id"]
            row = {"id": ident, "selection_roles": entry["selection_roles"], "outcome": "started",
                   "checkpoints": [], "snapshots": [], "initialization": entry}
            record["cases"].append(row)
            write_json(output / "run.json", record)
            event({"phase": "case_started", "id": ident, "roles": entry["selection_roles"]})
            source = source_rgb(entry["source_case"])
            pixel_hash = hashlib.sha256(source.tobytes()).hexdigest()
            if pixel_hash != entry["source_rgb8_sha256"]:
                raise ValueError("Canonical source differs from original reconstruction")
            row.update(raw_sha256=entry["source_case"]["sha256"], source_rgb8_sha256=pixel_hash)
            source_path = output / f"{ident}-source.png"
            Image.fromarray(source).save(source_path)
            row.update(source_png=str(source_path), source_png_sha256=sha(source_path))
            initial = load_start(entry).to("cuda")
            target = torch.from_numpy(source).permute(2, 0, 1)[None].float().to("cuda") / 255
            def measure(step, z, raw, float_mse):
                stem = f"{ident}-step{step:03d}"
                png, latent_path = output / (stem+".png"), output / (stem+".pt")
                rgb = (raw[0].permute(1, 2, 0).clamp(0, 1).cpu().numpy()*255).round().astype(np.uint8)
                Image.fromarray(rgb).save(png)
                with Image.open(png) as saved:
                    rgb = np.asarray(saved.convert("RGB"), dtype=np.uint8).copy()
                torch.save({"z": z.cpu(), "step": step, "latent_units": UNITS,
                            "source_rgb8_sha256": pixel_hash}, latent_path)
                point = {"step": step, "additional_step": step-200, "objective_float_mse": float_mse,
                    **base.quality(source, rgb), "lpips": lpips_score(metric, source, rgb),
                    "png_path": str(png), "png_sha256": sha(png), "latent_path": str(latent_path),
                    "latent_sha256": sha(latent_path), "seconds": time.monotonic()-started}
                point["quality_admissible"] = (point["psnr_infinite"] or point["psnr_db"] > 35) and point["ssim_rgb"] > .9 and point["lpips"] < .1
                row["checkpoints"].append(point)
                if step == 200:
                    point["reproduces_source_png"] = point["png_sha256"] == entry["checkpoint"]["png_sha256"]
                    # Compare pixels rather than compressed PNG bytes across writers.
                    with Image.open(entry["png_path"]) as prior:
                        point["baseline_max_abs_rgb8_drift"] = int(np.abs(np.asarray(prior.convert("RGB"), dtype=np.int16)-rgb.astype(np.int16)).max())
                    if point["baseline_max_abs_rgb8_drift"] > 0:
                        raise ValueError("Starting checkpoint decoder does not reproduce the prior saved pixels")
                event({"phase": "measurement", "id": ident, **point})
                write_json(output / "run.json", record)
            def snapshot(step, z, optimizer):
                path = output / f"{ident}-restart-step{step:03d}.pt"
                temporary = path.with_suffix(".pt.tmp")
                torch.save({"schema_version": VERSION, "z": z.cpu(), "optimizer": cpu_state(optimizer.state_dict()),
                    "total_step": step, "additional_step": step-200, "latent_units": UNITS,
                    "config_sha256": record["config_sha256"], "source_rgb8_sha256": pixel_hash,
                    "initial_latent_sha256": entry["checkpoint"]["latent_sha256"],
                    "torch_rng_cpu": torch.get_rng_state(), "torch_rng_cuda": [x.cpu() for x in torch.cuda.get_rng_state_all()]}, temporary)
                temporary.replace(path)
                receipt = {"step": step, "path": str(path), "sha256": sha(path)}
                row["snapshots"].append(receipt)
                event({"phase": "restart_snapshot", "id": ident, **receipt})
                write_json(output / "run.json", record)
            torch.cuda.reset_peak_memory_stats()
            terminal, info = fit_additional(vae, target, initial, CONFIG,
                lambda value: event({"id": ident, **value}), measure, snapshot,
                deadline=started+CONFIG["run_seconds_cap"])
            row.update(outcome="completed", optimization=info, comparison=comparison(row["checkpoints"]),
                       peak_allocated_bytes=torch.cuda.max_memory_allocated())
            write_json(output / f"{ident}-result.json", row)
            write_json(output / "run.json", record)
            del target, initial, terminal
            torch.cuda.empty_cache()
        record["outcome"] = "completed"
    except (Exception, KeyboardInterrupt) as error:
        outcome = "interrupted" if isinstance(error, KeyboardInterrupt) else "failed"
        record.update(outcome=outcome, error=str(error) or type(error).__name__, traceback=traceback.format_exc())
        if record["cases"] and record["cases"][-1]["outcome"] == "started":
            record["cases"][-1].update(outcome=outcome, error=record["error"])
        event({"phase": "run_"+outcome, "error": record["error"]})
    finally:
        attempted = {row["id"] for row in record["cases"]}
        for entry in selected:
            if entry["id"] not in attempted:
                record["cases"].append({"id": entry["id"], "selection_roles": entry["selection_roles"], "outcome": "not_attempted_after_stop"})
        record["duration_seconds"] = time.monotonic()-started
        write_json(output / "run.json", record)
    return 0 if record["outcome"] == "completed" else 1


def run(manifest_path, output):
    """Create an initial receipt before preflight; refuse existing run outputs."""
    manifest_path, output = Path(manifest_path).resolve(), Path(output).resolve()
    if not output.is_relative_to((MAIN / ".thesis-build/dev-runs").resolve()):
        raise ValueError("Output must be a new authoritative development run directory")
    output.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    initial = {"schema_version": "m1-development-run-v1", "method": VERSION,
        "command": sys.argv, "config": CONFIG, "data_split": "development", "seeds": [CONFIG["seed"]],
        "manifest_path": str(manifest_path), "manifest_sha256": None,
        "duration_seconds": 0, "outcome": "started", "phase": "preflight", "cases": []}
    write_json(output / "run.json", initial)
    try:
        if manifest_path.is_file(): initial["manifest_sha256"] = sha(manifest_path)
        initial["commit"] = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        write_json(output / "run.json", initial)
        return _run_verified(manifest_path, output)
    except (Exception, KeyboardInterrupt) as error:
        initial.update(outcome="interrupted" if isinstance(error, KeyboardInterrupt) else "failed",
            failure_phase="preflight_or_setup", error=str(error) or type(error).__name__,
            traceback=traceback.format_exc(), duration_seconds=time.monotonic()-started)
        write_json(output / "run.json", initial)
        with (output / "journal.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"phase": "run_"+initial["outcome"], "error": initial["error"],
                "failure_phase": initial["failure_phase"]}, allow_nan=False)+"\n")
        return 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--preview", action="store_true", help="Metadata selection only; no images, latent tensors, models or GPU")
    args = parser.parse_args()
    if args.preview:
        if args.output_dir is not None:
            parser.error("--preview must not have --output-dir")
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        try:
            entries, selected, ignored, snapshots, _ = load_inventory(manifest)
        except ValueError as error:
            print(json.dumps({"ready": False, "reason": str(error)}))
            return 2
        print(json.dumps({"ready": True, "complete_reserved_cases": len(entries),
            "selected": [{"id": e["id"], "roles": e["selection_roles"], "psnr_db": e["checkpoint"]["psnr_db"],
                "psnr_infinite": e["checkpoint"].get("psnr_infinite", False), "input_run": e["run_directory"]} for e in selected],
            "input_snapshot_hashes": [s["sha256"] for s in snapshots], "ignored_incomplete_receipts": ignored}, indent=2))
        return 0
    if args.output_dir is None:
        parser.error("--output-dir is required unless --preview")
    return run(args.manifest.resolve(), args.output_dir.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
