"""Two-tier dual-key DCT watermark, image-domain reference (revision v5).

v5 keeps the proposal's structure -- a semantic key ``Ws`` and an instance key
``Wi`` derived from a semantic code ``q``, a DCT perceptual hash ``H`` and the
OwnerID, read by correlating 8x8 block-DCT coefficients -- and changes where
the two keys live, because the retained revision-2 study showed that a 42 dB
mark on 8x8 coefficients of the full-resolution image is removed by the
autoencoder of a latent diffusion model before any diffusion step runs.

* The semantic key moves to a **robust tier**: the 8x8 block DCT of the image
  area-averaged to a fixed 128x128 grid.  For a 512x512 image a coarse block
  spans 32x32 pixels and the band used has periods of about 16 to 64 pixels,
  which an f=8 autoencoder keeps.  Coefficients are whitened by frequency and
  normalised per block, and the change is shaped by a texture mask so that it
  is spent where the image hides it.
* The instance key stays in a **fragile tier**: the 8x8 block DCT at full
  resolution, as in v4.  Regeneration removes it, which is what gives the
  proposal's state "only the semantic key is found" its meaning.
* Both keys are built **segment by segment** from the bits of the codes, so a
  code that moved by a few bits still matches most of the key.  This replaces
  the Reed-Muller helper data of v4.

The module reuses the primitives of ``revised_watermark_v4`` (revision 2),
which stays untouched; v5 derives its own ``detector_config_id`` and reads no
v4 mark.

Revision 2 (same day as revision 1, before any photograph was marked)
strengthens the robust tier where the synthetic development channel showed it
weak: the detector weights every slot by the share of the mark the embedder
puts there (recomputed from the suspect image, independent of the key); the
whitening exponent is 2; visibility is limited block by block, a flat strip
inside a busy block is protected pixel by pixel, and the PSNR floor is the
only global limit; the thresholds follow the tight Gaussian bound for weighted
random signs of Bentkus and Dzindzalieta instead of Hoeffding's.  Revision 1 is
the snapshot committed as f9087a2 on ``claude/v5-two-tier-study``; the two
revisions derive different ``detector_config_id`` values.

Revision 3 changes the embedder only; the detector, its configuration and its
``detector_config_id`` are those of revision 2, so either revision's marks are
read the same way.  The host rejection is designed for a channel that returns
a fifth of what is added (img2img at low strength) instead of a half, which
spends more of the budget on the key pattern; the fill raises quiet blocks,
where regeneration changes the least, before busy ones; and a colour image
receives its luminance change at constant chromaticity, like a change of
illumination, with the PSNR floor measured on the RGB error it causes.

Claim boundary: an image-domain codec and candidate comparator.  It does not
implement latent or initial-noise embedding, no detector state establishes
legal ownership, and survival of regeneration is a measured property of a
stated attack and dose, never a guarantee.  See
``research/method-amendment-v5.md``.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
import time
from pathlib import Path
from typing import Mapping, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import revised_watermark_v4 as base  # noqa: E402
from scripts.revised_watermark_v4 import (  # noqa: E402,F401  (re-exported helpers)
    EmbeddingError,
    canonical_owner,
    canonical_secret_key,
    key_fingerprint,
    luminance_from_rgb,
    mse,
    psnr,
)

if base.REVISION != 2 or base.CHANNEL_BITS != 320:
    raise ImportError("revised_watermark_v5 needs revised_watermark_v4 revision 2")

MAGIC = b"rw-v5"
VERSION = 5
REVISION = 3
# Revision of the detector (and of ``detector_config_id``); revision 3 changed the embedder only.
DETECTOR_REVISION = 2
BLOCK = 8
CANONICAL_SIDE = 128
MIN_SIDE = 256
CODE_BITS = 32
SEGMENT_CHIPS = 10
CHANNEL_CHIPS = CODE_BITS * SEGMENT_CHIPS
ROBUST_FREQUENCIES = tuple((u, v) for u in range(5) for v in range(5) if (u, v) != (0, 0))
INSTANCE_FREQUENCIES = base.INSTANCE_FREQUENCIES
PROXY_SOURCE = base.PROXY_SOURCE
BINDING_MODES = base.BINDING_MODES
PUBLIC_KEY = hashlib.sha256(MAGIC + b"/public-derived-profile-key").digest()
MAX_ROSTER = base.MAX_ROSTER
ZERO_PROJECTION = base.ZERO_PROJECTION
# A change supplied by an external embedder may exceed the planned budget by this much (rounding of its own arithmetic).
EXTERNAL_TOLERANCE = 1.02

_CONSTANTS = {
    "schema_version": "revised-watermark-v5",
    "profile": "two-tier-dual-key-dct",
    "code_bits": CODE_BITS,
    "segment_chips": SEGMENT_CHIPS,
    "canonical_side": CANONICAL_SIDE,
}
_ROBUST_FIELDS = frozenset(("floor", "whitening", "weight_exponent", "mask_base", "mask_weber", "mask_cap"))
_EMBEDDING_FIELDS = frozenset(
    (
        "visibility",
        "block_ratio_cap",
        "min_robust_psnr_db",
        "shape_window",
        "shape_percentile",
        "design_gain",
        "design_noise",
        "fill_order",
        "colour",
        "colour_offset",
        "instance_psnr_db",
        "instance_noise_std",
        "passes",
    )
)
COLOUR_MODES = ("equal", "proportional")
_DECISION_FIELDS = base._DECISION_FIELDS
_PROFILE_FIELDS = frozenset(_CONSTANTS) | {
    "security",
    "semantic_source",
    "minimum_side",
    "robust_frequencies",
    "instance_frequencies",
    "robust",
    "embedding",
    "decision",
}
_DETECTOR_FIELDS = (
    "schema_version",
    "profile",
    "security",
    "semantic_source",
    "minimum_side",
    "robust_frequencies",
    "instance_frequencies",
    "robust",
    "code_bits",
    "segment_chips",
    "canonical_side",
)


def _default_profile(security: str) -> dict[str, object]:
    """A fresh profile each time, so the module defaults share no nested object."""
    return {
        "schema_version": _CONSTANTS["schema_version"],
        "profile": _CONSTANTS["profile"],
        "security": security,
        "semantic_source": PROXY_SOURCE,
        "minimum_side": MIN_SIDE,
        "robust_frequencies": [list(pair) for pair in ROBUST_FREQUENCIES],
        "instance_frequencies": [list(pair) for pair in INSTANCE_FREQUENCIES],
        "code_bits": CODE_BITS,
        "segment_chips": SEGMENT_CHIPS,
        "canonical_side": CANONICAL_SIDE,
        "robust": {"floor": 12.0, "whitening": 2.0, "weight_exponent": 0.5, "mask_base": 0.4, "mask_weber": 0.35, "mask_cap": 5.0},
        "embedding": {
            "visibility": 1.0,
            "block_ratio_cap": 2.0,
            "min_robust_psnr_db": 35.5,
            "shape_window": 3,
            "shape_percentile": 75.0,
            "design_gain": 0.2,
            "design_noise": 0.3,
            "fill_order": 2.0,
            "colour": "proportional",
            "colour_offset": 10.0,
            "instance_psnr_db": 47.0,
            "instance_noise_std": 8.0,
            "passes": 3,
        },
        "decision": {
            "false_positive_target": 1e-6,
            "semantic_radius": 6,
            "semantic_mismatch_distance": 10,
            "instance_radius": 6,
            "instance_mismatch_distance": 10,
        },
    }


DEFAULT_PROFILE = _default_profile("public-derived")
KEYED_PROFILE = _default_profile("hmac-keyed")


# ---------------------------------------------------------------------------
# Profile and keyed derivation
# ---------------------------------------------------------------------------


def _frequency_set(value: object, name: str, reserved: Sequence[tuple[int, int]]) -> tuple[tuple[int, int], ...]:
    if not isinstance(value, (list, tuple)) or not 1 <= len(value) <= 48:
        raise ValueError(f"{name} must list 1..48 coefficient positions")
    pairs = []
    for pair in value:
        if not isinstance(pair, (list, tuple)) or len(pair) != 2 or any(isinstance(i, bool) or not isinstance(i, int) for i in pair):
            raise ValueError(f"{name} entries must be [u, v] integer pairs")
        u, v = pair
        if not (0 <= u < BLOCK and 0 <= v < BLOCK) or (u, v) == (0, 0):
            raise ValueError(f"{name} must use non-DC positions inside the 8x8 block")
        if (u, v) in reserved:
            raise ValueError(f"{name} must leave (0,1) and (1,0) untouched: the perceptual hash reads them")
        pairs.append((u, v))
    if len(set(pairs)) != len(pairs):
        raise ValueError(f"{name} repeats a coefficient position")
    return tuple(pairs)


def validate_profile(profile: Mapping[str, object]) -> dict[str, object]:
    """Return a checked copy of ``profile``; reject unknown, missing or out-of-range fields."""
    if not isinstance(profile, Mapping) or set(profile) != _PROFILE_FIELDS:
        raise ValueError("profile must contain exactly the revised-watermark-v5 fields")
    for key, expected in _CONSTANTS.items():
        if type(profile[key]) is not type(expected) or profile[key] != expected:
            raise ValueError(f"profile constant mismatch: {key}")
    if profile["security"] not in ("hmac-keyed", "public-derived"):
        raise ValueError("security must be hmac-keyed or public-derived")
    source = profile["semantic_source"]
    if not isinstance(source, str) or not (source == PROXY_SOURCE or base.EXTERNAL_SOURCE.fullmatch(source)):
        raise ValueError("semantic_source must be proxy-layout-v1 or external:<feature id of 1..128 characters from A-Za-z0-9._@/+:->")
    side = profile["minimum_side"]
    if isinstance(side, bool) or not isinstance(side, int) or not MIN_SIDE <= side <= 16384:
        raise ValueError(f"minimum_side must be an integer of at least {MIN_SIDE}")
    robust_set = _frequency_set(profile["robust_frequencies"], "robust_frequencies", ())
    instance_set = _frequency_set(profile["instance_frequencies"], "instance_frequencies", base.HASH_DETAIL_POSITIONS)
    if (CANONICAL_SIDE // BLOCK) ** 2 * len(robust_set) < CHANNEL_CHIPS * 4:
        raise ValueError("the robust channel has too few coefficient positions")
    if (side // BLOCK) ** 2 * len(instance_set) < CHANNEL_CHIPS * 4:
        raise ValueError("the instance channel has too few coefficient positions for an image of minimum_side")
    robust = profile["robust"]
    if not isinstance(robust, Mapping) or set(robust) != _ROBUST_FIELDS:
        raise ValueError("robust must contain exactly the revised-watermark-v5 fields")
    base._number(robust["floor"], 0.0, 256.0, "robust floor", low_open=True)
    base._number(robust["whitening"], 0.0, 3.0, "robust whitening")
    base._number(robust["weight_exponent"], 0.0, 2.0, "robust weight_exponent")
    base._number(robust["mask_base"], 0.0, 16.0, "mask_base", low_open=True)
    base._number(robust["mask_weber"], 0.0, 2.0, "mask_weber")
    base._number(robust["mask_cap"], float(robust["mask_base"]), 64.0, "mask_cap")
    embedding = profile["embedding"]
    if not isinstance(embedding, Mapping) or set(embedding) != _EMBEDDING_FIELDS:
        raise ValueError("embedding must contain exactly the revised-watermark-v5 fields")
    base._number(embedding["visibility"], 0.0, 8.0, "visibility", low_open=True)
    base._number(embedding["block_ratio_cap"], 0.0, 16.0, "block_ratio_cap", low_open=True)
    base._number(embedding["min_robust_psnr_db"], 25.0, 60.0, "min_robust_psnr_db")
    window = embedding["shape_window"]
    if isinstance(window, bool) or not isinstance(window, int) or not 1 <= window <= 15:
        raise ValueError("shape_window must be an integer in 1..15")
    base._number(embedding["shape_percentile"], 0.0, 100.0, "shape_percentile", low_open=True)
    base._number(embedding["design_gain"], 0.0, 1.0, "design_gain", low_open=True)
    base._number(embedding["design_noise"], 0.0, 16.0, "design_noise", low_open=True)
    base._number(embedding["fill_order"], 0.0, 8.0, "fill_order")
    if embedding["colour"] not in COLOUR_MODES:
        raise ValueError("embedding colour must be equal or proportional")
    base._number(embedding["colour_offset"], 0.0, 255.0, "colour_offset")
    base._number(embedding["instance_psnr_db"], 30.0, 60.0, "instance_psnr_db")
    base._number(embedding["instance_noise_std"], 0.0, 64.0, "instance_noise_std", low_open=True)
    if isinstance(embedding["passes"], bool) or not isinstance(embedding["passes"], int) or not 1 <= embedding["passes"] <= 8:
        raise ValueError("embedding passes must be an integer in 1..8")
    decision = profile["decision"]
    if not isinstance(decision, Mapping) or set(decision) != _DECISION_FIELDS:
        raise ValueError("decision must contain exactly the revised-watermark-v5 fields")
    base._number(decision["false_positive_target"], base.MIN_FALSE_POSITIVE_TARGET, 1e-2, "false_positive_target")
    for name in ("semantic", "instance"):
        radius, far = decision[name + "_radius"], decision[name + "_mismatch_distance"]
        if any(isinstance(value, bool) or not isinstance(value, int) for value in (radius, far)) or not 0 <= radius < far <= CODE_BITS // 2:
            raise ValueError(f"{name} distances must be integers with 0 <= radius < mismatch_distance <= {CODE_BITS // 2}")
    checked = dict(profile)
    checked["robust_frequencies"] = [list(pair) for pair in robust_set]
    checked["instance_frequencies"] = [list(pair) for pair in instance_set]
    checked["robust"] = {key: float(robust[key]) for key in sorted(robust)}
    checked["embedding"] = dict(embedding)
    checked["decision"] = dict(decision)
    return checked


def load_profile(path: str | Path) -> dict[str, object]:
    """Read and validate a profile; repeated keys and NaN/Infinity literals are errors."""
    text = Path(path).read_text(encoding="utf-8")
    return validate_profile(json.loads(text, object_pairs_hook=base._unique_keys, parse_constant=base._no_constant))


def detector_config_id(profile: Mapping[str, object]) -> str:
    """SHA-256 of the canonical JSON of every field the detector depends on."""
    checked = validate_profile(profile)
    static = {key: checked[key] for key in _DETECTOR_FIELDS}
    return hashlib.sha256(MAGIC + b"/config/r%d/" % DETECTOR_REVISION + base._canonical_json(static)).hexdigest()


def decision_id(profile: Mapping[str, object]) -> str:
    """SHA-256 of the decision thresholds, so a calibration version can be cited."""
    return hashlib.sha256(MAGIC + b"/decision/" + base._canonical_json(validate_profile(profile)["decision"])).hexdigest()


def _resolve(profile: Mapping[str, object] | None, secret_key: bytes | str | None) -> tuple[dict[str, object], bytes, bytes]:
    checked = validate_profile(DEFAULT_PROFILE if profile is None else profile)
    if checked["security"] == "hmac-keyed":
        if secret_key is None:
            raise ValueError("the hmac-keyed profile requires a secret key")
        key = canonical_secret_key(secret_key)
    else:
        if secret_key is not None:
            raise ValueError("the public-derived profile takes no secret key")
        key = PUBLIC_KEY
    return checked, key, bytes.fromhex(detector_config_id(checked))


# ---------------------------------------------------------------------------
# Phase 1: codes and segment-wise keys
# ---------------------------------------------------------------------------


def _semantic(means, checked, key: bytes, config: bytes, supplied, binding: bool) -> int:
    """Semantic code q of an image; ``binding`` is true when a mark is about to be bound to it."""
    if checked["semantic_source"] == PROXY_SOURCE:
        if supplied is not None:
            raise ValueError("the proxy-layout-v1 profile computes its own features")
        features = base._layout_features(means)
        if max(abs(value) for value in features) < 1e-9:
            if binding:
                raise ValueError("image has no coarse layout to bind: every region has the same mean")
            return 0
        return base._semantic_code(features, key, config)
    if supplied is None:
        raise ValueError("an external semantic_source requires the caller's semantic_features")
    return base._semantic_code(supplied, key, config)


def _signs(material: bytes) -> tuple[float, ...]:
    """SEGMENT_CHIPS signs from the leading bits of ``material``; bit 1 means -1."""
    return tuple(-1.0 if (material[index >> 3] >> (7 - (index & 7))) & 1 else 1.0 for index in range(SEGMENT_CHIPS))


def _semantic_table(owner: bytes, key: bytes, config: bytes) -> list[tuple[tuple[float, ...], tuple[float, ...]]]:
    """``table[j][b]``: the chips of segment ``j`` of ``Ws`` when bit ``j`` of ``q`` is ``b``."""
    width = (SEGMENT_CHIPS + 7) // 8
    return [
        tuple(_signs(base._stream(key, config, base._pack(b"ws", owner, bytes((segment, bit))), width)) for bit in (0, 1))
        for segment in range(CODE_BITS)
    ]


def _instance_table(owner: bytes, key: bytes, config: bytes) -> list[tuple[tuple[tuple[float, ...], ...], ...]]:
    """``table[j][bq][bh]``: the chips of segment ``j`` of ``Wi`` for bit ``j`` of ``q`` and of ``H``."""
    width = (SEGMENT_CHIPS + 7) // 8
    return [
        tuple(
            tuple(_signs(base._stream(key, config, base._pack(b"wi", owner, bytes((segment, q_bit, h_bit))), width)) for h_bit in (0, 1))
            for q_bit in (0, 1)
        )
        for segment in range(CODE_BITS)
    ]


def _bit(code: int, segment: int) -> int:
    """Bit of ``code`` carried by ``segment``; segment 0 is the most significant bit."""
    return (code >> (CODE_BITS - 1 - segment)) & 1


def derive_keys(q: int, h: int, owner: bytes, key: bytes, config: bytes) -> tuple[list[float], list[float]]:
    """The proposal's dual keys as chip patterns of +1/-1.

    ``Ws`` binds owner and semantics, ``Wi`` additionally binds the perceptual
    instance.  Each key is the concatenation of 32 segments; segment ``j`` is a
    pseudorandom function of the owner, ``j`` and bit ``j`` of the code(s).
    Two codes at Hamming distance ``d`` therefore share ``32 - d`` segments of
    the key exactly, and their other segments are independent.
    """
    semantic, instance = _semantic_table(owner, key, config), _instance_table(owner, key, config)
    ws = [chip for segment in range(CODE_BITS) for chip in semantic[segment][_bit(q, segment)]]
    wi = [chip for segment in range(CODE_BITS) for chip in instance[segment][_bit(q, segment)][_bit(h, segment)]]
    return ws, wi


# ---------------------------------------------------------------------------
# Robust tier: block DCT of the canonical coarse image
# ---------------------------------------------------------------------------


def _coarse(image: Sequence[Sequence[float]]) -> list[list[float]]:
    """The image area-averaged to the canonical grid."""
    return base._resample(image, CANONICAL_SIDE)


def _whitening(positions: Sequence[tuple[int, int]], exponent: float) -> list[float]:
    """Natural-image amplitude falls roughly as 1/f; the weight makes the band about flat."""
    return [math.hypot(u, v) ** exponent for u, v in positions]


def _cell_deviation(image: Sequence[Sequence[float]]) -> list[list[float]]:
    """Standard deviation of the pixels of every complete 8x8 block of the image."""
    out = []
    for by in range(len(image) // BLOCK):
        rows = image[by * BLOCK : by * BLOCK + BLOCK]
        line = []
        for bx in range(len(image[0]) // BLOCK):
            values = [float(value) for row in rows for value in row[bx * BLOCK : bx * BLOCK + BLOCK]]
            mean = sum(values) / 64.0
            line.append(math.sqrt(sum((value - mean) ** 2 for value in values) / 64.0))
        out.append(line)
    return out


def _activity(coarse: Sequence[Sequence[float]], image: Sequence[Sequence[float]]) -> list[float]:
    """Per coarse block: how much texture it has everywhere, at two scales.

    Coarse scale: the least, over the block's four quadrants, of the RMS that
    remains after the quadrant's best-fitting plane is removed.  A smooth
    gradient therefore counts as flat, and a block with one edge next to a flat
    area keeps the value of the flat part.  Fine scale: the second smallest
    standard deviation among the 8x8 pixel cells under the block, so that a
    block with a flat patch of more than one cell counts as flat however busy
    the rest of it is.  The smaller of the two is the block's texture.
    """
    blocks = CANONICAL_SIDE // BLOCK
    half = BLOCK // 2
    offsets = [index - (half - 1) / 2.0 for index in range(half)]
    spread = half * sum(offset * offset for offset in offsets)
    cells = _cell_deviation(image)
    height, width = len(image), len(image[0])

    def span(index: int, pixels: int, count: int) -> range:
        first = int(index * pixels / blocks) // BLOCK
        last = -(-int(math.ceil((index + 1) * pixels / blocks)) // BLOCK)
        return range(min(first, count - 1), max(min(last, count), min(first, count - 1) + 1))

    out = []
    for by in range(blocks):
        for bx in range(blocks):
            fine = sorted(cells[y][x] for y in span(by, height, len(cells)) for x in span(bx, width, len(cells[0])))
            lowest = fine[min(1, len(fine) - 1)]
            for qy in (0, half):
                for qx in (0, half):
                    rows = [coarse[by * BLOCK + qy + y][bx * BLOCK + qx : bx * BLOCK + qx + half] for y in range(half)]
                    mean = sum(map(sum, rows)) / (half * half)
                    slope_y = sum(offsets[y] * sum(rows[y]) for y in range(half)) / spread
                    slope_x = sum(offsets[x] * rows[y][x] for y in range(half) for x in range(half)) / spread
                    residual = sum(
                        (rows[y][x] - mean - slope_y * offsets[y] - slope_x * offsets[x]) ** 2 for y in range(half) for x in range(half)
                    )
                    lowest = min(lowest, math.sqrt(residual / (half * half)))
            out.append(lowest)
    return out


class _Robust:
    """Analysis of the robust tier of one image: coefficients, normalisers, mask, slot weights and chip projections.

    Revision 2 weights every slot by how much of the mark the embedder puts
    there, recomputed from the image itself: ``(mask * whitening * gain /
    normaliser) ** (2 * weight_exponent)``.  With exponent 0 every slot counts
    once, as in revision 1.  The weights never depend on the key, so for an
    unmarked image the statistic is still a weighted sum of independent random
    signs and the false-positive bound holds unchanged.
    """

    def __init__(self, coarse, image, checked, carrier):
        robust = checked["robust"]
        self.positions = tuple(tuple(pair) for pair in checked["robust_frequencies"])
        self.weights = _whitening(self.positions, float(robust["whitening"]))
        floor = float(robust["floor"])
        self.coefficients = base._analyse(coarse, [base._plane(u, v) for u, v in self.positions])[1]
        count = len(self.positions)
        self.normalisers = [
            math.sqrt(floor * floor + sum((value * weight) ** 2 for value, weight in zip(block, self.weights)) / count) for block in self.coefficients
        ]
        self.values = [value * weight / norm for block, norm in zip(self.coefficients, self.normalisers) for value, weight in zip(block, self.weights)]
        order = max(max(u, v) for u, v in self.positions) + 1
        gain_y, gain_x = _averaging_gain(len(image), order), _averaging_gain(len(image[0]), order)
        self.gains = [gain_y[u] * gain_x[v] for u, v in self.positions]
        base_level, weber, cap = float(robust["mask_base"]), float(robust["mask_weber"]), float(robust["mask_cap"])
        self.mask = [min(cap, math.hypot(base_level, weber * value)) for value in _activity(coarse, image)]
        exponent = float(robust["weight_exponent"])
        self.slot_weights = [
            (level * weight * gain / norm) ** (2.0 * exponent)
            for level, norm in zip(self.mask, self.normalisers)
            for weight, gain in zip(self.weights, self.gains)
        ]
        bit_of_slot, signs, _norms = carrier
        totals, squares = [0.0] * CHANNEL_CHIPS, [0.0] * CHANNEL_CHIPS
        for value, chip, sign, factor in zip(self.values, bit_of_slot, signs, self.slot_weights):
            totals[chip] += factor * sign * value
            squares[chip] += factor * factor
        self.carrier = (bit_of_slot, signs)
        self.norms = [math.sqrt(square) for square in squares]
        self.projections = [total / norm for total, norm in zip(totals, self.norms)]


def _robust_carrier(key: bytes, config: bytes, owner: bytes, positions: int):
    """The robust carrier depends on key, owner and configuration, not on the image size."""
    slots = (CANONICAL_SIDE // BLOCK) ** 2 * positions
    return base._carrier(key, config, owner, b"r", CANONICAL_SIDE, CANONICAL_SIDE, slots)


def _averaging_gain(source: int, order: int) -> list[float]:
    """Factor by which area-averaging to the canonical grid shrinks each continuous DCT basis function.

    Measured on the first coarse block of an axis with ``source`` pixels.  For
    an integer scale it is the same in every block; otherwise it varies a
    little from block to block and this value is the approximation used.
    """
    scale = CANONICAL_SIDE / source
    weights = base._area_weights(source, CANONICAL_SIDE)[:BLOCK]
    gains = []
    for u in range(order):
        numerator = denominator = 0.0
        for index, cell in enumerate(weights):
            reference = math.cos((2 * index + 1) * u * math.pi / (2 * BLOCK))
            averaged = sum(weight * math.cos((position + 0.5) * scale * u * math.pi / BLOCK) for position, weight in cell)
            numerator += reference * averaged
            denominator += reference * reference
        gains.append(numerator / denominator)
    return gains


def _axis_basis(source: int, order: int) -> list[tuple[int, list[float]]]:
    """Per pixel of an axis: its coarse block and the continuous 8-point DCT basis values there."""
    scale = CANONICAL_SIDE / source
    blocks = CANONICAL_SIDE // BLOCK
    out = []
    for position in range(source):
        coordinate = (position + 0.5) * scale
        block = min(blocks - 1, int(coordinate // BLOCK))
        local = coordinate - block * BLOCK
        out.append(
            (block, [(math.sqrt(1.0 / BLOCK) if u == 0 else math.sqrt(2.0 / BLOCK)) * math.cos(local * u * math.pi / BLOCK) for u in range(order)])
        )
    return out


def _render(height: int, width: int, positions, amplitudes: Sequence[Sequence[float]]) -> list[list[float]]:
    """Full-resolution luminance change whose coarse block DCT moves by the planned amounts.

    ``amplitudes[b][k]`` multiplies the smooth basis function of position ``k``
    in coarse block ``b``; the change is continuous inside a block.
    """
    order = max(max(u, v) for u, v in positions) + 1
    rows, columns = _axis_basis(height, order), _axis_basis(width, order)
    blocks = CANONICAL_SIDE // BLOCK
    column_groups: list[list[int]] = [[] for _ in range(blocks)]
    for x, (block, _values) in enumerate(columns):
        column_groups[block].append(x)
    out = [[0.0] * width for _ in range(height)]
    cache: dict[int, list[list[float]]] = {}
    current = -1
    for y, (row_block, row_values) in enumerate(rows):
        if row_block != current:
            current = row_block
            cache = {}
            for bx in range(blocks):
                partial = [[0.0] * len(column_groups[bx]) for _ in range(order)]
                for (u, v), amount in zip(positions, amplitudes[row_block * blocks + bx]):
                    if amount:
                        line = partial[u]
                        for offset, x in enumerate(column_groups[bx]):
                            line[offset] += amount * columns[x][1][v]
                cache[bx] = partial
        target = out[y]
        for bx in range(blocks):
            partial = cache[bx]
            for offset, x in enumerate(column_groups[bx]):
                target[x] = sum(row_values[u] * partial[u][offset] for u in range(order))
    return out


def _plan_robust(robust: _Robust, pattern: Sequence[float], checked) -> dict[str, object]:
    """Closed-form masked improved spread spectrum on the robust tier: the shape of the change.

    The weighted chip projections of the normalised coefficients are moved
    towards ``A * pattern`` after removing the share ``lambda`` of their host
    value.  Two budgets shape the plan: a visibility budget (the RMS over blocks
    of each block's RMS grey-level change divided by its mask) and an error
    budget (the PSNR floor).  Every chip's move is spread over its slots at the
    least cost in a weighted sum of the two, in proportion to each slot's
    detector weight.  Eleven weights are tried, starting with visibility alone;
    a weight replaces the best so far only if its plan, scaled until the
    tighter budget is met, promises at least 1% more.  The plan fixes the shape
    and the host rejection; :func:`_fill` then sets the scale of every block.
    """
    embedding = checked["embedding"]
    count = len(robust.positions)
    bit_of_slot, signs = robust.carrier
    weights_of_slot = robust.slot_weights
    norms = robust.norms
    blocks = len(robust.normalisers)
    visibility = float(embedding["visibility"])
    floor_mse = 255.0**2 / 10.0 ** (float(embedding["min_robust_psnr_db"]) / 10.0)
    # Cost of a unit move of a normalised coefficient in each budget, each scaled so that the budget is 1.
    seen, spent = [], []
    for block, norm in enumerate(robust.normalisers):
        for weight, gain in zip(robust.weights, robust.gains):
            energy = (norm / (weight * gain)) ** 2 / (BLOCK * BLOCK)  # mean squared grey-level change of the block
            seen.append(energy / (robust.mask[block] ** 2 * visibility * visibility * blocks))
            spent.append(energy / (floor_mse * blocks))
    host = robust.projections
    power = sum(p * p for p in host) / CHANNEL_CHIPS
    design_gain, design_noise = float(embedding["design_gain"]), float(embedding["design_noise"])

    def capacities(unit):
        capacity = [0.0] * CHANNEL_CHIPS
        seen_sum = [0.0] * CHANNEL_CHIPS
        spent_sum = [0.0] * CHANNEL_CHIPS
        for slot, chip in enumerate(bit_of_slot):
            share_of_move = weights_of_slot[slot] / unit[slot]
            capacity[chip] += weights_of_slot[slot] * share_of_move
            seen_sum[chip] += seen[slot] * share_of_move * share_of_move
            spent_sum[chip] += spent[slot] * share_of_move * share_of_move
        return capacity, seen_sum, spent_sum

    best = None
    for step in range(10, -1, -1):
        share = step / 10.0
        found = None
        unit = [share * a + (1.0 - share) * b for a, b in zip(seen, spent)]
        capacity, seen_sum, spent_sum = capacities(unit)
        cost = [norm * norm / value for norm, value in zip(norms, capacity)]  # per unit squared move of a chip projection
        total = sum(cost)
        cross = sum(c * e * p for c, e, p in zip(cost, pattern, host))
        square = sum(c * p * p for c, p in zip(cost, host))
        for rejection_step in range(41):
            rejection = rejection_step / 40.0
            discriminant = (rejection * cross) ** 2 - total * (rejection * rejection * square - 1.0)
            if discriminant <= 0.0:
                continue
            amplitude = (rejection * cross + math.sqrt(discriminant)) / total
            if amplitude <= 0.0:
                continue
            moves = [amplitude * e - rejection * p for e, p in zip(pattern, host)]
            factors = [move * move * norm * norm / (value * value) for move, norm, value in zip(moves, norms, capacity)]
            used = max(sum(f * s for f, s in zip(factors, seen_sum)), sum(f * s for f, s in zip(factors, spent_sum)))
            scale = 1.0 / math.sqrt(used)
            promise = design_gain * amplitude * scale / math.sqrt((1.0 - design_gain * rejection * scale) ** 2 * power + design_noise * design_noise)
            if found is None or promise > found[0]:
                found = (promise, share, rejection, amplitude, scale)
        # Visibility alone decides unless bringing in the error budget promises clearly more.
        if found is not None and (best is None or found[0] > best[0] * 1.01):
            best = found
    if best is None:
        raise ValueError("the robust tier has no admissible plan for this image")
    _promise, share, rejection, amplitude, scale = best
    unit = [share * a + (1.0 - share) * b for a, b in zip(seen, spent)]
    capacity = capacities(unit)[0]
    moves = [scale * (amplitude * e - rejection * p) for e, p in zip(pattern, host)]
    change = [[0.0] * count for _ in range(blocks)]
    for slot, (chip, sign) in enumerate(zip(bit_of_slot, signs)):
        block, index = divmod(slot, count)
        delta = moves[chip] * norms[chip] * weights_of_slot[slot] * sign / (unit[slot] * capacity[chip])
        change[block][index] = delta * robust.normalisers[block] / robust.weights[index]
    return {
        "change": change,
        "host_rejection": rejection * scale,
        "amplitude": amplitude * scale,
        "host_rms": math.sqrt(power),
        "visibility_share": share,
    }


def _block_of_pixel(source: int) -> list[int]:
    """Coarse block index of every pixel of an axis, as :func:`_render` assigns it."""
    return [block for block, _values in _axis_basis(source, 1)]


def _local_flatness(image: Sequence[Sequence[float]], window: int) -> list[list[float]]:
    """Per pixel: the standard deviation of the flattest ``window`` x ``window`` window that contains it.

    A flat strip at least ``window`` pixels wide therefore reads as flat right
    up to its edge, however busy the pixels beside it are.
    """
    height, width = len(image), len(image[0])
    window = max(1, min(window, height, width))
    # Integral images of the values and their squares.
    total = [[0.0] * (width + 1) for _ in range(height + 1)]
    square = [[0.0] * (width + 1) for _ in range(height + 1)]
    for y in range(height):
        row, above_t, above_s, here_t, here_s = image[y], total[y], square[y], total[y + 1], square[y + 1]
        running_t = running_s = 0.0
        for x in range(width):
            value = float(row[x])
            running_t += value
            running_s += value * value
            here_t[x + 1] = above_t[x + 1] + running_t
            here_s[x + 1] = above_s[x + 1] + running_s
    area = float(window * window)
    rows, columns = height - window + 1, width - window + 1
    deviation = []
    for y in range(rows):
        t0, t1, s0, s1 = total[y], total[y + window], square[y], square[y + window]
        line = []
        for x in range(columns):
            sum_t = t1[x + window] - t1[x] - t0[x + window] + t0[x]
            sum_s = s1[x + window] - s1[x] - s0[x + window] + s0[x]
            mean = sum_t / area
            line.append(math.sqrt(max(0.0, sum_s / area - mean * mean)))
        deviation.append(line)
    # Minimum over the windows that contain each pixel: a separable running minimum.
    across = [[min(line[max(0, x - window + 1) : min(columns, x + 1)]) for x in range(width)] for line in deviation]
    return [[min(across[k][x] for k in range(max(0, y - window + 1), min(rows, y + 1))) for x in range(width)] for y in range(height)]


def _percentile(values: Sequence[float], percent: float) -> float:
    """Linear-interpolation percentile of a non-empty sequence (numpy's default rule)."""
    ordered = sorted(values)
    position = (len(ordered) - 1) * percent / 100.0
    low = int(math.floor(position))
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)


def _shape_factors(image: Sequence[Sequence[float]], checked) -> list[list[float]]:
    """Per pixel: the share of the planned change it takes, from the flatness of its own neighbourhood.

    Each pixel gets the just-noticeable level of the mask formula from
    :func:`_local_flatness`.  A pixel flatter than the ``shape_percentile``-th
    pixel of its coarse block takes a proportionally smaller share; pixels as
    busy as most of their block take all of it.  This keeps a flat strip
    inside a busy block, which the block mask cannot see, free of the change.
    """
    robust, embedding = checked["robust"], checked["embedding"]
    base_level, weber = float(robust["mask_base"]), float(robust["mask_weber"])
    levels = [[math.hypot(base_level, weber * value) for value in row] for row in _local_flatness(image, int(embedding["shape_window"]))]
    rows, columns = _block_of_pixel(len(image)), _block_of_pixel(len(image[0]))
    blocks = CANONICAL_SIDE // BLOCK
    members: list[list[float]] = [[] for _ in range(blocks * blocks)]
    for y, row in enumerate(levels):
        offset = rows[y] * blocks
        for x, level in enumerate(row):
            members[offset + columns[x]].append(level)
    percent = float(embedding["shape_percentile"])
    reference = [_percentile(values, percent) for values in members]
    return [[min(1.0, level / reference[rows[y] * blocks + columns[x]]) for x, level in enumerate(row)] for y, row in enumerate(levels)]


def _block_energies(delta: Sequence[Sequence[float]], weights: Sequence[Sequence[float]] | None = None) -> tuple[list[float], list[int]]:
    """Sum of squared pixel changes (times ``weights`` when given) and pixel count of every coarse block."""
    rows, columns = _block_of_pixel(len(delta)), _block_of_pixel(len(delta[0]))
    blocks = CANONICAL_SIDE // BLOCK
    sums, counts = [0.0] * (blocks * blocks), [0] * (blocks * blocks)
    for y, row in enumerate(delta):
        offset = rows[y] * blocks
        factors = weights[y] if weights is not None else None
        for x, value in enumerate(row):
            sums[offset + columns[x]] += value * value * (factors[x] if factors is not None else 1.0)
            counts[offset + columns[x]] += 1
    return sums, counts


def _budget(delta, mask, embedding, weights=None) -> dict[str, float]:
    """Block ratios (RMS change of a block over its mask) and PSNR of a full-resolution robust change.

    The ratios are in luminance.  ``weights`` (see :func:`colour_weights`) puts
    the error in the domain of the image that receives the change, RGB for a
    colour image; without it the error is that of the luminance.
    """
    sums, counts = _block_energies(delta)
    ratios = [math.sqrt(total / count) / level if count else 0.0 for total, count, level in zip(sums, counts, mask)]
    error = sum(sums if weights is None else _block_energies(delta, weights)[0]) / float(len(delta) * len(delta[0]))
    return {
        "ratio_rms": math.sqrt(sum(ratio * ratio for ratio in ratios) / len(ratios)),
        "ratio_max": max(ratios),
        "planned_mse": error,
        "planned_psnr_db": float("inf") if error <= 0.0 else 10.0 * math.log10(255.0**2 / error),
    }


def _fill(unit, mask, embedding, weights=None) -> tuple[list[float], dict[str, object]]:
    """Scale factor of every coarse block: quiet blocks first, each block clipped at its own cap, up to the PSNR floor.

    ``unit`` is the shaped full-resolution change of the plan.  Visibility acts
    block by block, as a just-noticeable-difference limit (``block_ratio_cap``
    times the block's mask, RMS over the block); the PSNR floor is the only
    global limit.  Block ``b`` is scaled by ``min(s * (1 + mask[b]) ** -fill_order,
    its cap)`` (mask in grey levels) with one ``s`` for the image: regeneration
    changes a quiet block least, so a unit of error buys most score there
    (revision 3; ``fill_order`` 0 is the uniform scale of revision 2).  A plan
    that reaches every cap before the floor stops there.  ``weights`` measures
    the floor on the error of the image that receives the change (see
    :func:`_budget`).
    """
    cap = float(embedding["block_ratio_cap"])
    order = float(embedding["fill_order"])
    floor_mse = 255.0**2 / 10.0 ** (float(embedding["min_robust_psnr_db"]) / 10.0)
    sums, counts = _block_energies(unit)
    costs = sums if weights is None else _block_energies(unit, weights)[0]
    pixels = float(len(unit) * len(unit[0]))
    limits = [cap * level / math.sqrt(total / count) if total > 0.0 else math.inf for total, count, level in zip(sums, counts, mask)]
    priorities = [(1.0 + level) ** -order for level in mask]
    if all(total <= 0.0 for total in sums):
        raise ValueError("the robust change is zero")

    def error(scale: float) -> float:
        return sum(cost * min(scale * priority, limit) ** 2 for cost, limit, priority in zip(costs, limits, priorities)) / pixels

    ceiling = max(limit / priority for limit, priority in zip(limits, priorities) if math.isfinite(limit))
    if error(ceiling) <= floor_mse:
        scale, bound = ceiling, "block caps"
    else:
        low, high = 0.0, ceiling
        for _ in range(100):
            middle = (low + high) / 2.0
            low, high = (middle, high) if error(middle) < floor_mse else (low, middle)
        scale, bound = low, "psnr floor"
    return [min(scale * priority, limit) for limit, priority in zip(limits, priorities)], {"fill_scale": scale, "bound_by": bound}


def _apply(unit, factors) -> list[list[float]]:
    rows, columns = _block_of_pixel(len(unit)), _block_of_pixel(len(unit[0]))
    blocks = CANONICAL_SIDE // BLOCK
    return [[value * factors[rows[y] * blocks + columns[x]] for x, value in enumerate(row)] for y, row in enumerate(unit)]


# ---------------------------------------------------------------------------
# Fragile tier: block DCT at full resolution (the v4 instance channel)
# ---------------------------------------------------------------------------


class _Fragile:
    """Everything of the fragile tier that depends only on image size, owner, key and configuration."""

    def __init__(self, checked, key: bytes, config: bytes, owner: bytes, height: int, width: int):
        self.positions = tuple(tuple(pair) for pair in checked["instance_frequencies"])
        self.planes = [base._plane(u, v) for u, v in self.positions]
        self.analysis = list(base._DETAIL_PLANES) + self.planes
        self.skip = len(base._DETAIL_PLANES)
        slots = (height // BLOCK) * (width // BLOCK) * len(self.positions)
        if slots < CHANNEL_CHIPS * 4:
            raise ValueError("image has too few DCT slots for the instance key")
        self.carrier = base._carrier(key, config, owner, b"i", height, width, slots)

    def projections(self, coefficients) -> list[float]:
        return base._project([value for block in coefficients for value in block[self.skip :]], *self.carrier)


def _embed_fragile(output, fragile: _Fragile, pattern, checked, quantize: bool, reserve_rounding: bool) -> dict[str, object]:
    """Improved spread spectrum on the full-resolution block DCT, in place; as in v4."""
    embedding = checked["embedding"]
    height, width = len(output), len(output[0])
    coefficients = base._analyse(output, fragile.analysis)[1]
    host = fragile.projections(coefficients)
    target_mse = 255.0**2 / 10.0 ** (float(embedding["instance_psnr_db"]) / 10.0)
    if reserve_rounding:
        target_mse = max(target_mse - base.ROUNDING_MSE, 0.25 * target_mse)
    power = sum(value * value for value in host) / CHANNEL_CHIPS
    rejection, amplitude = base._host_rejection(target_mse * height * width / CHANNEL_CHIPS, power, float(embedding["instance_noise_std"]) ** 2)
    targets = [(1.0 - rejection) * value + amplitude * chip for value, chip in zip(host, pattern)]
    bit_of_slot, signs, norms = fragile.carrier
    per_block = len(fragile.positions)
    blocks_per_row = width // BLOCK
    most_clipped = 0
    for pass_index in range(int(embedding["passes"])):
        if pass_index:
            coefficients = base._analyse(output, fragile.analysis)[1]
        current = fragile.projections(coefficients)
        step = [(target - value) / norm for target, value, norm in zip(targets, current, norms)]
        clipped = 0
        for block_index in range(len(coefficients)):
            delta = [0.0] * 64
            for offset, plane in enumerate(fragile.planes):
                slot = block_index * per_block + offset
                change = step[bit_of_slot[slot]] * signs[slot]
                delta = [value + change * basis for value, basis in zip(delta, plane)]
            top, left = (block_index // blocks_per_row) * BLOCK, (block_index % blocks_per_row) * BLOCK
            for y in range(BLOCK):
                row = output[top + y]
                for x in range(BLOCK):
                    value = row[left + x] + delta[y * BLOCK + x]
                    if quantize:
                        value = math.floor(value + 0.5)
                    if value < 0.0 or value > 255.0:
                        clipped += 1
                        value = min(255.0, max(0.0, value))
                    row[left + x] = float(value)
        most_clipped = max(most_clipped, clipped)
    if quantize:
        # The strip outside the last full block carries no instance mark but is part of the saved image.
        for y, row in enumerate(output):
            for x in range(0 if y >= (height // BLOCK) * BLOCK else blocks_per_row * BLOCK, width):
                row[x] = float(min(255.0, max(0.0, math.floor(row[x] + 0.5))))
    return {"host_rejection": rejection, "amplitude": amplitude, "host_rms": math.sqrt(power), "clipped_fraction": most_clipped / float(height * width)}


# ---------------------------------------------------------------------------
# Phase 2: embedding
# ---------------------------------------------------------------------------


def _prepare(image, owner_id, secret_key, profile, semantic_features):
    checked, key, config = _resolve(profile, secret_key)
    height, width = base._check_image(image, int(checked["minimum_side"]))
    owner = canonical_owner(owner_id)
    means = base._analyse(image, ())[0]
    q = _semantic(means, checked, key, config, semantic_features, binding=True)
    coarse = _coarse(image)
    robust = _Robust(coarse, image, checked, _robust_carrier(key, config, owner, len(checked["robust_frequencies"])))
    table = _semantic_table(owner, key, config)
    ws = [chip for segment in range(CODE_BITS) for chip in table[segment][_bit(q, segment)]]
    plan = _plan_robust(robust, ws, checked)
    return checked, key, config, owner, height, width, q, robust, ws, plan


def _shaped(image, robust, change, shape) -> list[list[float]]:
    """Full-resolution luminance change of a coefficient-domain robust change, after the pixel shaping."""
    amplitudes = [[value / gain for value, gain in zip(block, robust.gains)] for block in change]
    rendered = _render(len(image), len(image[0]), robust.positions, amplitudes)
    return [[value * factor for value, factor in zip(row, factors)] for row, factors in zip(rendered, shape)]


def _closed_form(image, robust, plan, checked, weights=None):
    """The plan rendered, shaped and filled.

    Returns the final coefficient-domain change (what :func:`robust_plan`
    hands out), the full-resolution change, the shaping factors and the fill
    report.  Rendering is linear block by block, so scaling a block's
    coefficients scales its pixels by the same factor.
    """
    shape = _shape_factors(image, checked)
    unit = _shaped(image, robust, plan["change"], shape)
    factors, fill = _fill(unit, robust.mask, checked["embedding"], weights)
    change = [[value * factor for value in block] for block, factor in zip(plan["change"], factors)]
    return change, _apply(unit, factors), shape, fill


def robust_plan(
    image: Sequence[Sequence[float]],
    owner_id: str,
    secret_key: bytes | str | None = None,
    profile: Mapping[str, object] | None = None,
    semantic_features: Sequence[float] | None = None,
    error_weights: Sequence[Sequence[float]] | None = None,
) -> dict[str, object]:
    """Embedder-independent contract of the robust tier.

    Returns what an external embedder -- for example one that refines the
    change through a frozen autoencoder -- needs in order to be read by this
    detector: the slot layout and weights, the key pattern, the block masks,
    the pixel shaping, the closed-form change as a starting point and its
    budget.  ``change[b][k]`` is the move of coarse coefficient ``positions[k]``
    of coarse block ``b`` (row-major, 16 blocks per row); the image receives
    its rendering multiplied by ``shape`` pixel by pixel.  A change handed back
    to :func:`embed_with_report` is refused when, so rendered and shaped, a
    block exceeds its cap or the image falls below the PSNR floor.  For a
    colour image pass ``error_weights=colour_weights(rgb, profile)``, as
    :func:`embed_rgb` does, so that the floor is the one it will check.
    """
    checked, _key, config, _owner, height, width, q, robust, ws, plan = _prepare(image, owner_id, secret_key, profile, semantic_features)
    weights = _checked_weights(error_weights, height, width)
    change, delta, shape, fill = _closed_form(image, robust, plan, checked, weights)
    bit_of_slot, signs = robust.carrier
    return {
        "detector_config_id": config.hex(),
        "semantic_code": f"{q:08x}",
        "height": height,
        "width": width,
        "canonical_side": CANONICAL_SIDE,
        "positions": [list(pair) for pair in robust.positions],
        "whitening_weights": list(robust.weights),
        "floor": float(checked["robust"]["floor"]),
        "chip_of_slot": list(bit_of_slot),
        "sign_of_slot": list(signs),
        "slot_weights": list(robust.slot_weights),
        "chip_norms": list(robust.norms),
        "pattern": list(ws),
        "mask": list(robust.mask),
        "averaging_gains": list(robust.gains),
        "shape": shape,
        "change": change,
        "limits": {**_budget(delta, robust.mask, checked["embedding"], weights), **fill},
        "error_domain": "luminance" if weights is None else "weighted",
        "block_ratio_cap": float(checked["embedding"]["block_ratio_cap"]),
        "min_robust_psnr_db": float(checked["embedding"]["min_robust_psnr_db"]),
    }


def _checked_weights(weights, height: int, width: int):
    if weights is None:
        return None
    rows = [[float(value) for value in row] for row in weights]
    if len(rows) != height or any(len(row) != width for row in rows):
        raise ValueError("error_weights must have the image's shape")
    if any(not (math.isfinite(value) and value > 0.0) for row in rows for value in row):
        raise ValueError("error_weights must be finite and positive")
    return rows


def colour_directions(rgb: Sequence[Sequence[Sequence[float]]], profile: Mapping[str, object] | None = None) -> list[list[tuple[float, float, float]]]:
    """Per pixel, the RGB change that moves the luminance by one grey level (revision 3).

    ``equal`` adds the same value to R, G and B, as revisions 1 and 2 did.
    ``proportional`` moves the pixel along its own colour, offset by
    ``colour_offset`` in every channel and scaled to unit luminance: the
    chromaticity stays, as under a change of illumination, where an equal
    change would wash out a saturated colour; the offset keeps a dark pixel
    from putting the whole change into one channel.  A grey pixel gets
    ``(1, 1, 1)`` either way.
    """
    embedding = validate_profile(DEFAULT_PROFILE if profile is None else profile)["embedding"]
    if embedding["colour"] == "equal":
        return [[(1.0, 1.0, 1.0) for _pixel in row] for row in rgb]
    offset = float(embedding["colour_offset"])
    out = []
    for row in rgb:
        out_row = []
        for pixel in row:
            r, g, b = (float(channel) + offset for channel in pixel)
            luma = 0.299 * r + 0.587 * g + 0.114 * b
            if luma <= 0.0:
                out_row.append((1.0, 1.0, 1.0))
            else:
                out_row.append((r / luma, g / luma, b / luma))
        out.append(out_row)
    return out


def colour_weights(rgb: Sequence[Sequence[Sequence[float]]], profile: Mapping[str, object] | None = None) -> list[list[float]]:
    """Per pixel, the mean squared RGB change per squared grey level of luminance change (1 for ``equal``)."""
    return [[(r * r + g * g + b * b) / 3.0 for r, g, b in row] for row in colour_directions(rgb, profile)]


def embed_with_report(
    image: Sequence[Sequence[float]],
    owner_id: str,
    secret_key: bytes | str | None = None,
    profile: Mapping[str, object] | None = None,
    semantic_features: Sequence[float] | None = None,
    quantize: bool = True,
    strict: bool = True,
    reserve_rounding: bool | None = None,
    robust_change: Sequence[Sequence[float]] | None = None,
    error_weights: Sequence[Sequence[float]] | None = None,
) -> tuple[list[list[float]], dict[str, object]]:
    """Embed both keys and verify the result with the real detector.

    Order matters: the semantic key goes into the robust tier first; the
    perceptual hash is then read from that intermediate image, because the
    robust tier moves what the hash reads and the fragile tier does not; the
    instance key bound to that hash goes into the fragile tier last.

    ``robust_change`` replaces the closed-form robust change with one computed
    elsewhere under the same budget (see :func:`robust_plan`); it is used as it
    is, never scaled up.  ``error_weights`` measures the robust tier's PSNR
    floor on the error of the image that will receive the change (see
    :func:`colour_weights`; :func:`embed_rgb` passes them).  With ``strict`` a
    marked output that the detector does not accept as ``both_match`` raises
    :class:`EmbeddingError`; otherwise the failure is returned in the report.
    """
    output, report, _robust_only = _embed_luminance(image, owner_id, secret_key, profile, semantic_features, quantize, strict, reserve_rounding, robust_change, error_weights)
    return output, report


def _embed_luminance(image, owner_id, secret_key, profile, semantic_features, quantize, strict, reserve_rounding, robust_change, error_weights):
    """:func:`embed_with_report`, also returning the image after the robust tier alone."""
    if reserve_rounding is None:
        reserve_rounding = quantize
    checked, key, config, owner, height, width, q, robust, _ws, plan = _prepare(image, owner_id, secret_key, profile, semantic_features)
    embedding = checked["embedding"]
    weights = _checked_weights(error_weights, height, width)
    count = len(robust.positions)
    if robust_change is None:
        _change, delta, _shape, fill = _closed_form(image, robust, plan, checked, weights)
        source = "closed-form"
    else:
        supplied = [[float(value) for value in block] for block in robust_change]
        if len(supplied) != len(robust.normalisers) or any(len(block) != count for block in supplied):
            raise ValueError("robust_change must give one value per robust position of every coarse block")
        if any(not math.isfinite(value) for block in supplied for value in block):
            raise ValueError("robust_change must be finite")
        delta = _shaped(image, robust, supplied, _shape_factors(image, checked))
        spent = _budget(delta, robust.mask, embedding, weights)
        floor_mse = 255.0**2 / 10.0 ** (float(embedding["min_robust_psnr_db"]) / 10.0)
        if spent["planned_mse"] <= 0.0:
            raise ValueError("the robust change is zero")
        if spent["ratio_max"] > float(embedding["block_ratio_cap"]) * EXTERNAL_TOLERANCE or spent["planned_mse"] > floor_mse * EXTERNAL_TOLERANCE**2:
            raise ValueError("the supplied robust change exceeds the profile's block caps or PSNR floor")
        fill = {"fill_scale": None, "bound_by": "external"}
        source = "external"
    limits = {**_budget(delta, robust.mask, embedding, weights), **fill}
    output = [[min(255.0, max(0.0, float(value) + shift)) for value, shift in zip(row, delta_row)] for row, delta_row in zip(image, delta)]
    robust_mse = mse(image, output)
    robust_only = [list(row) for row in output]

    fragile = _Fragile(checked, key, config, owner, height, width)
    means, coefficients = base._analyse(output, fragile.analysis)
    h = base._perceptual_hash(means, coefficients, key, config)
    table = _instance_table(owner, key, config)
    wi = [chip for segment in range(CODE_BITS) for chip in table[segment][_bit(q, segment)][_bit(h, segment)]]
    instance = _embed_fragile(output, fragile, wi, checked, quantize, bool(reserve_rounding))

    result = detect(output, owner_id, secret_key, checked, semantic_features)
    report = {
        "detector_config_id": config.hex(),
        "security": checked["security"],
        "semantic_source": checked["semantic_source"],
        "embedding_domain": "image",
        "version": VERSION,
        "revision": REVISION,
        "embedding": dict(embedding),
        "decision_id": decision_id(checked),
        "semantic_code": f"{q:08x}",
        "perceptual_hash": f"{h:08x}",
        "psnr_db": psnr(image, output),
        "mse": mse(image, output),
        "robust_psnr_db": None if robust_mse == 0.0 else 10.0 * math.log10(255.0**2 / robust_mse),
        "quantized": bool(quantize),
        "rounding_reserved": bool(reserve_rounding),
        "robust_channel": {
            "source": source,
            "host_rejection": plan["host_rejection"],
            "amplitude": plan["amplitude"],
            "host_rms": plan["host_rms"],
            "visibility_share": plan["visibility_share"],
            "error_domain": "luminance" if weights is None else "weighted",
            **limits,
        },
        "instance_channel": instance,
        "clipped_fraction": instance["clipped_fraction"],
        "verification": result,
        "verified": result["outcome"] == "both_match",
        "verification_features": "recomputed" if checked["semantic_source"] == PROXY_SOURCE else "source-features-supplied-by-caller",
    }
    if strict and not report["verified"]:
        raise EmbeddingError("marked output failed self-verification: " + str(result["outcome"]), report)
    return output, report, robust_only


def embed(
    image: Sequence[Sequence[float]],
    owner_id: str,
    secret_key: bytes | str | None = None,
    profile: Mapping[str, object] | None = None,
    semantic_features: Sequence[float] | None = None,
) -> list[list[float]]:
    """Embed and return the verified, integer-valued marked luminance image."""
    return embed_with_report(image, owner_id, secret_key, profile, semantic_features)[0]


# ---------------------------------------------------------------------------
# Phase 3: blind correlation detection and the proposal's decision states
# ---------------------------------------------------------------------------


# Bentkus and Dzindzalieta (2015): for independent random signs e_i and weights with sum a_i^2 <= 1,
# P(sum a_i e_i >= t) <= c * P(Z >= t) with Z standard normal and the optimal c = 1 / (4 P(Z >= sqrt 2)).
TAIL_CONSTANT = 1.0 / (2.0 * math.erfc(1.0))


def _tail_bound(score: float, patterns: int) -> float:
    """Upper bound on the chance that one of ``patterns`` independent sign patterns scores ``score`` or more."""
    return TAIL_CONSTANT * patterns * 0.5 * math.erfc(score / math.sqrt(2.0))


def _threshold(false_positive_target: float, patterns: int) -> float:
    """Smallest score whose bound over ``patterns`` tries stays at or below the false-positive target.

    Revision 1 used Hoeffding's bound ``exp(-t*t/2)``, which is valid for the
    same statistic but looser: 5.26 against 4.98 for one pattern at 1e-6.
    """
    low, high = 0.0, 64.0
    for _ in range(200):
        middle = (low + high) / 2.0
        low, high = (middle, high) if _tail_bound(middle, patterns) > false_positive_target else (low, middle)
    return high


def _log10_bound(score: float, patterns: int) -> float:
    if score <= 0.0:
        return 0.0
    return min(0.0, math.log10(TAIL_CONSTANT * patterns) + math.log10(0.5 * math.erfc(score / math.sqrt(2.0))))


def _key_test(projections: Sequence[float], options: Sequence[Sequence[Sequence[float]]], recomputed: int) -> dict[str, float | int]:
    """Score the pattern of the recomputed code and decode the best-fitting code.

    ``options[j][b]`` is the chip pattern of segment ``j`` for bit value ``b``.
    The recomputed score tests one pattern.  The decoded score is the largest
    over all 2**32 codes; it is found segment by segment because the segments
    do not overlap.  On a tie the recomputed bit is kept.
    """
    energy = math.sqrt(sum(value * value for value in projections))
    if energy <= ZERO_PROJECTION:
        return {"recomputed": 0.0, "decoded": 0.0, "code": recomputed}
    fixed = best = 0.0
    code = 0
    for segment in range(CODE_BITS):
        chips = projections[segment * SEGMENT_CHIPS : (segment + 1) * SEGMENT_CHIPS]
        scores = [sum(sign * value for sign, value in zip(options[segment][bit], chips)) for bit in (0, 1)]
        own = _bit(recomputed, segment)
        fixed += scores[own]
        chosen = own if scores[own] >= scores[1 - own] else 1 - own
        best += scores[chosen]
        code = (code << 1) | chosen
    return {"recomputed": fixed / energy, "decoded": best / energy, "code": code}


def _expected_best(mean: float) -> float:
    """Expected larger of N(mean, 1) and N(0, 1): what one segment adds to the decoded score, in its own noise units."""
    return mean * 0.5 * (1.0 + math.erf(mean / 2.0)) + math.exp(-mean * mean / 4.0) / math.sqrt(math.pi)


def _decoding_error_rate(decoded_score: float) -> float:
    """Chance that a segment decodes to the wrong bit, inferred from the decoded score.

    Model: in units of the noise of one segment, its correct pattern scores
    N(mu, 1) and its other pattern N(0, 1).  The score divides by the energy of
    the projections, which holds the mark as well as the noise, so the decoded
    score has mean ``sqrt(32) * _expected_best(mu) / sqrt(1 + mu^2 / 10)``.
    That is inverted for ``mu``; a segment is wrong when the other pattern
    scores higher.  An unmarked image gives one half, a perfect score zero.
    """
    target = decoded_score / math.sqrt(CODE_BITS)
    if target <= _expected_best(0.0):
        return 0.5
    if target >= math.sqrt(SEGMENT_CHIPS):
        return 0.0
    low, high = 0.0, 1e6
    for _ in range(80):
        middle = (low + high) / 2.0
        if _expected_best(middle) / math.sqrt(1.0 + middle * middle / SEGMENT_CHIPS) < target:
            low = middle
        else:
            high = middle
    return 0.5 * math.erfc(low / 2.0)


def _channel_result(test, target: float, roster_size: int, recomputed_code: int) -> dict[str, object]:
    """Apply the two thresholds and compare the code the mark carries with the recomputed code.

    A key is found when the recomputed pattern passes the threshold for one
    pattern, or the decoded pattern passes the threshold for 2**32 patterns.
    Only a mark strong enough to pass the second can be read: its decoded code
    is then compared with the recomputed one.  The Hamming distance of the two
    includes decoding errors, whose expected number follows from the score;
    ``corrected_distance`` removes that expectation (it is the plain distance
    for a strong mark).  A key found by its recomputed pattern alone is too
    weak to be read and counts as carrying the recomputed code.
    """
    single = _threshold(target, roster_size)
    searched = _threshold(target, (1 << CODE_BITS) * roster_size)
    by_decoding = test["decoded"] >= searched
    by_recomputation = test["recomputed"] >= single
    decoded_code = int(test["code"])
    distance = corrected = error_rate = None
    if by_decoding:
        distance = base._distance(decoded_code, recomputed_code)
        error_rate = _decoding_error_rate(test["decoded"])
        # Rounded so that a strong mark, whose error rate is zero up to floating-point residue, keeps its plain distance.
        corrected = round(min(float(CODE_BITS), max(0.0, (distance - CODE_BITS * error_rate) / (1.0 - 2.0 * error_rate))), 6)
        candidate = "decoded" if distance else "recomputed"
    elif by_recomputation:
        distance, corrected, candidate = 0, 0.0, "recomputed"
    else:
        candidate = None
    score, threshold, patterns = (
        (test["decoded"], searched, (1 << CODE_BITS) * roster_size) if by_decoding else (test["recomputed"], single, roster_size)
    )
    return {
        "found": bool(by_decoding or by_recomputation),
        "read": bool(by_decoding),
        "candidate": candidate,
        "score": score,
        "threshold": threshold,
        "recomputed_score": test["recomputed"],
        "recomputed_threshold": single,
        "decoded_score": test["decoded"],
        "decoded_threshold": searched,
        "decoded_code": f"{decoded_code:08x}",
        "code_distance": distance,
        "corrected_distance": corrected,
        "decoding_error_rate": error_rate,
        "log10_false_positive_bound": _log10_bound(score, patterns),
    }


def detect(
    image: Sequence[Sequence[float]],
    owner_id: str,
    secret_key: bytes | str | None = None,
    profile: Mapping[str, object] | None = None,
    semantic_features: Sequence[float] | None = None,
    binding_mode: str = "combined",
    roster_size: int = 1,
    expected_config_id: str | None = None,
) -> dict[str, object]:
    """Blind verification from the suspect image, the claimed OwnerID and the profile.

    For each key two tests are made.  The proposal's route correlates with the
    key of the codes recomputed from the suspect image.  The second route
    decodes the code that the mark itself carries, which is what makes a
    transferred mark observable: its key verifies while its code disagrees with
    the image that now carries it.

    ``outcome`` is the observation; ``proposal_state`` is the label the
    proposal's decision table assigns to it.  Neither is ground truth: whether
    an image was regenerated or forged is known only from attack provenance.
    """
    started = time.perf_counter()
    if binding_mode not in BINDING_MODES:
        raise ValueError("binding_mode must be one of " + ", ".join(BINDING_MODES))
    if isinstance(roster_size, bool) or not isinstance(roster_size, int) or not 1 <= roster_size <= MAX_ROSTER:
        raise ValueError(f"roster_size must be an integer in 1..{MAX_ROSTER}")
    checked, key, config = _resolve(profile, secret_key)
    if expected_config_id is not None and expected_config_id != config.hex():
        raise ValueError("detector configuration differs from the expected enrolment configuration")
    height, width = base._check_image(image, int(checked["minimum_side"]))
    owner = canonical_owner(owner_id)
    decision = checked["decision"]
    target = float(decision["false_positive_target"])
    fragile = _Fragile(checked, key, config, owner, height, width)
    carrier = _robust_carrier(key, config, owner, len(checked["robust_frequencies"]))
    prepared = time.perf_counter()
    means, coefficients = base._analyse(image, fragile.analysis)
    instance_projections = fragile.projections(coefficients)
    robust = _Robust(_coarse(image), image, checked, carrier)
    transformed = time.perf_counter()
    q_now = _semantic(means, checked, key, config, semantic_features, binding=False)
    h_now = base._perceptual_hash(means, coefficients, key, config)
    featured = time.perf_counter()

    check_semantic = binding_mode in ("combined", "semantic_only")
    check_instance = binding_mode in ("combined", "perceptual_only")
    semantic_limits = (int(decision["semantic_radius"]), int(decision["semantic_mismatch_distance"]))
    instance_limits = (int(decision["instance_radius"]), int(decision["instance_mismatch_distance"]))

    semantic = _channel_result(_key_test(robust.projections, _semantic_table(owner, key, config), q_now), target, roster_size, q_now)
    s_found = bool(semantic["found"])
    s_status = base._content_status(semantic["corrected_distance"], *semantic_limits, check_semantic) if s_found else None
    # Wi is tested with one semantic code: the recomputed one, unless the mark was read and carries another.
    carries_other = s_found and base._content_status(semantic["corrected_distance"], *semantic_limits, True) != "match"
    q_bound = int(semantic["decoded_code"], 16) if carries_other else q_now
    table = _instance_table(owner, key, config)
    options = [table[segment][_bit(q_bound, segment)] for segment in range(CODE_BITS)]
    instance = _channel_result(_key_test(instance_projections, options, h_now), target, roster_size, h_now)
    i_found = bool(instance["found"])
    # The instance key binds both codes, so it inherits the worse of the two comparisons.
    i_status = (
        max(
            base._content_status(instance["corrected_distance"], *instance_limits, check_instance),
            base._content_status(semantic["corrected_distance"], *semantic_limits, check_semantic) if s_found else "unchecked",
            key=base._STATUS_RANK.get,
        )
        if i_found
        else None
    )
    outcome, state = base._decide(s_found, s_status, i_found, i_status)
    finished = time.perf_counter()

    def public(result, status):
        entry = dict(result)
        entry["content_status"] = status
        entry["content_match"] = bool(result["found"] and base._STATUS_RANK[status] == 0)
        return entry

    return {
        "outcome": outcome,
        "proposal_state": state,
        "present": outcome == "both_match",
        "watermark_found": bool(s_found or i_found),
        "semantic": public(semantic, s_status),
        "instance": public(instance, i_status),
        "semantic_code": f"{q_now:08x}",
        "perceptual_hash": f"{h_now:08x}",
        "instance_tested_with_semantic_code": f"{q_bound:08x}",
        "binding_mode": binding_mode,
        "owner_id": owner.decode("utf-8"),
        "owners_tested": roster_size,
        "security": checked["security"],
        "semantic_source": checked["semantic_source"],
        "embedding_domain": "image",
        "detector_config_id": config.hex(),
        "decision_id": decision_id(checked),
        "version": VERSION,
        "revision": REVISION,
        "height": height,
        "width": width,
        # setup: input checks and carrier derivation; transform: both block DCTs and projections.
        "timing_ms": {
            "setup": (prepared - started) * 1000.0,
            "transform": (transformed - prepared) * 1000.0,
            "features": (featured - transformed) * 1000.0,
            "scoring": (finished - featured) * 1000.0,
            "total": (finished - started) * 1000.0,
        },
    }


def identify(
    image: Sequence[Sequence[float]],
    owner_ids: Sequence[str],
    secret_key: bytes | str | None = None,
    profile: Mapping[str, object] | None = None,
    semantic_features: Sequence[float] | None = None,
) -> dict[str, object]:
    """Try a roster of OwnerIDs on one image with thresholds corrected for the roster size."""
    if isinstance(owner_ids, (str, bytes)):
        raise ValueError("owner roster must be a sequence of OwnerID strings, not one string")
    roster = [canonical_owner(owner).decode("utf-8") for owner in owner_ids]
    if not roster or len(set(roster)) != len(roster):
        raise ValueError("owner roster must be non-empty and free of duplicates")
    results = {owner: detect(image, owner, secret_key, profile, semantic_features, roster_size=len(roster)) for owner in roster}
    return {
        "roster_size": len(roster),
        "roster_sha256": hashlib.sha256(base._pack(*(owner.encode("utf-8") for owner in roster))).hexdigest(),
        "found": [owner for owner, result in results.items() if result["watermark_found"]],
        "both_match": [owner for owner, result in results.items() if result["outcome"] == "both_match"],
        "results": results,
    }


# ---------------------------------------------------------------------------
# Codes of an image, colour wrapper
# ---------------------------------------------------------------------------


def perceptual_hash(image: Sequence[Sequence[float]], secret_key: bytes | str | None = None, profile: Mapping[str, object] | None = None) -> int:
    """DCT perceptual hash H of v4, under this profile's key and configuration.

    Unlike in v4 the embedder does move what the hash reads: the robust tier
    changes block means and the (0,1) and (1,0) coefficients.  The instance key
    is therefore bound to the hash of the image after the robust tier.
    """
    checked, key, config = _resolve(profile, secret_key)
    base._check_image(image, int(checked["minimum_side"]))
    return base._perceptual_hash(*base._analyse(image, base._DETAIL_PLANES), key, config)


def semantic_code(features: Sequence[float], secret_key: bytes | str | None = None, profile: Mapping[str, object] | None = None) -> int:
    """Semantic code q: 32 sign projections of the semantic feature vector E."""
    _checked, key, config = _resolve(profile, secret_key)
    return base._semantic_code(features, key, config)


def layout_features(image: Sequence[Sequence[float]]) -> list[float]:
    """Model-free stand-in for the semantic vector E (see v4): a mean-removed 8x8 layout."""
    base._check_image(image, MIN_SIDE)
    return base._layout_features(base._analyse(image, ())[0])


def embed_rgb(
    rgb: Sequence[Sequence[Sequence[float]]],
    owner_id: str,
    secret_key: bytes | str | None = None,
    profile: Mapping[str, object] | None = None,
    semantic_features: Sequence[float] | None = None,
    strict: bool = True,
    robust_change: Sequence[Sequence[float]] | None = None,
) -> tuple[list[list[tuple[int, int, int]]], dict[str, object]]:
    """Mark a colour image: add the luminance change to R, G and B, then round to bytes.

    The robust tier's change goes along :func:`colour_directions` (revision 3:
    at constant chromaticity by default) and its PSNR floor is measured on the
    RGB error that causes; the fragile tier's fine-grained change is added
    equally to R, G and B.  The returned report verifies the rounded RGB output
    itself.
    """
    source = luminance_from_rgb(rgb)
    directions = colour_directions(rgb, profile)
    weights = [[(r * r + g * g + b * b) / 3.0 for r, g, b in row] for row in directions]
    marked, report, robust_only = _embed_luminance(
        source, owner_id, secret_key, profile, semantic_features, False, False, True, robust_change, weights
    )
    clipped = 0
    output = []
    error = 0.0
    for row, source_row, robust_row, marked_row, direction_row in zip(rgb, source, robust_only, marked, directions):
        output_row = []
        for pixel, before, middle, after, direction in zip(row, source_row, robust_row, marked_row, direction_row):
            values = [math.floor(float(channel) + (middle - before) * weight + (after - middle) + 0.5) for channel, weight in zip(pixel, direction)]
            clipped += sum(value < 0 or value > 255 for value in values)
            final = tuple(int(min(255, max(0, value))) for value in values)
            error += sum((value - float(channel)) ** 2 for value, channel in zip(final, pixel))
            output_row.append(final)
        output.append(output_row)
    saved = luminance_from_rgb(output)
    result = detect(saved, owner_id, secret_key, profile, semantic_features)
    rgb_mse = error / (3.0 * len(source) * len(source[0]))
    report.update(
        {
            "verification": result,
            "verified": result["outcome"] == "both_match",
            "quantized": True,
            # A channel at 0 or 255 cannot take its share of the luminance change.
            "clipped_fraction": clipped / (3.0 * len(source) * len(source[0])),
            "mse": mse(source, saved),
            "psnr_db": psnr(source, saved),
            "quality_domain": "luminance of the rounded RGB output",
            "rgb_mse": rgb_mse,
            "rgb_psnr_db": float("inf") if rgb_mse == 0.0 else 10.0 * math.log10(255.0**2 / rgb_mse),
        }
    )
    if strict and not report["verified"]:
        raise EmbeddingError("marked RGB output failed self-verification: " + str(result["outcome"]), report)
    return output, report


def detect_rgb(
    rgb: Sequence[Sequence[Sequence[float]]],
    owner_id: str,
    secret_key: bytes | str | None = None,
    profile: Mapping[str, object] | None = None,
    semantic_features: Sequence[float] | None = None,
    binding_mode: str = "combined",
    roster_size: int = 1,
    expected_config_id: str | None = None,
) -> dict[str, object]:
    """:func:`detect` on the luminance of an RGB image."""
    return detect(luminance_from_rgb(rgb), owner_id, secret_key, profile, semantic_features, binding_mode, roster_size, expected_config_id)
