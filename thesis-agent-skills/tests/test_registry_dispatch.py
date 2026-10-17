"""Development-only dispatcher exception: no image access, GPU, or approvals."""
import copy
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from thesis_agents.common import ContractError, digest, read
from thesis_agents.compute import dispatch, local_artifact_directory


BUNDLE = Path(__file__).resolve().parents[1]
ENTRY = "scripts/m1b_coco512_worker.py"
RUNTIME = "scripts/m1b_registry_runtime.py"
PLAN = "research/fixture.m1b-plan.json"
INDEX = "research/development-index.json"


class RegistryDispatchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="registry-dispatch-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.artifacts = self.root / "artifacts"
        self.put(ENTRY, '''import argparse, json
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument('--manifest')
p.add_argument('--output-dir')
a=p.parse_args()
Path(a.output_dir, 'metrics/values.json').write_text(json.dumps({'value': 1}))
''')
        # A fixture of the worker's independent metadata membership validator.
        self.put(RUNTIME, '''import json
def validate_plan(plan, repo):
    index=json.loads((repo / plan['sources']['index']['path']).read_text())
    if any(row['split'] != 'development' or row['uid'] != 'dev-001' for row in index):
        raise ValueError('source is absent from locked development cohort')
    return plan, index
''')
        self.put(INDEX, [{"uid": "dev-001", "split": "development"}])
        self.plan = {"protocol": "registry-two-factor-v1", "data_split": "development",
                     "sources": {"index": {"path": INDEX, "sha256": digest(self.repo / INDEX)}}}
        self.put(PLAN, self.plan)
        self.git("init", "--quiet")
        self.commit()
        self.manifest = read(BUNDLE / "fixtures/execution-manifest.json")
        self.manifest.update(execution_target="local", reviewed_script=ENTRY,
                             script_sha256=digest(self.repo / ENTRY), git_commit=self.git("rev-parse", "HEAD"),
                             datasets=[{"id": "development", "version": "fixture", "license": "synthetic fixture",
                                        "split": "development"}],
                             inputs=[{"path": p, "sha256": digest(self.repo / p)} for p in (PLAN, INDEX, RUNTIME)])

    def put(self, name, value):
        dest = self.repo / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(value if isinstance(value, str) else json.dumps(value), encoding="utf-8")

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.repo), *args], stderr=subprocess.PIPE, text=True).strip()

    def commit(self):
        self.git("add", ".")
        self.git("-c", "user.name=Offline Test", "-c", "user.email=test@example.invalid",
                 "commit", "--quiet", "-m", "Synthetic dispatcher fixture")

    def refresh(self):
        for ref in self.manifest["inputs"]:
            ref["sha256"] = digest(self.repo / ref["path"])
        self.commit()
        self.manifest["git_commit"] = self.git("rev-parse", "HEAD")

    def run_dispatch(self, **kwargs):
        return dispatch(self.manifest, self.repo, self.artifacts, development_rehearsal=True, **kwargs)

    def test_real_local_cpu_dispatch_without_fabricated_approval(self):
        result = self.run_dispatch(execute=True)
        self.assertEqual(result["status"], "completed")
        self.assertIsNone(result["approval_reference"])
        out = self.artifacts / result["stage_id"] / result["run_id"]
        context = read(out / "rehearsal-context.json")
        self.assertEqual(context["mode"], "development-rehearsal")
        self.assertIsNone(context["human_approval"])
        self.assertIn("clarification 3", context["authorization_source"])
        self.assertEqual(context["source_index"], self.plan["sources"]["index"])
        self.assertEqual(read(out / "manifest.json"), result)
        self.assertFalse(any("approval" in p.name for p in out.iterdir()))

    def test_preview_validates_scope_and_creates_nothing(self):
        result = self.run_dispatch()
        self.assertTrue(result["dry_run"])
        self.assertFalse(result["requires_approval"])
        self.assertFalse(self.artifacts.exists())

    def test_default_execution_still_requires_human_approval(self):
        with self.assertRaisesRegex(ContractError, "human approval required"):
            dispatch(self.manifest, self.repo, self.artifacts, execute=True)
        self.assertFalse(self.artifacts.exists())

    def test_default_preview_still_requires_approval(self):
        self.assertTrue(dispatch(self.manifest, self.repo, self.artifacts)["requires_approval"])

    def test_rehearsal_refuses_approval_argument(self):
        with self.assertRaisesRegex(ContractError, "cannot consume"):
            self.run_dispatch(approval={})

    def test_remote_and_nonzero_cost_are_refused(self):
        for field, value in (("execution_target", "mock"), ("execution_target", "runpod"),
                             ("max_usd", 1), ("hourly_usd", 1)):
            with self.subTest(field=field, value=value):
                m = copy.deepcopy(self.manifest)
                if field == "execution_target":
                    m[field] = value
                else:
                    m["budget"][field] = value
                    if field == "hourly_usd":
                        m["budget"]["max_usd"] = 1
                with self.assertRaisesRegex(ContractError, "local execution at USD 0"):
                    dispatch(m, self.repo, self.artifacts, development_rehearsal=True)
        self.assertFalse(self.artifacts.exists())

    def test_no_test_rehearsal_or_unspecified_manifest_dataset(self):
        for datasets in ([], [dict(self.manifest["datasets"][0], split="test")],
                         [*self.manifest["datasets"], dict(self.manifest["datasets"][0], split="rehearsal")]):
            with self.subTest(datasets=datasets):
                self.manifest["datasets"] = datasets
                with self.assertRaisesRegex(ContractError, "datasets must all be development"):
                    self.run_dispatch()

    def test_wrong_reviewed_entry_is_refused(self):
        self.put("scripts/noop.py", "# fixture")
        self.commit()
        self.manifest.update(reviewed_script="scripts/noop.py", script_sha256=digest(self.repo / "scripts/noop.py"),
                             git_commit=self.git("rev-parse", "HEAD"))
        with self.assertRaisesRegex(ContractError, "exact reviewed M1b entry"):
            self.run_dispatch()

    def test_plan_requires_development_and_registry_protocol(self):
        for key, value in (("data_split", "test"), ("data_split", "rehearsal"), ("protocol", "e3-s1-v1")):
            with self.subTest(key=key, value=value):
                plan = dict(self.plan, **{key: value})
                self.put(PLAN, plan)
                self.refresh()
                with self.assertRaisesRegex(ContractError, "registry-two-factor-v1 development plan"):
                    self.run_dispatch()

    def test_plan_index_and_validator_must_be_hash_bound(self):
        original = copy.deepcopy(self.manifest["inputs"])
        for remove in (PLAN, INDEX, RUNTIME):
            with self.subTest(remove=remove):
                self.manifest["inputs"] = [i for i in original if i["path"] != remove]
                with self.assertRaises(ContractError):
                    self.run_dispatch()

    def test_worker_membership_validator_rejects_disguised_heldout_source(self):
        self.put(INDEX, [{"uid": "heldout-001", "split": "development"}])
        self.plan["sources"]["index"]["sha256"] = digest(self.repo / INDEX)
        self.put(PLAN, self.plan)
        self.refresh()
        with self.assertRaisesRegex(ContractError, "locked development cohort"):
            self.run_dispatch(execute=True)
        self.assertFalse(self.artifacts.exists())

    def test_hash_and_clean_commit_checks_remain_required(self):
        self.manifest["script_sha256"] = "0" * 64
        with self.assertRaisesRegex(ContractError, "script hash mismatch"):
            self.run_dispatch()
        self.manifest["script_sha256"] = digest(self.repo / ENTRY)
        self.manifest["inputs"][0]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ContractError, "checksum mismatch"):
            self.run_dispatch()
        self.manifest["inputs"][0]["sha256"] = digest(self.repo / PLAN)
        self.put("dirty.txt", "unreviewed")
        with self.assertRaisesRegex(ContractError, "exact clean reviewed Git commit"):
            self.run_dispatch()

    def test_cli_has_explicit_flag(self):
        with patch("thesis_agents.compute.sys.argv", ["runner", "dispatch", "fixture.json", "--repo", "repo",
                                                     "--artifacts", "out", "--development-rehearsal"]), \
             patch("thesis_agents.compute.read", return_value=self.manifest), \
             patch("thesis_agents.compute.dispatch", return_value={"dry_run": True}) as mocked:
            from thesis_agents.compute import main
            main()
        self.assertTrue(mocked.call_args.kwargs["development_rehearsal"])

    def failed_attempt(self):
        self.manifest["outputs"].append("metrics/not-yet-produced.json")
        result = self.run_dispatch(execute=True)
        self.assertEqual(result["status"], "failed")
        out = self.artifacts / result["stage_id"] / result["run_id"]
        (out / "outputs/journal.jsonl").write_text('{"phase":"preserved"}\n')
        return out

    def test_resume_reopens_exact_directory_and_preserves_attempt_and_journal(self):
        out = self.failed_attempt()
        previous = (out / "manifest.json").read_bytes()
        journal = (out / "outputs/journal.jsonl").read_bytes()
        contracts = (out / "outputs/contract.json").read_bytes()
        (out / "metrics/not-yet-produced.json").write_text('{}')
        result = self.run_dispatch(execute=True, resume_incomplete=True)
        self.assertEqual(result["status"], "completed")
        archive = out / "attempts/attempt-001"
        self.assertEqual((archive / "manifest.json").read_bytes(), previous)
        self.assertTrue((archive / "logs/process.log").is_file())
        self.assertEqual((out / "outputs/journal.jsonl").read_bytes(), journal)
        self.assertEqual((out / "outputs/contract.json").read_bytes(), contracts)
        with self.assertRaisesRegex(ContractError, "Completed runs"):
            self.run_dispatch(execute=True, resume_incomplete=True)

    def test_resume_missing_endpoint_stays_failed_and_numbers_attempts(self):
        out = self.failed_attempt()
        for number in (1, 2):
            result = self.run_dispatch(execute=True, resume_incomplete=True)
            self.assertEqual(result["status"], "failed")
            self.assertTrue((out / f"attempts/attempt-{number:03d}/manifest.json").is_file())
        self.assertIn("Declared artifact missing", result["errors"][0])

    def test_resume_requires_exact_stored_manifest(self):
        self.failed_attempt()
        self.manifest["seeds"] = [91]
        with self.assertRaisesRegex(ContractError, "exact stored manifest"):
            self.run_dispatch(execute=True, resume_incomplete=True)

    def test_resume_refuses_active_child_and_uncertain_launch(self):
        out = self.failed_attempt()
        for state in ({"status": "running", "child_pid": __import__('os').getpid()},
                      {"status": "starting", "child_pid": None}):
            (out / "dispatcher-state.json").write_text(json.dumps(state))
            with self.assertRaisesRegex(ContractError, "resume refused"):
                self.run_dispatch(execute=True, resume_incomplete=True)

    def test_resume_refuses_concurrent_dispatcher(self):
        out = self.failed_attempt()
        _, lock = local_artifact_directory(out, self.manifest, True)
        try:
            with self.assertRaises(ContractError):
                self.run_dispatch(execute=True, resume_incomplete=True)
        finally:
            lock.close()

    def test_resume_without_flag_or_approval_is_not_admitted(self):
        self.failed_attempt()
        with self.assertRaises(FileExistsError):
            self.run_dispatch(execute=True)
        with self.assertRaisesRegex(ContractError, "human approval required"):
            dispatch(self.manifest, self.repo, self.artifacts, execute=True, resume_incomplete=True)

    def test_resume_is_local_only(self):
        self.manifest["execution_target"] = "mock"
        with self.assertRaisesRegex(ContractError, "only for local"):
            self.run_dispatch(resume_incomplete=True)

    def test_runtime_bundle_matches_source(self):
        self.assertEqual((BUNDLE / "src/thesis_agents/compute.py").read_bytes(),
                         (BUNDLE / "skills/thesis-compute-runner/scripts/_runtime/thesis_agents/compute.py").read_bytes())



