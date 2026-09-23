"""Synthetic, model-free pixel-DCT comparator reference for B2.

Templates must be supplied by the A5 signature/config implementation. This
module does not derive OwnerIDs, choose gains, calibrate detection thresholds,
load images, or execute a scientific experiment.
"""

from __future__ import annotations

import math


SEMANTIC_FREQUENCIES = ((1, 2), (2, 1), (2, 2), (1, 3))
INSTANCE_FREQUENCIES = ((3, 1), (2, 3), (3, 2), (1, 4))
_BASIS = tuple(
    tuple(math.sqrt(1 / 8) if k == 0 else math.sqrt(2 / 8) * math.cos(math.pi * (n + .5) * k / 8)
          for n in range(8))
    for k in range(8)
)


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
    if (type(width) is not int or type(height) is not int
            or width < 32 or height < 32):
        raise ValueError("RGB8 dimensions must be integers at least 32")
    if not isinstance(rgb8, bytes) or len(rgb8) != width * height * 3:
        raise ValueError("RGB8 byte length does not match dimensions")
    for gain in (semantic_gain, instance_gain):
        if isinstance(gain, bool) or not isinstance(gain, (int, float)) or not math.isfinite(gain) or gain < 0:
            raise ValueError("gains must be finite and nonnegative")
    block_columns, block_rows = (width + 7) // 8, (height + 7) // 8
    blocks = block_columns * block_rows
    _validate_template(semantic_template, blocks)
    _validate_template(instance_template, blocks)
    if semantic_gain == 0 and instance_gain == 0:
        return rgb8

    def luminance_at(x: int, y: int) -> float:
        pixel = 3 * (y * width + x)
        return (0.299 * rgb8[pixel] + 0.587 * rgb8[pixel + 1]
                + 0.114 * rgb8[pixel + 2]) / 255

    output = bytearray(rgb8)
    for block_y in range(block_rows):
        for block_x in range(block_columns):
            block_index = block_y * block_columns + block_x
            luminance = tuple(tuple(
                luminance_at(min(block_x * 8 + x, width - 1),
                             min(block_y * 8 + y, height - 1))
                for x in range(8)
            ) for y in range(8))
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
