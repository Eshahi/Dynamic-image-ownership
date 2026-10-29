"""Pure configuration and deterministic-seed tests; never construct the writer."""
import copy
import json
from pathlib import Path
from types import SimpleNamespace
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tifs_writer as writer

ROOT = Path(__file__).resolve().parents[1]


class MockVAE:
    """No tensor/model operations: check writer lifecycle only."""
    def __init__(self, train=False, requires_grad=False, broken=False):
        self.training, self.requires_grad, self.broken = train, requires_grad, broken
        self.encoder = SimpleNamespace(gradient_checkpointing=False)
        self.decoder = SimpleNamespace(gradient_checkpointing=False)

    def parameters(self):
        return [SimpleNamespace(requires_grad=self.requires_grad)]

    def enable_gradient_checkpointing(self):
        self.encoder.gradient_checkpointing=True
        self.decoder.gradient_checkpointing=not self.broken

    def disable_gradient_checkpointing(self):
        self.encoder.gradient_checkpointing=self.decoder.gradient_checkpointing=False


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

    def test_checkpointing_requires_frozen_eval_both_blocks(self):
        vae=MockVAE()
        writer.enable_writer_checkpointing(vae)
        self.assertTrue(vae.encoder.gradient_checkpointing)
        self.assertTrue(vae.decoder.gradient_checkpointing)
        for vae in (MockVAE(train=True),MockVAE(requires_grad=True),MockVAE(broken=True)):
            with self.assertRaises(ValueError): writer.enable_writer_checkpointing(vae)
            self.assertFalse(vae.encoder.gradient_checkpointing)
            self.assertFalse(vae.decoder.gradient_checkpointing)

    def test_checkpoint_scope_lazy_vae_cleanup_and_reader_reuse(self):
        instance=object.__new__(writer.F6Writer)
        reader_vae=MockVAE()
        instance.reader=SimpleNamespace(vae=reader_vae)
        instance.sdxl=None
        lazy=[]
        @writer.writer_gradient_scope
        def operate(self, fail=False):
            self.sdxl=MockVAE()
            lazy.append(self.sdxl)
            self._checkpoint_vae(self.sdxl)
            self._checkpoint_vae(self.sdxl)  # identity registration is idempotent
            self.assertions=(reader_vae.encoder.gradient_checkpointing,
                             self.sdxl.decoder.gradient_checkpointing)
            if fail:
                self.reader=self.sdxl=None  # emulate exception closure
                raise ValueError("failed writer")
        operate(instance)
        self.assertEqual(instance.assertions,(True,True))
        self.assertFalse(reader_vae.encoder.gradient_checkpointing)
        self.assertFalse(lazy[-1].decoder.gradient_checkpointing)
        with self.assertRaises(ValueError): operate(instance,True)
        self.assertFalse(reader_vae.encoder.gradient_checkpointing)
        self.assertTrue(all(not vae.decoder.gradient_checkpointing for vae in lazy))
        self.assertIsNone(instance._checkpoint_vaes)

    def test_checkpoint_scope_partial_enable_failure_is_cleaned(self):
        instance=object.__new__(writer.F6Writer)
        vae=MockVAE(broken=True)
        instance.reader=SimpleNamespace(vae=vae)
        instance.sdxl=None
        @writer.writer_gradient_scope
        def operate(self):
            self.fail("must not reach forward")
        with self.assertRaises(ValueError): operate(instance)
        self.assertFalse(vae.encoder.gradient_checkpointing)
        self.assertIsNone(instance._checkpoint_vaes)


if __name__ == "__main__":
    unittest.main()
