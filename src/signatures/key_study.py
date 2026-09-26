"""C6 precomputed-observation ledger; no model, pixel decode or execution.

Caller must separately establish image-to-feature/pHash custody in an approved
run. Validating these values does not certify that they came from an image.
"""
from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from .owner import canonical_owner, derive_public_signatures, pack_fields
from .semantic import quantize_features

DOMAINS = {"ms-coco", "div2k", "diffusiondb"}
LABELS = {
    "same_image_repeat": ("positive", "positive"),
    "same_image_benign": ("positive", "positive"),
    "wrong_owner": ("negative", "negative"),
    "same_topic_distinct": ("positive", "negative"),
    "near_instance": ("unresolved", "unresolved"),
    "unrelated": ("negative", "negative"),
    "distinct_unscreened": ("unresolved", "negative"),
}


class KeyStudyError(ValueError):
    pass


def _text(value):
    if not isinstance(value, str) or not value or len(value.encode("utf-8")) > 4096:
        raise KeyStudyError("nonempty bounded text required")
    return value


@dataclass(frozen=True)
class Sample:
    sample_id: str
    source_uid: str
    group_id: str
    domain: str
    variant: str
    split: str = "development"

    def validate(self):
        for value in (self.sample_id, self.source_uid, self.group_id, self.variant):
            _text(value)
        if self.domain not in DOMAINS or self.split != "development":
            raise KeyStudyError("only explicit development sources in declared domains")


@dataclass(frozen=True)
class Pair:
    pair_id: str
    left: str
    right: str
    left_owner: str
    right_owner: str
    relation: str
    evidence_ref: str


@dataclass(frozen=True)
class Observation:
    status: str
    features: tuple[float, ...] | None = None
    phash: bytes | None = None
    error: str | None = None

    def validate(self, projection_seed):
        if self.status == "completed":
            if self.error is not None or not isinstance(self.features, tuple):
                raise KeyStudyError("completed observation requires immutable features, no error")
            quantize_features(self.features, projection_seed)
            derive_public_signatures(bytes(2), self.phash, "c6:validation")
        elif self.status in ("failed", "pending"):
            if self.features is not None or self.phash is not None:
                raise KeyStudyError("missing observations cannot carry invented measurements")
            if self.status == "failed":
                _text(self.error)
            elif self.error is not None:
                raise KeyStudyError("pending is not a terminal failure")
        else:
            raise KeyStudyError("unknown observation status")


def validate_plan(samples, pairs):
    """Explicit labels only: a same-domain pair is not automatically same-topic."""
    if type(samples) not in (list, tuple) or type(pairs) not in (list, tuple):
        raise KeyStudyError("replayable list/tuple inventories required; no one-shot iterators")
    if not samples or not pairs:
        raise KeyStudyError("nonempty predeclared sample and pair inventory required")
    index, sources = {}, {}
    for sample in samples:
        if not isinstance(sample, Sample):
            raise KeyStudyError("typed sample required")
        sample.validate()
        if sample.sample_id in index:
            raise KeyStudyError("duplicate sample ID")
        source = (sample.group_id, sample.domain, sample.split)
        if sample.source_uid in sources and sources[sample.source_uid] != source:
            raise KeyStudyError("source cannot change domain, group or split across variants")
        sources[sample.source_uid] = source
        index[sample.sample_id] = sample
    seen = set()
    for pair in pairs:
        if not isinstance(pair, Pair) or pair.relation not in LABELS:
            raise KeyStudyError("typed declared relation required")
        _text(pair.pair_id)
        _text(pair.evidence_ref)
        if pair.pair_id in seen or pair.left not in index or pair.right not in index:
            raise KeyStudyError("duplicate pair ID or missing pair member")
        seen.add(pair.pair_id)
        left, right = index[pair.left], index[pair.right]
        lo, ro = canonical_owner(pair.left_owner)[1], canonical_owner(pair.right_owner)[1]
        same_source = left.source_uid == right.source_uid
        if pair.relation in ("same_image_repeat", "same_image_benign", "wrong_owner"):
            if not same_source:
                raise KeyStudyError("same-image/owner control requires the same source")
        elif same_source:
            raise KeyStudyError("distinct-content relation requires distinct source IDs")
        if (lo != ro) != (pair.relation == "wrong_owner"):
            raise KeyStudyError("wrong-owner must be distinct; other pairs must keep owner fixed")
        if pair.relation == "wrong_owner" and pair.left != pair.right:
            raise KeyStudyError("wrong-owner isolates only owner change on one observation")
        if pair.relation in ("same_image_repeat", "same_image_benign") and pair.left == pair.right:
            raise KeyStudyError("repeat/edit requires separately recorded observations")
    return index


def dependency_components(samples, pairs):
    """Union source groups through ALL planned pairs, including failed/missing ones.

    Component count is descriptive, not a certification of independent samples.
    Connected pairs never acquire independence by having different pair IDs.
    """
    index = validate_plan(samples, pairs)
    parent = {sample.group_id: sample.group_id for sample in samples}

    def root(node):
        while parent[node] != node:
            node = parent[node]
        return node

    for pair in pairs:
        a, b = root(index[pair.left].group_id), root(index[pair.right].group_id)
        parent[max(a, b)] = min(a, b)
    groups = {}
    for group in sorted(parent):
        groups.setdefault(root(group), []).append(group)
    ids = {key: hashlib.sha256(pack_fields(*(g.encode("utf-8") for g in value))).hexdigest()
           for key, value in groups.items()}
    return {sample.sample_id: ids[root(sample.group_id)] for sample in samples}


