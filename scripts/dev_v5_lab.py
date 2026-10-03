"""Development lab for the robust tier of v5: a numpy model of analysis, plan and rendering.

Development tooling, not part of the codec and not a study tool.  It
reproduces the robust tier of ``revised_watermark_v5`` (checked against the
codec by ``self_check``) and lets variants of the detector weighting and of the
embedding plan be compared on the same channel outputs, which are cached as PNG
files under ``.thesis-build/rehearsal/v5-lab/``.  Hosts are the synthetic
development hosts; no study image is read.

A variant is described by a small dict:

* ``detector``: ``"equal"`` (the codec: every slot counts once) or
  ``"informed"`` (every slot weighted by the share of the mark the embedder
  would put there, recomputed from the suspect image; see ``slot_weights``);
* ``gamma``: exponent of that weight;
* ``visibility``, ``min_psnr``, ``block_cap``, ``mask_cap``, ``weber``, ``base``:
  the embedding budget.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import revised_watermark_v4 as base  # noqa: E402
from scripts import revised_watermark_v5 as codec  # noqa: E402

OWNER = "dev-owner-0001"
SIDE = codec.CANONICAL_SIDE
BLOCK = codec.BLOCK
BLOCKS = SIDE // BLOCK
POSITIONS = codec.ROBUST_FREQUENCIES
COUNT = len(POSITIONS)
ORDER = max(max(u, v) for u, v in POSITIONS) + 1
PLANES = np.array([base._plane(u, v) for u, v in POSITIONS]).T  # (64, positions)
CHIPS = codec.CHANNEL_CHIPS
LAB = Path(__file__).resolve().parents[1] / ".thesis-build" / "rehearsal" / "v5-lab"

DEFAULT = {
    "detector": "equal",
    "gamma": 1.0,
    "visibility": 1.0,
    "min_psnr": 36.0,
    "block_cap": 1.5,
    "mask_cap": 5.0,
    "weber": 0.35,
    "base": 0.4,
    "floor": 12.0,
    "whitening": 1.0,
    "design_gain": 0.5,
    "design_noise": 0.3,
}


def luma(rgb: np.ndarray) -> np.ndarray:
    rgb = rgb.astype(np.float64)
    return 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]


_AREA: dict[int, np.ndarray] = {}


def _area(source: int) -> np.ndarray:
    if source not in _AREA:
        matrix = np.zeros((SIDE, source))
        for index, row in enumerate(base._area_weights(source, SIDE)):
            for position, weight in row:
                matrix[index, position] = weight
        _AREA[source] = matrix
    return _AREA[source]


def coarse(y: np.ndarray) -> np.ndarray:
    return _area(y.shape[0]) @ y @ _area(y.shape[1]).T


def coefficients(grid: np.ndarray) -> np.ndarray:
    """(blocks, positions) orthonormal DCT coefficients of the coarse grid, blocks row-major."""
    return grid.reshape(BLOCKS, BLOCK, BLOCKS, BLOCK).transpose(0, 2, 1, 3).reshape(BLOCKS * BLOCKS, 64) @ PLANES


def whitening(exponent: float) -> np.ndarray:
    return np.array([math.hypot(u, v) ** exponent for u, v in POSITIONS])


def cell_deviation(y: np.ndarray, cell: int) -> np.ndarray:
    height, width = y.shape
    return y[: height // cell * cell, : width // cell * cell].reshape(height // cell, cell, width // cell, cell).std(axis=(1, 3))


def activity(grid: np.ndarray, y: np.ndarray, cell: int = BLOCK, rank: int = 1) -> np.ndarray:
    """numpy copy of ``codec._activity`` (``cell`` 8, ``rank`` 1); other values give a finer flatness measure."""
    height, width = y.shape
    cells = cell_deviation(y, cell)

    def span(index: int, pixels: int, count: int) -> range:
        first = int(index * pixels / BLOCKS) // cell
        last = -(-int(math.ceil((index + 1) * pixels / BLOCKS)) // cell)
        return range(min(first, count - 1), max(min(last, count), min(first, count - 1) + 1))

    fine = np.empty((BLOCKS, BLOCKS))
    for by in range(BLOCKS):
        rows = span(by, height, cells.shape[0])
        for bx in range(BLOCKS):
            columns = span(bx, width, cells.shape[1])
            values = np.sort(cells[rows.start : rows.stop, columns.start : columns.stop], axis=None)
            fine[by, bx] = values[min(rank, values.size - 1)]
    half = BLOCK // 2
    offsets = np.arange(half) - (half - 1) / 2.0
    quads = grid.reshape(BLOCKS, 2, half, BLOCKS, 2, half).transpose(0, 3, 1, 4, 2, 5)  # by, bx, qy, qx, y, x
    mean = quads.mean(axis=(4, 5), keepdims=True)
    spread = half * float((offsets**2).sum())
    slope_y = (quads.sum(axis=5) * offsets).sum(axis=4) / spread
    slope_x = (quads.sum(axis=4) * offsets).sum(axis=4) / spread
    fit = mean + slope_y[..., None, None] * offsets[:, None] + slope_x[..., None, None] * offsets[None, :]
    residual = np.sqrt(((quads - fit) ** 2).mean(axis=(4, 5))).min(axis=(2, 3))
    return np.minimum(fine, residual).reshape(-1)


def averaging_gains(height: int, width: int) -> np.ndarray:
    gy, gx = codec._averaging_gain(height, ORDER), codec._averaging_gain(width, ORDER)
    return np.array([gy[u] * gx[v] for u, v in POSITIONS])


class Keys:
    """Carrier and key tables of one owner under the default public profile."""

    def __init__(self, owner: str = OWNER, profile=None):
        self.checked, self.key, self.config = codec._resolve(profile or codec.DEFAULT_PROFILE, None)
        self.owner = codec.canonical_owner(owner)
        chip, sign, _norms = codec._robust_carrier(self.key, self.config, self.owner, COUNT)
        self.chip = np.array(chip)
        self.sign = np.array(sign)
        table = codec._semantic_table(self.owner, self.key, self.config)
        self.options = np.array([[table[j][b] for b in (0, 1)] for j in range(codec.CODE_BITS)])  # (32, 2, 10)

    def q(self, y: np.ndarray) -> int:
        h, w = y.shape
        means = y[: h // BLOCK * BLOCK, : w // BLOCK * BLOCK].reshape(h // BLOCK, BLOCK, w // BLOCK, BLOCK).mean(axis=(1, 3))
        return codec._semantic(means.tolist(), self.checked, self.key, self.config, None, binding=False)

    def pattern(self, q: int) -> np.ndarray:
        return np.concatenate([self.options[j, codec._bit(q, j)] for j in range(codec.CODE_BITS)])


class Analysis:
    """Robust-tier analysis of one luminance image under a variant."""

    def __init__(self, y: np.ndarray, keys: Keys, variant: dict):
        self.y = y
        self.grid = coarse(y)
        self.c = coefficients(self.grid)
        self.w = whitening(variant["whitening"])
        floor = variant["floor"]
        self.n = np.sqrt(floor * floor + ((self.c * self.w) ** 2).mean(axis=1))
        self.v = (self.c * self.w / self.n[:, None]).reshape(-1)
        self.gains = averaging_gains(*y.shape)
        texture = activity(self.grid, y, variant.get("fine_cell", BLOCK), variant.get("fine_rank", 1))
        self.mask = np.minimum(variant["mask_cap"], np.hypot(variant["base"], variant["weber"] * texture))
        self.d = slot_weights(self, variant)
        self.keys = keys
        self.norms = np.sqrt(np.bincount(keys.chip, weights=self.d**2, minlength=CHIPS))
        self.x = np.bincount(keys.chip, weights=self.d * keys.sign * self.v, minlength=CHIPS) / self.norms

    def costs(self, variant: dict) -> tuple[np.ndarray, np.ndarray]:
        """Per slot, the cost of a unit move of the normalised coefficient in the visibility and the PSNR budget."""
        energy = (self.n[:, None] / (self.w * self.gains)) ** 2 / (BLOCK * BLOCK)
        blocks = self.n.size
        floor_mse = 255.0**2 / 10.0 ** (variant["min_psnr"] / 10.0)
        seen = energy / (self.mask[:, None] ** 2 * variant["visibility"] ** 2 * blocks)
        spent = energy / (floor_mse * blocks)
        return seen.reshape(-1), spent.reshape(-1)


def slot_weights(analysis: Analysis, variant: dict) -> np.ndarray:
    """Detector weight of every slot.

    ``informed``: the inverse of the slot's visibility cost, i.e. how much of a
    chip's move the visibility-bound plan would put there, to the power
    ``gamma``.  It depends on the image only, never on the key.
    """
    table = np.asarray(variant.get("position_weights") or [1.0] * COUNT, dtype=np.float64)
    if variant["detector"] == "equal":
        return np.tile(table, analysis.c.shape[0])
    energy = (analysis.n[:, None] / (analysis.w * analysis.gains)) ** 2
    inverse = (analysis.mask[:, None] ** 2 / energy) ** variant["gamma"] * table
    weights = inverse.reshape(-1)
    return weights / math.sqrt((weights**2).mean())


def score(analysis: Analysis, q: int) -> tuple[float, float, int]:
    """(recomputed score, decoded score, decoded code)."""
    x = analysis.x
    energy = math.sqrt(float((x * x).sum()))
    if energy <= 1e-12:
        return 0.0, 0.0, q
    segments = x.reshape(codec.CODE_BITS, codec.SEGMENT_CHIPS)
    scores = (analysis.keys.options * segments[:, None, :]).sum(axis=2)  # (32, 2)
    own = np.array([codec._bit(q, j) for j in range(codec.CODE_BITS)])
    fixed = scores[np.arange(codec.CODE_BITS), own].sum()
    chosen = np.where(scores[np.arange(codec.CODE_BITS), own] >= scores[np.arange(codec.CODE_BITS), 1 - own], own, 1 - own)
    best = scores[np.arange(codec.CODE_BITS), chosen].sum()
    code = int("".join(str(int(b)) for b in chosen), 2)
    return float(fixed / energy), float(best / energy), code


def plan(analysis: Analysis, pattern: np.ndarray, variant: dict, boost: float = 1.0) -> dict:
    """numpy copy of ``codec._plan_robust`` generalised to detector weights ``analysis.d``.

    ``boost`` tells the host-rejection search how much the fill will scale the
    plan up afterwards (1 in the codec).
    """
    seen, spent = analysis.costs(variant)
    chip, sign, d = analysis.keys.chip, analysis.keys.sign, analysis.d
    host = analysis.x
    power = float((host * host).mean())
    norms2 = analysis.norms**2
    gain, noise = variant["design_gain"], variant["design_noise"]
    best = None
    for step in range(10, -1, -1):
        share = step / 10.0
        unit = share * seen + (1.0 - share) * spent
        capacity = np.bincount(chip, weights=d * d / unit, minlength=CHIPS)
        seen_sum = np.bincount(chip, weights=seen * (d / unit) ** 2, minlength=CHIPS)
        spent_sum = np.bincount(chip, weights=spent * (d / unit) ** 2, minlength=CHIPS)
        cost = norms2 / capacity
        total = cost.sum()
        cross = (cost * pattern * host).sum()
        square = (cost * host * host).sum()
        found = None
        for rejection in np.arange(41) / 40.0 * variant.get("rejection_max", 1.0):
            disc = (rejection * cross) ** 2 - total * (rejection * rejection * square - 1.0)
            if disc <= 0.0:
                continue
            amplitude = (rejection * cross + math.sqrt(disc)) / total
            if amplitude <= 0.0:
                continue
            moves = amplitude * pattern - rejection * host
            factors = moves**2 * norms2 / capacity**2
            used = max((factors * seen_sum).sum(), (factors * spent_sum).sum())
            scale = 1.0 / math.sqrt(used)
            final = scale * boost
            promise = gain * amplitude * final / math.sqrt((1.0 - gain * rejection * final) ** 2 * power + noise * noise)
            if found is None or promise > found[0]:
                found = (promise, share, rejection, amplitude, scale)
        if found is not None and (best is None or found[0] > best[0] * 1.01):
            best = found
    _promise, share, rejection, amplitude, scale = best
    unit = share * seen + (1.0 - share) * spent
    capacity = np.bincount(chip, weights=d * d / unit, minlength=CHIPS)
    moves = scale * (amplitude * pattern - rejection * host)
    delta = moves[chip] * analysis.norms[chip] * d * sign / (unit * capacity[chip])
    change = delta.reshape(-1, COUNT) * analysis.n[:, None] / analysis.w
    return {"change": change, "share": share, "rejection": rejection * scale, "amplitude": amplitude * scale}


def limit(change: np.ndarray, analysis: Analysis, variant: dict) -> tuple[np.ndarray, dict]:
    """numpy copy of ``codec._limit_robust`` (closed-form change)."""
    gains, mask = analysis.gains, analysis.mask
    visibility = variant["visibility"]
    block_cap = variant["block_cap"] * (visibility if variant.get("block_cap_abs") is None else 1.0)
    floor_mse = 255.0**2 / 10.0 ** (variant["min_psnr"] / 10.0)
    ratios = np.sqrt(((change / gains) ** 2).sum(axis=1) / 64.0) / mask
    rms = math.sqrt(float((ratios**2).mean()))
    scale = min(1.0, visibility / rms)
    clip = np.where(ratios > 0, np.minimum(1.0, block_cap / np.maximum(ratios * scale, 1e-300)), 0.0)
    scaled = change * scale * clip[:, None]
    error = float(((scaled / gains) ** 2).sum() / (64.0 * scaled.shape[0]))
    if error > floor_mse:
        scaled = scaled * math.sqrt(floor_mse / error)
        error = floor_mse
    if variant.get("fill"):
        scaled, error = fill(change, ratios, gains, block_cap, floor_mse)
    ratios = np.sqrt(((scaled / gains) ** 2).sum(axis=1) / 64.0) / mask
    return scaled, {"ratio_rms": math.sqrt(float((ratios**2).mean())), "ratio_max": float(ratios.max()), "planned_mse": error}


def fill(change: np.ndarray, ratios: np.ndarray, gains: np.ndarray, block_cap: float, floor_mse: float) -> tuple[np.ndarray, float]:
    """Scale the planned shape up until the PSNR floor is met, every block clipped at its own cap.

    The visibility budget then acts block by block (a just-noticeable-difference
    model) and the PSNR floor is the only global limit.
    """
    energy = ((change / gains) ** 2).sum(axis=1) / 64.0  # mean squared change of each block for scale 1

    def mse(scale: float) -> float:
        factors = np.minimum(scale, block_cap / np.maximum(ratios, 1e-300))
        return float((energy * factors**2).sum() / change.shape[0])

    high = 1.0
    while mse(high) < floor_mse and high < 1e6:
        if mse(high * 2.0) == mse(high):  # every block at its cap
            break
        high *= 2.0
    low = 0.0
    for _ in range(60):
        middle = (low + high) / 2.0
        if mse(middle) < floor_mse:
            low = middle
        else:
            high = middle
    factors = np.minimum(low, block_cap / np.maximum(ratios, 1e-300))
    return change * factors[:, None], mse(low)


def render(height: int, width: int, change: np.ndarray, gains: np.ndarray) -> np.ndarray:
    """numpy copy of ``codec._render``: full-resolution change from per-block coefficient moves."""

    def axis(source: int):
        coordinate = (np.arange(source) + 0.5) * SIDE / source
        block = np.minimum(BLOCKS - 1, (coordinate // BLOCK).astype(int))
        local = coordinate - block * BLOCK
        basis = np.stack([(math.sqrt(1.0 / BLOCK) if u == 0 else math.sqrt(2.0 / BLOCK)) * np.cos(local * u * math.pi / BLOCK) for u in range(ORDER)], axis=1)
        return block, basis

    rows, row_basis = axis(height)
    columns, column_basis = axis(width)
    amplitudes = np.zeros((BLOCKS * BLOCKS, ORDER, ORDER))
    for index, (u, v) in enumerate(POSITIONS):
        amplitudes[:, u, v] = change[:, index] / gains[index]
    amplitudes = amplitudes.reshape(BLOCKS, BLOCKS, ORDER, ORDER)
    # out[y, x] = sum_uv row_basis[y, u] * A[rows[y], columns[x], u, v] * column_basis[x, v]
    per_row = np.einsum("yu,ybuv->ybv", row_basis, amplitudes[rows])  # (height, blocks_x, order)
    return np.einsum("ybv,xv->yxb", per_row, column_basis)[np.arange(height)[:, None], np.arange(width)[None, :], columns[None, :]]


def shape_factors(y: np.ndarray, variant: dict) -> np.ndarray:
    """Per pixel: how much of the planned change a fine cell takes, from its own texture.

    Every ``cell`` x ``cell`` pixel cell gets the just-noticeable level of the
    mask formula from its own standard deviation; a cell flatter than the
    ``percentile``-th cell of its coarse block takes a proportionally smaller
    share of the change.  Cells as busy as most of their block are left alone.
    """
    if variant.get("shape_mode") == "pixel":
        return pixel_shape_factors(y, variant)
    cell = variant.get("shape_cell", 4)
    height, width = y.shape
    levels = np.hypot(variant["base"], variant["weber"] * cell_deviation(y, cell))
    rows, columns = levels.shape
    per_block_y, per_block_x = rows // BLOCKS, columns // BLOCKS
    grouped = levels[: per_block_y * BLOCKS, : per_block_x * BLOCKS].reshape(BLOCKS, per_block_y, BLOCKS, per_block_x)
    reference = np.percentile(grouped, variant.get("shape_percentile", 25), axis=(1, 3))
    factors = np.minimum(1.0, grouped / reference[:, None, :, None]).reshape(per_block_y * BLOCKS, per_block_x * BLOCKS)
    out = np.ones((height, width))
    out[: factors.shape[0] * cell, : factors.shape[1] * cell] = np.kron(factors, np.ones((cell, cell)))
    return out


def local_flatness(y: np.ndarray, window: int) -> np.ndarray:
    """Per pixel: the standard deviation of the flattest ``window`` x ``window`` window that contains it."""
    from numpy.lib.stride_tricks import sliding_window_view

    windows = sliding_window_view(y, (window, window))
    deviation = windows.std(axis=(2, 3))  # (h - w + 1, w - w + 1), one value per window position
    padded = np.pad(deviation, window - 1, mode="constant", constant_values=np.inf)
    return sliding_window_view(padded, (window, window)).min(axis=(2, 3))  # back to (h, w)


def pixel_shape_factors(y: np.ndarray, variant: dict) -> np.ndarray:
    """Like ``shape_factors`` with one level per pixel from ``local_flatness``."""
    height, width = y.shape
    levels = np.hypot(variant["base"], variant["weber"] * local_flatness(y, variant.get("shape_window", 3)))
    out = np.ones((height, width))
    rows = [(index * height // BLOCKS, (index + 1) * height // BLOCKS) for index in range(BLOCKS)]
    columns = [(index * width // BLOCKS, (index + 1) * width // BLOCKS) for index in range(BLOCKS)]
    for top, bottom in rows:
        for left, right in columns:
            block = levels[top:bottom, left:right]
            reference = np.percentile(block, variant.get("shape_percentile", 25))
            out[top:bottom, left:right] = np.minimum(1.0, block / reference)
    return out


def shaped_fill(y: np.ndarray, change: np.ndarray, analysis: Analysis, variant: dict) -> tuple[np.ndarray, dict]:
    """Render the planned shape, apply the pixel shaping, then scale every block up to the PSNR floor.

    The block cap and the PSNR floor are measured on the shaped change, i.e. on
    what is actually added to the image.  Image sides must be multiples of 16.
    """
    height, width = y.shape
    unit = render(height, width, change, analysis.gains) * shape_factors(y, variant)
    bh, bw = height // BLOCKS, width // BLOCKS
    energy = (unit**2).reshape(BLOCKS, bh, BLOCKS, bw).mean(axis=(1, 3)).reshape(-1)
    ratios = np.sqrt(energy) / analysis.mask
    cap = variant["block_cap"]
    floor_mse = 255.0**2 / 10.0 ** (variant["min_psnr"] / 10.0)

    def mse(scale: float) -> float:
        return float((energy * np.minimum(scale, cap / np.maximum(ratios, 1e-300)) ** 2).mean())

    high = 1.0
    while mse(high) < floor_mse and mse(high * 2.0) > mse(high) * (1 + 1e-12) and high < 1e6:
        high *= 2.0
    low = 0.0
    for _ in range(60):
        middle = (low + high) / 2.0
        low, high = (middle, high) if mse(middle) < floor_mse else (low, middle)
    factors = np.minimum(low, cap / np.maximum(ratios, 1e-300))
    delta = unit * np.kron(factors.reshape(BLOCKS, BLOCKS), np.ones((bh, bw)))
    final = np.sqrt(energy) * factors / analysis.mask
    return delta, {"ratio_rms": float(np.sqrt((final**2).mean())), "ratio_max": float(final.max()), "planned_mse": mse(low)}


def mark(rgb: np.ndarray, keys: Keys, variant: dict, q: int | None = None) -> tuple[np.ndarray, dict]:
    """Robust tier only, closed form, onto an RGB image (the fragile tier is left out of the lab)."""
    y = luma(rgb)
    analysis = Analysis(y, keys, variant)
    q = keys.q(y) if q is None else q
    planned = plan(analysis, keys.pattern(q), variant)
    if variant.get("shape_fill"):
        delta, limits = shaped_fill(y, planned["change"], analysis, variant)
        if variant.get("two_pass"):
            unit = render(*y.shape, planned["change"], analysis.gains) * shape_factors(y, variant)
            boost = math.sqrt(float((delta**2).mean()) / float((unit**2).mean()))
            planned = plan(analysis, keys.pattern(q), variant, boost)
            delta, limits = shaped_fill(y, planned["change"], analysis, variant)
            limits["boost"] = boost
    else:
        change, limits = limit(planned["change"], analysis, variant)
        delta = render(*y.shape, change, analysis.gains)
        if variant.get("shape"):
            delta = delta * shape_factors(y, variant)
    shift = np.clip(y + delta, 0.0, 255.0) - y
    out = np.clip(np.floor(rgb.astype(np.float64) + shift[..., None] + 0.5), 0, 255).astype(np.uint8)
    difference = out.astype(np.float64) - rgb
    info = {
        "q": q,
        "rgb_psnr": float(10 * np.log10(255.0**2 / (difference**2).mean())),
        "worst_block_rms": float(np.sqrt((difference**2).mean(axis=2).reshape(16, y.shape[0] // 16, 16, y.shape[1] // 16).mean(axis=(1, 3))).max()),
        **{key: planned[key] for key in ("share", "rejection", "amplitude")},
        **limits,
    }
    return out, info


def self_check() -> None:
    """The numpy model against the codec on one procedural host."""
    from scripts import dev_v5_channel_probe as probe

    rgb = probe.procedural(100)
    y = luma(rgb)
    keys = Keys()
    analysis = Analysis(y, keys, DEFAULT)
    robust = codec._Robust(codec._coarse(y.tolist()), keys.checked, codec._robust_carrier(keys.key, keys.config, keys.owner, COUNT))
    assert np.allclose(analysis.x, robust.projections, atol=1e-9), "projections"
    assert np.allclose(analysis.mask, [min(5.0, math.hypot(0.4, 0.35 * a)) for a in codec._activity(codec._coarse(y.tolist()), y.tolist())]), "mask"
    q = keys.q(y)
    reference = codec._plan_robust(robust, codec._coarse(y.tolist()), y.tolist(), keys.pattern(q).tolist(), keys.checked)
    planned = plan(analysis, keys.pattern(q), DEFAULT)
    assert np.allclose(planned["change"], np.array(reference["change"]), atol=1e-9), "plan"
    change, _ = limit(planned["change"], analysis, DEFAULT)
    ref_change, _ = codec._limit_robust(reference["change"], reference["gains"], reference["mask"], keys.checked["embedding"], external=False)
    assert np.allclose(change, np.array(ref_change), atol=1e-9), "limit"
    ours = render(*y.shape, change, analysis.gains)
    theirs = np.array(codec._render(*y.shape, POSITIONS, [[value / gain for value, gain in zip(block, reference["gains"])] for block in ref_change]))
    assert np.allclose(ours, theirs, atol=1e-9), "render"
    marked, _ = mark(rgb, keys, DEFAULT)
    result = codec.detect_rgb(marked.tolist(), OWNER)
    ours = score(Analysis(luma(marked), keys, DEFAULT), keys.q(luma(marked)))
    assert abs(ours[0] - result["semantic"]["recomputed_score"]) < 1e-9, "score"
    print("self-check passed; recomputed score", round(ours[0], 3))


if __name__ == "__main__":
    self_check()
