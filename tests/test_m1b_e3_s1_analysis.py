import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]/"scripts"))
import m1b_e3_s1_analysis as A


def detection(semantic=True, full=True, read=True, q="00000001", h="00000002"):
    return dict(outcome="both_match" if full else "none", semantic=dict(found=semantic,content_match=semantic,read=read,decoded_code=q),
                instance=dict(found=full,read=read,decoded_code=h,own_h_content_match=False))


def fixture(n=2):
    sources = [dict(uid=f"u{i}") for i in range(n)]
    plan = dict(protocol="e3-s1-v1", t4_pairs=[])
    rows = {}
    for source in sources:
        u=source["uid"]
        for m in A.METHODS:
            rows[f"src:{u}:{m}:embed"] = dict(outcome="completed",admitted=True,supplier_success=True,returned_final_pixels=True,
                quality=dict(psnr_db=40,ssim_rgb=.95,lpips=.05),payload=dict(q="00000001",h="00000002"))
            rows[f"src:{u}:{m}:clean:C1:qim-pilot-owner-alpha"] = dict(outcome="completed",detection=detection())
            for s in A.STRENGTHS:
                for seed in A.SEEDS:
                    rows[f"t3:{u}:{m}:C1:ddim-{s}-{seed}:qim-pilot-owner-alpha"] = dict(outcome="completed",detection=detection())
    return plan,sources,rows


