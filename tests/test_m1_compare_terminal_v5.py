"""Fabricated fixtures: threshold parity, attrition, source pairing and hash integrity."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SPEC=importlib.util.spec_from_file_location('compare',Path(__file__).resolve().parents[1]/'scripts/m1_compare_terminal_v5.py')
m=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


def decision(s=4.,i=4.):
    flags={'s':s>=4,'i':i>=4}
    return dict(s=s,i=i,flags=flags,state=('both_match' if flags['i'] else 'semantic_only') if flags['s'] else (
        'ambiguous_instance_only' if flags['i'] else 'neither_supported'))


def fixtures():
    specs=m.selected()+m.selected('C0')
    candidate=[dict(**r,verified=True,input_outcome='completed',
                    blind={o:decision() for o in m.OWNERS},quality_pass=False) for r in specs]
    baseline=[]
    for r in specs:
        ds=[]
        for owner in m.OWNERS:
            channel=dict(recomputed_threshold=m.RECOMPUTED,decoded_threshold=m.DECODED,content_match=False,found=True)
            ds.append(dict(claimed_owner=owner,binding_mode='combined',result=dict(owners_tested=4,binding_mode='combined',
                embedding_domain='image',semantic=channel,instance=channel,outcome='neither_match',watermark_found=True)))
        baseline.append(dict(**r,detection_complete=True,status='metrics_complete',detections=ds,
                             image={'pixel_sha256':'a'*64}))
    cases=[dict(id=s,source={'rgb8_sha256':'a'*64}) for s in m.EXPANDED_IDS]
    return candidate,baseline,specs,cases


class ComparisonTests(unittest.TestCase):
    def test_dependent_descriptive_denominators_and_distinct_decisions(self):
        result=m.compare_rows(*fixtures())
        self.assertEqual([r['planned'] for r in result['groups']],[12,10,30,30,30])
        self.assertEqual(result['groups'][2]['source_clusters'],10)
        self.assertEqual(result['groups'][0]['candidate']['both'],12)
        self.assertEqual(result['groups'][0]['v5']['both'],0)
        self.assertEqual(result['groups'][0]['v5']['semantic_found'],12)
        self.assertIsNone(result['groups'][0]['candidate']['semantic_found'])
        self.assertEqual(result['negative_slots']['candidate']['planned'],784)

    def test_missing_and_adverse_preserve_planned_denominator(self):
        a,b,s,c=fixtures()
        a[0]=dict(s[0],verified=False,input_outcome='safety_blocked')
        b.pop(1)
        result=m.compare_rows(a,b,s,c)['groups'][0]
        self.assertEqual((result['planned'],result['paired_observed'],result['paired_unavailable']),(12,10,2))
        self.assertEqual(result['candidate']['outcomes']['safety_blocked'],1)
        self.assertEqual(result['v5']['outcomes']['missing'],1)
        self.assertEqual(result['candidate']['missing_or_adverse'],1)

    def test_threshold_boundary_and_parity_rejection(self):
        a,b,s,c=fixtures()
        a[0]['blind'][m.OWNERS[0]]=decision(4.,3.999999)
        result=m.compare_rows(a,b,s,c)
        self.assertEqual(result['rows'][0]['candidate']['state'],'semantic_only')
        a[0]['blind'][m.OWNERS[0]]['flags']['i']=True
        with self.assertRaisesRegex(ValueError,'parity'):m.compare_rows(a,b,s,c)

    def test_source_and_schedule_mismatch_reject(self):
        a,b,s,c=fixtures()
        c[0]['source']['rgb8_sha256']='b'*64
        with self.assertRaisesRegex(ValueError,'source pixel hash'):m.compare_rows(a,b,s,c)
        a,b,s,c=fixtures()
        s[0]['source_id']=999
        with self.assertRaisesRegex(ValueError,'schedule'):m.compare_rows(a,b,s,c)

    def test_baseline_operating_metadata_and_duplicates_reject(self):
        a,b,s,c=fixtures()
        b[0]['detections'][0]['result']['owners_tested']=1
        with self.assertRaisesRegex(ValueError,'operating'):m.compare_rows(a,b,s,c)
        with self.assertRaisesRegex(ValueError,'Duplicate'):m.index([a[0],a[0]])

    def test_input_hash_rejection(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'run.json'
            p.write_text('{}',encoding='utf-8')
            pinned=m.sha(p)
            self.assertEqual(m.read(p,pinned),{})
            p.write_text('{"changed":true}',encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'SHA-256'):m.read(p,pinned)
            with self.assertRaisesRegex(ValueError,'SHA-256'):m.load_inputs(p,pinned)

    def test_analysis_output_inventory_rejection(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'run.json'
            p.write_text(json.dumps(dict(schema='m1-terminal-e2e-threat-analysis-v1',data_split='development',
                outcome='completed',errors=[],outputs={'conditions.json':'0'*64})),encoding='utf-8')
            (p.parent/'conditions.json').write_text('[]',encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'output hash inventory'):m.load_inputs(p,m.sha(p))


if __name__=='__main__':unittest.main()
