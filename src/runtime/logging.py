"""Create immutable per-run provenance and preserve failed/interrupted attempts.

This module records evidence only. It neither approves nor executes scientific compute.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator, Mapping

from .config import LoadedConfig, PROJECT, load_method_config


class RunLogError(ValueError):
    """A run log failed a provenance or immutability check."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _regular(path: Path) -> Path:
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise RunLogError("evidence input/output must be a regular non-link file")
    return path


def _json_bytes(value: Any) -> bytes:
    try:
        return (json.dumps(value, sort_keys=True, ensure_ascii=False,
                           separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")
    except (TypeError, ValueError) as error:
        raise RunLogError("run metadata must be finite JSON") from error


def _write_once(path: Path, raw: bytes) -> None:
    with path.open("xb") as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())


def _git_code() -> dict[str, str]:
    def git(*arguments: str) -> str:
        completed = subprocess.run(["git", *arguments], cwd=PROJECT,
                                   capture_output=True, text=True, check=False,
                                   timeout=15)
        if completed.returncode != 0:
            raise RunLogError("Git code provenance could not be captured")
        return completed.stdout.strip()

    revision = git("rev-parse", "HEAD")
    if len(revision) != 40:
        raise RunLogError("Git revision is malformed")
    if git("status", "--porcelain", "--untracked-files=all"):
        raise RunLogError("run code checkout must be clean before execution")
    return {"git_commit": revision, "git_state": "clean"}


def _file_evidence(path: Path) -> dict[str, Any]:
    path = _regular(path)
    return {"path": str(path.resolve()), "size_bytes": path.stat().st_size,
            "sha256": _sha256(path)}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class RunRecord:
    directory: Path
    start_raw: bytes

    def finish(self, *, status: str, failure: str | None = None) -> Path:
        """Write the final manifest once; an absent final manifest means interrupted."""
        if status not in {"succeeded", "failed"}:
            raise RunLogError("final status must be succeeded or failed")
        if (status == "failed") != bool(failure):
            raise RunLogError("failed runs need a reason; successful runs cannot have one")
        if failure is not None and (len(failure) > 2048 or not failure.strip()):
            raise RunLogError("failure reason must be nonempty and bounded")
        if (self.directory / "start.json").read_bytes() != self.start_raw:
            raise RunLogError("start record changed after creation")
        original = json.loads(self.start_raw)
        config_file = _regular(self.directory / "config.json")
        if _sha256(config_file) != original["config"]["sha256"]:
            raise RunLogError("config snapshot changed after creation")
        evidence: dict[str, dict[str, Any]] = {}
        for path in sorted(self.directory.rglob("*")):
            relative = path.relative_to(self.directory).as_posix()
            if path.is_symlink():
                raise RunLogError("linked run artifact is forbidden")
            if path.is_dir():
                continue
            if not path.is_file():
                raise RunLogError("unsupported run artifact")
            if relative in {"config.json", "start.json"}:
                continue
            if relative == "manifest.json":
                raise RunLogError("run manifest already finalized")
            evidence[relative] = _file_evidence(path)
        manifest = {**original, "ended_at": _now(), "status": status,
                    "outputs": evidence, "failure": failure,
                    "scientific_execution_authorized": False}
        final = self.directory / "manifest.json"
        try:
            _write_once(final, _json_bytes(manifest))
        except FileExistsError as error:
            raise RunLogError("run manifest already finalized") from error
        return final


def start_run(root: Path, *, config_path: Path, inputs: Mapping[str, Path],
              environment_receipt: Path, seeds: Mapping[str, int],
              parameters: Mapping[str, Any]) -> RunRecord:
    """Validate all declared evidence before creating the unique run directory."""
    loaded: LoadedConfig = load_method_config(config_path)
    if not inputs or not seeds:
        raise RunLogError("run inputs and explicit seeds are required")
    if any(not isinstance(name, str) or not name for name in inputs):
        raise RunLogError("input labels must be nonempty strings")
    if any(not isinstance(name, str) or not name or isinstance(seed, bool)
           or not isinstance(seed, int) or seed < 0 for name, seed in seeds.items()):
        raise RunLogError("seeds must be named nonnegative integers")
    if not isinstance(parameters, Mapping):
        raise RunLogError("parameters must be a mapping")
    encoded_parameters = _json_bytes(dict(parameters))
    input_evidence = {name: _file_evidence(Path(path)) for name, path in inputs.items()}
    environment = _file_evidence(Path(environment_receipt))
    code = _git_code()
    root = Path(root)
    if root.is_symlink() or not root.is_dir():
        raise RunLogError("run root must be an existing non-link directory")
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex
    directory = root / run_id
    start = {"schema_version": "c1-run-v1", "run_id": run_id,
             "started_at": _now(), "code": code,
             "config": {"file": "config.json", "sha256": loaded.sha256,
                        "schema_sha256": loaded.schema_sha256},
             "inputs": input_evidence, "environment": environment,
             "seeds": dict(seeds), "parameters": json.loads(encoded_parameters),
             "python_version": sys.version.split()[0],
             "scientific_execution_authorized": False}
    start_raw = _json_bytes(start)
    staging = Path(tempfile.mkdtemp(prefix=f".staging-{run_id}-", dir=root))
    # The canonical run directory appears only after both records are durable.
    # A hard interruption before rename leaves a visible .staging-* directory,
    # not a falsely started run. Do not erase that evidence automatically.
    _write_once(staging / "config.json", loaded.raw)
    _write_once(staging / "start.json", start_raw)
    staging.rename(directory)
    return RunRecord(directory, start_raw)


@contextmanager
def recorded_run(root: Path, *, config_path: Path, inputs: Mapping[str, Path],
                 environment_receipt: Path, seeds: Mapping[str, int],
                 parameters: Mapping[str, Any]) -> Iterator[Path]:
    """Preserve ordinary exceptions as failed runs without logging sensitive text.

    A process kill can only leave ``start.json``; consumers must classify that as
    interrupted, never as a success. Yield only the output directory so the
    context owns finalization and cannot record success before later failure.
    """
    record = start_run(root, config_path=config_path, inputs=inputs,
                       environment_receipt=environment_receipt, seeds=seeds,
                       parameters=parameters)
    try:
        yield record.directory
    except BaseException as error:
        record.finish(status="failed", failure=type(error).__name__)
        raise
    else:
        record.finish(status="succeeded")