class S1Analysis(unittest.TestCase):
    def test_joint_admission_penalty_and_missing_positive(self):
        plan,sources,rows=fixture()
        rows["src:u0:e3-s1:embed"]["quality"]["lpips"] = .1
        rows.pop("t3:u1:e3-s1:C1:ddim-0.1-3:qim-pilot-owner-alpha")
        rows.pop("t3:u1:e3-s1:C1:ddim-0.1-4:qim-pilot-owner-alpha")
        out=A.analyse(plan,sources,rows,[])
        self.assertEqual(out["primary"]["0.1"]["e3_success"],0)
        self.assertEqual(out["primary"]["0.2"]["e3_success"],1)
        self.assertEqual(out["primary"]["0.1"]["risk_difference"],-1)
        self.assertEqual(out["secondary_source_majority"]["0.2"]["S"]["e3_success"],2)
        self.assertFalse(out["conjunction_superiority"])
        self.assertEqual(out["primary"]["0.1"]["bootstrap"]["resamples"],100000)

    def test_missing_negatives_are_brackets_not_fictitious_events(self):
        out=A.clustered_negative([[False]*7,[True,None]+[False]*5,[None]*7])
        self.assertEqual(out["positives"],1)
        self.assertEqual(out["unresolved"],1)
        self.assertEqual(out["sources_with_unavailable_calls"],2)
        self.assertEqual(out["completely_evaluated_sources"],1)
        self.assertEqual(out["planned_rate_bounds"],[1/3,2/3])
        self.assertEqual(out["independent_units"],3)
        panel=A.clustered_negative([[False]*42 for _ in range(300)])
        self.assertAlmostEqual(panel["observed_event_interval"]["upper_one_sided_95"],1-.05**(1/300))
        self.assertGreater(panel["observed_event_interval"]["upper_one_sided_95"],.009)

    def test_predicates_checked_does_not_require_found_and_unread_errors_unknown(self):
        d=detection(semantic=False,read=True)
        d["semantic"]["content_match"]=True
        out=A.predicates(d,dict(q="00000001",h="00000002"))
        self.assertFalse(out["S"])
        self.assertTrue(out["C"])
        self.assertTrue(out["D"])
        d["semantic"]["read"]=False
        out=A.predicates(d,dict(q="00000001",h="00000002"))
        self.assertFalse(out["Q"])
        self.assertIsNone(out["q_bit_errors"])

    def test_exact_test_direction_and_holm_and_conjunction(self):
        self.assertEqual(A.paired([True]*5,[False]*5)["exact_mcnemar_one_sided_p"],.03125)
        self.assertEqual(A.paired([False]*5,[True]*5)["exact_mcnemar_one_sided_p"],1)
        self.assertEqual(A.paired([False],[False])["exact_mcnemar_one_sided_p"],1)
        self.assertEqual(A.holm([.03125,.04]),[.0625,.0625])
        plan,sources,rows=fixture(5)
        for source in sources:
            for seed in A.SEEDS:
                rows[f"t3:{source['uid']}:v5-r3:C1:ddim-0.1-{seed}:qim-pilot-owner-alpha"]["detection"]=detection(False,False)
        out=A.analyse(plan,sources,rows,[])
        self.assertFalse(out["conjunction_superiority"])
        self.assertEqual(out["primary"]["0.1"]["holm_individual_p"],.0625)
        for source in sources:
            for seed in A.SEEDS:
                rows[f"t3:{source['uid']}:v5-r3:C1:ddim-0.2-{seed}:qim-pilot-owner-alpha"]["detection"]=detection(False,False)
        out=A.analyse(plan,sources,rows,[])
        self.assertTrue(out["conjunction_superiority"])
        self.assertGreater(out["primary"]["0.1"]["holm_individual_p"],.05)

    def test_transfer_delivery_from_none_and_zero_delivery_undefined(self):
        plan,sources,rows=fixture()
        plan["t4_pairs"]=[dict(pair_index=0,donor_uid="u0",recipient_uid="u1")]
        for m in A.METHODS:
            rows[f"t4:0:{m}:public:combined"]=dict(outcome="completed",detection=detection(True,True),payload=dict(q="1",h="2"),
                same_call_predicates=dict(semantic_only=True,perceptual_only=False,combined=True),quality_vs_recipient=dict(lpips=.25))
            rows[f"t4:0:{m}:public:none"]=dict(outcome="completed",detection=detection(False,False,q="3"),payload=dict(q="1",h="2"))
        out=A.analyse(plan,sources,rows,[])
        transfer=out["transfers"]["t4"]["public"]["methods"]["e3-s1"]
        self.assertEqual(transfer["events"]["F"]["positives"],1)
        self.assertEqual(transfer["events"]["D"]["positives"],0)
        self.assertIsNone(transfer["conditional_observed_D"]["F_rate"])
        self.assertEqual(transfer["same_call_discordance"]["perceptual_only"]["discordant"],1)
        self.assertEqual(transfer["lpips_descriptive"]["0.2"]["subset_pairs"],[])
        self.assertEqual(transfer["lpips_descriptive"]["0.3"]["subset_pairs"],[0])
        self.assertEqual(out["t5_selection"]["shortfall"],30)
        rows["t4:0:e3-s1:public:none"]["detection"]=detection(False,False)
        rows.pop("t4:0:e3-s1:public:combined")
        out=A.analyse(plan,sources,rows,[])
        transfer=out["transfers"]["t4"]["public"]["methods"]["e3-s1"]
        self.assertEqual(transfer["conditional_observed_D"]["n"],1)
        self.assertEqual(transfer["conditional_observed_D"]["F_bounds"],[0,1])
        self.assertIsNone(transfer["conditional_observed_D"]["F_rate"])
        self.assertEqual(out["transfers"]["t4"]["public"]["paired_unavailable"],1)

    def test_four_owner_negative_family_denominators(self):
        plan,sources,rows=fixture()
        for source in sources:
            u=source["uid"]
            for m in A.METHODS:
                for arm in ("C0","C1"):
                    for owner in A.OWNERS:
                        if arm=="C1" and owner==A.OWNERS[0]:
                            continue
                        rows[f"src:{u}:{m}:clean:{arm}:{owner}"]=dict(outcome="completed",detection=detection(False,False))
        out=A.analyse(plan,sources,rows,[])
        negatives=out["methods"]["e3-s1"]["negatives"]
        self.assertEqual(len([key for key in negatives["cells"] if key.startswith("clean:")]),7)
        self.assertEqual(negatives["clean_source_any"]["planned"],2)
        self.assertEqual(negatives["clean_source_any"]["completely_evaluated_sources"],2)
        self.assertEqual(negatives["clean_source_any"]["positives"],0)

    def test_sham_delivery_not_applicable_unknown_predicates_and_identity_quality(self):
        plan,sources,rows=fixture()
        plan["t4_pairs"]=[dict(pair_index=0,donor_uid="u0",recipient_uid="u1")]
        plan["t5"]=dict(max_pairs=2)
        rows["src:u0:e3-s1:embed"]["quality"]=dict(psnr_db=None,psnr_infinite=True,ssim_rgb=1,lpips=0)
        rows["t4:0:e3-s1:public-sham:combined"]=dict(outcome="completed",detection=detection(),
            same_call_predicates=dict(combined=True,semantic_only=None,perceptual_only=False),content_diagnostics=dict(route="operational"))
        rows["t4:0:e3-s1:public-sham:none"]=dict(outcome="completed",detection=detection())
        out=A.analyse(plan,sources,rows,[])
        sham=out["transfers"]["t4"]["public-sham"]["methods"]["e3-s1"]
        self.assertEqual(sham["events"]["F"]["positives"],1)
        self.assertIsNone(sham["events"]["D"])
        self.assertIsNone(sham["conditional_observed_D"])
        self.assertIsNone(sham["per_pair"][0]["native_modes"]["none"]["Q"])
        self.assertEqual(sham["same_call_discordance"]["semantic_only"],dict(discordant=0,known=0,unknown=1))
        self.assertEqual(sham["same_call_acceptance"]["combined"]["accepted"],1)
        self.assertEqual(sham["per_pair"][0]["content_diagnostics"]["route"],"operational")
        self.assertEqual(out["t5_selection"]["shortfall"],2)
        quality=out["methods"]["e3-s1"]["clean_coverage"]["metrics"]["psnr_db"]
        self.assertEqual((quality["infinite"],quality["absent"]),(1,0))

    def test_strict_boundaries_and_reproducible_source_bootstrap(self):
        self.assertFalse(A.strict_quality(dict(psnr_db=35,ssim_rgb=.95,lpips=.05)))
        self.assertFalse(A.strict_quality(dict(psnr_db=40,ssim_rgb=.9,lpips=.05)))
        self.assertTrue(A.strict_quality(dict(psnr_infinite=True,ssim_rgb=1,lpips=0)))
        a=A.paired([True,False,True],[False,True,False],bootstrap=True)
        b=A.paired([True,False,True],[False,True,False],bootstrap=True)
        self.assertEqual(a,b)

    def test_full_300_source_fake_journal_bookkeeping(self):
        """Synthetic dictionaries only: full fixed schedule and adverse missingness."""
        plan,sources,rows=fixture(300)
        plan["t4_pairs"]=[dict(pair_index=k,donor_uid=f"u{2*k}",recipient_uid=f"u{2*k+1}") for k in range(30)]
        plan["t5"]=dict(max_pairs=30)
        selected=[dict(left=f"u{60+2*k}",right=f"u{61+2*k}") for k in range(30)]
        ids=A.planned_ids(plan,sources,selected)
        self.assertEqual(len(ids),42031)
        self.assertEqual(len(ids),len(set(ids)))
        for rid in ids:
            rows.setdefault(rid,dict(outcome="completed",detection=detection(False,False),payload=dict(q="1",h="2")))
        rows["t5desc:0"]["descriptors"]=dict(clip_cosine_views1=.6,clip_cosine_views7=.7)
        rows["src:u0:e3-s1:embed"]["quality"]["lpips"]=.1
        for source in sources[:10]:
            for strength in A.STRENGTHS:
                for seed in A.SEEDS:
                    rows[f"t3:{source['uid']}:v5-r3:C1:ddim-{strength}-{seed}:{A.OWNERS[0]}"]["detection"]=detection(False,False)
        out=A.analyse(plan,sources,rows,selected)
        self.assertTrue(out["inventory"]["complete"])
        self.assertEqual(out["inventory"]["available"],42031)
        self.assertEqual(out["primary"]["0.1"]["e3_success"],299)
        self.assertEqual(out["primary"]["0.1"]["v5_success"],290)
        self.assertEqual(out["primary"]["0.1"]["e3_only"],9)
        self.assertTrue(out["conjunction_superiority"])
        self.assertEqual(out["methods"]["e3-s1"]["negatives"]["clean_source_any"]["completely_evaluated_sources"],300)
        self.assertEqual(out["methods"]["e3-s1"]["negatives"]["t3_source_any"]["independent_units"],300)
        self.assertEqual(out["methods"]["e3-s1"]["negatives"]["cells"][f"t3:C0:{A.OWNERS[0]}:0.1"]["planned"],900)
        self.assertIsNone(out["methods"]["v5-r3"]["clean_coverage"]["counts"]["supplier_success"])
        self.assertFalse(out["methods"]["v5-r3"]["clean_coverage"]["supplier_applicable"])
        self.assertEqual(out["t5_selection"]["source_descriptors"][0]["descriptors"]["clip_cosine_views7"],.7)
        rows.pop(f"src:u0:e3-s1:clean:C0:{A.OWNERS[0]}")
        rows.pop(f"src:u1:e3-s1:clean:C0:{A.OWNERS[0]}")
        rows[f"src:u1:e3-s1:clean:C0:{A.OWNERS[1]}"]["detection"]=detection(True,False)
        rows[f"t3:u2:e3-s1:C0:ddim-0.1-3:{A.OWNERS[0]}"]=dict(outcome="safety_blocked")
        out=A.analyse(plan,sources,rows,selected)
        self.assertFalse(out["inventory"]["complete"])
        self.assertEqual(out["inventory"]["states"]["not_attempted"],2)
        self.assertEqual(out["inventory"]["states"]["safety_blocked"],1)
        clean=out["methods"]["e3-s1"]["negatives"]["clean_source_any"]
        self.assertEqual((clean["positives"],clean["unresolved"]),(1,1))
        self.assertEqual(clean["planned_rate_bounds"],[1/300,2/300])
        t3=out["methods"]["e3-s1"]["negatives"]["t3_source_any"]
        self.assertEqual(t3["planned_rate_bounds"],[0,1/300])


if __name__=="__main__":
    unittest.main()
