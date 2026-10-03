"""CPU bridge/integrity tests; no photographs, weights, CUDA or scientific run."""
import copy
import json
from pathlib import Path
import types
import unittest
from unittest.mock import patch

import numpy as np
import torch

from scripts import m1_dual_latent as method


class DualLatentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        torch.set_num_threads(2)
        y, x = np.indices((512, 512))
        cls.source = np.stack([(3*x+7*y) % 256, (11*x+y) % 256, (x+13*y) % 256], axis=-1).astype(np.uint8)
        cls.features = np.random.default_rng(193).normal(size=512).tolist()
        cls.profile = method.codec.load_profile(method.ROOT / "configs/revised-watermark-v5.example.json")
        cls.profile["semantic_source"] = method.CLIP_SOURCE
        cls.objective = method.FixedPatternObjective(cls.source, cls.features, "dev-owner-0001", cls.profile,
                                                     device="cpu", dtype=torch.float64)
        cls.tensor = torch.from_numpy(cls.source).permute(2, 0, 1)[None].double() / 255

    def test_exact_source_projection_parity(self):
        semantic, instance = self.objective.projections(self.tensor)
        np.testing.assert_allclose(semantic.detach().numpy(), self.objective.reference_projections["semantic"], atol=1e-10, rtol=1e-10)
        np.testing.assert_allclose(instance.detach().numpy(), self.objective.reference_projections["instance"], atol=1e-10, rtol=1e-10)

    def test_score_directional_derivative(self):
        value = self.tensor.detach().clone().requires_grad_(True)
        s, i = self.objective.scores(value)
        score = s + .37 * i
        gradient, = torch.autograd.grad(score, value)
        self.assertTrue(bool(torch.isfinite(gradient).all()))
        direction = gradient / torch.linalg.vector_norm(gradient)
        epsilon = 1e-5
        def objective(v):
            a, b = self.objective.scores(v)
            return a + .37 * b
        finite_difference = (objective(value.detach()+epsilon*direction)-objective(value.detach()-epsilon*direction))/(2*epsilon)
        analytic = (gradient*direction).sum()
        self.assertGreater(float(analytic), 0)
        self.assertAlmostEqual(float(finite_difference), float(analytic), delta=1e-5*float(analytic))

    def test_frozen_margins_allow_code_reading(self):
        threshold = method.codec._threshold(self.profile["decision"]["false_positive_target"], 2**32)
        self.assertGreater(method.DEFAULT_CONFIG["semantic_margin"], threshold)
        self.assertGreater(method.DEFAULT_CONFIG["instance_margin"], threshold)
        self.assertGreater(method.DEFAULT_CONFIG["cycle_margin"], threshold)

    def test_output_routes_are_distinct(self):
        class FakeVAE(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.weight = torch.nn.Parameter(torch.tensor(1.0))
            def decode(self, z, return_dict=False):
                return (z * self.weight,)
        embedder = method.DualLatentEmbedder(FakeVAE(), method.DEFAULT_CONFIG)
        z = torch.zeros(1, 3, 4, 4)
        source = torch.full_like(z, .2)
        reference = embedder.decode(z)
        self.assertTrue(torch.equal(embedder.image(z, source, reference, "pure-decoder"), reference))
        torch.testing.assert_close(embedder.image(z, source, reference, "hybrid-source-bypass"), source, atol=1e-7, rtol=0)
        # Primary output has no source dependency; a changed source cannot change it.
        self.assertTrue(torch.equal(embedder.image(z, source+.3, reference, "pure-decoder"), reference))
        self.assertFalse(embedder.vae.weight.requires_grad)

    def test_blind_boundary_recomputes_suspect_features(self):
        calls = []
        def feature(rgb):
            calls.append(int(rgb[0, 0, 0]))
            return [float(rgb[0, 0, 0])]
        def detector(rgb, owner, profile, semantic_features):
            self.assertEqual(semantic_features, [float(rgb[0][0][0])])
            return {"proposal_state": "regenerated", "outcome": "semantic_only"}
        with patch.object(method.codec, "detect_rgb", side_effect=detector):
            for value in (3, 9):
                result = method.blind_detect(np.full((512, 512, 3), value, dtype=np.uint8), "o", self.profile, feature)
                self.assertEqual(result["qualified_state"], "regeneration-consistent")
        self.assertEqual(calls, [3, 9])

    def test_manifest_boundary_and_fixed_pilot(self):
        path = method.ROOT / "research/m1-dual-latent-dev.json"
        manifest = json.loads(path.read_text())
        cfg, cases, profile, *_ = method.validate_manifest(manifest)
        self.assertEqual([x["id"] for x in cases], [1675, 4795])
        self.assertEqual(cfg["routes"], ["pure-decoder"])
        self.assertEqual(profile["semantic_source"], method.CLIP_SOURCE)
        for key, value in (("data_split", "heldout"), ("case_ids", [999999]), ("case_ids", [1675, 1675])):
            wrong = copy.deepcopy(manifest)
            wrong[key] = value
            with self.assertRaises(ValueError):
                method.validate_manifest(wrong)


if __name__ == "__main__":
    unittest.main()
