"""In-process worker behaviour on generated parents with a fake adapter.

Needs the pinned WSL science interpreter (the worker imports resource, /proc and torch);
skipped everywhere else. No study image, model weight or approval is touched.
"""
import itertools
import json
import os
from pathlib import Path
import shutil
import signal
import sys
import tempfile
import unittest
from unittest.mock import patch
import prepare_v4_saved_evaluation as prepare

PINNED = sys.platform == "linux" and sys.prefix == prepare.core()["execution"]["python_prefix"]
if PINNED:
    import rehearse_v4_saved_evaluation as rehearse
    import v4_saved_evaluation_worker as worker
    from v4_evaluation_journal import Journal, atomic_json, file_sha, object_sha

    class Scientific(rehearse.FakeAdapter):
        """Stands in for the real adapter on the scientific branch; still no image or model."""
        def __init__(self, parent, rows, assets, profile, guard):
            super().__init__(rows,guard,0)
            self.assets = {"files":[]}

COUNTER = itertools.count()


@unittest.skipUnless(PINNED,"pinned WSL science interpreter required")
class WorkerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.core = prepare.core()
        runtime = json.loads((prepare.ROOT/"experiments/c4-three-threat-small-v1/runtime-files-v2.json").read_text())
        cls.inventory = {entry["path"]:entry["sha256"] for entry in runtime["files"]}
        cls.units = rehearse.evaluation_units()[1]

    def setUp(self):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.scratch = Path(scratch.name)
        real = worker.file_sha
        for item in (patch.object(prepare,"BUILD",(self.scratch/"build").as_posix()),
                     patch.dict(os.environ,self.core["execution"]["env"]),
                     patch.object(rehearse,"git",side_effect=lambda *a:"" if a[0] == "status" else "f"*40),
                     patch.object(rehearse,"texture",side_effect=lambda seed,base=None,spread=0:bytearray(bytes([seed*40]))*(512*512*3)),
                     # The 23,021 pinned runtime files are hashed for real by every rehearsal stage, not here.
                     patch.object(worker,"file_sha",side_effect=lambda path:self.inventory.get(str(path)) or real(path))):
            item.start()
            self.addCleanup(item.stop)

    def rehearsal(self):
        return rehearse.stage_directory("rehearsal-test","unit"+str(next(COUNTER)))

    def go(self, root, **options):
        options.setdefault("adapter",lambda parent,rows,guard:rehearse.FakeAdapter(rows,guard,0))
        options.setdefault("units",[u["unit_id"] for u in self.units[:3]])
        return worker.run(str(root/"execution-manifest.json"),str(root),rehearsal=options)

    def outputs(self, root):
        def load(name):
            path = root/"outputs"/name
            return json.loads(path.read_text()) if path.is_file() else None
        return {name.split(".")[0]:load(name) for name in ("results.json","runtime.json","failure.json","heartbeat.json","artifact-index.json")}

    def scientific(self, flagged=False):
        """A scientific-shaped run over a generated parent; exercises the non-rehearsal branch."""
        donor, donor_manifest = self.rehearsal()
        manifest = {**donor_manifest,"run_id":"c4-v4-saved-evaluation-004","git_commit":"a"*40}
        output = Path(prepare.run_root(manifest))
        (output/"outputs").mkdir(parents=True)
        parent = self.scratch/("parent-copy"+str(next(COUNTER)))
        shutil.copytree(donor/"parent",parent)
        snapshot = json.loads((parent/"outputs/results.json").read_text())
        if not flagged:
            del snapshot["rehearsal_synthetic"]
        atomic_json(parent/"outputs/results.json",snapshot)
        package = self.scratch/("package"+str(next(COUNTER)))
        package.mkdir()
        shutil.copy(worker.PACKAGE/"schedule.json",package)
        lock = {"parent_root":parent.as_posix(),"asset_root":"/nonexistent","results_sha256":file_sha(parent/"outputs/results.json"),
                "artifacts":[{"path":p.relative_to(parent).as_posix(),"sha256":file_sha(p)} for p in sorted(parent.rglob("*")) if p.is_file()]}
        if flagged:
            lock["rehearsal_synthetic"] = True
        atomic_json(package/"parent-input-lock.json",lock)
        # Field set of compute.py's running record.
        receipt = {"schema_version":"1.0","run_id":manifest["run_id"],"stage_id":manifest["stage_id"],"task_id":"C4",
                   "experiment_id":manifest["experiment_id"],"status":"running","executor":"thesis-agents-1.0.0",
                   "execution_target":"local","created_at":"2026-10-02T00:00:00+00:00","started_at":"2026-10-02T00:00:00+00:00",
                   "ended_at":None,"git_commit":manifest["git_commit"],"git_dirty":False,"command":["python"],
                   "environment":{},"system":{},"seeds":manifest["seeds"],"datasets":manifest["datasets"],
                   "input_artifacts":manifest["inputs"],"output_artifacts":[],"declared_metrics":manifest["metrics"],
                   "budget_limits":manifest["budget"],"approval_reference":"e"*64,
                   "execution_manifest_sha256":object_sha(manifest),"errors":[],"cleanup_status":"not-applicable",
                   "pod_id":None,"exit_status":None}
        atomic_json(output/"execution-manifest.json",manifest)
        atomic_json(output/"manifest.json",receipt)
        return output, manifest, package, receipt

    def science(self, output, package):
        with patch.object(worker,"PACKAGE",package),patch("v4_saved_evaluation_adapter.SavedEvaluation",Scientific):
            return worker.run(str(output/"execution-manifest.json"),str(output))

    def test_rehearsal_completes_marked_and_bound(self):
        root, manifest = self.rehearsal()
        self.assertEqual(self.go(root),0)
        out = self.outputs(root)
        self.assertIsNone(out["failure"])
        self.assertTrue(out["results"]["evaluation_phase_complete"])
        self.assertEqual(out["results"]["sealed_units"],[u["unit_id"] for u in self.units[:3]])
        self.assertEqual((out["results"]["expected_units"],out["results"]["integrity_errors"]),(3,[]))
        self.assertEqual(out["results"]["scientific_verdict"],"REHEARSAL_SYNTHETIC_INPUT_NOT_EVIDENCE")
        self.assertTrue(out["results"]["rehearsal"] and out["runtime"]["rehearsal"] and out["heartbeat"]["rehearsal"])
        self.assertEqual(out["runtime"]["scientific_core_sha256"],prepare.core_sha256(manifest))
        self.assertEqual(out["heartbeat"]["phase"],worker.COMPLETE)
        records = list((root/"outputs/journal").glob("*/*.json"))
        self.assertTrue(records)
        self.assertTrue(all(json.loads(p.read_text())["manifest_sha256"] == "REHEARSAL-"+object_sha(manifest) for p in records))
        self.assertEqual(out["results"]["journal_bytes"],sum(p.stat().st_size for p in records))
        self.assertEqual(out["artifact-index"]["errors"],[])
        for item in out["artifact-index"]["files"]:
            self.assertEqual(file_sha(root/item["path"]),item["sha256"])
        with self.assertRaises(ValueError):   # a scientific journal rejects every rehearsal record
            Journal(root/"outputs/journal",object_sha(manifest)).get(records[0].parent.name,records[0].stem)

    def test_lease_is_exclusive_and_never_stolen(self):
        root, _ = self.rehearsal()
        self.assertEqual(self.go(root),0)
        before = (root/"outputs/results.json").read_bytes()
        with self.assertRaises(FileExistsError):
            self.go(root)
        self.assertEqual((root/"outputs/results.json").read_bytes(),before)

    def test_scientific_branch_runs_the_whole_schedule_without_any_rehearsal_mark(self):
        output, manifest, package, _ = self.scientific()
        self.assertEqual(self.science(output,package),0)
        out = self.outputs(output)
        self.assertTrue(out["results"]["evaluation_phase_complete"])
        self.assertEqual((len(out["results"]["sealed_units"]),len(out["results"]["rows"])),(209,483))
        self.assertEqual(out["results"]["scientific_verdict"],"PENDING_ANALYSIS_AND_VISUAL_REVIEW_INCOMPLETE_ORIGINAL_CONTROLS")
        self.assertEqual(out["results"]["planned_original_detector_calls"],1884)
        for name in ("results","runtime","heartbeat","artifact-index"):
            self.assertNotIn("rehearsal",out[name],name)
        record = json.loads(next((output/"outputs/journal").glob("*/*.json")).read_text())
        self.assertEqual(record["manifest_sha256"],object_sha(manifest))
        self.assertEqual(out["runtime"]["scientific_core_sha256"],prepare.core_sha256(manifest))
        self.assertEqual(sum(1 for _ in (output/"outputs/journal").glob("*/*.json")),3565)

    def test_scientific_branch_requires_the_official_receipt(self):
        output, manifest, package, receipt = self.scientific()
        changes = [{"rehearsal":True},{"git_commit":"b"*40},{"git_dirty":True},{"approval_reference":None},
                   {"approval_reference":"short"},{"budget_limits":{"max_seconds":1,"max_usd":0,"hourly_usd":0}},
                   {"seeds":[0]},{"status":"completed"},{"execution_manifest_sha256":"0"*64},{"run_id":"c4-v4-saved-evaluation-005"}]
        for change in changes:
            with self.subTest(change=change):
                atomic_json(output/"manifest.json",{**receipt,**change})
                with self.assertRaises(ValueError):
                    self.science(output,package)
                self.assertFalse((output/"outputs/worker-lease.json").exists())

    def test_scientific_branch_refuses_a_rehearsal_parent(self):
        output, _, package, _ = self.scientific(flagged=True)
        self.assertEqual(self.science(output,package),1)
        failure = self.outputs(output)["failure"]
        self.assertIn("refuses a rehearsal parent",failure["message"])
        self.assertEqual(failure["phase"],"VERIFYING_INPUTS")

    def test_rehearsal_cannot_be_reached_or_redirected(self):
        root, manifest = self.rehearsal()
        with self.assertRaisesRegex(ValueError,"unlisted evaluation identity"):   # command-line path is scientific
            worker.run(str(root/"execution-manifest.json"),str(root))
        elsewhere = self.scratch/"elsewhere"
        shutil.copytree(root,elsewhere)
        with self.assertRaisesRegex(ValueError,"output root"):
            worker.run(str(elsewhere/"execution-manifest.json"),str(elsewhere),rehearsal={})
        receipt = json.loads((root/"manifest.json").read_text())
        for change in ({"rehearsal":False},{"approval_reference":"e"*64}):
            atomic_json(root/"manifest.json",{**receipt,**change})
            with self.assertRaisesRegex(ValueError,"rehearsal receipt required"):
                self.go(root)
        atomic_json(root/"manifest.json",receipt)
        lock = json.loads((root/"parent-input-lock.json").read_text())
        outside = self.scratch/"outside-parent"
        shutil.copytree(root/"parent",outside)
        atomic_json(root/"parent-input-lock.json",{**lock,"parent_root":outside.as_posix()})
        self.assertEqual(self.go(root),1)
        self.assertIn("own synthetic parent",self.outputs(root)["failure"]["message"])

    def test_early_failure_is_diagnosable_and_fully_finalised(self):
        root, manifest = self.rehearsal()
        with patch.dict(os.environ,{"OMP_NUM_THREADS":"8"}):
            self.assertEqual(self.go(root),1)
        out = self.outputs(root)
        self.assertEqual(out["failure"]["type"],"ValueError")
        self.assertIn("pinned interpreter",out["failure"]["message"])
        self.assertIn("Traceback (most recent call last)",out["failure"]["traceback"])
        self.assertEqual((out["failure"]["phase"],out["failure"]["unit"]),("VERIFYING_INPUTS",None))
        self.assertFalse(out["results"]["evaluation_phase_complete"])
        self.assertEqual(out["results"]["failure"]["type"],"ValueError")
        self.assertTrue(out["runtime"]["verification_incomplete"])
        self.assertEqual(out["runtime"]["scientific_core_sha256"],prepare.core_sha256(manifest))
        self.assertEqual(out["heartbeat"]["phase"],worker.FAILED)
        self.assertEqual(out["artifact-index"]["errors"],[])

    def test_unit_watchdog_starts_at_the_first_unit_and_total_deadline_from_the_start(self):
        root, _ = self.rehearsal()
        self.assertEqual(self.go(root,unit_seconds=-1),1)
        failure = self.outputs(root)["failure"]
        self.assertEqual((failure["type"],failure["unit"]),("TimeoutError",self.units[0]["unit_id"]))
        root, _ = self.rehearsal()
        self.assertEqual(self.go(root,deadline_seconds=-1),1)
        failure = self.outputs(root)["failure"]
        self.assertEqual((failure["type"],failure["unit"],failure["phase"]),("TimeoutError",None,"VERIFYING_INPUTS"))

    def test_stop_signal_during_a_unit_finalises_the_sealed_prefix(self):
        root, _ = self.rehearsal()
        original = signal.getsignal(signal.SIGTERM)
        third = self.units[2]["row_ids"][0]
        class Signalled(rehearse.FakeAdapter):
            def detect(self, row, image, feature, claim, slot):
                if row["id"] == third and slot == 1:
                    os.kill(os.getpid(),signal.SIGTERM)
                return super().detect(row,image,feature,claim,slot)
        self.assertEqual(self.go(root,adapter=lambda parent,rows,guard:Signalled(rows,guard,0)),1)
        out = self.outputs(root)
        self.assertEqual((out["failure"]["type"],out["failure"]["signals"]),("Terminated",["SIGTERM"]))
        self.assertEqual((out["failure"]["unit"],out["failure"]["row"]),(self.units[2]["unit_id"],third))
        self.assertEqual(out["results"]["sealed_units"],[u["unit_id"] for u in self.units[:2]])
        self.assertEqual(out["results"]["integrity_errors"],[])
        self.assertEqual((out["heartbeat"]["phase"],out["heartbeat"]["signals"]),(worker.FAILED,["SIGTERM"]))
        self.assertIs(signal.getsignal(signal.SIGTERM),original)

    def test_stop_signal_during_finalisation_is_recorded_without_losing_the_run(self):
        root, _ = self.rehearsal()
        real = worker.write_results
        def interrupted(*args):
            os.kill(os.getpid(),signal.SIGTERM)
            return real(*args)
        with patch.object(worker,"write_results",interrupted):
            self.assertEqual(self.go(root),0)
        out = self.outputs(root)
        self.assertTrue(out["results"]["evaluation_phase_complete"])
        self.assertEqual((out["heartbeat"]["phase"],out["heartbeat"]["signals"]),(worker.COMPLETE,["SIGTERM"]))

    def test_heartbeat_tolerates_a_held_file_but_not_a_dead_writer(self):
        real = worker.atomic_json
        calls = []
        def once(path, value):
            if Path(path).name == "heartbeat.json":
                calls.append(path)
                if len(calls) == 1:
                    raise PermissionError(13,"held by a monitor")
            return real(path,value)
        root, _ = self.rehearsal()
        with patch.object(worker,"atomic_json",once):
            self.assertEqual(self.go(root),0)
        def never(path, value):
            if Path(path).name == "heartbeat.json":
                raise PermissionError(13,"held by a monitor")
            return real(path,value)
        root, _ = self.rehearsal()
        with patch.object(worker,"atomic_json",never):
            self.assertEqual(self.go(root,heartbeat_seconds=0.01,units=None,
                                     adapter=lambda parent,rows,guard:rehearse.FakeAdapter(rows,guard,0.02)),1)
        failure = self.outputs(root)["failure"]
        self.assertEqual(failure["type"],"OSError")
        self.assertIn("heartbeat writer failed",failure["message"])

    def test_lost_launcher_or_log_channel_stops_the_evaluation(self):
        root, _ = self.rehearsal()
        real = os.getppid
        calls = itertools.count()
        with patch.object(worker.os,"getppid",lambda:real() if next(calls) < 40 else 1):
            self.assertEqual(self.go(root),1)
        self.assertIn("launcher process or log channel lost",self.outputs(root)["failure"]["message"])
        root, _ = self.rehearsal()
        def broken(*args, **kwargs):
            raise BrokenPipeError(32,"launcher gone")
        with patch.object(worker,"print",broken,create=True):
            self.assertEqual(self.go(root),1)
        out = self.outputs(root)
        self.assertIn("launcher process or log channel lost",out["failure"]["message"])
        self.assertEqual(out["artifact-index"]["errors"],[])

    def test_output_allowance_and_finalisation_faults_fail_closed(self):
        root, _ = self.rehearsal()
        with patch.object(worker,"tree_bytes",return_value=3000*1024**2):
            self.assertEqual(self.go(root),1)
        self.assertIn("output disk allowance reached",self.outputs(root)["failure"]["message"])
        root, _ = self.rehearsal()
        with patch.object(worker,"summarize_journal",side_effect=OSError("summary unreadable")):
            self.assertEqual(self.go(root),1)
        out = self.outputs(root)
        self.assertIsNone(out["results"])
        self.assertEqual(out["failure"]["finalisation_problems"][0]["step"],"results")
        self.assertEqual(out["heartbeat"]["phase"],worker.FAILED)
        self.assertIsNotNone(out["artifact-index"])


if __name__ == "__main__":
    unittest.main()
