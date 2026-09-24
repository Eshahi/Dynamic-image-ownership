"""Offline TrustMark Q/BCH_5 payload and decision contract for B2.

No TrustMark import, checkpoint load, image processing or network access occurs
here. This does not make the comparator runnable or authorize an experiment.
"""

from __future__ import annotations

import hashlib
import re


SOURCE_COMMIT = "2ecb73ad28d1a3f66ac9dc19e1b667711f14314f"
PROFILE = "Q/BCH_5/binary/v1"
PAYLOAD_BITS = 61
_HEX32 = re.compile(r"[0-9a-f]{64}\Z")
_BITS61 = re.compile(r"[01]{61}\Z")


def _field(value: str) -> bytes:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ValueError("dataset, version and image_id must be nonempty, unpadded strings")
    encoded = value.encode("utf-8")
    if len(encoded) > 65535:
        raise ValueError("identifier exceeds 65535 UTF-8 bytes")
    return len(encoded).to_bytes(2, "big") + encoded


def payload_for_image(seed_hex: str, dataset: str, version: str, image_id: str) -> str:
    """Derive the fixed 61-bit *comparator* payload for a frozen manifest ID.

    The 32-byte seed must be committed before test images are inspected. This
    is a reproducible pseudorandom schedule, not ownership authentication.
    """
    if not isinstance(seed_hex, str) or not _HEX32.fullmatch(seed_hex):
        raise ValueError("seed_hex must be exactly 64 lowercase hexadecimal digits")
    material = (b"b2-trustmark-q-bch5-payload-v1\x00" + bytes.fromhex(seed_hex)
                + _field(dataset) + _field(version) + _field(image_id))
    digest = hashlib.shake_256(material).digest(8)
    return "".join(f"{byte:08b}" for byte in digest)[:PAYLOAD_BITS]


def wrong_payload(expected: str) -> str:
    """A deterministic distinct valid-length payload for a negative control."""
    if not isinstance(expected, str) or not _BITS61.fullmatch(expected):
        raise ValueError("expected payload must be exactly 61 binary characters")
    return ("1" if expected[0] == "0" else "0") + expected[1:]


def classify_decode(decoded: str, detected: bool, version: int,
                    expected: str) -> dict[str, object]:
    """Separate upstream ECC validity from exact payload match.

    The official Q/BCH_5 decode path returns (decoded, detected, version).
    This adapter-boundary check does not invent a continuous detector score.
    """
    if not isinstance(expected, str) or not _BITS61.fullmatch(expected):
        raise ValueError("expected payload must be exactly 61 binary characters")
    if type(detected) is not bool or type(version) is not int or not isinstance(decoded, str):
        raise ValueError("malformed upstream decode tuple")
    if detected:
        if version != 1 or not _BITS61.fullmatch(decoded):
            raise ValueError("detected payload is not the frozen BCH_5 binary profile")
        match = decoded == expected
        return {"ecc_valid": True, "payload_match": match,
                "status": "MATCH" if match else "VALID_OTHER_PAYLOAD", "score": None}
    if version not in (-1, 1):
        raise ValueError("unsupported unsuccessful decode version")
    if decoded and not _BITS61.fullmatch(decoded):
        raise ValueError("malformed unsuccessful decode payload")
    return {"ecc_valid": False, "payload_match": False,
            "status": "NO_VALID_BCH_5", "score": None}
