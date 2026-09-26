"""Synthetic metadata-only tests; no Parquet or image download."""

import unittest
import uuid

from b3_diffusiondb_selection import (
    MAX_PARTS, NSFW_CEILING, REVISION, SelectionError,
    candidate_part_handoff, ranked_parts,
)


def row(part: int, number: int, *, score: float = 0.0, prompt: str | None = None):
    return {"part_id": part, "image_name": str(uuid.UUID(int=number + 1, version=4)) + ".png",
            "width": 512, "height": 512, "image_nsfw": score,
            "prompt_nsfw": 0.0, "prompt": prompt or f"synthetic prompt {number}"}


class DiffusionDBSelectionTests(unittest.TestCase):
    def test_revision_bound_part_order_is_complete_and_stable(self):
        order = ranked_parts()
        self.assertEqual(len(order), 2000)
        self.assertEqual(set(order), set(range(1, 2001)))
        self.assertEqual(len(REVISION), 40)
        self.assertEqual(order, ranked_parts())

    def test_minimum_prefix_and_order_independence(self):
        parts = ranked_parts()[:MAX_PARTS]
        rows = [row(parts[n // 1000], n) for n in range(MAX_PARTS * 1000)]
        forward = candidate_part_handoff(rows)
        reverse = candidate_part_handoff(reversed(rows))
        self.assertEqual(forward, reverse)
        self.assertEqual(forward["status"], "candidate_parts_ready")
        self.assertEqual(forward["selected_part_ids"], list(parts[:6]))
        self.assertEqual(forward["distinct_prompt_groups"], 6000)
        self.assertFalse(forward["image_ids_frozen"])

    def test_insufficient_or_nsfw_scores_do_not_shrink_commitment(self):
        parts = ranked_parts()[:MAX_PARTS]
        rows = [row(parts[n // 1000], n,
                    score=NSFW_CEILING if n == 0 or n >= 6000 else 0.0)
                for n in range(MAX_PARTS * 1000)]
        result = candidate_part_handoff(rows)
        self.assertEqual(result["status"], "blocked_insufficient_metadata_eligible_groups")
        self.assertEqual(result["selected_part_ids"], [])
        self.assertEqual(result["distinct_prompt_groups"], 5999)

    def test_prompt_groups_and_bad_metadata_fail_closed(self):
        part = ranked_parts()[0]
        grouped = candidate_part_handoff([row(part, n, prompt="Cafe\u0301  sky" if n % 2
                                             else "Caf\u00e9 sky") for n in range(1000)])
        self.assertEqual(grouped["distinct_prompt_groups"], 1)
        with self.assertRaisesRegex(SelectionError, "duplicate image_name"):
            candidate_part_handoff([row(part, 0), row(part, 0)])
        with self.assertRaisesRegex(SelectionError, "finite numeric"):
            candidate_part_handoff([row(part, 0, score=float("nan"))])
        with self.assertRaisesRegex(SelectionError, "UUID"):
            candidate_part_handoff([{**row(part, 0), "image_name": "bad.png"}])

    def test_missing_ranked_part_cannot_be_skipped(self):
        parts = ranked_parts()[:MAX_PARTS]
        rows = [row(parts[1 + n // 1000], n) for n in range(6000)]
        result = candidate_part_handoff(rows)
        self.assertEqual(result["status"], "blocked_missing_ranked_part_metadata")
        self.assertEqual(result["selected_part_ids"], [])

    def test_later_missing_or_incomplete_parts_block_favorable_prefix(self):
        parts = ranked_parts()[:MAX_PARTS]
        rows = [row(parts[n // 1000], n) for n in range(MAX_PARTS * 1000)]
        for removed in (1, 1000):
            result = candidate_part_handoff(rows[:-removed])
            self.assertNotEqual(result["status"], "candidate_parts_ready")
            self.assertEqual(result["selected_part_ids"], [])
        rows[-1]["prompt"] = None
        rows[-1]["image_nsfw"] = 2.0
        with self.assertRaisesRegex(SelectionError, "prompt must be text"):
            candidate_part_handoff(rows)

    def test_invalid_part_ids_block_even_outside_candidate_filter(self):
        parts = ranked_parts()[:MAX_PARTS]
        good = [row(parts[n // 1000], n) for n in range(6000)]
        for invalid in (None, "1", True, 0, 2001, 1.0):
            with self.subTest(invalid=invalid), self.assertRaisesRegex(SelectionError, "part_id"):
                candidate_part_handoff(good + [{"part_id": invalid}])

    def test_incomplete_and_overfull_parts_block(self):
        part = ranked_parts()[0]
        for count in (1, 999):
            result = candidate_part_handoff(row(part, n) for n in range(count))
            self.assertEqual(result["status"], "blocked_incomplete_ranked_part_metadata")
            self.assertEqual(result["selected_part_ids"], [])
        for count in (1001, 6000):
            with self.assertRaisesRegex(SelectionError, "exceeds 1000"):
                candidate_part_handoff(row(part, n) for n in range(count))

    def test_empty_prompt_is_an_explicit_exclusion_not_a_group(self):
        part = ranked_parts()[0]
        rows = [row(part, n) for n in range(1000)]
        rows[0]["prompt"] = "  \t"
        result = candidate_part_handoff(rows)
        self.assertEqual(result["rows_excluded_by_empty_prompt"], 1)
        self.assertEqual(result["distinct_prompt_groups"], 999)
        rows[0]["prompt"] = None
        with self.assertRaisesRegex(SelectionError, "prompt must be text"):
            candidate_part_handoff(rows)

    def test_blurred_image_sentinel_is_excluded_but_other_invalid_scores_block(self):
        part = ranked_parts()[0]
        rows = [row(part, n) for n in range(1000)]
        rows[0]["image_nsfw"] = 2.0
        result = candidate_part_handoff(rows)
        self.assertEqual(result["rows_excluded_by_score_or_size"], 1)
        self.assertEqual(result["distinct_prompt_groups"], 999)
        for field, value in (("image_nsfw", 1.1), ("prompt_nsfw", 2.0)):
            invalid = {**row(part, 0), field: value}
            with self.assertRaisesRegex(SelectionError, "finite numeric"):
                candidate_part_handoff([invalid])


if __name__ == "__main__":
    unittest.main()
