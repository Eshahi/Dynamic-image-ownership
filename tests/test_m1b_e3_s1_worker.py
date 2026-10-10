"""No held-out pixels or models: S1 control flow, adverse pixels and continuation."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT)]
import m1b_coco512_worker as W
import m1b_e3_s1_runtime as S


def fixture():
    uids=['synthetic:1','synthetic:2']
    ref=dict(path='unused',sha256='0'*64)
    return dict(schema=W.PLAN_SCHEMA,protocol=S.PROTOCOL,data_split='development',
        methods=list(S.METHODS),owners=list(S.OWNERS),f5_config=ref,profile=ref,
        s1_config=ref,environment_lock=ref,sdxl_lock=ref,assets_root='unused',
        sources=dict(inline=[dict(uid=u,group_id='g'+u,raw_path='unused/'+u,raw_sha256=str(i)*64) for i,u in enumerate(uids)]),
        strengths=[.1,.2],seeds=[3,4,5],patch_sizes=[],t3_uids=uids,
        t4_pairs=[dict(pair_index=0,donor_uid=uids[0],recipient_uid=uids[1])],
        t5=dict(selector='fixture-categories',categories={u:[1] for u in uids},max_pairs=1))


class Fake:
    def __init__(self): self.order=[]; self.embeds=0
    def canonical(self,s): self.order.append('source');return np.full((32,32,3),int(s['uid'][-1]),np.uint8),{}
    def phash(self,r): return 0 if r[0,0,0]==1 else 65535
    def categories(self,uids,t5): self.order.append('selection'); return {u:(1,) for u in uids}
    def supply(self,r,folder): return dict(status="ok",payload=dict(q="00000001",h="00000002"))
    def embed(self,m,r,u,o,folder,supplier=None):
        if 'source' in self.order: assert 'selection' in self.order
        self.order.append('embed');self.embeds+=1
        return r.copy(),dict(supplier=dict(status='ok'),payload=dict(q='00000001',h='00000002'),admitted=False,admission=dict(accepted=False))
    def clip_vector(self,r,views): return [1.,0.]
    def quality(self,a,b): return dict(psnr_infinite=False,psnr_db=40.,ssim_rgb=.96,lpips=.01)
    def detect(self,m,r,o,mode,roster):
        assert roster==(1 if m=='e3-s1' or mode!='combined' else 4) or roster==1
        tier=dict(found=False,read=False,content_match=False,decoded_code=None,own_h_content_match=False)
        return dict(semantic=tier,instance=tier,outcome='neither_match',owner_id=o,owners_tested=roster,binding_mode=mode)
    def attack(self,r,d):return r.copy(),dict(dose=d)
    def transfer(self,m,r,d,d0,c):return r.copy(),dict(condition=c)


class Tests(unittest.TestCase):
    def sources(self,p): return W.load_sources(p)
    def test_full_inventory_admission_failure_keeps_pixels_and_descendants(self):
        p=fixture();rt=Fake()
        with tempfile.TemporaryDirectory() as td:
            worker=W.Worker(p,self.sources(p),Path(td),rt)
            status,selected,error=worker.run()
            self.assertEqual(status,'finished'); self.assertIsNone(error)
            self.assertTrue(selected)
            self.assertEqual(set(worker.journal.rows),set(W.planned_ids(p,worker.sources,selected)))
            for row in worker.journal.rows.values():
                if row.get('stage')=='embed': self.assertFalse(row['admitted']);self.assertIn('image',row)
            self.assertEqual(rt.order[:3],['source','source','selection'])
            self.assertEqual(len([r for r in worker.journal.rows.values() if r.get('stage')=='t3_attack']),36)
            self.assertEqual(len([r for r in worker.journal.rows.values() if r.get('stage')=='t3']),192)
    def test_completed_units_reused_without_embedding(self):
        p=fixture()
        with tempfile.TemporaryDirectory() as td:
            a=W.Worker(p,self.sources(p),Path(td),Fake());self.assertEqual(a.run()[0],'finished')
            second=Fake();b=W.Worker(p,a.sources,Path(td),second)
            self.assertEqual(b.run()[0],'finished');self.assertEqual(second.embeds,0)
    def test_mid_writer_checkpoint_is_not_scientific_failure_and_orphan_kept(self):
        p=fixture();clock=[0.];p['max_wall_seconds']=60
        class Interrupted(Fake):
            def embed(self,*args): clock[0]=61.;self.budget()
        with tempfile.TemporaryDirectory() as td:
            a=W.Worker(p,self.sources(p),Path(td),Interrupted(),clock=lambda:clock[0])
            self.assertEqual(a.run()[0],'checkpointed')
            self.assertFalse(any(r.get('stage')=='embed' for r in a.journal.rows.values()))
            orphan=list(a.images.glob('c-*'));self.assertEqual(len(orphan),1)
            clock[0]=0.;b=W.Worker(p,a.sources,Path(td),Fake(),clock=lambda:clock[0])
            self.assertEqual(b.run()[0],'finished');self.assertTrue(orphan[0].is_dir())
    def test_non_test_guard_fresh_uid_group_and_digest(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td);historical=base/W.HELD_OUT_INDEX;historical.parent.mkdir(parents=True)
            historical.write_text(json.dumps(dict(entries=[])))
            fresh=base/S.FRESH_INVENTORY;fresh.parent.mkdir(parents=True,exist_ok=True)
            fresh.write_text(json.dumps(dict(entries=[dict(source_uid='held:1',group_id='held-g',raw_sha256='a'*64)])))
            for field,value in [('uid','held:1'),('group_id','held-g'),('raw_sha256','a'*64)]:
                p=fixture();p['sources']['inline'][0][field]=value;p['t3_uids']=[r['uid'] for r in p['sources']['inline']]
                p['t4_pairs'][0]['donor_uid']=p['t3_uids'][0]
                with self.assertRaises(ValueError): W.validate_plan(p,base)
    def test_unknown_protocol_and_old_digest_stable(self):
        p=fixture();p['protocol']='ambiguous'
        with self.assertRaises(ValueError): W.validate_plan(p)
        del p['protocol']
        expected=W.object_digest({k:p.get(k) for k in W.SCIENCE_FIELDS if k not in ('protocol','owners','s1_config','environment_lock','sdxl_lock')})
        self.assertEqual(W.science_digest(p),expected)




class ScientificAdapterTests(unittest.TestCase):
    def test_fresh_seed_operator_receipts_and_safety(self):
        from types import SimpleNamespace
        from contextlib import nullcontext
        import m1_confirmatory_image_operations as ops
        import three_threat_models as models
        from PIL import Image
        class Generator:
            def __init__(self,device): self.device=device
            def manual_seed(self,seed):self.seed=seed;return self
        class Pipeline:
            def __init__(self):
                self.scheduler=SimpleNamespace(config=SimpleNamespace(**models.DDIM_CONFIG),timesteps=list(ops.TIMESTEPS))
                self.safety_checker,self.feature_extractor=object(),object()
                self.unet=self;self.removed=False;self.block=False
            def register_forward_hook(self,fn,with_kwargs): self.hook=fn;return SimpleNamespace(remove=lambda:setattr(self,'removed',True))
            def __call__(self,**kwargs):
                self.kwargs=kwargs
                for t in ops.TIMESTEPS[-int(20*kwargs['strength']):]: self.hook(self,(None,t),{},None)
                return SimpleNamespace(images=[kwargs['image']],nsfw_content_detected=[self.block])
        rgb=np.zeros((512,512,3),np.uint8)
        for strength in (.1,.2):
            for seed in (3,4,5):
                pipe=Pipeline();result=S.s1_regeneration(rgb,strength,seed,pipeline=pipe,generator_factory=Generator,inference_context=nullcontext)
                self.assertEqual(pipe.kwargs['generator'].seed,seed)
                self.assertEqual(result.receipt['actual_ddim_timesteps'],list(ops.TIMESTEPS[-int(20*strength):]))
                self.assertTrue(pipe.removed);self.assertEqual(result.receipt['safety_verdict'],[False])
                self.assertEqual(result.receipt['prompt'],'');self.assertEqual(pipe.kwargs['guidance_scale'],1.)
        pipe=Pipeline();pipe.block=True
        with self.assertRaises(ops.OperationFailure) as cm:S.s1_regeneration(rgb,.1,3,pipeline=pipe,generator_factory=Generator,inference_context=nullcontext)
        self.assertTrue(W.is_safety_block(cm.exception));self.assertEqual(cm.exception.receipt['safety_verdict'],[True]);self.assertTrue(pipe.removed)
        self.assertEqual(ops.SEEDS,(0,1,2))
        with self.assertRaises(ValueError):S.s1_regeneration(rgb,.1,0,pipeline=Pipeline(),generator_factory=Generator,inference_context=nullcontext)
    def test_native_transfer_arm_mapping_and_json_safe_vectors(self):
        from types import SimpleNamespace
        from unittest.mock import patch
        import v5_study_protocol as native
        rgb=np.zeros((512,512,3),np.uint8)
        rt=object.__new__(S.Runtime);rt.np=np;rt.profile={};rt.budget=lambda:None
        with patch.object(native,'transfer',return_value=rgb.tolist()) as fn:
            for condition,arm in [('public','public_projection'),('public-sham','unmarked_projection_sham')]:
                rt.transfer('v5-r3',rgb,rgb,rgb,condition)
                self.assertEqual(fn.call_args.args[-1],arm);self.assertIn(arm,native.TRANSFER_ARMS)
        rt.ev=SimpleNamespace(reader=SimpleNamespace(latent=lambda rgb:None))
        rt.layout=SimpleNamespace(projections=lambda z:np.array([1.,2.]))
        rt.fragile=SimpleNamespace(analysis=None,projections=lambda z:np.array([3.,4.]))
        rt.v5=SimpleNamespace(luminance_from_rgb=lambda x:None,base=SimpleNamespace(_analyse=lambda *a:(None,None)))
        import journal_e3_public_projection as pp
        with patch.object(pp,'semantic_inverse',return_value=(rgb,{})),patch.object(pp,'fragile_replace',return_value=rgb):
            _,receipt=rt.transfer('e3-s1',rgb,rgb,rgb,'public')
            json.dumps(receipt,allow_nan=False)
            self.assertEqual(receipt['public_vector_targets']['semantic'],[1.,2.])
    def test_same_call_requires_both_presence_and_own_h(self):
        call=dict(semantic=dict(found=True,content_match=True),instance=dict(found=False,content_match=True,own_h_content_match=True))
        self.assertFalse(any(S.same_call_predicates(call)[k] for k in ('semantic_only','perceptual_only','none','combined')))
        call['instance'].update(found=True,content_match=False)
        p=S.same_call_predicates(call);self.assertTrue(p['semantic_only']);self.assertTrue(p['perceptual_only']);self.assertTrue(p['none']);self.assertFalse(p['combined'])
    def test_supplier_failure_no_pixels_retains_descendant_missingness(self):
        class Failed(Fake):
            def supply(self,*args):return dict(status='supplier_failed',error='Fresh F5 bootstrap native channels unreadable')
            def embed(self,m,*args):
                if m=='e3-s1':raise AssertionError('failed supplier must not enter writer')
                return super().embed(m,*args)
        p=fixture()
        with tempfile.TemporaryDirectory() as td:
            w=W.Worker(p,W.load_sources(p),Path(td),Failed());self.assertEqual(w.run()[0],'finished')
            row=w.journal.get('src:synthetic:1:e3-s1:embed');self.assertFalse(row['returned_final_pixels']);self.assertNotIn('image',row)
            self.assertEqual(w.journal.get('src:synthetic:1:e3-s1:clean:C1:'+S.OWNERS[0])['outcome'],'missing_dependency')
            self.assertIsNone(w.journal.get('src:synthetic:1:v5-r3:embed')['supplier_success'])
    def test_v5_own_h_is_independent_of_propagation_and_missing_is_unknown(self):
        from types import SimpleNamespace
        rt=object.__new__(S.Runtime);rt.budget=lambda:None
        rt.ev=SimpleNamespace(features=lambda *a:[]);rt.profile=dict(decision=dict(instance_radius=6))
        for distance,expected in [(4,True),(9,False),(None,None)]:
            def native(*args,**kwargs):
                return dict(semantic=dict(found=True,content_match=False),instance=dict(found=True,content_match=False,corrected_distance=distance))
            rt.v5=SimpleNamespace(detect_rgb=native)
            result=rt.detect('v5-r3',np.zeros((1,1,3),np.uint8),S.OWNERS[0])
            self.assertIs(result['instance']['own_h_content_match'],expected)

    def test_frozen_catcher_software_defects_stop_infrastructure(self):
        rt=object.__new__(S.Runtime)
        for kind in ('TypeError','NameError','ImportError','KeyError','CUDA error'):
            with self.assertRaises(Exception) as cm:rt._execution_error(dict(error=kind+': bad'))
            self.assertTrue(W.is_infrastructure(cm.exception))

class ExplicitScientificFailureTests(unittest.TestCase):
    def test_third_failure_is_persisted_and_never_retried(self):
        p=fixture();calls=[]
        with tempfile.TemporaryDirectory() as td:
            w=W.Worker(p,W.load_sources(p),Path(td),Fake())
            def fail(i): calls.append(i);raise S.ScientificFailure('known failed observation')
            for i in range(2):w._unit('known:'+str(i),lambda i=i:fail(i))
            with self.assertRaises(W.InfrastructureStop):w._unit('known:2',lambda:fail(2))
            self.assertEqual(len(w.journal.rows),3);self.assertEqual(w.journal.get('known:2')['outcome'],'failed')
            resumed=W.Worker(p,w.sources,Path(td),Fake())
            resumed._unit('known:2',lambda:fail(2))
            self.assertEqual(calls,[0,1,2])
    def test_unexpected_value_assertion_and_wrapped_defects_get_no_row(self):
        p=fixture()
        with tempfile.TemporaryDirectory() as td:
            w=W.Worker(p,W.load_sources(p),Path(td),Fake())
            for i,error in enumerate((ValueError('unexpected'),AssertionError('defect'),RuntimeError('software defect'))):
                def fail(error=error):raise error
                with self.assertRaises(W.InfrastructureStop):w._unit('defect:'+str(i),fail)
                self.assertNotIn('defect:'+str(i),w.journal.rows)
    def test_supplier_exact_unreadable_and_admission_are_retained_but_defects_refused(self):
        rt=object.__new__(S.Runtime)
        rt._execution_error(dict(status='supplier_failed',error='Traceback (most recent call last):\nValueError: Fresh F5 bootstrap native channels unreadable'))
        rt._execution_error(dict(status='admission_failed',admitted=False))
        for error in ('AssertionError: failed assertion','ValueError: arbitrary defect','ValueError: Fresh F5 bootstrap native channels unreadable extra'):
            with self.assertRaises(OSError):rt._execution_error(dict(status='construction_failed',error=error))
        with self.assertRaises(OSError):rt._execution_error(dict(status='supplier_failed'))
    def test_supply_classifies_before_return_and_commit(self):
        rt=object.__new__(S.Runtime);rt.ev=None;rt.budget=lambda:None
        rt.supplier=lambda *args:dict(status='supplier_failed',error='AssertionError: defect')
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(OSError):rt.supply(None,Path(td))
            rt.supplier=lambda *args:dict(status='supplier_failed',error='ValueError: Fresh F5 bootstrap native channels unreadable')
            self.assertEqual(rt.supply(None,Path(td))['status'],'supplier_failed')

    def test_safety_stays_observed_and_no_generic_substring_allowlist(self):
        self.assertTrue(S.is_scientific_failure(RuntimeError('safety_checker_blocked_output')))
        self.assertFalse(S.is_scientific_failure(AssertionError('safety_checker_blocked_output')))
        self.assertFalse(S.is_scientific_failure(ValueError('safety_checker_blocked_output')))
        self.assertFalse(S.is_scientific_failure(RuntimeError('software defect mentions safety_checker_blocked_output')))

if __name__=='__main__':unittest.main()
