"""Synthetic numerical fixtures; no retained scientific data are analyzed here."""
import json
import math
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
import torch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import m1_initializer_legacy_comparison as module

class ComparisonTests(unittest.TestCase):
    def test_exact_zero_and_analytic_float64_delta(self):
        left=torch.tensor([1.,2.,3.,4.],dtype=torch.float32)
        exact=module.latent_difference(left,left.clone())
        self.assertTrue(exact["values_exact"])
        self.assertTrue(exact["bytes_exact"])
        self.assertEqual(exact["l2"],0)
        result=module.latent_difference(left+torch.tensor([3.,0.,0.,4.]),left)
        self.assertEqual(result["l2"],5)
        self.assertEqual(result["rms"],2.5)
        self.assertEqual(result["max_abs"],4)
        self.assertFalse(result["values_exact"])
        self.assertIsNone(result["closeness_tolerance"])
        self.assertFalse(result["reuse_claim"])

    def test_signed_zero_exact_value_separate_storage_flag(self):
        result=module.latent_difference(torch.tensor([0.]),torch.tensor([-0.]))
        self.assertTrue(result["values_exact"])
        self.assertFalse(result["bytes_exact"])
        self.assertEqual(result["rms"],0)
        typed=module.latent_difference(torch.ones(1,dtype=torch.float64),torch.ones(1,dtype=torch.float32))
        self.assertTrue(typed["values_exact"])
        self.assertFalse(typed["dtype_equal"])
        self.assertFalse(typed["bytes_exact"])

    def test_nonfinite_shape_type_and_overflow_refused(self):
        for a,b in ((torch.tensor([float("nan")]),torch.zeros(1)),(torch.zeros(1),torch.zeros(2)),
            (torch.tensor([True]),torch.tensor([False])),(torch.tensor([],dtype=torch.float32),torch.tensor([])),
            (torch.tensor([1e308],dtype=torch.float64),torch.tensor([-1e308],dtype=torch.float64))):
            with self.assertRaises(ValueError):module.latent_difference(a,b)

    def test_recorded_metrics_signed_missing_bool_nonfinite(self):
        self.assertEqual(module.metric_difference(2.,5.)["new_minus_legacy"],-3.)
        for value in (None,True,"0.1",float("nan"),float("inf")):
            result=module.metric_difference(value,.5)
            self.assertIsNone(result["new_minus_legacy"])
            json.dumps(result,allow_nan=False)
        self.assertIsNone(module.metric_difference(1e308,-1e308)["new_minus_legacy"])

    def test_same_source_identity_and_mismatches(self):
        new=dict(id=1675,raw_sha256="a"*64,native_shape=[480,640,3],rgb8_sha256="b"*64)
        old=dict(id=1675,raw_sha256="a"*64,native_shape=[480,640,3],source_rgb8_sha256="b"*64)
        self.assertTrue(module.source_join(1675,new,old)["same_canonical_input"])
        for key,value in (("id",4795),("raw_sha256","c"*64),("native_shape",[640,480,3]),("source_rgb8_sha256","c"*64)):
            with self.assertRaises(ValueError):module.source_join(1675,new,old|{key:value})
        with self.assertRaises(ValueError):module.case({"cases":[old|{"outcome":"completed"}]*2},1675)

    def test_fresh_failed_analysis_receipt_retains_both_endpoints(self):
        with tempfile.TemporaryDirectory(prefix="m1-comparison-fixture-") as temporary:
            main=Path(temporary); output=main/".thesis-build/dev-runs/new"
            fake=types.SimpleNamespace(require_committed=lambda paths:{})
            with patch.object(module,"MAIN",main),patch.dict(sys.modules,{"m1_dual_latent":fake}),patch.object(module.subprocess,"check_output",return_value="0"*40),patch.object(module,"compare",side_effect=ValueError("synthetic failure")):
                status=module.main(["--source-id","1675","--new-bridge","unused-fixture","--legacy-dir","unused-fixture","--output-dir",str(output)])
            self.assertEqual(status,1)
            record=json.loads((output/"run.json").read_text())
            self.assertEqual(record["outcome"],"incomplete")
            self.assertEqual([r["step"] for r in record["comparisons"]],[0,200])
            self.assertTrue(all(r["outcome"]=="incomplete" for r in record["comparisons"]))
            self.assertIsNone(record["gate"])
            with patch.object(module,"MAIN",main):
                with self.assertRaises(FileExistsError):module.main(["--source-id","1675","--new-bridge","unused","--legacy-dir","unused","--output-dir",str(output)])

    def test_completed_first_endpoint_survives_second_failure(self):
        def partial(source_id,new,legacy,on_row):
            on_row(dict(step=0,outcome="completed",fixture=True))
            raise ValueError("synthetic second-endpoint failure")
        with tempfile.TemporaryDirectory(prefix="m1-comparison-fixture-") as temporary:
            main=Path(temporary); output=main/".thesis-build/dev-runs/partial"
            fake=types.SimpleNamespace(require_committed=lambda paths:{})
            with patch.object(module,"MAIN",main),patch.dict(sys.modules,{"m1_dual_latent":fake}),patch.object(module.subprocess,"check_output",return_value="0"*40),patch.object(module,"compare",side_effect=partial):
                self.assertEqual(module.main(["--source-id","1675","--new-bridge","unused","--legacy-dir","unused","--output-dir",str(output)]),1)
            record=json.loads((output/"run.json").read_text())
            self.assertEqual([r["outcome"] for r in record["comparisons"]],["completed","incomplete"])

if __name__=="__main__":unittest.main()
