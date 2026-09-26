"""C2 protocol/cache and synthetic CPU-tensor tests; never load a model."""
import hashlib
import json
import math
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.signatures.owner import derive_public_signatures, pack_fields
from src.signatures.semantic import (FeatureCache, SemanticError, derive_ws,
                                    feature_identity, normalize_tensor, quantize_features)
from src.signatures.semantic import PinnedClipEncoder
from scripts.pixel_dct_control import semantic_code_from_normalized_embedding


def basis(index=0, sign=1):
    return tuple(float(sign if k==index else 0) for k in range(512))


def identity():
    return {"model":"synthetic-not-a-model", "checkpoint_sha256":"1"*64,
            "source_commit":"2"*40,"source_digests":{"fixture":"3"*64},
            "preprocess":{"crop":224},"arithmetic":"synthetic-exact-float32",
            "device":"cpu","runtime":{"fixture":1},"implementation_sha256":"4"*64}


class SemanticProtocolTests(unittest.TestCase):
    def test_basis_bits_order_reference_and_owner_protocol(self):
        seed = bytes(range(32))
        stream = hashlib.shake_256(pack_fields(b"a5-semproj-v1",seed)).digest(768)
        for index in (0,7,8,127,511):
            for sign in (1,-1):
                features = basis(index,sign)
                result = quantize_features(features,seed)
                bits = sum((((stream[(r*512+index)//8] >> ((r*512+index)%8))&1)==(sign==-1)) << r
                           for r in range(12))
                self.assertEqual(result.packed,bits.to_bytes(2,"little"))
                self.assertEqual(result.packed,semantic_code_from_normalized_embedding(features,seed))
                self.assertEqual(result.packed[1]&0xf0,0)
                self.assertEqual(len(result.projections),12)
                self.assertTrue(all(abs(v)==1/math.sqrt(512) for v in result.projections))
                code,ws = derive_ws(features,seed,"e\u0301")
                self.assertEqual(ws,derive_public_signatures(code.packed,b"\0"*4,"\u00e9").semantic)

    def test_ordered_dense_float32_vector_and_margin(self):
        # 512 entries of +/-1/sqrt512, rounded to actual float32 before use.
        value = struct.unpack("<f",struct.pack("<f",1/math.sqrt(512)))[0]
        features = tuple(value if k%3 else -value for k in range(512))
        seed = b"\0"*32
        result = quantize_features(features,seed)
        self.assertEqual(result.packed,semantic_code_from_normalized_embedding(features,seed))
        self.assertEqual(result,quantize_features(list(features),seed))
        stream = hashlib.shake_256(pack_fields(b"a5-semproj-v1",seed)).digest(768)
        for r,projection in enumerate(result.projections):
            total = 0.0
            for k in range(512):
                total += features[k]*(-1 if (stream[(r*512+k)//8] >> ((r*512+k)%8))&1 else 1)/math.sqrt(512)
            self.assertAlmostEqual(projection,total,places=15)

    def test_invalid_shape_values_normalization_and_seed_fail(self):
        for value in (basis()[:511],[[1.0]]*512,basis()+ (0.0,),[False]*512,
                      [0.0]*512,[math.nan]+[0.0]*511,[math.inf]+[0.0]*511,
                      [0.6,0.8]+[0.0]*510):
            with self.assertRaises(SemanticError): quantize_features(value,b"\0"*32)
        for seed in (b"", b"x"*31,b"x"*33,bytearray(32),"0"*64):
            with self.assertRaises(SemanticError): quantize_features(basis(),seed)

    def test_changed_owner_changes_public_digest_not_code(self):
        first,one = derive_ws(basis(),b"\0"*32,"owner-one")
        second,two = derive_ws(basis(),b"\0"*32,"owner-two")
        self.assertEqual(first,second)
        self.assertNotEqual(one,two)

    def test_exact_zero_projection_uses_nonnegative_bit(self):
        value=struct.unpack("<f",struct.pack("<f",1/math.sqrt(2)))[0]
        result=quantize_features((value,value)+ (0.0,)*510,b"\0"*32)
        zeros=[r for r,p in enumerate(result.projections) if p==0.0]
        self.assertTrue(zeros)
        self.assertTrue(all((int.from_bytes(result.packed,"little") >> r)&1 for r in zeros))


class FeatureCacheTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.cache = FeatureCache(self.root)
        self.identity,self.key = feature_identity("a"*64,identity())

    def test_roundtrip_and_exclusive_no_overwrite(self):
        self.assertIsNone(self.cache.read(self.identity,self.key))
        self.cache.write(self.identity,self.key,basis())
        self.assertEqual(self.cache.read(self.identity,self.key),basis())
        before=(self.root/(self.key+".json")).read_bytes()
        with self.assertRaises(FileExistsError): self.cache.write(self.identity,self.key,basis(1))
        self.assertEqual((self.root/(self.key+".json")).read_bytes(),before)

    def test_input_model_preprocessing_runtime_device_code_isolation(self):
        self.cache.write(self.identity,self.key,basis())
        changed,newkey = feature_identity("b"*64,identity())
        self.assertIsNone(self.cache.read(changed,newkey))
        for field,value in (("model","different-model"),("checkpoint_sha256","f"*64),
                            ("source_commit","f"*40),("source_digests",{"fixture":"f"*64}),
                            ("preprocess",{"crop":225}),("arithmetic","different"),
                            ("device","cuda"),("runtime",{"fixture":2}),("implementation_sha256","f"*64)):
            changed,newkey = feature_identity("a"*64,dict(identity(),**{field:value}))
            self.assertNotEqual(newkey,self.key)
            self.assertIsNone(self.cache.read(changed,newkey))
        original=identity();snapshot,key=feature_identity("a"*64,original)
        original["preprocess"]["crop"]=999
        self.assertEqual(snapshot,self.identity)

    def test_corruption_identity_wrong_key_fail_preserve(self):
        self.cache.write(self.identity,self.key,basis())
        path=self.root/(self.key+".json")
        record=json.loads(path.read_bytes());record["features"][0]=-1.0
        path.write_text(json.dumps(record))
        before=path.read_bytes()
        with self.assertRaisesRegex(SemanticError,"digest"): self.cache.read(self.identity,self.key)
        self.assertEqual(path.read_bytes(),before)
        with self.assertRaisesRegex(SemanticError,"key"): self.cache.read(self.identity,"../wrong")
        record["identity"]["encoder"]["preprocess"]["crop"]=225
        path.write_text(json.dumps(record))
        with self.assertRaisesRegex(SemanticError,"identity"): self.cache.read(self.identity,self.key)

    def test_invalid_identity_and_nonunit_cache_fail(self):
        for digest in ("z"*64,"a"*63,1):
            with self.assertRaises(SemanticError): feature_identity(digest,identity())
        with self.assertRaises(SemanticError): feature_identity("a"*64,{})
        with self.assertRaises(SemanticError): self.cache.write(self.identity,self.key,[0.0]*512)

    def test_linked_cache_path_is_rejected(self):
        link=self.root/"linked-cache"
        try: link.symlink_to(self.root, target_is_directory=True)
        except OSError: self.skipTest("host does not permit test symlink creation")
        with self.assertRaisesRegex(SemanticError,"linked"): FeatureCache(link)


try:
    import torch
except ImportError:
    torch = None


@contextmanager
def deterministic_flags():
    # Torch backend flags are descriptors; mock patch/delattr cannot restore
    # them on Torch 2.12. Preserve and set through their supported setters.
    original=(torch.are_deterministic_algorithms_enabled(),torch.backends.cuda.matmul.allow_tf32,
              torch.backends.cudnn.allow_tf32,torch.backends.cudnn.benchmark)
    torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32=False
    torch.backends.cudnn.allow_tf32=False
    torch.backends.cudnn.benchmark=False
    try: yield
    finally:
        torch.use_deterministic_algorithms(original[0])
        torch.backends.cuda.matmul.allow_tf32=original[1]
        torch.backends.cudnn.allow_tf32=original[2]
        torch.backends.cudnn.benchmark=original[3]


@unittest.skipIf(torch is None,"science Torch absent in workflow venv; run in pinned WSL env")
class Float32NormalizationTests(unittest.TestCase):
    def test_normalize_real_cpu_tensor_shape_and_dtype(self):
        features=normalize_tensor(torch.arange(512,dtype=torch.float32).reshape(1,512))
        self.assertEqual(len(features),512)
        self.assertAlmostEqual(sum(v*v for v in features),1,places=6)
        self.assertEqual(quantize_features(features,b"\0"*32).packed,
                         semantic_code_from_normalized_embedding(features,b"\0"*32))

    def test_zero_tiny_nonfinite_wrong_shape_and_dtype_fail(self):
        for value in (torch.zeros(1,512),torch.full((1,512),1e-15),
                      torch.full((1,512),float("nan")),torch.full((1,512),float("inf")),
                      torch.ones(512),torch.ones(1,513),torch.ones(1,512,dtype=torch.float64)):
            with self.assertRaises(SemanticError): normalize_tensor(value)

    def test_extract_path_recomputes_self_consistent_tampered_cache(self):
        import numpy as np
        from src.data.preprocess import pixel_sha
        class SyntheticModel:
            calls=0
            def encode_image(self,tensor):
                self.calls+=1
                return torch.tensor([basis()],dtype=torch.float32)
        encoder=PinnedClipEncoder()
        encoder.identity=identity()  # explicitly synthetic, never a CLIP load
        encoder._device="cpu";encoder._model=SyntheticModel()
        encoder._transform=lambda image: torch.zeros((3,224,224),dtype=torch.float32)
        pixels=np.zeros((8,8,3),dtype=np.uint8)
        with tempfile.TemporaryDirectory() as temp, deterministic_flags():
            cache=FeatureCache(Path(temp))
            self.assertEqual(encoder.extract_features(pixels,cache),basis())
            self.assertEqual(encoder.extract_features(pixels,cache),basis())
            self.assertEqual(encoder._model.calls,2)
            record_identity,key=feature_identity(pixel_sha(pixels),encoder.identity)
            path=Path(temp)/(key+".json")
            record=json.loads(path.read_bytes());record["features"]=list(basis(1))
            record["features_sha256"]=hashlib.sha256(struct.pack("<512f",*basis(1))).hexdigest()
            path.write_text(json.dumps(record));before=path.read_bytes()
            with self.assertRaisesRegex(SemanticError,"re-extraction"):
                encoder.extract_features(pixels,cache)
            self.assertEqual(encoder._model.calls,3)
            self.assertEqual(path.read_bytes(),before)


if __name__=="__main__": unittest.main()
