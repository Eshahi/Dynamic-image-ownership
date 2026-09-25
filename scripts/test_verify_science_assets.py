"""Synthetic, model-free checks for the A6 local asset-identity verifier."""

import hashlib
import importlib.util
import pathlib
import tempfile
import unittest


SPEC = importlib.util.spec_from_file_location(
    "verify_science_assets", pathlib.Path(__file__).with_name("verify_science_assets.py")
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class AssetIdentityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = pathlib.Path(self.tmp.name)
        (self.root / "model").mkdir()
        (self.root / "model" / "weights.safetensors").write_bytes(b"synthetic")
        self.lock = {"schema_version": MODULE.SCHEMA_VERSION, "files": [{
            "path": "model/weights.safetensors", "size_bytes": 9,
            "sha256": hashlib.sha256(b"synthetic").hexdigest()}]}

    def test_matches_only_listed_bytes(self):
        receipt = MODULE.verify(self.root, self.lock)
        self.assertEqual(receipt["scope"], "listed-files-only")
        self.assertEqual(receipt["files"][0]["sha256"], self.lock["files"][0]["sha256"])

    def test_fails_on_missing_size_and_digest(self):
        file = self.root / "model" / "weights.safetensors"
        file.write_bytes(b"different")
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            MODULE.verify(self.root, self.lock)
        file.write_bytes(b"short")
        with self.assertRaisesRegex(ValueError, "size mismatch"):
            MODULE.verify(self.root, self.lock)
        file.unlink()
        with self.assertRaisesRegex(ValueError, "missing"):
            MODULE.verify(self.root, self.lock)

    def test_rejects_path_escape_and_duplicates(self):
        for value in ("../outside", "/absolute", "model/../other", "model\\other", "C:drive"):
            with self.subTest(value=value):
                self.lock["files"][0]["path"] = value
                with self.assertRaises(ValueError):
                    MODULE.verify(self.root, self.lock)
        self.lock["files"][0]["path"] = "model/weights.safetensors"
        self.lock["files"].append(dict(self.lock["files"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            MODULE.verify(self.root, self.lock)

    def test_rejects_malformed_lock(self):
        for value in (True, -1, 1.5):
            with self.subTest(value=value):
                self.lock["files"][0]["size_bytes"] = value
                with self.assertRaises(ValueError):
                    MODULE.verify(self.root, self.lock)

    def test_rejects_symlink_when_available(self):
        source = self.root / "model" / "weights.safetensors"
        link = self.root / "model" / "link.safetensors"
        try:
            link.symlink_to(source)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable on this host")
        self.lock["files"][0]["path"] = "model/link.safetensors"
        with self.assertRaisesRegex(ValueError, "linked"):
            MODULE.verify(self.root, self.lock)


if __name__ == "__main__":
    unittest.main()
