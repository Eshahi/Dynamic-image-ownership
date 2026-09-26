"""Exact C1 config snapshot -> immutable component computation binding.

This verifies the supplied C1 snapshot, not compute permission. Full schema
validation is done by C1 before construction; a worker may not fabricate one.
"""
import hashlib
import json
from dataclasses import asdict, dataclass

from src.runtime.config import LoadedConfig, SCHEMA, strict_json_bytes
from .proposed import EmbeddingError, Settings


def validate_loaded_snapshot(loaded):
    if (not isinstance(loaded, LoadedConfig) or hashlib.sha256(loaded.raw).hexdigest() != loaded.sha256
            or strict_json_bytes(loaded.raw) != loaded.value
            or hashlib.sha256(SCHEMA.read_bytes()).hexdigest() != loaded.schema_sha256):
        raise EmbeddingError("C1 config snapshot/value/schema identity changed or absent")
    value = loaded.value
    dct = dict(value["dct"])
    claimed = dct.pop("config_id")
    static = {"feature": value["feature"], "signature": value["signature"], "dct": dct}
    raw = json.dumps(static, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")
    if hashlib.sha256(raw).hexdigest() != claimed:
        raise EmbeddingError("static detector configuration ID mismatch")
    return value


@dataclass(frozen=True)
class ConfigBinding:
    config_hash: str
    schema_hash: str
    detector_config_id: str
    seed: int
    settings_json: bytes
    source_tensor_sha256: str | None


def bind_settings(loaded, settings, seed, config_id, *, source_tensor_sha256=None):
    value = validate_loaded_snapshot(loaded)
    if (Settings.from_embedding_config(value["embedding"]) != settings
            or value["embedding"]["noise_seed"] != seed
            or value["dct"]["config_id"] != config_id.hex()):
        raise EmbeddingError("computation settings/seed/static ID differ from exact C1 config")
    return ConfigBinding(loaded.sha256, loaded.schema_sha256, config_id.hex(), seed,
                         json.dumps(asdict(settings), sort_keys=True, separators=(",", ":"), allow_nan=False).encode("ascii"),
                         source_tensor_sha256)
