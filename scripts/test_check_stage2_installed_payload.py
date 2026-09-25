import tempfile
import unittest
import warnings
import zipfile
from pathlib import Path

from check_stage2_installed_payload import compare_payload


class InstalledPayloadTests(unittest.TestCase):
    def test_matching_payload_and_excluded_metadata(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            installed = root / "installed"
            (installed / "alpha").mkdir(parents=True)
            (installed / "alpha" / "module.py").write_bytes(b"VALUE = 1\n")
            wheel = root / "alpha.whl"
            with zipfile.ZipFile(wheel, "w") as archive:
                archive.writestr("alpha/module.py", b"VALUE = 1\n")
                archive.writestr("alpha-1.dist-info/METADATA", b"Name: alpha\n")
            report = compare_payload(wheel, installed)
            self.assertEqual(report["compared_payload_files"], 1)
            self.assertEqual(report["excluded_metadata_files"], 1)
            self.assertEqual(report["failure_count"], 0)

    def test_mismatch_and_data_transform_are_not_silent(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            installed = root / "installed"
            (installed / "alpha").mkdir(parents=True)
            (installed / "alpha" / "module.py").write_bytes(b"changed")
            wheel = root / "alpha.whl"
            with zipfile.ZipFile(wheel, "w") as archive:
                archive.writestr("alpha/module.py", b"original")
                archive.writestr("alpha-1.data/scripts/tool", b"script")
            report = compare_payload(wheel, installed)
            self.assertEqual(report["failure_count"], 1)
            self.assertEqual(report["excluded_data_files"], 1)

    def test_duplicate_or_unsafe_member_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            installed = root / "installed"
            installed.mkdir()
            wheel = root / "alpha.whl"
            with zipfile.ZipFile(wheel, "w") as archive:
                archive.writestr("../outside", b"unsafe")
            with self.assertRaisesRegex(ValueError, "unsafe member path"):
                compare_payload(wheel, installed)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                with zipfile.ZipFile(wheel, "w") as archive:
                    archive.writestr("alpha/module.py", b"one")
                    archive.writestr("alpha/module.py", b"two")
            with self.assertRaisesRegex(ValueError, "duplicate member"):
                compare_payload(wheel, installed)

    def test_metadata_only_wheel_is_not_a_payload_match(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            installed = root / "installed"
            installed.mkdir()
            wheel = root / "alpha.whl"
            with zipfile.ZipFile(wheel, "w") as archive:
                archive.writestr("alpha-1.dist-info/METADATA", b"Name: alpha\n")
            report = compare_payload(wheel, installed)
            self.assertEqual(report["failure_examples"],
                             ["no-package-payload-files"])


if __name__ == "__main__":
    unittest.main()
