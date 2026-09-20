"""Shared contracts, path boundaries and deterministic serialization."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path, PureWindowsPath
import re
import sys
from datetime import datetime, timezone

class ContractError(ValueError):
    pass

def now():
    return datetime.now(timezone.utc).isoformat()

def timestamp(value):
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if result.tzinfo is None:
            raise ValueError()
        return result
    except (ValueError, TypeError, AttributeError):
        raise ContractError("Expected timezone-aware ISO 8601 timestamp") from None

def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,127}", value):
        raise ContractError("Invalid identifier; identifiers are never repaired")
    return value

def relative(value):
    if not isinstance(value, str) or not value or "\x00" in value:
        raise ContractError("Invalid relative path")
    win = PureWindowsPath(value)
    parts = value.replace("\\", "/").split("/")
    if win.drive or win.root or value.startswith("/") or any(p in ("", ".", "..") or ":" in p for p in parts):
        raise ContractError("Path must be a contained portable relative path")
    return Path(*parts)

def contained(root, value):
    root = Path(root).resolve()
    path = root / relative(value)
    current = root
    for part in path.relative_to(root).parts:
        current = current / part
        if current.is_symlink() or (hasattr(current, "is_junction") and current.is_junction()):
            raise ContractError("Links are not allowed in artifact paths")
    if not path.resolve().is_relative_to(root):
        raise ContractError("Path escapes root")
    return path

def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))

def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def object_digest(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()).hexdigest()

def write(path, value, force=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    content = value if isinstance(value, str) else json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    # Exclusive creation by default. Atomic replace only when explicitly requested.
    if not force:
        with path.open("x", encoding="utf-8", newline="\n") as f:
            f.write(content)
    else:
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as f:
            f.write(content)
            name = f.name
        os.replace(name, path)

def fresh_dir(path):
    path = Path(path)
    path.mkdir(parents=True, exist_ok=False)
    return path

def redact(value):
    text = str(value)
    for key, secret in os.environ.items():
        if re.search(r"TOKEN|SECRET|PASSWORD|API_KEY", key, re.I) and len(secret) >= 4:
            text = text.replace(secret, "[REDACTED]")
    text = re.sub(r"(?i)(bearer\s+)[\w.\-]+", r"\1[REDACTED]", text)
    text = re.sub(r"(?i)((?:api[_-]?key|token|password|secret)\s*[=:]\s*)[^\s,;]+", r"\1[REDACTED]", text)
    return text

def safe_env():
    # NVML discovery on Windows depends on ProgramFiles (or ProgramW6432).
    # These are non-secret installation roots and are safe to pass through.
    allowed = {
        "PATH", "SYSTEMROOT", "WINDIR", "TEMP", "TMP", "HOME", "USERPROFILE",
        "LANG", "LC_ALL", "VIRTUAL_ENV", "PROGRAMFILES", "PROGRAMW6432",
    }
    result = {k: v for k, v in os.environ.items() if k.upper() in allowed}
    result.update(PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1")
    return result

def schema_path(name):
    return Path(__file__).parent / "schemas" / (name + ".schema.json")

def validate(data, name):
    try:
        from jsonschema import Draft202012Validator, FormatChecker
    except ImportError:
        raise ContractError("Install pinned dependencies: jsonschema==4.26.0 PyYAML==6.0.3") from None
    errors = sorted(Draft202012Validator(read(schema_path(name)), format_checker=FormatChecker()).iter_errors(data), key=lambda e: str(list(e.path)))
    if errors:
        raise ContractError("; ".join(f"{'.'.join(map(str,e.path)) or '$'}: {e.message}" for e in errors))
    return data

def cli_entry(fn):
    try:
        result = fn()
        if result is not None:
            print(json.dumps(result, ensure_ascii=True, allow_nan=False))
        return 0
    except (ContractError, FileExistsError, FileNotFoundError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": redact(exc), "type": type(exc).__name__}), file=sys.stderr)
        return 2

def parser(description):
    p = argparse.ArgumentParser(description=description)
    p.add_argument("--json", action="store_true", help="Stable JSON output (also the default)")
    return p
