"""Content-bound dual-key DCT watermark, image-domain reference (revision v4).

This module is an engineering successor to ``revised_watermark_v3.py``; the v2
and v3 candidates stay untouched so their outputs remain reproducible.  v4
restores the mechanisms of the approved proposal that the QIM candidates
dropped, inside a dependency-free image-domain reference codec:

* a dual signature: a semantic code ``q`` (sign random projections of a
  semantic feature vector, CLIP in the study profile) and a DCT-based
  perceptual hash ``H``, combined with the OwnerID into a semantic key ``Ws``
  and an instance key ``Wi``;
* blind detection by correlating low and low-to-mid band 8x8 block-DCT
  coefficients with the patterns expected from the re-derived candidate keys;
* the proposal's decision states: both keys found, semantic key only, and a
  watermark that is present but bound to different content.

The embedder is improved spread spectrum (host-rejecting, antipodal) on keyed
projections of those coefficients, sized by a PSNR budget.  The detection
statistic is a self-normalised correlation whose false-positive probability is
bounded by Hoeffding's inequality, so thresholds follow from a stated
false-positive target instead of ad hoc accuracy cut-offs.

Claim boundary: this is an image-domain codec, proposed as a candidate pixel
comparator and DCT-detector positive control of the study; its adoption is
undecided.  It does not implement or validate latent/initial-noise embedding,
it is not evidence of regeneration survival, and no detector state establishes
legal ownership.  The default ``public-derived`` profile follows the proposal's
key model: every derivation is public, so anyone can re-embed for any OwnerID.
The shipped profiles use the ``proxy-layout-v1`` stand-in for the semantic
vector; the proposal's CLIP vector enters through an ``external:`` profile.
The ``hmac-keyed`` profile is a separately labelled variant whose results must
never be pooled with the default.  See ``research/method-amendment-v4.md``.

Revision 2.  Revision 1 is the snapshot committed as 0e91bd2 on
``codex/18-v4-three-threats`` and used by run ``c4-v4-three-threat-dev-001``.
Revision 2 changes the perceptual hash and the decision table, so it derives a
different ``detector_config_id``: the two revisions never read each other's
marks and their results cannot be confused.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import math
import re
import time
import unicodedata
from operator import mul
from pathlib import Path
from typing import Mapping, Sequence


MAGIC = b"rw-v4"
VERSION = 4
REVISION = 2
BLOCK = 8
MIN_SIDE = 160
HASH_GRID = 32
LAYOUT_GRID = 8
HASH_COARSE_SHARE = 0.25
HASH_DETAIL_DEAD_ZONE = 6.0
# Detail weaker than this (RMS of the compressed values) keeps a proportionally smaller share.
HASH_DETAIL_FLOOR = 0.4
HASH_DETAIL_KNEE = 8.0
HASH_DETAIL_POSITIONS = ((0, 1), (1, 0))
CODE_BITS = 32
CHECK_BITS = 4
HADAMARD_ORDER = 5
SYMBOL_BITS = HADAMARD_ORDER + 1
SYMBOL_CHIPS = 1 << HADAMARD_ORDER
HELPER_CHIPS = ((CODE_BITS + CHECK_BITS) // SYMBOL_BITS) * SYMBOL_CHIPS
TAG_BITS = 128
CHANNEL_BITS = HELPER_CHIPS + TAG_BITS
SEMANTIC_FREQUENCIES = ((1, 1), (0, 2), (2, 0), (1, 2), (2, 1), (2, 2))
INSTANCE_FREQUENCIES = ((0, 3), (3, 0), (1, 3), (3, 1), (2, 3), (3, 2))
PROXY_SOURCE = "proxy-layout-v1"
EXTERNAL_SOURCE = re.compile(r"external:[A-Za-z0-9._@/+:-]{1,128}")
BINDING_MODES = ("combined", "semantic_only", "perceptual_only", "none")
PUBLIC_KEY = hashlib.sha256(MAGIC + b"/public-derived-profile-key").digest()
# Below this target the threshold would exceed the largest attainable score.
MIN_FALSE_POSITIVE_TARGET = 1e-20
MAX_ROSTER = 1_000_000
# Rounding to bytes adds this much mean squared error on its own.
ROUNDING_MSE = 1.0 / 12.0
# Numerical guards of the detector.  Projections are in luminance units; a mark
# has an amplitude of several units, floating-point residue about 1e-13.
ZERO_PROJECTION = 1e-6
TIE_TOLERANCE = 1e-9
TIE_FLOOR = 1e-9
FINGERPRINT_ROUNDS = 200_000

_CONSTANTS = {
    "schema_version": "revised-watermark-v4",
    "profile": "image-domain-dual-key-dct-iss",
    "code_bits": CODE_BITS,
    "tag_bits": TAG_BITS,
}
_EMBEDDING_FIELDS = frozenset(("target_psnr_db", "semantic_energy_share", "design_noise_std", "passes"))
_DECISION_FIELDS = frozenset(
    ("false_positive_target", "semantic_radius", "semantic_mismatch_distance", "instance_radius", "instance_mismatch_distance")
)
_PROFILE_FIELDS = frozenset(_CONSTANTS) | {
    "security",
    "semantic_source",
    "minimum_side",
    "semantic_frequencies",
    "instance_frequencies",
    "embedding",
    "decision",
}


def _default_profile(security: str) -> dict[str, object]:
    """A fresh profile each time, so the two module defaults share no nested object."""
    return {
        "schema_version": _CONSTANTS["schema_version"],
        "profile": _CONSTANTS["profile"],
        "security": security,
        "semantic_source": PROXY_SOURCE,
        "minimum_side": MIN_SIDE,
        "semantic_frequencies": [list(pair) for pair in SEMANTIC_FREQUENCIES],
        "instance_frequencies": [list(pair) for pair in INSTANCE_FREQUENCIES],
        "code_bits": CODE_BITS,
        "tag_bits": TAG_BITS,
        "embedding": {
            "target_psnr_db": 42.0,
            "semantic_energy_share": 0.6,
            "design_noise_std": 8.0,
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

# Fields that change what the detector computes.  Embedding strength and
# decision thresholds are excluded: the correlation detector needs neither the
# embedding amplitude nor a re-enrolment when a calibration version changes.
_DETECTOR_FIELDS = (
    "schema_version",
    "profile",
    "security",
    "semantic_source",
    "minimum_side",
    "semantic_frequencies",
    "instance_frequencies",
    "code_bits",
    "tag_bits",
)


def _dct_basis(points: int, rows: int) -> tuple[tuple[float, ...], ...]:
    return tuple(
        tuple(
            (math.sqrt(1.0 / points) if u == 0 else math.sqrt(2.0 / points)) * math.cos((2 * n + 1) * u * math.pi / (2 * points))
            for n in range(points)
        )
        for u in range(rows)
    )


_DCT_BASIS = _dct_basis(BLOCK, BLOCK)
_HASH_BASIS = _dct_basis(HASH_GRID, 8)
_HASH_BAND = tuple(sorted(((u, v) for u in range(8) for v in range(8) if (u, v) != (0, 0)), key=lambda p: (p[0] + p[1], p[0], p[1])))


class EmbeddingError(ValueError):
    """The marked output failed self-verification; ``report`` holds the diagnostics."""

    def __init__(self, message: str, report: Mapping[str, object]):
        super().__init__(message)
        self.report = dict(report)


def _plane(u: int, v: int) -> tuple[float, ...]:
    return tuple(_DCT_BASIS[u][y] * _DCT_BASIS[v][x] for y in range(BLOCK) for x in range(BLOCK))


_DETAIL_PLANES = tuple(_plane(u, v) for u, v in HASH_DETAIL_POSITIONS)


# ---------------------------------------------------------------------------
# Canonical inputs, profile and keyed derivation
# ---------------------------------------------------------------------------


def _check_image(image: Sequence[Sequence[float]], minimum_side: int = MIN_SIDE) -> tuple[int, int]:
    height = len(image)
    width = len(image[0]) if height else 0
    if height < minimum_side or width < minimum_side:
        raise ValueError(f"image must be at least {minimum_side}x{minimum_side}")
    for row in image:
        if len(row) != width:
            raise ValueError("image rows must have equal length")
        for value in row:
            value = float(value)
            if not math.isfinite(value) or not 0.0 <= value <= 255.0:
                raise ValueError("image values must be finite luminance bytes in [0, 255]")
    return height, width


def canonical_owner(owner_id: str) -> bytes:
    if not isinstance(owner_id, str):
        raise TypeError("OwnerID must be a string")
    value = unicodedata.normalize("NFC", owner_id).encode("utf-8")
    if not 1 <= len(value) <= 256:
        raise ValueError("OwnerID must contain 1..256 UTF-8 bytes")
    return value


def canonical_secret_key(secret_key: bytes | str) -> bytes:
    if isinstance(secret_key, str):
        value = secret_key.encode("utf-8")
    elif isinstance(secret_key, bytes):
        value = secret_key
    else:
        raise TypeError("secret_key must be bytes or str")
    if len(value) < 16 or len(value) > 4096:
        raise ValueError("secret_key must contain 16..4096 bytes")
    return value


def _number(value: object, low: float, high: float, name: str, low_open: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite number")
    try:
        number = float(value)
    except OverflowError as error:
        raise ValueError(f"{name} must be a finite number") from error
    if not math.isfinite(number):
        raise ValueError(f"{name} must be a finite number")
    if number > high or number < low or (low_open and number == low):
        raise ValueError(f"{name} is outside its allowed range")
    return number


def _frequency_set(value: object, name: str) -> tuple[tuple[int, int], ...]:
    if not isinstance(value, (list, tuple)) or not 1 <= len(value) <= 16:
        raise ValueError(f"{name} must list 1..16 coefficient positions")
    pairs = []
    for pair in value:
        if not isinstance(pair, (list, tuple)) or len(pair) != 2 or any(isinstance(i, bool) or not isinstance(i, int) for i in pair):
            raise ValueError(f"{name} entries must be [u, v] integer pairs")
        u, v = pair
        if not (0 <= u < BLOCK and 0 <= v < BLOCK) or (u, v) == (0, 0):
            raise ValueError(f"{name} must use non-DC positions inside the 8x8 block")
        if (u, v) in HASH_DETAIL_POSITIONS:
            raise ValueError(f"{name} must leave (0,1) and (1,0) untouched: the perceptual hash reads them")
        pairs.append((u, v))
    if len(set(pairs)) != len(pairs):
        raise ValueError(f"{name} repeats a coefficient position")
    return tuple(pairs)


def validate_profile(profile: Mapping[str, object]) -> dict[str, object]:
    """Return a checked copy of ``profile``; reject unknown, missing or out-of-range fields."""
    if not isinstance(profile, Mapping) or set(profile) != _PROFILE_FIELDS:
        raise ValueError("profile must contain exactly the revised-watermark-v4 fields")
    for key, expected in _CONSTANTS.items():
        # The type check keeps 32.0 out: it would change the canonical JSON and so the carrier.
        if type(profile[key]) is not type(expected) or profile[key] != expected:
            raise ValueError(f"profile constant mismatch: {key}")
    if profile["security"] not in ("hmac-keyed", "public-derived"):
        raise ValueError("security must be hmac-keyed or public-derived")
    source = profile["semantic_source"]
    if not isinstance(source, str) or not (source == PROXY_SOURCE or EXTERNAL_SOURCE.fullmatch(source)):
        raise ValueError("semantic_source must be proxy-layout-v1 or external:<feature id of 1..128 characters from A-Za-z0-9._@/+:->")
    side = profile["minimum_side"]
    if isinstance(side, bool) or not isinstance(side, int) or not MIN_SIDE <= side <= 16384:
        raise ValueError(f"minimum_side must be an integer of at least {MIN_SIDE}")
    semantic = _frequency_set(profile["semantic_frequencies"], "semantic_frequencies")
    instance = _frequency_set(profile["instance_frequencies"], "instance_frequencies")
    if set(semantic) & set(instance):
        raise ValueError("semantic and instance channels must use disjoint coefficients")
    if (side // BLOCK) ** 2 * min(len(semantic), len(instance)) < CHANNEL_BITS * 4:
        raise ValueError("a channel has too few coefficient positions for an image of minimum_side")
    embedding = profile["embedding"]
    if not isinstance(embedding, Mapping) or set(embedding) != _EMBEDDING_FIELDS:
        raise ValueError("embedding must contain exactly the revised-watermark-v4 fields")
    _number(embedding["target_psnr_db"], 30.0, 60.0, "target_psnr_db")
    _number(embedding["semantic_energy_share"], 0.05, 0.95, "semantic_energy_share")
    _number(embedding["design_noise_std"], 0.0, 64.0, "design_noise_std", low_open=True)
    if isinstance(embedding["passes"], bool) or not isinstance(embedding["passes"], int) or not 1 <= embedding["passes"] <= 8:
        raise ValueError("embedding passes must be an integer in 1..8")
    decision = profile["decision"]
    if not isinstance(decision, Mapping) or set(decision) != _DECISION_FIELDS:
        raise ValueError("decision must contain exactly the revised-watermark-v4 fields")
    _number(decision["false_positive_target"], MIN_FALSE_POSITIVE_TARGET, 1e-2, "false_positive_target")
    for name in ("semantic", "instance"):
        radius, far = decision[name + "_radius"], decision[name + "_mismatch_distance"]
        if any(isinstance(value, bool) or not isinstance(value, int) for value in (radius, far)) or not 0 <= radius < far <= CODE_BITS // 2:
            raise ValueError(f"{name} distances must be integers with 0 <= radius < mismatch_distance <= {CODE_BITS // 2}")
    checked = dict(profile)
    checked["semantic_frequencies"] = [list(pair) for pair in semantic]
    checked["instance_frequencies"] = [list(pair) for pair in instance]
    checked["embedding"] = dict(embedding)
    checked["decision"] = dict(decision)
    return checked


def _unique_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    keys = [key for key, _value in pairs]
    if len(set(keys)) != len(keys):
        raise ValueError("profile JSON repeats a key")
    return dict(pairs)


def _no_constant(name: str) -> float:
    raise ValueError(f"profile JSON contains the non-finite literal {name}")


def load_profile(path: str | Path) -> dict[str, object]:
    """Read and validate a profile; repeated keys and NaN/Infinity literals are errors."""
    text = Path(path).read_text(encoding="utf-8")
    return validate_profile(json.loads(text, object_pairs_hook=_unique_keys, parse_constant=_no_constant))


def _canonical_json(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("ascii")


def detector_config_id(profile: Mapping[str, object]) -> str:
    """SHA-256 of the canonical JSON of every field the detector depends on."""
    checked = validate_profile(profile)
    static = {key: checked[key] for key in _DETECTOR_FIELDS}
    return hashlib.sha256(MAGIC + b"/config/r%d/" % REVISION + _canonical_json(static)).hexdigest()


def decision_id(profile: Mapping[str, object]) -> str:
    """SHA-256 of the decision thresholds, so a calibration version can be cited."""
    return hashlib.sha256(MAGIC + b"/decision/" + _canonical_json(validate_profile(profile)["decision"])).hexdigest()


def _pack(*fields: bytes) -> bytes:
    """Length-prefixed concatenation, so distinct field tuples never collide."""
    return b"".join(len(field).to_bytes(4, "big") + field for field in fields)


def _stream(key: bytes, config: bytes, label: bytes, length: int) -> bytes:
    """HMAC-SHA256 in counter mode: a keyed pseudorandom byte string for one label."""
    blocks = []
    for counter in range((length + 31) // 32):
        blocks.append(hmac.new(key, _pack(MAGIC, config, label, counter.to_bytes(4, "big")), hashlib.sha256).digest())
    return b"".join(blocks)[:length]


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


def key_fingerprint(secret_key: bytes | str) -> str:
    """A label for grouping keyed results by key without storing the key.

    It is deliberately slow, and detection results do not carry it: a cheap
    fingerprint in a published result would let anyone test key guesses offline.
    """
    key = canonical_secret_key(secret_key)
    return hashlib.pbkdf2_hmac("sha256", key, MAGIC + b"/fingerprint", FINGERPRINT_ROUNDS).hex()[:16]


# ---------------------------------------------------------------------------
# Block DCT analysis
# ---------------------------------------------------------------------------


def _analyse(image: Sequence[Sequence[float]], planes: Sequence[Sequence[float]]) -> tuple[list[list[float]], list[list[float]]]:
    """Per full 8x8 block: the block mean, and the requested DCT coefficients.

    Only complete blocks are used.  A right/bottom remainder of up to seven
    pixels is not read by the hash or the carrier and carries no mark; the
    embedder only rounds it when it rounds the rest of the image.
    """
    height, width = len(image), len(image[0])
    means: list[list[float]] = []
    coefficients: list[list[float]] = []
    for by in range(height // BLOCK):
        rows = image[by * BLOCK : by * BLOCK + BLOCK]
        mean_row = []
        for bx in range(width // BLOCK):
            block = [float(value) for row in rows for value in row[bx * BLOCK : bx * BLOCK + BLOCK]]
            mean_row.append(sum(block) / 64.0)
            coefficients.append([sum(map(mul, block, plane)) for plane in planes])
        means.append(mean_row)
    return means, coefficients


def block_coefficients(image: Sequence[Sequence[float]], positions: Sequence[tuple[int, int]]) -> tuple[list[list[float]], list[list[float]]]:
    """Block means, and the DCT coefficients at ``positions``, of every complete 8x8 block (row-major)."""
    return _analyse(image, [_plane(u, v) for u, v in positions])


def basis_plane(u: int, v: int) -> tuple[float, ...]:
    """The 64 samples (row-major) of the 8x8 DCT basis function with vertical index ``u`` and horizontal index ``v``."""
    return _plane(u, v)


def _area_weights(source: int, target: int) -> list[list[tuple[int, float]]]:
    """Exact area-average resampling weights from ``source`` to ``target`` samples."""
    scale = source / target
    weights = []
    for index in range(target):
        start, stop = index * scale, (index + 1) * scale
        row = []
        for position in range(int(math.floor(start)), min(source, int(math.ceil(stop)))):
            overlap = min(stop, position + 1.0) - max(start, float(position))
            if overlap > 0.0:
                row.append((position, overlap / scale))
        weights.append(row)
    return weights


def _resample(grid: Sequence[Sequence[float]], size: int) -> list[list[float]]:
    row_weights = _area_weights(len(grid), size)
    column_weights = _area_weights(len(grid[0]), size)
    narrowed = [[sum(row[position] * weight for position, weight in weights) for weights in column_weights] for row in grid]
    return [[sum(narrowed[position][x] * weight for position, weight in weights) for x in range(size)] for weights in row_weights]


# ---------------------------------------------------------------------------
# Phase 1: semantic code, perceptual hash and the dual keys
# ---------------------------------------------------------------------------


def _sign_projections(vector: Sequence[float], key: bytes, config: bytes, label: bytes) -> int:
    """CODE_BITS signs of keyed Rademacher projections (random-hyperplane hashing).

    Two vectors at angle ``theta`` disagree in each bit with probability
    ``theta / pi``, so nearby content gives nearby codes and there is no
    avalanche.  The hyperplanes are derived from the profile key: public in the
    public-derived profile, unknown to an attacker in the keyed one.
    """
    width = len(vector)
    row_bytes = (width + 7) // 8
    material = _stream(key, config, _pack(label, width.to_bytes(4, "big")), CODE_BITS * row_bytes)
    code = 0
    for row in range(CODE_BITS):
        chunk = material[row * row_bytes : (row + 1) * row_bytes]
        total = 0.0
        for index, value in enumerate(vector):
            total += -value if (chunk[index >> 3] >> (index & 7)) & 1 else value
        # The tolerance keeps a featureless input at zero despite rounding error.
        code = (code << 1) | int(total > 1e-9)
    return code


def _unit(vector: Sequence[float], weight: float, floor: float = 1e-9) -> list[float]:
    """Scale ``vector`` to length ``weight``, or shorter when its own length is below ``floor``."""
    norm = math.sqrt(sum(value * value for value in vector))
    return [0.0] * len(vector) if norm < 1e-9 else [value * weight / max(norm, floor) for value in vector]


def _local_detail(field: Sequence[Sequence[float]]) -> list[float]:
    """Remove each value's 3x3 neighbourhood mean, then compress it to (-1, 1).

    The subtraction drops the slowly varying part of the gradient, which images
    of one composition share.  The dead zone silences blocks whose remaining
    gradient is at noise level, and the soft sign lets every textured block
    count about equally.
    """
    height, width = len(field), len(field[0])
    output = []
    for y in range(height):
        rows = [field[min(height - 1, max(0, y + dy))] for dy in (-1, 0, 1)]
        for x in range(width):
            local = field[y][x] - sum(row[min(width - 1, max(0, x + dx))] for row in rows for dx in (-1, 0, 1)) / 9.0
            excess = max(0.0, abs(local) - HASH_DETAIL_DEAD_ZONE)
            output.append(math.copysign(excess / (excess + HASH_DETAIL_KNEE), local))
    return output


def _perceptual_hash(means: Sequence[Sequence[float]], detail: Sequence[Sequence[float]], key: bytes, config: bytes) -> int:
    """Hash two scales of block-DCT content that the embedder never modifies.

    ``means`` gives coarse structure (the classic pHash input: the low band of
    a 32x32 map).  ``detail`` holds each block's (0,1) and (1,0) coefficients,
    its local gradient, which is what differs between two images that share a
    composition.  Detail carries three quarters of the vector's energy when the
    image has that much detail.  A smooth image has almost none; its few
    noise-level entries then keep a proportionally small share instead of being
    blown up to three quarters, and the hash rests on the coarse part.
    """
    grid = _resample(means, HASH_GRID)
    coarse = []
    for u, v in _HASH_BAND:
        partial = [sum(_HASH_BASIS[u][y] * grid[y][x] for y in range(HASH_GRID)) for x in range(HASH_GRID)]
        # Natural-image amplitude falls roughly as 1/f; the weight keeps the
        # lowest two or three coefficients from deciding every bit.
        coarse.append(sum(partial[x] * _HASH_BASIS[v][x] for x in range(HASH_GRID)) * math.hypot(u, v))
    columns = len(means[0])
    fine: list[float] = []
    for position in range(len(HASH_DETAIL_POSITIONS)):
        fine += _local_detail([[block[position] for block in detail[start : start + columns]] for start in range(0, len(detail), columns)])
    floor = HASH_DETAIL_FLOOR * math.sqrt(len(fine))
    vector = _unit(coarse, math.sqrt(HASH_COARSE_SHARE)) + _unit(fine, math.sqrt(1.0 - HASH_COARSE_SHARE), floor)
    return _sign_projections(vector, key, config, b"perceptual-projection")


def _layout_features(means: Sequence[Sequence[float]]) -> list[float]:
    flat = [value for row in _resample(means, LAYOUT_GRID) for value in row]
    mean = sum(flat) / len(flat)
    return [value - mean for value in flat]


def _semantic_code(features: Sequence[float], key: bytes, config: bytes) -> int:
    if isinstance(features, (str, bytes)):
        raise ValueError("semantic feature vector must be a sequence of numbers")
    try:
        vector = [float(value) for value in features]
    except (TypeError, OverflowError) as error:
        raise ValueError("semantic feature vector must be a sequence of finite numbers") from error
    if len(vector) < 16 or len(vector) > 65536:
        raise ValueError("semantic feature vector must have 16..65536 entries")
    if any(not math.isfinite(value) for value in vector):
        raise ValueError("semantic feature vector must be finite and non-zero")
    largest = max(abs(value) for value in vector)
    if largest < 1e-12:
        raise ValueError("semantic feature vector must be finite and non-zero")
    # Dividing by the largest entry makes the code independent of the vector's scale.
    return _sign_projections([value / largest for value in vector], key, config, b"semantic-projection")


def _codes(
    means: Sequence[Sequence[float]],
    detail: Sequence[Sequence[float]],
    checked: Mapping[str, object],
    key: bytes,
    config: bytes,
    supplied: Sequence[float] | None,
    binding: bool,
) -> tuple[int, int]:
    """Content codes of an image.  ``binding`` is true when a mark is about to be bound to them."""
    if checked["semantic_source"] == PROXY_SOURCE:
        if supplied is not None:
            raise ValueError("the proxy-layout-v1 profile computes its own features")
        features: Sequence[float] = _layout_features(means)
        if max(abs(value) for value in features) < 1e-9:
            if binding:
                raise ValueError("image has no coarse layout to bind: every region has the same mean")
            # A suspect image may be featureless; its code is then the all-zero code.
            return 0, _perceptual_hash(means, detail, key, config)
    elif supplied is None:
        raise ValueError("an external semantic_source requires the caller's semantic_features")
    else:
        features = supplied
    return _semantic_code(features, key, config), _perceptual_hash(means, detail, key, config)


def perceptual_hash(image: Sequence[Sequence[float]], secret_key: bytes | str | None = None, profile: Mapping[str, object] | None = None) -> int:
    """DCT perceptual hash H: 32 sign projections of coarse structure and block gradients.

    It reads only block means and the (0,1) and (1,0) coefficients, none of
    which the embedder changes, so marking an image does not move its own hash
    except through rounding and clipping.  A constant image hashes to zero;
    that is a documented collision.
    """
    checked, key, config = _resolve(profile, secret_key)
    _check_image(image, int(checked["minimum_side"]))
    return _perceptual_hash(*_analyse(image, _DETAIL_PLANES), key, config)


def layout_features(image: Sequence[Sequence[float]]) -> list[float]:
    """Model-free stand-in for the semantic vector E: a mean-removed 8x8 layout.

    This is a coarse-layout descriptor for dependency-free tests and controls.
    It is not CLIP and carries no semantic meaning; the study profile supplies
    the pinned encoder's vector through ``semantic_features`` instead.
    """
    _check_image(image)
    return _layout_features(_analyse(image, ())[0])


def semantic_code(features: Sequence[float], secret_key: bytes | str | None = None, profile: Mapping[str, object] | None = None) -> int:
    """Semantic code q: 32 sign projections of the semantic feature vector E."""
    _checked, key, config = _resolve(profile, secret_key)
    return _semantic_code(features, key, config)


def _bits(value: bytes, count: int) -> list[int]:
    return [(value[index >> 3] >> (7 - (index & 7))) & 1 for index in range(count)]


def derive_keys(q: int, h: int, owner: bytes, key: bytes, config: bytes) -> tuple[list[int], list[int]]:
    """The proposal's dual keys as bit patterns.

    ``Ws = PRF(q, OwnerID)`` binds owner and semantics; ``Wi = PRF(q, H,
    OwnerID)`` additionally binds the perceptual instance.
    """
    q_bytes, h_bytes = q.to_bytes(CODE_BITS // 8, "big"), h.to_bytes(CODE_BITS // 8, "big")
    ws = _stream(key, config, _pack(b"ws", owner, q_bytes), TAG_BITS // 8)
    wi = _stream(key, config, _pack(b"wi", owner, q_bytes, h_bytes), TAG_BITS // 8)
    return _bits(ws, TAG_BITS), _bits(wi, TAG_BITS)


# ---------------------------------------------------------------------------
# Helper data: biorthogonal Reed-Muller RM(1,5) with soft maximum-likelihood decoding
# ---------------------------------------------------------------------------


def _crc4(code: int) -> int:
    register = 0
    for index in range(CODE_BITS - 1, -1, -1):
        feedback = ((register >> 3) & 1) ^ ((code >> index) & 1)
        register = ((register << 1) & 0xF) ^ (0x3 if feedback else 0)
    return register


def _parity(value: int) -> int:
    return bin(value).count("1") & 1


def _helper_encode(code: int) -> list[int]:
    word = (code << CHECK_BITS) | _crc4(code)
    chips: list[int] = []
    for shift in range(CODE_BITS + CHECK_BITS - SYMBOL_BITS, -1, -SYMBOL_BITS):
        symbol = (word >> shift) & (SYMBOL_CHIPS * 2 - 1)
        sign, index = symbol >> HADAMARD_ORDER, symbol & (SYMBOL_CHIPS - 1)
        chips.extend(sign ^ _parity(index & chip) for chip in range(SYMBOL_CHIPS))
    return chips


def _helper_decode(soft: Sequence[float]) -> tuple[int, bool]:
    """Soft-decision decode; positive soft values mean chip 0.  Returns (code, check_ok).

    A symbol whose transform stays within ``ZERO_PROJECTION`` is an erasure and
    decodes to symbol 0.  Values within ``TIE_TOLERANCE`` (relative) or
    ``TIE_FLOOR`` (absolute) of the largest count as tied and the lowest index
    wins, so that the decoded code does not follow the floating-point summation
    order of an implementation.  The floor matters on near-flat images, whose
    transform values are small while rounding residue stays about 1e-12.
    """
    word = 0
    erased = False
    for start in range(0, HELPER_CHIPS, SYMBOL_CHIPS):
        spectrum = list(soft[start : start + SYMBOL_CHIPS])
        span = 1
        while span < SYMBOL_CHIPS:  # fast Walsh-Hadamard transform
            for base in range(0, SYMBOL_CHIPS, span * 2):
                for offset in range(base, base + span):
                    a, b = spectrum[offset], spectrum[offset + span]
                    spectrum[offset], spectrum[offset + span] = a + b, a - b
            span *= 2
        peak = max(abs(value) for value in spectrum)
        if peak <= ZERO_PROJECTION:
            erased = True
            word <<= SYMBOL_BITS
            continue
        window = max(peak * TIE_TOLERANCE, TIE_FLOOR)
        index = next(i for i in range(SYMBOL_CHIPS) if abs(spectrum[i]) >= peak - window)
        word = (word << SYMBOL_BITS) | (int(spectrum[index] < 0.0) << HADAMARD_ORDER) | index
    code = word >> CHECK_BITS
    return code, not erased and (word & ((1 << CHECK_BITS) - 1)) == _crc4(code)


# ---------------------------------------------------------------------------
# Carrier: keyed, owner-specific spreading of each channel bit over many coefficients
# ---------------------------------------------------------------------------


def _carrier(key: bytes, config: bytes, owner: bytes, channel: bytes, height: int, width: int, slots: int) -> tuple[list[int], list[float], list[float]]:
    """Assign every coefficient slot a channel bit and a sign; return per-bit norms."""
    label = _pack(b"carrier", channel, owner, height.to_bytes(4, "big"), width.to_bytes(4, "big"))
    material = _stream(key, config, label, slots * 8)
    words = [int.from_bytes(material[index * 8 : index * 8 + 8], "big") for index in range(slots)]
    order = sorted(range(slots), key=lambda slot: (words[slot] >> 1, slot))
    bit_of_slot = [0] * slots
    for rank, slot in enumerate(order):
        bit_of_slot[slot] = rank % CHANNEL_BITS
    signs = [1.0 if word & 1 else -1.0 for word in words]
    counts = [0] * CHANNEL_BITS
    for bit in bit_of_slot:
        counts[bit] += 1
    return bit_of_slot, signs, [math.sqrt(count) for count in counts]


def _project(values: Sequence[float], bit_of_slot: Sequence[int], signs: Sequence[float], norms: Sequence[float]) -> list[float]:
    """Unit-norm keyed projection of the slot coefficients onto each channel bit."""
    totals = [0.0] * CHANNEL_BITS
    for value, bit, sign in zip(values, bit_of_slot, signs):
        totals[bit] += value * sign
    return [total / norm for total, norm in zip(totals, norms)]


def _correlation(pattern: Sequence[int], projections: Sequence[float]) -> float:
    """Self-normalised correlation of the tag projections with an expected key pattern.

    For any fixed projections and an independent uniformly random pattern the
    statistic exceeds ``t`` with probability at most ``exp(-t*t/2)`` (Hoeffding).
    Projections without energy (a flat image) score zero instead of a ratio of
    rounding residues.
    """
    energy = math.sqrt(sum(value * value for value in projections))
    if energy <= ZERO_PROJECTION:
        return 0.0
    return sum((-value if bit else value) for bit, value in zip(pattern, projections)) / energy


def _threshold(false_positive_target: float, patterns: int) -> float:
    """Score needed so that ``patterns`` tries stay below the false-positive target."""
    return math.sqrt(2.0 * math.log(patterns / false_positive_target))


def _log10_bound(score: float, patterns: int) -> float:
    if score <= 0.0:
        return 0.0
    return min(0.0, (math.log(patterns) - score * score / 2.0) / math.log(10.0))


class _Geometry:
    """Everything that depends only on image size, owner, key and detector configuration."""

    def __init__(self, checked: Mapping[str, object], key: bytes, config: bytes, owner: bytes, height: int, width: int):
        self.frequencies = (
            tuple(tuple(pair) for pair in checked["semantic_frequencies"]),
            tuple(tuple(pair) for pair in checked["instance_frequencies"]),
        )
        self.planes = [_plane(u, v) for channel in self.frequencies for (u, v) in channel]
        # Every analysis also reads the two hash positions, ahead of the channel coefficients.
        self.analysis = list(_DETAIL_PLANES) + self.planes
        self.skip = len(_DETAIL_PLANES)
        self.split = self.skip + len(self.frequencies[0])
        blocks = (height // BLOCK) * (width // BLOCK)
        self.carriers = []
        for name, channel in zip((b"s", b"i"), self.frequencies):
            slots = blocks * len(channel)
            if slots < CHANNEL_BITS * 4:
                raise ValueError("image has too few DCT slots for the dual-key payload")
            self.carriers.append(_carrier(key, config, owner, name, height, width, slots))

    def channel_values(self, coefficients: Sequence[Sequence[float]], channel: int) -> list[float]:
        start, stop = (self.skip, self.split) if channel == 0 else (self.split, len(self.analysis))
        return [value for block in coefficients for value in block[start:stop]]

    def projections(self, coefficients: Sequence[Sequence[float]]) -> list[list[float]]:
        return [_project(self.channel_values(coefficients, channel), *self.carriers[channel]) for channel in (0, 1)]


# ---------------------------------------------------------------------------
# Phase 2 (image-domain arm): improved spread-spectrum embedding
# ---------------------------------------------------------------------------


def _host_rejection(budget_per_bit: float, host_power: float, noise_power: float) -> tuple[float, float]:
    """Choose the host-rejection factor that maximises the detector's signal-to-noise ratio.

    Moving a projection from host value ``p`` to ``(1-lam)*p + a*e`` costs
    ``a*a + lam*lam*host_power`` on average over the key pattern and leaves
    ``(1-lam)**2*host_power`` of host interference.  The cost expression is
    derived for this codec; the scheme is improved spread spectrum after
    Malvar and Florencio (2003).
    """
    best = (-1.0, 0.0, 0.0)
    for step in range(101):
        rejection = step / 100.0
        amplitude_power = budget_per_bit - rejection * rejection * host_power
        if amplitude_power <= 0.0:
            break
        ratio = amplitude_power / ((1.0 - rejection) ** 2 * host_power + noise_power)
        if ratio > best[0]:
            best = (ratio, rejection, math.sqrt(amplitude_power))
    return best[1], best[2]


def _plan(
    image: Sequence[Sequence[float]],
    owner_id: str,
    secret_key: bytes | str | None,
    profile: Mapping[str, object] | None,
    semantic_features: Sequence[float] | None,
    reserve_rounding: bool,
) -> dict[str, object]:
    checked, key, config = _resolve(profile, secret_key)
    height, width = _check_image(image, int(checked["minimum_side"]))
    owner = canonical_owner(owner_id)
    geometry = _Geometry(checked, key, config, owner, height, width)
    means, coefficients = _analyse(image, geometry.analysis)
    q, h = _codes(means, coefficients, checked, key, config, semantic_features, binding=True)
    ws, wi = derive_keys(q, h, owner, key, config)
    host = geometry.projections(coefficients)
    embedding = checked["embedding"]
    target_mse = 255.0**2 / 10.0 ** (float(embedding["target_psnr_db"]) / 10.0)
    if reserve_rounding:
        # Byte rounding spends part of the budget by itself; plan the signal with the rest.
        target_mse = max(target_mse - ROUNDING_MSE, 0.25 * target_mse)
    total = target_mse * height * width
    share = float(embedding["semantic_energy_share"])
    noise_power = float(embedding["design_noise_std"]) ** 2
    targets, channels = [], []
    for channel, (code, tag, fraction) in enumerate(((q, ws, share), (h, wi, 1.0 - share))):
        bits = _helper_encode(code) + list(tag)
        power = sum(value * value for value in host[channel]) / CHANNEL_BITS
        rejection, amplitude = _host_rejection(total * fraction / CHANNEL_BITS, power, noise_power)
        targets.append([(1.0 - rejection) * value + (-amplitude if bit else amplitude) for value, bit in zip(host[channel], bits)])
        channels.append({"host_rejection": rejection, "amplitude": amplitude, "host_rms": math.sqrt(power)})
    return {
        "checked": checked,
        "key": key,
        "config": config,
        "height": height,
        "width": width,
        "geometry": geometry,
        "coefficients": coefficients,
        "host": host,
        "targets": targets,
        "channels": channels,
        "q": q,
        "h": h,
    }


def projection_targets(
    image: Sequence[Sequence[float]],
    owner_id: str,
    secret_key: bytes | str | None = None,
    profile: Mapping[str, object] | None = None,
    semantic_features: Sequence[float] | None = None,
) -> dict[str, object]:
    """Embedding-domain-independent contract: which projections must reach which values.

    Any embedder -- this pixel-domain one or a diffusion-latent optimiser -- that
    drives ``projection[channel][bit]`` of the output image to ``target`` is read
    by the same detector.  Each slot is ``(block_index, u, v, bit, sign, norm)``
    and ``projection[bit] = sum(sign * C[block, u, v]) / norm`` over its slots.
    """
    plan = _plan(image, owner_id, secret_key, profile, semantic_features, reserve_rounding=True)
    geometry: _Geometry = plan["geometry"]
    channels = []
    for channel, name in enumerate(("semantic", "instance")):
        bit_of_slot, signs, norms = geometry.carriers[channel]
        frequencies = geometry.frequencies[channel]
        slots = [
            (slot // len(frequencies), *frequencies[slot % len(frequencies)], bit, sign, norms[bit])
            for slot, (bit, sign) in enumerate(zip(bit_of_slot, signs))
        ]
        channels.append({"channel": name, "slots": slots, "host": plan["host"][channel], "target": plan["targets"][channel]})
    return {
        "detector_config_id": plan["config"].hex(),
        "semantic_code": f"{plan['q']:08x}",
        "perceptual_hash": f"{plan['h']:08x}",
        "height": plan["height"],
        "width": plan["width"],
        "channels": channels,
    }


def embed_with_report(
    image: Sequence[Sequence[float]],
    owner_id: str,
    secret_key: bytes | str | None = None,
    profile: Mapping[str, object] | None = None,
    semantic_features: Sequence[float] | None = None,
    quantize: bool = True,
    strict: bool = True,
    reserve_rounding: bool | None = None,
) -> tuple[list[list[float]], dict[str, object]]:
    """Embed the dual-key payload and verify the result with the real detector.

    ``quantize`` rounds the output to integer luminance levels.
    ``reserve_rounding`` plans the signal with the budget that byte rounding
    leaves; it defaults to ``quantize`` and is set on its own by a caller that
    rounds later (:func:`embed_rgb`).  Further passes re-aim at the same
    targets; they matter only where clipping removed part of the change.  With
    ``strict`` a marked output that the detector does not accept as
    ``both_match`` raises :class:`EmbeddingError`; otherwise the failure is
    returned in the report so a study can keep it in its inventory.
    """
    if reserve_rounding is None:
        reserve_rounding = quantize
    plan = _plan(image, owner_id, secret_key, profile, semantic_features, bool(reserve_rounding))
    checked, geometry = plan["checked"], plan["geometry"]
    height, width = plan["height"], plan["width"]
    output = [[float(value) for value in row] for row in image]
    blocks_per_row = width // BLOCK
    most_clipped = 0
    coefficients = plan["coefficients"]
    for pass_index in range(int(checked["embedding"]["passes"])):
        if pass_index:
            coefficients = _analyse(output, geometry.analysis)[1]
        current = geometry.projections(coefficients)
        changes: list[list[float]] = [[] for _ in coefficients]
        for channel in (0, 1):
            bit_of_slot, signs, norms = geometry.carriers[channel]
            step = [(target - value) / norm for target, value, norm in zip(plan["targets"][channel], current[channel], norms)]
            per_block = len(geometry.frequencies[channel])
            for slot, (bit, sign) in enumerate(zip(bit_of_slot, signs)):
                changes[slot // per_block].append(step[bit] * sign)
        clipped = 0
        for block_index, block_changes in enumerate(changes):
            delta = [0.0] * 64
            for change, plane in zip(block_changes, geometry.planes):
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
        # The strip outside the last full block carries no mark but is part of the saved image.
        for y, row in enumerate(output):
            for x in range(0 if y >= (height // BLOCK) * BLOCK else blocks_per_row * BLOCK, width):
                row[x] = float(math.floor(row[x] + 0.5))
    result = detect(output, owner_id, secret_key, checked, semantic_features)
    error = mse(image, output)
    report = {
        "detector_config_id": plan["config"].hex(),
        "security": checked["security"],
        "semantic_source": checked["semantic_source"],
        "embedding_domain": "image",
        "revision": REVISION,
        "embedding": dict(checked["embedding"]),
        "decision_id": decision_id(checked),
        "semantic_code": f"{plan['q']:08x}",
        "perceptual_hash": f"{plan['h']:08x}",
        "psnr_db": psnr(image, output),
        "mse": error,
        "clipped_fraction": most_clipped / float(height * width),
        "quantized": bool(quantize),
        "rounding_reserved": bool(reserve_rounding),
        "semantic_channel": plan["channels"][0],
        "instance_channel": plan["channels"][1],
        "verification": result,
        "verified": result["outcome"] == "both_match",
        # With an external encoder the caller must repeat verification using
        # features recomputed from the saved marked image.
        "verification_features": "recomputed" if checked["semantic_source"] == PROXY_SOURCE else "source-features-supplied-by-caller",
    }
    if strict and not report["verified"]:
        raise EmbeddingError("marked output failed self-verification: " + str(result["outcome"]), report)
    return output, report


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


def _distance(left: int, right: int) -> int:
    return bin(left ^ right).count("1")


_STATUS_RANK = {"unchecked": 0, "match": 0, "uncertain": 1, "mismatch": 2}


def _content_status(distance: int, radius: int, far: int, checked: bool) -> str:
    """Compare a verified key's code with the code of the suspect image.

    Between ``radius`` and ``far`` the comparison abstains: heavy but harmless
    processing moves a few bits, and that must not read as a transferred mark.
    """
    if not checked:
        return "unchecked"
    if distance <= radius:
        return "match"
    return "mismatch" if distance >= far else "uncertain"


def _decide(s_found: bool, s_status: str | None, i_found: bool, i_status: str | None) -> tuple[str, str]:
    """Map the two key tests and their content statuses to (outcome, proposal_state).

    Only a key that was found has a status; the status of a key that was not
    found is ignored.
    """
    for found, status in ((s_found, s_status), (i_found, i_status)):
        if found and status not in _STATUS_RANK:
            raise ValueError("a found key needs a content status")
    if not s_found and not i_found:
        return "neither_match", "not_detected"
    if (s_found and s_status == "mismatch") or (i_found and i_status == "mismatch"):
        return "content_mismatch", "copy_paste"
    semantic_ok = s_found and _STATUS_RANK[s_status] == 0
    instance_ok = i_found and _STATUS_RANK[i_status] == 0
    if semantic_ok and instance_ok:
        return "both_match", "authentic"
    if semantic_ok and not i_found:
        return "semantic_only", "regenerated"
    if instance_ok and not s_found:
        return "instance_only", "unclassified"
    # A key was found whose code comparison is undecided.
    return "content_uncertain", "unclassified"


def _best(candidates: Sequence[tuple[str, int, int, Sequence[int]]], projections: Sequence[float]) -> tuple[float, str, int, int]:
    best = (-math.inf, "", 0, 0)
    for label, q, h, pattern in candidates:
        score = _correlation(pattern, projections)
        if score > best[0]:
            best = (score, label, q, h)
    return best


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

    Candidate keys are re-derived from the suspect image (the proposal's route)
    and, as a second candidate, from the content codes carried in the mark.  The
    second candidate is what makes a transferred mark observable: its key
    verifies while its codes disagree with the image that now carries it.

    ``outcome`` is the observation; ``proposal_state`` is the label the
    proposal's decision table assigns to it.  Neither is ground truth: whether
    an image was regenerated or forged is known only from attack provenance.

    ``binding_mode`` selects the content checks for ablation controls:
    ``combined`` (default), ``semantic_only``, ``perceptual_only`` or ``none``.
    ``roster_size`` is the number of OwnerIDs being tried on this image; the
    thresholds are corrected for it.
    """
    started = time.perf_counter()
    if binding_mode not in BINDING_MODES:
        raise ValueError("binding_mode must be one of " + ", ".join(BINDING_MODES))
    if isinstance(roster_size, bool) or not isinstance(roster_size, int) or not 1 <= roster_size <= MAX_ROSTER:
        raise ValueError(f"roster_size must be an integer in 1..{MAX_ROSTER}")
    checked, key, config = _resolve(profile, secret_key)
    if expected_config_id is not None and expected_config_id != config.hex():
        raise ValueError("detector configuration differs from the expected enrolment configuration")
    height, width = _check_image(image, int(checked["minimum_side"]))
    owner = canonical_owner(owner_id)
    decision = checked["decision"]
    target = float(decision["false_positive_target"])
    geometry = _Geometry(checked, key, config, owner, height, width)
    prepared = time.perf_counter()
    means, coefficients = _analyse(image, geometry.analysis)
    semantic, instance = geometry.projections(coefficients)
    transformed = time.perf_counter()
    q_now, h_now = _codes(means, coefficients, checked, key, config, semantic_features, binding=False)
    featured = time.perf_counter()

    q_read, q_check = _helper_decode(semantic[:HELPER_CHIPS])
    h_read, h_check = _helper_decode(instance[:HELPER_CHIPS])

    q_candidates = [("recomputed", q_now)] + ([("decoded", q_read)] if q_read != q_now else [])
    semantic_candidates = [(label, q, 0, derive_keys(q, 0, owner, key, config)[0]) for label, q in q_candidates]
    s_score, s_label, q_bound, _ = _best(semantic_candidates, semantic[HELPER_CHIPS:])
    s_threshold = _threshold(target, len(semantic_candidates) * roster_size)
    s_found = s_score >= s_threshold

    # Once the semantic key is found its code is the only one the instance key may use.
    q_for_instance = [(s_label, q_bound)] if s_found else q_candidates
    h_candidates = [("recomputed", h_now)] + ([("decoded", h_read)] if h_read != h_now else [])
    instance_candidates = [
        (h_label, q, h, derive_keys(q, h, owner, key, config)[1]) for _q_label, q in q_for_instance for h_label, h in h_candidates
    ]
    i_score, i_label, q_instance, h_bound = _best(instance_candidates, instance[HELPER_CHIPS:])
    i_threshold = _threshold(target, len(instance_candidates) * roster_size)
    i_found = i_score >= i_threshold

    s_distance = _distance(q_bound, q_now) if s_found else None
    i_distance = _distance(h_bound, h_now) if i_found else None
    check_semantic = binding_mode in ("combined", "semantic_only")
    check_instance = binding_mode in ("combined", "perceptual_only")
    semantic_limits = (int(decision["semantic_radius"]), int(decision["semantic_mismatch_distance"]), check_semantic)
    instance_limits = (int(decision["instance_radius"]), int(decision["instance_mismatch_distance"]), check_instance)
    s_status = _content_status(s_distance, *semantic_limits) if s_found else None
    # The instance key binds both codes, so it inherits the worse of the two comparisons.
    i_status = (
        max(_content_status(i_distance, *instance_limits), _content_status(_distance(q_instance, q_now), *semantic_limits), key=_STATUS_RANK.get)
        if i_found
        else None
    )
    semantic_ok = s_found and _STATUS_RANK[s_status] == 0
    instance_ok = i_found and _STATUS_RANK[i_status] == 0
    outcome, state = _decide(s_found, s_status, i_found, i_status)
    finished = time.perf_counter()
    return {
        "outcome": outcome,
        "proposal_state": state,
        "present": outcome == "both_match",
        "watermark_found": bool(s_found or i_found),
        "semantic": {
            "score": s_score,
            "threshold": s_threshold,
            "found": bool(s_found),
            "candidates": len(semantic_candidates),
            "candidate": s_label if s_found else None,
            "log10_false_positive_bound": _log10_bound(s_score, len(semantic_candidates) * roster_size),
            "code_distance": s_distance,
            "content_status": s_status,
            "content_match": bool(semantic_ok),
            "helper_check_ok": bool(q_check),
        },
        "instance": {
            "score": i_score,
            "threshold": i_threshold,
            "found": bool(i_found),
            "candidates": len(instance_candidates),
            "candidate": i_label if i_found else None,
            "log10_false_positive_bound": _log10_bound(i_score, len(instance_candidates) * roster_size),
            "code_distance": i_distance,
            "content_status": i_status,
            "content_match": bool(instance_ok),
            "helper_check_ok": bool(h_check),
        },
        "semantic_code": f"{q_now:08x}",
        "perceptual_hash": f"{h_now:08x}",
        "binding_mode": binding_mode,
        "owner_id": owner.decode("utf-8"),
        "owners_tested": roster_size,
        "candidates_tested": len(semantic_candidates) + len(instance_candidates),
        "security": checked["security"],
        "semantic_source": checked["semantic_source"],
        "embedding_domain": "image",
        "detector_config_id": config.hex(),
        "decision_id": decision_id(checked),
        "version": VERSION,
        "height": height,
        "width": width,
        "revision": REVISION,
        # setup: input checks and carrier derivation; transform: block DCT and projections.
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
        "roster_sha256": hashlib.sha256(_pack(*(owner.encode("utf-8") for owner in roster))).hexdigest(),
        "found": [owner for owner, result in results.items() if result["watermark_found"]],
        "both_match": [owner for owner, result in results.items() if result["outcome"] == "both_match"],
        "results": results,
    }


