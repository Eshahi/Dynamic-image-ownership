"""CPU synthetic integration only; no pretrained models, images or science runs."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import m1_progressive_phase as p
import torch
from diffusers import DDIMScheduler
from three_threat_models import DDIM_CONFIG
torch.set_num_threads(1)


class ToyUnet:
    dtype=torch.float16
    def __call__(self,inp,*args,**kwargs):return (inp*.01,)


class ToyVae:
    dtype=torch.float16
    config=SimpleNamespace(scaling_factor=.18215)
    def decode(self,z,**kwargs):return (torch.zeros(1,3,8,8,dtype=torch.float16),)
    def encode(self,x):return SimpleNamespace(latent_dist=SimpleNamespace(mode=lambda:torch.zeros(1,4,64,64,dtype=torch.float16)))


class ToyPipe:
    def __init__(self):
        self.unet=ToyUnet();self.vae=ToyVae()
        self.image_processor=SimpleNamespace(postprocess=lambda *args,**kwargs:['synthetic-placeholder'])
    def encode_prompt(self,*args,**kwargs):return torch.zeros(1,1,1),torch.zeros(1,1,1)
    def run_safety_checker(self,decoded,*args):return decoded,[False]


def old_loop(seed,guided):
    """Literal original DDIM/guidance arithmetic with a synthetic CPU UNet."""
    pipe=ToyPipe();sch=DDIMScheduler(**DDIM_CONFIG);sch.set_timesteps(50)
    z=torch.randn((1,4,64,64),generator=torch.Generator().manual_seed(seed),dtype=torch.float16)*sch.init_noise_sigma
    basis=p.original.dct_matrix(64);targ,mask=p.original.target_and_mask(.5,basis)
    for i,t in enumerate(sch.timesteps):
        out=pipe.unet(sch.scale_model_input(torch.cat([z,z]),t))[0];u,c=out.chunk(2);eps=u+7.5*(c-u)
        if guided and i<25:
            a=sch.alphas_cumprod[int(t)].float();z0=(z.float()-(1-a).sqrt()*eps.float())/a.sqrt()
            grad=p.original.analytic_gradient(z0[0,0],targ,mask,basis);corrected=z0.clone();corrected[0,0]-=100.*grad
            eps=((z.float()-a.sqrt()*corrected)/(1-a).sqrt()).to(torch.float16)
        z=sch.step(eps,t,z,eta=0.,return_dict=False)[0]
    return z


class PhaseTests(unittest.TestCase):
    def test_frozen_manifest_inventory(self):
        manifest=json.loads((ROOT/'research/m1-progressive-phase-dev.json').read_text())
        self.assertEqual(manifest,p.configuration());rows=p.planned()
        self.assertEqual(len(rows),16);self.assertEqual(len({r['id'] for r in rows}),16)
        self.assertEqual(sum(len(r['conditions']) for r in rows),32)
        self.assertEqual(p.guided_indices('C0-replay'),[])
        self.assertEqual(p.guided_indices('C-E100-replay'),list(range(25)))
        self.assertEqual(p.guided_indices('C-L100'),list(range(25,50)))
        self.assertEqual(p.guided_indices('C-L100-complement'),list(range(25,50)))

    def test_target_complement_and_reference_free_extraction(self):
        basis=p.original.dct_matrix(64);a,mask=p.target(.5,basis,p.ORIGINAL);b,other=p.target(.5,basis,p.COMPLEMENT)
        self.assertTrue(torch.equal(a,-b));self.assertTrue(torch.equal(mask,other));self.assertEqual(int(mask.sum()),128)
        plane=p.original.idct2(a,basis)
        own=p.stage(plane,basis,p.ORIGINAL);inverse=p.stage(plane,basis,p.COMPLEMENT)
        self.assertEqual(own['bits'],inverse['bits']);self.assertEqual(own['bits'],p.ORIGINAL)
        self.assertEqual(own['intended_matches'],16);self.assertEqual(inverse['intended_matches'],0)
        self.assertEqual(own['wrong_payload_queries'],inverse['wrong_payload_queries'])
        self.assertNotIn(p.COMPLEMENT,p.original.wrong_payloads())

    def test_threshold_boundaries(self):
        for errors,want in ((2,True),(3,False)):
            word=''.join(('1' if b=='0' else '0') if i<errors else b for i,b in enumerate(p.ORIGINAL))
            self.assertEqual(p.evaluate_word(word,p.ORIGINAL)['intended_present'],want)

    def test_scheduler_q_final_alpha(self):
        scheduler=DDIMScheduler(**DDIM_CONFIG);scheduler.set_timesteps(50)
        values=[p.ddim_factors(scheduler,t)[2] for t in (981,501,481,21,1)]
        for got,want in zip(values,(.009393912,.035377406,.036744273,.707346467,.293886832)):
            self.assertAlmostEqual(got,want,places=6)
        self.assertEqual(p.ddim_factors(scheduler,1)[1],float(scheduler.alphas_cumprod[0]))

    def test_instrumented_cpu_replay_parity_and_full_traces(self):
        original_hash=p.sha(ROOT/'scripts/m1_progressive_latent.py');initials=[]
        for arm in p.ARMS:
            arrays={};traces=[]
            def save(name,value):
                arrays[name]=value.clone();return {'raw_sha256':hashlib.sha256(value.numpy().tobytes()).hexdigest()}
            image,result=p.generate(ToyPipe(),dict(seed=1000,prompt='synthetic'),arm,
                p.COMPLEMENT if arm.endswith('complement') else p.ORIGINAL,save,traces.append,lambda:None,device='cpu')
            initials.append(arrays['initial_latent'])
            self.assertEqual(len(traces),50);self.assertEqual([r['step_index'] for r in traces],list(range(50)))
            self.assertEqual([r['step_index'] for r in traces if r['guided']],p.guided_indices(arm))
            self.assertEqual(set(result['readout_stages']),set(p.STAGES[:2]))
            for trace in traces:
                self.assertEqual(set(trace['stages']),{'ordinary_predicted_clean','corrected_predicted_clean',
                    'effective_fp16_predicted_clean','actual_noisy_scheduler_output'})
                self.assertTrue(all(len(s['selected_coefficients'])==128 for s in trace['stages'].values()))
                self.assertEqual(trace['changed_other_channels_count'],0)
                json.dumps(trace,allow_nan=False)
            if arm in p.ARMS[:2]:self.assertTrue(torch.equal(arrays['terminal_latent'],old_loop(1000,arm=='C-E100-replay')))
            self.assertFalse(result['readout_stages']['terminal_predecode']['eligible_image_detector'])
        self.assertTrue(all(torch.equal(initials[0],z) for z in initials[1:]))
        self.assertEqual(p.sha(ROOT/'scripts/m1_progressive_latent.py'),original_hash)

    def test_replay_mismatch_not_success(self):
        value=p.replay_status('a','b');self.assertFalse(value['matched'])
        self.assertEqual(value['attribution'],'replay-attribution-failure');self.assertIsNone(value['original_latent_hash'])

    def test_incomplete_gates_null(self):
        values=p.gates(p.planned());self.assertFalse(values['complete'])
        self.assertIsNone(values['late_carrier']);self.assertIsNone(values['late_quality'])

    def test_joint_gates_preserve_one_failure_and_replay_attribution(self):
        rows=p.planned()
        null_word=''.join(('1' if b=='0' else '0') if i<8 else b for i,b in enumerate(p.ORIGINAL))
        for row in rows:
            row['outcome']='completed';row['quality_to_new_C0']={'quality_admissible':True}
            word=null_word if row['arm']=='C0-replay' else row['intended_payload']
            for value in row['conditions'].values():
                value.update(outcome='completed',native_vae_dct=p.evaluate_word(word,row['intended_payload']))
                if row['arm'] in p.ARMS[:2]:value['replay']={'matched':True}
        self.assertTrue(p.gates(rows)['necessary_condition']);self.assertTrue(p.gates(rows)['quality_attribution'])
        rows[-1]['conditions']['vae']['native_vae_dct']['intended_present']=False
        self.assertFalse(p.gates(rows)['late_carrier']);self.assertFalse(p.gates(rows)['necessary_condition'])
        rows[-1]['conditions']['vae']['native_vae_dct']['intended_present']=True
        rows[0]['conditions']['clean']['replay']['matched']=False
        self.assertIsNone(p.gates(rows)['necessary_condition']);self.assertIsNone(p.gates(rows)['quality_attribution'])
        self.assertTrue(p.gates(rows)['late_carrier'])
        del rows[0]['conditions']['vae']
        self.assertIsNone(p.gates(rows)['late_carrier'])

    def test_interrupt_pre_model_retains_all_inventory(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(p,'MAIN',Path(tmp)),patch.object(p,'require_committed',side_effect=KeyboardInterrupt):
            output=Path(tmp)/'.thesis-build/dev-runs/fixture'
            self.assertEqual(p.run(ROOT/'research/m1-progressive-phase-dev.json',output),1)
            record=json.loads((output/'run.json').read_text())
            self.assertEqual(record['outcome'],'interrupted');self.assertEqual(len(record['incomplete_planned_ids']),16)
            self.assertEqual(len(record['missing_image_conditions']),32)
            self.assertEqual(len(json.loads((output/'conditions.json').read_text())),32)
            self.assertIsNone(record['gates']['late_carrier'])


if __name__=='__main__':unittest.main()
