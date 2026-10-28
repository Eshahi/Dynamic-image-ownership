"""Pure configuration and deterministic-seed tests; never construct the writer."""
import copy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tifs_writer as writer

ROOT = Path(__file__).resolve().parents[1]


class WriterLogicTests(unittest.TestCase):
    def setUp(self):
        self.base = json.loads((ROOT / "research/encoder-transfer-20261019/stage2b-config.json").read_text())
        self.frozen = json.loads((ROOT / "research/tifs-20261028/stage-s/frozen-config.json").read_text())

    def test_retained_and_new_configs_agree(self):
        writer.validate_writer_config(self.base, self.frozen)

    def test_changed_retained_reader_is_rejected(self):
        for key, value in (("semantic_views", 1), ("binding", "none"), ("steps", 149)):
            changed = copy.deepcopy(self.base)
            changed["f5"][key] = value
            with self.assertRaises(ValueError):
                writer.validate_writer_config(changed, self.frozen)

    def test_surrogate_or_budget_changes_are_rejected(self):
        for key, value in (("posterior", "sample"), ("reader_gradient_evaluations", 349),
                           ("refine_steps", 49), ("cycle", [])):
            changed = copy.deepcopy(self.frozen)
            changed["writer"][key] = value
            with self.assertRaises(ValueError):
                writer.validate_writer_config(self.base, changed)

    def test_seed_domains_and_process_independence(self):
        values = [writer.draw_seed(s, v, k, stream)
                  for s in ("1", "2") for v in writer.VARIANTS
                  for k in range(3) for stream in ("optimization", "diagnostic")]
        self.assertEqual(len(values), len(set(values)))
        self.assertTrue(all(0 <= x < 2**63 for x in values))
        self.assertEqual(writer.draw_seed(1, "f6-noise", 0), writer.draw_seed("1", "f6-noise", 0))
        with self.assertRaises(ValueError):
            writer.draw_seed("1", "f6-noise", 0, "native")
        with self.assertRaises(ValueError):
            writer.draw_seed("1", "f5-r2", 0)


if __name__ == "__main__":
    unittest.main()