class ProcessIdentityTests(unittest.TestCase):
    def setUp(self):
        from thesis_agents.common import object_digest
        self.temp = tempfile.TemporaryDirectory(prefix="process-identity-")
        self.addCleanup(self.temp.cleanup)
        self.out = Path(self.temp.name)
        self.manifest = dict(run_id="synthetic", datasets=[dict(split="development")])
        self.digest = object_digest
        self.reset()

    def reset(self, **state):
        (self.out / "execution-manifest.json").write_text(json.dumps(self.manifest))
        (self.out / "manifest.json").write_text(json.dumps(dict(run_id="synthetic", status="failed", execution_manifest_sha256=self.digest(self.manifest))))
        (self.out / "dispatcher-state.json").write_text(json.dumps(dict(status="exited", child_pid=None, **state)))

    def reopen(self):
        _, lock = local_artifact_directory(self.out, self.manifest, True)
        lock.close()

    def test_os_birth_token_is_stable_for_current_process(self):
        import os
        from thesis_agents.compute import process_start_token
        token = process_start_token(os.getpid())
        self.assertTrue(token)
        self.assertEqual(token, process_start_token(os.getpid()))

    def test_matching_live_birth_identity_refuses_resume(self):
        (self.out / "dispatcher-state.json").write_text(json.dumps(dict(status="running", child_pid=123, child_start_token="birth-a")))
        with patch("thesis_agents.compute.process_alive", return_value=True), patch("thesis_agents.compute.process_start_token", return_value="birth-a"):
            with self.assertRaisesRegex(ContractError, "still active"):
                self.reopen()

    def test_recycled_pid_birth_identity_allows_resume(self):
        (self.out / "dispatcher-state.json").write_text(json.dumps(dict(status="running", child_pid=123, child_start_token="before-reboot")))
        with patch("thesis_agents.compute.process_alive", return_value=True), patch("thesis_agents.compute.process_start_token", return_value="after-reboot"):
            self.reopen()
        self.assertTrue((self.out / "attempts/attempt-001").is_dir())

    def test_unknown_legacy_live_identity_is_conservative(self):
        (self.out / "dispatcher-state.json").write_text(json.dumps(dict(status="running", child_pid=123)))
        with patch("thesis_agents.compute.process_alive", return_value=True), patch("thesis_agents.compute.process_start_token", return_value="known-now"):
            with self.assertRaisesRegex(ContractError, "identity is uncertain"):
                self.reopen()

    def test_absent_prior_pid_allows_resume_without_birth_query(self):
        (self.out / "dispatcher-state.json").write_text(json.dumps(dict(status="running", child_pid=123)))
        with patch("thesis_agents.compute.process_alive", return_value=False), patch("thesis_agents.compute.process_start_token", side_effect=AssertionError("dead PID queried")):
            self.reopen()

    def test_test_resumes_capped_at_two(self):
        self.manifest["datasets"] = [dict(split="test")]
        self.reset()
        self.reopen()
        self.reopen()
        with self.assertRaisesRegex(ContractError, "limit of two"):
            self.reopen()
        self.assertFalse((self.out / "attempts/attempt-003").exists())

    def test_development_resumes_uncapped(self):
        for _ in range(4):
            self.reopen()
        self.assertTrue((self.out / "attempts/attempt-004").exists())


if __name__ == "__main__":
    unittest.main()
