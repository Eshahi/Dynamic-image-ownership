"""Synthetic local intake guard tests; never imports a model."""

import tempfile
import unittest
import importlib.util
from pathlib import Path

from b3_local_data_receipt import IntakeError, checked_bytes, source_folder, image_record


class IntakeTests(unittest.TestCase):
    def test_regular_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "source.bin"
            path.write_bytes(b"test")
            self.assertEqual(checked_bytes(path, root), b"test")

    def test_outside_and_missing_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "root"
            root.mkdir()
            outside = Path(directory) / "outside.bin"
            outside.write_bytes(b"test")
            with self.assertRaises(IntakeError):
                checked_bytes(outside, root)
            with self.assertRaises(IntakeError):
                checked_bytes(root / "absent.bin", root)

    def test_single_archive_wrapper_is_explicitly_supported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            wrapper = root / "val2017"
            nested = wrapper / "val2017"
            nested.mkdir(parents=True)
            self.assertEqual(source_folder(root, "val2017"), nested)
            (wrapper / "unexpected.txt").write_text("extra")
            self.assertEqual(source_folder(root, "val2017"), wrapper)

    @unittest.skipUnless(importlib.util.find_spec("PIL"), "Pillow required for decode guard")
    def test_image_bytes_and_corruption(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "synthetic.png"
            Image.new("RGB", (64, 64), "red").save(path)
            result = image_record(path, root, "synthetic", "1", "none")
            self.assertEqual((result["width"], result["height"]), (64, 64))
            self.assertEqual(result["bytes"], path.stat().st_size)
            path.write_bytes(path.read_bytes()[:30])
            with self.assertRaises(Exception):
                image_record(path, root, "synthetic", "1", "none")


if __name__ == "__main__":
    unittest.main()
