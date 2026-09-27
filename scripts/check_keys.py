"""C6 strict metadata-only pair preview. Scientific execution is not wired.

The library supports owned/precomputed fixtures. A real extraction runner must
still pin data/code/environment and receive exact compute approval separately.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.signatures.key_study import Sample, Pair, validate_plan, dependency_components


def no_duplicates(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def preview(payload: bytes):
    if len(payload) > 2*1024*1024:
        raise ValueError("pair plan exceeds 2 MiB")
    plan = json.loads(payload, object_pairs_hook=no_duplicates,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite JSON")))
    if not isinstance(plan, dict) or set(plan) != {"schema_version", "samples", "pairs"}:
        raise ValueError("strict pair plan fields required")
    if plan["schema_version"] != "c6-pair-preview-v1":
        raise ValueError("unsupported pair plan schema")
    if not isinstance(plan["samples"], list) or not isinstance(plan["pairs"], list):
        raise ValueError("pair and sample arrays required")
    sample_fields = {"sample_id", "source_uid", "group_id", "domain", "variant", "split"}
    pair_fields = {"pair_id", "left", "right", "left_owner", "right_owner", "relation", "evidence_ref"}
    for entries, expected in ((plan["samples"], sample_fields), (plan["pairs"], pair_fields)):
        if any(not isinstance(item, dict) or set(item) != expected for item in entries):
            raise ValueError("strict inventory row fields required")
    samples = [Sample(**item) for item in plan["samples"]]
    pairs = [Pair(**item) for item in plan["pairs"]]
    validate_plan(samples, pairs)
    components = dependency_components(samples, pairs)
    return {"status": "metadata_preview_only", "scientific_compute_authorized": False,
            "extraction_adapter": "NOT_IMPLEMENTED", "sample_count": len(samples),
            "pair_count": len(pairs), "source_count": len({s.source_uid for s in samples}),
            "dependence_component_count": len(set(components.values())),
            "independent_n": None, "plan_bytes_sha256": hashlib.sha256(payload).hexdigest()}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--preview", action="store_true", required=True)
    args = parser.parse_args(argv)
    try:
        # Fixed read cap; no directory discovery, study pixels, model or writes.
        with args.plan.open("rb") as handle:
            payload = handle.read(2*1024*1024+1)
        print(json.dumps(preview(payload), sort_keys=True, allow_nan=False))
        return 0
    except (ValueError, TypeError, OSError, UnicodeError) as error:
        print(json.dumps({"status": "invalid_plan", "scientific_compute_authorized": False,
                          "error": str(error)}, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
