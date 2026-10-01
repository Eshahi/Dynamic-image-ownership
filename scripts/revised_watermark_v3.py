"""Keyed, error-correcting image-domain DCT-QIM candidate (revision v3).

This module is an engineering successor to ``revised_watermark.py``.  The
previous v2 candidate remains intact for reproducibility of historical runs.
The v3 candidate addresses four observed weaknesses without claiming latent,
regeneration, semantic, or legal-ownership evidence:

* the owner tag is keyed with HMAC-SHA256;
* the payload uses SECDED(8,4) codewords and deterministic interleaving;
* the instance binding is widened to 32 bits;
* detection reports weighted margins and explicit admissibility/rejection
  reasons instead of treating owner vote agreement as confidence.

The carrier is still a fixed-grid luminance DCT-QIM codec. Crop, resize,
rotation, and generative regeneration remain separate, unclaimed attack
conditions until a new approved experiment is run.
"""

from __future__ import annotations

import hashlib
import hmac
import math
import unicodedata
from typing import Mapping, Sequence


MAGIC = b"rw-v3"
VERSION = 3
MIN_SIDE = 160
MIN_DYNAMIC_RANGE = 8.0
CLIP_TOLERANCE = 8.0
FREQUENCIES = ((1, 2), (2, 1), (2, 2), (1, 3), (3, 1), (2, 3))
OWNER_BITS = 64
BINDING_BITS = 32
RAW_PAYLOAD_BITS = 4 + OWNER_BITS + BINDING_BITS + 8
CODE_BITS = ((RAW_PAYLOAD_BITS + 3) // 4) * 8
REPETITION_FLOOR = 3
BINDING_DELTA = 1.0
LOCAL_STD_TARGET = 8.0
MIN_LOCAL_VARIANCE = 4.0

DEFAULT_PROFILE = {
    "schema_version": "revised-watermark-v3",
    "profile": "image-domain-dct-qim-keyed-weighted",
    "qim_step": 4.0,
    "minimum_side": MIN_SIDE,
    "minimum_dynamic_range": MIN_DYNAMIC_RANGE,
    "clip_tolerance": CLIP_TOLERANCE,
    "repetition_floor": REPETITION_FLOOR,
    "frequencies": [list(pair) for pair in FREQUENCIES],
    "owner_bits": OWNER_BITS,
    "binding_bits": BINDING_BITS,
    "security": "hmac-sha256",
    "thresholds": {
        "owner_accuracy": 0.75,
        "instance_accuracy": 0.75,
        "confidence": 0.65,
    },
}

_DCT_BASIS = tuple(
    tuple(
        (math.sqrt(1.0 / 8.0) if u == 0 else 0.5)
        * math.cos((2 * n + 1) * u * math.pi / 16.0)
        for n in range(8)
    )
    for u in range(8)
)


def _check_image(image: Sequence[Sequence[float]]) -> tuple[int, int]:
    height = len(image)
    width = len(image[0]) if height else 0
    if height < MIN_SIDE or width < MIN_SIDE:
        raise ValueError(f"image must be at least {MIN_SIDE}x{MIN_SIDE}")
    if any(len(row) != width for row in image):
        raise ValueError("image rows must have equal length")
    for row in image:
        for value in row:
            value = float(value)
            if not math.isfinite(value) or not 0.0 <= value <= 255.0:
                raise ValueError("image values must be finite RGB/luminance bytes")
    return height, width


def canonical_owner(owner_id: str) -> bytes:
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


def validate_profile(profile: Mapping[str, object]) -> dict[str, object]:
    if profile.get("schema_version") != DEFAULT_PROFILE["schema_version"]:
        raise ValueError("unsupported revised watermark profile")
    if profile.get("profile") != DEFAULT_PROFILE["profile"]:
        raise ValueError("unsupported revised watermark profile")
    for key in (
        "minimum_side",
        "minimum_dynamic_range",
        "clip_tolerance",
        "repetition_floor",
        "frequencies",
        "owner_bits",
        "binding_bits",
        "security",
    ):
        if profile.get(key) != DEFAULT_PROFILE[key]:
            raise ValueError(f"profile constant mismatch: {key}")
    step = profile.get("qim_step")
    if not isinstance(step, (int, float)) or not math.isfinite(float(step)) or not 0 < float(step) <= 32:
        raise ValueError("qim_step must be in (0, 32]")
    thresholds = profile.get("thresholds")
    if not isinstance(thresholds, Mapping):
        raise ValueError("thresholds must be an object")
    for key in ("owner_accuracy", "instance_accuracy", "confidence"):
        value = thresholds.get(key)
        if not isinstance(value, (int, float)) or not 0.5 <= float(value) <= 1:
            raise ValueError(f"threshold {key} must be in [0.5, 1]")
    return dict(profile)


def _bits_from_int(value: int, width: int) -> list[int]:
    return [(value >> (width - 1 - i)) & 1 for i in range(width)]


def _bits_to_bytes(bits: Sequence[int]) -> bytes:
    if len(bits) % 8:
        raise ValueError("bit length must be a multiple of eight")
    result = bytearray()
    for start in range(0, len(bits), 8):
        byte = 0
        for bit in bits[start : start + 8]:
            byte = (byte << 1) | int(bit)
        result.append(byte)
    return bytes(result)


def _crc8(data: bytes) -> int:
    value = 0
    for byte in data:
        value ^= byte
        for _ in range(8):
            value = ((value << 1) ^ 0x07) & 0xFF if value & 0x80 else (value << 1) & 0xFF
    return value


def _owner_tag(owner: bytes, binding: int, secret_key: bytes) -> bytes:
    # Bind the authenticated owner tag to the enrolled image descriptor.
    message = MAGIC + b"/owner-instance/" + owner + binding.to_bytes(BINDING_BITS // 8, "big")
    return hmac.new(secret_key, message, hashlib.sha256).digest()[: OWNER_BITS // 8]


def _carrier_sign(height: int, width: int, block_y: int, block_x: int, frequency_index: int, code_index: int) -> int:
    material = (
        b"/carrier/"
        + height.to_bytes(4, "big")
        + width.to_bytes(4, "big")
        + block_y.to_bytes(4, "big")
        + block_x.to_bytes(4, "big")
        + frequency_index.to_bytes(2, "big")
        + code_index.to_bytes(4, "big")
    )
    return 1 if hashlib.sha256(MAGIC + material).digest()[0] & 1 else -1


def _slot_permutation(height: int, width: int, count: int) -> list[int]:
    seed = MAGIC + b"/interleave/" + height.to_bytes(4, "big") + width.to_bytes(4, "big")
    return sorted(
        range(count),
        key=lambda index: hashlib.sha256(seed + index.to_bytes(4, "big")).digest(),
    )


def _nearest_integer(value: float) -> int:
    return math.floor(value + 0.5)


def _qim_embed(coefficient: float, bit: int, carrier: int, step: float) -> float:
    target = int(bit) ^ (1 if carrier < 0 else 0)
    nearest = _nearest_integer(coefficient / step)
    if (nearest & 1) == target:
        return nearest * step
    lower, upper = nearest - 1, nearest + 1
    chosen = lower if abs(coefficient / step - lower) <= abs(coefficient / step - upper) else upper
    return chosen * step


def _qim_read(coefficient: float, carrier: int, step: float) -> int:
    return (_nearest_integer(coefficient / step) & 1) ^ (1 if carrier < 0 else 0)


def _dct8(block: Sequence[Sequence[float]]) -> list[list[float]]:
    intermediate = [
        [sum(_DCT_BASIS[u][y] * float(block[y][x]) for y in range(8)) for x in range(8)]
        for u in range(8)
    ]
    return [
        [sum(intermediate[u][x] * _DCT_BASIS[v][x] for x in range(8)) for v in range(8)]
        for u in range(8)
    ]


def _idct8(coefficients: Sequence[Sequence[float]]) -> list[list[float]]:
    # First restore the horizontal-frequency axis, then the spatial axis.
    # Keeping the second frequency index in ``intermediate`` is essential;
    # summing over it too early breaks the orthonormal inverse transform.
    intermediate = [
        [sum(_DCT_BASIS[u][y] * float(coefficients[u][v]) for u in range(8)) for v in range(8)]
        for y in range(8)
    ]
    return [
        [sum(intermediate[y][v] * _DCT_BASIS[v][x] for v in range(8)) for x in range(8)]
        for y in range(8)
    ]


def _padded(image: Sequence[Sequence[float]]) -> tuple[list[list[float]], int, int]:
    height, width = len(image), len(image[0])
    padded_height = ((height + 7) // 8) * 8
    padded_width = ((width + 7) // 8) * 8
    padded = []
    for y in range(padded_height):
        source_y = min(y, height - 1)
        padded.append([float(image[source_y][min(x, width - 1)]) for x in range(padded_width)])
    return padded, padded_height, padded_width


def _block_variance(block: Sequence[Sequence[float]]) -> float:
    values = [float(value) for row in block for value in row]
    mean = sum(values) / len(values)
    return sum((value - mean) ** 2 for value in values) / len(values)


def perceptual_bits(image: Sequence[Sequence[float]], bits: int = BINDING_BITS) -> int:
    """Return a wider low-frequency block-order binding diagnostic."""
    if bits <= 0 or bits > 64:
        raise ValueError("bits must be in 1..64")
    padded, padded_height, padded_width = _padded(image)
    means: list[float] = []
    for by in range(0, padded_height, 8):
        for bx in range(0, padded_width, 8):
            means.append(sum(padded[by + y][bx + x] for y in range(8) for x in range(8)) / 64.0)
    count = len(means)
    value = 0
    for index in range(bits):
        left = (index * 53 + 11) % count
        right = (index * 97 + 29) % count
        if right == left:
            right = (right + 1) % count
        value = (value << 1) | int(means[left] > means[right] + BINDING_DELTA)
    return value


def _hamming84_encode(bits: Sequence[int]) -> list[int]:
    if len(bits) % 4:
        raise ValueError("SECDED(8,4) input must be divisible by four")
    encoded: list[int] = []
    for start in range(0, len(bits), 4):
        d1, d2, d3, d4 = (int(bit) & 1 for bit in bits[start : start + 4])
        p1 = d1 ^ d2 ^ d4
        p2 = d1 ^ d3 ^ d4
        p4 = d2 ^ d3 ^ d4
        p0 = p1 ^ p2 ^ d1 ^ p4 ^ d2 ^ d3 ^ d4
        encoded.extend([p1, p2, d1, p4, d2, d3, d4, p0])
    return encoded


def _hamming84_decode(bits: Sequence[int]) -> tuple[list[int], int, int]:
    if len(bits) % 8:
        raise ValueError("SECDED(8,4) input must be divisible by eight")
    decoded: list[int] = []
    corrected = 0
    uncorrectable = 0
    for start in range(0, len(bits), 8):
        code = [int(bit) & 1 for bit in bits[start : start + 8]]
        syndrome = (
            (code[0] ^ code[2] ^ code[4] ^ code[6])
            | ((code[1] ^ code[2] ^ code[5] ^ code[6]) << 1)
            | ((code[3] ^ code[4] ^ code[5] ^ code[6]) << 2)
        )
        parity = sum(code) & 1
        if syndrome and parity:
            code[syndrome - 1] ^= 1
            corrected += 1
        elif syndrome and not parity:
            uncorrectable += 1
        elif not syndrome and parity:
            code[7] ^= 1
            corrected += 1
        decoded.extend([code[2], code[4], code[5], code[6]])
    return decoded, corrected, uncorrectable


def _payload_bits(owner_id: str, image: Sequence[Sequence[float]], secret_key: bytes) -> list[int]:
    owner = canonical_owner(owner_id)
    binding = perceptual_bits(image, BINDING_BITS)
    owner_tag = _owner_tag(owner, binding, secret_key)
    body = bytes([VERSION]) + owner_tag + binding.to_bytes(BINDING_BITS // 8, "big")
    return (
        _bits_from_int(VERSION, 4)
        + _bits_from_int(int.from_bytes(owner_tag, "big"), OWNER_BITS)
        + _bits_from_int(binding, BINDING_BITS)
        + _bits_from_int(_crc8(body), 8)
    )


def payload_bits(owner_id: str, image: Sequence[Sequence[float]], secret_key: bytes | str) -> list[int]:
    """Return the raw keyed payload before SECDED coding."""
    return _payload_bits(owner_id, image, canonical_secret_key(secret_key))


def _slot_records(image: Sequence[Sequence[float]]) -> tuple[list[list[float]], int, int, list[dict[str, object]]]:
    padded, padded_height, padded_width = _padded(image)
    height, width = len(image), len(image[0])
    records: list[dict[str, object]] = []
    slot_number = 0
    for by in range(0, padded_height, 8):
        for bx in range(0, padded_width, 8):
            block = [row[bx : bx + 8] for row in padded[by : by + 8]]
            coeff = _dct8(block)
            variance = _block_variance(block)
            for frequency_index, (u, v) in enumerate(FREQUENCIES):
                records.append(
                    {
                        "slot": slot_number,
                        "block": (by // 8, bx // 8),
                        "frequency": frequency_index,
                        "u": u,
                        "v": v,
                        "coefficient": coeff[u][v],
                        "variance": variance,
                    }
                )
                slot_number += 1
    return padded, padded_height, padded_width, records


def _slot_code_indices(height: int, width: int, count: int) -> dict[int, int]:
    permutation = _slot_permutation(height, width, count)
    return {physical_slot: rank % CODE_BITS for rank, physical_slot in enumerate(permutation)}


def embed(
    image: Sequence[Sequence[float]],
    owner_id: str,
    secret_key: bytes | str,
    strength: float = 4.0,
    profile: Mapping[str, object] | None = None,
) -> list[list[float]]:
    """Embed a keyed, SECDED-coded owner/content payload."""
    height, width = _check_image(image)
    key = canonical_secret_key(secret_key)
    dynamic_range = max(float(value) for row in image for value in row) - min(float(value) for row in image for value in row)
    if dynamic_range < MIN_DYNAMIC_RANGE:
        raise ValueError("embedding requires at least 8 luminance levels of source headroom")
    if profile is not None:
        checked = validate_profile(profile)
        strength = float(checked["qim_step"])
    if not math.isfinite(strength) or not 0 < strength <= 32:
        raise ValueError("QIM step must be finite and positive")

    raw = _payload_bits(owner_id, image, key)
    coded = _hamming84_encode(raw)
    padded, padded_height, padded_width, records = _slot_records(image)
    if len(records) < len(coded) * REPETITION_FLOOR:
        raise ValueError("image has insufficient DCT slots for the error-correcting payload")
    code_index_by_slot = _slot_code_indices(height, width, len(records))
    block_coefficients: dict[tuple[int, int], list[list[float]]] = {}
    for record in records:
        block = record["block"]
        if block not in block_coefficients:
            by, bx = block
            block_coefficients[block] = _dct8([row[bx * 8 : bx * 8 + 8] for row in padded[by * 8 : by * 8 + 8]])
        code_index = code_index_by_slot[int(record["slot"])]
        by, bx = block
        carrier = _carrier_sign(height, width, by, bx, int(record["frequency"]), code_index)
        block_coefficients[block][int(record["u"])][int(record["v"])] = _qim_embed(
            float(record["coefficient"]), coded[code_index], carrier, strength
        )
    for (block_y, block_x), coeff in block_coefficients.items():
        restored = _idct8(coeff)
        if any(value < -CLIP_TOLERANCE or value > 255.0 + CLIP_TOLERANCE for row in restored for value in row):
            raise ValueError("embedding would clip a block; source is outside the admissible luminance headroom")
        for y in range(8):
            for x in range(8):
                if block_y * 8 + y < height and block_x * 8 + x < width:
                    padded[block_y * 8 + y][block_x * 8 + x] = min(255.0, max(0.0, restored[y][x]))
    return [row[:width] for row in padded[:height]]


def detect(
    image: Sequence[Sequence[float]],
    owner_id: str,
    secret_key: bytes | str,
    strength: float = 4.0,
    owner_threshold: float = 0.75,
    instance_threshold: float = 0.75,
    confidence_threshold: float = 0.65,
    profile: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Decode the keyed payload and return auditable diagnostics."""
    height, width = _check_image(image)
    key = canonical_secret_key(secret_key)
    if profile is not None:
        checked = validate_profile(profile)
        strength = float(checked["qim_step"])
        thresholds = checked["thresholds"]
        owner_threshold = float(thresholds["owner_accuracy"])
        instance_threshold = float(thresholds["instance_accuracy"])
        confidence_threshold = float(thresholds["confidence"])
    if strength <= 0 or not math.isfinite(strength) or strength > 32:
        raise ValueError("QIM step must be finite and positive")
    if not (0.5 <= owner_threshold <= 1 and 0.5 <= instance_threshold <= 1 and 0.5 <= confidence_threshold <= 1):
        raise ValueError("decision thresholds must be in [0.5, 1]")

    padded, padded_height, padded_width, records = _slot_records(image)
    if len(records) < len(_hamming84_encode([0] * RAW_PAYLOAD_BITS)) * REPETITION_FLOOR:
        raise ValueError("image has insufficient DCT slots for the error-correcting payload")
    code_index_by_slot = _slot_code_indices(height, width, len(records))
    votes = [[0.0, 0.0] for _ in range(CODE_BITS)]
    for record in records:
        code_index = code_index_by_slot[int(record["slot"])]
        by, bx = record["block"]
        carrier = _carrier_sign(height, width, by, bx, int(record["frequency"]), code_index)
        observed = _qim_read(float(record["coefficient"]), carrier, strength)
        variance_weight = min(1.0, math.sqrt(float(record["variance"])) / LOCAL_STD_TARGET)
        coefficient_weight = min(1.0, abs(float(record["coefficient"])) / max(1.0, strength * 2.0))
        weight = 0.25 + 0.75 * variance_weight * max(0.25, coefficient_weight)
        votes[code_index][observed] += weight

    code_bits = [int(pair[1] >= pair[0]) for pair in votes]
    code_margins = [abs(pair[1] - pair[0]) / (sum(pair) or 1.0) for pair in votes]
    raw_bits, corrected_codewords, uncorrectable_codewords = _hamming84_decode(code_bits)
    version = sum(raw_bits[index] << (3 - index) for index in range(4))
    owner_start, owner_end = 4, 4 + OWNER_BITS
    binding_start, binding_end = owner_end, owner_end + BINDING_BITS
    crc_start = binding_end
    decoded_owner = _bits_to_bytes(raw_bits[owner_start:owner_end])
    decoded_binding = sum(raw_bits[index] << (binding_end - 1 - index) for index in range(binding_start, binding_end))
    body = bytes([version]) + decoded_owner + decoded_binding.to_bytes(BINDING_BITS // 8, "big")
    crc_ok = _bits_to_bytes(raw_bits[crc_start : crc_start + 8])[0] == _crc8(body)
    observed_binding = perceptual_bits(image, BINDING_BITS)
    # Authenticate the claimed owner against the descriptor of the image being
    # verified. A copied payload therefore fails when the current image's
    # binding differs from the enrolled source.
    expected_owner = _owner_tag(canonical_owner(owner_id), observed_binding, key)
    expected_owner_bits = _bits_from_int(int.from_bytes(expected_owner, "big"), OWNER_BITS)
    decoded_owner_bits = raw_bits[owner_start:owner_end]
    owner_accuracy = sum(a == b for a, b in zip(decoded_owner_bits, expected_owner_bits)) / OWNER_BITS
    binding_distance = (decoded_binding ^ observed_binding).bit_count()
    instance_accuracy = 1.0 - binding_distance / BINDING_BITS

    raw_margins = []
    owner_margins = []
    for raw_index in range(RAW_PAYLOAD_BITS):
        data_offset = raw_index % 4
        data_index = (raw_index // 4) * 8 + (2, 4, 5, 6)[data_offset]
        raw_margins.append(code_margins[data_index])
    owner_payload_offset = owner_start
    for raw_index in range(owner_payload_offset, owner_end):
        data_offset = raw_index % 4
        data_index = (raw_index // 4) * 8 + (2, 4, 5, 6)[data_offset]
        owner_margins.append(code_margins[data_index])
    owner_margin = sum(owner_margins) / len(owner_margins)
    weighted_margin = sum(raw_margins) / len(raw_margins)
    dynamic_range = max(float(value) for row in image for value in row) - min(float(value) for row in image for value in row)
    block_count = len(records) // len(FREQUENCIES)
    eligible_blocks = sum(1 for record in records[:: len(FREQUENCIES)] if float(record["variance"]) >= MIN_LOCAL_VARIANCE)
    eligible_fraction = eligible_blocks / max(1, block_count)
    admissible = dynamic_range >= MIN_DYNAMIC_RANGE and eligible_fraction >= 0.25
    confidence = min(owner_margin, owner_accuracy, instance_accuracy, weighted_margin)
    present = (
        admissible
        and version == VERSION
        and uncorrectable_codewords == 0
        and crc_ok
        and owner_accuracy >= owner_threshold
        and instance_accuracy >= instance_threshold
        and confidence >= confidence_threshold
    )
    reason = "accepted" if present else "rejected"
    if not admissible:
        reason = "inadmissible_dynamic_range"
    elif uncorrectable_codewords:
        reason = "uncorrectable_ecc"
    elif version != VERSION:
        reason = "version_mismatch"
    elif not crc_ok:
        reason = "crc_mismatch"
    elif owner_accuracy < owner_threshold:
        reason = "owner_threshold"
    elif instance_accuracy < instance_threshold:
        reason = "instance_threshold"
    elif confidence < confidence_threshold:
        reason = "confidence_threshold"
    return {
        "present": present,
        "version": version,
        "crc_ok": crc_ok,
        "ecc_ok": uncorrectable_codewords == 0,
        "corrected_codewords": corrected_codewords,
        "uncorrectable_codewords": uncorrectable_codewords,
        "owner_accuracy": owner_accuracy,
        "instance_accuracy": instance_accuracy,
        "owner_margin": owner_margin,
        "weighted_margin": weighted_margin,
        "confidence": confidence,
        "binding_distance": binding_distance,
        "payload_bits": RAW_PAYLOAD_BITS,
        "coded_bits": CODE_BITS,
        "interleaved": True,
        "security": "hmac-sha256",
        "admissible": admissible,
        "dynamic_range": dynamic_range,
        "eligible_block_fraction": eligible_fraction,
        "rejection_reason": reason,
        "height": height,
        "width": width,
    }


def mse(left: Sequence[Sequence[float]], right: Sequence[Sequence[float]]) -> float:
    if len(left) != len(right) or any(len(a) != len(b) for a, b in zip(left, right)):
        raise ValueError("image shapes differ")
    values = [(float(a) - float(b)) ** 2 for row_a, row_b in zip(left, right) for a, b in zip(row_a, row_b)]
    return sum(values) / len(values)
