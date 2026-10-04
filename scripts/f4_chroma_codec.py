"""Family 4: chroma-channel carrier.

The v5 r3 dual-key structure is kept as it is: semantic code q from CLIP and
the semantic key Ws in a robust tier; perceptual hash H and the instance key
Wi in the fragile full-resolution luminance tier; the same carriers, key test,
Bentkus-Dzindzalieta threshold and decision table.  One thing changes: the
robust tier reads and writes the isoluminant Cr plane (JPEG/BT.601 full range)
instead of luminance.

Why: `research/f4-chroma-carrier.md`.  The regeneration transfer probe
(`scripts/f4_transfer_probe.py`) showed that SD1.5 img2img keeps 8-32
cycles/image chroma about as well as luminance (gain about .3-.7 at strength
.2), while natural photographs carry one to three orders of magnitude less
chroma than luminance power in that band.  A correlation detector's
post-attack score scales with gain / sqrt(host power), so the same energy
buys a far larger score in Cr.

A change along CR_DIRECTION leaves Y and Cb unchanged, so the fragile tier and
the perceptual hash read the same luminance as in v5.  The detector is blind:
suspect RGB, claimed OwnerID, profile and the suspect's own CLIP features.
Image-domain comparator; not the proposal's latent method.
"""
from __future__ import annotations

import math
import sys
import time
from pathlib import Path
from typing import Mapping, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import revised_watermark_v5 as v5  # noqa: E402

base = v5.base
FAMILY = "f4-chroma-carrier"
REVISION = 1
CR_ROW = (0.5, -0.418688, -0.081312)
CR_DIRECTION = (1.402, -0.714136, 0.0)  # RGB change per unit Cr at constant Y and Cb
CR_WEIGHT = sum(c * c for c in CR_DIRECTION) / 3.0  # mean squared RGB change per squared Cr change
CB_ROW = (-0.168736, -0.331264, 0.5)
CB_DIRECTION = (0.0, -0.344136, 1.772)  # RGB change per unit Cb at constant Y and Cr
# Plane -> (analysis row, RGB direction, carrier label).  Cr keeps v5's robust carrier label;
# Cb gets an independent carrier, so its host noise and its chip signs are independent of Cr's.
PLANES = {"Cr": (CR_ROW, CR_DIRECTION, b"r"), "Cb": (CB_ROW, CB_DIRECTION, b"rcb")}


def _plane(rgb, row) -> list[list[float]]:
    a, b, c = row
    return [[128.0 + a * float(r) + b * float(g) + c * float(bl) for r, g, bl in line] for line in rgb]


def cr_plane(rgb: Sequence[Sequence[Sequence[float]]]) -> list[list[float]]:
    return _plane(rgb, CR_ROW)


