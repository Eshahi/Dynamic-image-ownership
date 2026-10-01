"""Synthetic engineering checks for the v4 reference codec.

Every image here is procedurally generated.  These tests show that the codec
does what its specification says; they are not evidence about real images,
real regeneration or real semantic features.
"""

import json
import math
import random
import statistics
import unittest
from pathlib import Path

from scripts import revised_watermark_v3 as v3
from scripts.revised_watermark_v4 import (
    CHANNEL_BITS,
    CODE_BITS,
    DEFAULT_PROFILE,
    HELPER_CHIPS,
    KEYED_PROFILE,
    TAG_BITS,
    EmbeddingError,
    _analyse,
    _correlation,
    _helper_decode,
    _helper_encode,
    _plane,
    _threshold,
    decision_id,
    detect,
    detect_rgb,
    detector_config_id,
    embed,
    embed_rgb,
    embed_with_report,
    identify,
    load_profile,
    perceptual_hash,
    projection_targets,
    psnr,
    validate_profile,
)


KEY = "local-test-key-20260930"
OWNER = "owner-alpha"
SIZE = 256
BAND = [(1, 1), (0, 2), (2, 0), (1, 2), (2, 1), (2, 2), (0, 3), (3, 0), (1, 3), (3, 1), (2, 3), (3, 2)]
INSTANCE_BAND = BAND[6:]
CONFIGS = Path(__file__).resolve().parents[1] / "configs"


def clamp(value):
    return float(min(255, max(0, math.floor(value + 0.5))))


