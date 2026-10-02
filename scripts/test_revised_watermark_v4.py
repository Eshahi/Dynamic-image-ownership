"""Synthetic engineering checks for the v4 reference codec.

Every image here is procedurally generated.  These tests show that the codec
does what its specification says; they are not evidence about real images,
real regeneration or real semantic features.

Image-level properties are asserted over several keys and scenes, because a
single key or seed can make an outcome look more stable than it is.
"""

import hashlib
import json
import math
import random
import statistics
import tempfile
import unittest
from pathlib import Path

from scripts import revised_watermark_v3 as v3
from scripts.revised_watermark_v4 import (
    CHANNEL_BITS,
    CODE_BITS,
    DEFAULT_PROFILE,
    HELPER_CHIPS,
    KEYED_PROFILE,
    PUBLIC_KEY,
    REVISION,
    TAG_BITS,
    EmbeddingError,
    _carrier,
    _content_status,
    _correlation,
    _crc4,
    _decide,
    _helper_decode,
    _helper_encode,
    _pack,
    _stream,
    _threshold,
    block_coefficients,
    decision_id,
    derive_keys,
    detect,
    detect_rgb,
    detector_config_id,
    embed,
    embed_rgb,
    embed_with_report,
    identify,
    key_fingerprint,
    layout_features,
    load_profile,
    luminance_from_rgb,
    perceptual_hash,
    projection_targets,
    psnr,
    semantic_code,
    validate_profile,
)
from scripts.watermark_synthetic import (
    add_noise,
    box_blur,
    clamp,
    import_block_means,
    plain_hosts,
    replace_band,
    requantise,
    residual_copy,
    sawtooth,
    scale,
    scene,
)


KEY = "local-test-key-20260930"
KEYS = (KEY, "third-test-key-000000001", "another-test-key-20261001")
OWNER = "owner-alpha"
SEMANTIC_BAND = [tuple(pair) for pair in KEYED_PROFILE["semantic_frequencies"]]
INSTANCE_BAND = [tuple(pair) for pair in KEYED_PROFILE["instance_frequencies"]]
BAND = SEMANTIC_BAND + INSTANCE_BAND
HASH_POSITIONS = [(0, 1), (1, 0)]
RADIUS = KEYED_PROFILE["decision"]["instance_radius"]
FAR = KEYED_PROFILE["decision"]["instance_mismatch_distance"]
CONFIGS = Path(__file__).resolve().parents[1] / "configs"


def profile_with(base=KEYED_PROFILE, **changes):
    profile = validate_profile(base)
    for key, value in changes.items():
        if isinstance(value, dict):
            profile[key].update(value)
        else:
            profile[key] = value
    return validate_profile(profile)


def bits(left, right):
    return bin(left ^ right).count("1")


def hexbits(values):
    return f"{int(''.join(map(str, values)), 2):0{len(values) // 4}x}"


