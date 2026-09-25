"""A6 offline CLIP/LPIPS synthetic metric preflight; no study images.

Default mode verifies bytes only. --load-metrics constructs pretrained models
and runs fixed CPU/CUDA vectors, so it requires separate explicit user
authorization and an external 20-minute process timeout before invocation.
It is not a scientific experiment or approval for diffusion inference.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import importlib.util
import json
import os
import socket
import time
from pathlib import Path

from check_a6_lpips_assets import LOCK_SHA256, verify_package
from verify_science_assets import verify


CLIP_PATH = "clip/ViT-B-32.pt"
ALEXNET_PATH = "alexnet/alexnet-owt-7be5be79.pth"
EXPECTED_PATHS = {CLIP_PATH, ALEXNET_PATH}
CLIP_SOURCE_SHA256 = {
    "clip/clip.py": "3891eee0ad659a781ec3fd0240f9d69b7f3845837f671ff6670accf0d4bad0a2",
    "clip/model.py": "dc4981bbd17867430890cfe711bb813466232f3b19c5753e26de0b7b047b0926",
}


def check_inputs(asset_root: Path, lock_path: Path, lpips_root: Path) -> dict[str, object]:
    raw = lock_path.read_bytes()
    observed_lock = hashlib.sha256(raw).hexdigest()
    if observed_lock != LOCK_SHA256:
        raise ValueError("A6 candidate asset-lock digest changed")
    lock = json.loads(raw)
    paths = {entry["path"] for entry in lock["files"]}
    if len(paths) != 17 or not EXPECTED_PATHS.issubset(paths):
        raise ValueError("A6 lock lacks the exact 17-file candidate inventory")
    receipt = verify(asset_root, lock)
    package = verify_package(lpips_root)
    return {
        "status": "verified_no_model_load",
        "asset_lock_sha256": observed_lock,
        "verified_asset_count": len(receipt["files"]),
        "verified_lpips_file_count": len(package),
    }


def synthetic_rgb8(size: int) -> bytes:
    if size not in (64, 224):
        raise ValueError("only preregistered synthetic sizes are allowed")
    return bytes(
        (17 * x + 31 * y + 47 * channel) % 256
        for y in range(size) for x in range(size) for channel in range(3)
    )


def _block_network() -> None:
    def denied(*_args: object, **_kwargs: object) -> None:
        raise RuntimeError("A6 metric preflight forbids network connections")

    socket.socket.connect = denied  # type: ignore[method-assign]
    socket.create_connection = denied  # type: ignore[assignment]


def _check_launch_environment() -> None:
    if os.environ.get("CUBLAS_WORKSPACE_CONFIG") != ":4096:8":
        raise RuntimeError("set CUBLAS_WORKSPACE_CONFIG=:4096:8 before launch")
    if os.environ.get("PYTHONHASHSEED") != "0":
        raise RuntimeError("set PYTHONHASHSEED=0 before launch")


def _finite_vector(tensor: object, expected: int, label: str) -> None:
    import torch

    if tensor.ndim != 2 or tensor.shape != (1, expected):
        raise RuntimeError(f"{label} has unexpected shape")
    if not bool(torch.isfinite(tensor).all()):
        raise RuntimeError(f"{label} is nonfinite")
    if float(torch.linalg.vector_norm(tensor.float())) < 1e-12:
        raise RuntimeError(f"{label} has near-zero norm")


def _verified_clip_visual_source() -> object:
    """Load the pinned official visual model file without the unused tokenizer.

    CLIP's package initializer imports a native regex tokenizer even for an
    image-only encode. On this host Windows Code Integrity blocks that native
    binary. This uses the same installed, hash-checked official model.py, not
    alternate weights or a modified security policy. Text APIs stay unavailable.
    """
    distribution = importlib.metadata.distribution("clip")
    files = {name: Path(distribution.locate_file(name)) for name in CLIP_SOURCE_SHA256}
    for name, path in files.items():
        if not path.is_file() or path.is_symlink() or path.is_junction():
            raise RuntimeError(f"missing or linked pinned CLIP source: {name}")
        if hashlib.sha256(path.read_bytes()).hexdigest() != CLIP_SOURCE_SHA256[name]:
            raise RuntimeError(f"pinned CLIP source digest changed: {name}")
    spec = importlib.util.spec_from_file_location(
        "a6_verified_official_clip_visual", files["clip/model.py"])
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load pinned CLIP visual source")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_model


def _load_clip_and_measure(checkpoint: Path) -> dict[str, object]:
    import numpy as np
    import torch
    from PIL import Image
    from torchvision.transforms import (
        CenterCrop, Compose, InterpolationMode, Normalize, Resize, ToTensor,
    )

    build_model = _verified_clip_visual_source()

    # The pinned official checkpoint is a JIT archive. Refuse a fallback to
    # arbitrary pickle state-dict deserialization.
    archive = torch.jit.load(str(checkpoint), map_location="cpu").eval()
    model = build_model(archive.state_dict()).float().eval()
    if model.visual.input_resolution != 224:
        raise RuntimeError("CLIP input resolution differs from A5")
    image = Image.frombytes("RGB", (224, 224), synthetic_rgb8(224))
    # Exact operations/constants in the hash-checked official clip.py _transform.
    transform = Compose([
        Resize(224, interpolation=InterpolationMode.BICUBIC),
        CenterCrop(224),
        lambda value: value.convert("RGB"),
        ToTensor(),
        Normalize((0.48145466, 0.4578275, 0.40821073),
                  (0.26862954, 0.26130258, 0.27577711)),
    ])
    pixels = transform(image).unsqueeze(0)
    with torch.no_grad():
        cpu = model.encode_image(pixels).float()
    _finite_vector(cpu, 512, "CLIP CPU embedding")
    model = model.to("cuda")
    with torch.no_grad():
        gpu = model.encode_image(pixels.to("cuda")).float().cpu()
    _finite_vector(gpu, 512, "CLIP CUDA embedding")
    cpu_unit = cpu / torch.linalg.vector_norm(cpu, dim=-1, keepdim=True)
    gpu_unit = gpu / torch.linalg.vector_norm(gpu, dim=-1, keepdim=True)
    return {
        "input": "synthetic_rgb8_224",
        "visual_loader": "pinned_official_model_py_without_unused_tokenizer",
        "feature_dimension": 512,
        "cpu_embedding_sha256": hashlib.sha256(
            cpu.detach().numpy().astype("<f4").tobytes()).hexdigest(),
        "cuda_embedding_sha256": hashlib.sha256(
            gpu.detach().numpy().astype("<f4").tobytes()).hexdigest(),
        "unit_max_abs_difference": float((cpu_unit - gpu_unit).abs().max()),
        "unit_cosine_similarity": float(
            torch.nn.functional.cosine_similarity(cpu_unit, gpu_unit).item()),
        "preprocess_tensor_sha256": hashlib.sha256(
            np.asarray(pixels.numpy(), dtype="<f4").tobytes()).hexdigest(),
    }


def _load_lpips_and_measure(alexnet_path: Path, learned_path: Path) -> dict[str, object]:
    import numpy as np
    import torch
    import torchvision
    import lpips

    # Both constructors explicitly disable their implicit pretrained
    # downloads. Load the two already-verified local files separately.
    metric = lpips.LPIPS(
        pretrained=False, pnet_rand=True, net="alex", version="0.1",
        spatial=False, use_dropout=True, eval_mode=True, verbose=False,
    )
    trunk = torchvision.models.alexnet(weights=None)
    trunk_state = torch.load(alexnet_path, map_location="cpu", weights_only=True)
    if not isinstance(trunk_state, dict) or not all(
        isinstance(key, str) and isinstance(value, torch.Tensor)
        for key, value in trunk_state.items()
    ):
        raise RuntimeError("AlexNet checkpoint is not a tensor state dict")
    trunk.load_state_dict(trunk_state, strict=True)
    for name, start, stop in (
        ("slice1", 0, 2), ("slice2", 2, 5), ("slice3", 5, 8),
        ("slice4", 8, 10), ("slice5", 10, 12),
    ):
        setattr(metric.net, name, torch.nn.Sequential(
            *(trunk.features[index] for index in range(start, stop))))
    del trunk_state, trunk

    linear_state = torch.load(learned_path, map_location="cpu", weights_only=True)
    required = {f"lin{index}.model.1.weight" for index in range(5)}
    if not isinstance(linear_state, dict) or not required.issubset(linear_state):
        raise RuntimeError("LPIPS learned layer lacks the five pinned AlexNet layers")
    if set(linear_state) - set(metric.state_dict()):
        raise RuntimeError("LPIPS learned layer has unexpected state keys")
    missing, unexpected = metric.load_state_dict(linear_state, strict=False)
    if unexpected or any(key.startswith("lin") and not key.startswith("lins.")
                         for key in missing):
        raise RuntimeError("LPIPS learned layer failed to load completely")
    metric.requires_grad_(False).eval()

    rgb = np.frombuffer(synthetic_rgb8(64), dtype=np.uint8).copy().reshape(64, 64, 3)
    altered = rgb.copy()
    altered[::4, ::4, 0] = np.minimum(
        altered[::4, ::4, 0].astype(np.int16) + 1, 255).astype(np.uint8)
    def tensor(value: object) -> object:
        return torch.from_numpy(value).permute(2, 0, 1).unsqueeze(0).float() / 255 * 2 - 1
    first, second = tensor(rgb), tensor(altered)
    with torch.no_grad():
        cpu = metric(first, second, normalize=False).float()
    if cpu.numel() != 1 or not bool(torch.isfinite(cpu).all()):
        raise RuntimeError("LPIPS CPU score is invalid")
    metric = metric.to("cuda")
    with torch.no_grad():
        gpu = metric(first.to("cuda"), second.to("cuda"), normalize=False).float().cpu()
    if gpu.numel() != 1 or not bool(torch.isfinite(gpu).all()):
        raise RuntimeError("LPIPS CUDA score is invalid")
    return {
        "input": "synthetic_rgb8_pair_64",
        "cpu_score": float(cpu.item()),
        "cuda_score": float(gpu.item()),
        "absolute_difference": abs(float(cpu.item()) - float(gpu.item())),
    }


def _selected_measurements(metric: str, asset_root: Path,
                           lpips_root: Path) -> dict[str, object]:
    if metric not in ("both", "clip", "lpips"):
        raise ValueError("unsupported metric selection")
    measurements: dict[str, object] = {}
    if metric in ("both", "clip"):
        measurements["clip"] = _load_clip_and_measure(asset_root / CLIP_PATH)
    if metric in ("both", "lpips"):
        measurements["lpips"] = _load_lpips_and_measure(
            asset_root / ALEXNET_PATH,
            lpips_root / "weights/v0.1/alex.pth",
        )
    return measurements


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--asset-root", type=Path, required=True)
    parser.add_argument("--lock", type=Path, required=True)
    parser.add_argument("--lpips-root", type=Path, required=True)
    parser.add_argument("--load-metrics", action="store_true")
    parser.add_argument("--metric", choices=("both", "clip", "lpips"), default="both")
    args = parser.parse_args()
    result = check_inputs(args.asset_root, args.lock, args.lpips_root)
    if not args.load_metrics:
        print(json.dumps(result, sort_keys=True))
        return

    _check_launch_environment()
    for name in ("HF_HUB_OFFLINE", "TRANSFORMERS_OFFLINE",
                 "HF_DATASETS_OFFLINE", "HF_HUB_DISABLE_TELEMETRY"):
        os.environ[name] = "1"
    _block_network()
    import torch

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is not available")
    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.benchmark = False
    torch.cuda.reset_peak_memory_stats()
    started = time.monotonic()
    result.update(_selected_measurements(args.metric, args.asset_root,
                                         args.lpips_root))
    torch.cuda.synchronize()
    result["status"] = "synthetic_metrics_measured_not_accepted"
    result["selected_metric"] = args.metric
    result["cuda_device"] = torch.cuda.get_device_name()
    result["cuda_peak_allocated_bytes"] = torch.cuda.max_memory_allocated()
    result["elapsed_seconds"] = round(time.monotonic() - started, 3)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
