"""Metadata-only recovery schedule and receipt conformance reference.

Not an execution entrypoint, dispatcher, live monitor or lifecycle controller.
No model imports, image decoding, scientific calculations or approval records.
"""
import math
from collections import defaultdict, deque
from v4_study_protocol import RUN, claims, inventory


def make_schedule(snapshot, labels):
    if snapshot.get("run_id") != RUN:
        raise ValueError("wrong source run")
    rows = snapshot["rows"]
    expected = inventory(labels)
    lookup = {row["id"]: row for row in rows}
    if len(lookup) != len(rows) or set(lookup) != {r["id"] for r in expected}:
        raise ValueError("duplicate, missing or unexpected source rows")
    for wanted in expected:
        row = lookup[wanted["id"]]
        if any(k not in row or row[k] != value for k, value in wanted.items()):
            raise ValueError("frozen recipe changed: " + row["id"])
    # Parent T3 execution is sequential, but had no durable attempt-start record.
    # The first NOT_RUN cell may have been in flight; only its downstream suffix
    # is known unreached under that verified path. Never infer this from status alone.
    ordered_t3 = [lookup[r["id"]] for r in expected if r["axis"] == "T3"]
    pending = [i for i, row in enumerate(ordered_t3) if row["status"] == "NOT_RUN"]
    ambiguous = None
    if pending:
        first = pending[0]
        if any(row["status"] != "NOT_RUN" or row.get("image") for row in ordered_t3[first:]):
            raise ValueError("parent sequential checkpoint boundary not established")
        ambiguous = ordered_t3[first]["id"]
    buckets = defaultdict(lambda: defaultdict(list))
    kinds = {}
    for row in rows:
        axis = row["axis"]
        if row.get("image"):
            if row.get("errors"):
                raise ValueError("unexpected saved-row failure requires manual classification")
            kind = "evaluate_saved"
        elif axis == "T3" and row["status"] == "failed":
            errors = row.get("errors", [])
            if not errors or any(e.get("message") != "safety_checker_blocked_output" for e in errors):
                raise ValueError("unclassified failure; never automatically retry")
            kind = "retain_safety_failure"
        elif axis == "T3" and row["status"] == "NOT_RUN":
            kind = "pending_attempt_disposition" if row["id"] == ambiguous else "generate_then_evaluate"
        elif axis == "T5" and row["status"] == "NOT_RUN":
            kind = "compare_components"
        else:
            raise ValueError("unexpected row state")
        kinds[row["id"]] = kind
        if axis == "clean":
            group = str(row["source_id"])
            phase = "clean_evaluation"
        elif axis == "T3":
            group = str((row["source_id"], row["dose"], row["strength"], row["seed"]))
            phase = ("attempt_quarantine" if kind == "pending_attempt_disposition" else
                     "new_generation" if kind == "generate_then_evaluate" else "T3_recovered")
        elif axis == "T5":
            group = row["id"]
            phase = "T5_components"
        else:
            group = str((row["donor_id"], row["recipient_id"]))
            phase = axis + "_recovered"
        buckets[phase][group].append(row["id"])

    def units(phase):
        return [{"unit_id":phase+"-"+str(i+1).zfill(3), "phase":phase,
                 "row_ids": sorted(ids), "actions":{identity:kinds[identity] for identity in sorted(ids)}}
                for i, (_,ids) in enumerate(sorted(buckets[phase].items()))]

    scheduled = units("clean_evaluation")
    queues = [deque(units(p)) for p in
              ("T4_recovered","T5_components","T5-transfer_recovered","T3_recovered")]
    while any(queues):
        for queue in queues:
            if queue:
                scheduled.append(queue.popleft())
    scheduled.extend(units("new_generation"))
    scheduled.extend(units("attempt_quarantine"))
    inherited_calls = 0
    for row in rows:
        if row["axis"] == "clean":
            detections = row.get("detections", [])
            if not row.get("detection_complete") or len(detections) != 4:
                raise ValueError("clean inherited call evidence incomplete")
            if [(d["claimed_owner"],d["binding_mode"],d["result"]["owners_tested"]) for d in detections] != claims(row):
                raise ValueError("clean roster evidence changed")
            inherited_calls += len(detections)
        elif row.get("detections"):
            raise ValueError("unexpected new scientific evidence; snapshot needs new review")
    return {"status":"DESIGN_ONLY_NOT_EXECUTABLE", "source_run_id":RUN,
            "units":scheduled, "planned_rows":len(rows),
            "planned_detector_calls":sum(len(claims(row)) for row in rows),
            "inherited_detector_calls":inherited_calls,
            "new_detector_calls_if_safe":sum(len(claims(row)) for row in rows
                if row["axis"]!="clean" and kinds[row["id"]] not in
                ("retain_safety_failure","compare_components","pending_attempt_disposition")),
            "known_missing_detector_calls":sum(len(claims(row)) for row in rows
                if kinds[row["id"]]=="retain_safety_failure"),
            "unresolved_detector_calls":sum(len(claims(row)) for row in rows
                if kinds[row["id"]]=="pending_attempt_disposition"),
            "ambiguous_attempt_row_id":ambiguous,
            "downstream_classification_basis":"Verified parent sequential T3 loop and terminal checkpoint prefix; not NOT_RUN alone",
            "action_counts":{kind:sum(value==kind for value in kinds.values()) for kind in sorted(set(kinds.values()))}}


