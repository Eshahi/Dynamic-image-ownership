"""Owned CPU arithmetic/toy-component tests, never scientific model evidence."""
import dataclasses
import hashlib
import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from src.embedding.proposed import (DiffusersComponents, EmbeddingError, Settings,
    centered_score, dct_coefficients, latent_streams, optimize_existing, padded_source)
from scripts.noise_path_reference import eta_zero_step
from scripts.pixel_dct_control import dct8, template_from_key

try:
    import torch
except ImportError:
    torch = None

SETTINGS = Settings(10, .2, .18215, 256, .2, .3, .01, .005, 2, 1, 1, 1, 1, .1, .1)
SOURCE = bytes.fromhex("01"*32)
WS = bytes.fromhex("02"*32)
WI = bytes.fromhex("03"*32)
CONFIG = bytes.fromhex("04"*32)


class ConfigContract(unittest.TestCase):
    def test_reject_bad_parameters(self):
        for field, value in (("alpha_s", -1), ("rho", 0), ("lambda_q", float("nan")),
                             ("maximum_side", 257), ("iterations", True), ("strength", 0),
                             ("inference_steps", 1000), ("margin_i", 2)):
            with self.subTest(field=field), self.assertRaises(ValueError):
                dataclasses.replace(SETTINGS, **{field: value})

    def test_cli_invalid_config_no_model_import(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary)/"bad.json"
            path.write_text("{}", encoding="utf-8")
            proc = subprocess.run([sys.executable, str(root/"scripts/embed.py"), "--config", str(path), "--preview"],
                                  capture_output=True, text=True, timeout=40)
            self.assertEqual(proc.returncode, 2)
            self.assertFalse(json.loads(proc.stdout)["scientific_execution_authorized"])

    def test_cli_valid_synthetic_structure_preview_is_not_execution(self):
        root = Path(__file__).resolve().parents[1]
        sys.path.insert(0, str(root/"scripts"))
        from test_validate_method_config import detector_id, specimen
        value = specimen(json.loads((root/"configs/method.schema.json").read_text()))
        value["embedding"]["scheduler"]["strength"] = 1
        value["embedding"]["alpha_s"] = 1
        value["dct"]["config_id"] = detector_id(value)
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary)/"synthetic-config.json"
            path.write_text(json.dumps(value), encoding="utf-8")
            for preview, code, status in ((True, 0, "component_preflight_only"),
                                           (False, 4, "execution_adapter_not_ready")):
                command = [sys.executable, str(root/"scripts/embed.py"), "--config", str(path)]
                if preview:
                    command.append("--preview")
                proc = subprocess.run(command, capture_output=True, text=True, timeout=40)
                self.assertEqual(proc.returncode, code, proc.stderr)
                record = json.loads(proc.stdout)
                self.assertEqual(record["status"], status)
                self.assertFalse(record["scientific_execution_authorized"])
                self.assertEqual(record["config_sha256"], hashlib.sha256(path.read_bytes()).hexdigest())