def _distance(a, b):
    return sum((x ^ y).bit_count() for x, y in zip(a, b))


def evaluate(samples, pairs, observations, projection_seed):
    """Evaluate exact inventory; absent inputs remain pending, never zero-distance.

    Malformed supplied observations block the package; explicit extraction
    failures propagate as failed rows. No detector score/threshold is inferred.
    """
    index = validate_plan(samples, pairs)
    if not isinstance(projection_seed, bytes) or len(projection_seed) != 32:
        raise KeyStudyError("exact immutable 32-byte projection seed required")
    if not isinstance(observations, dict) or set(observations) - set(index):
        raise KeyStudyError("unexpected observation ID")
    for observation in observations.values():
        if not isinstance(observation, Observation):
            raise KeyStudyError("typed observation required")
        observation.validate(projection_seed)
    components = dependency_components(samples, pairs)
    rows = []
    for pair in pairs:
        left, right = index[pair.left], index[pair.right]
        a = observations.get(pair.left, Observation("pending"))
        b = observations.get(pair.right, Observation("pending"))
        row = {
            "pair_id": pair.pair_id, "image_id": left.source_uid,
            "paired_image_id": right.source_uid, "group_id": left.group_id,
            "paired_group_id": right.group_id, "dependency_component": components[pair.left],
            "domain": left.domain, "paired_domain": right.domain,
            "transform": pair.relation, "left_variant": left.variant,
            "right_variant": right.variant, "evidence_ref": pair.evidence_ref,
            "semantic_label": LABELS[pair.relation][0], "instance_label": LABELS[pair.relation][1],
            "status": "pending", "error": None,
            **{key: None for key in ("representation_distance", "q_distance", "phash_distance",
                "ws_distance", "wi_distance", "ws_exact_match", "wi_exact_match")},
        }
        if "failed" in (a.status, b.status):
            row.update(status="failed", error="; ".join(
                f"{member}: {item.error}" for member, item in ((pair.left, a), (pair.right, b))
                if item.status == "failed"))
        elif a.status == b.status == "completed":
            qa = quantize_features(a.features, projection_seed).packed
            qb = quantize_features(b.features, projection_seed).packed
            ka = derive_public_signatures(qa, a.phash, pair.left_owner)
            kb = derive_public_signatures(qb, b.phash, pair.right_owner)
            # Norm-correct cosine, not 1-dot where float32 norm error makes
            # identical vectors appear different or yields a negative distance.
            dot = math.fsum(x*y for x, y in zip(a.features, b.features))
            norm = math.sqrt(math.fsum(x*x for x in a.features) *
                             math.fsum(x*x for x in b.features))
            row.update(status="completed", representation_distance=1-max(-1., min(1., dot/norm)),
                       q_distance=_distance(qa, qb), phash_distance=_distance(a.phash, b.phash),
                       ws_distance=_distance(ka.semantic, kb.semantic),
                       wi_distance=_distance(ka.instance, kb.instance),
                       ws_exact_match=ka.semantic == kb.semantic,
                       wi_exact_match=ka.instance == kb.instance)
        rows.append(row)
    return rows


def summarize(rows):
    """Descriptive pair strata only; no pair-binomial CI or efficacy verdict.

    Missing rows are separate and numerator/denominator for completed-only
    agreement stays explicit. No missing observation is a measured collision.
    """
    strata = {}
    seen = set()
    for row in rows:
        if row["pair_id"] in seen:
            raise KeyStudyError("duplicate result pair")
        seen.add(row["pair_id"])
        for component, label, match in (("Ws", row["semantic_label"], row["ws_exact_match"]),
                                        ("Wi", row["instance_label"], row["wi_exact_match"])):
            key = (row["domain"], row["paired_domain"], row["transform"], component, label)
            cell = strata.setdefault(key, {"planned": 0, "completed": 0, "failed": 0,
                "pending": 0, "exact_matches": 0, "dependency_components": set()})
            status = row["status"]
            if status not in ("completed", "failed", "pending"):
                raise KeyStudyError("unknown result status")
            if (status == "completed" and type(match) is not bool) or (status != "completed" and match is not None):
                raise KeyStudyError("missing exact-match must not become measured zero")
            cell["planned"] += 1
            cell[status] += 1
            cell["exact_matches"] += int(match is True)
            cell["dependency_components"].add(row["dependency_component"])
    return [{"domain": key[0], "paired_domain": key[1], "relation": key[2],
             "component": key[3], "label": key[4],
             **{k: v for k, v in value.items() if k != "dependency_components"},
             "dependence_component_count": len(value["dependency_components"]),
             "completed_only_exact_rate": value["exact_matches"]/value["completed"] if value["completed"] else None,
             "independent_n": None, "confidence_interval": None,
             "inference_status": "UNRESOLVED_DEPENDENCE_AND_PROTOCOL"}
            for key, value in sorted(strata.items())]
