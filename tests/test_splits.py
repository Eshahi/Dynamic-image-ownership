"""Synthetic component tests; no fabricated actual split manifest."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from b4_metadata_dependence import components, private_record, summarize
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data.splits import allocate, grouped_frame, near, near_pairs
from build_b4_splits import coverage_join


class MetadataDependenceTests(unittest.TestCase):
    def test_excluded_prompt_bridge_and_order(self):
        nodes = [{"id":"a", "raw_sha256":"raw-a", "prompt_group":"p"},
                 {"id":"excluded", "raw_sha256":"raw-b", "prompt_group":"p"},
                 {"id":"c", "raw_sha256":"raw-b", "prompt_group":"q"}]
        groups = components(nodes)
        self.assertEqual(groups, [["a", "c", "excluded"]])
        self.assertEqual(groups, components(list(reversed(nodes))))
        summary = summarize(groups, {"a", "c"}, {"a"})
        self.assertEqual(summary["forced_development_members"], 2)
        self.assertEqual(summary["selected_components"], 1)

    def test_producer_and_unknown_quarantine_are_explicit(self):
        nodes = [{"id":"a", "producer_group":"one", "producer_status":"known-hash"},
                 {"id":"b", "producer_group":"one", "producer_status":"known-hash"},
                 {"id":"c", "producer_group":None, "producer_status":"unknown-or-deleted"},
                 {"id":"d", "producer_group":None, "producer_status":"unknown-or-deleted"}]
        self.assertEqual(len(components(nodes)), 4)
        self.assertEqual(components(nodes, True), [["a","b"],["c","d"]])
        with self.assertRaisesRegex(ValueError, "duplicate"):
            components(nodes+nodes[:1])

    def test_metadata_values_and_no_raw_text(self):
        row = {"image_name":"00000000-0000-4000-8000-000000000001.png", "part_id":948,
               "prompt":" Original Private Prompt ", "seed":42, "user_name":"a"*64}
        result = private_record(row)
        self.assertNotIn(row["prompt"], str(result))
        self.assertNotIn(row["user_name"], str(result))
        self.assertEqual(private_record(dict(row, user_name="deleted_account"))["producer_group"], None)
        self.assertEqual(private_record(dict(row, user_name="deleted_acount"))["producer_group"], None)
        for user in ("bad-user", "", 1):
            with self.assertRaises(ValueError):
                private_record(dict(row,user_name=user))
        with self.assertRaises(ValueError):
            private_record(dict(row,seed=True))


class GroupedAllocationTests(unittest.TestCase):
    def test_reject_retained_without_canonical_identity_or_eligibility(self):
        row={"domain":"ms-coco","release_id":"2017","source_split":"val","source_id":"1","raw_sha256":"r"}
        rejected={"raw_sha256":"r","status":"canonical_rejected_coverage_failure","reason":"unsupported_source_mode_or_alpha"}
        joined=coverage_join(row,rejected)
        self.assertEqual(joined["source_uid"],"ms-coco:2017:val:1")
        self.assertEqual(joined["canonical_pixel_sha256"],"")
        self.assertFalse(joined["independence_certified"])
        self.assertEqual(joined["canonical_rejection_reason"],rejected["reason"])
        for changed in (dict(rejected,raw_sha256="wrong"),dict(rejected,reason=""),
                        dict(rejected,canonical_pixel_sha256="fake"),dict(rejected,status="canonical_pass")):
            with self.assertRaises(ValueError): coverage_join(row,changed)
    def rule(self):
        return {"near_dhash64_max_hamming":6,"near_color8_mean_absolute_difference_max_rgb8":4,
                "near_aspect_relative_difference_max_percent":5}
    def fp(self,uid,value,color=0,width=8,height=8):
        return {"id":uid,"status":"canonical_pass","raw_sha256":uid,
                "canonical_pixel_sha256":"pixel-"+uid,"width":width,"height":height,
                "leakage_dhash64":f"{value:016x}","private_color8_rgb_hex":bytes([color]*192).hex()}
    def test_near_index_matches_bruteforce_and_color_aspect_guards(self):
        import random
        rng=random.Random(31)
        values=[rng.getrandbits(64) for _ in range(40)]
        values += [v^0x0001000100030003 for v in values[:10]]  # radius6 across all4 blocks
        rows=[self.fp(f"node{i:03}",value) for i,value in enumerate(values)]
        expected={(a["id"],b["id"]) for i,a in enumerate(rows) for b in rows[i+1:] if near(a,b)}
        self.assertEqual(set(near_pairs(list(reversed(rows)),self.rule())),expected)
        self.assertFalse(near(self.fp("a",0,0),self.fp("b",0,255)))
        self.assertFalse(near(self.fp("a",0,width=8,height=8),self.fp("b",0,width=8,height=16)))
        self.assertTrue(near(self.fp("a",0,color=0),self.fp("b",0,color=4)))
    def test_full_canonical_excluded_bridge_retained(self):
        a,b,c=self.fp("a",0,0),self.fp("b",2**64-1,255),self.fp("c",0,128)
        c["canonical_pixel_sha256"]=b["canonical_pixel_sha256"]
        metadata={"a":{"raw_sha256":"a","prompt_group":"p"},
                  "b":{"raw_sha256":"b","prompt_group":"p"}}
        groups,_=grouped_frame([a,b,c],metadata,self.rule())
        self.assertEqual(groups[0]["members"],["a","b","c"])
    def fixture(self):
        config={"allocation":{d:{s:1 for s in ("development","validation","test")}
                               for d in ("ms-coco","div2k","diffusiondb")}}
        rows=[{"id":d+str(i),"source_uid":d+str(i),"domain":d,
               "source_split":"valid" if d=="div2k" and i==2 else "train"}
              for d in config["allocation"] for i in range(3)]
        groups=[{"group_id":"group-"+r["id"],"members":[r["id"]]} for r in rows]
        return config,rows,groups
    def test_deterministic_exact_counts_reserved_and_native_holdout(self):
        config,rows,groups=self.fixture(); reserved={"ms-coco0","diffusiondb0"}
        a=allocate(groups,rows,reserved,config)
        self.assertEqual(a,allocate(list(reversed(groups)),list(reversed(rows)),reserved,config))
        for row in a:
            if row["id"] in reserved: self.assertEqual(row["study_split"],"development")
            if row["id"]=="div2k2": self.assertEqual(row["study_split"],"test")
        self.assertTrue(all(r["primary_group_representative"] for r in a))
        from collections import Counter
        self.assertEqual(set(Counter((r["domain"],r["study_split"]) for r in a).values()),{1})
    def test_conflicts_and_oversize_fail_not_group_breaking(self):
        config,rows,groups=self.fixture()
        with self.assertRaisesRegex(ValueError,"holdout"):
            allocate(groups,rows,{"div2k2"},config)
        merged={"group_id":"merged","members":["ms-coco0","ms-coco1","ms-coco2"]}
        groups=[g for g in groups if not g["members"][0].startswith("ms-coco")]+[merged]
        with self.assertRaisesRegex(ValueError,"infeasible"):
            allocate(groups,rows,{"ms-coco0"},config)


class ProvisionalArtifactTests(unittest.TestCase):
    def test_real_coverage_counts_reservations_and_no_science_claim(self):
        import csv
        import hashlib
        import io
        import json
        from collections import Counter, defaultdict
        root=Path(__file__).resolve().parents[1]
        artifact=root/"data/b4-provisional-v2-20260926"
        rows=list(csv.DictReader(io.StringIO((artifact/"splits.csv").read_text(encoding="utf-8"))))
        manifest=list(csv.DictReader(io.StringIO((root/"data/manifest.csv").read_text(encoding="utf-8"))))
        identities=lambda row: ":".join(row[k] for k in ("domain","release_id","source_split","source_id"))
        expected={identities(r):r["raw_sha256"] for r in manifest}
        self.assertEqual({r["source_uid"]:r["raw_sha256"] for r in rows},expected)
        self.assertEqual(len(rows),6900)
        self.assertEqual(Counter(r["domain"] for r in rows),{"ms-coco":1000,"div2k":900,"diffusiondb":5000})
        groups=defaultdict(set)
        for row in rows:
            self.assertEqual(row["independence_certified"],"false")
            groups[row["group_id"]].add(row["study_split"])
        self.assertTrue(all(len(splits)==1 for splits in groups.values()))
        reserved={(r["domain"],r["source_id"]) for r in json.loads((root/"data/dev-ids.json").read_text())["images"]}
        self.assertTrue(all(r["study_split"]=="development" for r in rows if (r["domain"],r["source_id"]) in reserved))
        failures=[r for r in rows if r["canonical_status"]!="canonical_pass"]
        self.assertEqual({r["source_id"] for r in failures},{"205289","431848","455597"})
        self.assertTrue(all(not r["canonical_pixel_sha256"] and r["canonical_rejection_reason"] for r in failures))
        for name in ("holdout.json","sample-size-check.json","b4-observed-group-summary.json"):
            report=json.loads((artifact/name).read_text())
            self.assertFalse(report["final_scientific_split_accepted"])
            self.assertEqual(report["inputs"]["splits_sha256"],hashlib.sha256((artifact/"splits.csv").read_bytes()).hexdigest())
        holdout=json.loads((artifact/"holdout.json").read_text())
        native={r["source_uid"] for r in rows if r["domain"]=="div2k" and r["source_split"]=="valid"}
        self.assertEqual(set(holdout["declared_source_ids"]),native)
        self.assertEqual(len(native),100)
        self.assertTrue(all(r["study_split"]=="test" for r in rows if r["source_uid"] in holdout["linked_test_only_source_ids"]))
        for cell in json.loads((artifact/"sample-size-check.json").read_text())["cells"]:
            pool=[r for r in rows if r["domain"]==cell["domain"] and r["study_split"]==cell["split"]]
            self.assertEqual(cell["images"],len(pool))
            self.assertEqual(cell["observed_groups"],len({r["group_id"] for r in pool}))
            invalid={r["group_id"] for r in pool if r["canonical_status"]!="canonical_pass"}
            self.assertEqual(cell["canonical_screened_candidate_groups_not_certified_independent"],cell["observed_groups"]-len(invalid))


class AdmittedPlanTests(unittest.TestCase):
    def test_declared_outputs_full_coverage_admission_and_class_counts(self):
        import csv
        import hashlib
        import io
        import json
        from collections import Counter, defaultdict
        root=Path(__file__).resolve().parents[1]
        config=json.loads((root/"configs/splits.json").read_text())
        self.assertEqual(config["counts"],{d:config["allocation"][d] for d in ("ms-coco","div2k","diffusiondb")})
        self.assertEqual(config["grouping_rule"],config["grouping"])
        self.assertEqual(config["near_duplicate_threshold"],{k:v for k,v in config["grouping"].items() if k.startswith("near_")})
        manifest_raw=(root/config["source_manifest"]).read_bytes()
        self.assertEqual(hashlib.sha256(manifest_raw).hexdigest(),config["manifest_sha256"])
        admitted=list(csv.DictReader(io.StringIO(manifest_raw.decode())))
        rows=list(csv.DictReader(io.StringIO((root/"data/splits.csv").read_text())))
        identities=lambda r: ":".join(r[k] for k in ("domain","release_id","source_split","source_id"))
        self.assertEqual({r["source_uid"]:r["raw_sha256"] for r in rows},
                         {identities(r):r["raw_sha256"] for r in admitted})
        self.assertEqual(len(rows),6900)
        self.assertTrue(all(r["canonical_status"]=="canonical_pass" and r["canonical_pixel_sha256"] for r in rows))
        self.assertTrue(all(r["image_id"]==r["source_uid"] and r["split"]==r["study_split"] and r["dataset"]==r["domain"] for r in rows))
        self.assertTrue(all(r["independence_certified"]=="false" for r in rows))
        by_group=defaultdict(set)
        for r in rows: by_group[r["group_id"]].add(r["study_split"])
        self.assertTrue(all(len(values)==1 for values in by_group.values()))
        old_dev=json.loads((root/"data/dev-ids.json").read_text())
        new_dev=json.loads((root/config["development_ids"]).read_text())
        self.assertEqual(old_dev["images"],new_dev["images"])
        reserved={(r["domain"],r["source_id"]) for r in old_dev["images"]}
        self.assertTrue(all(r["study_split"]=="development" for r in rows if (r["domain"],r["source_id"]) in reserved))
        report=json.loads((root/"data/sample-size-check.json").read_text())
        self.assertTrue(report["engineering_split_locked"])
        self.assertFalse(report["scientific_compute_authorized"])
        self.assertEqual(len(report["class_cells"]),36)
        self.assertEqual(report["cells"],report["class_cells"])
        self.assertEqual(report["plan_hash"],hashlib.sha256((root/"research/sample-size.md").read_bytes()).hexdigest())
        self.assertEqual(report["split_hash"],hashlib.sha256((root/"data/splits.csv").read_bytes()).hexdigest())
        self.assertEqual(len(report["shortfalls"]),12)
        for cell in report["class_cells"]:
            pool=[r for r in rows if r["domain"]==cell["domain"] and r["study_split"]==cell["split"]]
            self.assertEqual(cell["row_count"],len(pool))
            self.assertEqual(cell["actual_independent_n_under_declared_group_assumption"],len({r["group_id"] for r in pool}))
            self.assertEqual(cell["observed_outcome_count"],0)
            self.assertEqual(cell["actual_independent_n"],cell["actual_independent_n_under_declared_group_assumption"])
            self.assertTrue(cell["actual_independent_n_is_conditional"])
            self.assertFalse(cell["independence_certified"])
        holdout=json.loads((root/"data/holdout.json").read_text())
        self.assertFalse(holdout["required"])
        self.assertIsNone(holdout["domain"])
        self.assertEqual(holdout["ids"],[])
        self.assertTrue(holdout["exclusion_from_dev"])
        self.assertTrue(holdout["reason_if_not_required"])
        self.assertEqual(len(holdout["declared_source_ids"]),100)
        self.assertTrue(all(r["study_split"]=="test" for r in rows if r["source_uid"] in holdout["linked_test_only_source_ids"]))
        self.assertEqual(Counter(r["study_split"] for r in rows),{"development":1500,"validation":1500,"test":3900})


if __name__ == "__main__":
    unittest.main()
