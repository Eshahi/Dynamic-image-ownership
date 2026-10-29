"""Pure VINE-B framing/decoder and reader-contract tests; no scientific runs."""
import hashlib
import hmac
from pathlib import Path
import struct
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parent))
import tifs_vine_b as vb

KEY=b"public-profile-key"
CONFIG=bytes(range(32))
OWNER=b"owner-alpha"
Q,H=0x12345678,0x90abcdef


class PayloadTests(unittest.TestCase):
    def test_framing_and_wire(self):
        fields=(vb.DOMAIN,CONFIG,OWNER,Q.to_bytes(4,"big"))
        expected=b"".join(struct.pack(">I",len(f))+f for f in fields)
        self.assertEqual(vb.frame(Q,CONFIG,OWNER),expected)
        expected_tag=int.from_bytes(hmac.new(KEY,expected,hashlib.sha256).digest()[:5],"big")>>4
        self.assertEqual(vb.tag36(Q,KEY,CONFIG,OWNER),expected_tag)
        bits=vb.encode_payload(Q,H,KEY,CONFIG,OWNER)
        self.assertEqual(len(bits),100)
        self.assertEqual(int("".join(map(str,bits[:32])),2),Q)
        self.assertEqual(int("".join(map(str,bits[32:68])),2),expected_tag)
        self.assertEqual(int("".join(map(str,bits[68:])),2),H^vb.mask32(Q,KEY,CONFIG,OWNER))
        self.assertNotEqual(vb.frame(Q,CONFIG,OWNER),vb.frame(Q,CONFIG,OWNER,domain=vb.MASK_DOMAIN))

    def test_domain_owner_config_and_data_bind(self):
        original=vb.tag36(Q,KEY,CONFIG,OWNER)
        for q,k,c,o in ((Q^1,KEY,CONFIG,OWNER),(Q,KEY+b"x",CONFIG,OWNER),
                         (Q,KEY,CONFIG[::-1],OWNER),(Q,KEY,CONFIG,OWNER+b"x")):
            self.assertNotEqual(original,vb.tag36(q,k,c,o))
        self.assertNotIn(b"".join((CONFIG,OWNER)),vb.frame(Q,CONFIG,OWNER))
        changed_h=vb.encode_payload(Q,H^1,KEY,CONFIG,OWNER)
        self.assertEqual(changed_h[:68],vb.encode_payload(Q,H,KEY,CONFIG,OWNER)[:68])

    def test_real_radius_mixed_data_tag_and_wrong_owner(self):
        bits=vb.encode_payload(Q,H,KEY,CONFIG,OWNER)
        for index in (0,15,45,67): bits[index]^=1
        result=vb.decode_payload(bits,KEY,CONFIG,OWNER)
        self.assertTrue(result["unique"])
        self.assertEqual((result["q"],result["h"],result["distance"]),(f"{Q:08x}",f"{H:08x}",4))
        self.assertEqual(result["candidates_examined"],41449)
        self.assertFalse(vb.decode_payload(bits,KEY,CONFIG,b"owner-beta")["unique"])
        result["q"]="mutated"
        self.assertEqual(vb.decode_payload(bits,KEY,CONFIG,OWNER)["q"],f"{Q:08x}")

    def test_five_tag_errors_reject(self):
        bits=vb.encode_payload(Q,H,KEY,CONFIG,OWNER)
        for index in (63,64,65,66,67): bits[index]^=1
        self.assertEqual(vb.decode_payload(bits,KEY,CONFIG,OWNER)["status"],"no_codeword")

    def test_data_only_and_tag_only_boundary(self):
        for indices in ((0,1,2,3),(32,33,34,35)):
            bits=vb.encode_payload(Q,H,KEY,CONFIG,OWNER)
            for index in indices: bits[index]^=1
            result=vb.decode_payload(bits,KEY,CONFIG,OWNER)
            self.assertTrue(result["unique"])
            self.assertEqual((result["q"],result["h"],result["distance"]),(f"{Q:08x}",f"{H:08x}",4))

    def test_h_errors_do_not_destroy_q(self):
        bits=vb.encode_payload(Q,H,KEY,CONFIG,OWNER)
        for index in range(68,100): bits[index]^=1
        result=vb.decode_payload(bits,KEY,CONFIG,OWNER)
        self.assertTrue(result["unique"])
        self.assertEqual(result["q"],f"{Q:08x}")
        self.assertEqual(result["h"],f"{H^0xffffffff:08x}")
        self.assertEqual(result["distance"],0)

    def test_ambiguity_exhausted(self):
        bits=[0]*100
        result=vb._decode_uncached(bits,KEY,CONFIG,OWNER,tagger=lambda *args:0)
        self.assertEqual(result["status"],"ambiguous")
        self.assertFalse(result["unique"])
        self.assertEqual(result["candidates"],41449)
        self.assertEqual(result["candidates_examined"],41449)
        self.assertIsNone(result["q"])

    def test_malformed_and_boundary_values(self):
        for bits in ([0]*99,[0]*101,[0]*99+[2],[0]*99+[True],[0]*99+[0.0]):
            with self.assertRaises(ValueError): vb.decode_payload(bits,KEY,CONFIG,OWNER)
        for q in (-1,2**32,True,"00000000"):
            with self.assertRaises(ValueError): vb.encode_payload(q,H,KEY,CONFIG,OWNER)
        for k,c,o in ((b"",CONFIG,OWNER),(KEY,b"short",OWNER),(KEY,CONFIG,b"")):
            with self.assertRaises(ValueError): vb.encode_payload(Q,H,k,c,o)
        self.assertEqual(len(vb.encode_payload(0,2**32-1,KEY,CONFIG,OWNER)),100)
        self.assertEqual(vb._cached_decode.cache_info().maxsize,256)

    def test_evaluator_delivery_is_separate(self):
        bits=vb.encode_payload(Q,H,KEY,CONFIG,OWNER)
        payload=dict(q=f"{Q:08x}",h=f"{H:08x}",bits=bits)
        raw=bits.copy();raw[1]^=1
        decode=dict(unique=True,q=payload["q"],h=payload["h"])
        diagnostic=vb.delivery_diagnostics(raw,decode,payload)
        self.assertEqual(diagnostic["raw_payload_bit_errors"],1)
        self.assertFalse(diagnostic["raw_payload_exact"])
        self.assertTrue(diagnostic["corrected_payload_exact"])
        self.assertIsNone(vb.delivery_diagnostics(raw,decode,None))


