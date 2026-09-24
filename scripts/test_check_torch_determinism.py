"""Model-free deterministic-setting contract tests with a fake Torch API."""

import importlib.util
import pathlib
import types
import unittest
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location(
    "check_torch_determinism", pathlib.Path(__file__).with_name("check_torch_determinism.py")
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class FakeTorch:
    __version__ = "synthetic"
    version = types.SimpleNamespace(cuda=None)

    def __init__(self):
        self.backends = types.SimpleNamespace(
            fp32_precision="tf32",
            cuda=types.SimpleNamespace(matmul=types.SimpleNamespace(fp32_precision="tf32")),
            cudnn=types.SimpleNamespace(benchmark=True, deterministic=False, fp32_precision="tf32"),
        )
        self.seed = None
        self.deterministic = False

    def manual_seed(self, value):
        self.seed = value

    def use_deterministic_algorithms(self, value, *, warn_only):
        self.deterministic = value and not warn_only

    def are_deterministic_algorithms_enabled(self):
        return self.deterministic


class DeterminismSettingTests(unittest.TestCase):
    def test_launcher_fails_closed(self):
        good = {"CUBLAS_WORKSPACE_CONFIG": ":4096:8", "PYTHONHASHSEED": "0"}
        MODULE.check_launcher(good, {})
        for changed, loaded in (({"PYTHONHASHSEED": "1"}, {}),
                                ({"CUBLAS_WORKSPACE_CONFIG": ":16:8"}, {}),
                                ({}, {"torch": object()})):
            with self.subTest(changed=changed, loaded=loaded), self.assertRaises(ValueError):
                MODULE.check_launcher(good | changed, loaded)

    @patch.dict(MODULE.os.environ, {"CUBLAS_WORKSPACE_CONFIG": ":4096:8", "PYTHONHASHSEED": "0"})
    def test_configure_exact_flags_and_seed(self):
        torch = FakeTorch()
        record = MODULE.configure(torch, 2**64 - 1)
        self.assertEqual(torch.seed, 2**64 - 1)
        self.assertTrue(torch.deterministic)
        self.assertFalse(torch.backends.cudnn.benchmark)
        self.assertEqual(torch.backends.cuda.matmul.fp32_precision, "ieee")
        self.assertEqual(record["scope"], "settings-only-no-kernel-parity")
        self.assertFalse(record["numpy_seeded"])

    def test_rejects_invalid_seed(self):
        for value in (-1, 2**64, True, 1.0):
            with self.subTest(value=value), self.assertRaises(ValueError):
                MODULE.configure(FakeTorch(), value)


if __name__ == "__main__":
    unittest.main()
