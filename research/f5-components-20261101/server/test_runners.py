"""Pure logic integration checks; synthetic byte files only, no images/models."""
import argparse
import contextlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import common
import q_res


class Contracts(unittest.TestCase):
    def test_fixed_development_ids(self):
        self.assertEqual(len(set(common.S60)),60)
        self.assertEqual(sorted(common.S60),list(common.S60))
        self.assertEqual(sum(common.split(s)=='EVALUATE' for s in common.S12),6)
        self.assertEqual(common.load_config()['seeds'],[12,13,14])
        with self.assertRaises(ValueError): common.split(999999)

    def test_missing_seeds_are_failures_and_upper_separate(self):
        self.assertEqual(q_res.majority([True,None,False]),
                         dict(success=False,upper=True,positive_calls=1,missing_calls=1))
        self.assertFalse(q_res.majority([False,False,None])['upper'])
        self.assertTrue(q_res.majority([True,True,None])['success'])
        with self.assertRaises(ValueError): q_res.majority([True,1,None])

    def test_crossed_grid_and_calls(self):
        p=q_res.plan()
        self.assertEqual((p['images'],p['reader_calls'],p['new_marks']),(1440,3240,0))
        self.assertEqual(p['pilot']['images'],24)
        self.assertEqual(len({u['id'] for u in p['units']}),1440)
        self.assertAlmostEqual(p['scenarios']['area_scaled_assumption']['total_seconds'],6638.4)
        self.assertEqual(set(u['source_id'] for u in p['units']),set(common.S60))

    def test_vine_not_semantic(self):
        raw={'detections':{'vine-r':{common.ALPHA:{'status':'ok','presence':{'present':True},
                                                  'wrong_message_presence':{'present':False}}}}}
        self.assertIsNone(q_res.call_metrics(raw,'vine-r',common.ALPHA)['B'])
        self.assertTrue(q_res.call_metrics(raw,'vine-r',common.ALPHA)['presence'])
        self.assertFalse(q_res.call_metrics(raw,'vine-r',common.BETA)['presence'])
        self.assertIsNone(q_res.call_metrics({},'vine-r',common.ALPHA)['presence'])

    def test_no_paid_defaults(self):
        parser=argparse.ArgumentParser()
        common.add_execution_args(parser)
        args=parser.parse_args(['--execute'])
        with self.assertRaisesRegex(ValueError,'requires'): common.validate_args(args)
        for key in ('hourly','max_hours','max_usd'): self.assertIsNone(getattr(args,key))

    def test_guard_rejects_before_heavy_import(self):
        args=argparse.Namespace(assets='none',stage2a='none',stage2b='none',out='none',
                               instance_start='2026-11-01T00:00:00Z',hourly=.551,max_hours=4.,max_usd=3.)
        with patch.dict(os.environ,{'CUDA_VISIBLE_DEVICES':'-1'}):
            with self.assertRaisesRegex(RuntimeError,'hidden'): common.execution_context(args,'Q-RES')
        self.assertNotIn('encoder_transfer_runtime',sys.modules)
        self.assertNotIn('torch',sys.modules)

    def test_reader_preserves_native_endpoints_and_rejects_recomputed_rescue(self):
        def tier(score):
            return dict(decoded_score=score,decoded_code='00000000',recomputed_score=20.,
                        found=True,read=False,content_match=True)
        raw=dict(semantic=tier(1.),instance=tier(1.),semantic_code='00000000',perceptual_hash='00000000')
        fields=common.reader_fields(raw,dict(C=False,J=False,H=False))
        self.assertFalse(fields['B'])
        self.assertTrue(fields['O_U'])
        self.assertFalse(fields['C'])
        raw['semantic'].update(read=True,content_match=False)
        raw['instance']['decoded_score']=12.
        self.assertFalse(common.reader_fields(raw,dict(C=False,J=False,H=False))['B'])

    def test_journal_latest_and_torn_fail_closed(self):
        with tempfile.TemporaryDirectory(prefix='logic-',dir=Path(__file__).parent) as name:
            root=Path(name).resolve()
            self.assertTrue(root.is_relative_to(common.RD/'server'))
            path=root/'rows.jsonl'
            path.write_text('{"id":"x","status":"ok"}\n{"id":"x","status":"error"}\n',encoding='utf-8')
            self.assertEqual(common.journal_rows(path)['x']['status'],'error')
            path.write_text('{"id":"x"}',encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'Torn'): common.journal_rows(path)

    def test_saved_clean_resolver_uses_hash_and_retains_failure(self):
        with tempfile.TemporaryDirectory(prefix='logic-',dir=Path(__file__).parent) as name:
            root=Path(name).resolve()
            self.assertTrue(root.is_relative_to(common.RD/'server'))
            a,b=root/'stage2a-full',root/'stage2b-full'
            (a/'images').mkdir(parents=True); b.mkdir()
            output=a/'images/clean_30_unmarked_None_None.png'
            output.write_bytes(b'pure-logic bytes, never interpreted as an image')
            row=dict(id='clean:30:unmarked:None:None',source_id=30,arm='unmarked',channel='clean',status='ok',
                     output=dict(path='/workspace/runs/stage2a-full/images/'+output.name,sha256=common.digest(output)))
            (a/'rows.jsonl').write_text(json.dumps(row)+'\n',encoding='utf-8')
            (b/'rows.jsonl').write_text('',encoding='utf-8')
            self.assertEqual(common.clean_inputs(a,b,[30],['unmarked'])[(30,'unmarked')]['local_path'],str(output))
            output.write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'hash/path'): common.clean_inputs(a,b,[30],['unmarked'])
            (b/'rows.jsonl').write_text(json.dumps({**row,'status':'error'})+'\n',encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'Missing successful'): common.clean_inputs(a,b,[30],['unmarked'])

    def test_started_failure_is_not_success(self):
        row={**next(q_res.units()),'status':'running','detections':{'f5-r2':{common.ALPHA:{'status':'running'}}}}
        recovered,changed=q_res.interrupted(row)
        self.assertTrue(changed)
        self.assertEqual(recovered['status'],'interrupted')
        final=q_res.finalize(recovered)
        self.assertTrue(final['final'])
        self.assertEqual(final['detections']['f5-r2'][common.BETA]['status'],'input_missing')
        self.assertIsNone(q_res.call_metrics(final,'f5-r2',common.ALPHA)['B'])

    def test_empty_inventory_cannot_claim_survival(self):
        summary=q_res.analyze({})
        self.assertEqual(summary['scale']['verdict'],'PENDING_FIXED_INVENTORY')
        self.assertEqual(summary['scale']['sd15_gain_missing_bounds'],[-30,30])

    def test_q_res_self_test(self):
        self.assertEqual(q_res.self_test()['status'],'PASS')

    def test_q_stage_self_test(self):
        import q_stage
        self.assertEqual(q_stage.self_test()['status'],'PASS')

    def test_no_science_imports(self):
        for module in ('torch','numpy','PIL','diffusers','encoder_transfer_runtime'):
            self.assertNotIn(module,sys.modules)


if __name__=='__main__':
    unittest.main(verbosity=2)
