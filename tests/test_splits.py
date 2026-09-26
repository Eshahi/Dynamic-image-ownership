"""Synthetic component tests; no fabricated actual split manifest."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from b4_metadata_dependence import components, private_record, summarize


class MetadataDependenceTests(unittest.TestCase):
    def test_excluded_prompt_bridge_and_order(self):
        nodes = [{"id":"a", "raw_sha256":"raw-a", "prompt_group":"p"},
                 {"id":"excluded", "raw_sha256":"raw-b", "prompt_group":"p"},
                 {"id":"c", "raw_sha256":"raw-b", "prompt_group":"q"}]
        groups = components(nodes)
        self.assertEqual(groups, [["a", "c", "excluded"]])
        self.assertEqual(groups, components(list(reversed(nodes))))
        summary = summarize(groups, {"a", "c"}, {"a"})
        self.assertEqual(summary["forced_development_members"], 2)
        self.assertEqual(summary["selected_components"], 1)

    def test_producer_and_unknown_quarantine_are_explicit(self):
        nodes = [{"id":"a", "producer_group":"one", "producer_status":"known-hash"},
                 {"id":"b", "producer_group":"one", "producer_status":"known-hash"},
                 {"id":"c", "producer_group":None, "producer_status":"unknown-or-deleted"},
                 {"id":"d", "producer_group":None, "producer_status":"unknown-or-deleted"}]
        self.assertEqual(len(components(nodes)), 4)
        self.assertEqual(components(nodes, True), [["a","b"],["c","d"]])
        with self.assertRaisesRegex(ValueError, "duplicate"):
            components(nodes+nodes[:1])

    def test_metadata_values_and_no_raw_text(self):
        row = {"image_name":"00000000-0000-4000-8000-000000000001.png", "part_id":948,
               "prompt":" Original Private Prompt ", "seed":42, "user_name":"a"*64}
        result = private_record(row)
        self.assertNotIn(row["prompt"], str(result))
        self.assertNotIn(row["user_name"], str(result))
        self.assertEqual(private_record(dict(row, user_name="deleted_account"))["producer_group"], None)
        self.assertEqual(private_record(dict(row, user_name="deleted_acount"))["producer_group"], None)
        for user in ("bad-user", "", 1):
            with self.assertRaises(ValueError):
                private_record(dict(row,user_name=user))
        with self.assertRaises(ValueError):
            private_record(dict(row,seed=True))


if __name__ == "__main__":
    unittest.main()
