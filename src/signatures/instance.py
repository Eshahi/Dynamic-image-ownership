"""A5 instance code, public binding and complete common-q score fusion.

No file decoding, model, calibration, detector DCT, enrollment registry or
scientific execution. Canonical pixels and candidate scores are caller inputs.
"""
from __future__ import annotations

import math
import struct
from dataclasses import dataclass
from .owner import PublicSignatures, derive_public_signatures

PROFILE = "a5-phash32-rgb8-f32-channels-f64-bilinear-fsum-dct-v1"
_CHANNEL = tuple(struct.unpack("<f", struct.pack("<f", value / 255))[0] for value in range(256))
_BASIS = tuple(tuple((math.sqrt(1/32) if k == 0 else math.sqrt(2/32)) *
                    math.cos(math.pi*(n+.5)*k/32) for n in range(32)) for k in range(8))
POSITIONS = tuple(sorted(((u, v) for u in range(8) for v in range(8) if (u, v) != (0, 0)),
                         key=lambda position: (sum(position), *position))[:32])


@dataclass(frozen=True)
class PerceptualCode:
    packed: bytes
    coefficients: tuple[tuple[float, ...], ...]
    median: float
    minimum_selected_margin: float
    constant_rgb: bool
    profile: str = PROFILE


def perceptual_code(rgb8: bytes, width: int, height: int) -> PerceptualCode:
    """Native canonical RGB8 -> fixed32x32 Y -> orthonormal DCT-II ->32 bits.

    Channels round to IEEE binary32 byte/255 then widen to binary64 for the
    declared luminance/resize/fsum DCT. This is not a configurable image resize.
    Constant RGB is analytically zero AC, avoiding numerical tie artifacts.
    """
    if (type(width) is not int or type(height) is not int or
            not 32 <= width <= 0xffffffff or not 32 <= height <= 0xffffffff or
            not isinstance(rgb8, bytes) or len(rgb8) != 3*width*height):
        raise ValueError("expected immutable native RGB8, uint32 dimensions >=32")
    if all(rgb8[i:i+3] == rgb8[:3] for i in range(0, len(rgb8), 3)):
        y = sum(weight*_CHANNEL[value] for weight, value in zip((.299, .587, .114), rgb8[:3]))
        coefficients = tuple(tuple(32*y if u == v == 0 else 0.0 for v in range(8)) for u in range(8))
        return PerceptualCode(bytes(4), coefficients, 0.0, 0.0, True)

    def luminance(x, y):
        offset = 3*(y*width+x)
        return .299*_CHANNEL[rgb8[offset]] + .587*_CHANNEL[rgb8[offset+1]] + .114*_CHANNEL[rgb8[offset+2]]

    def axes(size):
        result = []
        for destination in range(32):
            coordinate = (destination+.5)*size/32-.5
            low = math.floor(coordinate)
            result.append((max(0, min(size-1, low)), max(0, min(size-1, low+1)), coordinate-low))
        return result

    resized = []
    for y0, y1, wy in axes(height):
        row = []
        for x0, x1, wx in axes(width):
            top = (1-wx)*luminance(x0, y0)+wx*luminance(x1, y0)
            bottom = (1-wx)*luminance(x0, y1)+wx*luminance(x1, y1)
            row.append((1-wy)*top+wy*bottom)
        resized.append(row)
    horizontal = [[math.fsum(resized[y][x]*_BASIS[v][x] for x in range(32)) for v in range(8)] for y in range(32)]
    coefficients = tuple(tuple(math.fsum(_BASIS[u][y]*horizontal[y][v] for y in range(32)) for v in range(8)) for u in range(8))
    median = sorted(coefficients[u][v] for u in range(8) for v in range(8) if (u, v) != (0, 0))[31]
    bits = sum(1 << bit for bit, (u, v) in enumerate(POSITIONS) if coefficients[u][v] > median)
    margin = min(abs(coefficients[u][v]-median) for u, v in POSITIONS)
    return PerceptualCode(bits.to_bytes(4, "little"), coefficients, median, margin, False)


def derive_instance(q: bytes, phash: bytes, owner_id: str) -> bytes:
    """Exact shared C3a domain-separated Wi; public, not authentication."""
    return derive_public_signatures(q, phash, owner_id).instance


def bind_canonical_image(rgb8: bytes, width: int, height: int, q: bytes,
                         owner_id: str) -> tuple[PerceptualCode, PublicSignatures]:
    # q is supplied by C2; this does not recompute or certify its image origin.
    derive_public_signatures(q, bytes(4), owner_id)  # reject malformed binding first
    code = perceptual_code(rgb8, width, height)
    return code, derive_public_signatures(q, code.packed, owner_id)


