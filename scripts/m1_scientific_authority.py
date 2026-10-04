"""Read-only M1 authority join; never writes decisions or grants raw access.

Trust boundary: the existing Codex Desktop user-message store and real Spec Kit
records on the trusted host. Hashes bind scope; they do not attest a human against
a malicious same-user process. No GPU, network, controller mutation or raw I/O.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, fields
from datetime import datetime, timezone
import hashlib
import importlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sqlite3
import stat
import sys

VERSION = "m1-scientific-authority-v1"
PACKET_VERSION = "m1-scientific-decision-packet-v1"
OFFICIAL_ROOT = "C:/Users/Soroush/.codex/skills/thesis-compute-runner/scripts/_runtime/thesis_agents"
OFFICIAL_PINS = {
    "__init__.py": "f7452c632feb2dcc0ac88862d6502b7ccf4c49894b9a292c6ba6c66af8e0c1e7",
    "compute.py": "4b98e5429d57bda48dbe7b239602b1c7ef60c7cbb19058e17136b29a09437d30",
    "common.py": "0c5bbcba998cf58d76961c4ba62674788d27e50882dd0740e114899ca3b84749",
    "design.py": "363c7f52ef2fa2821c16bcbb9684107fe5b4aeef1328d13bd0c78e050c2c985e",
    "schemas/approval.schema.json": "a4e58ad1dbff5d0135784ea236b1ba2a3f78a5812ddf34f4162f185be9daad33",
    "schemas/execution.schema.json": "bb935080e74a657adb9f23e2c3ed3b9ce93968768bcc13635baac161267d27ed",
    "schemas/gate-decision.schema.json": "b6846ce6e14e279913d3e33b057a5b3a4c234f814d31a4f25e7bad15dd229007",
}
ADOPTIONS = (
    "narrow-coco512-scope-v1", "exact-extracted-annotations-v1",
    "public-owner-seed-v1", "same-code-bounded-recovery-v1",
)
_HASH = re.compile(r"[0-9a-f]{64}\Z")
_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,127}\Z")
_UUID = r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}"
_REF = re.compile(r"codex-user-v1:(" + _UUID + r")/(" + _UUID + r")/(" + _UUID + r")/([0-9a-f]{64})/([0-9a-f]{64})\Z")
_SEAL = object()
MAX_METADATA = 4 * 1024 * 1024
MAX_ROLLOUT_SCAN = 512 * 1024 * 1024


class AuthorityDenied(ValueError):
    def __init__(self, code, detail):
        self.code = code
        super().__init__(f"{code}: {detail}")


def _need(condition, code, detail):
    if not condition:
        raise AuthorityDenied(code, detail)


def object_digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                    ensure_ascii=False, allow_nan=False).encode("utf-8")).hexdigest()


def _json(data):
    def pairs(items):
        out = {}
        for key, value in items:
            _need(key not in out, "malformed_metadata", "Duplicate JSON key")
            out[key] = value
        return out
    def bad(value):
        raise AuthorityDenied("malformed_metadata", "Nonfinite JSON value")
    return json.loads(data, object_pairs_hook=pairs, parse_constant=bad)


def _timestamp(value):
    _need(type(value) is str, "malformed_metadata", "Timestamp must be a string")
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    _need(result.tzinfo is not None, "malformed_metadata", "Timezone required")
    return result


def _hash(value):
    return type(value) is str and _HASH.fullmatch(value) is not None


def _keys(value, names):
    _need(type(value) is dict and set(value) == set(names), "malformed_metadata", "Unexpected or missing fields")


def _path(value):
    value = os.fspath(value)
    if value.startswith("\\\\?\\UNC\\"):
        value = "\\\\" + value[8:]
    elif value.startswith("\\\\?\\"):
        value = value[4:]
    result = Path(value).absolute()
    _need(not any(p.casefold() == "raw" for p in result.parts), "metadata_path", "Raw paths are outside authority scope")
    return result


def _same_path(a, b):
    return os.path.normcase(str(_path(a))) == os.path.normcase(str(_path(b)))


def _safe_path(path, root):
    path, root = _path(path), _path(root)
    _need(path != root and path.is_relative_to(root), "metadata_path", "Path outside fixed metadata root")
    for part in (root, *[root.joinpath(*path.relative_to(root).parts[:i])
                         for i in range(1, len(path.relative_to(root).parts) + 1)]):
        info = part.lstat()
        _need(not stat.S_ISLNK(info.st_mode) and not (getattr(info, "st_file_attributes", 0) & 0x400),
              "metadata_path", "Link/junction/reparse metadata refused")
    info = path.stat()
    _need(stat.S_ISREG(info.st_mode) and info.st_nlink == 1, "metadata_path", "Regular single-link metadata required")
    return path


@contextmanager
def _opened(path, root):
    path = _safe_path(path, root)
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0))
    try:
        from m1_confirmatory_raw_guard import _handle_final_path
        _need(_same_path(_handle_final_path(fd), path), "metadata_path", "Metadata handle was redirected")
        before = os.fstat(fd)
        _need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1, "metadata_path", "Metadata handle is not regular")
        with os.fdopen(fd, "rb", closefd=False) as stream:
            yield stream
    finally:
        os.close(fd)


def _read_bytes(path, root, limit=MAX_METADATA):
    with _opened(path, root) as stream:
        before = os.fstat(stream.fileno())
        _need(before.st_size <= limit, "metadata_size", "Metadata exceeds declared bound")
        content = stream.read(limit + 1)
        after = os.fstat(stream.fileno())
        _need((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) ==
              (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns) and len(content) == before.st_size,
              "metadata_changed", "Metadata changed while read")
        return content


@dataclass(frozen=True, slots=True)
class ExpectedScope:
    scientific_core_sha256: str
    source_contract_sha256: str
    external_index_sha256: str
    schedule_sha256: str
    attempt_plan_sha256: str

    def to_dict(self):
        result = {f.name: getattr(self, f.name) for f in fields(self)}
        _need(all(_hash(v) for v in result.values()), "scope", "Exact scope hashes required")
        return result


@dataclass(frozen=True, slots=True)
class AuthorityPolicy:
    codex_home: str
    trusted_thread_id: str
    creator_identity_sha256: str
    trusted_cwd: str
    controller_project: str
    controller_run_id: str
    controller_workflow_sha256: str
    decision_store_root: str
    artifact_root: str
    official_runtime_root: str = OFFICIAL_ROOT

    def validate(self):
        _need(re.fullmatch(_UUID, self.trusted_thread_id) is not None, "policy", "Fixed root thread required")
        _need(_hash(self.creator_identity_sha256) and _hash(self.controller_workflow_sha256), "policy", "Fixed identity/workflow digests required")
        _need(_ID.fullmatch(self.controller_run_id) is not None, "policy", "Invalid controller run ID")
        for name in ("codex_home", "trusted_cwd", "controller_project", "decision_store_root", "artifact_root", "official_runtime_root"):
            _need(Path(getattr(self, name)).is_absolute(), "policy", "Absolute frozen roots required")
            _path(getattr(self, name))


@dataclass(frozen=True, slots=True, init=False)
class VerifiedAuthority:
    """Parent-only evidence object. to_dict() is audit data, never authority."""
    mode: str
    manifest_sha256: str
    approval_sha256: str
    packet_sha256: str
    scope: ExpectedScope
    output_root: str
    expires_at: str
    run_id: str
    experiment_id: str
    source_ref: str
    actor: str
    controller_run_id: str
    adoption_decision_sha256: str
    compute_decision_sha256: str
    max_seconds_per_attempt: int
    max_seconds_total: int
    max_usd: float
    exceptional_recovery_limit: int
    evidence_receipts: tuple
    _seal: object

    def to_dict(self):
        result = {f.name: getattr(self, f.name) for f in fields(self) if f.name not in ("_seal", "scope", "evidence_receipts")}
        return {"version": VERSION, **result, **self.scope.to_dict(),
                "evidence_receipts": dict(self.evidence_receipts)}


def require_verified_authority(authority, *, scope, manifest_sha256, output_root):
    _need(type(authority) is VerifiedAuthority and getattr(authority, "_seal", None) is _SEAL,
          "authority_type", "Parent-held verified authority object required")
    _need(authority.mode == "host-recorded-user", "fixture_authority", "Fixture evidence cannot authorize science")
    _need(type(scope) is ExpectedScope and authority.scope == scope and authority.manifest_sha256 == manifest_sha256
          and _same_path(authority.output_root, output_root), "authority_scope", "Authority scope differs")
    _need(datetime.now(timezone.utc) < _timestamp(authority.expires_at), "authority_expired", "Authority expired")
    return authority


def _official(root):
    root = _path(root)
    for relative, expected in OFFICIAL_PINS.items():
        _need(hashlib.sha256(_read_bytes(root / relative, root)).hexdigest() == expected,
              "official_runtime_changed", f"Inspected official runtime differs: {relative}")
    name = "_m1_scientific_official_" + hashlib.sha256(str(root).encode()).hexdigest()[:16]
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, root / "__init__.py", submodule_search_locations=[str(root)])
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return importlib.import_module(name + ".compute"), importlib.import_module(name + ".common")


def parse_source_ref(value):
    _need(type(value) is str, "source_ref", "Structured source reference required")
    match = _REF.fullmatch(value)
    _need(match is not None, "source_ref", "Unrecognized source reference; actor text is not evidence")
    return dict(zip(("thread_id", "turn_id", "item_id", "packet_sha256", "message_sha256"), match.groups()))


def _texts(content):
    _need(type(content) is list and bool(content), "user_message", "Text-only explicit user message required")
    _need(all(type(x) is dict and x.get("type") == "text" and type(x.get("text")) is str for x in content),
          "user_message", "Attachments/nontext do not grant approval")
    return "".join(x["text"] for x in content)


def _check_user_evidence(ref, evidence, policy):
    thread, meta, row, event = (evidence[k] for k in ("thread", "session_meta", "item_row", "event"))
    identity = {k: meta.get(k) for k in ("creator_user_id", "creator_account_id")}
    _need(all(type(v) is str and v for v in identity.values()) and object_digest(identity) == policy.creator_identity_sha256,
          "human_identity", "Host creator identity differs")
    _need(ref["thread_id"] == policy.trusted_thread_id and thread["id"] == ref["thread_id"]
          and meta.get("id") == ref["thread_id"] and meta.get("session_id") == ref["thread_id"],
          "human_thread", "Decision is not in the frozen user task")
    for obj in (thread, meta):
        _need(obj.get("thread_source") == "user" and obj.get("source") == "vscode"
              and obj.get("originator") == "Codex Desktop" and obj.get("agent_path") is None
              and _same_path(obj["cwd"], policy.trusted_cwd), "human_thread", "Root desktop user task required")
        _need(all(obj.get(k) == v for k, v in identity.items()), "human_identity", "Host identity stores disagree")
    _need(thread.get("history_mode") == "paginated", "host_format", "Only inspected paginated desktop history is supported")
    _need(row["thread_id"] == ref["thread_id"] and row["turn_id"] == ref["turn_id"]
          and row["item_id"] == ref["item_id"] and row["item_type"] == "userMessage", "user_message", "Not a host user item")
    item = row["item"]
    _need(item.get("type") == "userMessage" and item.get("id") == ref["item_id"]
          and type(item.get("clientId")) is str and re.fullmatch(_UUID, item["clientId"]) is not None,
          "user_message", "Desktop user item/client identity missing")
    payload = event.get("payload", {})
    raw = payload.get("item", {})
    _need(event.get("type") == "event_msg" and event.get("ordinal") == row["rollout_ordinal"]
          and payload.get("type") == "item_completed" and payload.get("thread_id") == ref["thread_id"]
          and payload.get("turn_id") == ref["turn_id"] and raw.get("type") == "UserMessage"
          and raw.get("id") == ref["item_id"] and raw.get("client_id") == item["clientId"],
          "user_event", "Host item and rollout event disagree")
    message = _texts(item.get("content"))
    _need(_texts(raw.get("content")) == message and hashlib.sha256(message.encode("utf-8")).hexdigest() == ref["message_sha256"],
          "user_message", "Actual user-message bytes differ")
    _need(message.strip() in (f"approve M1 {ref['packet_sha256']}", f"تأیید M1 {ref['packet_sha256']}"),
          "no_human_approval", "A continue message or inferred intent is not M1 approval")
    stamp = _timestamp(event["timestamp"])
    _need(abs(int(stamp.timestamp() * 1000) - row["created_at_ms"]) <= 1
          and payload.get("completed_at_ms") == row["created_at_ms"], "user_time", "Host user-event timestamps disagree")
    _need(stamp <= datetime.now(timezone.utc), "user_time", "Future user event refused")
    receipts = {"codex_thread_record_sha256": object_digest(thread), "codex_user_item_sha256": object_digest(row),
                "codex_user_event_sha256": object_digest(event), "creator_identity_sha256": object_digest(identity)}
    return f"codex-user:{identity['creator_user_id']}", stamp, receipts


class _HostEvidence:
    """All lookups are fixed metadata roots; no authority files are created."""
    def __init__(self, policy):
        self.policy = policy

    def approval(self, digest):
        root = _path(self.policy.decision_store_root)
        return _json(_read_bytes(root / digest / "approval.json", root))

    def packet(self, digest):
        root = _path(self.policy.decision_store_root)
        return _json(_read_bytes(root / "packets" / digest / "packet.json", root))

    @contextmanager
    def _db(self, filename):
        root = _path(self.policy.codex_home)
        path = _safe_path(root / filename, root)
        conn = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True, timeout=5)
        try:
            conn.execute("PRAGMA query_only=ON")
            conn.execute("BEGIN")
            conn.row_factory = sqlite3.Row
            yield conn
        finally:
            conn.close()

    def user(self, ref):
        _need(ref["thread_id"] == self.policy.trusted_thread_id, "human_thread", "Unexpected task refused before lookup")
        with self._db("state_5.sqlite") as db:
            row = db.execute("SELECT id,rollout_path,source,thread_source,originator,agent_path,history_mode,cwd,creator_user_id,creator_account_id FROM threads WHERE id=?", (ref["thread_id"],)).fetchone()
        _need(row is not None, "human_thread", "Root task is missing from host store")
        thread = dict(row)
        with self._db("thread_history_1.sqlite") as db:
            row = db.execute("SELECT thread_id,turn_id,item_id,item_type,rollout_ordinal,created_at_ms,item_json FROM thread_items WHERE thread_id=? AND turn_id=? AND item_id=?", (ref["thread_id"], ref["turn_id"], ref["item_id"])).fetchone()
            turn = db.execute("SELECT rollout_byte_offset FROM thread_turns WHERE thread_id=? AND turn_id=?", (ref["thread_id"], ref["turn_id"])).fetchone()
        _need(row is not None and turn is not None, "user_message", "Exact host user item/turn is missing")
        item_row = dict(row)
        _need(len(item_row["item_json"].encode()) <= MAX_METADATA, "metadata_size", "User item too large")
        item_row["item"] = _json(item_row.pop("item_json"))
        root = _path(self.policy.codex_home) / "sessions"
        with _opened(thread["rollout_path"], root) as stream:
            first = _json(stream.readline(MAX_METADATA + 1))
            _need(first.get("type") == "session_meta", "host_format", "Host rollout metadata missing")
            meta = first["payload"]
            offset = turn["rollout_byte_offset"]
            _need(type(offset) is int and 0 <= offset <= os.fstat(stream.fileno()).st_size, "host_format", "Invalid host turn offset")
            if offset:
                stream.seek(offset - 1)
                _need(stream.read(1) == b"\n", "host_format", "Host turn offset is not a record boundary")
            stream.seek(offset)
            scanned = 0
            found = None
            while scanned <= MAX_ROLLOUT_SCAN:
                line = stream.readline(MAX_METADATA + 1)
                if not line:
                    break
                scanned += len(line)
                _need(len(line) <= MAX_METADATA and line.endswith(b"\n"), "host_format", "Incomplete/oversized rollout record")
                event = _json(line)
                ordinal = event.get("ordinal")
                if ordinal == item_row["rollout_ordinal"]:
                    found = event
                    break
                if type(ordinal) is int and ordinal > item_row["rollout_ordinal"]:
                    break
        _need(found is not None, "user_event", "Matching host rollout event unavailable")
        return {"thread": thread, "session_meta": meta, "item_row": item_row, "event": found}

    def controller(self, source_ref):
        root = _path(self.policy.controller_project)
        run = self.policy.controller_run_id
        base = root / ".specify/workflows/runs" / run
        state = _json(_read_bytes(base / "state.json", root))
        inputs = _json(_read_bytes(base / "inputs.json", root))
        workflow_bytes = _read_bytes(base / "workflow.yml", root)
        installed_bytes = _read_bytes(root / ".specify/workflows/thesis-lifecycle/workflow.yml", root)
        # The inspected installed workflow is JSON-compatible YAML. Other YAML
        # encodings need a separately reviewed parser, not an unsafe fallback.
        workflow, installed = _json(workflow_bytes), _json(installed_bytes)
        logs = [_json(line) for line in _read_bytes(base / "log.jsonl", root).splitlines() if line]
        archives = []
        for step in ("plan-acceptance", "compute-approval"):
            paths = sorted((root / ".specify/thesis-decisions").glob(f"{run}-{step}-*.json"))
            _need(len(paths) <= 64, "controller_records", "Ambiguous archive inventory")
            for path in paths:
                decision = _json(_read_bytes(path, root))
                if decision.get("source_ref") == source_ref:
                    archives.append({"filename": path.name, "decision": decision})
        return {"state": state, "inputs": inputs, "workflow": workflow, "installed_workflow": installed,
                "logs": logs, "archives": archives}


def _pre_gate_fingerprint(workflow, run_id, step_id):
    """Reconstruct the supported successful linear controller's pre-gate status."""
    steps = workflow["steps"]
    index = next(i for i, s in enumerate(steps) if s["id"] == step_id)
    step = steps[index]
    data = {"run_id": run_id, "workflow_id": "thesis-lifecycle", "workflow_sha256": object_digest(workflow),
            "status": "paused", "current_step_id": step_id,
            "steps": {s["id"]: "completed" for s in steps[:index]},
            "gate": {"step_id": step_id, "message": step["message"], "options": step["options"], "choice": None}, "error": None}
    data["steps"][step_id] = "paused"
    return object_digest(data)


