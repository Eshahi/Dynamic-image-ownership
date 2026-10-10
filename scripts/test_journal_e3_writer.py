"""CPU control-flow contracts for E3 and its prospective S1 supplier.

No model loads or retained scientific pixels: tensors and PNG roundtrips are
real, while native readers/optimization objectives are controlled test doubles.
Run directly with the existing a6-science Python.
"""
from __future__ import annotations

from contextlib import ExitStack
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import numpy as np
from PIL import Image
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import journal_e3_writer as writer

torch.set_num_threads(1)
Q, H = 0x12345678, 0x89ABCDEF


def metrics(psnr=40., ssim=.95, lpips=.05, infinite=False):
    return dict(psnr_db=psnr, ssim_rgb=ssim, lpips=lpips, psnr_infinite=infinite)


def native(q=Q, h=H, outcome='both_match', readable=True):
    return dict(outcome=outcome,
        semantic=dict(read=readable, found=True, decoded_code=f'{q:08x}'),
        instance=dict(read=readable, found=True, decoded_code=f'{h:08x}'))


class ControlledObjective:
    """Positive case has a genuine CPU autograd graph, not a fake gradient."""
    def __init__(self, active=False):
        self.active = active
        self.branches = []

    def enable_checkpointing(self):
        pass

    def loss_details(self, x, branch):
        self.branches.append(branch)
        loss = x.mean() + 1 if self.active else x.sum() * 0
        return loss, dict(finite_forward=True, hinges_inactive=not self.active,
            score_hinge=1. if self.active else 0.,
            maximum_bit_hinge=1. if self.active else 0.)


