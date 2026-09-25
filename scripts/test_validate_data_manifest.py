import csv
import hashlib
import tempfile
import unittest
from pathlib import Path

from validate_data_manifest import FIELDS, validate


def write_manifest(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


class DataManifestTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.assets = self.root / "assets"
        self.assets.mkdir()
        self.image = self.assets / "example.bin"
        self.image.write_bytes(b"synthetic-image-placeholder")
        self.manifest = self.root / "manifest.csv"
        self.row = dict(zip(FIELDS, (
            "ms-coco", "coco-2017", "val2017", "0001", "example.bin",
            hashlib.sha256(self.image.read_bytes()).hexdigest(),
            str(self.image.stat().st_size), "2", "2", "group-1",
            "https://example.org/archive", "https://example.org/terms",
            "pending-image-rights", "No redistribution clearance claimed",
        )))

    def test_checked_bytes_do_not_claim_rights(self):
        write_manifest(self.manifest, [self.row])
        report = validate(self.manifest, self.assets)
        self.assertEqual(report["row_count"], 1)
        self.assertEqual(report["rights_status_counts"],
                         {"pending-image-rights": 1})
        self.assertIn("rights-not-certified", report["status"])

    def test_hash_and_traversal_fail_closed(self):
        bad = dict(self.row, raw_sha256="0" * 64)
        write_manifest(self.manifest, [bad])
        with self.assertRaisesRegex(ValueError, "mismatch"):
            validate(self.manifest, self.assets)
        bad = dict(self.row, relative_path="../example.bin")
        write_manifest(self.manifest, [bad])
        with self.assertRaisesRegex(ValueError, "traversal"):
            validate(self.manifest, self.assets)

    def test_duplicate_id_and_split_group_error(self):
        write_manifest(self.manifest, [self.row, self.row])
        with self.assertRaisesRegex(ValueError, "duplicate source image ID"):
            validate(self.manifest, self.assets)
        copy = self.assets / "copy.bin"
        copy.write_bytes(self.image.read_bytes())
        second = dict(self.row, source_id="0002", relative_path="copy.bin",
                      group_id="different-group")
        write_manifest(self.manifest, [self.row, second])
        with self.assertRaisesRegex(ValueError, "different groups"):
            validate(self.manifest, self.assets)

    def test_empty_and_unknown_rights_fail_closed(self):
        write_manifest(self.manifest, [])
        with self.assertRaisesRegex(ValueError, "no image rows"):
            validate(self.manifest, self.assets)
        write_manifest(self.manifest, [dict(self.row, rights_status="cleared")])
        with self.assertRaisesRegex(ValueError, "unknown rights status"):
            validate(self.manifest, self.assets)

    def test_url_userinfo_and_query_fail_closed(self):
        for source_url in ("https://user:secret@example.org/archive",
                           "https://example.org/archive?token=secret"):
            with self.subTest(source_url=source_url):
                write_manifest(self.manifest, [dict(self.row, source_url=source_url)])
                with self.assertRaisesRegex(ValueError, "URL credentials or query"):
                    validate(self.manifest, self.assets)


if __name__ == "__main__":
    unittest.main()
