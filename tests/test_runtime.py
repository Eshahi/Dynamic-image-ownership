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
        manifest = record.finish(status="succeeded", outputs={"sample": output})
        final = json.loads(manifest.read_text(encoding="utf-8"))
        self.assertEqual(final["inputs"]["source_image"]["sha256"],
                         hashlib.sha256(self.input.read_bytes()).hexdigest())
        self.assertEqual(final["outputs"]["sample"]["sha256"],
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
        with self.assertRaisesRegex(RunLogError, "run directory"):
            record.finish(status="succeeded", outputs={"outside": self.input})
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


if __name__ == "__main__":
    unittest.main()
