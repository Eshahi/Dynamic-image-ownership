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
from scripts.c2_dev_probe import prepare,distances
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
        self.assertEqual(len(seen),32)
        self.assertTrue(all(r[2]["study_split"]=="development" for r in rows))
        expected=json.loads((ROOT/config["development_ids"]).read_bytes())["images"]
        uid=lambda r: ":".join(r[k] for k in ("domain","release_id","source_split","source_id"))
        self.assertEqual({r[0] for r in rows},{uid(r) for r in expected})
        self.assertEqual(digest,hashlib.sha256((ROOT/"configs/semantic-dev.json").read_bytes()).hexdigest())

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


if __name__=="__main__": unittest.main()
