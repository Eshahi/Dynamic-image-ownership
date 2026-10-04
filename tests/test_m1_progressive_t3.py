"""CPU/receipt tests only. No pretrained inference, GPU or source-output mutation."""
import copy
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import m1_progressive_t3 as p
import torch
import numpy as np
from PIL import Image
from diffusers import DDIMScheduler,StableDiffusionImg2ImgPipeline
from three_threat_models import DDIM_CONFIG

MANIFEST=ROOT/'research/m1-progressive-t3-dev.json'


def complete_rows():
    rows=p.planned()
    null=''.join(('0' if b=='1' else '1') if i<8 else b for i,b in enumerate(p.parent.ORIGINAL))
    for row in rows:
        word=null if row['arm']=='C0-replay' else row['intended_payload']
        row.update(outcome='completed',actual_timesteps=row['expected_timesteps'][:],
            unet_calls=len(row['expected_timesteps']),readout={'native_vae_dct':{'bits':word}})
    return rows


class T3Tests(unittest.TestCase):
    def test_actual_prepared_manifest_readonly_source_gate(self):
        cfg=json.loads(MANIFEST.read_text());folder=Path(cfg['source_dir'])
        before=p.sha(folder/'run.json')
        snapshot=p.source_snapshot(folder,cfg['source_run_sha256'])
        self.assertEqual(cfg,p.configuration(snapshot));self.assertEqual(before,p.sha(folder/'run.json'))
        self.assertEqual(len(snapshot['inputs']),12);self.assertEqual(len(snapshot['source_artifact_receipts']),160)
        self.assertEqual(snapshot['source_gate']['promoted_operator'],'C-Q5M5')
        self.assertEqual(len(p.planned()),24);self.assertEqual(sum(len(r['expected_timesteps']) for r in p.planned()),120)
        self.assertEqual({r['attack_seed'] for r in p.planned()},{0})

    def test_real_scheduler_and_img2img_step_selection(self):
        scheduler=DDIMScheduler(**DDIM_CONFIG);scheduler.set_timesteps(20)
        dummy=SimpleNamespace(scheduler=scheduler)
        for strength in p.STRENGTHS:
            timesteps,count=StableDiffusionImg2ImgPipeline.get_timesteps(dummy,20,strength,'cpu')
            self.assertEqual(timesteps.tolist(),p.expected_timesteps(strength))
            self.assertEqual(count,2 if strength==.1 else 8)
        with self.assertRaises(ValueError):p.expected_timesteps(.2)

    def test_all_eight_each_strength_and_both_null_words(self):
        rows=complete_rows();self.assertTrue(p.gates(rows)['joint_pass'])
        row=next(r for r in rows if r['arm']=='C-Q5M5-complement' and r['strength']==.4)
        word=row['intended_payload']
        for errors,expected in ((2,True),(3,False)):
            row['readout']['native_vae_dct']['bits']=''.join(('0' if b=='1' else '1') if i<errors else b for i,b in enumerate(word))
            gate=p.gates(rows);self.assertEqual(gate['joint_pass'],expected)
            self.assertTrue(gate['by_strength']['0.1']['pass_gate'])
        for word in (p.parent.ORIGINAL,p.parent.COMPLEMENT):
            rows=complete_rows();rows[0]['readout']['native_vae_dct']['bits']=word
            self.assertFalse(p.gates(rows)['joint_pass'])
        for altered in (complete_rows()[:-1],complete_rows()+[complete_rows()[-1]],p.planned()):
            self.assertFalse(p.gates(altered)['complete'])
        rows=complete_rows();rows[-1]['actual_timesteps']=[1]
        self.assertFalse(p.gates(rows)['complete'])

    def test_raw_word_and_nonfinite_rejection(self):
        payload=p.parent.ORIGINAL
        stage=dict(bits=payload,selected_coefficients=[.5 if b=='1' else -.5 for b in payload for _ in range(8)])
        self.assertEqual(p.word_from_coefficients(stage),payload)
        stage['bits']=p.parent.COMPLEMENT
        with self.assertRaises(ValueError):p.word_from_coefficients(stage)
        stage['bits']=payload;stage['selected_coefficients'][0]=float('nan')
        with self.assertRaises(ValueError):p.word_from_coefficients(stage)

    def test_gate_failure_refuses_manifest_before_artifact_access(self):
        cfg=json.loads(MANIFEST.read_text());source=json.loads((Path(cfg['source_dir'])/'run.json').read_text())
        with tempfile.TemporaryDirectory() as temp,patch.object(p,'MAIN',Path(temp)):
            folder=Path(temp)/'.thesis-build/dev-runs/source';folder.mkdir(parents=True)
            output=Path(temp)/'manifest.json'
            mutations=[]
            bad=copy.deepcopy(source);bad['outcome']='started';mutations.append(bad)
            bad=copy.deepcopy(source);bad['rows'].pop();mutations.append(bad)
            bad=copy.deepcopy(source);bad['rows'][-1]['quality_to_new_C0']['psnr_db']=35.;mutations.append(bad)
            bad=copy.deepcopy(source);bad['rows'][0]['conditions']['clean']['replay']['matched']=False;mutations.append(bad)
            bad=copy.deepcopy(source);bad['rows'][-1]['conditions']['vae']['native_vae_dct']['bits']='0'*16;mutations.append(bad)
            for bad in mutations:
                (folder/'run.json').write_text(json.dumps(bad))
                with patch.object(p,'checked_artifact') as check:
                    with self.assertRaises(ValueError):p.prepare(folder,output)
                    check.assert_not_called()
                self.assertFalse(output.exists())

    def test_source_hash_and_asset_artifact_corruption(self):
        cfg=json.loads(MANIFEST.read_text())
        with self.assertRaises(ValueError):p.source_snapshot(cfg['source_dir'],'0'*64)
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp);path=folder/'fixture.png';path.write_bytes(b'fixture')
            receipt=dict(path=path.name,sha256=p.sha(path),bytes=path.stat().st_size)
            self.assertEqual(p.checked_artifact(folder,receipt),path)
            path.write_bytes(b'broken!')
            with self.assertRaises(ValueError):p.checked_artifact(folder,receipt)
            path.unlink()
            with self.assertRaises(ValueError):p.checked_artifact(folder,receipt)
            with self.assertRaises(ValueError):p.checked_artifact(folder,{**receipt,'path':'../escape.png'})

    def test_attack_kwargs_fresh_scheduler_callbacks_and_counts(self):
        class Unet:
            def register_forward_pre_hook(self,hook):
                self.hook=hook;self.removed=False
                return SimpleNamespace(remove=lambda:setattr(self,'removed',True))
        class Attack:
            def __init__(self):self.unet=Unet();self.schedulers=[];self.calls=[];self.extra=False
            def __call__(self,**kwargs):
                self.calls.append(kwargs);self.schedulers.append(self.scheduler)
                self.scheduler.set_timesteps(20)
                timesteps,_=StableDiffusionImg2ImgPipeline.get_timesteps(self,20,kwargs['strength'],'cpu')
                values=timesteps.tolist()+([1] if self.extra else [])
                for index,timestep in enumerate(values):
                    self.unet.hook(self.unet,(None,timestep))
                    kwargs['callback_on_step_end'](self,index,timestep,{})
                return SimpleNamespace(images=[Image.new('RGB',(512,512))],nsfw_content_detected=[False])
        seeds=[]
        def generator(**kwargs):
            self.assertEqual(kwargs,{'device':'cuda'})
            return SimpleNamespace(manual_seed=lambda seed:seeds.append(seed) or 'fixed-generator')
        attack=Attack();rgb=np.zeros((512,512,3),dtype=np.uint8)
        with patch.object(torch,'Generator',side_effect=generator):
            for strength in p.STRENGTHS:
                progress={};_,times,calls=p.attack_one(attack,rgb,strength,lambda:None,progress)
                self.assertEqual(times,p.expected_timesteps(strength));self.assertEqual(calls,len(times))
                self.assertEqual(progress['unet_timesteps'],times);self.assertTrue(attack.unet.removed)
            self.assertIsNot(attack.schedulers[0],attack.schedulers[1]);self.assertEqual(seeds,[0,0])
            for call in attack.calls:
                self.assertEqual(call['prompt'],'');self.assertEqual(call['negative_prompt'],'')
                self.assertEqual(call['guidance_scale'],1.);self.assertEqual(call['eta'],0.);self.assertEqual(call['num_inference_steps'],20)
            attack.extra=True;progress={}
            with self.assertRaises(ValueError):p.attack_one(attack,rgb,.1,lambda:None,progress)
            self.assertEqual(len(progress['unet_timesteps']),3);self.assertTrue(attack.unet.removed)

    def test_failed_source_run_retains_all24_before_gpu_loading(self):
        with tempfile.TemporaryDirectory() as temp,patch.object(p,'MAIN',Path(temp)),patch.object(p,'source_snapshot',side_effect=ValueError('source gate failed')):
            output=Path(temp)/'.thesis-build/dev-runs/t3'
            with patch('three_threat_models.block_network') as before_models:
                self.assertEqual(p.run(MANIFEST,output),1);before_models.assert_not_called()
            record=json.loads((output/'run.json').read_text())
            self.assertEqual(record['outcome'],'failed');self.assertEqual(len(record['missing_condition_ids']),24)
            self.assertEqual(record['observed_unet_calls'],0);self.assertIsNone(record['gates']['joint_pass'])
            with self.assertRaises(FileExistsError):p.run(MANIFEST,output)


if __name__=='__main__':unittest.main()
