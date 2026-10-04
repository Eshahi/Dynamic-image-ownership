"""Real filesystem tests use only generated tokens in owned temporary directories."""
from dataclasses import FrozenInstanceError,replace
import hashlib
import os
from pathlib import Path
import sys
import tempfile
import struct
import stat
import zlib
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import m1_confirmatory_raw_guard as guard

class GuardTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix="m1-scoped-fixture-")
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        (self.root/guard.MARKER).write_bytes(guard.FIXTURE_MAGIC)
        self.data=guard.FIXTURE_MAGIC+b"generated token; not a dataset/image/annotation\n"
        self.path=self.root/"input.token"; self.path.write_bytes(self.data)
        self.receipt=guard.InputReceipt("fixture:one","source-token","input.token",hashlib.sha256(self.data).hexdigest(),len(self.data))
        self.scope=dict(manifest_sha256="a"*64,index_sha256="b"*64,output_root=self.root/"outputs")
        self.cap=self.issue([self.receipt])

    def issue(self,receipts,**options):
        return guard.issue_fixture_capability(self.root,self.scope["output_root"],receipts,
            manifest_sha256=self.scope["manifest_sha256"],index_sha256=self.scope["index_sha256"],**options)

    def read(self,cap=None,**overrides):
        return guard.read_scoped_input(self.cap if cap is None else cap,"fixture:one","source-token",**(self.scope|overrides))

    def test_real_windows_handle_and_exact_bytes(self):
        result=self.read()
        self.assertEqual(result.data,self.data)
        self.assertEqual(result.receipt,self.receipt)
        self.assertEqual(result.observed_sha256,self.receipt.sha256)
        self.assertFalse(self.cap.official_approval_verified)
        self.assertFalse(self.cap.source_adoption_verified)
        self.assertEqual(result.capability_mode,"synthetic-fixture-only")
        self.assertFalse(hasattr(result,"path"))

    def test_scope_failures_precede_any_open(self):
        for override in ({"manifest_sha256":"c"*64},{"index_sha256":"c"*64},{"output_root":self.root/"other"}):
            with patch.object(guard.os,"open",side_effect=AssertionError("opened before authorization")):
                with self.assertRaises(guard.AccessDenied): self.read(**override)
        with patch.object(guard.os,"open",side_effect=AssertionError("opened before authorization")):
            with self.assertRaises(guard.AccessDenied):
                guard.read_scoped_input(self.cap,"fixture:absent","source-token",**self.scope)
            with self.assertRaises(guard.AccessDenied):
                guard.read_scoped_input({"verified":True},"fixture:one","source-token",**self.scope)

    def test_scientific_issuance_never_inspects_inputs(self):
        class Poison:
            def __fspath__(self): raise AssertionError("scientific path inspected")
            def __getitem__(self,key): raise AssertionError("approval inspected")
        with patch.object(guard.os,"open",side_effect=AssertionError("opened scientific input")):
            for evidence in (None,True,{"decision":"approve","verified":True},Poison()):
                with self.assertRaises(guard.AccessDenied): guard.issue_scientific_capability(evidence,raw_path=Poison())

    def test_capability_and_allowlist_immutable(self):
        with self.assertRaises(FrozenInstanceError): self.cap.mode="scientific"
        with self.assertRaises(FrozenInstanceError): self.cap.receipts[0].relative_path="other"
        receipts=[self.receipt]; cap=self.issue(receipts); receipts.clear()
        self.assertEqual(len(cap.receipts),1)
        with self.assertRaises(TypeError): guard.ScopedCapability(mode="scientific")

    def test_expiry_checked_before_and_after_read(self):
        with patch.object(guard.time,"monotonic",return_value=self.cap.expires_monotonic),patch.object(guard.os,"open",side_effect=AssertionError("expired open")):
            with self.assertRaises(guard.AccessDenied): self.read()
        with patch.object(guard.time,"monotonic",side_effect=[self.cap.expires_monotonic-1,self.cap.expires_monotonic+1]):
            with self.assertRaises(guard.AccessDenied): self.read()

    def test_hash_size_magic_and_changed_bytes(self):
        for data in (self.data+b"longer",self.data.replace(b"generated",b"generated",1)[:-1]+b"X",b"X"*len(self.data)):
            self.path.write_bytes(data)
            with self.assertRaises(guard.AccessDenied): self.read()
        self.path.write_bytes(b"X"*len(self.data))
        forged=replace(self.receipt,sha256=hashlib.sha256(self.path.read_bytes()).hexdigest())
        cap=self.issue([forged])
        with self.assertRaises(guard.AccessDenied): self.read(cap)

    def test_traversal_duplicates_output_and_malformed_receipts(self):
        for path in ("../escape","nested/../../escape","/absolute","C:/escape","nested\\escape","./input.token","outputs/token"):
            with self.assertRaises(guard.AccessDenied): self.issue([replace(self.receipt,relative_path=path)])
        for receipts in ([self.receipt,self.receipt],[replace(self.receipt,source_uid="ms-coco:heldout")],
            [replace(self.receipt,sha256=True)],[replace(self.receipt,size_bytes=True)]):
            with self.assertRaises(guard.AccessDenied): self.issue(receipts)
        with self.assertRaises(guard.AccessDenied):
            guard.issue_fixture_capability(self.root,self.root/".."/"escape",[self.receipt],manifest_sha256="a"*64,index_sha256="b"*64)

    def test_dataset_root_rejected_before_stat(self):
        with patch.object(Path,"resolve",side_effect=AssertionError("resolved actual path")),patch.object(Path,"lstat",side_effect=AssertionError("statted actual path")):
            with self.assertRaises(guard.AccessDenied):
                guard.issue_fixture_capability("W:/not-followed/data/raw", "W:/not-followed/outputs",[self.receipt],manifest_sha256="a"*64,index_sha256="b"*64)

    def test_nonregular_input_refused_before_blocking_open(self):
        real=guard._reject_reparse
        fake=type("Pipe",(),{"st_mode":stat.S_IFIFO,"st_nlink":1,"st_size":len(self.data)})()
        with patch.object(guard,"_reject_reparse",side_effect=lambda path:fake if path==self.path else real(path)),patch.object(guard.os,"open",side_effect=AssertionError("nonregular open would block")):
            with self.assertRaises(guard.AccessDenied): self.read()

    def test_final_handle_escape_refused_before_read(self):
        outside=self.root.parent/"not-an-input.token" # no creation/stat/read of this path
        with patch.object(guard,"_handle_final_path",return_value=outside),patch.object(guard.os,"fdopen",side_effect=AssertionError("read before handle containment")):
            with self.assertRaises(guard.AccessDenied): self.read()

    def test_symlink_or_junction_and_hardlink_refused(self):
        target=self.root/"second.token"; target.write_bytes(self.data)
        linked=self.root/"linked.token"
        try: os.link(target,linked)
        except (OSError,NotImplementedError): self.skipTest("Hardlinks unavailable")
        receipt=replace(self.receipt,relative_path="linked.token")
        cap=self.issue([receipt])
        with self.assertRaises(guard.AccessDenied): self.read(cap)
        # Synthetic reparse metadata assertion also covers Windows junction flag even without symlink privilege.
        fake=type("Reparse",(),{"st_mode":0,"st_file_attributes":0x400})()
        with patch.object(Path,"lstat",return_value=fake):
            with self.assertRaises(guard.AccessDenied): guard._reject_reparse(self.path)

    def test_generated_png_through_byte_only_canonicalizer(self):
        # Entire PNG is created from deterministic RGB literals, never an acquired image.
        def chunk(kind,payload):
            return struct.pack(">I",len(payload))+kind+payload+struct.pack(">I",zlib.crc32(kind+payload)&0xffffffff)
        width,height=7,5
        rgb=bytes((255,0,0))*width
        data=guard.PNG_MAGIC+chunk(b"IHDR",struct.pack(">IIBBBBB",width,height,8,2,0,0,0))+chunk(b"IDAT",zlib.compress((bytes([0])+rgb)*height))+chunk(b"IEND",b"")
        image=self.root/"generated.png"; image.write_bytes(data)
        receipt=guard.InputReceipt("fixture:red-image","synthetic-generated-image","generated.png",hashlib.sha256(data).hexdigest(),len(data))
        cap=self.issue([receipt])
        result=guard.read_scoped_input(cap,"fixture:red-image","synthetic-generated-image",**self.scope)
        self.assertEqual(result.data,data)
        from m1_canonical_source import canonicalize
        array,record=canonicalize(result.data,result.receipt.sha256)
        self.assertEqual(array.shape,(512,512,3))
        self.assertTrue((array[:,:,0]==255).all())
        self.assertTrue((array[:,:,1:]==0).all())
        self.assertEqual(record["raw_sha256"],receipt.sha256)
        self.assertEqual(record["encoded_shape"],[height,width,3])

    def test_generated_image_role_does_not_accept_token_or_nonfixture_identity(self):
        receipt=replace(self.receipt,role="synthetic-generated-image")
        cap=self.issue([receipt])
        with self.assertRaises(guard.AccessDenied):
            guard.read_scoped_input(cap,"fixture:one","synthetic-generated-image",**self.scope)
        with self.assertRaises(guard.AccessDenied):
            self.issue([replace(receipt,source_uid="ms-coco:coco-2017:val2017:999")])

    def test_read_mutation_refused(self):
        original=guard.os.fstat
        count=0
        def mutated(fd):
            nonlocal count
            count+=1
            info=original(fd)
            if count==2:
                return type("Changed",(),{"st_dev":info.st_dev,"st_ino":info.st_ino,"st_size":info.st_size,"st_mtime_ns":info.st_mtime_ns+1})()
            return info
        with patch.object(guard.os,"fstat",side_effect=mutated):
            with self.assertRaises(guard.AccessDenied): self.read()

if __name__=="__main__": unittest.main()
