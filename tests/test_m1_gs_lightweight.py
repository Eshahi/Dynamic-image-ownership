"""Procedural CPU tests only: no retained images or pretrained model loading."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import numpy as np
import torch
from scripts import m1_gs_lightweight as lw

class LightweightTests(unittest.TestCase):
    def setUp(self):
        self.gs=lw.native()
        self.manifest=json.loads((lw.ROOT/'research/m1-gs-synthetic.json').read_text(encoding='utf-8'))
        self.key=self.manifest['development_key_hex'];self.wrong=self.manifest['wrong_key_hex'];self.nonce=self.gs.nonce_for(1000)

    def test_reconstructed_fp16_source_input_all_four_exact(self):
        for seed in range(1000,1004):
            result=lw.selfcheck(seed,self.key)
            self.assertEqual(result['matches'],256);self.assertTrue(result['exact_message'])

    def test_coordinate_tile_order_matches_native_decoder(self):
        rng=np.random.default_rng(10)
        for _ in range(3):
            z=rng.standard_normal((1,4,64,64)).astype(np.float32)
            decoded,_=lw.decode_votes(z,self.key,self.nonce)
            np.testing.assert_array_equal(decoded,self.gs.decode(z,self.key,self.nonce))
        reference=self.gs.payload_for(1000)
        z=(2*self.gs.embed_signs(reference,self.key,self.nonce).astype(np.float32)-1).reshape(1,4,64,64)
        bits,votes=lw.decode_votes(z,self.key,self.nonce)
        np.testing.assert_array_equal(bits,reference);np.testing.assert_array_equal(votes,reference*64)
        other,_=lw.decode_votes(z,self.wrong,self.nonce)
        self.assertFalse(np.array_equal(other,reference))
        other_nonce,_=lw.decode_votes(z,self.key,self.gs.nonce_for(1001))
        self.assertFalse(np.array_equal(other_nonce,reference))

    def test_strict_32_33_votes_and_zero_vote_tensor(self):
        # Construct chip positions in the exact (channel,tile,row,tile,col) order.
        plain=np.zeros((4,8,8,8,8),dtype=np.uint8)
        positions=[(a,b) for a in range(8) for b in range(8)]
        for a,b in positions[:32]:plain[:,a,:,b,:]=1
        stream=self.gs.bitstream(self.key,self.nonce,16384)
        z=(2*(plain.reshape(-1)^stream).astype(np.float32)-1).reshape(1,4,64,64)
        bits,votes=lw.decode_votes(z,self.key,self.nonce)
        self.assertTrue((votes==32).all());self.assertFalse(bits.any())
        a,b=positions[32];plain[:,a,:,b,:]=1
        z=(2*(plain.reshape(-1)^stream).astype(np.float32)-1).reshape(1,4,64,64)
        bits,votes=lw.decode_votes(z,self.key,self.nonce)
        self.assertTrue((votes==33).all());self.assertTrue(bits.all())
        z=(2*stream.astype(np.float32)-1).reshape(1,4,64,64)
        bits,votes=lw.decode_votes(z,self.key,self.nonce)
        self.assertFalse(votes.any());self.assertFalse(bits.any())

    def test_scaling_and_fp16_zero_diagnostics(self):
        rng=np.random.default_rng(30);u=rng.standard_normal((1,4,64,64)).astype(np.float16)
        u.flat[0]=np.nextafter(np.float16(0),np.float16(1));u.flat[1]=0
        z=(torch.from_numpy(u)*.18215).numpy()
        diagnostics=lw.latent_diagnostics(u,z)
        self.assertEqual(diagnostics['sign_changes_after_scaling'],1)
        self.assertEqual(diagnostics['scaled_zero_count'],diagnostics['posterior_zero_count']+1)
        positive=u.astype(np.float32);positive.flat[0]=1
        a,_=lw.decode_votes(positive,self.key,self.nonce);b,_=lw.decode_votes(positive*.18215,self.key,self.nonce)
        np.testing.assert_array_equal(a,b)

    def test_nonfinite_shape_and_dtype_rejected(self):
        z=np.ones((1,4,64,64),dtype=np.float32)
        for bad in (z.reshape(4,64,64),z.astype(np.int32),z*np.nan,z*np.inf):
            with self.assertRaises(ValueError):lw.decode_votes(bad,self.key,self.nonce)
        with self.assertRaises(ValueError):lw.latent_diagnostics(z,z)

    def test_presence_179_180_and_reference_is_not_decoder_input(self):
        z=np.ones((1,4,64,64),dtype=np.float32);bits,votes=lw.decode_votes(z,self.key,self.nonce)
        for count in (179,180):
            ref=1-bits.copy();ref.flat[:count]=bits.flat[:count]
            result=lw.evaluate(bits,votes,ref)
            self.assertEqual(result['matches'],count);self.assertEqual(result['present'],count==180)
        again,_=lw.decode_votes(z,self.key,self.nonce);np.testing.assert_array_equal(again,bits)

    def test_processor_matches_native_constructor_without_models(self):
        from diffusers import StableDiffusionPipeline
        # Native constructor, all model components absent: only CPU image processor.
        pipe=StableDiffusionPipeline(vae=None,text_encoder=None,tokenizer=None,unet=None,scheduler=None,
            safety_checker=None,feature_extractor=None,requires_safety_checker=False)
        from types import SimpleNamespace
        vae=SimpleNamespace(config=SimpleNamespace(block_out_channels=[128,256,512,512]))
        processor=lw.processor_for(vae)
        from PIL import Image
        rgb=np.random.default_rng(4).integers(0,256,(512,512,3),dtype=np.uint8)
        image=Image.fromarray(rgb)
        self.assertEqual(dict(processor.config),dict(pipe.image_processor.config))
        self.assertTrue(torch.equal(processor.preprocess(image),pipe.image_processor.preprocess(image)))

    def test_conditional_null_uses_payload_weight_and_majority_bias(self):
        expected=[1.9407882e-11,1.5120879e-11,5.6494634e-11,2.7023851e-11]
        for seed,tail in zip(range(1000,1004),expected):
            result=lw.conditional_null(self.gs.payload_for(seed))
            self.assertAlmostEqual(result['ideal_tail_ge180']/tail,1,places=6)
            self.assertLess(result['decoded_one_probability'],.5)

    def test_plan_summary_and_frozen_manifest_missing_denominator(self):
        rows=lw.plan(self.manifest);self.assertEqual(len(rows),112)
        result=lw.summarize(rows)
        self.assertIsNone(result['gates']['clean']);self.assertIsNone(result['gates']['vae'])
        self.assertEqual(len(result['channels']),28)
        self.assertTrue(all(r['missing_C0']==4 and r['missing_C1']==4 for r in result['channels']))
        manifest=json.loads((lw.ROOT/'research/m1_gs_lightweight-dev.json').read_text(encoding='utf-8'))
        lw.validate(manifest);manifest['data_split']='heldout'
        with self.assertRaises(ValueError):lw.validate(manifest)

    def test_native_counts_remain_visible_when_lightweight_fails(self):
        rows=lw.plan(self.manifest)
        row=next(r for r in rows if r['channel']=='clean' and r['arm']=='C1')
        row.update(outcome='failed',native={'bit_accuracy':1.,'detected':True,'exact_payload':True,'wrong_key_detected':False})
        result=lw.summarize(rows)
        n=next(r for r in result['channels'] if r['channel']=='clean' and r['decoder']=='native')
        l=next(r for r in result['channels'] if r['channel']=='clean' and r['decoder']=='lightweight')
        self.assertEqual(n['C1_present'],1);self.assertEqual(n['missing_C1'],3)
        self.assertEqual(l['C1_present'],0);self.assertEqual(l['missing_C1'],4)

    def test_native_metadata_hash_and_row_join_without_opening_images(self):
        gs=self.gs
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);artifacts={}
            for channel in ('original','clean'):
                path=root/f'prompt-0-C1-{channel}.png';path.write_bytes(b'opaque metadata fixture '+channel.encode())
                artifacts[path.name]={'sha256':gs.digest(path),'size_bytes':path.stat().st_size}
            gs.write(root/'artifacts.json',artifacts)
            row={'case':'prompt-0','arm':'C1','channel':'clean','generation_seed':1000,'prompt':self.manifest['cases'][0]['prompt'],
                'image':'prompt-0-C1-clean.png','image_sha256':artifacts['prompt-0-C1-clean.png']['sha256'],
                'bit_accuracy':1.,'wrong_key_bit_accuracy':.5,'detected':True,'wrong_key_detected':False,
                'exact_payload':True,'detector_seconds':2.,'detector_unet_evaluations':50}
            gs.append_row(root/'rows.jsonl',row,1)
            gs.write(root/'run.json',{'commit':'1'*40,'outcome':'incomplete','config':gs.CONFIG,'script_sha256':lw.NATIVE_HASH,'manifest_sha256':lw.MANIFEST_HASH})
            _,receipts,index,_=lw.collect(root,self.manifest)
            self.assertEqual(len(receipts),4);self.assertEqual(list(index),['prompt-0-C1-clean'])
            (root/'prompt-0-C1-clean.png').write_bytes(b'corrupt')
            with self.assertRaises(ValueError):lw.collect(root,self.manifest)

    def test_failed_preflight_and_rejected_resume_preserve_receipts(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);manifest=root/'bad.json';manifest.write_text('{}')
            output=root/'.thesis-build/dev-runs/lightweight'
            with mock.patch.object(lw,'MAIN',root):
                self.assertEqual(lw.run(manifest,root/'absent',output),1)
                raw=(output/'run.json').read_bytes()
                record=json.loads(raw);self.assertEqual(record['outcome'],'failed')
                self.assertEqual(len(record['conditions']),112)
                with self.assertRaises(ValueError):lw.run(manifest,root/'absent',output)
                self.assertEqual((output/'run.json').read_bytes(),raw)

if __name__=='__main__':unittest.main()
