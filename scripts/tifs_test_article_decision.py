"""Round 2 decision integration tests on synthetic JSON; no image or ML calls."""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
import tifs_stage_s_analyze as analysis
from tifs_test_stage_s_analyze import fixture, bound_call as call


class ArticleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = fixture()

    def values(self, vine_pass=False):
        values = copy.deepcopy(self.base)
        if vine_pass:
            for uid,row in values[4].items():
                if uid.startswith('det:vine-b:native:') and uid.endswith(':vine-b'):
                    row['calls'][values[0]['owners']['positive']] = call(True)
        return values

    def result(self, values):
        return analysis.analyze(*values)

    def test_f6_retention_edge_even_if_baseline_not_viable(self):
        result=self.result(self.values())
        self.assertEqual(result['verdict'],'GO')
        self.assertEqual(result['article']['verdict'],'F6_GO_ARTICLE_CONDITIONAL_GO')
        self.assertEqual(result['article']['baseline_viability'],'fail')

    def test_equal_baseline_removes_article_edge_without_changing_thesis(self):
        result=self.result(self.values(True))
        self.assertEqual(result['verdict'],'GO')
        self.assertEqual(result['article']['baseline_viability'],'pass')
        self.assertEqual(result['article']['verdict'],'F6_GO_NO_ARTICLE_EDGE')
        self.assertIn('NUMERICAL_PARITY',result['article']['flags'])
        self.assertEqual(result['article']['numerical_parity_status'],'pass')
        self.assertEqual(result['article']['human_quality_status'],'MISSING')

    def test_quality_superiority_requires_both_metrics(self):
        vals=self.values(True)
        for uid,row in vals[5].items():
            if uid.startswith('quality:clean:') and uid.endswith(':vine-b'):
                row['total']['lpips']=.013
        self.assertEqual(self.result(vals)['article']['verdict'],'F6_GO_NO_ARTICLE_EDGE')
        for uid,row in vals[5].items():
            if uid.startswith('quality:clean:') and uid.endswith(':vine-b'):
                row['total']['psnr_db']=38.5
        self.assertEqual(self.result(vals)['article']['verdict'],'F6_GO_ARTICLE_CONDITIONAL_GO')

    def test_vine_dominates_and_no_automatic_novelty_rescue(self):
        vals=self.values(True)
        for uid,row in vals[5].items():
            if uid.startswith('quality:clean:') and uid.endswith(':vine-b'):
                row['total'].update(lpips=.005,psnr_db=42)
        result=self.result(vals)
        self.assertEqual(result['verdict'],'GO')
        self.assertEqual(result['article']['verdict'],'F6_GO_VINE_B_DOMINATES_ARTICLE_NO_GO')
        self.assertIn('PREEMPTED',result['article']['generic_bound_carrier_novelty'])
        # A positive VINE-B primary negative invalidates its qualification only.
        uid=next(u for u in vals[4] if u.startswith('det:vine-b:clean:') and u.endswith(':unmarked'))
        vals[4][uid]['calls'][vals[0]['owners']['positive']]=call(True)
        result=self.result(vals)
        self.assertEqual(result['verdict'],'GO')
        self.assertEqual(result['article']['baseline_viability'],'fail')
        self.assertEqual(result['article']['verdict'],'F6_GO_NO_ARTICLE_EDGE')
        self.assertIn('VINE_B_SECURITY_SCREEN_FAIL',result['article']['flags'])

    def test_kill_labels_do_not_rescue_thesis(self):
        for vine_pass,label in ((True,'F6_KILL_VINE_B_VIABLE_NOT_NOVEL'),(False,'BOTH_FAIL')):
            vals=self.values(vine_pass)
            uid=next(u for u in vals[5] if u.startswith('quality:clean:') and u.endswith(':f6-noise'))
            vals[5][uid]['total']['psnr_db']=35
            result=self.result(vals)
            self.assertEqual(result['verdict'],'SCIENTIFIC_KILL')
            self.assertEqual(result['article']['verdict'],label)

    def test_missing_vine_reference_or_call_never_article_go(self):
        vals=self.values()
        uid=next(u for u in vals[4] if u.startswith('det:vine-b:native:') and u.endswith(':vine-b'))
        del vals[4][uid]
        result=self.result(vals)
        self.assertEqual(result['article']['verdict'],'INCOMPLETE')
        self.assertEqual(result['numerical_thesis_gate_status'],'pass')
        vals=self.values()
        uid=next(u for u in vals[5] if u.startswith('quality:clean:') and u.endswith(':vine-b'))
        vals[5][uid]['total']['lpips']=None
        result=self.result(vals)
        self.assertEqual(result['article']['verdict'],'INCOMPLETE')
        self.assertEqual(result['article']['f6_over_vine_b']['quality_noninferiority'][0]['status'],'unknown')

    def test_missing_bound_reference_never_hidden_by_majority_or_no_read(self):
        for field in ('q','h','bits'):
            for cell in ('R0-0.2','R1-0.1'):
                vals=self.values()
                uid=next(u for u in vals[3]['native'] if u.startswith('native:'+cell+':') and u.endswith(':vine-b'))
                del vals[3]['native'][uid]['payload'][field]
                result=self.result(vals)
                self.assertFalse(result['inventory_complete'],(cell,field))
                self.assertEqual(result['article']['verdict'],'INCOMPLETE')
                receipt=next(r for r in result['bound_carrier_delivery'] if r['item']==uid)
                self.assertEqual(receipt['status'],'invalid')

    def test_missing_bound_decode_or_delivery_metadata_is_incomplete(self):
        for field in ('carrier_decode','native','delivery'):
            vals=self.values()
            uid=next(u for u in vals[4] if u.startswith('det:vine-b:clean:') and u.endswith(':vine-b'))
            own=vals[4][uid]['calls'][vals[0]['owners']['positive']]
            del (own if field=='delivery' else own['raw'])[field]
            result=self.result(vals)
            self.assertFalse(result['inventory_complete'])
            self.assertEqual(result['article']['verdict'],'INCOMPLETE')

    def test_read_without_decoded_code_is_incomplete(self):
        for channel in ('semantic','instance'):
            vals=self.values()
            uid=next(u for u in vals[4] if u.startswith('det:vine-b:clean:') and u.endswith(':vine-b'))
            own=vals[4][uid]['calls'][vals[0]['owners']['positive']]
            del own['raw'][channel]['decoded_code']
            result=self.result(vals)
            self.assertFalse(result['inventory_complete'])
            self.assertEqual(result['article']['verdict'],'INCOMPLETE')

    def test_missing_run_seal_invalidates_article_without_losing_numeric_result(self):
        result=self.result(self.values(True))
        analysis.mark_provenance_missing(result)
        self.assertEqual(result['verdict'],'INCOMPLETE')
        self.assertEqual(result['article']['verdict'],'INCOMPLETE')
        self.assertEqual(result['article']['thesis_verdict'],'INCOMPLETE')
        self.assertEqual(result['numerical_thesis_gate_status'],'pass')
        self.assertEqual(result['article']['numerical_parity_status'],'unknown')
        self.assertNotIn('NUMERICAL_PARITY',result['article']['flags'])

    def test_quality_failure_is_explicit_without_automatic_article_edge(self):
        vals=self.values(True)
        uid=next(u for u in vals[5] if u.startswith('quality:clean:') and u.endswith(':vine-b'))
        vals[5][uid]['total']['psnr_db']=35
        result=self.result(vals)
        self.assertIn('VINE_B_QUALITY_INELIGIBLE',result['article']['flags'])
        self.assertEqual(result['article']['verdict'],'F6_GO_NO_ARTICLE_EDGE')

    def test_vine_combined_mode_required_without_extra_ablations(self):
        vals=self.values(True)
        threats=[r for r in self.result(vals)['threats'] if r['method']=='vine-b']
        self.assertEqual({r['mode'] for r in threats},{'combined'})
        self.assertEqual(len(threats),7)
        uid=next(u for u in vals[4] if u.startswith('det:vine-b:threat:') and ':vine-b:patch128' in u)
        del vals[4][uid]['modes']['combined']
        self.assertEqual(self.result(vals)['article']['verdict'],'INCOMPLETE')

    def test_retention_uses_both_C_and_J_same_cell(self):
        vals=self.values(True)
        # Baseline C stays high, J fails: not an F6 advantage on BOTH endpoints.
        for uid,row in vals[4].items():
            if uid.startswith('det:vine-b:native:R1-0.1:') and uid.endswith(':vine-b'):
                row['calls'][vals[0]['owners']['positive']]=call(True,exact=False)
        result=self.result(vals)
        self.assertEqual(result['article']['f6_over_vine_b']['retention_edge'],'fail')
        self.assertEqual(result['article']['verdict'],'F6_GO_NO_ARTICLE_EDGE')


if __name__=='__main__': unittest.main()
