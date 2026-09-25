"""Model-free LPIPS package byte-identity tests."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from check_a6_lpips_assets import PACKAGE_FILES, verify_package


class PackageIdentityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for relative in PACKAGE_FILES:
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"x" * 6009 if relative == "weights/v0.1/alex.pth"
                             else b"synthetic test bytes")

    def test_known_hashes_accept(self) -> None:
        fake_hash = {relative: "test" for relative in PACKAGE_FILES}
        with patch("check_a6_lpips_assets.PACKAGE_FILES", fake_hash), \
                patch("check_a6_lpips_assets._file_digest", return_value="test"):
            self.assertEqual(verify_package(self.root), fake_hash)

    def test_missing_file_rejected(self) -> None:
        (self.root / "weights/v0.1/alex.pth").unlink()
        matching_digest = lambda path: PACKAGE_FILES[path.relative_to(self.root).as_posix()]
        with patch("check_a6_lpips_assets._file_digest", side_effect=matching_digest), \
                self.assertRaisesRegex(ValueError, "missing LPIPS file"):
            verify_package(self.root)

    def test_hash_mismatch_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "LPIPS SHA-256 mismatch"):
            verify_package(self.root)


if __name__ == "__main__":
    unittest.main()
