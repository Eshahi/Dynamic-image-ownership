"""Model-free adapter contract tests, with no Torch or study image imports."""
from types import SimpleNamespace
import unittest
from three_threat_models import DDIM_CONFIG, regeneration_kwargs, validate_generated


class FakeGenerator:
    def __init__(self, device):
        self.device = device
    def manual_seed(self, seed):
        self.seed = seed
        return self


class ModelContractTests(unittest.TestCase):
    def test_paired_seed_is_fresh_not_reused_stream(self):
        first = regeneration_kwargs(0.2, 1, "c0", FakeGenerator)
        second = regeneration_kwargs(0.2, 1, "c1", FakeGenerator)
        self.assertIsNot(first["generator"], second["generator"])
        self.assertEqual(first["generator"].seed, second["generator"].seed)
        self.assertEqual(first["image"], "c0")
        self.assertEqual(second["image"], "c1")
        self.assertEqual(first["eta"], 0)
        self.assertEqual(first["guidance_scale"], 1)
        self.assertEqual(first["num_inference_steps"], 20)

    def test_reject_unplanned_seeds_strengths(self):
        for strength, seed in ((0.3, 0), (0.2, 7), (0.2, True), (True, 1)):
            with self.assertRaises(ValueError):
                regeneration_kwargs(strength, seed, "input", FakeGenerator)

    def test_safety_failures_not_valid_outputs(self):
        image = SimpleNamespace(mode="RGB", size=(512, 512))
        self.assertIs(validate_generated(SimpleNamespace(images=[image], nsfw_content_detected=[False])), image)
        for images, flags in (([image], None), ([image], [True]), ([], [False]), ([image], []),
                              ([image], [None]), ([image], [0]), ([image], [""])):
            with self.assertRaises(RuntimeError):
                validate_generated(SimpleNamespace(images=images, nsfw_content_detected=flags))
        with self.assertRaises(RuntimeError):
            validate_generated(SimpleNamespace(images=[SimpleNamespace(mode="RGB", size=(256, 512))], nsfw_content_detected=[False]))

    def test_scheduler_is_explicit_adaptation(self):
        self.assertEqual(DDIM_CONFIG["timestep_spacing"], "leading")
        self.assertEqual(DDIM_CONFIG["steps_offset"], 1)
        self.assertFalse(DDIM_CONFIG["set_alpha_to_one"])
        self.assertFalse(DDIM_CONFIG["clip_sample"])


if __name__ == "__main__":
    unittest.main()
