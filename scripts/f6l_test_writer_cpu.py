"""Lean writer on real models, CPU only, with very few steps. Needs the science venv and local assets.

Run: CUDA_VISIBLE_DEVICES=-1 .thesis-build/a6-science-venv/Scripts/python.exe scripts/f6l_test_writer_cpu.py
Not a scientific result: no regeneration runs and the step counts are far below the real writer.
"""
import importlib.metadata
import json
import math
import os
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import numpy as np
import torch

assert not torch.cuda.is_available()
torch.set_num_threads(6)

import f6l_common as lean_common
from f6l_writer import LeanWriter

MAIN = Path("W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5")
ASSETS = MAIN / ".thesis-build/assets"
IMAGE = MAIN / ".thesis-build/dev-runs/20261024-1431-encoder-transfer-stage2a/results/stage2a-full/images/clean_544_unmarked_None_None.png"
SHARED = {}


def shared():
    """One set of real models for the whole file: CPU loads are slow."""
    if SHARED:
        return SHARED
    from PIL import Image
    from diffusers import AutoencoderKL
    import a6_clip_visual
    import et_final_pilot as pilot
    import f5_gate
    import f5_latent_codec as f5
    import m1_latent_reconstruction as m1
    import three_threat_models as models
    profile = json.loads((ROOT / "experiments/c4-v5-two-tier-regeneration-v1/profile.json").read_text(encoding="utf-8"))
    reader = f5.Reader(ASSETS / "a6", device="cpu")
    clip, transform = a6_clip_visual.load_visual_encoder(ASSETS / "a6/clip/ViT-B-32.pt", device="cpu")
    clip.eval().requires_grad_(False)
    lpips = models.load_lpips(ASSETS / "a6", Path(importlib.metadata.distribution("lpips").locate_file("lpips")))
    sdxl = AutoencoderKL.from_pretrained(ASSETS / "journal-sdxl-vae-6f5909a7", use_safetensors=True, local_files_only=True,
                                         torch_dtype=torch.float32).eval().requires_grad_(False)
    with Image.open(IMAGE) as image:
        rgb = np.asarray(image.convert("RGB"), dtype=np.uint8).copy()
    def resize(size_in, size_out):
        mat = torch.from_numpy(pilot.lanczos_matrix(size_in, size_out)).float()
        return lambda image: (mat @ image @ mat.T).clamp(0, 1)
    SHARED.update(f5=f5, reader=reader, profile=profile, sdxl=sdxl, rgb=rgb, up=resize(512, 1024), down=resize(1024, 512),
        features=lambda value, views: f5_gate.semantic_feature(models, clip, transform, value, views),
        metric=lambda a, b: {**m1.quality(a, b), "lpips": models.lpips_score(lpips, a, b)})
    return SHARED


def build(policy=None, steps=(2, 1), metric=None, cushion=None):
    s = shared()
    f5, t = s["f5"], torch
    lean = lean_common.load_lean()
    writer = object.__new__(LeanWriter)
    writer.settings = dict(lean["writer"], robust_steps=steps[0], refine_steps=steps[1])
    writer.policy = dict(policy or {})
    writer.metric = metric or s["metric"]
    writer.within_cushion = cushion or (lambda m: lean_common.within_cushion(lean, m))
    writer._spec, writer._closed, writer.np, writer.torch, writer.f5 = None, False, np, t, f5
    writer.reader, writer.features, writer.profile, writer.sdxl = s["reader"], s["features"], s["profile"], s["sdxl"]
    writer.checked, writer.key, writer.config = f5.v5._resolve(writer.profile, None)
    writer.owner_id = "qim-pilot-owner-alpha"
    writer.owner = f5.v5.canonical_owner(writer.owner_id)
    writer.layout = f5.Layout(writer.checked, writer.key, writer.config, writer.owner, [4, 32], 1.0)
    l = writer.layout
    writer.D = t.from_numpy(l.dct.astype(np.float32))
    writer.ch, writer.u, writer.v = (t.from_numpy(a) for a in (l.ch, l.u, l.v))
    writer.coeff = t.from_numpy((l.weights * l.signs).astype(np.float32))
    writer.chip, writer.norms = t.from_numpy(l.chip), t.from_numpy(l.norms.astype(np.float32))
    writer._denoisers = {}
    writer.resize_up, writer.resize_down = s["up"], s["down"]
    row = dict(timestep=151, a=math.sqrt(.83), b=math.sqrt(.17), alpha_bar=.83)
    writer._schedule = {("R1", .2): dict(row, family="R1", strength=.2, scaling_factor=.13025),
                        ("R0", .2): dict(row, family="R0", strength=.2, scaling_factor=f5.SCALE)}
    writer.close = lambda: setattr(writer, "_closed", True)
    return writer


