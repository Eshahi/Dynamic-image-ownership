"""Prospective fixed v4 inventory and public carrier transfers; no model execution."""
import math
from itertools import combinations
from three_threat_protocol import EXPANDED_IDS, ORIGINAL_IDS, inventory as previous_inventory

EXP = "c4-v4-three-threat-small-v1"
RUN = "c4-v4-three-threat-dev-001"
OWNERS = ("qim-pilot-owner-alpha", "qim-pilot-owner-beta",
          "qim-pilot-owner-gamma", "qim-pilot-owner-delta")
MODES = ("combined", "semantic_only", "perceptual_only", "none")
STRENGTHS = (0.05, 0.1, 0.2, 0.4)
SEEDS = (0, 1, 2)


def inventory(labels):
    rows = [r for r in previous_inventory() if r["axis"] in ("clean", "T4")]
    for i, donor in enumerate(ORIGINAL_IDS):
        for offset in (1, 5):
            recipient = ORIGINAL_IDS[(i + offset) % 10]
            for arm in ("public_band", "unmarked_band_sham", "public_projection"):
                rows.append({"id": f"t4-{arm}-{donor}-{recipient}", "axis": "T4",
                             "arm": arm, "donor_id": donor, "recipient_id": recipient,
                             "query_budget": 0, "carrier_knowledge": "public"})
    for source in ORIGINAL_IDS:
        for control in ("C0", "C1"):
            rows.append({"id": f"vae-{source}-{control}", "axis": "T3",
                         "source_id": source, "control": control, "dose": "vae_mode",
                         "seed": None, "strength": None, "query_budget": 0})
            for strength in STRENGTHS:
                for seed in SEEDS:
                    rows.append({"id": f"t3-{source}-{strength}-{seed}-{control}",
                                 "axis": "T3", "source_id": source, "control": control,
                                 "dose": "diffusion", "strength": strength,
                                 "seed": seed, "query_budget": 0})
    pairs = {(p["left"], p["right"]): p["label"] for p in labels}
    expected = set(combinations(EXPANDED_IDS, 2))
    if len(labels) != 66 or set(pairs) != expected:
        raise ValueError("frozen 66-pair label inventory required")
    for left, right in sorted(expected):
        rows.append({"id": f"t5-{left}-{right}", "axis": "T5",
                     "left": left, "right": right, "semantic_label": pairs[left, right]})
        if pairs[left, right] == "same":
            rows.append({"id": f"t5-transfer-{left}-{right}", "axis": "T5-transfer",
                         "donor_id": left, "recipient_id": right, "arm": "public_projection",
                         "semantic_label": "same", "query_budget": 0})
    if len(rows) != 537:
        raise ValueError("frozen cohort labels differ from seven same-semantic pairs")
    return rows


def claims(row):
    if row["axis"] in ("clean", "T3"):
        return [(owner, "combined", len(OWNERS)) for owner in OWNERS]
    if row["axis"] in ("T4", "T5-transfer"):
        return [(OWNERS[0], mode, 1) for mode in MODES]
    return []


def planned_calls(rows):
    return sum(len(claims(row)) for row in rows)


def distance(left, right):
    if any(type(x) is not int or not 0 <= x < 2**32 for x in (left, right)):
        raise ValueError("32-bit code required")
    return (left ^ right).bit_count()


def transfer(recipient, donor, profile, arm):
    """Public fixed one-shot transfer, without detector queries or secret access.

    Band arm copies all carrier coefficients; projection arm copies only their
    640 public carrier projections, correcting quantization for three passes.
    Donor is an actual saved C1 or C0 image, never a freshly re-embedded victim.
    """
    from revised_watermark_v4 import _Geometry, _resolve, _analyse, luminance_from_rgb
    if arm not in ("public_band", "unmarked_band_sham", "public_projection"):
        raise ValueError("unlisted public transfer")
    if profile["security"] != "public-derived":
        raise ValueError("this arm does not model access to a secret carrier")
    height, width = len(recipient), len(recipient[0])
    if height % 8 or width % 8 or len(donor) != height or any(len(r) != width for r in donor):
        raise ValueError("equal full-block RGB geometry required")
    checked, key, config = _resolve(profile, None)
    from revised_watermark_v4 import canonical_owner
    geometry = _Geometry(checked, key, config, canonical_owner(OWNERS[0]), height, width)
    source = luminance_from_rgb(recipient)
    _, donor_coeff = _analyse(luminance_from_rgb(donor), geometry.analysis)
    targets = geometry.projections(donor_coeff)
    output = [[tuple(p) for p in row] for row in recipient]
    for _ in range(3):
        _, current_coeff = _analyse(luminance_from_rgb(output), geometry.analysis)
        changes = [[] for _ in current_coeff]
        if arm in ("public_band", "unmarked_band_sham"):
            # Hash-detail planes precede the carrier bands and remain untouched.
            for b in range(len(changes)):
                changes[b] = [a - c for a, c in zip(donor_coeff[b][geometry.skip:],
                                                   current_coeff[b][geometry.skip:])]
        else:
            current = geometry.projections(current_coeff)
            for channel in (0, 1):
                bits, signs, norms = geometry.carriers[channel]
                step = [(a - c) / norm for a, c, norm in
                        zip(targets[channel], current[channel], norms)]
                count = len(geometry.frequencies[channel])
                for slot, (bit, sign) in enumerate(zip(bits, signs)):
                    changes[slot // count].append(step[bit] * sign)
        for b, values in enumerate(changes):
            top, left = b // (width // 8) * 8, b % (width // 8) * 8
            for y in range(8):
                for x in range(8):
                    delta = sum(value * plane[y * 8 + x] for value, plane in zip(values, geometry.planes))
                    output[top+y][left+x] = tuple(int(min(255, max(0, math.floor(c+delta+0.5))))
                                                  for c in output[top+y][left+x])
    return output
