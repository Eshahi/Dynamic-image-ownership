"""Synthetic contract tests for the read-only A6 inventory."""

import importlib.util
import pathlib
import unittest
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location(
    "capture_environment", pathlib.Path(__file__).with_name("capture_environment.py")
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class CaptureEnvironmentTests(unittest.TestCase):
    def test_parse_gpu(self):
        gpu = MODULE.parse_gpus("0, NVIDIA GPU, 610.88, 12227, 11501, 12.0\n")
        self.assertEqual(gpu[0]["compute_capability"], "12.0")
        self.assertEqual(gpu[0]["free_mib"], 11501)

    def test_rejects_malformed_gpu(self):
        for text in ("", "0, GPU, 610.88, 12227\n", "0, GPU, 610.88, 12227, 13000, 12.0\n"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                MODULE.parse_gpus(text)

    @patch.object(MODULE.shutil, "which", return_value=None)
    def test_missing_nvidia_smi_is_explicit(self, _which):
        self.assertEqual(MODULE.gpu_snapshot()["status"], "nvidia-smi-not-found")

    @patch.object(MODULE, "git_output", side_effect=["", "a" * 40])
    @patch.object(MODULE, "gpu_snapshot", return_value={"status": "nvidia-smi-not-found", "devices": []})
    def test_capture_has_lock_and_clean_status(self, _gpu, _git):
        project = pathlib.Path(__file__).resolve().parent.parent
        record = MODULE.capture(project)
        self.assertEqual(record["git_commit"], "a" * 40)
        self.assertFalse(record["git_dirty"])
        self.assertEqual(len(record["requirements_lock_sha256"]), 64)
        self.assertIn("torch", record["packages"])
        self.assertNotIn("environment_variables", record)


if __name__ == "__main__":
    unittest.main()
