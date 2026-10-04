"""CPU import/startup mocks: no model loading, GPU access or scientific results."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import Mock, patch

ROOT=Path(__file__).resolve().parents[1]


def load(name):
    # Deliberately do not register this alias in sys.modules: provenance must
    # use explicit source paths rather than assume an import alias exists.
    spec=importlib.util.spec_from_file_location("readiness_"+name,ROOT/"scripts"/(name+".py"))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


class StartupBoundary(Exception):pass


class Config(dict):
    def __getattr__(self,name):return self[name]


class Pipeline:
    def __init__(self,**kwargs):
        self.components={};self.safety_checker=Mock();self.feature_extractor=Mock()
        self.unet=Mock();self.vae=Mock();self.text_encoder=Mock()
    def to(self,device):return self
    def set_progress_bar_config(self,**kwargs):pass


class ReadinessTests(unittest.TestCase):
    def test_imports_do_not_load_models_and_assets_are_main(self):
        for name in ("m1_gaussian_shading","m1_progressive_latent"):
            module=load(name)
            self.assertEqual(module.ASSETS,module.MAIN/".thesis-build/assets/a6")
            self.assertNotIn(module.__name__,sys.modules)

    def startup(self,name,manifest_name):
        module=load(name)
        torch=ModuleType("torch");torch.float16="fixture-float16"
        torch.cuda=SimpleNamespace(is_available=lambda:True,set_per_process_memory_fraction=Mock(),
          get_device_properties=lambda n:SimpleNamespace(total_memory=24*1024**3),get_device_name=lambda n:"MOCK-NO-GPU")
        torch.backends=SimpleNamespace(cuda=SimpleNamespace(matmul=SimpleNamespace()),cudnn=SimpleNamespace())
        ddim=Mock(side_effect=lambda **kwargs:SimpleNamespace(config=Config(kwargs)))
        inverse=SimpleNamespace(from_config=lambda config:SimpleNamespace(config=Config(config)))
        pretrained=Mock(return_value=Pipeline())
        diffusers=ModuleType("diffusers");diffusers.DDIMScheduler=ddim;diffusers.DDIMInverseScheduler=inverse
        diffusers.StableDiffusionPipeline=SimpleNamespace(from_pretrained=pretrained)
        diffusers.StableDiffusionImg2ImgPipeline=Pipeline
        threats=ModuleType("three_threat_models");threats.block_network=Mock()
        threats.DDIM_CONFIG={"prediction_type":"epsilon","clip_sample":False}
        threats.verify_assets=Mock(return_value=({"files":[]},Path("fixture-lpips-package")))
        threats.load_lpips=Mock(return_value=object());threats.lpips_score=Mock();threats.validate_generated=Mock();threats.clip_feature=Mock()
        visual=ModuleType("a6_clip_visual")
        visual.load_visual_encoder=Mock(side_effect=StartupBoundary("CPU startup boundary before checkpoint loading"))
        reconstruction=ModuleType("m1_latent_reconstruction");reconstruction.quality=Mock()
        pil=ModuleType("PIL");pil.Image=Mock()
        mocks={"torch":torch,"diffusers":diffusers,"numpy":ModuleType("numpy"),"PIL":pil,
               "three_threat_models":threats,"a6_clip_visual":visual,"m1_latent_reconstruction":reconstruction}
        with tempfile.TemporaryDirectory(prefix="m1-bc-readiness-") as directory:
            output=Path(directory)/".thesis-build/dev-runs/mock-startup"
            with patch.dict(sys.modules,mocks),patch.object(module,"MAIN",Path(directory)),patch.object(module.importlib.metadata,"version",return_value="mock-no-import"):
                if name=="m1_gaussian_shading":
                    with patch.object(module,"require_committed",return_value={"fixture":"not-a-scientific-run"}):
                        with self.assertRaises(StartupBoundary):module.run(ROOT/"research"/manifest_name,output)
                else:
                    self.assertEqual(module.run(ROOT/"research"/manifest_name,output),1)
                record=json.loads((output/"run.json").read_text())
                self.assertIn("CPU startup boundary",record["error"])
            threats.verify_assets.assert_called_once_with(module.ASSETS,ROOT/"research/a6-candidate-model-assets.json")
            threats.load_lpips.assert_called_once_with(module.ASSETS,Path("fixture-lpips-package"))
            visual.load_visual_encoder.assert_called_once_with(module.ASSETS/"clip/ViT-B-32.pt",device="cpu")
            self.assertEqual(pretrained.call_args.args[0],module.ASSETS/"sd15-fp16")
            self.assertTrue(pretrained.call_args.kwargs["local_files_only"])
            self.assertTrue(pretrained.call_args.kwargs["use_safetensors"])
            self.assertTrue(record["dependency_sha256"])
            self.assertEqual(record["data_split"],"synthetic")

    def test_gaussian_shading_mocked_startup_uses_explicit_assets_and_provenance(self):
        self.startup("m1_gaussian_shading","m1-gs-synthetic.json")

    def test_progressive_mocked_startup_uses_explicit_assets_and_provenance(self):
        self.startup("m1_progressive_latent","m1-progressive-synthetic.json")


if __name__=="__main__":unittest.main()
