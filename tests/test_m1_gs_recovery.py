"""CPU-only byte fixtures for Gaussian Shading recovery, not detector evidence."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("gs_recovery",ROOT/"scripts/m1_gaussian_shading.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


class BytesImage:
    def save(self,path):Path(path).write_bytes(b"fixture PNG bytes, not an actual image")


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.output=Path(self.temp.name)
        self.manifest={"cases":[{"id":"prompt-0","prompt":"fixture","seed":1000}]}

    def one_row(self):
        artifacts={}
        for name in ("prompt-0-C0-original.png","prompt-0-C0-clean.png"):
            m.save_artifact(BytesImage(),self.output,name,artifacts)
        row={"case":"prompt-0","arm":"C0","channel":"clean","prompt":"fixture","generation_seed":1000,
             "image":"prompt-0-C0-clean.png","image_sha256":artifacts["prompt-0-C0-clean.png"]["sha256"]}
        m.append_row(self.output/"rows.jsonl",row,1)
        return artifacts,row

    def test_partial_resume_verifies_receipted_original_and_attack(self):
        artifacts,row=self.one_row()
        loaded,rows,done=m.load_resume_state(self.output,self.manifest)
        self.assertEqual(loaded,artifacts);self.assertEqual(rows,[row])
        self.assertEqual(done,{("prompt-0","C0","clean")})

    def test_corrupt_and_missing_original_refused(self):
        self.one_row();path=self.output/"prompt-0-C0-original.png"
        path.write_bytes(b"corrupt")
        with self.assertRaisesRegex(ValueError,"refused reuse/overwrite"):
            m.load_resume_state(self.output,self.manifest)
        path.unlink()
        with self.assertRaisesRegex(ValueError,"refused reuse/overwrite"):
            m.load_resume_state(self.output,self.manifest)

    def test_unreceipted_artifact_is_preserved_and_not_overwritten(self):
        path=self.output/"prompt-0-C0-original.png";path.write_bytes(b"orphan")
        with self.assertRaisesRegex(ValueError,"Unreceipted artifact preserved"):
            m.load_resume_state(self.output,self.manifest)
        with self.assertRaisesRegex(ValueError,"Refused artifact overwrite"):
            m.save_artifact(BytesImage(),self.output,path.name,{})
        self.assertEqual(path.read_bytes(),b"orphan")

    def test_truncated_journal_preserved(self):
        self.one_row();path=self.output/"rows.jsonl"
        path.write_bytes(path.read_bytes()+b'{"case":')
        before=path.read_bytes()
        with self.assertRaisesRegex(ValueError,"Truncated journal preserved unchanged"):
            m.load_resume_state(self.output,self.manifest)
        self.assertEqual(before,path.read_bytes())

    def test_changed_complete_journal_refused(self):
        self.one_row();path=self.output/"rows.jsonl"
        path.write_bytes(path.read_bytes().replace(b'fixture',b'changed'))
        with self.assertRaisesRegex(ValueError,"Journal receipt mismatch"):
            m.load_resume_state(self.output,self.manifest)

    def test_duplicate_rows_rejected_even_with_valid_receipt(self):
        _,row=self.one_row();m.append_row(self.output/"rows.jsonl",row,2)
        with self.assertRaisesRegex(ValueError,"duplicate completed journal row"):
            m.load_resume_state(self.output,self.manifest)

    def test_row_image_hash_must_match_artifact(self):
        _,row=self.one_row();row["image_sha256"]="wrong"
        (self.output/"rows.jsonl").unlink();m.append_row(self.output/"rows.jsonl",row,1)
        with self.assertRaisesRegex(ValueError,"row image hash mismatch"):
            m.load_resume_state(self.output,self.manifest)

    def test_completed_run_validates_all_files_and_rows(self):
        artifacts={};count=0
        case=self.manifest["cases"][0]
        for arm in ("C0","C1"):
            m.save_artifact(BytesImage(),self.output,f"prompt-0-{arm}-original.png",artifacts)
            for channel,_,_ in m.channels_for_run():
                name=f"prompt-0-{arm}-{channel}.png"
                m.save_artifact(BytesImage(),self.output,name,artifacts);count+=1
                m.append_row(self.output/"rows.jsonl",{"case":case["id"],"arm":arm,"channel":channel,
                    "prompt":case["prompt"],"generation_seed":case["seed"],"image":name,
                    "image_sha256":artifacts[name]["sha256"]},count)
        m.write(self.output/"summary.json",{"fixture":True})
        prior={"outcome":"completed","completed_rows":count,"completed_file_sha256":{name:m.digest(self.output/name) for name in
                    ("rows.jsonl","artifacts.json","rows-receipt.json","summary.json")}}
        self.assertEqual(len(m.load_resume_state(self.output,self.manifest,prior)[1]),28)
        (self.output/"summary.json").write_text("{}")
        with self.assertRaisesRegex(ValueError,"Completed run provenance mismatch"):
            m.load_resume_state(self.output,self.manifest,prior)

    def test_keyboardinterrupt_finalizes_record_before_model_imports(self):
        manifest=json.loads((ROOT/"research/m1-gs-synthetic.json").read_text())
        path=self.output/"manifest.json";m.write(path,manifest)
        target=self.output/"run"
        fake=types.ModuleType("three_threat_models")
        def stop():raise KeyboardInterrupt("fixture interruption")
        fake.block_network=stop
        for name in ("DDIM_CONFIG","validate_generated","verify_assets","load_lpips","lpips_score"):
            setattr(fake,name,None)
        with patch.object(m,"require_committed",return_value={}),patch.object(m.subprocess,"check_output",return_value="fixture-commit\n"),patch.dict(sys.modules,{"three_threat_models":fake}),patch.object(m.time,"monotonic",side_effect=[10.0,12.0]):
            with self.assertRaises(KeyboardInterrupt):m.run(path,target)
        record=json.loads((target/"run.json").read_text())
        self.assertEqual(record["outcome"],"interrupted")
        self.assertEqual(record["error_type"],"KeyboardInterrupt")
        self.assertEqual(record["duration_seconds"],2.0)

    def test_committed_check_uses_git_clean_filter_for_crlf(self):
        path=ROOT/"scripts/m1_gaussian_shading.py"
        with patch.object(m.subprocess,"check_output",side_effect=["blob\n","blob\n"]) as mock:
            receipt=m.require_committed([path])
        args=mock.call_args_list[1].args[0]
        self.assertIn("--path=scripts/m1_gaussian_shading.py",args)
        self.assertEqual(receipt["scripts/m1_gaussian_shading.py"]["git_blob_oid"],"blob")
        with patch.object(m.subprocess,"check_output",side_effect=["blob\n","modified\n"]):
            with self.assertRaisesRegex(ValueError,"differs from HEAD"):m.require_committed([path])

    def test_uncommitted_input_refused_before_output_creation(self):
        manifest=json.loads((ROOT/"research/m1-gs-synthetic.json").read_text())
        path=self.output/"manifest.json";m.write(path,manifest)
        target=self.output/"not-created"
        with patch.object(m,"require_committed",side_effect=ValueError("Scientific input differs from HEAD")):
            with self.assertRaisesRegex(ValueError,"differs from HEAD"):m.run(path,target)
        self.assertFalse(target.exists())


if __name__=="__main__":unittest.main()
