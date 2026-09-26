"""A5 native RGB8/sRGB contract, versioned bytes and fail-closed local cache.

No resize, model, captioner, dataset discovery or scientific run lives here.
Arrays are HWC. Callers must explicitly transpose for CHW method interfaces.
"""
from __future__ import annotations

import hashlib
import io
import json
import platform
import struct
import sys
import warnings
from pathlib import Path

import numpy as np
import PIL
from PIL import Image, ImageCms, ImageOps, features


class PreprocessError(ValueError):
    """A retained coverage failure, never a clean negative detector result."""


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_bytes(value: dict) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("utf-8")


def runtime() -> dict:
    return {"python": sys.version.split()[0], "os": platform.system(),
            "pillow": PIL.__version__, "numpy": np.__version__,
            **{name: features.version(name) for name in
               ("littlecms2", "zlib", "jpg", "libjpeg_turbo")}}


def load_config(path: Path) -> tuple[dict, str]:
    # Reject unknown policy edits instead of silently ignoring a new field.
    config = json.loads(path.read_text(encoding="utf-8"))
    expected = {
        "schema_version": "b5-canonical-rgb8-v1", "input_formats": ["JPEG", "PNG"],
        "input_mode": "RGB", "orientation": "apply-exif-1-through-8",
        "color": "embedded-icc-to-srgb-perceptual-flags0-otherwise-assume-srgb",
        "normalization": "rgb8-to-float32-div255-hwc", "resize": "none-native-grid",
        "caption": "fixed-empty-string-no-source-prompts",
        "output": "png-rgb8-no-ancillary-compress6-optimizefalse",
        "quantization": "finite-clamp01-float64-times255-rint-ties-even",
    }
    if set(config) != set(expected) | {"max_source_bytes", "max_pixels", "max_icc_bytes", "runtime_profiles"}:
        raise PreprocessError("unknown/missing configuration field")
    if any(config[k] != v for k, v in expected.items()):
        raise PreprocessError("unsupported preprocessing policy")
    for name in ("max_source_bytes", "max_pixels", "max_icc_bytes"):
        if type(config[name]) is not int or config[name] <= 0:
            raise PreprocessError("invalid resource limit: " + name)
    if runtime() not in config["runtime_profiles"]:
        raise PreprocessError("unrecognized preprocessing runtime")
    return config, sha(json_bytes(config))


def pixel_sha(rgb: np.ndarray) -> str:
    if rgb.dtype != np.uint8 or rgb.ndim != 3 or rgb.shape[2] != 3:
        raise PreprocessError("pixel identity requires HWC RGB8")
    h, w, _ = rgb.shape
    return sha(b"b5-rgb8-srgb-v1\0" + struct.pack(">II", w, h) + rgb.tobytes(order="C"))


def decode_source(raw: bytes, config: dict) -> tuple[np.ndarray, dict]:
    """Consume the checked snapshot, not a second open of mutable source bytes."""
    if not raw or len(raw) > config["max_source_bytes"]:
        raise PreprocessError("unsupported_source_size")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            with Image.open(io.BytesIO(raw)) as check:
                if check.format not in config["input_formats"]:
                    raise PreprocessError("unsupported_source_format")
                if check.mode != "RGB" or "transparency" in check.info:
                    raise PreprocessError("unsupported_source_mode_or_alpha")
                if getattr(check, "n_frames", 1) != 1:
                    raise PreprocessError("unsupported_multiframe")
                if check.width * check.height > config["max_pixels"]:
                    raise PreprocessError("unsupported_pixel_count")
                # PNG RGB can conceal 16-bit input under Pillow's RGB decoder.
                if check.format == "PNG" and (raw[24] != 8 or raw[25] != 2):
                    raise PreprocessError("unsupported_png_bit_depth_or_color_type")
                check.verify()
            with Image.open(io.BytesIO(raw)) as source:
                source.load()
                orientation = source.getexif().get(274, 1)
                if type(orientation) is not int or not 1 <= orientation <= 8:
                    raise PreprocessError("invalid_exif_orientation")
                original_size = [source.width, source.height]
                profile = source.info.get("icc_profile")
                if profile is not None and (not isinstance(profile, bytes) or
                                            not profile or len(profile) > config["max_icc_bytes"]):
                    raise PreprocessError("invalid_icc_profile")
                oriented = ImageOps.exif_transpose(source)
                if profile is not None:
                    oriented = ImageCms.profileToProfile(
                        oriented, ImageCms.ImageCmsProfile(io.BytesIO(profile)),
                        ImageCms.createProfile("sRGB"), renderingIntent=0,
                        outputMode="RGB", inPlace=False, flags=0)
                rgb = np.array(oriented, dtype=np.uint8, copy=True)
                return rgb, {"raw_sha256": sha(raw), "raw_size_bytes": len(raw),
                             "source_format": source.format, "source_mode": source.mode,
                             "source_size": original_size, "exif_orientation": orientation,
                             "color_action": "icc-to-srgb" if profile is not None else "assumed-srgb-no-icc",
                             "icc_sha256": sha(profile) if profile is not None else None,
                             "width": int(rgb.shape[1]), "height": int(rgb.shape[0]),
                             "canonical_pixel_sha256": pixel_sha(rgb), "caption": "",
                             "resize_applied": False}
    except PreprocessError:
        raise
    except Exception as exc:
        # No metadata/prompt contents in the error. Retain exception type only.
        raise PreprocessError("source_decode_or_color_failure:" + type(exc).__name__) from exc


