"""Synthetic CPU contract/owned-fixture tests; no models, scientific data or gates."""
import copy
import json
import os
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch
import zlib
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import m1_confirmatory_worker_contract as worker


def plan(n=2):
    return dict(schema=worker.SCHEMA,mode='synthetic-only',candidate='UNRESOLVED',units=[
        dict(id=f'fixture-{i}',source_uid=f'generated:{i}',group_id=f'fixture-group-{i}',method='candidate',
            axis='clean',arm='C1',owner='fixture-owner',seed_uint64_hex=f'{2**64-1-i:016x}',dependencies=[])
        for i in range(n)])


def fixture(fail=None):return dict(width=16,height=12,fail_phase=fail,delay_seconds=0)


class ContractTests(unittest.TestCase):
    def setUp(self):
        root=ROOT/'.thesis-build/rehearsal';root.mkdir(parents=True,exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(prefix='worker-contract-test-',dir=root)
        self.output=Path(self.temp.name)
    def tearDown(self):self.temp.cleanup()
    def test_uint64_and_fixed_missing_inventory(self):
        p=plan();row=worker.execute_fixture(p,'fixture-0',fixture(),self.output)
        ledger=worker.reconcile(p,[row],self.output)
        self.assertEqual(len(ledger),2);self.assertEqual(ledger[0]['seed_uint64_hex'],'ffffffffffffffff')
        self.assertEqual(ledger[1]['outcome'],'planned');self.assertEqual(ledger[1]['reason'],'not_attempted')
        self.assertIsNone(ledger[0]['human_visual_verdict']);self.assertEqual(ledger[0]['scientific_verdict'],'NOT_EVIDENCE')
    def test_generated_rgb8_png_crc_and_determinism(self):
        data,h=worker.fixture_png(16,12,2**64-1)
        self.assertEqual((data,h),worker.fixture_png(16,12,2**64-1))
        self.assertTrue(data.startswith(b'\x89PNG\r\n\x1a\n'))
        pos=8;parts={}
        while pos<len(data):
            size=struct.unpack('>I',data[pos:pos+4])[0];tag=data[pos+4:pos+8];value=data[pos+8:pos+8+size]
            crc=struct.unpack('>I',data[pos+8+size:pos+12+size])[0]
            self.assertEqual(zlib.crc32(tag+value)&0xffffffff,crc);parts[tag]=value;pos+=12+size
        self.assertEqual(struct.unpack('>IIBBBBB',parts[b'IHDR']),(16,12,8,2,0,0,0))
        scan=zlib.decompress(parts[b'IDAT']);pixels=b''.join(scan[y*49+1:(y+1)*49] for y in range(12))
        import hashlib
        self.assertEqual(hashlib.sha256(pixels).hexdigest(),h)
    def test_scientific_rejected_before_io(self):
        p=plan();p.update(mode='scientific',candidate='A-C')
        with patch.object(Path,'mkdir',side_effect=AssertionError('I/O reached')):
            with self.assertRaisesRegex(ValueError,'unlock unavailable'):worker.execute_fixture(p,'fixture-0',fixture(),self.output/'no-create')
        self.assertFalse((self.output/'no-create').exists())
    def test_no_external_source_fields_or_float_seed(self):
        p=plan();p['units'][0]['raw_path']='DO-NOT-OPEN'
        with self.assertRaises(ValueError):worker.validate_plan(p)
        p=plan();p['units'][0]['seed_uint64_hex']=float(2**64-1)
        with self.assertRaises(ValueError):worker.validate_plan(p)
        with self.assertRaises(ValueError):worker.validate_fixture(dict(fixture(),raw_path='DO-NOT-OPEN'))
    def test_duplicate_extra_and_dependency_cycles(self):
        p=plan();p['units'][1]['id']='fixture-0'
        with self.assertRaises(ValueError):worker.initial_inventory(p)
        p=plan();p['units'][0]['dependencies']=['fixture-1'];p['units'][1]['dependencies']=['fixture-0']
        with self.assertRaisesRegex(ValueError,'Cyclic'):worker.validate_plan(p)
        p=plan();p['units'][0]['dependencies']=['unknown']
        with self.assertRaisesRegex(ValueError,'Undeclared'):worker.validate_plan(p)
        with self.assertRaises(ValueError):worker.reconcile(plan(),[{'id':'unknown'}],self.output)
    def test_corrupt_missing_artifact_keeps_failed_row(self):
        p=plan(1);row=worker.execute_fixture(p,'fixture-0',fixture(),self.output)
        image=self.output/row['artifacts'][0]['path'];image.write_bytes(b'bad')
        ledger=worker.reconcile(p,[row],self.output)
        self.assertEqual(len(ledger),1);self.assertEqual(ledger[0]['outcome'],'failed')
        self.assertIn('corrupt artifact',ledger[0]['reason']);self.assertEqual(ledger[0]['observed'],row)
        image.unlink();self.assertEqual(worker.reconcile(p,[row],self.output)[0]['outcome'],'failed')
    def test_failures_preserve_partial_stage_and_png(self):
        for phase in ('generate','save','finalize'):
            p=plan(1);target=self.output/phase
            row=worker.execute_fixture(p,'fixture-0',fixture(phase),target)
            self.assertEqual(row['outcome'],'failed');self.assertIn(phase,row['reason'])
            self.assertEqual(len(row['artifacts']),1 if phase=='finalize' else 0)
            self.assertEqual(worker.reconcile(p,[row],target)[0]['outcome'],'failed')
    def test_transitive_dependency_failure_order_independent(self):
        p=plan(3);p['units'][0]['dependencies']=['fixture-1'];p['units'][1]['dependencies']=['fixture-2']
        rows=[worker.execute_fixture(p,f'fixture-{i}',fixture('generate' if i==2 else None),self.output) for i in range(3)]
        ledger=worker.reconcile(p,rows,self.output)
        self.assertEqual([r['outcome'] for r in ledger],['failed']*3)
        self.assertEqual(ledger[0]['reason'],'dependency_not_completed')
    def test_nonfinite_duration_and_incomplete_stage(self):
        p=plan(1);row=worker.execute_fixture(p,'fixture-0',fixture(),self.output)
        for value in (None,float('nan'),float('inf'),True,-1):
            bad=copy.deepcopy(row);bad['duration_seconds']=value
            self.assertEqual(worker.reconcile(p,[bad],self.output)[0]['outcome'],'failed')
        bad=copy.deepcopy(row);bad['stages'][0]['outcome']='started'
        self.assertEqual(worker.reconcile(p,[bad],self.output)[0]['outcome'],'failed')
    def test_paths_duplicate_results_and_no_overwrite(self):
        for path in ('../escape.png','C:/escape.png','outputs/../escape.png','outputs\\image.png'):
            with self.assertRaises(ValueError):worker.safe_artifact(self.output,path)
        p=plan(1);row=worker.execute_fixture(p,'fixture-0',fixture(),self.output)
        with self.assertRaises(ValueError):worker.reconcile(p,[row,row],self.output)
        with self.assertRaisesRegex(ValueError,'overwrite'):worker.execute_fixture(p,'fixture-0',fixture(),self.output)
        with self.assertRaisesRegex(ValueError,'rehearsal'):worker.execute_fixture(p,'fixture-0',fixture(),ROOT/'research/no-fixture')
    def test_other_condition_artifact_is_not_valid_completion(self):
        p=plan();rows=[worker.execute_fixture(p,f'fixture-{i}',fixture(),self.output) for i in range(2)]
        rows[1]['artifacts']=copy.deepcopy(rows[0]['artifacts'])
        ledger=worker.reconcile(p,rows,self.output)
        self.assertEqual(ledger[1]['outcome'],'failed');self.assertIn('namespace',ledger[1]['reason'])
    def test_versioned_fixture_plan_is_valid(self):
        fixture_doc=json.loads((ROOT/'research/m1-confirmatory-worker-fixture.json').read_text(encoding='utf-8'))
        worker.validate_plan(fixture_doc['plan']);worker.validate_fixture(fixture_doc['fixture'])
        self.assertEqual(fixture_doc['plan']['candidate'],'UNRESOLVED')
    @unittest.skipUnless(os.name=='nt','Windows owned fixture child')
    def test_owned_generated_image_child(self):
        row=worker.launch_fixture(plan(1),'fixture-0',fixture(),self.output,timeout_seconds=5)
        self.assertEqual(row['outcome'],'completed')
        states=json.loads((self.output/'fixture-ownership.json').read_text())
        self.assertEqual([r['state'] for r in states[:3]],['created_suspended','assigned_suspended','running'])
        self.assertTrue(states[1]['assignment_verified']);self.assertTrue(states[0]['kill_on_close'])
        self.assertEqual(worker.reconcile(plan(1),[row],self.output)[0]['outcome'],'completed')
    @unittest.skipUnless(os.name=='nt','Windows owned fixture timeout')
    def test_owned_timeout_preserves_ownership_and_plan_inventory(self):
        with self.assertRaises(TimeoutError):worker.launch_fixture(plan(2),'fixture-0',dict(fixture(),delay_seconds=1),self.output,timeout_seconds=.05)
        states=json.loads((self.output/'fixture-ownership.json').read_text());self.assertTrue(states[1]['assignment_verified'])
        final=json.loads((self.output/'fixture-ownership-final.json').read_text());self.assertEqual(final['state'],'closed')
        ledger=json.loads((self.output/'checkpoints/fixture-inventory.json').read_text())
        self.assertEqual(len(ledger),2);self.assertEqual(ledger[0]['outcome'],'timeout');self.assertEqual(ledger[1]['reason'],'not_attempted')

if __name__=='__main__':unittest.main()
