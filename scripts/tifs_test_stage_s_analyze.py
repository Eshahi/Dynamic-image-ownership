"""Synthetic JSON-only analysis tests. No image/model/science operations."""
import copy
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tifs_common as common
import tifs_stage_s_analyze as analysis

TD = Path(__file__).resolve().parents[1]/"research/tifs-20261028/stage-s"


def call(positive, exact=True):
    return dict(status="ok",raw=dict(semantic=dict(read=positive,found=positive,content_match=positive,decoded_code="a" if exact else "b"),
        instance=dict(read=positive,found=positive,decoded_code="f"),outcome="both_match" if positive else "neither_match"))


def bound_call(positive, exact=True):
    """Structurally complete synthetic bound-reader receipt, not neural data."""
    result = call(positive, exact)
    result["raw"]["native"] = dict(raw=dict(decoded_message=[0]*100, probabilities=[.1]*100))
    result["raw"]["carrier_decode"] = dict(unique=positive, candidates=int(positive), candidates_examined=41449,
        radius=4, status="unique" if positive else "no_codeword", q=("a" if exact else "b") if positive else None,
        h="f" if positive else None, distance=0 if positive else None)
    result["delivery"] = dict(raw_payload_exact=positive, corrected_payload_exact=positive and exact,
        decoded_h_bit_errors=0 if positive else None)
    for field,width in (("raw_payload",100),("raw_q",32),("raw_tag",36),("raw_masked_h",32)):
        result["delivery"].update({field+"_bit_errors":0 if positive else width//2, field+"_accuracy":1.0 if positive else .5})
    return result


def fixture():
    config = common.load_json(TD/"frozen-config.json")
    manifest = common.load_json(TD/"source-manifest.json")
    sources = [str(r["source_id"]) for r in manifest["screen_donors"]]
    targets = [str(r["source_id"]) for r in manifest["screen_targets"]]
    prepared = dict(pairs=[dict(donor=s,target=t) for s,t in zip(sources,targets)])
    expected = analysis.expected_inventory(config,sources,prepared["pairs"])
    producers, detections, qualities = {}, {}, {}
    for stage, ids in expected.items():
        producers[stage] = {}
        for uid in ids:
            fields = uid.split(":")
            arm = fields[-2] if stage == "threats" else fields[-1]
            sid = fields[2] if stage in ("native","secondary","threats") else fields[1]
            row = dict(id=uid,status="ok",arm=arm,source=sid,output=dict(sha256="a"*64),payload=dict(q="a",h="f"))
            if arm == "vine-b": row["payload"]["bits"] = [0]*100
            producers[stage][uid] = row
            qualities["quality:"+uid] = dict(id="quality:"+uid,status="ok",input_sha256="a"*64,
                total=dict(psnr_db=40,ssim_rgb=.99,lpips=.01))
            for method in config["arms"]:
                if method == "unmarked" or arm not in (method,"unmarked"):
                    continue
                positive = arm != "unmarked" and stage != "threats"
                if stage == "native" and fields[1] != "R0-0.2":
                    positive = arm == method == "f6-noise"
                uid_det = f"det:{method}:{uid}"
                if method in analysis.INTERNAL:
                    make_call = bound_call if method == "vine-b" else call
                    calls = {config["owners"]["positive"]:make_call(positive),config["owners"]["wrong"]:make_call(False)}
                    modes = {mode:make_call(False) for mode in analysis.read_modes(config,method)} if stage=="threats" else {}
                else:
                    calls = {config["owners"]["positive"]:dict(status="ok",presence=dict(present=positive),wrong_message_presence=dict(present=False))}
                    modes = {}
                detections[uid_det] = dict(id=uid_det,status="ok",input_sha256="a"*64,calls=calls,modes=modes)
    return config,manifest,prepared,producers,detections,qualities


class AnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = fixture()

    def run_analysis(self, values=None, **kwargs):
        return analysis.analyze(*(values or self.base),**kwargs)

    def test_complete_go_exact_inventory_and_tables(self):
        r = self.run_analysis()
        self.assertEqual(r["verdict"],"GO")
        self.assertTrue(r["inventory_complete"])
        self.assertEqual({x["stage"]:x["expected"] for x in r["inventory"]},
                         dict(clean=176,native=2112,secondary=1408,threats=1232,detect=8960,quality=4928))
        self.assertTrue(all(x["status"]=="pass" for x in r["gates"]))
        self.assertAlmostEqual(r["zero_event_source_upper_95"],.1707497229824809)
        with tempfile.TemporaryDirectory() as tmp:
            analysis.write_report(r,tmp)
            self.assertEqual(common.load_json(Path(tmp)/"analysis.json")["verdict"],"GO")
            self.assertTrue((Path(tmp)/"native.csv").read_text().startswith("arm,cell,rule"))

    def test_missing_absent_and_failed_outputs_are_not_negative(self):
        vals = copy.deepcopy(self.base)
        c,m,p,pro,det,q = vals
        sid = str(m["screen_donors"][0]["source_id"])
        uid=f"native:R1-0.1:{sid}:0:f6-noise"
        pro["native"][uid]["status"]="safety_blocked"
        r=self.run_analysis(vals)
        self.assertEqual(r["verdict"],"INCOMPLETE")
        n=next(x for x in r["native"] if x["arm"]=="f6-noise" and x["cell"]=="R1-0.1" and x["rule"]=="J")
        self.assertEqual((n["lower"],n["upper"],n["missing_seed_outcomes"]),(16,16,1))
        uid=f"native:R1-0.1:{sid}:1:f6-noise"
        del pro["native"][uid]
        r=self.run_analysis(vals)
        n=next(x for x in r["native"] if x["arm"]=="f6-noise" and x["cell"]=="R1-0.1" and x["rule"]=="J")
        self.assertEqual((n["lower"],n["upper"]),(15,16))

    def test_exact_original_q_is_not_historical_C(self):
        vals=copy.deepcopy(self.base)
        c,m,p,pro,det,q=vals
        for uid,row in det.items():
            if uid.startswith("det:f6-noise:native:R1-0.1:"):
                row["calls"][c["owners"]["positive"]]=call(True,exact=False)
        r=self.run_analysis(vals)
        self.assertEqual(r["verdict"],"SCIENTIFIC_KILL")
        rows={x["rule"]:x for x in r["native"] if x["arm"]=="f6-noise" and x["cell"]=="R1-0.1"}
        self.assertEqual(rows["C"]["lower"],16)
        self.assertEqual(rows["J"]["upper"],0)
        self.assertIsNone(analysis.endpoint(call(True),{},"J"))
        self.assertFalse(analysis.endpoint(call(False),{},"J"))

    def test_gain_missingness_uses_comparator_upper(self):
        vals=copy.deepcopy(self.base)
        c,m,p,pro,det,q=vals
        # Six comparator source majorities become unresolved, not false.
        for row in m["screen_donors"][:6]:
            sid=str(row["source_id"])
            for seed in c["seeds"]:
                del det[f"det:f5-r2:native:R1-0.1:{sid}:{seed}:f5-r2"]
        r=self.run_analysis(vals)
        gain=next(x for x in r["gains"] if x["rule"]=="J" and x["cell"]=="R1-0.1" and x["comparator"]=="f5-r2")
        self.assertEqual((gain["lower"],gain["upper"]),(10,16))
        self.assertEqual(r["verdict"],"INCOMPLETE")

    def test_proved_failure_precedes_resource_stop_and_missingness(self):
        vals=copy.deepcopy(self.base)
        uid=next(uid for uid in vals[5] if uid.endswith(":f6-noise") and uid.startswith("quality:clean:"))
        vals[5][uid]["total"]["psnr_db"]=35
        r=self.run_analysis(vals,resource_stop=True)
        self.assertEqual(r["verdict"],"SCIENTIFIC_KILL")
        self.assertEqual(self.run_analysis(resource_stop=True)["verdict"],"RESOURCE_STOP")
        vals[5][uid]["total"]["psnr_db"]=None
        self.assertEqual(self.run_analysis(vals)["verdict"],"INCOMPLETE")

    def test_clean_F_and_paired_medians_are_independent_bars(self):
        for metric, value in (("lpips",.016),("psnr_db",38.9)):
            vals=copy.deepcopy(self.base)
            for uid,row in vals[5].items():
                if uid.startswith("quality:clean:") and uid.endswith(":f6-noise"):
                    row["total"][metric]=value
            r=self.run_analysis(vals)
            self.assertEqual(r["verdict"],"SCIENTIFIC_KILL")
            self.assertEqual(next(g for g in r["gates"] if g["name"]=="paired_median:"+metric)["status"],"fail")
        vals=copy.deepcopy(self.base)
        c,m,p,pro,det,q=vals
        ids=[uid for uid in det if uid.startswith("det:f6-noise:clean:") and uid.endswith(":f6-noise")]
        det[ids[0]]["calls"][c["owners"]["positive"]]=call(False)
        self.assertEqual(self.run_analysis(vals)["verdict"],"GO")
        det[ids[1]]["calls"][c["owners"]["positive"]]=call(False)
        self.assertEqual(self.run_analysis(vals)["verdict"],"SCIENTIFIC_KILL")

    def test_eligible_threat_event_vs_ineligible_missing(self):
        vals=copy.deepcopy(self.base)
        c,m,p,pro,det,q=vals
        uid=next(uid for uid in det if uid.startswith("det:f6-noise:threat:") and uid.endswith(":patch128"))
        det[uid]["modes"]["combined"]=call(True)
        self.assertEqual(self.run_analysis(vals)["verdict"],"SCIENTIFIC_KILL")
        producer=uid[len("det:f6-noise:"):]
        q["quality:"+producer]["total"]["lpips"]=.2
        self.assertEqual(self.run_analysis(vals)["verdict"],"GO")
        q["quality:"+producer]["total"]["lpips"]=None
        self.assertEqual(self.run_analysis(vals)["verdict"],"INCOMPLETE")

    def test_negative_missingness_and_baseline_events(self):
        vals=copy.deepcopy(self.base)
        c,m,p,pro,det,q=vals
        uid=next(uid for uid in det if uid.startswith("det:f6-noise:clean:") and uid.endswith(":unmarked"))
        det[uid]["calls"][c["owners"]["positive"]]=call(True)
        self.assertEqual(self.run_analysis(vals)["verdict"],"SCIENTIFIC_KILL")
        del det[uid]
        self.assertEqual(self.run_analysis(vals)["verdict"],"INCOMPLETE")
        vals=copy.deepcopy(self.base)
        uid=next(uid for uid in vals[4] if uid.startswith("det:v5-r3:clean:") and uid.endswith(":unmarked"))
        vals[4][uid]["calls"][c["owners"]["positive"]]=call(True)
        self.assertEqual(self.run_analysis(vals)["verdict"],"GO")

    def test_disabled_binding_is_diagnostic_but_wrong_owner_threat_is_primary(self):
        vals=copy.deepcopy(self.base)
        c,m,p,pro,det,q=vals
        uid=next(uid for uid in det if uid.startswith("det:f6-noise:threat:") and ":f6-noise:patch128" in uid)
        det[uid]["modes"]["none"]=call(True)
        self.assertEqual(self.run_analysis(vals)["verdict"],"GO")
        det[uid]["calls"][c["owners"]["wrong"]]=call(True)
        self.assertEqual(self.run_analysis(vals)["verdict"],"SCIENTIFIC_KILL")
        det[uid]["calls"][c["owners"]["wrong"]]=call(False)
        uid=next(uid for uid in det if uid.startswith("det:f6-noise:threat:") and ":unmarked:patch128" in uid)
        det[uid]["calls"][c["owners"]["positive"]]=call(True)
        self.assertEqual(self.run_analysis(vals)["verdict"],"SCIENTIFIC_KILL")

    def test_missing_binding_ablation_is_incomplete(self):
        vals=copy.deepcopy(self.base)
        uid=next(uid for uid in vals[4] if uid.startswith("det:f6-noise:threat:") and ":f6-noise:patch128" in uid)
        del vals[4][uid]["modes"]["none"]
        result=self.run_analysis(vals)
        self.assertEqual(result["verdict"],"INCOMPLETE")
        self.assertFalse(result["inventory_complete"])

    def test_secondary_is_descriptive_but_inventory_required(self):
        vals=copy.deepcopy(self.base)
        c,m,p,pro,det,q=vals
        for uid,row in det.items():
            if uid.startswith("det:f6-noise:secondary:"):
                row["calls"][c["owners"]["positive"]]=call(False)
        self.assertEqual(self.run_analysis(vals)["verdict"],"GO")
        uid=next(uid for uid in det if uid.startswith("det:f6-noise:secondary:") and uid.endswith(":unmarked"))
        det[uid]["calls"][c["owners"]["positive"]]=call(True)
        r=self.run_analysis(vals)
        self.assertEqual(r["verdict"],"GO")
        self.assertTrue(any(x["control"]=="C0" and x["lower"]>0 and x["selection_weight"]==0 for x in r["secondary"]))
        del pro["secondary"][next(iter(pro["secondary"]))]
        self.assertEqual(self.run_analysis(vals)["verdict"],"INCOMPLETE")

    def test_hash_mismatch_and_inflight_tail_prevent_go(self):
        vals=copy.deepcopy(self.base)
        vals[4][next(iter(vals[4]))]["input_sha256"]="b"*64
        self.assertEqual(self.run_analysis(vals)["verdict"],"INCOMPLETE")
        self.assertEqual(self.run_analysis(tails=[dict(path="x",bytes=2)])["verdict"],"INCOMPLETE")

    def test_shard_overlap_and_missing_preparation(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths=[Path(tmp)/str(i) for i in range(2)]
            for path in paths:
                common.Journal(path).append(dict(id="x",status="ok"))
            with self.assertRaises(ValueError):
                analysis.merge_journals(paths)
        vals=copy.deepcopy(self.base)
        vals=list(vals);vals[2]=None;vals[3]["threats"]={};vals[4]={};vals[5]={}
        self.assertEqual(self.run_analysis(vals)["verdict"],"INCOMPLETE")


if __name__=="__main__":
    unittest.main()
