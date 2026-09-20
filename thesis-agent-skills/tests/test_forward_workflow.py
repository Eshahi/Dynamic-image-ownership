"""Forward integration with the real pinned Spec Kit CLI, isolated from live services.

Run with an interpreter containing specify-cli and an editable thesis-agent-skills
installation. Synthetic decisions below are test fixtures, never human approvals.
"""
from datetime import datetime, timedelta, timezone
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CONTROL = ROOT / "skills/thesis-workflow-control/scripts/spec_control.py"


@unittest.skipUnless(importlib.util.find_spec("specify_cli"), "pinned Spec Kit is required")
class ForwardWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.sandbox = tempfile.TemporaryDirectory(prefix="thesis-forward-")
        self.addCleanup(self.sandbox.cleanup)
        self.project = Path(self.sandbox.name)
        (self.project / ".specify").mkdir()
        shutil.copytree(ROOT / "spec-kit/steps/thesis-safe",
                        self.project / ".specify/workflows/steps/thesis-safe")
        self.cli("add", str(ROOT / "spec-kit/workflows/thesis-smoke"), "--dev", json_output=False)

    def run_command(self, command, expected=0):
        result = subprocess.run(command, cwd=self.project, stdin=subprocess.DEVNULL,
                                capture_output=True, text=True, encoding="utf-8", timeout=90)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def cli(self, *args, json_output=True):
        result = self.run_command([sys.executable, "-c", "from specify_cli import main; main()",
                                   "workflow", *args, *(["--json"] if json_output else [])])
        return json.loads(result.stdout) if json_output else result.stdout

    def controller(self, *args, expected=0, empty=False):
        result = self.run_command([sys.executable, str(CONTROL), "--project", str(self.project), *args], expected)
        if empty:
            self.assertEqual(result.stdout, "")
            return None
        return json.loads(result.stderr if expected else result.stdout)

    def start(self):
        state = self.controller("start", "thesis-smoke", "--execute")
        self.assertEqual(state["status"], "paused", state)
        self.assertEqual(state["current_step_id"], "evidence-review", state)
        return state

    def decision(self, state, verdict="approve", **changes):
        package = self.controller("prepare-approval", state["run_id"])
        self.assertEqual(package["approval"], "not-granted")
        self.assertEqual(package["allowed_verdicts"], ["approve", "reject"])
        current = datetime.now(timezone.utc)
        decision = {"run_id": state["run_id"], "step_id": package["step_id"],
                    "state_sha256": package["state_sha256"], "verdict": verdict,
                    "timestamp": (current - timedelta(seconds=2)).isoformat(),
                    "expires_at": (current + timedelta(minutes=10)).isoformat(),
                    "actor": "SYNTHETIC-UNITTEST-NOT-A-HUMAN",
                    "source_ref": "isolated-unittest-fixture:no-live-authorization"}
        decision.update(changes)
        path = self.project / "synthetic-test-decision.json"
        path.write_text(json.dumps(decision), encoding="utf-8")
        return path

    def test_resume_real_paused_workflow_to_completion(self):
        state = self.start()
        run_id = state["run_id"]
        first = self.controller("watch-once", run_id)
        self.assertLessEqual(len(first["notification"]), 1500)
        self.controller("watch-once", run_id, "--previous-token", first["token"], empty=True)
        before = self.cli("status", run_id)
        decision = self.decision(state)
        preview = self.controller("resume", run_id, "--decision", str(decision))
        self.assertTrue(preview["dry_run"])
        self.assertEqual(before, self.cli("status", run_id))
        self.assertFalse((self.project / ".specify/thesis-decisions").exists())
        next_state = self.controller("resume", run_id, "--decision", str(decision), "--execute")
        self.assertEqual(next_state["status"], "paused", next_state)
        self.assertEqual(next_state["current_step_id"], "compute-approval", next_state)
        next_note = self.controller("watch-once", run_id, "--previous-token", first["token"])
        self.assertNotEqual(next_note["token"], first["token"])
        output = self.project / "smoke-output" / run_id
        self.assertFalse((output / "metrics.json").exists())
        decision = self.decision(next_state)
        completed = self.controller("resume", run_id, "--decision", str(decision), "--execute")
        self.assertEqual(completed["status"], "completed", completed)
        self.assertEqual(self.cli("status", run_id)["status"], "completed")
        self.assertEqual(self.controller("status", run_id)["run_id"], run_id)
        completion = json.loads((output / "completion.json").read_text())
        self.assertEqual(completion["status"], "completed")
        self.assertFalse(completion["live_services_contacted"])
        execution = json.loads((output / "mock-execution.json").read_text())
        self.assertFalse(execution["real_experiment"])
        self.assertEqual(execution["network_calls"], 0)
        self.assertFalse(execution["gpu_work"])
        self.assertEqual(len(list((self.project / ".specify/thesis-decisions").glob("*.json"))), 2)

    def test_unsupported_and_misbound_verdicts_preserve_paused_state(self):
        state = self.start()
        run_id = state["run_id"]
        before = self.cli("status", run_id)
        for verdict in ("revise", "retry", "stop", "unknown", "APPROVE", "approve; echo injected"):
            with self.subTest(verdict=verdict):
                path = self.decision(state, verdict)
                error = self.controller("resume", run_id, "--decision", str(path), "--execute", expected=2)
                self.assertIn("error", error)
                self.assertEqual(before, self.cli("status", run_id))
        for changes in ({"step_id": "compute-approval"}, {"run_id": "another-run"},
                        {"state_sha256": "0" * 64},
                        {"expires_at": (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()}):
            with self.subTest(changes=changes):
                path = self.decision(state, **changes)
                self.controller("resume", run_id, "--decision", str(path), "--execute", expected=2)
                self.assertEqual(before, self.cli("status", run_id))
        self.assertFalse((self.project / ".specify/thesis-decisions").exists())

    def test_explicit_reject_stops_at_gate(self):
        state = self.start()
        path = self.decision(state, "reject")
        result = self.controller("stop", state["run_id"], "--decision", str(path), "--execute")
        self.assertEqual(result["status"], "aborted", result)
        self.assertEqual(self.cli("status", state["run_id"])["status"], "aborted")
        self.assertFalse((self.project / "smoke-output" / state["run_id"] / "metrics.json").exists())


if __name__ == "__main__":
    unittest.main()
