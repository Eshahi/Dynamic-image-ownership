"""Owned synthetic CPU equations only; no model, image, weights or CUDA."""
import unittest
try:
    import torch
except ImportError:
    torch=None
from src.embedding.inverse_acceleration import AccelerationPolicy, invert_pair_accelerated
from src.embedding.inversion import DDIMPair
from src.embedding.proposed import EmbeddingError


class PolicyTests(unittest.TestCase):
    def test_bad_policy(self):
        for values in ({"history":True},{"history":1},{"max_evaluations":False},
                {"regularization":float("nan")},{"coefficient_l1_limit":.5},
                {"fallback_damping":[1.,.5]},{"fallback_damping":(True,)},
                {"fallback_damping":(.5,1.)},{"maximum_step_rms":float("inf")}):
            with self.subTest(values=values),self.assertRaises(EmbeddingError):
                AccelerationPolicy(**values)


@unittest.skipIf(torch is None,"no Torch in base environment")
class SolverTests(unittest.TestCase):
    def setUp(self):
        self.pair=DDIMPair(.5,.8)
        self.target=torch.full((1,4,2,2),.25)

    def map_predictor(self, mapping):
        a,b=self.pair.coefficients
        return lambda x:(self.target-a*mapping(x))/b

    def run_map(self,mapping,**policy):
        return invert_pair_accelerated(self.pair,self.target,self.map_predictor(mapping),AccelerationPolicy(**policy))

    def test_constant_root(self):
        out=self.run_map(lambda x:torch.full_like(x,.1))
        self.assertEqual(out.status,"converged")
        self.assertEqual(out.evaluations,2)
        torch.testing.assert_close(out.state,torch.full_like(self.target,.1))

    def test_negative_unstable_root(self):
        out=self.run_map(lambda x:-1.2*x+.1)
        self.assertEqual(out.status,"converged")
        torch.testing.assert_close(out.state,torch.full_like(self.target,.1/2.2),atol=1e-5,rtol=1e-5)
        self.assertGreater(out.rejected_trials,0)

    def test_positive_unstable_root_uses_rejected_history(self):
        out=self.run_map(lambda x:1.2*x+.1)
        self.assertEqual(out.status,"converged")
        torch.testing.assert_close(out.state,torch.full_like(self.target,-.5),atol=1e-5,rtol=1e-5)
        self.assertGreater(out.rejected_trials,0)
        self.assertTrue(any(row["phase"]=="mix_proposed" for row in out.trace))

    def test_no_root_is_not_success(self):
        out=self.run_map(lambda x:x+.1)
        self.assertNotEqual(out.status,"converged")
        self.assertGreater(out.residual_max,1e-5)
        self.assertLessEqual(out.evaluations,32)

    def test_budget_returns_evaluated_accepted_state(self):
        out=self.run_map(lambda x:1.2*x+.1,max_evaluations=2)
        self.assertEqual(out.status,"evaluation_budget")
        self.assertEqual(out.evaluations,2)
        torch.testing.assert_close(out.state,self.target)
        a,b=self.pair.coefficients
        residual=a*out.state+b*self.map_predictor(lambda x:1.2*x+.1)(out.state)-self.target
        self.assertAlmostEqual(out.residual_max,float(residual.abs().max()),places=6)

    def test_trial_and_nfe_accounting(self):
        out=self.run_map(lambda x:1.2*x+.1)
        self.assertEqual(sum(row["phase"]=="evaluation_started" for row in out.trace),out.evaluations)
        decisions=[row for row in out.trace if row["phase"]=="trial_decision"]
        self.assertEqual(len(decisions),out.evaluations-1)
        self.assertEqual(sum(row["accepted"] for row in decisions),out.accepted_updates)
        self.assertEqual(sum(not row["accepted"] for row in decisions),out.rejected_trials)

    def test_observer_mutations_do_not_change_solver(self):
        saved=[]
        def observe(count,state,residual):
            saved.append(count);state.zero_();residual.fill_(123)
        out=invert_pair_accelerated(self.pair,self.target,self.map_predictor(lambda x:1.2*x+.1),
                                   AccelerationPolicy(),state_observer=observe)
        self.assertEqual(out.status,"converged")
        self.assertEqual(saved,list(range(1,out.evaluations+1)))
        torch.testing.assert_close(self.target,torch.full_like(self.target,.25))

    def test_journal_and_observer_failures_propagate(self):
        def fail(*_):raise RuntimeError("owned persistence failure")
        for name in ("progress","state_observer"):
            with self.subTest(name=name),self.assertRaisesRegex(RuntimeError,"persistence"):
                invert_pair_accelerated(self.pair,self.target,lambda x:torch.zeros_like(x),
                                        AccelerationPolicy(),**{name:fail})

    def test_nonfinite_prediction_fails(self):
        with self.assertRaises(EmbeddingError):
            invert_pair_accelerated(self.pair,self.target,lambda x:torch.full_like(x,float("nan")),AccelerationPolicy())

    def test_mutating_predictor_is_isolated(self):
        def predict(x):x.fill_(100);return torch.zeros_like(x)
        out=invert_pair_accelerated(self.pair,self.target,predict,AccelerationPolicy())
        self.assertEqual(out.status,"converged")
        a,_=self.pair.coefficients
        torch.testing.assert_close(out.state,self.target/a)

    def test_step_guard_refuses_without_predictor_call(self):
        out=self.run_map(lambda x:torch.full_like(x,1000.),maximum_step_rms=.001)
        self.assertEqual(out.status,"safeguard_stagnation")
        self.assertEqual(out.evaluations,1)

    def test_shape_and_type_guard(self):
        for bad in (self.target.double(),self.target.requires_grad_(),torch.zeros(2,4,2,2)):
            with self.assertRaises(EmbeddingError):
                invert_pair_accelerated(self.pair,bad,lambda x:x,AccelerationPolicy())


if __name__=="__main__":unittest.main()
