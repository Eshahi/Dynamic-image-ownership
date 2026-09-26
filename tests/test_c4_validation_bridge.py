"""Owned config/receipt tests only; no worker, assets or scientific permission."""
import copy
import dataclasses
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from src.embedding.proposed import EmbeddingError, Settings
from src.embedding import validation_bridge as bridge
from tests.c4_fixtures import loaded_fixture
from tests import test_c4_feasibility as feasibility_fixtures

SETTINGS = Settings(10, .2, .18215, 256, .2, .3, .01, .005, 2, 1, 1, 1, 1, .1, .1)
ROOT = Path(__file__).resolve().parents[1]


class ValidationBridgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)/"owned-repo"
        self.root.mkdir()
        self.checkpoints = Path(self.tmp.name)/"checkpoints"
        self.checkpoints.mkdir()
        self.loaded = loaded_fixture(SETTINGS)
        for name in bridge.REQUIRED:
            path = self.root/name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(self.loaded.raw if name == bridge.CONFIG_PATH else (ROOT/name).read_bytes())
        self.manifest = {"schema_version": "1.0", "experiment_id": bridge.EXPERIMENT_ID,
            "run_id": "owned-bridge-test", "task_id": "C4", "execution_target": "local",
            "git_commit": "a"*40, "seeds": [7],
            "inputs": [{"path": name, "sha256": hashlib.sha256((self.root/name).read_bytes()).hexdigest()}
                       for name in sorted(bridge.REQUIRED)]}
        # This intentionally partial manifest is a bridge fixture, not a
        # runner-valid manifest, selected scientific config or user approval.
        self.manifest_path = Path(self.tmp.name)/"manifest.json"
        self.write_manifest()

    def write_manifest(self):
        self.manifest_path.write_text(json.dumps(self.manifest), encoding="utf-8")

    def fixture_receipt(self):
        # Mock only in synthetic receipt tests; production never has this
        # bypass. The separate Windows test invokes the ACTUAL C1 validator.
        with mock.patch.object(bridge, "load_method_config", return_value=self.loaded) as validate:
            path = bridge.write_validation_receipt(self.manifest_path, self.checkpoints, root=self.root)
            validate.assert_called_once_with(self.root/bridge.CONFIG_PATH)
        return path

    def test_owned_roundtrip_and_receipt_is_not_approval(self):
        path = self.fixture_receipt()
        got = bridge.consume_validation_receipt(self.manifest_path, self.checkpoints, root=self.root)
        self.assertEqual(got, self.loaded)
        record = json.loads(path.read_bytes())
        self.assertFalse(record["validator_verdict"]["scientific_execution_authorized"])
        self.assertEqual(record["config_raw_hex"], self.loaded.raw.hex())
        self.assertNotIn("decision", record)

    def test_receipt_boolean_claim_cannot_be_numeric_alias(self):
        path = self.fixture_receipt()
        original = json.loads(path.read_bytes())
        for key, number in (("valid_structure", 1), ("scientific_execution_authorized", 0)):
            changed = copy.deepcopy(original)
            changed["validator_verdict"][key] = number
            path.write_text(json.dumps(changed), encoding="utf-8")
            with self.assertRaises(EmbeddingError):
                bridge.consume_validation_receipt(self.manifest_path, self.checkpoints, root=self.root)

    def test_explicit_development_receipt_does_not_become_final_method(self):
        self.loaded = feasibility_fixtures.owned_development_fixture()
        (self.root/bridge.CONFIG_PATH).write_bytes(self.loaded.raw)
        for entry in self.manifest["inputs"]:
            if entry["path"] == bridge.CONFIG_PATH: entry["sha256"] = self.loaded.sha256
        self.write_manifest()
        if importlib.util.find_spec("jsonschema") is not None:
            path = bridge.write_validation_receipt(self.manifest_path, self.checkpoints, root=self.root)
        else:
            with mock.patch.object(bridge, "load_feasibility_config", return_value=self.loaded):
                path = bridge.write_validation_receipt(self.manifest_path, self.checkpoints, root=self.root)
        got = bridge.consume_validation_receipt(self.manifest_path, self.checkpoints, root=self.root)
        self.assertEqual(type(got), type(self.loaded))
        self.assertEqual(got, self.loaded)
        record = json.loads(path.read_bytes()); self.assertEqual(record["config_kind"], "feasibility")
        record["config_kind"] = "final-method"
        path.write_text(json.dumps(record), encoding="utf-8")
        with self.assertRaises(EmbeddingError):
            bridge.consume_validation_receipt(self.manifest_path, self.checkpoints, root=self.root)

    def test_actual_c1_full_validation_and_malformed_config_rejection(self):
        if importlib.util.find_spec("jsonschema") is None:
            self.skipTest("actual C1 full validator available in Windows controller, not Linux science env")
        path = bridge.write_validation_receipt(self.manifest_path, self.checkpoints, root=self.root)
        self.assertEqual(bridge.consume_validation_receipt(self.manifest_path, self.checkpoints, root=self.root), self.loaded)
        self.assertTrue(path.is_file())
        invalid = copy.deepcopy(self.loaded.value)
        invalid["embedding"]["safety_policy"] = "skip-safety"
        (self.root/bridge.CONFIG_PATH).write_text(json.dumps(invalid), encoding="utf-8")
        for entry in self.manifest["inputs"]:
            if entry["path"] == bridge.CONFIG_PATH:
                entry["sha256"] = hashlib.sha256((self.root/bridge.CONFIG_PATH).read_bytes()).hexdigest()
        self.write_manifest()
        other = Path(self.tmp.name)/"invalid-checkpoints"
        other.mkdir()
        with self.assertRaises(ValueError):
            bridge.write_validation_receipt(self.manifest_path, other, root=self.root)
        self.assertFalse((other/bridge.RECEIPT_NAME).exists())

    def test_changed_run_or_seed_cannot_reuse_receipt(self):
        self.fixture_receipt()
        original = copy.deepcopy(self.manifest)
        for field, value in (("run_id", "other-run"), ("seeds", [8]), ("git_commit", "b"*40)):
            self.manifest = copy.deepcopy(original)
            self.manifest[field] = value
            self.write_manifest()
            with self.subTest(field=field), self.assertRaises(EmbeddingError):
                bridge.consume_validation_receipt(self.manifest_path, self.checkpoints, root=self.root)

    def test_manifest_seed_mismatch_rejects_before_receipt(self):
        self.manifest["seeds"] = [8]
        self.write_manifest()
        with mock.patch.object(bridge, "load_method_config", return_value=self.loaded), self.assertRaises(EmbeddingError):
            bridge.write_validation_receipt(self.manifest_path, self.checkpoints, root=self.root)
        self.assertFalse((self.checkpoints/bridge.RECEIPT_NAME).exists())

    def test_changed_validator_bytes_or_expanded_input_inventory_rejected(self):
        self.fixture_receipt()
        target = self.root/"scripts/validate_method_config.py"
        target.write_bytes(target.read_bytes()+b"\n# owned test mutation\n")
        with self.assertRaises(EmbeddingError):
            bridge.consume_validation_receipt(self.manifest_path, self.checkpoints, root=self.root)
        for entry in self.manifest["inputs"]:
            if entry["path"] == "scripts/validate_method_config.py":
                entry["sha256"] = hashlib.sha256(target.read_bytes()).hexdigest()
        self.write_manifest()
        with self.assertRaises(EmbeddingError):
            bridge.consume_validation_receipt(self.manifest_path, self.checkpoints, root=self.root)

    def test_receipt_mutations_and_added_approval_claim_rejected(self):
        path = self.fixture_receipt()
        original = json.loads(path.read_bytes())
        for field, value in (("config_raw_hex", "7b7d"), ("schema_sha256", "b"*64),
                ("validator_verdict", {"valid_structure": True, "scientific_execution_authorized": True}),
                ("decision", "approve"), ("validation_runtime", {})):
            changed = copy.deepcopy(original)
            changed[field] = value
            path.write_text(json.dumps(changed), encoding="utf-8")
            with self.subTest(field=field), self.assertRaises(EmbeddingError):
                bridge.consume_validation_receipt(self.manifest_path, self.checkpoints, root=self.root)

    def test_missing_dependency_duplicate_or_path_escape_fails_before_validator(self):
        original = copy.deepcopy(self.manifest)
        for name in ("../escape", "/absolute", "C:/absolute", "scripts\\file", "a//b", "a/./b"):
            self.manifest = copy.deepcopy(original)
            self.manifest["inputs"][0]["path"] = name
            self.write_manifest()
            with mock.patch.object(bridge, "load_method_config") as validate, self.assertRaises(EmbeddingError):
                bridge.write_validation_receipt(self.manifest_path, self.checkpoints, root=self.root)
            validate.assert_not_called()
        for entries in (original["inputs"][:-1], original["inputs"]+[original["inputs"][0]]):
            self.manifest = copy.deepcopy(original)
            self.manifest["inputs"] = entries
            self.write_manifest()
            with mock.patch.object(bridge, "load_method_config") as validate, self.assertRaises(EmbeddingError):
                bridge.write_validation_receipt(self.manifest_path, self.checkpoints, root=self.root)
            validate.assert_not_called()

    def test_changed_bytes_during_validation_and_snapshot_mismatch_rejected(self):
        def changed(_):
            path = self.root/"scripts/noise_path_reference.py"
            path.write_bytes(path.read_bytes()+b"\n# mutation\n")
            return self.loaded
        with mock.patch.object(bridge, "load_method_config", side_effect=changed), self.assertRaises(EmbeddingError):
            bridge.write_validation_receipt(self.manifest_path, self.checkpoints, root=self.root)
        self.assertFalse((self.checkpoints/bridge.RECEIPT_NAME).exists())

    def test_existing_receipt_not_overwritten_and_relative_root_refused(self):
        path = self.fixture_receipt()
        raw = path.read_bytes()
        with mock.patch.object(bridge, "load_method_config", return_value=self.loaded), self.assertRaises(FileExistsError):
            bridge.write_validation_receipt(self.manifest_path, self.checkpoints, root=self.root)
        self.assertEqual(path.read_bytes(), raw)
        with self.assertRaises(EmbeddingError):
            bridge.check_inputs(self.manifest_path.read_bytes(), Path("relative"))

    def test_hex_expansion_rejected_before_receipt_publication(self):
        # Valid trailing JSON whitespace is not malformed configuration; its
        # hex-encoded receipt would exceed the child's two-MiB bounded reader.
        padded = self.loaded.raw + b" "*(1_100_000-len(self.loaded.raw))
        self.loaded = dataclasses.replace(self.loaded, raw=padded,
            sha256=hashlib.sha256(padded).hexdigest())
        (self.root/bridge.CONFIG_PATH).write_bytes(padded)
        for entry in self.manifest["inputs"]:
            if entry["path"] == bridge.CONFIG_PATH:
                entry["sha256"] = self.loaded.sha256
        self.write_manifest()
        self.assertLess(len(padded), bridge.MAX_FILE_BYTES)
        if importlib.util.find_spec("jsonschema") is not None:
            # Real full Windows C1 validation, not mock acceptance.
            with self.assertRaisesRegex(EmbeddingError, "serialized C1 bridge receipt"):
                bridge.write_validation_receipt(self.manifest_path, self.checkpoints, root=self.root)
        else:
            # Linux receipt-bound unit check only; no false C1 verdict claim.
            with mock.patch.object(bridge, "load_method_config", return_value=self.loaded), \
                    self.assertRaisesRegex(EmbeddingError, "serialized C1 bridge receipt"):
                bridge.write_validation_receipt(self.manifest_path, self.checkpoints, root=self.root)
        self.assertFalse((self.checkpoints/bridge.RECEIPT_NAME).exists())

    def test_linked_receipt_or_input_ancestor_rejected(self):
        path = self.fixture_receipt()
        link = Path(self.tmp.name)/"linked-checkpoints"
        try:
            link.symlink_to(self.checkpoints, target_is_directory=True)
        except OSError:
            self.skipTest("Windows account cannot create symlinks")
        with self.assertRaises(EmbeddingError):
            bridge.consume_validation_receipt(self.manifest_path, link, root=self.root)
        self.assertTrue(path.is_file())


if __name__ == "__main__":
    unittest.main()
