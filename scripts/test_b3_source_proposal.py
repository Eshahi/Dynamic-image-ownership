import unittest

from b3_source_proposal import propose_sources


class SourceProposalTests(unittest.TestCase):
    def fixture(self):
        members = [{"part_id": 948, "image_name": name, "member_rank_sha256": str(i)}
                   for i, name in enumerate(("a.png", "b.png", "c.png", "d.png"))]
        pool = {"group_count": 3, "ranked_prompt_groups": [
            {"ordered_members": members[:1]}, {"ordered_members": members[1:3]},
            {"ordered_members": members[3:]}]}
        records = [dict(domain="diffusiondb2m-part-000948", id="948:" + member["image_name"],
                        sha256=digest, bytes="4", width="2", height="2")
                   for member, digest in zip(members, ("a"*64, "a"*64, "c"*64, "d"*64))]
        return pool, records

    def test_ordered_member_fallback_and_no_false_acceptance(self):
        pool, records = self.fixture()
        result = propose_sources(pool, records, target=2)
        self.assertEqual([r["image_name"] for r in result["selected"]], ["a.png", "c.png"])
        self.assertEqual(result["skipped_members"][0]["image_name"], "b.png")
        self.assertEqual(result["raw_byte_duplicate_skips"], 1)
        self.assertFalse(result["source_ids_frozen"])
        self.assertFalse(result["rights_cleared"])
        self.assertEqual(result, propose_sources(pool, list(reversed(records)), target=2))

    def test_whole_pool_missing_member_blocks_before_prefix(self):
        pool, records = self.fixture()
        with self.assertRaisesRegex(ValueError, "missing"):
            propose_sources(pool, records[:-1], target=1)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            propose_sources(pool, records + records[:1], target=1)
        with self.assertRaisesRegex(ValueError, "insufficient"):
            propose_sources(pool, records, target=4)
        for target in (True, 0, -1):
            with self.assertRaises(ValueError):
                propose_sources(pool, records, target=target)


if __name__ == "__main__":
    unittest.main()
