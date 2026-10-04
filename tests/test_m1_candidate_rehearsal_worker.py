"""CPU mechanics fixtures only; no model inference or scientific evidence."""
import copy, hashlib, json, os, subprocess, sys, tempfile, time, unittest
from pathlib import Path
from unittest import mock
import numpy as np
import torch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(ROOT/'tests'))
import m1_candidate_rehearsal_worker as worker
import m1_candidate_adapter as candidate
import m1_source_initialization as initializer
import test_m1_candidate_adapter as fixtures


class WorkerTests(unittest.TestCase):
    def setUp(self):
        self.fixture=fixtures.AdapterTests();self.fixture.setUp()
        self.adapter=self.fixture.adapter
    def tearDown(self):self.fixture.tearDown()
    def states(self):
        initial=self.fixture.init()
        final=self.adapter.embed(self.fixture.rgb,initial)['checkpoint']
        record=dict(binding=initial['binding'],model_identity=self.fixture.models,
          scientific_core_sha256=self.fixture.models['scientific_core_sha256'],
          config={'owners':list(candidate.component.core.OWNERS)},
          source={'rgb8_sha256':hashlib.sha256(self.fixture.rgb.tobytes()).hexdigest(),'uid':'synthetic-fixture'},
          source_E=(np.ones(512)/np.sqrt(512)).tolist(),source_H=17)
        target=torch.from_numpy(self.fixture.rgb.copy()).permute(2,0,1)[None].float()/255
        return initial,final,record,target
    def test_generator_deterministic_distinct_canonical_and_path_free(self):
        a,raw,ra=worker.generated_source(0);b,rawb,rb=worker.generated_source(1)
        self.assertEqual(a.shape,(512,512,3));self.assertEqual(a.dtype,np.uint8)
        self.assertEqual(worker.generated_source(0)[1],raw)
        self.assertNotEqual(ra['rgb8_sha256'],rb['rgb8_sha256'])
        self.assertFalse(ra['external_raw_io']);self.assertEqual(ra['raw_sha256'],hashlib.sha256(raw).hexdigest())
        for v in (True,2,-1,'0'):
            with self.assertRaises(ValueError):worker.generated_source(v)
    def test_import_stdlib_no_torch_or_model_dependency(self):
        command=[sys.executable,'-c',"import sys;sys.path.insert(0,'scripts');import m1_candidate_rehearsal_worker as w;assert 'torch' not in sys.modules;assert 'diffusers' not in sys.modules;assert len(w.generated_seeds())==2"]
        subprocess.run(command,cwd=ROOT,check=True,capture_output=True,text=True)
    def test_pins_actual_adapter_and_owner_mapping(self):
        names={p.name for p in worker.dependency_paths()}
        self.assertTrue({'m1_candidate_adapter.py','m1_owner_interface.py','a4_protocol_reference.py'}<=names)
        self.assertEqual(worker.configuration()['steps'],candidate.CONFIG['embedding_updates'])
        self.assertEqual(worker.configuration()['initialization_updates'],candidate.CONFIG['initializer_updates'])
    def test_phase_seals_optimizer_and_rng_valid(self):
        initial,final,record,target=self.states()
        before=initializer.digest(initializer._rng())
        worker.validate_phase_checkpoint(initial,record,target)
        worker.validate_phase_checkpoint(final,record,target,initializer_payload=initial)
        self.assertEqual(before,initializer.digest(initializer._rng()))
    def test_resealed_bad_embedding_moments_and_rng_are_rejected(self):
        initial,final,record,target=self.states()
        for defect in ('moment','rng','identity','config','initializer'):
            bad=copy.deepcopy(final)
            if defect=='moment':bad['state']['optimizer']['state'][0]['exp_avg'][0,0,0,0]=float('nan')
            if defect=='rng':bad['state']['rng']['torch_cpu']=torch.zeros(7,dtype=torch.uint8)
            if defect=='identity':bad['binding']['owner']=candidate.component.core.OWNERS[1]
            if defect=='config':bad['configuration']['embedding_lr']=.2
            if defect=='initializer':bad['initializer_sha256']='0'*64
            bad=candidate._sealed({k:v for k,v in bad.items() if k!='integrity_sha256'})
            with self.subTest(defect=defect),self.assertRaises(ValueError):worker.validate_phase_checkpoint(bad,record,target,initializer_payload=initial)
    def test_original_initializer_seal_and_source_target_required(self):
        initial,final,record,target=self.states()
        bad=copy.deepcopy(initial);bad['state']['z'][0,0,0,0]+=1
        bad=candidate._sealed({k:v for k,v in bad.items() if k!='integrity_sha256'})
        with self.assertRaises(ValueError):worker.validate_phase_checkpoint(bad,record,target)
        with self.assertRaises(ValueError):worker.validate_phase_checkpoint(initial,record,target+.001)
    def test_adapter_against_direct_core_analytic_trajectory_exact(self):
        """RNG/Adam plumbing parity, analytic substitute explicitly not efficacy."""
        initial=self.fixture.init();adapted=self.adapter.embed(self.fixture.rgb,initial)['checkpoint']
        candidate._seed_fresh_phase();saved=[]
        def save(step,u,opt):
            saved.append({'u':u.detach().clone(),'optimizer':initializer._cpu_tree(opt.state_dict()),'step':step,'rng':candidate._method_rng()})
        fixtures.analytic_optimize(self.adapter.embedder,torch.from_numpy(self.fixture.rgb).permute(2,0,1)[None].float()/255,
          initial['state']['z'],object(),{'steps':100,'learning_rate':.01,'adam_betas':[.9,.999],'adam_eps':1e-8,'checkpoint_every':10},
          lambda row:None,save,lambda:None)
        self.assertEqual(initializer.digest(adapted['state']),initializer.digest(saved[-1]))
    def test_raw_feature_normalized_once(self):
        value=np.linspace(.0001,1.1,512,dtype=np.float64)
        self.adapter.feature_input=lambda rgb:value
        expected=value/float(np.linalg.norm(value))
        self.assertTrue(np.array_equal(self.adapter.feature(self.fixture.rgb),expected))
    def test_exact_full_resume_gate_false_if_any_state_drifts(self):
        with tempfile.TemporaryDirectory() as temp:
            base=Path(temp);left=base/'left';right=base/'right';left.mkdir();right.mkdir()
            def record(path,stage):
                cps=[]
                for phase,steps in [('initialization',range(0 if stage=='full' else 100,201,10)),('embedding',range(0,101,10))]:
                    for step in steps:
                        dest=path/f'{phase}-{step}.pt';torch.save({'phase':phase,'step':step,'fixture':torch.tensor([step])},dest)
                        cps.append({'phase':phase,'step':step,'path':str(dest),'sha256':worker.file_sha(dest)})
                return {'stage':stage,'outcome':'completed','source':{'fixture':True},'checkpoints':cps,'initialization_endpoint_digest':'a',
                    'embedding_endpoint_digest':'b','conditions':[{'control':'C0','dose':'clean','rgb8_sha256':'x','owner_decisions':{}}]}
            a=record(left,'full');b=record(right,'resume')
            with mock.patch.object(worker,'audit_rehearsal_run',side_effect=[a,b]):result=worker.compare_full_resume(left,right)
            self.assertTrue(result['passes']);self.assertEqual(len(result['overlap_checks']),22)
            target=right/'initialization-150.pt';torch.save({'phase':'initialization','step':150,'fixture':torch.tensor([151])},target)
            with mock.patch.object(worker,'audit_rehearsal_run',side_effect=[a,b]):result=worker.compare_full_resume(left,right)
            self.assertFalse(result['passes']);self.assertFalse(result['checks']['overlap_states_adam_rng_exact'])
    def test_quality_missing_nonfinite_bool_and_changed_conjunction_rejected(self):
        quality={'mse_rgb8':1.,'psnr_db':48.,'psnr_infinite':False,'ssim_rgb':.99,'lpips':.01,'quality_admissible':True}
        worker.validate_quality(quality)
        for bad in (dict(quality,lpips=float('nan')),dict(quality,ssim_rgb=True),dict(quality,quality_admissible=False),dict(quality,psnr_db=None)):
            with self.assertRaises(ValueError):worker.validate_quality(bad)
        with self.assertRaises(ValueError):worker.validate_quality({})
    def test_destination_rejects_real_data_and_base_root(self):
        with tempfile.TemporaryDirectory() as temp,mock.patch.object(worker,'MAIN',Path(temp)):
            for dest in [Path(temp)/'inputs/image.png',Path(temp)/'.thesis-build/rehearsal']:
                with self.assertRaises(ValueError):worker.destination(dest)
            dest=Path(temp)/'.thesis-build/rehearsal/owned-child'
            self.assertEqual(worker.destination(dest),dest.absolute())

if __name__=='__main__':unittest.main()
