"""Synthetic CPU controls; no original transfer image is scored."""
import copy,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import m1_a_binding_ablation as a

class AblationTests(unittest.TestCase):
    def test_frozen_inventory_and_manifest_87_348(self):
        planned=a.fixed_inventory();self.assertEqual(len(planned),87)
        self.assertEqual(sum(r['axis']=='T4' for r in planned),80);self.assertEqual(sum(r['axis']=='T5-transfer' for r in planned),7)
        config=a.read(a.ROOT/'research/m1-A-binding-ablation-dev.json')
        self.assertEqual(config['planned_pngs'],87);self.assertEqual(config['planned_calls'],348)
        self.assertEqual(config['modes'],list(a.MODES));self.assertEqual(config['roster_size'],1)
    def test_missing_duplicate_and_altered_pair(self):
        rows=[dict(**r,outcome='completed') for r in a.fixed_inventory()]
        result,errors=a.transfer_rows(rows[:-1]);self.assertEqual(len(result),87);self.assertEqual(len(errors),1);self.assertEqual(result[-1]['outcome'],'missing')
        with self.assertRaisesRegex(ValueError,'duplicate'):a.transfer_rows(rows+[rows[0]])
        rows[0]['recipient_id']=999
        with self.assertRaisesRegex(ValueError,'membership'):a.transfer_rows(rows)
    def test_quality_strict_and_nonfinite(self):
        q=dict(psnr_db=35.1,psnr_infinite=False,mse_rgb8=1.,ssim_rgb=.95,lpips=.01)
        self.assertTrue(a.quality_pass(q));self.assertFalse(a.quality_pass(dict(q,psnr_db=35)))
        for key in ('psnr_db','mse_rgb8','ssim_rgb','lpips'):
            for value in (True,float('nan'),float('inf'),'1',None):self.assertIsNone(a.quality_pass(dict(q,**{key:value})))
    def channel(self,code='00000000',read=True,found=True,error=0.):
        return dict(decoded_code=code,read=read,found=found,decoding_error_rate=error)
    def test_unreadable_owner_presence_not_donor_attribution(self):
        actual=a.donor_channel(self.channel(read=False),'00000000',6)
        self.assertTrue(actual['carrier_found']);self.assertFalse(actual['donor_attributed']);self.assertIsNone(actual['donor_distance'])
    def test_corrected_distance_matches_existing_formula_boundary(self):
        result=a.donor_channel(self.channel(code='0000007f',error=.05),'00000000',6)
        self.assertEqual(result['donor_distance'],7);self.assertEqual(result['donor_corrected_distance'],6.)
        self.assertTrue(result['donor_attributed'])
        self.assertFalse(a.donor_channel(self.channel(code='000000ff',error=.05),'00000000',6)['donor_attributed'])
        with self.assertRaisesRegex(ValueError,'error rate'):a.donor_channel(self.channel(error=.5),'00000000',6)
    def test_sham_never_delivers_donor_and_components_separate(self):
        profile={'decision':{'semantic_radius':6,'instance_radius':6}}
        enrolled={'semantic_code':'00000000','perceptual_hash':'00000000'}
        result={'semantic':self.channel(),'instance':self.channel()}
        sham=a.delivery(result,enrolled,profile,'unmarked_projection_sham')
        self.assertTrue(sham['semantic']['donor_attributed']);self.assertFalse(sham['dual_donor_delivered'])
        result['instance']=self.channel(read=False)
        transfer=a.delivery(result,enrolled,profile,'clean_donor_residual')
        self.assertTrue(transfer['semantic_donor_delivered']);self.assertFalse(transfer['dual_donor_delivered'])
    def test_real_cpu_codec_binding_preserves_carrier_and_parity(self):
        rgb=np.full((256,256,3),128,np.uint8);feature=[1.]+[0.]*511
        profile=a.read(a.ROOT/'research/m1-A-binding-ablation-dev.json')['profile']
        calls=a.evaluate_modes(rgb,feature,profile)
        self.assertEqual(len(calls),4);self.assertTrue(all(c['outcome']=='completed' for c in calls))
        baseline=calls[0]['result']
        self.assertTrue(a.parity(baseline,copy.deepcopy(baseline)))
        for c in calls:
            self.assertEqual(c['result']['owners_tested'],1)
            for channel in ('semantic','instance'):
                for key in ('found','read','decoded_code','score','threshold'):self.assertEqual(c['result'][channel][key],baseline[channel][key])
        changed=copy.deepcopy(baseline);changed['semantic']['threshold']+=.01;self.assertFalse(a.parity(changed,baseline))
    def test_failed_call_retained_and_remaining_modes_attempted(self):
        captured=[]
        def detector(*args,**kwargs):
            self.assertEqual(kwargs['roster_size'],1);self.assertEqual(args[1],a.OWNER)
            if kwargs['binding_mode']=='none':raise RuntimeError('synthetic owned fixture')
            return {'outcome':'dummy'}
        output=a.evaluate_modes(np.zeros((2,2,3),np.uint8),[1.],{},detector=detector,callback=lambda rows:captured.append(rows))
        self.assertEqual(len(output),4);self.assertEqual(output[1]['outcome'],'failed');self.assertIn('synthetic',output[1]['error'])
        self.assertEqual([len(v) for v in captured],[1,2,3,4])
    def test_source_clusters_not_repeated_call_denominator(self):
        rows=[]
        for j in range(80):
            rows.append(dict(id=str(j),axis='T4',recipient_id=j%10,outcome='completed',strict_recipient_quality=True,
                delivery={'semantic_donor_delivered':True,'dual_donor_delivered':True},old_clip_receipt_equal=True,old_combined_parity=True,
                calls=[dict(outcome='completed',result={'outcome':'content_mismatch'}) for _ in range(4)]))
        summary=a.summarize(rows)[0]
        self.assertEqual(summary['planned_calls'],320);self.assertEqual(summary['completed_calls'],320)
        self.assertEqual(summary['dual_delivered_quality_recipient_n'],10);self.assertTrue(summary['minimum10_t4_dual_delivery_coverage'])
        for r in rows:
            if r['recipient_id']==0:r['strict_recipient_quality']=False
        summary=a.summarize(rows)[0];self.assertEqual(summary['dual_delivered_quality_recipient_n'],9);self.assertFalse(summary['minimum10_t4_dual_delivery_coverage'])
        rows[0]['outcome']='failed';self.assertIsNone(a.summarize(rows)[0]['minimum10_t4_dual_delivery_coverage'])
        self.assertIsNone(summary['security_verdict'])
    def test_parity_requires_mandatory_channels(self):
        with self.assertRaisesRegex(ValueError,'Missing detector'):a.parity({'outcome':'x'},{'outcome':'x'})

if __name__=='__main__':unittest.main()
