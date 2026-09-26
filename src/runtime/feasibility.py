"""Strict C4 development configuration: same method, NO calibrated decision.

Final C1 schema and loader remain separate and reject this profile. This type
cannot claim scientific success, calibration or compute approval. Full schema
and unchanged cross-field checks run in the trusted Windows controller.
"""
import copy
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from .config import LoadedConfig, SCHEMA, regular_bytes, strict_json_bytes, _load_config_against_schema

PROFILE = "public-derived-existing-image-feasibility"
VERSION = "c4-feasibility-v1"
CALIBRATION = {"status": "not-calibrated-development-only", "decision": "prohibited", "thresholds": "absent"}


@dataclass(frozen=True)
class FeasibilityConfig(LoadedConfig):
    """Distinct from final method config; trusted-code provenance, not authentication."""


def schema_bytes():
    schema = copy.deepcopy(strict_json_bytes(regular_bytes(SCHEMA)))
    schema["$id"] = "https://github.com/Eshahi/Dynamic-image-ownership/c4-feasibility-v1"
    schema["title"] = "C4 development mechanism feasibility without threshold decisions"
    schema["description"] = "Same pinned A5 embedding; no threshold, detection label, C4 scientific acceptance or permission."
    schema["properties"]["schema_version"] = {"const": VERSION}
    schema["properties"]["profile"] = {"const": PROFILE}
    schema["properties"]["calibration"] = {"const": CALIBRATION}
    return json.dumps(schema, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def load_feasibility_config(path: Path):
    loaded = _load_config_against_schema(path, schema_bytes())
    return FeasibilityConfig(loaded.value, loaded.raw, loaded.sha256, loaded.schema_sha256)


def assert_feasibility_identity(loaded):
    if (type(loaded) is not FeasibilityConfig or loaded.schema_sha256 != hashlib.sha256(schema_bytes()).hexdigest()
            or loaded.value.get("schema_version") != VERSION or loaded.value.get("profile") != PROFILE
            or loaded.value.get("calibration") != CALIBRATION):
        raise ValueError("wrong development type/schema or calibrated-decision claim")
