"""Bounded A6 offline SD component-load probe; never runs image inference.

This is an environment compatibility check, not a scientific experiment or
evidence that the thesis embedding/detection method works. The explicit
--load-model flag is reserved for a separately authorized local preflight.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import socket
import time
from pathlib import Path

from verify_science_assets import verify
from check_a6_lpips_assets import LOCK_SHA256

REQUIRED_SD_FILES = frozenset({
    "feature_extractor/preprocessor_config.json",
    "model_index.json",
    "safety_checker/config.json",
    "safety_checker/model.fp16.safetensors",
    "scheduler/scheduler_config.json",
    "text_encoder/config.json",
    "text_encoder/model.fp16.safetensors",
    "tokenizer/merges.txt",
    "tokenizer/special_tokens_map.json",
    "tokenizer/tokenizer_config.json",
    "tokenizer/vocab.json",
    "unet/config.json",
    "unet/diffusion_pytorch_model.fp16.safetensors",
    "vae/config.json",
    "vae/diffusion_pytorch_model.fp16.safetensors",
})


def _read_pinned_lock(path: Path) -> dict[str, object]:
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != LOCK_SHA256:
        raise ValueError("A6 candidate asset-lock digest changed")
    return json.loads(raw)


def _check_model_inventory(model_dir: Path, lock: dict[str, object]) -> None:
    listed = {entry["path"].removeprefix("sd15-fp16/")
              for entry in lock["files"] if entry["path"].startswith("sd15-fp16/")}
    if listed != REQUIRED_SD_FILES:
        raise ValueError("SD lock must list exactly the pinned fp16 component inventory")
    present = {path.relative_to(model_dir).as_posix()
               for path in model_dir.rglob("*") if path.is_file()}
    if present != REQUIRED_SD_FILES:
        raise ValueError("SD asset directory has missing or unlisted regular files")


def _block_network() -> None:
    def denied(*_args: object, **_kwargs: object) -> None:
        raise RuntimeError("A6 model-load preflight forbids all network connections")

    socket.socket.connect = denied  # type: ignore[method-assign]
    socket.create_connection = denied  # type: ignore[assignment]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--asset-root", type=Path, required=True)
    parser.add_argument("--lock", type=Path, required=True)
    parser.add_argument("--load-model", action="store_true")
    args = parser.parse_args()

    lock = _read_pinned_lock(args.lock)
    receipt = verify(args.asset_root, lock)
    required = {"unet", "vae", "text_encoder", "tokenizer", "scheduler",
                "safety_checker", "feature_extractor"}
    model_dir = args.asset_root / "sd15-fp16"
    _check_model_inventory(model_dir, lock)
    model_index = json.loads((model_dir / "model_index.json").read_text(encoding="utf-8"))
    if not required.issubset(model_index):
        raise ValueError(f"model index missing components: {sorted(required - model_index.keys())}")
    if not args.load_model:
        print(json.dumps({"status": "identity_only", "verified_files": len(receipt["files"]),
                          "model_components": sorted(required)}, sort_keys=True))
        return

    for name in ("HF_HUB_OFFLINE", "TRANSFORMERS_OFFLINE", "DIFFUSERS_OFFLINE",
                 "HF_DATASETS_OFFLINE", "HF_HUB_DISABLE_TELEMETRY"):
        os.environ[name] = "1"
    _block_network()
    import torch
    from diffusers import StableDiffusionImg2ImgPipeline

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is not available")
    torch.cuda.reset_peak_memory_stats()
    before_free, total = torch.cuda.mem_get_info()
    started = time.monotonic()
    pipeline = StableDiffusionImg2ImgPipeline.from_pretrained(
        model_dir, variant="fp16", use_safetensors=True,
        local_files_only=True, torch_dtype=torch.float16,
    )
    if pipeline.safety_checker is None or pipeline.feature_extractor is None:
        raise RuntimeError("safety checker or feature extractor was not loaded")
    pipeline.to("cuda")
    torch.cuda.synchronize()
    after_free, _ = torch.cuda.mem_get_info()
    result = {
        "status": "model_loaded_no_inference",
        "verified_files": len(receipt["files"]),
        "pipeline_class": type(pipeline).__name__,
        "scheduler_class": type(pipeline.scheduler).__name__,
        "safety_checker_loaded": True,
        "feature_extractor_loaded": True,
        "cuda_device": torch.cuda.get_device_name(),
        "cuda_total_bytes": total,
        "cuda_free_before_bytes": before_free,
        "cuda_free_after_bytes": after_free,
        "cuda_peak_allocated_bytes": torch.cuda.max_memory_allocated(),
        "elapsed_seconds": round(time.monotonic() - started, 3),
    }
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
