import unittest
from unittest.mock import patch

from b3_diffusiondb_eligibility_index import build_index, eligibility_record
from b3_diffusiondb_selection import MAX_PARTS, SelectionError, ranked_parts
from b3_read_diffusiondb_metadata import notify_observer


class EligibilityIndexTests(unittest.TestCase):
    def row(self, **changes):
        row = {"image_name": "00000000-0000-4000-8000-000000000001.png", "part_id": 1,
               "width": 512, "height": 512, "image_nsfw": 0.0, "prompt_nsfw": 0.0,
               "prompt": "Example  text"}
        row.update(changes)
        return row

    def test_group_normalization_without_prompt_export(self):
        _, record = eligibility_record(self.row())
        self.assertEqual(record, eligibility_record(self.row(prompt="  example text  "))[1])
        self.assertEqual(record["reason"], "metadata_eligible")
        self.assertEqual(set(record), {"reason", "prompt_group_sha256"})

    def test_observer_cannot_modify_authoritative_row(self):
        row = self.row()
        original = dict(row)

        def mutate(record):
            record["image_nsfw"] = 0.99

        with self.assertRaises(TypeError):
            notify_observer(mutate, row)
        self.assertEqual(row, original)
        seen = []
        notify_observer(lambda record: seen.append(eligibility_record(record)), row)
        self.assertEqual(seen, [eligibility_record(original)])

    def test_cutoff_sentinel_empty_and_precedence(self):
        self.assertEqual(eligibility_record(self.row(image_nsfw=0.10))[1]["reason"], "score_or_size")
        self.assertEqual(eligibility_record(self.row(image_nsfw=2.0))[1]["reason"], "score_or_size")
        self.assertEqual(eligibility_record(self.row(prompt="  "))[1]["reason"], "empty_prompt")
        record = eligibility_record(self.row(width=63, prompt=""))[1]
        self.assertEqual(record, {"reason": "score_or_size", "prompt_group_sha256": None})

    def test_malformed_excluded_values_still_block(self):
        for changes in ({"width": True}, {"prompt": None, "image_nsfw": 2.0},
                        {"prompt_nsfw": float("nan")}, {"image_nsfw": 3.0}):
            with self.subTest(changes=changes), self.assertRaises(SelectionError):
                eligibility_record(self.row(**changes))

    def test_incomplete_frame_or_production_mismatch_blocks(self):
        with patch("b3_diffusiondb_eligibility_index.select_local_metadata",
                   return_value={"status": "blocked_missing_ranked_part_metadata"}):
            with self.assertRaisesRegex(SelectionError, "production"):
                build_index(None)

    def test_complete_synthetic_frame_and_aggregate_disagreement(self):
        parts = list(ranked_parts()[:MAX_PARTS])

        def replay(path, candidate_observer):
            for part in parts:
                for index in range(1000):
                    candidate_observer(self.row(part_id=part,
                        image_name=f"{part:08x}-0000-4000-8000-{index:012x}.png"))
            return {"status": "candidate_parts_ready", "selected_part_ids": parts,
                    "distinct_prompt_groups": 1, "rows_excluded_by_score_or_size": 0,
                    "rows_excluded_by_empty_prompt": 0}

        with patch("b3_diffusiondb_eligibility_index.select_local_metadata", side_effect=replay):
            result = build_index(None)
            self.assertEqual(result["eligibility_counts"], {"metadata_eligible": 14000})
            self.assertFalse(result["source_ids_frozen"])

        def mismatch(path, candidate_observer):
            receipt = replay(path, candidate_observer)
            receipt["distinct_prompt_groups"] = 2
            return receipt

        with patch("b3_diffusiondb_eligibility_index.select_local_metadata", side_effect=mismatch):
            with self.assertRaisesRegex(SelectionError, "disagree"):
                build_index(None)
        with patch("b3_diffusiondb_eligibility_index.select_local_metadata",
                   return_value={"status": "candidate_parts_ready", "selected_part_ids": []}):
            with self.assertRaisesRegex(SelectionError, "production"):
                build_index(None)


if __name__ == "__main__":
    unittest.main()
