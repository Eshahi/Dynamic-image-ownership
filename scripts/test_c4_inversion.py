"""Owned synthetic CPU tensors only; scheduler parity never loads weights."""
import unittest
try:
    import torch
except ImportError:
    torch = None
from src.embedding.inversion import DDIMPair, InversionPolicy, invert_pair
from src.embedding.proposed import EmbeddingError


class PolicyTests(unittest.TestCase):
    def test_strict_alpha(self):
        for alpha, previous in ((True, 1), (0, 1), (.5, .4), (float("nan"), 1),
                                (.5, float("inf")), (.5, "1"), (10**1000, 1)):
            with self.subTest(alpha=alpha, previous=previous), self.assertRaises(EmbeddingError):
                DDIMPair(alpha, previous)

    def test_strict_policy(self):
        invalid = ({"max_evaluations":True}, {"max_evaluations":1.5}, {"max_evaluations":257},
                   {"max_backtracks":-1}, {"method":"unknown"}, {"damping":0},
                   {"prior_weight":1}, {"residual_tolerance":float("nan")},
                   {"denominator_eta":True}, {"maximum_coordinate_step":float("inf")})
        for kwargs in invalid:
            with self.subTest(kwargs=kwargs), self.assertRaises(EmbeddingError):
                InversionPolicy(**kwargs)


