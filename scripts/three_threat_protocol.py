"""Fixed attack inventory and RGB arithmetic; no codec, model or dispatch.

This module has no detector interface: attack construction cannot adapt to its
feedback. All semantic labels and image references belong to the evaluator.
"""
from itertools import combinations
import math

ORIGINAL_IDS = (6012, 25394, 80932, 109798, 134882, 147498, 177015, 190676, 468505, 499768)
EXPANDED_IDS = tuple(sorted((*ORIGINAL_IDS, 1675, 4795)))
REGEN_SETTINGS = {
    "num_inference_steps": 20, "eta": 0.0, "guidance_scale": 1.0,
    "prompt": "", "negative_prompt": "", "width": 512, "height": 512,
    "safety_checker_required": True, "scheduler": "DDIM",
    "strengths": [0.2, 0.4], "seeds": [0, 1, 2],
}


def inventory():
    """Return all prospective rows, not results; IDs are never reused runs."""
    rows = []
    for source in EXPANDED_IDS:
        for control in ("C0", "C1"):
            rows.append({"id": f"clean-{source}-{control}", "axis": "clean",
                         "source_id": source, "control": control})
    for index, donor in enumerate(ORIGINAL_IDS):
        for offset in (1, 5):
            recipient = ORIGINAL_IDS[(index + offset) % 10]
            for size in (128, 256):
                for arm, donor_control in (("public_patch", "C1"), ("unmarked_patch_sham", "C0")):
                    rows.append({"id": f"t4-{arm}-{donor}-{recipient}-{size}", "axis": "T4",
                                 "arm": arm, "donor_id": donor, "recipient_id": recipient,
                                 "donor_control": donor_control, "recipient_control": "C0",
                                 "patch_size": size, "query_budget": 0})
            for scale in (0.5, 1.0):
                rows.append({"id": f"t4-residual-{donor}-{recipient}-{scale}", "axis": "T4",
                             "arm": "clean_donor_residual", "donor_id": donor,
                             "recipient_id": recipient, "donor_control": "C1_minus_C0",
                             "recipient_control": "C0", "scale": scale, "query_budget": 0})
    for source in ORIGINAL_IDS:
        for strength in REGEN_SETTINGS["strengths"]:
            for seed in REGEN_SETTINGS["seeds"]:
                for control in ("C0", "C1"):
                    rows.append({"id": f"t3-{source}-{strength}-{seed}-{control}", "axis": "T3",
                                 "source_id": source, "strength": strength, "seed": seed,
                                 "control": control, "query_budget": 0})
    for left, right in combinations(EXPANDED_IDS, 2):
        rows.append({"id": f"t5-{left}-{right}", "axis": "T5",
                     "left": left, "right": right, "binding_bits": 12,
                     "diagnostic_collision_max_distance": 3})
    return rows


def shape(rgb):
    """Strict RGB8 input: no coercion, implicit crop, alpha or broadcasting."""
    height = len(rgb)
    width = len(rgb[0]) if height else 0
    if height == 0 or width == 0 or any(len(row) != width for row in rgb):
        raise ValueError("nonempty rectangular RGB8 required")
    for row in rgb:
        for pixel in row:
            if len(pixel) != 3 or any(type(value) is not int or not 0 <= value <= 255 for value in pixel):
                raise ValueError("three integer RGB8 channels required")
    return height, width


def same_shape(*images):
    shapes = [shape(image) for image in images]
    if len(set(shapes)) != 1:
        raise ValueError("RGB shapes differ")
    return shapes[0]


def center_patch(recipient_c0, donor_rgb, size):
    """Same-coordinate central patch; public/sham distinction is caller input.

    Copies RGB bytes exactly without any metric, blending or detector query.
    """
    height, width = same_shape(recipient_c0, donor_rgb)
    if type(size) is not int or size <= 0 or size > min(height, width):
        raise ValueError("invalid central patch size")
    y0, x0 = (height - size) // 2, (width - size) // 2
    return [[list(donor_rgb[y][x] if y0 <= y < y0 + size and x0 <= x < x0 + size
                  else recipient_c0[y][x]) for x in range(width)] for y in range(height)]


def residual_transfer(recipient_c0, donor_c1, donor_c0, scale):
    """Separate stronger-access arm; clip then ties-to-even RGB8 quantization."""
    height, width = same_shape(recipient_c0, donor_c1, donor_c0)
    if type(scale) not in (int, float) or not math.isfinite(scale) or scale not in (0.5, 1.0):
        raise ValueError("only frozen residual scales allowed")
    return [[[round(min(255.0, max(0.0, recipient_c0[y][x][channel] +
                  scale * (donor_c1[y][x][channel] - donor_c0[y][x][channel]))))
              for channel in range(3)] for x in range(width)] for y in range(height)]


def binding_distance(left, right):
    if any(type(value) is not int or not 0 <= value < 4096 for value in (left, right)):
        raise ValueError("12-bit binding integer required")
    return (left ^ right).bit_count()
