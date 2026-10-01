import sys
import ast
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock
sys.path.insert(0,str(Path(__file__).resolve().parent))
from v4_study_boundary import prepare_marked
from v4_study_protocol import claims


class Tests(unittest.TestCase):
    def test_failed_diagnostic_kept_saved_reopened_and_reencoded(self):
        source=object()
        source_features=[1.,0.]
        returned=object()
        reopened=object()
        suspect_features=[0.,1.]
        events=[]
        def embed(pixels,**kw):
            events.append("embed")
            self.assertIs(pixels,source)
            self.assertEqual(kw,{"semantic_features":source_features,"strict":False})
            return returned,{"verified":False}
        def record(report,seconds):
            events.append("record")
            self.assertFalse(report["verified"])
            self.assertGreaterEqual(seconds,0)
        def save(pixels):
            events.append("save")
            self.assertIs(pixels,returned)
        def read():
            events.append("read")
            return reopened
        def feature(pixels):
            events.append("feature")
            self.assertIs(pixels,reopened)
            return suspect_features
        pixels,vector=prepare_marked(source,source_features,embed,save,read,feature,record)
        self.assertIs(pixels,reopened)
        self.assertIs(vector,suspect_features)
        self.assertEqual(events,["embed","record","save","read","feature"])

    def test_exception_never_fabricates_pixels_or_verdict(self):
        embed=Mock(side_effect=ValueError("host failure"))
        save,read,feature,record=Mock(),Mock(),Mock(),Mock()
        with self.assertRaises(ValueError):
            prepare_marked([],[],embed,save,read,feature,record)
        for fn in (save,read,feature,record):
            fn.assert_not_called()

    def test_four_owner_claims_use_roster_correction(self):
        for axis in ("clean","T3"):
            calls=claims({"axis":axis})
            self.assertEqual(len(calls),4)
            self.assertTrue(all(mode=="combined" and roster==4 for _,mode,roster in calls))

    def test_actual_checkpoint_writer_rejects_nonfinite_without_replacing_checkpoint(self):
        # Extract the exact stdlib writer, avoiding unrelated scientific imports.
        source=Path(__file__).with_name("qim_rgb_pilot.py")
        module=ast.parse(source.read_text(encoding="utf-8"))
        function=next(node for node in module.body if isinstance(node,ast.FunctionDef) and node.name=="write_json")
        namespace={"Path":Path,"json":json,"os":os}
        exec(compile(ast.Module(body=[function],type_ignores=[]),str(source),"exec"),namespace)
        with tempfile.TemporaryDirectory(prefix="v4-checkpoint-test-") as directory:
            target=Path(directory)/"results.json"
            namespace["write_json"](target,{"score":1.0,"failure":None})
            original=target.read_bytes()
            for value in (float("nan"),float("inf"),float("-inf")):
                with self.subTest(value=value),self.assertRaises(ValueError):
                    namespace["write_json"](target,{"score":value})
                self.assertEqual(target.read_bytes(),original)
            self.assertEqual(json.loads(original),{"score":1.0,"failure":None})


if __name__=="__main__":
    unittest.main()
