"""Read-only byte audit of the pinned CLIP wheel against its installed files.

This is a source-package integrity check, not a checkpoint load or inference.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path


EXPECTED_COMMIT = "d05afc436d78f1c48dc0dbf8e5980a9d471f35f6"
EXPECTED_URL = "https://github.com/openai/CLIP.git"
EXPECTED_WHEEL_SHA256 = "68fc1aa1fc25591c3c61e621cfd47b6f8e19536901db70f5da0c1af1ba485969"
SOURCE_FILES = (
    "clip/__init__.py",
    "clip/bpe_simple_vocab_16e6.txt.gz",
    "clip/clip.py",
    "clip/model.py",
    "clip/simple_tokenizer.py",
)


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def digest_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _regular_file(path: Path) -> None:
    if not path.is_file() or path.is_symlink() or path.is_junction():
        raise ValueError(f"missing or linked file: {path.name}")


def _origin(path: Path) -> None:
    _regular_file(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    info = data.get("vcs_info", {})
    if (data.get("url") != EXPECTED_URL or info.get("vcs") != "git"
            or info.get("commit_id") != EXPECTED_COMMIT
            or info.get("requested_revision") != EXPECTED_COMMIT):
        raise ValueError("CLIP source origin differs from pinned commit")


def audit(wheel: Path, origin: Path, site_packages: Path) -> dict[str, object]:
    _regular_file(wheel)
    if digest_file(wheel) != EXPECTED_WHEEL_SHA256:
        raise ValueError("cached CLIP wheel digest differs from recorded candidate")
    _origin(origin)
    if not site_packages.is_dir() or site_packages.is_symlink() or site_packages.is_junction():
        raise ValueError("site-packages must be a non-link directory")
    for relative_dir in ("clip", "clip-1.0.dist-info"):
        directory = site_packages / relative_dir
        if not directory.is_dir() or directory.is_symlink() or directory.is_junction():
            raise ValueError(f"installed CLIP directory is missing or linked: {relative_dir}")
    _origin(site_packages / "clip-1.0.dist-info/direct_url.json")

    verified: dict[str, str] = {}
    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())
        if not set(SOURCE_FILES).issubset(names):
            raise ValueError("cached wheel lacks pinned CLIP source inventory")
        for relative in SOURCE_FILES:
            installed = site_packages / relative
            _regular_file(installed)
            expected = digest_bytes(archive.read(relative))
            if digest_file(installed) != expected:
                raise ValueError(f"installed CLIP source differs from cached wheel: {relative}")
            verified[relative] = expected
    return {
        "status": "pinned_clip_source_files_match_cached_wheel",
        "source_commit": EXPECTED_COMMIT,
        "wheel_sha256": EXPECTED_WHEEL_SHA256,
        "source_file_sha256": verified,
        "source_file_count": len(verified),
        "limits": "not a checkpoint/model-load, build attestation, complete distribution or runtime parity",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheel", type=Path, required=True)
    parser.add_argument("--origin", type=Path, required=True)
    parser.add_argument("--site-packages", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(audit(args.wheel, args.origin, args.site_packages), sort_keys=True))


if __name__ == "__main__":
    main()
