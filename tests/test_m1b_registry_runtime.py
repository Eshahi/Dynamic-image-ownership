import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import m1b_registry_runtime as R
import m1b_canonical_source as C

class RegistryGuards(unittest.TestCase):
    def plan(self):return json.loads((ROOT/'research/registry-confirmation/development.m1b-plan.json').read_text())
    def test_journal_uses_artifact_root(self):
        import tempfile
        import m1b_coco512_worker as W
        with tempfile.TemporaryDirectory() as d:
            out=Path(d);journal=W.Journal(out);journal.emit(dict(id="test",outcome="completed"))
            self.assertTrue((out/"outputs/journal.jsonl").is_file())
            self.assertEqual(len(W.Journal(out).rows),1)
    def test_fixed_values_and_index(self):
        p=self.plan();self.assertEqual(len(R.validate_plan(p)[1]),8)
        for field,value in [('seeds',[12,13,14]),('strengths',[.2]),('scenario_seeds',[12,13]),('sibling_seeds',[21])]:
            q=copy.deepcopy(p);q[field]=value
            with self.assertRaises(ValueError):R.validate_plan(q)
    def test_no_heldout_read_before_approval(self):
        with patch.object(Path,'read_bytes',side_effect=AssertionError('pixel read')):
            with self.assertRaises(PermissionError):C.registry_canonical({'raw_path':'heldout.png'},'test')
    def test_development_index_not_test(self):
        p=self.plan();p['data_split']='test'
        with self.assertRaises(ValueError):R.validate_plan(p)
    def test_heldout_metadata_valid_without_pixels(self):
        p=json.loads((ROOT/'research/registry-confirmation/test.m1b-plan.json').read_text())
        _,sources=R.validate_plan(p)
        self.assertEqual(len(sources),300)
        self.assertEqual(len({s['group_id'] for s in sources}),300)
    def test_footage_test_gate(self):
        from m1b_registry_footage import prepare_near
        with self.assertRaises(PermissionError):prepare_near({'data_split':'test'},Path('unused'),lambda:None)

if __name__=='__main__':unittest.main()
