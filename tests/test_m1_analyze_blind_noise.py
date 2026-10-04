"""CPU-only analytic fixtures; no scientific image, feature or model loads."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SPEC=importlib.util.spec_from_file_location('analysis',Path(__file__).resolve().parents[1]/'scripts/m1_analyze_blind_noise.py')
a=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(a)

def decision(s,i):return dict(s=s,i=i,flags=dict(s=s>=4,i=i>=4),state=a.expected_state(s,i),denominators=dict(s=1.,i=1.),errors=[])
def fixture():
    rows=[]
    for p in a.planned():
        projection={k:0. for k in a.PROJECTION};projection.update(norm_sq_1=1.,norm_sq_2=1.,sampling_fraction=.5,normalization_error_bound=0.)
        quality=dict(psnr_db=40.,psnr_infinite=False,mse_rgb8=6.5,ssim_rgb=.99,lpips=.01)
        scores={o:decision(0.,0.) for o in a.OWNERS}
        if p['control']=='C1':scores[a.OWNERS[0]]=decision(4.,4. if p['dose']=='clean' else 0.)
        rows.append(dict(**p,outcome='completed',owner_decisions=scores,projection_diagnostics={o:copy.deepcopy(projection) for o in a.OWNERS},quality_vs_source=quality,quality_vs_same_arm_clean=copy.deepcopy(quality),extract_seconds=.1,source_clip_cosine=.99,semantic_template_cosine=.99,source_phash_distance=1,suspect_E=[1.]+[0.]*511,suspect_H=1,forward=dict(seconds=1.,nfe=50,safety_blocked=False),perturbation=dict(l2=1.,rounding_l2=.01,template_rms=1.) if p['control']=='C1' else None))
    return rows

class AnalyzerTests(unittest.TestCase):
    def aggregate(self,rows,provenance=True):
        normalized,unexpected=a.normalize(rows);self.assertFalse(unexpected)
        return a.summarize(normalized,provenance)

    def test_inventory_selection_and_query_denominators(self):
        out=self.aggregate(fixture());self.assertEqual(out['planned_rows'],48);self.assertEqual(len(out['queries']),192)
        self.assertEqual(out['selection']['selected_alpha'],.025)
        self.assertEqual(len(out['groups']),24);self.assertTrue(all(g['planned_rows']==2 and g['distinct_source_n']==2 for g in out['groups']))

    def test_smallest_hybrid_without_pure_substitution(self):
        rows=fixture()
        for r in rows:
            if r['route']=='hybrid' and r['alpha']==.025 and r['control']=='C1' and r['dose']=='clean':r['quality_vs_source']['psnr_db']=35.
        self.assertEqual(self.aggregate(rows)['selection']['selected_alpha'],.05)
        for r in rows:
            if r['route']=='hybrid' and r['control']=='C1' and r['dose']=='clean':r['quality_vs_source']['psnr_db']=35.
        out=self.aggregate(rows);self.assertEqual(out['selection']['outcome'],'no_dose_passed');self.assertIsNone(out['selection']['selected_alpha'])
        self.assertTrue(all(g['passes'] for g in out['gates'] if g['route']=='pure'))

    def test_missing_or_duplicate_never_selects_larger_dose(self):
        for rows in (fixture()[1:],fixture()+[fixture()[0]]):
            out=self.aggregate(rows);self.assertFalse(out['selection']['complete']);self.assertIsNone(out['selection']['selected_alpha'])
            self.assertEqual(len(out['queries']),192)

    def test_wrong_owner_either_channel_or_c0_blocks(self):
        for control in ('C0','C1'):
            rows=fixture()
            r=next(r for r in rows if r['route']=='hybrid' and r['alpha']==.025 and r['control']==control)
            owner=a.OWNERS[0] if control=='C0' else a.OWNERS[1];r['owner_decisions'][owner]=decision(0.,4.)
            out=self.aggregate(rows);g=next(g for g in out['gates'] if g['route']=='hybrid' and g['alpha']==.025)
            self.assertFalse(g['c0_and_wrong_below_both']);self.assertEqual(out['selection']['selected_alpha'],.05)

    def test_vae_semantic_required_instance_not_required(self):
        rows=fixture();self.assertEqual(self.aggregate(rows)['selection']['selected_alpha'],.025)
        r=next(r for r in rows if r['route']=='hybrid' and r['alpha']==.025 and r['control']=='C1' and r['dose']=='vae_cycle');r['owner_decisions'][a.OWNERS[0]]=decision(0.,4.)
        out=self.aggregate(rows);g=next(g for g in out['gates'] if g['route']=='hybrid' and g['alpha']==.025)
        self.assertFalse(g['vae_semantic']);self.assertEqual(out['selection']['selected_alpha'],.05)

    def test_incomplete_fields_nonfinite_bool_and_flags(self):
        for kind in ('field','nan','bool','flags','projection','quality','feature'):
            rows=fixture();r=rows[0]
            if kind=='field':del r['owner_decisions'][a.OWNERS[0]]['denominators']
            elif kind=='nan':r['owner_decisions'][a.OWNERS[0]]['s']=float('nan')
            elif kind=='bool':r['extract_seconds']=True
            elif kind=='flags':r['owner_decisions'][a.OWNERS[0]]['flags']['s']=True
            elif kind=='projection':del r['projection_diagnostics'][a.OWNERS[0]]['variance_inner']
            elif kind=='quality':r['quality_vs_source']['lpips']=float('inf')
            elif kind=='feature':r['suspect_E']=[1.]*512
            with self.subTest(kind=kind):
                normalized,_=a.normalize(rows);self.assertFalse(normalized[0]['complete']);self.assertFalse(self.aggregate(rows)['selection']['complete'])

    def test_quality_strict_thresholds_and_infinite_identity(self):
        q=fixture()[0]['quality_vs_source'];self.assertTrue(a.quality_pass(q))
        for k,v in [('psnr_db',35.),('ssim_rgb',.9),('lpips',.1),('lpips',False),('psnr_db',float('inf'))]:
            bad=dict(q);bad[k]=v;self.assertFalse(a.quality_pass(bad))
        self.assertTrue(a.quality_pass(dict(q,psnr_infinite=True,psnr_db=None,mse_rgb8=0.)))
        self.assertFalse(a.quality_pass(dict(q,psnr_infinite=True,psnr_db=None,mse_rgb8=True)))

    def test_failed_and_invalid_measurement_retained(self):
        rows=fixture();rows[0].update(outcome='failed',error='safety blocked')
        n,_=a.normalize(rows);self.assertEqual(n[0]['outcome'],'failed');self.assertFalse(n[0]['complete'])
        rows=fixture();rows[0]['owner_decisions'][a.OWNERS[0]]=dict(s=None,i=None,flags=dict(s=None,i=None),denominators=dict(s=None,i=None),state='invalid_measurement',errors=['zero denominator'])
        out=self.aggregate(rows);g=next(g for g in out['groups'] if g['route']=='pure' and g['alpha']==.025 and g['control']=='C0' and g['dose']=='clean')
        self.assertEqual(g['states'][a.OWNERS[0]]['invalid_measurement'],1);self.assertFalse(out['gates'][0]['c0_and_wrong_below_both'])

    def test_provenance_blocks_gate_without_hiding_rows(self):
        out=self.aggregate(fixture(),False);self.assertIsNone(out['selection']['selected_alpha']);self.assertTrue(all(g['complete_rows']==2 for g in out['groups']))
        self.assertTrue(all(g['passes'] is None for g in out['gates']))

    def test_unexpected_identity_and_nonfinite_serialization(self):
        rows=fixture();extra=dict(rows[0],id='unplanned');n,u=a.normalize(rows+[extra]);self.assertEqual(len(n),48);self.assertEqual(len(u),1)
        self.assertEqual(a.sanitized({'metric':float('nan')}),{'metric':'nonfinite: nan'})

    def receipt_fixture(self,root):
        from PIL import Image
        rows=fixture();expected=json.loads((a.ROOT/'research/m1-blind-noise-dev.json').read_text());receipts={}
        def png(name):
            path=root/name
            if name not in receipts:
                im=Image.new('RGB',(512,512),(3,5,7));im.save(path)
                import hashlib
                receipts[name]=dict(path=str(path),sha256=a.sha(path),rgb8_sha256=hashlib.sha256(im.tobytes()).hexdigest())
            return dict(receipts[name])
        for r in rows:
            suffix='clean' if r['dose']=='clean' else 'vae'
            name=f"{r['source_id']}-{r['route']}-C0-{suffix}.png" if r['control']=='C0' else f"{r['source_id']}-{r['alpha']}-{r['route']}-C1-{suffix}.png"
            r['image']=png(name);r['source']=png(f"{r['source_id']}-source.png")
            fp=root/(f"{r['source_id']}-D0.npy" if r['control']=='C0' else f"{r['source_id']}-{r['alpha']}-Da.npy")
            fp.write_bytes(b'fixture-only')
            r['forward'].update(float_path=str(fp),float_sha256=a.sha(fp))
        a.write(root/'manifest.json',expected);a.write(root/'conditions.json',rows)
        run=dict(config=expected,data_split='development',manifest_sha256=a.sha(root/'manifest.json'),conditions=rows,outcome='completed',nfe_total=500,commit='f'*40,
                 committed_files={name:dict(working_sha256=a.sha(a.ROOT/name),git_blob_oid='fixture-blob') for name in a.REQUIRED_CODE},
                 case_events=[dict(source_id=i,outcome='completed',inverse_nfe=50,inverse_seconds=1.) for i in a.IDS],source_pair_projection=copy.deepcopy(rows[0]['projection_diagnostics']))
        run['output_hashes']={p.name:a.sha(p) for p in root.iterdir() if p.is_file()};a.write(root/'run.json',run)
        real_sha=a.sha
        reserved={Path(c['path']).resolve():c['sha256'] for c in expected['cases']}
        def fixture_sha(path):
            path=Path(path).resolve()
            return reserved[path] if path in reserved else real_sha(path)
        return run,fixture_sha

    def test_receipt_verification_then_hash_corruption(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);run,fixture_sha=self.receipt_fixture(root)
            with patch.object(a,'sha',side_effect=fixture_sha),patch.object(a.subprocess,'check_output',return_value='fixture-blob\n'):
                _,rows,unexpected,errors,_=a.load(root)
                self.assertFalse(errors);self.assertFalse(unexpected);self.assertTrue(all(r['complete'] for r in rows))
                (root/'1675-source.png').write_bytes(b'corruption')
                _,rows,_,errors,_=a.load(root)
                self.assertTrue(errors);self.assertFalse(rows[0]['complete']);self.assertIsNone(a.summarize(rows,not errors)['selection']['selected_alpha'])

    def test_hash_valid_wrong_png_identity_and_missing_conditions(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);run,fixture_sha=self.receipt_fixture(root)
            run['conditions'][0]['image']=dict(run['conditions'][0]['source'])
            a.write(root/'conditions.json',run['conditions']);run['output_hashes']['conditions.json']=a.sha(root/'conditions.json');a.write(root/'run.json',run)
            with patch.object(a,'sha',side_effect=fixture_sha),patch.object(a.subprocess,'check_output',return_value='fixture-blob\n'):
                _,rows,_,errors,_=a.load(root)
                self.assertFalse(rows[0]['complete']);self.assertTrue(any('membership' in e for e in rows[0]['errors_analysis']))
                (root/'conditions.json').unlink()
                _,rows,_,errors,_=a.load(root);self.assertEqual(len(rows),48);self.assertTrue(all(not r['complete'] for r in rows));self.assertTrue(errors)

if __name__=='__main__':unittest.main()
