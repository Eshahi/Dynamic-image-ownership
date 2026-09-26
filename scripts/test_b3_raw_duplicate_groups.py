import csv
import io
import unittest

from b3_raw_duplicate_groups import inventory_records, overlap_groups
from b3_diffusiondb_selection import ranked_parts


class RawOverlapTests(unittest.TestCase):
    def row(self, identity, digest="a" * 64, domain="one", size=10):
        return {"id": identity, "domain": domain, "sha256": digest,
                "bytes": size, "width": 64, "height": 64}

    def test_stable_group_and_order(self):
        rows = [self.row("one:a"), self.row("two:b", domain="two")]
        result = overlap_groups(rows)
        self.assertEqual(result, overlap_groups(list(reversed(rows))))
        self.assertEqual(result["cross_source_group_count"], 1)
        original = result["duplicate_groups"][0]["group_id"]
        rows.append(self.row("three:c", domain="three"))
        self.assertEqual(overlap_groups(rows)["duplicate_groups"][0]["group_id"], original)
        self.assertFalse(result["decoded_or_near_duplicates_checked"])
        self.assertFalse(result["study_ids_frozen"])

    def test_identity_and_digest_conflicts_block(self):
        with self.assertRaisesRegex(ValueError, "identity"):
            overlap_groups([self.row("a"), self.row("a", "b" * 64)])
        with self.assertRaisesRegex(ValueError, "conflicting"):
            overlap_groups([self.row("a"), self.row("b", size=11)])

    def zip_csv(self, count=1000, part=None):
        stream = io.StringIO()
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["part_id", "image_name", "bytes", "sha256", "width", "height", "mode"])
        chosen_part = part or ranked_parts()[0]
        for index in range(count):
            # Unique, syntactically valid UUIDv4 fixtures; no dataset identity claim.
            name = f"00000000-0000-4000-8000-{index:012x}.png"
            writer.writerow([chosen_part, name, 10, "a" * 64, 64, 64, "RGB"])
        return stream.getvalue().encode()

    def test_full_zip_frame_and_partial_rejection(self):
        self.assertEqual(len(inventory_records(self.zip_csv())), 1000)
        with self.assertRaisesRegex(ValueError, "complete"):
            inventory_records(self.zip_csv(999))
        with self.assertRaisesRegex(ValueError, "outside"):
            inventory_records(self.zip_csv(part=2001))

    def test_malformed_headers_and_digest_block(self):
        with self.assertRaisesRegex(ValueError, "columns"):
            inventory_records(b"source,source\na,b\n")
        with self.assertRaisesRegex(ValueError, "digest"):
            inventory_records(self.zip_csv().replace(b"a" * 64, b"invalid", 1))

    def test_parts_are_not_different_sources(self):
        result = overlap_groups([self.row("p:a", domain="diffusiondb2m-part-000948"),
                                 self.row("q:b", domain="diffusiondb2m-part-001232")])
        self.assertEqual(result["cross_source_group_count"], 0)
        self.assertEqual(result["cross_inventory_domain_group_count"], 1)


if __name__ == "__main__":
    unittest.main()
