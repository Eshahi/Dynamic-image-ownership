"""Only generated JSON fixtures and bounded stdlib subprocesses; no science data."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("m1_harness",ROOT/"scripts/m1_confirmatory_harness.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


class HarnessTests(unittest.TestCase):
    def setUp(self):
        self.allowed=ROOT/".thesis-build/rehearsal";self.allowed.mkdir(parents=True,exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(prefix="m1-harness-test-",dir=self.allowed)
        self.addCleanup(self.temp.cleanup);self.base=Path(self.temp.name);self.output=self.base/"output"

    def fixture(self,units=None,timeout=2,budget=10):
        units=units or [{"id":"unit-0","seed":2**64-1,"delay_seconds":0,"action":"complete"}]
        plan={"schema_version":"m1-harness-plan-v1","mode":"synthetic-only","candidate_status":"UNRESOLVED","unit_timeout_seconds":timeout,"units":units}
        path=self.base/"plan.json";m.atomic(path,plan)
        manifest={"schema_version":"1.0","experiment_id":"m1-harness","run_id":"fixture","stage_id":"rehearsal","task_id":"m1",
          "execution_target":"local","reviewed_script":"scripts/m1_confirmatory_harness.py","script_sha256":m.file_sha(m.__file__),
          "git_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),"seeds":sorted({u["seed"] for u in units}),
          "datasets":[{"id":"m1-synthetic-lifecycle","version":"1","license":"generated-fixture","split":"synthetic"}],
          "inputs":[{"path":path.relative_to(ROOT).as_posix(),"sha256":m.file_sha(path)}],"outputs":m.OUTPUTS,
          "metrics":["synthetic_units_completed"],"budget":{"max_seconds":budget,"max_usd":0,"hourly_usd":0},
          "resources":{"vram_mib":0,"ram_mib":128,"disk_mib":10},"cleanup_policy":"stop-for-recovery"}
        manifest_path=self.base/"manifest.json";m.atomic(manifest_path,manifest)
        return manifest_path,manifest

    def execute(self,path,recover=False):return m.run(path,self.output,recover,root=ROOT,rehearsal_root=self.allowed)

    def test_real_subprocess_completion_and_verified_idempotence(self):
        path,_=self.fixture();self.assertEqual(self.execute(path),0)
        result=m.read(self.output/"outputs/results.json")
        self.assertEqual(result["completed_units"],1);self.assertEqual(result["scientific_verdict"],"NOT_EVIDENCE")
        before=m.file_sha(self.output/"checkpoints/journal.json")
        self.assertEqual(self.execute(path),0)
        self.assertEqual(m.file_sha(self.output/"checkpoints/journal.json"),before)
        self.assertFalse((self.output/"harness.lock").exists())

    def runner_envelope(self,manifest):
        m.atomic(self.output/"execution-manifest.json",manifest)
        for folder in ("logs","metrics","checkpoints","outputs"):
            m.atomic(self.output/folder/"contract.json",{"declared":[p for p in manifest["outputs"] if p.startswith(folder+"/")],"note":"Empty declared list means no such artifact required"})
        record={key:manifest[key] for key in ("run_id","stage_id","task_id","experiment_id","execution_target","git_commit","seeds","datasets")}
        record.update(status="running",git_dirty=False,execution_manifest_sha256=m.object_sha(manifest))
        m.atomic(self.output/"manifest.json",record)

    def test_official_runner_envelope_accepted_without_modification(self):
        path,manifest=self.fixture();self.runner_envelope(manifest)
        before=m.file_sha(self.output/"manifest.json")
        self.assertEqual(self.execute(path),0)
        self.assertEqual(m.file_sha(self.output/"manifest.json"),before)
        self.assertTrue((self.output/"outputs/heartbeat.json").is_file())

    def test_wrong_envelope_and_unjournaled_artifact_refused(self):
        path,manifest=self.fixture();self.runner_envelope(manifest)
        contract=self.output/"outputs/contract.json";m.atomic(contract,{"declared":[]})
        with self.assertRaisesRegex(ValueError,"contract mismatch"):self.execute(path)
        self.runner_envelope(manifest)
        stray=self.output/"unknown.bin";stray.write_bytes(b"preserve")
        with self.assertRaisesRegex(ValueError,"Nonempty unjournaled"):self.execute(path)
        self.assertEqual(stray.read_bytes(),b"preserve")

    def test_interruption_terminates_child_and_recovery_retains_attempt(self):
        units=[{"id":"unit-0","seed":0,"delay_seconds":0,"action":"complete"},{"id":"unit-1","seed":1,"delay_seconds":.2,"action":"complete"}]
        path,_=self.fixture(units);original=m.atomic
        def interrupt(path,value):
            if path.name=="heartbeat.json" and value["unit"]=="unit-1":raise KeyboardInterrupt("fixture pause")
            return original(path,value)
        with patch.object(m,"atomic",side_effect=interrupt):
            with self.assertRaises(KeyboardInterrupt):self.execute(path)
        prior=m.read(self.output/"outputs/harness-run.json");self.assertEqual(prior["outcome"],"interrupted")
        with self.assertRaisesRegex(ValueError,"Explicit --recover"):self.execute(path)
        self.assertEqual(self.execute(path,True),0)
        attempts=m.read(self.output/"checkpoints/journal.json")["attempts"]
        self.assertEqual([x["status"] for x in attempts],["completed","interrupted","completed"])
        self.assertEqual([x["attempt"] for x in attempts],[1,1,2])

    def test_unit_timeout_is_retained_not_completion(self):
        path,_=self.fixture([{"id":"slow","seed":0,"delay_seconds":1,"action":"complete"}],timeout=.1)
        with self.assertRaises(TimeoutError):self.execute(path)
        self.assertEqual(m.read(self.output/"outputs/harness-run.json")["outcome"],"timeout")
        self.assertFalse((self.output/"harness.lock").exists())
        self.assertEqual(m.read(self.output/"checkpoints/journal.json")["attempts"][0]["status"],"timeout")

    def test_worker_failure_is_not_scientific_negative(self):
        path,_=self.fixture([{"id":"fail","seed":0,"delay_seconds":0,"action":"fail"}])
        with self.assertRaises(RuntimeError):self.execute(path)
        record=m.read(self.output/"outputs/harness-run.json")
        self.assertEqual(record["outcome"],"failed");self.assertEqual(record["candidate_status"],"UNRESOLVED")

    def test_corrupt_completed_artifact_refused(self):
        path,_=self.fixture();self.execute(path)
        unit=self.output/"outputs/units/unit-0-attempt1.json";unit.write_text("{}")
        with self.assertRaisesRegex(ValueError,"artifact missing/corrupt"):self.execute(path)
        self.assertEqual(unit.read_text(),"{}")

    def test_truncated_journal_preserved(self):
        path,_=self.fixture();self.execute(path)
        journal=self.output/"checkpoints/journal.json";journal.write_bytes(b'{"truncated":')
        with self.assertRaises(ValueError):self.execute(path,True)
        self.assertEqual(journal.read_bytes(),b'{"truncated":')

    def test_changed_plan_and_stale_lock_refused(self):
        path,manifest=self.fixture();self.execute(path)
        plan=ROOT/manifest["inputs"][0]["path"];plan.write_text("{}")
        with self.assertRaisesRegex(ValueError,"Plan hash mismatch"):self.execute(path)
        path,_=self.fixture();(self.output/"harness.lock").write_text("unknown PID")
        with self.assertRaisesRegex(ValueError,"Live/stale lock preserved"):self.execute(path,True)

    def test_test_input_rejected_before_open_or_hash(self):
        _,manifest=self.fixture();manifest["inputs"][0]["path"]="data/heldout-test.json"
        with patch.object(m,"file_sha",wraps=m.file_sha) as spy:
            with self.assertRaisesRegex(ValueError,"Plan must be synthetic JSON"):m.validate_manifest(manifest,ROOT)
        self.assertFalse(any("heldout-test" in str(call.args[0]) for call in spy.call_args_list))

    def test_scientific_dataset_or_unknown_candidate_refused(self):
        _,manifest=self.fixture();manifest["datasets"][0]["split"]="test"
        with self.assertRaisesRegex(ValueError,"Synthetic fixture dataset only"):m.validate_manifest(manifest,ROOT)
        path,manifest=self.fixture();plan_path=ROOT/manifest["inputs"][0]["path"]
        plan=m.read(plan_path);plan["candidate_status"]="frozen";m.atomic(plan_path,plan)
        manifest["inputs"][0]["sha256"]=m.file_sha(plan_path)
        with self.assertRaisesRegex(ValueError,"unresolved-candidate"):m.validate_manifest(manifest,ROOT)


if __name__=="__main__":unittest.main()