class KnownAnswerTests(unittest.TestCase):
    """Fixed inputs and outputs, so a second implementation can check each step of the specification."""

    CONFIG = bytes(range(32))
    SECRET = b"k" * 16
    IMAGE = [[float((3 * x + 5 * y + (x * y) % 23 + ((x // 16) * 40) % 90) % 256) for x in range(168)] for y in range(160)]

    def test_keyed_stream_and_keys(self):
        self.assertEqual(PUBLIC_KEY.hex(), "5a0f653d89fb5c38ce39edcc5d323ad27824c321de3664f8a3dfa5001cf0e384")
        self.assertEqual(_pack(b"ab", b"", b"c").hex(), "000000026162000000000000000163")
        self.assertEqual(
            _stream(self.SECRET, self.CONFIG, b"label", 40).hex(),
            "f328c68b235af553a67880c017989e581f20d3a9cd4304e00698cef82cad751a82448b2896647d0d",
        )
        ws, wi = derive_keys(0x01234567, 0x89ABCDEF, b"owner", self.SECRET, self.CONFIG)
        self.assertEqual((hexbits(ws), hexbits(wi)), ("69f995d99d3b644cc6c33677499036b3", "5a4d31d0ff9faaf0bb39d351e271ee93"))
        # Each binding matters on its own: the owner, the semantic code, and for Wi the hash.
        self.assertNotEqual(derive_keys(0x01234567, 0x89ABCDEF, b"other", self.SECRET, self.CONFIG), (ws, wi))
        self.assertNotEqual(derive_keys(0x01234566, 0x89ABCDEF, b"owner", self.SECRET, self.CONFIG)[0], ws)
        self.assertNotEqual(derive_keys(0x01234566, 0x89ABCDEF, b"owner", self.SECRET, self.CONFIG)[1], wi)
        self.assertEqual(derive_keys(0x01234567, 0x89ABCDEE, b"owner", self.SECRET, self.CONFIG)[0], ws)
        self.assertNotEqual(derive_keys(0x01234567, 0x89ABCDEE, b"owner", self.SECRET, self.CONFIG)[1], wi)

    def test_helper_code(self):
        self.assertEqual([_crc4(code) for code in (0xC0FFEE42, 0, 1, 0x80000000)], [6, 0, 3, 6])
        self.assertEqual(hexbits(_helper_encode(0xC0FFEE42)), "ffff00006996699696696996c33cc33c0000ffffc3c3c3c3")

    def test_carrier(self):
        bit_of_slot, signs, norms = _carrier(self.SECRET, self.CONFIG, b"owner", b"s", 160, 168, 2520)
        self.assertEqual(bit_of_slot[:12], [135, 257, 59, 122, 130, 45, 3, 189, 145, 142, 143, 3])
        self.assertEqual([int(sign) for sign in signs[:12]], [1, 1, -1, 1, -1, 1, -1, -1, -1, -1, 1, 1])
        self.assertEqual((sum(bit_of_slot), sum(signs)), (396340, -18.0))
        counts = [bit_of_slot.count(bit) for bit in range(CHANNEL_BITS)]
        self.assertLessEqual(max(counts) - min(counts), 1)
        self.assertEqual(norms, [math.sqrt(count) for count in counts])
        # The owner, the channel and the key each change the assignment.
        for other in (
            _carrier(self.SECRET, self.CONFIG, b"other", b"s", 160, 168, 2520),
            _carrier(self.SECRET, self.CONFIG, b"owner", b"i", 160, 168, 2520),
            _carrier(b"j" * 16, self.CONFIG, b"owner", b"s", 160, 168, 2520),
        ):
            self.assertLess(sum(a == b for a, b in zip(bit_of_slot, other[0])), 60)
            self.assertLess(abs(sum(a * b for a, b in zip(signs, other[1]))), 250)

    def test_content_codes_and_scores_of_a_fixed_image(self):
        vector = [((index * 37) % 11) - 5.0 for index in range(64)]
        self.assertEqual(f"{semantic_code(vector):08x}", "f757448e")
        self.assertEqual(f"{semantic_code(vector, self.SECRET, KEYED_PROFILE):08x}", "f6e75778")
        # The vector is scaled before projection; without that a small vector falls under the sign tolerance.
        for factor in (1e-11, 1e-9, 1e30):
            self.assertEqual(semantic_code([value * factor for value in vector]), semantic_code(vector), factor)
        self.assertEqual(f"{perceptual_hash(self.IMAGE):08x}", "3cfa1a45")
        self.assertEqual(f"{perceptual_hash(self.IMAGE, self.SECRET, KEYED_PROFILE):08x}", "09670bb9")
        self.assertEqual([round(value, 6) for value in layout_features(self.IMAGE)[:4]], [-28.169048, 28.397619, -5.501042, -41.620387])
        result = detect(self.IMAGE, "owner")
        self.assertEqual((result["semantic_code"], result["perceptual_hash"]), ("4e3e39c7", "3cfa1a45"))
        self.assertAlmostEqual(result["semantic"]["score"], -0.176874464, places=8)
        self.assertAlmostEqual(result["instance"]["score"], 1.326837994, places=8)
        self.assertEqual((result["semantic"]["candidates"], result["instance"]["candidates"]), (2, 4))

    def test_embedding_plan_and_marked_image_of_a_fixed_host(self):
        # Non-square on purpose: height and width enter the carrier in that order.
        host = scene(11, 176, 200)
        marked, report = embed_with_report(host, "owner-alpha")
        semantic, instance = report["semantic_channel"], report["instance_channel"]
        self.assertEqual((semantic["host_rejection"], instance["host_rejection"]), (0.58, 0.72))
        self.assertAlmostEqual(semantic["amplitude"], 12.781012121872985, places=9)
        self.assertAlmostEqual(instance["amplitude"], 12.984931903705977, places=9)
        self.assertAlmostEqual(semantic["host_rms"], 17.407009423337012, places=9)
        self.assertEqual((report["semantic_code"], report["perceptual_hash"], report["rounding_reserved"]), ("1a097f41", "6b560eac", True))
        digest = hashlib.sha256(bytes(int(value) for row in marked for value in row)).hexdigest()
        self.assertEqual(digest, "22785a89acd1ae2d6fbf75eba468a3677aeda6f3cd0324b989fded99b1b29b81")
        targets = projection_targets(host, "owner-alpha")
        self.assertEqual((targets["height"], targets["width"]), (176, 200))
        self.assertAlmostEqual(targets["channels"][0]["target"][0], 6.693276204728214, places=9)
        self.assertAlmostEqual(targets["channels"][1]["target"][2], -13.67528701628506, places=9)
        result = detect(marked, "owner-alpha")
        self.assertEqual((result["outcome"], result["height"], result["width"]), ("both_match", 176, 200))
        # The transposed pixels carry no readable mark: block order, frequencies and the size in the
        # carrier label all change.  The order of height and width in the label is pinned by the digest above.
        turned = [list(column) for column in zip(*marked)]
        self.assertEqual((len(turned), len(turned[0])), (200, 176))
        self.assertEqual(detect(turned, "owner-alpha")["outcome"], "neither_match")

    def test_identifiers_luminance_and_fingerprint(self):
        self.assertEqual(REVISION, 2)
        self.assertEqual(detector_config_id(DEFAULT_PROFILE), "cdcbd2fcd50464eed7750a3c26c42aa47370b1645d8481fa86f2d93324650185")
        self.assertEqual(detector_config_id(KEYED_PROFILE), "ee70c66a021a0ebc1bc346bc01fb3a7c2982a1377801fa49041d40999aa103fa")
        self.assertEqual(decision_id(DEFAULT_PROFILE), "0f9fa5aba9c6b39ae0dce89a18c944b539538f1ffd36120ecfeb282690afb9b0")
        self.assertEqual(decision_id(KEYED_PROFILE), decision_id(DEFAULT_PROFILE))
        self.assertAlmostEqual(luminance_from_rgb([[(10, 200, 30)]])[0][0], 123.81, places=9)
        self.assertEqual(key_fingerprint(KEY), "06c7e89d8458dc75")
        self.assertNotEqual(key_fingerprint(KEYS[1]), key_fingerprint(KEY))
        self.assertNotIn(KEY.encode().hex()[:16], key_fingerprint(KEY))


class DecisionTests(unittest.TestCase):
    def test_every_combination_of_key_tests_and_content_statuses(self):
        # Rows: semantic key; columns: instance key.  None means the key was not found.
        states = (None, "match", "unchecked", "uncertain", "mismatch")
        table = {
            None: ("neither_match", "instance_only", "instance_only", "content_uncertain", "content_mismatch"),
            "match": ("semantic_only", "both_match", "both_match", "content_uncertain", "content_mismatch"),
            "unchecked": ("semantic_only", "both_match", "both_match", "content_uncertain", "content_mismatch"),
            "uncertain": ("content_uncertain", "content_uncertain", "content_uncertain", "content_uncertain", "content_mismatch"),
            "mismatch": ("content_mismatch",) * 5,
        }
        labels = {
            "neither_match": "not_detected",
            "both_match": "authentic",
            "semantic_only": "regenerated",
            "content_mismatch": "copy_paste",
            "instance_only": "unclassified",
            "content_uncertain": "unclassified",
        }
        for semantic in states:
            for instance, outcome in zip(states, table[semantic]):
                decided = _decide(semantic is not None, semantic, instance is not None, instance)
                self.assertEqual(decided, (outcome, labels[outcome]), (semantic, instance))
        # The status of a key that was not found is ignored; a found key must have one.
        self.assertEqual(_decide(False, "mismatch", True, "match"), ("instance_only", "unclassified"))
        self.assertEqual(_decide(True, "match", False, "mismatch"), ("semantic_only", "regenerated"))
        self.assertEqual(_decide(False, "mismatch", False, "mismatch"), ("neither_match", "not_detected"))
        for arguments in ((True, None, False, None), (False, None, True, None), (True, "match", True, "found")):
            with self.assertRaises(ValueError):
                _decide(*arguments)

    def test_content_status_boundaries(self):
        self.assertEqual(
            [_content_status(d, 6, 10, True) for d in (0, 6, 7, 9, 10, 32)],
            ["match", "match", "uncertain", "uncertain", "mismatch", "mismatch"],
        )
        self.assertEqual(_content_status(32, 6, 10, False), "unchecked")

    def test_false_positive_bound_and_thresholds(self):
        rng = random.Random(0)
        projections = [rng.gauss(0, 1) * rng.choice((1, 5, 25)) for _ in range(TAG_BITS)]
        scores = [_correlation([rng.getrandbits(1) for _ in range(TAG_BITS)], projections) for _ in range(20000)]
        for level in (2.0, 3.0, 4.0):
            self.assertLessEqual(sum(score >= level for score in scores) / len(scores), math.exp(-level * level / 2.0))
        self.assertLess(max(scores), _threshold(1e-6, 1))
        self.assertAlmostEqual(_threshold(1e-6, 2), math.sqrt(2.0 * math.log(2e6)))
        self.assertAlmostEqual(_correlation([0] * TAG_BITS, [2.0] * TAG_BITS), math.sqrt(TAG_BITS))
        self.assertAlmostEqual(_correlation([1] * TAG_BITS, [2.0] * TAG_BITS), -math.sqrt(TAG_BITS))
        self.assertEqual(_correlation([0] * TAG_BITS, [0.0] * TAG_BITS), 0.0)
        # Rounding residue is not a signal; a faint real signal is.
        self.assertEqual(_correlation([0] * TAG_BITS, [1e-9] * TAG_BITS), 0.0)
        self.assertAlmostEqual(_correlation([0] * TAG_BITS, [1e-3] * TAG_BITS), math.sqrt(TAG_BITS))
        # The guard is on the energy sqrt(sum p^2) at 1e-6: 9.8e-7 is below it, 1.02e-6 above.
        self.assertEqual(_correlation([0] * TAG_BITS, [8.7e-8] * TAG_BITS), 0.0)
        self.assertAlmostEqual(_correlation([0] * TAG_BITS, [9.0e-8] * TAG_BITS), math.sqrt(TAG_BITS))
        # The strictest accepted target with the largest roster is still attainable.
        self.assertLess(_threshold(1e-20, 4 * 1_000_000), math.sqrt(TAG_BITS))

    def test_helper_code_corrects_soft_errors_and_flags_failures(self):
        code = 0xC0FFEE42
        soft = [-1.0 if chip else 1.0 for chip in _helper_encode(code)]
        self.assertEqual((len(soft), _helper_decode(soft)), (HELPER_CHIPS, (code, True)))
        rng = random.Random(3)
        noisy = soft[:]
        for start in range(0, HELPER_CHIPS, 32):
            for position in rng.sample(range(32), 7):
                noisy[start + position] *= -1.0
        self.assertEqual(_helper_decode(noisy), (code, True))
        # A wrong bit in the code symbols is caught by the check, which sits in
        # the last symbol; an erased channel never passes it.
        for flipped in (2, 13, 31):
            wrong = [-1.0 if chip else 1.0 for chip in _helper_encode(code ^ (1 << flipped))]
            mixed = wrong[: HELPER_CHIPS - 32] + soft[HELPER_CHIPS - 32 :]
            self.assertEqual(_helper_decode(mixed), (code ^ (1 << flipped), False), flipped)
        self.assertEqual(_helper_decode([0.0] * HELPER_CHIPS), (0, False))
        # Residue far below any mark is an erasure; a faint consistent signal decodes.
        self.assertEqual(_helper_decode([1e-9] * HELPER_CHIPS), (0, False))
        self.assertEqual(_helper_decode([1e-5] * HELPER_CHIPS), (0, True))
        self.assertEqual(_helper_decode([1e-9] * 32 + soft[32:])[1], False)
        # The erasure threshold is 1e-6 on the largest transform value: 32 chips of 3.0e-8 stay below, 3.3e-8 pass.
        self.assertEqual(_helper_decode([3.0e-8] * HELPER_CHIPS), (0, False))
        self.assertEqual(_helper_decode([3.3e-8] * HELPER_CHIPS), (0, True))

        # Two transform values that differ only by rounding are a tie, and the lower index wins.
        def symbol(first, second):
            return [first * (-1.0 if bin(5 & chip).count("1") & 1 else 1.0) + second * (-1.0 if bin(9 & chip).count("1") & 1 else 1.0) for chip in range(32)]

        self.assertEqual(_helper_decode(symbol(0.3, 0.3 * (1.0 + 1e-12)) + soft[32:])[0], 0x14FFEE42)
        self.assertEqual(_helper_decode(symbol(0.3, 0.3001) + soft[32:])[0], 0x24FFEE42)
        # The relative window is 1e-9 of the largest value ...
        self.assertEqual(_helper_decode(symbol(0.3, 0.3 * (1.0 + 5e-10)) + soft[32:])[0], 0x14FFEE42)
        self.assertEqual(_helper_decode(symbol(0.3, 0.3 * (1.0 + 2e-9)) + soft[32:])[0], 0x24FFEE42)
        # ... and never narrower than 1e-9 absolute, which is what decides on a near-flat image.
        self.assertEqual(_helper_decode(symbol(1e-4, 1e-4 + 1e-11) + soft[32:])[0], 0x14FFEE42)
        self.assertEqual(_helper_decode(symbol(1e-4, 1e-4 + 1e-10) + soft[32:])[0], 0x24FFEE42)


class EmbedDetectTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = scene(1)
        cls.other = scene(2)
        cls.marked, cls.report = embed_with_report(cls.source, OWNER, KEY, KEYED_PROFILE)
        # The same properties are checked for other keys and another scene.
        cls.cases = [(KEY, cls.source, cls.other, cls.marked)]
        for key, seed in ((KEYS[1], 11), (KEYS[2], 21)):
            source = scene(seed)
            cls.cases.append((key, source, scene(seed + 1), embed(source, OWNER, key, KEYED_PROFILE)))

    def check(self, image, owner=OWNER, key=KEY, profile=KEYED_PROFILE, **options):
        return detect(image, owner, key, profile, **options)

    # -- clean operation -------------------------------------------------

    def test_round_trip_finds_both_keys_within_the_quality_budget(self):
        for key, source, _other, marked in self.cases:
            result = self.check(marked, key=key)
            self.assertEqual((result["outcome"], result["proposal_state"]), ("both_match", "authentic"), key)
            self.assertTrue(result["present"] and result["watermark_found"])
            for channel in ("semantic", "instance"):
                self.assertGreater(result[channel]["score"], result[channel]["threshold"] + 3.0, result)
                self.assertLessEqual(result[channel]["code_distance"], 1)
                self.assertEqual(result[channel]["content_status"], "match")
                self.assertLess(result[channel]["log10_false_positive_bound"], -12.0)
                # A decoded code equal to the recomputed one is not a second candidate.
                if result[channel]["code_distance"] == 0:
                    self.assertEqual(result[channel]["candidates"], 1)
                    self.assertAlmostEqual(result[channel]["threshold"], _threshold(1e-6, 1))
            self.assertLess(abs(psnr(source, marked) - 42.0), 0.25)

    def test_report_and_result_fields(self):
        result, report = self.check(self.marked), self.report
        self.assertTrue(report["verified"])
        self.assertEqual((report["revision"], result["revision"], result["version"]), (2, 2, 4))
        self.assertEqual((result["height"], result["width"]), (256, 256))
        self.assertEqual(result["detector_config_id"], detector_config_id(KEYED_PROFILE))
        self.assertEqual(report["detector_config_id"], result["detector_config_id"])
        self.assertEqual((result["decision_id"], report["decision_id"]), (decision_id(KEYED_PROFILE),) * 2)
        self.assertEqual(report["embedding"], KEYED_PROFILE["embedding"])
        self.assertEqual((result["embedding_domain"], result["owner_id"], result["owners_tested"]), ("image", OWNER, 1))
        self.assertEqual(result["candidates_tested"], result["semantic"]["candidates"] + result["instance"]["candidates"])
        self.assertAlmostEqual(report["psnr_db"], psnr(self.source, self.marked))
        self.assertAlmostEqual(report["mse"], 255.0**2 / 10 ** (report["psnr_db"] / 10))
        self.assertEqual((report["clipped_fraction"], report["verification_features"]), (0.0, "recomputed"))
        self.assertEqual((report["semantic_code"], report["perceptual_hash"]), (result["semantic_code"], result["perceptual_hash"]))
        timing = result["timing_ms"]
        self.assertEqual(set(timing), {"setup", "transform", "features", "scoring", "total"})
        self.assertTrue(all(value > 0.0 for value in timing.values()))
        self.assertAlmostEqual(sum(value for name, value in timing.items() if name != "total"), timing["total"], places=6)
        # No key material, and no cheap key fingerprint, leaves the detector.
        self.assertNotIn(KEY, repr(result) + repr(report))
        self.assertNotIn("key_fingerprint", result)

    def test_output_is_deterministic_and_byte_valued(self):
        self.assertEqual(self.marked, embed(self.source, OWNER, KEY, KEYED_PROFILE))
        self.assertTrue(all(value == math.floor(value) and 0 <= value <= 255 for row in self.marked for value in row))
        # A float-valued host with a remainder strip is saved as whole bytes everywhere.
        host = [[value + 0.37 for value in row] for row in scene(5, 203, 331, texture=6.0)]
        marked = embed(host, OWNER, KEY, KEYED_PROFILE)
        self.assertTrue(all(value == math.floor(value) for row in marked for value in row))
        self.assertEqual([row[328:] for row in marked], [[math.floor(value + 0.5) for value in row[328:]] for row in host])
        self.assertEqual(marked[200:], [[math.floor(value + 0.5) for value in row] for row in host[200:]])

    def test_wrong_owner_wrong_key_and_unmarked_images_are_negative(self):
        for key, source, other, marked in self.cases:
            cases = (
                self.check(marked, owner="owner-beta", key=key),
                self.check(marked, key="a-different-secret-key"),
                self.check(source, key=key),
                self.check(other, key=key),
            )
            for result in cases:
                self.assertEqual((result["outcome"], result["proposal_state"]), ("neither_match", "not_detected"), result)
                self.assertFalse(result["watermark_found"] or result["present"])
                self.assertLess(result["semantic"]["score"], result["semantic"]["threshold"] - 1.0)
                self.assertLess(result["instance"]["score"], result["instance"]["threshold"] - 1.0)
                self.assertIsNone(result["semantic"]["candidate"])

    def test_public_derived_profile_is_the_default_and_never_mixes_with_the_keyed_one(self):
        self.assertEqual(DEFAULT_PROFILE["security"], "public-derived")
        marked = embed(self.source, OWNER)
        self.assertEqual(detect(marked, OWNER)["outcome"], "both_match")
        self.assertEqual(detect(marked, OWNER)["security"], "public-derived")
        self.assertEqual(detect(marked, "owner-beta")["outcome"], "neither_match")
        self.assertEqual(self.check(marked)["outcome"], "neither_match")
        self.assertEqual(detect(self.marked, OWNER)["outcome"], "neither_match")
        # The public profile behaves the same way against a transplant and noise.
        self.assertEqual(detect(replace_band(self.other, marked, BAND), OWNER)["outcome"], "content_mismatch")
        self.assertEqual(detect(add_noise(marked, 5.0), OWNER)["outcome"], "both_match")
        with self.assertRaises(ValueError):
            embed(self.source, OWNER, KEY)
        with self.assertRaises(ValueError):
            detect(self.marked, OWNER, profile=KEYED_PROFILE)

    def test_unmarked_scores_follow_the_stated_null(self):
        # 12 images x 5 owners: no mark, so each score is the largest of two
        # (semantic) or four (instance) null correlations.
        owners = [f"owner-{index}" for index in range(5)]
        semantic, instance = [], []
        for seed in range(20, 32):
            image = scene(seed, 160, 160)
            for owner in owners:
                result = self.check(image, owner=owner)
                self.assertEqual(result["outcome"], "neither_match")
                self.assertEqual((result["semantic"]["candidates"], result["instance"]["candidates"]), (2, 4))
                semantic.append(result["semantic"]["score"])
                instance.append(result["instance"]["score"])
        # Expected maxima of 2 and 4 standard normals: 0.56 and 1.03.
        self.assertLess(abs(statistics.fmean(semantic) - 0.56), 0.4)
        self.assertLess(abs(statistics.fmean(instance) - 1.03), 0.4)
        self.assertLess(max(semantic + instance), 4.5)

    def test_featureless_suspect_image_is_a_negative_not_an_error(self):
        for image in ([[127.0] * 160 for _ in range(160)], [[float(64 + 128 * ((x + y) % 2)) for x in range(160)] for y in range(160)]):
            result = self.check(image)
            self.assertEqual(result["outcome"], "neither_match")
            self.assertEqual(result["semantic_code"], "00000000")
            with self.assertRaises(ValueError):
                embed(image, OWNER, KEY, KEYED_PROFILE)
        # A flat image has no band energy: both scores are zero, not a ratio of rounding residues.
        for level in (127.0, 255.0):
            result = self.check([[level] * 160 for _ in range(160)])
            self.assertEqual((result["semantic"]["score"], result["instance"]["score"]), (0.0, 0.0), level)
            self.assertEqual((result["semantic"]["candidates"], result["instance"]["candidates"]), (1, 1), level)
            self.assertFalse(result["semantic"]["helper_check_ok"] or result["instance"]["helper_check_ok"])

    def test_odd_sizes_and_plain_hosts_verify_and_stay_stable_under_mild_noise(self):
        hosts = {"odd size": scene(5, 203, 331), **plain_hosts()}
        for name, host in hosts.items():
            marked, report = embed_with_report(host, OWNER, KEY, KEYED_PROFILE)
            self.assertTrue(report["verified"], name)
            self.assertLess(abs(report["psnr_db"] - 42.0), 0.4, name)
            self.assertEqual(self.check(host)["outcome"], "neither_match", name)
            self.assertEqual(self.check(marked, owner="owner-beta")["outcome"], "neither_match", name)
            # A hash that reads noise-level detail would flag these genuine images.
            for seed in range(3):
                self.assertEqual(self.check(add_noise(marked, 2.0, seed))["outcome"], "both_match", (name, seed))
        odd = embed(hosts["odd size"], OWNER, KEY, KEYED_PROFILE)
        self.assertEqual([row[328:] for row in odd], [row[328:] for row in hosts["odd size"]])
        self.assertEqual(odd[200:], hosts["odd size"][200:])

    # -- robustness (T1-style processing) --------------------------------

    def test_survives_noise_gain_blur_and_requantisation(self):
        attacks = {
            "noise sigma 5": lambda image: add_noise(image, 5.0),
            "contrast 0.8": lambda image: scale(image, 0.8),
            "contrast 1.1 plus 10": lambda image: scale(image, 1.1, 10.0),
            "3x3 box blur": box_blur,
            "coefficient quantisation step 12": lambda image: requantise(image, 12.0),
        }
        for key, _source, _other, marked in self.cases:
            for name, attack in attacks.items():
                attacked = attack(marked)
                self.assertEqual(self.check(attacked, key=key)["outcome"], "both_match", (name, key))
                self.assertEqual(self.check(attacked, owner="owner-beta", key=key)["outcome"], "neither_match", name)

    def test_heavy_noise_degrades_to_undecided_and_keeps_both_keys(self):
        # At sigma 10 and 20 the keys are still found.  The hash may move into
        # the undecided zone; over these keys and seeds it is never a mismatch.
        outcomes = []
        for key, _source, _other, marked in self.cases:
            for sigma, seed in ((10.0, 9), (10.0, 3), (20.0, 9)):
                result = self.check(add_noise(marked, sigma, seed), key=key)
                self.assertTrue(result["semantic"]["found"] and result["instance"]["found"], (key, sigma, seed))
                self.assertIn(result["outcome"], ("both_match", "content_uncertain"), (key, sigma, seed))
                outcomes.append(result["outcome"])
        self.assertGreaterEqual(outcomes.count("both_match"), 5)

    def test_tolerates_distortions_that_defeat_the_v3_candidate(self):
        marked_v3 = [[clamp(value) for value in row] for row in v3.embed(self.source, OWNER, KEY)]
        self.assertTrue(v3.detect(marked_v3, OWNER, KEY)["present"])
        self.assertGreater(psnr(self.source, marked_v3), psnr(self.source, self.marked))
        for attack in (lambda image: add_noise(image, 3.0), lambda image: scale(image, 0.8)):
            self.assertFalse(v3.detect(attack(marked_v3), OWNER, KEY)["present"])
            self.assertEqual(self.check(attack(self.marked))["outcome"], "both_match")

    # -- transfer of a mark to other content ------------------------------

    def test_transplanted_mark_is_found_and_reported_as_bound_to_other_content(self):
        for key, _source, other, marked in self.cases:
            forged = replace_band(other, marked, BAND)
            result = self.check(forged, key=key)
            self.assertEqual((result["outcome"], result["proposal_state"]), ("content_mismatch", "copy_paste"), result)
            self.assertFalse(result["present"])
            self.assertTrue(result["watermark_found"])
            self.assertEqual(result["semantic"]["candidate"], "decoded")
            self.assertEqual(result["semantic"]["content_status"], "mismatch")
            # Each content check rejects on its own; only with both off is the transplant accepted.
            for mode in ("semantic_only", "perceptual_only"):
                self.assertEqual(self.check(forged, key=key, binding_mode=mode)["outcome"], "content_mismatch", mode)
            accepted = self.check(forged, key=key, binding_mode="none")
            self.assertEqual(accepted["outcome"], "both_match")
            self.assertEqual(accepted["instance"]["content_status"], "unchecked")

    def test_one_transplanted_channel_is_never_accepted(self):
        for key, _source, other, marked in self.cases:
            # The semantic channel alone carries its own code and is found and flagged.
            semantic = self.check(replace_band(other, marked, SEMANTIC_BAND), key=key)
            self.assertEqual(semantic["outcome"], "content_mismatch")
            self.assertEqual((semantic["semantic"]["found"], semantic["instance"]["found"]), (True, False))
            self.assertEqual(semantic["semantic"]["content_status"], "mismatch")
            # The instance key also binds the semantic code, which travels in the
            # other channel, so the instance channel alone verifies nothing.
            self.assertEqual(self.check(replace_band(other, marked, INSTANCE_BAND), key=key)["outcome"], "neither_match")

    def test_residual_and_patch_copies_onto_another_image_are_not_authentic(self):
        for key, source, other, marked in self.cases:
            patch = [row[:] for row in other]
            for y in range(64, 192):
                patch[y][64:192] = marked[y][64:192]
            for name, forged in (("residual", residual_copy(other, marked, source)), ("quarter patch", patch)):
                result = self.check(forged, key=key)
                self.assertIn(result["outcome"], ("content_mismatch", "neither_match"), (name, key))

    def test_forcing_the_content_codes_requires_importing_the_donor_content(self):
        # With the donor's block means the semantic proxy matches but the hash,
        # which also reads local gradients, does not.  Importing those too is
        # accepted, and by then the forgery no longer resembles the recipient.
        for key, _source, other, marked in self.cases:
            means_only = self.check(replace_band(import_block_means(other, marked, 1.0), marked, BAND), key=key)
            self.assertEqual(means_only["semantic"]["content_status"], "match")
            self.assertEqual(means_only["instance"]["content_status"], "mismatch")
            self.assertEqual(means_only["outcome"], "content_mismatch")
            everything = replace_band(import_block_means(other, marked, 1.0), marked, BAND + HASH_POSITIONS)
            self.assertEqual(self.check(everything, key=key)["outcome"], "both_match")
            self.assertLess(psnr(other, everything), 22.0)

    def test_content_code_drift_is_tolerated_without_avalanche(self):
        # Coarse edits move code bits one at a time.  The keys keep verifying
        # through the codes carried in the mark, and the distance alone decides.
        seen, small_drift = set(), 0
        for key, _source, other, marked in self.cases:
            for weight in (0.1, 0.2, 0.3, 0.5, 1.0):
                result = self.check(import_block_means(marked, other, weight), key=key)
                self.assertGreater(result["semantic"]["score"], result["semantic"]["threshold"] + 3.0)
                distance = result["semantic"]["code_distance"]
                self.assertEqual(result["semantic"]["content_status"], _content_status(distance, RADIUS, FAR, True))
                if distance > 0:
                    self.assertEqual(result["semantic"]["candidate"], "decoded")
                    # The instance key may only use the semantic code that verified.
                    self.assertLessEqual(result["instance"]["candidates"], 2)
                small_drift += result["outcome"] == "both_match" and distance > 0
                seen.add((result["outcome"], result["semantic"]["content_status"]))
        # A drift of a few bits is accepted; a replaced layout is a mismatch.
        self.assertGreaterEqual(small_drift, 3)
        self.assertIn(("content_mismatch", "mismatch"), seen)

    def test_images_of_one_composition(self):
        # Same structure, different texture.  The layout proxy cannot tell them
        # apart (a semantic collision).  The hash separates most pairs but not
        # all, and a transplant is authentic exactly when the hashes are close.
        marked = embed(scene(7, detail_seed=70), OWNER, KEY, KEYED_PROFILE)
        outcomes = []
        for seed in range(71, 79):
            recipient = scene(7, detail_seed=seed)
            forged = replace_band(recipient, marked, BAND)
            result = self.check(forged)
            self.assertTrue(result["semantic"]["found"] and result["instance"]["found"])
            self.assertEqual(result["semantic"]["content_status"], "match")
            distance = result["instance"]["code_distance"]
            expected = {"match": "both_match", "uncertain": "content_uncertain", "mismatch": "content_mismatch"}
            self.assertEqual(result["outcome"], expected[_content_status(distance, RADIUS, FAR, True)])
            # Without the perceptual check every one of these forgeries is accepted.
            self.assertEqual(self.check(forged, binding_mode="semantic_only")["outcome"], "both_match")
            self.assertGreater(psnr(recipient, forged), 30.0)
            outcomes.append(result["outcome"])
        self.assertGreaterEqual(outcomes.count("content_mismatch"), 4)
        self.assertLessEqual(outcomes.count("both_match"), 1)

    def test_known_limit_semantic_key_alone_transfers_within_a_composition(self):
        # The semantic key binds the semantic code and the owner, nothing else.
        # Copying only the semantic band onto another image of the composition
        # therefore reads as the semantic key alone.  This is a limit of the
        # proposal's decision table, pinned here so that it stays visible.
        marked = embed(scene(7, detail_seed=70), OWNER, KEY, KEYED_PROFILE)
        results = [self.check(replace_band(scene(7, detail_seed=seed), marked, SEMANTIC_BAND)) for seed in (71, 72, 73)]
        self.assertEqual([result["outcome"] for result in results], ["semantic_only"] * 3)
        self.assertEqual({result["proposal_state"] for result in results}, {"regenerated"})

    def test_known_limit_informed_transplant_within_a_composition_is_accepted(self):
        # The content codes are functions of the pixels, so an attacker who also
        # copies the two coefficients the hash reads makes the recipient's hash
        # equal the donor's.  No key is needed.  Within one composition the
        # result still resembles the recipient, and the detector accepts it.
        marked = embed(scene(7, detail_seed=70), OWNER, KEY, KEYED_PROFILE)
        for seed in (71, 72, 73):
            recipient = scene(7, detail_seed=seed)
            forged = replace_band(recipient, marked, BAND + HASH_POSITIONS)
            self.assertEqual(self.check(forged)["outcome"], "both_match", seed)
            self.assertGreater(psnr(recipient, forged), 27.0)
            self.assertEqual(self.check(recipient)["outcome"], "neither_match")

    def test_perceptual_hash_separates_instances_that_share_a_semantic_vector(self):
        external = profile_with(semantic_source="external:test-encoder")
        rng = random.Random(4)
        subject = [rng.gauss(0, 1) for _ in range(512)]
        unrelated = [rng.gauss(0, 1) for _ in range(512)]
        marked, report = embed_with_report(self.source, OWNER, KEY, external, subject)
        self.assertEqual(report["verification_features"], "source-features-supplied-by-caller")
        self.assertEqual(detect(marked, OWNER, KEY, external, subject)["outcome"], "both_match")
        # A different photograph of the same subject: same semantic vector, different instance.
        forged = replace_band(self.other, marked, BAND)
        combined = detect(forged, OWNER, KEY, external, subject)
        self.assertEqual((combined["outcome"], combined["proposal_state"]), ("content_mismatch", "copy_paste"), combined)
        self.assertEqual(combined["semantic"]["content_status"], "match")
        self.assertEqual(combined["instance"]["content_status"], "mismatch")
        self.assertEqual(detect(forged, OWNER, KEY, external, subject, binding_mode="semantic_only")["outcome"], "both_match")
        self.assertEqual(detect(forged, OWNER, KEY, external, subject, binding_mode="perceptual_only")["outcome"], "content_mismatch")
        # The untouched marked image presented with unrelated semantics fails the semantic check.
        self.assertEqual(detect(marked, OWNER, KEY, external, unrelated)["outcome"], "content_mismatch")
        self.assertEqual(detect(marked, OWNER, KEY, external, unrelated, binding_mode="perceptual_only")["outcome"], "both_match")
        with self.assertRaises(ValueError):
            detect(marked, OWNER, KEY, external)
        with self.assertRaises(ValueError):
            self.check(self.marked, semantic_features=subject)

    def test_losing_one_band_leaves_the_other_key_alone(self):
        for key, source, _other, marked in self.cases:
            without_instance = self.check(replace_band(marked, source, INSTANCE_BAND), key=key)
            self.assertEqual((without_instance["outcome"], without_instance["proposal_state"]), ("semantic_only", "regenerated"))
            self.assertFalse(without_instance["instance"]["found"])
            self.assertIsNone(without_instance["instance"]["content_status"])
            without_semantic = self.check(replace_band(marked, source, SEMANTIC_BAND), key=key)
            self.assertEqual((without_semantic["outcome"], without_semantic["proposal_state"]), ("instance_only", "unclassified"))
            self.assertFalse(without_semantic["present"])
            self.assertTrue(without_semantic["watermark_found"])

    # -- components -------------------------------------------------------

    def test_perceptual_hash_is_keyed_stable_and_instance_specific(self):
        for key, source, other, marked in self.cases:
            base = perceptual_hash(source, key, KEYED_PROFILE)
            self.assertLessEqual(bits(perceptual_hash(marked, key, KEYED_PROFILE), base), 1)
            self.assertLessEqual(bits(perceptual_hash(add_noise(marked, 5.0), key, KEYED_PROFILE), base), RADIUS)
            self.assertLessEqual(bits(perceptual_hash(box_blur(marked), key, KEYED_PROFILE), base), 4)
            self.assertGreaterEqual(bits(perceptual_hash(other, key, KEYED_PROFILE), base), FAR)
        base = perceptual_hash(self.source, KEY, KEYED_PROFILE)
        # Without the key the hyperplanes, and therefore the code, are different.
        self.assertGreaterEqual(bits(perceptual_hash(self.source, KEYS[1], KEYED_PROFILE), base), 6)
        self.assertGreaterEqual(bits(perceptual_hash(self.source), base), 6)
        self.assertEqual(perceptual_hash([[90.0] * 160 for _ in range(160)]), 0)
        self.assertLess(base, 1 << CODE_BITS)

    def test_roster_identification_corrects_both_thresholds(self):
        roster = ["owner-beta", OWNER, "owner-gamma", "owner-delta"]
        result = identify(self.marked, roster, KEY, KEYED_PROFILE)
        self.assertEqual((result["roster_size"], result["found"], result["both_match"]), (4, [OWNER], [OWNER]))
        self.assertEqual(len(result["roster_sha256"]), 64)
        self.assertNotEqual(result["roster_sha256"], identify(self.marked, roster[:3], KEY, KEYED_PROFILE)["roster_sha256"])
        single, listed = self.check(self.marked), result["results"][OWNER]
        self.assertEqual(listed["owners_tested"], 4)
        for channel in ("semantic", "instance"):
            self.assertAlmostEqual(single[channel]["threshold"], _threshold(1e-6, single[channel]["candidates"]))
            self.assertAlmostEqual(listed[channel]["threshold"], _threshold(1e-6, 4 * listed[channel]["candidates"]))
            self.assertGreater(listed[channel]["log10_false_positive_bound"], single[channel]["log10_false_positive_bound"])
        # An unmarked image tries two semantic and four instance patterns per owner.
        unmarked = self.check(self.source, roster_size=4)
        self.assertAlmostEqual(unmarked["instance"]["threshold"], _threshold(1e-6, 16))
        self.assertEqual(identify(self.source, roster, KEY, KEYED_PROFILE)["found"], [])
        # A semantic-band transplant is found for the owner but is not a both-key match.
        donor = embed(scene(7, detail_seed=70), OWNER, KEY, KEYED_PROFILE)
        partial = identify(replace_band(scene(7, detail_seed=71), donor, SEMANTIC_BAND), roster, KEY, KEYED_PROFILE)
        self.assertEqual((partial["found"], partial["both_match"]), ([OWNER], []))
        for bad in ([OWNER, OWNER], [], "owner-alpha", [OWNER, 7]):
            with self.assertRaises((ValueError, TypeError), msg=repr(bad)):
                identify(self.marked, bad, KEY, KEYED_PROFILE)

    def test_owner_identifiers_are_compared_in_normal_form(self):
        composed, decomposed = "Zoë", "Zoë"
        marked = embed(self.source, decomposed, KEY, KEYED_PROFILE)
        self.assertEqual(self.check(marked, owner=composed)["outcome"], "both_match")
        self.assertEqual(self.check(marked, owner=decomposed)["owner_id"], composed)
        with self.assertRaises(ValueError):
            identify(marked, [composed, decomposed], KEY, KEYED_PROFILE)

    def test_projection_targets_describe_what_the_detector_reads(self):
        contract = projection_targets(self.source, OWNER, KEY, KEYED_PROFILE)
        self.assertEqual(contract["detector_config_id"], self.report["detector_config_id"])
        self.assertEqual((contract["semantic_code"], contract["perceptual_hash"]), (self.report["semantic_code"], self.report["perceptual_hash"]))
        for channel, band in zip(contract["channels"], (SEMANTIC_BAND, INSTANCE_BAND)):
            self.assertEqual(len(channel["target"]), CHANNEL_BITS)
            for image, expected in ((self.source, channel["host"]), (self.marked, channel["target"])):
                coefficients = block_coefficients(image, band)[1]
                reached = [0.0] * CHANNEL_BITS
                for block, u, v, bit, sign, norm in channel["slots"]:
                    reached[bit] += sign * coefficients[block][band.index((u, v))] / norm
                # Exact for the host; byte rounding leaves a residual far below the amplitude.
                tolerance = 1e-9 if image is self.source else 2.0
                self.assertLess(max(abs(a - b) for a, b in zip(reached, expected)), tolerance, channel["channel"])

    # -- embedding budget and failure handling -------------------------------

    def test_embedding_parameters_do_what_the_profile_says(self):
        base = self.report
        stronger = embed_with_report(self.source, OWNER, KEY, profile_with(embedding={"target_psnr_db": 38.0}))[1]
        self.assertLess(abs(stronger["psnr_db"] - 38.0), 0.25)
        self.assertGreater(stronger["semantic_channel"]["amplitude"], base["semantic_channel"]["amplitude"] * 1.4)
        shifted = embed_with_report(self.source, OWNER, KEY, profile_with(embedding={"semantic_energy_share": 0.8}))[1]
        self.assertGreater(shifted["semantic_channel"]["amplitude"], base["semantic_channel"]["amplitude"])
        self.assertLess(shifted["instance_channel"]["amplitude"], base["instance_channel"]["amplitude"])
        noisy = embed_with_report(self.source, OWNER, KEY, profile_with(embedding={"design_noise_std": 40.0}))[1]
        self.assertLess(noisy["semantic_channel"]["host_rejection"], base["semantic_channel"]["host_rejection"])
        # The budget is met on average over the key pattern; one key and owner scatter around it.
        rounded, unrounded = [], []
        for key in KEYS:
            for owner in (OWNER, "owner-beta"):
                rounded.append(embed_with_report(self.source, owner, key, KEYED_PROFILE)[1])
                unrounded.append(embed_with_report(self.source, owner, key, KEYED_PROFILE, quantize=False)[1])
        for reports in (rounded, unrounded):
            self.assertLess(abs(statistics.fmean(report["psnr_db"] for report in reports) - 42.0), 0.1)
            self.assertTrue(all(abs(report["psnr_db"] - 42.0) < 0.4 for report in reports))
        self.assertTrue(all(report["quantized"] and report["rounding_reserved"] for report in rounded))
        self.assertFalse(any(report["quantized"] or report["rounding_reserved"] for report in unrounded))
        # Byte rounding is paid from the budget: the planned signal is smaller when the output is rounded.
        for with_rounding, without in zip(rounded, unrounded):
            self.assertLess(with_rounding["semantic_channel"]["amplitude"], without["semantic_channel"]["amplitude"])
        # An explicit choice overrides the default in both directions.
        spent = embed_with_report(self.source, OWNER, KEY, KEYED_PROFILE, quantize=True, reserve_rounding=False, strict=False)[1]
        self.assertTrue(spent["quantized"] and not spent["rounding_reserved"])
        self.assertEqual(spent["semantic_channel"]["amplitude"], unrounded[0]["semantic_channel"]["amplitude"])

    def test_host_dominated_source_fails_loudly_instead_of_returning_a_weak_mark(self):
        with self.assertRaises(EmbeddingError) as caught:
            embed(sawtooth(), OWNER, KEY, KEYED_PROFILE)
        self.assertFalse(caught.exception.report["verified"])
        self.assertGreater(caught.exception.report["semantic_channel"]["host_rms"], 60.0)
        _, report = embed_with_report(sawtooth(), OWNER, KEY, KEYED_PROFILE, strict=False)
        self.assertFalse(report["verified"])
        self.assertNotEqual(report["verification"]["outcome"], "both_match")

    def test_saturated_regions_are_clipped_not_rejected(self):
        bright = [[clamp(value + 120.0) if x < 96 else value for x, value in enumerate(row)] for row in self.source]
        marked, report = embed_with_report(bright, OWNER, KEY, KEYED_PROFILE)
        self.assertGreater(report["clipped_fraction"], 0.02)
        self.assertEqual(self.check(marked)["outcome"], "both_match")
        # Further passes recover part of what clipping removed.
        once = embed_with_report(bright, OWNER, KEY, profile_with(embedding={"passes": 1}))[0]
        self.assertGreater(self.check(marked)["semantic"]["score"], self.check(once)["semantic"]["score"])

    def test_colour_wrapper_round_trip_and_failures(self):
        rgb = [[(clamp(value + 12), value, clamp(value - 9)) for value in row[:160]] for row in self.source[:160]]
        marked, report = embed_rgb(rgb, OWNER, KEY, KEYED_PROFILE)
        self.assertTrue(report["verified"])
        self.assertLess(abs(report["psnr_db"] - 42.0), 0.6)
        self.assertEqual((report["clipped_fraction"], report["quality_domain"]), (0.0, "luminance of the rounded RGB output"))
        # The colour path plans like the rounded luminance path, not like the unrounded one.
        luminance = luminance_from_rgb(rgb)
        planned = embed_with_report(luminance, OWNER, KEY, KEYED_PROFILE)[1]
        self.assertTrue(report["rounding_reserved"] and report["quantized"])
        self.assertEqual(report["semantic_channel"]["amplitude"], planned["semantic_channel"]["amplitude"])
        self.assertTrue(all(isinstance(channel, int) and 0 <= channel <= 255 for row in marked for pixel in row for channel in pixel))
        self.assertEqual(detect_rgb(marked, OWNER, KEY, KEYED_PROFILE)["outcome"], "both_match")
        self.assertEqual(detect_rgb(rgb, OWNER, KEY, KEYED_PROFILE)["outcome"], "neither_match")
        self.assertEqual(detect_rgb(marked, OWNER, KEY, KEYED_PROFILE, roster_size=8)["owners_tested"], 8)
        self.assertEqual(detect_rgb(marked, OWNER, KEY, KEYED_PROFILE, binding_mode="none")["binding_mode"], "none")
        with self.assertRaises(ValueError):
            detect_rgb(marked, OWNER, KEY, KEYED_PROFILE, expected_config_id="0" * 64)
        with self.assertRaises(ValueError):
            detect_rgb([[(300, 0, 0)] * 160 for _ in range(160)], OWNER, KEY, KEYED_PROFILE)
        # A saturated channel cannot carry its share of the change; the report says so.
        red = [[(255, green, 0) for _red, green, _blue in row] for row in rgb]
        marked_red, report_red = embed_rgb(red, OWNER, KEY, KEYED_PROFILE)
        self.assertGreater(report_red["clipped_fraction"], 0.1)
        self.assertEqual(detect_rgb(marked_red, OWNER, KEY, KEYED_PROFILE)["outcome"], "both_match")
        # Verification reads the saved RGB image.  Here the unrounded luminance would pass,
        # but with red and blue saturated the green channel alone carries too little.
        faint = profile_with(embedding={"target_psnr_db": 50.5})
        small = [[(255, green, 0) for _red, green, _blue in row] for row in rgb]
        unsaved = embed_with_report(luminance_from_rgb(small), OWNER, KEY, faint, quantize=False, strict=False, reserve_rounding=True)[1]
        self.assertTrue(unsaved["verified"])
        saved, report_small = embed_rgb(small, OWNER, KEY, faint, strict=False)
        self.assertFalse(report_small["verified"])
        self.assertNotEqual(detect_rgb(saved, OWNER, KEY, faint)["outcome"], "both_match")
        with self.assertRaises(EmbeddingError):
            embed_rgb(small, OWNER, KEY, faint)
        # A host that cannot be marked fails in the colour wrapper as it does in the luminance one.
        hopeless = [[(value, value, value) for value in row] for row in sawtooth()]
        with self.assertRaises(EmbeddingError):
            embed_rgb(hopeless, OWNER, KEY, KEYED_PROFILE)
        self.assertFalse(embed_rgb(hopeless, OWNER, KEY, KEYED_PROFILE, strict=False)[1]["verified"])

    # -- configuration -------------------------------------------------------

    def test_detector_and_decision_identity(self):
        base = detector_config_id(KEYED_PROFILE)
        self.assertEqual(base, detector_config_id(profile_with(embedding={"target_psnr_db": 38.0})))
        self.assertEqual(base, detector_config_id(profile_with(decision={"semantic_radius": 4})))
        self.assertNotEqual(decision_id(KEYED_PROFILE), decision_id(profile_with(decision={"semantic_radius": 4})))
        self.assertEqual(decision_id(KEYED_PROFILE), decision_id(profile_with(embedding={"target_psnr_db": 38.0})))
        self.assertNotEqual(base, detector_config_id(DEFAULT_PROFILE))
        self.assertNotEqual(base, detector_config_id(profile_with(minimum_side=168)))
        self.assertNotEqual(base, detector_config_id(profile_with(semantic_frequencies=[[1, 1], [0, 2], [2, 0], [1, 2], [2, 1]])))
        with self.assertRaises(ValueError):
            self.check(self.marked, expected_config_id=detector_config_id(DEFAULT_PROFILE))
        self.assertEqual(self.check(self.marked, expected_config_id=base)["outcome"], "both_match")
        # Separate distances for the two codes are applied to the right code.
        drifted = import_block_means(self.marked, self.other, 0.3)
        distance = self.check(drifted)["semantic"]["code_distance"]
        self.assertGreater(distance, 0)
        tight = profile_with(decision={"semantic_radius": distance - 1, "semantic_mismatch_distance": distance})
        self.assertEqual(self.check(drifted, profile=tight)["semantic"]["content_status"], "mismatch")
        tight_instance = profile_with(decision={"instance_radius": 0, "instance_mismatch_distance": 1})
        self.assertEqual(self.check(drifted, profile=tight_instance)["semantic"]["content_status"], "match")
        noisy = add_noise(self.marked, 10.0, 0)
        hash_distance = self.check(noisy)["instance"]["code_distance"]
        self.assertGreater(hash_distance, 0)
        self.assertEqual(self.check(noisy)["semantic"]["code_distance"], 0)
        tight_hash = profile_with(decision={"instance_radius": hash_distance - 1, "instance_mismatch_distance": hash_distance})
        self.assertEqual(self.check(noisy, profile=tight_hash)["instance"]["content_status"], "mismatch")
        tight_semantic = profile_with(decision={"semantic_radius": 0, "semantic_mismatch_distance": 1})
        self.assertEqual(self.check(noisy, profile=tight_semantic)["instance"]["content_status"], "match")

    def test_profile_validation(self):
        def changed(group=None, **fields):
            profile = validate_profile(DEFAULT_PROFILE)
            (profile[group] if group else profile).update(fields)
            return profile

        accepted = (
            changed("embedding", target_psnr_db=30),
            changed("embedding", target_psnr_db=60.0),
            changed("embedding", semantic_energy_share=0.05, design_noise_std=64, passes=8),
            changed("decision", false_positive_target=1e-20, semantic_radius=0, semantic_mismatch_distance=1),
            changed("decision", instance_radius=15, instance_mismatch_distance=16),
            changed(minimum_side=16384, semantic_source="external:openai-clip-vit-b32@d05afc4"),
        )
        for profile in accepted:
            validate_profile(profile)
        rejected = (
            {**DEFAULT_PROFILE, "unknown": 1},
            {key: value for key, value in DEFAULT_PROFILE.items() if key != "decision"},
            changed(schema_version="revised-watermark-v3"),
            changed(code_bits=32.0),
            changed(tag_bits=True),
            changed(security="none"),
            changed(semantic_source="clip"),
            changed(semantic_source="external:"),
            changed(semantic_source="external:clip vit"),
            changed(semantic_source="external:clip\n"),
            changed(semantic_source="external:" + "a" * 129),
            changed(minimum_side=True),
            changed(minimum_side=160.0),
            changed(minimum_side=159),
            changed(minimum_side=16385),
            changed(instance_frequencies=[[1, 1], [3, 0], [0, 3], [1, 3]]),
            changed(semantic_frequencies=[[0, 0], [1, 1], [0, 2], [2, 0]]),
            changed(instance_frequencies=[[0, 1], [3, 0], [0, 3], [1, 3]]),
            changed(semantic_frequencies=[[1, 1], [1, 1], [0, 2], [2, 0]]),
            changed(semantic_frequencies=[[1, 8], [1, 1], [0, 2], [2, 0]]),
            changed(semantic_frequencies=[[1.0, 1.0], [0, 2], [2, 0], [1, 2]]),
            changed(semantic_frequencies=[[1, 1], [0, 2], [2, 0]]),
            changed(semantic_frequencies=[]),
            changed("embedding", target_psnr_db=29.9),
            changed("embedding", target_psnr_db=60.1),
            changed("embedding", target_psnr_db=float("nan")),
            changed("embedding", target_psnr_db=True),
            changed("embedding", target_psnr_db=10**400),
            changed("embedding", semantic_energy_share=0.04),
            changed("embedding", semantic_energy_share=0.96),
            changed("embedding", design_noise_std=0),
            changed("embedding", design_noise_std=True),
            changed("embedding", semantic_energy_share=True),
            changed("embedding", design_noise_std=64.1),
            changed("embedding", passes=0),
            changed("embedding", passes=9),
            changed("embedding", passes=3.0),
            changed("embedding", passes=True),
            changed("embedding", extra=1),
            changed("decision", false_positive_target=0.5),
            changed("decision", false_positive_target=1e-21),
            changed("decision", false_positive_target=0),
            changed("decision", semantic_radius=10),
            changed("decision", instance_mismatch_distance=17),
            changed("decision", instance_radius=6.0),
            changed("decision", semantic_radius=-1),
            changed("decision", extra=1),
        )
        for profile in rejected:
            with self.assertRaises(ValueError, msg=repr(profile)[:200]):
                validate_profile(profile)

    def test_module_defaults_are_independent_and_profile_files_are_read_strictly(self):
        self.assertIsNot(DEFAULT_PROFILE["decision"], KEYED_PROFILE["decision"])
        self.assertIsNot(DEFAULT_PROFILE["embedding"], KEYED_PROFILE["embedding"])
        checked = validate_profile(KEYED_PROFILE)
        checked["decision"]["semantic_radius"] = 1
        checked["semantic_frequencies"].append([4, 4])
        self.assertEqual(KEYED_PROFILE["decision"]["semantic_radius"], 6)
        self.assertEqual(len(KEYED_PROFILE["semantic_frequencies"]), 6)
        strictest = profile_with(decision={"false_positive_target": 1e-20})
        self.assertEqual(embed_with_report(self.source, OWNER, KEY, strictest)[1]["verification"]["outcome"], "both_match")
        text = (CONFIGS / "revised-watermark-v4.example.json").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as folder:
            for name, broken in (
                ("repeat.json", text.replace('"security": "public-derived",', '"security": "hmac-keyed",\n  "security": "public-derived",')),
                ("nan.json", text.replace("42.0", "NaN")),
                ("infinity.json", text.replace("42.0", "Infinity")),
            ):
                path = Path(folder) / name
                path.write_text(broken, encoding="utf-8")
                with self.assertRaises(ValueError, msg=name):
                    load_profile(path)

    def test_example_profiles_and_schema_match_the_module(self):
        examples = {"revised-watermark-v4.example.json": DEFAULT_PROFILE, "revised-watermark-v4-keyed.example.json": KEYED_PROFILE}
        for name, expected in examples.items():
            self.assertEqual(load_profile(CONFIGS / name), validate_profile(expected))
        schema = json.loads((CONFIGS / "revised-watermark-v4.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(set(schema["required"]), set(DEFAULT_PROFILE))
        for group in ("embedding", "decision"):
            self.assertEqual(set(schema["properties"][group]["required"]), set(DEFAULT_PROFILE[group]))
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema is not installed")
        for name in examples:
            jsonschema.validate(json.loads((CONFIGS / name).read_text(encoding="utf-8")), schema)
        for broken in (
            {**DEFAULT_PROFILE, "unknown": 1},
            {**DEFAULT_PROFILE, "security": "none"},
            {**DEFAULT_PROFILE, "semantic_source": "external:clip vit"},
            {**DEFAULT_PROFILE, "semantic_frequencies": [[0, 1], [1, 1], [0, 2], [2, 0]]},
            {**DEFAULT_PROFILE, "decision": {**DEFAULT_PROFILE["decision"], "false_positive_target": 1e-30}},
            {**DEFAULT_PROFILE, "decision": {**DEFAULT_PROFILE["decision"], "extra": 1}},
        ):
            with self.assertRaises(jsonschema.ValidationError):
                jsonschema.validate(broken, schema)

    def test_malformed_inputs_are_rejected(self):
        spoiled = [row[:] for row in self.source]
        spoiled[10][10] = 300.0
        ragged = [row[:] for row in self.source]
        ragged[5] = ragged[5][:-1]
        for arguments in (
            ([[100.0 + (x % 7) for x in range(152)] for _ in range(152)], OWNER, KEY),
            (spoiled, OWNER, KEY),
            (ragged, OWNER, KEY),
            (self.source, "", KEY),
            (self.source, "x" * 257, KEY),
            (self.source, OWNER, "short"),
            (self.source, OWNER, "k" * 4097),
        ):
            with self.assertRaises(ValueError):
                embed(*arguments, KEYED_PROFILE)
            with self.assertRaises(ValueError):
                detect(*arguments, KEYED_PROFILE)
        for options in ({"binding_mode": "strict"}, {"roster_size": 0}, {"roster_size": 1_000_001}, {"roster_size": 2.0}, {"roster_size": True}):
            with self.assertRaises(ValueError, msg=options):
                self.check(self.marked, **options)
        with self.assertRaises(ValueError):
            layout_features([[100.0] * 8 for _ in range(4)])
        external = profile_with(semantic_source="external:test-encoder")
        for features in ("1234567890123456789012", [10**400] * 32, [0.0] * 32, [float("nan")] * 32, [1.0] * 8, [None] * 32):
            with self.assertRaises(ValueError, msg=repr(features)[:40]):
                detect(self.marked, OWNER, KEY, external, features)


if __name__ == "__main__":
    unittest.main()
