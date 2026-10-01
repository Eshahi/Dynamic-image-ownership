"""Ordinary fault-injection tests: fake adapter, no images/models/approval."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
import os
import subprocess
import sys
from v4_evaluation_journal import Journal,evaluate_units,atomic_json,summarize_journal


class Fake:
    def __init__(self):
        self.calls = []
        self.features = []
    def image(self,row): return {"sha256":"a"*64,"pixel_sha256":"b"*64}
    def feature(self,row,image):
        self.features.append(row["id"])
        return {"values":[1.0],"pixel_sha256":image["pixel_sha256"]}
    def verify_feature(self,row,image,feature):
        if feature["pixel_sha256"] != image["pixel_sha256"]: raise ValueError("feature pixel mismatch")
    def claims(self,row): return ["owner-"+str(i) for i in range(4)]
    def detect(self,row,image,feature,claim,slot):
        self.calls.append((row["id"],slot))
        return {"id":row["id"],"slot":slot,"owner":claim}
    def verify_call(self,row,image,claim,result,slot):
        if result != {"id":row["id"],"slot":slot,"owner":claim}: raise ValueError("call mismatch")
    def quality(self,row,image):
        score={"psnr":40.0,"ssim":.95,"lpips":.02}
        return {"quality_source":score,"quality_immediate":score}
    def components(self,row): return {"diagnostic":True}


def fixture():
    rows = {"t3-first":{"id":"t3-first"},"t3-second":{"id":"t3-second"}}
    units = [{"unit_id":"unit-"+str(i),"row_ids":[identity],"actions":{identity:"evaluate_saved"}}
             for i,identity in enumerate(rows)]
    return rows,units


class Tests(unittest.TestCase):
    def test_adapter_exceptions_keep_active_step_and_partial_call_accounting(self):
        for step,expected_calls in (("feature",0),("call-2",2),("quality",4)):
            with self.subTest(step=step),tempfile.TemporaryDirectory() as root:
                rows,units=fixture()
                active=[]
                adapter=Fake()
                if step=="feature":
                    def failed(*args): raise RuntimeError("feature backend failure")
                    adapter.feature=failed
                elif step=="quality":
                    def failed(*args): raise RuntimeError("metric backend failure")
                    adapter.quality=failed
                else:
                    original=adapter.detect
                    def failed(row,image,feature,claim,slot):
                        if slot==2: raise RuntimeError("detector backend failure")
                        result=original(row,image,feature,claim,slot)
                        result["inherited"]=True
                        return result
                    adapter.detect=failed
                    adapter.verify_call=lambda *args:None
                journal=Journal(root,"c"*64)
                with self.assertRaises(RuntimeError):
                    evaluate_units(units,rows,journal,adapter,progress=lambda *args:active.append(args))
                self.assertEqual(active[-1],("t3-first",step+"-start"))
                summary=summarize_journal(units,journal)
                self.assertEqual(summary["completed_detector_calls"],expected_calls)
                self.assertEqual(summary["inherited_detector_calls"],2 if step=="call-2" else 0)
                self.assertEqual(summary["rows"],[])
                self.assertEqual(summary["sealed_units"],[])
                self.assertIsNone(journal.get("t3-second","image"))

    def test_corrupt_receipt_final_summary_preserves_verified_prefix(self):
        rows,units=fixture()
        with tempfile.TemporaryDirectory() as root:
            journal=Journal(root,"c"*64)
            evaluate_units(units,rows,journal,Fake())
            path=journal.path("t3-second","complete")
            path.write_bytes(b"{broken-json")
            with self.assertRaises(ValueError): summarize_journal(units,journal)
            summary=summarize_journal(units,journal,tolerate_corruption=True)
            self.assertEqual(summary["sealed_units"],["unit-0"])
            self.assertTrue(summary["integrity_errors"])
            atomic_json(Path(root)/"terminal-diagnostics.json",summary)
            self.assertTrue((Path(root)/"terminal-diagnostics.json").is_file())

    def test_valid_json_wrong_envelope_and_payload_shapes_remain_reportable(self):
        for malformed in ([],None,3,"wrong",{}, {"value":[]}):
            with self.subTest(shape=malformed),tempfile.TemporaryDirectory() as root:
                rows,units=fixture()
                journal=Journal(root,"c"*64)
                evaluate_units(units,rows,journal,Fake())
                atomic_json(journal.path("t3-second","complete"),malformed)
                summary=summarize_journal(units,journal,tolerate_corruption=True)
                self.assertEqual(summary["sealed_units"],["unit-0"])
                self.assertTrue(summary["integrity_errors"])
                atomic_json(Path(root)/"terminal.json",summary)

    def test_malformed_terminal_detections_do_not_abort_diagnostics(self):
        rows,units=fixture()
        with tempfile.TemporaryDirectory() as root:
            journal=Journal(root,"c"*64)
            evaluate_units(units,rows,journal,Fake())
            value=journal.get("t3-second","complete")
            value["detections"]=None
            from v4_evaluation_journal import object_sha
            atomic_json(journal.path("t3-second","complete"),{"row_id":"t3-second","step":"complete",
                "manifest_sha256":"c"*64,"value":value,"value_sha256":object_sha(value)})
            summary=summarize_journal(units,journal,tolerate_corruption=True)
            self.assertEqual(summary["sealed_units"],["unit-0"])
            self.assertTrue(summary["integrity_errors"])

    def test_malformed_nested_metrics_do_not_abort_diagnostics(self):
        for malformed in (None,[],"wrong",3):
            with self.subTest(shape=malformed),tempfile.TemporaryDirectory() as root:
                rows,units=fixture()
                journal=Journal(root,"c"*64)
                evaluate_units(units,rows,journal,Fake())
                value=journal.get("t3-second","complete")
                value["quality_source"]=malformed
                from v4_evaluation_journal import object_sha
                atomic_json(journal.path("t3-second","complete"),{"row_id":"t3-second","step":"complete",
                    "manifest_sha256":"c"*64,"value":value,"value_sha256":object_sha(value)})
                summary=summarize_journal(units,journal,tolerate_corruption=True)
                self.assertEqual(summary["sealed_units"],["unit-0"])
                self.assertTrue(summary["integrity_errors"])
    def test_actual_child_process_loss_and_verified_resume(self):
        for boundary in ("image","feature","call-0","call-1","call-2","call-3","quality","complete","seal"):
            with self.subTest(boundary=boundary),tempfile.TemporaryDirectory() as root:
                child=subprocess.run([sys.executable,"-B",__file__,"--fault-child",root,boundary],timeout=15)
                self.assertEqual(child.returncode,91)
                rows,units=fixture()
                journal=Journal(Path(root)/"journal","c"*64)
                self.assertTrue(journal.verified_seal(units[0]))
                child=subprocess.run([sys.executable,"-B",__file__,"--fault-child",root,"none"],timeout=15)
                self.assertEqual(child.returncode,0)
                self.assertTrue(all(journal.verified_seal(u) for u in units))
                calls=json.loads((Path(root)/"calls.json").read_text())
                self.assertEqual(len(calls),8)
                self.assertEqual(len({tuple(c) for c in calls}),8)
    def test_each_fault_boundary_preserves_prefix_without_duplicate_work(self):
        for boundary in ("image","feature","call-0","call-1","call-2","call-3","quality","complete","seal"):
            with self.subTest(boundary=boundary),tempfile.TemporaryDirectory() as root:
                rows,units=fixture()
                adapter=Fake()
                journal=Journal(root,"c"*64)
                def fail(identity,step):
                    if step == boundary and identity in ("t3-second","unit-1"):
                        raise RuntimeError("injected process loss")
                with self.assertRaises(RuntimeError): evaluate_units(units,rows,journal,adapter,hook=fail)
                self.assertTrue(journal.verified_seal(units[0]))
                reopened=Journal(root,"c"*64)
                evaluate_units(units,rows,reopened,adapter)
                self.assertTrue(all(reopened.verified_seal(u) for u in units))
                self.assertEqual(len(adapter.calls),8)
                self.assertEqual(len(set(adapter.calls)),8)
                self.assertEqual(adapter.features,["t3-first","t3-second"])

    def test_next_unit_never_starts_after_infrastructure_failure(self):
        rows,units=fixture()
        with tempfile.TemporaryDirectory() as root:
            adapter=Fake()
            def fail(*_): raise OSError("disk full")
            with self.assertRaises(OSError): evaluate_units(units,rows,Journal(root,"c"*64),adapter,hook=fail)
            self.assertEqual(adapter.calls,[])
            self.assertEqual(adapter.features,[])

    def test_sealed_corruption_blocks_recovery(self):
        rows,units=fixture()
        with tempfile.TemporaryDirectory() as root:
            journal=Journal(root,"c"*64)
            evaluate_units(units,rows,journal,Fake())
            path=journal.path("t3-first","call-0")
            item=json.loads(path.read_text())
            item["value"]["slot"]=99
            atomic_json(path,item)
            with self.assertRaises(ValueError): evaluate_units(units,rows,journal,Fake())

    def test_duplicate_receipt_and_manifest_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            journal=Journal(root,"c"*64)
            journal.put("x","image",{"a":1})
            with self.assertRaises(ValueError): journal.put("x","image",{"a":2})
            with self.assertRaises(ValueError): Journal(root,"d"*64).get("x","image")
            with self.assertRaises(ValueError): journal.path("../outside","image")

    def test_nonfinite_quality_and_partial_unit_not_sealed(self):
        rows,units=fixture()
        with tempfile.TemporaryDirectory() as root:
            journal=Journal(root,"c"*64)
            adapter=Fake()
            adapter.quality=lambda *args:{"quality_source":{"psnr":float("nan")}}
            with self.assertRaises(ValueError): evaluate_units(units,rows,journal,adapter)
            self.assertFalse(journal.verified_seal(units[0]))
            self.assertIsNone(journal.get("t3-second","image"))

    def test_generation_and_ambiguous_actions_refused(self):
        for action in ("generate_then_evaluate","pending_attempt_disposition"):
            with self.subTest(action=action),tempfile.TemporaryDirectory() as root:
                unit={"unit_id":"x","row_ids":["t3-first"],"actions":{"t3-first":action}}
                with self.assertRaises(ValueError): evaluate_units([unit],{"t3-first":{"id":"t3-first"}},Journal(root,"c"*64),Fake())


if __name__ == "__main__":
    if len(sys.argv)>1 and sys.argv[1]=="--fault-child":
        root=Path(sys.argv[2])
        boundary=sys.argv[3]
        class DurableFake(Fake):
            def detect(self,row,image,feature,claim,slot):
                path=root/"calls.json"
                ledger=json.loads(path.read_text()) if path.exists() else []
                ledger.append([row["id"],slot])
                atomic_json(path,ledger)
                return super().detect(row,image,feature,claim,slot)
        def abrupt(identity,step):
            if step==boundary and identity in ("t3-second","unit-1"): os._exit(91)
        rows,units=fixture()
        evaluate_units(units,rows,Journal(root/"journal","c"*64),DurableFake(),hook=abrupt)
    else:
        unittest.main()