def signs(writer, rgb):
    f5 = writer.f5
    q, ws = f5._semantic_pattern(writer.checked, writer.key, writer.config, writer.owner, writer.features(rgb, 7),
                                 f5.v5.luminance_from_rgb(rgb.tolist()))
    return q, ws


class Toy:
    """No model: exposes exact arithmetic of the update rule."""
    def __init__(self):
        self.vae = SimpleNamespace(parameters=lambda: [])
        self.device = "cpu"

    def tensor(self, rgb01):
        return torch.from_numpy(np.ascontiguousarray(np.asarray(rgb01, np.float32).transpose(2, 0, 1)))[None]


class UpdateRule(unittest.TestCase):
    def toy(self, policy=None, steps=1):
        writer = object.__new__(LeanWriter)
        writer.settings = dict(lean_common.load_lean()["writer"], robust_steps=steps, refine_steps=1)
        writer.policy = dict(policy or {}, checkpoint=False)
        writer.torch, writer.np, writer.reader, writer.sdxl = torch, np, Toy(), None
        writer._spec = dict(robust_psnr_db=20.)
        self.a = torch.zeros(1, 3, 8, 8); self.a[0, 0] = 1.
        self.b = torch.zeros(1, 3, 8, 8); self.b[0, 1] = 1.
        writer._loss = lambda image, w: -(image * (self.b if w == "surrogate" else self.a)).sum()
        return writer

    def run_rule(self, writer):
        losses = writer._loss
        writer._surrogate = lambda image, *a: image * 1000
        calls = []
        def loss(image, w):
            calls.append(1)
            # Odd calls are the clean term, even calls the surrogate, as in the optimizer.
            return losses(image, "surrogate" if len(calls) % 2 == 0 else "clean")
        writer._loss = loss
        start = np.full((8, 8, 3), .5)
        return writer._optimize(start, None, "s", "f6-noise") - start

    def test_a_huge_surrogate_gradient_does_not_outweigh_the_clean_term(self):
        change = self.run_rule(self.toy())
        red, green = change[..., 0].sum(), change[..., 1].sum()
        self.assertGreater(red, 0)
        self.assertAlmostEqual(red, green, places=4)

    def test_update_stays_inside_the_budget_ball(self):
        change = self.run_rule(self.toy(steps=30))
        budget = 10 ** (-20. / 20) * math.sqrt(8 * 8 * 3)
        self.assertLessEqual(float(np.linalg.norm(change)), budget * (1 + 1e-5))

    def test_momentum_changes_later_steps_only(self):
        first = self.run_rule(self.toy(dict({"f6-noise": dict(momentum=True)}), steps=1))
        plain = self.run_rule(self.toy(steps=1))
        np.testing.assert_allclose(first, plain, atol=1e-6)