def _carrier(checked, key, config, owner, label):
    slots = (v5.CANONICAL_SIDE // v5.BLOCK) ** 2 * len(checked["robust_frequencies"])
    return base._carrier(key, config, owner, label, v5.CANONICAL_SIDE, v5.CANONICAL_SIDE, slots)


def _carriers(checked, key, config, owner):
    return v5._robust_carrier(key, config, owner, len(checked["robust_frequencies"]))


def robust_projections(rgb, checked, key, config, owner, planes=("Cr",)) -> list[float]:
    """Chip projections of the robust tier, pooled over the chroma planes.

    Each plane's chip total and weight norm add, so the pooled statistic is
    still a weighted sum of independent random carrier signs under the null.
    """
    totals = squares = None
    for name in planes:
        row, _direction, label = PLANES[name]
        plane = _plane(rgb, row)
        robust = v5._Robust(v5._coarse(plane), plane, checked, _carrier(checked, key, config, owner, label))
        t = [p * n for p, n in zip(robust.projections, robust.norms)]
        s = [n * n for n in robust.norms]
        totals = t if totals is None else [a + b for a, b in zip(totals, t)]
        squares = s if squares is None else [a + b for a, b in zip(squares, s)]
    return [t / math.sqrt(s) if s > 0 else 0.0 for t, s in zip(totals, squares)]


def embed_rgb(rgb, owner_id: str, profile: Mapping[str, object], semantic_features: Sequence[float], planes=("Cr",)):
    """Return (RGB8 rows, report); the report verifies the rounded output with :func:`detect_rgb`.

    Every plane in ``planes`` gets its own closed-form robust change towards
    the same semantic key pattern, under its own block caps and PSNR floor.
    """
    checked, key, config = v5._resolve(profile, None)
    luma = v5.luminance_from_rgb(rgb)
    height, width = base._check_image(luma, int(checked["minimum_side"]))
    owner = v5.canonical_owner(owner_id)
    q = v5._semantic(base._analyse(luma, ())[0], checked, key, config, semantic_features, binding=True)
    table = v5._semantic_table(owner, key, config)
    ws = [chip for segment in range(v5.CODE_BITS) for chip in table[segment][v5._bit(q, segment)]]

    rgb_change = [[[0.0, 0.0, 0.0] for _ in range(width)] for _ in range(height)]
    channels = {}
    for name in planes:
        row_coefficients, direction, label = PLANES[name]
        plane = _plane(rgb, row_coefficients)
        robust = v5._Robust(v5._coarse(plane), plane, checked, _carrier(checked, key, config, owner, label))
        plan = v5._plan_robust(robust, ws, checked)
        weight = sum(c * c for c in direction) / 3.0
        weights = [[weight] * width for _ in range(height)]
        _change, delta, _shape, fill = v5._closed_form(plane, robust, plan, checked, weights)
        channels[name] = dict(host_rejection=plan["host_rejection"], amplitude=plan["amplitude"], host_rms=plan["host_rms"],
                              **v5._budget(delta, robust.mask, checked["embedding"], weights), **fill)
        for out_row, d_row in zip(rgb_change, delta):
            for pixel, d in zip(out_row, d_row):
                for index in range(3):
                    pixel[index] += d * direction[index]

    # Fragile tier on luminance, which the Cr change leaves unchanged.
    marked_luma = [[float(value) for value in row] for row in luma]
    fragile = v5._Fragile(checked, key, config, owner, height, width)
    means, coefficients = base._analyse(marked_luma, fragile.analysis)
    h = base._perceptual_hash(means, coefficients, key, config)
    itable = v5._instance_table(owner, key, config)
    wi = [chip for segment in range(v5.CODE_BITS) for chip in itable[segment][v5._bit(q, segment)][v5._bit(h, segment)]]
    instance = v5._embed_fragile(marked_luma, fragile, wi, checked, False, True)

    output, clipped, error = [], 0, 0.0
    for row, change_row, before_row, after_row in zip(rgb, rgb_change, luma, marked_luma):
        out_row = []
        for pixel, change, before, after in zip(row, change_row, before_row, after_row):
            values = [math.floor(float(c) + d + (after - before) + 0.5) for c, d in zip(pixel, change)]
            clipped += sum(v < 0 or v > 255 for v in values)
            final = tuple(int(min(255, max(0, v))) for v in values)
            error += sum((v - float(c)) ** 2 for v, c in zip(final, pixel))
            out_row.append(final)
        output.append(out_row)
    mse = error / (3.0 * height * width)
    result = detect_rgb(output, owner_id, checked, semantic_features, planes=planes)
    report = dict(family=FAMILY, revision=REVISION, semantic_code=f"{q:08x}", perceptual_hash=f"{h:08x}",
                  rgb_psnr_db=None if mse == 0 else 10 * math.log10(255.0**2 / mse), clipped_channels=clipped,
                  robust_planes=list(planes), robust_channel=channels,
                  instance_channel=instance, verification=result, verified=result["outcome"] == "both_match")
    return output, report


def detect_rgb(rgb, owner_id: str, profile: Mapping[str, object], semantic_features: Sequence[float],
               binding_mode: str = "combined", roster_size: int = 1, planes=("Cr",)) -> dict[str, object]:
    """v5 :func:`detect` with the robust tier read from the chroma ``planes``."""
    started = time.perf_counter()
    checked, key, config = v5._resolve(profile, None)
    luma = v5.luminance_from_rgb(rgb)
    height, width = base._check_image(luma, int(checked["minimum_side"]))
    owner = v5.canonical_owner(owner_id)
    decision = checked["decision"]
    target = float(decision["false_positive_target"])
    fragile = v5._Fragile(checked, key, config, owner, height, width)
    means, coefficients = base._analyse(luma, fragile.analysis)
    instance_projections = fragile.projections(coefficients)
    robust_chips = robust_projections(rgb, checked, key, config, owner, planes)
    q_now = v5._semantic(means, checked, key, config, semantic_features, binding=False)
    h_now = base._perceptual_hash(means, coefficients, key, config)

    check_semantic = binding_mode in ("combined", "semantic_only")
    check_instance = binding_mode in ("combined", "perceptual_only")
    semantic_limits = (int(decision["semantic_radius"]), int(decision["semantic_mismatch_distance"]))
    instance_limits = (int(decision["instance_radius"]), int(decision["instance_mismatch_distance"]))
    semantic = v5._channel_result(v5._key_test(robust_chips, v5._semantic_table(owner, key, config), q_now),
                                  target, roster_size, q_now)
    s_found = bool(semantic["found"])
    s_status = base._content_status(semantic["corrected_distance"], *semantic_limits, check_semantic) if s_found else None
    carries_other = s_found and base._content_status(semantic["corrected_distance"], *semantic_limits, True) != "match"
    q_bound = int(semantic["decoded_code"], 16) if carries_other else q_now
    table = v5._instance_table(owner, key, config)
    options = [table[segment][v5._bit(q_bound, segment)] for segment in range(v5.CODE_BITS)]
    instance = v5._channel_result(v5._key_test(instance_projections, options, h_now), target, roster_size, h_now)
    i_found = bool(instance["found"])
    i_status = (
        max(base._content_status(instance["corrected_distance"], *instance_limits, check_instance),
            base._content_status(semantic["corrected_distance"], *semantic_limits, check_semantic) if s_found else "unchecked",
            key=base._STATUS_RANK.get)
        if i_found else None)
    outcome, state = base._decide(s_found, s_status, i_found, i_status)

    def public(result, status):
        entry = dict(result)
        entry["content_status"] = status
        entry["content_match"] = bool(result["found"] and base._STATUS_RANK[status] == 0)
        return entry

    return {"outcome": outcome, "proposal_state": state, "watermark_found": bool(s_found or i_found),
            "semantic": public(semantic, s_status), "instance": public(instance, i_status),
            "semantic_code": f"{q_now:08x}", "perceptual_hash": f"{h_now:08x}", "binding_mode": binding_mode,
            "owner_id": owner.decode("utf-8"), "owners_tested": roster_size, "family": FAMILY, "revision": REVISION,
            "robust_planes": list(planes), "detector_config_id": config.hex(),
            "side_information": ["public OwnerID", "profile", "pinned CLIP weights"],
            "seconds": time.perf_counter() - started}
