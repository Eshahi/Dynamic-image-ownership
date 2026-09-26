import unittest

from b3_source_candidate_order import candidate_order, group_rank, member_rank


class SourceOrderTests(unittest.TestCase):
    def test_literal_revision_bound_vectors(self):
        self.assertEqual(group_rank("a" * 64),
                         "6455fd523e474607d8da2ccf28411df5c83c5a6792ab2906af9a4dd20978cc5f")
        self.assertEqual(member_rank("00000000-0000-4000-8000-000000000001.png"),
                         "370ec891730816c3aa16f75f0ea4936866b72fe951bf38089761a0a491e106d5")

    def name(self, index):
        return f"00000000-0000-4000-8000-{index:012x}.png"

    def fixture(self):
        return {"parts": {"948": {
            self.name(1): {"reason": "metadata_eligible", "prompt_group_sha256": "a" * 64},
            self.name(2): {"reason": "metadata_eligible", "prompt_group_sha256": "a" * 64},
            self.name(3): {"reason": "metadata_eligible", "prompt_group_sha256": "b" * 64},
            self.name(4): {"reason": "score_or_size", "prompt_group_sha256": None}}}}

    def test_permutation_and_pool_preservation(self):
        ledger = self.fixture()
        result = candidate_order(ledger)
        ledger["parts"]["948"] = dict(reversed(list(ledger["parts"]["948"].items())))
        self.assertEqual(result, candidate_order(ledger))
        self.assertEqual(result["group_count"], 2)
        self.assertEqual(result["eligible_member_count"], 3)
        self.assertFalse(result["source_ids_frozen"])
        self.assertFalse(result["study_ids_frozen"])
        self.assertEqual(result["images_removed"], 0)

    def test_malformed_group_or_identity_blocks(self):
        with self.assertRaises(ValueError):
            group_rank("invalid")
        with self.assertRaises(ValueError):
            member_rank("../source.png")
        ledger = self.fixture()
        ledger["parts"]["1232"] = {self.name(1): ledger["parts"]["948"][self.name(1)]}
        with self.assertRaisesRegex(ValueError, "duplicate"):
            candidate_order(ledger)


if __name__ == "__main__":
    unittest.main()
