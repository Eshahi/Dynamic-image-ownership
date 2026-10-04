"""CPU-only execution lifecycle/parity tests; no model inference."""
import copy
from pathlib import Path
import sys
import tempfile
import unittest

import torch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import m1_terminal_continuous as method


class RecoveryTests(unittest.TestCase):
    def test_model_placement_preserves_dtype_values_and_frozen_state(self):
        models=[torch.nn.Linear(3,2).to(dtype=d).requires_grad_(False).eval()
                for d in (torch.float16,torch.float32)]
        old=[copy.deepcopy(m.state_dict()) for m in models]
        sizes=method.move_inference_models(models,'cpu')
        self.assertEqual(sizes,[16,32])
        for model,state in zip(models,old):
            self.assertTrue(method.exact_tree_equal(model.state_dict(),state))
            self.assertFalse(model.training)
            self.assertFalse(any(p.requires_grad for p in model.parameters()))
        with self.assertRaises(ValueError):
            method.move_inference_models([torch.nn.Linear(2,2)],'cpu')

    def fixture(self,root):
        endpoint=dict(u=torch.ones((1,4,64,64)),optimizer={'state':{0:{'exp_avg':torch.ones(2)}}},
                      rng={'torch_cpu':torch.tensor([1,2],dtype=torch.uint8),'torch_cuda':[]},step=100)
        cases=[];all_rows=[]
        for name in ('old','fresh'):
            directory=root/name;directory.mkdir()
            path=directory/'step100.pt'
            torch.save(dict(endpoint,identity={'commit':name}),path)
            case=dict(source_id=1675,outcome='completed',source={'rgb8_sha256':'source'},
                      initialization={'sha256':'unmarked'},checkpoints=[dict(step=100,path=str(path),sha256=method.util.sha(path))])
            rows=[]
            for number in range(4):
                row=dict(id=f'1675-{number}',source_id=1675,outcome='completed',
                         owner_decisions={'alpha':{'s':5.0,'state':'both_match'}})
                for field in ('image','terminal_reader_latent','terminal_fp32_latent'):
                    artifact=directory/f'{number}-{field}.bin';artifact.write_bytes(f'{number}-{field}'.encode())
                    row[field]={'path':str(artifact),'sha256':method.util.sha(artifact)}
                rows.append(row)
            cases.append(case);all_rows.append(rows)
        reference={'case_events':[cases[0]],'conditions':all_rows[0]}
        return cases[1],all_rows[1],reference

    def test_replay_accepts_different_provenance_but_same_scientific_endpoint(self):
        with tempfile.TemporaryDirectory() as temp:
            current,rows,reference=self.fixture(Path(temp))
            value=method.verify_completed_case_replay(current,rows,reference)
            self.assertTrue(value['passed']);self.assertEqual(value['images'],4)
            self.assertFalse(value['provenance_identity_compared'])

    def test_replay_rejects_changed_endpoint_even_with_updated_file_receipt(self):
        for field in ('u','optimizer','rng','step'):
            with self.subTest(field=field),tempfile.TemporaryDirectory() as temp:
                current,rows,reference=self.fixture(Path(temp))
                receipt=current['checkpoints'][0];path=Path(receipt['path'])
                data=torch.load(path,weights_only=True)
                if field=='u':data['u'][0,0,0,0]=2
                elif field=='optimizer':data['optimizer']['state'][0]['exp_avg'][0]=2
                elif field=='rng':data['rng']['torch_cpu'][0]=2
                else:data['step']=90
                torch.save(data,path);receipt['sha256']=method.util.sha(path)
                with self.assertRaisesRegex(ValueError,'endpoint replay differs'):
                    method.verify_completed_case_replay(current,rows,reference)

    def test_replay_rejects_missing_modified_and_changed_decision_artifacts(self):
        for kind in ('missing','file','decision','initialization'):
            with self.subTest(kind=kind),tempfile.TemporaryDirectory() as temp:
                current,rows,reference=self.fixture(Path(temp))
                if kind=='missing':rows.pop()
                elif kind=='file':Path(rows[0]['image']['path']).write_bytes(b'changed')
                elif kind=='decision':rows[0]['owner_decisions']['alpha']['s']=4.5
                else:current['initialization']['sha256']='changed'
                with self.assertRaises(ValueError):method.verify_completed_case_replay(current,rows,reference)


if __name__=='__main__':unittest.main()
