"""Small CPU-only reference for A5's deterministic latent streams.

This is a byte/numeric unit-test oracle, not a model sampler or scientific run.
It deliberately caps output size and uses no torch, NumPy, image or network API.
"""

from __future__ import annotations

import hashlib
import math
import struct


_DOMAIN = b"a5-base-noise-v1"
_CARRIER_DOMAIN = b"a5-carrier-v1"
_MAX_ELEMENTS = 1_000_000


def _pack(fields: tuple[bytes, ...]) -> bytes:
    return b"".join(struct.pack(">I", len(field)) + field for field in fields)


def _hex_digest(value: str, label: str) -> bytes:
    if (not isinstance(value, str) or len(value) != 64
            or any(char not in "0123456789abcdef" for char in value)):
        raise ValueError(f"{label} must be 64 lowercase hex characters")
    return bytes.fromhex(value)


def _latent_dimensions(seed: int, channels: int, height: int,
                       width: int) -> tuple[tuple[int, int, int], int]:
    if type(seed) is not int or not 0 <= seed < 2**64:
        raise ValueError("seed must be uint64")
    dims = (channels, height, width)
    if any(type(dim) is not int or not 1 <= dim < 2**32 for dim in dims):
        raise ValueError("latent dimensions must be positive uint32")
    count = channels * height * width
    if count > _MAX_ELEMENTS:
        raise ValueError("reference output exceeds one million elements")
    return dims, count


def base_noise_f32le(seed: int, source_sha256_hex: str,
                     channels: int, height: int, width: int) -> bytes:
    """Return C/H/W ordered float32 values as canonical little-endian bytes.

    Uses length-prefixed fields, big-endian integers and U64 XOF words as
    specified in research/method-spec.md. Box-Muller math is Python's libm;
    cross-runtime numeric parity is *not* presumed from this reference.
    """
    dims, count = _latent_dimensions(seed, channels, height, width)
    framed = _pack((_DOMAIN, seed.to_bytes(8, "big"),
                    _hex_digest(source_sha256_hex, "source digest"),
                    *(dim.to_bytes(4, "big") for dim in dims)))
    words = hashlib.shake_256(framed).digest(16 * ((count + 1) // 2))
    output = bytearray()
    for offset in range(0, len(words), 16):
        x1, x2 = struct.unpack_from(">QQ", words, offset)
        u1 = (x1 + 0.5) / 2**64
        u2 = (x2 + 0.5) / 2**64
        radius = math.sqrt(-2.0 * math.log(u1))
        angle = 2.0 * math.pi * u2
        for value in (radius * math.cos(angle), radius * math.sin(angle)):
            if len(output) == 4 * count:
                break
            if not math.isfinite(value):
                raise ValueError("nonfinite Box-Muller output")
            output.extend(struct.pack("<f", value))
    return bytes(output)


def unit_carrier_f32le(component: str, signature_hex: str, seed: int,
                       channels: int, height: int, width: int,
                       detector_config_id_hex: str) -> bytes:
    """Return A5's unit-norm Rademacher carrier in C/H/W float32 order.

    The exact mathematical amplitude is 1/sqrt(C*h*w). The returned bytes are
    rounded float32 values, whose measured norm may differ slightly from one.
    Component 's' and 'i' are separate streams; no source image is read.
    """
    if component not in ("s", "i") or type(component) is not str:
        raise ValueError("component must be 's' or 'i'")
    dims, count = _latent_dimensions(seed, channels, height, width)
    framed = _pack((_CARRIER_DOMAIN, component.encode("ascii"),
                    _hex_digest(signature_hex, "signature"),
                    seed.to_bytes(8, "big"),
                    *(dim.to_bytes(4, "big") for dim in dims),
                    _hex_digest(detector_config_id_hex, "detector config ID")))
    bits = hashlib.shake_256(framed).digest((count + 7) // 8)
    magnitude = 1.0 / math.sqrt(count)
    output = bytearray()
    for index in range(count):
        bit = (bits[index // 8] >> (index % 8)) & 1
        output.extend(struct.pack("<f", magnitude if bit else -magnitude))
    return bytes(output)
