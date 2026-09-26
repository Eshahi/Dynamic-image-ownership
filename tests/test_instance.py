"""Owned synthetic fixtures and supplied scores, not scientific method results."""
import hashlib
import math
import struct
import unittest
from dataclasses import replace
from src.signatures.instance import (InstanceScore, SemanticScore, bind_canonical_image,
    derive_instance, fuse_candidates, perceptual_code, radius_one)
from src.signatures.owner import derive_public_signatures, pack_fields
from scripts.candidate_search_reference import evaluate


def fixture(width=37, height=43):
    return bytes((17*x+29*y+53*c+3*x*y) % 256 for y in range(height) for x in range(width) for c in range(3))


class InstanceTests(unittest.TestCase):
    q = bytes.fromhex("a503")
    h = bytes.fromhex("12345678")

    def test_constant_rgb_analytic_ac_collision(self):
        for width, height in ((32, 32), (33, 65), (97, 41)):
            for color in ((0, 0, 0), (23, 45, 67), (255, 255, 255)):
                result = perceptual_code(bytes(color)*(width*height), width, height)
                self.assertEqual(result.packed, bytes(4))
                self.assertEqual(result.median, 0)
                self.assertEqual(result.minimum_selected_margin, 0)
                self.assertTrue(result.constant_rgb)

    def test_resize_and_coefficients_against_direct_2d_dct(self):
        width, height = 37, 43; raw = fixture(width, height)
        rounded = lambda byte: struct.unpack("<f", struct.pack("<f", byte/255))[0]
        plane = [[sum(weight*rounded(raw[3*(y*width+x)+c]) for c, weight in enumerate((.299, .587, .114)))
                  for x in range(width)] for y in range(height)]
        sampled = []
        for y in range(32):
            sy = (y+.5)*height/32-.5; iy = math.floor(sy); dy = sy-iy
            row = []
            for x in range(32):
                sx = (x+.5)*width/32-.5; ix = math.floor(sx); dx = sx-ix
                def get(a, b): return plane[min(height-1, max(0, b))][min(width-1, max(0, a))]
                row.append((1-dy)*((1-dx)*get(ix, iy)+dx*get(ix+1, iy))+
                           dy*((1-dx)*get(ix, iy+1)+dx*get(ix+1, iy+1)))
            sampled.append(row)
        coefficient = {}
        for u in range(8):
            for v in range(8):
                coefficient[u, v] = (math.sqrt(1/32) if u == 0 else math.sqrt(2/32))*(math.sqrt(1/32) if v == 0 else math.sqrt(2/32))*math.fsum(
                    sampled[y][x]*math.cos(math.pi*(y+.5)*u/32)*math.cos(math.pi*(x+.5)*v/32)
                    for y in range(32) for x in range(32))
        result = perceptual_code(raw, width, height)
        for (u, v), value in coefficient.items(): self.assertAlmostEqual(result.coefficients[u][v], value, places=12)
        median = sorted(value for position, value in coefficient.items() if position != (0, 0))[31]
        positions = sorted((p for p in coefficient if p != (0, 0)), key=lambda p: (sum(p), *p))[:32]
        bits = sum(1 << i for i, p in enumerate(positions) if coefficient[p] > median)
        self.assertEqual(result.packed, bits.to_bytes(4, "little"))
        self.assertGreater(result.minimum_selected_margin, 0)

    def test_pixel_contract_rejects_shapes_types(self):
        for raw, w, h in ((b"", 32, 32), (bytes(3072), True, 32), (bytes(3072), 32.0, 32),
                          (bytes(3072), 31, 32), (bytes(3072), 2**32, 32), (bytearray(3072), 32, 32)):
            with self.assertRaises(ValueError): perceptual_code(raw, w, h)

    def test_binding_matches_domain_separated_known_formula(self):
        one = derive_public_signatures(self.q, self.h, "Cafe\u0301")
        expected = hashlib.sha256(pack_fields(b"a5-wi-v1", self.q, self.h, "Caf\u00e9".encode())).digest()
        self.assertEqual(derive_instance(self.q, self.h, "Caf\u00e9"), expected)
        self.assertEqual(one.instance, expected)
        changed = derive_public_signatures(self.q, bytes(4), "Caf\u00e9")
        self.assertEqual(one.semantic, changed.semantic)
        self.assertNotEqual(one.instance, changed.instance)
        self.assertNotEqual(one.instance, derive_instance(self.q, self.h, "other-owner"))
        for malformed in (b"", b"\x00\xf0", bytearray(self.q)):
            with self.assertRaises(ValueError): derive_instance(malformed, self.h, "owner")

    def test_native_binding_deterministic(self):
        raw = fixture(); first = bind_canonical_image(raw, 37, 43, self.q, "owner")
        self.assertEqual(first, bind_canonical_image(raw, 37, 43, self.q, "owner"))
        self.assertEqual(first[0].packed.hex(), "1cbe0da9")
        other = bind_canonical_image(fixture(43, 37), 43, 37, self.q, "owner")
        self.assertEqual(other[0].packed.hex(), "1cbf0ac5")
        self.assertNotEqual(first[0].packed, other[0].packed)
        self.assertEqual(first[1].semantic, other[1].semantic)
        self.assertNotEqual(first[1].instance, other[1].instance)

    def scores(self, s_hit=None, i_hit=None, veto=False):
        qs, hs = radius_one(self.q, 12), radius_one(self.h, 32)
        s = tuple(SemanticScore(q, .9 if q == s_hit else -.7, veto) for q in qs)
        i = tuple(InstanceScore(q, h, .9 if (q, h) == i_hit else -.7, veto) for q in qs for h in hs)
        return s, i

    def fused(self, s, i, **kwargs):
        options = dict(tau_s=.5, tau_i=.5, detector_config_id=b"\x01"*32,
                       threshold_version="synthetic-not-calibrated-v1", owner_id="owner")
        return fuse_candidates(self.q, self.h, s, i, **(options | kwargs))

    def test_fixed_search_order_and_counts(self):
        for bits, code in ((12, self.q), (32, self.h)):
            values = radius_one(code, bits)
            self.assertEqual(values[0], code)
            self.assertEqual(len(set(values)), bits+1)
            for bit, value in enumerate(values[1:]):
                self.assertEqual(int.from_bytes(value, "little")^int.from_bytes(code, "little"), 1 << bit)
        for code, bits in ((b"\x00\xf0", 12), (bytes(4), 12), (self.q, True)):
            with self.assertRaises(ValueError): radius_one(code, bits)

    def test_same_q_required_and_all_scores_retained(self):
        qs, hs = radius_one(self.q, 12), radius_one(self.h, 32)
        for q_s, pair in ((None, None), (qs[1], None), (None, (qs[2], hs[1])),
                          (qs[1], (qs[2], hs[1])), (qs[1], (qs[1], hs[1]))):
            s, i = self.scores(q_s, pair); actual = self.fused(s[::-1], i[::-1])
            reference = evaluate(self.q, self.h, .5, .5,
                lambda q: (.9 if q == q_s else -.7, False),
                lambda q, h: (.9 if (q, h) == pair else -.7, False))
            for key in reference: self.assertEqual(actual[key], reference[key])
            self.assertEqual(len(actual["semantic_scores"]), 13)
            self.assertEqual(len(actual["instance_scores"]), 429)
        cross = self.fused(*self.scores(qs[1], (qs[2], hs[1])))
        self.assertTrue(cross["semantic_hit"] and cross["instance_hit"] and cross["cross_q_only"])
        self.assertFalse(cross["both_match"])

    def test_threshold_strictness_zero_variance_veto(self):
        s, i = self.scores(self.q, (self.q, self.h))
        self.assertFalse(self.fused(s, i, tau_s=.9, tau_i=.9)["both_match"])
        s = tuple(replace(r, score=0, zero_variance=True) for r in s)
        i = tuple(replace(r, score=0, zero_variance=True) for r in i)
        result = self.fused(s, i, tau_s=-.5, tau_i=-.5)
        self.assertFalse(result["semantic_hit"] or result["instance_hit"])

    def test_incomplete_duplicate_extra_invalid_scores_are_errors(self):
        s, i = self.scores()
        for ss, ii in ((s[:-1], i), (s, i[:-1]), ((s[0],)*13, i), (s, (i[0],)*429),
                       ((replace(s[0], q=b"\xff\x0f"), *s[1:]), i),
                       ((replace(s[0], score=float("nan")), *s[1:]), i),
                       (s, (replace(i[0], zero_variance=1), *i[1:])),
                       ((replace(s[0], score=True), *s[1:]), i)):
            with self.assertRaises(ValueError): self.fused(ss, ii)
        for changes in ({"tau_s": True}, {"tau_i": float("inf")}, {"detector_config_id": bytes(32)},
                        {"threshold_version": ""}, {"owner_id": ""}):
            with self.assertRaises(ValueError): self.fused(s, i, **changes)

    def test_owned_report_records_complete_distances_and_shapes(self):
        from scripts.instance_protocol_examples import examples
        report = examples()
        self.assertFalse(report["scientific_study_run"])
        self.assertEqual(report["output_lengths"], {"q_bytes": 2, "phash_bytes": 4, "Ws_bytes": 32, "Wi_bytes": 32})
        self.assertEqual(len(report["controlled_pairs"]), 4)
        same, changed, wrong, constant = report["controlled_pairs"]
        self.assertTrue(all(value == 0 for value in same["distances_hamming_bits"].values()))
        self.assertEqual(changed["distances_hamming_bits"]["q_bits"], 0)
        self.assertEqual(changed["distances_hamming_bits"]["Ws_bits"], 0)
        self.assertGreater(changed["distances_hamming_bits"]["phash_bits"], 0)
        self.assertGreater(changed["distances_hamming_bits"]["Wi_bits"], 0)
        self.assertEqual(wrong["distances_hamming_bits"]["phash_bits"], 0)
        self.assertGreater(wrong["distances_hamming_bits"]["Ws_bits"], 0)
        self.assertGreater(wrong["distances_hamming_bits"]["Wi_bits"], 0)
        self.assertTrue(all(value == 0 for value in constant["distances_hamming_bits"].values()))
        self.assertNotEqual(changed["input_shapes_hwc"][0], changed["input_shapes_hwc"][1])


if __name__ == "__main__": unittest.main()
