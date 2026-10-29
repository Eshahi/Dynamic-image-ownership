"""Pure configuration and deterministic-seed tests; never construct the writer."""
import copy
import json
from pathlib import Path
from types import SimpleNamespace
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tifs_writer as writer
from tifs_test_denoiser import MockUNet

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

    def test_only_registered_stage_p_robust_budgets_are_accepted(self):
        for budget in writer.ROBUST_PSNR_CHOICES:
            changed = copy.deepcopy(self.frozen)
            changed["writer"]["psnr_db"] = budget
            writer.validate_writer_config(self.base, changed)
        for budget in (35., 45., 53., None, True):
            changed["writer"]["psnr_db"] = budget
            with self.assertRaises(ValueError):
                writer.validate_writer_config(self.base, changed)

    def test_variant_dispatch_includes_x0_and_disables_budget_surrogate(self):
        instance = object.__new__(writer.F6Writer)
        instance._generic = lambda *args: ("generic", args)
        instance._codec = lambda *args: ("codec", args)
        for variant in ("f6-noise", "f6-codec", "f6-x0"):
            result = instance._surrogate("image", "R1", .2, variant, "source", 4, "optimization")
            self.assertEqual(result, ("codec", ("image", "R1", .2, variant, "source", 4, "optimization")))
        self.assertEqual(instance._surrogate("image", "R1", .2, "f6-generic", "s", 4, "optimization")[0], "generic")
        with self.assertRaises(ValueError):
            instance._surrogate(None, "R1", .2, "f5-budget", "s", 0, "optimization")

    def test_f5_budget_original_quality_delegates_identical_retained_pgd_calls(self):
        instance = object.__new__(writer.F6Writer)
        instance.reader, instance.sdxl = SimpleNamespace(vae=MockVAE()), None
        instance.frozen_config = copy.deepcopy(self.frozen)
        instance.layout = object()
        calls, returned = [], object()
        def retained_pgd(*args):
            calls.append(args)
            return returned
        instance.f5 = SimpleNamespace(robust_pgd=retained_pgd)
        rgb, chips = object(), object()
        for refine in (False, True):
            self.assertIs(instance._optimize(rgb, chips, "s", "f5-budget", refine=refine), returned)
        self.assertEqual(calls, [(instance.reader, rgb, instance.layout, chips, 52., 150, 4., 0.),
                                (instance.reader, rgb, instance.layout, chips, 58., 50, 4., 0.)])
        # Same callable, inputs and return object, not a floating-point rewrite.
        for budget in (46., 42., 38.):
            instance.frozen_config["writer"]["psnr_db"] = budget
            instance._optimize(rgb, chips, "s", "f5-budget")
            self.assertEqual(calls[-1][4:], (budget, 150, 4., 0.))

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

    def test_unet_scope_cleanup_after_success_close_and_partial_failure(self):
        for fail, broken in ((False, False), (True, False), (False, True)):
            instance = object.__new__(writer.F6Writer)
            vae, unet = MockVAE(), MockUNet(broken=broken)
            instance.reader, instance.sdxl = SimpleNamespace(vae=vae), None
            @writer.writer_gradient_scope
            def operate(self):
                self._checkpoint_unet(unet)
                self._checkpoint_unet(unet)
                self.assertions = len(self._checkpoint_unets)
                if fail:
                    self.reader = None
                    raise ValueError("closed during gradient failure")
            if fail or broken:
                with self.assertRaises(ValueError): operate(instance)
            else:
                operate(instance)
                self.assertEqual(instance.assertions, 1)
            self.assertFalse(vae.encoder.gradient_checkpointing)
            self.assertTrue(all(not block.gradient_checkpointing for block in unet.blocks))
            self.assertIsNone(instance._checkpoint_unets)


if __name__ == "__main__":
    unittest.main()
