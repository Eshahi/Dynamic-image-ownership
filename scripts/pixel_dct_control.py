"""Synthetic, model-free pixel-DCT comparator reference for B2.

Signatures are derived from supplied A5 q/H codes and public OwnerID; templates
also need a validated detector-configuration digest. This module does not
extract q/H from images, choose gains, calibrate thresholds, load images, or
execute an experiment.
"""

from __future__ import annotations

import hashlib
import math
import unicodedata


SEMANTIC_FREQUENCIES = ((1, 2), (2, 1), (2, 2), (1, 3))
INSTANCE_FREQUENCIES = ((3, 1), (2, 3), (3, 2), (1, 4))
_BASIS = tuple(
    tuple(math.sqrt(1 / 8) if k == 0 else math.sqrt(2 / 8) * math.cos(math.pi * (n + .5) * k / 8)
          for n in range(8))
    for k in range(8)
)


def _pack(fields: tuple[bytes, ...]) -> bytes:
    return b"".join(len(field).to_bytes(4, "big") + field for field in fields)


def keys_from_codes(q_bytes: bytes, phash_bytes: bytes, owner_id: str) -> tuple[bytes, bytes]:
    """Derive A5's public Ws/Wi digests from already-extracted source codes.

    This does not authenticate owner enrollment or establish image-to-code
    stability. Those are separate experimental and trust-model obligations.
    """
    if not isinstance(q_bytes, bytes) or len(q_bytes) != 2 or q_bytes[1] & 0xF0:
        raise ValueError("q must be a canonical packed 12-bit code")
    if not isinstance(phash_bytes, bytes) or len(phash_bytes) != 4:
        raise ValueError("pHash must be a packed 32-bit code")
    if not isinstance(owner_id, str) or unicodedata.normalize("NFC", owner_id) != owner_id:
        raise ValueError("OwnerID must be NFC text")
    try:
        owner = owner_id.encode("utf-8")
    except UnicodeEncodeError as error:
        raise ValueError("OwnerID must be valid UTF-8 text") from error
    if not 1 <= len(owner) <= 256:
        raise ValueError("OwnerID must have 1..256 UTF-8 bytes")
    semantic = hashlib.sha256(_pack((b"a5-ws-v1", q_bytes, owner))).digest()
    instance = hashlib.sha256(_pack((b"a5-wi-v1", q_bytes, phash_bytes, owner))).digest()
    return semantic, instance


