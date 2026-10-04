"""Generated worker consumes real UnitEngine with explicitly mocked model context."""
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import m1_candidate_rehearsal_worker as worker


class FakeContext:
    def __init__(self,*args,**kwargs):
        self.profile=worker.read(worker.ROOT/'configs/revised-watermark-v5.example.json')
        self.adapter=types.SimpleNamespace(initialize=self.initialize,embed=self.embed,
            public=types.SimpleNamespace(observations=lambda rgb:(self.feature(rgb),0,np.zeros(16384))))
    def feature(self,rgb):return np.ones(512,dtype=np.float64)/np.sqrt(512)
    def initialize(self,source,identity,owner,*,source_uid,resume,stop_step,on_checkpoint,check):
        for n in range(0,stop_step+1,10):
            result=dict(phase='initialization',step=n,binding=dict(source_identity=identity,owner=owner,source_uid=source_uid))
            on_checkpoint(result);check()
        return result
    def embed(self,source,initial,*,resume,stop_step,on_checkpoint,event,check):
        for n in range(0,101,10):
            result=dict(phase='embedding',step=n,binding=initial['binding'])
            on_checkpoint(result);check()
        return dict(completed=True,checkpoint=result,marked_rgb8=source.copy(),cap=dict(alpha=0.),
            core_result={name:np.zeros((1,3,512,512),dtype=np.float32) for name in ('reference','decoded','residual','surrogate')})
    def place_inference(self,device):pass
    def quality(self,a,b):return dict(psnr_db=None,psnr_infinite=True,mse_rgb8=0.,ssim_rgb=1.,lpips=0.,quality_admissible=True)
    def safety_check(self,rgb,**kw):
        if kw.get('before_safety'):kw['before_safety']()
        return dict(nsfw=False)
    def vae_cycle(self,rgb,**kw):return rgb.copy()
    def readout(self,rgb,owner):return dict(s=0.,i=0.,state='uncertain')


class WorkerEngineIntegrationTests(unittest.TestCase):
    def test_full_generated_worker_runs_engine_and_preserves_inventory(self):
        import torch
        import m1_candidate_model_context as context_module
        import m1_candidate_lifecycle as lifecycle
        with tempfile.TemporaryDirectory() as temporary:
            output=Path(temporary)
            for name in ('outputs','logs','checkpoints'):(output/name).mkdir()
            worker.atomic(output/'logs/worker-process-binding.json',{})
            manifest=dict(git_commit='0'*40,budget=dict(max_seconds=1800))
            path=output/'manifest.json';worker.atomic(path,manifest)
            scope=dict(scenario='real',stage='full',unit_index=0,injection=None,cooperative_stop_path=str(output/'stop.json'))
            with patch.object(worker,'validate_launch_scope',return_value=scope),patch.object(worker,'destination',side_effect=lambda value:Path(value)),patch.object(lifecycle,'pin_execution',return_value={}),patch.object(context_module,'CandidateModelContext',FakeContext),patch.object(torch.cuda,'synchronize'):
                self.assertEqual(worker.run(path,output),0)
            record=worker.read(output/'outputs/worker-run.json')
            self.assertEqual(record['unit_engine_version'],'m1-scientific-unit-engine-v1')
            self.assertEqual(len(record['conditions']),4)
            self.assertEqual([cp['step'] for cp in record['checkpoints'] if cp['phase']=='initialization'],list(range(0,201,10)))
            self.assertEqual([cp['step'] for cp in record['checkpoints'] if cp['phase']=='embedding'],list(range(0,101,10)))
            self.assertEqual(set(record['enrollment_images']),{'C0-source','C0-reconstruction','C1'})
            for row in record['conditions']:
                self.assertEqual(row['outcome'],'completed')
                self.assertEqual(len(row['owner_decisions']),4)
            for receipt in record['float_arrays'].values():
                value=np.load(receipt['path'],allow_pickle=False)
                self.assertEqual(value.shape,(512,512,3));self.assertEqual(value.dtype,np.float64)


if __name__=='__main__':unittest.main()
