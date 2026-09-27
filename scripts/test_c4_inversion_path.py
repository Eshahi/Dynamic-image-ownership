"""Owned CPU fake UNet; real scheduler arithmetic, never checkpoints/images."""
from types import SimpleNamespace
from unittest.mock import patch
import unittest
try:
    import torch
    from diffusers import DDIMScheduler
except ImportError:
    torch = DDIMScheduler = None
from src.embedding.proposed import DiffusersComponents, EmbeddingError, Settings
from src.embedding.inversion import InversionPolicy
from src.embedding.inversion_path import PinnedDDIMPath, SCHEDULER_PROFILE, invert_roundtrip


@unittest.skipIf(torch is None or DDIMScheduler is None,"pinned software absent; do not install")
class PathTests(unittest.TestCase):
    def setUp(self):
        self.target = torch.full((1,4,2,2),.25)
        class OwnedUNet(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.slope = torch.nn.Parameter(torch.tensor(.1),requires_grad=False)
                self.register_buffer("offset",torch.tensor(.01))
                self.config=SimpleNamespace(in_channels=4,out_channels=4,cross_attention_dim=768)
                self.calls=[]
            def forward(self,state,timestep,encoder_hidden_states):
                self.calls.append((timestep,torch.is_grad_enabled()))
                return SimpleNamespace(sample=state*self.slope+self.offset)
        self.backend=DiffusersComponents.__new__(DiffusersComponents)
        self.backend.unet=OwnedUNet().eval()
        self.backend.condition=torch.zeros(1,77,768)
        self.backend.settings=Settings(10,.2,.18215,256,.2,.3,.01,.005,2,1,1,1,1,.1,.1)
        self.backend.scheduler=DDIMScheduler(**SCHEDULER_PROFILE)
        self.backend.scheduler.set_timesteps(10)
        self.backend.times=(101,1)
        self.path=PinnedDDIMPath(self.backend)
        self.events=[];self.saved=[]

    def run_path(self, **kwargs):
        defaults=dict(maximum_evaluations=64,maximum_seconds=10,roundtrip_tolerance=1e-5,
                      progress=self.events.append,save_state=lambda row,x:self.saved.append((row,x)))
        defaults.update(kwargs)
        policy=defaults.pop("policy",InversionPolicy())
        return invert_roundtrip(self.path,self.target,policy,**defaults)

    def test_reverse_inversion_forward_replay_and_terminal_alpha(self):
        out=self.run_path()
        self.assertEqual(out.status,"completed")
        self.assertLess(out.roundtrip_residual_max,1e-5)
        self.assertNotEqual(self.path.terminal_alpha,1.)
        self.assertEqual(self.path.terminal_alpha,float(self.backend.scheduler.alphas_cumprod[0]))
        self.assertEqual([row["timestep"] for row in self.events if row["phase"]=="pair_started"],[1,101])
        self.assertEqual([row["timestep"] for row in self.events if row["phase"]=="replay_started"],[101,1])
        self.assertEqual(out.evaluations,len(self.backend.unet.calls))
        self.assertEqual(out.backward_evaluations,0)
        self.assertTrue(torch.all(self.target==.25))
        self.assertFalse(out.state.requires_grad)
        torch.testing.assert_close(out.reconstructed,self.target,atol=1e-5,rtol=1e-5)

    def test_guided_path_preserves_gradient_only_during_inverse_evaluations(self):
        out=self.run_path(policy=InversionPolicy(method="guided_coordinate"))
        self.assertEqual(out.status,"completed")
        self.assertGreater(out.backward_evaluations,0)
        self.assertEqual(out.evaluations,len(self.backend.unet.calls))
        self.assertEqual(self.backend.unet.calls[-2:],[(101,False),(1,False)])
        self.assertIsNone(self.backend.unet.slope.grad)

    def test_failed_pair_stops_and_persists_before_any_later_pair(self):
        out=self.run_path(policy=InversionPolicy(max_evaluations=1))
        self.assertEqual(out.status,"pair_not_converged")
        self.assertEqual(len(out.pair_results),1)
        self.assertEqual(len(self.saved),1)
        self.assertEqual(self.saved[0][0]["status"],"evaluation_budget")
        self.assertTrue(all(t==1 for t,_ in self.backend.unet.calls))
        self.assertIsNone(out.reconstructed)

    def test_whole_budget_reserves_replay_and_preserves_partial(self):
        out=self.run_path(maximum_evaluations=4)
        self.assertEqual(out.status,"evaluation_budget")
        self.assertLessEqual(out.evaluations,4)
        self.assertEqual(len(self.saved),1)
        self.assertEqual(self.saved[0][0]["timestep"],1)
        self.assertEqual(out.evaluations,len(self.backend.unet.calls))

    def test_pair_convergence_does_not_substitute_roundtrip_residual(self):
        out=self.run_path(policy=InversionPolicy(residual_tolerance=1.),roundtrip_tolerance=0.)
        self.assertEqual(out.status,"roundtrip_residual_failed")
        self.assertTrue(all(result.status=="converged" for result in out.pair_results))
        self.assertGreater(out.roundtrip_residual_max,0)

    def test_save_failure_leaves_start_not_false_completion(self):
        def fail(row,x): raise OSError("owned disk failure")
        with self.assertRaisesRegex(OSError,"owned disk"):
            self.run_path(save_state=fail)
        self.assertFalse(any(row["phase"]=="pair_state" for row in self.events))
        self.assertFalse(any(row["phase"]=="path_terminated" for row in self.events))

    def test_persistence_mutation_cannot_modify_trajectory(self):
        def mutate(row,x): x.zero_();row["status"]="invented"
        out=self.run_path(save_state=mutate)
        self.assertEqual(out.status,"completed")
        self.assertGreater(float(out.state.abs().max()),0)
        self.assertTrue(all(row.get("status")!="invented" for row in self.events))

    def test_callback_failure_precedes_any_predictor(self):
        def fail(row): raise RuntimeError("owned journal failure")
        with self.assertRaisesRegex(RuntimeError,"owned journal"):
            self.run_path(progress=fail)
        self.assertEqual(self.backend.unet.calls,[])

    def test_cooperative_timeout_is_recorded_not_silently_retried(self):
        with patch("src.embedding.inversion_path.time.monotonic",side_effect=[0.,2.]):
            with self.assertRaisesRegex(EmbeddingError,"time limit"):
                self.run_path(maximum_seconds=1.)
        self.assertEqual(self.backend.unet.calls,[])
        self.assertEqual(self.events[-1]["phase"],"path_time_limit")

    def test_overdue_measured_numeric_row_is_not_suppressed(self):
        clock=[0.]
        original=self.backend.unet.forward
        def forward(*args,**kwargs):
            result=original(*args,**kwargs);clock[0]=2.;return result
        self.backend.unet.forward=forward
        with patch("src.embedding.inversion_path.time.monotonic",side_effect=lambda:clock[0]):
            with self.assertRaisesRegex(EmbeddingError,"time limit"):
                self.run_path(maximum_seconds=1.)
        self.assertEqual(len(self.backend.unet.calls),1)
        self.assertEqual(self.events[-2]["phase"],"evaluated")
        self.assertIn("residual_max",self.events[-2])
        self.assertEqual(self.events[-1]["phase"],"path_time_limit")

    def test_declared_prior_order_and_malformed_member_validation(self):
        policy=InversionPolicy(method="guided_coordinate",prior_weight=.0001)
        out=self.run_path(policy=policy,prior_means=(self.target*.9,self.target*.8))
        self.assertLessEqual(out.evaluations,64)
        self.setUp()
        with self.assertRaises(EmbeddingError):
            self.run_path(policy=policy,prior_means=(self.target.double(),self.target))
        self.assertEqual(self.backend.unet.calls,[])

    def test_bound_step_identity_cannot_drift(self):
        self.path.steps=tuple(reversed(self.path.steps))
        with self.assertRaises(EmbeddingError):self.run_path()
        self.assertEqual(self.backend.unet.calls,[])

    def test_invalid_policy_resources_and_priors_reject_before_model(self):
        for kwargs in ({"maximum_evaluations":True},{"maximum_evaluations":2},
                {"maximum_seconds":float("nan")},{"roundtrip_tolerance":-1},
                {"prior_means":(self.target,self.target)},{"save_state":None},
                {"policy":InversionPolicy(method="guided_coordinate",prior_weight=.1)}):
            with self.subTest(kwargs=kwargs),self.assertRaises(EmbeddingError):
                self.run_path(**kwargs)
        self.assertEqual(self.backend.unet.calls,[])

    def test_schedule_condition_model_profile_drift_refused(self):
        mutations=(lambda:self.backend.scheduler.register_to_config(clip_sample=True),
            lambda:self.backend.scheduler.alphas_cumprod.add_(.0001),
            lambda:self.backend.condition.add_(.1),lambda:self.backend.unet.train(),
            lambda:self.backend.unet.slope.requires_grad_(True),
            lambda:self.backend.unet.double(),lambda:setattr(self.backend,"times",(1,101)))
        for mutate in mutations:
            self.setUp();mutate()
            with self.assertRaises(EmbeddingError): self.run_path()
            self.assertEqual(self.backend.unet.calls,[])

    def test_drift_during_path_fails_before_next_prediction(self):
        original=self.backend.unet.forward
        def forward(*args,**kwargs):
            result=original(*args,**kwargs)
            self.backend.unet.slope.requires_grad_(True)
            return result
        self.backend.unet.forward=forward
        with self.assertRaises(EmbeddingError):self.run_path()
        self.assertEqual(len(self.backend.unet.calls),1)
        self.assertEqual(self.events[-1]["phase"],"evaluation_started")


if __name__ == "__main__": unittest.main()
