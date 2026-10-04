"""CPU formula/control-flow parity; fake models, device literals mapped to CPU."""
import ast
import copy
import inspect
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock
import torch
from scripts import m1_progressive_latent as c

sys.path.insert(0,str(c.ROOT/'scripts'))
from three_threat_models import DDIM_CONFIG

def cpu_function(fn):
    # Preserve the actual function body; change only CUDA string literals and
    # synchronization availability. No scientific equations are rewritten.
    tree=ast.parse(inspect.getsource(fn))
    class Device(ast.NodeTransformer):
        def visit_Constant(self,node):
            return ast.copy_location(ast.Constant('cpu'),node) if node.value=='cuda' else node
    scope=dict(c.__dict__);exec(compile(ast.fix_missing_locations(Device().visit(tree)),'<cpu-device-parity>','exec'),scope)
    return scope[fn.__name__]

class FakeUNet:
    dtype=torch.float32
    def __init__(self):self.inputs=[]
    def __call__(self,x,t,**kwargs):
        self.inputs.append(x.clone())
        eps=torch.zeros_like(x);eps[:1]=.1;eps[1:]=.2
        return (eps,)

class FakeVAE:
    dtype=torch.float32
    config=SimpleNamespace(scaling_factor=.18215)
    def __init__(self,latent=None):self.latent=latent;self.decoded=None
    def decode(self,z,**kwargs):self.decoded=z.clone();return (torch.zeros(1,3,512,512),)
    def encode(self,x):return SimpleNamespace(latent_dist=SimpleNamespace(mode=lambda:self.latent.clone()))

class FakePipe:
    def __init__(self,latent=None):
        self.unet=FakeUNet();self.vae=FakeVAE(latent)
        from diffusers.image_processor import VaeImageProcessor
        self.image_processor=VaeImageProcessor(vae_scale_factor=8)
    def encode_prompt(self,*args,**kwargs):return (torch.ones(1,1,1),torch.zeros(1,1,1))
    def run_safety_checker(self,decoded,*args):return decoded,[False]

