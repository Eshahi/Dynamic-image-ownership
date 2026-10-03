"""CPU-only mathematical and manifest boundaries; no models or images loaded."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

import m1_progressive_latent as candidate


class ManifestBoundary(unittest.TestCase):
    def setUp(self):
        self.manifest=json.loads((candidate.ROOT/"research/m1-progressive-synthetic.json").read_text())

    def test_exact_gs_prompts_and_seeds(self):
        cases=candidate.validate(self.manifest)
        reference=json.loads((candidate.ROOT/"research/m1-gs-synthetic.json").read_text())
        self.assertEqual([(x["seed"],x["prompt"]) for x in cases],
                         [(x["seed"],x["prompt"]) for x in reference["cases"]])

    def test_reject_heldout_threshold_change_and_prompt_change(self):
        for change in ("split","threshold","prompt","seed"):
            modified=copy.deepcopy(self.manifest)
            if change=="split": modified["data_split"]="heldout"
            elif change=="threshold": modified["config"]["threshold"]=.5
            elif change=="prompt": modified["cases"][0]["prompt"]="new prompt"
            else: modified["cases"][0]["seed"]=999
            with self.subTest(change=change),self.assertRaises(ValueError):
                candidate.validate(modified)

    def test_reject_missing_duplicate_and_unsafe_resume_paths(self):
        modified=copy.deepcopy(self.manifest)
        modified["cases"].append(modified["cases"][0])
        with self.assertRaises(ValueError): candidate.validate(modified)
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            (root/"example.png").write_bytes(b"retained-placeholder")
            self.assertEqual(candidate.artifact_path(root,"example.png"),root/"example.png")
            for path in ("../example.png","missing.png",str(root/"example.png"),"example.txt"):
                with self.subTest(path=path),self.assertRaises(ValueError):
                    candidate.artifact_path(root,path)

    def test_wrong_payloads_fixed_before_scores(self):
        payloads=candidate.wrong_payloads()
        self.assertEqual(len(payloads),64)
        self.assertEqual(payloads,candidate.wrong_payloads())
        self.assertNotIn(candidate.CONFIG["payload"],payloads)
        result=candidate.wrong_payload_scores([int(x) for x in candidate.CONFIG["payload"]])
        self.assertEqual(result["false_findings"],sum(x>=.875 for x in result["bit_accuracies"]))
        self.assertEqual(result["denominator"],64)

    def test_resume_retains_failure_marks_interruption_and_rejects_missing_complete(self):
        with tempfile.TemporaryDirectory() as directory:
            identity={"commit":"fixed"}
            record={**identity,"rows":[{"id":"failed","outcome":"failed","error":"OOM"},
                                        {"id":"interrupted","outcome":"started"}]}
            resumed=candidate.prepare_resume(record,identity,Path(directory))
            self.assertEqual(resumed["rows"][0]["error"],"OOM")
            self.assertEqual(resumed["rows"][1]["outcome"],"interrupted")
            with self.assertRaises(ValueError):
                candidate.prepare_resume(record,{"commit":"changed"},Path(directory))
            record["rows"].append({"id":"incomplete","control":"C1","outcome":"completed","conditions":{},"artifacts":[]})
            with self.assertRaises(ValueError):
                candidate.prepare_resume(record,identity,Path(directory))


class DCTMathematics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import torch
        except ImportError:
            raise unittest.SkipTest("Torch absent; run mathematical tests with pinned science Python")
        cls.torch=torch
        cls.basis=candidate.dct_matrix(64)

    def test_orthonormal_energy_and_inverse(self):
        torch=self.torch
        x=torch.arange(4096,dtype=torch.float32).reshape(64,64)/4096
        transformed=candidate.dct2(x,self.basis)
        self.assertTrue(torch.allclose(self.basis@self.basis.T,torch.eye(64),atol=1e-5))
        self.assertTrue(torch.allclose(candidate.idct2(transformed,self.basis),x,atol=4e-5))
        self.assertAlmostEqual(float(x.square().sum()),float(transformed.square().sum()),places=2)

    def test_analytic_gradient_and_descent(self):
        torch=self.torch
        torch.manual_seed(1701)
        x=torch.randn(64,64).requires_grad_(True)
        target,mask=candidate.target_and_mask(.3,self.basis)
        loss=(mask*(candidate.dct2(x,self.basis)-target).square()).sum()/mask.sum()
        loss.backward()
        grad=candidate.analytic_gradient(x.detach(),target,mask,self.basis)
        self.assertTrue(torch.allclose(x.grad,grad,atol=2e-7))
        after=(mask*(candidate.dct2(x.detach()-25*grad,self.basis)-target).square()).sum()/mask.sum()
        self.assertLess(float(after),float(loss.detach()))

    def test_payload_roundtrip_and_majority_tie_zero(self):
        torch=self.torch
        target,mask=candidate.target_and_mask(.3,self.basis)
        plane=candidate.idct2(target,self.basis)
        self.assertEqual(candidate.read_bits(plane,self.basis)["bit_accuracy"],1)
        locations=candidate.positions()
        for i,(u,v) in enumerate(locations[:8]): target[u,v]=.3 if i<4 else -.3
        report=candidate.read_bits(candidate.idct2(target,self.basis),self.basis)
        self.assertEqual(report["bits"][0],"0")
        self.assertEqual(int(mask.sum()),128)
        self.assertEqual(len(set(locations)),128)


if __name__=="__main__":
    unittest.main()
