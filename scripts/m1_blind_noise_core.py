"""CPU-only B3-C public content-template algebra; no image/model/source access.

Frozen scientific definition: research/m1-blind-noise-template-design.md.
The public hash maps confer no cryptographic ownership or adaptive-forgery bound.
Only owner-dependent maps are cached. Image-dependent descriptors never are.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import hashlib
import math
import numbers
import struct

import numpy as np

VERSION = "m1-blind-noise-template-v1"
MAP_VERSION = "m1-blind-noise-template-v1"
OWNER_INTERFACE_VERSION = "m1-public-owner-interface-v1"
N = 16384
M = 8192
FEATURE_DIM = 512
HASH_BITS = 32
THRESHOLD = 4.0
UNIT_NORM_TOLERANCE = 1e-6
OWNERS = tuple(f"qim-pilot-owner-{suffix}" for suffix in ("alpha", "beta", "gamma", "delta"))
A4_OWNERS = tuple(f"thesis:owner:{index:02d}" for index in range(16))
ACCEPTED_OWNERS = OWNERS + A4_OWNERS


def _owner(owner: str) -> str:
    if not isinstance(owner, str) or owner not in ACCEPTED_OWNERS:
        raise ValueError("owner must be one of the twenty frozen ASCII public owners")
    return owner


def _frame(value: str) -> bytes:
    raw = value.encode("utf-8")
    return struct.pack(">I", len(raw)) + raw


def _prefix(domain: str, owner: str) -> bytes:
    return _frame(MAP_VERSION) + _frame(domain) + _frame(owner)


def _permutation(domain: str, owner: str, n: int) -> np.ndarray:
    prefix = _prefix(domain, owner)
    return np.asarray(sorted(range(n), key=lambda j: (
        hashlib.sha256(prefix + struct.pack(">I", j)).digest(), j)), dtype=np.int64)


def _signs(domain: str, owner: str, n: int) -> np.ndarray:
    raw = hashlib.shake_256(_prefix(domain, owner)).digest((n + 7) // 8)
    bits = np.unpackbits(np.frombuffer(raw, dtype=np.uint8), bitorder="big")[:n]
    return 2.0 * bits.astype(np.float64) - 1.0


def fwht(values) -> np.ndarray:
    """Normalized natural-order Sylvester transform of a finite 1-D vector."""
    original = np.asarray(values)
    if np.iscomplexobj(original):
        raise ValueError("FWHT requires real values")
    a = np.asarray(values, dtype=np.float64)
    if a.ndim != 1 or a.size == 0 or a.size & (a.size - 1):
        raise ValueError("FWHT length must be a positive power of two")
    if not np.all(np.isfinite(a)):
        raise ValueError("FWHT values must be finite")
    a = a.copy()
    width = 1
    while width < a.size:
        blocks = a.reshape(-1, 2 * width)
        left, right = blocks[:, :width].copy(), blocks[:, width:].copy()
        blocks[:, :width] = left + right
        blocks[:, width:] = left - right
        width *= 2
    return a / math.sqrt(a.size)


def _feature(E) -> np.ndarray:
    original = np.asarray(E)
    if np.iscomplexobj(original):
        raise ValueError("E must be real")
    feature = np.asarray(E, dtype=np.float64)
    if feature.shape != (FEATURE_DIM,) or not np.all(np.isfinite(feature)):
        raise ValueError("E must have exactly 512 finite entries")
    norm = float(np.linalg.norm(feature))
    if not math.isfinite(norm) or abs(norm - 1.0) > UNIT_NORM_TOLERANCE:
        raise ValueError("E must be unit-normalized within absolute tolerance 1e-6")
    # Correct only floating-point normalization roundoff; reject arbitrary scale.
    return feature / norm


def _hash(H) -> int:
    if isinstance(H, (bool, np.bool_)) or not isinstance(H, numbers.Integral):
        raise ValueError("H must be an unsigned 32-bit integer, not bool/float")
    value = int(H)
    if not 0 <= value < (1 << HASH_BITS):
        raise ValueError("H is outside unsigned 32-bit range")
    return value


def _product(feature: np.ndarray, H: int) -> np.ndarray:
    b = np.asarray([2 * ((H >> (31 - k)) & 1) - 1 for k in range(HASH_BITS)],
                   dtype=np.float64) / math.sqrt(HASH_BITS)
    return (feature[:, None] * b[None, :]).ravel(order="C")


@dataclass(frozen=True)
class _Maps:
    coords_s: np.ndarray
    coords_i: np.ndarray
    columns_s: np.ndarray
    pre_signs_i: np.ndarray
    rows_i: np.ndarray
    r_s: np.ndarray
    r_i: np.ndarray


@lru_cache(maxsize=len(ACCEPTED_OWNERS))
def _owner_maps(owner: str) -> _Maps:
    _owner(owner)
    coordinates = _permutation("coordinates", owner, N)
    arrays = [coordinates[:M].copy(), coordinates[M:].copy(),
              _permutation("semantic-columns", owner, M)[:FEATURE_DIM].copy(),
              _signs("instance-pre-signs", owner, N),
              _permutation("instance-rows", owner, N)[:M].copy(),
              _signs("semantic-row-signs", owner, M),
              _signs("instance-row-signs", owner, M)]
    for array in arrays:
        array.setflags(write=False)
    return _Maps(*arrays)


def _projection(feature: np.ndarray, H: int, maps: _Maps):
    product = _product(feature, H)
    transformed = fwht(maps.pre_signs_i * product)
    projected = math.sqrt(N / M) * transformed[maps.rows_i]
    norm_sq = float(projected @ projected)
    if not math.isfinite(norm_sq) or norm_sq <= 0.0:
        raise ValueError("instance projection has zero/nonfinite squared norm")
    return product, transformed, projected, norm_sq


def _sampling_variance(population: np.ndarray, population_sum: float) -> float:
    """Exact conditional variance of (N/M)*sum of M rows without replacement."""
    centered = population - population_sum / N
    sample_variance = float(centered @ centered) / (N - 1)
    return (N * N) * (1.0 - M / N) * sample_variance / M


def template(E, H, owner: str) -> dict:
    """Make both templates from this descriptor only; no enrollment side input."""
    feature, hash_value, owner = _feature(E), _hash(H), _owner(owner)
    maps = _owner_maps(owner)
    semantic_input = np.zeros(M, dtype=np.float64)
    semantic_input[maps.columns_s] = feature
    v_s = fwht(semantic_input)
    _, transformed, projected, norm_sq = _projection(feature, hash_value, maps)
    v_i = projected / math.sqrt(norm_sq)
    T = np.zeros(N, dtype=np.float64)
    T[maps.coords_s] = math.sqrt(M) * maps.r_s * v_s
    T[maps.coords_i] = math.sqrt(M) * maps.r_i * v_i
    return {
        "coords_s": maps.coords_s, "coords_i": maps.coords_i,
        "v_s": v_s, "v_i": v_i, "r_s": maps.r_s, "r_i": maps.r_i, "T": T,
        "projection": {
            "input_dim": N, "output_dim": M, "sampling_scale": math.sqrt(N / M),
            "norm_sq": norm_sq, "norm": math.sqrt(norm_sq),
            "variance_norm": _sampling_variance(transformed * transformed, 1.0),
            "template_rms": float(np.sqrt(np.mean(T * T))),
        },
    }


def classify_scores(s, i) -> dict:
    """Three substantive states plus declared instance-only/invalid abstentions."""
    flags = {}
    for name, value in (("s", s), ("i", i)):
        flags[name] = (None if value is None or not math.isfinite(float(value))
                       else bool(float(value) >= THRESHOLD))
    if None in flags.values():
        state = "invalid_measurement"
    elif flags["s"]:
        state = "both_match" if flags["i"] else "semantic_only"
    else:
        state = "ambiguous_instance_only" if flags["i"] else "neither_supported"
    return {"flags": flags, "state": state}


def scores(zflat, E, H, owner: str) -> dict:
    """Blind score from suspect latent/features and public owner only.

    Invalid numerical inputs return a retained invalid_measurement result.
    No source image, source feature, payload or enrollment argument exists.
    """
    result = {"s": None, "i": None, "denominators": {"s": None, "i": None}, "errors": []}
    try:
        original = np.asarray(zflat)
        if np.iscomplexobj(original):
            raise ValueError("zflat must be real")
        z = np.asarray(zflat, dtype=np.float64)
        if z.shape != (N,) or not np.all(np.isfinite(z)):
            raise ValueError("zflat must have exactly 16384 finite entries in C-order")
        parts = template(E, H, owner)
        for channel in ("s", "i"):
            with np.errstate(over="ignore", invalid="ignore"):
                weights = z[parts[f"coords_{channel}"]] * parts[f"v_{channel}"]
                denominator = float(np.linalg.norm(weights))
                numerator = float(weights @ parts[f"r_{channel}"])
            if not math.isfinite(denominator) or denominator <= 0.0 or not math.isfinite(numerator):
                result["errors"].append(f"{channel}: zero/nonfinite score denominator or numerator")
                continue
            score = numerator / denominator
            if not math.isfinite(score):
                result["errors"].append(f"{channel}: nonfinite score")
                continue
            result[channel] = float(score)
            result["denominators"][channel] = denominator
    except (ValueError, TypeError, OverflowError) as exc:
        result["errors"].append(str(exc))
    result.update(classify_scores(result["s"], result["i"]))
    return result


def projection_diagnostic(E, H, E2, H2, owner: str) -> dict:
    """Exact kernels and conditional sampling moments; never choose a map."""
    feature, feature2 = _feature(E), _feature(E2)
    hash_value, hash_value2, owner = _hash(H), _hash(H2), _owner(owner)
    maps = _owner_maps(owner)
    x, u, p, norm1 = _projection(feature, hash_value, maps)
    y, w, q, norm2 = _projection(feature2, hash_value2, maps)
    exact = float(x @ y)
    raw = float(p @ q)
    normalized = raw / math.sqrt(norm1 * norm2)
    inner_error = abs(raw - exact)
    delta = max(abs(norm1 - 1.0), abs(norm2 - 1.0))
    bound = ((inner_error + abs(exact) * delta) / (1.0 - delta)
             if delta < 1.0 else None)
    return {
        "kernel_exact": exact, "kernel_projected_raw": raw,
        "kernel_projected_normalized": normalized,
        "norm_sq_1": norm1, "norm_sq_2": norm2,
        "inner_error": inner_error, "normalized_error": abs(normalized - exact),
        "delta": delta, "normalization_error_bound": bound,
        "variance_inner": _sampling_variance(u * w, exact),
        "variance_norm_1": _sampling_variance(u * u, 1.0),
        "variance_norm_2": _sampling_variance(w * w, 1.0),
        "sampling_fraction": M / N,
    }