def _check_controller(evidence, policy, source_ref, actor, user_time, common):
    state, workflow = evidence["state"], evidence["workflow"]
    _need(object_digest(workflow) == policy.controller_workflow_sha256
          and workflow == evidence["installed_workflow"] and workflow["workflow"]["id"] == "thesis-lifecycle",
          "controller_workflow", "Real installed/snapshotted workflow differs")
    _need(state.get("run_id") == policy.controller_run_id and state.get("workflow_id") == "thesis-lifecycle"
          and state.get("status") not in ("failed", "aborted") and state.get("error") is None,
          "controller_state", "Controller run identity/status differs")
    results = state.get("step_results", {})
    _need(results.get("scope-acceptance", {}).get("status") == "completed"
          and results["scope-acceptance"].get("output", {}).get("choice") == "approve",
          "pending_source_adoption", "Existing scope gate is not complete")
    selected = {}
    for step in ("plan-acceptance", "compute-approval"):
        result = results.get(step, {})
        _need(result.get("type") == "gate" and result.get("status") == "completed"
              and result.get("output", {}).get("choice") == "approve"
              and evidence["inputs"].get("inputs", {}).get(step.replace("-", "_") + "_verdict") == "approve",
              "pending_source_adoption" if step == "plan-acceptance" else "pending_compute_gate",
              f"Real {step} has not accepted this package")
        entries = [e for e in evidence["archives"] if e["decision"].get("step_id") == step]
        _need(len(entries) == 1, "controller_archive", "Exactly one matching consumed decision required")
        entry, decision = entries[0], entries[0]["decision"]
        common.validate(decision, "gate-decision")
        digest = object_digest(decision)
        _need(entry["filename"] == f"{policy.controller_run_id}-{step}-{digest}.json"
              and decision["run_id"] == policy.controller_run_id and decision["verdict"] == "approve"
              and decision["source_ref"] == source_ref and decision["actor"] == actor,
              "controller_archive", "Decision archive does not join the actual M1 user event")
        _need(decision["state_sha256"] == _pre_gate_fingerprint(workflow, policy.controller_run_id, step),
              "controller_prestate", "Consumed decision pre-gate fingerprint differs")
        issued, expiry = _timestamp(decision["timestamp"]), _timestamp(decision["expires_at"])
        matches = [x for x in evidence["logs"] if x.get("event") == "step_completed" and x.get("step_id") == step and x.get("status") == "completed"]
        _need(len(matches) == 1 and user_time <= issued <= _timestamp(matches[0]["timestamp"]) < expiry,
              "controller_consumption", "Completed gate log is outside the actual decision interval")
        _need(_timestamp(matches[0]["timestamp"]) <= datetime.now(timezone.utc), "controller_consumption", "Future gate completion")
        selected[step] = digest
    receipts = {"controller_state_sha256": object_digest(state), "controller_log_sha256": object_digest(evidence["logs"]),
                "controller_inputs_sha256": object_digest(evidence["inputs"]), "controller_workflow_sha256": object_digest(workflow)}
    return selected, receipts


