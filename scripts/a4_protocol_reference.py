"""A4 calibration semantics on supplied scores; no image, model, or scientific run.

This reference deliberately accepts only precomputed, validation-only score rows.
The caller must map invalid outputs to None and separately prove source eligibility,
split isolation, score provenance, and implementation parity before study use.
Malformed numeric data mislabeled as a valid score row is rejected, not treated
as a clean negative.
"""

from bisect import bisect_left
from dataclasses import dataclass
from fractions import Fraction
import hashlib
import math
import unicodedata


DOMAINS = ("MS-COCO", "DIV2K", "DiffusionDB")
CONDITIONS = ("C1", "C0-source", "C0-reconstruction", "C2")
NEGATIVE_CONDITIONS = CONDITIONS[1:]
GRID = tuple((j - 50) / 50 for j in range(101))


def _source_bytes(source_uid: str) -> bytes:
    if not isinstance(source_uid, str) or not source_uid:
        raise ValueError("source_uid must be nonempty text")
    if unicodedata.normalize("NFC", source_uid) != source_uid:
        raise ValueError("source_uid must already be NFC-normalized")
    raw = source_uid.encode("utf-8")
    if len(raw) > 0xFFFFFFFF:
        raise ValueError("source_uid exceeds uint32 byte length")
    return raw


def owner_and_seed(source_uid: str) -> tuple[str, str, int]:
    """Return the preregistered enrolled/wrong OwnerIDs and exact uint64 seed."""
    raw = _source_bytes(source_uid)

    def first_uint64(tag: bytes) -> int:
        digest = hashlib.sha256(tag + b"\x00" + len(raw).to_bytes(4, "big") + raw).digest()
        return int.from_bytes(digest[:8], "big")

    index = first_uint64(b"a4-owner-v1") % 16
    return f"thesis:owner:{index:02d}", f"thesis:owner:{(index + 1) % 16:02d}", first_uint64(b"a4-seed-v1")


@dataclass(frozen=True)
class Candidate:
    """One common-q candidate; None denotes a vetoed component score."""

    semantic: float | None
    instances: tuple[float | None, ...]


def _eligible_pairs(candidates: tuple[Candidate, ...]) -> tuple[tuple[float, float], ...]:
    pairs = []
    for candidate in candidates:
        semantic = candidate.semantic
        if semantic is not None and (isinstance(semantic, bool) or not isinstance(semantic, (int, float)) or not -1 <= semantic <= 1 or not math.isfinite(semantic)):
            raise ValueError("semantic score must be finite in [-1,1] or None")
        if not isinstance(candidate.instances, tuple):
            raise ValueError("instance scores must be a tuple")
        valid_instances = []
        for instance in candidate.instances:
            if instance is None:
                continue
            if isinstance(instance, bool) or not isinstance(instance, (int, float)) or not -1 <= instance <= 1 or not math.isfinite(instance):
                raise ValueError("instance score must be finite in [-1,1] or None")
            valid_instances.append(instance)
        if semantic is not None and valid_instances:
            pairs.append((semantic, max(valid_instances)))
    return tuple(pairs)


def both_match(candidates: tuple[Candidate, ...], tau_s: float, tau_i: float) -> bool:
    """A5 common-q strict decision for a valid detector output."""
    if any(isinstance(t, bool) or not isinstance(t, (int, float)) or not -1 <= t <= 1 or not math.isfinite(t) for t in (tau_s, tau_i)):
        raise ValueError("thresholds must be finite in [-1,1]")
    return any(s > tau_s and i > tau_i for s, i in _eligible_pairs(candidates))


@dataclass(frozen=True)
class CalibrationResult:
    semantic_index: int
    instance_index: int
    tau_s: float
    tau_i: float
    positive_counts: dict[str, int]
    negative_counts: dict[str, dict[str, int]]
    planned_counts: dict[str, int]


