"""B-LW1 generated metadata fixtures: no image/model/scientific run access."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('family_lw',Path(__file__).resolve().parents[1]/'scripts/m1_analyze_families.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


def score(matches):
    return {'matches':matches,'bit_accuracy':matches/256,'present':matches>=180,'exact_message':matches==256,'tie_count':0}


def fixture():
    rows=[]
    channels=[('clean',None,None),('vae',None,None)]+[(f'regen-{s}-seed{a}',s,a) for s in (.05,.1,.2,.4) for a in (0,1,2)]
    for i in range(4):
        for arm in ('C0','C1'):
            for channel,strength,attack_seed in channels:
                matches=256 if arm=='C1' else 128
                native={'case':f'prompt-{i}','arm':arm,'channel':channel,'image_sha256':'a'*64,
                    'bit_accuracy':matches/256,'detected':matches>=180,'exact_payload':matches==256,
                    'wrong_key_bit_accuracy':.5,'wrong_key_detected':False,'detector_seconds':1,'detector_unet_evaluations':50}
                rows.append({'id':f'prompt-{i}-{arm}-{channel}','case':f'prompt-{i}','generation_seed':1000+i,'arm':arm,'channel':channel,'strength':strength,'attack_seed':attack_seed,
                    'outcome':'completed','native':native,'correct_key':score(matches),'wrong_key':score(128),'image_sha256':'a'*64,
                    'source_row_sha256':hashlib.sha256(json.dumps(native,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
                    'diagnostics':{'total_seconds':.1,'unet_evaluations':0}})
    return {'run':{'schema_version':'m1-gs-terminal-sign-v1','config':{'presence_matches':180},'data_split':'synthetic','expected_conditions':112},
        'conditions':rows,'errors':[],'source_outcome':'completed'}


class LightweightAnalysisTests(unittest.TestCase):
    def test_complete_plan_and_cluster_denominators(self):
        result=m.analyze_gs_lightweight(fixture())
        self.assertFalse(result['incomplete']);self.assertEqual(len(result['raw']),224)
        self.assertEqual(len(result['paired']),112);self.assertEqual(len(result['summary']),28)
        self.assertEqual(result['prompt_clusters'],4)
        self.assertTrue(all(g['carrier_gate'] for g in result['gates']))
        self.assertTrue(all(s['C1_present']==4 and s['C1_exact']==4 and s['C0_positive']==0 and s['C1_wrong_positive']==0 for s in result['summary']))

    def test_missing_condition_null_not_false(self):
        package=fixture();package['conditions']=package['conditions'][1:]
        result=m.analyze_gs_lightweight(package)
        self.assertTrue(result['incomplete'])
        self.assertTrue(all(g['carrier_gate'] is None for g in result['gates'] if g['channel']=='clean'))
        self.assertIsNone(result['paired'][0]['presence_cell'])

    def test_failed_lw_retains_native_only_observation(self):
        package=fixture();package['conditions'][0]['outcome']='failed'
        result=m.analyze_gs_lightweight(package)
        self.assertEqual(result['raw'][0]['status'],'observed')
        self.assertEqual(result['raw'][1]['status'],'missing_or_failed')
        self.assertIsNone(result['paired'][0]['native_matches_minus_lightweight'])

    def test_paired_native_only_cell_and_delta(self):
        package=fixture();row=next(r for r in package['conditions'] if r['arm']=='C1' and r['channel']=='clean')
        row['correct_key']=score(170)
        result=m.analyze_gs_lightweight(package)
        pair=next(r for r in result['paired'] if r['id']==row['id'])
        self.assertEqual(pair['presence_cell'],'native-only');self.assertEqual(pair['native_matches_minus_lightweight'],86)
        self.assertFalse(next(g['carrier_gate'] for g in result['gates'] if g['decoder']=='lightweight' and g['channel']=='clean'))

    def test_duplicate_unplanned_hash_and_score_rejections(self):
        for mutate in (lambda p:p['conditions'].append(copy.deepcopy(p['conditions'][0])),
                       lambda p:p['conditions'][0].update(id='unplanned'),
                       lambda p:p['conditions'][0].update(image_sha256='b'*64),
                       lambda p:p['conditions'][0]['correct_key'].update(present=True)):
            package=fixture();mutate(package)
            with self.assertRaises(ValueError):m.analyze_gs_lightweight(package)

    def test_pending_and_provenance_errors_null_gates(self):
        for changes in ({'source_outcome':'started'},{'errors':[{'error':'receipt mismatch'}]}):
            package=fixture();package.update(changes);result=m.analyze_gs_lightweight(package)
            self.assertTrue(result['incomplete']);self.assertTrue(all(g['carrier_gate'] is None for g in result['gates']))

    def test_loader_hashes_snapshots_without_opening_images(self):
        with tempfile.TemporaryDirectory() as temp:
            directory=Path(temp);package=fixture();run=package['run']
            manifest=directory/'fixture-manifest.json';m.write(manifest,{})
            run.update(command=['fixture','--manifest',str(manifest)],manifest_sha256=m.sha(manifest),outcome='completed',source_receipts={})
            for name in ('run.json','artifacts.json','rows.jsonl','rows-receipt.json'):
                snapshot=directory/('source-'+name);snapshot.write_text('{}',encoding='utf-8')
                run['source_receipts'][name]={'sha256':m.sha(snapshot),'path':'absent-native/'+name}
            m.write(directory/'conditions.json',package['conditions']);(directory/'rows.jsonl').write_text('',encoding='utf-8')
            run['output_hashes']={name:m.sha(directory/name) for name in ('conditions.json','rows.jsonl')}
            m.write(directory/'run.json',run)
            loaded=m.load_family('gs_lightweight',directory)
            self.assertEqual(loaded['errors'],[])
            (directory/'source-artifacts.json').write_text('corrupt',encoding='utf-8')
            loaded=m.load_family('gs_lightweight',directory)
            self.assertTrue(any(e['error']=='source snapshot hash mismatch' for e in loaded['errors']))


if __name__=='__main__':unittest.main()
