"""One offline C4 development trial through the exact-approved runner only.

No approval writer, scheduling, downloads, retries or threshold decisions.
Import is model-free. Owned tests may inject operations; production CLI cannot.
"""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import platform
import shutil
import socket
import time
from pathlib import Path

from src.runtime.config import PROJECT, strict_json_bytes
from src.runtime.feasibility import FeasibilityConfig
from .development_case import PINS, validate_frozen_case
from .validation_bridge import check_inputs, consume_validation_receipt, _read, _no_links

CASE = "experiments/c4-embedding-development-v1/frozen-case.json"
ENVIRONMENT = "experiments/c4-embedding-development-v1/environment.json"
EXPERIMENT_ID = "c4-embedding-checkpoint-development-v1"
RUN_ID = "c4-embedding-dev-003"
SPEC_ROOT = "experiments/" + EXPERIMENT_ID
RESIDENCY_CONFIG = "configs/c4-residency.json"
RESIDENCY_SHA = "03630075a7c9cf2dfd1b881bda2b7e8ffa3be726b368698372316acfc6e414cf"
CHECKPOINT_CONFIG = "configs/c4-checkpointing.json"
CHECKPOINT_SHA = "804cb5e28e4c3ef39e81a6aae99d4c4fdbc2d4842467a076ba69a40968960653"
CONFIG_SHA = "27bedaf1cd7f848ecc9b5b4a76ebe3ca3189c5da099fb3a4a00fac29063b216b"
OWNER = "c4-public-development-owner-v1"
RAW_ROOT = Path("/mnt/w/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/data/raw")
ASSET_ROOT = Path("/mnt/w/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/assets/a6")
SCRIPT = "scripts/run_c4_dev_probe.py"
WORKER_SCRIPT = "scripts/c4_dev_probe.py"
OUTPUTS = ["outputs/c4-development.json", "logs/c4-progress.jsonl", "logs/c4-launcher.jsonl"]
BUDGET = {"max_seconds": 1200, "max_usd": 0, "hourly_usd": 0}
RESOURCES = {"vram_mib": 8192, "ram_mib": 12288, "disk_mib": 4096}
REQUIRED = frozenset({CASE, ENVIRONMENT, *PINS, "configs/data.json", "research/a6-candidate-model-assets.json",
    "src/embedding/worker.py", SCRIPT, WORKER_SCRIPT, "scripts/a6_clip_visual.py",
    "scripts/verify_science_assets.py", "scripts/pixel_dct_control.py", "scripts/base_noise_reference.py",
    "src/data/preprocess.py", "src/embedding/proposed.py", "src/embedding/output.py",
    "src/embedding/local_assets.py", "src/embedding/development_case.py", "src/embedding/residency.py",
    RESIDENCY_CONFIG, CHECKPOINT_CONFIG, "src/embedding/checkpointing.py",
    "src/signatures/semantic.py", "src/signatures/owner.py", "src/signatures/instance.py",
    "src/__init__.py", "src/data/__init__.py", "src/runtime/__init__.py",
    "src/embedding/__init__.py", "src/signatures/__init__.py",
    "requirements-wsl-stage2-py314.txt", "requirements-wsl-torch-py314.txt",
    SPEC_ROOT+"/experiment-spec.yaml", SPEC_ROOT+"/plan.md",
    SPEC_ROOT+"/acceptance-criteria.md", SPEC_ROOT+"/compute-estimate.json",
    SPEC_ROOT+"/prior-failures.json",
    "scripts/prepare_c4_execution.py"})


def _json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def _new(path, value):
    with path.open("xb") as handle:
        handle.write(_json(value)); handle.flush(); os.fsync(handle.fileno())


def check_environment(expected, actual):
    """Exact interpreter/distribution metadata check, not payload attestation."""
    if _json(expected) != _json(actual):
        raise ValueError("C4 scientific environment changed")


def check_recipe(manifest, snapshots):
    """Additional fixed worker contract; official runner still owns approval."""
    expected = {"experiment_id": EXPERIMENT_ID, "task_id": "C4",
        "run_id": RUN_ID, "execution_target": "local", "seeds": [0],
        "reviewed_script": SCRIPT, "budget": BUDGET, "resources": RESOURCES, "outputs": OUTPUTS}
    if any(_json(manifest.get(key)) != _json(value) for key, value in expected.items()):
        raise ValueError("unexpected fixed C4 worker contract")
    if not REQUIRED <= set(snapshots):
        raise ValueError("C4 transitive worker inventory incomplete")
    if hashlib.sha256(snapshots["configs/c4-development.json"]).hexdigest() != CONFIG_SHA:
        raise ValueError("prospective C4 settings changed")
    if hashlib.sha256(snapshots[RESIDENCY_CONFIG]).hexdigest() != RESIDENCY_SHA:
        raise ValueError("explicit residency profile changed")
    if hashlib.sha256(snapshots[CHECKPOINT_CONFIG]).hexdigest() != CHECKPOINT_SHA:
        raise ValueError("explicit checkpoint profile changed")
    if manifest.get("script_sha256") != hashlib.sha256(snapshots[SCRIPT]).hexdigest():
        raise ValueError("launcher digest mismatch")


