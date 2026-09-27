"""Owned synthetic CPU decoder; never learned weights, study pixels or GPU."""
from types import SimpleNamespace,MethodType
from unittest.mock import patch
import unittest
try:
    import torch
    import diffusers
except ImportError:
    torch=diffusers=None
from src.embedding.proposed import DiffusersComponents,EmbeddingError
from src.embedding.checkpointing import CheckpointedComponents
from src.embedding.latent_refinement import refine,RefinementPolicy
from scripts import test_c4_inversion_path as fixture


@unittest.skipIf(torch is None or diffusers is None,"existing pinned software absent; do not install")
class RefinementTests(unittest.TestCase):
    def setUp(self):
        original=fixture.PathTests();original.setUp()
        class Decoder(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.scale=torch.nn.Parameter(torch.tensor(.1),requires_grad=False)
                self.calls=0
            def forward(self,x):
                self.calls+=1
                return torch.nn.functional.interpolate(x[:,:3]*self.scale,scale_factor=8,mode="nearest")
        class VAE(torch.nn.Module):
            def __init__(self):
                super().__init__();self.decoder=Decoder()
                self.config=SimpleNamespace(scaling_factor=.18215)
            def decode(self,x):return SimpleNamespace(sample=self.decoder(x))
        b=original.backend
        self.backend=DiffusersComponents(VAE(),b.unet,b.condition,b.settings)
        self.source=torch.full((1,3,33,35),.65)
        self.latent=torch.zeros(1,4,8,8)
        self.policy=RefinementPolicy(4,32,5,1.,10.,0.,1e-6,10.)
        self.events=[];self.saved=[]

    def run_refine(self,**kwargs):
        args=dict(progress=self.events.append,save_state=lambda row,x:self.saved.append((row,x)))
        args.update(kwargs)
        return refine(self.backend,self.source,self.latent,self.policy,**args)

    def checkpointed(self):
        b=self.backend
        self.backend=CheckpointedComponents(b.vae,b.unet,b.condition,b.settings)

    def test_owned_descent_cropped_native_grid_and_no_model_gradient(self):
        result=self.run_refine()
        self.assertLess(result.mse_rgb01,.15**2)
        self.assertEqual(tuple(result.native_image.shape),(1,3,33,35))
        self.assertEqual(result.actual_decoder_forward_starts,result.evaluations)
        self.assertEqual(self.backend.vae.decoder.calls,result.evaluations)
        self.assertEqual(self.backend.unet.calls,[])
        self.assertIsNone(self.backend.vae.decoder.scale.grad)
        self.assertFalse(result.latent.requires_grad);self.assertFalse(result.native_image.requires_grad)
        self.assertTrue(torch.all(self.latent==0));self.assertTrue(torch.all(self.source==.65))
        accepted=[row["objective"] for row in self.events if row["phase"]=="refinement_trial" and row["accepted"]]
        self.assertTrue(all(b<a for a,b in zip(accepted,accepted[1:])))
        self.assertEqual(self.saved[-1][0]["phase"],"refinement_final_state")
        self.assertFalse(self.events[-1]["scientific_acceptance"])

    def test_checkpointed_profile_retains_exact_owned_trajectory_and_counts_recompute(self):
        base=self.run_refine()
        self.setUp();self.checkpointed()
        candidate=self.run_refine()
        torch.testing.assert_close(base.latent,candidate.latent,atol=0,rtol=0)
        torch.testing.assert_close(base.native_image,candidate.native_image,atol=0,rtol=0)
        self.assertEqual(base.evaluations,candidate.evaluations)
        self.assertGreater(candidate.checkpoint_recomputations,0)
        self.assertEqual(candidate.actual_decoder_forward_starts,
                         candidate.evaluations+candidate.checkpoint_recomputations)
        self.assertEqual(candidate.actual_decoder_forward_starts,self.backend.vae.decoder.calls)
        self.assertEqual(len(self.backend.vae.decoder._forward_pre_hooks),0)

    def test_explicit_budget_without_unreported_final_decode(self):
        self.policy=RefinementPolicy(4,2,0,1.,10.,0.,0.,10.)
        result=self.run_refine()
        self.assertEqual(result.status,"evaluation_budget")
        self.assertEqual(result.evaluations,1)
        self.assertEqual(self.backend.vae.decoder.calls,1)
        self.assertEqual(result.backward_evaluations,0)

    def test_trust_ball_projection(self):
        self.policy=RefinementPolicy(2,20,2,10.,.01,.1,0.,10.)
        result=self.run_refine()
        self.assertLessEqual(result.displacement_l2,.01000001)
        self.assertTrue(all(row["displacement_l2"]<=.01000001 for row,_ in self.saved))

    def test_zero_gradient_has_explicit_status_and_no_fallback(self):
        self.backend.vae.decoder.scale.zero_()
        result=self.run_refine()
        self.assertEqual(result.status,"zero_gradient")
        self.assertEqual(result.backward_evaluations,1)
        self.assertEqual(result.evaluations,2)

    def test_initial_mse_diagnostic_does_not_claim_quality_success(self):
        self.source.fill_(.5)
        result=self.run_refine()
        self.assertEqual(result.status,"mse_tolerance_met")
        self.assertEqual(result.evaluations,1)
        self.assertEqual(self.events[-1]["saved_png_quality"],"NOT_RUN")

    def test_state_payload_mutation_is_isolated(self):
        reference=self.run_refine()
        self.setUp()
        def mutate(row,x):row["mse_rgb01"]=999.;x.fill_(9.)
        candidate=self.run_refine(save_state=mutate)
        torch.testing.assert_close(reference.latent,candidate.latent,atol=0,rtol=0)
        self.assertEqual(reference.mse_rgb01,candidate.mse_rgb01)

    def test_persistence_failure_no_terminal_and_hook_removed(self):
        def fail(row,x):raise OSError("owned save failure")
        with self.assertRaisesRegex(OSError,"owned save"):
            self.run_refine(save_state=fail)
        self.assertFalse(any(r["phase"]=="refinement_terminated" for r in self.events))
        self.assertEqual(len(self.backend.vae.decoder._forward_pre_hooks),0)

    def test_decoder_profile_mutation_in_callback_refused(self):
        def mutate(row,x):self.backend.vae.decoder.scale.add_(.1)
        with self.assertRaisesRegex(EmbeddingError,"decoder identity"):
            self.run_refine(save_state=mutate)
        self.assertEqual(self.backend.vae.decoder.calls,1)
        self.assertEqual(len(self.backend.vae.decoder._forward_pre_hooks),0)

    def test_cross_owner_backend_and_vae_methods_refused(self):
        for name in ("backend","vae"):
            self.setUp();other=RefinementTests();other.setUp()
            if name=="backend":self.backend._decode=other.backend._decode
            else:self.backend.vae.decode=other.backend.vae.decode
            with self.subTest(name=name),self.assertRaisesRegex(EmbeddingError,"decoder identity"):
                self.run_refine()
            self.assertEqual(self.backend.vae.decoder.calls,0)
            self.assertEqual(other.backend.vae.decoder.calls,0)

    def test_timeout_before_any_decoder_start(self):
        with patch("src.embedding.latent_refinement.time.monotonic",side_effect=[0.,11.]):
            with self.assertRaisesRegex(EmbeddingError,"time limit"):
                self.run_refine()
        self.assertEqual(self.backend.vae.decoder.calls,0)
        self.assertEqual(len(self.backend.vae.decoder._forward_pre_hooks),0)

    def test_journal_failure_before_decoder_start(self):
        def fail(row):raise OSError("owned journal failure")
        with self.assertRaises(OSError):self.run_refine(progress=fail)
        self.assertEqual(self.backend.vae.decoder.calls,0)
        self.assertEqual(len(self.backend.vae.decoder._forward_pre_hooks),0)

    def test_bad_policy_or_input_no_decoder_call(self):
        for values in ((True,20,2,1.,10.,0.,0.,10.),(2,20,2,float("nan"),10.,0.,0.,10.),
                (2,20,2,1.,-1.,0.,0.,10.)):
            with self.assertRaises(EmbeddingError):RefinementPolicy(*values)
        self.latent=self.latent.double()
        with self.assertRaises(EmbeddingError):self.run_refine()
        self.assertEqual(self.backend.vae.decoder.calls,0)

    def test_rejected_line_trials_preserved_without_adaptive_restart(self):
        self.policy=RefinementPolicy(2,8,1,100.,1000.,0.,0.,10.)
        result=self.run_refine()
        self.assertEqual(result.status,"line_search_failed")
        rejected=[row for row in self.events if row["phase"]=="refinement_trial"]
        self.assertEqual(len(rejected),2)
        self.assertTrue(all(not row["accepted"] for row in rejected))
        self.assertEqual(len([row for row,_ in self.saved if row.get("role")=="trial"]),2)
        self.assertTrue(torch.all(result.latent==0))

    def test_actual_decoder_call_ceiling_and_exception_cleanup(self):
        def repeated(b,state):
            for _ in range(5):value=b.vae.decode(state).sample
            return value
        self.backend._decode=MethodType(repeated,self.backend)
        self.policy=RefinementPolicy(1,2,0,1.,10.,0.,0.,10.)
        with self.assertRaisesRegex(EmbeddingError,"actual decoder forward ceiling"):
            self.run_refine()
        self.assertEqual(self.backend.vae.decoder.calls,4)
        self.assertEqual(self.events[-1]["phase"],"decoder_forward_ceiling")
        self.assertEqual(len(self.backend.vae.decoder._forward_pre_hooks),0)

    def test_nonfinite_decoder_and_detached_gradient_are_terminal(self):
        def nonfinite(b,state):return b.vae.decode(state).sample*float("nan")
        self.backend._decode=MethodType(nonfinite,self.backend)
        with self.assertRaisesRegex(EmbeddingError,"decoder output"):
            self.run_refine()
        self.assertEqual(len(self.backend.vae.decoder._forward_pre_hooks),0)
        self.setUp()
        def detached(b,state):return b.vae.decode(state).sample.detach()
        self.backend._decode=MethodType(detached,self.backend)
        with self.assertRaisesRegex(EmbeddingError,"detached refinement"):
            self.run_refine()
        self.assertFalse(any(r["phase"]=="refinement_terminated" for r in self.events))
        self.assertEqual(len(self.backend.vae.decoder._forward_pre_hooks),0)


if __name__=="__main__":unittest.main()
