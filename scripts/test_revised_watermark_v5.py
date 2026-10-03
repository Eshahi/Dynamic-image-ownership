"""Synthetic engineering checks for the v5 reference codec.

Every image here is procedurally generated and no model is loaded.  These tests
show that the codec does what its specification says.  They are not evidence
about photographs, about regeneration by a diffusion model or about real
semantic features; the low-pass and resampling operations below only stand in
for the property that matters to the design, the loss of fine detail with the
coarse band kept.
"""

import hashlib
import json
import math
import random
import tempfile
import unittest
from pathlib import Path

from scripts import revised_watermark_v4 as v4
from scripts.revised_watermark_v5 import (
    CHANNEL_CHIPS,
    CODE_BITS,
    DEFAULT_PROFILE,
    KEYED_PROFILE,
    PUBLIC_KEY,
    REVISION,
    SEGMENT_CHIPS,
    TAIL_CONSTANT,
    EmbeddingError,
    _activity,
    _averaging_gain,
    _channel_result,
    _coarse,
    _decoding_error_rate,
    _key_test,
    _local_flatness,
    _percentile,
    _Robust,
    _robust_carrier,
    _semantic_table,
    _shape_factors,
    _tail_bound,
    _threshold,
    decision_id,
    derive_keys,
    detect,
    detect_rgb,
    detector_config_id,
    embed,
    embed_rgb,
    embed_with_report,
    identify,
    load_profile,
    perceptual_hash,
    robust_plan,
    validate_profile,
)
from scripts.watermark_synthetic import add_noise, box_blur, plain_hosts, requantise, residual_copy, scale, scene

KEY = "local-test-key-20261002"
KEYS = (KEY, "second-test-key-0000001")
OWNER = "owner-alpha"
CONFIGS = Path(__file__).resolve().parents[1] / "configs"
SINGLE = _threshold(1e-6, 1)
SEARCHED = _threshold(1e-6, 1 << CODE_BITS)


def profile_with(base=KEYED_PROFILE, **changes):
    profile = validate_profile(base)
    for key, value in changes.items():
        if isinstance(value, dict):
            profile[key].update(value)
        else:
            profile[key] = value
    return validate_profile(profile)


def encode(chips):
    return "".join("1" if chip < 0 else "0" for chip in chips)


