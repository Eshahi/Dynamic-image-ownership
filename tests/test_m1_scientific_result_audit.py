import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from m1_verified_unit_sink import VerifiedUnitSink
import m1_scientific_result_audit as audit
import m1_blind_noise_core as core


class ArtifactAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.sink=VerifiedUnitSink(self.root,allowed_root=self.root)
        self.artifacts=audit.Artifacts([self.root])
        self.source=np.full((512,512,3),128,dtype=np.uint8)
        rgb,image=self.sink.save_image('image',self.source)
        rng=np.random.default_rng(41);E=rng.normal(size=512);E/=np.linalg.norm(E)
        z=rng.normal(size=16384);H=19;owner=core.OWNERS[0]
        quality=dict(audit.pixel_quality(rgb,rgb),lpips=0.,quality_admissible=True)
        query=dict(id='query',outcome='completed',owner=owner,decision=core.scores(z,E,H,owner),
            upstream_image_id='image',upstream_image=image,upstream_rgb8_sha256=hashlib.sha256(rgb.tobytes()).hexdigest())
        self.row=dict(id='image',outcome='completed',image=image,rgb8_sha256=query['upstream_rgb8_sha256'],
            safety={'checker':'pinned SD1.5 FP16','nsfw':False},quality_vs_source=quality,
            quality_vs_same_arm_clean=copy.deepcopy(quality),suspect_E=E.tolist(),suspect_H=H,
            reader_arrays={'E':self.sink.save_array('E',E),'z':self.sink.save_array('z',z)},queries=[query])

    def run_audit(self,row=None):
        return audit.audit_candidate_image(row or self.row,self.artifacts,
            source_rgb8=self.source,matched_clean_rgb8=self.source)

    def test_saved_png_arrays_score_and_quality_replay(self):
        result=self.run_audit()
        self.assertEqual(result['verified_queries'],['query'])
        self.assertIn('not re-inferred',result['model_observations'])

    def test_changed_bytes_fail_before_score(self):
        path=Path(self.row['reader_arrays']['z']['path'])
        with path.open('ab') as stream:stream.write(b'corrupt')
        with self.assertRaisesRegex(ValueError,'bytes differ'):self.run_audit()

    def test_recomputed_scores_not_only_threshold_flags(self):
        row=copy.deepcopy(self.row);row['queries'][0]['decision']['s']+=.01
        with self.assertRaisesRegex(ValueError,'score algebra'):self.run_audit(row)

    def test_query_cannot_switch_to_other_image_receipt(self):
        row=copy.deepcopy(self.row);row['queries'][0]['upstream_rgb8_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'image receipt'):self.run_audit(row)

    def test_flat_query_observations_join_same_image(self):
        row=copy.deepcopy(self.row);queries=row.pop('queries')
        queries[0]['suspect_H']=row['suspect_H']+1
        with self.assertRaisesRegex(ValueError,'readout observation'):
            audit.audit_candidate_image(row,self.artifacts,source_rgb8=self.source,
                matched_clean_rgb8=self.source,queries=queries)

    def test_quality_not_trusted_from_json(self):
        row=copy.deepcopy(self.row);row['quality_vs_source']['ssim_rgb']=.99
        with self.assertRaisesRegex(ValueError,'pixel quality'):self.run_audit(row)

    def test_outside_root_refused_even_with_correct_hash(self):
        row=copy.deepcopy(self.row);row['image']['path']=str(self.root.parent/'outside.png')
        with self.assertRaisesRegex(ValueError,'outside'):self.run_audit(row)

    def test_failed_safety_cannot_be_completed(self):
        row=copy.deepcopy(self.row);row['safety']['nsfw']=True
        with self.assertRaisesRegex(ValueError,'safety'):self.run_audit(row)

    def test_nonfinite_array_rejected_with_updated_hash(self):
        value=np.zeros(16384);value[0]=np.nan
        path=Path(self.row['reader_arrays']['z']['path']);np.save(path,value,allow_pickle=False)
        self.row['reader_arrays']['z'].update(sha256=hashlib.sha256(path.read_bytes()).hexdigest(),size_bytes=path.stat().st_size)
        with self.assertRaisesRegex(ValueError,'Finite floating'):self.run_audit()

    def enrollment(self):
        from m1_phase_residual import cap
        from m1_blind_noise import rgb8
        reference=np.full((1,3,512,512),.5,dtype=np.float32)
        decoded=np.full_like(reference,.51);residual=decoded-reference
        marked,receipt=cap(self.source,residual[0].transpose(1,2,0).astype(np.float64))
        images={}
        for name,value in {'C0-source':self.source,'C0-reconstruction':rgb8(reference[0].transpose(1,2,0).astype(np.float64)),'C1':marked}.items():
            saved,artifact=self.sink.save_image(name,value)
            images[name]={'image':artifact,'rgb8_sha256':hashlib.sha256(saved.tobytes()).hexdigest()}
        arrays={name:self.sink.save_array(name,value) for name,value in
            {'reference':reference,'decoded':decoded,'residual':residual,'surrogate':decoded}.items()}
        return images,arrays,receipt

    def test_native_stage_residual_and_cap_reconstruct_saved_controls(self):
        images,arrays,cap=self.enrollment()
        result=audit.audit_enrollment(self.source,images,arrays,cap,self.artifacts)
        self.assertEqual(result['cap'],'recomputed_exactly')

    def test_cap_metadata_cannot_override_pixel_reconstruction(self):
        images,arrays,cap=self.enrollment();cap=dict(cap,unreviewed_change=True)
        with self.assertRaisesRegex(ValueError,'quality cap'):
            audit.audit_enrollment(self.source,images,arrays,cap,self.artifacts)

    def test_v5_exact_codec_replay_and_changed_decision(self):
        from m1_confirmatory_image_operations import V5Comparator
        from m1_owner_interface import A4_OWNERS
        profile=json.loads((Path(__file__).resolve().parents[1]/'configs/revised-watermark-v5.example.json').read_text())
        profile['semantic_source']='external:clip-vit-b32-a6-40d365715913'
        feature=np.asarray([1.,0.,.25,-.5]*128,dtype=np.float32)
        row=copy.deepcopy(self.row);row.pop('queries')
        row['reader_arrays']={'v5_semantic_features':self.sink.save_array('v5-feature',feature)}
        query=dict(id='v5-query',outcome='completed',upstream_image_id=row['id'],
            upstream_image=row['image'],upstream_rgb8_sha256=row['rgb8_sha256'],
            reader_arrays=row['reader_arrays'],owner=A4_OWNERS[0],
            decision=V5Comparator(profile,lambda image:feature).extract(self.source,A4_OWNERS[0]))
        kwargs=dict(source_rgb8=self.source,matched_clean_rgb8=self.source,profile=profile,queries=[query])
        result=audit.audit_v5_image(row,self.artifacts,**kwargs)
        self.assertEqual(result['verified_queries'],['v5-query'])
        query['decision']['version']='tampered'
        with self.assertRaisesRegex(ValueError,'v5 codec replay'):
            audit.audit_v5_image(row,self.artifacts,**kwargs)


if __name__=='__main__':unittest.main()
