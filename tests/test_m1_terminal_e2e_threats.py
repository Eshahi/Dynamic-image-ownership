"""CPU inventory/algebra/admission/recovery tests; no CUDA or model execution."""
import ast, copy, hashlib, json, math, sys, tempfile, unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import m1_assess_terminal_e2e as w
import m1_analyze_terminal_e2e_threats as a

class InventoryTests(unittest.TestCase):
    def test_exact_frozen_schedule(self):
        cfg=w.schedule();self.assertEqual(cfg,json.loads((ROOT/'research/m1-terminal-e2e-threat-schedule.json').read_text()))
        rows=cfg['conditions'];self.assertEqual(Counter(r['axis'] for r in rows),{'clean':24,'T3':312,'T4':80,'T5':66,'T5-transfer':7})
        self.assertEqual(sum(r['axis']!='T5' for r in rows)*4,1692)
        self.assertEqual(len({r['id'] for r in rows}),489)

    def test_partition_cover_without_overlap(self):
        cfg=w.schedule();parts=cfg['partitions'];allids=[i for p in parts.values() for i in p]
        self.assertEqual([len(parts[p]) for p in w.PARTITIONS],[56]*6+[153])
        self.assertEqual(len(allids),len(set(allids)));self.assertEqual(set(allids),{r['id'] for r in cfg['conditions']})

    def test_all_diagnostic_and_geometry_slots(self):
        slots=w.diagnostic_inventory();self.assertEqual(len(slots),1164)
        self.assertEqual(Counter(s['kind'] for s in slots),{'source-oracle':336,'transfer-tuple':348,'anchor-tuple':216,'cross-template':264})
        self.assertEqual(len({s['id'] for s in slots}),1164)
        self.assertEqual(66*2*4+87*4,876)

    def test_exact_donor_graph_seeds_owners(self):
        rows=w.schedule()['conditions'];self.assertEqual(len(w.directed_pairs()),27)
        pairs={(r['donor_id'],r['recipient_id']) for r in rows if r['axis']=='T4'}
        expected={(d,w.graph.ORIGINAL_IDS[(k+offset)%10]) for k,d in enumerate(w.graph.ORIGINAL_IDS) for offset in (1,5)}
        self.assertEqual(pairs,expected)
        self.assertEqual(sum(r['axis']=='T3' and r.get('dose')=='diffusion' for r in rows),288)
        for sid in w.candidate.IDS:
            for control in ('C0','C1'):
                actual={(r['strength'],r['seed']) for r in rows if r['axis']=='T3' and r.get('dose')=='diffusion' and r['source_id']==sid and r['control']==control}
                self.assertEqual(actual,{(s,seed) for s in (.05,.1,.2,.4) for seed in (0,1,2)})
        self.assertEqual(w.schedule()['owners'],list(w.graph.OWNERS));self.assertEqual(w.schedule()['threshold'],4.)

    def test_frozen_label_hash_rejected(self):
        with patch.object(w,'LABEL_SHA','0'*64):
            with self.assertRaisesRegex(ValueError,'label bytes'):w.schedule()

