"""Pure stdlib mocks only: never import tensor packages or load models."""
import math
from pathlib import Path
from types import SimpleNamespace
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tifs_denoiser as d


class Token:
    def __init__(self, *values):
        self.values, self.dtype, self.shape = values, "fp16", (1, 2, 1280)
    def to(self, *args, **kwargs):
        return self


class MockTorch:
    @staticmethod
    def cat(tokens, dim=0):
        assert dim == 0
        return Token(*(v for token in tokens for v in token.values))


class MockPipe:
    def __init__(self):
        self.unet = SimpleNamespace(config=SimpleNamespace(time_cond_proj_dim=None))
        self.text_encoder_2 = SimpleNamespace(config=SimpleNamespace(projection_dim=1280))
    def encode_prompt(self, **kwargs):
        self.kwargs = kwargs
        values = (Token("positive"), Token("negative"))
        return values + (Token("pooled"), Token("negative-pooled")) if "prompt_2" in kwargs else values
    def _get_add_time_ids(self, *args, **kwargs):
        self.time_args, self.time_kwargs = args, kwargs
        return Token("positive-time"), Token("negative-time")


class MockUNet:
    def __init__(self, train=False, requires_grad=False, broken=False):
        self.training, self.requires_grad, self.broken = train, requires_grad, broken
        self.blocks = [SimpleNamespace(gradient_checkpointing=False) for _ in range(3)]
    def modules(self):
        return [self, *self.blocks]
    def parameters(self):
        return [SimpleNamespace(requires_grad=self.requires_grad)]
    def enable_gradient_checkpointing(self):
        for block in self.blocks:
            block.gradient_checkpointing = True
        if self.broken:
            self.blocks[1].gradient_checkpointing = False
    def disable_gradient_checkpointing(self):
        for block in self.blocks:
            block.gradient_checkpointing = False


