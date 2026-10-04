"""CPU fixtures only; no retained experiment results or images are opened."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT=Path(__file__).resolve().parents[1]/"scripts/m1_analyze_families.py"
spec=importlib.util.spec_from_file_location("families",SCRIPT)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.config={"steps":[0,50,100,200],"objective":"fixture"}

    def case(self,ident,complete=True,steps=None,value=40):
        return {"id":ident,"outcome":"completed" if complete else "started",
                "checkpoints":[{"step":s,"psnr_db":value,"ssim_rgb":.95,"lpips":.02,"seconds":s+1}
                               for s in (steps if steps is not None else [0,50,100,200])]}

    def fixture_run(self,name,ids,cases,outcome="completed",recovery=None,config=None):
        directory=self.root/name;directory.mkdir()
        manifest={"data_split":"development","config":config or self.config,
                  "cases":[{"id":i,"path":"fixture-"+str(i),"sha256":str(i)*64} for i in ids]}
        if recovery:manifest["recovery"]=recovery
        path=self.root/(name+"-manifest.json");m.write(path,manifest)
        m.write(directory/"run.json",{"data_split":"development","outcome":outcome,
                "config":config or self.config,"cases":cases,"command":["fixture","--manifest",str(path)],
                "manifest_sha256":m.sha(path),"seeds":[0]})
        (directory/"images.jsonl").write_text("{\"fixture\":true}\n",encoding="utf-8")
        return m.load_family("reconstruction",directory)

    def receipt(self,package):
        directory=Path(package["directory"])
        (directory/"checkpoint.pt").write_bytes(b"fixture checkpoint; never executed")
        path=self.root/"pause.json"
        m.write(path,{"files":[{"path":str(p),"bytes":p.stat().st_size,"sha256":m.sha(p)}
                                for p in sorted(directory.iterdir())]})
        return path

    def test_partial_recovery_counts_sources_once_and_retains_attempts(self):
        original=self.fixture_run("original",[1,2],[self.case(1),self.case(2,False,[0,50])],"started")
        receipt=self.receipt(original)
        recovery=self.fixture_run("recovery",[2],[self.case(2,value=30)],recovery={"previous_run":"original","receipt_sha256":m.sha(receipt)})
        result=m.analyze_reconstruction([original,recovery],receipt)
        self.assertFalse(result["incomplete"])
        self.assertEqual(result["planned_source_n"],2)
        self.assertEqual(len(result["raw"]),8)
        self.assertEqual(len(result["attempt_inventory"]),12)
        self.assertTrue(all(s["planned"]==2 for s in result["summary"]))
        chosen=[r for r in result["raw"] if r["case"]==2]
        self.assertTrue(all(r["psnr_db"]==30 for r in chosen)) # never take better original 40
        self.assertTrue(all(r["chosen_run_sha256"]==m.sha(Path(recovery["directory"])/"run.json") for r in chosen))
        partial=[r for r in result["attempt_inventory"] if r["status"]=="observed_partial"]
        self.assertEqual(len(partial),2)
        self.assertTrue(all(not r["selected_final_attempt"] for r in partial))
        self.assertEqual(original["source_outcome"],"started")

    def test_started_requires_receipt_even_when_cases_complete(self):
        original=self.fixture_run("original",[1],[self.case(1)],"started")
        self.assertTrue(m.analyze_reconstruction([original])["incomplete"])
        self.assertFalse(m.analyze_reconstruction([original],self.receipt(original))["incomplete"])
        self.assertTrue(m.analyze_reconstruction([original])["incomplete"])

    def test_all_relevant_receipt_hashes_checked(self):
        original=self.fixture_run("original",[1],[self.case(1)],"started")
        receipt=self.receipt(original)
        (Path(original["directory"])/"checkpoint.pt").write_bytes(b"corrupted")
        with self.assertRaisesRegex(ValueError,"hash/size mismatch"):
            m.analyze_reconstruction([original],receipt)

    def test_double_completed_conflict_without_recovery_mapping(self):
        original=self.fixture_run("original",[1],[self.case(1)])
        another=self.fixture_run("another",[1],[self.case(1)])
        with self.assertRaisesRegex(ValueError,"explicit recovery mapping"):
            m.analyze_reconstruction([original,another])

    def test_explicit_mapping_can_replace_complete_trajectory(self):
        original=self.fixture_run("original",[1],[self.case(1)],"started")
        receipt=self.receipt(original)
        another=self.fixture_run("another",[1],[self.case(1,value=20)],recovery={"previous_run":"original","receipt_sha256":m.sha(receipt)})
        result=m.analyze_reconstruction([original,another],receipt)
        self.assertEqual(len(result["raw"]),4)
        self.assertTrue(all(r["psnr_db"]==20 for r in result["raw"]))

    def test_selected_missing_recovery_never_falls_back(self):
        original=self.fixture_run("original",[1],[self.case(1)],"started")
        receipt=self.receipt(original)
        another=self.fixture_run("another",[1],[],recovery={"previous_run":"original","receipt_sha256":m.sha(receipt)})
        result=m.analyze_reconstruction([original,another],receipt)
        self.assertTrue(result["incomplete"])
        self.assertTrue(all(r["status"]=="missing_or_failed" and r["psnr_db"] is None for r in result["raw"]))

    def test_config_mismatch_rejected(self):
        original=self.fixture_run("original",[1],[self.case(1)])
        another=self.fixture_run("another",[2],[self.case(2)],config={"steps":[0,50,100,200],"objective":"different"})
        with self.assertRaisesRegex(ValueError,"configurations differ"):
            m.analyze_reconstruction([original,another])

    def test_missing_cohort_does_not_infer_observed_denominator(self):
        original=self.fixture_run("original",[1],[self.case(1)])
        original["manifest"]={}
        result=m.analyze_reconstruction([original])
        self.assertTrue(result["incomplete"])
        self.assertEqual(result["raw"],[])
        self.assertIsNone(result["planned_source_n"])

    def test_wrong_receipt_mapping_and_source_identity_rejected(self):
        original=self.fixture_run("original",[1],[self.case(1)],"started")
        receipt=self.receipt(original)
        another=self.fixture_run("another",[1],[self.case(1)],recovery={"previous_run":"original","receipt_sha256":"wrong"})
        with self.assertRaisesRegex(ValueError,"matching explicit pause receipt"):
            m.analyze_reconstruction([original,another],receipt)
        another["manifest"]["recovery"]["receipt_sha256"]=m.sha(receipt)
        another["manifest"]["cases"][0]["sha256"]="changed"
        with self.assertRaisesRegex(ValueError,"source identity/hash mismatch"):
            m.analyze_reconstruction([original,another],receipt)

    def test_receipt_requires_both_metadata_files(self):
        original=self.fixture_run("original",[1],[self.case(1)],"started")
        receipt=self.receipt(original)
        obj=json.loads(receipt.read_text());obj["files"]=[x for x in obj["files"] if not x["path"].endswith("images.jsonl")]
        m.write(receipt,obj)
        with self.assertRaisesRegex(ValueError,"run.json and images.jsonl"):
            m.analyze_reconstruction([original],receipt)

    def test_duplicate_case_and_checkpoint_are_ambiguous(self):
        original=self.fixture_run("original",[1],[self.case(1),self.case(1)])
        result=m.analyze_reconstruction([original])
        self.assertTrue(result["incomplete"])
        self.assertTrue(all(r["status"]=="ambiguous_duplicate" for r in result["raw"]))
        one=self.case(2);one["checkpoints"].append(one["checkpoints"][0].copy())
        package=self.fixture_run("single",[2],[one])
        result=m.analyze_reconstruction([package])
        self.assertEqual(result["raw"][0]["status"],"ambiguous_duplicate")


if __name__=="__main__":unittest.main()

