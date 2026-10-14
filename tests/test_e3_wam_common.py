"""Interface regressions: no target-assisted decode or fabricated empty-mask word."""
import inspect
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import e3_wam_common as common


class CommonInterfaceTests(unittest.TestCase):
    def test_message_order_and_leading_zero(self):
        self.assertEqual(common.hex_bits('80000001'), [1]+[0]*30+[1])
        for q in common.TARGETS + ('00000000', 'ffffffff', '80000001'):
            self.assertEqual(common.bits_hex(common.hex_bits(q)), q)

    def test_target_is_evaluator_only(self):
        self.assertEqual(list(inspect.signature(common.read_e3).parameters), ['ev','rgb'])
        self.assertEqual(list(inspect.signature(common.read_wam).parameters), ['adapter','rgb'])
        r = dict(readable=True, decoded_hex='00000000')
        self.assertTrue(common.evaluate(r, '00000000')['Q'])
        self.assertFalse(common.evaluate(r, 'ffffffff')['Q'])
        self.assertEqual(r, dict(readable=True, decoded_hex='00000000'))
        r['readable'] = False
        self.assertFalse(common.evaluate(r, '00000000')['Q'])
        self.assertIsNone(common.evaluate(r, '00000000')['bit_errors'])

    def test_empty_mask_never_calls_decoder(self):
        import torch
        def forbidden(*args):
            self.fail('Empty mask must not decode NaNs into a zero message')
        r = common.wam_predictions(torch.zeros(1,33,2,2), forbidden)
        self.assertFalse(r['readable'])
        self.assertIsNone(r['decoded_hex'])

    def test_native_half_logit_threshold_and_selection(self):
        import torch
        sys.path[:0] = [str(common.MAIN/'.thesis-build/journal-wam-deps'),
            str(common.MAIN/'.thesis-build/assets/journal-wam-2c08af04/source')]
        from watermark_anything.data.metrics import msg_predict_inference
        p = torch.zeros(1,33,2,2)
        p[:,0,0,0] = 1  # Exactly one selected pixel; huge other pixels must be ignored.
        p[:,1:] = 100
        p[:,1:,0,0] = .25  # Positive raw logits below .5 must decode to zero.
        p[:,1,0,0] = .5001
        p[:,32,0,0] = 1
        result = common.wam_predictions(p, msg_predict_inference)
        self.assertEqual(result['decoded_hex'], '80000001')
        self.assertEqual(result['native']['mask_positive_pixels'], 1)


if __name__ == '__main__':
    unittest.main()
