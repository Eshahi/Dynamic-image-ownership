"""Owned CPU fake modules only; test policy values are not science parameters."""
from types import SimpleNamespace
import unittest
from unittest.mock import patch
try:
    import torch
    import diffusers
except ImportError:
    torch=diffusers=None
from src.embedding.proposed import EmbeddingError
from src.embedding.inversion import InversionPolicy
from src.embedding.reconstruction_comparison import comparison, ComparisonPolicy, ARMS
from scripts import test_c4_inversion_path as owned_fixture


@unittest.skipIf(torch is None or diffusers is None,"existing pinned Torch/Diffusers absent")
class ComparisonTests(unittest.TestCase):
    def setUp(self):
        fixture=owned_fixture.PathTests();fixture.setUp();self.backend=fixture.backend
        class FakeVAE(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.scale=torch.nn.Parameter(torch.tensor(.1),requires_grad=False)
                self.config=SimpleNamespace(scaling_factor=.18215)
                self.calls=[]
            def encode(self,x):
                self.calls.append("encode")
                value=torch.full((1,4,x.shape[-2]//8,x.shape[-1]//8),.25)
                return SimpleNamespace(latent_dist=SimpleNamespace(mode=lambda:value))
            def decode(self,x):
                self.calls.append("decode")
                return SimpleNamespace(sample=torch.nn.functional.interpolate(
                    x.mean(1,keepdim=True)*self.scale,scale_factor=8,mode="nearest").repeat(1,3,1,1))
        self.backend.vae=FakeVAE().eval();self.backend.progress=None
        self.source=torch.full((1,3,33,35),.25)
        self.noise=torch.full((1,4,8,8),.1)
        self.policy=ComparisonPolicy(InversionPolicy(),
            InversionPolicy(method="guided_coordinate",prior_weight=1e-8),64,10,1e-5)
        self.events=[];self.images={};self.states=[]

    def run_comparison(self,**kwargs):
        args=dict(progress=self.events.append,
            save_arm=lambda arm,image,metadata:self.images.update({arm:(image,metadata)}),
            save_state=lambda arm,row,state:self.states.append((arm,row,state)))
        args.update(kwargs)
        return comparison(self.backend,self.source,self.noise,self.policy,**args)

    def test_one_shared_encode_fixed_arm_order_native_grid(self):
        result=self.run_comparison()
        self.assertEqual(tuple(result["arms"]),ARMS)
        self.assertEqual(self.backend.vae.calls.count("encode"),1)
        self.assertEqual(result["status"],"completed_requires_png_safety_quality")
        self.assertEqual(tuple(self.images),ARMS)
        for image,metadata in self.images.values():
            self.assertEqual(tuple(image.shape),(1,3,33,35))
            self.assertFalse(image.requires_grad)
            self.assertEqual(metadata["safety"],"NOT_RUN")
            self.assertEqual(metadata["image_quality"],"NOT_RUN")
        self.assertTrue(torch.all(self.source==.25));self.assertTrue(torch.all(self.noise==.1))
        self.assertFalse(result["scientific_acceptance"])

    def test_owned_payload_mutation_cannot_change_later_inputs(self):
        def mutate(arm,image,metadata):
            image.zero_();metadata["status"]="invented"
        result=self.run_comparison(save_arm=mutate)
        self.assertTrue(all(row["status"]=="rendered_requires_png_safety_quality" for row in result["arms"].values()))
        self.assertTrue(torch.all(self.source==.25));self.assertTrue(torch.all(self.noise==.1))

    def test_nonconverged_arms_recorded_without_decoder_fallback(self):
        self.policy=ComparisonPolicy(InversionPolicy(max_evaluations=1),
            InversionPolicy(method="guided_coordinate",prior_weight=.01,max_evaluations=1),64,10,1e-5)
        result=self.run_comparison()
        self.assertEqual(result["failed_arms"],ARMS[3:])
        self.assertEqual(tuple(self.images),ARMS[:3])
        self.assertEqual(result["status"],"completed_with_nonconverged_arms")
        self.assertEqual(self.backend.vae.calls.count("decode"),3)
        self.assertEqual([arm for arm,_,_ in self.states],list(ARMS[3:]))

    def test_arm_save_failure_keeps_earlier_arm_only(self):
        def save(arm,image,metadata):
            if arm==ARMS[1]:raise OSError("owned save failure")
            self.images[arm]=(image,metadata)
        with self.assertRaisesRegex(OSError,"owned save"):
            self.run_comparison(save_arm=save)
        self.assertEqual(tuple(self.images),(ARMS[0],))
        self.assertEqual([r["arm"] for r in self.events if r["phase"]=="comparison_arm_saved"],[ARMS[0]])
        self.assertFalse(any(r["phase"]=="comparison_terminated" for r in self.events))

    def test_vae_mutation_after_arm_persistence_is_not_marked_saved(self):
        def mutate(arm,image,metadata):self.backend.vae.scale.add_(.1)
        with self.assertRaisesRegex(EmbeddingError,"VAE identity or mutation"):
            self.run_comparison(save_arm=mutate)
        self.assertFalse(any(r["phase"]=="comparison_arm_saved" for r in self.events))

    def test_journal_failure_precedes_encoding(self):
        def fail(row):raise RuntimeError("owned journal failure")
        with self.assertRaisesRegex(RuntimeError,"owned journal"):
            self.run_comparison(progress=fail)
        self.assertEqual(self.backend.vae.calls,[])
        self.assertEqual(self.backend.unet.calls,[])

    def test_malformed_noise_policy_callbacks_refused_before_encoding(self):
        self.noise=self.noise.double()
        with self.assertRaises(EmbeddingError):self.run_comparison()
        self.assertEqual(self.backend.vae.calls,[])
        self.noise=self.noise.float()
        with self.assertRaises(EmbeddingError):self.run_comparison(save_state=None)
        self.assertEqual(self.backend.vae.calls,[])
        with self.assertRaises(EmbeddingError):
            ComparisonPolicy(InversionPolicy(),InversionPolicy(method="guided_coordinate"),64,10,1e-5)

    def test_cooperative_comparison_timeout_before_encode(self):
        with patch("src.embedding.reconstruction_comparison.time.monotonic",side_effect=[0.,11.]):
            with self.assertRaisesRegex(EmbeddingError,"time limit"):
                self.run_comparison()
        self.assertEqual(self.backend.vae.calls,[])
        self.assertEqual(self.events[-1]["phase"],"comparison_time_limit")


if __name__=="__main__":unittest.main()