def prepare(manifest_path, output, root=PROJECT):
    manifest, snapshots, _ = check_inputs(_read(manifest_path), root)
    check_recipe(manifest, snapshots)
    loaded = consume_validation_receipt(manifest_path, output/"checkpoints", root=root)
    if type(loaded) is not FeasibilityConfig or loaded.sha256 != CONFIG_SHA:
        raise ValueError("distinct fixed non-calibrated configuration required")
    case = validate_frozen_case(root, snapshots[CASE])
    return manifest, loaded, case["selected"]


def execute_phases(selected, loaded, output, operations, record):
    """Shared orchestration; ordinary tests supply only owned fake operations."""
    record({"phase": "source_and_resources_started", "source_uid": selected["source_uid"]})
    source = operations.source(selected, output)
    record({"phase": "source_and_resources_checked"})
    store = operations.trial(source, selected, loaded, output)
    try:
        record({"phase": "model_load_started"})
        models, enrollment = operations.models(source, loaded, output)
        store.record({"phase": "source_enrollment", "enrollment": enrollment})
        record({"phase": "model_load_completed"})
        operations.attach_progress(models, store.record)
        record({"phase": "idle_residency_started"})
        operations.park_idle(models, store.record)
        record({"phase": "idle_residency_completed"})
        candidate = operations.optimize(source, selected, loaded, models, enrollment, store.record)
        record({"phase": "optimization_completed"})
        record({"phase": "safety_residency_started"})
        operations.prepare_safety(models, store.record)
        record({"phase": "safety_residency_completed"})
        receipt, _ = store.save_pair(candidate, models.check_saved_pixels)
        record({"phase": "pair_persisted", "status": receipt["status"]})
        return {"pair": receipt, "trial_directory": store.directory.name,
                "resources": operations.resources(), "calibrated_decision": "PROHIBITED",
                "q_h_drift": "NOT_RUN", "PSNR": "NOT_RUN", "SSIM": "NOT_RUN",
                "LPIPS": "NOT_RUN", "blind_verification": "NOT_RUN",
                "scientific_acceptance": False}
    except Exception as error:
        if not store._finished: store.fail(error)
        raise


def run_worker(manifest_path, output, *, root=PROJECT, operations=None):
    """Invoke only as the official runner's reviewed child. Never a preview."""
    output = _no_links(Path(output))
    if not output.is_dir(): raise ValueError("existing runner artifact root required")
    for name in ("outputs", "logs", "checkpoints"):
        _no_links(output/name)
        if not (output/name).is_dir(): raise ValueError("runner artifact layout missing")
    journal = output/OUTPUTS[1]
    if (output/OUTPUTS[0]).exists(): raise ValueError("existing report cannot be retried or overwritten")
    started = time.monotonic()
    # Exclusive journal prevents resume/retry/overwrite of a consumed run.
    with journal.open("xb") as handle:
        def record(row):
            handle.write(_json(dict(row, elapsed_seconds=time.monotonic()-started))+b"\n")
            handle.flush(); os.fsync(handle.fileno())
        record({"phase": "worker_started", "scientific_acceptance": False})
        try:
            manifest, loaded, selected = prepare(Path(manifest_path), output, root)
            record({"phase": "exact_inputs_checked", "run_id": manifest["run_id"],
                    "source_uid": selected["source_uid"], "config_sha256": loaded.sha256})
            if operations is None:
                operations = RealOperations(root)
            result = execute_phases(selected, loaded, output, operations, record)
            status = "failed_safety_flagged" if result["pair"]["status"] == "failed_safety_flagged" else "completed_diagnostic_only"
            report = {"schema_version": "c4-development-worker-v1", "status": status,
                "run_id": manifest["run_id"], "selected_case": selected,
                "result": result, "scientific_acceptance": False}
            _new(output/OUTPUTS[0], report)
            record({"phase": "worker_completed", "status": status})
            return 3 if status == "failed_safety_flagged" else 0
        except Exception as error:
            record({"phase": "worker_failed", "error_type": type(error).__name__})
            # OOM and loader failures need resource evidence too. Never let a
            # failed telemetry query suppress the original failure/report.
            failure_resources = {"status": "not_available_before_resource_preflight"}
            if operations is not None and hasattr(operations, "failure_resources"):
                try:
                    failure_resources = operations.failure_resources()
                except Exception as telemetry_error:
                    failure_resources = {"status": "telemetry_failed", "error_type": type(telemetry_error).__name__}
            _new(output/OUTPUTS[0], {"schema_version": "c4-development-worker-v1",
                "status": "failed", "error_type": type(error).__name__,
                "resources": failure_resources,
                "scientific_acceptance": False, "calibrated_decision": "PROHIBITED"})
            return 2