class ProjectionTests(unittest.TestCase):
    def fixture(self):
        rng=np.random.default_rng(9);E=rng.normal(size=512);E/=np.linalg.norm(E)
        return E,0x3af15962,rng.normal(size=w.core.N),rng.normal(size=w.core.N)

    def test_minimum_displacement_and_units(self):
        E,H,donor,recipient=self.fixture();target,info=w.projection_displacement(donor,recipient,E,H)
        p=w.core.template(E,H,w.core.OWNERS[0]);weights=[]
        for j in ('s','i'):
            vector=np.zeros(w.core.N);vector[p['coords_'+j]]=p['r_'+j]*p['v_'+j];weights.append(vector)
            self.assertAlmostEqual(target@vector,donor@vector,places=12)
        self.assertAlmostEqual(weights[0]@weights[1],0.,places=15)
        self.assertAlmostEqual(info['displacement_l2']**2,info['minimum_norm_squared'],places=12)
        alternative=np.random.default_rng(10).normal(size=w.core.N)
        for vector in weights:alternative-=alternative@vector*vector
        self.assertGreater(np.linalg.norm(target+alternative-recipient),np.linalg.norm(target-recipient))
        self.assertEqual(info['adaptive_detector_decision_queries'],0)

    def test_no_projection_shape_or_nonfinite_fallback(self):
        E,H,d,r=self.fixture()
        with self.assertRaises(ValueError):w.projection_displacement(d[:-1],r,E,H)
        d[0]=np.nan
        with self.assertRaises(ValueError):w.projection_displacement(d,r,E,H)

    def test_semantic_controls_hash_independent(self):
        E,H,z,_=self.fixture();other=np.roll(E,1)
        values=w.tuple_scores(z,{'E':E,'H':H},{'E':other,'H':H^0xffffffff})
        self.assertEqual(values['DD']['s'],values['DR']['s']);self.assertEqual(values['RD']['s'],values['RR']['s'])

    def test_public_projection_never_queries_detector_decisions(self):
        tree=ast.parse((ROOT/'scripts/m1_assess_terminal_e2e.py').read_text())
        cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ReadoutModels')
        project=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='project')
        called={n.func.attr for n in ast.walk(project) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)}
        self.assertNotIn('detect',called);self.assertNotIn('observe',called);self.assertIn('observations',called)
        observe=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='observe')
        self.assertEqual([n.arg for n in observe.args.args],['self','rgb'])

    def test_residual_operator_and_cap_exact(self):
        recipient=np.full((4,4,3),100,np.uint8);d0=np.full_like(recipient,90);d1=np.full_like(recipient,93)
        result=np.asarray(w.protocol.residual_transfer(recipient.tolist(),d1.tolist(),d0.tolist(),.5),np.uint8)
        expected=np.rint(np.clip(recipient.astype(float)+.5*(d1.astype(float)-d0.astype(float)),0,255)).astype(np.uint8)
        self.assertTrue(np.array_equal(result,expected))
        rgb=np.full((512,512,3),128,np.uint8);delta=np.random.default_rng(2).normal(0,.04,rgb.shape)
        new,receipt=w.candidate.residual.cap(rgb,delta);ref,refreceipt=a.audit_math.cap(rgb,delta)
        self.assertTrue(np.array_equal(new,ref));a.audit_math.equal(receipt,refreceipt,'cap')

class WitnessAndMissingTests(unittest.TestCase):
    def score(self,s,i):return dict(s=s,i=i,**w.core.classify_scores(s,i))
    def quality(self):return dict(psnr_infinite=False,psnr_db=36.,mse_rgb8=10.,ssim_rgb=.99,lpips=.01)

    def test_delivery_needs_background_quality_and_semantic_challenge(self):
        good=self.score(5.,5.);output={'DD':good};background={'DD':self.score(0.,0.)};anchor={'RR':self.score(4.,0.)}
        result=w.transfer_witness(good,output,background,self.quality(),anchor)
        self.assertTrue(result['strict_dual_delivery']);self.assertTrue(result['continuous_semantic_challenge'])
        self.assertFalse(w.transfer_witness(good,output,{'DD':good},self.quality(),anchor)['strict_dual_delivery'])
        q=self.quality();q['psnr_db']=35.
        self.assertFalse(w.transfer_witness(good,output,background,q,anchor)['strict_dual_delivery'])
        self.assertFalse(w.transfer_witness(good,output,background,self.quality(),{'RR':self.score(np.nextafter(4.,0.),0.)})['continuous_semantic_challenge'])

    def test_missing_denominators_never_become_rejection_or_security_pass(self):
        specs=w.schedule()['conditions'];missing=[dict(**r,verified=False,input_outcome='missing_enrollment') for r in specs]
        result=a.summaries(specs,missing)
        self.assertEqual(result['planned']['primary_queries'],1692);self.assertEqual(result['negative_controls']['planned'],1437)
        self.assertEqual(result['negative_controls']['observed'],0)
        for r in result['survival']:self.assertEqual(r['observed'],0)
        for r in result['transfer_coverage'].values():
            self.assertFalse(r['coverage_met']);self.assertIsNone(r['security_pass'])

    def test_missing_anchor_slots_retained(self):
        rows=w.anchor_controls({});self.assertEqual(len(rows),27)
        self.assertTrue(all(r['outcome']=='missing_enrollment' for r in rows))

