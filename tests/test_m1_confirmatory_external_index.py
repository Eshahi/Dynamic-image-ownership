"""Metadata-only synthetic joins; no image/annotation paths are followed."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import m1_confirmatory_external_index as index


def fixtures():
    sources=[];splits=[]
    for i in range(1,301):
        raw_hash=hashlib.sha256(('fixture-raw-'+str(i)).encode()).hexdigest()
        group=hashlib.sha256(('fixture-component-'+str(i)).encode()).hexdigest()
        source=dict(domain='ms-coco',release_id='coco-2017',source_split='val2017',source_id=str(i),relative_path=f'val2017/val2017/{i:012d}.jpg',raw_sha256=raw_hash,raw_size_bytes='123',group_id='raw-'+raw_hash,source_url='https://example.invalid/coco2017.zip',license_reference='https://example.invalid/license',rights_status='pending-image-rights',use_limitations='synthetic metadata fixture only')
        sources.append(source)
        splits.append(dict(source_uid=index.uid(source),domain='ms-coco',release_id='coco-2017',source_split='val2017',source_id=str(i),raw_sha256=raw_hash,group_id=group,study_split='test',primary_group_representative='true'))
    schedule=index.derive_schedule(splits)
    config=dict(source_manifest='data/b4-admission-20260926/source-manifest.csv',manifest_sha256=index.PINS['data/b4-admission-20260926/source-manifest.csv'],scientific_compute_authorized=False,final_scientific_split_accepted=False)
    acquisition=dict(annotations=[dict(name='instances_val2017.json',sha256='a'*64,bytes=19987840)],archive_hashes_available=False)
    return schedule,sources,splits,config,acquisition


class ExternalIndexTests(unittest.TestCase):
    def test_exact300_join_determinism_and_no_filesystem_access(self):
        args=fixtures()
        with patch.object(Path,'read_bytes',side_effect=AssertionError('raw read')),patch.object(Path,'stat',side_effect=AssertionError('raw stat')),patch.object(Path,'resolve',side_effect=AssertionError('raw resolve')):
            a=index.assemble(*args);b=index.assemble(*args)
        self.assertEqual(a,b);self.assertTrue(a['metadata_readiness']['raw_index_ready']);self.assertEqual(len(a['entries']),300)
        self.assertFalse(a['scientific_unlock']);self.assertFalse(a['source_contract_accepted']);self.assertFalse(a['images_annotations_features_opened'])
        self.assertEqual([e['source_uid'] for e in a['entries']],[e['source_uid'] for e in args[0]['clean']])
        self.assertNotEqual(a['entries'][0]['group_id'],a['entries'][0]['source_manifest_raw_group_id'])
    def test_missing_source_receipt_preserves_denominator(self):
        args=list(fixtures());args[1]=args[1][1:];r=index.assemble(*args)
        self.assertEqual(len(r['entries']),300);self.assertEqual(r['metadata_readiness']['existing_raw_receipts_ready'],299)
        self.assertFalse(r['metadata_readiness']['raw_index_ready']);self.assertTrue(r['input_errors'])
        missing=next(e for e in r['entries'] if e['source_uid'].endswith(':1'))
        self.assertIsNone(missing['external_raw_path']);self.assertIn('missing_admitted_source_receipt',missing['errors'])
    def test_source_hash_mismatch_and_malformed_receipt_preserved(self):
        args=list(fixtures());args[1][0]['raw_sha256']='b'*64;args[1][1]['raw_size_bytes']='0'
        r=index.assemble(*args);self.assertEqual(r['metadata_readiness']['existing_raw_receipts_ready'],298)
        self.assertTrue(any('raw_hash_mismatch' in x['reason'] for x in r['input_errors']))
    def test_frozen_subset_group_seed_and_unlock_tamper_rejected(self):
        for modification in ('subset','group','seed','unlock','candidate'):
            args=list(fixtures())
            if modification=='subset':args[0]['clean'].pop()
            elif modification=='group':args[0]['clean'][0]['group_id']='wrong'
            elif modification=='seed':args[0]['clean'][0]['seed_uint64_hex']='0'*16
            elif modification=='unlock':args[0]['scientific_run_authorized']=True
            elif modification=='candidate':args[0]['candidate']='A-C'
            with self.assertRaises(ValueError):index.assemble(*args)
    def test_duplicates_and_wrong_authority_rejected(self):
        args=list(fixtures());args[1].append(copy.deepcopy(args[1][0]))
        with self.assertRaisesRegex(ValueError,'Duplicate authoritative'):index.assemble(*args)
        args=list(fixtures());args[3]['source_manifest']='data/manifest.csv'
        with self.assertRaisesRegex(ValueError,'authoritative'):index.assemble(*args)
    def test_lexical_path_guards_and_no_follow(self):
        for bad in ('../image.jpg','/absolute.jpg','C:/absolute.jpg','val2017\\image.jpg','val2017//image.jpg','val2017/./image.jpg','val2017/../image.jpg','a\0b'):
            with self.assertRaises(ValueError):index.safe_relative(bad)
        args=list(fixtures());args[1][0]['relative_path']='../DO-NOT-OPEN.jpg'
        with patch.object(Path,'read_bytes',side_effect=AssertionError('followed raw path')):
            r=index.assemble(*args)
        self.assertEqual(r['metadata_readiness']['existing_raw_receipts_ready'],299)
    def test_annotation_file_receipt_does_not_invent_archive(self):
        r=index.assemble(*fixtures());a=r['annotation']
        self.assertEqual(a['sha256'],'a'*64);self.assertEqual(a['size_bytes'],19987840)
        self.assertIsNone(a['archive_sha256']);self.assertIsNone(a['archive_revision']);self.assertFalse(a['values_opened'])
        self.assertTrue(r['metadata_readiness']['complete_protocol_receipts_ready'])
        self.assertFalse(r['metadata_readiness']['annotation_archive_identity_required_for_extracted_artifact'])
        self.assertTrue(a['external_path'].endswith('/annotations_trainval2017/annotations/instances_val2017.json'))
    def test_annotation_missing_bad_duplicate_and_changed_archive_schema(self):
        for change in ('missing','bad','duplicate','archive'):
            args=list(fixtures());a=args[4]
            if change=='missing':a['annotations']=[]
            elif change=='bad':a['annotations'][0]['sha256']='unknown'
            elif change=='duplicate':a['annotations']*=2
            else:a['archive_hashes_available']=True
            with self.assertRaises(ValueError):index.assemble(*args)
    def test_unknown_metadata_input_rejected_before_read(self):
        with patch.object(Path,'read_bytes',side_effect=AssertionError('metadata raw follow')):
            with self.assertRaises(ValueError):index.read_pinned_metadata(ROOT,'data/raw/DO-NOT-OPEN.jpg','a'*64)

if __name__=='__main__':unittest.main()
