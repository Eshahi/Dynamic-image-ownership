"""Model-free engineering tests for the v5 two-tier study package; no dataset image, no model."""
import json
import os
import random
import sys
import unittest
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import revised_watermark_v5 as v5
import v5_study_protocol as p
import prepare_v5_study as prep
import run_v5_study as launcher
from watermark_synthetic import scene

try:
    import resource  # noqa: F401  (the worker needs it; Windows has none)
    import v5_study_worker as worker
except ImportError:
    worker = None

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "experiments/c4-v5-two-tier-regeneration-v1"


def features(seed):
    rng = random.Random(seed)
    values = [rng.gauss(0.0, 1.0) for _ in range(512)]
    norm = sum(v * v for v in values) ** 0.5
    return [v / norm for v in values]


def rgb(seed):
    return [[[int(round(v))] * 3 for v in row] for row in scene(seed, 256, 256)]


class PackageTests(unittest.TestCase):
    def test_identity_is_consistent(self):
        self.assertEqual((v5.VERSION, v5.REVISION), (5, 1))
        self.assertEqual((p.EXP, p.RUN), (prep.EXP, prep.RUN))
        self.assertEqual((launcher.RUN, launcher.REHEARSAL_RUN), (p.RUN, p.REHEARSAL_RUN))
        self.assertEqual(prep.REHEARSAL_RUN, p.REHEARSAL_RUN)
        if worker is not None:
            self.assertEqual((worker.EXP, worker.RUN, worker.REHEARSAL_RUN), (p.EXP, p.RUN, p.REHEARSAL_RUN))
        source = Path(launcher.__file__).read_text(encoding="utf-8")
        self.assertIn('with_name("v5_study_worker.py")', source)
        if os.name == "nt":  # the launcher is the Windows entrypoint; its path mapping needs drive paths
            self.assertEqual(launcher.command("C:/m.json", "C:/out")[-4:], ["--manifest", "/mnt/c/m.json", "--output-dir", "/mnt/c/out"])
            self.assertEqual(launcher.command("C:/m.json", "C:/out", True)[-1], "--rehearsal")

    def test_inventory_and_calls(self):
        labels = json.loads((ROOT / "experiments/c4-three-threat-small-v1/semantic-labels.json").read_text())["pairs"]
        rows = p.inventory(labels)
        self.assertEqual(len(rows), p.ROWS)
        self.assertEqual(len({row["id"] for row in rows}), p.ROWS)
        self.assertEqual(dict(Counter(row["axis"] for row in rows)), {"clean": 34, "T4": 80, "T3": 390, "T1s": 40, "T5": 66, "T5-transfer": 7})
        self.assertEqual(p.planned_calls(rows), p.CALLS)
        self.assertEqual(dict(Counter(row["arm"] for row in rows if row["axis"] == "T4")),
                         {"clean_donor_residual": 40, "public_projection": 20, "unmarked_projection_sham": 20})
        with self.assertRaises(ValueError):
            p.inventory(labels[:-1])

    def test_profile_is_the_shipped_public_profile_with_the_clip_source(self):
        study = v5.load_profile(PACKAGE / "profile.json")
        shipped = v5.load_profile(ROOT / "configs/revised-watermark-v5.example.json")
        self.assertEqual(study["semantic_source"], "external:clip-vit-b32-a6-40d365715913")
        self.assertEqual({k: v for k, v in study.items() if k != "semantic_source"}, {k: v for k, v in shipped.items() if k != "semantic_source"})
        strong = v5.load_profile(PACKAGE / "profile-strong.json")
        self.assertEqual(v5.detector_config_id(strong), v5.detector_config_id(study))
        changed = {k: (study["embedding"][k], strong["embedding"][k]) for k in study["embedding"] if study["embedding"][k] != strong["embedding"][k]}
        self.assertEqual(changed, {"visibility": (1.0, 2.0), "min_robust_psnr_db": (36.0, 33.0)})
        self.assertEqual({k: v for k, v in strong.items() if k != "embedding"}, {k: v for k, v in study.items() if k != "embedding"})

    def test_marked_synthetic_roundtrip_and_two_tier_transfer(self):
        profile = v5.load_profile(PACKAGE / "profile.json")
        donor, recipient = rgb(1), rgb(2)
        fd, fr = features(1), features(2)
        marked, report = v5.embed_rgb(donor, p.OWNERS[0], profile=profile, semantic_features=fd, strict=False)
        marked = [[list(pixel) for pixel in row] for row in marked]
        self.assertEqual(v5.detect_rgb(marked, p.OWNERS[0], profile=profile, semantic_features=fd)["outcome"], "both_match")
        self.assertFalse(v5.detect_rgb(marked, p.OWNERS[1], profile=profile, semantic_features=fd)["watermark_found"])
        self.assertFalse(v5.detect_rgb(recipient, p.OWNERS[0], profile=profile, semantic_features=fr)["watermark_found"])
        moved = p.transfer(recipient, marked, profile, "public_projection")
        self.assertNotEqual(moved, recipient)
        delivered = v5.detect_rgb(moved, p.OWNERS[0], profile=profile, semantic_features=fr, binding_mode="none")
        self.assertEqual(delivered["outcome"], "both_match")
        bound = v5.detect_rgb(moved, p.OWNERS[0], profile=profile, semantic_features=fr)
        self.assertEqual(bound["outcome"], "content_mismatch")
        sham = p.transfer(recipient, donor, profile, "unmarked_projection_sham")
        self.assertFalse(v5.detect_rgb(sham, p.OWNERS[0], profile=profile, semantic_features=fr, binding_mode="none")["watermark_found"])
        with self.assertRaises(ValueError):
            p.transfer(recipient, marked, profile, "public_band")

    def test_ordinary_operations(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow is not installed in this interpreter")
        image = Image.new("RGB", (512, 512), (120, 130, 140))
        self.assertEqual(p.ordinary(image, "jpeg75").size, (512, 512))
        self.assertEqual(p.ordinary(image, "down384").size, (384, 384))
        with self.assertRaises(ValueError):
            p.ordinary(image, "rotate")


if __name__ == "__main__":
    unittest.main()
