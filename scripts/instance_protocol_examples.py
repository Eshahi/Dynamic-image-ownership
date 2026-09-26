"""Generate owned synthetic C3b byte-protocol examples; not dataset evidence."""
import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.signatures.instance import (PROFILE, InstanceScore, SemanticScore,
    bind_canonical_image, fuse_candidates, radius_one)


def examples():
    q = bytes.fromhex("a503")  # supplied synthetic12-bit code, not extracted CLIP
    cases = []
    for name, width, height, owner in (("owned-pattern-37x43", 37, 43, "synthetic-owner"),
                                      ("changed-instance-43x37", 43, 37, "synthetic-owner"),
                                      ("wrong-owner-control", 37, 43, "synthetic-other-owner"),
                                      ("constant-collision-black", 32, 32, "synthetic-owner"),
                                      ("constant-collision-white", 32, 32, "synthetic-owner")):
        raw = bytes([255 if name.endswith("white") else 0])*(width*height*3) if name.startswith("constant-") else bytes(
            (17*x+29*y+53*c+3*x*y) % 256 for y in range(height) for x in range(width) for c in range(3))
        code, keys = bind_canonical_image(raw, width, height, q, owner)
        cases.append({"case_id": name, "source": "owned-synthetic-rgb8-not-study-data", "width": width,
                      "height": height, "raw_sha256": hashlib.sha256(raw).hexdigest(),
                      "q_origin": "supplied-synthetic-not-CLIP", "q_hex": q.hex(), "phash_hex": code.packed.hex(),
                      "minimum_selected_margin": code.minimum_selected_margin, "constant_rgb": code.constant_rgb,
                      "owner_id": keys.owner_id, "semantic_signature_hex": keys.semantic.hex(),
                      "instance_signature_hex": keys.instance.hex()})
    h = bytes.fromhex("12345678"); qs, hs = radius_one(q, 12), radius_one(h, 32)
    fusion = []
    for label, semantic_q, instance_q in (("same-q-joint", qs[1], qs[1]), ("different-q-no-joint", qs[1], qs[2])):
        s = tuple(SemanticScore(qc, .9 if qc == semantic_q else -.7) for qc in qs)
        i = tuple(InstanceScore(qc, hc, .9 if (qc, hc) == (instance_q, hs[1]) else -.7) for qc in qs for hc in hs)
        result = fuse_candidates(q, h, s, i, tau_s=.5, tau_i=.5, detector_config_id=b"\x01"*32,
                                 threshold_version="synthetic-not-calibrated-v1", owner_id="synthetic-owner")
        fusion.append({"case_id": label, "supplied_scores_not_image_detector": True, "result": result})
    by_name = {row["case_id"]: row for row in cases}
    lengths = {"q_bytes": 2, "phash_bytes": 4, "Ws_bytes": 32, "Wi_bytes": 32}
    pairs = []
    for label, left, right in (
            ("same-instance-same-owner-repeat", "owned-pattern-37x43", "owned-pattern-37x43"),
            ("same-supplied-q-different-instance-same-owner", "owned-pattern-37x43", "changed-instance-43x37"),
            ("same-instance-wrong-owner", "owned-pattern-37x43", "wrong-owner-control"),
            ("known-constant-instance-collision", "constant-collision-black", "constant-collision-white")):
        one, two = by_name[left], by_name[right]
        distances = {}
        for field, metric, size in (("q_hex", "q_bits", 2), ("phash_hex", "phash_bits", 4),
                                     ("semantic_signature_hex", "Ws_bits", 32), ("instance_signature_hex", "Wi_bits", 32)):
            a, b = bytes.fromhex(one[field]), bytes.fromhex(two[field])
            if len(a) != size or len(b) != size: raise ValueError("unexpected public protocol length")
            distances[metric] = sum((a_byte ^ b_byte).bit_count() for a_byte, b_byte in zip(a, b))
        pairs.append({"case_id": label, "left": left, "right": right, "distances_hamming_bits": distances,
                      "output_lengths": lengths,
                      "input_shapes_hwc": [[one["height"], one["width"], 3], [two["height"], two["width"], 3]],
                      "semantic_control": "same supplied synthetic q, not measured same semantic content"})
    return {"schema_version": "c3b-owned-synthetic-protocol-examples-v1", "profile": PROFILE,
            "scientific_study_run": False, "no_study_images_or_models_used": True,
            "no_empirical_stability_or_detector_performance_claim": True,
            "fixture_rule": "RGB(x,y,c)=(17*x+29*y+53*c+3*x*y)%256; named constants0/255; suppliedq=a503",
            "examples": cases, "fusion_examples": fusion, "controlled_pairs": pairs, "output_lengths": lengths,
            "runtime": {"python": sys.version.split()[0], "os": platform.system(), "libc": platform.libc_ver(),
                        "float_mantissa_bits": sys.float_info.mant_dig},
            "provenance": {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in
                ("src/signatures/instance.py", "src/signatures/owner.py", "scripts/instance_protocol_examples.py",
                 "research/method-spec.md", "research/scope-guard.md")}}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = examples()
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump(report, handle, sort_keys=True, indent=2, allow_nan=False)
        handle.write("\n")
    print(json.dumps({"owned_synthetic_examples": len(report["examples"]), "fusion_cases": len(report["fusion_examples"]),
                      "scientific_study_run": False, "output": str(args.output)}))