@unittest.skipIf(torch is None, "owned tensor tests require existing WSL Torch environment")
class TensorContracts(unittest.TestCase):
    def setUp(self):
        torch.set_num_threads(1)
        # Owned analytic pixels, no fixture file, original study image or RNG.
        self.source = (.2 + torch.arange(3*37*43, dtype=torch.float32).remainder(71)/150).reshape(1, 3, 37, 43)

    def backend(self, settings=SETTINGS):
        class VAE(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.parameter = torch.nn.Parameter(torch.tensor(.8))
                self.config = SimpleNamespace(scaling_factor=settings.vae_scale)

            def encode(self, image):
                value = torch.nn.functional.avg_pool2d(image, 8)*self.parameter
                value = torch.cat((value, value.mean(1, keepdim=True)), 1)
                return SimpleNamespace(latent_dist=SimpleNamespace(mode=lambda: value))

            def decode(self, latent):
                image = torch.nn.functional.interpolate(latent[:, :3], scale_factor=8, mode="nearest")
                return SimpleNamespace(sample=image*self.parameter)

        class UNet(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.parameter = torch.nn.Parameter(torch.tensor(.01))
                self.config = SimpleNamespace(in_channels=4, out_channels=4, cross_attention_dim=768)
                self.calls = []

            def forward(self, sample, timestep, encoder_hidden_states):
                self.calls.append((int(timestep), tuple(sample.shape), tuple(encoder_hidden_states.shape)))
                return SimpleNamespace(sample=sample*self.parameter)

        return DiffusersComponents(VAE(), UNet(), torch.zeros(1, 77, 768), settings)

    def run_candidate(self, **kwargs):
        return optimize_existing(self.source, SETTINGS, self.backend(), seed=7,
            source_digest=SOURCE, ws=WS, wi=WI, config_id=CONFIG, **kwargs)

    def test_padding_only_bottom_right_and_resolution_guard(self):
        padded = padded_source(self.source, 256)
        self.assertEqual(tuple(padded.shape), (1, 3, 64, 64))
        self.assertTrue(torch.equal(padded[:, :, :37, :43], self.source))
        self.assertTrue(torch.equal(padded[:, :, -1, -1], self.source[:, :, -1, -1]))
        for source in (self.source.double(), self.source*2, torch.zeros(1, 3, 31, 43),
                       torch.zeros(1, 3, 257, 32), self.source.clone().requires_grad_()):
            with self.assertRaises(EmbeddingError):
                padded_source(source, 256)

    def test_stream_known_answer_repeat_domain_unit_norm(self):
        base, ps, pi = latent_streams(7, bytes(32), WS, WI, CONFIG, 2, 3, "cpu")
        from scripts.base_noise_reference import base_noise_f32le
        raw = base.numpy().astype("<f4").tobytes()
        self.assertEqual(raw, base_noise_f32le(7, "00"*32, 4, 2, 3))
        again = latent_streams(7, bytes(32), WS, WI, CONFIG, 2, 3, "cpu")
        self.assertTrue(all(torch.equal(a, b) for a, b in zip((base, ps, pi), again)))
        self.assertFalse(torch.equal(ps, pi))
        self.assertAlmostEqual(torch.linalg.vector_norm(ps.double()).item(), 1, places=7)
        self.assertFalse(torch.equal(base, latent_streams(8, bytes(32), WS, WI, CONFIG, 2, 3, "cpu")[0]))

    def test_dct_native_edge_block_and_scalar_reference(self):
        image = self.source.double().requires_grad_()
        coefficients = dct_coefficients(image)
        self.assertEqual(tuple(coefficients.shape), (30, 8, 8))
        y = .299*image[0, 0]+.587*image[0, 1]+.114*image[0, 2]
        for index, by, bx in ((0, 0, 0), (29, 4, 5)):
            block = tuple(tuple(y[min(by*8+j, 36), min(bx*8+k, 42)].item() for k in range(8)) for j in range(8))
            expected = torch.tensor(dct8(block), dtype=torch.float64)
            self.assertLess((coefficients[index]-expected).abs().max().item(), 2e-14)
        template = template_from_key("semantic", WS, CONFIG, 43, 37)
        score, zero = centered_score(coefficients, template, ((1, 2), (2, 1), (2, 2), (1, 3)))
        self.assertFalse(zero)
        score.backward()
        self.assertTrue(torch.isfinite(image.grad).all())
        self.assertGreater(image.grad.abs().max().item(), 0)
        # Central finite difference on a non-edge/saturated pixel.
        delta = 1e-6
        def evaluated(sign):
            changed = image.detach().clone()
            changed[0, 0, 3, 4] += sign*delta
            return centered_score(dct_coefficients(changed), template, ((1, 2), (2, 1), (2, 2), (1, 3)))[0].item()
        self.assertAlmostEqual((evaluated(1)-evaluated(-1))/(2*delta), image.grad[0, 0, 3, 4].item(), places=7)

    def test_zero_variance_is_diagnostic_not_positive_match(self):
        image = torch.full((1, 3, 32, 32), .5, requires_grad=True)
        score, zero = centered_score(dct_coefficients(image), [(1, -1, 1, -1)]*16,
                                     ((1, 2), (2, 1), (2, 2), (1, 3)))
        self.assertTrue(zero)
        self.assertEqual(score.item(), 0)
        score.backward()
        self.assertTrue(torch.isfinite(image.grad).all())

    def test_scheduler_eta_zero_scalar_parity_and_no_cfg(self):
        backend = self.backend()
        self.assertEqual(backend.times, (101, 1))
        schedule = backend.scheduler
        sample, prediction = torch.tensor([.2]), torch.tensor([.3])
        for t in backend.times:
            previous = t-100
            ap = schedule.alphas_cumprod[previous if previous >= 0 else 0].item()
            expected = eta_zero_step(.2, .3, schedule.alphas_cumprod[t].item(), ap)
            actual = schedule.step(prediction, t, sample, eta=0).prev_sample.item()
            self.assertAlmostEqual(actual, expected, places=6)
        latent = backend.encode(padded_source(self.source, 256))
        noise = torch.zeros_like(latent, requires_grad=True)
        output = backend.reconstruct(latent, noise)
        output.sum().backward()
        self.assertGreater(noise.grad.abs().sum().item(), 0)
        self.assertEqual(len(backend.unet.calls), 2)
        self.assertTrue(all(shape[0] == 1 for _, shape, _ in backend.unet.calls))
        self.assertTrue(all(p.grad is None and not p.requires_grad for m in (backend.vae, backend.unet) for p in m.parameters()))

    def test_control_gains_and_u_are_zero_even_with_nonzero_settings(self):
        backend = self.backend()
        result = optimize_existing(self.source, SETTINGS, backend, seed=7,
            source_digest=SOURCE, ws=WS, wi=WI, config_id=CONFIG, control=True)
        self.assertTrue(torch.equal(result.image, result.matched_control))
        self.assertEqual(result.perturbation.abs().sum().item(), 0)
        self.assertEqual(result.metadata["effective_alpha_s"], 0)
        self.assertEqual(result.metadata["effective_alpha_i"], 0)
        self.assertEqual(len(backend.unet.calls), 2)
        self.assertEqual(len(result.trajectory), 1)

    def test_optimize_shape_finite_projection_final_iteration_and_repeat(self):
        records = []
        first = self.run_candidate(record=records.append)
        second = self.run_candidate()
        self.assertEqual(tuple(first.image.shape), tuple(self.source.shape))
        self.assertTrue(torch.equal(first.image, second.image))
        self.assertTrue(torch.isfinite(first.image).all())
        self.assertLessEqual(torch.linalg.vector_norm(first.perturbation.double()).item(), SETTINGS.rho+1e-8)
        self.assertFalse(torch.equal(first.image, first.matched_control))
        self.assertEqual(records, first.trajectory)
        self.assertEqual(records[-1]["iteration"], SETTINGS.iterations)
        self.assertGreater(records[0]["gradient_norm"], 0)
        self.assertEqual(first.metadata["final_discrete_verification"], "NOT_RUN")
        self.assertNotEqual(first.status, "success")

    def test_detached_nonfinite_or_wrong_shape_backend_fails(self):
        for mode in ("detach", "nan", "shape"):
            backend = self.backend()
            original = backend.reconstruct
            def broken(latent, noise, mode=mode):
                output = original(latent, noise)
                if mode == "detach": return output.detach()
                if mode == "nan": return output*float("nan")
                return output[:, :, :-1]
            backend.reconstruct = broken
            with self.subTest(mode=mode), self.assertRaises(EmbeddingError):
                optimize_existing(self.source, SETTINGS, backend, seed=7,
                    source_digest=SOURCE, ws=WS, wi=WI, config_id=CONFIG)

    def test_settings_mismatch_and_failed_journal_callback_abort(self):
        with self.assertRaises(EmbeddingError):
            optimize_existing(self.source, SETTINGS, self.backend(dataclasses.replace(SETTINGS, strength=.3)),
                seed=7, source_digest=SOURCE, ws=WS, wi=WI, config_id=CONFIG)
        def failed_record(row):
            raise OSError("owned synthetic journal failure")
        with self.assertRaises(OSError):
            self.run_candidate(record=failed_record)


if __name__ == "__main__":
    unittest.main()
