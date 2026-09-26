"""Synthetic adversarial ZIP tests; no network, extraction or models."""

import copy
import io
import stat
import unittest
import uuid
import zipfile

from b3_diffusiondb_archive_receipt import MAX_MEMBER_BYTES, inspect_archive, validate_directory

try:
    from PIL import Image
except ImportError:
    Image = None


def fixture():
    expected = {str(uuid.UUID(int=n + 1, version=4)) + ".png": {"width": 2, "height": 2}
                for n in range(1000)}
    entries = []
    for name in list(expected) + ["part-000948.json"]:
        entry = zipfile.ZipInfo(name)
        entry.file_size = 100
        entry.compress_size = 100
        entry.external_attr = (stat.S_IFREG | 0o644) << 16
        entries.append(entry)
    return expected, entries


class ArchiveDirectoryTests(unittest.TestCase):
    def test_exact_membership_and_whole_frame(self):
        expected, entries = fixture()
        self.assertEqual(validate_directory(entries, 948, expected), 100100)
        for removed in (1, 1000):
            with self.assertRaisesRegex(ValueError, "cardinality"):
                validate_directory(entries[:-removed], 948, expected)

    def test_duplicate_traversal_links_encryption_and_byte_caps_block(self):
        expected, entries = fixture()
        for mutation in ("duplicate", "path", "symlink", "encrypted", "compression", "bytes", "directory"):
            changed = copy.deepcopy(entries)
            if mutation == "duplicate":
                changed[-1] = copy.deepcopy(changed[0])
            elif mutation == "path":
                changed[0].filename = "../" + changed[0].filename
            elif mutation == "symlink":
                changed[0].external_attr = (stat.S_IFLNK | 0o777) << 16
            elif mutation == "encrypted":
                changed[0].flag_bits |= 1
            elif mutation == "compression":
                changed[0].compress_type = zipfile.ZIP_LZMA
            elif mutation == "bytes":
                changed[0].file_size = MAX_MEMBER_BYTES + 1
            else:
                changed[0].external_attr |= 0x10
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                validate_directory(changed, 948, expected)

    def test_expected_metadata_and_json_name_fail_closed(self):
        expected, entries = fixture()
        for dimension in (True, 0, "2", 100000000):
            changed = copy.deepcopy(expected)
            changed[next(iter(changed))]["width"] = dimension
            with self.subTest(dimension=dimension), self.assertRaises(ValueError):
                validate_directory(entries, 948, changed)
        with self.assertRaises(ValueError):
            validate_directory(entries, 1232, expected)


@unittest.skipIf(Image is None, "Pillow is not installed in workflow-only interpreter")
class ArchiveDecodeTests(unittest.TestCase):
    def payload(self, *, wrong_dimensions=False, corrupt=False):
        expected, _ = fixture()
        image = io.BytesIO()
        Image.new("RGB", (3, 2) if wrong_dimensions else (2, 2), "red").save(image, format="PNG")
        output = io.BytesIO()
        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED) as archive:
            for name in expected:
                archive.writestr(name, image.getvalue())
            # Metadata intentionally is not valid JSON: its integrity, not private content, is checked.
            archive.writestr("part-000948.json", b"unparsed private metadata")
        payload = bytearray(output.getvalue())
        if corrupt:
            # Change first PNG body without updating ZIP CRC.
            offset = payload.find(image.getvalue())
            payload[offset + 15] ^= 1
        return bytes(payload), expected

    def test_full_crc_decode_and_no_metadata_content_export(self):
        payload, expected = self.payload()
        records, result = inspect_archive(payload, 948, expected)
        self.assertEqual(len(records), 1000)
        self.assertEqual(result["images"], 1000)
        self.assertEqual(result["zip_members"], 1001)
        self.assertEqual(len(result["archive_json_sha256"]), 64)
        self.assertTrue(all(row["mode"] == "RGB" for row in records))

    def test_dimension_or_crc_corruption_blocks(self):
        payload, expected = self.payload(wrong_dimensions=True)
        with self.assertRaisesRegex(ValueError, "mismatch"):
            inspect_archive(payload, 948, expected)
        payload, expected = self.payload(corrupt=True)
        with self.assertRaises(zipfile.BadZipFile):
            inspect_archive(payload, 948, expected)


if __name__ == "__main__":
    unittest.main()
