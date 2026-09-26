import unittest
from b4_source_admission import admit
from build_b3_manifest import manifest_row


class SourceAdmissionTests(unittest.TestCase):
    def fixture(self):
        items=[{"source_id":str(i),"raw_sha256":str(i)*64,"relative_path":str(i)+".jpg",
                "raw_size_bytes":100,"width":64,"height":64,"license_id":4,
                "license_reference":"http://creativecommons.org/licenses/by/2.0/"} for i in range(1,5)]
        rows=[manifest_row("ms-coco","coco-2017","val2017",r["source_id"],r["relative_path"],
                r["raw_sha256"],100,64,64,"https://example.org/source","https://example.org/terms","local only")
              for r in items[:3]]
        candidates={"candidates":items[:3],"ordered_reserves":items[3:]}
        canonical={"ms-coco:"+r["source_id"]:{"status":"canonical_pass","raw_sha256":r["raw_sha256"],
                   "source_width":64,"source_height":64} for r in items}
        canonical["ms-coco:2"].update(status="canonical_rejected_coverage_failure",reason="unsupported_source_mode_or_alpha")
        return rows,candidates,canonical,[dict(rows[0])]

    def test_fixed_reserve_repair_preserves_original_and_development(self):
        rows,candidates,canonical,reserved=self.fixture()
        repaired,rejects,replacements=admit(rows,candidates,canonical,reserved,target=3)
        self.assertEqual([r["source_id"] for r in repaired],["1","3","4"])
        self.assertEqual(replacements,[{"source_id":"4","raw_sha256":"4"*64,"ordered_reserve_index":0}])
        self.assertEqual(rejects[0]["source_id"],"2")
        self.assertTrue(rejects[0]["was_original_candidate"])
        self.assertEqual([r["source_id"] for r in rows],["1","2","3"])
        self.assertEqual(repaired,admit(list(reversed(rows)),candidates,canonical,reserved,target=3)[0])
        self.assertEqual(repaired[0],rows[0])
        self.assertEqual(repaired[-1]["rights_status"],"pending-image-rights")

    def test_fail_closed_identity_capacity_and_development(self):
        rows,candidates,canonical,reserved=self.fixture()
        with self.assertRaisesRegex(ValueError,"development"):
            admit(rows,candidates,canonical,[dict(rows[1])],target=3)
        canonical["ms-coco:4"].update(status="canonical_rejected_coverage_failure",reason="failure")
        with self.assertRaisesRegex(ValueError,"insufficient"):
            admit(rows,candidates,canonical,reserved,target=3)
        canonical["ms-coco:4"].update(status="canonical_pass",raw_sha256="wrong")
        with self.assertRaisesRegex(ValueError,"identity"):
            admit(rows,candidates,canonical,reserved,target=3)


if __name__=="__main__": unittest.main()
