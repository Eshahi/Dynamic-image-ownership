"""Owned CPU quadratics; no source images or learned-model operations."""
from dataclasses import replace
import unittest
from unittest.mock import patch
try:
    import torch
except ImportError:torch=None
from src.embedding.adaptive_refinement import AdaptivePolicy,continue_latent
from src.embedding.proposed import EmbeddingError


def policy(**kwargs):
    return replace(AdaptivePolicy(32,160,12,.25,1e-8,1.,1e-4,80.,1e-8,1e-10,10.),**kwargs)


class PolicyTests(unittest.TestCase):
    def test_bad_policy(self):
        for changes in ({"iterations":True},{"maximum_backtracks":21},{"armijo":0},
                        {"initial_step":2.},{"radius_l2":float("nan")},{"maximum_seconds":False}):
            with self.subTest(changes=changes),self.assertRaises(EmbeddingError):policy(**changes)


@unittest.skipIf(torch is None,"base environment has no Torch")
class AdaptiveTests(unittest.TestCase):
    def setUp(self):
        self.anchor=torch.zeros(1,4,1,1);self.current=torch.full_like(self.anchor,.02)
        self.events=[];self.saved=[]
    def run_owned(self,objective,**kwargs):
        defaults={"progress":self.events.append,"save_state":lambda row,x:self.saved.append((row,x))}
        defaults.update(kwargs)
        return continue_latent(objective,self.current,self.anchor,defaults.pop("policy",policy()),**defaults)
    def test_deeper_search_below_quarter_and_decrease(self):
        out=self.run_owned(lambda x:x.square().mean())
        accepted=[r for r in self.events if r["phase"]=="adaptive_trial" and r["accepted"]]
        self.assertTrue(any(r["step"]<.25 for r in accepted))
        self.assertLess(out.objective,1e-8)
        self.assertEqual(out.evaluations,len([r for r in self.events if r["phase"]=="adaptive_evaluation_started"]))
        self.assertTrue(all(a["objective"]>b["objective"] for a,b in zip(accepted,accepted[1:])))
    def test_original_anchor_is_not_restart_point(self):
        self.current.fill_(.49)
        out=self.run_owned(lambda x:(x-2).square().mean(),policy=policy(radius_l2=1.))
        self.assertLessEqual(float(torch.linalg.vector_norm((out.state-self.anchor).double())),1.)
        self.assertLess(float(out.state.max()),.501)
    def test_start_outside_original_ball_refused(self):
        with self.assertRaises(EmbeddingError):self.run_owned(lambda x:x.square().mean(),policy=policy(radius_l2=.01))
        self.assertEqual(self.events,[])
    def test_accepted_update_does_not_claim_final_gradient(self):
        out=self.run_owned(lambda x:x.square().mean(),policy=policy(iterations=1))
        self.assertEqual(out.accepted_updates,1)
        self.assertIsNone(out.gradient_at_returned_state_l2)
    def test_stationary_gradient_measured_at_returned_state(self):
        self.current.zero_()
        out=self.run_owned(lambda x:x.square().mean()+.1,policy=policy(objective_tolerance=0.))
        self.assertEqual(out.status,"gradient_tolerance")
        self.assertEqual(out.gradient_at_returned_state_l2,0.)
        self.assertGreater(out.objective,0.)
    def test_budget_keeps_measured_current(self):
        out=self.run_owned(lambda x:x.square().mean(),policy=policy(maximum_evaluations=2))
        self.assertEqual((out.status,out.evaluations),("evaluation_budget",1))
        torch.testing.assert_close(out.state,self.current)
    def test_persistence_failure_propagates(self):
        def fail(*_):raise OSError("owned sink failure")
        with self.assertRaises(OSError):self.run_owned(lambda x:x.square().mean(),save_state=fail)
        self.assertFalse(any(r["phase"]=="adaptive_terminated" for r in self.events))
    def test_callback_input_and_observer_are_isolated(self):
        def save(row,x):x.fill_(100);row["phase"]="bad"
        before=self.current.clone()
        out=self.run_owned(lambda x:x.square().mean(),save_state=save)
        torch.testing.assert_close(before,self.current)
        self.assertLess(out.objective,1e-8)
    def test_nonfinite_or_detached_objective_refused(self):
        for fn in (lambda x:x.sum()*float("nan"),lambda x:x.detach().square().mean()):
            with self.assertRaises(EmbeddingError):self.run_owned(fn)
    def test_final_progress_overrun_cannot_return_success(self):
        clock=[0.]
        def journal(row):
            self.events.append(row)
            if row["phase"]=="adaptive_terminated":clock[0]=2.
        self.current.zero_()
        with patch("src.embedding.adaptive_refinement.time.monotonic",side_effect=lambda:clock[0]):
            with self.assertRaisesRegex(EmbeddingError,"time limit"):
                self.run_owned(lambda x:x.square().mean(),policy=policy(maximum_seconds=1.),progress=journal)
        self.assertEqual(self.saved[-1][0]["phase"],"adaptive_terminated")
        # An emitted terminal row is retained evidence, not normal return.


if __name__=="__main__":unittest.main()
