import hashlib
import tempfile
import unittest
import zipfile
from pathlib import Path

from prepare_science_wheelhouse import materialize, select_wheels


def make_wheel(path: Path) -> str:
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("alpha-1.dist-info/METADATA",
                         "Metadata-Version: 2.1\nName: Alpha\nVersion: 1\n")
        archive.writestr("alpha-1.dist-info/WHEEL",
                         "Wheel-Version: 1.0\nTag: py3-none-any\n")
    return hashlib.sha256(path.read_bytes()).hexdigest()


class WheelhouseTests(unittest.TestCase):
    def test_cached_body_is_named_and_copied_by_exact_hash(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            cache = root / "cache"
            cache.mkdir()
            source = cache / "download.body"
            expected = make_wheel(source)
            output = root / "out"
            report = materialize({("alpha", "1"): expected}, [cache], output)
            self.assertEqual(report["wheel_count"], 1)
            self.assertEqual(hashlib.sha256(
                (output / "alpha-1-py3-none-any.whl").read_bytes()).hexdigest(),
                expected)
            self.assertEqual(materialize({("alpha", "1"): expected},
                                         [cache], output)["wheel_count"], 1)

    def test_missing_hash_and_wrong_existing_target_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            cache = root / "cache"
            cache.mkdir()
            source = cache / "alpha-1-py3-none-any.whl"
            expected = make_wheel(source)
            with self.assertRaisesRegex(ValueError, "missing locked wheels"):
                select_wheels({("alpha", "1"): "0" * 64}, [cache])
            output = root / "out"
            output.mkdir()
            (output / source.name).write_bytes(b"wrong")
            with self.assertRaisesRegex(ValueError, "wrong hash"):
                materialize({("alpha", "1"): expected}, [cache], output)

    def test_output_cannot_be_nested_under_source_cache(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            cache = root / "cache"
            cache.mkdir()
            source = cache / "alpha-1-py3-none-any.whl"
            expected = make_wheel(source)
            with self.assertRaisesRegex(ValueError, "inside a source root"):
                materialize({("alpha", "1"): expected}, [cache], cache / "out")


if __name__ == "__main__":
    unittest.main()
