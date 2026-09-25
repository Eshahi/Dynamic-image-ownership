"""A5 public OwnerID binding and domain-separated signature derivation.

This module deliberately has no secret-key mode, registry, or transfer API.
The returned values are reproducible by anyone who knows the public inputs.
"""

from __future__ import annotations

import hashlib
import unicodedata
from dataclasses import dataclass


class OwnerProtocolError(ValueError):
    """The public-derived owner/signature contract is not satisfied."""


@dataclass(frozen=True)
class PublicSignatures:
    owner_id: str
    owner_bytes: bytes
    semantic: bytes
    instance: bytes
    profile: str = "public-derived-existing-image"


def canonical_owner(owner_id: str) -> tuple[str, bytes]:
    """NFC and UTF-8 only; never trim, case-fold, or treat ID as a secret."""
    if not isinstance(owner_id, str):
        raise OwnerProtocolError("OwnerID must be Unicode text")
    canonical = unicodedata.normalize("NFC", owner_id)
    try:
        encoded = canonical.encode("utf-8", errors="strict")
    except UnicodeError as error:
        raise OwnerProtocolError("OwnerID cannot be encoded as strict UTF-8") from error
    if not 1 <= len(encoded) <= 256:
        raise OwnerProtocolError("OwnerID must occupy 1..256 UTF-8 bytes")
    return canonical, encoded


def pack_fields(*fields: bytes) -> bytes:
    """A5 pack: uint32be length before each raw byte field, in order."""
    packed = bytearray()
    for field in fields:
        if not isinstance(field, bytes):
            raise OwnerProtocolError("pack fields must be immutable bytes")
        if len(field) >= 2**32:
            raise OwnerProtocolError("pack field exceeds uint32 length")
        packed.extend(len(field).to_bytes(4, "big"))
        packed.extend(field)
    return bytes(packed)


def _codes(q_bytes: bytes, phash_bytes: bytes) -> None:
    if not isinstance(q_bytes, bytes) or len(q_bytes) != 2 or q_bytes[1] & 0xF0:
        raise OwnerProtocolError("q must be a canonical 12-bit little-bit-first code")
    if not isinstance(phash_bytes, bytes) or len(phash_bytes) != 4:
        raise OwnerProtocolError("pHash must be a 32-bit little-bit-first code")


def derive_public_signatures(q_bytes: bytes, phash_bytes: bytes,
                             owner_id: str, *, secret_ref: None = None) -> PublicSignatures:
    """Compute exact A5 Ws/Wi; reject a supposed secret rather than ignore it."""
    if secret_ref is not None:
        raise OwnerProtocolError("secret_ref is unsupported in the public-derived profile")
    _codes(q_bytes, phash_bytes)
    canonical, owner_bytes = canonical_owner(owner_id)
    ws = hashlib.sha256(pack_fields(b"a5-ws-v1", q_bytes, owner_bytes)).digest()
    wi = hashlib.sha256(pack_fields(b"a5-wi-v1", q_bytes, phash_bytes,
                                   owner_bytes)).digest()
    return PublicSignatures(canonical, owner_bytes, ws, wi)


def wrong_owner_control(q_bytes: bytes, phash_bytes: bytes,
                        correct_owner: str, wrong_owner: str) -> tuple[PublicSignatures, PublicSignatures]:
    """Derive C2 candidates without supplying an oracle key to the detector."""
    correct = derive_public_signatures(q_bytes, phash_bytes, correct_owner)
    wrong = derive_public_signatures(q_bytes, phash_bytes, wrong_owner)
    if correct.owner_bytes == wrong.owner_bytes:
        raise OwnerProtocolError("wrong-owner control collapsed to the same NFC OwnerID")
    return correct, wrong


def rotation_requires_reenrollment(old_owner: str, new_owner: str) -> bool:
    """A changed public ID produces new signatures; no transparent transfer exists."""
    _, old_bytes = canonical_owner(old_owner)
    _, new_bytes = canonical_owner(new_owner)
    if old_bytes == new_bytes:
        raise OwnerProtocolError("rotation requires a distinct canonical OwnerID")
    return True