class ProgressiveParity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.basis=c.dct_matrix(64)

    def test_gradient_128_normalization_and_exact_coefficient_contraction(self):
        generator=torch.Generator().manual_seed(670)
        x=torch.randn(64,64,generator=generator)
        target,mask=c.target_and_mask(.3,self.basis)
        before=c.dct2(x,self.basis)
        self.assertEqual(int(mask.sum()),128)
        for eta in (25.,100.):
            gradient=c.analytic_gradient(x,target,mask,self.basis)
            after=c.dct2(x-eta*gradient,self.basis)
            expected=(1-2*eta/128)*(before-target)
            self.assertTrue(torch.allclose((after-target)[mask.bool()],expected[mask.bool()],atol=3e-5,rtol=2e-5))
            self.assertTrue(torch.allclose(after[~mask.bool()],before[~mask.bool()],atol=3e-5))
            if eta==100.:self.assertLess(1-2*eta/128,0)

    def test_rearranged_epsilon_recovers_guided_clean_latent(self):
        from diffusers import DDIMScheduler
        scheduler=DDIMScheduler(**DDIM_CONFIG);scheduler.set_timesteps(50)
        self.assertEqual([int(t) for t in scheduler.timesteps[:25]],list(range(981,500,-20)))
        for timestep in (981,501,1):
            a=scheduler.alphas_cumprod[timestep]
            generator=torch.Generator().manual_seed(timestep)
            zt=torch.randn(1,4,64,64,generator=generator);epsilon=torch.randn(zt.shape,generator=generator)
            z0=(zt-(1-a).sqrt()*epsilon)/a.sqrt();target,mask=c.target_and_mask(.3,self.basis)
            guided=z0.clone();guided[0,0]-=25*c.analytic_gradient(z0[0,0],target,mask,self.basis)
            eps=(zt-a.sqrt()*guided)/(1-a).sqrt()
            recovered=(zt-(1-a).sqrt()*eps)/a.sqrt()
            self.assertTrue(torch.allclose(recovered,guided,atol=2e-5,rtol=2e-5))
            self.assertTrue(torch.equal(guided[:,1:],z0[:,1:]))

    def test_actual_generate_body_pairing_guidance_indices_sampler_eta_and_scaling(self):
        from diffusers import DDIMScheduler
        actual=DDIMScheduler;instances=[]
        class Spy(actual):
            def __init__(self,**kwargs):super().__init__(**kwargs);self.noises=[];self.etas=[];self.outputs=[];instances.append(self)
            def step(self,eps,t,latent,**kwargs):
                self.noises.append(eps.clone());self.etas.append(kwargs['eta'])
                result=super().step(eps,t,latent,**kwargs);self.outputs.append(result[0].clone());return result
        generate=cpu_function(c.generate);records=[];pipes=[]
        with mock.patch('diffusers.DDIMScheduler',Spy):
            for alpha,eta in ((0,0),(.3,25.)):
                pipe=FakePipe();pipes.append(pipe)
                _,record=generate(pipe,'procedural fixture prompt',1000,alpha,eta,lambda row:None);records.append(record)
        self.assertTrue(torch.equal(pipes[0].unet.inputs[0],pipes[1].unet.inputs[0]))
        self.assertEqual(records[0]['guided_step_indices'],[]);self.assertEqual(records[1]['guided_step_indices'],list(range(25)))
        baseline=torch.full((1,4,64,64),.85)
        self.assertTrue(torch.allclose(instances[1].noises[25],baseline,atol=1e-6))
        self.assertFalse(torch.allclose(instances[1].noises[0],baseline,atol=1e-6))
        self.assertTrue(all(e==0. for instance in instances for e in instance.etas))
        for pipe,instance in zip(pipes,instances):
            self.assertTrue(torch.equal(pipe.vae.decoded,instance.outputs[-1]/.18215))

    def test_readout_word_does_not_depend_on_reference_or_wrong_hypotheses(self):
        target,_=c.target_and_mask(.3,self.basis);plane=c.idct2(target,self.basis)
        first=c.read_bits(plane,self.basis)
        config=dict(c.CONFIG,payload='0100101110010110',wrong_payload_seed='alternate-fixed-reference')
        with mock.patch.object(c,'CONFIG',config):second=c.read_bits(plane,self.basis)
        self.assertEqual(first['bits'],second['bits']);self.assertEqual(first['bit_accuracy'],1.)
        self.assertEqual(second['bit_accuracy'],0.)

    def test_native_score_scaled_vae_mode_and_no_generation_reference(self):
        import numpy as np
        target,_=c.target_and_mask(.3,self.basis)
        scaled=torch.zeros(1,4,64,64);scaled[0,0]=c.idct2(target,self.basis)
        pipe=FakePipe(scaled/.18215);score=cpu_function(c.score)
        with mock.patch.object(torch.cuda,'synchronize',return_value=None):
            result=score(pipe,np.zeros((512,512,3),dtype=np.uint8))
        self.assertEqual(result['native_vae_dct']['bit_accuracy'],1.)
        self.assertIn('image_dct_diagnostic',result)
        self.assertNotEqual(result['native_vae_dct']['bits'],result['image_dct_diagnostic']['bits'])

    def test_integer_presence_threshold_and_majority_ties(self):
        positions=c.positions();expected=[int(x) for x in c.CONFIG['payload']]
        for matches in (13,14):
            decoded=[b if i<matches else 1-b for i,b in enumerate(expected)]
            coef=torch.zeros(64,64)
            for i,(u,v) in enumerate(positions):coef[u,v]=1. if decoded[i//8] else -1.
            result=c.read_bits(c.idct2(coef,self.basis),self.basis)
            self.assertEqual(result['found_descriptive'],matches==14)
        self.assertEqual(c.read_bits(torch.zeros(64,64),self.basis)['bits'],'0'*16)

    def test_model_failure_retains_all_28_planned_variants(self):
        manifest=c.ROOT/'research/m1-progressive-synthetic.json'
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);output=root/'.thesis-build/dev-runs/injected-failure'
            with mock.patch.object(c,'MAIN',root),mock.patch('three_threat_models.block_network'),mock.patch('three_threat_models.verify_assets',side_effect=RuntimeError('injected pre-model failure')):
                self.assertEqual(c.run(manifest,output),1)
            record=json.loads((output/'run.json').read_text(encoding='utf-8'))
            self.assertEqual(record['outcome'],'failed');self.assertEqual(len(record['planned_ids']),28)
            self.assertEqual(record['incomplete_planned_ids'],record['planned_ids']);self.assertEqual(record['rows'],[])

    def test_subset_manifest_cannot_shrink_fixed_denominator(self):
        manifest=json.loads((c.ROOT/'research/m1-progressive-synthetic.json').read_text(encoding='utf-8'))
        manifest['cases']=manifest['cases'][:1]
        with self.assertRaises(ValueError):c.validate(manifest)

    def test_resume_duplicate_paths_empty_scores_missing_fields_and_nonfinite_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder);path=output/'placeholder.png';path.write_bytes(b'metadata fixture')
            row={'id':'seed1000-a0.3-e25.0','seed':1000,'alpha':.3,'eta':25.,'artifact_prefix':'seed1000-a0.3-e25.0-attempt1','outcome':'completed','control':'C1',
                'conditions':{k:{} for k in ('clean','vae','t3-0.1','t3-0.4')},
                'artifacts':[{'path':path.name,'sha256':c.sha(path)} for _ in range(4)]}
            record={'commit':'fixture','config':c.CONFIG,'planned_ids':c.planned_ids(),'rows':[row,copy.deepcopy(row)]}
            with self.assertRaises(ValueError):c.prepare_resume(record,{'commit':'fixture'},output)
            q={'mse_rgb8':0.,'psnr_db':None,'psnr_infinite':True,'ssim_rgb':1.,'lpips':0.,'clip_cosine':1.}
            read=c.read_bits(torch.zeros(64,64),self.basis)
            condition={'native_vae_dct':read,'image_dct_diagnostic':copy.deepcopy(read),
                'native_vae_dct_seconds':.1,'image_dct_diagnostic_seconds':.1,'extract_both_seconds':.2,'quality_vs_same_arm_clean':q}
            c.validate_condition(condition)
            for field in ('bits','found_descriptive','wrong_payload_queries'):
                bad=copy.deepcopy(condition);del bad['native_vae_dct'][field]
                with self.subTest(field=field),self.assertRaises(ValueError):c.validate_condition(bad)
            for bad_value in (float('nan'),float('inf'),True,None,'1'):
                for group,key in ((None,'native_vae_dct_seconds'),('quality_vs_same_arm_clean','lpips')):
                    bad=copy.deepcopy(condition)
                    if group:bad[group][key]=bad_value
                    else:bad[key]=bad_value
                    with self.subTest(key=key,value=bad_value),self.assertRaises(ValueError):c.validate_condition(bad)
            prefix=row['artifact_prefix'];artifacts=[]
            for name in ('clean','vae','t3-0.1','t3-0.4'):
                path=output/(prefix+'-'+name+'.png');path.write_bytes(name.encode())
                artifacts.append({'path':path.name,'sha256':c.sha(path)})
            row.update(artifacts=artifacts,conditions={k:copy.deepcopy(condition) for k in ('clean','vae','t3-0.1','t3-0.4')},
                quality_to_matched_C0=q,generation={'timesteps':list(range(981,0,-20)),'guided_step_indices':list(range(25)),'safety_flag':False,'scheduler_eta':0.})
            record['rows']=[row];c.prepare_resume(record,{'commit':'fixture'},output)
            for mutation in ('duplicate','missing_score','wrong_member','missing_paired_quality'):
                bad=copy.deepcopy(record)
                if mutation=='duplicate':bad['rows'].append(copy.deepcopy(row))
                elif mutation=='missing_score':del bad['rows'][0]['conditions']['vae']['native_vae_dct']['bits']
                elif mutation=='wrong_member':bad['rows'][0]['artifacts'][0]['path']='placeholder.png'
                else:del bad['rows'][0]['quality_to_matched_C0']
                with self.subTest(mutation=mutation),self.assertRaises(ValueError):c.prepare_resume(bad,{'commit':'fixture'},output)

if __name__=='__main__':unittest.main()