class RealWriter(unittest.TestCase):
    def test_render_hits_the_rms_and_drives_the_reader(self):
        writer, rgb = build(), shared()["rgb"]
        _, ws = signs(writer, rgb)
        rendered, report = writer._render(rgb, ws, 38)
        self.assertLess(abs(report["saved_rms"] - 255 * 10 ** (-38 / 20)), .05)
        layout, latent = writer.layout, writer.reader.latent
        gain = np.asarray(ws) * (np.asarray(layout.projections(latent(rendered))) - np.asarray(layout.projections(latent(rgb))))
        # The six-source mean at 38 dB is .225; this one source is lower.
        self.assertGreater(float(gain.mean()), .05)

    def embed(self, spec, policy=None):
        writer = build(policy)
        output, payload, report = writer.embed_arm(shared()["rgb"], spec, "544")
        self.assertEqual(output.shape, (512, 512, 3))
        self.assertEqual(output.dtype, np.uint8)
        self.assertEqual(payload["q"], report["semantic_code"])
        json.dumps(report, allow_nan=False)
        return output, report

    def test_budget_arm_end_to_end(self):
        _, report = self.embed(dict(variant="f5-budget", robust_psnr_db=46, render_db=None))
        self.assertIsNone(report["render"])
        self.assertIsNone(report["gradient_combination"])
        self.assertEqual(report["attempts"][0]["scale"], 1.0)

    def test_render_arm_end_to_end(self):
        output, report = self.embed(dict(variant="f5-budget", robust_psnr_db=52, render_db=38))
        self.assertEqual(report["render"]["target_db"], 38.0)
        self.assertLess(report["attempts"][-1]["metrics"]["psnr_db"], 45)

    def test_generic_arm_with_momentum_end_to_end(self):
        _, report = self.embed(dict(variant="f6-generic", robust_psnr_db=46, render_db=None), dict({"f6-generic": dict(momentum=True)}))
        self.assertTrue(report["momentum"])
        self.assertIsNotNone(report["gradient_combination"])

    def test_quality_control_scales_only_as_needed(self):
        seen = []
        def cushion(metrics):
            seen.append(1)
            return len(seen) == 3
        writer = build(metric=lambda a, b: dict(psnr_db=40., ssim_rgb=.95, lpips=.05), cushion=cushion)
        _, _, report = writer.embed_arm(shared()["rgb"], dict(variant="f5-budget", robust_psnr_db=46, render_db=None), "544")
        self.assertEqual([a["scale"] for a in report["attempts"]], [1.0, .8, .64])
        self.assertEqual(report["residual_scale"], .64)

    def test_quality_control_never_hides_a_failure(self):
        writer = build(metric=lambda a, b: dict(psnr_db=30., ssim_rgb=.5, lpips=.5), cushion=lambda m: False)
        _, _, report = writer.embed_arm(shared()["rgb"], dict(variant="f5-budget", robust_psnr_db=46, render_db=None), "544")
        self.assertEqual(len(report["attempts"]), 4)
        self.assertEqual(report["attempts"][-1]["metrics"]["lpips"], .5)

    def surrogate_gradient(self, policy):
        writer = build(policy)
        rgb = shared()["rgb"]
        _, ws = signs(writer, rgb)
        w = torch.as_tensor(np.asarray(ws, np.float32))
        x = writer.reader.tensor(rgb.astype(np.float64) / 255)
        writer._spec = dict(robust_psnr_db=46)
        gradients, seconds, _ = writer._timed_gradients(x, w, "f6-noise", "R1", .2, "544", [1000])
        self.assertTrue(bool(torch.isfinite(gradients[0]).all()))
        self.assertGreater(float(gradients[0].norm()), 0)
        return gradients[0], seconds[0]

    def test_noise_surrogate_through_the_real_sdxl_vae_in_fp32_and_bf16(self):
        fp32, slow = self.surrogate_gradient(dict(checkpoint=False))
        bf16, fast = self.surrogate_gradient(dict(checkpoint=False, bf16=True))
        cosine = float(torch.nn.functional.cosine_similarity(fp32, bf16, dim=0))
        print(json.dumps(dict(sdxl_cpu_seconds_fp32=slow, sdxl_cpu_seconds_bf16=fast, gradient_cos=cosine)), flush=True)
        self.assertGreater(cosine, .5)


class ProbeLogic(unittest.TestCase):
    def test_measure_produces_what_the_policy_rule_reads(self):
        writer = build()
        writer.f5 = SimpleNamespace(robust_pgd=lambda reader, rgb01, *a: rgb01, _semantic_pattern=shared()["f5"]._semantic_pattern, v5=shared()["f5"].v5)
        base = torch.randn(64)
        def fake(self_x, w, variant, family, strength, source_id, draws):
            return [base + .1 * torch.randn(64) for _ in draws], [.5 for _ in draws], 10
        writer._timed_gradients = fake
        result = writer.measure(shared()["rgb"], "544")
        policy = lean_common.decide_policy(lean_common.load_lean()["probe_rules"], [result])
        self.assertFalse(policy["f6-noise"]["momentum"])
        self.assertGreater(result["f6-noise"]["pairwise_cos_median"], .9)
        self.assertEqual(writer.policy, {})


if __name__ == "__main__":
    unittest.main(verbosity=2)