def validate_design_receipt(unit, records):
    """Validate simulated completion fields; real adapters must verify all bytes.

    This reference cannot authenticate callers or replace exact artifact review.
    Each evaluated image needs its own detector and quality results, including
    both source and immediate reference roles for regeneration.
    """
    observed = {record["id"]:record for record in records}
    if len(observed)!=len(records) or set(observed)!=set(unit["row_ids"]):
        raise ValueError("incomplete or duplicate completion records")
    for identity in unit["row_ids"]:
        kind = unit["actions"][identity]
        record = observed[identity]
        if kind == "pending_attempt_disposition":
            raise ValueError("ambiguous parent attempt cannot seal or retry without explicit reviewed disposition")
        elif kind == "generate_then_evaluate" and record.get("status") == "NEW_SAFETY_BLOCKED":
            validate_new_safety_receipt(identity, record)
        elif kind == "retain_safety_failure":
            if record.get("status")!="INHERITED_SAFETY_BLOCKED" or not record.get("source_failure_sha256"):
                raise ValueError("known failure must remain bound and terminal")
        elif kind == "compare_components":
            if record.get("status")!="COMPARED" or not record.get("component_artifact_sha256"):
                raise ValueError("component evidence missing")
        else:
            if record.get("status")!="EVALUATED" or record.get("detector_calls")!=4:
                raise ValueError("generation alone is not completion")
            if not record.get("image_sha256") or not record.get("feature_pixel_binding_verified"):
                raise ValueError("saved-suspect binding missing")
            references = ("quality_source","quality_immediate") if identity.startswith(("t3-","vae-")) else ("quality",)
            for reference in references:
                quality = record.get(reference, {})
                for metric in ("psnr","ssim","lpips"):
                    value = quality.get(metric)
                    if metric=="psnr" and value is None and quality.get("identical_pixels") is True:
                        continue
                    if type(value) not in (int,float) or not math.isfinite(value):
                        raise ValueError("missing or nonfinite quality result")
    return True


def validate_new_safety_receipt(identity, record):
    """Shape/binding conformance only; production must verify durable receipt bytes."""
    start = record.get("attempt_start", {})
    failure = record.get("failure", {})
    def digest(value):
        return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)
    if (start.get("row_id") != identity or not start.get("attempt_id") or
        failure.get("row_id") != identity or failure.get("attempt_id") != start.get("attempt_id")):
        raise ValueError("new safety failure lacks matching attempt identity")
    for field in ("receipt_sha256", "recipe_sha256", "input_sha256"):
        if not digest(start.get(field)):
            raise ValueError("durable attempt-start binding missing")
    if (not digest(failure.get("receipt_sha256")) or
        failure.get("attempt_start_sha256") != start["receipt_sha256"] or
        failure.get("recipe_sha256") != start["recipe_sha256"] or
        failure.get("input_sha256") != start["input_sha256"] or
        failure.get("message") != "safety_checker_blocked_output"):
        raise ValueError("new safety failure provenance incomplete")
    if (record.get("detector_calls") != 0 or record.get("missing_detector_calls") != 4 or
        record.get("scientific_success") is not False or record.get("image_sha256") is not None):
        raise ValueError("safety rejection must remain zero-output, missing-call evidence, not success")
    return True


def observed_liveness(receipt_status, owner_alive, heartbeat_age_seconds):
    if receipt_status != "running":
        return receipt_status
    if not owner_alive:
        return "INTERRUPTED_OBSERVED_CAUSE_UNKNOWN"
    if heartbeat_age_seconds is None or heartbeat_age_seconds > 120:
        return "STALLED_NEEDS_CHECK"
    return "RUNNING_OBSERVED"
