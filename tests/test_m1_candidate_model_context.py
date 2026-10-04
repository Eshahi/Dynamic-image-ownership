"""Loader wiring and path-free numerical hooks with CPU-only mocked model fixtures."""
import hashlib, subprocess, sys, types, unittest
from pathlib import Path
from unittest import mock
import numpy as np
import torch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import m1_candidate_model_context as context
import m1_candidate_rehearsal_worker as worker


class FixtureVAE(torch.nn.Module):
    loads=[]
    def __init__(self,dtype):
        super().__init__();self.weight=torch.nn.Parameter(torch.ones(1,dtype=dtype));self.config=types.SimpleNamespace(scaling_factor=.18215)
    def to(self,*args,**kwargs):return self
    @classmethod
    def from_pretrained(cls,path,**kwargs):
        cls.loads.append((path,kwargs));return cls(kwargs['torch_dtype'])

class FixtureSafety(FixtureVAE):loads=[]
class FixtureProcessor:
    loads=[]
    @classmethod
    def from_pretrained(cls,path,**kwargs):cls.loads.append((path,kwargs));return object()


class ContextTests(unittest.TestCase):
    def test_import_does_not_import_torch_or_load_models(self):
        subprocess.run([sys.executable,'-c',"import sys;sys.path.insert(0,'scripts');import m1_candidate_model_context;assert 'torch' not in sys.modules;assert 'diffusers' not in sys.modules"],cwd=ROOT,check=True,capture_output=True)
    def test_invalid_paths_and_resource_types_fail_before_models(self):
        config=worker.configuration();context.validate_inputs(config,'a'*64)
        for bad in [dict(config,profile='inputs/heldout.png'),dict(config,gpu_budget_bytes=True),dict(config,ram_budget_bytes=17*1024**3)]:
            with self.assertRaises(ValueError):context.validate_inputs(bad,'a'*64)
        with self.assertRaises(ValueError):context.validate_inputs(config,'HEAD')
    def test_real_loader_wiring_local_only_frozen_dtype_and_cpu_evaluators(self):
        import three_threat_models as models
        import a6_clip_visual as clip_module
        import m1_terminal_repeatability as repeat
        import m1_phasemark as util
        FixtureVAE.loads=[];FixtureSafety.loads=[];FixtureProcessor.loads=[]
        diff=types.ModuleType('diffusers');diff.AutoencoderKL=FixtureVAE
        image=types.ModuleType('diffusers.image_processor');image.VaeImageProcessor=lambda **kwargs:object()
        safety=types.ModuleType('diffusers.pipelines.stable_diffusion.safety_checker');safety.StableDiffusionSafetyChecker=FixtureSafety
        trans=types.ModuleType('transformers');trans.CLIPImageProcessor=FixtureProcessor
        patches=[mock.patch.dict(sys.modules,{'diffusers':diff,'diffusers.image_processor':image,'diffusers.pipelines.stable_diffusion.safety_checker':safety,'transformers':trans}),
            mock.patch.object(models,'block_network'),mock.patch.object(repeat,'configure',return_value={'fixture':True}),
            mock.patch.object(models,'verify_assets',return_value=({'files':[None]*17},Path('fixture-package'))),
            mock.patch.object(models,'load_lpips',return_value=torch.nn.Linear(1,1).requires_grad_(False)),
            mock.patch.object(clip_module,'load_visual_encoder',return_value=(torch.nn.Linear(1,1),object())),
            mock.patch.object(torch.cuda,'is_available',return_value=True),mock.patch.object(torch.cuda,'is_initialized',return_value=False),
            mock.patch.object(torch.cuda,'get_device_name',return_value='CPU-only fixture'),mock.patch.object(torch.cuda,'get_device_capability',return_value=(0,0)),
            mock.patch.object(torch.cuda,'mem_get_info',return_value=(12*1024**3,16*1024**3)),mock.patch.object(torch.cuda,'set_per_process_memory_fraction'),
            mock.patch.object(torch.backends.cudnn,'version',return_value=0),mock.patch.object(context.subprocess,'check_output',return_value='fixture-only telemetry'),
            mock.patch.object(context,'sha',side_effect=lambda path:hashlib.sha256(str(path).encode()).hexdigest()),mock.patch.object(util,'working_set_bytes',return_value=12345)]
        for p in patches:p.start()
        try:
            publications=[];events=[];value=context.CandidateModelContext(worker.configuration(),'a'*64,publish=publications.append,event=lambda **v:events.append(v))
            self.assertEqual(len(FixtureVAE.loads),2);self.assertEqual(len(FixtureSafety.loads),1)
            for path,kwargs in FixtureVAE.loads+FixtureSafety.loads:
                self.assertTrue(kwargs['local_files_only']);self.assertTrue(kwargs['use_safetensors']);self.assertEqual(kwargs['variant'],'fp16')
            self.assertEqual([kw['torch_dtype'] for _,kw in FixtureVAE.loads],[torch.float32,torch.float16])
            self.assertFalse(value.vae_fp32.training);self.assertTrue(all(not p.requires_grad for p in value.vae_fp32.parameters()))
            self.assertTrue(all(p.device.type=='cpu' and not p.requires_grad for model in (value.clip,value.metric) for p in model.parameters()))
            self.assertEqual(value.provenance['assets']['files'],[None]*17);self.assertEqual(value.peaks['peak_rss_bytes'],12345)
            self.assertTrue(events);self.assertTrue(publications)
        finally:
            for p in reversed(patches):p.stop()
    def test_feature_input_preserves_helper_result_without_normalization(self):
        import three_threat_models as models
        obj=context.CandidateModelContext.__new__(context.CandidateModelContext);obj.clip=object();obj.transform=object()
        helper=torch.tensor([[.3,.4]])
        with mock.patch.object(models,'clip_feature',return_value=helper) as spy:
            self.assertIs(obj.adapter_feature_input(np.zeros((512,512,3),np.uint8)),helper);self.assertEqual(spy.call_count,1)
    def test_shared_vae_operation_injection_and_receipt(self):
        import m1_confirmatory_image_operations as ops
        obj=context.CandidateModelContext.__new__(context.CandidateModelContext)
        obj.vae_public=object();obj.processor=object();obj.safety_processor=object();order=[]
        obj.safety=lambda **kwargs:order.append('safety') or ('fixture',[False]);obj.event=lambda **v:order.append(v['receipt']['operator'])
        rgb=np.zeros((512,512,3),np.uint8)
        def operation(image,**kwargs):
            kwargs['safety'](images='fixture');return ops.OperationResult(rgb.copy(),{'operator':'fixture-vae'})
        with mock.patch.object(ops,'vae_mode',side_effect=operation):
            result=obj.vae_cycle(rgb,before_safety=lambda:order.append('injection-hook'))
        self.assertTrue(np.array_equal(result,rgb));self.assertEqual(order,['injection-hook','safety','fixture-vae'])
    def test_quality_uses_same_pixel_definition_and_cpu_lpips(self):
        import three_threat_models as models
        from m1_latent_reconstruction import quality
        obj=context.CandidateModelContext.__new__(context.CandidateModelContext);obj.metric=object()
        a=np.zeros((512,512,3),np.uint8);b=a.copy();b[4:20,4:20]=1
        with mock.patch.object(models,'lpips_score',return_value=.02):actual=obj.quality(a,b)
        expected=quality(a,b)
        self.assertEqual({k:actual[k] for k in expected},expected);self.assertEqual(actual['lpips'],.02);self.assertTrue(actual['quality_admissible'])
        with self.assertRaises(ValueError):obj.quality(a.astype(np.float32),b)

if __name__=='__main__':unittest.main()
