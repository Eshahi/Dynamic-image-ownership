"""Generated metadata fixtures only; no retained run/image/model is opened."""
import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location("family_pilot_fixtures",Path(__file__).resolve().parents[1]/"scripts/m1_analyze_families.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


def q():return {"psnr_db":40,"ssim_rgb":.95,"lpips":.02,"quality_admissible":True}


def detector(found=True):
    return {"watermark_found":found,"present":found,"proposal_state":"authentic" if found else "not_detected",
            "qualified_state":"authentic-consistent" if found else "no-evidence","timing_ms":{"total":7},
            "semantic":{"found":found,"content_match":found,"content_status":"match" if found else None},
            "instance":{"found":found,"content_match":found,"content_status":"match" if found else None}}


class PilotTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)

    def package(self,name,run,manifest):
        directory=self.root/(name+str(len(list(self.root.iterdir()))));directory.mkdir()
        path=directory/"source-manifest.json";m.write(path,manifest)
        run.update(command=["fixture","--manifest",str(path)],manifest_sha256=m.sha(path),seeds=[0],data_split="development")
        m.write(directory/"run.json",run)
        (directory/("journal.jsonl" if name=="dual" else "rows.jsonl")).write_text("",encoding="utf-8")
        with patch.object(m,"ROOT",self.root):return m.load_family(name,directory)

    def dual(self,ids=(1,2),complete=True,route="pure-decoder",outcome="completed"):
        cohort=self.root/"research/m1-reconstruction-dev.json";cohort.parent.mkdir(exist_ok=True)
        m.write(cohort,{"data_split":"development","cases":[{"id":i,"path":"do-not-open.png","sha256":"a"*64} for i in range(1,13)]})
        assessed={**q(),"correct_owner":detector(),"wrong_owner":detector(False),"png_path":"must-not-open.png","png_sha256":"b"*64}
        cases=[]
        for ident in ids:
            entry={"route":route,"outcome":"completed" if complete else "started","C0_matched":copy.deepcopy(assessed),
                   "optimization":{"seconds":2,"surrogate_semantic":5,"surrogate_instance":4}}
            if complete:
                for name in ("C1","C0_VAE_cycle","C1_VAE_cycle"):entry[name]=copy.deepcopy(assessed)
            cases.append({"id":ident,"outcome":"completed" if complete else "started","raw_sha256":"a"*64,
                          "C0_source":copy.deepcopy(assessed),"routes":[entry]})
        config={"routes":[route]}
        return self.package("dual",{"outcome":outcome,"config":config,"cases":cases},
                            {"config":config,"case_ids":list(ids),"cohort_manifest":"research/m1-reconstruction-dev.json"})

    def phase(self,complete=True,outcome="completed"):
        owners=["alpha","beta","gamma","delta"];config={"arms":["APM","IPS"],"owners":owners,"presence_matches":82}
        conditions=[]
        for ident in (1,2):
            for arm in config["arms"]:
                for control in ("C0","C1"):
                    for dose in ("clean","vae_cycle"):
                        entry={"id":f"{ident}-{arm}-{control}-{dose}","source_id":ident,"arm":arm,"control":control,"dose":dose,
                               "outcome":"completed" if complete else "planned"}
                        if complete:
                            decisions={o:{"matches":100 if o==owners[0] and control=="C1" else 64,
                                          "bit_accuracy":100/128 if o==owners[0] and control=="C1" else .5,"pilot_state":"fixture"} for o in owners}
                            entry.update(owner_decisions=decisions,quality_vs_source=q(),quality_vs_same_arm_clean=q(),extract_seconds=.03,
                                         paired_C1_vs_C0_quality=q() if control=="C1" and dose=="clean" else None,
                                         extracted={"scores":[1]*128,"zero_magnitude_coefficients_per_block":[0]*128})
                        conditions.append(entry)
        return self.package("phasemark",{"outcome":outcome,"config":config,"conditions":conditions},
                            {"config":config,"cases":[{"id":1,"sha256":"a"*64},{"id":2,"sha256":"b"*64}]})

    def test_dual_pilot_two_is_not_reserved_twelve(self):
        result=m.analyze_dual(self.dual())
        self.assertEqual(len(result["raw"]),10);self.assertEqual(result["declared_pilot_source_n"],2)
        self.assertEqual(result["declared_pilot_completed_source_n"],2);self.assertEqual(result["reserved_source_n"],12)
        self.assertEqual(result["reserved_not_declared_n"],10)
        self.assertEqual(sum(r["status"]=="reserved_not_declared" for r in result["coverage"]),10)
        self.assertTrue(all(r["paired_quality"] is None for r in result["raw"]))
        first=result["raw"][0];self.assertTrue(first["correct_semantic_content_match"]);self.assertFalse(first["wrong_watermark_found"])
        self.assertEqual(first["correct_timing_ms"]["total"],7)
        self.assertEqual(result["summary"][0]["correct_detector_total_ms"]["mean"],7)

    def test_dual_partial_pending_keeps_missing_and_null_quality(self):
        result=m.analyze_dual(self.dual(complete=False,outcome="started"))
        self.assertTrue(result["incomplete"]);self.assertEqual(result["declared_pilot_completed_source_n"],0)
        missing=[r for r in result["raw"] if r["condition"]=="C1"]
        self.assertEqual(len(missing),2);self.assertTrue(all(r["quality_all_three"] is None for r in missing))
        self.assertTrue(all(r["correct_watermark_found"] is None for r in missing))

    def test_dual_disjoint_sources_merge_overlap_rejected(self):
        a=self.dual(ids=(1,));b=self.dual(ids=(2,))
        self.assertEqual(m.analyze_dual([a,b])["declared_pilot_source_n"],2)
        with self.assertRaisesRegex(ValueError,"Overlapping dual"):m.analyze_dual([a,a])

    def test_dual_duplicate_actual_case_or_route_rejected(self):
        a=self.dual();a["run"]["cases"].append(copy.deepcopy(a["run"]["cases"][0]))
        with self.assertRaisesRegex(ValueError,"Duplicate actual dual source"):m.analyze_dual(a)
        a=self.dual();a["run"]["cases"][0]["routes"]*=2
        with self.assertRaisesRegex(ValueError,"Duplicate/unplanned actual dual route"):m.analyze_dual(a)

    def test_phase_full_inventory_queries_and_unique_condition_quality(self):
        result=m.analyze_phasemark(self.phase())
        self.assertEqual(result["planned_conditions"],16);self.assertEqual(result["planned_queries"],64)
        self.assertEqual(len(result["condition_inventory"]),16);self.assertEqual(result["planned_source_n"],2)
        self.assertTrue(all(r["carrier_gate"] and r["source_quality_gate"] for r in result["arm_screen"]))
        self.assertTrue(all(len(r["zero_magnitude_coefficients_per_block"])==128 for r in result["raw"]))
        self.assertTrue(all("proposal_state" not in r for r in result["raw"]))

    def test_phase_pending_or_missing_query_nulls_gate(self):
        package=self.phase(complete=False,outcome="started");result=m.analyze_phasemark(package)
        self.assertTrue(result["incomplete"]);self.assertEqual(len(result["raw"]),64)
        self.assertTrue(all(s["carrier_gate"] is None and s["source_quality_gate"] is None for s in result["arm_screen"]))
        package=self.phase();del package["run"]["conditions"][0]["owner_decisions"]["beta"]
        result=m.analyze_phasemark(package)
        self.assertTrue(result["incomplete"]);self.assertIsNone(result["arm_screen"][0]["carrier_gate"])
        self.assertEqual(sum(r["query_observed"] for r in result["raw"]),63)

    def test_phase_missing_quality_and_duplicate_conditions(self):
        package=self.phase();del package["run"]["conditions"][2]["quality_vs_source"]["lpips"]
        self.assertIsNone(m.analyze_phasemark(package)["arm_screen"][0]["source_quality_gate"])
        package=self.phase();package["run"]["conditions"].append(copy.deepcopy(package["run"]["conditions"][0]))
        with self.assertRaisesRegex(ValueError,"Duplicate PhaseMark condition"):m.analyze_phasemark(package)

    def test_manifest_hash_mismatch_and_original_metadata_preserved(self):
        package=self.phase();manifest=Path(package["input_files"][1]["path"]);before=(Path(package["directory"])/"run.json").read_bytes()
        manifest.write_text("{}")
        again=m.load_family("phasemark",Path(package["directory"]))
        self.assertFalse(again["manifest_hash_matches_run"])
        with self.assertRaisesRegex(ValueError,"planned metadata unavailable"):m.analyze_phasemark(again)
        self.assertEqual((Path(package["directory"])/"run.json").read_bytes(),before)


if __name__=="__main__":unittest.main()
