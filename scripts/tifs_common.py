"""Stage S immutable identities, journals and frozen endpoints; stdlib only.

No image access or model imports. Journal ownership is single-writer per file;
different worker processes must use separate shard files.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import tempfile
import time

TERMINAL_STATUSES = frozenset({"ok", "safety_blocked", "error_terminal"})
SOURCE_GROUPS = ("screen_donors", "screen_targets", "rehearsal_donors", "rehearsal_targets")


def _reject_constant(value):
    raise ValueError("Non-finite JSON number: " + value)


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key: " + key)
        result[key] = value
    return result


def _loads(value):
    result = json.loads(value, parse_constant=_reject_constant, object_pairs_hook=_unique_object)
    # JSON numeric literals such as 1e999 must also be rejected.
    json.dumps(result, allow_nan=False)
    return result


def load_json(path):
    return _loads(Path(path).read_text(encoding="utf-8-sig"))


def atomic_json(path, value):
    data = (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def sha256_file(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def stable_seed(*parts):
    """Length-unambiguous typed JSON seed, independent of Python hash randomization."""
    raw = json.dumps(list(parts), sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return int.from_bytes(hashlib.sha256(b"tifs-stage-s-seed-v1/" + raw).digest()[:4], "big")


def _row_id(row):
    key = row.get("output_id", row.get("id"))
    if not isinstance(key, str) or not key:
        raise ValueError("Journal row requires a nonempty output_id (or historical id)")
    if "id" in row and "output_id" in row and row["id"] != row["output_id"]:
        raise ValueError("Conflicting journal IDs")
    if not isinstance(row.get("status"), str) or not row["status"]:
        raise ValueError("Journal row requires status")
    return key


class Journal:
    """Last row wins; only an invalid, unterminated final line is recoverable.

    Torn bytes are preserved in a unique sidecar before truncation. A valid
    final row without a newline is retained and newline-terminated on opening.
    Malformed interior or newline-terminated records always raise.
    """
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.latest = {}
        if not self.path.exists():
            return
        raw = self.path.read_bytes()
        lines = raw.splitlines(keepends=True)
        offset = 0
        for i, line in enumerate(lines):
            try:
                row = _loads(line.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                if i != len(lines) - 1 or line.endswith(b"\n"):
                    raise ValueError(f"Malformed journal record {i + 1}: {self.path}")
                tail = self.path.with_name(self.path.name + f".torn-{time.time_ns()}")
                tail.write_bytes(line)
                with self.path.open("r+b") as stream:
                    stream.truncate(offset)
                    stream.flush()
                    os.fsync(stream.fileno())
                break
            key = _row_id(row)
            self.latest[key] = row
            offset += len(line)
            if i == len(lines) - 1 and not line.endswith(b"\n"):
                with self.path.open("ab") as stream:
                    stream.write(b"\n")
                    stream.flush()
                    os.fsync(stream.fileno())

    def done(self, output_id):
        return self.latest.get(output_id, {}).get("status") in TERMINAL_STATUSES

    def append(self, row):
        key = _row_id(row)
        data = (json.dumps(row, sort_keys=True, allow_nan=False) + "\n").encode()
        with self.path.open("ab") as stream:
            if stream.write(data) != len(data):
                raise OSError("Short journal write")
            stream.flush()
            os.fsync(stream.fileno())
        self.latest[key] = _loads(data)


def validate_output(row, root=None):
    """Raise on absent/corrupt successful artifact; terminal failures have no image.

    Successful non-artifact tasks must explicitly set artifact_required=False.
    This prevents a missing image from silently satisfying resume.
    """
    if row.get("status") != "ok":
        return False
    output = row.get("output") or row
    path = output.get("output_path", output.get("path"))
    digest = output.get("output_sha256", output.get("sha256"))
    if path is None and row.get("artifact_required") is False:
        return True
    if not isinstance(path, str) or not isinstance(digest, str) or len(digest) != 64:
        raise ValueError("Successful artifact requires output_path and output_sha256")
    p = Path(path)
    if root is not None:
        root = Path(root).resolve()
        p = p.resolve() if p.is_absolute() else (root / p).resolve()
        if not p.is_relative_to(root):
            raise ValueError("Artifact path escapes output root")
    if not p.is_file() or sha256_file(p) != digest:
        raise ValueError("Missing/corrupt successful output: " + str(p))
    if row.get("tape"):
        validate_output({"status": "ok", "output": row["tape"]}, root=root)
    return True


def majority_bounds(values):
    """Exactly three fixed-seed values, bool or None; returns (lower,upper)."""
    values = list(values)
    if len(values) != 3 or any(v is not None and type(v) is not bool for v in values):
        raise ValueError("Exactly three bool/None values required")
    yes = sum(v is True for v in values)
    unknown = sum(v is None for v in values)
    return yes >= 2, yes + unknown >= 2


def _word(value):
    if isinstance(value, bool):
        return None
    try:
        return int(value, 16) if isinstance(value, str) else int(value) if isinstance(value, int) else None
    except ValueError:
        return None


def predicates(detection, payload=None):
    """Literal frozen E3 predicates, independently importable without NumPy/SciPy.

    Unavailable exact-target diagnostics are false in this historical function;
    q_bit_errors/h_bit_errors=None record that unavailability. Missing whole
    detector outcomes MUST be kept None by callers, never passed as evidence.
    """
    d, target = detection or {}, payload or {}
    s, h = d.get("semantic") or {}, d.get("instance") or {}
    qword, hword = _word(s.get("decoded_code")), _word(h.get("decoded_code"))
    qtarget, htarget = _word(target.get("q")), _word(target.get("h"))
    q = bool(s.get("read") and qword is not None and qtarget is not None and qword == qtarget)
    exact_h = bool(h.get("read") and hword is not None and htarget is not None and hword == htarget)
    result = dict(S=bool(s.get("found") and s.get("content_match")),
                  C=bool(s.get("read") and s.get("content_match")), Q=q,
                  J=bool(q and s.get("content_match")), H=exact_h, D=q and exact_h,
                  F=d.get("outcome") == "both_match", A=bool(s.get("found") or h.get("found")))
    result["recomputed_only_S"] = result["S"] and not bool(s.get("read"))
    result["q_bit_errors"] = (qword ^ qtarget).bit_count() if s.get("read") and qword is not None and qtarget is not None else None
    result["h_bit_errors"] = (hword ^ htarget).bit_count() if h.get("read") and hword is not None and htarget is not None else None
    return result


def _finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def quality_eligible(metrics, psnr=35., ssim=.9, lpips=.1):
    if not isinstance(metrics, dict):
        return False
    p, s, l = metrics.get("psnr_db"), metrics.get("ssim_rgb"), metrics.get("lpips")
    # Exact identity uses JSON null plus an explicit flag, never Infinity JSON.
    valid_p = (_finite(p) and p > psnr) or (p is None and metrics.get("psnr_infinite") is True)
    return bool(valid_p and _finite(s) and s > ssim and _finite(l) and 0 <= l < lpips)


def strict_quality(metrics):
    return quality_eligible(metrics)


def planned_output_ids(config, source_ids):
    """Native inventory only. Other stages own explicit independently frozen IDs."""
    ids = [str(x) for x in source_ids]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate source identities")
    arms, cells, seeds = config["arms"], config["cells"], config["seeds"]
    cells = [cell["id"] if isinstance(cell, dict) else cell for cell in cells]
    if any(len(x) != len(set(x)) for x in (arms, cells, seeds)):
        raise ValueError("Duplicate arm/cell/seed")
    if any("|" in str(x) for x in [*ids, *arms, *cells]):
        raise ValueError("Inventory identity contains reserved delimiter")
    return [f"native:{cell}:{uid}:{seed}:{arm}" for uid in ids for arm in arms for cell in cells for seed in seeds]


native_ids = planned_output_ids


def clean_ids(config, source_ids):
    return [f"clean:{sid}:{arm}" for sid in source_ids for arm in config["arms"]]


def secondary_ids(config, source_ids):
    transforms = config["secondary"]["transforms"]
    return [f"secondary:{t['id']}:{sid}:{arm}" for sid in source_ids for arm in config["arms"] for t in transforms]


def validate_sources(manifest, source_pool=None):
    expected = (16, 16, 2, 2)
    records = []
    pool = {r["source_uid"]: r for r in source_pool["sources"]} if source_pool is not None else None
    for group, n in zip(SOURCE_GROUPS, expected):
        rows = manifest[group]
        if len(rows) != n:
            raise ValueError("Wrong source group count: " + group)
        for row in rows:
            if row.get("data_split") != "development" or not row.get("license"):
                raise ValueError("Only licensed development sources allowed")
            for key in ("raw_sha256", "canonical_png_sha256", "rgb8_sha256"):
                value = row.get(key, "")
                if len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
                    raise ValueError("Bad source hash: " + key)
            if pool is not None:
                original = pool.get(row["source_uid"])
                if original is None or any(row.get(k) != v for k, v in original.items()):
                    raise ValueError("Source differs from frozen development pool")
            records.append(row)
    for key in ("source_uid", "source_id", "raw_sha256", "canonical_png_sha256", "rgb8_sha256"):
        if len({r[key] for r in records}) != len(records):
            raise ValueError("Source groups overlap by " + key)
    if source_pool is not None:
        ordered = sorted(source_pool["sources"], key=lambda r: hashlib.sha256((manifest["selection_prefix"] + r["source_uid"]).encode()).hexdigest())
        if [r["source_uid"] for r in records] != [r["source_uid"] for r in ordered[:36]]:
            raise ValueError("Source selection violates frozen identifier-only order")
    return True


def runtime_identity(config_path, source_manifest_path, code_paths, profile_paths=(), source_paths=()):
    """Snapshot byte hashes; comparing the whole object enforces resume identity."""
    def snapshots(paths):
        return {str(Path(p)): sha256_file(p) for p in paths}
    result = dict(schema="tifs-stage-s-identity-v1", config_sha256=sha256_file(config_path),
                  source_manifest_sha256=sha256_file(source_manifest_path),
                  code=snapshots(code_paths), profiles=snapshots(profile_paths), sources=snapshots(source_paths))
    result["identity_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return result


class ResourceStop(RuntimeError):
    pass


class Budget:
    """Wall-clock guard; call before each indivisible unit, never during it."""
    def __init__(self, max_seconds, *, start_time=None, clock=time.monotonic, reserve_seconds=3600, elapsed_seconds=0):
        seconds = max_seconds
        if any(not _finite(v) or v < 0 for v in (seconds, reserve_seconds, elapsed_seconds)):
            raise ValueError("Nonnegative finite budget values required")
        self.seconds, self.reserve_seconds = seconds, reserve_seconds
        self.clock, self.start, self.prior_elapsed = clock, clock() if start_time is None else start_time, elapsed_seconds

    @property
    def elapsed(self):
        return self.prior_elapsed + max(0, self.clock() - self.start)

    @property
    def remaining(self):
        return max(0, self.seconds - self.elapsed)

    def can_start(self, estimated_seconds):
        if not _finite(estimated_seconds) or estimated_seconds < 0:
            raise ValueError("Finite nonnegative unit estimate required")
        return self.remaining >= estimated_seconds + self.reserve_seconds

    def require(self, estimated_seconds):
        if not self.can_start(estimated_seconds):
            raise ResourceStop("RESOURCE_STOP: next unit plus retrieval reserve exceeds wall-clock budget")

    @staticmethod
    def forecast(one_time_seconds, measured_variable_seconds, retrieval_seconds=3600, ceiling_seconds=54000):
        vals = (one_time_seconds, measured_variable_seconds, retrieval_seconds, ceiling_seconds)
        if any(not _finite(v) or v < 0 for v in vals):
            raise ValueError("Invalid forecast input")
        total = one_time_seconds + 1.5 * measured_variable_seconds + retrieval_seconds
        return {"forecast_seconds": total, "within_budget": total <= ceiling_seconds}
