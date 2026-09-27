"""Model-free package/launcher/failure tests and owned CPU storage fixtures."""
import copy
import json
import os
import struct
from pathlib import Path
import tempfile
from contextlib import ExitStack
import unittest
from unittest.mock import patch
from src.embedding import continuation_package as package
from src.embedding.quality_package import canonical, CONFIG_SHA
from scripts.run_c4_continuation import command
from scripts import c4_continuation as worker
try:
    import torch
    import safetensors
except ImportError:
    torch = safetensors = None


class RefinementPackageTests(unittest.TestCase):
    def test_tracked_configuration_matches_exact_typed_recipe(self):
        root=Path(__file__).resolve().parents[1]
        package.policy((root/package.POLICY).read_bytes())
        self.assertEqual(package.custody.strict_json_bytes((root/package.RETENTION).read_bytes()),package.CUSTODY)

    def test_long_revision_is_still_bounded_and_includes_final_measurement(self):
        from dataclasses import replace
        from src.embedding.proposed import EmbeddingError
        policy=package.policy(canonical(package.PARAMETERS))
        for profile in (policy.control,policy.adaptive):
            self.assertEqual(profile.iterations,512)
            self.assertEqual(profile.maximum_evaluations+1,2050)
            self.assertEqual(profile.maximum_seconds,1500.)
            for change in ({'iterations':513},{'maximum_evaluations':4097},{'maximum_seconds':1801},
                           {'iterations':True}):
                with self.assertRaises(EmbeddingError):replace(profile,**change)
        self.assertEqual(package.BUDGET['max_seconds'],3600)
        self.assertLess(4112*49232,worker.STATE_QUOTA)
        self.assertEqual(worker.JOURNAL_QUOTA,32*1024**2)

    def test_retained_header_is_bounded_typed_grid_not_pickle(self):
        header=canonical({"latent":{"dtype":"F32","shape":[1,4,48,64],"data_offsets":[0,49152]}})
        header=header+b' '*(72-len(header))
        raw=struct.pack('<Q',len(header))+header+bytes(49152)
        package.state_header(raw)
        for value in (b'pickle', raw[:-1], struct.pack('<Q',9000)+raw[8:], raw.replace(b'F32',b'F16')):
            with self.assertRaises(ValueError):package.state_header(value)

    def test_retained_custody_contract_cannot_change(self):
        values=self.fixture();values[1][package.RETENTION]=canonical({})
        with self.assertRaisesRegex(ValueError,'retained-input'):self.check(values)

    def fixture(self):
        snapshots = {name: b"owned" for name in package.REQUIRED}
        snapshots[package.POLICY] = canonical(package.PARAMETERS)
        snapshots[package.RETENTION] = canonical(package.CUSTODY)
        snapshots[package.SPEC+"/experiment-spec.yaml"] = canonical({"datasets": []})
        pins = {name: "a"*64 for name in package.REQUIRED}
        pins["configs/c4-development.json"] = CONFIG_SHA
        manifest = {"experiment_id": package.EXPERIMENT, "run_id": package.RUN, "stage_id": package.STAGE,
            "task_id": "C4", "execution_target": "local", "seeds": [0], "reviewed_script": package.SCRIPT,
            "outputs": package.OUTPUTS, "metrics": package.METRICS, "budget": package.BUDGET,
            "resources": package.RESOURCES, "cleanup_policy": "stop-for-recovery",
            "script_sha256": pins[package.SCRIPT], "datasets": []}
        return manifest, snapshots, pins

    def check(self, values):
        with patch("src.embedding.continuation_package.check_inputs", return_value=values):
            return package.inputs(b"owned", Path("/owned"))

    def test_fixed_recipe_and_every_field_reject(self):
        values = self.fixture(); self.check(values)
        for field in values[0]:
            altered = copy.deepcopy(values); altered[0][field] = "wrong"
            with self.subTest(field=field), self.assertRaises(ValueError): self.check(altered)

    def test_exact_inventory_config_policy_outputs_and_cell_inventory(self):
        values = self.fixture()
        for name in (package.POLICY, package.CHILD, "src/embedding/decoder_continuation.py"):
            altered = copy.deepcopy(values); del altered[1][name]
            with self.assertRaises(ValueError): self.check(altered)
        altered = copy.deepcopy(values); altered[1]["extra"] = b"owned"
        with self.assertRaises(ValueError): self.check(altered)
        altered = copy.deepcopy(values); altered[2]["configs/c4-development.json"] = "b"*64
        with self.assertRaises(ValueError): self.check(altered)
        altered = copy.deepcopy(values)
        policy = copy.deepcopy(package.PARAMETERS); policy["control"]["iterations"] = 65
        altered[1][package.POLICY] = canonical(policy)
        with self.assertRaises(ValueError): self.check(altered)
        self.assertEqual(len(package.OUTPUTS), 6)
        self.assertEqual(len(worker.cells()), 13)
        self.assertEqual(set(worker.cells().values()), {"pending"})
        self.assertLess(len(package.REQUIRED), 128)

    def test_each_policy_value_is_frozen_and_unknown_fields_reject(self):
        for field in package.PARAMETERS:
            altered = copy.deepcopy(package.PARAMETERS); altered[field] = "wrong"
            with self.subTest(field=field), self.assertRaises(ValueError): package.policy(canonical(altered))
        altered = copy.deepcopy(package.PARAMETERS); altered["unreviewed"] = True
        with self.assertRaises(ValueError): package.policy(canonical(altered))
        observed = package.policy(canonical(package.PARAMETERS))
        self.assertEqual(observed.control.maximum_evaluations, 1+512*(1+3))
        self.assertEqual(observed.adaptive.maximum_evaluations, 2049)
        self.assertEqual(observed.control.latent_penalty, 0.)

    @unittest.skipUnless(os.name == "nt", "Windows launcher path contract")
    def test_launcher_exact_offline_array_and_timeout(self):
        args = command(Path("W:/owned manifest.json"), Path("W:/owned outputs"))
        self.assertIn("3540s", args); self.assertIn("--kill-after=10s", args)
        self.assertIn("/mnt/w/owned manifest.json", args)
        self.assertIn(package.CHILD, args); self.assertIn("/usr/bin/env", args)
        self.assertIn("-i", args); self.assertIn("HF_HUB_OFFLINE=1", args)
        self.assertNotIn("--execute", args)

    def test_environment_failure_is_durable_before_any_source_or_model(self):
        manifest = {"git_commit": "a"*40}
        snapshots = {package.custody.ENV: canonical({"python": "wrong", "versions": []})}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            for name in ("outputs", "logs", "checkpoints"): (root/name).mkdir()
            with ExitStack() as stack:
                stack.enter_context(patch.object(worker.package, "inputs", return_value=(manifest, snapshots, {})))
                stack.enter_context(patch.object(worker.custody, "read", return_value=b"owned"))
                source = stack.enter_context(patch.object(worker.custody, "retained", side_effect=AssertionError("source forbidden")))
                stack.enter_context(patch.object(worker.importlib.metadata, "distributions", return_value=[]))
                stack.enter_context(patch.dict(os.environ, {"HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1",
                    "DIFFUSERS_OFFLINE": "1", "CUBLAS_WORKSPACE_CONFIG": ":4096:8"}))
                for name, obj in (("connect", worker.socket.socket), ("connect_ex", worker.socket.socket),
                                  ("create_connection", worker.socket)):
                    stack.enter_context(patch.object(obj, name))
                self.assertEqual(worker.run(root/"owned-manifest", root), 1)
                source.assert_not_called()
            result = json.loads((root/"outputs/continuation.json").read_bytes())
            self.assertEqual(result["status"], "failed_retained_partial")
            self.assertEqual(set(result["cell_inventory"].values()), {"pending"})
            self.assertFalse(result["scientific_acceptance"])
            self.assertEqual(result["arms"], {})
            self.assertIn(b'"phase":"failed"', (root/"logs/continuation-progress.jsonl").read_bytes())

    @unittest.skipUnless(torch is not None and safetensors is not None, "existing pinned CPU storage software absent")
    def test_owned_state_persistence_hash_quota_and_exclusive_no_pickle(self):
        from safetensors.torch import load
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve(); counter = [0, 0]; rows = []
            state = torch.full((1, 4, 2, 2), .25)
            worker.persist_state(root, counter, "retained_start", {"phase": "owned"}, state,
                                 lambda phase, **row: rows.append((phase, row)))
            path = root/"000000-retained_start.safetensors"
            raw = path.read_bytes()
            self.assertEqual(rows[0][1]["state_sha256"], package.custody.sha(raw))
            self.assertEqual(counter, [1, len(raw)])
            torch.testing.assert_close(load(raw)["latent"], state, atol=0, rtol=0)
            with self.assertRaises(FileExistsError):
                worker.persist_state(root, [0, 0], "retained_start", {}, state, lambda *a, **k: None)
            with patch.object(worker, "STATE_QUOTA", len(raw)-1):
                with self.assertRaisesRegex(ValueError, "storage quota"):
                    worker.persist_state(root, counter, "fixed_continuation", {}, state, lambda *a, **k: None)
            self.assertEqual(len(list(root.iterdir())), 1)
            with self.assertRaisesRegex(ValueError, "count"):
                worker.persist_state(root, [4112, 0], "retained_start", {}, state, lambda *a, **k: None)
            with self.assertRaisesRegex(ValueError, "name"):
                worker.persist_state(root, counter, "../escape", {}, state, lambda *a, **k: None)


if __name__ == "__main__": unittest.main()