# ---------------------------------------------------------------------------
# Colour wrapper and quality helpers
# ---------------------------------------------------------------------------


def luminance_from_rgb(rgb: Sequence[Sequence[Sequence[float]]]) -> list[list[float]]:
    """sRGB luma Y = 0.299 R + 0.587 G + 0.114 B without gamma linearisation."""
    luma = [[0.299 * float(r) + 0.587 * float(g) + 0.114 * float(b) for r, g, b in row] for row in rgb]
    if any(not 0.0 <= float(channel) <= 255.0 for row in rgb for pixel in row for channel in pixel):
        raise ValueError("RGB channel values must be in [0, 255]")
    return luma


def embed_rgb(
    rgb: Sequence[Sequence[Sequence[float]]],
    owner_id: str,
    secret_key: bytes | str | None = None,
    profile: Mapping[str, object] | None = None,
    semantic_features: Sequence[float] | None = None,
    strict: bool = True,
) -> tuple[list[list[tuple[int, int, int]]], dict[str, object]]:
    """Mark a colour image: add the luminance change to R, G and B, then round to bytes.

    The returned report verifies the rounded RGB output itself, not the
    intermediate floating-point luminance.  The signal is planned with the
    budget that the rounding of the three channels leaves: for integer input
    they round alike, so the luminance loses the same 1/12 as a rounded
    luminance image.
    """
    source = luminance_from_rgb(rgb)
    marked, report = embed_with_report(
        source, owner_id, secret_key, profile, semantic_features, quantize=False, strict=False, reserve_rounding=True
    )
    clipped = 0
    output = []
    for row, source_row, marked_row in zip(rgb, source, marked):
        output_row = []
        for pixel, before, after in zip(row, source_row, marked_row):
            values = [math.floor(float(channel) + after - before + 0.5) for channel in pixel]
            clipped += sum(value < 0 or value > 255 for value in values)
            output_row.append(tuple(int(min(255, max(0, value))) for value in values))
        output.append(output_row)
    saved = luminance_from_rgb(output)
    result = detect(saved, owner_id, secret_key, profile, semantic_features)
    error = mse(source, saved)
    report.update(
        {
            "verification": result,
            "verified": result["outcome"] == "both_match",
            "quantized": True,
            # A channel at 0 or 255 cannot take its share of the luminance change.
            "clipped_fraction": clipped / (3.0 * len(source) * len(source[0])),
            "mse": error,
            "psnr_db": psnr(source, saved),
            "quality_domain": "luminance of the rounded RGB output",
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
    luma = luminance_from_rgb(rgb)
    return detect(luma, owner_id, secret_key, profile, semantic_features, binding_mode, roster_size, expected_config_id)


def mse(left: Sequence[Sequence[float]], right: Sequence[Sequence[float]]) -> float:
    """Mean squared error between two images of the same shape."""
    if len(left) != len(right) or any(len(a) != len(b) for a, b in zip(left, right)):
        raise ValueError("image shapes differ")
    values = [(float(a) - float(b)) ** 2 for row_a, row_b in zip(left, right) for a, b in zip(row_a, row_b)]
    return sum(values) / len(values)


def psnr(left: Sequence[Sequence[float]], right: Sequence[Sequence[float]]) -> float | None:
    """PSNR in dB for an 8-bit range, or ``None`` when the images are identical."""
    error = mse(left, right)
    return None if error == 0.0 else 10.0 * math.log10(255.0**2 / error)
