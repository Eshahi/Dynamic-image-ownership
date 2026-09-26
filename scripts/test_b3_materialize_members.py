import hashlib
import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from b3_materialize_members import stage_selected, unique_selected_mapping
from test_b3_diffusiondb_archive_receipt import Image, fixture


class SelectionMappingTests(unittest.TestCase):
    def test_duplicate_json_keys_block(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            json.loads('{"same": "first", "same": "second"}', object_pairs_hook=unique_selected_mapping)


@unittest.skipIf(Image is None, "Pillow absent from workflow-only interpreter")
class MemberStagingTests(unittest.TestCase):
    def fixture_bytes(self):
        expected, _ = fixture()
        image = io.BytesIO()
        Image.new("RGB", (2, 2), "red").save(image, format="PNG")
        output = io.BytesIO()
        with zipfile.ZipFile(output, "w") as archive:
            for name in expected:
                archive.writestr(name, image.getvalue())
            archive.writestr("part-000948.json", b"{}")
        name = next(iter(expected))
        return output.getvalue(), expected, name, image.getvalue()

    def test_preview_and_only_exact_selected_bytes(self):
        payload, expected, name, image = self.fixture_bytes()
        selected = {name: hashlib.sha256(image).hexdigest()}
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            result = stage_selected(payload, 948, expected, selected, root)
            self.assertEqual(result["files_written"], 0)
            self.assertEqual(list(root.iterdir()), [])
            result = stage_selected(payload, 948, expected, selected, root, execute=True)
            output = root / "part-000948" / name
            self.assertEqual(output.read_bytes(), image)
            self.assertEqual(len(list(output.parent.iterdir())), 1)
            self.assertEqual(result["files_written"], 1)
            self.assertFalse(result["source_ids_frozen"])
            with self.assertRaisesRegex(ValueError, "exists"):
                stage_selected(payload, 948, expected, selected, root, execute=True)

    def test_invalid_selection_or_link_blocks_before_write(self):
        payload, expected, name, image = self.fixture_bytes()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            with self.assertRaisesRegex(ValueError, "absolute"):
                stage_selected(payload, 948, expected, {name: hashlib.sha256(image).hexdigest()}, Path("."), execute=True)
            for selected in ({name: "0" * 64}, {"../unsafe.png": "0" * 64}, {}):
                with self.subTest(selected=selected), self.assertRaises(ValueError):
                    stage_selected(payload, 948, expected, selected, root, execute=True)
                self.assertEqual(list(root.iterdir()), [])
            target = root / "real"
            target.mkdir()
            linked = root / "linked"
            try:
                linked.symlink_to(target, target_is_directory=True)
            except OSError:
                return
            with self.assertRaisesRegex(ValueError, "unlinked"):
                stage_selected(payload, 948, expected, {name: hashlib.sha256(image).hexdigest()}, linked)


if __name__ == "__main__":
    unittest.main()
