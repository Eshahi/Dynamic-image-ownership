"""Pinned official CLIP ViT-B/32 image-only adapter for the A5 method.

The official CLIP package initializer eagerly imports its text tokenizer and
the native ``regex`` extension. This adapter executes only the hash-checked
official visual model source and the documented official image transform. It
does not modify host code-integrity policy, supply a tokenizer, or authorize a
scientific run. Callers must still use the compute runner for study images.
"""

from __future__ import annotations

import hashlib
import importlib.metadata
import importlib.util
from pathlib import Path


CLIP_SOURCE_SHA256 = {
    "clip/clip.py": "3891eee0ad659a781ec3fd0240f9d69b7f3845837f671ff6670accf0d4bad0a2",
    "clip/model.py": "dc4981bbd17867430890cfe711bb813466232f3b19c5753e26de0b7b047b0926",
}
CLIP_UPSTREAM_LF_SHA256 = {
    "clip/clip.py": "9540f200fbf8145479fa655382a56dab048d238cc698b9cbd8df3b6d86d3f1b6",
    "clip/model.py": "9902cbe5ee90a1da2aa3e6f043e8a23dc1f8831193b963785c9af03d5c7bef2c",
}
CHECKPOINT_SHA256 = "40d365715913c9da98579312b702a82c18be219cc2a73407c4526f58eba950af"
CHECKPOINT_SIZE_BYTES = 353_976_522


def _digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _regular_file(path: Path) -> None:
    if not path.is_file() or path.is_symlink() or path.is_junction():
        raise RuntimeError(f"missing or linked CLIP file: {path.name}")


def verified_visual_builder() -> object:
    """Return the installed, pinned official ``build_model`` without tokenizer import."""
    distribution = importlib.metadata.distribution("clip")
    files = {name: Path(distribution.locate_file(name)) for name in CLIP_SOURCE_SHA256}
    for name, path in files.items():
        _regular_file(path)
        if _digest_file(path) != CLIP_SOURCE_SHA256[name]:
            raise RuntimeError(f"pinned CLIP source digest changed: {name}")
        # Windows wheel-building converted upstream LF to CRLF. Require the
        # exact pinned upstream bytes after only that reversible conversion.
        normalized = path.read_bytes().replace(b"\r\n", b"\n")
        if hashlib.sha256(normalized).hexdigest() != CLIP_UPSTREAM_LF_SHA256[name]:
            raise RuntimeError(f"pinned CLIP upstream content changed: {name}")
    spec = importlib.util.spec_from_file_location(
        "a6_verified_official_clip_visual", files["clip/model.py"])
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load pinned CLIP visual source")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_model


def official_image_transform() -> object:
    """Exact operations/constants in pinned official ``clip.py`` ``_transform(224)``."""
    from torchvision.transforms import (
        CenterCrop, Compose, InterpolationMode, Normalize, Resize, ToTensor,
    )

    return Compose([
        Resize(224, interpolation=InterpolationMode.BICUBIC),
        CenterCrop(224),
        lambda value: value.convert("RGB"),
        ToTensor(),
        Normalize((0.48145466, 0.4578275, 0.40821073),
                  (0.26862954, 0.26130258, 0.27577711)),
    ])


def load_visual_encoder(checkpoint: Path, *, device: str = "cpu") -> tuple[object, object]:
    """Load the exact local official JIT archive into official source model code.

    This refuses all implicit downloads and arbitrary pickle checkpoints. The
    returned model has ``encode_image``; text tokenization is not provided.
    """
    if device not in ("cpu", "cuda"):
        raise ValueError("CLIP device must be cpu or cuda")
    checkpoint = Path(checkpoint)
    _regular_file(checkpoint)
    if checkpoint.stat().st_size != CHECKPOINT_SIZE_BYTES:
        raise RuntimeError("CLIP checkpoint size differs from pinned archive")
    if _digest_file(checkpoint) != CHECKPOINT_SHA256:
        raise RuntimeError("CLIP checkpoint SHA-256 differs from pinned archive")

    build_model = verified_visual_builder()
    import torch

    archive = torch.jit.load(str(checkpoint), map_location="cpu").eval()
    model = build_model(archive.state_dict()).float().eval().to(device)
    if model.visual.input_resolution != 224:
        raise RuntimeError("CLIP input resolution differs from A5")
    return model, official_image_transform()
