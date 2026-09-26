"""Model-free C2 launcher/selection checks; no subprocess or image decode."""
import copy
import csv
import hashlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.c2_dev_probe import prepare,distances,planned_cases,CaseLedger
from scripts.run_c2_dev_probe import command
from src.signatures.semantic import quantize_features


def manifest():
    names=["scripts/c2_dev_probe.py","src/signatures/semantic.py","src/signatures/owner.py",
           "src/data/preprocess.py","scripts/a6_clip_visual.py","configs/semantic-dev.json",
           "configs/data.json","data/splits.csv",
           "data/b4-admission-20260926/source-manifest.csv",
           "data/b4-admission-20260926/development-reservation.json"]
    return {"experiment_id":"c2-semantic-development-v1","task_id":"C2","execution_target":"local",
            "seeds":[0],"budget":{"max_seconds":1200,"max_usd":0},
            "inputs":[{"path":n,"sha256":hashlib.sha256((ROOT/n).read_bytes()).hexdigest()} for n in names]}


class ProbeContractTests(unittest.TestCase):
    def test_only_original_32_locked_development_ids_admitted_no_real_reads(self):
        seen=[]
        from scripts.c2_dev_probe import checked
        def fake_raw(path,digest):
            if path.is_relative_to(ROOT): return checked(path,digest)
            seen.append((str(path),digest));return b"synthetic-do-not-decode"
        with tempfile.TemporaryDirectory() as temp, patch("scripts.c2_dev_probe.RAW_ROOT",Path(temp)), \
                patch("scripts.c2_dev_probe.checked",side_effect=fake_raw):
            config,digest,rows=prepare(manifest())
        self.assertEqual(len(rows),32)
        self.assertEqual(len(seen),0)  # raw bytes are checked after durable inventory creation
        self.assertTrue(all(r[2]["study_split"]=="development" for r in rows))
        expected=json.loads((ROOT/config["development_ids"]).read_bytes())["images"]
        uid=lambda r: ":".join(r[k] for k in ("domain","release_id","source_split","source_id"))
        self.assertEqual({r[0] for r in rows},{uid(r) for r in expected})
        self.assertEqual(digest,hashlib.sha256((ROOT/"configs/semantic-dev.json").read_bytes()).hexdigest())
        cases=planned_cases(rows)
        self.assertEqual(len(cases),96)
        self.assertEqual(len({r["case_id"] for r in cases}),96)
        self.assertTrue(all(r["status"]=="pending" for r in cases))

    def test_missing_binding_or_recipe_mismatch_fails_before_raw_reads(self):
        for change in (lambda m:m["inputs"].pop(),lambda m:m.update(experiment_id="other"),
                       lambda m:m.update(seeds=[1])):
            m=manifest();change(m)
            with self.assertRaises(ValueError): prepare(m)

    def test_launcher_fixed_timeout_environment_and_argument_array(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/"manifest.json";path.write_text(json.dumps(manifest()))
            argv=command(path,Path(temp)/"outputs")
            self.assertIn("--kill-after=10s",argv)
            self.assertIn("1160s",argv)
            self.assertIn("-i",argv)
            self.assertIn("HF_HUB_OFFLINE=1",argv)
            self.assertEqual(argv[-4],"--manifest")
            for key,value in (("execution_target","runpod"),("seeds",[1]),("task_id","C3b")):
                m=manifest();m[key]=value;path.write_text(json.dumps(m))
                with self.assertRaises(ValueError): command(path,Path(temp)/"outputs")

    def test_distances_explicit_code_and_digest_units(self):
        one=(1.0,)+(0.0,)*511;two=(0.0,1.0)+(0.0,)*510
        a=quantize_features(one,b"\0"*32);b=quantize_features(two,b"\0"*32)
        record=distances(one,two,a,b,b"\0"*32,b"\xff"*32)
        self.assertEqual(record["feature_distance"],1)
        self.assertEqual(record["key_distance"],256)
        self.assertEqual(record["semantic_code_distance"],(int.from_bytes(a.packed,"little")^int.from_bytes(b.packed,"little")).bit_count())


class DurableCaseTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        for folder in ("outputs","logs","checkpoints"): (self.root/folder).mkdir()
        self.selected=[("synthetic-a",{"domain":"fixture"},{},None),
                       ("synthetic-b",{"domain":"fixture"},{},None)]
        self.target=self.root/"outputs/semantic-examples.json"
        self.ledger=CaseLedger(self.target,planned_cases(self.selected),"f"*64)

    def test_predeclared_pairs_and_partial_failure_survive_interruption(self):
        initial=json.loads(self.target.read_bytes())
        self.assertEqual(initial["pending_cases"],6)
        self.assertEqual(initial["cases"][2]["paired_image_id"],"synthetic-b")
        self.ledger.record("synthetic-a","same_image_uncached_repeat","completed",semantic_code_distance=0)
        self.ledger.fail("synthetic-a","jpeg_quality95_subsampling0","jpeg_failure",ValueError("synthetic failure"))
        # Simulate no finish after crash: durable file keeps every planned case.
        partial=json.loads(self.target.read_bytes())
        self.assertEqual(len(partial["cases"]),6)
        self.assertEqual(len(partial["examples"]),1)
        self.assertEqual(len(partial["failures"]),1)
        self.assertEqual(partial["pending_cases"],4)
        self.assertEqual(partial["status"],"running")
        self.assertEqual(partial["failures"][0]["transform"],"jpeg_quality95_subsampling0")
        journal=[json.loads(line) for line in self.ledger.journal.read_text().splitlines()]
        self.assertEqual(len(journal),3)
        self.assertEqual(journal[-1]["status"],"failed")
        self.assertEqual(self.ledger.finish(),1)
        self.assertEqual(json.loads(self.target.read_bytes())["status"],"incomplete")

    def test_model_failure_marks_all_planned_cases_no_overwrite_or_reassignment(self):
        self.ledger.fail_pending("synthetic_model_failure",RuntimeError("synthetic only"))
        self.assertEqual(self.ledger.finish(),1)
        report=json.loads(self.target.read_bytes())
        self.assertEqual(report["pending_cases"],0)
        self.assertEqual(len(report["failures"]),6)
        self.assertEqual(report["status"],"failed")
        with self.assertRaises(ValueError): self.ledger.record("synthetic-a","different_content","completed")
        with self.assertRaises(FileExistsError): CaseLedger(self.target,planned_cases(self.selected),"f"*64)


if __name__=="__main__": unittest.main()
