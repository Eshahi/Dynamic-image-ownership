import hashlib
import tempfile
import unittest
from pathlib import Path

from b3_observed_dependence import bound_snapshot, connected_components, join_observed


class ObservedDependenceTests(unittest.TestCase):
    def row(self, name, raw, prompt):
        return {"id": name, "sha256": raw, "prompt_group_sha256": prompt}

    def test_transitive_union_not_separate_group_counts(self):
        rows = [self.row("a", "r1", "p1"), self.row("b", "r1", "p2"),
                self.row("c", "r2", "p2"), self.row("d", "r3", "p3")]
        result = connected_components(rows)
        self.assertEqual([r["members"] for r in result], [["a", "b", "c"], ["d"]])
        self.assertEqual(result, connected_components(list(reversed(rows))))

    def test_raw_and_prompt_namespaces_distinct(self):
        rows = [self.row("a", "x", "y"), self.row("b", "y", "z")]
        self.assertEqual(len(connected_components(rows)), 2)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            connected_components(rows + [rows[0]])

    def test_join_identity_exclusion_and_partial_boundaries(self):
        domain = "diffusiondb2m-part-000948"
        rows = [{"id": domain + ":" + name, "domain": domain, "sha256": "a" * 64,
                 "bytes": 10, "width": 64, "height": 64} for name in ("a", "b")]
        ledger = {"parts": {"948": {"a": {"reason": "metadata_eligible", "prompt_group_sha256": "b" * 64},
                                    "b": {"reason": "score_or_size", "prompt_group_sha256": None}}}}
        result = join_observed(rows, ledger)
        self.assertEqual(result["eligible_observed_components"], 1)
        self.assertEqual(result["eligible_component_coverage"], 1)
        self.assertEqual(result["images_removed"], 0)
        self.assertFalse(result["all_candidate_parts_present"])
        self.assertFalse(result["study_ids_frozen"])
        with self.assertRaisesRegex(ValueError, "missing"):
            join_observed(rows, {"parts": {}})

    def test_wrong_digest_and_symlink_block(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "fixture"
            # Fixture creation is performed by unittest, not source-file editing.
            path.write_bytes(b"fixture")
            digest = hashlib.sha256(b"fixture").hexdigest()
            self.assertEqual(bound_snapshot(path, digest), b"fixture")
            with self.assertRaisesRegex(ValueError, "digest"):
                bound_snapshot(path, "0" * 64)
            link = Path(folder) / "linked"
            try:
                link.symlink_to(path)
            except OSError:
                return  # Windows link privilege may be unavailable.
            with self.assertRaises(ValueError):
                bound_snapshot(link, digest)


if __name__ == "__main__":
    unittest.main()
