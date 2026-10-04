import contextlib
import json
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import m1_confirmatory_image_operations as ops


class UNet:
    def register_forward_hook(self, hook, with_kwargs=False):
        self.hook=hook;self.removed=False
        return types.SimpleNamespace(remove=lambda:setattr(self,'removed',True))


class Pipeline:
    def __init__(self):
        self.unet=UNet();self.safety_checker=object();self.feature_extractor=object()
        self.scheduler=types.SimpleNamespace(config=types.SimpleNamespace(**ops.models.DDIM_CONFIG),timesteps=list(ops.TIMESTEPS))
        self.flags=[False];self.drift=False
    def __call__(self,**kw):
        self.kw=kw
        for timestep in ops.TIMESTEPS[-int(20*kw['strength']):]:
            self.unet.hook(self.unet,(),{'timestep':timestep+(1 if self.drift else 0)},None)
        return types.SimpleNamespace(images=[kw['image']],nsfw_content_detected=self.flags)


class Generator:
    def __init__(self,device):self.device=device
    def manual_seed(self,seed):self.seed=seed;return self


class ImageOperationsTests(unittest.TestCase):
    def setUp(self):self.image=np.zeros((512,512,3),dtype=np.uint8)
    def regen(self,pipeline,strength=.1,seed=2):
        return ops.regeneration(self.image,strength,seed,pipeline=pipeline,generator_factory=Generator,inference_context=contextlib.nullcontext)
    def test_all_actual_timesteps_and_fresh_generators(self):
        pipe=Pipeline();generators=[]
        for strength in ops.STRENGTHS:
            result=self.regen(pipe,strength);generators.append(pipe.kw['generator'])
            self.assertEqual(result.receipt['actual_ddim_timesteps'],list(ops.TIMESTEPS[-int(20*strength):]))
            self.assertEqual(pipe.kw['prompt'],'');self.assertEqual(pipe.kw['negative_prompt'],'')
            self.assertEqual(pipe.kw['guidance_scale'],1);self.assertEqual(pipe.kw['eta'],0)
            self.assertEqual(pipe.kw['generator'].device,'cuda');self.assertTrue(pipe.unet.removed)
        self.assertEqual(len({id(g) for g in generators}),4)
    def test_safety_block_retains_executed_steps(self):
        pipe=Pipeline();pipe.flags=[True]
        with self.assertRaises(ops.OperationFailure) as caught:self.regen(pipe)
        self.assertEqual(caught.exception.receipt['actual_ddim_timesteps'],[51.,1.])
        self.assertEqual(caught.exception.receipt['safety_verdict'],[True]);self.assertTrue(pipe.unet.removed)
    def test_timestep_drift_and_scheduler_rejected(self):
        pipe=Pipeline();pipe.drift=True
        with self.assertRaises(ops.OperationFailure):self.regen(pipe)
        pipe=Pipeline();pipe.scheduler.config.eta=1;pipe.scheduler.config.steps_offset=0
        with self.assertRaises(ValueError):self.regen(pipe)
    def test_no_strength_seed_coercion(self):
        for strength,seed in ((.3,0),(.1,True),(.1,3)):
            with self.assertRaises(ValueError):self.regen(Pipeline(),strength,seed)
    def test_patch_exact_bounds_both_arms(self):
        donor=np.full_like(self.image,221)
        for size in (128,256):
            for arm in ('C0','C1'):
                result=ops.center_patch(self.image,donor,size,donor_control=arm)
                lo=(512-size)//2;expected=self.image.copy();expected[lo:lo+size,lo:lo+size]=donor[lo:lo+size,lo:lo+size]
                np.testing.assert_array_equal(result.rgb8,expected)
                self.assertEqual(result.receipt['query_budget'],0)
                self.assertEqual(result.receipt['recipient_control'],'C0-source')
        self.assertFalse(self.image.any())
    def test_rgb_and_patch_reject_coercion(self):
        for image in (self.image.astype(float),self.image[:256],self.image.tolist()):
            with self.assertRaises(ValueError):ops.rgb8(image)
        with self.assertRaises(ValueError):ops.center_patch(self.image,self.image,64,donor_control='C1')
    def vae_fixture(self):
        import torch
        latent=torch.full((1,4,64,64),.125,dtype=torch.float16)
        vae=types.SimpleNamespace(config=types.SimpleNamespace(scaling_factor=.18215),
             encode=lambda x:types.SimpleNamespace(latent_dist=types.SimpleNamespace(mode=lambda:latent)))
        def decode(u,return_dict=False):
            vae.decoder_input=u.clone();return (torch.zeros((1,3,512,512),dtype=torch.float16),)
        vae.decode=decode
        processor=types.SimpleNamespace(preprocess=lambda image:torch.zeros((1,3,512,512),dtype=torch.float16),
            postprocess=lambda x,output_type,**kw: [np.full((512,512,3),.5)] if output_type=='np' else [image for image in [ops.Image.fromarray(self.image)]])
        safety_processor=lambda images,return_tensors:types.SimpleNamespace(pixel_values=torch.zeros((1,3,224,224)))
        return torch,latent,vae,processor,safety_processor
    def test_vae_mode_actual_half_scale_order(self):
        torch,latent,vae,processor,sp=self.vae_fixture()
        result=ops.vae_mode(self.image,vae=vae,processor=processor,safety=lambda **kw:(kw['images'],[False]),safety_processor=sp,torch_module=torch,device='cpu')
        self.assertTrue(torch.equal(vae.decoder_input,(latent*.18215)/.18215))
        self.assertEqual(vae.decoder_input.dtype,torch.float16);self.assertTrue((result.rgb8==128).all())
    def test_vae_wrong_latent_and_malformed_safety(self):
        torch,latent,vae,processor,sp=self.vae_fixture()
        kwargs=dict(vae=vae,processor=processor,safety_processor=sp,torch_module=torch,device='cpu')
        with self.assertRaises(ops.OperationFailure):ops.vae_mode(self.image,safety=lambda **kw:(kw['images'],[0]),**kwargs)
        vae.encode=lambda x:types.SimpleNamespace(latent_dist=types.SimpleNamespace(mode=lambda:latent.float()))
        with self.assertRaises(ops.OperationFailure):ops.vae_mode(self.image,safety=lambda **kw:(kw['images'],[False]),**kwargs)
    def test_vae_rgb_rounding_promotes_before_multiplication(self):
        torch,latent,vae,processor,sp=self.vae_fixture()
        value=np.full((512,512,3),np.float32(.5/255),dtype=np.float32)
        self.assertEqual(int(np.rint(value[0,0,0]*np.float32(255))),0)
        processor.postprocess=lambda x,output_type,**kw:[value] if output_type=='np' else [ops.Image.fromarray(self.image)]
        result=ops.vae_mode(self.image,vae=vae,processor=processor,safety=lambda **kw:(kw['images'],[False]),safety_processor=sp,torch_module=torch,device='cpu')
        self.assertTrue((result.rgb8==1).all())
    def profile(self):
        value=json.loads((Path(__file__).resolve().parents[1]/'configs/revised-watermark-v5.example.json').read_text())
        value['semantic_source']='external:clip-vit-b32-a6-40d365715913';return value
    def test_v5_real_cpu_saved_rgb_parity_and_seed_metadata(self):
        profile=self.profile();features=[1.,0.,.25,-.5]*4;adapter=ops.V5Comparator(profile,lambda rgb:features)
        yy,xx=np.indices((512,512));image=np.stack([(xx//2)%256,(yy//2)%256,((xx+yy)//4)%256],axis=-1).astype(np.uint8)
        result,report=adapter.embed(image,'fixture:image-ops')
        schedule=result.receipt['schedule'];self.assertIn(schedule['owner'],ops.owners.A4_OWNERS)
        ops.owners.validate_seed_metadata(schedule['seed_uint64_decimal'],schedule['seed_uint64_hex'])
        self.assertIsNone(schedule['scientific_embedding_seed'])
        actual=adapter.extract(result.rgb8,schedule['owner'])
        expected=ops.codec.detect_rgb(result.rgb8.tolist(),schedule['owner'],profile=profile,semantic_features=features,roster_size=1)
        scientific=lambda result:{key:value for key,value in result.items() if key!='timing_ms'}
        self.assertEqual(scientific(actual),scientific(expected))
        self.assertEqual(scientific(actual),scientific(report['verification']))
        with self.assertRaises(ValueError):adapter.extract(result.rgb8,'fixture:owner')
    def test_t5_selector_preserves_missing_and_disjoint(self):
        rows=[dict(uid='a',group_id='a',categories=[1],phash=0,error=None),dict(uid='b',group_id='b',categories=[1],phash=255,error=None)]
        result=ops.select_t5_pairs(rows,['a','b','c'])
        self.assertEqual(result['enumerated_pairs'],3);self.assertEqual(result['selected_pairs'],1)
        self.assertEqual(sum(row['reason']=='missing_source_observation' for row in result['ledger']),2)


if __name__=='__main__':unittest.main()
