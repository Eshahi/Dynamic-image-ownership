"""Pinned local SD component snapshot and explicit future model-load boundary.

Import and inventory planning load no weights. Snapshot creation and model
loading belong ONLY inside a separately approved scientific worker. No network
fallback, missing safety component, floating revision or pickle route.
"""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

from src.runtime.config import LoadedConfig, strict_json_bytes
from scripts.verify_science_assets import _entries, verify
from .proposed import DiffusersComponents, EmbeddingError, Settings
from .config_binding import validate_loaded_snapshot

LOCK_SHA256 = "b8c2595857853ea5b7835bb71f12a34dde07b78623c5e638f692dc7eb220b27e"
SD_FILES = frozenset({
    "feature_extractor/preprocessor_config.json", "model_index.json",
    "safety_checker/config.json", "safety_checker/model.fp16.safetensors",
    "scheduler/scheduler_config.json", "text_encoder/config.json", "text_encoder/model.fp16.safetensors",
    "tokenizer/merges.txt", "tokenizer/special_tokens_map.json", "tokenizer/tokenizer_config.json",
    "tokenizer/vocab.json", "unet/config.json", "unet/diffusion_pytorch_model.fp16.safetensors",
    "vae/config.json", "vae/diffusion_pytorch_model.fp16.safetensors"})
GROUPS = {"vae": ("vae/",), "unet": ("unet/",), "text_encoder": ("text_encoder/",),
          "tokenizer": ("tokenizer/",), "safety_checker": ("safety_checker/", "feature_extractor/")}


def _json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                      allow_nan=False).encode("ascii")


def _no_links(path):
    if not path.is_absolute():
        raise EmbeddingError("absolute asset/staging path required")
    if any(p.is_symlink() or p.is_junction() for p in (path, *path.parents)):
        raise EmbeddingError("linked asset/staging path or ancestor")


def _config(loaded):
    return validate_loaded_snapshot(loaded)


@dataclass(frozen=True)
class AssetPlan:
    raw_lock: bytes
    entries_json: bytes
    component_hashes_json: bytes
    lock_sha256: str
    total_bytes: int

    @property
    def entries(self):
        return json.loads(self.entries_json)

    @property
    def component_hashes(self):
        return json.loads(self.component_hashes_json)


def _plan_bytes(raw):
    if hashlib.sha256(raw).hexdigest() != LOCK_SHA256:
        raise EmbeddingError("candidate A6 lock differs from pinned bytes")
    lock = strict_json_bytes(raw)
    _entries(lock)
    entries = sorted(({**entry, "path": entry["path"].removeprefix("sd15-fp16/")}
                      for entry in lock["files"] if entry["path"].startswith("sd15-fp16/")),
                     key=lambda entry: entry["path"])
    if {entry["path"] for entry in entries} != SD_FILES:
        raise EmbeddingError("SD candidate inventory incomplete or expanded")
    hashes = {}
    for name, prefixes in GROUPS.items():
        members = [entry for entry in entries if entry["path"].startswith(prefixes)]
        hashes[name] = hashlib.sha256(_json({"profile": "c4-component-inventory-v1", "name": name,
                                            "files": members})).hexdigest()
    return AssetPlan(raw, _json(entries), _json(hashes), LOCK_SHA256, sum(e["size_bytes"] for e in entries))


def _check_plan(plan):
    if not isinstance(plan, AssetPlan) or _plan_bytes(plan.raw_lock) != plan:
        raise EmbeddingError("asset plan differs from pinned raw inventory")


def plan_assets(lock_path: Path) -> AssetPlan:
    """Small metadata-only read; does not read or validate actual weight bytes."""
    lock_path = Path(lock_path)
    _no_links(lock_path)
    if not lock_path.is_file() or lock_path.stat().st_size > 64*1024:
        raise EmbeddingError("invalid asset lock file")
    return _plan_bytes(lock_path.read_bytes())


