"""Model-free durable per-step evidence journal; not an approval/controller."""
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def object_sha(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def file_sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def atomic_json(path, value):
    """Single-writer atomic replace, with durable file and directory flush on Linux."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".pending-", delete=False) as stream:
        stream.write(encoded(value))
        stream.flush()
        os.fsync(stream.fileno())
        temporary = stream.name
    os.replace(temporary, path)
    if os.name == "posix":
        descriptor = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)


class Journal:
    """Immutable records within a single-writer directory, with checksum envelopes.

    Reopening in tests demonstrates byte recovery only. Scientific recovery still
    needs a separately exact-approved package, never a consumed run approval.
    """
    def __init__(self, root, manifest_sha256):
        self.root = Path(root)
        self.binding = manifest_sha256
        self.root.mkdir(parents=True, exist_ok=True)

    def path(self, row, step):
        for token in (row, step):
            if not re.fullmatch(r"[A-Za-z0-9_.-]+", token) or token in (".", ".."):
                raise ValueError("invalid journal identity")
        path = self.root / row / (step + ".json")
        if not path.resolve().is_relative_to(self.root.resolve()) or path.is_symlink():
            raise ValueError("journal path escapes root")
        return path

    def get(self, row, step):
        path = self.path(row, step)
        if not path.exists():
            return None
        item = json.loads(path.read_text())
        if (not isinstance(item,dict) or
            set(item) != {"row_id","step","manifest_sha256","value","value_sha256"} or
            not isinstance(item["value"],dict)):
            raise ValueError("journal envelope/payload must have the declared object shape")
        if (item.get("row_id"), item.get("step"), item.get("manifest_sha256")) != (row, step, self.binding):
            raise ValueError("journal identity/binding changed")
        if object_sha(item["value"]) != item["value_sha256"]:
            raise ValueError("journal payload checksum changed")
        return item["value"]

    def put(self, row, step, value):
        previous = self.get(row, step)
        if previous is not None:
            if previous != value:
                raise ValueError("immutable evidence conflict")
            return value
        atomic_json(self.path(row, step), {"row_id":row, "step":step,
                    "manifest_sha256":self.binding, "value":value, "value_sha256":object_sha(value)})
        return value

    def seal(self, unit, records):
        from v4_recovery_design import validate_design_receipt
        validate_design_receipt(unit, records)
        dependencies = []
        for identity in unit["row_ids"]:
            # Each row's terminal result is a required, independently hashed input.
            if self.get(identity, "complete") != next(r for r in records if r["id"] == identity):
                raise ValueError("terminal row receipt missing or changed")
            for path in sorted(self.path(identity, "complete").parent.glob("*.json")):
                self.get(identity, path.stem)
                dependencies.append({"path":path.relative_to(self.root).as_posix(), "sha256":file_sha(path)})
        return self.put(unit["unit_id"], "seal", {"unit_sha256":object_sha(unit), "dependencies":dependencies})

    def verified_seal(self, unit):
        seal = self.get(unit["unit_id"], "seal")
        if seal is None:
            return False
        if seal["unit_sha256"] != object_sha(unit):
            raise ValueError("unit recipe changed")
        for item in seal["dependencies"]:
            path = self.root / item["path"]
            if not path.resolve().is_relative_to(self.root.resolve()) or file_sha(path) != item["sha256"]:
                raise ValueError("sealed dependency corrupted")
        from v4_recovery_design import validate_design_receipt
        validate_design_receipt(unit, [self.get(identity, "complete") for identity in unit["row_ids"]])
        return True


def evaluate_row(row, action, journal, adapter, hook=lambda *_:None, progress=lambda *_:None):
    """Persist each boundary; the adapter has no generation capability."""
    identity = row["id"]
    progress(identity,"row-start")
    complete = journal.get(identity, "complete")
    if complete is not None:
        return complete
    if action == "retain_safety_failure":
        complete = {"id":identity, "status":"INHERITED_SAFETY_BLOCKED",
                    "source_failure_sha256":object_sha(row), "detector_calls":0,
                    "missing_detector_calls":4, "parent_evidence":row}
    elif action == "compare_components":
        progress(identity,"components-start")
        result = journal.get(identity, "components")
        if result is None:
            result = journal.put(identity, "components", adapter.components(row))
        hook(identity, "components")
        complete = {"id":identity, "status":"COMPARED", "component_artifact_sha256":object_sha(result),
                    "components":result, "detector_calls":0}
    elif action == "evaluate_saved":
        # Check the original image bytes again even when partial evidence is reused.
        progress(identity,"image-start")
        image = adapter.image(row)
        prior = journal.get(identity, "image")
        if prior is not None and prior != image:
            raise ValueError("saved image changed since partial evaluation")
        journal.put(identity, "image", image)
        hook(identity, "image")
        feature = journal.get(identity, "feature")
        progress(identity,"feature-start")
        if feature is None:
            feature = journal.put(identity, "feature", adapter.feature(row, image))
        adapter.verify_feature(row, image, feature)
        hook(identity, "feature")
        calls = []
        for slot, claim in enumerate(adapter.claims(row)):
            step = "call-" + str(slot)
            progress(identity,step+"-start")
            result = journal.get(identity, step)
            if result is None:
                result = journal.put(identity, step, adapter.detect(row, image, feature, claim, slot))
            adapter.verify_call(row, image, claim, result, slot)
            calls.append(result)
            hook(identity, step)
        scores = journal.get(identity, "quality")
        progress(identity,"quality-start")
        if scores is None:
            scores = journal.put(identity, "quality", adapter.quality(row, image))
        hook(identity, "quality")
        complete = {"id":identity, "status":"EVALUATED", "detector_calls":len(calls),
                    "image_sha256":image["sha256"], "pixel_sha256":image["pixel_sha256"],
                    "feature_pixel_binding_verified":True, "feature":feature, "detections":calls,
                    "parent_evidence":row, **scores}
    else:
        raise ValueError("evaluation-only package cannot generate or resolve ambiguous attempts")
    journal.put(identity, "complete", complete)
    hook(identity, "complete")
    return complete


def evaluate_units(units, rows, journal, adapter, guard=lambda:None, hook=lambda *_:None, progress=lambda *_:None):
    completed = []
    for unit in units:
        guard()
        if journal.verified_seal(unit):
            completed.append(unit["unit_id"])
            continue
        records = []
        for identity in unit["row_ids"]:
            guard()
            records.append(evaluate_row(rows[identity], unit["actions"][identity], journal, adapter, hook, progress))
        journal.seal(unit, records)
        hook(unit["unit_id"], "seal")
        completed.append(unit["unit_id"])
    return completed


def summarize_journal(units, journal, tolerate_corruption=False):
    """Partial calls are evidence, never evaluated rows; tolerate only for final diagnostics."""
    observed, sealed, partial, errors = [], [], [], []
    def checked(function, identity):
        try:
            return function()
        except (ValueError,OSError,KeyError,TypeError,AttributeError,json.JSONDecodeError) as error:
            if not tolerate_corruption:
                raise
            errors.append({"identity":identity,"type":type(error).__name__,"message":str(error)})
            return None
    def terminal(unit, identity):
        value = journal.get(identity,"complete")
        if value is None:
            return None
        from v4_recovery_design import validate_design_receipt
        single = {"row_ids":[identity],"actions":{identity:unit["actions"][identity]}}
        validate_design_receipt(single,[value])
        detections = value.get("detections",[])
        if not isinstance(detections,list) or any(not isinstance(call,dict) for call in detections):
            raise ValueError("terminal detector evidence has malformed shape")
        if value["status"] == "EVALUATED" and len(detections) != 4:
            raise ValueError("terminal detector receipt inventory incomplete")
        return value
    for unit in units:
        if checked(lambda:journal.verified_seal(unit),unit["unit_id"]):
            sealed.append(unit["unit_id"])
        for identity in unit["row_ids"]:
            value = checked(lambda:terminal(unit,identity),identity)
            if value is not None:
                observed.append(value)
            else:
                calls = [value for slot in range(4)
                         if (value:=checked(lambda:journal.get(identity,"call-"+str(slot)),identity)) is not None]
                partial.append({"id":identity,"detector_calls":calls,
                    "feature_recorded":checked(lambda:journal.get(identity,"feature"),identity) is not None,
                    "quality_recorded":checked(lambda:journal.get(identity,"quality"),identity) is not None})
    calls = [c for row in observed for c in row.get("detections",[])]
    calls += [c for row in partial for c in row["detector_calls"]]
    return {"rows":observed,"sealed_units":sealed,"partial_rows":partial,"integrity_errors":errors,
            "completed_detector_calls":len(calls),
            "inherited_detector_calls":sum(c.get("inherited") is True for c in calls),
            "new_detector_calls":sum(c.get("inherited") is not True for c in calls)}
