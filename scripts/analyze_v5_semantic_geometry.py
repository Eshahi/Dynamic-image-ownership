"""Bounded exploratory ranking analysis of pinned dev-001 JSON; stdlib only."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
from itertools import combinations
import json
import math
from pathlib import Path
import re
import statistics
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from scripts import revised_watermark_v5 as codec
from scripts.v5_study_protocol import inventory

MAIN = Path("W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5")
PLAN = ROOT / "research/v5-semantic-geometry-analysis-plan-20261003.md"
PROFILE = ROOT / "experiments/c4-v5-two-tier-regeneration-v1/profile.json"
LABELS = ROOT / "experiments/c4-three-threat-small-v1/semantic-labels.json"
RUN = "c4-v5-two-tier-dev-001"
EXPECTED = "58766c579377f344770887e6cad8bf4ed779ee207c2b6872b4a24ac4a90b9b4d"
CHECKPOINT = "40d365715913c9da98579312b702a82c18be219cc2a73407c4526f58eba950af"
OWNER = "qim-pilot-owner-alpha"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def feature_hash(values):
    return hashlib.sha256(json.dumps(values, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def validate_feature(row):
    f = row["clip"]
    values = f["values"]
    require(f["dimension"] == 512 and len(values) == 512, "feature dimension mismatch")
    require(all(type(v) in (float, int) and math.isfinite(v) for v in values), "nonfinite/non-numeric feature")
    require(f["feature_sha256"] == feature_hash(values), "feature hash mismatch")
    require(f["l2_normalized"] is True and abs(math.sqrt(dot(values, values)) - 1) <= 1e-5,
            "feature normalization mismatch")
    require(f["checkpoint_sha256"] == CHECKPOINT, "checkpoint mismatch")
    pixels = row["image"]["pixel_sha256"]
    require(bool(re.fullmatch(r"[0-9a-f]{64}", pixels)) and f["pixel_sha256"] == pixels,
            "saved feature/pixel linkage mismatch")
    detections = [d for d in row["detections"] if d["claimed_owner"] == OWNER and d["binding_mode"] == "combined"]
    require(len(detections) == 1, "missing or duplicate claimed-owner combined detection")
    d = detections[0]
    require(d["pixel_sha256"] == pixels and d["feature_origin"] == "same saved suspect RGB8",
            "saved detection/pixel linkage mismatch")
    result = d["result"]
    require(result["owner_id"] == OWNER and result["binding_mode"] == "combined" and
            result["semantic_source"] == "external:clip-vit-b32-a6-40d365715913", "saved detection identity mismatch")
    for field in ("semantic_code", "perceptual_hash"):
        require(bool(re.fullmatch(r"[0-9a-f]{8}", result[field])), "invalid saved 32-bit code")
    return values, result


def describe(values):
    return {"n": len(values), "mean": statistics.mean(values) if values else None,
            "median": statistics.median(values) if values else None,
            "sample_sd": statistics.stdev(values) if len(values) > 1 else None,
            "min": min(values) if values else None, "max": max(values) if values else None,
            "undefined_reason": "empty set" if not values else "sample SD requires n >= 2" if len(values) == 1 else None}


def order(positive, negative):
    return (positive > negative) - (positive < negative)


def empirical_auc(positive, negative):
    counts = Counter(order(p, n) for p in positive for n in negative)
    total = len(positive) * len(negative)
    return {"auc": (counts[1] + .5 * counts[0]) / total if total else None,
            "wins": counts[1], "ties": counts[0], "losses": counts[-1], "comparisons": total,
            "same_pairs": len(positive), "different_pairs": len(negative),
            "undefined_reason": None if total else "at least one binary class is empty"}


def omit_source(pairs, source):
    return [p for p in pairs if source not in (p["left"], p["right"])]


def rank_stats(pairs, arm):
    same = [p[arm] for p in pairs if p["label"] == "same"]
    different = [p[arm] for p in pairs if p["label"] == "different"]
    cosine = empirical_auc([p["cosine"] for p in same], [p["cosine"] for p in different])
    q = empirical_auc([-p["q"] for p in same], [-p["q"] for p in different])
    return {"cosine": cosine, "negative_q": q,
            "cosine_minus_code_auc": cosine["auc"] - q["auc"] if cosine["auc"] is not None else None}


def validate_inputs(data, labels, profile):
    sources = labels["source_ids"]
    require(len(sources) == 12 and len(set(sources)) == 12, "source roster mismatch")
    frozen = labels["pairs"]
    keys = [(p["left"], p["right"]) for p in frozen]
    require(len(frozen) == 66 and len(set(keys)) == 66 and
            {frozenset(k) for k in keys} == {frozenset(k) for k in combinations(sources, 2)}, "pair roster mismatch")
    require(Counter(p["label"] for p in frozen) == Counter(same=7, different=57, uncertain=2), "label count mismatch")
    expected_rows = inventory(frozen)
    rows = data["rows"]
    index = {r["id"]: r for r in rows}
    require(data["run_id"] == RUN and len(rows) == len(index) == 617 and
            set(index) == {r["id"] for r in expected_rows}, "complete unique 617-row roster required")
    for expected_row in expected_rows:
        require(all(index[expected_row["id"]].get(k) == v for k, v in expected_row.items()),
                "saved row identity/label disagreement: " + expected_row["id"])
    vectors, codes, hashes = {}, {}, {}
    for source in sources:
        for arm in ("C0", "C1"):
            row = index[f"clean-{source}-{arm}"]
            # Existing embedding acceptance failures do not erase otherwise complete saved features.
            require(row.get("detection_complete") is True, "incomplete clean detection roster")
            vectors[source, arm], detection = validate_feature(row)
            codes[source, arm] = codec.semantic_code(vectors[source, arm], profile=profile)
            require(f"{codes[source, arm]:08x}" == detection["semantic_code"], "recomputed semantic code mismatch")
            hashes[source, arm] = int(detection["perceptual_hash"], 16)
    pairs = []
    for p in frozen:
        left, right = p["left"], p["right"]
        row = index[f"t5-{left}-{right}"]
        require(row.get("status") == "complete_component_diagnostic" and not row.get("errors"), "incomplete T5 pair")
        entry = {"id": row["id"], "left": left, "right": right, "label": p["label"], "label_rationale": p["rationale"]}
        for arm in ("C0", "C1"):
            q = (codes[left, arm] ^ codes[right, arm]).bit_count()
            h = (hashes[left, arm] ^ hashes[right, arm]).bit_count()
            require(row["distances_" + arm] == {"semantic": q, "instance": h}, "saved pair distance mismatch")
            entry[arm] = {"cosine": dot(vectors[left, arm], vectors[right, arm]), "q": q, "H": h,
                          "q_le_6": q <= 6, "q_le_6_and_H_gt_6": q <= 6 and h > 6}
        require(type(row["clip_pair_cosine"]) in (int, float) and math.isfinite(row["clip_pair_cosine"]) and
                abs(entry["C0"]["cosine"] - row["clip_pair_cosine"]) <= 1e-9, "saved C0 dot product mismatch")
        entry["C1_minus_C0"] = {k: entry["C1"][k] - entry["C0"][k] for k in ("cosine", "q", "H")}
        pairs.append(entry)
    changes = []
    for source in sources:
        distances = {"semantic": (codes[source, "C0"] ^ codes[source, "C1"]).bit_count(),
                     "instance": (hashes[source, "C0"] ^ hashes[source, "C1"]).bit_count()}
        require(index[f"clean-{source}-C1"]["same_instance_distances"] == distances, "same-source distance mismatch")
        changes.append({"source_id": source, "C0_to_C1_cosine": dot(vectors[source, "C0"], vectors[source, "C1"]),
                        "semantic_bit_flips": distances["semantic"], "instance_bit_flips": distances["instance"]})
    return index, pairs, changes


def analyze(pairs, sources, changes):
    comparisons = []
    for p in pairs:
        if p["label"] != "same":
            continue
        for n in pairs:
            if n["label"] != "different":
                continue
            entry = {"same_pair": p["id"], "different_pair": n["id"]}
            for arm in ("C0", "C1"):
                c = order(p[arm]["cosine"], n[arm]["cosine"])
                q = order(-p[arm]["q"], -n[arm]["q"])
                entry[arm] = {"cosine_order": c, "negative_q_order": q, "strict_reversal": c * q == -1,
                              "coding_order_loss": c > q, "coding_order_gain": c < q,
                              "auc_contribution_difference": (c - q) / 2}
            entry["cosine_order_changed_after_marking"] = entry["C0"]["cosine_order"] != entry["C1"]["cosine_order"]
            entry["q_order_changed_after_marking"] = entry["C0"]["negative_q_order"] != entry["C1"]["negative_q_order"]
            comparisons.append(entry)
    arms = {}
    for arm in ("C0", "C1"):
        groups = {}
        for label in ("same", "different", "uncertain"):
            group = [p[arm] for p in pairs if p["label"] == label]
            groups[label] = {"pairs": len(group), "cosine": describe([p["cosine"] for p in group]),
                             "q": describe([p["q"] for p in group]), "H": describe([p["H"] for p in group]),
                             "q_le_6": sum(p["q_le_6"] for p in group),
                             "q_le_6_and_H_gt_6": sum(p["q_le_6_and_H_gt_6"] for p in group)}
        arms[arm] = {"ranking": rank_stats(pairs, arm), "by_label": groups,
                     "comparison_counts": {k: sum(e[arm][k] for e in comparisons)
                                           for k in ("strict_reversal", "coding_order_loss", "coding_order_gain")}}
    sensitivity = []
    for source in sources:
        retained = omit_source(pairs, source)
        sensitivity.append({"omitted_source": source, "removed_pair_ids": [p["id"] for p in pairs if source in (p["left"], p["right"])],
                            "retained_pairs": len(retained),
                            "label_counts": {label: sum(p["label"] == label for p in retained) for label in ("same", "different", "uncertain")},
                            "C0": rank_stats(retained, "C0"), "C1": rank_stats(retained, "C1")})
    return {"analysis_type": "post-outcome exploratory saved-output reanalysis", "sources": len(sources), "pairs": len(pairs),
            "arms": arms, "source_omission_sensitivity": sensitivity, "same_source_change": changes,
            "same_source_summaries": {k: describe([c[k] for c in changes]) for k in ("C0_to_C1_cosine", "semantic_bit_flips", "instance_bit_flips")},
            "undefined_value_policy": "null with explicit reason; no missing-input imputation or implicit deletion",
            "paired_comparison_dependence": "399 correlated graph comparisons per arm, not independent trials"}, comparisons


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def report(stats):
    lines = ["# Retained v5 semantic geometry", "", "Post-outcome exploratory reanalysis of pinned dev-001; 12 sources, all 66 frozen pairs retained. Seven same and 57 different pairs enter 399 correlated comparisons; two uncertain pairs remain outside binary AUC.", "",
             f"Source run: `{RUN}`; results SHA256 `{EXPECTED}`. Recorded plan: `research/v5-semantic-geometry-analysis-plan-20261003.md`. [provenance.json](provenance.json) records the exact input, plan, script, codec and output hashes.", "",
             "Labels are earlier agent topic assessments, not independent human ground truth. Cosine/q AUC ranks these labels; it does not prove adequacy of q <= 6. No causal interpretation, inferential statistics, projection null model, threshold/seed search or method acceptance is supplied.", "",
             "| Arm | Cosine AUC | Negative-q AUC | Difference | Strict rank reversals |", "| --- | --- | --- | --- | --- |"]
    for arm in ("C0", "C1"):
        s = stats["arms"][arm]
        r = s["ranking"]
        lines.append(f"| {arm} | {r['cosine']['auc']:.9f} | {r['negative_q']['auc']:.9f} | {r['cosine_minus_code_auc']:.9f} | {s['comparison_counts']['strict_reversal']} |")
    primary = stats["arms"]["C0"]["ranking"]["cosine_minus_code_auc"]
    lines.extend(["", "The directional prediction is supported on this fixed cohort." if primary > 0 else "The directional prediction is contradicted (equality or reversal); coding cannot be called the primary bottleneck from this diagnostic.",
                  "A positive difference indicates ordering loss in this coding path and cohort, without establishing an extractor defect, causal mechanism, deployment improvement or generalization.", "",
                  "| Omitted source | Same | Different | Uncertain | C0 AUC difference | C1 AUC difference |", "| --- | --- | --- | --- | --- | --- |"])
    for s in stats["source_omission_sensitivity"]:
        c = s["label_counts"]
        lines.append(f"| {s['omitted_source']} | {c.get('same', 0)} | {c.get('different', 0)} | {c.get('uncertain', 0)} | {s['C0']['cosine_minus_code_auc']} | {s['C1']['cosine_minus_code_auc']} |")
    lines.extend(["", "All twelve omission subsets remove every incident pair. They are descriptive sensitivity checks, not cross-validation, independent studies or an uncertainty interval. Undefined metrics are null with their reason in statistics.json.", "",
                  "The unchanged component coverage q <= 6 and H > 6 is reported by label and arm in statistics.json. Ranking diagnostics do not replace the at-least-five same-pair criterion or other component checks. Original parent-run T3 failures remain in exclusions.json and are absent from this complete T5 component; this analysis does not recover them. Independent human quality/content assessment remains missing.", "",
                  "pairs.json contains every pair and C0/C1 change; comparisons.json contains every same/different ordering comparison; statistics.json contains descriptive summaries and all omission subsets. No images, model calls, GPU work or downloads were used.", ""])
    return "\n".join(lines)


def main():
    started = time.monotonic()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    require(not args.out.exists(), "output must be a fresh directory")
    require(args.out.resolve().is_relative_to((MAIN / ".thesis-build").resolve()), "output must be inside MAIN .thesis-build")
    require(EXPECTED in PLAN.read_text(encoding="utf-8"), "plan no longer pins the declared input")
    require(sha(args.results) == EXPECTED, "pinned results hash mismatch")
    data = json.loads(args.results.read_text(encoding="utf-8"))
    labels = json.loads(LABELS.read_text(encoding="utf-8"))
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    index, pairs, changes = validate_inputs(data, labels, profile)
    stats, comparisons = analyze(pairs, labels["source_ids"], changes)
    failures = [{"id": r["id"], "axis": r["axis"], "status": r.get("status"), "errors": r.get("errors", []),
                 "detector_failures": r.get("detector_failures", [])} for r in index.values() if r.get("status") == "failed" or r.get("errors")]
    exclusions = {"binary_auc_only": [p["id"] for p in pairs if p["label"] == "uncertain"],
                  "binary_auc_reason": "frozen uncertain labels; retained in pairs, coverage and descriptive summaries",
                  "parent_inventory_rows": 617, "parent_failures_preserved": failures,
                  "parent_T3_failures": sum(r["axis"] == "T3" for r in failures),
                  "T5_missing_or_failed": 0, "failure_scope": "parent failures are outside the complete T5 component; none recovered or erased"}
    require(time.monotonic() - started < 120, "analysis timeout before output")
    args.out.mkdir(parents=True, exist_ok=False)
    for name, value in (("statistics.json", stats), ("pairs.json", pairs), ("comparisons.json", comparisons), ("exclusions.json", exclusions)):
        write_json(args.out / name, value)
    (args.out / "analysis-report.md").write_text(report(stats), encoding="utf-8")
    files = [PLAN, PROFILE, LABELS, Path(__file__), ROOT / "scripts/test_v5_semantic_geometry.py",
             ROOT / "scripts/revised_watermark_v5.py", ROOT / "scripts/revised_watermark_v4.py",
             ROOT / "scripts/v5_study_protocol.py", ROOT / "scripts/three_threat_protocol.py"]
    provenance = {"run_id": RUN, "input": {"path": str(args.results.resolve()), "sha256": sha(args.results)},
                  "code_and_plan_inputs": [{"path": str(p.resolve()), "sha256": sha(p)} for p in files],
                  "outputs": {p.name: sha(p) for p in sorted(args.out.iterdir())},
                  "elapsed_seconds": time.monotonic() - started, "timeout_seconds": 120,
                  "feature_validation": "24 vectors; finite 512 values, hashes, normalization, checkpoint, saved-pixel/detection linkage, codes, pair and same-source distances",
                  "image_pixels_reopened": False, "independent_human_labels": False}
    require(provenance["elapsed_seconds"] < 120, "analysis timeout")
    write_json(args.out / "provenance.json", provenance)
    print(json.dumps({"out": str(args.out), "pairs": len(pairs), "comparisons": len(comparisons)}, sort_keys=True))


if __name__ == "__main__":
    main()
