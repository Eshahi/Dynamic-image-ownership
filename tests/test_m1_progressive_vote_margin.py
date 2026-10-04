"""CPU synthetic tests only: no model loading, CUDA or scientific image generation."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import m1_progressive_vote_margin as p
import torch
from test_m1_progressive_phase import ToyPipe
torch.set_num_threads(1)


def completed_rows():
    rows=p.planned()
    null=''.join(('1' if b=='0' else '0') if i<8 else b for i,b in enumerate(p.ORIGINAL))
    for r in rows:
        r['outcome']='completed'
        r['quality_to_new_C0']=dict(psnr_db=36.,psnr_infinite=False,ssim_rgb=.95,lpips=.05)
        for v in r['conditions'].values():
            v.update(outcome='completed',native_vae_dct=p.evaluate_word(null if r['arm']=='C0-replay' else r['intended_payload'],r['intended_payload']))
            if r['arm'] in p.ARMS[:2]:v['replay']={'matched':True}
    return rows


class VoteMarginTests(unittest.TestCase):
    def test_manifest_inventory_and_window(self):
        self.assertEqual(json.loads((ROOT/'research/m1-progressive-vote-margin-dev.json').read_text()),p.configuration())
        self.assertEqual(len(p.planned()),24)
        self.assertEqual(sum(len(r['conditions']) for r in p.planned()),48)
        self.assertEqual(p.guided_indices('C0-replay'),[])
        self.assertEqual(p.guided_indices('C-L100-replay'),list(range(25,50)))
        for arm in p.ARMS[2:]:self.assertEqual(p.guided_indices(arm),list(range(45,50)))
        with self.assertRaises(ValueError):p.guided_indices('unknown')

    def test_five_selection_stable_ties_and_overshoot(self):
        c=torch.zeros(128,dtype=torch.float64)
        g,info=p.coefficient_objective(c,p.ORIGINAL,'five-vote-margin')
        self.assertEqual(info['selected_local_indices'],[list(range(5))]*16)
        self.assertEqual(info['active_coordinate_count'],80)
        self.assertTrue(torch.equal(g.reshape(16,8)[:,5:],torch.zeros(16,3,dtype=c.dtype)))
        y=c.new_tensor([1 if b=='1' else -1 for b in p.ORIGINAL]).repeat_interleave(8)
        after=y*(c-100*g)
        self.assertTrue(torch.allclose(after.reshape(16,8)[:,:5],torch.full((16,5),.46875,dtype=c.dtype)))
        _,other=p.coefficient_objective(c,p.COMPLEMENT,'five-vote-margin')
        og,_=p.coefficient_objective(c,p.COMPLEMENT,'five-vote-margin')
        self.assertTrue(torch.equal(g,-og));self.assertEqual(info['selected_local_indices'],other['selected_local_indices'])

    def test_satisfied_and_unselected_coordinates_untouched(self):
        signed=torch.tensor([.5,.4,.31,.3,.2,-.2,-.4,-.8],dtype=torch.float64).repeat(16)
        y=torch.tensor([1 if b=='1' else -1 for b in p.ORIGINAL],dtype=torch.float64).repeat_interleave(8)
        g,info=p.coefficient_objective(y*signed,p.ORIGINAL,'five-vote-margin')
        self.assertEqual(info['selected_local_indices'],[list(range(5))]*16)
        self.assertEqual(info['signed_margin_counts'],[4]*16)
        self.assertEqual(int((g!=0).sum()),16)
        self.assertTrue(torch.all(g.reshape(16,8)[:,4]!=0))

    def test_piecewise_gradient_finite_difference(self):
        c=torch.linspace(-.913,.877,128,dtype=torch.float64)
        for kind in ('equality','five-vote-margin'):
            grad,_=p.coefficient_objective(c,p.ORIGINAL,kind)
            for j in (0,4,7,31,67,95,127):
                plus=c.clone();minus=c.clone();plus[j]+=1e-6;minus[j]-=1e-6
                _,a=p.coefficient_objective(plus,p.ORIGINAL,kind)
                _,b=p.coefficient_objective(minus,p.ORIGINAL,kind)
                self.assertAlmostEqual(float(grad[j]),(a['objective_value']-b['objective_value'])/2e-6,places=8)

    def test_spatial_adjoint_and_reader_independent_of_payload(self):
        basis=p.original.dct_matrix(64)
        plane=torch.randn(64,64,generator=torch.Generator().manual_seed(813))
        grad,info=p.objective_gradient(plane,basis,p.ORIGINAL,'five-vote-margin')
        coeff=p.original.dct2(plane,basis)[tuple(zip(*p.original.positions()))]
        cg,_=p.coefficient_objective(coeff,p.ORIGINAL,'five-vote-margin')
        recovered=p.original.dct2(grad,basis)
        self.assertTrue(torch.allclose(recovered[tuple(zip(*p.original.positions()))],cg,atol=2e-7))
        a=p.stage(plane,basis,p.ORIGINAL,.3);b=p.stage(plane,basis,p.COMPLEMENT,.3)
        self.assertEqual(a['bits'],b['bits']);self.assertEqual(a['wrong_payload_queries'],b['wrong_payload_queries'])
        self.assertNotIn('selected_local_indices',a)

    def test_control_replay_and_all_trace_rows(self):
        paths=[ROOT/'scripts/m1_progressive_phase.py',ROOT/'scripts/m1_progressive_latent.py']
        hashes=[p.sha(path) for path in paths];initials=[]
        for arm in p.ARMS:
            arrays={};traces=[]
            def save(name,value):
                arrays[name]=value.clone();return {'raw_sha256':hashlib.sha256(value.numpy().tobytes()).hexdigest()}
            payload=p.COMPLEMENT if arm.endswith('complement') else p.ORIGINAL
            _,result=p.generate(ToyPipe(),dict(seed=1000,prompt='synthetic'),arm,payload,save,traces.append,lambda:None,device='cpu')
            initials.append(arrays['initial_latent'])
            self.assertEqual(len(traces),50)
            self.assertEqual([r['step_index'] for r in traces if r['guided']],p.guided_indices(arm))
            self.assertEqual(set(result['readout_stages']),set(p.STAGES[:2]))
            self.assertFalse(result['readout_stages']['terminal_predecode']['eligible_image_detector'])
            for row in traces:
                self.assertEqual(len(row['stages']),4)
                self.assertTrue(all(len(v['selected_coefficients'])==128 for v in row['stages'].values()))
                self.assertEqual(row['objective'] is not None,row['guided'])
                if row['guided']:
                    self.assertEqual(row['objective']['active_coordinate_count'],80 if arm.startswith('C-Q5') else 128)
                    self.assertIn('after_intended_update',row['objective'])
                json.dumps(row,allow_nan=False)
            if arm in p.ARMS[:2]:
                old={}
                def retain(name,value):old[name]=value.clone();return {'raw_sha256':'fixture'}
                p.phase.generate(ToyPipe(),dict(seed=1000,prompt='synthetic'),
                    'C0-replay' if arm=='C0-replay' else 'C-L100',payload,retain,lambda _:None,lambda:None,device='cpu')
                self.assertTrue(torch.equal(arrays['terminal_latent'],old['terminal_latent']))
        self.assertTrue(all(torch.equal(initials[0],v) for v in initials[1:]))
        self.assertEqual(hashes,[p.sha(path) for path in paths])

    def test_strict_quality_boundaries_and_nonfinite(self):
        baseline=dict(psnr_db=36.,psnr_infinite=False,ssim_rgb=.95,lpips=.05)
        self.assertTrue(p.quality_pass(baseline))
        for key,value in [('psnr_db',35.),('ssim_rgb',.9),('lpips',.1),('lpips',float('nan')),('ssim_rgb',float('inf'))]:
            self.assertFalse(p.quality_pass({**baseline,key:value}))
        self.assertTrue(p.quality_pass({**baseline,'psnr_db':None,'psnr_infinite':True}))

    def test_all_eight_gates_and_prospective_priority(self):
        rows=completed_rows();gate=p.gates(rows)
        self.assertEqual(gate['promoted_operator'],'C-Q5')
        r=next(r for r in rows if r['arm']=='C-Q5-complement')
        original=r['conditions']['vae']['native_vae_dct']['bits']
        for errors,expected in ((2,'C-Q5'),(3,'C-EQ5')):
            word=''.join(('0' if b=='1' else '1') if i<errors else b for i,b in enumerate(original))
            r['conditions']['vae']['native_vae_dct']['bits']=word
            self.assertEqual(p.gates(rows)['promoted_operator'],expected)
        r['conditions']['vae']['native_vae_dct']['bits']=original
        r['quality_to_new_C0']['psnr_db']=35.
        self.assertEqual(p.gates(rows)['promoted_operator'],'C-EQ5')
        next(r for r in rows if r['arm']=='C-EQ5')['quality_to_new_C0']['lpips']=.1
        self.assertIsNone(p.gates(rows)['promoted_operator'])

    def test_null_replay_and_invalid_inventory(self):
        rows=completed_rows();rows[0]['conditions']['clean']['replay']['matched']=False
        gate=p.gates(rows)
        self.assertIsNone(gate['operators']['C-Q5']['eligible_for_t3'])
        self.assertIsNone(gate['promoted_operator'])
        rows=completed_rows();rows[0]['conditions']['clean']['native_vae_dct']['bits']=p.COMPLEMENT
        self.assertFalse(p.gates(rows)['c0_absence']);self.assertIsNone(p.gates(rows)['promoted_operator'])
        for mutated in (rows[:-1],rows+[rows[-1]],p.planned()):
            self.assertFalse(p.gates(mutated)['complete'])
        rows=completed_rows();rows[-1]['intended_payload']=p.ORIGINAL
        self.assertFalse(p.gates(rows)['complete'])

    def test_interrupt_inventory_before_models(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(p,'MAIN',Path(tmp)),patch.object(p,'require_committed',side_effect=KeyboardInterrupt):
            output=Path(tmp)/'.thesis-build/dev-runs/fixture'
            self.assertEqual(p.run(ROOT/'research/m1-progressive-vote-margin-dev.json',output),1)
            record=json.loads((output/'run.json').read_text())
            self.assertEqual(record['outcome'],'interrupted')
            self.assertEqual(record['planned_counts']['unet_calls'],1200)
            self.assertEqual(len(record['incomplete_planned_ids']),24)
            self.assertEqual(len(record['missing_image_conditions']),48)
            self.assertEqual(len(json.loads((output/'conditions.json').read_text())),48)
            with self.assertRaises(FileExistsError):p.run(ROOT/'research/m1-progressive-vote-margin-dev.json',output)


if __name__=='__main__':unittest.main()
