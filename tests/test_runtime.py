"""C1 provenance tests use synthetic bytes only; no experiment is executed."""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))
sys.path.insert(0, str(PROJECT / "scripts"))

from src.runtime.config import ConfigError, SCHEMA, load_method_config  # noqa: E402
from src.runtime.logging import RunLogError, recorded_run, start_run  # noqa: E402
from test_validate_method_config import detector_id, specimen  # noqa: E402


class RuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.runs = self.root / "runs"
        self.runs.mkdir()
        self.config_path = self.root / "method.json"
        self.input = self.root / "input.bin"
        self.input.write_bytes(b"synthetic input")
        self.environment = self.root / "environment.json"
        self.environment.write_text('{"test":"synthetic"}', encoding="utf-8")
        config = specimen(json.loads(SCHEMA.read_text(encoding="utf-8")))
        config["embedding"]["scheduler"]["strength"] = 1
        config["embedding"]["alpha_s"] = 1
        config["dct"]["config_id"] = detector_id(config)
        self.config_path.write_text(json.dumps(config), encoding="utf-8")

    def start(self):
        with patch("src.runtime.logging._git_code", return_value={
            "git_commit": "a" * 40, "git_state": "clean"
        }):
            return start_run(self.runs, config_path=self.config_path,
                             inputs={"source_image": self.input},
                             environment_receipt=self.environment,
                             seeds={"method": 1234}, parameters={"batch": 1})

    def test_valid_contract_and_unique_immutable_run(self):
        loaded = load_method_config(self.config_path)
        self.assertEqual(loaded.sha256, hashlib.sha256(self.config_path.read_bytes()).hexdigest())
        record = self.start()
        second = self.start()
        self.assertNotEqual(record.directory, second.directory)
        self.assertEqual((record.directory / "config.json").read_bytes(), self.config_path.read_bytes())
        output = record.directory / "sample.bin"
        output.write_bytes(b"synthetic result")
        manifest = record.finish(status="succeeded")
        final = json.loads(manifest.read_text(encoding="utf-8"))
        self.assertEqual(final["inputs"]["source_image"]["sha256"],
                         hashlib.sha256(self.input.read_bytes()).hexdigest())
        self.assertEqual(final["outputs"]["sample.bin"]["sha256"],
                         hashlib.sha256(output.read_bytes()).hexdigest())
        self.assertFalse(final["scientific_execution_authorized"])
        with self.assertRaisesRegex(RunLogError, "already finalized"):
            record.finish(status="succeeded")

    def test_invalid_config_fails_before_run_directory(self):
        config = json.loads(self.config_path.read_text(encoding="utf-8"))
        config["calibration"]["threshold_version"] = "TBD"
        self.config_path.write_text(json.dumps(config), encoding="utf-8")
        with self.assertRaises(ConfigError):
            self.start()
        self.assertEqual(list(self.runs.iterdir()), [])

    def test_duplicate_json_key_rejected_before_run_directory(self):
        self.config_path.write_bytes(b'{"a":1,"a":2}')
        with self.assertRaisesRegex(ConfigError, "duplicate JSON key"):
            self.start()
        self.assertEqual(list(self.runs.iterdir()), [])

    def test_failed_and_interrupted_attempts_remain_visible(self):
        failed = self.start()
        failed.finish(status="failed", failure="synthetic decoder error")
        self.assertEqual(json.loads((failed.directory / "manifest.json").read_text())
                         ["failure"], "synthetic decoder error")
        interrupted = self.start()
        self.assertTrue((interrupted.directory / "start.json").exists())
        self.assertFalse((interrupted.directory / "manifest.json").exists())

    def test_bad_seed_and_output_escape_fail_closed(self):
        with patch("src.runtime.logging._git_code", return_value={
            "git_commit": "a" * 40, "git_state": "clean"
        }):
            with self.assertRaisesRegex(RunLogError, "seeds"):
                start_run(self.runs, config_path=self.config_path,
                          inputs={"source_image": self.input},
                          environment_receipt=self.environment,
                          seeds={"method": True}, parameters={})
        self.assertEqual(list(self.runs.iterdir()), [])
        record = self.start()
        try:
            (record.directory / "linked.bin").symlink_to(self.input)
        except OSError:
            self.skipTest("this Windows account cannot create symlinks")
        with self.assertRaisesRegex(RunLogError, "linked run artifact"):
            record.finish(status="succeeded")
        self.assertFalse((record.directory / "manifest.json").exists())

    def test_context_records_exception_type_without_sensitive_message(self):
        with patch("src.runtime.logging._git_code", return_value={
            "git_commit": "a" * 40, "git_state": "clean"
        }):
            with self.assertRaisesRegex(RuntimeError, "secret-not-for-log"):
                with recorded_run(self.runs, config_path=self.config_path,
                                  inputs={"source_image": self.input},
                                  environment_receipt=self.environment,
                                  seeds={"method": 1234}, parameters={}):
                    raise RuntimeError("secret-not-for-log")
        (directory,) = self.runs.iterdir()
        final = (directory / "manifest.json").read_text(encoding="utf-8")
        self.assertIn('"failure":"RuntimeError"', final)
        self.assertNotIn("secret-not-for-log", final)

    def test_context_inventories_outputs_and_later_failure_cannot_be_success(self):
        with patch("src.runtime.logging._git_code", return_value={
            "git_commit": "a" * 40, "git_state": "clean"
        }):
            with self.assertRaises(RuntimeError):
                with recorded_run(self.runs, config_path=self.config_path,
                                  inputs={"source_image": self.input},
                                  environment_receipt=self.environment,
                                  seeds={"method": 1234}, parameters={}) as output_dir:
                    (output_dir / "partial.bin").write_bytes(b"partial")
                    raise RuntimeError("later failure")
        (directory,) = self.runs.iterdir()
        final = json.loads((directory / "manifest.json").read_text())
        self.assertEqual(final["status"], "failed")
        self.assertEqual(final["outputs"]["partial.bin"]["sha256"],
                         hashlib.sha256(b"partial").hexdigest())

    def test_start_snapshot_is_immune_to_caller_mutation(self):
        record = self.start()
        self.assertIsInstance(record.start_raw, bytes)
        record.finish(status="succeeded")
        final = json.loads((record.directory / "manifest.json").read_text())
        self.assertEqual(final["seeds"]["method"], 1234)

    def test_changed_config_snapshot_cannot_be_finalized(self):
        record = self.start()
        (record.directory / "config.json").write_bytes(b"{}")
        with self.assertRaisesRegex(RunLogError, "config snapshot changed"):
            record.finish(status="succeeded")
        self.assertFalse((record.directory / "manifest.json").exists())

    def test_staging_write_failure_never_exposes_canonical_run(self):
        from src.runtime import logging as logging_module
        original = logging_module._write_once
        calls = 0

        def fail_second(path, raw):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("synthetic disk fault")
            return original(path, raw)

        with patch("src.runtime.logging._git_code", return_value={
            "git_commit": "a" * 40, "git_state": "clean"
        }), patch("src.runtime.logging._write_once", side_effect=fail_second):
            with self.assertRaises(OSError):
                start_run(self.runs, config_path=self.config_path,
                          inputs={"source_image": self.input},
                          environment_receipt=self.environment,
                          seeds={"method": 1234}, parameters={})
        (staging,) = self.runs.iterdir()
        self.assertTrue(staging.name.startswith(".staging-"))
        self.assertFalse((staging / "start.json").exists())


if __name__ == "__main__":
    unittest.main()