@unittest.skipIf(torch is None, "base Windows environment has no Torch")
class InversionTests(unittest.TestCase):
    def setUp(self):
        self.target = torch.full((1,4,2,2), .25)
        self.pair = DDIMPair(.5, .8)

    def test_constant_predictor_exact_fixed_point_and_budget_count(self):
        events = []
        out = invert_pair(self.pair, self.target, lambda x: torch.full_like(x, .1),
                          InversionPolicy(), progress=events.append)
        a,b = self.pair.coefficients
        torch.testing.assert_close(out.state, (self.target-b*.1)/a)
        self.assertEqual(out.status,"converged")
        self.assertEqual((out.evaluations,out.backward_evaluations),(2,0))
        self.assertEqual(sum(r["phase"] == "evaluation_started" for r in events),2)
        self.assertTrue(torch.all(self.target == .25))
        self.assertFalse(out.state.requires_grad)

    def test_guided_coordinate_affine_root(self):
        slope, intercept = .2,.1
        policy=InversionPolicy(method="guided_coordinate",max_evaluations=32)
        out=invert_pair(self.pair,self.target,lambda x:slope*x+intercept,policy)
        a,b=self.pair.coefficients
        expected=(self.target-b*intercept)/(a+b*slope)
        self.assertEqual(out.status,"converged")
        torch.testing.assert_close(out.state,expected,atol=1e-5,rtol=1e-5)
        self.assertGreater(out.backward_evaluations,0)
        self.assertLessEqual(out.evaluations,policy.max_evaluations)

    def test_prior_cannot_hide_nonzero_reconstruction_residual(self):
        out=invert_pair(self.pair,self.target,lambda x:torch.zeros_like(x),
            InversionPolicy(method="guided_coordinate",prior_weight=100.,max_evaluations=16),
            prior_mean=self.target)
        self.assertNotEqual(out.status,"converged")
        self.assertGreater(out.residual_max,1e-5)
        self.assertLessEqual(out.evaluations,16)

    def test_nonzero_guidance_and_backtrack_accounting(self):
        policy=InversionPolicy(method="guided_coordinate",prior_weight=.01,
            max_evaluations=16,maximum_coordinate_step=.05,residual_tolerance=0)
        out=invert_pair(self.pair,self.target,lambda x:x*.2+.1,policy,
                        prior_mean=torch.zeros_like(self.target))
        self.assertEqual(sum(r["phase"]=="evaluation_started" for r in out.trace),out.evaluations)
        self.assertEqual(sum(r["phase"]=="backward_started" for r in out.trace),out.backward_evaluations)
        self.assertLessEqual(out.evaluations,16)
        self.assertIn(out.status,("evaluation_budget","line_search_failed","converged"))
        # Returned forward error, not last rejected trial's error.
        error=float((self.pair.denoise(out.state,out.state*.2+.1)-self.target).abs().max())
        self.assertAlmostEqual(out.residual_max,error,places=6)

    def test_unsafe_coordinate_denominator_is_not_division_fallback(self):
        # First prediction coordinate cancels identity dependence while others
        # remain nonzero; gradient is zero only on that coordinate.
        a,b=self.pair.coefficients
        def predict(x):
            mask=torch.zeros_like(x);mask.flatten()[0]=1
            return -a*x*mask/b
        out=invert_pair(self.pair,-self.target,predict,
            InversionPolicy(method="guided_coordinate",denominator_eta=1.))
        self.assertEqual(out.status,"unsafe_denominator")
        self.assertEqual(out.evaluations,1)

    def test_predictor_failure_propagates_with_partial_start(self):
        events=[]
        def fail(x): raise RuntimeError("owned predictor failure")
        with self.assertRaisesRegex(RuntimeError,"owned predictor"):
            invert_pair(self.pair,self.target,fail,InversionPolicy(),progress=events.append)
        self.assertEqual(events,[{"phase":"evaluation_started","evaluation":1,"gradient_enabled":False}])

    def test_noncontractive_fixed_point_budget_not_success(self):
        policy=InversionPolicy(max_evaluations=4)
        out=invert_pair(self.pair,self.target,lambda x:10*x,policy)
        self.assertEqual(out.status,"evaluation_budget")
        self.assertEqual(out.evaluations,4)
        self.assertGreater(out.residual_max,1.)

    def test_zero_gradient_preserves_evaluated_state(self):
        a,b=self.pair.coefficients
        out=invert_pair(self.pair,self.target,lambda x:(-a*x)/b,
                       InversionPolicy(method="guided_coordinate"))
        self.assertEqual(out.status,"zero_gradient")
        self.assertEqual(out.backward_evaluations,1)
        torch.testing.assert_close(out.state,self.target)

    def test_one_evaluation_budget_returns_initial_not_unchecked_proposal(self):
        for method in ("fixed_point","guided_coordinate"):
            out=invert_pair(self.pair,self.target,lambda x:x*.2,
                           InversionPolicy(method=method,max_evaluations=1))
            self.assertEqual(out.status,"evaluation_budget")
            self.assertEqual(out.backward_evaluations,0)
            torch.testing.assert_close(out.state,self.target)

    def test_shape_finite_grad_and_prior_fail_closed_before_predictor(self):
        calls=[]
        def predict(x): calls.append(1); return x
        invalid=(self.target.double(),self.target.clone().requires_grad_(),
                 torch.zeros(1,3,2,2),torch.full_like(self.target,float("nan")),
                 torch.empty(1,4,0,2))
        for target in invalid:
            with self.assertRaises(EmbeddingError):
                invert_pair(self.pair,target,predict,InversionPolicy())
        for mean,weight in ((self.target,0.),(None,1.),(self.target.double(),1.)):
            with self.assertRaises(EmbeddingError):
                invert_pair(self.pair,self.target,predict,
                    InversionPolicy(method="guided_coordinate",prior_weight=weight),prior_mean=mean)
        self.assertEqual(calls,[])

    def test_bad_predictions_and_failure_journal(self):
        for bad in (torch.zeros(1,4,3,2),self.target.double(),
                    torch.full_like(self.target,float("inf"))):
            events=[]
            with self.assertRaises(EmbeddingError):
                invert_pair(self.pair,self.target,lambda x:bad,InversionPolicy(),progress=events.append)
            self.assertEqual(events[-1]["phase"],"evaluation_started")
            self.assertFalse(any(row["phase"]=="terminated" for row in events))

    def test_callback_failure_and_mutation_isolation(self):
        calls=[]
        def broken(row): raise OSError("owned journal failure")
        with self.assertRaises(OSError):
            invert_pair(self.pair,self.target,lambda x:calls.append(1),InversionPolicy(),progress=broken)
        self.assertEqual(calls,[])
        def mutate(x): x.fill_(.1); return x
        out=invert_pair(self.pair,self.target,mutate,InversionPolicy())
        self.assertEqual(out.status,"converged")
        self.assertTrue(torch.all(self.target==.25))

    def test_direct_pair_validation_and_identity(self):
        epsilon=torch.ones_like(self.target)
        torch.testing.assert_close(DDIMPair(.5,.5).denoise(self.target,epsilon),self.target)
        with self.assertRaises(EmbeddingError):
            self.pair.denoise(self.target,epsilon.double())

    def test_all_pinned_ddim_pairs_match_diffusers_synthetic_scheduler(self):
        try:
            from diffusers import DDIMScheduler
        except ImportError:
            self.skipTest("pinned Diffusers absent, no installation inferred")
        scheduler=DDIMScheduler(num_train_timesteps=1000,beta_start=.00085,beta_end=.012,
            beta_schedule="scaled_linear",prediction_type="epsilon",timestep_spacing="leading",
            steps_offset=1,set_alpha_to_one=False,clip_sample=False,thresholding=False,
            rescale_betas_zero_snr=False)
        scheduler.set_timesteps(10)
        state=torch.linspace(-1,1,16).reshape(1,4,2,2)
        epsilon=torch.linspace(.1,.4,16).reshape_as(state)
        for time in scheduler.timesteps.tolist():
            previous=time-100
            alpha=float(scheduler.alphas_cumprod[time])
            previous_alpha=float(scheduler.alphas_cumprod[previous] if previous>=0
                                 else scheduler.final_alpha_cumprod)
            out=DDIMPair(alpha,previous_alpha).denoise(state,epsilon)
            expected=scheduler.step(epsilon,time,state,eta=0,return_dict=False)[0]
            torch.testing.assert_close(out,expected,atol=2e-6,rtol=2e-6)


if __name__ == "__main__": unittest.main()