def radius_one(code: bytes, bits: int) -> tuple[bytes, ...]:
    if (type(bits) is not int or bits not in (12, 32) or not isinstance(code, bytes) or
            len(code) != (bits+7)//8 or int.from_bytes(code, "little") >= 1 << bits):
        raise ValueError("expected canonical12/32-bit code")
    original = int.from_bytes(code, "little")
    return tuple((original ^ mask).to_bytes(len(code), "little") for mask in (0, *(1 << i for i in range(bits))))


@dataclass(frozen=True)
class SemanticScore:
    q: bytes
    score: float
    zero_variance: bool = False


@dataclass(frozen=True)
class InstanceScore:
    q: bytes
    phash: bytes
    score: float
    zero_variance: bool = False


def _score(value, veto):
    if (isinstance(value, bool) or not isinstance(value, (int, float)) or
            not math.isfinite(value) or not -1 <= value <= 1 or type(veto) is not bool):
        raise ValueError("scores require finite[-1,1] value and bool zero_variance")
    return float(value)


def fuse_candidates(q: bytes, phash: bytes, semantic: tuple[SemanticScore, ...],
                    instance: tuple[InstanceScore, ...], *, tau_s: float, tau_i: float,
                    detector_config_id: bytes, threshold_version: str, owner_id: str) -> dict:
    """One owner's complete13/429 score inventory; no oracle/source code input.

    Supplied thresholds/version/config are labels, not evidence of calibration.
    No component hit on a different q can become a joint match. Incomplete,
    duplicate, extra or malformed candidate scores are errors, never negatives.
    """
    owners = derive_public_signatures(q, phash, owner_id)
    q_codes, h_codes = radius_one(q, 12), radius_one(phash, 32)
    _score(tau_s, False); _score(tau_i, False)
    if (not isinstance(detector_config_id, bytes) or len(detector_config_id) != 32 or
            detector_config_id == bytes(32) or not isinstance(threshold_version, str) or
            not 1 <= len(threshold_version.encode("utf-8")) <= 256):
        raise ValueError("explicit nonzero config digest and threshold version required")
    if (not isinstance(semantic, tuple) or len(semantic) != 13 or
            any(type(row) is not SemanticScore for row in semantic) or
            not isinstance(instance, tuple) or len(instance) != 429 or
            any(type(row) is not InstanceScore for row in instance)):
        raise ValueError("complete typed13/429 candidate inventories required")
    s = {}; i = {}
    for row in semantic:
        radius_one(row.q, 12)
        if row.q in s: raise ValueError("duplicate semantic candidate")
        s[row.q] = (_score(row.score, row.zero_variance), row.zero_variance)
    for row in instance:
        radius_one(row.q, 12); radius_one(row.phash, 32)
        key = (row.q, row.phash)
        if key in i: raise ValueError("duplicate instance candidate")
        i[key] = (_score(row.score, row.zero_variance), row.zero_variance)
    if set(s) != set(q_codes) or set(i) != {(qc, hc) for qc in q_codes for hc in h_codes}:
        raise ValueError("candidate inventory outside fixed radius-one search")
    semantic_rows, instance_rows = [], []
    s_hits, i_hits, joint = set(), set(), None
    for qc in q_codes:
        score, veto = s[qc]; hit = not veto and score > tau_s
        semantic_rows.append({"q": qc.hex(), "score": score, "zero_variance": veto, "hit": hit})
        if hit: s_hits.add(qc)
        for hc in h_codes:
            value, zero = i[(qc, hc)]; i_hit = not zero and value > tau_i
            instance_rows.append({"q": qc.hex(), "h": hc.hex(), "score": value, "zero_variance": zero, "hit": i_hit})
            if i_hit:
                i_hits.add(qc)
                if hit and joint is None: joint = {"q": qc.hex(), "h": hc.hex()}
    return {"semantic_candidates": 13, "instance_candidates": 429,
            "semantic_scores": semantic_rows, "instance_scores": instance_rows,
            "semantic_hit": bool(s_hits), "instance_hit": bool(i_hits), "both_match": joint is not None,
            "cross_q_only": bool(s_hits and i_hits and joint is None), "first_joint_candidate": joint,
            "maximum_semantic_candidate": max(semantic_rows, key=lambda row: row["score"]),
            "maximum_instance_candidate": max(instance_rows, key=lambda row: row["score"]),
            "owner_id": owners.owner_id, "tested_owner_count": 1,
            "detector_config_id": detector_config_id.hex(), "threshold_version": threshold_version,
            "thresholds": {"tau_s": float(tau_s), "tau_i": float(tau_i)},
            "score_origin": "caller_supplied_not_full_detector_or_calibration_evidence"}
