import hashlib
import tempfile
import unittest
import zipfile
from pathlib import Path

from audit_science_wheels import audit, parse_lock, wheel_identity


class ScienceWheelAuditTests(unittest.TestCase):
    def test_lock_rejects_duplicate_and_unhashed_line(self):
        value = "alpha==1 --hash=sha256:" + "a" * 64
        with self.assertRaises(ValueError):
            parse_lock(value + "\n" + value)
        with self.assertRaises(ValueError):
            parse_lock("alpha==1")

    def test_cached_wheel_matches_lock_and_reports_missing_dependency(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            wheel = root / "alpha-1-py3-none-any.whl"
            with zipfile.ZipFile(wheel, "w") as archive:
                archive.writestr("alpha-1.dist-info/METADATA",
                                 "Metadata-Version: 2.1\nName: Alpha\nVersion: 1\n")
            self.assertEqual(wheel_identity(wheel), ("alpha", "1"))
            expected = hashlib.sha256(wheel.read_bytes()).hexdigest()
            report = audit({"alpha": "1", "beta": "2"}, [root],
                           parse_lock(f"alpha==1 --hash=sha256:{expected}"))
            self.assertEqual(report["locked_failures"], [])
            self.assertEqual(report["installed_without_cached_wheel"], ["beta==2"])
            self.assertEqual(report["status"], "partial_inventory")

    def test_hash_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            wheel = root / "alpha-1-py3-none-any.whl"
            with zipfile.ZipFile(wheel, "w") as archive:
                archive.writestr("alpha-1.dist-info/METADATA",
                                 "Metadata-Version: 2.1\nName: Alpha\nVersion: 1\n")
            report = audit({"alpha": "1"}, [root],
                           parse_lock("alpha==1 --hash=sha256:" + "0" * 64))
            self.assertEqual(report["locked_failures"],
                             ["alpha==1:wheel-hash-missing"])

    def test_invalid_wheel_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "broken.whl").write_bytes(b"not a wheel")
            with self.assertRaises(ValueError):
                audit({}, [root], {("alpha", "1"): "0" * 64})


if __name__ == "__main__":
    unittest.main()
