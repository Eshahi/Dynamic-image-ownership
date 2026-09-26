"""C1 Windows validation -> exact-byte Linux worker handoff, not approval.

Used only by a future reviewed launcher after official runner authorization.
No model, dataset, Torch, subprocess launcher or network is imported here.
The receipt is provenance from trusted reviewed code, NOT authentication or a
replacement for the compute runner's user decision. Ordinary tests use fixtures.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import sys
from pathlib import Path, PurePosixPath

from src.runtime.config import PROJECT, LoadedConfig, load_method_config, strict_json_bytes
from src.runtime.feasibility import FeasibilityConfig, load_feasibility_config, schema_bytes, VERSION
from .config_binding import validate_loaded_snapshot
from .proposed import EmbeddingError

CONFIG_PATH = "configs/c4-development.json"
EXPERIMENT_ID = "c4-embedding-residency-development-v1"
RECEIPT_NAME = "c4-config-validation.json"
REQUIRED = frozenset({CONFIG_PATH, "configs/method.schema.json",
    "scripts/validate_method_config.py", "scripts/noise_path_reference.py",
    "src/runtime/config.py", "src/embedding/config_binding.py",
    "src/runtime/feasibility.py",
    "src/embedding/validation_bridge.py"})
MAX_FILE_BYTES = 2 * 1024 * 1024


def _json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _digest(value):
    if not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
        raise EmbeddingError("bridge digest is not lowercase SHA-256")
    return value


def _no_links(path):
    path = Path(path)
    if not path.is_absolute() or any(p.is_symlink() or p.is_junction() for p in (path, *path.parents)):
        raise EmbeddingError("bridge paths must be absolute and unlinked")
    return path


def _read(path, *, maximum_bytes=MAX_FILE_BYTES):
    path = _no_links(path)
    if not path.is_file() or path.stat().st_size > maximum_bytes:
        raise EmbeddingError("bridge requires bounded regular files")
    with path.open("rb") as handle:
        raw = handle.read(maximum_bytes + 1)
    if len(raw) > maximum_bytes:
        raise EmbeddingError("bridge input grew past bound")
    return raw


def _relative(name):
    if not isinstance(name, str) or not name or "\\" in name or ":" in name:
        raise EmbeddingError("bridge input needs a plain relative POSIX path")
    parts = PurePosixPath(name).parts
    if name.startswith("/") or any(p in {"", ".", ".."} for p in name.split("/")) or not parts:
        raise EmbeddingError("bridge input escapes or aliases repository")
    return name


def check_inputs(manifest_raw: bytes, root: Path = PROJECT):
    """Recheck small manifest-bound code/config bytes before any model import.

    The official runner validates its complete schema/clean commit/approval.
    This supplementary narrow C4 check cannot authorize execution or establish
    completeness of future worker inputs. No external weight/data paths here.
    """
    root = _no_links(root)
    if len(manifest_raw) > MAX_FILE_BYTES:
        raise EmbeddingError("oversized bridge manifest")
    manifest = strict_json_bytes(manifest_raw)
    if (not isinstance(manifest, dict) or manifest.get("experiment_id") != EXPERIMENT_ID
            or manifest.get("task_id") != "C4" or manifest.get("execution_target") != "local"
            or not isinstance(manifest.get("git_commit"), str)
            or len(manifest["git_commit"]) != 40
            or any(c not in "0123456789abcdef" for c in manifest["git_commit"])
            or not isinstance(manifest.get("run_id"), str)
            or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,127}", manifest["run_id"]) is None):
        raise EmbeddingError("unexpected C4 bridge manifest identity")
    inputs = manifest.get("inputs")
    if not isinstance(inputs, list) or not 1 <= len(inputs) <= 128:
        raise EmbeddingError("bounded C4 input inventory required")
    snapshots, pins = {}, {}
    for item in inputs:
        if not isinstance(item, dict) or set(item) != {"path", "sha256"}:
            raise EmbeddingError("malformed C4 bridge input")
        name, digest = _relative(item["path"]), _digest(item["sha256"])
        if name in snapshots:
            raise EmbeddingError("duplicate C4 bridge input")
        # The immutable admitted CSVs are larger than the small-code/config
        # bound. Only these two named metadata inputs get a 16MiB ceiling;
        # manifest/config/receipt publication remain bounded at 2MiB.
        metadata_csv = name in {"data/splits.csv", "data/b4-admission-20260926/source-manifest.csv"}
        raw = _read(root/name, maximum_bytes=16*1024*1024 if metadata_csv else MAX_FILE_BYTES)
        if _sha(raw) != digest:
            raise EmbeddingError("C4 bridge input hash mismatch")
        snapshots[name], pins[name] = raw, digest
    if not REQUIRED <= set(snapshots):
        raise EmbeddingError("C4 manifest omits full C1 validation dependencies")
    return manifest, snapshots, pins


def _check_executing_validation_code(snapshots):
    # C1 uses its installed PROJECT/VALIDATOR constants, not an arbitrary
    # caller-supplied root. Ensure the actually executing validation sources
    # equal the manifest snapshots even when tests use an owned copied tree.
    for name in REQUIRED - {CONFIG_PATH}:
        if _read(PROJECT/name) != snapshots[name]:
            raise EmbeddingError("executing C1/bridge code differs from manifest snapshots")


def write_validation_receipt(manifest_path: Path, checkpoint_dir: Path, *, root: Path = PROJECT):
    """Trusted future parent launcher only: perform FULL existing C1 validation.

    Receipts are exclusively created in the official run's checkpoints folder,
    never accepted as an input/user verdict or reused across invocations. This
    helper itself does not check/grant compute approval or start any process.
    """
    raw_manifest = _read(manifest_path)
    manifest, snapshots, pins = check_inputs(raw_manifest, root)
    _check_executing_validation_code(snapshots)
    development = strict_json_bytes(snapshots[CONFIG_PATH]).get("schema_version") == VERSION
    loader = load_feasibility_config if development else load_method_config
    loaded = loader(Path(root)/CONFIG_PATH)
    expected_schema = _sha(schema_bytes()) if development else pins["configs/method.schema.json"]
    if loaded.raw != snapshots[CONFIG_PATH] or loaded.schema_sha256 != expected_schema:
        raise EmbeddingError("C1 validated bytes differ from reviewed manifest")
    validate_loaded_snapshot(loaded)
    if manifest.get("seeds") != [loaded.value["embedding"]["noise_seed"]]:
        raise EmbeddingError("C1 config seed differs from exact run seed inventory")
    # Trusted single writer: check again after subprocess validation, before
    # publishing a receipt. This is not an adversarial OS immutability claim.
    if check_inputs(raw_manifest, root)[1] != snapshots:
        raise EmbeddingError("C4 inputs changed during C1 validation")
    checkpoint_dir = _no_links(checkpoint_dir)
    if not checkpoint_dir.is_dir():
        raise EmbeddingError("existing official checkpoint directory required")
    record = {"schema_version": "c4-c1-validated-byte-bridge-v2",
        "manifest_sha256": _sha(_json(manifest)), "git_commit": manifest["git_commit"],
        "experiment_id": manifest["experiment_id"], "run_id": manifest["run_id"],
        "input_sha256": pins, "config_path": CONFIG_PATH,
        "config_raw_hex": loaded.raw.hex(), "config_sha256": loaded.sha256,
        "schema_sha256": loaded.schema_sha256, "config_kind": "feasibility" if development else "final-method",
        "validator_verdict": {"valid_structure": True, "scientific_execution_authorized": False},
        "validation_runtime": {"python": platform.python_version(), "executable": sys.executable},
        "authority": "trusted-reviewed-launcher-provenance-not-user-approval"}
    receipt_path = checkpoint_dir/RECEIPT_NAME
    receipt_raw = _json(record)
    # Hex expansion and inventory overhead must not publish a receipt that
    # the child cannot read under the same bounded-file contract.
    if len(receipt_raw) > MAX_FILE_BYTES:
        raise EmbeddingError("serialized C1 bridge receipt exceeds bounded read contract")
    with receipt_path.open("xb") as handle:
        handle.write(receipt_raw); handle.flush(); os.fsync(handle.fileno())
    return receipt_path


def consume_validation_receipt(manifest_path: Path, checkpoint_dir: Path, *, root: Path = PROJECT):
    """Future Linux child: recheck ALL bound bytes and the parent's C1 receipt.

    Full schema validation happened in the reviewed parent, not in this pure
    stdlib check. A forged self-consistent receipt is not authenticated here;
    only the exact reviewed launcher plus runner approval is a trust boundary.
    """
    manifest, snapshots, pins = check_inputs(_read(manifest_path), root)
    _check_executing_validation_code(snapshots)
    record = strict_json_bytes(_read(Path(checkpoint_dir)/RECEIPT_NAME))
    expected_keys = {"schema_version", "manifest_sha256", "git_commit", "experiment_id", "run_id",
        "input_sha256", "config_path", "config_raw_hex", "config_sha256", "schema_sha256",
        "validator_verdict", "validation_runtime", "authority", "config_kind"}
    if not isinstance(record, dict) or set(record) != expected_keys:
        raise EmbeddingError("malformed C1 bridge receipt")
    development = strict_json_bytes(snapshots[CONFIG_PATH]).get("schema_version") == VERSION
    expected_schema = _sha(schema_bytes()) if development else pins["configs/method.schema.json"]
    expected = {"schema_version": "c4-c1-validated-byte-bridge-v2",
        "manifest_sha256": _sha(_json(manifest)), "git_commit": manifest["git_commit"],
        "experiment_id": manifest["experiment_id"], "run_id": manifest["run_id"],
        "input_sha256": pins, "config_path": CONFIG_PATH,
        "config_raw_hex": snapshots[CONFIG_PATH].hex(), "config_sha256": pins[CONFIG_PATH],
        "schema_sha256": expected_schema, "config_kind": "feasibility" if development else "final-method",
        "validator_verdict": {"valid_structure": True, "scientific_execution_authorized": False},
        "authority": "trusted-reviewed-launcher-provenance-not-user-approval"}
    if any(_json(record[key]) != _json(value) for key, value in expected.items()):
        raise EmbeddingError("C1 receipt does not bind this exact manifest/config/input inventory")
    runtime = record["validation_runtime"]
    if (not isinstance(runtime, dict) or set(runtime) != {"python", "executable"}
            or any(not isinstance(value, str) or not value for value in runtime.values())):
        raise EmbeddingError("missing C1 parent runtime provenance")
    cls = FeasibilityConfig if development else LoadedConfig
    loaded = cls(strict_json_bytes(snapshots[CONFIG_PATH]), snapshots[CONFIG_PATH], pins[CONFIG_PATH], expected_schema)
    validate_loaded_snapshot(loaded)
    if manifest.get("seeds") != [loaded.value["embedding"]["noise_seed"]]:
        raise EmbeddingError("C1 config seed differs from exact run seed inventory")
    return loaded
