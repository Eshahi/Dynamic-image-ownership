"""Model-free engineering tests only."""
import json
import sys
import unittest
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4_study_protocol as p
import revised_watermark_v4 as v4


class ProtocolTests(unittest.TestCase):
    def test_inventory_and_accounting(self):
        labels = json.loads((Path(__file__).resolve().parents[1] /
            "experiments/c4-three-threat-small-v1/semantic-labels.json").read_text())["pairs"]
        rows = p.inventory(labels)
        self.assertEqual(len(rows), 537)
        self.assertEqual(len({r["id"] for r in rows}), 537)
        self.assertEqual(p.planned_calls(rows), 1884)
        self.assertEqual(Counter(r["axis"] for r in rows),
                         {"clean":24, "T3":260, "T4":180, "T5":66, "T5-transfer":7})
        self.assertEqual(Counter(r["arm"] for r in rows if r["axis"] == "T4"),
                         {"public_patch":40,"unmarked_patch_sham":40,"clean_donor_residual":40,
                          "public_band":20,"unmarked_band_sham":20,"public_projection":20})

    def test_external_profile_requires_features(self):
        from copy import deepcopy
        profile = deepcopy(v4.DEFAULT_PROFILE)
        profile["semantic_source"] = "external:clip-vit-b32-a6-40d365715913"
        with self.assertRaises(ValueError):
            v4.detect([[128.0]*160 for _ in range(160)], p.OWNERS[0], profile=profile)

    def test_transfer_identity_and_projection(self):
        # Two analytic RGB fixtures, not dataset images; no encoder invoked.
        import math
        def host(phase):
            return [[(int(128+20*math.cos(x*.12+phase)+10*math.sin(y*.13)),)*3
                      for x in range(160)] for y in range(160)]
        left, right = host(0), host(1)
        for arm in ("public_band","public_projection","unmarked_band_sham"):
            same = p.transfer(left,left,v4.DEFAULT_PROFILE,arm)
            self.assertEqual(same,left)
            copied = p.transfer(right,left,v4.DEFAULT_PROFILE,arm)
            self.assertNotEqual(copied,right)
            planes = [v4._plane(*pair) for pair in v4.SEMANTIC_FREQUENCIES+v4.INSTANCE_FREQUENCIES]
            donor = v4._analyse(v4.luminance_from_rgb(left),planes)[1]
            before = v4._analyse(v4.luminance_from_rgb(right),planes)[1]
            after = v4._analyse(v4.luminance_from_rgb(copied),planes)[1]
            e0 = sum((a-b)**2 for x,y in zip(donor,before) for a,b in zip(x,y))
            e1 = sum((a-b)**2 for x,y in zip(donor,after) for a,b in zip(x,y))
            self.assertLess(e1,e0)

    def test_public_only_and_distance(self):
        image = [[(128,128,128)]*160 for _ in range(160)]
        with self.assertRaises(ValueError):
            p.transfer(image,image,v4.KEYED_PROFILE,"public_projection")
        self.assertEqual(p.distance(0,2**32-1),32)
        with self.assertRaises(ValueError):
            p.distance(True,0)


if __name__ == "__main__":
    unittest.main()
