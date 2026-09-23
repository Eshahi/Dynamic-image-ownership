"""Regression checks for documentary validation; no data or source writes."""
import contextlib
import copy
import io
import unittest
from unittest.mock import patch

import validate_b1 as validator


class DocumentaryChecks(unittest.TestCase):
    def test_current_package(self):
        with contextlib.redirect_stdout(io.StringIO()):
            validator.main()

    def run_bad_rows(self, path, mutate, message):
        original = validator.rows

        def changed(name):
            result = copy.deepcopy(original(name))
            if name == path:
                mutate(result)
            return result

        with patch.object(validator, "rows", side_effect=changed):
            with self.assertRaisesRegex(ValueError, message):
                validator.main()

    def test_shifted_matrix_columns_rejected(self):
        def swap(rows):
            row = rows[0]
            row["limitation"], row["image_dct"] = row["image_dct"], row["limitation"]
        self.run_bad_rows("research/literature-matrix.csv", swap, "Shifted limitation")

    def test_unknown_evidence_rejected(self):
        self.run_bad_rows("research/claim-evidence-map.csv",
                          lambda rows: rows[0].update(evidence_ids="NONEXISTENT"),
                          "Unknown mapped evidence")

    def test_false_acceptance_rejected(self):
        self.run_bad_rows("research/claim-evidence-map.csv",
                          lambda rows: rows[0].update(thesis_status="VERIFIED"),
                          "Unexpected scientific acceptance")


if __name__ == "__main__":
    unittest.main()
