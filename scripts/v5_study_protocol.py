"""Prospective fixed v5 inventory, ordinary operations and public transfers; no model execution."""
import io
import math
from itertools import combinations

from three_threat_protocol import EXPANDED_IDS, ORIGINAL_IDS

EXP = "c4-v5-two-tier-regeneration-v1"
RUN = "c4-v5-two-tier-dev-001"
REHEARSAL_RUN = RUN + "-rehearsal"
OWNERS = ("qim-pilot-owner-alpha", "qim-pilot-owner-beta",
          "qim-pilot-owner-gamma", "qim-pilot-owner-delta")
MODES = ("combined", "semantic_only", "perceptual_only", "none")
STRENGTHS = (0.05, 0.1, 0.2, 0.4)
SEEDS = (0, 1, 2)
ORDINARY = ("jpeg75", "down384")
TRANSFER_ARMS = ("public_projection", "unmarked_projection_sham")
ROWS = 617
CALLS = 2204


def inventory(labels):
    """All prospective rows, not results.  Same sources, doses, seeds and pairings as the revision-2 study."""
    rows = []
    for source in EXPANDED_IDS:
        for control in ("C0", "C1"):
            rows.append({"id": f"clean-{source}-{control}", "axis": "clean",
                         "source_id": source, "control": control})
    # Secondary arm: the same ten T3 sources marked with the strong profile (control C2).
    for source in ORIGINAL_IDS:
        rows.append({"id": f"clean-{source}-C2", "axis": "clean", "source_id": source,
                     "control": "C2", "arm": "strong_profile"})
    for index, donor in enumerate(ORIGINAL_IDS):
        for offset in (1, 5):
            recipient = ORIGINAL_IDS[(index + offset) % 10]
            for scale in (0.5, 1.0):
                rows.append({"id": f"t4-residual-{donor}-{recipient}-{scale}", "axis": "T4",
                             "arm": "clean_donor_residual", "donor_id": donor,
                             "recipient_id": recipient, "scale": scale, "query_budget": 0})
            for arm in TRANSFER_ARMS:
                rows.append({"id": f"t4-{arm}-{donor}-{recipient}", "axis": "T4",
                             "arm": arm, "donor_id": donor, "recipient_id": recipient,
                             "query_budget": 0, "carrier_knowledge": "public"})
    for source in ORIGINAL_IDS:
        for control in ("C0", "C1", "C2"):
            rows.append({"id": f"vae-{source}-{control}", "axis": "T3",
                         "source_id": source, "control": control, "dose": "vae_mode",
                         "seed": None, "strength": None, "query_budget": 0})
            for strength in STRENGTHS:
                for seed in SEEDS:
                    rows.append({"id": f"t3-{source}-{strength}-{seed}-{control}",
                                 "axis": "T3", "source_id": source, "control": control,
                                 "dose": "diffusion", "strength": strength,
                                 "seed": seed, "query_budget": 0})
    for source in ORIGINAL_IDS:
        for control in ("C0", "C1"):
            for operation in ORDINARY:
                rows.append({"id": f"t1-{operation}-{source}-{control}", "axis": "T1s",
                             "source_id": source, "control": control, "operation": operation})
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
    if len(rows) != ROWS:
        raise ValueError("frozen cohort labels differ from seven same-semantic pairs")
    return rows


def claims(row):
    if row["axis"] in ("clean", "T3", "T1s"):
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


def ordinary(image, operation):
    """Supplementary ordinary processing of a PIL RGB image; fixed settings, no tuning."""
    from PIL import Image
    if operation == "jpeg75":
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=75, subsampling=2, optimize=False, progressive=False)
        with Image.open(io.BytesIO(buffer.getvalue())) as decoded:
            return decoded.convert("RGB")
    if operation == "down384":
        return image.resize((384, 384), Image.Resampling.LANCZOS)
    raise ValueError("unlisted ordinary operation")


