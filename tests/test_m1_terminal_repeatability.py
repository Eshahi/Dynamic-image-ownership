"""CPU-only deterministic-policy, prefix evidence and stale-receipt tests."""
import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import torch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import m1_terminal_continuous as method
import m1_terminal_repeatability as repeat


class RepeatabilityTests(unittest.TestCase):
    def test_configuration_is_strict_and_does_not_initialize_cuda(self):
        old=(torch.are_deterministic_algorithms_enabled(),torch.is_deterministic_algorithms_warn_only_enabled(),
             torch.backends.cudnn.deterministic,torch.backends.cudnn.benchmark,
             torch.backends.cudnn.allow_tf32,torch.backends.cuda.matmul.allow_tf32)
        try:
            with patch.dict(os.environ,{},clear=False):
                os.environ.pop('CUBLAS_WORKSPACE_CONFIG',None)
                receipt=repeat.configure()
                self.assertEqual(receipt['version'],repeat.VERSION)
                self.assertEqual(os.environ['CUBLAS_WORKSPACE_CONFIG'],repeat.WORKSPACE)
                self.assertTrue(torch.are_deterministic_algorithms_enabled())
                self.assertFalse(torch.is_deterministic_algorithms_warn_only_enabled())
                self.assertTrue(torch.backends.cudnn.deterministic)
                self.assertFalse(torch.backends.cudnn.benchmark)
                self.assertFalse(torch.cuda.is_initialized())
            with patch.dict(os.environ,{'CUBLAS_WORKSPACE_CONFIG':':16:8'}):
                with self.assertRaisesRegex(ValueError,'Conflicting'):repeat.configure()
            with patch.object(torch.cuda,'is_initialized',return_value=True):
                with self.assertRaisesRegex(RuntimeError,'before CUDA'):repeat.configure()
        finally:
            torch.use_deterministic_algorithms(old[0],warn_only=old[1])
            torch.backends.cudnn.deterministic=old[2];torch.backends.cudnn.benchmark=old[3]
            torch.backends.cudnn.allow_tf32=old[4];torch.backends.cuda.matmul.allow_tf32=old[5]

    def fixture(self,directory):
        records=[]
        for index in (1,2):
            root=directory/str(index);root.mkdir()
            source=root/'source.png';source.write_bytes(b'identical-source')
            case=dict(source_id=1675,outcome='probe_completed',source=dict(path=str(source),sha256=repeat.sha(source),rgb8_sha256='rgb'),
                      initialization={'unmarked':'step200'},source_E=[1.]+[0.]*511,source_H=13,
                      probe_trajectory=[{'step':s,'gradient_l2':128.} for s in range(1,11)],
                      probe_gradients=[],checkpoints=[],probe_arrays={})
            for step in range(1,11):
                path=root/f'grad{step}.npy';np.save(path,np.full((1,4,64,64),step,np.float32))
                case['probe_gradients'].append(dict(step=step,path=str(path),sha256=repeat.sha(path)))
            for step in (0,10):
                path=root/f'step{step}.pt'
                state=dict(u=torch.full((1,4,64,64),float(step)),optimizer={'state':{0:{'exp_avg':torch.ones(3)}}},
                           rng={'torch_cpu':torch.tensor([1,2],dtype=torch.uint8)},step=step,identity={'commit':str(index)})
                torch.save(state,path);case['checkpoints'].append(dict(step=step,path=str(path),sha256=repeat.sha(path)))
            for field in ('reference','decoded','surrogate'):
                path=root/(field+'.npy');np.save(path,np.ones((2,2,3),np.float64))
                case['probe_arrays'][field]=dict(path=str(path),sha256=repeat.sha(path))
            record=dict(schema=method.VERSION,data_split='development',config=method.configuration(),manifest_sha256='manifest',
                        run_kind=repeat.PROBE_VERSION,outcome='probe_completed',repeatability_prefix_updates=10,
                        conditions=[],gate=None,case_events=[case],process_id=index,
                        execution_variant=repeat.VERSION,deterministic_execution={'deterministic_algorithms':True},
                        scientific_files={'scripts/worker.py':'code','config.json':'params'},environment={'torch':'pinned'},
                        assets={'model':'pinned'},device_identity={'gpu':'fixed'},lpips_learned_sha256='lpips',reconstruction_run_sha256='init')
            records.append(record)
        return records

    def test_exact_independent_prefix_is_not_a_full_pilot_or_old_replay(self):
        with tempfile.TemporaryDirectory() as tmp:
            left,right=self.fixture(Path(tmp));result=repeat.compare_records(left,right)
            self.assertTrue(result['passed']);self.assertEqual(len(result['gradient_steps']),10)
            self.assertFalse(result['full100_step_repeatability_tested'])
            self.assertFalse(result['old_nondeterministic_replay_required'])
            self.assertFalse(torch.cuda.is_initialized())

    def test_equal_gradient_norm_does_not_mask_different_full_gradient(self):
        with tempfile.TemporaryDirectory() as tmp:
            left,right=self.fixture(Path(tmp));item=right['case_events'][0]['probe_gradients'][0]
            path=Path(item['path']);x=np.load(path);x[0,0,0,0]=-1;np.save(path,x);item['sha256']=repeat.sha(path)
            with self.assertRaisesRegex(ValueError,'gradient arrays differ'):repeat.compare_records(left,right)

    def test_metadata_missing_steps_and_changed_adam_rejected(self):
        for change in ('same_process','environment','source','missing_gradient','adam','nonfinite','trajectory'):
            with self.subTest(change=change),tempfile.TemporaryDirectory() as tmp:
                left,right=self.fixture(Path(tmp));case=right['case_events'][0]
                if change=='same_process':right['process_id']=left['process_id']
                elif change=='environment':right['environment']['torch']='different'
                elif change=='source':case['initialization']['unmarked']='other'
                elif change=='missing_gradient':case['probe_gradients'].pop()
                elif change=='trajectory':case['probe_trajectory'][0]['gradient_l2']=129.
                elif change=='nonfinite':
                    r=case['probe_gradients'][0];p=Path(r['path']);x=np.load(p);x[0,0,0,0]=np.nan;np.save(p,x);r['sha256']=repeat.sha(p)
                else:
                    r=case['checkpoints'][-1];p=Path(r['path']);x=torch.load(p,weights_only=False);x['optimizer']['state'][0]['exp_avg'][0]=2.;torch.save(x,p);r['sha256']=repeat.sha(p)
                with self.assertRaises(ValueError):repeat.compare_records(left,right)

    def test_receipt_revalidates_artifacts_and_ignores_only_report_dependency(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);records=self.fixture(root);inputs=[]
            for i,record in enumerate(records):
                p=root/f'run{i}.json';p.write_text(json.dumps(record));inputs.append(dict(path=str(p),sha256=repeat.sha(p)))
            comparison=repeat.compare_records(*records)
            p=root/'comparison.json';p.write_text(json.dumps(dict(schema=repeat.COMPARISON_VERSION,data_split='development',outcome='completed',input_runs=inputs,comparison=comparison)))
            files=dict(records[0]['scientific_files'],**{'research/new-report.md':'new'})
            self.assertTrue(repeat.require_receipt(p,files,'manifest')['comparison']['passed'])
            with self.assertRaisesRegex(ValueError,'bytes differ'):repeat.require_receipt(p,dict(files,**{'scripts/worker.py':'changed'}),'manifest')
            Path(records[0]['case_events'][0]['probe_gradients'][0]['path']).write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'artifact'):repeat.require_receipt(p,files,'manifest')


if __name__=='__main__':unittest.main()
