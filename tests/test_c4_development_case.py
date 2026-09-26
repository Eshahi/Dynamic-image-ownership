"""Owned metadata attack fixtures and pinned real metadata; no image reads."""
import copy
import csv
import io
import json
import tempfile
import unittest
from pathlib import Path

from src.embedding.development_case import COUNTS, PINS, freeze_case, select_case, validate_frozen_case


def fixtures():
    sources, images, splits = [], [], []
    for domain, count in COUNTS.items():
        for index in range(count):
            identity = dict(domain=domain, release_id="owned-v1", source_split="train", source_id=str(index))
            uid = ":".join(identity.values())
            digest = f"{len(sources)+1:064x}"
            common = dict(**identity, raw_sha256=digest)
            image = dict(**common, relative_path=f"owned/{domain}/{index}.png", group_id="raw-"+digest)
            images.append(image)
            sources.append(dict(**image, width="100", height="100", raw_size_bytes="100",
                                rights_status="owned-test-only", use_limitations="not study data"))
            splits.append(dict(**common, group_id="linked-"+digest, source_uid=uid, image_id=uid,
                               canonical_pixel_sha256=digest, canonical_status="canonical_pass",
                               canonical_rejection_reason="", split="development", study_split="development"))
    return sources, dict(images=images, counts_by_domain=COUNTS,
                        b4_must_reserve_all_linked_groups_for_development=True), splits


def encoded(sources, reservation, splits):
    def csv_bytes(rows):
        out = io.StringIO(newline="")
        writer = csv.DictWriter(out, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
        return out.getvalue().encode()
    return csv_bytes(sources), json.dumps(reservation).encode(), csv_bytes(splits)


class DevelopmentCaseTests(unittest.TestCase):
    def select(self, f, cap=1024):
        return select_case(*encoded(*f), maximum_side=cap)

    def test_rank_order_invariant_and_uid_ties(self):
        f = fixtures()
        one = self.select(f)
        for part in (f[0], f[1]["images"], f[2]): part.reverse()
        self.assertEqual(one, self.select(f))
        self.assertEqual(one["selected"]["source_uid"], "diffusiondb:owned-v1:train:0")
        self.assertFalse(one["scientific_execution_authorized"])
        self.assertFalse(one["rights_clearance"])

    def test_padded_area_precedes_raw_area(self):
        f = fixtures()
        # 65x65 has less raw area than 64x100 but larger pad64 area.
        f[0][0].update(width="65", height="65")
        f[0][1].update(width="64", height="100")
        self.assertEqual(self.select(f)["selected"]["source_uid"], "diffusiondb:owned-v1:train:1")

    def test_all_reservations_checked_before_size_exclusion(self):
        for field, value in (("raw_sha256", "0"*64), ("width", "0"),
                             ("relative_path", "../outside.png")):
            f = fixtures(); f[0][-1]["height"] = "2000"; f[0][-1][field] = value
            with self.assertRaises(ValueError): self.select(f)
        f = fixtures(); f[0][-1]["height"] = "2000"; f[2][-1]["study_split"] = "test"
        with self.assertRaises(ValueError): self.select(f)

    def test_duplicates_and_reservation_count_rejected(self):
        for part in (0, 2):
            f = fixtures(); f[part].append(copy.deepcopy(f[part][0]))
            with self.assertRaises(ValueError): self.select(f)
        f = fixtures(); f[1]["images"][-1] = copy.deepcopy(f[1]["images"][0])
        with self.assertRaises(ValueError): self.select(f)
        f = fixtures(); f[1]["images"].pop()
        with self.assertRaises(ValueError): self.select(f)

    def test_linked_group_holdout_and_div2k_valid_rejected(self):
        f = fixtures()
        other = copy.deepcopy(f[2][0]); other["source_id"] = "extra"
        other["study_split"] = other["split"] = "validation"; f[2].append(other)
        with self.assertRaises(ValueError): self.select(f)
        f = fixtures()
        for part in (f[0][12], f[1]["images"][12], f[2][12]): part["source_split"] = "valid"
        with self.assertRaises(ValueError): self.select(f)

    def test_no_eligible_no_resize_or_fallback(self):
        with self.assertRaises(ValueError): self.select(fixtures(), cap=64)
        for cap in (True, 0, 1025, 64.0):
            with self.assertRaises(ValueError): self.select(fixtures(), cap=cap)

    def test_real_pinned_metadata_only_and_tamper_rejected(self):
        root = Path(__file__).resolve().parents[1]
        result = freeze_case(root)
        self.assertEqual(result["selected"]["source_uid"], "ms-coco:coco-2017:val2017:109798")
        self.assertEqual(result["eligible_count"], 22)
        self.assertEqual(result["selected"]["padded_area"], 196608)
        self.assertFalse(result["actual_pixels_revalidated"])
        with tempfile.TemporaryDirectory() as tmp:
            for name in PINS:
                target = Path(tmp)/name; target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((root/name).read_bytes())
            (Path(tmp)/next(iter(PINS))).write_bytes(b"changed")
            with self.assertRaises(ValueError): freeze_case(tmp)

    def test_actual_frozen_receipt_replay_and_relabel_rejections(self):
        root = Path(__file__).resolve().parents[1]
        raw = (root/"experiments/c4-embedding-development-v1/frozen-case.json").read_bytes()
        value = validate_frozen_case(root, raw)
        for key, changed in (("scientific_execution_authorized", True),
                             ("maximum_side", 512), ("rights_clearance", True),
                             ("actual_pixels_revalidated", True)):
            altered = copy.deepcopy(value); altered[key] = changed
            with self.assertRaises(ValueError): validate_frozen_case(root, json.dumps(altered).encode())
        altered = copy.deepcopy(value)
        altered["selected"]["source_uid"] = altered["ranking"][1]["source_uid"]
        with self.assertRaises(ValueError): validate_frozen_case(root, json.dumps(altered).encode())


if __name__ == "__main__": unittest.main()
