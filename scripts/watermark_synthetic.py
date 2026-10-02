"""Procedural hosts and standard-library distortions for watermark tests and benchmarks.

Everything here is synthetic.  The hosts stand in for photographs only in the
sense that they have smooth structure, texture and noise; results on them say
nothing about real images, JPEG files or diffusion regeneration.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.revised_watermark_v4 import block_coefficients  # noqa: E402

ALL_POSITIONS = [(u, v) for u in range(8) for v in range(8)]


def clamp(value: float) -> float:
    return float(min(255, max(0, math.floor(value + 0.5))))


def scene(seed: int, height: int = 256, width: int = 256, texture: float = 12.0, detail_seed: int | None = None) -> list[list[float]]:
    """Smooth structure, mid-scale texture and sensor noise.

    ``detail_seed`` redraws the texture and noise while keeping the structure,
    which gives different images of one composition.
    """
    rng = random.Random(seed)
    waves = [(rng.uniform(0.01, 0.09), rng.uniform(0.01, 0.09), rng.uniform(0, 6.28), rng.uniform(8, 28)) for _ in range(8)]
    if detail_seed is not None:
        rng = random.Random(detail_seed)
    coarse = [[rng.gauss(0, 1) for _ in range(width // 4 + 2)] for _ in range(height // 4 + 2)]
    image = []
    for y in range(height):
        row = []
        y0, ty = y // 4, (y % 4) / 4.0
        for x in range(width):
            x0, tx = x // 4, (x % 4) / 4.0
            grain = (
                coarse[y0][x0] * (1 - ty) * (1 - tx)
                + coarse[y0][x0 + 1] * (1 - ty) * tx
                + coarse[y0 + 1][x0] * ty * (1 - tx)
                + coarse[y0 + 1][x0 + 1] * ty * tx
            )
            value = 128.0 + sum(a * math.cos(fx * x + fy * y + phase) for fx, fy, phase, a in waves)
            row.append(clamp(value + texture * grain + rng.gauss(0, 2.0)))
        image.append(row)
    return image


def object_on_flat_background(seed: int, size: int = 256) -> list[list[float]]:
    """A textured disc at a fixed place on a flat background; only the texture varies."""
    rng = random.Random(seed)
    background = 110 + rng.uniform(-3, 3)
    texture = [[rng.gauss(0, 1) for _ in range(size // 4 + 2)] for _ in range(size // 4 + 2)]
    radius = (size * 0.22) ** 2
    return [
        [
            clamp(150 + 25 * texture[y // 4][x // 4] + rng.gauss(0, 2))
            if (x - size / 2) ** 2 + (y - size / 2) ** 2 < radius
            else clamp(background + rng.gauss(0, 1.5))
            for x in range(size)
        ]
        for y in range(size)
    ]


def sawtooth(size: int = 160) -> list[list[float]]:
    """The modular-arithmetic pattern of the v2/v3 tests: enormous mid-band energy."""
    return [[float((x * 17 + y * 29 + ((x * y) % 37)) % 256) for x in range(size)] for y in range(size)]


def plain_hosts(size: int = 256) -> dict[str, list[list[float]]]:
    """Hosts with little or no texture: the cases a detail-based hash finds hardest."""
    base = scene(1, size, size)
    return {
        "low contrast": [[clamp(120 + (value - 128) * 0.08) for value in row] for row in base],
        "gradient": [[clamp(40 + 0.5 * x + 0.25 * y) for x in range(size)] for y in range(size)],
        "three tones": [[float((60, 130, 200)[(x // 90 + y // 110) % 3]) for x in range(size)] for y in range(size)],
        "smooth waves": scene(3, size, size, texture=0.0),
    }


def add_noise(image, sigma: float, seed: int = 9):
    rng = random.Random(seed)
    return [[clamp(value + rng.gauss(0, sigma)) for value in row] for row in image]


def scale(image, gain: float, offset: float = 0.0):
    return [[clamp(value * gain + offset) for value in row] for row in image]


def box_blur(image, radius: int = 1):
    height, width = len(image), len(image[0])
    span = range(-radius, radius + 1)
    count = float(len(span) ** 2)
    output = []
    for y in range(height):
        rows = [image[min(height - 1, max(0, y + dy))] for dy in span]
        output.append([clamp(sum(row[min(width - 1, max(0, x + dx))] for row in rows for dx in span) / count) for x in range(width)])
    return output


def _rebuild(image, positions, change):
    """Apply ``change(block_index, coefficients) -> deltas`` to the listed coefficients of every block."""
    from scripts.revised_watermark_v4 import basis_plane

    planes = [basis_plane(u, v) for u, v in positions]
    output = [row[:] for row in image]
    per_row = len(image[0]) // 8
    for index, coefficients in enumerate(block_coefficients(image, positions)[1]):
        delta = [0.0] * 64
        for amount, plane in zip(change(index, coefficients), planes):
            if amount:
                delta = [value + amount * basis for value, basis in zip(delta, plane)]
        top, left = (index // per_row) * 8, (index % per_row) * 8
        for y in range(8):
            for x in range(8):
                output[top + y][left + x] = clamp(output[top + y][left + x] + delta[y * 8 + x])
    return output


def requantise(image, step: float):
    """JPEG-like loss: uniform quantisation of every 8x8 block-DCT coefficient."""
    return _rebuild(image, ALL_POSITIONS, lambda _index, block: [round(value / step) * step - value for value in block])


def replace_band(recipient, donor, positions):
    """Give ``recipient`` the donor's block-DCT coefficients at the listed positions."""
    theirs = block_coefficients(donor, positions)[1]
    return _rebuild(recipient, positions, lambda index, block: [a - b for a, b in zip(theirs[index], block)])


def residual_copy(recipient, marked, source):
    """Add the difference between a marked image and its source to another image."""
    return [[clamp(r + m - s) for r, m, s in zip(a, b, c)] for a, b, c in zip(recipient, marked, source)]


def import_block_means(recipient, donor, weight: float):
    """Move each 8x8 block mean of ``recipient`` towards the donor's by ``weight``."""
    theirs, mine = block_coefficients(donor, [])[0], block_coefficients(recipient, [])[0]
    output = [row[:] for row in recipient]
    for by, (their_row, my_row) in enumerate(zip(theirs, mine)):
        for bx, (a, b) in enumerate(zip(their_row, my_row)):
            for y in range(8):
                for x in range(8):
                    output[by * 8 + y][bx * 8 + x] = clamp(output[by * 8 + y][bx * 8 + x] + weight * (a - b))
    return output
