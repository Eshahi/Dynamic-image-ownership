"""Metadata/inventory/resumption tests: no images, scores, models or GPU."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import m1_assess_dual_threats as assessor
import m1_analyze_dual_threats as analysis


class AssessmentProtocol(unittest.TestCase):
    def setUp(self):
        self.labels=json.loads(assessor.LABELS.read_text())['pairs']
        self.manifest=dict(schema=assessor.VERSION,data_split='development',route='pure-decoder',
            owners=list(assessor.v5.OWNERS),source_ids=list(assessor.protocol.EXPANDED_IDS),
            assets=str(assessor.ASSETS),attack_settings=copy.deepcopy(assessor.ATTACK_SETTINGS),
            labels_sha256=assessor.sha(assessor.LABELS),dependencies={p:'placeholder' for p in assessor.DEPENDENCIES},
            cases=[dict(id=i,raw_sha256=h,status='missing') for i,h in assessor.reservation().items()])
        self.manifest['cases'].sort(key=lambda x:assessor.protocol.EXPANDED_IDS.index(x['id']))

    def test_fixed_inventory_preserves_pairings_and_negative_controls(self):
        rows=assessor.validate(self.manifest)
        counts={a:sum(r['axis']==a for r in rows) for a in ('clean','T3','T4','T5','T5-transfer')}
        self.assertEqual(counts,{'clean':24,'T3':312,'T4':80,'T5':66,'T5-transfer':7})
        inherited=[r for r in assessor.v5.inventory(self.labels) if r['axis'] in ('T4','T5','T5-transfer')]
        self.assertEqual(rows[:153],inherited)
        self.assertEqual(len([r for r in rows if r.get('arm')=='unmarked_projection_sham']),20)
        for ident in assessor.protocol.EXPANDED_IDS:
            self.assertEqual(sum(r['axis']=='T3' and r['source_id']==ident for r in rows),26)

    def test_pilot_never_drops_missing_denominator(self):
        self.assertEqual(len(assessor.validate(self.manifest)),489)
        modified=copy.deepcopy(self.manifest); modified['cases']=modified['cases'][:2]
        with self.assertRaises(ValueError): assessor.validate(modified)

    def test_split_owner_schedule_and_reservation_are_locked(self):
        changes=[('data_split','heldout'),('route','auto'),('owners',['other']),
                 ('attack_settings',{}),('dependencies',{}),('source_ids',[1675])]
        for name,value in changes:
            m=copy.deepcopy(self.manifest);m[name]=value
            with self.subTest(name=name),self.assertRaises(ValueError): assessor.validate(m)
        m=copy.deepcopy(self.manifest);m['cases'][0]['raw_sha256']='0'*64
        with self.assertRaises(ValueError): assessor.validate(m)

    def test_corrupt_and_outside_resume_artifacts_are_not_completed(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);inside=root/'artifact.png';inside.write_bytes(b'not-an-image-just-hash-test')
            row={'outcome':'completed','image':{'path':str(inside),'sha256':assessor.sha(inside)},
                'detections':[{'owner':o,'result':{}} for o in assessor.v5.OWNERS],
                'quality_vs_same_arm_original':{},'quality_vs_source':{}}
            self.assertTrue(assessor.complete_artifact(row,root))
            inside.write_bytes(b'changed')
            self.assertFalse(assessor.complete_artifact(row,root))
            row['image']['sha256']=assessor.sha(inside)
            self.assertFalse(assessor.complete_artifact(row,root/'nested'))
            row['outcome']='failed'
            self.assertFalse(assessor.complete_artifact(row,root))

    def test_truncated_attempt_journal_does_not_swallow_next_record(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'rows.jsonl';path.write_text('{"interrupted":')
            assessor.append_jsonl(path,{'id':'next','outcome':'planned'})
            lines=path.read_text().splitlines()
            self.assertEqual(lines[0],'{"interrupted":')
            self.assertEqual(json.loads(lines[1])['id'],'next')

    def test_revised_semantic_labels_are_rejected(self):
        self.labels[0]['label']='different'
        with self.assertRaises(ValueError): assessor.planned(self.labels)

    def test_shard_order_code_locks_and_overlap_rejection(self):
        with tempfile.TemporaryDirectory() as directory:
            paths=[Path(directory)/name for name in ('first','second')]
            records=[]
            for i,p in enumerate(paths):
                p.mkdir()
                record={'schema':'A','data_split':'development','commit':str(i),
                    'profile':{'fixed':'profile'},'config':{'owner':assessor.v5.OWNERS[0],'routes':['pure-decoder']},
                    'committed_files':{'scripts/m1_dual_latent.py':{'git_blob_oid':'same-code'},
                        'research/different-shard-'+str(i)+'.json':{'git_blob_oid':str(i)}},
                    'cases':[{'id':assessor.protocol.EXPANDED_IDS[i]}]}
                records.append(record);assessor.write(p/'run.json',record)
            entries,receipts,reference=assessor.merge_enrollments(paths,'pure-decoder')
            self.assertEqual(list(entries),[1675,4795])
            self.assertEqual([r['commit'] for r in receipts],['0','1'])
            records[1]['cases'][0]['id']=1675;assessor.write(paths[1]/'run.json',records[1])
            with self.assertRaisesRegex(ValueError,'Overlapping'):assessor.merge_enrollments(paths,'pure-decoder')
            records[1]['cases'][0]['id']=4795
            records[1]['committed_files']['scripts/m1_dual_latent.py']['git_blob_oid']='changed-code'
            assessor.write(paths[1]/'run.json',records[1])
            with self.assertRaisesRegex(ValueError,'code version'):assessor.merge_enrollments(paths,'pure-decoder')

    def test_empty_analysis_preserves_all_planned_rows(self):
        raw,summary,errors=analysis.tables(assessor.planned(self.labels),[])
        self.assertEqual(len(raw),489);self.assertFalse(errors)
        self.assertEqual(sum(s['n_planned'] for s in summary),489)
        self.assertTrue(all(r['source_outcome']=='missing_condition' for r in raw))
        self.assertTrue(all(r['semantic_match_and_same_arm_quality'] is None for r in raw))

    def test_analysis_quality_thresholds_and_component_joint_are_strict(self):
        self.assertFalse(analysis.quality_pass({'psnr_db':35,'ssim_rgb':.99,'lpips':0}))
        self.assertFalse(analysis.quality_pass({'psnr_db':40,'ssim_rgb':.9,'lpips':0}))
        self.assertFalse(analysis.quality_pass({'psnr_db':40,'ssim_rgb':.99,'lpips':.1}))
        self.assertIsNone(analysis.quality_pass({'psnr_db':40,'ssim_rgb':.99}))
        spec={'id':'test','axis':'T3','source_id':1675,'control':'C1'}
        row=dict(spec,outcome='completed',quality_vs_same_arm_original={'psnr_db':40,'ssim_rgb':.99,'lpips':.01,'clip_cosine':.86},
            detections=[{'owner':assessor.v5.OWNERS[0],'result':{'semantic':{'content_match':True}}}])
        raw,_,errors=analysis.tables([spec],[row]);self.assertFalse(errors)
        self.assertTrue(raw[0]['semantic_match_and_same_arm_quality'])
        self.assertTrue(raw[0]['semantic_match_and_clip085_exploratory'])
        self.assertTrue(raw[0]['wrong_beta_missing'])

    def test_nonfinite_boolean_and_malformed_quality_are_missing(self):
        base={'psnr_db':40,'ssim_rgb':.95,'lpips':.05,'clip_cosine':.9}
        for field in ('psnr_db','ssim_rgb','lpips'):
            for invalid in (float('nan'),float('inf'),True,'40',[]):
                q=dict(base);q[field]=invalid
                with self.subTest(field=field,value=repr(invalid)):
                    self.assertIsNone(analysis.quality_pass(q))
        q=dict(base,psnr_db=None,psnr_infinite=True)
        self.assertTrue(analysis.quality_pass(q))
        self.assertIsNone(analysis.quality_pass(dict(base,psnr_infinite='yes')))
        self.assertFalse(analysis.quality_valid(dict(base,clip_cosine=float('nan')),include_clip=True))

    def completed_fixture(self,axis='T3'):
        q={'psnr_db':40,'psnr_infinite':False,'ssim_rgb':.95,'lpips':.05,'clip_cosine':.9}
        spec={'id':'fixture','axis':axis,'source_id':1675,'control':'C1'}
        row=dict(spec,outcome='completed',quality_vs_same_arm_original=copy.deepcopy(q),
            quality_vs_source=copy.deepcopy(q),paired_family_quality=copy.deepcopy(q),
            source_preservation_quality=copy.deepcopy(q),suspect_clip_seconds=.2,attack_seconds=1.,
            detections=[{'owner':o,'seconds':.5,'result':{'outcome':'both_match',
                'proposal_state':'authentic','qualified_state':'authentic-consistent',
                'semantic':{'found':True,'content_match':True},'instance':{'found':True,'content_match':True}}}
                for o in assessor.v5.OWNERS])
        return spec,row

    def test_channel_and_runtime_receipts_required_for_completeness(self):
        spec,row=self.completed_fixture()
        self.assertTrue(analysis.record_complete(spec,row))
        for mutation in ('channel','found','content_match','time','cliptime','attacktime','quality','owner'):
            changed=copy.deepcopy(row)
            if mutation=='channel':del changed['detections'][2]['result']['instance']
            elif mutation=='found':changed['detections'][1]['result']['semantic']['found']=1
            elif mutation=='content_match':del changed['detections'][3]['result']['instance']['content_match']
            elif mutation=='time':changed['detections'][0]['seconds']=float('nan')
            elif mutation=='cliptime':changed['suspect_clip_seconds']=True
            elif mutation=='attacktime':del changed['attack_seconds']
            elif mutation=='quality':changed['quality_vs_source']['lpips']=float('inf')
            else:changed['detections'][0]['owner']=None
            with self.subTest(mutation=mutation):self.assertFalse(analysis.record_complete(spec,changed))

    def test_clean_c1_requires_both_quality_references(self):
        spec,row=self.completed_fixture('clean')
        self.assertTrue(analysis.record_complete(spec,row))
        for field in ('paired_family_quality','source_preservation_quality'):
            changed=copy.deepcopy(row);del changed[field]
            self.assertFalse(analysis.record_complete(spec,changed))

    def test_t5_components_require_actual_finite_measurements(self):
        spec={'id':'pair','axis':'T5','left':1675,'right':4795}
        row=dict(spec,outcome='completed',components={c:{'semantic_hamming':4,'instance_hamming':18,'clip_cosine':.8} for c in ('C0','C1')})
        self.assertTrue(analysis.record_complete(spec,row))
        for field,bad in [('semantic_hamming',None),('instance_hamming',True),('clip_cosine',float('nan'))]:
            changed=copy.deepcopy(row);changed['components']['C1'][field]=bad
            self.assertFalse(analysis.record_complete(spec,changed))
        self.assertFalse(analysis.record_complete(spec,dict(row,components={'C0':{},'C1':{}})))

    def test_repeated_seeds_have_explicit_source_denominator(self):
        specs=[{'id':f'{ident}-{seed}','axis':'T3','source_id':ident,'control':'C1','dose':'diffusion','strength':.1,'seed':seed}
               for ident in (1675,4795) for seed in (0,1,2)]
        raw,summary,_=analysis.tables(specs,[])
        self.assertEqual(summary[0]['n_planned'],6)
        self.assertEqual(summary[0]['n_distinct_sources_planned'],2)
        self.assertEqual(summary[0]['n_distinct_seeds_planned'],3)
        self.assertEqual(summary[0]['n_distinct_sources_complete_records'],0)


if __name__=='__main__': unittest.main()