def bind_config_assets(loaded: LoadedConfig, plan: AssetPlan):
    _check_plan(plan)
    config = _config(loaded)
    e = config["embedding"]
    if (e["model_repository"] != "stable-diffusion-v1-5/stable-diffusion-v1-5"
            or e["model_revision"] != "451f4fe16113bff5a5d2269ed5ad43b0592e9a14"
            or e["diffusers_commit"] != "0f252be0ed42006c125ef4429156cb13ae6c1d60"
            or e["model_component_hashes"] != plan.component_hashes):
        raise EmbeddingError("configuration model/component inventory mismatch")
    return Settings.from_embedding_config(e)


def _copy_checked(source, destination, entry):
    """Exclusive bounded copy; a failed partial stays available for diagnosis."""
    _no_links(source)
    _no_links(destination)
    if not source.is_file() or source.stat().st_size != entry["size_bytes"]:
        raise EmbeddingError("candidate source asset size mismatch")
    count, digest = 0, hashlib.sha256()
    with source.open("rb") as reader, destination.open("xb") as writer:
        while chunk := reader.read(1024*1024):
            count += len(chunk)
            if count > entry["size_bytes"]:
                raise EmbeddingError("candidate source grew while copying")
            digest.update(chunk)
            writer.write(chunk)
        writer.flush()
        os.fsync(writer.fileno())
    if count != entry["size_bytes"] or digest.hexdigest() != entry["sha256"]:
        raise EmbeddingError("candidate asset snapshot digest mismatch")


def snapshot_assets(asset_root: Path, staging_parent: Path, plan: AssetPlan) -> Path:
    """Future approved worker only: copy SD bytes into a fresh private directory.

    This has an explicit extra disk cost, not a fresh acquisition/download.
    Never overwrite/reuse/clean another snapshot, even on failure.
    """
    _check_plan(plan)
    asset_root, staging_parent = Path(asset_root), Path(staging_parent)
    _no_links(asset_root)
    _no_links(staging_parent)
    if not asset_root.is_dir() or not staging_parent.is_dir():
        raise EmbeddingError("asset root and staging parent must already exist")
    root = Path(tempfile.mkdtemp(prefix="c4-sd-snapshot-", dir=staging_parent))
    start = {"status": "copy_started", "lock_sha256": plan.lock_sha256,
             "entries_sha256": hashlib.sha256(plan.entries_json).hexdigest(), "planned_bytes": plan.total_bytes}
    (root/"snapshot-start.json").write_bytes(_json(start))
    model = root/"sd15-fp16"
    model.mkdir()
    try:
        for entry in plan.entries:
            destination = model/entry["path"]
            destination.parent.mkdir(parents=True, exist_ok=True)
            _copy_checked(asset_root/"sd15-fp16"/entry["path"], destination, entry)
        verify(model, {"schema_version": "a6-asset-lock-v1", "files": plan.entries})
        (root/"snapshot-complete.json").write_bytes(_json({**start, "status": "copied_and_hash_checked"}))
    except Exception as error:
        (root/"snapshot-failed.json").write_bytes(_json({**start, "status": "copy_failed", "error_type": type(error).__name__}))
        raise
    return root


@dataclass
class LocalModels:
    components: DiffusersComponents
    pipeline: object
    identity: dict

    def check_saved_pixels(self, rgb8):
        """Actual safety check on final RGB8; never replace flagged pixels with black.

        Checker may modify its own copy. Return only flag; preserve original
        diagnostic PNG and count a flag as failure in the caller's ledger.
        """
        import numpy as np
        import torch
        from PIL import Image
        from src.data.preprocess import pixel_sha
        pixel_sha(rgb8)
        pixels = rgb8.copy()
        pil = Image.fromarray(pixels)
        model = self.pipeline.safety_checker
        parameter = next(model.parameters())
        inputs = self.pipeline.feature_extractor([pil], return_tensors="pt").pixel_values.to(
            device=parameter.device, dtype=parameter.dtype)
        with torch.no_grad():
            _, flags = model(clip_input=inputs, images=np.expand_dims(pixels.astype(np.float32)/255, 0))
        if not isinstance(flags, list) or len(flags) != 1 or type(flags[0]) not in (bool, np.bool_):
            raise EmbeddingError("unexpected safety checker result")
        return bool(flags[0])