class E3WriterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='e3-cpu-')
        self.addCleanup(self.tmp.cleanup)
        self.out = Path(self.tmp.name) / 'writer'
        self.source = np.full((512, 512, 3), 128, dtype=np.uint8)
        self.marked = self.source.copy()
        # Signed contraction and its integer rounding are both exercised.
        self.marked[0, :4, 0] = [131, 125, 133, 123]
        self.reader = SimpleNamespace(vae=SimpleNamespace(
            enable_gradient_checkpointing=Mock()),
            tensor=lambda x: torch.from_numpy(x).permute(2, 0, 1).unsqueeze(0),
            latent=Mock(return_value='native-latent'))
        self.ev = SimpleNamespace(torch=torch, reader=self.reader, profile={'test': True},
            features=Mock(return_value='seven-view-features'), metrics=Mock())
        self.channel = SimpleNamespace(forward=Mock(
            side_effect=lambda x, strength, seed: SimpleNamespace(image=x)))
        self.budget = Mock()

    def embed(self, calls, qualities, active=False):
        self.ev.metrics.side_effect = qualities
        self.obj = ControlledObjective(active)
        with ExitStack() as stack:
            self.pgd = stack.enter_context(patch.object(writer.f5, 'robust_pgd',
                return_value=self.marked.astype(np.float64)/255))
            self.restore = stack.enter_context(patch.object(writer, 'restore_fragile',
                side_effect=lambda rgb, q, h, profile: (rgb, {'fixed': True})))
            stack.enter_context(patch.object(writer, 'patterns',
                return_value=('fixed-layout', 'fixed-pattern', 'fixed-gaps')))
            stack.enter_context(patch.object(writer, 'Objective', return_value=self.obj))
            self.detect = stack.enter_context(patch.object(writer.rc, 'detect_rgb',
                side_effect=calls))
            stack.enter_context(patch.object(writer, 'coded_diagnostics', return_value={}))
            stack.enter_context(patch.object(writer, 'delivery', return_value={}))
            self.contraction = stack.enter_context(patch.object(writer, 'contract',
                wraps=writer.contract))
            # Ineligible proposals still require all nine saved-image losses.
            self.project = stack.enter_context(patch.object(writer, 'projected_update',
                side_effect=lambda trial, base, clean, b, t, torch: (base.clone(), False)))
            return writer.embed(self.source, writer.ALPHA, Q, H, self.ev,
                object(), self.channel, self.out, self.budget)

    def assert_retained_outputs(self, row):
        self.assertEqual(json.loads((self.out/'result.json').read_text()), row)
        for key in ('start_image', 'final_state_image', 'final_image'):
            self.assertTrue(Path(row[key]).is_file(), key)
        self.assertTrue((self.out/'images'/'E1-initial-46-restored.png').is_file())
        self.assertTrue((self.out/'iterations.jsonl').is_file())

    def test_invalid_initializer_can_contract_once_and_be_admitted(self):
        row = self.embed([native(h=H ^ 1), native()],
            [metrics(psnr=34), metrics(psnr=34), metrics()])
        self.assertEqual(row['status'], 'ok')
        self.assertEqual(row['update_status'], 'invalid_initializer_no_refinement')
        self.assertEqual(row['completed_logical_iterations'], 0)
        self.assertEqual(row['quality_branch'], 'contract_0.8')
        self.assertEqual(self.obj.branches, [])
        self.contraction.assert_called_once()
        expected = self.source.copy()
        expected[0, :4, 0] = [130, 126, 132, 124]
        np.testing.assert_array_equal(np.asarray(Image.open(row['final_image'])), expected)
        self.assert_retained_outputs(row)

    def test_retain_payload_failure_never_tries_contraction(self):
        row = self.embed([native(), native(q=Q ^ 1)], [metrics()]*3)
        self.assertEqual(row['status'], 'admission_failed')
        self.assertEqual(row['quality_branch'], 'retain')
        self.assertFalse(row['admission']['exact_q'])
        self.contraction.assert_not_called()
        self.assert_retained_outputs(row)

    def test_contraction_payload_failure_is_retained_without_repair(self):
        row = self.embed([native(h=H ^ 1), native(h=H ^ 1)],
            [metrics(psnr=34), metrics(psnr=34), metrics()])
        self.assertEqual(row['status'], 'admission_failed')
        self.assertEqual(row['quality_branch'], 'contract_0.8')
        self.contraction.assert_called_once()
        self.assertEqual(self.detect.call_count, 2)
        self.assertEqual(self.restore.call_count, 2)
        self.assertEqual(self.pgd.call_count, 2)
        self.assert_retained_outputs(row)

    def test_valid_initializer_inactive_hinges_complete_twenty_logical_steps(self):
        row = self.embed([native(), native()], [metrics()]*3)
        self.assertTrue(row['admitted'])
        self.assertEqual(row['update_status'], 'exact_inactive')
        self.assertEqual(row['completed_logical_iterations'], 20)
        self.assertEqual(row['accepted_updates'], 0)
        self.project.assert_not_called()
        self.assertEqual(self.obj.branches, ['clean', 'sd15_vae', 'sdxl_vae']+['clean']*6)
        self.assertEqual([(c.args[1], c.args[2]) for c in self.channel.forward.call_args_list],
            [(s, seed) for s in (.1, .2) for seed in range(3)])
        self.assertEqual([c.args[4:] for c in self.pgd.call_args_list],
            [(46., 150, 4., 0.), (52., 50, 4., 0.)])
        self.assertEqual([(c.args[1], c.args[2]) for c in self.restore.call_args_list],
            [(Q, H), (Q, H)])
        self.assertTrue(all(c.kwargs == {'binding': 'soft', 'roster_size': 1}
            for c in self.detect.call_args_list))
        self.assert_retained_outputs(row)

    def test_no_eligible_proposals_evaluates_nine_then_tests_second_phase(self):
        row = self.embed([native()]*8, [metrics()]*9, active=True)
        self.assertEqual(row['status'], 'ok')
        self.assertEqual(row['completed_logical_iterations'], 20)
        self.assertEqual(row['accepted_updates'], 0)
        records = [json.loads(line) for line in (self.out/'iterations.jsonl').read_text().splitlines()]
        proposals = [r for r in records if r['stage']=='proposal']
        self.assertEqual([(r['logical_step'], r['fraction_B']) for r in proposals],
            [(0, f) for f in (.1, .5, 1.)]+[(10, f) for f in (.025, .125, .25)])
        for proposal in proposals:
            self.assertFalse(proposal['eligible'])
            self.assertFalse(proposal['projected_feasible'])
            self.assertEqual(list(proposal['branch_losses']), list(writer.BRANCHES))
            self.assertTrue(Path(proposal['image']).is_file())
        self.assertEqual(self.channel.forward.call_count, 7*6)
        iterations = [r for r in records if r['stage']=='iteration']
        self.assertEqual([r['exact_same_phase_noops'] for r in iterations],
            [dict(logical_start=1, logical_end_exclusive=10),
             dict(logical_start=11, logical_end_exclusive=20)])
        self.assert_retained_outputs(row)

    def test_strict_quality_boundaries_and_nonfinite_failure(self):
        for values in (metrics(psnr=35), metrics(ssim=.9), metrics(lpips=.1)):
            with self.subTest(values=values):
                self.assertFalse(writer.strict_quality(values))
        self.assertTrue(writer.strict_quality(metrics(psnr=None, infinite=True)))
        for values in (metrics(psnr=float('nan')), metrics(ssim=float('inf')),
                       metrics(lpips=float('nan')), metrics(psnr=40, infinite=True)):
            with self.subTest(values=values):
                with self.assertRaises(ValueError):
                    writer.strict_quality(values)
        with self.assertRaises(KeyError):
            writer.strict_quality({})

    def test_invalid_quality_is_execution_failure_without_contraction(self):
        row = self.embed([native()], [metrics(), metrics(lpips=float('nan'))])
        self.assertEqual(row['status'], 'construction_failed')
        self.contraction.assert_not_called()
        self.assertTrue(Path(row['final_state_image']).is_file())
        self.assertTrue((self.out/'result.json').is_file())

    def test_selected_contraction_quality_failure_has_no_retry(self):
        row = self.embed([native(h=H ^ 1), native()],
            [metrics(psnr=34), metrics(psnr=34), metrics(ssim=.9)])
        self.assertEqual(row['status'], 'admission_failed')
        self.assertFalse(row['admission']['strict_quality'])
        self.contraction.assert_called_once()
        self.assertEqual(self.pgd.call_count, 2)
        self.assertEqual(self.restore.call_count, 2)
        self.assert_retained_outputs(row)

    def test_alpha_only_and_unsigned_targets_rejected_before_output(self):
        for owner, q, h in [('wrong-owner', Q, H)]+[(writer.ALPHA, q, H)
                for q in (-1, 2**32, True, np.bool_(True), 1.5, '123')]+[
                (writer.ALPHA, Q, -1), (writer.ALPHA, Q, 2**32)]:
            with self.subTest(owner=owner, q=q, h=h):
                with self.assertRaises(ValueError):
                    writer.embed(self.source, owner, q, h, self.ev, None,
                        self.channel, self.out, self.budget)
        self.assertFalse(self.out.exists())
        self.budget.assert_not_called()

    def supply(self, native_call):
        self.bootstrap = self.source.copy()
        self.bootstrap[0, 0, 0] = 129
        with patch.object(writer.f5, 'embed_rgb', return_value=(self.bootstrap,
                {'semantic_code': f'{Q:08x}'})) as embed, patch.object(
                writer.f5, 'detect_rgb', return_value=native_call) as detect:
            row = writer.supply_f5(self.source, self.ev, self.out, self.budget)
        return row, embed, detect

    def test_supplier_intended_q_native_h_without_exact_q_quality_or_match_filter(self):
        row, embed, detect = self.supply(native(q=Q ^ 1, outcome='no_match'))
        self.assertEqual(row['status'], 'ok')
        self.assertEqual((row['q'], row['h']), (Q, H))
        self.assertEqual(row['clean_decoded_q'], f'{Q ^ 1:08x}')
        embed.assert_called_once()
        self.assertEqual(embed.call_args.kwargs, dict(psnr_db=52., steps=150,
            target_margin=4., mask_power=0., band=(4, 32), whitening=1.,
            refine_rounds=1, binding='soft'))
        self.assertEqual(embed.call_args.args[1], writer.ALPHA)
        np.testing.assert_array_equal(embed.call_args.args[0], self.source)
        np.testing.assert_array_equal(detect.call_args.args[0], self.bootstrap)
        self.assertEqual(detect.call_args.kwargs, dict(binding_mode='combined',
            roster_size=1, band=(4, 32), whitening=1., binding='soft'))
        self.ev.metrics.assert_not_called()
        self.assertEqual(self.ev.features.call_count, 2)
        np.testing.assert_array_equal(self.ev.features.call_args_list[0].args[0], self.source)
        np.testing.assert_array_equal(self.ev.features.call_args_list[1].args[0], self.bootstrap)
        self.assertEqual([c.args[1] for c in self.ev.features.call_args_list], [7, 7])
        self.assertTrue(Path(row['bootstrap_image']).is_file())
        self.assertEqual(json.loads((self.out/'supplier.json').read_text()), row)

    def test_unreadable_supplier_keeps_bootstrap_and_failure(self):
        for tier in ('semantic', 'instance'):
            with self.subTest(tier=tier):
                self.out = Path(self.tmp.name) / tier
                call = native()
                call[tier]['read'] = False
                row, embed, detect = self.supply(call)
                self.assertEqual(row['status'], 'supplier_failed')
                self.assertNotIn('payload', row)
                self.assertTrue(Path(row['bootstrap_image']).is_file())
                self.assertEqual(json.loads((self.out/'supplier.json').read_text()), row)
                embed.assert_called_once()
                detect.assert_called_once()


if __name__ == '__main__':
    unittest.main(verbosity=2)