def calibrate(
    sources: tuple[tuple[str, str], ...],
    observations: dict[tuple[str, str], tuple[Candidate, ...] | None],
) -> CalibrationResult | None:
    """Choose A4's validation pair; None means no FPR-admissible pair.

    ``sources`` is the predeclared eligible (domain, UID) roster. Missing/None
    observations count as C1 misses and adverse matches in negative cells.
    An empty candidate tuple is a *valid nonmatch*, not a failed observation.
    This function cannot establish that inputs really came from validation.
    """
    if not sources or len(set(sources)) != len(sources):
        raise ValueError("sources must be nonempty and unique")
    planned = {domain: 0 for domain in DOMAINS}
    seen_uid = set()
    for domain, uid in sources:
        if domain not in DOMAINS or uid in seen_uid:
            raise ValueError("unknown domain or duplicate source UID")
        _source_bytes(uid)
        seen_uid.add(uid)
        planned[domain] += 1
    if any(n == 0 for n in planned.values()):
        raise ValueError("all three domains require predeclared eligible sources")
    allowed_keys = {(uid, condition) for _, uid in sources for condition in CONDITIONS}
    if set(observations) - allowed_keys:
        raise ValueError("observation outside source/condition roster")

    # For each semantic grid row, a candidate covers instance thresholds
    # strictly below its best eligible instance score. Difference arrays make
    # the reference O(sources * conditions * grid * candidates), not one full
    # score pass for each of the 10,201 threshold pairs.
    differences = {
        domain: {condition: [[0] * 102 for _ in GRID] for condition in CONDITIONS}
        for domain in DOMAINS
    }
    missing_negatives = {domain: {condition: 0 for condition in NEGATIVE_CONDITIONS} for domain in DOMAINS}
    for domain, uid in sources:
        for condition in CONDITIONS:
            observed = observations.get((uid, condition))
            if observed is None:
                if condition != "C1":
                    missing_negatives[domain][condition] += 1
                continue
            if not isinstance(observed, tuple) or any(not isinstance(c, Candidate) for c in observed):
                raise ValueError("valid observations must be tuples of Candidate")
            pairs = _eligible_pairs(observed)
            for sem_index, tau_s in enumerate(GRID):
                best_instance = max((inst for sem, inst in pairs if sem > tau_s), default=None)
                if best_instance is not None:
                    count = bisect_left(GRID, best_instance)
                    differences[domain][condition][sem_index][0] += 1
                    differences[domain][condition][sem_index][count] -= 1

    counts = {
        domain: {condition: [[0] * len(GRID) for _ in GRID] for condition in CONDITIONS}
        for domain in DOMAINS
    }
    for domain in DOMAINS:
        for condition in CONDITIONS:
            adverse = missing_negatives[domain].get(condition, 0)
            for sem_index in range(len(GRID)):
                current = adverse
                for inst_index in range(len(GRID)):
                    current += differences[domain][condition][sem_index][inst_index]
                    counts[domain][condition][sem_index][inst_index] = current

    winner = None
    winner_key = None
    for sem_index, tau_s in enumerate(GRID):
        for inst_index, tau_i in enumerate(GRID):
            if any(
                100 * counts[domain][condition][sem_index][inst_index] > planned[domain]
                for domain in DOMAINS for condition in NEGATIVE_CONDITIONS
            ):
                continue
            macro_tpr = sum(
                (Fraction(counts[domain]["C1"][sem_index][inst_index], planned[domain]) for domain in DOMAINS),
                Fraction(),
            ) / len(DOMAINS)
            key = (macro_tpr, sem_index, inst_index)
            if winner_key is None or key > winner_key:
                winner_key = key
                winner = (sem_index, inst_index, tau_s, tau_i)
    if winner is None:
        return None
    sem_index, inst_index, tau_s, tau_i = winner
    return CalibrationResult(
        sem_index, inst_index, tau_s, tau_i,
        {domain: counts[domain]["C1"][sem_index][inst_index] for domain in DOMAINS},
        {domain: {condition: counts[domain][condition][sem_index][inst_index] for condition in NEGATIVE_CONDITIONS} for domain in DOMAINS},
        planned,
    )