class DenoiserTests(unittest.TestCase):
    def test_exact_cfg_prediction_and_explicit_native_dtype(self):
        class Scalar:
            def __init__(self, value): self.value = value
            def to(self, dtype):
                self.requested_dtype = dtype
                return self
        class Prediction:
            def chunk(self, count):
                self_test.assertEqual(count, 2)
                return 2., 5.
        class UNet:
            dtype = "fp16"
            def __call__(self, latent, timestep, **kwargs):
                self_test.assertEqual(latent, "doubled-and-scaled")
                self_test.assertEqual(timestep, 51)
                self_test.assertEqual(kwargs["encoder_hidden_states"], "condition")
                self_test.assertIsNone(kwargs["timestep_cond"])
                return (Prediction(),)
        self_test, noisy = self, Scalar(4.)
        def cat(values, dim):
            self.assertEqual(values, [noisy, noisy])
            return "doubled"
        scheduler = SimpleNamespace(scale_model_input=lambda value, step: value + "-and-scaled")
        cond = dict(do_cfg=True, guidance_scale=7.5, encoder_hidden_states="condition", added_cond_kwargs=None)
        result = d.predict_epsilon(UNet(), scheduler, noisy, 51, cond, SimpleNamespace(cat=cat))
        self.assertEqual(result, 2. + 7.5*(5.-2.))
        self.assertEqual(noisy.requested_dtype, "fp16")

    def test_native_hook_cleanup_on_callback_failure_without_tensor_library(self):
        # Inject a stdlib stand-in: the real torch package is never imported.
        unet = SimpleNamespace(modules=lambda: [], forward=lambda: None)
        scheduler = SimpleNamespace(step=lambda: None)
        pipe = SimpleNamespace(unet=unet, scheduler=scheduler)
        original_forward, original_step = unet.forward, scheduler.step
        def failed_native():
            raise RuntimeError("native callback failed")
        with patch.dict(sys.modules, {"torch": SimpleNamespace()}):
            with self.assertRaisesRegex(RuntimeError, "native callback failed"):
                d.native_first_step_parity(pipe, "R1", {}, failed_native)
        self.assertIs(unet.forward, original_forward)
        self.assertIs(scheduler.step, original_step)

    def test_native_window_delegates_exact_native_steps_and_strength(self):
        scheduler = SimpleNamespace(config=SimpleNamespace(prediction_type="epsilon", clip_sample=False,
            thresholding=False), order=1, alphas_cumprod={1: .99, 51: .9, 101: .8, 151: .7})
        calls = []
        scheduler.set_timesteps = lambda n, device: calls.append((n, device))
        class Pipe:
            @staticmethod
            def get_timesteps(self, n, strength, device):
                self_test.assertIs(self.scheduler, scheduler)
                calls.append((n, strength, device))
                return ([51, 1], 2) if strength == .1 else ([151, 101, 51, 1], 4)
        self_test = self
        small = d.native_window(scheduler, Pipe, 20, .1)
        large = d.native_window(scheduler, Pipe, 20, .2)
        self.assertEqual([r["timestep"] for r in small], [51, 1])
        self.assertEqual([r["timestep"] for r in large], [151, 101, 51, 1])
        self.assertEqual(calls, [(20, "cpu"), (20, .1, "cpu"), (20, "cpu"), (20, .2, "cpu")])
        self.assertAlmostEqual(large[0]["a"]**2 + large[0]["b"]**2, 1)
        scheduler.config.prediction_type = "v_prediction"
        with self.assertRaises(ValueError):
            d.native_window(scheduler, Pipe, 20, .2)

    def test_window_sampling_is_deterministic_domain_separated_and_supported(self):
        window = [dict(timestep=t) for t in (151, 101, 51, 1)]
        draws = [d.sample_window(window, "source-1", "R1", .2, k, "optimization") for k in range(150)]
        self.assertEqual({v["timestep"] for v in draws}, {151, 101, 51, 1})
        self.assertEqual(draws[0], d.sample_window(window, "source-1", "R1", .2, 0, "optimization"))
        self.assertNotEqual(draws[0]["timestep_seed"], d.sample_window(window, "source-1", "R1", .2, 0, "diagnostic")["timestep_seed"])
        with self.assertRaises(ValueError):
            d.sample_window(window, "1", "K3", .2, 0, "optimization")
        with self.assertRaises(ValueError):
            d.sample_window([], "1", "R1", .2, 0, "optimization")

    def test_x0_formula_has_denoiser_dependence(self):
        alpha, clean, noise = .8, 2.5, -.7
        zt = math.sqrt(alpha)*clean + math.sqrt(1-alpha)*noise
        self.assertAlmostEqual(d.x0_from_epsilon(zt, noise, alpha), clean)
        self.assertNotEqual(d.x0_from_epsilon(zt, 0., alpha), clean)
        with self.assertRaises(ValueError):
            d.x0_from_epsilon(1., 1., 0.)

    def test_sd15_native_single_branch(self):
        pipe = MockPipe()
        cond = d.assemble_conditioning(pipe, "R0", dict(prompt="", guidance_scale=1.), MockTorch)
        self.assertFalse(cond["do_cfg"])
        self.assertEqual(cond["encoder_hidden_states"].values, ("positive",))
        self.assertIsNone(cond["added_cond_kwargs"])
        self.assertEqual(pipe.kwargs, dict(prompt="", device="cuda", num_images_per_prompt=1,
            do_classifier_free_guidance=False, negative_prompt="", clip_skip=None))

    def test_sdxl_native_added_conditioning_and_cfg_order(self):
        for guidance, expected in ((1., ("positive",)), (7.5, ("negative", "positive"))):
            pipe = MockPipe()
            cond = d.assemble_conditioning(pipe, "R1", dict(prompt="", guidance_scale=guidance), MockTorch)
            self.assertEqual(cond["encoder_hidden_states"].values, expected)
            self.assertEqual(pipe.kwargs["prompt_2"], "")
            self.assertIsNone(pipe.kwargs["negative_prompt_2"])
            self.assertEqual(pipe.time_args, ((1024,1024), (0,0), (1024,1024), 6., 2.5,
                                              (1024,1024), (0,0), (1024,1024)))
            self.assertEqual(pipe.time_kwargs, dict(dtype="fp16", text_encoder_projection_dim=1280))
            self.assertEqual(cond["added_cond_kwargs"]["text_embeds"].values,
                ("pooled",) if guidance == 1 else ("negative-pooled", "pooled"))
            self.assertEqual(cond["added_cond_kwargs"]["time_ids"].values,
                ("positive-time",) if guidance == 1 else ("negative-time", "positive-time"))

    def test_eval_frozen_unet_checkpointing_all_blocks(self):
        model = MockUNet()
        d.enable_unet_checkpointing(model)
        self.assertTrue(all(block.gradient_checkpointing for block in model.blocks))
        for model in (MockUNet(train=True), MockUNet(requires_grad=True), MockUNet(broken=True)):
            with self.assertRaises(ValueError):
                d.enable_unet_checkpointing(model)
            self.assertTrue(all(not block.gradient_checkpointing for block in model.blocks))


if __name__ == "__main__":
    unittest.main()
