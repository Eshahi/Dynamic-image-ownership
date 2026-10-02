"""Synthetic engineering benchmark: v3 QIM candidate versus the v4 dual-key codec.

Every host is procedurally generated and every distortion is a standard-library
stand-in (additive noise, contrast, box blur, block-DCT requantisation, band
transplant, residual copy).  The tables show how the codecs respond to the same
inputs at matched and at budgeted distortion.  They are not evidence about real
images, JPEG files or diffusion regeneration, and must not be cited as such.

Usage: python scripts/bench_revised_watermark_synthetic.py [--hosts 6] [--size 256] [--family 40] [--json out.json]
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import revised_watermark_v3 as v3  # noqa: E402
from scripts import revised_watermark_v4 as v4  # noqa: E402
from scripts.watermark_synthetic import (  # noqa: E402
    add_noise,
    box_blur,
    clamp,
    object_on_flat_background,
    plain_hosts,
    replace_band,
    requantise,
    residual_copy,
    scale,
    scene,
)

KEY = "synthetic-benchmark-key-0001"
SECOND_KEY = "synthetic-benchmark-key-0002"
OWNER = "bench-owner"
TEXTURES = (6.0, 12.0, 20.0)
SEMANTIC_BAND = [tuple(pair) for pair in v4.SEMANTIC_FREQUENCIES]
BAND = SEMANTIC_BAND + [tuple(pair) for pair in v4.INSTANCE_FREQUENCIES]
V3_BAND = [tuple(pair) for pair in v3.FREQUENCIES]

# Each distortion gets its own noise seed per host, so the cells are independent trials.
DISTORTIONS = (
    ("none", lambda image, seed: image),
    ("noise sigma 2", lambda image, seed: add_noise(image, 2.0, seed)),
    ("noise sigma 5", lambda image, seed: add_noise(image, 5.0, seed)),
    ("noise sigma 10", lambda image, seed: add_noise(image, 10.0, seed)),
    ("noise sigma 20", lambda image, seed: add_noise(image, 20.0, seed)),
    ("contrast x0.8", lambda image, seed: scale(image, 0.8)),
    ("box blur 3x3", lambda image, seed: box_blur(image, 1)),
    ("box blur 5x5", lambda image, seed: box_blur(image, 2)),
    ("requantise step 8", lambda image, seed: requantise(image, 8.0)),
    ("requantise step 16", lambda image, seed: requantise(image, 16.0)),
    ("requantise step 24", lambda image, seed: requantise(image, 24.0)),
    ("blur 3x3 + noise 4", lambda image, seed: add_noise(box_blur(image, 1), 4.0, seed)),
    ("blur 5x5 + noise 6", lambda image, seed: add_noise(box_blur(image, 2), 6.0, seed)),
)


def _v3_embed(image):
    return [[clamp(value) for value in row] for row in v3.embed(image, OWNER, KEY)]


def _v3_outcome(image, owner=OWNER, key=KEY):
    result = v3.detect(image, owner, key)
    return "both_match" if result["present"] else ("payload_readable" if result["crc_ok"] else "neither_match")


def _v4_codec(profile, key):
    def embed(image):
        marked, report = v4.embed_with_report(image, OWNER, key, profile, strict=False)
        if not report["verified"]:
            raise v4.EmbeddingError("not verified", report)
        return marked

    def outcome(image, owner=OWNER, key=key, **options):
        return v4.detect(image, owner, key, profile, **options)["outcome"]

    return {"embed": embed, "outcome": outcome, "band": BAND, "keyed": key is not None}


def _histogram(outcomes):
    return dict(sorted(Counter(outcomes).items()))


def _mean_psnr(pairs):
    values = [v4.psnr(a, b) for a, b in pairs]
    return sum(values) / len(values) if values else None


def run(hosts: int, size: int) -> dict[str, object]:
    textured = [scene(100 + index, size, size, TEXTURES[index % len(TEXTURES)]) for index in range(hosts)]
    plain = plain_hosts(size)
    groups = {"textured": textured, "plain": list(plain.values())}
    v3_marked = [_v3_embed(image) for image in textured]
    v3_psnr = _mean_psnr(zip(textured, v3_marked))
    keyed = v4.validate_profile(v4.KEYED_PROFILE)
    matched = v4.validate_profile({**v4.KEYED_PROFILE, "embedding": {**v4.KEYED_PROFILE["embedding"], "target_psnr_db": round(v3_psnr, 2)}})
    codecs = {
        "v3 QIM step 4": {"embed": _v3_embed, "outcome": _v3_outcome, "band": V3_BAND, "keyed": True},
        "v4 keyed, PSNR matched to v3": _v4_codec(matched, KEY),
        "v4 keyed, 42 dB": _v4_codec(keyed, KEY),
        "v4 public-derived, 42 dB": _v4_codec(v4.validate_profile(v4.DEFAULT_PROFILE), None),
    }
    table: dict[str, object] = {
        "size": size,
        "textures": list(TEXTURES),
        "groups": {name: len(images) for name, images in groups.items()},
        "plain_hosts": list(plain),
        "codecs": {},
    }
    for name, codec in codecs.items():
        entry: dict[str, object] = {}
        for group, sources in groups.items():
            marked, positions, failed = [], [], 0
            for position, source in enumerate(sources):
                try:
                    marked.append((source, codec["embed"](source)))
                    positions.append(position)
                except ValueError:
                    failed += 1
            processed = {
                label: _histogram(codec["outcome"](attack(image, 1000 * number + index)) for index, (_source, image) in enumerate(marked))
                for number, (label, attack) in enumerate(DISTORTIONS)
            }
            entry[group] = {
                "embedding_failures": failed,
                "psnr_db_mean": _mean_psnr(marked),
                "processed": processed,
                "unmarked": _histogram(codec["outcome"](source) for source in sources),
                "wrong_owner": _histogram(codec["outcome"](image, owner="another-owner") for _source, image in marked),
                "wrong_key": _histogram(codec["outcome"](image, key=SECOND_KEY) for _source, image in marked) if codec["keyed"] else None,
            }
            if group != "textured" or len(marked) < 2:
                continue
            # Transfers onto the next host; the recipient is always a different, unmarked image.
            recipients = [sources[(position + 1) % len(sources)] for position in positions]
            forged = {
                "band transplant": [replace_band(r, image, codec["band"]) for r, (_s, image) in zip(recipients, marked)],
                "residual copy": [residual_copy(r, image, source) for r, (source, image) in zip(recipients, marked)],
            }
            if codec["band"] is BAND:
                forged["semantic band only"] = [replace_band(r, image, SEMANTIC_BAND) for r, (_s, image) in zip(recipients, marked)]
            entry["transfers"] = {
                label: {"outcomes": _histogram(codec["outcome"](image) for image in images), "psnr_db_vs_recipient": _mean_psnr(zip(recipients, images))}
                for label, images in forged.items()
            }
            if codec["band"] is BAND:
                entry["transplant_by_binding_mode"] = {
                    mode: _histogram(codec["outcome"](image, binding_mode=mode) for image in forged["band transplant"])
                    for mode in v4.BINDING_MODES
                }
        table["codecs"][name] = entry
    return table


def same_composition(size: int, count: int) -> dict[str, object]:
    """Distinct images of one composition: code distances, and what a transplant between them gives."""
    profile = v4.validate_profile(v4.KEYED_PROFILE)
    decision = profile["decision"]
    families = {
        "same structure, texture 14": [scene(500, size, size, 14.0, detail_seed=index) for index in range(count)],
        "same structure, texture 6": [scene(500, size, size, 6.0, detail_seed=index) for index in range(count)],
        "object on flat background": [object_on_flat_background(index, size) for index in range(count)],
        "unrelated scenes": [scene(700 + index, size, size, TEXTURES[index % 3]) for index in range(count)],
    }
    table: dict[str, object] = {}
    for name, images in families.items():
        entry = {}
        for key in (KEY, SECOND_KEY):
            codes = [v4.detect(image, OWNER, key, profile) for image in images]
            pairs = [(a, b) for index, a in enumerate(codes) for b in codes[index + 1 :]]
            semantic = [bin(int(a["semantic_code"], 16) ^ int(b["semantic_code"], 16)).count("1") for a, b in pairs]
            instance = [bin(int(a["perceptual_hash"], 16) ^ int(b["perceptual_hash"], 16)).count("1") for a, b in pairs]
            entry[key] = {
                "pairs": len(pairs),
                "semantic_within_radius": sum(d <= decision["semantic_radius"] for d in semantic),
                "instance_within_radius": sum(d <= decision["instance_radius"] for d in instance),
                "instance_undecided": sum(decision["instance_radius"] < d < decision["instance_mismatch_distance"] for d in instance),
                "instance_distance_mean": sum(instance) / len(instance),
            }
        # Mark the first images and move each mark onto the next image of the family.
        donors = min(12, count - 1)
        full, semantic_only = [], []
        for index in range(donors):
            try:
                marked = v4.embed(images[index], OWNER, KEY, profile)
            except ValueError:
                continue
            recipient = images[index + 1]
            full.append(v4.detect(replace_band(recipient, marked, BAND), OWNER, KEY, profile)["outcome"])
            semantic_only.append(v4.detect(replace_band(recipient, marked, SEMANTIC_BAND), OWNER, KEY, profile)["outcome"])
        entry["band_transplant_to_next_image"] = _histogram(full)
        entry["semantic_band_transplant_to_next_image"] = _histogram(semantic_only)
        table[name] = entry
    return table


def _cell(histogram: dict[str, int] | None) -> str:
    if histogram is None:
        return "-"
    total = sum(histogram.values())
    authentic, flagged = histogram.get("both_match", 0), histogram.get("content_mismatch", 0)
    return f"{authentic}/{total - authentic - flagged}/{flagged}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--hosts", type=int, default=6, help="textured hosts (at least 2)")
    parser.add_argument("--size", type=int, default=256)
    parser.add_argument("--family", type=int, default=40, help="images per same-composition family (at least 3)")
    parser.add_argument("--json", type=Path)
    arguments = parser.parse_args()
    if arguments.hosts < 2 or arguments.family < 3 or arguments.size < 160:
        parser.error("need --hosts >= 2, --family >= 3 and --size >= 160")
    table = run(arguments.hosts, arguments.size)
    table["same_composition"] = same_composition(arguments.size, arguments.family)
    names = list(table["codecs"])

    def row(label: str, cells: list[str]) -> None:
        print(f"{label:28s} " + " ".join(f"{cell:>30s}" for cell in cells))

    print("cells: authentic / neither authentic nor flagged / flagged as bound to other content")
    for group, count in table["groups"].items():
        print(f"\n{group} hosts: {count} at {table['size']}x{table['size']}")
        row("condition", names)
        entries = [table["codecs"][name][group] for name in names]
        row("embedding failures", [str(entry["embedding_failures"]) for entry in entries])
        row("mean PSNR (dB)", ["-" if entry["psnr_db_mean"] is None else f"{entry['psnr_db_mean']:.2f}" for entry in entries])
        for label, _attack in DISTORTIONS:
            row(label, [_cell(entry["processed"][label]) for entry in entries])
        row("unmarked source", [_cell(entry["unmarked"]) for entry in entries])
        row("marked, wrong owner", [_cell(entry["wrong_owner"]) for entry in entries])
        row("marked, wrong key", [_cell(entry["wrong_key"]) for entry in entries])
    print("\ntransfers onto the next textured host (outcome counts, mean PSNR against the recipient)")
    for name in names:
        entry = table["codecs"][name]
        for label, transfer in entry.get("transfers", {}).items():
            print(f"  {name} / {label}: {transfer['outcomes']} at {transfer['psnr_db_vs_recipient']:.1f} dB")
        for mode, outcomes in entry.get("transplant_by_binding_mode", {}).items():
            print(f"  {name} / band transplant with binding_mode={mode}: {outcomes}")
    print("\noutcomes of processed marked images, v4 keyed at 42 dB (textured | plain)")
    reference = table["codecs"]["v4 keyed, 42 dB"]
    for label, _attack in DISTORTIONS:
        print(f"  {label:22s} {reference['textured']['processed'][label]} | {reference['plain']['processed'][label]}")
    print("\nimages of one composition (keyed profile, layout proxy): pairs within the instance radius / undecided, per key")
    for name, entry in table["same_composition"].items():
        per_key = "; ".join(
            f"{entry[key]['instance_within_radius']}/{entry[key]['instance_undecided']} of {entry[key]['pairs']} (mean distance {entry[key]['instance_distance_mean']:.1f})"
            for key in (KEY, SECOND_KEY)
        )
        print(f"  {name}: {per_key}")
        print(f"    band transplant to the next image: {entry['band_transplant_to_next_image']}")
        print(f"    semantic band only: {entry['semantic_band_transplant_to_next_image']}")
    if arguments.json:
        arguments.json.write_text(json.dumps(table, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
