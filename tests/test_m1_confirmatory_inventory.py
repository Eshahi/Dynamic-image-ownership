"""Synthetic metadata fixtures only: no dataset paths are followed."""
import copy
import itertools
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import m1_confirmatory_inventory as module
import m1_confirmatory_worker_contract  # import before no-I/O guards


def fixture():
    clean=[dict(source_uid=f"synthetic:{n}",group_id=f"group-{n}",owner=f"owner-{n%16}",
        wrong_owner=f"owner-{(n+1)%16}",seed_uint64_hex=f"{2**63+n:016x}",
        seed_uint64_decimal=str(2**63+n)) for n in range(300)]
    schedule=dict(schema_version="m1-coco512-metadata-schedule-v1",candidate="UNRESOLVED",
        source_contract_accepted=False,scientific_run_authorized=False,images_or_annotations_opened=False,
        clean=clean,t3_source_uids=[r["source_uid"] for r in clean[:30]],
        t4_pairs=[dict(pair_index=n,donor_uid=clean[n]["source_uid"],recipient_uid=clean[n+32]["source_uid"]) for n in range(30)],
        t5=dict(status="post-approval-only",design="bounded disjoint30 pairs",
            annotation_signature="identical nonempty noncrowd COCO category sets",
            minimum_source_phash_hamming=8,maximum_pairs=30,selection_tag="m1-coco512-t5-v1",no_replacement=True))
    index=dict(schema_version="m1-confirmatory-external-index-v1",candidate="UNRESOLVED",
        source_contract_accepted=False,scientific_split_accepted=False,scientific_unlock=False,
        scientific_compute_authorized=False,images_annotations_features_opened=False,
        entries=[dict(row,schedule_index=n,external_raw_path="NEVER_OPEN/raw/private.jpg") for n,row in enumerate(clean)],input_errors=[])
    return schedule,index


class InventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schedule,cls.index=fixture()
        cls.result=module.build_inventory(cls.schedule,cls.index)

    def test_counts_separate_methods_and_kinds(self):
        self.assertEqual(len(self.result["units"]),9120)
        for method in ("candidate","v5"):
            rows=[u for u in self.result["units"] if u["method"]==method]
            self.assertEqual(sum(u["kind"]=="image" for u in rows),1800)
            self.assertEqual(sum(u["kind"]=="query" for u in rows),2610)
            self.assertEqual(sum(u["kind"]=="stage" for u in rows),300 if method=="candidate" else 0)
        self.assertIsNone(self.result["scientific_config"])
        self.assertFalse(self.result["scientific_unlock"])
        self.assertEqual(len({u["artifact_namespace"] for u in self.result["units"]}),9120)

    def test_pure_builder_no_path_io_or_mutation(self):
        schedule,index=fixture(); original=copy.deepcopy((schedule,index))
        with patch.object(Path,"read_bytes",side_effect=AssertionError("read forbidden")), patch.object(Path,"read_text",side_effect=AssertionError("read forbidden")), patch.object(Path,"stat",side_effect=AssertionError("stat forbidden")), patch.object(Path,"resolve",side_effect=AssertionError("resolve forbidden")):
            first=module.build_inventory(schedule,index)
            second=module.build_inventory(schedule,index)
        self.assertEqual(first,second)
        self.assertEqual((schedule,index),original)
        self.assertNotIn("NEVER_OPEN",str(first))

    def test_t3_untouched_inputs_and_query_asymmetry(self):
        by_id={u["id"]:u for u in self.result["units"]}
        for method in ("candidate","v5"):
            images=[u for u in by_id.values() if u["method"]==method and u["axis"]=="T3" and u["kind"]=="image"]
            self.assertEqual(len(images),780)
            self.assertEqual(len({u["source_cluster"] for u in images}),30)
            for image in images:
                self.assertEqual(len(image["dependencies"]),1)
                parent=by_id[image["dependencies"][0]]
                self.assertEqual(parent["axis"],"clean")
                self.assertEqual(parent["arm"],image["arm"])
                queries=[u for u in by_id.values() if u["kind"]=="query" and u["dependencies"]==[image["id"]]]
                self.assertEqual(len(queries),1 if image["arm"]=="C0" else 2)

    def test_t4_claim_roles_survive_owner_coincidence(self):
        rows=[u for u in self.result["units"] if u["axis"]=="T4" and u["method"]=="candidate"]
        self.assertTrue(all(u["same_public_owner"] for u in rows if u["kind"]=="query"))
        for image in (u for u in rows if u["kind"]=="image"):
            queries=[u for u in rows if u["kind"]=="query" and u["dependencies"]==[image["id"]]]
            self.assertEqual({u["claim_role"] for u in queries},{"donor","recipient"})
            self.assertEqual(len(image["dependencies"]),2)
            self.assertNotEqual(image["donor_uid"],image["recipient_uid"])

    def test_t5_complete_metadata_universe_not_eligibility(self):
        ledger=self.result["t5_pair_eligibility_ledger"]
        self.assertEqual(len(ledger),44850)
        self.assertEqual({(r["left_source_index"],r["right_source_index"]) for r in ledger},set(itertools.combinations(range(300),2)))
        self.assertTrue(all(r["eligibility"] is None and r["selected"] is None for r in ledger))
        self.assertFalse(any(u["axis"]=="T5" for u in self.result["units"]))
        self.assertIsNone(self.result["counts"]["candidate"]["T5"]["actual_planned_queries"])
        self.assertEqual(self.result["t5_post_unlock"]["unmarked_endpoint_artifact"],"C0-source")

    def test_missing_receipts_preserve_full_planned_denominator(self):
        schedule,index=fixture(); index["input_errors"]=[{"reason":"missing_source_receipt","source_uid":"synthetic:2"}]
        result=module.build_inventory(schedule,index)
        self.assertEqual(len(result["units"]),9120)
        self.assertEqual(result["external_index_errors"],index["input_errors"])

    def test_subset_duplicate_foreign_and_unlocked_rejected(self):
        for mutation in (lambda s:s["clean"].pop(),
                         lambda s:s["clean"].__setitem__(1,copy.deepcopy(s["clean"][0])),
                         lambda s:s["t3_source_uids"].__setitem__(0,"foreign"),
                         lambda s:s["t4_pairs"][1].update(donor_uid=s["t4_pairs"][0]["donor_uid"]),
                         lambda s:s.update(scientific_run_authorized=True),
                         lambda s:s["t5"].update(minimum_source_phash_hamming=7)):
            schedule,index=fixture(); mutation(schedule)
            with self.assertRaises(ValueError): module.build_inventory(schedule,index)

    def test_uint64_exactness_and_index_join(self):
        schedule,index=fixture(); schedule["clean"][0]["seed_uint64_decimal"]=float(2**63)
        with self.assertRaises(ValueError): module.build_inventory(schedule,index)
        schedule,index=fixture(); index["entries"][2]["group_id"]="other"
        with self.assertRaises(ValueError): module.build_inventory(schedule,index)
        schedule,index=fixture(); index["scientific_unlock"]=True
        with self.assertRaises(ValueError): module.build_inventory(schedule,index)

    def test_dag_missing_dependency_cycle_duplicate_and_missing_pair(self):
        for mutation in (lambda r:r["units"][0]["dependencies"].append("not-declared"),
                         lambda r:r["units"][0]["dependencies"].append(r["units"][2]["id"]),
                         lambda r:r["units"][1].update(id=r["units"][0]["id"]),
                         lambda r:r["t5_pair_eligibility_ledger"].pop()):
            result=copy.deepcopy(self.result); mutation(result)
            with self.assertRaises(ValueError): module.validate_inventory(result)

if __name__=="__main__": unittest.main()
