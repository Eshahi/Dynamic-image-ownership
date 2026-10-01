import sys
from pathlib import Path
import unittest
from contextlib import nullcontext
from types import SimpleNamespace
from unittest.mock import Mock, patch
sys.path.insert(0,str(Path(__file__).resolve().parent))
from v4_study_models import diffusion_kwargs, vae_round_trip


class Generator:
    def __init__(self,device):
        self.device = device
    def manual_seed(self,seed):
        self.seed = seed
        return self


class Tests(unittest.TestCase):
    def test_exact_settings_and_fresh_paired_generators(self):
        a = diffusion_kwargs(.05,2,"C0",Generator)
        b = diffusion_kwargs(.05,2,"C1",Generator)
        self.assertIsNot(a["generator"],b["generator"])
        self.assertEqual(a["generator"].seed,b["generator"].seed)
        self.assertEqual(a["guidance_scale"],1.0)
        self.assertEqual(a["num_inference_steps"],20)
        self.assertEqual(a["eta"],0.0)
        self.assertEqual(a["prompt"],"")
    def test_unplanned_attempts_rejected(self):
        for strength,seed in ((.3,0),(.05,4),(.1,True),(True,0)):
            with self.assertRaises(ValueError):
                diffusion_kwargs(strength,seed,"input",Generator)

    def fake_pipeline(self, flags):
        image=SimpleNamespace(mode="RGB",size=(512,512))
        inputs,latent,decoded=object(),object(),object()
        tensor=Mock()
        tensor.to.return_value=inputs
        distribution=SimpleNamespace(mode=Mock(return_value=latent),sample=Mock())
        pipeline=SimpleNamespace(
            safety_checker=object(),feature_extractor=object(),
            vae=SimpleNamespace(dtype="fp16",encode=Mock(return_value=SimpleNamespace(latent_dist=distribution)),
                                decode=Mock(return_value=(decoded,))),
            image_processor=SimpleNamespace(preprocess=Mock(return_value=tensor),
                                            postprocess=Mock(return_value=[image])),
            run_safety_checker=Mock(return_value=(decoded,flags)))
        torch=SimpleNamespace(inference_mode=nullcontext,device=lambda value:"device:"+value)
        return pipeline,torch,distribution,tensor,inputs,latent,decoded,image

    def test_vae_mode_unscaled_with_safe_postprocess(self):
        pipeline,torch,distribution,tensor,inputs,latent,decoded,image=self.fake_pipeline([False])
        with patch.dict(sys.modules,{"torch":torch}):
            self.assertIs(vae_round_trip(pipeline,"source"),image)
        distribution.mode.assert_called_once_with()
        distribution.sample.assert_not_called()
        tensor.to.assert_called_once_with(device="cuda",dtype="fp16")
        pipeline.vae.encode.assert_called_once_with(inputs)
        pipeline.vae.decode.assert_called_once_with(latent,return_dict=False)
        pipeline.run_safety_checker.assert_called_once_with(decoded,"device:cuda","fp16")
        pipeline.image_processor.postprocess.assert_called_once_with(decoded,output_type="pil",do_denormalize=[True])

    def test_vae_unsafe_or_malformed_rejected_before_postprocess(self):
        for flags in (None,[],[True],[None],[0],[1],["False"],[False,False],False):
            with self.subTest(flags=flags):
                pipeline,torch,*_=self.fake_pipeline(flags)
                with patch.dict(sys.modules,{"torch":torch}),self.assertRaises((RuntimeError,TypeError)):
                    vae_round_trip(pipeline,"source")
                pipeline.image_processor.postprocess.assert_not_called()

    def test_vae_missing_safety_rejected_before_encode(self):
        for name in ("safety_checker","feature_extractor"):
            with self.subTest(component=name):
                pipeline,torch,*_=self.fake_pipeline([False])
                setattr(pipeline,name,None)
                with patch.dict(sys.modules,{"torch":torch}),self.assertRaises(RuntimeError):
                    vae_round_trip(pipeline,"source")
                pipeline.vae.encode.assert_not_called()
                pipeline.image_processor.postprocess.assert_not_called()


if __name__ == "__main__":
    unittest.main()
