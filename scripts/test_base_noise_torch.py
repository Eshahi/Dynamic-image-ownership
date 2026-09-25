"""Optional, model-free CPU comparison of the A6 scalar oracle with torch."""

import hashlib
import math
import struct
import unittest

from base_noise_reference import base_noise_f32le


class BaseNoiseTorchTests(unittest.TestCase):
    def test_cpu_float64_box_muller_then_float32(self):
        try:
            import torch
        except ImportError:
            self.skipTest("torch is absent from this environment")
        # Reconstruct the six canonical fields independently of the oracle.
        fields = [b"a5-base-noise-v1", (7).to_bytes(8, "big"), bytes(32),
                  (1).to_bytes(4, "big"), (2).to_bytes(4, "big"),
                  (3).to_bytes(4, "big")]
        message = b"".join(len(value).to_bytes(4, "big") + value for value in fields)
        words = hashlib.shake_256(message).digest(48)
        computed = []
        for offset in range(0, len(words), 16):
            x1, x2 = struct.unpack_from(">QQ", words, offset)
            u1 = torch.tensor((x1 + 0.5) / 2**64, dtype=torch.float64)
            u2 = torch.tensor((x2 + 0.5) / 2**64, dtype=torch.float64)
            radius = torch.sqrt(-2.0 * torch.log(u1))
            angle = (2.0 * math.pi) * u2
            computed.extend((float((radius * torch.cos(angle)).float()),
                             float((radius * torch.sin(angle)).float())))
        reference = struct.unpack("<6f", base_noise_f32le(7, "00" * 32, 1, 2, 3))
        self.assertEqual(len(computed), len(reference))
        for observed, expected in zip(computed, reference):
            self.assertLessEqual(abs(observed - expected), 2e-6)


if __name__ == "__main__":
    unittest.main()