class ReaderContractTests(unittest.TestCase):
    def test_content_status_reuses_soft_rule_and_semantic_maximum(self):
        adapter=vb.VineB.__new__(vb.VineB)
        calls=[]
        rank={"unchecked":0,"match":0,"uncertain":1,"mismatch":2}
        def content(distance,radius,far,checked):
            calls.append((distance,radius,far,checked))
            return "match" if distance<=radius else "mismatch" if distance>=far else "uncertain"
        def decide(sf,ss,hf,hs):
            calls.append((sf,ss,hf,hs))
            return ("both_match","authentic") if ss==hs=="match" else ("content_mismatch","copy_paste")
        adapter.v5=SimpleNamespace(canonical_owner=lambda x:x.encode(),base=SimpleNamespace(
            _STATUS_RANK=rank,_content_status=content,_decide=decide))
        adapter.checked=dict(decision=dict(semantic_radius=6,semantic_mismatch_distance=10,
            instance_radius=6,instance_mismatch_distance=10))
        adapter.key,adapter.config=KEY,CONFIG
        adapter.codes=lambda rgb,features:(Q,H)
        def semantic(channel,features,key,config,limits,check,binding):
            self.assertEqual((channel["decoded_code"],channel["decoding_error_rate"]),(f"{Q:08x}",0.0))
            self.assertEqual((features,key,config,limits,check,binding),([1],KEY,CONFIG,(6,10),True,"soft"))
            return "mismatch",12.5
        adapter.f5=SimpleNamespace(_semantic_status=semantic)
        blind=dict(raw=dict(decoded_message=[0]*100))
        with patch.object(vb,"decode_payload",return_value=dict(unique=True,q=f"{Q:08x}",h=f"{H:08x}")):
            result=adapter.read("suspect",OWNER.decode(),blind=blind,features=[1])
        self.assertEqual(calls,[(0,6,10,True),(True,"mismatch",True,"mismatch")])
        self.assertEqual(result["semantic"]["soft_distance"],12.5)
        self.assertFalse(result["instance"]["content_match"])
        self.assertIsNone(result["instance"]["decoding_error_rate"])
        self.assertFalse(result["instance"]["independent_carrier_evidence"])

    def test_blind_discards_dummy_presence(self):
        seen=[]
        adapter=vb.VineB.__new__(vb.VineB)
        def detect(rgb,bits):
            seen.append(bits)
            return dict(raw=dict(decoded_message=[1]*100,probabilities=[.9]*100),presence={"present":True},native={"rule":"native"})
        adapter.vine=SimpleNamespace(detect=detect)
        result=adapter.blind("suspect")
        self.assertEqual(seen,[[0]*100])
        self.assertNotIn("presence",result)
        self.assertEqual(result["raw"]["decoded_message"],[1]*100)

    def test_read_has_no_reference_argument_or_vae_path(self):
        import inspect
        self.assertEqual(set(inspect.signature(vb.VineB.read).parameters),{"self","rgb","owner","blind","features"})
        source=inspect.getsource(vb.VineB)
        self.assertNotIn("f5.Reader",source)
        self.assertNotIn("rt.Internal",source)


if __name__=="__main__":
    unittest.main()
