import unittest
from build_b3_manifest import manifest_row, reserve_development


class DevelopmentReservationTests(unittest.TestCase):
    def row(self, identity, digest, split="train"):
        return manifest_row("div2k", "div2k-2017", split, identity, identity + ".png", digest,
                            1, 2, 2, "https://example.org/source", "https://example.org/terms", "local only")

    def test_permutation_duplicate_groups_and_validation_holdout(self):
        rows = [self.row("a", "a"*64), self.row("b", "a"*64), self.row("c", "c"*64),
                self.row("d", "d"*64, "valid")]
        result = reserve_development(rows, "f"*64, allocation={"div2k":2})
        self.assertEqual(result, reserve_development(list(reversed(rows)), "f"*64, allocation={"div2k":2}))
        self.assertEqual(len({r["group_id"] for r in result["images"]}),2)
        self.assertTrue(all(r["source_split"] == "train" for r in result["images"]))
        self.assertFalse(result["scientific_compute_authorized"])
        with self.assertRaisesRegex(ValueError, "insufficient"):
            reserve_development(rows, "f"*64, allocation={"div2k":3})

    def test_literal_development_order_and_rights_limit(self):
        rows = [self.row("a", "a"*64), self.row("b", "b"*64)]
        result = reserve_development(rows, "f"*64, allocation={"div2k":2})
        # Independent .NET SHA256 vectors: b=3d2beda3...; a=d90d02ca...
        self.assertEqual([r["source_id"] for r in result["images"]], ["b","a"])
        self.assertEqual(rows[0]["rights_status"], "pending-image-rights")


if __name__ == "__main__":
    unittest.main()
