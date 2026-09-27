"""Bounded C6 recorded-observation replay, not extraction or approval evidence.

Expected digest and frozen typed plan/seed must come from a trusted external
record. A self-supplied digest proves nothing about image or model custody.
"""
import hashlib
import json
import re
from dataclasses import asdict

from .key_study import KeyStudyError, Observation, evaluate, summarize, validate_plan

MAX_BYTES = 8 * 1024 * 1024


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def plan_digest(samples, pairs):
    validate_plan(samples, pairs)
    return hashlib.sha256(canonical({"samples": [asdict(s) for s in samples],
                                     "pairs": [asdict(p) for p in pairs]})).hexdigest()


def _unique(items):
    result = {}
    for key, value in items:
        if key in result:
            raise KeyStudyError("duplicate JSON field")
        result[key] = value
    return result


def _hex(value, length):
    if type(value) is not str or re.fullmatch(r"[0-9a-f]{%d}" % length, value) is None:
        raise KeyStudyError("exact lowercase hexadecimal required")
    return bytes.fromhex(value)


def read_results(payload, *, expected_sha256, samples, pairs, projection_seed):
    """Recompute every saved row before descriptive summarization.

All sample statuses must be explicit, including pending and failed. This
checks mathematical consistency with recorded observations, NOT that those
observations are genuine image extractions. No file access or model loading.
"""
    index = validate_plan(samples, pairs)
    if type(projection_seed) is not bytes or len(projection_seed) != 32:
        raise KeyStudyError("externally bound 32-byte seed required")
    _hex(expected_sha256, 64)
    if type(payload) is not bytes or not payload or len(payload) > MAX_BYTES:
        raise KeyStudyError("bounded immutable result bytes required")
    if hashlib.sha256(payload).hexdigest() != expected_sha256:
        raise KeyStudyError("external result digest mismatch")
    try:
        data = json.loads(payload, object_pairs_hook=_unique,
                          parse_constant=lambda value: (_ for _ in ()).throw(
                              KeyStudyError("nonfinite JSON forbidden")))
        if type(data) is not dict or set(data) != {
                "schema_version", "plan_sha256", "projection_seed", "observations", "rows"}:
            raise KeyStudyError("exact result envelope required")
        if data["schema_version"] != "c6-recorded-results-v1":
            raise KeyStudyError("unknown result version")
        if data["plan_sha256"] != plan_digest(samples, pairs):
            raise KeyStudyError("frozen plan mismatch")
        if _hex(data["projection_seed"], 64) != projection_seed:
            raise KeyStudyError("frozen seed mismatch")
        records = data["observations"]
        if type(records) is not dict or set(records) != set(index):
            raise KeyStudyError("complete explicit sample status inventory required")
        observations = {}
        for sample_id, record in records.items():
            if type(record) is not dict or set(record) != {"status", "features", "phash", "error"}:
                raise KeyStudyError("exact observation fields required")
            features = record["features"]
            if features is not None and (type(features) is not list or len(features) != 512):
                raise KeyStudyError("512 recorded features required")
            observations[sample_id] = Observation(
                record["status"], tuple(features) if features is not None else None,
                _hex(record["phash"], 8) if record["phash"] is not None else None,
                record["error"])
        rows = evaluate(samples, pairs, observations, projection_seed)
        # Canonical comparison distinguishes bool/int, null/zero, integer/float,
        # extra fields, ordering, dropped failures, relabeling and all distances.
        if type(data["rows"]) is not list or canonical(data["rows"]) != canonical(rows):
            raise KeyStudyError("saved rows do not exactly replay frozen inventory")
    except (ValueError, TypeError, KeyError, RecursionError, OverflowError) as exc:
        raise KeyStudyError("invalid saved result: " + str(exc)[:256]) from exc
    return {"rows": rows, "summary": summarize(rows),
            "result_sha256": expected_sha256, "plan_sha256": data["plan_sha256"],
            "extraction_custody": "NOT_ESTABLISHED", "scientific_acceptance": False}
