"""Owned RGB8 fixtures only. No study data, models, science or thresholds."""
import copy
import hashlib
import json
import struct
import unittest
from pathlib import Path
from unittest import mock

from src.embedding import dct_baseline as baseline
from src.signatures.owner import derive_public_signatures
from scripts.pixel_dct_control import embed_pixel_dct, templates_from_keys

ROOT = Path(__file__).resolve().parents[1]


class BaselineTests(unittest.TestCase):
    def setUp(self):
        self.raw = (ROOT/"configs/dct-baseline.json").read_bytes()
        self.config = baseline.load_config_bytes(self.raw)
        self.width, self.height = 33, 35
        self.image = bytes(c for y in range(35) for x in range(33) for c in ((5*x+7*y)%256,(11*x+3*y)%256,(x+13*y)%256))
        self.q, self.h, self.owner, self.digest = b"\x23\x01", b"\x12\x34\x56\x78", "owned-fixture-owner", bytes(range(32))

    def pair(self, **kwargs):
        return baseline.embed_control(self.image,self.width,self.height,self.q,self.h,self.owner,self.digest,kwargs.get("config",self.config))

    def test_exact_reference_parity_and_native_shape(self):
        pair = self.pair()
        keys = derive_public_signatures(self.q,self.h,self.owner)
        templates = templates_from_keys(keys.semantic,keys.instance,self.digest,33,35)
        expected = embed_pixel_dct(self.image,33,35,*templates,semantic_gain=.01,instance_gain=.01)
        self.assertEqual(pair.marked,expected); self.assertEqual(pair.source,self.image)
        self.assertEqual(len(pair.marked),len(self.image)); self.assertNotEqual(pair.marked,self.image)
        self.assertEqual(pair.marked,self.pair().marked)
        self.assertEqual(pair.receipt["coefficient_slots_per_component"],4*5*5)
        self.assertEqual(pair.receipt["source_pixel_sha256"],hashlib.sha256(b"b5-rgb8-srgb-v1\0"+struct.pack(">II",33,35)+self.image).hexdigest())

    def test_source_quality_recomputed_from_actual_quantized_bytes(self):
        pair=self.pair()
        mse=sum(((a-b)/255)**2 for a,b in zip(self.image,pair.marked))/len(self.image)
        self.assertAlmostEqual(pair.receipt["quality_versus_source_rgb8"]["rgb_mse"],mse,15)
        self.assertFalse(pair.receipt["scientific_acceptance"])
        self.assertEqual(pair.receipt["PNG_custody"],"NOT_RUN")
        json.dumps(pair.receipt,allow_nan=False)

    def test_identity_diagnostic_has_explicit_infinite_not_nan(self):
        with mock.patch.object(baseline,"embed_pixel_dct",return_value=self.image):
            pair=self.pair()
        self.assertIsNone(pair.receipt["quality_versus_source_rgb8"]["PSNR_dB"])
        self.assertEqual(pair.receipt["quality_versus_source_rgb8"]["PSNR_status"],"infinite_identity")

    def test_invalid_config_and_forged_digest_rejected(self):
        value=json.loads(self.raw)
        for key,bad in (("semantic_gain",True),("semantic_gain",0),("instance_gain",-1),("instance_gain",2),
                        ("maximum_native_side",1024.0),("maximum_native_side",2048),("calibration","accepted")):
            changed=copy.deepcopy(value); changed[key]=bad
            with self.subTest(key=key,bad=bad),self.assertRaises(ValueError): baseline.load_config_bytes(json.dumps(changed).encode())
        with self.assertRaises(ValueError): baseline.load_config_bytes(b'{"semantic_gain":1,"semantic_gain":2}')
        with self.assertRaises(ValueError): self.pair(config=baseline.BaselineConfig(self.raw,"0"*64))

    def test_native_resolution_limit_and_malformed_inputs_fail_before_embedding(self):
        value=json.loads(self.raw); value["maximum_native_side"]=32
        with mock.patch.object(baseline,"embed_pixel_dct") as embed:
            with self.assertRaises(ValueError): self.pair(config=baseline.load_config_bytes(json.dumps(value).encode()))
            embed.assert_not_called()
        for rgb,w,h,q,d in ((bytearray(self.image),33,35,self.q,self.digest),(self.image,True,35,self.q,self.digest),
                            (self.image,33,35,b"\x00\xf0",self.digest),(self.image,33,35,self.q,bytes(32))):
            with self.assertRaises(ValueError): baseline.embed_control(rgb,w,h,q,self.h,self.owner,d,self.config)

    def test_oracle_and_wrong_owner_results_never_blind_or_calibrated(self):
        pair=self.pair()
        result=baseline.oracle_component_scores(pair.marked,33,35,self.q,self.h,self.owner,self.digest,wrong_owner="owned-wrong")
        self.assertEqual(result["tested_owner_count"],2); self.assertEqual(result["decision"],"PROHIBITED")
        self.assertIn("not_blind",result["knowledge_profile"])
        for row in result["rows"]:
            for comp in ("semantic","instance"):
                self.assertTrue(-1 <= row[comp]["score"] <= 1)
        with self.assertRaises(ValueError): baseline.oracle_component_scores(self.image,33,35,self.q,self.h,self.owner,self.digest,wrong_owner=self.owner)


if __name__ == "__main__": unittest.main()