def normalized(rgb: np.ndarray) -> np.ndarray:
    pixel_sha(rgb)  # Validate RGB8, do not silently coerce unsupported inputs.
    return rgb.astype(np.float32) / np.float32(255)


def encode_output(pixels: np.ndarray) -> tuple[bytes, np.ndarray]:
    """Quantize and re-decode: only returned decoded bytes feed final metrics."""
    pixels = np.asarray(pixels)
    if pixels.ndim != 3 or pixels.shape[2] != 3 or min(pixels.shape[:2]) <= 0:
        raise PreprocessError("output_requires_nonempty_hwc_rgb")
    if pixels.dtype.kind != "f" or not np.isfinite(pixels).all():
        raise PreprocessError("output_requires_finite_float")
    rgb = np.rint(np.clip(pixels.astype(np.float64), 0, 1) * 255).astype(np.uint8)
    stream = io.BytesIO()
    # New image: no inherited EXIF/ICC/text/transparency metadata.
    Image.fromarray(rgb).save(stream, format="PNG", compress_level=6, optimize=False)
    data = stream.getvalue()
    # Encoder output must contain only critical RGB image chunks.
    offset = 8
    while offset < len(data):
        length = int.from_bytes(data[offset:offset+4], "big")
        if data[offset+4:offset+8] not in (b"IHDR", b"IDAT", b"IEND"):
            raise PreprocessError("unexpected_output_metadata")
        offset += 12 + length
    with Image.open(io.BytesIO(data)) as saved:
        saved.load()
        decoded = np.array(saved, dtype=np.uint8, copy=True)
    if not np.array_equal(rgb, decoded):
        raise PreprocessError("output_roundtrip_mismatch")
    return data, decoded


def no_links(path: Path) -> None:
    if not path.is_absolute():
        raise PreprocessError("absolute_path_required")
    for candidate in (path, *path.parents):
        if candidate.is_symlink() or getattr(candidate, "is_junction", lambda: False)():
            raise PreprocessError("linked_path_not_allowed")


def preprocess_file(source: Path, expected_sha256: str, expected_size: int,
                    cache_root: Path, config_path: Path) -> tuple[np.ndarray, dict]:
    """Native-grid preprocessing with exact-source, code, policy and runtime identity.

    A partial/corrupt cache is an error, not a reason to overwrite earlier evidence.
    Caller logs rejected image ID/error in its coverage inventory and must serialize
    writers. Cache is local-only while source rights remain pending.
    """
    config, config_sha = load_config(config_path)
    no_links(source)
    no_links(cache_root)
    if type(expected_size) is not int or not 0 < expected_size <= config["max_source_bytes"]:
        raise PreprocessError("invalid_expected_source_size")
    if not source.is_file() or source.stat().st_size != expected_size:
        raise PreprocessError("source_size_mismatch")
    with source.open("rb") as handle:
        raw = handle.read(config["max_source_bytes"] + 1)
    if len(raw) != expected_size or sha(raw) != expected_sha256:
        raise PreprocessError("source_snapshot_mismatch")
    identity = {"raw_sha256": expected_sha256, "config_sha256": config_sha,
                "code_sha256": sha(Path(__file__).read_bytes()), "runtime": runtime()}
    key = sha(json_bytes(identity))
    cache_root.mkdir(parents=True, exist_ok=True)
    png_path, receipt_path = cache_root / (key + ".png"), cache_root / (key + ".json")
    no_links(png_path)
    no_links(receipt_path)
    if png_path.exists() or receipt_path.exists():
        if not (png_path.is_file() and receipt_path.is_file()):
            raise PreprocessError("incomplete_cache_retained")
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        if receipt.get("identity") != identity or receipt.get("cache_key") != key:
            raise PreprocessError("cache_identity_mismatch")
        data = png_path.read_bytes()
        if len(data) != receipt.get("output_size_bytes") or sha(data) != receipt.get("output_sha256"):
            raise PreprocessError("cache_output_mismatch")
        rgb, _ = decode_source(data, config)
        if pixel_sha(rgb) != receipt.get("canonical_pixel_sha256"):
            raise PreprocessError("cache_pixel_mismatch")
        return normalized(rgb), receipt
    rgb, source_receipt = decode_source(raw, config)
    data, decoded = encode_output(normalized(rgb))
    if not np.array_equal(rgb, decoded):
        raise PreprocessError("canonical_rgb8_roundtrip_mismatch")
    receipt = {**source_receipt, "schema_version": "b5-preprocess-receipt-v1",
               "identity": identity, "cache_key": key, "output_sha256": sha(data),
               "output_size_bytes": len(data), "output_color": "sRGB-declared-no-icc",
               "status": "software_preprocessing_only_rights_and_science_not_accepted"}
    with png_path.open("xb") as handle:
        handle.write(data)
    with receipt_path.open("xb") as handle:
        handle.write(json_bytes(receipt) + b"\n")
    return normalized(decoded), receipt
