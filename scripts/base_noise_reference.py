"""Small CPU-only reference for A5's deterministic base epsilon stream.

This is a byte/numeric unit-test oracle, not a model sampler or scientific run.
It deliberately caps output size and uses no torch, NumPy, image or network API.
"""

from __future__ import annotations

import hashlib
import math
import struct


_DOMAIN = b"a5-base-noise-v1"
_MAX_ELEMENTS = 1_000_000


def _pack(fields: tuple[bytes, ...]) -> bytes:
    return b"".join(struct.pack(">I", len(field)) + field for field in fields)


def base_noise_f32le(seed: int, source_sha256_hex: str,
                     channels: int, height: int, width: int) -> bytes:
    """Return C/H/W ordered float32 values as canonical little-endian bytes.

    Uses length-prefixed fields, big-endian integers and U64 XOF words as
    specified in research/method-spec.md. Box-Muller math is Python's libm;
    cross-runtime numeric parity is *not* presumed from this reference.
    """
    if type(seed) is not int or not 0 <= seed < 2**64:
        raise ValueError("seed must be uint64")
    if (not isinstance(source_sha256_hex, str) or len(source_sha256_hex) != 64
            or any(char not in "0123456789abcdef" for char in source_sha256_hex)):
        raise ValueError("source digest must be 64 lowercase hex characters")
    dims = (channels, height, width)
    if any(type(dim) is not int or not 1 <= dim < 2**32 for dim in dims):
        raise ValueError("latent dimensions must be positive uint32")
    count = channels * height * width
    if count > _MAX_ELEMENTS:
        raise ValueError("reference output exceeds one million elements")
    framed = _pack((_DOMAIN, seed.to_bytes(8, "big"),
                    bytes.fromhex(source_sha256_hex),
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
