"""C2 pinned CLIP image features and A5 public-derived semantic signature.

Importing this module loads no model. Real study-image extraction belongs in an
exact-manifest approved run; ordinary synthetic tests do not authorize it.
"""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
import math
import platform
import struct
import sys
from dataclasses import dataclass
from pathlib import Path

from .owner import canonical_owner, pack_fields


class SemanticError(ValueError):
    """Retained extraction/protocol failure, never a negative detector result."""


def _json(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False, ensure_ascii=True).encode("ascii")


def _vector(values: object) -> tuple[float, ...]:
    if not isinstance(values, (list, tuple)) or len(values) != 512:
        raise SemanticError("feature shape must be exactly 512")
    if any(type(v) not in (float, int) or not math.isfinite(v) for v in values):
        raise SemanticError("features must be finite real scalars, not booleans")
    result = tuple(float(v) for v in values)
    if abs(math.sqrt(math.fsum(v*v for v in result))-1) > 1e-5:
        raise SemanticError("features must already be float32 unit-normalized")
    # JSON/Python widening must not introduce a different arithmetic profile.
    try:
        if any(struct.unpack("<f", struct.pack("<f", v))[0] != v for v in result):
            raise SemanticError("features are not exact widened float32 values")
    except OverflowError as exc:
        raise SemanticError("feature is outside float32") from exc
    return result


@dataclass(frozen=True)
class SemanticCode:
    packed: bytes
    projections: tuple[float, ...]


