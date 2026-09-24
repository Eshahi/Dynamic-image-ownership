"""Model-free inventory tests for the bounded A6 local loader preflight."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from check_a6_local_model_load import REQUIRED_SD_FILES, _check_model_inventory


class InventoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.model_dir = Path(self.temp.name) / "sd15-fp16"
        for name in REQUIRED_SD_FILES:
            path = self.model_dir / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()
        self.lock = {"files": [{"path": f"sd15-fp16/{name}"}
                               for name in sorted(REQUIRED_SD_FILES)]}

    def test_exact_inventory(self) -> None:
        _check_model_inventory(self.model_dir, self.lock)

    def test_missing_lock_entry(self) -> None:
        self.lock["files"].pop()
        with self.assertRaisesRegex(ValueError, "lock must list exactly"):
            _check_model_inventory(self.model_dir, self.lock)

    def test_unlisted_file(self) -> None:
        (self.model_dir / "unet" / "pytorch_model.bin").touch()
        with self.assertRaisesRegex(ValueError, "unlisted regular files"):
            _check_model_inventory(self.model_dir, self.lock)


if __name__ == "__main__":
    unittest.main()
