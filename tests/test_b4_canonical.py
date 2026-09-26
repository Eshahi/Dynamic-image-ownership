import io
import sys
import unittest
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"scripts"))
from b4_canonical_inventory import leakage_fingerprint, fingerprint
from src.data.preprocess import load_config, sha


class CanonicalInventoryTests(unittest.TestCase):
    def test_luminance_gradient_bit_order_and_coarse_color(self):
        rgb = np.repeat(np.arange(9,dtype=np.uint8)[None,:,None],8,axis=0)
        rgb = np.repeat(rgb,3,axis=2)
        result = leakage_fingerprint(rgb)
        self.assertEqual(result["leakage_dhash64"], "ffffffffffffffff")
        self.assertEqual(len(bytes.fromhex(result["private_color8_rgb_hex"])),192)
        reverse = leakage_fingerprint(rgb[:,::-1])
        self.assertEqual(reverse["leakage_dhash64"], "0000000000000000")

    def test_actual_snapshot_binding_and_coverage_failure(self):
        config,_ = load_config(Path(__file__).resolve().parents[1]/"configs/data.json")
        for mode, status in (("RGB","canonical_pass"),("RGBA","canonical_rejected_coverage_failure")):
            stream=io.BytesIO(); Image.new(mode,(2,3)).save(stream,format="PNG"); raw=stream.getvalue()
            expected={"uid":"synthetic:"+mode,"bytes":len(raw),"sha256":sha(raw),"width":2,"height":3}
            result=fingerprint(raw,expected,config)
            self.assertEqual(result["status"],status)
            with self.assertRaisesRegex(ValueError,"hash"):
                fingerprint(raw,dict(expected,sha256="0"*64),config)


if __name__ == "__main__":
    unittest.main()