def templates_from_keys(
    semantic_key: bytes, instance_key: bytes, detector_config_id: bytes,
    width: int, height: int,
) -> tuple[tuple[tuple[int, ...], ...], tuple[tuple[int, ...], ...]]:
    """A5 SHAKE256 Rademacher templates on the original image block grid.

    All three digests are raw 32-byte values, not hex text; the caller must
    decode the schema's 64-character config-ID hex after verifying it, and
    derive the keys from canonical q/H/OwnerID. This
    function deliberately cannot authenticate those claims.
    """
    if type(width) is not int or type(height) is not int or not 32 <= width <= 0xFFFFFFFF or not 32 <= height <= 0xFFFFFFFF:
        raise ValueError("image dimensions must fit uint32 and be at least 32")
    for name, digest in (("semantic_key", semantic_key), ("instance_key", instance_key),
                         ("detector_config_id", detector_config_id)):
        if not isinstance(digest, bytes) or len(digest) != 32:
            raise ValueError(f"{name} must be a raw 32-byte digest")
    blocks = ((width + 7) // 8) * ((height + 7) // 8)

    def one(component: bytes, key: bytes) -> tuple[tuple[int, ...], ...]:
        payload = _pack((b"a5-template-v1", component, key,
                        height.to_bytes(4, "big"), width.to_bytes(4, "big"),
                        detector_config_id))
        stream = hashlib.shake_256(payload).digest((blocks * 4 + 7) // 8)
        signs = tuple(1 if (stream[j // 8] >> (j % 8)) & 1 else -1
                      for j in range(blocks * 4))
        return tuple(signs[4 * block:4 * block + 4] for block in range(blocks))

    return one(b"s", semantic_key), one(b"i", instance_key)


def dct8(block: tuple[tuple[float, ...], ...]) -> tuple[tuple[float, ...], ...]:
    """Orthonormal 8x8 DCT-II, with mathematical vertical/horizontal axes."""
    if len(block) != 8 or any(len(row) != 8 for row in block):
        raise ValueError("DCT block must be 8x8")
    if any(not math.isfinite(value) for row in block for value in row):
        raise ValueError("DCT input must be finite")
    horizontal = [[math.fsum(block[y][x] * _BASIS[v][x] for x in range(8))
                   for v in range(8)] for y in range(8)]
    return tuple(tuple(math.fsum(_BASIS[u][y] * horizontal[y][v] for y in range(8))
                       for v in range(8)) for u in range(8))


def idct8(coefficients: tuple[tuple[float, ...], ...]) -> tuple[tuple[float, ...], ...]:
    """Inverse of dct8; no clamping or quantization is hidden here."""
    if len(coefficients) != 8 or any(len(row) != 8 for row in coefficients):
        raise ValueError("DCT coefficients must be 8x8")
    if any(not math.isfinite(value) for row in coefficients for value in row):
        raise ValueError("DCT coefficients must be finite")
    vertical = [[math.fsum(_BASIS[u][y] * coefficients[u][v] for u in range(8))
                 for v in range(8)] for y in range(8)]
    return tuple(tuple(math.fsum(vertical[y][v] * _BASIS[v][x] for v in range(8))
                       for x in range(8)) for y in range(8))


def _validate_template(template: tuple[tuple[int, ...], ...], blocks: int) -> None:
    if (not isinstance(template, tuple) or len(template) != blocks
            or any(not isinstance(row, tuple) or len(row) != 4
                   or any(type(value) is not int or value not in (-1, 1) for value in row)
                   for row in template)):
        raise ValueError("template must have one four-sign tuple per padded block")


def _validate_rgb8(rgb8: bytes, width: int, height: int) -> tuple[int, int]:
    if (type(width) is not int or type(height) is not int
            or width < 32 or height < 32):
        raise ValueError("RGB8 dimensions must be integers at least 32")
    if not isinstance(rgb8, bytes) or len(rgb8) != width * height * 3:
        raise ValueError("RGB8 byte length does not match dimensions")
    return (width + 7) // 8, (height + 7) // 8


def _luminance_block(rgb8: bytes, width: int, height: int,
                     block_x: int, block_y: int) -> tuple[tuple[float, ...], ...]:
    def value(x: int, y: int) -> float:
        pixel = 3 * (min(y, height - 1) * width + min(x, width - 1))
        return (0.299 * rgb8[pixel] + 0.587 * rgb8[pixel + 1]
                + 0.114 * rgb8[pixel + 2]) / 255

    return tuple(tuple(value(block_x * 8 + x, block_y * 8 + y)
                       for x in range(8)) for y in range(8))


def embed_pixel_dct(
    rgb8: bytes, width: int, height: int,
    semantic_template: tuple[tuple[int, ...], ...],
    instance_template: tuple[tuple[int, ...], ...],
    semantic_gain: float, instance_gain: float,
) -> bytes:
    """Add fixed A5-frequency templates to RGB8 luminance DCT coefficients.

    The output grid is unchanged. Right/bottom padding replicates edge pixels
    only while computing blocks. The inverse-DCT luminance delta is applied
    equally to R/G/B, then clamped and ties-to-even rounded to RGB8. There is
    exactly one attempt: no score/quality feedback or strength retries.
    """
    block_columns, block_rows = _validate_rgb8(rgb8, width, height)
    for gain in (semantic_gain, instance_gain):
        if isinstance(gain, bool) or not isinstance(gain, (int, float)) or not math.isfinite(gain) or gain < 0:
            raise ValueError("gains must be finite and nonnegative")
    blocks = block_columns * block_rows
    _validate_template(semantic_template, blocks)
    _validate_template(instance_template, blocks)
    if semantic_gain == 0 and instance_gain == 0:
        return rgb8

    output = bytearray(rgb8)
    for block_y in range(block_rows):
        for block_x in range(block_columns):
            block_index = block_y * block_columns + block_x
            luminance = _luminance_block(rgb8, width, height, block_x, block_y)
            coefficients = [list(row) for row in dct8(luminance)]
            for frequencies, template, gain in (
                (SEMANTIC_FREQUENCIES, semantic_template[block_index], semantic_gain),
                (INSTANCE_FREQUENCIES, instance_template[block_index], instance_gain),
            ):
                for (u, v), sign in zip(frequencies, template):
                    coefficients[u][v] += gain * sign
            changed = idct8(tuple(tuple(row) for row in coefficients))
            for y in range(8):
                image_y = block_y * 8 + y
                if image_y >= height:
                    break
                for x in range(8):
                    image_x = block_x * 8 + x
                    if image_x >= width:
                        break
                    delta = changed[y][x] - luminance[y][x]
                    pixel = 3 * (image_y * width + image_x)
                    for channel in range(3):
                        value = rgb8[pixel + channel] / 255 + delta
                        output[pixel + channel] = round(255 * min(1.0, max(0.0, value)))
    return bytes(output)


def score_pixel_dct(
    rgb8: bytes, width: int, height: int,
    template: tuple[tuple[int, ...], ...], component: str,
) -> tuple[float, bool]:
    """A5's one-component centered DCT cosine on supplied RGB8 and template.

    Returns (score, zero_variance). This is an oracle-component reference:
    supplying the enrollment template bypasses the blind q/H key search, so
    it must never be reported as the full A5 verification outcome or latency.
    """
    block_columns, block_rows = _validate_rgb8(rgb8, width, height)
    blocks = block_columns * block_rows
    _validate_template(template, blocks)
    if component == "semantic":
        frequencies = SEMANTIC_FREQUENCIES
    elif component == "instance":
        frequencies = INSTANCE_FREQUENCIES
    else:
        raise ValueError("component must be semantic or instance")
    observed = []
    for block_y in range(block_rows):
        for block_x in range(block_columns):
            coefficients = dct8(_luminance_block(rgb8, width, height, block_x, block_y))
            observed.append(tuple(coefficients[u][v] for u, v in frequencies))
    observed_means = tuple(math.fsum(row[f] for row in observed) / blocks for f in range(4))
    template_means = tuple(math.fsum(row[f] for row in template) / blocks for f in range(4))
    centered_observed = tuple(row[f] - observed_means[f] for row in observed for f in range(4))
    centered_template = tuple(row[f] - template_means[f] for row in template for f in range(4))
    observed_norm = math.sqrt(math.fsum(value * value for value in centered_observed))
    template_norm = math.sqrt(math.fsum(value * value for value in centered_template))
    if observed_norm <= 1e-12 or template_norm <= 1e-12:
        return 0.0, True
    score = math.fsum(x * y for x, y in zip(centered_observed, centered_template)) / (observed_norm * template_norm)
    if not math.isfinite(score) or abs(score) > 1 + 1e-9:
        raise ValueError("invalid DCT correlation")
    return max(-1.0, min(1.0, score)), False
