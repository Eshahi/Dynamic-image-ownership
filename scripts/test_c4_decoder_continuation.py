"""Owned CPU fixtures only, no real image/model/GPU execution."""
from dataclasses import replace
import unittest
from unittest.mock import patch
from scripts import test_c4_latent_refinement as fixture_module
torch, diffusers = fixture_module.torch, fixture_module.diffusers
from src.embedding.decoder_continuation import compare, ContinuationPolicy, ARMS
from src.embedding.adaptive_refinement import AdaptivePolicy
from src.embedding.latent_refinement import refine
from src.embedding.checkpointing import CheckpointedComponents
from src.embedding.proposed import EmbeddingError


@unittest.skipIf(torch is None or diffusers is None, "existing software absent; no installs")
class ContinuationTests(unittest.TestCase):
    def setUp(self):
        fixture=fixture_module.RefinementTests();fixture.setUp()
        self.backend,self.source,self.anchor=fixture.backend,fixture.source,fixture.latent
        self.start=self.anchor+.01
        self.policy=ContinuationPolicy(fixture.policy,
            AdaptivePolicy(4,32,5,.25,2**-16,1.,1e-4,10.,1e-12,1e-6,10.),30.)
        self.events=[];self.states=[];self.images={}

    def run_comparison(self,**extra):
        callbacks=dict(progress=self.events.append,
            save_state=lambda a,r,s:self.states.append((a,r,s)),
            save_arm=lambda a,i,r:self.images.update({a:(i,r)}))
        callbacks.update(extra)
        return compare(self.backend,self.source,self.start,self.anchor,self.policy,**callbacks)

    def test_identical_starts_fixed_anchor_native_images_and_measured_final_gradients(self):
        result=self.run_comparison()
        self.assertEqual(tuple(result['arms']),ARMS)
        for a,r,s in self.states:
            if r['phase']=='arm_identical_start': torch.testing.assert_close(s,self.start,atol=0,rtol=0)
            if r['phase']=='fixed_original_anchor': torch.testing.assert_close(s,self.anchor,atol=0,rtol=0)
        for arm in ARMS[1:]:
            image,row=self.images[arm]
            self.assertEqual(tuple(image.shape),(1,3,33,35))
            self.assertGreater(row['final_gradient_l2'],0)
            self.assertEqual(row['decoder_evaluations'],row['optimizer_evaluations']+1)
            self.assertEqual(row['actual_decoder_forward_starts'],row['decoder_evaluations'])
        self.assertEqual(self.backend.unet.calls,[])
        self.assertFalse(result['scientific_acceptance'])
        self.assertEqual(len(self.backend.vae.decoder._forward_pre_hooks),0)
        self.assertIsNone(self.backend.vae.decoder.scale.grad)

    def test_checkpoint_recomputations_and_profile_preserve_owned_results(self):
        plain=self.run_comparison();images={k:v[0].clone() for k,v in self.images.items()}
        self.setUp();b=self.backend;self.backend=CheckpointedComponents(b.vae,b.unet,b.condition,b.settings)
        result=self.run_comparison()
        for arm in ARMS:
            torch.testing.assert_close(images[arm],self.images[arm][0],atol=0,rtol=0)
        for arm in ARMS[1:]:
            row=result['arms'][arm]
            self.assertEqual(row['checkpoint_recomputations'],row['backward_evaluations'])
            self.assertEqual(row['actual_decoder_forward_starts'],row['decoder_evaluations']+row['checkpoint_recomputations'])

    def test_control_default_equivalence_and_nonrecentering_refusal(self):
        def run(anchor=None):
            return refine(self.backend,self.source,self.start,self.policy.control,
                progress=lambda r:None,save_state=lambda r,s:None,constraint_anchor=anchor)
        old=run();explicit=run(self.start)
        torch.testing.assert_close(old.latent,explicit.latent,atol=0,rtol=0)
        self.assertEqual(old.objective,explicit.objective)
        self.assertEqual(old.evaluations,explicit.evaluations)
        self.start.fill_(1.)
        with self.assertRaisesRegex(EmbeddingError,'outside original'):run(self.anchor)
        with self.assertRaisesRegex(EmbeddingError,'outside original'):self.run_comparison()

    def test_replay_save_failure_stops_before_either_optimization(self):
        def fail(a,i,r):raise ValueError('owned replay mismatch')
        with self.assertRaisesRegex(ValueError,'replay mismatch'):self.run_comparison(save_arm=fail)
        self.assertEqual(self.backend.vae.decoder.calls,1)
        self.assertFalse(any(r['phase']=='final_gradient_evaluation_started' for r in self.events))

    def test_mutated_decoder_and_callbacks_fail_without_terminal(self):
        def mutate(a,i,r):self.backend.vae.decoder.scale.add_(1.)
        with self.assertRaisesRegex(EmbeddingError,'identity/profile'):self.run_comparison(save_arm=mutate)
        self.assertFalse(any(r['phase']=='continuation_terminated' for r in self.events))
        self.assertEqual(len(self.backend.vae.decoder._forward_pre_hooks),0)

    def test_callback_payload_mutation_does_not_change_internal_start(self):
        original=self.start.clone()
        def save(a,r,s):s.zero_();r.clear()
        result=self.run_comparison(save_state=save)
        torch.testing.assert_close(self.start,original,atol=0,rtol=0)
        self.assertEqual(tuple(result['arms']),ARMS)

    def test_terminal_callback_deadline_refused(self):
        clock=[0.]
        def progress(row):
            if row['phase']=='continuation_terminated':clock[0]=31.
        with patch('src.embedding.decoder_continuation.time.monotonic',side_effect=lambda:clock[0]):
            with self.assertRaisesRegex(EmbeddingError,'time limit'):self.run_comparison(progress=progress)

    def test_insufficient_second_arm_window_refused_not_silently_shortened(self):
        clock=[0.]
        self.policy=replace(self.policy,maximum_seconds=15.)
        def progress(row):
            if row['phase']=='continuation_arm_saved' and row['arm']=='fixed_continuation':clock[0]=6.
        with patch('src.embedding.decoder_continuation.time.monotonic',side_effect=lambda:clock[0]):
            with self.assertRaisesRegex(EmbeddingError,'full equal arm allowance'):
                self.run_comparison(progress=progress)
        self.assertEqual(tuple(self.images),ARMS[:2])

    def test_equal_budget_and_typed_policy(self):
        with self.assertRaisesRegex(EmbeddingError,'equal ceilings'):
            replace(self.policy,adaptive=replace(self.policy.adaptive,iterations=3))
        with self.assertRaises(EmbeddingError):replace(self.policy,maximum_seconds=True)


if __name__=='__main__':unittest.main()