def coarsen(image, factor):
    """Area-average by ``factor`` and replicate back: fine detail is lost, block means of that size are kept."""
    height, width = len(image), len(image[0])
    small = [
        [sum(image[y * factor + a][x * factor + b] for a in range(factor) for b in range(factor)) / factor**2 for x in range(width // factor)]
        for y in range(height // factor)
    ]
    return [[float(math.floor(small[y // factor][x // factor] + 0.5)) for x in range(width)] for y in range(height)]


def resample(image, size):
    return [[float(min(255, max(0, math.floor(value + 0.5)))) for value in row] for row in v4._resample(image, size)]


class KnownAnswerTests(unittest.TestCase):
    """Fixed inputs and outputs, so a second implementation can check each step of the specification."""

    CONFIG = bytes(range(32))
    SECRET = b"k" * 16
    IMAGE = [[float((3 * x + 5 * y + (x * y) % 23 + ((x // 16) * 40) % 90) % 256) for x in range(264)] for y in range(256)]

    def test_identifiers(self):
        self.assertEqual(REVISION, 2)
        self.assertEqual(PUBLIC_KEY.hex(), "8976bcd96c9a5e3693f59e1c2a5dfc1c28c5222dddee630d26f762ce4801dca7")
        self.assertEqual(detector_config_id(DEFAULT_PROFILE), "92ce199715efa6bce86a9640cecf36c2f2e94aae07cc9cf2be43b1fa4410b40f")
        self.assertEqual(detector_config_id(KEYED_PROFILE), "61599617d99fbc496a9a07a9ff1228ba049be30249356a626bc792775008c9e8")
        self.assertEqual(decision_id(DEFAULT_PROFILE), "7c44fc85ce6e4e34c48ffd8c18222d42e22eea3eabc70a400f19228fa93c974d")
        self.assertNotEqual(detector_config_id(DEFAULT_PROFILE), v4.detector_config_id(v4.DEFAULT_PROFILE))

    def test_segment_keys(self):
        ws, wi = derive_keys(0x01234567, 0x89ABCDEF, b"owner", self.SECRET, self.CONFIG)
        self.assertEqual((len(ws), len(wi)), (CHANNEL_CHIPS, CHANNEL_CHIPS))
        self.assertEqual(encode(ws[:40]), "0000100001100001010000100110011011110111")
        self.assertEqual(encode(wi[:40]), "1001000101100001001101000110001011101011")
        self.assertEqual(hashlib.sha256(encode(ws).encode()).hexdigest()[:16], "3b8baf147d697c34")
        self.assertEqual(hashlib.sha256(encode(wi).encode()).hexdigest()[:16], "61dccd3022bf6030")
        self.assertNotEqual(derive_keys(0x01234567, 0x89ABCDEF, b"other", self.SECRET, self.CONFIG), (ws, wi))

    def test_a_changed_code_bit_changes_one_segment(self):
        ws, wi = derive_keys(0x01234567, 0x89ABCDEF, b"owner", self.SECRET, self.CONFIG)
        for segment in (0, 13, 31):
            flip = 1 << (CODE_BITS - 1 - segment)
            span = range(segment * SEGMENT_CHIPS, (segment + 1) * SEGMENT_CHIPS)
            ws_q, wi_q = derive_keys(0x01234567 ^ flip, 0x89ABCDEF, b"owner", self.SECRET, self.CONFIG)
            ws_h, wi_h = derive_keys(0x01234567, 0x89ABCDEF ^ flip, b"owner", self.SECRET, self.CONFIG)
            self.assertEqual(ws_h, ws)  # the semantic key does not read the hash
            for other, reference in ((ws_q, ws), (wi_q, wi), (wi_h, wi)):
                changed = [index for index in range(CHANNEL_CHIPS) if other[index] != reference[index]]
                self.assertTrue(changed)
                self.assertTrue(all(index in span for index in changed))

    def test_robust_carrier_and_geometry(self):
        chip_of_slot, signs, norms = _robust_carrier(self.SECRET, self.CONFIG, b"owner", 24)
        self.assertEqual(len(chip_of_slot), 6144)
        self.assertEqual(chip_of_slot[:12], [17, 159, 281, 299, 60, 39, 312, 108, 87, 3, 104, 138])
        self.assertEqual([int(sign) for sign in signs[:12]], [-1, 1, 1, 1, 1, 1, -1, 1, -1, -1, -1, 1])
        self.assertEqual((sum(chip_of_slot), sum(signs)), (971776, -34.0))
        counts = [chip_of_slot.count(chip) for chip in range(CHANNEL_CHIPS)]
        self.assertLessEqual(max(counts) - min(counts), 1)
        self.assertEqual(norms, [math.sqrt(count) for count in counts])
        for value, expected in zip(_averaging_gain(512, 5), (1.0, 0.993986, 0.976063, 0.946583, 0.906127)):
            self.assertAlmostEqual(value, expected, places=6)
        for value, expected in zip(_activity(_coarse(self.IMAGE), self.IMAGE)[:6], (2.4869, 2.1706, 2.5327, 3.5253, 3.2463, 2.044)):
            self.assertAlmostEqual(value, expected, places=4)

    def test_slot_weights_mask_and_shaping(self):
        checked = validate_profile(KEYED_PROFILE)
        robust = _Robust(_coarse(self.IMAGE), self.IMAGE, checked, _robust_carrier(self.SECRET, self.CONFIG, b"owner", 24))
        for values, expected in (
            (robust.mask[:4], (0.957931, 0.858568, 0.972506, 1.297074)),
            (robust.slot_weights[:6], (0.009947, 0.038847, 0.083955, 0.140947, 0.009981, 0.019799)),
            (robust.projections[:6], (0.267818, -2.016585, 0.839627, -0.638985, 0.978817, -0.960567)),
            (_local_flatness(self.IMAGE, 3)[0][:6], (5.925463, 5.925463, 5.925463, 6.616478, 7.333333, 8.069146)),
            (_shape_factors(self.IMAGE, checked)[0][:6], (0.837077, 0.837077, 0.837077, 0.931371, 1.0, 1.0)),
        ):
            for value, reference in zip(values, expected):
                self.assertAlmostEqual(value, reference, places=6)
        self.assertEqual(_percentile([4.0, 1.0, 3.0, 2.0], 75.0), 3.25)

    def test_marked_image(self):
        image = scene(4, 256, 256)
        marked, report = embed_with_report(image, OWNER, self.SECRET, KEYED_PROFILE)
        self.assertEqual(hashlib.sha256(json.dumps(marked).encode()).hexdigest(), "ef8e7295842fcb266e66a66d60851c97dafb96ba209e1d218ba50a8b7a67dab2")
        self.assertEqual((report["semantic_code"], report["perceptual_hash"]), ("fb6be451", "4e2fd97a"))
        unmarked = detect(image, OWNER, self.SECRET, KEYED_PROFILE)
        self.assertEqual(unmarked["outcome"], "neither_match")
        self.assertEqual(unmarked["semantic_code"], report["semantic_code"])

    def test_thresholds(self):
        self.assertAlmostEqual(SINGLE, 4.982033056390042, places=9)
        self.assertAlmostEqual(SEARCHED, 8.259326826136963, places=9)
        # Tighter than Hoeffding's exp(-t^2/2), which revision 1 used, and tight where it must be:
        # two equal weights reach sqrt(2) with probability exactly 1/4, and the bound gives exactly 1/4 there.
        self.assertLess(SINGLE, v4._threshold(1e-6, 1))
        self.assertLess(SEARCHED, v4._threshold(1e-6, 1 << CODE_BITS))
        self.assertAlmostEqual(_tail_bound(math.sqrt(2.0), 1), 0.25, places=12)
        self.assertAlmostEqual(TAIL_CONSTANT, 3.178656, places=6)
        self.assertLess(_threshold(1e-20, (1 << CODE_BITS) * 1_000_000), math.sqrt(CHANNEL_CHIPS))

    def test_tail_bound_holds_for_weighted_signs(self):
        """Exhaustive check on small weighted sums: the exact tail never exceeds the bound."""
        rng = random.Random(4)
        for size in (1, 2, 3, 5, 9, 12):
            for _ in range(20):
                weights = [rng.uniform(0.05, 1.0) for _ in range(size)]
                norm = math.sqrt(sum(w * w for w in weights))
                weights = [w / norm for w in weights]
                sums = sorted(sum(w if (pattern >> i) & 1 else -w for i, w in enumerate(weights)) for pattern in range(1 << size))
                for index, value in enumerate(sums):
                    exact = (len(sums) - index) / len(sums)  # P(S >= value)
                    self.assertLessEqual(exact, _tail_bound(value - 1e-12, 1) + 1e-12, (size, value))


class KeyTestTests(unittest.TestCase):
    """The statistic alone, on constructed projections."""

    def setUp(self):
        self.table = _semantic_table(b"owner", b"k" * 16, bytes(range(32)))
        self.code = 0xC0FFEE42

    def pattern(self, code):
        return [chip for segment in range(CODE_BITS) for chip in self.table[segment][(code >> (CODE_BITS - 1 - segment)) & 1]]

    def test_exact_pattern(self):
        test = _key_test([3.0 * chip for chip in self.pattern(self.code)], self.table, self.code)
        self.assertAlmostEqual(test["recomputed"], math.sqrt(CHANNEL_CHIPS), places=9)
        self.assertEqual((test["code"], test["decoded"]), (self.code, test["recomputed"]))

    def test_score_falls_in_proportion_to_the_code_distance(self):
        projections = self.pattern(self.code)
        rng = random.Random(5)
        for distance in (1, 3, 6, 10, 16):
            other = self.code
            for segment in rng.sample(range(CODE_BITS), distance):
                other ^= 1 << segment
            test = _key_test(projections, self.table, other)
            self.assertEqual(test["code"], self.code)  # decoding still reads the code the mark carries
            self.assertAlmostEqual(test["decoded"], math.sqrt(CHANNEL_CHIPS), places=9)
            expected = math.sqrt(CHANNEL_CHIPS) * (CODE_BITS - distance) / CODE_BITS
            # The segments of the wrong bits are independent patterns: about zero each, not exactly.
            self.assertLess(abs(test["recomputed"] - expected), math.sqrt(CHANNEL_CHIPS) * 0.14)

    def test_null_scores(self):
        rng = random.Random(11)
        recomputed, decoded = [], []
        for _ in range(300):
            test = _key_test([rng.gauss(0, 1) for _ in range(CHANNEL_CHIPS)], self.table, rng.getrandbits(CODE_BITS))
            recomputed.append(test["recomputed"])
            decoded.append(test["decoded"])
        self.assertLess(max(recomputed), SINGLE)
        self.assertLess(max(decoded), SEARCHED)
        self.assertLess(abs(sum(recomputed) / len(recomputed)), 0.25)
        # The decoded score is the best of 2**32 patterns, so its null mean is well above zero.
        self.assertTrue(2.6 < sum(decoded) / len(decoded) < 3.8)

    def test_zero_projections_and_ties(self):
        self.assertEqual(_key_test([0.0] * CHANNEL_CHIPS, self.table, 7), {"recomputed": 0.0, "decoded": 0.0, "code": 7})
        # A segment whose two patterns score alike keeps the recomputed bit.
        projections = [0.0] * CHANNEL_CHIPS
        projections[-1] = 1.0 if self.table[31][0][-1] == self.table[31][1][-1] else 0.0
        self.assertEqual(_key_test(projections, self.table, 0xFFFFFFFF)["code"] & 0xFFFFFFFE, 0xFFFFFFFE)

    def test_candidate_and_threshold_selection(self):
        strong = _channel_result({"recomputed": 6.0, "decoded": 17.0, "code": 0xFF}, 1e-6, 1, 0)
        self.assertEqual((strong["found"], strong["read"], strong["candidate"], strong["threshold"]), (True, True, "decoded", SEARCHED))
        self.assertEqual((strong["code_distance"], strong["decoded_code"]), (8, "000000ff"))
        self.assertAlmostEqual(strong["corrected_distance"], 8.0, places=6)
        same = _channel_result({"recomputed": 9.0, "decoded": 9.0, "code": 4}, 1e-6, 1, 4)
        self.assertEqual((same["candidate"], same["code_distance"], same["corrected_distance"]), ("recomputed", 0, 0.0))
        # Found by the recomputed pattern alone: too weak to be read, counted as carrying the recomputed code.
        weak = _channel_result({"recomputed": 6.0, "decoded": 8.0, "code": 5}, 1e-6, 1, 4)
        self.assertEqual((weak["found"], weak["read"], weak["candidate"], weak["threshold"]), (True, False, "recomputed", SINGLE))
        self.assertEqual((weak["code_distance"], weak["corrected_distance"], weak["decoding_error_rate"]), (0, 0.0, None))
        none = _channel_result({"recomputed": 4.9, "decoded": 8.2, "code": 5}, 1e-6, 1, 4)
        self.assertEqual((none["found"], none["candidate"], none["code_distance"], none["corrected_distance"]), (False, None, None, None))
        self.assertGreater(_channel_result({"recomputed": 6.0, "decoded": 9.0, "code": 5}, 1e-6, 1000, 4)["recomputed_threshold"], SINGLE)

    def test_distance_is_corrected_for_decoding_errors(self):
        self.assertEqual(_decoding_error_rate(0.0), 0.5)
        self.assertEqual(_decoding_error_rate(math.sqrt(CHANNEL_CHIPS)), 0.0)
        rates = [_decoding_error_rate(score) for score in (4.0, 6.0, 8.5, 11.0, 14.0, 17.0)]
        self.assertEqual(rates, sorted(rates, reverse=True))
        # The model against a simulation: chips are the pattern plus unit noise.
        rng = random.Random(1)
        pattern = self.pattern(self.code)
        for amplitude in (0.3, 0.5, 0.8):
            errors = predicted = 0.0
            for _ in range(120):
                test = _key_test([amplitude * chip + rng.gauss(0, 1) for chip in pattern], self.table, self.code)
                errors += bin(test["code"] ^ self.code).count("1")
                predicted += CODE_BITS * _decoding_error_rate(test["decoded"])
            self.assertLess(abs(errors - predicted) / 120, 0.6, amplitude)
        # A weakly read mark of the right code: the raw distance is several bits, the corrected one near zero.
        weak = _channel_result({"recomputed": 7.5, "decoded": 8.6, "code": 0b1111}, 1e-6, 1, 0)
        self.assertEqual(weak["code_distance"], 4)
        self.assertLess(weak["corrected_distance"], 0.5)


class ProfileTests(unittest.TestCase):
    def test_shipped_profiles(self):
        self.assertEqual(load_profile(CONFIGS / "revised-watermark-v5.example.json"), validate_profile(DEFAULT_PROFILE))
        self.assertEqual(load_profile(CONFIGS / "revised-watermark-v5-keyed.example.json"), validate_profile(KEYED_PROFILE))
        schema = json.loads((CONFIGS / "revised-watermark-v5.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(set(schema["required"]), set(DEFAULT_PROFILE))

    def test_detector_identifier_follows_detector_fields_only(self):
        reference = detector_config_id(KEYED_PROFILE)
        embedding_only = {"visibility": 2.0, "block_ratio_cap": 3.0, "min_robust_psnr_db": 33.0, "shape_window": 5, "shape_percentile": 50.0}
        self.assertEqual(detector_config_id(profile_with(embedding=embedding_only)), reference)
        self.assertEqual(detector_config_id(profile_with(decision={"semantic_radius": 4})), reference)
        self.assertNotEqual(decision_id(profile_with(decision={"semantic_radius": 4})), decision_id(KEYED_PROFILE))
        self.assertNotEqual(detector_config_id(profile_with(robust={"floor": 8.0})), reference)
        # The detector weighs slots by the mask, so the mask belongs to the detector configuration.
        for change in ({"mask_weber": 0.2}, {"mask_base": 0.5}, {"mask_cap": 4.0}, {"weight_exponent": 0.0}, {"whitening": 1.0}):
            self.assertNotEqual(detector_config_id(profile_with(robust=change)), reference, change)
        self.assertNotEqual(detector_config_id(profile_with(robust_frequencies=[[u, v] for u in range(4) for v in range(4) if u or v])), reference)
        self.assertNotEqual(detector_config_id(profile_with(semantic_source="external:clip-vit-b32")), reference)

    def test_rejected_profiles(self):
        bad = [
            dict(DEFAULT_PROFILE, extra=1),
            {key: value for key, value in DEFAULT_PROFILE.items() if key != "robust"},
            dict(DEFAULT_PROFILE, canonical_side=64),
            dict(DEFAULT_PROFILE, segment_chips=10.0),
            dict(DEFAULT_PROFILE, security="none"),
            dict(DEFAULT_PROFILE, minimum_side=128),
            dict(DEFAULT_PROFILE, robust_frequencies=[[0, 0], [1, 1]]),
            dict(DEFAULT_PROFILE, robust_frequencies=[[1, 1], [1, 1]]),
            dict(DEFAULT_PROFILE, robust_frequencies=[[1, 1], [1, 2]]),  # too few slots for 320 chips
            dict(DEFAULT_PROFILE, instance_frequencies=[[0, 1], [3, 0], [1, 3], [3, 1], [2, 3], [3, 2]]),  # a hash position
            dict(DEFAULT_PROFILE, robust=dict(DEFAULT_PROFILE["robust"], floor=0.0)),
            dict(DEFAULT_PROFILE, robust={"floor": 12.0, "whitening": 1.0}),  # the revision-1 fields
            dict(DEFAULT_PROFILE, robust=dict(DEFAULT_PROFILE["robust"], mask_cap=0.1)),
            dict(DEFAULT_PROFILE, robust=dict(DEFAULT_PROFILE["robust"], weight_exponent=2.5)),
            dict(DEFAULT_PROFILE, robust=dict(DEFAULT_PROFILE["robust"], whitening=3.5)),
            dict(DEFAULT_PROFILE, embedding=dict(DEFAULT_PROFILE["embedding"], visibility=0.0)),
            dict(DEFAULT_PROFILE, embedding=dict(DEFAULT_PROFILE["embedding"], mask_cap=5.0)),  # moved to robust
            dict(DEFAULT_PROFILE, embedding=dict(DEFAULT_PROFILE["embedding"], block_ratio_cap=0.0)),
            dict(DEFAULT_PROFILE, embedding=dict(DEFAULT_PROFILE["embedding"], shape_window=0)),
            dict(DEFAULT_PROFILE, embedding=dict(DEFAULT_PROFILE["embedding"], shape_window=3.0)),
            dict(DEFAULT_PROFILE, embedding=dict(DEFAULT_PROFILE["embedding"], shape_percentile=0.0)),
            dict(DEFAULT_PROFILE, embedding=dict(DEFAULT_PROFILE["embedding"], passes=0)),
            dict(DEFAULT_PROFILE, embedding=dict(DEFAULT_PROFILE["embedding"], design_gain=float("nan"))),
            dict(DEFAULT_PROFILE, decision=dict(DEFAULT_PROFILE["decision"], semantic_radius=10)),
            dict(DEFAULT_PROFILE, decision=dict(DEFAULT_PROFILE["decision"], false_positive_target=0.5)),
        ]
        for profile in bad:
            with self.assertRaises(ValueError):
                validate_profile(profile)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "profile.json"
            path.write_text(json.dumps(DEFAULT_PROFILE)[:-1] + ', "security": "hmac-keyed"}', encoding="utf-8")
            with self.assertRaises(ValueError):
                load_profile(path)

    def test_key_handling(self):
        image = scene(1, 256, 256)
        with self.assertRaises(ValueError):
            detect(image, OWNER, KEY)  # the public profile takes no key
        with self.assertRaises(ValueError):
            detect(image, OWNER, None, KEYED_PROFILE)
        with self.assertRaises(ValueError):
            detect(image[:200], OWNER)
        with self.assertRaises(ValueError):
            detect(image, OWNER, expected_config_id="00" * 32)
        with self.assertRaises(ValueError):
            detect(image, OWNER, binding_mode="other")
        with self.assertRaises(ValueError):
            detect(image, OWNER, roster_size=0)


class EmbeddingTests(unittest.TestCase):
    """Image-level behaviour, repeated over keys and scenes."""

    @classmethod
    def setUpClass(cls):
        cls.cases = []
        for key in KEYS:
            for seed in (2, 7):
                image = scene(seed, 256, 256)
                marked, report = embed_with_report(image, OWNER, key, KEYED_PROFILE)
                cls.cases.append((key, image, marked, report))

    def test_marked_images_verify_within_the_declared_limits(self):
        embedding = KEYED_PROFILE["embedding"]
        for key, image, marked, report in self.cases:
            self.assertTrue(report["verified"])
            result = detect(marked, OWNER, key, KEYED_PROFILE)
            self.assertEqual((result["outcome"], result["proposal_state"]), ("both_match", "authentic"))
            self.assertTrue(result["semantic"]["content_match"] and result["instance"]["content_match"])
            self.assertLessEqual(result["semantic"]["corrected_distance"], 3.0)
            self.assertLessEqual(result["instance"]["corrected_distance"], 3.0)
            self.assertGreater(result["semantic"]["decoded_score"], SEARCHED)
            self.assertGreater(result["instance"]["decoded_score"], SEARCHED)
            robust = report["robust_channel"]
            self.assertLessEqual(robust["ratio_max"], embedding["block_ratio_cap"] + 1e-9)
            self.assertGreaterEqual(robust["planned_psnr_db"], embedding["min_robust_psnr_db"] - 1e-6)
            self.assertGreaterEqual(report["robust_psnr_db"], embedding["min_robust_psnr_db"] - 0.2)
            self.assertTrue(35.0 < report["psnr_db"] < 50.0)
            self.assertTrue(all(value == math.floor(value) and 0 <= value <= 255 for row in marked for value in row))

    def test_fill_spends_the_tighter_of_block_caps_and_psnr_floor(self):
        image = scene(2, 256, 256)
        # Generous caps: the PSNR floor binds and is met exactly.
        floor_bound = embed_with_report(image, OWNER, KEY, profile_with(embedding={"block_ratio_cap": 8.0, "min_robust_psnr_db": 38.0}))[1]["robust_channel"]
        self.assertEqual(floor_bound["bound_by"], "psnr floor")
        self.assertAlmostEqual(floor_bound["planned_psnr_db"], 38.0, places=6)
        self.assertLess(floor_bound["ratio_max"], 8.0 + 1e-9)
        # Tight caps: every block reaches its cap before the floor.
        cap_bound = embed_with_report(image, OWNER, KEY, profile_with(embedding={"block_ratio_cap": 1.0, "min_robust_psnr_db": 30.0}))[1]["robust_channel"]
        self.assertEqual(cap_bound["bound_by"], "block caps")
        self.assertAlmostEqual(cap_bound["ratio_max"], 1.0, places=9)
        self.assertAlmostEqual(cap_bound["ratio_rms"], 1.0, places=9)
        self.assertGreater(cap_bound["planned_psnr_db"], 30.0)
        # The plan's own visibility budget shapes the change but does not set its final size.
        for case in self.cases:
            self.assertEqual(case[3]["robust_channel"]["visibility_share"], 1.0)

    def test_shaping_keeps_a_flat_strip_inside_a_busy_block_free(self):
        """A strip narrower than one 8x8 cell, which the block mask cannot see, takes almost none of the change."""
        rng = random.Random(9)
        image = [[float(min(255, max(0, 128 + rng.gauss(0, 30)))) for _ in range(256)] for _ in range(256)]
        for y in range(64, 128):
            for x in range(66, 72):  # 6 pixels wide, inside the coarse block columns of 16 pixels at x 64..79
                image[y][x] = 90.0 + rng.gauss(0, 1.0)
        factors = _shape_factors(image, validate_profile(KEYED_PROFILE))
        strip = [factors[y][x] for y in range(66, 126) for x in range(67, 71)]
        busy = [factors[y][x] for y in range(66, 126) for x in range(74, 79)]
        self.assertLess(max(strip), 0.3)
        self.assertGreater(sum(busy) / len(busy), 0.8)
        # The block mask of those blocks is that of the busy part: without shaping the strip would take the full change.
        checked = validate_profile(KEYED_PROFILE)
        robust = _Robust(_coarse(image), image, checked, _robust_carrier(b"k" * 16, bytes(range(32)), b"owner", 24))
        self.assertGreater(min(robust.mask[by * 16 + 4] for by in range(4, 8)), 3.0)

    def test_informed_weights_keep_the_null_distribution(self):
        """The slot weights come from the image, not the key: on an unmarked image random keys score like noise."""
        image = scene(6, 256, 256)
        checked = validate_profile(KEYED_PROFILE)
        robust = _Robust(_coarse(image), image, checked, _robust_carrier(b"k" * 16, bytes(range(32)), b"owner", 24))
        self.assertGreater(max(robust.slot_weights) / min(robust.slot_weights), 10.0)  # far from equal
        rng = random.Random(12)
        scores = []
        for _ in range(400):
            pattern = [rng.choice((-1.0, 1.0)) for _ in range(CHANNEL_CHIPS)]
            energy = math.sqrt(sum(p * p for p in robust.projections))
            scores.append(sum(e * p for e, p in zip(pattern, robust.projections)) / energy)
        mean = sum(scores) / len(scores)
        spread = math.sqrt(sum((s - mean) ** 2 for s in scores) / len(scores))
        self.assertLess(abs(mean), 0.2)
        self.assertTrue(0.85 < spread < 1.15)
        self.assertLess(max(scores), SINGLE)
        # Exponent 0 gives every slot weight 1: the statistic of revision 1.
        equal = _Robust(_coarse(image), image, profile_with(robust={"weight_exponent": 0.0}), _robust_carrier(b"k" * 16, bytes(range(32)), b"owner", 24))
        self.assertEqual(set(equal.slot_weights), {1.0})
        chips, _signs, norms = _robust_carrier(b"k" * 16, bytes(range(32)), b"owner", 24)
        self.assertEqual(equal.norms, norms)

    def test_unmarked_wrong_owner_and_wrong_key_are_negatives(self):
        for key, image, marked, _report in self.cases:
            for suspect, owner, used in ((image, OWNER, key), (marked, "owner-beta", key), (marked, OWNER, "a-different-key-000001")):
                result = detect(suspect, owner, used, KEYED_PROFILE)
                self.assertEqual((result["outcome"], result["watermark_found"]), ("neither_match", False))
                self.assertLess(result["semantic"]["recomputed_score"], SINGLE)
                self.assertLess(result["semantic"]["decoded_score"], SEARCHED)
                self.assertLess(result["instance"]["decoded_score"], SEARCHED)

    def test_ordinary_processing_keeps_both_keys(self):
        for key, _image, marked, _report in self.cases[:2]:
            for processed in (add_noise(marked, 2.0), add_noise(marked, 5.0), scale(marked, 0.8), requantise(marked, 8.0), box_blur(marked, 1)):
                self.assertEqual(detect(processed, OWNER, key, KEYED_PROFILE)["outcome"], "both_match")

    def test_loss_of_fine_detail_leaves_the_semantic_key_only(self):
        """The tier split: fine detail gone, coarse band kept, reads as the proposal's 'regenerated' state."""
        for key in KEYS:
            marked = embed(scene(2, 512, 512), OWNER, key, KEYED_PROFILE)
            # Averaging 4x4 pixels leaves the canonical 128x128 image exactly as it was; the fragile key is
            # weakened but, with the revision-2 threshold, can still be found (about 5.2 against 4.98).
            kept = detect(coarsen(marked, 4), OWNER, key, KEYED_PROFILE)
            self.assertGreater(kept["semantic"]["recomputed_score"], 15.0)
            self.assertLess(kept["instance"]["recomputed_score"], 7.0)
            # Averaging 8x8 pixels removes the fragile key and keeps the semantic key.
            result = detect(coarsen(marked, 8), OWNER, key, KEYED_PROFILE)
            self.assertEqual((result["outcome"], result["proposal_state"]), ("semantic_only", "regenerated"))
            self.assertTrue(result["semantic"]["content_match"])
            self.assertFalse(result["instance"]["found"])
            self.assertEqual(detect(add_noise(box_blur(marked, 2), 6.0), OWNER, key, KEYED_PROFILE)["outcome"], "semantic_only")

    def test_resized_image_keeps_the_semantic_key(self):
        """The robust carrier does not depend on the image size; the fragile one does."""
        image = scene(2, 512, 512)
        marked = embed(image, OWNER, KEY, KEYED_PROFILE)
        for size in (384, 320):
            result = detect(resample(marked, size), OWNER, KEY, KEYED_PROFILE)
            self.assertEqual(result["outcome"], "semantic_only", size)
            self.assertEqual(detect(resample(image, size), OWNER, KEY, KEYED_PROFILE)["outcome"], "neither_match")

    def test_public_profile_and_colour_wrapper(self):
        rng = random.Random(3)
        luminance = scene(6, 256, 256)
        rgb = [[tuple(min(255, max(0, int(value + rng.uniform(-12, 12)))) for _ in range(3)) for value in row] for row in luminance]
        marked, report = embed_rgb(rgb, OWNER)
        self.assertTrue(report["verified"])
        self.assertEqual(report["quality_domain"], "luminance of the rounded RGB output")
        self.assertEqual(detect_rgb(marked, OWNER)["outcome"], "both_match")
        self.assertEqual(detect_rgb(rgb, OWNER)["outcome"], "neither_match")
        self.assertEqual(detect_rgb(marked, "owner-beta")["outcome"], "neither_match")

    def test_plain_hosts_can_be_marked(self):
        for name, host in plain_hosts(256).items():
            report = embed_with_report(host, OWNER, KEY, KEYED_PROFILE)[1]
            self.assertTrue(report["verified"], name)
            # With no texture to hide in, the robust change stays at the base level of the mask.
            self.assertGreater(report["robust_psnr_db"], 44.0, name)

    def test_mask_ignores_gradients_and_sees_flat_patches(self):
        """The texture measure behind the mask: a ramp is flat, and so is a busy block with a flat patch."""
        rng = random.Random(8)
        ramp = [[float(40 + 0.3 * x + 0.2 * y) for x in range(512)] for y in range(512)]
        noisy = [[float(min(255, max(0, 128 + rng.gauss(0, 25)))) for _ in range(512)] for _ in range(512)]
        patched = [row[:] for row in noisy]
        for y in range(40, 64):  # a 24x24 flat patch inside the coarse block at (1, 1)
            for x in range(40, 64):
                patched[y][x] = 128.0
        flat = _activity(_coarse(ramp), ramp)
        busy = _activity(_coarse(noisy), noisy)
        holed = _activity(_coarse(patched), patched)
        self.assertLess(max(flat), 0.2)
        self.assertGreater(min(busy), 1.5)
        self.assertLess(holed[17], 0.5)
        self.assertEqual([value for index, value in enumerate(holed) if index != 17], [value for index, value in enumerate(busy) if index != 17])

    def test_hash_is_bound_after_the_robust_tier(self):
        _key, image, marked, report = self.cases[0]
        self.assertEqual(f"{perceptual_hash(marked, KEYS[0], KEYED_PROFILE):08x}", report["perceptual_hash"])
        self.assertLessEqual(v4._distance(perceptual_hash(image, KEYS[0], KEYED_PROFILE), int(report["perceptual_hash"], 16)), 6)

    def test_roster(self):
        _key, image, marked, _report = self.cases[0]
        roster = identify(marked, ["owner-beta", OWNER, "owner-gamma"], KEYS[0], KEYED_PROFILE)
        self.assertEqual((roster["found"], roster["both_match"], roster["roster_size"]), ([OWNER], [OWNER], 3))
        self.assertGreater(roster["results"][OWNER]["semantic"]["decoded_threshold"], SEARCHED)
        self.assertEqual(identify(image, ["owner-beta", OWNER], KEYS[0], KEYED_PROFILE)["found"], [])
        with self.assertRaises(ValueError):
            identify(marked, OWNER, KEYS[0], KEYED_PROFILE)

    def test_strict_embedding_reports_a_failed_verification(self):
        # Block caps this small cannot carry the semantic key through the detector's thresholds.
        starved = profile_with(embedding={"block_ratio_cap": 0.02})
        image = scene(2, 256, 256)
        with self.assertRaises(EmbeddingError) as caught:
            embed_with_report(image, OWNER, KEY, starved)
        self.assertFalse(caught.exception.report["verified"])
        self.assertFalse(embed_with_report(image, OWNER, KEY, starved, strict=False)[1]["verified"])


class ExternalEmbedderTests(unittest.TestCase):
    """The robust-tier contract for embedders that compute the change elsewhere."""

    def test_contract_reproduces_the_closed_form(self):
        image = scene(2, 256, 256)
        plan = robust_plan(image, OWNER, KEY, KEYED_PROFILE)
        self.assertEqual((len(plan["change"]), len(plan["change"][0]), len(plan["chip_of_slot"]), len(plan["slot_weights"])), (256, 24, 6144, 6144))
        self.assertEqual((len(plan["pattern"]), len(plan["chip_norms"])), (CHANNEL_CHIPS, CHANNEL_CHIPS))
        self.assertEqual((len(plan["shape"]), len(plan["shape"][0])), (256, 256))
        own, report = embed_with_report(image, OWNER, KEY, KEYED_PROFILE)
        supplied, external = embed_with_report(image, OWNER, KEY, KEYED_PROFILE, robust_change=plan["change"])
        self.assertEqual(supplied, own)
        self.assertEqual((report["robust_channel"]["source"], external["robust_channel"]["source"]), ("closed-form", "external"))

    def test_budget_is_enforced(self):
        image = scene(2, 256, 256)
        plan = robust_plan(image, OWNER, KEY, KEYED_PROFILE)
        with self.assertRaises(ValueError):
            embed_with_report(image, OWNER, KEY, KEYED_PROFILE, robust_change=[[1.5 * value for value in block] for block in plan["change"]])
        with self.assertRaises(ValueError):
            embed_with_report(image, OWNER, KEY, KEYED_PROFILE, robust_change=plan["change"][:-1])
        with self.assertRaises(ValueError):
            embed_with_report(image, OWNER, KEY, KEYED_PROFILE, robust_change=[[0.0] * 24 for _ in range(256)])
        # A weaker change is accepted as it is, never scaled up.
        weaker = [[0.5 * value for value in block] for block in plan["change"]]
        report = embed_with_report(image, OWNER, KEY, KEYED_PROFILE, robust_change=weaker, strict=False)[1]
        self.assertAlmostEqual(report["robust_channel"]["ratio_rms"], 0.5 * plan["limits"]["ratio_rms"], places=6)


class TransferTests(unittest.TestCase):
    """Marks moved onto other images, including the cases that are known to pass."""

    @classmethod
    def setUpClass(cls):
        cls.donor = scene(5, 256, 256)
        cls.marked = embed(cls.donor, OWNER, KEY, KEYED_PROFILE)
        # Two images of one composition: same structure, different texture and noise.
        cls.first, cls.second = scene(3, 512, 512, detail_seed=11), scene(3, 512, 512, detail_seed=12)
        cls.family_marked = embed(cls.first, OWNER, KEY, KEYED_PROFILE)

    def test_whole_mark_on_an_unrelated_image_is_reported_as_bound_to_other_content(self):
        result = detect(residual_copy(scene(9, 256, 256), self.marked, self.donor), OWNER, KEY, KEYED_PROFILE)
        self.assertEqual((result["outcome"], result["proposal_state"]), ("content_mismatch", "copy_paste"))
        self.assertEqual((result["semantic"]["candidate"], result["semantic"]["read"]), ("decoded", True))
        self.assertGreaterEqual(result["semantic"]["corrected_distance"], KEYED_PROFILE["decision"]["semantic_mismatch_distance"])
        # About half the segments of an unrelated code agree by chance, so the recomputed pattern scores well above
        # zero and can pass on its own; the code read from the mark decides.
        self.assertGreater(result["semantic"]["recomputed_score"], 0.25 * result["semantic"]["decoded_score"])
        for mode, expected in (("none", "both_match"), ("perceptual_only", "content_mismatch"), ("semantic_only", "content_mismatch")):
            moved = detect(residual_copy(scene(9, 256, 256), self.marked, self.donor), OWNER, KEY, KEYED_PROFILE, binding_mode=mode)
            self.assertEqual(moved["outcome"], expected, mode)

    def test_whole_mark_within_one_composition_is_caught_by_the_instance_key(self):
        result = detect(residual_copy(self.second, self.family_marked, self.first), OWNER, KEY, KEYED_PROFILE)
        self.assertEqual(result["outcome"], "content_mismatch")
        self.assertEqual(result["semantic"]["content_status"], "match")
        self.assertGreaterEqual(result["instance"]["corrected_distance"], KEYED_PROFILE["decision"]["instance_mismatch_distance"])

    def test_known_limit_coarse_part_alone_carries_the_semantic_key_within_a_composition(self):
        """Copying only the coarse part of a mark yields the 'regenerated' label on another image of the composition."""
        residual = coarsen([[128.0 + a - b for a, b in zip(row_a, row_b)] for row_a, row_b in zip(self.family_marked, self.first)], 4)
        forged = [[float(min(255, max(0, value + shift - 128.0))) for value, shift in zip(row, shifts)] for row, shifts in zip(self.second, residual)]
        result = detect(forged, OWNER, KEY, KEYED_PROFILE)
        self.assertEqual((result["outcome"], result["proposal_state"]), ("semantic_only", "regenerated"))


if __name__ == "__main__":
    unittest.main()