def scene(seed, height=SIZE, width=SIZE, texture=12.0, detail_seed=None):
    """Synthetic photograph stand-in: smooth structure, mid-scale texture and sensor noise.

    ``detail_seed`` redraws the texture and noise while keeping the structure,
    which gives two different images of one composition.
    """
    rng = random.Random(seed)
    waves = [(rng.uniform(0.01, 0.09), rng.uniform(0.01, 0.09), rng.uniform(0, 6.28), rng.uniform(8, 28)) for _ in range(8)]
    if detail_seed is not None:
        rng = random.Random(detail_seed)
    coarse = [[rng.gauss(0, 1) for _ in range(width // 4 + 2)] for _ in range(height // 4 + 2)]
    image = []
    for y in range(height):
        row = []
        y0, ty = y // 4, (y % 4) / 4.0
        for x in range(width):
            x0, tx = x // 4, (x % 4) / 4.0
            grain = (
                coarse[y0][x0] * (1 - ty) * (1 - tx)
                + coarse[y0][x0 + 1] * (1 - ty) * tx
                + coarse[y0 + 1][x0] * ty * (1 - tx)
                + coarse[y0 + 1][x0 + 1] * ty * tx
            )
            value = 128.0 + sum(a * math.cos(fx * x + fy * y + phase) for fx, fy, phase, a in waves)
            row.append(clamp(value + texture * grain + rng.gauss(0, 2.0)))
        image.append(row)
    return image


def sawtooth(size=160):
    return [[float((x * 17 + y * 29 + ((x * y) % 37)) % 256) for x in range(size)] for y in range(size)]


def add_noise(image, sigma, seed=9):
    rng = random.Random(seed)
    return [[clamp(value + rng.gauss(0, sigma)) for value in row] for row in image]


def scale(image, gain, offset=0.0):
    return [[clamp(value * gain + offset) for value in row] for row in image]


def box_blur(image):
    height, width = len(image), len(image[0])
    output = []
    for y in range(height):
        rows = [image[min(height - 1, max(0, y + dy))] for dy in (-1, 0, 1)]
        output.append([clamp(sum(row[min(width - 1, max(0, x + dx))] for row in rows for dx in (-1, 0, 1)) / 9.0) for x in range(width)])
    return output


def requantise(image, step):
    """JPEG-like loss: uniform quantisation of every 8x8 block-DCT coefficient."""
    planes = [_plane(u, v) for u in range(8) for v in range(8)]
    output = [row[:] for row in image]
    for by in range(len(image) // 8):
        for bx in range(len(image[0]) // 8):
            block = [image[by * 8 + y][bx * 8 + x] for y in range(8) for x in range(8)]
            rebuilt = [0.0] * 64
            for plane in planes:
                level = round(sum(a * b for a, b in zip(block, plane)) / step) * step
                if level:
                    rebuilt = [value + level * basis for value, basis in zip(rebuilt, plane)]
            for y in range(8):
                for x in range(8):
                    output[by * 8 + y][bx * 8 + x] = clamp(rebuilt[y * 8 + x])
    return output


def replace_band(recipient, donor, band):
    """Give ``recipient`` the donor's block-DCT coefficients at the listed positions."""
    planes = [_plane(u, v) for u, v in band]
    donor_coefficients = _analyse(donor, planes)[1]
    recipient_coefficients = _analyse(recipient, planes)[1]
    output = [row[:] for row in recipient]
    blocks_per_row = len(recipient[0]) // 8
    for index, (theirs, mine) in enumerate(zip(donor_coefficients, recipient_coefficients)):
        delta = [0.0] * 64
        for a, b, plane in zip(theirs, mine, planes):
            delta = [value + (a - b) * basis for value, basis in zip(delta, plane)]
        top, left = (index // blocks_per_row) * 8, (index % blocks_per_row) * 8
        for y in range(8):
            for x in range(8):
                output[top + y][left + x] = clamp(output[top + y][left + x] + delta[y * 8 + x])
    return output


def import_block_means(recipient, donor, weight):
    """Move each 8x8 block mean of ``recipient`` towards the donor's by ``weight``."""
    theirs, mine = _analyse(donor, ())[0], _analyse(recipient, ())[0]
    output = [row[:] for row in recipient]
    for by, (their_row, my_row) in enumerate(zip(theirs, mine)):
        for bx, (a, b) in enumerate(zip(their_row, my_row)):
            for y in range(8):
                for x in range(8):
                    output[by * 8 + y][bx * 8 + x] = clamp(output[by * 8 + y][bx * 8 + x] + weight * (a - b))
    return output


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


class RevisedWatermarkV4Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = scene(1)
        cls.other = scene(2)
        cls.marked, cls.report = embed_with_report(cls.source, OWNER, KEY, KEYED_PROFILE)

    def check(self, image, owner=OWNER, key=KEY, profile=KEYED_PROFILE, **options):
        return detect(image, owner, key, profile, **options)

    # -- clean operation -------------------------------------------------

    def test_round_trip_finds_both_keys_within_the_quality_budget(self):
        result = self.check(self.marked)
        self.assertEqual((result["outcome"], result["proposal_state"]), ("both_match", "authentic"))
        self.assertTrue(result["present"])
        for channel in ("semantic", "instance"):
            self.assertGreater(result[channel]["score"], result[channel]["threshold"] + 3.0, result)
            self.assertEqual(result[channel]["code_distance"], 0)
            self.assertEqual(result[channel]["candidate"], "recomputed")
            self.assertTrue(result[channel]["helper_check_ok"])
            self.assertLess(result[channel]["log10_false_positive_bound"], -12.0)
        self.assertGreater(psnr(self.source, self.marked), 41.0)
        self.assertEqual(result["detector_config_id"], detector_config_id(KEYED_PROFILE))
        self.assertEqual(result["decision_id"], decision_id(KEYED_PROFILE))
        self.assertEqual(result["embedding_domain"], "image")
        self.assertEqual((result["owner_id"], result["owners_tested"]), (OWNER, 1))
        self.assertNotIn(KEY, repr(result))
        self.assertGreater(result["timing_ms"]["total"], 0.0)

    def test_output_is_deterministic_and_byte_valued(self):
        self.assertEqual(self.marked, embed(self.source, OWNER, KEY, KEYED_PROFILE))
        self.assertTrue(all(value == math.floor(value) and 0 <= value <= 255 for row in self.marked for value in row))
        self.assertTrue(self.report["verified"])
        self.assertEqual(self.report["clipped_fraction"], 0.0)

    def test_wrong_owner_wrong_key_and_unmarked_images_are_negative(self):
        cases = (
            self.check(self.marked, owner="owner-beta"),
            self.check(self.marked, key="a-different-secret-key"),
            self.check(self.source),
            self.check(self.other),
        )
        for result in cases:
            self.assertEqual((result["outcome"], result["proposal_state"]), ("neither_match", "no_watermark"), result)
            self.assertFalse(result["watermark_found"])
            self.assertLess(result["semantic"]["score"], result["semantic"]["threshold"] - 1.0)
            self.assertLess(result["instance"]["score"], result["instance"]["threshold"] - 1.0)

    def test_public_derived_profile_is_the_default_and_never_mixes_with_the_keyed_one(self):
        self.assertEqual(DEFAULT_PROFILE["security"], "public-derived")
        marked = embed(self.source, OWNER)
        result = detect(marked, OWNER)
        self.assertEqual((result["outcome"], result["key_fingerprint"]), ("both_match", "public"))
        self.assertEqual(detect(marked, "owner-beta")["outcome"], "neither_match")
        self.assertEqual(self.check(marked)["outcome"], "neither_match")
        self.assertEqual(detect(self.marked, OWNER)["outcome"], "neither_match")
        self.assertNotEqual(self.check(self.marked)["key_fingerprint"], "public")
        with self.assertRaises(ValueError):
            embed(self.source, OWNER, KEY)
        with self.assertRaises(ValueError):
            detect(self.marked, OWNER, profile=KEYED_PROFILE)

    def test_unmarked_scores_follow_the_stated_null(self):
        # 12 images x 5 owners x 2 channels: no mark, so every score is a null draw.
        owners = [f"owner-{index}" for index in range(5)]
        scores = []
        for seed in range(20, 32):
            image = scene(seed, 160, 160)
            for owner in owners:
                result = self.check(image, owner=owner)
                self.assertEqual(result["outcome"], "neither_match")
                scores += [result["semantic"]["score"], result["instance"]["score"]]
        # Each score is the larger of at most two candidate correlations.
        self.assertLess(abs(statistics.fmean(scores) - 0.4), 0.5)
        self.assertLess(statistics.pstdev(scores), 1.3)
        self.assertLess(max(scores), 4.5)

    def test_sizes_that_are_not_multiples_of_eight_and_plain_hosts(self):
        hosts = {
            "odd size": scene(5, 203, 331),
            "low contrast": [[clamp(120 + (value - 128) * 0.08) for value in row] for row in self.source],
            "gradient": [[clamp(40 + 0.5 * x + 0.25 * y) for x in range(SIZE)] for y in range(SIZE)],
            "three tones": [[float((60, 130, 200)[(x // 90 + y // 110) % 3]) for x in range(SIZE)] for y in range(SIZE)],
        }
        for name, host in hosts.items():
            marked, report = embed_with_report(host, OWNER, KEY, KEYED_PROFILE)
            self.assertTrue(report["verified"], name)
            self.assertGreater(report["psnr_db"], 40.0, name)
            self.assertEqual(self.check(host)["outcome"], "neither_match", name)
            self.assertEqual(self.check(marked, owner="owner-beta")["outcome"], "neither_match", name)
        odd = embed(hosts["odd size"], OWNER, KEY, KEYED_PROFILE)
        self.assertEqual([row[328:] for row in odd], [row[328:] for row in hosts["odd size"]])
        self.assertEqual(odd[200:], hosts["odd size"][200:])

    # -- robustness (T1-style processing) --------------------------------

    def test_survives_noise_gain_blur_and_requantisation(self):
        attacks = {
            "noise sigma 5": add_noise(self.marked, 5.0),
            "noise sigma 10": add_noise(self.marked, 10.0),
            "contrast 0.8": scale(self.marked, 0.8),
            "contrast 1.1 plus 10": scale(self.marked, 1.1, 10.0),
            "3x3 box blur": box_blur(self.marked),
            "coefficient quantisation step 12": requantise(self.marked, 12.0),
        }
        for name, attacked in attacks.items():
            result = self.check(attacked)
            self.assertEqual(result["outcome"], "both_match", (name, result))
            self.assertEqual(self.check(attacked, owner="owner-beta")["outcome"], "neither_match", name)

    def test_tolerates_distortions_that_defeat_the_v3_candidate(self):
        marked_v3 = [[clamp(value) for value in row] for row in v3.embed(self.source, OWNER, KEY)]
        self.assertTrue(v3.detect(marked_v3, OWNER, KEY)["present"])
        self.assertGreater(psnr(self.source, marked_v3), psnr(self.source, self.marked))
        for attack in (lambda image: add_noise(image, 3.0), lambda image: scale(image, 0.8)):
            self.assertFalse(v3.detect(attack(marked_v3), OWNER, KEY)["present"])
            self.assertEqual(self.check(attack(self.marked))["outcome"], "both_match")

    # -- copy-paste, semantic collision and regeneration-like states ------

    def test_transplanted_mark_is_found_and_reported_as_bound_to_other_content(self):
        forged = replace_band(self.other, self.marked, BAND)
        result = self.check(forged)
        self.assertEqual((result["outcome"], result["proposal_state"]), ("content_mismatch", "copy_paste"), result)
        self.assertFalse(result["present"])
        self.assertTrue(result["watermark_found"])
        self.assertEqual(result["semantic"]["candidate"], "decoded")
        self.assertGreater(result["semantic"]["code_distance"], KEYED_PROFILE["decision"]["semantic_radius"])
        # Binding-disabled control: the same transplant is accepted once content checks are off.
        self.assertEqual(self.check(forged, binding_mode="none")["outcome"], "both_match")

    def test_residual_and_patch_copies_are_never_accepted(self):
        residual = [
            [clamp(value + marked - source) for value, marked, source in zip(row, marked_row, source_row)]
            for row, marked_row, source_row in zip(self.other, self.marked, self.source)
        ]
        patch = [row[:] for row in self.other]
        for y in range(64, 192):
            patch[y][64:192] = self.marked[y][64:192]
        for name, forged in (("residual", residual), ("patch", patch)):
            result = self.check(forged)
            self.assertIn(result["outcome"], ("content_mismatch", "neither_match"), (name, result))
            self.assertNotIn(result["proposal_state"], ("authentic", "regenerated"), (name, result))

    def test_forcing_the_content_codes_requires_importing_the_donor_content(self):
        # A transplant plus the donor's block means still mismatches, because
        # the hash also reads local gradients.  Importing those as well matches,
        # and by then the forgery no longer resembles the recipient.
        means_only = replace_band(import_block_means(self.other, self.marked, 1.0), self.marked, BAND)
        result = self.check(means_only)
        self.assertEqual(result["outcome"], "content_mismatch", result)
        self.assertTrue(result["semantic"]["content_match"])
        self.assertFalse(result["instance"]["content_match"])
        everything = replace_band(import_block_means(self.other, self.marked, 1.0), self.marked, BAND + [(0, 1), (1, 0)])
        self.assertEqual(self.check(everything)["outcome"], "both_match")
        self.assertLess(psnr(self.other, everything), 20.0)

    def test_content_code_drift_is_tolerated_without_avalanche(self):
        # Coarse edits move a few code bits.  The keys still verify through the
        # codes carried in the mark, and the distance decides the outcome.
        drifted = self.check(add_noise(import_block_means(self.marked, self.other, 0.1), 8.0))
        self.assertEqual(drifted["outcome"], "both_match", drifted)
        for channel in ("semantic", "instance"):
            self.assertEqual(drifted[channel]["candidate"], "decoded")
            self.assertGreater(drifted[channel]["code_distance"], 0)
            self.assertLessEqual(drifted[channel]["code_distance"], KEYED_PROFILE["decision"][channel + "_radius"])
        replaced = self.check(import_block_means(self.marked, self.other, 0.5))
        self.assertEqual(replaced["outcome"], "content_mismatch", replaced)
        self.assertGreater(replaced["semantic"]["score"], replaced["semantic"]["threshold"])

    def test_two_images_of_one_composition_are_separated_by_the_instance_key(self):
        # Same structure, different texture: the layout proxy cannot tell them
        # apart (a semantic collision), the perceptual hash can.
        first, second = scene(7, detail_seed=70), scene(7, detail_seed=71)
        marked = embed(first, OWNER, KEY, KEYED_PROFILE)
        forged = replace_band(second, marked, BAND)
        result = self.check(forged)
        self.assertEqual((result["outcome"], result["proposal_state"]), ("content_mismatch", "copy_paste"), result)
        self.assertTrue(result["semantic"]["content_match"])
        self.assertFalse(result["instance"]["content_match"])
        self.assertGreater(result["instance"]["code_distance"], KEYED_PROFILE["decision"]["instance_radius"])
        self.assertEqual(self.check(forged, binding_mode="semantic_only")["outcome"], "both_match")
        self.assertGreater(psnr(second, forged), 30.0)

    def test_perceptual_hash_separates_instances_that_share_a_semantic_vector(self):
        external = profile_with(semantic_source="external:test-encoder")
        rng = random.Random(4)
        subject = [rng.gauss(0, 1) for _ in range(512)]
        unrelated = [rng.gauss(0, 1) for _ in range(512)]
        marked = embed(self.source, OWNER, KEY, external, subject)
        self.assertEqual(detect(marked, OWNER, KEY, external, subject)["outcome"], "both_match")
        # A different photograph of the same subject: same semantic vector, different instance.
        forged = replace_band(self.other, marked, BAND)
        combined = detect(forged, OWNER, KEY, external, subject)
        self.assertEqual((combined["outcome"], combined["proposal_state"]), ("content_mismatch", "copy_paste"), combined)
        self.assertTrue(combined["semantic"]["content_match"])
        self.assertFalse(combined["instance"]["content_match"])
        self.assertEqual(detect(forged, OWNER, KEY, external, subject, binding_mode="semantic_only")["outcome"], "both_match")
        # The untouched marked image presented with unrelated semantics fails the semantic check.
        self.assertEqual(detect(marked, OWNER, KEY, external, unrelated)["outcome"], "content_mismatch")
        self.assertEqual(detect(marked, OWNER, KEY, external, unrelated, binding_mode="perceptual_only")["outcome"], "both_match")
        with self.assertRaises(ValueError):
            detect(marked, OWNER, KEY, external)
        with self.assertRaises(ValueError):
            self.check(self.marked, semantic_features=subject)

    def test_losing_only_the_instance_band_reads_as_the_semantic_key_alone(self):
        regenerated = replace_band(self.marked, self.source, INSTANCE_BAND)
        result = self.check(regenerated)
        self.assertEqual((result["outcome"], result["proposal_state"]), ("semantic_only", "regenerated"), result)
        self.assertTrue(result["semantic"]["content_match"])
        self.assertFalse(result["instance"]["found"])

    # -- components -------------------------------------------------------

    def test_perceptual_hash_is_keyed_stable_and_instance_specific(self):
        base = perceptual_hash(self.source, KEY, KEYED_PROFILE)
        self.assertEqual(perceptual_hash(self.marked, KEY, KEYED_PROFILE), base)
        self.assertLessEqual(bits(perceptual_hash(add_noise(self.marked, 5.0), KEY, KEYED_PROFILE), base), 4)
        self.assertLessEqual(bits(perceptual_hash(box_blur(self.marked), KEY, KEYED_PROFILE), base), 4)
        self.assertGreaterEqual(bits(perceptual_hash(self.other, KEY, KEYED_PROFILE), base), 8)
        # Without the key the hyperplanes, and therefore the code, are different.
        self.assertGreaterEqual(bits(perceptual_hash(self.source, "a-different-secret-key", KEYED_PROFILE), base), 6)
        self.assertGreaterEqual(bits(perceptual_hash(self.source), base), 6)
        self.assertEqual(perceptual_hash([[90.0] * 160 for _ in range(160)]), 0)
        self.assertLess(base, 1 << CODE_BITS)

    def test_helper_code_corrects_soft_errors_and_flags_failures(self):
        code = 0xC0FFEE42
        chips = _helper_encode(code)
        self.assertEqual(len(chips), HELPER_CHIPS)
        soft = [-1.0 if chip else 1.0 for chip in chips]
        self.assertEqual(_helper_decode(soft), (code, True))
        rng = random.Random(3)
        noisy = soft[:]
        for start in range(0, HELPER_CHIPS, 32):
            for position in rng.sample(range(32), 7):
                noisy[start + position] *= -1.0
        self.assertEqual(_helper_decode(noisy), (code, True))
        failures = sum(not _helper_decode([rng.gauss(0, 1) for _ in range(HELPER_CHIPS)])[1] for _ in range(200))
        self.assertGreater(failures, 150)

    def test_false_positive_bound_holds_for_random_patterns(self):
        rng = random.Random(0)
        projections = [rng.gauss(0, 1) * rng.choice((1, 5, 25)) for _ in range(TAG_BITS)]
        scores = [_correlation([rng.getrandbits(1) for _ in range(TAG_BITS)], projections) for _ in range(20000)]
        for level in (2.0, 3.0, 4.0):
            self.assertLessEqual(sum(score >= level for score in scores) / len(scores), math.exp(-level * level / 2.0))
        self.assertLess(max(scores), _threshold(1e-6, 1))
        self.assertAlmostEqual(_threshold(1e-6, 2), math.sqrt(2.0 * math.log(2e6)))
        self.assertAlmostEqual(_correlation([0] * TAG_BITS, [2.0] * TAG_BITS), math.sqrt(TAG_BITS))

    def test_roster_identification_corrects_the_threshold(self):
        roster = ["owner-beta", OWNER, "owner-gamma", "owner-delta"]
        result = identify(self.marked, roster, KEY, KEYED_PROFILE)
        self.assertEqual((result["roster_size"], result["found"], result["both_match"]), (4, [OWNER], [OWNER]))
        single = self.check(self.marked)
        listed = result["results"][OWNER]
        self.assertEqual(listed["owners_tested"], 4)
        self.assertGreater(listed["semantic"]["threshold"], single["semantic"]["threshold"])
        self.assertAlmostEqual(listed["semantic"]["threshold"], _threshold(1e-6, 4 * listed["semantic"]["candidates"]))
        self.assertEqual(identify(self.source, roster, KEY, KEYED_PROFILE)["found"], [])
        with self.assertRaises(ValueError):
            identify(self.marked, [OWNER, OWNER], KEY, KEYED_PROFILE)

    def test_projection_targets_describe_what_the_detector_reads(self):
        contract = projection_targets(self.source, OWNER, KEY, KEYED_PROFILE)
        self.assertEqual(contract["detector_config_id"], self.report["detector_config_id"])
        self.assertEqual(contract["semantic_code"], self.report["semantic_code"])
        for channel in contract["channels"]:
            self.assertEqual(len(channel["target"]), CHANNEL_BITS)
            planes, positions = [], {}
            for _block, u, v, _bit, _sign, _norm in channel["slots"]:
                if (u, v) not in positions:
                    positions[(u, v)] = len(planes)
                    planes.append(_plane(u, v))
            coefficients = _analyse(self.marked, planes)[1]
            reached = [0.0] * CHANNEL_BITS
            for block, u, v, bit, sign, norm in channel["slots"]:
                reached[bit] += sign * coefficients[block][positions[(u, v)]] / norm
            # Byte rounding leaves a residual far below the embedded amplitude.
            self.assertLess(max(abs(a - b) for a, b in zip(reached, channel["target"])), 2.0, channel["channel"])

    # -- configuration and failure handling --------------------------------

    def test_profile_validation_and_detector_identity(self):
        base = detector_config_id(KEYED_PROFILE)
        self.assertEqual(base, detector_config_id(profile_with(embedding={"target_psnr_db": 38.0})))
        self.assertEqual(base, detector_config_id(profile_with(decision={"semantic_radius": 4})))
        self.assertNotEqual(decision_id(KEYED_PROFILE), decision_id(profile_with(decision={"semantic_radius": 4})))
        self.assertNotEqual(base, detector_config_id(DEFAULT_PROFILE))
        self.assertNotEqual(base, detector_config_id(profile_with(semantic_frequencies=[[1, 1], [0, 2], [2, 0], [1, 2], [2, 1]])))
        with self.assertRaises(ValueError):
            self.check(self.marked, expected_config_id=detector_config_id(DEFAULT_PROFILE))
        self.assertEqual(self.check(self.marked, expected_config_id=base)["outcome"], "both_match")
        for broken in (
            {**DEFAULT_PROFILE, "unknown": 1},
            {key: value for key, value in DEFAULT_PROFILE.items() if key != "decision"},
            {**DEFAULT_PROFILE, "instance_frequencies": [[1, 1], [3, 0]]},
            {**DEFAULT_PROFILE, "semantic_frequencies": [[0, 0], [1, 1]]},
            {**DEFAULT_PROFILE, "security": "none"},
            {**DEFAULT_PROFILE, "semantic_source": "clip"},
            {**DEFAULT_PROFILE, "minimum_side": True},
            {**DEFAULT_PROFILE, "embedding": {**DEFAULT_PROFILE["embedding"], "target_psnr_db": 20.0}},
            {**DEFAULT_PROFILE, "embedding": {**DEFAULT_PROFILE["embedding"], "passes": True}},
            {**DEFAULT_PROFILE, "decision": {**DEFAULT_PROFILE["decision"], "false_positive_target": 0.5}},
            {**DEFAULT_PROFILE, "decision": {**DEFAULT_PROFILE["decision"], "semantic_radius": 16}},
            {**DEFAULT_PROFILE, "decision": {**DEFAULT_PROFILE["decision"], "extra": 1}},
        ):
            with self.assertRaises(ValueError):
                validate_profile(broken)

    def test_example_profiles_and_schema_match_the_module(self):
        self.assertEqual(load_profile(CONFIGS / "revised-watermark-v4.example.json"), validate_profile(DEFAULT_PROFILE))
        self.assertEqual(load_profile(CONFIGS / "revised-watermark-v4-keyed.example.json"), validate_profile(KEYED_PROFILE))
        schema = json.loads((CONFIGS / "revised-watermark-v4.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(set(schema["required"]), set(DEFAULT_PROFILE))
        self.assertFalse(schema["additionalProperties"])
        for name in ("schema_version", "profile", "code_bits", "tag_bits"):
            self.assertEqual(schema["properties"][name]["const"], DEFAULT_PROFILE[name])
        for group in ("embedding", "decision"):
            self.assertEqual(set(schema["properties"][group]["required"]), set(DEFAULT_PROFILE[group]))
            self.assertFalse(schema["properties"][group]["additionalProperties"])

    def test_malformed_inputs_are_rejected(self):
        for arguments in (
            ([[100.0] * 152 for _ in range(152)], OWNER, KEY),
            ([[100.0] * 160 for _ in range(159)] + [[100.0] * 159], OWNER, KEY),
            ([[300.0] * 160 for _ in range(160)], OWNER, KEY),
            # A featureless image has no content to bind a signature to.
            ([[127.0] * 160 for _ in range(160)], OWNER, KEY),
            (self.source, "", KEY),
            (self.source, OWNER, "short"),
        ):
            with self.assertRaises(ValueError):
                embed(*arguments, KEYED_PROFILE)
        with self.assertRaises(ValueError):
            self.check(self.marked, binding_mode="strict")
        with self.assertRaises(ValueError):
            self.check(self.marked, roster_size=0)

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
        self.assertGreater(report["clipped_fraction"], 0.0)
        self.assertEqual(self.check(marked)["outcome"], "both_match")

    def test_colour_wrapper_round_trip(self):
        rgb = [[(clamp(value + 12), value, clamp(value - 9)) for value in row[:160]] for row in self.source[:160]]
        marked, report = embed_rgb(rgb, OWNER, KEY, KEYED_PROFILE)
        self.assertTrue(report["verified"])
        self.assertGreater(report["psnr_db"], 40.0)
        self.assertTrue(all(isinstance(channel, int) and 0 <= channel <= 255 for row in marked for pixel in row for channel in pixel))
        self.assertEqual(detect_rgb(marked, OWNER, KEY, KEYED_PROFILE)["outcome"], "both_match")
        self.assertEqual(detect_rgb(rgb, OWNER, KEY, KEYED_PROFILE)["outcome"], "neither_match")


if __name__ == "__main__":
    unittest.main()
