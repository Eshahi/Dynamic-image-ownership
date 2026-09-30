"""A dependency-free, image-domain watermark candidate (revision v2).

The implementation is intentionally small and deterministic. It is a positive
control and a runnable replacement candidate for the unimplemented latent-to-DCT
bridge; it is not evidence of regeneration robustness or ownership.
The carrier is a public deterministic, repeated DCT-QIM code. QIM is used instead of trying
to infer a weak latent-to-image correlation from a shared random seed.
"""

from __future__ import annotations

import hashlib
import json
import math
import unicodedata
from pathlib import Path
from typing import Mapping, Sequence


MAGIC = b"rw-v2"
VERSION = 2
REPETITIONS = 3
MIN_SIDE = 160
MIN_DYNAMIC_RANGE = 8.0
CLIP_TOLERANCE = 8.0
FREQUENCIES = ((1, 2), (2, 1), (2, 2), (1, 3), (3, 1), (2, 3))
OWNER_BITS = 48
BINDING_BITS = 12
PAYLOAD_BITS = 4 + OWNER_BITS + BINDING_BITS + 8
DEFAULT_PROFILE = {
    "schema_version": "revised-watermark-v2",
    "profile": "image-domain-dct-qim-public-owner",
    "qim_step": 4.0,
    "minimum_side": MIN_SIDE,
    "minimum_dynamic_range": MIN_DYNAMIC_RANGE,
    "clip_tolerance": CLIP_TOLERANCE,
    "repetition_floor": REPETITIONS,
    "frequencies": [list(pair) for pair in FREQUENCIES],
    "owner_bits": OWNER_BITS,
    "binding_bits": BINDING_BITS,
    "thresholds": {"owner_accuracy": 0.75, "instance_accuracy": 0.75, "confidence": 0.65},
}
_DCT_BASIS = tuple(
    tuple((math.sqrt(1.0 / 8.0) if u == 0 else 0.5) * math.cos((2 * n + 1) * u * math.pi / 16.0) for n in range(8))
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
            if not math.isfinite(float(value)) or not 0.0 <= float(value) <= 255.0:
                raise ValueError("image values must be finite RGB/luminance bytes")
    return height, width


def canonical_owner(owner_id: str) -> bytes:
    value = unicodedata.normalize("NFC", owner_id).encode("utf-8")
    if not 1 <= len(value) <= 256:
        raise ValueError("OwnerID must contain 1..256 UTF-8 bytes")
    return value


def validate_profile(profile: Mapping[str, object]) -> dict[str, object]:
    """Validate the executable subset of revised-watermark.schema.json."""
    if profile.get("schema_version") != DEFAULT_PROFILE["schema_version"] or profile.get("profile") != DEFAULT_PROFILE["profile"]:
        raise ValueError("unsupported revised watermark profile")
    if profile.get("minimum_side") != MIN_SIDE or profile.get("minimum_dynamic_range") != MIN_DYNAMIC_RANGE or profile.get("clip_tolerance") != CLIP_TOLERANCE or profile.get("repetition_floor") != REPETITIONS:
        raise ValueError("profile geometry/repetition constants do not match implementation")
    if profile.get("frequencies") != DEFAULT_PROFILE["frequencies"] or profile.get("owner_bits") != OWNER_BITS or profile.get("binding_bits") != BINDING_BITS:
        raise ValueError("profile payload or frequency constants do not match implementation")
    step = profile.get("qim_step")
    thresholds = profile.get("thresholds")
    if not isinstance(step, (int, float)) or not math.isfinite(float(step)) or not 0 < float(step) <= 32:
        raise ValueError("qim_step must be in (0, 32]")
    if not isinstance(thresholds, Mapping):
        raise ValueError("thresholds must be an object")
    for key in ("owner_accuracy", "instance_accuracy", "confidence"):
        value = thresholds.get(key)
        if not isinstance(value, (int, float)) or not 0.5 <= float(value) <= 1:
            raise ValueError(f"threshold {key} must be in [0.5, 1]")
    return dict(profile)


def load_profile(path: str | Path) -> dict[str, object]:
    return validate_profile(json.loads(Path(path).read_text(encoding="utf-8")))


def _bits_from_int(value: int, width: int) -> list[int]:
    return [(value >> (width - 1 - i)) & 1 for i in range(width)]


def _bits_to_bytes(bits: Sequence[int]) -> bytes:
    if len(bits) % 8:
        raise ValueError("bit length must be a multiple of eight")
    output = bytearray()
    for offset in range(0, len(bits), 8):
        byte = 0
        for bit in bits[offset : offset + 8]:
            byte = (byte << 1) | int(bit)
        output.append(byte)
    return bytes(output)


def _crc8(data: bytes) -> int:
    value = 0
    for byte in data:
        value ^= byte
        for _ in range(8):
            value = ((value << 1) ^ 0x07) & 0xFF if value & 0x80 else (value << 1) & 0xFF
    return value


def _owner_tag(owner: bytes) -> bytes:
    return hashlib.sha256(MAGIC + b"/owner/" + owner).digest()[: OWNER_BITS // 8]


def _carrier_sign(height: int, width: int, block_y: int, block_x: int, frequency_index: int, payload_index: int = -1) -> int:
    material = b"/carrier/" + height.to_bytes(4, "big") + width.to_bytes(4, "big")
    material += block_y.to_bytes(4, "big") + block_x.to_bytes(4, "big")
    material += frequency_index.to_bytes(2, "big")
    material += payload_index.to_bytes(2, "big", signed=True)
    return 1 if hashlib.sha256(MAGIC + material).digest()[0] & 1 else -1


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
    intermediate = [[sum(_DCT_BASIS[u][y] * float(block[y][x]) for y in range(8)) for x in range(8)] for u in range(8)]
    return [[sum(intermediate[u][x] * _DCT_BASIS[v][x] for x in range(8)) for v in range(8)] for u in range(8)]


def _idct8(coefficients: Sequence[Sequence[float]]) -> list[list[float]]:
    intermediate = [[sum(_DCT_BASIS[u][y] * float(coefficients[u][v]) for u in range(8)) for v in range(8)] for y in range(8)]
    return [[sum(intermediate[y][v] * _DCT_BASIS[v][x] for v in range(8)) for x in range(8)] for y in range(8)]


def perceptual_bits(image: Sequence[Sequence[float]]) -> int:
    """Return a 16-bit block-mean binding invariant to non-DC DCT edits."""
    padded, padded_height, padded_width = _padded(image)
    block_means = []
    for by in range(0, padded_height, 8):
        for bx in range(0, padded_width, 8):
            block_means.append(sum(padded[by + y][bx + x] for y in range(8) for x in range(8)) / 64.0)
    count = len(block_means)
    value = 0
    for index in range(16):
        left = (index * 37) % count
        right = (left + 17) % count
        value = (value << 1) | int(block_means[left] > block_means[right] + 1.0)
    return value


def payload_bits(owner_id: str, image: Sequence[Sequence[float]]) -> list[int]:
    owner = canonical_owner(owner_id)
    binding = perceptual_bits(image)
    binding_value = binding >> (16 - BINDING_BITS)
    body = bytes([VERSION]) + _owner_tag(owner) + binding_value.to_bytes(2, "big")
    return _bits_from_int(VERSION, 4) + list(_bits_from_int(int.from_bytes(_owner_tag(owner), "big"), OWNER_BITS)) + _bits_from_int(binding_value, BINDING_BITS) + _bits_from_int(_crc8(body), 8)


def _padded(image: Sequence[Sequence[float]]) -> tuple[list[list[float]], int, int]:
    height, width = len(image), len(image[0])
    padded_height = ((height + 7) // 8) * 8
    padded_width = ((width + 7) // 8) * 8
    output = []
    for y in range(padded_height):
        source_y = min(y, height - 1)
        output.append([float(image[source_y][min(x, width - 1)]) for x in range(padded_width)])
    return output, padded_height, padded_width


def _read_slots(image: Sequence[Sequence[float]]) -> tuple[list[tuple[int, float, int]], int, int]:
    padded, padded_height, padded_width = _padded(image)
    height, width = len(image), len(image[0])
    slots: list[tuple[int, float, int]] = []
    for by in range(0, padded_height, 8):
        for bx in range(0, padded_width, 8):
            block = [row[bx : bx + 8] for row in padded[by : by + 8]]
            coeff = _dct8(block)
            for frequency_index, (u, v) in enumerate(FREQUENCIES):
                slots.append((frequency_index, coeff[u][v], _carrier_sign(height, width, by // 8, bx // 8, frequency_index)))
    return slots, padded_height, padded_width


def embed(image: Sequence[Sequence[float]], owner_id: str, strength: float = 4.0, profile: Mapping[str, object] | None = None) -> list[list[float]]:
    """Embed a repeated owner/content payload in mid-band DCT coefficients."""
    height, width = _check_image(image)
    dynamic_range = max(float(value) for row in image for value in row) - min(float(value) for row in image for value in row)
    if dynamic_range < MIN_DYNAMIC_RANGE:
        raise ValueError("embedding requires at least 8 luminance levels of source headroom")
    if profile is not None:
        checked = validate_profile(profile)
        strength = float(checked["qim_step"])
    if not math.isfinite(strength) or not 0 < strength <= 32:
        raise ValueError("QIM step must be finite and positive")
    payload = payload_bits(owner_id, image)
    padded, padded_height, padded_width = _padded(image)
    slots = padded_height // 8 * (padded_width // 8) * len(FREQUENCIES)
    if slots < len(payload) * REPETITIONS:
        raise ValueError("image has insufficient DCT slots for the error-correcting payload")
    for by in range(0, padded_height, 8):
        for bx in range(0, padded_width, 8):
            block = [row[bx : bx + 8] for row in padded[by : by + 8]]
            coeff = _dct8(block)
            for frequency_index, (u, v) in enumerate(FREQUENCIES):
                slot_index = (by // 8) * (padded_width // 8) * len(FREQUENCIES) + (bx // 8) * len(FREQUENCIES) + frequency_index
                payload_index = slot_index % len(payload)
                carrier = _carrier_sign(height, width, by // 8, bx // 8, frequency_index, payload_index)
                coeff[u][v] = _qim_embed(coeff[u][v], payload[payload_index], carrier, strength)
            restored = _idct8(coeff)
            if any(value < -CLIP_TOLERANCE or value > 255.0 + CLIP_TOLERANCE for row in restored for value in row):
                raise ValueError("embedding would clip a block; source is outside the admissible luminance headroom")
            for y in range(8):
                for x in range(8):
                    if by + y < height and bx + x < width:
                        padded[by + y][bx + x] = min(255.0, max(0.0, restored[y][x]))
    return [row[:width] for row in padded[:height]]


def detect(
    image: Sequence[Sequence[float]],
    owner_id: str,
    strength: float = 4.0,
    owner_threshold: float = 0.75,
    instance_threshold: float = 0.75,
    confidence_threshold: float = 0.65,
    profile: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Decode the public owner/content payload and return auditable scores."""
    height, width = _check_image(image)
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
    slots, padded_height, padded_width = _read_slots(image)
    votes = [[0, 0] for _ in range(PAYLOAD_BITS)]
    slots_per_row = padded_width // 8
    slot_number = 0
    for frequency_index, coefficient, _ in slots:
        block_number, slot_frequency = divmod(slot_number, len(FREQUENCIES))
        block_y, block_x = divmod(block_number, slots_per_row)
        payload_index = slot_number % PAYLOAD_BITS
        carrier = _carrier_sign(height, width, block_y, block_x, slot_frequency, payload_index)
        votes[payload_index][_qim_read(coefficient, carrier, strength)] += 1
        slot_number += 1
    decoded = [int(pair[1] >= pair[0]) for pair in votes]
    version = sum(decoded[index] << (3 - index) for index in range(4))
    owner_start, owner_end = 4, 4 + OWNER_BITS
    binding_start, binding_end = owner_end, owner_end + BINDING_BITS
    crc_start = binding_end
    decoded_owner = _bits_to_bytes(decoded[owner_start:owner_end])
    decoded_binding = sum(decoded[index] << (binding_end - 1 - index) for index in range(binding_start, binding_end))
    body = bytes([version]) + decoded_owner + decoded_binding.to_bytes(2, "big")
    crc_ok = _bits_to_bytes(decoded[crc_start:crc_start + 8])[0] == _crc8(body)
    owner_expected = _bits_from_int(int.from_bytes(_owner_tag(canonical_owner(owner_id)), "big"), OWNER_BITS)
    owner_accuracy = sum(decoded[owner_start + index] == bit for index, bit in enumerate(owner_expected)) / OWNER_BITS
    observed_binding = perceptual_bits(image) >> (16 - BINDING_BITS)
    binding_distance = (decoded_binding ^ observed_binding).bit_count()
    instance_accuracy = 1.0 - binding_distance / BINDING_BITS
    owner_margin = sum((max(pair) / sum(pair)) for pair in votes[owner_start:owner_end]) / OWNER_BITS
    present = version == VERSION and crc_ok and owner_accuracy >= owner_threshold and instance_accuracy >= instance_threshold and owner_margin >= confidence_threshold
    return {
        "present": present,
        "version": version,
        "crc_ok": crc_ok,
        "owner_accuracy": owner_accuracy,
        "instance_accuracy": instance_accuracy,
        "owner_margin": owner_margin,
        "confidence": owner_margin,
        "binding_distance": binding_distance,
        "payload_bits": PAYLOAD_BITS,
        "repetitions": REPETITIONS,
        "height": height,
        "width": width,
    }


def mse(left: Sequence[Sequence[float]], right: Sequence[Sequence[float]]) -> float:
    if len(left) != len(right) or any(len(a) != len(b) for a, b in zip(left, right)):
        raise ValueError("image shapes differ")
    values = [(float(a) - float(b)) ** 2 for row_a, row_b in zip(left, right) for a, b in zip(row_a, row_b)]
    return sum(values) / len(values)

