"""Synthetic OwnerID and domain-separation tests; no images or model loads."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))

from src.signatures.owner import (  # noqa: E402
    OwnerProtocolError, canonical_owner, derive_public_signatures,
    pack_fields, rotation_requires_reenrollment, wrong_owner_control,
)


class OwnerProtocolTests(unittest.TestCase):
    def test_length_prefix_and_unicode_nfc(self):
        self.assertEqual(pack_fields(b"a", b"bc"),
                         b"\x00\x00\x00\x01a\x00\x00\x00\x02bc")
        self.assertEqual(canonical_owner("Cafe\u0301"), ("Caf\u00e9", b"Caf\xc3\xa9"))
        self.assertNotEqual(canonical_owner("Alice")[1], canonical_owner("alice")[1])
        self.assertNotEqual(canonical_owner("Alice")[1], canonical_owner(" Alice")[1])

    def test_pinned_known_answer_vectors(self):
        vectors = json.loads((PROJECT / "research" / "key-test-vectors.json")
                             .read_text(encoding="utf-8"))
        for item in vectors["vectors"]:
            with self.subTest(name=item["name"]):
                keys = derive_public_signatures(bytes.fromhex(item["q_hex"]),
                                                bytes.fromhex(item["phash_hex"]),
                                                item["owner_input"])
                self.assertEqual(keys.owner_id, item["owner_nfc"])
                self.assertEqual(keys.owner_bytes.hex(), item["owner_utf8_hex"])
                self.assertEqual(keys.semantic.hex(), item["ws_hex"])
                self.assertEqual(keys.instance.hex(), item["wi_hex"])
                self.assertEqual(len(keys.semantic), 32)
                self.assertEqual(len(keys.instance), 32)

    def test_wrong_owner_control_and_rotation(self):
        correct, wrong = wrong_owner_control(b"\x34\x0a", b"\x00\x01\x02\x03",
                                             "Alice", "Bob")
        self.assertNotEqual(correct.semantic, wrong.semantic)
        self.assertNotEqual(correct.instance, wrong.instance)
        self.assertTrue(rotation_requires_reenrollment("Alice", "Bob"))
        with self.assertRaisesRegex(OwnerProtocolError, "same NFC"):
            wrong_owner_control(b"\x34\x0a", b"\x00\x01\x02\x03",
                                "Caf\u00e9", "Cafe\u0301")
        with self.assertRaisesRegex(OwnerProtocolError, "distinct canonical"):
            rotation_requires_reenrollment("Caf\u00e9", "Cafe\u0301")

    def test_component_namespace_and_feature_dependency(self):
        base = derive_public_signatures(b"\x34\x0a", b"\x00\x01\x02\x03", "Alice")
        changed_phash = derive_public_signatures(b"\x34\x0a", b"\x01\x01\x02\x03", "Alice")
        changed_q = derive_public_signatures(b"\x35\x0a", b"\x00\x01\x02\x03", "Alice")
        self.assertEqual(base.semantic, changed_phash.semantic)
        self.assertNotEqual(base.instance, changed_phash.instance)
        self.assertNotEqual(base.semantic, changed_q.semantic)
        self.assertNotEqual(base.instance, changed_q.instance)
        self.assertNotEqual(base.semantic, base.instance)

    def test_invalid_owner_codes_and_secret_fail_closed(self):
        for owner in ("", "x" * 257, "\ud800"):
            with self.subTest(owner=repr(owner)), self.assertRaises(OwnerProtocolError):
                canonical_owner(owner)
        with self.assertRaisesRegex(OwnerProtocolError, "canonical 12-bit"):
            derive_public_signatures(b"\x34\xfa", b"\x00" * 4, "Alice")
        with self.assertRaisesRegex(OwnerProtocolError, "32-bit"):
            derive_public_signatures(b"\x34\x0a", b"\x00" * 3, "Alice")
        with self.assertRaisesRegex(OwnerProtocolError, "unsupported"):
            derive_public_signatures(b"\x34\x0a", b"\x00" * 4,
                                     "Alice", secret_ref="private-key")


if __name__ == "__main__":
    unittest.main()