def load_snapshot(loaded: LoadedConfig, plan: AssetPlan, snapshot: Path, *, device: str):
    """Explicit model-load boundary, NEVER called by current CLI or ordinary tests.

    Scientific runner must already have approved exact config/input/code/resource
    package. Caller must block network and set offline/determinism flags in a
    fresh process. No boolean here can manufacture that external authorization.
    """
    settings = bind_config_assets(loaded, plan)
    if device not in ("cpu", "cuda"):
        raise EmbeddingError("explicit cpu/cuda profile required")
    if any(os.environ.get(name) != "1" for name in ("HF_HUB_OFFLINE", "TRANSFORMERS_OFFLINE", "DIFFUSERS_OFFLINE")):
        raise EmbeddingError("offline launcher flags absent")
    for name, expected in (("diffusers", "0.35.1"), ("transformers", "4.57.6")):
        if importlib.metadata.version(name) != expected:
            raise EmbeddingError("model-loader software version mismatch")
    _no_links(snapshot)
    model = snapshot/"sd15-fp16"
    verify(model, {"schema_version": "a6-asset-lock-v1", "files": plan.entries})
    present = {p.relative_to(model).as_posix() for p in model.rglob("*") if p.is_file()}
    if present != SD_FILES:
        raise EmbeddingError("snapshot model has unlisted files")
    import torch
    from diffusers import StableDiffusionImg2ImgPipeline
    if not torch.are_deterministic_algorithms_enabled() or torch.backends.cuda.matmul.allow_tf32 or torch.backends.cudnn.allow_tf32 or torch.backends.cudnn.benchmark:
        raise EmbeddingError("declared deterministic float32 flags absent")
    pipeline = StableDiffusionImg2ImgPipeline.from_pretrained(model, local_files_only=True,
        use_safetensors=True, variant="fp16", torch_dtype=torch.float32)
    if pipeline.safety_checker is None or pipeline.feature_extractor is None:
        raise EmbeddingError("safety components absent")
    pipeline.to(device)
    for module in (pipeline.text_encoder, pipeline.safety_checker):
        module.eval().requires_grad_(False)
        for parameter in module.parameters():
            if parameter.dtype != torch.float32 or parameter.device.type != device:
                raise EmbeddingError("text/safety parameter precision or device mismatch")
    tokens = pipeline.tokenizer([""], padding="max_length", max_length=77,
                                truncation=True, return_tensors="pt")
    if tuple(tokens.input_ids.shape) != (1, 77) or pipeline.tokenizer.model_max_length != 77:
        raise EmbeddingError("empty-tokenizer shape/profile mismatch")
    with torch.no_grad():
        # SD1.5 CLIPTextModel profile does not use an attention mask.
        condition = pipeline.text_encoder(tokens.input_ids.to(device))[0]
    components = DiffusersComponents(pipeline.vae, pipeline.unet, condition, settings)
    return LocalModels(components, pipeline, {"lock_sha256": plan.lock_sha256,
        "component_hashes": plan.component_hashes, "config_sha256": loaded.sha256,
        "conditioning": "fixed-empty-string", "token_ids": tokens.input_ids.tolist(),
        "token_ids_sha256": hashlib.sha256(_json(tokens.input_ids.tolist())).hexdigest(),
        "device": device, "model_dtype": "float32", "model_runtime_parity": "NOT_PROVEN",
        "custody": "pinned-unaffiliated-mirror-not-original-publisher-attestation"})
