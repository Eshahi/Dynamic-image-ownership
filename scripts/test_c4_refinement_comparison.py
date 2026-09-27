"""Owned CPU fixtures only: no study pixels, learned weights, GPU or runner."""
from dataclasses import replace
from types import SimpleNamespace, MethodType
import unittest
from unittest.mock import patch
try:
    import torch
    import diffusers
except ImportError:
    torch = diffusers = None
from src.embedding.proposed import DiffusersComponents, EmbeddingError
from src.embedding.checkpointing import CheckpointedComponents
from src.embedding.inversion import InversionPolicy
from src.embedding.inversion_path import invert_roundtrip
from src.embedding.refinement_comparison import ARMS, RefinementComparisonPolicy, comparison
from scripts import test_c4_latent_refinement as fixture


@unittest.skipIf(torch is None or diffusers is None, "existing pinned software absent; do not install")
class RefinementComparisonTests(unittest.TestCase):
    def setUp(self):
        original = fixture.RefinementTests(); original.setUp()
        self.backend = original.backend
        self.backend.vae.encodes = 0
        def encode(vae, image):
            vae.encodes += 1
            value = torch.full((1, 4, image.shape[-2]//8, image.shape[-1]//8), .25)
            return SimpleNamespace(latent_dist=SimpleNamespace(mode=lambda: value))
        self.backend.vae.encode = MethodType(encode, self.backend.vae)
        self.source = original.source
        self.noise = torch.full((1, 4, 8, 8), .1)
        self.policy = RefinementComparisonPolicy(original.policy, InversionPolicy(), 64, 10., 1e-5)
        self.events = []; self.images = {}; self.states = []

    def run_comparison(self, **kwargs):
        args = dict(progress=self.events.append,
            save_arm=lambda arm, image, metadata: self.images.update({arm: (image, metadata)}),
            save_state=lambda arm, row, state: self.states.append((arm, row, state)))
        args.update(kwargs)
        return comparison(self.backend, self.source, self.noise, self.policy, **args)

    def test_six_arms_one_encode_and_native_output_no_quality_claim(self):
        result = self.run_comparison()
        self.assertEqual(tuple(result["arms"]), ARMS)
        self.assertEqual(tuple(self.images), ARMS)
        self.assertEqual(self.backend.vae.encodes, 1)
        self.assertEqual(result["status"], "completed_requires_png_safety_quality")
        self.assertFalse(result["scientific_acceptance"])
        self.assertEqual(result["blind_detection"], "NOT_RUN")
        self.assertEqual(self.states[0][0], "shared_encoded")
        self.assertTrue(torch.all(self.source == .65)); self.assertTrue(torch.all(self.noise == .1))
        for image, row in self.images.values():
            self.assertEqual(tuple(image.shape), (1, 3, 33, 35))
            self.assertFalse(image.requires_grad)
            self.assertEqual(row["image_quality"], "NOT_RUN")
            self.assertEqual(row["safety"], "NOT_RUN")
        self.assertIsNone(self.backend.vae.decoder.scale.grad)
        self.assertIsNone(self.backend.unet.slope.grad)
        self.assertEqual(len(self.backend.unet._forward_pre_hooks), 0)
        self.assertEqual(len(self.backend.vae.decoder._forward_pre_hooks), 0)

    def test_refined_inverse_targets_refined_latent_not_original_encoded(self):
        targets = []
        def capture(path, terminal, policy, **kwargs):
            targets.append(terminal.detach().clone())
            return invert_roundtrip(path, terminal, policy, **kwargs)
        with patch("src.embedding.refinement_comparison.invert_roundtrip", side_effect=capture):
            result = self.run_comparison()
        encoded = self.states[0][2]
        refined = next(state for arm, row, state in self.states if row["phase"] == "refined_terminal_target")
        torch.testing.assert_close(targets[0], encoded, atol=0, rtol=0)
        torch.testing.assert_close(targets[1], refined, atol=0, rtol=0)
        self.assertGreater(float((refined-encoded).abs().max()), 0)
        self.assertLess(float((self.images[ARMS[3]][0]-self.source).square().mean()),
                        float((self.images[ARMS[0]][0]-self.source).square().mean()))
        torch.testing.assert_close(self.images[ARMS[3]][0], self.images[ARMS[5]][0], atol=1e-5, rtol=0)
        self.assertEqual(result["arms"][ARMS[5]]["target_identity"], "refined_terminal")

    def test_historical_controls_match_direct_owned_backend(self):
        result = self.run_comparison()
        encoded = self.states[0][2]
        with torch.no_grad():
            expected = (self.backend.decode_encoded(encoded),
                self.backend.reconstruct(encoded, torch.zeros_like(self.noise)),
                self.backend.reconstruct(encoded, self.noise))
        for arm, image in zip(ARMS[:3], expected):
            torch.testing.assert_close(self.images[arm][0], image[:, :, :33, :35], atol=0, rtol=0)
        self.assertEqual(result["arms"][ARMS[1]]["scheduler_evaluations"], 2)

    def test_checkpoint_profile_preserves_synthetic_trajectory(self):
        base = self.run_comparison(); images = {arm: image.clone() for arm, (image, _) in self.images.items()}
        self.setUp(); b = self.backend
        self.backend = CheckpointedComponents(b.vae, b.unet, b.condition, b.settings)
        candidate = self.run_comparison()
        for arm in ARMS:
            torch.testing.assert_close(images[arm], self.images[arm][0], atol=0, rtol=0)
        self.assertEqual(base["arms"][ARMS[3]]["continuous_mse_rgb01"],
                         candidate["arms"][ARMS[3]]["continuous_mse_rgb01"])
        self.assertGreater(candidate["arms"][ARMS[3]]["checkpoint_recomputations"], 0)
        self.assertEqual(len(self.backend.unet._forward_pre_hooks), 0)
        self.assertEqual(len(self.backend.vae.decoder._forward_pre_hooks), 0)

    def test_both_nonconverged_inverse_arms_retained_without_decode_fallback(self):
        self.policy = replace(self.policy, inverse=InversionPolicy(max_evaluations=1))
        result = self.run_comparison()
        self.assertEqual(tuple(self.images), ARMS[:4])
        self.assertEqual(result["failed_arms"], ARMS[4:])
        self.assertEqual(result["status"], "completed_with_nonconverged_arms")
        # Three controls plus declared refinement evaluations; no inverse decoder.
        self.assertEqual(self.backend.vae.decoder.calls, 3+result["arms"][ARMS[3]]["decoder_evaluations"])
        for arm in ARMS[4:]:
            self.assertTrue(any(a == arm and r["phase"] == "inverse_returned_state" for a, r, _ in self.states))

    def test_budget_stopped_refinement_keeps_explicit_status_through_inverse(self):
        self.policy = replace(self.policy, refinement=replace(self.policy.refinement, maximum_evaluations=2))
        result = self.run_comparison()
        self.assertEqual(result["arms"][ARMS[3]]["refinement_status"], "evaluation_budget")
        self.assertEqual(result["arms"][ARMS[5]]["refinement_status"], "evaluation_budget")
        self.assertEqual(result["arms"][ARMS[3]]["decoder_evaluations"], 1)
        self.assertFalse(result["scientific_acceptance"])

    def test_roundtrip_failure_is_not_decoded_or_substituted(self):
        self.policy = replace(self.policy, inverse=InversionPolicy(residual_tolerance=1.), roundtrip_tolerance=0.)
        result = self.run_comparison()
        self.assertEqual(result["failed_arms"], ARMS[4:])
        self.assertTrue(all(result["arms"][arm]["path_status"] == "roundtrip_residual_failed" for arm in ARMS[4:]))
        self.assertEqual(tuple(self.images), ARMS[:4])

    def test_payload_mutation_cannot_modify_terminal_targets_or_outcomes(self):
        base = self.run_comparison()
        self.setUp()
        def save(arm, row, state):
            self.states.append((arm, dict(row), state.clone()))
            state.zero_(); row["phase"] = "invented"
        def journal(row):
            if "outcome" in row: row["outcome"]["status"] = "invented"
        result = self.run_comparison(save_state=save, progress=journal)
        self.assertEqual(result, base)
        self.assertGreater(float(next(s for _, r, s in self.states if r["phase"] == "refined_terminal_target").abs().max()), 0)

    def test_save_failure_leaves_prior_controls_and_no_terminal(self):
        def save(arm, image, row):
            if arm == ARMS[3]: raise OSError("owned PNG persistence failure")
            self.images[arm] = (image, row)
        with self.assertRaisesRegex(OSError, "owned PNG"):
            self.run_comparison(save_arm=save)
        self.assertEqual(tuple(self.images), ARMS[:3])
        self.assertFalse(any(r["phase"] == "refinement_comparison_terminated" for r in self.events))
        self.assertEqual(len(self.backend.vae.decoder._forward_pre_hooks), 0)

    def test_state_failure_before_control_keeps_no_image(self):
        def fail(*args): raise OSError("owned latent persistence failure")
        with self.assertRaisesRegex(OSError, "owned latent"):
            self.run_comparison(save_state=fail)
        self.assertEqual(self.backend.vae.encodes, 1)
        self.assertEqual(self.backend.vae.decoder.calls, 0)
        self.assertEqual(self.images, {})

    def test_rounded_projection_refusal_preserves_controls_without_inverse_or_terminal(self):
        self.policy = replace(self.policy, refinement=replace(self.policy.refinement,
                              learning_rate=1., maximum_displacement_l2=1e-4))
        with self.assertRaisesRegex(EmbeddingError, "rounded refinement projection"):
            self.run_comparison()
        self.assertEqual(tuple(self.images), ARMS[:3])
        self.assertEqual(self.states[-1][1]["phase"], "refinement_projection_refused")
        self.assertFalse(any(arm in ARMS[4:] for arm, _, _ in self.states))
        self.assertFalse(any(r["phase"] == "refinement_comparison_terminated" for r in self.events))

    def test_cross_owner_methods_refused_before_encode(self):
        for name in ("encode", "reconstruct", "decode_encoded", "_decode"):
            self.setUp(); other = RefinementComparisonTests(); other.setUp()
            setattr(self.backend, name, getattr(other.backend, name))
            with self.subTest(name=name), self.assertRaisesRegex(EmbeddingError, "exact owner"):
                self.run_comparison()
            self.assertEqual(self.backend.vae.encodes, 0)

    def test_post_save_method_mutation_is_refused_before_later_arm(self):
        other = RefinementComparisonTests(); other.setUp()
        def save(arm, image, row):
            self.images[arm] = (image, row)
            self.backend.decode_encoded = other.backend.decode_encoded
        with self.assertRaisesRegex(EmbeddingError, "owner/function drift"):
            self.run_comparison(save_arm=save)
        self.assertEqual(tuple(self.images), (ARMS[0],))
        self.assertFalse(any(r["phase"] == "refinement_comparison_arm_saved" for r in self.events))

    def test_post_save_vae_mutation_is_refused(self):
        def save(arm, image, row): self.backend.vae.decoder.scale.add_(.1)
        with self.assertRaisesRegex(EmbeddingError, "VAE identity/profile"):
            self.run_comparison(save_arm=save)
        self.assertFalse(any(r["phase"] == "refinement_comparison_arm_saved" for r in self.events))

    def test_slow_last_save_retains_partial_without_terminal(self):
        clock = [0.]
        def save(arm, image, row):
            self.images[arm] = (image, row)
            if arm == ARMS[-1]: clock[0] = 11.
        with patch("src.embedding.refinement_comparison.time.monotonic", side_effect=lambda: clock[0]):
            with self.assertRaisesRegex(EmbeddingError, "cooperative time"):
                self.run_comparison(save_arm=save)
        self.assertEqual(tuple(self.images), ARMS)
        self.assertFalse(any(r["phase"] == "refinement_comparison_terminated" for r in self.events))
        self.assertEqual(len(self.backend.unet._forward_pre_hooks), 0)

    def test_journal_failure_before_encoding(self):
        def fail(row): raise OSError("owned journal failure")
        with self.assertRaises(OSError): self.run_comparison(progress=fail)
        self.assertEqual(self.backend.vae.encodes, 0)

    def test_malformed_policy_noise_and_callbacks_refused_before_encode(self):
        with self.assertRaises(EmbeddingError):
            replace(self.policy, inverse=InversionPolicy(method="guided_coordinate"))
        with self.assertRaises(EmbeddingError): replace(self.policy, maximum_seconds=True)
        self.policy = replace(self.policy, maximum_evaluations_per_inverse_arm=2)
        with self.assertRaisesRegex(EmbeddingError, "replay reservation"): self.run_comparison()
        self.policy = replace(self.policy, maximum_evaluations_per_inverse_arm=64)
        with self.assertRaisesRegex(EmbeddingError, "persistence callbacks"):
            self.run_comparison(save_state=None)
        self.noise = self.noise.double()
        with self.assertRaises(EmbeddingError): self.run_comparison()
        self.assertEqual(self.backend.vae.encodes, 0)


if __name__ == "__main__": unittest.main()
