import copy
from pathlib import Path
import sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import m1_scientific_analysis as a

def unit(n,role='marked-correct',**extra):
    return dict(id=str(n),method='candidate',source_uid='u'+str(n),group_id='g'+str(n),
      axis='clean',arm='C1',owner='fixture-owner',claim_role=role,kind='query',**extra)
def result(u,s=5,i=5):return dict(u,outcome='completed',decision=dict(s=s,i=i,**a.classify_scores(s,i)))

class AnalysisTests(unittest.TestCase):
    def test_missing_positive_and_negative_conservative_directions(self):
        p=[unit(0),unit(1)];r=a.analyze_verified_units(p,[result(p[0])])
        c=r['cells'][0]['endpoints']['both']['conservative']
        self.assertEqual((c['planned'],c['missing'],c['conservative_events']),(2,1,1))
        p=[unit(0,'marked-wrong'),unit(1,'marked-wrong')]
        c=a.analyze_verified_units(p,[result(p[0],0,0)])['cells'][0]['endpoints']['both']['conservative']
        self.assertEqual(c['conservative_events'],1)
    def test_semantic_support_is_not_false_attribution(self):
        p=[unit(0,'marked-wrong')];r=a.analyze_verified_units(p,[result(p[0],5,0)])
        e=r['cells'][0]['endpoints'];self.assertEqual(e['semantic']['supported'],1)
        self.assertNotIn('conservative',e['semantic']);self.assertEqual(e['both']['supported'],0)
    def test_invalid_score_or_plan_join_remains_missing(self):
        p=[unit(0),unit(1)];x=result(p[0]);x['decision']['state']='neither_supported'
        y=result(p[1]);y['owner']='changed'
        r=a.analyze_verified_units(p,[x,y]);self.assertEqual(len(r['invalid_observations']),2)
        self.assertEqual(r['cells'][0]['endpoints']['both']['missing'],2)
    def test_seeds_do_not_inflate_source_denominator(self):
        p=[unit(0),dict(unit(1),group_id='g0')]
        with self.assertRaisesRegex(ValueError,'Repeated cluster'):a.analyze_verified_units(p,[])
    def test_quality_strict_thresholds_and_absence(self):
        self.assertFalse(a.quality(dict(psnr_infinite=False,psnr_db=35,ssim_rgb=.9,lpips=.1))['joint'])
        self.assertTrue(a.quality(dict(psnr_infinite=True,psnr_db=None,ssim_rgb=1,lpips=0))['joint'])
        with self.assertRaises(ValueError):a.quality(dict(psnr_infinite=False,psnr_db=40,ssim_rgb=.99,lpips=None))
        p=[dict(unit(0),kind='image')];r=a.analyze_verified_units(p,[])
        self.assertEqual(r['clean_quality']['candidate']['missing'],1)
    def test_t4_recipient_has_no_false_attribution_target(self):
        u=dict(unit(0),axis='T4',claim_role='recipient',pair_index=0,patch_size=128,donor_arm='C1')
        r=a.analyze_verified_units([u],[result(u)])
        self.assertNotIn('conservative',r['cells'][0]['endpoints']['both'])
    def test_t3_cell_is_descriptive_without_clean_target(self):
        u=dict(unit(0),axis='T3',claim_role='correct',attack_channel={'id':'DDIM-s10-r0'})
        c=a.analyze_verified_units([u],[result(u)])['cells'][0]['endpoints']['both']['conservative']
        self.assertNotIn('meets_numerical_target',c)
    def test_v5_operating_profile_not_candidate_threshold(self):
        channel=dict(found=True,content_match=True,recomputed_threshold=a.V5_THRESHOLDS[0],decoded_threshold=a.V5_THRESHOLDS[1])
        d=dict(owners_tested=1,binding_mode='combined',embedding_domain='image',semantic=channel,instance=copy.deepcopy(channel),outcome='both_match',watermark_found=True)
        self.assertTrue(a.decisions('v5',d)['both'])
        d['semantic']['recomputed_threshold']=4
        with self.assertRaises(ValueError):a.decisions('v5',d)
    def test_t5_shortfall_and_duplicate_observation_rejected(self):
        self.assertFalse(a.analyze_verified_units([],[],t5_selected_pairs=0)['t5']['sufficient_fixed_coverage'])
        p=[unit(0)]
        with self.assertRaises(ValueError):a.analyze_verified_units(p,[result(p[0]),result(p[0])])

if __name__=='__main__':unittest.main()