def _check_packet(packet, digest, manifest, policy, scope):
    _keys(packet, ("version", "scope", "controller", "adoptions", "execution_manifests", "limits", "expires_at"))
    _need(packet["version"] == PACKET_VERSION and object_digest(packet) == digest, "packet", "Decision packet identity differs")
    _need(packet["scope"] == scope.to_dict() and packet["adoptions"] == list(ADOPTIONS), "packet_scope", "Required exact source/method amendments not adopted")
    _need(packet["controller"] == {"run_id": policy.controller_run_id, "workflow_id": "thesis-lifecycle",
                                   "workflow_sha256": policy.controller_workflow_sha256,
                                   "adoption_step_id": "plan-acceptance", "compute_step_id": "compute-approval"},
          "packet_controller", "Packet controller mapping differs")
    items = packet["execution_manifests"]
    _need(type(items) is list and 0 < len(items) <= 10000, "packet", "Finite manifest batch required")
    for item in items:
        _keys(item, ("run_id", "sha256", "max_seconds", "max_usd"))
        _need(type(item["run_id"]) is str and _ID.fullmatch(item["run_id"]) is not None and _hash(item["sha256"])
              and type(item["max_seconds"]) is int and 0 < item["max_seconds"] <= 3600
              and type(item["max_usd"]) in (int, float) and item["max_usd"] == 0,
              "packet", "Invalid manifest batch entry")
    _need(len({x["run_id"] for x in items}) == len(items) == len({x["sha256"] for x in items}), "packet", "Duplicate manifest batch entry")
    found = [x for x in items if x["run_id"] == manifest["run_id"] and x["sha256"] == object_digest(manifest)]
    _need(len(found) == 1 and found[0]["max_seconds"] == manifest["budget"]["max_seconds"]
          and found[0]["max_usd"] == manifest["budget"]["max_usd"], "packet_manifest", "Exact execution is absent from the user-approved batch")
    limits = packet["limits"]
    _keys(limits, ("max_seconds_per_attempt", "max_seconds_total", "max_usd", "exceptional_recovery_limit"))
    _need(type(limits["max_seconds_per_attempt"]) is int and 0 < limits["max_seconds_per_attempt"] <= 3600
          and all(x["max_seconds"] <= limits["max_seconds_per_attempt"] for x in items)
          and type(limits["max_seconds_total"]) is int and limits["max_seconds_total"] >= limits["max_seconds_per_attempt"]
          and type(limits["max_usd"]) in (int, float) and limits["max_usd"] == 0
          and type(limits["exceptional_recovery_limit"]) is int
          and 0 <= limits["exceptional_recovery_limit"] <= 2, "packet_budget", "Invalid local aggregate/recovery budget")
    return limits