class RecoveryTests(unittest.TestCase):
    def fixture(self,temp,outcome='incomplete'):
        base=Path(temp)/'.thesis-build/dev-runs/first';base.mkdir(parents=True)
        image=base/'generated.png';image.write_bytes(b'fixture-image-byte-receipt')
        identity={'assessment_core_sha256':'fixed','partition':'shard-0','condition_ids':['x']}
        rows=[dict(id='x',outcome='execution_failed',error='readout interrupted',image=w.receipt(image))]
        (base/'conditions.json').write_text(json.dumps(rows))
        record=dict(identity=identity,outcome=outcome,conditions_receipt=w.receipt(base/'conditions.json'),duration_seconds=4.)
        (base/'run.json').write_text(json.dumps(record));return base,identity,image

    def test_resume_reuses_generated_image_after_readout_failure(self):
        with tempfile.TemporaryDirectory() as temp,patch.object(w,'MAIN',Path(temp)):
            base,identity,image=self.fixture(temp);old,rows,r=w.resume_rows(base,identity)
            self.assertEqual(rows[0]['outcome'],'attack_persisted');self.assertEqual(rows[0]['image']['path'],str(image))
            self.assertIn('prior_execution_failure',rows[0])

    def test_identity_second_resume_completed_and_tamper_rejected(self):
        with tempfile.TemporaryDirectory() as temp,patch.object(w,'MAIN',Path(temp)):
            base,identity,image=self.fixture(temp)
            with self.assertRaisesRegex(ValueError,'identical'):w.resume_rows(base,dict(identity,assessment_core_sha256='changed'))
            value=json.loads((base/'run.json').read_text());value['resume_input']={'path':'earlier'};(base/'run.json').write_text(json.dumps(value))
            with self.assertRaisesRegex(ValueError,'one continuation'):w.resume_rows(base,identity)
            value.pop('resume_input');value['outcome']='completed';(base/'run.json').write_text(json.dumps(value))
            with self.assertRaises(ValueError):w.resume_rows(base,identity)
            value['outcome']='incomplete';(base/'run.json').write_text(json.dumps(value));image.write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'receipt changed'):w.resume_rows(base,identity)

class PrecisionTests(unittest.TestCase):
    def test_explicit_division_cast_and_errors(self):
        values=np.resize(np.array([0.,-0.,1.,-1.,np.finfo(np.float16).smallest_subnormal*.18215,1e-8,-.271828]),w.core.N)
        u64,u16,represented,info=w.decoder_input(values)
        self.assertTrue(np.array_equal(u64,np.divide(values,np.float64(.18215))))
        self.assertTrue(np.array_equal(u16,u64.astype(np.float16)));self.assertEqual(u16.dtype,np.float16)
        self.assertEqual(info['fp16_bytes_sha256'],hashlib.sha256(u16.astype('<f2').tobytes()).hexdigest())
        for key,delta,ref in [('unscaled_error',u16.astype(np.float64)-u64,u64),('scaled_error',represented-values,values)]:
            self.assertEqual(info[key]['l2'],float(np.linalg.norm(delta)))
            self.assertEqual(info[key]['relative_l2'],float(np.linalg.norm(delta))/float(np.linalg.norm(ref)))
        wrong=np.divide(values.astype(np.float16),np.float16(.18215)).astype(np.float16)
        self.assertTrue(np.any(wrong!=u16))
        self.assertIsNone(w.decoder_input(np.zeros(w.core.N))[3]['scaled_error']['relative_l2'])

    def test_overflow_shape_scale_rejected(self):
        for z,s in [(np.ones(w.core.N),.18),(np.ones((4,64,64)),.18215),(np.full(w.core.N,1e100),.18215),(np.full(w.core.N,np.nan),.18215)]:
            with self.assertRaises(ValueError):w.decoder_input(z,s)

    def test_postcast_residual_definitions(self):
        E,H,donor,recipient=ProjectionTests().fixture();target,info=w.projection_displacement(donor,recipient,E,H)
        t=w.decoder_input(target)[2];r=w.decoder_input(recipient)[2]
        result=w.postcast_residuals(t,r,donor,E,H,info['coefficients']);p=w.core.template(E,H,w.core.OWNERS[0])
        for j in ('s','i'):
            vector=np.zeros(w.core.N);vector[p['coords_'+j]]=p['r_'+j]*p['v_'+j]
            self.assertEqual(result[j]['absolute'],float(t@vector)-float(donor@vector))
            self.assertEqual(result[j]['displacement'],float((t-r)@vector)-info['coefficients'][j])

if __name__=='__main__':unittest.main()
