"""Generated metadata only. Approval/gate dictionaries never become JSON files.

The positive algebra path returns fixture-mode authority, which the production
consumer rejects. SQLite/rollout fixtures describe a synthetic desktop user only.
No existing task event, controller gate, approval store or scientific raw is changed.
"""
from copy import deepcopy
from contextlib import closing
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import m1_scientific_authority as auth


class MemoryEvidence:
    def __init__(self, approval, packet, user, controller):
        self.a, self.p, self.u, self.c = approval, packet, user, controller
        self.calls = []

    def approval(self, digest):
        self.calls.append(("approval", digest))
        return deepcopy(self.a)

    def packet(self, digest):
        self.calls.append(("packet", digest))
        return deepcopy(self.p)

    def user(self, ref):
        self.calls.append(("user", ref["item_id"]))
        return deepcopy(self.u)

    def controller(self, ref):
        self.calls.append(("controller", ref))
        return deepcopy(self.c)


class AuthorityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="m1-authority-fixture-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.now = datetime.now(timezone.utc).replace(microsecond=0)
        self.iso = lambda seconds: (self.now + timedelta(seconds=seconds)).isoformat()
        self.thread_id = "11111111-1111-7111-8111-111111111111"
        self.turn_id = "22222222-2222-7222-8222-222222222222"
        self.item_id = "33333333-3333-7333-8333-333333333333"
        self.client_id = "44444444-4444-7444-8444-444444444444"
        self.identity = {"creator_user_id": "SYNTHETIC-FIXTURE-USER", "creator_account_id": "SYNTHETIC-FIXTURE-ACCOUNT"}
        self.actor = "codex-user:" + self.identity["creator_user_id"]
        self.workflow = {"workflow": {"id": "thesis-lifecycle"}, "steps": [
            {"id": "scope-acceptance", "type": "gate", "message": "Fixture scope", "options": ["approve", "reject"]},
            {"id": "plan-acceptance", "type": "gate", "message": "Fixture plan", "options": ["approve", "reject"]},
            {"id": "implementation", "type": "prompt"},
            {"id": "compute-approval", "type": "gate", "message": "Fixture compute", "options": ["approve", "reject"]},
        ]}
        self.scope = auth.ExpectedScope(*[c * 64 for c in "12345"])
        self.policy = auth.AuthorityPolicy(str(self.root / "codex"), self.thread_id, auth.object_digest(self.identity),
            str(self.root / "project"), str(self.root / "project"), "fixture-run", auth.object_digest(self.workflow),
            str(self.root / "decision-store"), str(self.root / "artifacts"))
        self.manifest = {"schema_version": "1.0", "experiment_id": "fixture-only", "run_id": "fixture-attempt-0",
            "stage_id": "fixture-stage", "task_id": "fixture-task", "execution_target": "local",
            "reviewed_script": "scripts/fixture_only.py", "script_sha256": "a" * 64, "git_commit": "b" * 40,
            "seeds": [0], "datasets": [{"id": "generated-only", "version": "fixture-v1", "license": "generated", "split": "synthetic"}],
            "inputs": [{"path": "research/fixture-only.json", "sha256": "c" * 64}],
            "outputs": ["outputs/fixture-receipt.json"], "metrics": ["fixture-metric"],
            "budget": {"max_seconds": 60, "max_usd": 0, "hourly_usd": 0},
            "resources": {"vram_mib": 0, "ram_mib": 256, "disk_mib": 10}, "cleanup_policy": "stop-for-recovery"}
        self.output = Path(self.policy.artifact_root) / self.manifest["stage_id"] / self.manifest["run_id"]
        self.packet = {"version": auth.PACKET_VERSION, "scope": self.scope.to_dict(),
            "controller": {"run_id": self.policy.controller_run_id, "workflow_id": "thesis-lifecycle",
                           "workflow_sha256": self.policy.controller_workflow_sha256,
                           "adoption_step_id": "plan-acceptance", "compute_step_id": "compute-approval"},
            "adoptions": list(auth.ADOPTIONS), "execution_manifests": [{"run_id": self.manifest["run_id"],
                "sha256": auth.object_digest(self.manifest), "max_seconds": 60, "max_usd": 0}],
            "limits": {"max_seconds_per_attempt": 60, "max_seconds_total": 180, "max_usd": 0, "exceptional_recovery_limit": 2},
            "expires_at": self.iso(7200)}
        self.message = "approve M1 " + auth.object_digest(self.packet) + "\n"
        self.ref = (f"codex-user-v1:{self.thread_id}/{self.turn_id}/{self.item_id}/" + auth.object_digest(self.packet)
                    + "/" + hashlib.sha256(self.message.encode()).hexdigest())
        self.approval = {"schema_version": "1.0", "experiment_id": self.manifest["experiment_id"], "run_id": self.manifest["run_id"],
            "execution_target": "local", "manifest_sha256": auth.object_digest(self.manifest), "decision": "approve",
            "timestamp": self.iso(-120), "expires_at": self.iso(3600), "max_seconds": 60, "max_usd": 0,
            "actor": self.actor, "source_ref": self.ref}
        self.envelope = {k: self.manifest[k] for k in ("run_id", "stage_id", "task_id", "experiment_id", "execution_target", "git_commit")}
        self.envelope.update(status="running", git_dirty=False, executor="thesis-agents-1.0.0", started_at=self.iso(-60),
            execution_manifest_sha256=auth.object_digest(self.manifest), approval_reference=auth.object_digest(self.approval))
        user_ms = int((self.now - timedelta(seconds=180)).timestamp() * 1000)
        self.rollout = Path(self.policy.codex_home) / "sessions/fixture.jsonl"
        common = {"source": "vscode", "thread_source": "user", "originator": "Codex Desktop",
                  "cwd": self.policy.trusted_cwd, **self.identity}
        self.user = {
            "thread": {"id": self.thread_id, "rollout_path": str(self.rollout), "history_mode": "paginated", "agent_path": None, **common},
            "session_meta": {"id": self.thread_id, "session_id": self.thread_id, **common},
            "item_row": {"thread_id": self.thread_id, "turn_id": self.turn_id, "item_id": self.item_id,
                         "item_type": "userMessage", "rollout_ordinal": 1, "created_at_ms": user_ms,
                         "item": {"type": "userMessage", "id": self.item_id, "clientId": self.client_id,
                                  "content": [{"type": "text", "text": self.message}]}},
            "event": {"timestamp": self.iso(-180), "ordinal": 1, "type": "event_msg", "payload": {
                "type": "item_completed", "thread_id": self.thread_id, "turn_id": self.turn_id,
                "completed_at_ms": user_ms, "item": {"type": "UserMessage", "id": self.item_id,
                "client_id": self.client_id, "content": [{"type": "text", "text": self.message}]}}}}
        results = {s["id"]: {"type": s["type"], "status": "completed", "output": {"choice": "approve"}}
                   for s in self.workflow["steps"]}
        self.controller = {"state": {"run_id": self.policy.controller_run_id, "workflow_id": "thesis-lifecycle",
                "status": "running", "error": None, "step_results": results},
            "inputs": {"inputs": {"plan_acceptance_verdict": "approve", "compute_approval_verdict": "approve"}},
            "workflow": self.workflow, "installed_workflow": deepcopy(self.workflow), "logs": [], "archives": []}
        for step in ("plan-acceptance", "compute-approval"):
            decision = {"run_id": self.policy.controller_run_id, "step_id": step, "verdict": "approve",
                "state_sha256": auth._pre_gate_fingerprint(self.workflow, self.policy.controller_run_id, step),
                "timestamp": self.iso(-110), "expires_at": self.iso(-80), "actor": self.actor, "source_ref": self.ref}
            self.controller["archives"].append({"filename": f"fixture-run-{step}-{auth.object_digest(decision)}.json", "decision": decision})
            self.controller["logs"].append({"event": "step_completed", "step_id": step, "status": "completed", "timestamp": self.iso(-100)})
        self.evidence = MemoryEvidence(self.approval, self.packet, self.user, self.controller)

    def verify(self):
        return auth._verify(self.manifest, self.envelope, self.output, self.policy, self.scope, self.evidence, mode="generated-fixture")

    def denied(self, code=None):
        with self.assertRaises((auth.AuthorityDenied, ValueError)) as result:
            self.verify()
        if code:
            self.assertIn(code, str(result.exception))
        return result.exception

    def rebind_approval(self):
        self.envelope["approval_reference"] = auth.object_digest(self.approval)

    def test_positive_fixture_exact_joins_and_no_scientific_authority(self):
        result = self.verify()
        self.assertEqual(result.manifest_sha256, auth.object_digest(self.manifest))
        self.assertEqual(result.scope, self.scope)
        self.assertEqual(result.exceptional_recovery_limit, 2)
        self.assertEqual(result.to_dict()["source_contract_sha256"], self.scope.source_contract_sha256)
        with self.assertRaises(FrozenInstanceError):
            result.actor = "other"
        for value in (result, result.to_dict()):
            with self.assertRaises(auth.AuthorityDenied):
                auth.require_verified_authority(value, scope=self.scope, manifest_sha256=result.manifest_sha256, output_root=self.output)

    def test_installed_official_checker_is_called_unchanged(self):
        official, _ = auth._official(self.policy.official_runtime_root)
        with patch.object(official, "approval_check", wraps=official.approval_check) as check:
            self.verify()
        check.assert_called_once_with(self.approval, self.manifest)

    def test_expired_rejected_wrong_manifest_and_budget_fail_official(self):
        for field, value in (("expires_at", self.iso(-1)), ("decision", "reject"),
                             ("manifest_sha256", "9" * 64), ("max_seconds", 59)):
            with self.subTest(field=field):
                old = self.approval[field]
                self.approval[field] = value
                self.rebind_approval()
                self.denied()
                self.approval[field] = old
                self.rebind_approval()

    def test_actor_string_without_source_reference_is_not_authority(self):
        self.approval["actor"] = "user"
        self.approval["source_ref"] = "Authenticated user approved everything"
        self.rebind_approval()
        self.denied("source_ref")
        self.assertFalse(any(call[0] == "user" for call in self.evidence.calls))

    def test_actor_misattribution_is_rejected(self):
        self.approval["actor"] = "user"
        self.rebind_approval()
        self.denied("approval_origin")

    def test_wrong_thread_subagent_or_creator_is_rejected(self):
        cases = [("thread", "thread_source", "agent"), ("thread", "agent_path", "/root/agent"),
                 ("session_meta", "creator_user_id", "different"), ("thread", "id", self.turn_id)]
        for section, field, value in cases:
            with self.subTest(field=field):
                old = self.user[section].get(field)
                self.user[section][field] = value
                self.denied()
                self.user[section][field] = old

    def test_assistant_message_and_rollout_mismatch_are_rejected(self):
        self.user["item_row"]["item_type"] = "agentMessage"
        self.denied("user_message")
        self.user["item_row"]["item_type"] = "userMessage"
        self.user["event"]["payload"]["item"]["client_id"] = self.item_id
        self.denied("user_event")

    def test_continue_is_not_approval_even_with_matching_hash(self):
        message = "continue\n"
        ref = auth.parse_source_ref(self.ref)
        ref["message_sha256"] = hashlib.sha256(message.encode()).hexdigest()
        self.user["item_row"]["item"]["content"][0]["text"] = message
        self.user["event"]["payload"]["item"]["content"][0]["text"] = message
        with self.assertRaisesRegex(auth.AuthorityDenied, "no_human_approval"):
            auth._check_user_evidence(ref, self.user, self.policy)

    def test_packet_changed_core_index_schedule_or_manifest_denied(self):
        for field in self.scope.to_dict():
            with self.subTest(field=field):
                bad_scope = replace(self.scope, **{field: "f" * 64})
                with self.assertRaisesRegex(auth.AuthorityDenied, "packet_scope"):
                    auth._verify(self.manifest, self.envelope, self.output, self.policy, bad_scope, self.evidence, mode="generated-fixture")
        self.packet["execution_manifests"][0]["sha256"] = "f" * 64
        self.denied("packet")

    def test_envelope_hash_output_and_dirty_deny_before_approval_lookup(self):
        for field, value in (("approval_reference", "f" * 64), ("execution_manifest_sha256", "f" * 64),
                             ("git_dirty", True), ("executor", "pretend"), ("status", "completed")):
            with self.subTest(field=field):
                old = self.envelope[field]
                self.envelope[field] = value
                self.denied("official_envelope")
                self.envelope[field] = old
        with self.assertRaisesRegex(auth.AuthorityDenied, "output_scope"):
            auth._verify(self.manifest, self.envelope, self.root / "elsewhere", self.policy, self.scope, self.evidence, mode="generated-fixture")

    def test_source_adoption_and_compute_gate_must_be_real_completed(self):
        for step, code in (("plan-acceptance", "pending_source_adoption"), ("compute-approval", "pending_compute_gate")):
            self.controller["state"]["step_results"][step]["status"] = "paused"
            self.denied(code)
            self.controller["state"]["step_results"][step]["status"] = "completed"

    def test_old_generic_approval_and_stale_gate_fingerprint_do_not_adopt_packet(self):
        entry = self.controller["archives"][0]
        entry["decision"]["source_ref"] = "old-scope-not-this-package"
        self.denied("controller_archive")
        entry["decision"]["source_ref"] = self.ref
        entry["decision"]["state_sha256"] = "f" * 64
        entry["filename"] = f"fixture-run-plan-acceptance-{auth.object_digest(entry['decision'])}.json"
        self.denied("controller_prestate")

    def test_archive_filename_log_time_and_duplicate_decisions_fail(self):
        entry = self.controller["archives"][0]
        saved = entry["filename"]
        entry["filename"] = "wrong.json"
        self.denied("controller_archive")
        entry["filename"] = saved
        self.controller["logs"][0]["timestamp"] = self.iso(1)
        self.denied("controller_consumption")
        self.controller["logs"][0]["timestamp"] = self.iso(-100)
        self.controller["archives"].append(deepcopy(entry))
        self.denied("controller_archive")

    def test_previously_consumed_expired_gate_decision_is_historical_not_new_approval(self):
        # Gate decisions expired 80 seconds ago, but their real consumption fell
        # inside the interval. The distinct compute approval is still valid now.
        self.assertLess(auth._timestamp(self.controller["archives"][0]["decision"]["expires_at"]), self.now)
        self.verify()

    def test_approval_cannot_predate_user_or_extend_packet_expiry(self):
        self.approval["timestamp"] = self.iso(-200)
        self.rebind_approval()
        self.denied("approval_origin")
        self.approval["timestamp"] = self.iso(-120)
        self.approval["expires_at"] = self.iso(8000)
        self.rebind_approval()
        self.denied("approval_expiry")

    def test_fixed_lookup_no_arbitrary_approval_path(self):
        provider = auth._HostEvidence(self.policy)
        with patch.object(auth, "_read_bytes", return_value=b"{}") as reader:
            provider.approval("a" * 64)
            provider.packet("b" * 64)
        paths = [str(x.args[0]) for x in reader.call_args_list]
        self.assertEqual(paths, [str(Path(self.policy.decision_store_root) / ("a" * 64) / "approval.json"),
                                 str(Path(self.policy.decision_store_root) / "packets" / ("b" * 64) / "packet.json")])

    def test_packet_boolean_budget_is_not_numeric_zero(self):
        for target in (self.packet["limits"], self.packet["execution_manifests"][0]):
            with self.subTest(target=target):
                target["max_usd"] = False
                with self.assertRaises(auth.AuthorityDenied):
                    auth._check_packet(self.packet, auth.object_digest(self.packet), self.manifest, self.policy, self.scope)
                target["max_usd"] = 0

    def test_uninitialized_receipt_is_not_authority(self):
        with self.assertRaisesRegex(auth.AuthorityDenied, "authority_type"):
            auth.require_verified_authority(auth.VerifiedAuthority(), scope=self.scope,
                manifest_sha256=auth.object_digest(self.manifest), output_root=self.output)

    def test_production_missing_authority_is_pending_without_raw_or_verdict_write(self):
        self.output.mkdir(parents=True)
        (self.output / "execution-manifest.json").write_text(json.dumps(self.manifest), encoding="utf-8")
        (self.output / "manifest.json").write_text(json.dumps(self.envelope), encoding="utf-8")
        before = sorted(str(p.relative_to(self.root)) for p in self.root.rglob("*"))
        with self.assertRaisesRegex(auth.AuthorityDenied, "pending_authority"):
            auth.verify_authority(self.output / "execution-manifest.json", self.output, policy=self.policy, scope=self.scope)
        after = sorted(str(p.relative_to(self.root)) for p in self.root.rglob("*"))
        self.assertEqual(before, after)
        self.assertFalse(any(p.name == "approval.json" for p in self.root.rglob("*")))

    def test_strict_metadata_and_raw_path_exclusion(self):
        for text in ('{"a":1,"a":2}', '{"a":NaN}'):
            with self.assertRaises(auth.AuthorityDenied):
                auth._json(text)
        with self.assertRaisesRegex(auth.AuthorityDenied, "metadata_path"):
            auth._path(self.root / "data/raw/a.jpg")

    def write_host_fixture(self):
        home = Path(self.policy.codex_home)
        home.mkdir()
        self.rollout.parent.mkdir()
        meta = {"type": "session_meta", "ordinal": 0, "payload": self.user["session_meta"]}
        self.rollout.write_text(json.dumps(meta) + "\n" + json.dumps(self.user["event"]) + "\n", encoding="utf-8")
        with closing(sqlite3.connect(home / "state_5.sqlite")) as db:
            columns = tuple(self.user["thread"])
            db.execute("CREATE TABLE threads (" + ",".join(f"{c} TEXT" for c in columns) + ")")
            db.execute("INSERT INTO threads VALUES (" + ",".join("?" for _ in columns) + ")", tuple(self.user["thread"].values()))
            db.commit()
        with closing(sqlite3.connect(home / "thread_history_1.sqlite")) as db:
            db.execute("CREATE TABLE thread_items(thread_id TEXT,turn_id TEXT,item_id TEXT,item_type TEXT,rollout_ordinal INTEGER,created_at_ms INTEGER,item_json TEXT)")
            row = self.user["item_row"]
            db.execute("INSERT INTO thread_items VALUES (?,?,?,?,?,?,?)", tuple(row[k] for k in ("thread_id", "turn_id", "item_id", "item_type", "rollout_ordinal", "created_at_ms")) + (json.dumps(row["item"]),))
            db.execute("CREATE TABLE thread_turns(thread_id TEXT,turn_id TEXT,rollout_byte_offset INTEGER)")
            db.execute("INSERT INTO thread_turns VALUES (?,?,?)", (self.thread_id, self.turn_id, 0))
            db.commit()

    def test_real_readonly_sqlite_and_rollout_fixture_join(self):
        self.write_host_fixture()
        provider = auth._HostEvidence(self.policy)
        observed = provider.user(auth.parse_source_ref(self.ref))
        actor, _, _ = auth._check_user_evidence(auth.parse_source_ref(self.ref), observed, self.policy)
        self.assertEqual(actor, self.actor)
        self.assertEqual(observed, self.user)
        self.assertFalse(any(p.name == "approval.json" for p in self.root.rglob("*")))

    def test_rollout_only_without_host_item_cannot_authorize(self):
        self.write_host_fixture()
        with closing(sqlite3.connect(Path(self.policy.codex_home) / "thread_history_1.sqlite")) as db:
            db.execute("DELETE FROM thread_items")
            db.commit()
        with self.assertRaisesRegex(auth.AuthorityDenied, "user_message"):
            auth._HostEvidence(self.policy).user(auth.parse_source_ref(self.ref))


if __name__ == "__main__":
    unittest.main()
