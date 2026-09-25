"""Load an A5 method configuration only after its existing contract passes."""

from __future__ import annotations

import hashlib
import json
import math
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROJECT = Path(__file__).resolve().parents[2]
SCHEMA = PROJECT / "configs" / "method.schema.json"
VALIDATOR = PROJECT / "scripts" / "validate_method_config.py"


class ConfigError(ValueError):
    """A configuration failed a check before any run was created."""


def _object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for name, value in pairs:
        if name in result:
            raise ConfigError(f"duplicate JSON key: {name}")
        result[name] = value
    return result


def _reject_constant(value: str) -> None:
    raise ConfigError(f"nonfinite JSON constant: {value}")


def strict_json_bytes(raw: bytes) -> Any:
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_object_pairs,
                           parse_constant=_reject_constant)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise ConfigError("configuration is not strict UTF-8 JSON") from error

    def check(item: Any) -> None:
        if isinstance(item, float) and not math.isfinite(item):
            raise ConfigError("configuration contains a nonfinite number")
        if isinstance(item, dict):
            for child in item.values():
                check(child)
        if isinstance(item, list):
            for child in item:
                check(child)

    check(value)
    return value


def regular_bytes(path: Path) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise ConfigError("configuration or schema must be a regular non-link file")
    return path.read_bytes()


@dataclass(frozen=True)
class LoadedConfig:
    value: dict[str, Any]
    raw: bytes
    sha256: str
    schema_sha256: str


def load_method_config(path: Path) -> LoadedConfig:
    """Reuse A5's schema and cross-field validator; never substitute a shape-only check."""
    path = Path(path)
    raw = regular_bytes(path)
    value = strict_json_bytes(raw)
    if not isinstance(value, dict):
        raise ConfigError("method configuration must be an object")
    schema_bytes = regular_bytes(SCHEMA)
    if not VALIDATOR.is_file() or VALIDATOR.is_symlink():
        raise ConfigError("A5 contract validator is unavailable")
    try:
        # Validate the very bytes returned to the caller, not a file that may
        # change between our read and the A5 subprocess read.
        with tempfile.TemporaryDirectory(prefix="c1-config-check-") as temporary:
            snapshot = Path(temporary)
            checked_config = snapshot / "method.json"
            checked_schema = snapshot / "method.schema.json"
            checked_config.write_bytes(raw)
            checked_schema.write_bytes(schema_bytes)
            checked = subprocess.run(
                [sys.executable, str(VALIDATOR), "--schema", str(checked_schema),
                 "--config", str(checked_config)],
                cwd=PROJECT, capture_output=True, text=True, timeout=30, check=False,
            )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise ConfigError("A5 contract validation could not complete") from error
    if checked.returncode != 0:
        raise ConfigError("A5 method configuration contract rejected the file")
    try:
        verdict = json.loads(checked.stdout)
    except json.JSONDecodeError as error:
        raise ConfigError("A5 validator returned no structured verdict") from error
    if verdict != {"valid_structure": True, "scientific_execution_authorized": False}:
        raise ConfigError("A5 validator returned an unexpected verdict")
    return LoadedConfig(value, raw, hashlib.sha256(raw).hexdigest(),
                        hashlib.sha256(schema_bytes).hexdigest())