def quantize_features(features: object, projection_seed: bytes) -> SemanticCode:
    """Ordered float64 sums of A5 SHAKE Rademacher rows; no float hashing."""
    values = _vector(features)
    if not isinstance(projection_seed, bytes) or len(projection_seed) != 32:
        raise SemanticError("projection seed must be exactly 32 immutable bytes")
    stream = hashlib.shake_256(pack_fields(b"a5-semproj-v1", projection_seed)).digest(768)
    scale = 1/math.sqrt(512)
    projections = []
    bits = 0
    for row in range(12):
        total = 0.0
        for column, value in enumerate(values):
            index = row*512+column
            sign = -1 if (stream[index//8] >> (index % 8)) & 1 else 1
            total += value*sign*scale
        projections.append(total)
        if total >= 0:
            bits |= 1 << row
    return SemanticCode(bits.to_bytes(2, "little"), tuple(projections))


def derive_ws(features: object, projection_seed: bytes, owner_id: str) -> tuple[SemanticCode, bytes]:
    code = quantize_features(features, projection_seed)
    _, owner = canonical_owner(owner_id)
    return code, hashlib.sha256(pack_fields(b"a5-ws-v1", code.packed, owner)).digest()


def normalize_tensor(encoded: object) -> tuple[float, ...]:
    """A5 Torch float32 vector norm/division, widened only after normalization."""
    import torch
    if not isinstance(encoded, torch.Tensor) or tuple(encoded.shape) != (1, 512):
        raise SemanticError("encoder output must be a 1x512 tensor")
    if encoded.dtype != torch.float32 or not bool(torch.isfinite(encoded).all()):
        raise SemanticError("encoder must return finite float32")
    norm = torch.linalg.vector_norm(encoded, dim=1, keepdim=True)
    if not bool(torch.isfinite(norm).all()) or float(norm.item()) < 1e-12:
        raise SemanticError("feature norm is nonfinite or below 1e-12")
    normalized = encoded/norm
    return _vector(normalized.detach().cpu().tolist()[0])


def feature_identity(pixel_sha256: str, encoder_identity: dict) -> tuple[dict, str]:
    if (not isinstance(pixel_sha256, str) or len(pixel_sha256) != 64
            or any(c not in "0123456789abcdef" for c in pixel_sha256)):
        raise SemanticError("canonical pixel digest must be lowercase SHA256")
    required = {"model", "checkpoint_sha256", "source_commit", "source_digests",
                "preprocess", "arithmetic", "device", "runtime", "implementation_sha256"}
    if not isinstance(encoder_identity, dict) or set(encoder_identity) != required:
        raise SemanticError("incomplete encoder/cache identity")
    identity = {"schema_version":"c2-feature-cache-v1", "canonical_pixel_sha256":pixel_sha256,
                "encoder":encoder_identity}
    # Defensive snapshot: caller mutations cannot alter a computed cache key.
    identity = json.loads(_json(identity))
    return identity, hashlib.sha256(_json(identity)).hexdigest()


def _unlinked(path: Path) -> None:
    for part in (path, *path.parents):
        if part.is_symlink() or part.is_junction():
            raise SemanticError("linked cache path or ancestor")


class FeatureCache:
    """Local-only, fail-closed cache; corrupt evidence is never silently replaced."""
    def __init__(self, root: Path):
        self.root = Path(root).absolute()
        _unlinked(self.root)
        self.root.mkdir(parents=True, exist_ok=True)

    def read(self, identity: dict, key: str) -> tuple[float, ...] | None:
        self._key(identity, key)
        path = self.root/(key+".json")
        _unlinked(path)
        if not path.exists():
            return None
        if not path.is_file() or path.stat().st_size > 64*1024:
            raise SemanticError("invalid cache file")
        try:
            record = json.loads(path.read_bytes())
            if set(record) != {"identity", "features", "features_sha256"} or record["identity"] != identity:
                raise SemanticError("cache identity mismatch")
            features = _vector(record["features"])
            if hashlib.sha256(struct.pack("<512f", *features)).hexdigest() != record["features_sha256"]:
                raise SemanticError("cache feature digest mismatch")
            return features
        except (json.JSONDecodeError, UnicodeError, KeyError, TypeError) as exc:
            raise SemanticError("malformed cache record") from exc

    @staticmethod
    def _key(identity: dict, key: str) -> None:
        if hashlib.sha256(_json(identity)).hexdigest() != key:
            raise SemanticError("cache key disagrees with identity")

    def write(self, identity: dict, key: str, features: object) -> None:
        self._key(identity, key)
        values = _vector(features)
        path = self.root/(key+".json")
        _unlinked(path)
        payload = _json({"identity":identity, "features":values,
                         "features_sha256":hashlib.sha256(struct.pack("<512f", *values)).hexdigest()})
        # Exclusive create is deliberate: interrupted/corrupt entries require
        # recorded diagnosis, not overwrite or invented successful recovery.
        with path.open("xb") as handle:
            handle.write(payload+b"\n")


class PinnedClipEncoder:
    """Explicit offline model-load boundary, not an execution permission check."""
    @classmethod
    def from_checkpoint(cls, checkpoint: Path, *, device: str = "cuda") -> "PinnedClipEncoder":
        # This explicit operation must occur only in the reviewed approved run.
        from scripts.a6_clip_visual import (CHECKPOINT_SHA256, CLIP_UPSTREAM_LF_SHA256,
                                            load_visual_encoder)
        import torch
        model, transform = load_visual_encoder(checkpoint, device=device)
        model.requires_grad_(False)
        torch.use_deterministic_algorithms(True)
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        torch.backends.cudnn.benchmark = False
        encoder = cls()
        encoder._model, encoder._transform, encoder._device = model, transform, device
        encoder.identity = {
            "model":"ViT-B/32", "checkpoint_sha256":CHECKPOINT_SHA256,
            "source_commit":"d05afc436d78f1c48dc0dbf8e5980a9d471f35f6",
            "source_digests":CLIP_UPSTREAM_LF_SHA256,
            "preprocess":{"short_edge":224,"crop":224,"interpolation":"bicubic",
                          "mean":[0.48145466,0.4578275,0.40821073],
                          "std":[0.26862954,0.26130258,0.27577711],"color":"canonical-rgb8-srgb"},
            "arithmetic":"torch-float32-norm-divide-then-float64-ordered-projection-tf32-off-v1",
            "device":device,
            "runtime":{"python":sys.version.split()[0],"os":platform.system(),
                       **{name:importlib.metadata.version(name) for name in ("torch","torchvision","pillow")},
                       "cuda":torch.version.cuda,
                       "gpu":torch.cuda.get_device_name() if device=="cuda" else None},
            "implementation_sha256":hashlib.sha256(Path(__file__).read_bytes()+
                Path(__file__).resolve().parents[2].joinpath("scripts/a6_clip_visual.py").read_bytes()).hexdigest(),
        }
        return encoder

    def extract_features(self, rgb: object, cache: FeatureCache | None = None) -> tuple[float, ...]:
        import torch
        from PIL import Image
        from src.data.preprocess import pixel_sha
        if (not torch.are_deterministic_algorithms_enabled()
                or torch.backends.cuda.matmul.allow_tf32 or torch.backends.cudnn.allow_tf32
                or torch.backends.cudnn.benchmark):
            raise SemanticError("declared deterministic float32 runtime flags changed")
        # Snapshot input pixels once; never trust caller-supplied digest/cache ID.
        pixels = rgb.copy()
        digest = pixel_sha(pixels)
        identity, key = feature_identity(digest, self.identity)
        cached = cache.read(identity, key) if cache else None
        if cached is not None:
            return cached
        tensor = self._transform(Image.fromarray(pixels)).unsqueeze(0).to(self._device, dtype=torch.float32)
        with torch.inference_mode(), torch.autocast(device_type=self._device, enabled=False):
            features = normalize_tensor(self._model.encode_image(tensor))
        if cache:
            cache.write(identity, key, features)
        return features


def extract_features(rgb: object, encoder: PinnedClipEncoder,
                     cache: FeatureCache | None = None) -> tuple[float, ...]:
    if not isinstance(encoder, PinnedClipEncoder) or not hasattr(encoder, "identity"):
        raise SemanticError("explicit verified CLIP encoder required")
    return encoder.extract_features(rgb, cache)
