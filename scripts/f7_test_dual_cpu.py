"""F7 writer and readers on real models, CPU only, with F5 cut to 3 PGD steps. Not a scientific result.

Run: CUDA_VISIBLE_DEVICES=-1 .thesis-build/a6-science-venv/Scripts/python.exe scripts/f7_test_dual_cpu.py
"""
import importlib.metadata
import json
import os
from pathlib import Path
import sys
import unittest

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import numpy as np
import torch

assert not torch.cuda.is_available()
torch.set_num_threads(8)

import f7_dual
import tifs_common as common

MAIN = Path("W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5")
ASSETS = MAIN / ".thesis-build/assets/a6"
IMAGE = MAIN / ".thesis-build/dev-runs/20261024-1431-encoder-transfer-stage2a/results/stage2a-full/images/clean_544_unmarked_None_None.png"
ALPHA, BETA = "qim-pilot-owner-alpha", "qim-pilot-owner-beta"


class CPUInternal:
    """The attributes of encoder_transfer_runtime.Internal that F7 uses, with the reader on the CPU."""
    def __init__(self):
        import a6_clip_visual
        import f5_gate
        import f5_latent_codec as f5
        import journal_vae_probe
        import m1_latent_reconstruction as m1
        import revised_watermark_v5 as v5
        import three_threat_models as models
        self.torch, self.models, self.f5, self.v5 = torch, models, f5, v5
        self.reader = f5.Reader(ASSETS, device="cpu")
        self.clip, self.transform = a6_clip_visual.load_visual_encoder(ASSETS / "clip/ViT-B-32.pt", device="cpu")
        self.lpips = models.load_lpips(ASSETS, Path(importlib.metadata.distribution("lpips").locate_file("lpips")))
        self.profile = json.loads((ROOT / "experiments/c4-v5-two-tier-regeneration-v1/profile.json").read_text(encoding="utf-8"))
        self.semantic_feature, self.quality = f5_gate.semantic_feature, m1.quality
        self._detect = journal_vae_probe.Evaluator.detect.__get__(self, type(self))

    def features(self, rgb, views):
        return self.semantic_feature(self.models, self.clip, self.transform, rgb, views)

    def metrics(self, a, b):
        return {**self.quality(a, b), "lpips": self.models.lpips_score(self.lpips, a, b)}


SHARED = {}


def shared():
    if not SHARED:
        from PIL import Image
        internal = CPUInternal()
        base = json.loads((ROOT / "research/encoder-transfer-20261019/stage2b-config.json").read_text(encoding="utf-8"))
        with Image.open(IMAGE) as image:
            rgb = np.asarray(image.convert("RGB"), dtype=np.uint8).copy()
        marked, payload, report = f7_dual.embed(internal, rgb, base, ALPHA, f5_overrides=dict(steps=3))
        SHARED.update(internal=internal, rgb=rgb, marked=marked, payload=payload, report=report)
    return SHARED


class RealF7(unittest.TestCase):
    def test_threshold_matches_the_frozen_bound(self):
        f7_dual.check_threshold(shared()["internal"].v5)

    def test_both_carriers_carry_one_code(self):
        s = shared()
        self.assertTrue(s["report"]["same_q"])
        self.assertEqual(s["marked"].shape, (512, 512, 3))
        self.assertEqual(s["marked"].dtype, np.uint8)
        json.dumps(s["report"], allow_nan=False)

    def test_quality_attempts_are_recorded(self):
        attempts = shared()["report"]["attempts"]
        self.assertGreaterEqual(len(attempts), 1)
        self.assertIn(attempts[-1]["v5_scale"], f7_dual.SCALES)
        print(json.dumps(dict(attempts=[dict(scale=a["v5_scale"], psnr=round(a["metrics"]["psnr_db"], 2),
            lpips=round(a["metrics"]["lpips"], 4), ssim=round(a["metrics"]["ssim_rgb"], 3)) for a in attempts])), flush=True)

    def test_owner_reads_and_wrong_owner_does_not(self):
        s = shared()
        internal = s["internal"]
        features, latent = internal.features(s["marked"], 7), internal.reader.latent(s["marked"])
        own = f7_dual.endpoints(f7_dual.read(internal, s["marked"], ALPHA, features, latent), s["payload"])
        wrong = f7_dual.endpoints(f7_dual.read(internal, s["marked"], BETA, features, latent), None)
        print(json.dumps(dict(own={k: own[k] for k in ("C", "C_f5", "C_v5", "C_combined", "J", "F", "decoded_scores")},
                              wrong={k: wrong[k] for k in ("C", "F", "decoded_scores")})), flush=True)
        self.assertTrue(own["C"])
        self.assertTrue(own["C_v5"])
        self.assertTrue(own["C_combined"])
        self.assertFalse(wrong["C"])
        self.assertFalse(wrong["F"])
        self.assertFalse(wrong["C_combined"])

    def test_unmarked_image_does_not_read(self):
        s = shared()
        e = f7_dual.endpoints(f7_dual.read(s["internal"], s["rgb"], ALPHA), None)
        self.assertFalse(e["C"])
        self.assertFalse(e["C_combined"])
        self.assertLess(e["decoded_scores"]["combined"], 8.3895)


if __name__ == "__main__":
    unittest.main(verbosity=2)
