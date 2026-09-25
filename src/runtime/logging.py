"""Create immutable per-run provenance and preserve failed/interrupted attempts.

This module records evidence only. It neither approves nor executes scientific compute.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
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
    start: dict[str, Any]

    def finish(self, *, status: str, outputs: Mapping[str, Path] | None = None,
               failure: str | None = None) -> Path:
        """Write the final manifest once; an absent final manifest means interrupted."""
        if status not in {"succeeded", "failed"}:
            raise RunLogError("final status must be succeeded or failed")
        if (status == "failed") != bool(failure):
            raise RunLogError("failed runs need a reason; successful runs cannot have one")
        if failure is not None and (len(failure) > 2048 or not failure.strip()):
            raise RunLogError("failure reason must be nonempty and bounded")
        evidence: dict[str, dict[str, Any]] = {}
        for label, path in (outputs or {}).items():
            if not isinstance(label, str) or not label or label in evidence:
                raise RunLogError("output labels must be unique nonempty strings")
            resolved = _regular(Path(path)).resolve()
            if not resolved.is_relative_to(self.directory.resolve()):
                raise RunLogError("output must reside in this run directory")
            evidence[label] = _file_evidence(resolved)
        manifest = {**self.start, "ended_at": _now(), "status": status,
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
    directory.mkdir(exist_ok=False)
    start = {"schema_version": "c1-run-v1", "run_id": run_id,
             "started_at": _now(), "code": code,
             "config": {"file": "config.json", "sha256": loaded.sha256,
                        "schema_sha256": loaded.schema_sha256},
             "inputs": input_evidence, "environment": environment,
             "seeds": dict(seeds), "parameters": json.loads(encoded_parameters),
             "python_version": sys.version.split()[0],
             "scientific_execution_authorized": False}
    _write_once(directory / "config.json", loaded.raw)
    _write_once(directory / "start.json", _json_bytes(start))
    return RunRecord(directory, start)


@contextmanager
def recorded_run(root: Path, *, config_path: Path, inputs: Mapping[str, Path],
                 environment_receipt: Path, seeds: Mapping[str, int],
                 parameters: Mapping[str, Any]) -> Iterator[RunRecord]:
    """Preserve ordinary exceptions as failed runs without logging sensitive text.

    A process kill can only leave ``start.json``; consumers must classify that as
    interrupted, never as a success. The caller may explicitly finalize outputs
    inside the block; otherwise normal exit finalizes an empty-output success.
    """
    record = start_run(root, config_path=config_path, inputs=inputs,
                       environment_receipt=environment_receipt, seeds=seeds,
                       parameters=parameters)
    try:
        yield record
    except BaseException as error:
        if not (record.directory / "manifest.json").exists():
            record.finish(status="failed", failure=type(error).__name__)
        raise
    else:
        if not (record.directory / "manifest.json").exists():
            record.finish(status="succeeded")
