"""CPU synthetic fixtures: denominators, cap replay and endpoint corruption."""
import copy, hashlib, json, math, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import m1_analyze_terminal_continuous as a

class AnalysisTests(unittest.TestCase):
    def test_inventory_missing_duplicate_and_wrong_membership(self):
        rows=a.runner.planned();selected,errors=a.inventory(rows)
        self.assertFalse(errors);self.assertEqual(len(selected),8)
        selected,errors=a.inventory(rows[:-1]+[rows[0]])
        self.assertIsNone(selected[rows[0]['id']]);self.assertIsNone(selected[rows[-1]['id']]);self.assertEqual(len(errors),2)
        rows[0]['source_id']=999
        self.assertIsNone(a.inventory(rows)[0][rows[0]['id']])
    def test_quality_rejects_nonfinite_boolean_and_strict_boundary(self):
        q=dict(psnr_infinite=False,psnr_db=35.1,mse_rgb8=1,ssim_rgb=.95,lpips=.01)
        self.assertTrue(a.quality_pass(q))
        self.assertFalse(a.quality_pass(dict(q,psnr_db=35)))
        for field in ('psnr_db','mse_rgb8','ssim_rgb','lpips'):
            for value in (True,float('nan'),float('inf'),'1',None):self.assertIsNone(a.quality_pass(dict(q,**{field:value})))
        self.assertIsNone(a.quality_pass(dict(q,psnr_infinite=True)))
    def test_cap_roundtrip_exact_and_budget(self):
        source=np.full((32,32,3),127,np.uint8);delta=np.full(source.shape,.15,np.float64)
        actual,receipt=a.cap(source,delta);expected,ref=a.runner.residual.cap(source,delta)
        np.testing.assert_array_equal(actual,expected);self.assertEqual(receipt,ref)
        self.assertLessEqual(receipt['mse_rgb8'],receipt['budget_mse_rgb8']);self.assertEqual(receipt['iterations'],36)
        unchanged,r=a.cap(source,np.zeros_like(delta));np.testing.assert_array_equal(source,unchanged);self.assertEqual(r['weight'],1)
    def successful_rows(self):
        result={}
        for r in a.runner.planned():
            decisions={o:dict(s=0.,i=0.,flags={'s':False,'i':False},state='neither_supported') for o in a.core.OWNERS}
            if r['control']=='C1':decisions[a.core.OWNERS[0]]=dict(s=6.,i=8.,flags={'s':True,'i':True},state='both_match')
            result[r['id']]=dict(**r,verified=True,quality_pass=True,blind_both=r['control']=='C1',blind_semantic=r['control']=='C1',blind=decisions)
        return result
    def test_strict_promotion_and_missing_not_negative(self):
        rows=self.successful_rows();self.assertTrue(a.gates(rows,True)['promotion'])
        self.assertIsNone(a.gates(rows,False)['promotion'])
        rows.pop('1675-C0-clean');g=a.gates(rows,True)
        self.assertEqual(g['negative_queries']['planned'],28);self.assertEqual(g['negative_queries']['observed'],24);self.assertIsNone(g['promotion'])
    def test_instance_only_and_negative_boundary_fail(self):
        rows=self.successful_rows();rows['1675-C1-clean']['blind_both']=False
        self.assertFalse(a.gates(rows,True)['promotion'])
        rows=self.successful_rows();rows['1675-C0-clean']['blind'][a.core.OWNERS[0]]['i']=4.
        self.assertFalse(a.gates(rows,True)['promotion'])
    def test_float64_score_independent_manual_dot(self):
        e=np.arange(1,513,dtype=np.float64);e/=np.linalg.norm(e);t=a.core.template(e,123,a.core.OWNERS[0]);z=t['T']
        actual=a.core.scores(z,e,123,a.core.OWNERS[0])
        for c in ('s','i'):
            w=z[t['coords_'+c]]*t['v_'+c]
            self.assertAlmostEqual(actual[c],float(np.dot(w,t['r_'+c])/np.linalg.norm(w)),places=12)
        self.assertEqual(actual['state'],'both_match')
    def test_receipts_hash_paths_and_array_finiteness(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'a.npy';np.save(p,np.ones(3,np.float64))
            receipt=dict(path=str(p),sha256=a.sha(p));audit=a.Audit(directory)
            np.testing.assert_array_equal(audit.receipt(receipt,'a',array=True),np.ones(3))
            with self.assertRaisesRegex(ValueError,'duplicate'):audit.receipt(receipt,'b',array=True)
            with self.assertRaisesRegex(ValueError,'hash mismatch'):a.Audit(directory).receipt(dict(receipt,sha256='0'*64),'a')
            np.save(p,np.array([float('nan')]))
            with self.assertRaisesRegex(ValueError,'finite float64'):a.Audit(directory).receipt(dict(receipt,sha256=a.sha(p)),'a',array=True)
    def fixture(self,directory):
        rid='1675-C1-clean';rgb=np.full((512,512,3),128,np.uint8)
        e=np.zeros(512,np.float64);e[0]=1.;h=0;z=a.core.template(e,h,a.core.OWNERS[0])['T'].copy()
        def save(name,value,image=False):
            p=Path(directory)/name
            if image:Image.fromarray(value).save(p)
            else:np.save(p,value)
            r=dict(path=str(p),sha256=a.sha(p))
            if image:r['rgb8_sha256']=hashlib.sha256(value.tobytes()).hexdigest()
            return r
        receipt=save(rid+'.png',rgb,True);q=a.quality(rgb,rgb);q.update(lpips=0.,quality_admissible=True)
        row=dict(id=rid,source_id=1675,control='C1',dose='clean',outcome='completed',image=receipt,source=receipt,
            suspect_E=e.tolist(),suspect_H=h,source_clip_cosine=1.,source_phash_distance=0,
            terminal_reader_latent=save(rid+'-reader-z.npy',z),terminal_fp32_latent=save(rid+'-fp32-z.npy',z),
            owner_decisions={o:a.core.scores(z,e,h,o) for o in a.core.OWNERS},
            source_template_oracle_fp16=a.core.scores(z,e,h,a.core.OWNERS[0]),source_template_oracle_fp32=a.core.scores(z,e,h,a.core.OWNERS[0]),
            projection_diagnostics={o:a.core.projection_diagnostic(e,h,e,h,o) for o in a.core.OWNERS},
            quality_vs_source=q,quality_vs_same_arm_clean=q,extract_seconds=.1)
        return row,dict(source=receipt,source_E=e.tolist(),source_H=h),rgb
    def test_full_endpoint_recompute_and_missing_channel(self):
        with tempfile.TemporaryDirectory() as d:
            row,ce,rgb=self.fixture(d)
            with patch.object(a.runner.codec,'perceptual_hash',return_value=0):
                result=a.verify_row(a.Audit(d),row,ce,rgb,rgb,{})
                self.assertTrue(result['verified']);self.assertTrue(result['blind_both'])
                corrupt=copy.deepcopy(row);del corrupt['owner_decisions'][a.core.OWNERS[0]]['s']
                with self.assertRaisesRegex(ValueError,'key mismatch'):a.verify_row(a.Audit(d),corrupt,ce,rgb,rgb,{})
                corrupt=copy.deepcopy(row);corrupt['source_template_oracle_fp16']['s']+=1
                with self.assertRaisesRegex(ValueError,'numerical mismatch'):a.verify_row(a.Audit(d),corrupt,ce,rgb,rgb,{})
    def test_nonfinite_projection_and_png_membership(self):
        with tempfile.TemporaryDirectory() as d:
            row,ce,rgb=self.fixture(d)
            with patch.object(a.runner.codec,'perceptual_hash',return_value=0):
                corrupt=copy.deepcopy(row);corrupt['projection_diagnostics'][a.core.OWNERS[0]]['kernel_exact']=float('nan')
                with self.assertRaisesRegex(ValueError,'numerical mismatch'):a.verify_row(a.Audit(d),corrupt,ce,rgb,rgb,{})
                corrupt=copy.deepcopy(row);corrupt['image']['path']=str(Path(d)/'wrong.png')
                with self.assertRaisesRegex(ValueError,'membership'):a.verify_row(a.Audit(d),corrupt,ce,rgb,rgb,{})
    def test_pixel_quality_recomputes_not_trusting_flag(self):
        rgb=np.full((20,20,3),128,np.uint8);q=a.quality(rgb,rgb);q.update(lpips=0.,quality_admissible=True)
        a.pixel_quality(q,rgb,rgb)
        with self.assertRaisesRegex(ValueError,'numerical mismatch'):a.pixel_quality(dict(q,ssim_rgb=.95),rgb,rgb)

    def test_incomplete_analysis_retains_eight_conditions_32_queries(self):
        with tempfile.TemporaryDirectory() as d:
            main=Path(d)/'main';base=Path(d)/'input';base.mkdir();recon=Path(d)/'reconstruction';recon.mkdir()
            (base/'run.json').write_text(json.dumps(dict(schema=a.runner.VERSION,data_split='development',outcome='failed',error='synthetic safety refusal',case_events=[])))
            (base/'conditions.json').write_text(json.dumps(a.runner.planned()[:-1]))
            (recon/'run.json').write_text('{}')
            output=main/'.thesis-build/dev-runs/fixture-analysis'
            with patch.object(a.runner,'MAIN',main),patch.object(a.runner,'RECONSTRUCTION',recon):
                record=a.analyze(base,output)
            self.assertEqual(record['outcome'],'incomplete');self.assertIsNone(record['gate']['promotion'])
            self.assertEqual(record['gate']['negative_queries']['planned'],28)
            self.assertEqual(len(a.read(output/'conditions.json')),8)
            import csv
            with (output/'queries.csv').open() as f:self.assertEqual(len(list(csv.DictReader(f))),32)
            self.assertEqual(record['source_error'],'synthetic safety refusal')
            self.assertTrue(any('missing or duplicate' in e for e in record['errors']))

if __name__=='__main__':unittest.main()