class RealOperations:
    """Actual operations, only reachable inside the separately approved child."""
    def __init__(self, root):
        self.root, self.measurement = root, {}
        if hashlib.sha256(_read(root/RESIDENCY_CONFIG)).hexdigest() != RESIDENCY_SHA:
            raise ValueError("residency profile changed before actual operations")
        if hashlib.sha256(_read(root/CHECKPOINT_CONFIG)).hexdigest() != CHECKPOINT_SHA:
            raise ValueError("checkpoint profile changed before actual operations")
        self.residency = None
        for name in ("HF_HUB_OFFLINE", "TRANSFORMERS_OFFLINE", "DIFFUSERS_OFFLINE", "PYTHONNOUSERSITE"):
            if os.environ.get(name) != "1": raise ValueError("offline launcher flags absent")
        if os.environ.get("CUBLAS_WORKSPACE_CONFIG") != ":4096:8":
            raise ValueError("determinism environment absent")
        # Defense in depth, not an OS network sandbox. No worker subprocesses.
        def blocked(*args, **kwargs): raise RuntimeError("network prohibited")
        socket.socket.connect = blocked
        socket.socket.connect_ex = blocked
        socket.create_connection = blocked

    def source(self, selected, output):
        expected = strict_json_bytes(_read(self.root/ENVIRONMENT))
        check_environment(expected, {"python": platform.python_version(),
            "versions": sorted((d.metadata["Name"], d.version) for d in importlib.metadata.distributions())})
        from src.data.preprocess import load_config, no_links, decode_source, pixel_sha
        import torch
        for name, value in (("torch", "2.12.1+cu130"), ("torchvision", "0.27.1+cu130"),
                            ("numpy", "2.5.3"), ("diffusers", "0.35.1"), ("transformers", "4.57.6")):
            if importlib.metadata.version(name) != value: raise ValueError("science software version mismatch")
        if not torch.cuda.is_available(): raise ValueError("CUDA unavailable")
        free, total = torch.cuda.mem_get_info()
        limit = RESOURCES["vram_mib"]*1024**2
        available = int(next(line.split()[1] for line in Path("/proc/meminfo").read_text().splitlines()
                             if line.startswith("MemAvailable:")))*1024
        self.measurement = {"initial_free_vram_bytes": free, "total_vram_bytes": total,
            "initial_available_ram_bytes": available, "torch_allocation_limit_bytes": limit,
            "initial_free_disk_bytes": shutil.disk_usage(output).free,
            "gpu": torch.cuda.get_device_name(), "cuda": torch.version.cuda,
            "installed_versions": sorted((d.metadata["Name"], d.version) for d in importlib.metadata.distributions()),
            "whole_os_memory_limit_enforced": False}
        if (free < limit+1024**3 or available < (RESOURCES["ram_mib"]+1024)*1024**2
                or self.measurement["initial_free_disk_bytes"] < RESOURCES["disk_mib"]*1024**2):
            raise ValueError("prospective resource headroom unavailable")
        torch.cuda.set_per_process_memory_fraction(limit/total)
        torch.cuda.reset_peak_memory_stats()
        torch.use_deterministic_algorithms(True)
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        torch.backends.cudnn.benchmark = False
        path = RAW_ROOT/selected["relative_path"]; no_links(path)
        if not path.is_file() or path.stat().st_size != selected["raw_size_bytes"]:
            raise ValueError("selected source size mismatch")
        with path.open("rb") as handle: raw = handle.read(selected["raw_size_bytes"]+1)
        if len(raw) != selected["raw_size_bytes"] or hashlib.sha256(raw).hexdigest() != selected["raw_sha256"]:
            raise ValueError("selected source bytes changed")
        config, _ = load_config(self.root/"configs/data.json")
        rgb, info = decode_source(raw, config)
        if (pixel_sha(rgb) != selected["canonical_pixel_sha256"]
                or rgb.shape != (selected["metadata_height"], selected["metadata_width"], 3)):
            raise ValueError("selected canonical pixels or native dimensions changed")
        with (output/"checkpoints/source-snapshot.bin").open("xb") as handle:
            handle.write(raw); handle.flush(); os.fsync(handle.fileno())
        _new(output/"checkpoints/source-checked.json", info)
        return rgb

    def trial(self, source, selected, loaded, output):
        from .output import TrialStore
        return TrialStore(output/"outputs", source_id=selected["source_uid"], seed=0,
            method_config=loaded, source_raw_hash=selected["raw_sha256"], source_rgb8=source)

    def models(self, source, loaded, output):
        from .local_assets import plan_assets, snapshot_assets, load_snapshot
        from .output import enroll_canonical
        from src.signatures.semantic import PinnedClipEncoder
        from src.data.preprocess import no_links
        plan = plan_assets(self.root/"research/a6-candidate-model-assets.json")
        snapshot = snapshot_assets(ASSET_ROOT, output/"checkpoints", plan)
        checkpoint = ASSET_ROOT/"clip/ViT-B-32.pt"; no_links(checkpoint)
        # Keep the C2 CUDA float32 arithmetic profile; release the encoder
        # before loading SD, not an unrecorded CPU signature substitution.
        encoder = PinnedClipEncoder.from_checkpoint(checkpoint, device="cuda")
        enrollment = enroll_canonical(source, encoder, bytes.fromhex(loaded.value["feature"]["clip"]["projection_seed"]), OWNER)
        enrollment["encoder_identity"] = encoder.identity
        del encoder
        import torch
        torch.cuda.empty_cache()
        models = load_snapshot(loaded, plan, snapshot, device="cuda", activation_checkpointing=True)
        from .checkpointing import CheckpointedComponents
        if (type(models.components) is not CheckpointedComponents or
                models.identity.get("activation_checkpoint_profile") != CheckpointedComponents.profile_id):
            raise ValueError("exact checkpointed component binding required")
        models.identity["activation_checkpoint_config_sha256"] = CHECKPOINT_SHA
        _new(output/"checkpoints/model-load.json", models.identity)
        return models, enrollment

    def optimize(self, source, selected, loaded, models, enrollment, record):
        import torch
        from src.data.preprocess import normalized
        from .proposed import optimize_existing, Settings
        tensor = torch.from_numpy(normalized(source).transpose(2, 0, 1).copy()).unsqueeze(0).to("cuda")
        return optimize_existing(tensor, Settings.from_embedding_config(loaded.value["embedding"]),
            models.components, seed=0, source_digest=bytes.fromhex(selected["raw_sha256"]),
            ws=bytes.fromhex(enrollment["Ws"]), wi=bytes.fromhex(enrollment["Wi"]),
            config_id=bytes.fromhex(loaded.value["dct"]["config_id"]), record=record, method_config=loaded,
            progress=record)

    def attach_progress(self, models, record):
        from .residency import PhaseResidency
        models.components.progress = record
        self.residency = PhaseResidency(models, progress=record)

    def park_idle(self, models, record):
        if self.residency is None or self.residency.models is not models:
            raise ValueError("bound residency instance required")
        record({"phase":"residency_resources_before_idle", "resources":self.failure_resources()})
        self.residency.park_idle()
        record({"phase":"residency_resources_after_idle", "resources":self.failure_resources(),
                "residency_profile_sha256":RESIDENCY_SHA})

    def prepare_safety(self, models, record):
        if self.residency is None or self.residency.models is not models:
            raise ValueError("bound residency instance required")
        self.residency.prepare_safety()
        record({"phase":"residency_resources_before_safety", "resources":self.failure_resources(),
                "residency_profile_sha256":RESIDENCY_SHA})

    def resources(self):
        import torch
        torch.cuda.synchronize()
        return self.failure_resources()

    def failure_resources(self):
        import torch
        import resource
        # No synchronize after an OOM/device failure; retain readable peaks.
        initialized = torch.cuda.is_initialized()
        return dict(self.measurement, peak_torch_allocated_bytes=torch.cuda.max_memory_allocated() if initialized else None,
            peak_torch_reserved_bytes=torch.cuda.max_memory_reserved() if initialized else None,
            current_torch_allocated_bytes=torch.cuda.memory_allocated() if initialized else None,
            current_torch_reserved_bytes=torch.cuda.memory_reserved() if initialized else None,
            peak_worker_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024)