def transfer(recipient, donor, profile, arm):
    """Public fixed one-shot transfer of both tiers, without detector queries, secrets or semantic features.

    The 320 robust and 320 fragile carrier projections of the donor image are
    computed with the public derivation and the recipient's projections are
    forced to them at the least squared error, three passes per tier.  The
    donor is an actual saved C1 image, or a C0 image for the sham; it is never
    a freshly re-embedded victim.  Since codec revision 2 (revision 3 keeps its
    detector) the robust projections are the detector's weighted ones (slot weights recomputed from each image),
    and every chip's move is spread over its slots in proportion to the slot
    weight, which is the least-squared-error move for that projection.
    """
    import revised_watermark_v5 as codec
    base = codec.base
    if arm not in TRANSFER_ARMS:
        raise ValueError("unlisted public transfer")
    if profile["security"] != "public-derived":
        raise ValueError("this arm does not model access to a secret carrier")
    height, width = len(recipient), len(recipient[0])
    if height % 8 or width % 8 or len(donor) != height or any(len(r) != width for r in donor):
        raise ValueError("equal full-block RGB geometry required")
    checked, key, config = codec._resolve(profile, None)
    owner = codec.canonical_owner(OWNERS[0])
    carrier = codec._robust_carrier(key, config, owner, len(checked["robust_frequencies"]))
    fragile = codec._Fragile(checked, key, config, owner, height, width)
    donor_luma = codec.luminance_from_rgb(donor)
    robust_target = codec._Robust(codec._coarse(donor_luma), donor_luma, checked, carrier).projections
    fragile_target = fragile.projections(base._analyse(donor_luma, fragile.analysis)[1])

    positions = [tuple(pair) for pair in checked["robust_frequencies"]]
    count = len(positions)
    chip_of_slot, signs, _counts = carrier
    output = [[[float(c) for c in pixel] for pixel in row] for row in recipient]
    for _ in range(3):
        luma = codec.luminance_from_rgb(output)
        robust = codec._Robust(codec._coarse(luma), luma, checked, carrier)
        unit = [(norm / (weight * gain)) ** 2 for norm in robust.normalisers
                for weight, gain in zip(robust.weights, robust.gains)]
        capacity = [0.0] * codec.CHANNEL_CHIPS
        for slot, chip in enumerate(chip_of_slot):
            capacity[chip] += robust.slot_weights[slot] ** 2 / unit[slot]
        moves = [a - c for a, c in zip(robust_target, robust.projections)]
        amplitudes = [[0.0] * count for _ in robust.normalisers]
        for slot, (chip, sign) in enumerate(zip(chip_of_slot, signs)):
            block, index = divmod(slot, count)
            delta = moves[chip] * robust.norms[chip] * robust.slot_weights[slot] * sign / (unit[slot] * capacity[chip])
            amplitudes[block][index] = delta * robust.normalisers[block] / (robust.weights[index] * robust.gains[index])
        shift = codec._render(height, width, positions, amplitudes)
        output = [[[min(255.0, max(0.0, c + s)) for c in pixel] for pixel, s in zip(row, shifts)]
                  for row, shifts in zip(output, shift)]
    output = [[tuple(int(min(255, max(0, math.floor(c + 0.5)))) for c in pixel) for pixel in row] for row in output]
    bits, fragile_signs, fragile_norms = fragile.carrier
    per_block = len(fragile.positions)
    for _ in range(3):
        coefficients = base._analyse(codec.luminance_from_rgb(output), fragile.analysis)[1]
        current = fragile.projections(coefficients)
        step = [(a - c) / norm for a, c, norm in zip(fragile_target, current, fragile_norms)]
        for b in range(len(coefficients)):
            values = [step[bits[b * per_block + offset]] * fragile_signs[b * per_block + offset] for offset in range(per_block)]
            top, left = b // (width // 8) * 8, b % (width // 8) * 8
            for y in range(8):
                for x in range(8):
                    delta = sum(value * plane[y * 8 + x] for value, plane in zip(values, fragile.planes))
                    output[top + y][left + x] = tuple(int(min(255, max(0, math.floor(c + delta + 0.5))))
                                                      for c in output[top + y][left + x])
    return [[list(pixel) for pixel in row] for row in output]