def _verify(manifest, envelope, output_root, policy, scope, evidence, *, mode):
    """Shared CPU algebra; production constructs its own host evidence provider."""
    policy.validate()
    _need(type(scope) is ExpectedScope, "scope", "Typed immutable expected scope required")
    scope.to_dict()
    official, common = _official(policy.official_runtime_root)
    common.validate(manifest, "execution")
    digest = object_digest(manifest)
    _need(manifest["execution_target"] == "local" and manifest["budget"]["max_usd"] == 0
          and manifest["budget"]["hourly_usd"] == 0, "target", "Only the frozen local USD0 route is supported")
    expected_output = _path(policy.artifact_root) / manifest["stage_id"] / manifest["run_id"]
    _need(_same_path(output_root, expected_output), "output_scope", "Unexpected official output destination")
    _need(envelope.get("status") == "running" and envelope.get("git_dirty") is False
          and envelope.get("executor") == "thesis-agents-1.0.0"
          and envelope.get("execution_manifest_sha256") == digest
          and all(envelope.get(k) == manifest[k] for k in ("run_id", "stage_id", "task_id", "experiment_id", "execution_target", "git_commit")),
          "official_envelope", "Dispatcher launch envelope mismatch")
    approval = evidence.approval(digest)
    official.approval_check(approval, manifest)  # Unchanged installed official check.
    _need(envelope.get("approval_reference") == object_digest(approval), "official_envelope", "Official approval receipt differs")
    _need(_timestamp(approval["timestamp"]) <= _timestamp(envelope["started_at"]) < _timestamp(approval["expires_at"])
          and _timestamp(envelope["started_at"]) <= datetime.now(timezone.utc),
          "official_envelope", "Dispatcher start is outside the real approval interval")
    ref = parse_source_ref(approval["source_ref"])
    packet = evidence.packet(ref["packet_sha256"])
    limits = _check_packet(packet, ref["packet_sha256"], manifest, policy, scope)
    actor, user_time, receipts = _check_user_evidence(ref, evidence.user(ref), policy)
    _need(approval["actor"] == actor and user_time <= _timestamp(approval["timestamp"]),
          "approval_origin", "Approval predates or misattributes the actual user event")
    _need(_timestamp(approval["expires_at"]) <= _timestamp(packet["expires_at"]), "approval_expiry", "Approval exceeds the adopted packet expiry")
    decisions, controller_receipts = _check_controller(evidence.controller(approval["source_ref"]), policy,
                                                      approval["source_ref"], actor, user_time, common)
    result = object.__new__(VerifiedAuthority)
    values = dict(mode=mode, manifest_sha256=digest, approval_sha256=object_digest(approval), packet_sha256=ref["packet_sha256"],
                  scope=scope, output_root=str(expected_output), expires_at=approval["expires_at"], run_id=manifest["run_id"],
                  experiment_id=manifest["experiment_id"], source_ref=approval["source_ref"], actor=actor,
                  controller_run_id=policy.controller_run_id, adoption_decision_sha256=decisions["plan-acceptance"],
                  compute_decision_sha256=decisions["compute-approval"], **limits,
                  evidence_receipts=tuple(sorted((receipts | controller_receipts).items())), _seal=_SEAL)
    for key, value in values.items():
        object.__setattr__(result, key, value)
    return result


