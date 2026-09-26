"""Owned worker orchestration/launcher fixtures; never actual models or images."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from src.embedding import worker
from src.embedding import validation_bridge as bridge
from scripts import run_c4_dev_probe as launcher

ROOT = Path(__file__).resolve().parents[1]


class FakeStore:
    def __init__(self, output, flagged=False):
        self.directory = output/"outputs/owned-trial"
        self.directory.mkdir(); self.rows = []; self._finished = False; self.flagged = flagged
    def record(self, row): self.rows.append(row)
    def fail(self, error): self.rows.append({"failed": type(error).__name__}); self._finished = True
    def save_pair(self, candidate, safety):
        self._finished = True
        return {"status": "failed_safety_flagged" if self.flagged else "saved_pair_pending_metrics_and_blind_verification"}, {}


class FakeOperations:
    def __init__(self, fail=None, flagged=False): self.calls = []; self.fail = fail; self.flagged = flagged
    def source(self, selected, output):
        self.calls.append("source")
        if self.fail == "source": raise ValueError("owned failure")
        return "owned-not-pixels"
    def trial(self, source, selected, loaded, output):
        self.calls.append("trial"); self.store = FakeStore(output, self.flagged); return self.store
    def models(self, source, loaded, output):
        self.calls.append("models")
        if self.fail == "models": raise RuntimeError("owned failure")
        return mock.Mock(check_saved_pixels=lambda x: False), {"owned": True}
    def optimize(self, source, selected, loaded, models, enrollment, record):
        self.calls.append("optimize"); record({"owned_trajectory": True})
        if self.fail == "optimize": raise ArithmeticError("owned failure")
        return "owned-not-candidate"
    def attach_progress(self, models, record): self.calls.append("attach_progress")
    def park_idle(self, models, record):
        self.calls.append("park_idle")
        if self.fail == "park_idle": raise MemoryError("owned transfer failure")
    def prepare_safety(self, models, record):
        self.calls.append("prepare_safety")
        if self.fail == "prepare_safety": raise MemoryError("owned transfer failure")
    def resources(self): return {"owned_measurement": True}
    def failure_resources(self): return {"owned_failure_peak": 123}


class WorkerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.output = Path(self.tmp.name)
        for name in ("logs", "checkpoints", "outputs"): (self.output/name).mkdir()
        self.selected = {"source_uid": "owned-fixture"}

    def run_owned(self, operations):
        with mock.patch.object(worker, "prepare", return_value=({"run_id": "owned"}, mock.Mock(sha256="owned"), self.selected)):
            return worker.run_worker(self.output/"owned-manifest.json", self.output, operations=operations)

    def test_phase_order_and_no_success_or_calibrated_claim(self):
        ops = FakeOperations(); self.assertEqual(self.run_owned(ops), 0)
        self.assertEqual(ops.calls, ["source", "trial", "models", "attach_progress", "park_idle", "optimize", "prepare_safety"])
        report = json.loads((self.output/worker.OUTPUTS[0]).read_bytes())
        self.assertEqual(report["status"], "completed_diagnostic_only")
        self.assertFalse(report["scientific_acceptance"])
        self.assertEqual(report["result"]["blind_verification"], "NOT_RUN")
        self.assertEqual(report["result"]["calibrated_decision"], "PROHIBITED")
        with self.assertRaises(ValueError): self.run_owned(ops)
        self.assertEqual(len(ops.calls), 7)

    def test_source_failure_never_loads_and_remains_recorded(self):
        ops = FakeOperations(fail="source"); self.assertEqual(self.run_owned(ops), 2)
        self.assertEqual(ops.calls, ["source"])
        report = json.loads((self.output/worker.OUTPUTS[0]).read_bytes())
        self.assertEqual(report["error_type"], "ValueError")
        self.assertEqual(report["resources"], {"owned_failure_peak": 123})
        self.assertNotIn("owned failure", json.dumps(report))

    def test_model_failure_retains_trial(self):
        ops = FakeOperations(fail="models"); self.assertEqual(self.run_owned(ops), 2)
        self.assertEqual(ops.calls, ["source", "trial", "models"])
        self.assertTrue(ops.store._finished)
        self.assertEqual(ops.store.rows[-1], {"failed": "RuntimeError"})

    def test_gradient_failure_retains_trajectory_and_no_fallback(self):
        ops = FakeOperations(fail="optimize"); self.assertEqual(self.run_owned(ops), 2)
        self.assertIn({"owned_trajectory": True}, ops.store.rows)
        self.assertEqual(ops.store.rows[-1], {"failed": "ArithmeticError"})
        self.assertEqual(ops.calls.count("source"), 1)

    def test_safety_flag_terminal_nonzero(self):
        self.assertEqual(self.run_owned(FakeOperations(flagged=True)), 3)
        self.assertEqual(json.loads((self.output/worker.OUTPUTS[0]).read_bytes())["status"], "failed_safety_flagged")

    def test_telemetry_failure_never_replaces_original_failure(self):
        ops = FakeOperations(fail="models")
        ops.failure_resources = mock.Mock(side_effect=OSError("owned telemetry"))
        self.assertEqual(self.run_owned(ops), 2)
        report = json.loads((self.output/worker.OUTPUTS[0]).read_bytes())
        self.assertEqual(report["error_type"], "RuntimeError")
        self.assertEqual(report["resources"], {"status": "telemetry_failed", "error_type": "OSError"})

    def test_preflight_failure_no_operation_or_actual_import(self):
        ops = FakeOperations()
        with mock.patch.object(worker, "prepare", side_effect=ValueError("owned preflight")):
            self.assertEqual(worker.run_worker(self.output/"missing", self.output, operations=ops), 2)
        self.assertEqual(ops.calls, [])

    def test_fixed_recipe_inventory_budget_types_and_config(self):
        names = worker.REQUIRED | bridge.REQUIRED
        snapshots = {name: (ROOT/name).read_bytes() for name in names}
        manifest = {"experiment_id": worker.EXPERIMENT_ID, "task_id": "C4",
                    "run_id": worker.RUN_ID, "execution_target": "local", "seeds": [0],
                    "reviewed_script": worker.SCRIPT, "budget": worker.BUDGET,
                    "resources": worker.RESOURCES, "outputs": worker.OUTPUTS,
                    "script_sha256": hashlib.sha256(snapshots[worker.SCRIPT]).hexdigest()}
        worker.check_recipe(manifest, snapshots)
        for key, bad in (("seeds", [False]), ("run_id", "c4-embedding-dev-001"),
                         ("run_id", "c4-embedding-dev-002"), ("execution_target", "runpod"),
                         ("budget", dict(worker.BUDGET, max_seconds=1200.0)),
                         ("resources", dict(worker.RESOURCES, vram_mib=8193))):
            altered = copy.deepcopy(manifest); altered[key] = bad
            with self.assertRaises(ValueError): worker.check_recipe(altered, snapshots)
        for amount in (8192,12288):
            altered=copy.deepcopy(manifest);altered["resources"]["vram_mib"]=amount
            with self.assertRaises(ValueError):worker.check_recipe(altered,snapshots)
        altered = dict(snapshots); del altered["scripts/base_noise_reference.py"]
        with self.assertRaises(ValueError): worker.check_recipe(manifest, altered)
        altered=dict(snapshots);altered[worker.RESIDENCY_CONFIG]+=b" "
        with self.assertRaises(ValueError):worker.check_recipe(manifest,altered)
        altered=dict(snapshots);altered[worker.CHECKPOINT_CONFIG]+=b" "
        with self.assertRaises(ValueError):worker.check_recipe(manifest,altered)
        altered=dict(snapshots);del altered["src/embedding/checkpointing.py"]
        with self.assertRaises(ValueError):worker.check_recipe(manifest,altered)

    def test_transfer_failure_is_terminal_before_optimization_or_pair(self):
        for stage in ("park_idle","prepare_safety"):
            with self.subTest(stage=stage),tempfile.TemporaryDirectory() as tmp:
                output=Path(tmp)
                for name in ("logs","checkpoints","outputs"):(output/name).mkdir()
                ops=FakeOperations(fail=stage)
                with mock.patch.object(worker,"prepare",return_value=({"run_id":"owned"},mock.Mock(sha256="owned"),self.selected)):
                    self.assertEqual(worker.run_worker(output/"owned.json",output,operations=ops),2)
                self.assertTrue(ops.store._finished)
                if stage=="park_idle":self.assertNotIn("optimize",ops.calls)
                self.assertEqual(ops.store.rows[-1],{"failed":"MemoryError"})

    def test_actual_residency_adapter_with_owned_module_labels_only(self):
        from tests.test_c4_residency import owned_models
        models=owned_models();rows=[]
        # Do not construct RealOperations/offline sockets/import Torch or call
        # source/models/optimize. Only its exact residency adapter on owned labels.
        ops=worker.RealOperations.__new__(worker.RealOperations)
        ops.residency=None;ops.failure_resources=lambda:{"owned_metadata":True}
        callback=rows.append
        ops.attach_progress(models,callback)
        self.assertIs(models.components.progress,callback)
        ops.park_idle(models,rows.append)
        self.assertEqual(ops.residency.state,"optimization")
        self.assertEqual(rows[0]["phase"],"residency_resources_before_idle")
        self.assertEqual(rows[-1]["phase"],"residency_resources_after_idle")
        self.assertEqual(rows[-1]["residency_profile_sha256"],worker.RESIDENCY_SHA)
        ops.prepare_safety(models,rows.append)
        self.assertEqual(ops.residency.state,"safety")
        self.assertEqual(models.pipeline.safety_checker.weight.device,"cuda:0")
        self.assertEqual(rows[-1]["phase"],"residency_resources_before_safety")
        with self.assertRaises(ValueError):ops.park_idle(owned_models(),rows.append)

    def test_real_metadata_csv_bound_separate_from_receipt_bound(self):
        # Only immutable named CSV inputs may exceed2MiB. This is metadata,
        # not image bytes; the case selector independently enforces their pins.
        snapshots = {name: (ROOT/name).read_bytes() for name in bridge.REQUIRED | set(worker.REQUIRED)}
        manifest = {"experiment_id": worker.EXPERIMENT_ID, "task_id": "C4",
            "run_id": "owned-bound-test", "execution_target": "local", "git_commit": "a"*40,
            "inputs": [{"path": name, "sha256": hashlib.sha256(raw).hexdigest()} for name, raw in snapshots.items()]}
        got = bridge.check_inputs(json.dumps(manifest).encode(), ROOT)
        self.assertEqual(got[1]["data/splits.csv"], snapshots["data/splits.csv"])
        self.assertGreater(len(got[1]["data/splits.csv"]), bridge.MAX_FILE_BYTES)

    @unittest.skipUnless(__import__("os").name == "nt", "Windows launcher path conversion")
    def test_windows_command_is_array_offline_no_shell_and_nested_deadline(self):
        args = launcher.command(self.output/"manifest.json", self.output)
        self.assertEqual(args[0], "C:/Windows/System32/wsl.exe")
        self.assertIn("1140s", args); self.assertIn("--kill-after=10s", args)
        self.assertIn("DIFFUSERS_OFFLINE=1", args); self.assertIn("-i", args)
        self.assertEqual(args.count("--manifest"), 1)
        self.assertNotIn("sh", args); self.assertNotIn("--execute", args)
        with self.assertRaises(ValueError): launcher.linux_path("//server/share/input")


if __name__ == "__main__": unittest.main()
