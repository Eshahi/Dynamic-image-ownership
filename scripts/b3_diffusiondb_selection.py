"""Deterministic, metadata-only candidate-part selection for DiffusionDB 2M.

The input is an iterator of plain Python metadata records. A later, separately
checked Parquet reader must supply them after the user provides the local file.
This module never downloads, opens, or approves image bytes.
"""

from __future__ import annotations

import hashlib
import math
import unicodedata
import uuid
from collections.abc import Iterable, Mapping
from typing import Any


REVISION = "fb620fbe49fa4420e0734bd9c0df11f51176b61f"
PART_COUNT = 2000
ROWS_PER_PART = 1000
MAX_PARTS = 14  # User-authorized resource amendment, 2026-09-26; ranking unchanged.
TARGET_IMAGES = 5000
RESERVE_GROUPS = 1000
NSFW_CEILING = 0.10  # Scores at or above this are ineligible.


class SelectionError(ValueError):
    """The metadata cannot support a defensible bounded handoff."""


def ranked_parts() -> tuple[int, ...]:
    """Fixed, revision-bound order independent of outcomes or file arrival."""
    prefix = b"b3-diffusiondb-part-v1\x00" + bytes.fromhex(REVISION)
    return tuple(sorted(range(1, PART_COUNT + 1),
                        key=lambda part: (hashlib.sha256(prefix + part.to_bytes(2, "big")).digest(),
                                          part)))


def _canonical_image_name(value: Any) -> str:
    if not isinstance(value, str) or not value.endswith(".png"):
        raise SelectionError("image_name must be a PNG UUID filename")
    name = value[:-4]
    try:
        identity = uuid.UUID(name)
    except (ValueError, AttributeError) as error:
        raise SelectionError("image_name is not a UUID") from error
    if identity.version != 4 or str(identity) != name:
        raise SelectionError("image_name is not a canonical lowercase UUIDv4")
    return value


def _score(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise SelectionError(f"{field} must be a finite numeric score")
    result = float(value)
    if field == "image_nsfw" and result == 2.0:
        return result  # Curator-documented already-blurred NSFW sentinel; always excluded.
    if not math.isfinite(result) or not 0 <= result <= 1:
        raise SelectionError(f"{field} must be a finite numeric score in [0,1]")
    return result


def _prompt_group(value: Any) -> str | None:
    if not isinstance(value, str):
        raise SelectionError("prompt must be text")
    normalized = " ".join(unicodedata.normalize("NFC", value).casefold().split())
    if not normalized:
        return None  # Known source eligibility exclusion, not a fabricated group.
    return hashlib.sha256(b"b3-prompt-group-v1\x00" + normalized.encode("utf-8")).hexdigest()


def candidate_part_handoff(rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """Return a bounded PART list, never final image IDs or rights clearance.

    Select the shortest prefix of the first fourteen hash-ranked parts containing
    at least 6,000 metadata-eligible *distinct normalized prompt groups*.
    Anything short of that is blocked, not a count reduction or adaptive search.
    """
    candidates = ranked_parts()[:MAX_PARTS]
    candidate_set = set(candidates)
    groups: dict[int, set[str]] = {part: set() for part in candidates}
    seen_per_part: dict[int, int] = {part: 0 for part in candidates}
    seen_names: set[str] = set()
    examined = 0
    excluded_by_score = 0
    excluded_by_empty_prompt = 0
    for row in rows:
        if not isinstance(row, Mapping):
            raise SelectionError("metadata row must be a mapping")
        part = row.get("part_id")
        if isinstance(part, bool) or not isinstance(part, int) or not 1 <= part <= PART_COUNT:
            raise SelectionError("part_id must be an integer in [1,2000]")
        if part not in candidate_set:
            continue
        examined += 1
        seen_per_part[part] += 1
        if seen_per_part[part] > ROWS_PER_PART:
            raise SelectionError("candidate part exceeds 1000 metadata rows")
        name = _canonical_image_name(row.get("image_name"))
        if name in seen_names:
            raise SelectionError("duplicate image_name in candidate parts")
        seen_names.add(name)
        width, height = row.get("width"), row.get("height")
        if (isinstance(width, bool) or isinstance(height, bool) or
                not isinstance(width, int) or not isinstance(height, int) or
                width <= 0 or height <= 0):
            raise SelectionError("image dimensions must be positive integers")
        image_score = _score(row.get("image_nsfw"), "image_nsfw")
        prompt_score = _score(row.get("prompt_nsfw"), "prompt_nsfw")
        group = _prompt_group(row.get("prompt"))  # Malformed text blocks even excluded rows.
        if min(width, height) < 64 or image_score >= NSFW_CEILING or prompt_score >= NSFW_CEILING:
            excluded_by_score += 1
            continue
        if group is None:
            excluded_by_empty_prompt += 1
            continue
        groups[part].add(group)
    accumulated: set[str] = set()
    selected: list[int] = []
    # Validate cardinality of EVERY candidate part, including later unused parts.
    # A favorable early prefix cannot hide missing or incomplete candidate input.
    for part in candidates:
        if seen_per_part[part] != ROWS_PER_PART:
            all_groups = set().union(*groups.values())
            return {"status": ("blocked_missing_ranked_part_metadata" if seen_per_part[part] == 0
                               else "blocked_incomplete_ranked_part_metadata"),
                    "revision": REVISION, "selected_part_ids": [],
                    "candidate_order": list(candidates),
                    "distinct_prompt_groups": len(all_groups),
                    "rows_examined_in_candidate_parts": examined,
                    "rows_excluded_by_score_or_size": excluded_by_score,
                    "rows_excluded_by_empty_prompt": excluded_by_empty_prompt,
                    "image_ids_frozen": False, "images_downloaded": False}
    for part in candidates:
        selected.append(part)
        accumulated.update(groups[part])
        if len(accumulated) >= TARGET_IMAGES + RESERVE_GROUPS:
            return {"status": "candidate_parts_ready", "revision": REVISION,
                    "selected_part_ids": selected, "candidate_order": list(candidates),
                    "distinct_prompt_groups": len(accumulated),
                    "rows_examined_in_candidate_parts": examined,
                    "rows_excluded_by_score_or_size": excluded_by_score,
                    "rows_excluded_by_empty_prompt": excluded_by_empty_prompt,
                    "image_ids_frozen": False, "images_downloaded": False}
    return {"status": "blocked_insufficient_metadata_eligible_groups",
            "revision": REVISION, "selected_part_ids": [],
            "candidate_order": list(candidates),
            "distinct_prompt_groups": len(accumulated),
            "rows_examined_in_candidate_parts": examined,
            "rows_excluded_by_score_or_size": excluded_by_score,
            "rows_excluded_by_empty_prompt": excluded_by_empty_prompt,
            "image_ids_frozen": False, "images_downloaded": False}
