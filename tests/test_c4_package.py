"""Metadata-only packaging tests. No datasets, models, CUDA or launch."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import prepare_c4_execution as package
from src.embedding import worker, validation_bridge


class PackageTests(unittest.TestCase):
    def test_environment_exact_and_rejects_changed_extra_or_missing(self):
        value = {"python":"3.14.4", "versions":[["owned","1.0"]]}
        worker.check_environment(value, copy.deepcopy(value))
        for changed in ({"python":"3.14.5","versions":value["versions"]},
                        {"python":"3.14.4","versions":[]}, dict(value, extra=True)):
            with self.assertRaises(ValueError): worker.check_environment(value, changed)

    def test_owned_exclusive_manifest_and_canonical_digest(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/"owned.json"
            value = {"owned":True}
            import hashlib
            self.assertEqual(package.write_manifest(path, value), hashlib.sha256(validation_bridge._json(value)).hexdigest())
            self.assertEqual(json.loads(path.read_bytes()), value)
            with self.assertRaises(FileExistsError): package.write_manifest(path, value)

    def test_checkout_output_rejected(self):
        with self.assertRaises(ValueError): package.write_manifest(package.ROOT/"owned-never-created.json", {})

    def test_dirty_checkout_rejected_before_inputs(self):
        with mock.patch.object(package.subprocess, "run", return_value=mock.Mock(stdout=" M owned.txt")):
            with self.assertRaises(ValueError): package.build()

    def test_design_input_inventory_and_scope(self):
        required = worker.REQUIRED | validation_bridge.REQUIRED
        for name in (worker.ENVIRONMENT, "scripts/prepare_c4_execution.py", "configs/c4-development.json",
                     worker.SPEC_ROOT+"/experiment-spec.yaml",worker.RESIDENCY_CONFIG,"src/embedding/residency.py",
                     worker.CHECKPOINT_CONFIG,"src/embedding/checkpointing.py",worker.SPEC_ROOT+"/prior-failures.json"):
            self.assertIn(name, required)
        spec = json.loads((package.ROOT/(worker.SPEC_ROOT+"/experiment-spec.yaml")).read_bytes())
        self.assertEqual(spec["seeds"], [0]); self.assertEqual(len(spec["datasets"]), 1)
        self.assertEqual(spec["analysis"]["exclusion_rule"], "none")
        self.assertEqual(spec["analysis"]["confidence_interval"], "none")
        self.assertEqual(spec["analysis"]["mode"], "exploratory")
        self.assertEqual(spec["analysis"]["expected_runs"][0]["run_id"],worker.RUN_ID)
        self.assertIn(worker.SPEC_ROOT+"/resource-amendment.json",required)
        self.assertEqual(worker.RESOURCES["vram_mib"],9216)
        self.assertEqual(json.loads((package.ROOT/(worker.SPEC_ROOT+"/resource-amendment.json")).read_bytes())
                         ["required_free_mib_at_launch"],9216+1024)


if __name__ == "__main__": unittest.main()
