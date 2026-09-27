"""Owned metadata/fake-launcher tests; no study decode, model or execution."""
import copy
import json
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.embedding import quality_package as package
from scripts.run_c4_saved_pair import command
from scripts.c4_saved_pair import run, append_progress


def fixture():
    snapshots = {name: (ROOT/name).read_bytes() for name in package.REQUIRED}
    manifest = {"experiment_id": package.EXPERIMENT, "run_id": package.RUN,
        "stage_id": "C4-quality-development", "task_id": "C4", "execution_target": "local",
        "seeds": [0], "reviewed_script": package.SCRIPT, "outputs": package.OUTPUTS,
        "metrics": package.METRICS, "budget": package.BUDGET, "resources": package.RESOURCES,
        "cleanup_policy": "stop-for-recovery", "script_sha256": package.sha(snapshots[package.SCRIPT]),
        "datasets": json.loads(snapshots[package.SPEC+"/experiment-spec.yaml"])["datasets"],
        "git_commit": "0"*40, "inputs": [{"path": name, "sha256": package.sha(raw)}
        for name, raw in sorted(snapshots.items())]}
    return manifest, snapshots


class PackageTests(unittest.TestCase):
    def test_fixed_recipe(self):
        manifest, snapshots = fixture()
        package.recipe(manifest, snapshots)
        self.assertEqual(package.inputs(package.canonical(manifest), ROOT)[1], snapshots)

    def test_no_scope_target_resource_output_change(self):
        manifest, snapshots = fixture()
        for name, value in (("seeds", [True]), ("run_id", "other"),
                            ("execution_target", "runpod"), ("budget", {"max_seconds": 1200, "max_usd": 1}),
                            ("resources", {"vram_mib": 8192}), ("outputs", []), ("datasets", [])):
            with self.assertRaises(ValueError):
                package.recipe({**manifest, name: value}, snapshots)

    def test_missing_extra_duplicate_and_mismatch(self):
        manifest, snapshots = fixture()
        for mutate in (lambda m: m["inputs"].pop(),
                       lambda m: m["inputs"].append(m["inputs"][0]),
                       lambda m: m["inputs"][0].update(path="../escape"),
                       lambda m: m["inputs"][0].update(sha256="0"*64)):
            changed = copy.deepcopy(manifest); mutate(changed)
            with self.assertRaises(ValueError):
                package.inputs(package.canonical(changed), ROOT)
        with self.assertRaises(ValueError):
            package.recipe(manifest, {**snapshots, "extra": b""})

    def test_json_duplicate_nonfinite_rejected(self):
        for raw in (b'{"git_commit":"x","git_commit":"y"}', b'{"inputs":NaN}'):
            with self.assertRaises(ValueError): package.inputs(raw, ROOT)

    def test_retained_custody_reads_only_fixed_frames(self):
        # Owned fake bytes only: this test never opens actual retained outputs.
        expected = {"q": "5f0f", "h": "40a9a967", "OwnerID": package.OWNER,
            "Ws": "a19372203dc6735b3ff30701e87572a5bd82a5df312ab80fd2e3e85c55378b54",
            "Wi": "ad6fc565f4c3068dc333561de41339a6729889080514dd1309feb10481db1015"}
        def fake(path, *args):
            if path.name == "manifest.json": return b'{"status":"completed"}'
            if path.name == "pair.json": return package.canonical({"status":"saved_pair_pending_metrics_and_blind_verification", "rows":[{"safety_flagged":False}]*2})
            if path.name == "trajectory.jsonl": return package.canonical({"enrollment":expected})
            return b"owned-fixture"
        with patch.object(package, "checked", side_effect=fake):
            data, enrollment = package.retained(ROOT)
        self.assertEqual(set(data), {"source", "control", "candidate"})
        self.assertEqual(enrollment, expected)

    def test_bounded_argument_array(self):
        with patch("scripts.run_c4_saved_pair.linux_path", side_effect=lambda p: "/mnt/c/owned/"+Path(p).name):
            args = command(Path("C:/owned/manifest.json"), Path("C:/owned/out"))
        self.assertIn("1140s", args)
        self.assertIn("--kill-after=10s", args)
        self.assertIn("-i", args)
        self.assertEqual(args[-4:], ["--manifest", "/mnt/c/owned/manifest.json", "--output-dir", "/mnt/c/owned/out"])
        self.assertFalse(any("--execute" in arg for arg in args))

    def test_failure_retention_before_any_model_import(self):
        manifest, snapshots = fixture()
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder).absolute()
            for name in ("outputs", "logs", "checkpoints"):
                (output/name).mkdir()
            with patch.object(package, "inputs", return_value=(manifest, snapshots, {})), \
                 patch.object(package, "read", return_value=b"owned"), \
                 patch("scripts.c4_saved_pair.importlib.metadata.distributions", return_value=[]), \
                 patch("scripts.c4_saved_pair.socket.socket.connect"), \
                 patch("scripts.c4_saved_pair.socket.socket.connect_ex"), \
                 patch("scripts.c4_saved_pair.socket.create_connection"):
                # Exact environment mismatch stops before retained decode/Torch.
                self.assertEqual(run(output/"owned-manifest", output), 1)
            result = json.loads((output/"outputs/saved-pair-quality.json").read_bytes())
            self.assertEqual(result["status"], "failed_retained_partial")
            self.assertEqual(result["quality"], {})
            self.assertEqual(result["error_type"], "ValueError")
            self.assertFalse(result["scientific_acceptance"])
            lines = (output/"logs/saved-pair-progress.jsonl").read_text().splitlines()
            self.assertEqual(json.loads(lines[-1])["phase"], "failed")
            self.assertEqual(result["failure_phase"], "worker_started")

    def test_completed_values_durable_without_terminal_report(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/"owned-progress"
            with path.open("xb") as journal:
                append_progress(journal, time.monotonic(), "classical_complete",
                                comparison="owned", metrics={"mse_rgb01": 0.02})
                # Read before closing, like a forced stop lacking final JSON.
                observed = json.loads(path.read_bytes())
                self.assertEqual(observed["metrics"]["mse_rgb01"], 0.02)
            self.assertFalse((Path(folder)/"result.json").exists())


if __name__ == "__main__": unittest.main()
