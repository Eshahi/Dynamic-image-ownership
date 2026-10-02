"""Model-free engineering tests for the v4 revision-2 study package; no dataset image, no model."""
import random
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import revised_watermark_v4 as v4
import v4_study_protocol as p
import prepare_v4r2_study as prep
import run_v4r2_study as launcher
import v4r2_study_worker as worker
from watermark_synthetic import scene

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "experiments/c4-v4r2-three-threat-small-v1"


def features(seed):
    rng = random.Random(seed)
    values = [rng.gauss(0.0, 1.0) for _ in range(512)]
    norm = sum(v * v for v in values) ** 0.5
    return [v / norm for v in values]


class RevisionTwoPackageTests(unittest.TestCase):
    def test_identity_is_consistent(self):
        self.assertEqual(v4.REVISION, 2)
        self.assertEqual((worker.EXP, worker.RUN), (prep.EXP, prep.RUN))
        self.assertEqual(worker.RUN, "c4-v4r2-three-threat-dev-001")
        source = Path(launcher.__file__).read_text(encoding="utf-8")
        self.assertIn('with_name("v4r2_study_worker.py")', source)
        self.assertIn('"c4-v4r2-three-threat-dev-001"', source)

    def test_profile_is_revision_one_profile_plus_mismatch_fields(self):
        import json
        new = json.loads((PACKAGE / "profile.json").read_text())
        old = json.loads((ROOT / "experiments/c4-v4-three-threat-small-v1/profile.json").read_text())
        added = {k: v for k, v in new["decision"].items() if k not in old["decision"]}
        self.assertEqual(added, {"semantic_mismatch_distance": 10, "instance_mismatch_distance": 10})
        for key in old:
            if key != "decision":
                self.assertEqual(new[key], old[key], key)
        profile = v4.load_profile(PACKAGE / "profile.json")
        self.assertEqual(profile["semantic_source"], "external:clip-vit-b32-a6-40d365715913")
        self.assertIn("/config/r2/", "rw-v4/config/r%d/" % v4.REVISION)

    def test_marked_synthetic_roundtrip_and_projection_transfer(self):
        profile = v4.load_profile(PACKAGE / "profile.json")
        donor = [[(int(round(v)),) * 3 for v in row] for row in scene(1, 256, 256)]
        recipient = [[(int(round(v)),) * 3 for v in row] for row in scene(2, 256, 256)]
        fd, fr = features(1), features(2)
        marked, report = v4.embed_rgb(donor, p.OWNERS[0], profile=profile, semantic_features=fd, strict=False)
        result = v4.detect(v4.luminance_from_rgb(marked), p.OWNERS[0], profile=profile, semantic_features=fd)
        self.assertEqual(result["outcome"], "both_match")
        wrong = v4.detect(v4.luminance_from_rgb(marked), p.OWNERS[1], profile=profile, semantic_features=fd)
        self.assertFalse(wrong["watermark_found"])
        moved = p.transfer(recipient, marked, profile, "public_projection")
        self.assertNotEqual(moved, recipient)
        plain = v4.detect(v4.luminance_from_rgb(recipient), p.OWNERS[0], profile=profile, semantic_features=fr)
        self.assertFalse(plain["watermark_found"])


if __name__ == "__main__":
    unittest.main()
