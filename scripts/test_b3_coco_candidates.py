"""Synthetic source-selection tests; no images, model loads or network."""

import copy
import hashlib
import unittest

from b3_coco_candidates import CandidateError, LICENSE_URLS, candidate_frame


def fixture():
    annotation = {"licenses": [{"id": identity, "url": url}
                               for identity, url in {**LICENSE_URLS, 3: "https://example.org/nd"}.items()],
                  "images": []}
    inventory = []
    for number in range(1, 5):
        identity = f"{number:012d}"
        license_id = 3 if number == 4 else 4 + number % 2
        annotation["images"].append({"id": number, "file_name": identity + ".jpg",
                                     "width": 640, "height": 480, "license": license_id,
                                     "flickr_url": f"http://farm1.staticflickr.com/1/{number}.jpg"})
        inventory.append({"source": "coco2017-val", "source_id": str(number),
                          "relative_path": f"val2017/val2017/{identity}.jpg",
                          "bytes": "1000", "sha256": hashlib.sha256(identity.encode()).hexdigest(),
                          "width": "640", "height": "480", "license_id": str(license_id),
                          "mode": "RGB", "format": "JPEG"})
    return annotation, inventory


def select(annotation, inventory, target=2):
    return candidate_frame(annotation, inventory, expected_count=4, target=target)


class CocoCandidateTests(unittest.TestCase):
    def test_stable_rank_reserves_and_no_acceptance(self):
        annotation, inventory = fixture()
        result = select(annotation, inventory)
        annotation["images"].reverse()
        self.assertEqual(result, select(annotation, reversed(inventory)))
        self.assertEqual(result["eligible_count"], 3)
        self.assertEqual(result["exclusions"], {"license_label": 1, "native_dimensions": 0})
        self.assertEqual(len(result["candidates"]), 2)
        self.assertEqual(len(result["ordered_reserves"]), 1)
        for field in ("rights_cleared", "study_ids_frozen", "scientific_compute_authorized"):
            self.assertIs(result[field], False)
        self.assertTrue(all(row["rights_status"] == "pending-image-rights"
                            for row in result["candidates"]))

    def test_rank_known_vector(self):
        annotation, inventory = fixture()
        rows = select(annotation, inventory)["candidates"]
        expected = hashlib.sha256(b"b3-coco-source-candidate-v1\x00" + bytes.fromhex(
            "e8c7f7908f1d7278341fae127d0da654f102f11bd7b21d8aeefa635b8c810b6f")
            + int(rows[0]["source_id"]).to_bytes(8, "big")).hexdigest()
        self.assertEqual(rows[0]["rank_sha256"], expected)

    def test_dimensions_exclude_without_silent_count_reduction(self):
        annotation, inventory = fixture()
        annotation["images"][0]["width"] = 63
        inventory[0]["width"] = "63"
        self.assertEqual(select(annotation, inventory)["exclusions"]["native_dimensions"], 1)
        with self.assertRaisesRegex(CandidateError, "cannot shrink"):
            select(annotation, inventory, target=3)

    def test_all_rows_checked_even_when_license_ineligible(self):
        annotation, inventory = fixture()
        inventory[-1]["width"] = "639"
        with self.assertRaisesRegex(CandidateError, "mismatch"):
            select(annotation, inventory)

    def test_duplicate_missing_or_extra_frame(self):
        for kind in ("duplicate_annotation", "duplicate_inventory", "missing", "extra"):
            annotation, inventory = fixture()
            if kind == "duplicate_annotation":
                annotation["images"][-1] = copy.deepcopy(annotation["images"][0])
            elif kind == "duplicate_inventory":
                inventory[-1] = copy.deepcopy(inventory[0])
            elif kind == "missing":
                inventory.pop()
            else:
                inventory.append({**inventory[0], "source_id": "5"})
            with self.subTest(kind=kind), self.assertRaises(CandidateError):
                select(annotation, inventory)

    def test_license_definition_and_unknown_id_fail(self):
        annotation, inventory = fixture()
        annotation["licenses"][0]["url"] = "https://creativecommons.org/licenses/by/4.0/"
        with self.assertRaisesRegex(CandidateError, "definitions"):
            select(annotation, inventory)
        annotation, inventory = fixture()
        annotation["images"][0]["license"] = 99
        with self.assertRaisesRegex(CandidateError, "undefined"):
            select(annotation, inventory)

    def test_unsafe_paths_and_bad_hooks_fail(self):
        for path in ("../000000000001.jpg", "/val2017/000000000001.jpg",
                     "val2017//000000000001.jpg", "val2017/./000000000001.jpg",
                     "val2017\\000000000001.jpg", "val2017/C:000000000001.jpg"):
            annotation, inventory = fixture()
            inventory[0]["relative_path"] = path
            with self.subTest(path=path), self.assertRaisesRegex(CandidateError, "path"):
                select(annotation, inventory)
        for url in ("https://evilstaticflickr.com/a", "https://farm1.staticflickr.com@evil.org/a",
                    "https://farm1.staticflickr.com/a?secret=x", "file:///a"):
            annotation, inventory = fixture()
            annotation["images"][0]["flickr_url"] = url
            with self.subTest(url=url), self.assertRaisesRegex(CandidateError, "hook"):
                select(annotation, inventory)

    def test_bad_digest_duplicate_bytes_and_numeric_inputs_fail(self):
        annotation, inventory = fixture()
        inventory[0]["sha256"] = "not-a-hash"
        with self.assertRaisesRegex(CandidateError, "digest"):
            select(annotation, inventory)
        annotation, inventory = fixture()
        inventory[1]["sha256"] = inventory[0]["sha256"]
        with self.assertRaisesRegex(CandidateError, "identical-byte"):
            select(annotation, inventory)
        for value in (True, 0, -1, 1.5, "640"):
            annotation, inventory = fixture()
            annotation["images"][0]["width"] = value
            with self.subTest(value=value), self.assertRaises(CandidateError):
                select(annotation, inventory)


if __name__ == "__main__":
    unittest.main()
