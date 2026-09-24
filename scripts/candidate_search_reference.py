"""Model-free A5 radius-one candidate and common-q decision reference for B2.

Score callbacks consume already-extracted suspect codes. This does not extract
CLIP/pHash features, decode images, compute DCT, or run a scientific detector.
"""

from __future__ import annotations

import math
from collections.abc import Callable


def candidates(code: bytes, bits: int) -> tuple[bytes, ...]:
    if bits not in (12, 32) or not isinstance(code, bytes) or len(code) != bits // 8 + (bits % 8 != 0):
        raise ValueError("expected canonical 12-bit q or 32-bit pHash")
    value = int.from_bytes(code, "little")
    if value >= 1 << bits:
        raise ValueError("unused q bits must be zero")
    return tuple((value ^ mask).to_bytes(len(code), "little")
                 for mask in (0, *(1 << bit for bit in range(bits))))


def _result(result: object) -> tuple[float, bool]:
    if (not isinstance(result, tuple) or len(result) != 2
            or isinstance(result[0], bool) or not isinstance(result[0], (int, float))
            or not -1 <= result[0] <= 1 or not math.isfinite(result[0])
            or type(result[1]) is not bool):
        raise ValueError("score callback must return (finite [-1,1] score, bool zero_variance)")
    return float(result[0]), result[1]


def evaluate(
    suspect_q: bytes, suspect_h: bytes, tau_s: float, tau_i: float,
    semantic_score: Callable[[bytes], tuple[float, bool]],
    instance_score: Callable[[bytes, bytes], tuple[float, bool]],
) -> dict[str, object]:
    """Evaluate complete radius-one search; only a common q can jointly match.

    Zero-variance candidates cannot hit even if their score exceeds a negative
    threshold. The score lists retain all attempts in original-then-bit order.
    """
    q_codes, h_codes = candidates(suspect_q, 12), candidates(suspect_h, 32)
    for threshold in (tau_s, tau_i):
        if isinstance(threshold, bool) or not isinstance(threshold, (int, float)) or not -1 <= threshold <= 1 or not math.isfinite(threshold):
            raise ValueError("thresholds must be finite values in [-1,1]")
    semantic, instance = [], []
    semantic_hits, instance_hits, joint = set(), set(), None
    for q in q_codes:
        s, s_veto = _result(semantic_score(q))
        s_hit = not s_veto and s > tau_s
        semantic.append({"q": q.hex(), "score": s, "zero_variance": s_veto, "hit": s_hit})
        if s_hit:
            semantic_hits.add(q)
        for h in h_codes:
            i, i_veto = _result(instance_score(q, h))
            i_hit = not i_veto and i > tau_i
            instance.append({"q": q.hex(), "h": h.hex(), "score": i,
                             "zero_variance": i_veto, "hit": i_hit})
            if i_hit:
                instance_hits.add(q)
                if s_hit and joint is None:
                    joint = {"q": q.hex(), "h": h.hex()}
    return {"semantic_candidates": len(semantic), "instance_candidates": len(instance),
            "semantic_scores": semantic, "instance_scores": instance,
            "semantic_hit": bool(semantic_hits), "instance_hit": bool(instance_hits),
            "both_match": joint is not None, "first_joint_candidate": joint,
            "cross_q_only": bool(semantic_hits and instance_hits and joint is None)}