def verify_authority(manifest_path, output_root, *, policy, scope):
    """Verify genuine future decisions; read-only and intentionally no CLI issuer.

    The caller must obtain policy/scope from its hash-bound frozen launch contract,
    not command-line overrides. Missing future decisions fail normally, not via a
    permanent stub. This receipt alone never opens data or advances a gate.
    """
    try:
        _need(type(policy) is AuthorityPolicy, "policy", "Typed frozen authority policy required")
        policy.validate()
        output = _path(output_root)
        _need(_same_path(manifest_path, output / "execution-manifest.json"), "official_envelope", "Exact official manifest path required")
        manifest = _json(_read_bytes(manifest_path, policy.artifact_root))
        envelope = _json(_read_bytes(output / "manifest.json", policy.artifact_root))
        return _verify(manifest, envelope, output, policy, scope, _HostEvidence(policy), mode="host-recorded-user")
    except AuthorityDenied:
        raise
    except FileNotFoundError as exc:
        raise AuthorityDenied("pending_authority", "Required real decision/controller metadata is absent") from exc
    except (ValueError, TypeError, KeyError, StopIteration, OSError, sqlite3.Error) as exc:
        raise AuthorityDenied("invalid_authority", f"Metadata verification failed ({type(exc).__name__})") from exc
