"""Procedural CPU fixtures; no pretrained weights or retained scores opened."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import numpy as np

SPEC=importlib.util.spec_from_file_location('probe',Path(__file__).resolve().parents[1]/'scripts/m1_gs_lightweight_probe.py')
p=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(p)

class ProbeTests(unittest.TestCase):
    key='01'*32
    nonce='02'*12

    def signs(self):
        ref=p.message(1000)
        return np.tile(ref,(1,8,8)).reshape(1,4,64,64)^p.whitening(self.key,self.nonce)

    def sealed(self):
        return dict(schema_version=p.VERSION,config=copy.deepcopy(p.CONFIG),keys={'correct':self.key,'wrong':'03'*32},
            nonces=[p.nonce_for(s) for s in range(1000,1004)],images=[dict(opaque_id=f'image-{"a"*64}-{i:02d}',path=str(Path.cwd()/f'image-{"a"*64}-{i:02d}.png'),sha256='a'*64) for i in range(24)])

    def test_documented_shake_bytes(self):
        expected=hashlib.shake_256(b'm1-gs-whitening-v1'+bytes.fromhex(self.key)+bytes.fromhex(self.nonce)).digest(2048)
        self.assertEqual(np.packbits(p.whitening(self.key,self.nonce)).tobytes(),expected)

    def test_known_message_exact_and_one_coordinate(self):
        signs=self.signs();before=p.independent_votes(signs,self.key,self.nonce)
        self.assertEqual(p.evaluate(before,p.message(1000))['matches'],256)
        signs[0,2,17,26]^=1;after=p.independent_votes(signs,self.key,self.nonce)
        changed=[i for i,(a,b) in enumerate(zip(before['votes'],after['votes'])) if a!=b]
        self.assertEqual(changed,[2*64+1*8+2]);self.assertEqual(abs(before['votes'][changed[0]]-after['votes'][changed[0]]),1)

    def test_runtime_synthetic_selfcheck(self):self.assertTrue(all(p.synthetic_selfcheck().values()))

    def test_zero_exception_not_hidden(self):
        latent=np.where(self.signs(),1.,-1.).astype(np.float32);latent[0,0,0,0]=0
        signs=(latent>0).astype(np.uint8);negative=(-latent>0).astype(np.uint8)
        result=p.zero_aware_algebra(signs,negative,latent==0,self.key,self.nonce)
        self.assertEqual(result['zero_coordinate_count'],1);self.assertEqual(result['zero_affected_bits'],1)
        self.assertTrue(result['votes_complement_zero_adjusted']);self.assertTrue(result['zero_signs_remain_zero'])
        self.assertEqual(sum(abs(v) for v in result['zero_vote_adjustments']),1)

    def test_reference_cannot_change_raw_outputs(self):
        result=p.independent_votes(self.signs(),self.key,self.nonce);before=copy.deepcopy(result)
        a=p.evaluate(result,p.message(1000));b=p.evaluate(result,1-p.message(1000))
        self.assertEqual(a['matches']+b['matches'],256);self.assertEqual(before,result)

    def test_bad_bits_votes_lengths_rejected(self):
        original=p.independent_votes(self.signs(),self.key,self.nonce)
        for field,bad in (('bits',original['bits'][:-1]),('bits',[False]*256),('votes',[False]*256),('votes',[65]*256),('ties',999)):
            with self.subTest(field=field,bad=str(bad)[:20]):
                result=copy.deepcopy(original);result[field]=bad
                with self.assertRaises(ValueError):p.evaluate(result,p.message(1000))
        with self.assertRaises(ValueError):p.independent_votes(np.full((1,4,64,64),np.nan),self.key,self.nonce)

    def test_sealed_data_boundary_and_fixed_denominator(self):
        p.sealed_validate(self.sealed())
        for mutation in ('payload','subset','duplicate','relative','label'):
            sealed=self.sealed()
            if mutation=='payload':sealed['images'][0]['payload']=[0]*256
            elif mutation=='subset':sealed['images'].pop()
            elif mutation=='duplicate':sealed['images'][1]=sealed['images'][0]
            elif mutation=='relative':sealed['images'][0]['path']=Path(sealed['images'][0]['path']).name
            elif mutation=='label':sealed['images'][0]['opaque_id']='prompt-0-C1'
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):p.sealed_validate(sealed)

    def test_source_noise_magnitude_and_roundtrip(self):
        base,marked=p.initial_noises(1000,self.key)
        self.assertEqual(base.dtype,np.float16);np.testing.assert_array_equal(abs(base),abs(marked))
        self.assertEqual(p.evaluate(p.independent_votes((marked>0).astype(np.uint8),self.key,p.nonce_for(1000)),p.message(1000))['matches'],256)

    def test_transport_no_decision_threshold(self):
        a=np.ones((1,4,64,64),np.float32)
        self.assertEqual(p.transport(a,-a),{'sign_agreement':0.,'cosine':-1.})
        self.assertIsNone(p.transport(a,a*0)['cosine'])

    def test_stopped_worker_preserves_24_failures_and_null_gates(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'readout').mkdir()
            mapping={'keys':{'correct':self.key,'wrong':'03'*32},'selfchecks':{},'entries':[]}
            for seed in range(1000,1004):
                marked=p.initial_noises(seed,self.key)[1]
                mapping['selfchecks'][str(seed)]={'tensor_sha256':hashlib.sha256(marked.tobytes()).hexdigest()}
            rows=[]
            for i in range(24):
                opaque=f'fixture-{i}'
                mapping['entries'].append({'opaque_id':opaque,'source_row':{'id':opaque,'case':f'prompt-{i//6}','arm':'C0' if i%6<3 else 'C1','channel':p.CONFIG['channels'][i%3]}})
                rows.append({'opaque_id':opaque,'outcome':'not_completed_after_stop'})
            (root/'evaluator-map.json').write_text(json.dumps(mapping))
            (root/'readout/run.json').write_text(json.dumps({'rows':rows}))
            result=p.evaluate_emitted(root)
            self.assertEqual(len(result['rows']),24);self.assertFalse(result['complete'])
            self.assertTrue(all(r['outcome']=='failed' for r in result['rows']))
            self.assertIsNone(result['implementation_gate']);self.assertIsNone(result['exact_replication_gate'])

if __name__=='__main__':unittest.main()
