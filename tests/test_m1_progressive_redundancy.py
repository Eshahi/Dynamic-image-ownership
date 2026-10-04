"""CPU fixtures for the one fixed .5 margin amendment; no model/CUDA inference."""
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
import m1_progressive_redundancy as p
import torch
from test_m1_progressive_phase import ToyPipe
from test_m1_progressive_vote_margin import completed_rows as previous_completed_rows
torch.set_num_threads(1)


def completed_rows():
    rows=p.planned()
    null=''.join(('1' if b=='0' else '0') if i<8 else b for i,b in enumerate(p.ORIGINAL))
    for row in rows:
        row['outcome']='completed'
        row['quality_to_new_C0']=dict(psnr_db=36.,psnr_infinite=False,ssim_rgb=.95,lpips=.05)
        for value in row['conditions'].values():
            value.update(outcome='completed',native_vae_dct=p.evaluate_word(
                null if row['arm']=='C0-replay' else row['intended_payload'],row['intended_payload']))
            if row['arm'] in p.REPLAYS:value['replay']={'matched':True}
    return rows


class RedundancyTests(unittest.TestCase):
    def test_frozen_manifest_inventory_and_margins(self):
        self.assertEqual(json.loads((ROOT/'research/m1-progressive-redundancy-dev.json').read_text()),p.configuration())
        self.assertEqual(len(p.planned()),20)
        self.assertEqual(sum(len(r['conditions']) for r in p.planned()),40)
        self.assertEqual(sum(2 for r in p.planned() if r['arm'] in p.REPLAYS),24)
        for arm in p.ARMS:
            self.assertEqual(p.guided_indices(arm),[] if arm=='C0-replay' else list(range(45,50)))
            self.assertEqual(p.arm_alpha(arm),.3 if arm in p.ARMS[1:3] else .5)
        self.assertIs(p.objective_gradient,p.previous.objective_gradient)
        self.assertIs(p.coefficient_objective,p.previous.coefficient_objective)

    def test_point_five_ties_satisfied_entries_and_eta(self):
        c=torch.zeros(128,dtype=torch.float64)
        grad,meta=p.coefficient_objective(c,p.ORIGINAL,'five-vote-margin',.5)
        self.assertEqual(meta['selected_local_indices'],[list(range(5))]*16)
        self.assertEqual(meta['active_coordinate_count'],80)
        signed=torch.tensor([1 if b=='1' else -1 for b in p.ORIGINAL],dtype=c.dtype).repeat_interleave(8)
        self.assertTrue(torch.allclose((signed*(-100*grad)).reshape(16,8)[:,:5],torch.full((16,5),.78125,dtype=c.dtype)))
        cg,_=p.coefficient_objective(c,p.COMPLEMENT,'five-vote-margin',.5)
        self.assertTrue(torch.equal(grad,-cg))
        satisfied=signed*torch.tensor([.8,.7,.6,.5,.4,-.1,-.2,-.3],dtype=c.dtype).repeat(16)
        grad,_=p.coefficient_objective(satisfied,p.ORIGINAL,'five-vote-margin',.5)
        self.assertEqual(int((grad!=0).sum()),16)
        self.assertTrue(torch.all(grad.reshape(16,8)[:,4]!=0))

    def test_gradient_away_from_piecewise_boundaries(self):
        c=torch.linspace(-1.137,1.071,128,dtype=torch.float64)
        grad,_=p.coefficient_objective(c,p.ORIGINAL,'five-vote-margin',.5)
        for index in (0,4,7,35,63,91,127):
            a=c.clone();b=c.clone();a[index]+=1e-6;b[index]-=1e-6
            _,pa=p.coefficient_objective(a,p.ORIGINAL,'five-vote-margin',.5)
            _,pb=p.coefficient_objective(b,p.ORIGINAL,'five-vote-margin',.5)
            self.assertAlmostEqual(float(grad[index]),(pa['objective_value']-pb['objective_value'])/2e-6,places=8)

    def test_same_reader_independent_of_margin_payload_and_groups(self):
        plane=torch.randn(64,64,generator=torch.Generator().manual_seed(804))
        basis=p.original.dct_matrix(64)
        values=[p.stage(plane,basis,word,margin) for word in (p.ORIGINAL,p.COMPLEMENT) for margin in (.3,.5)]
        self.assertEqual(len({v['bits'] for v in values}),1)
        self.assertTrue(all(v['wrong_payload_queries']==values[0]['wrong_payload_queries'] for v in values))
        self.assertTrue(all(len(v['groups'])==16 for v in values))
        for value in values:
            for group in value['groups']:
                index=group['bit_index'];coeff=value['selected_coefficients'][8*index:8*index+8]
                self.assertEqual(group['positive_votes'],sum(x>0 for x in coeff))
            self.assertNotIn('selected_local_indices',value)

    def test_exact_replay_all_three_arms_and_full_candidate_trace(self):
        oldpaths=[ROOT/'scripts/m1_progressive_vote_margin.py',ROOT/'scripts/m1_progressive_phase.py',ROOT/'scripts/m1_progressive_latent.py']
        hashes=[p.sha(path) for path in oldpaths];initials=[]
        for arm in p.ARMS:
            arrays={};traces=[]
            def save(name,value):
                arrays[name]=value.clone();return {'raw_sha256':hashlib.sha256(value.numpy().tobytes()).hexdigest()}
            intended=p.COMPLEMENT if arm.endswith('complement') else p.ORIGINAL
            _,result=p.generate(ToyPipe(),dict(seed=1001,prompt='synthetic'),arm,intended,save,traces.append,lambda:None,device='cpu')
            initials.append(arrays['initial_latent']);self.assertEqual(len(traces),50)
            self.assertEqual(result['unet_calls'],50)
            self.assertEqual(result['embedding_margin'],None if arm=='C0-replay' else p.arm_alpha(arm))
            self.assertEqual(result['reference_target_amplitude'],p.arm_alpha(arm))
            self.assertEqual([v['step_index'] for v in traces if v['guided']],p.guided_indices(arm))
            for tr in traces:
                self.assertEqual(len(tr['stages']),4)
                self.assertTrue(all(len(stage['groups'])==16 and len(stage['selected_coefficients'])==128 for stage in tr['stages'].values()))
                if tr['guided']:
                    self.assertEqual(tr['objective']['margin'],p.arm_alpha(arm))
                    self.assertEqual(tr['objective']['active_coordinate_count'],80)
                json.dumps(tr,allow_nan=False)
            if arm in p.REPLAYS:
                old={}
                def retain(name,value):old[name]=value.clone();return {'raw_sha256':'fixture'}
                p.previous.generate(ToyPipe(),dict(seed=1001,prompt='synthetic'),p.REPLAYS[arm],intended,retain,lambda _:None,lambda:None,device='cpu')
                self.assertTrue(torch.equal(arrays['terminal_latent'],old['terminal_latent']))
        self.assertTrue(all(torch.equal(initials[0],value) for value in initials))
        self.assertEqual(hashes,[p.sha(path) for path in oldpaths])

    def test_all_eight_gate_no_average_and_no_stale_boolean(self):
        rows=completed_rows();self.assertEqual(p.gates(rows)['promoted_operator'],'C-Q5M5')
        row=rows[-1];word=row['intended_payload']
        for errors,expected in ((2,'C-Q5M5'),(3,None)):
            row['conditions']['vae']['native_vae_dct']['bits']=''.join(('0' if b=='1' else '1') if i<errors else b for i,b in enumerate(word))
            self.assertEqual(p.gates(rows)['promoted_operator'],expected)
        rows=completed_rows();rows[-1]['quality_to_new_C0']['psnr_db']=35.
        self.assertIsNone(p.gates(rows)['promoted_operator'])
        for key,value in [('psnr_db',35.),('ssim_rgb',.9),('lpips',.1),('lpips',float('nan'))]:
            self.assertFalse(p.quality_pass({**completed_rows()[-1]['quality_to_new_C0'],key:value}))

    def test_c0_both_words_replay_and_inventory_failures(self):
        rows=completed_rows();rows[2]['conditions']['vae']['replay']['matched']=False
        gate=p.gates(rows);self.assertIsNone(gate['operators']['C-Q5M5']['eligible_for_t3'])
        for word in (p.ORIGINAL,p.COMPLEMENT):
            rows=completed_rows();rows[0]['conditions']['clean']['native_vae_dct']['bits']=word
            self.assertFalse(p.gates(rows)['c0_absence']);self.assertIsNone(p.gates(rows)['promoted_operator'])
        for rows in (p.planned(),completed_rows()[:-1],completed_rows()+[completed_rows()[-1]]):
            self.assertFalse(p.gates(rows)['complete'])
        rows=completed_rows();rows[-1]['intended_payload']=p.ORIGINAL
        self.assertFalse(p.gates(rows)['complete'])

    def test_exact_source_hash_24_receipts_missing_corruption_readonly(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp);rows=previous_completed_rows()
            for row in rows:
                if row['arm'] not in p.REPLAYS.values():continue
                for channel,value in row['conditions'].items():
                    path=folder/(row['id']+'-'+channel+'.png');path.write_bytes((row['id']+channel).encode())
                    value['artifact']=dict(path=path.name,sha256=p.sha(path),bytes=path.stat().st_size)
            source=dict(outcome='completed',schema_version=p.previous.VERSION,config=p.previous.configuration(),rows=rows,gates=p.previous.gates(rows))
            run=folder/'run.json';run.write_text(json.dumps(source));original_bytes=run.read_bytes()
            with patch.object(p,'SOURCE',folder),patch.object(p,'SOURCE_SHA',p.sha(run)):
                self.assertEqual(len(p.source_receipts()),24);self.assertEqual(run.read_bytes(),original_bytes)
                path=folder/rows[0]['conditions']['clean']['artifact']['path'];original_png=path.read_bytes()
                path.write_bytes(b'corrupt')
                with self.assertRaises(ValueError):p.source_receipts()
                path.write_bytes(original_png);path.unlink()
                with self.assertRaises(ValueError):p.source_receipts()
                path.write_bytes(original_png)
                with patch.object(p,'SOURCE_SHA','0'*64):
                    with self.assertRaises(ValueError):p.source_receipts()
                broken=copy.deepcopy(source);broken['rows'].pop()
                with self.assertRaises(ValueError):p.replay_receipts(broken)

    def test_pre_model_interrupt_retains_twenty_forty(self):
        with tempfile.TemporaryDirectory() as temp,patch.object(p,'MAIN',Path(temp)),patch.object(p,'require_committed',side_effect=KeyboardInterrupt):
            output=Path(temp)/'.thesis-build/dev-runs/fixture'
            self.assertEqual(p.run(ROOT/'research/m1-progressive-redundancy-dev.json',output),1)
            record=json.loads((output/'run.json').read_text())
            self.assertEqual(record['outcome'],'interrupted')
            self.assertEqual(record['planned_counts']['unet_calls'],1000)
            self.assertEqual(len(record['incomplete_planned_ids']),20)
            self.assertEqual(len(record['missing_image_conditions']),40)
            self.assertIsNone(record['gates']['operators'])
            with self.assertRaises(FileExistsError):p.run(ROOT/'research/m1-progressive-redundancy-dev.json',output)


if __name__=='__main__':unittest.main()
