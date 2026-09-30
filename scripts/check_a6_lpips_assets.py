"""Offline A6 LPIPS byte preflight; never imports Torch or constructs a metric.

The result is a prerequisite for a future separately authorized two-weight
compatibility test, not evidence of LPIPS numerical validity or use rights.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from verify_science_assets import verify


LOCK_SHA256 = "b8c2595857853ea5b7835bb71f12a34dde07b78623c5e638f692dc7eb220b27e"
PACKAGE_FILES = {
    "lpips.py": "780d09b907cb9b661e0ae28b2d163ddfba92f9e870d7feba34d4790cc6590658",
    "pretrained_networks.py": "6a27f714c51796db466e86bebba6a617c1bfc4d566f3a1756497629c1248686e",
    "__init__.py": "36ee004a45e2cc2c5ab47fa3955f00c0e41f6a151ef0249fb6f362533ed58b22",
    "weights/v0.1/alex.pth": "df73285e35b22355a2df87cdb6b70b343713b667eddbda73e1977e0c860835c0",
}


def _file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_package(package_root: Path) -> dict[str, str]:
    if not package_root.is_dir() or package_root.is_symlink() or package_root.is_junction():
        raise ValueError("LPIPS package root must be an existing non-link directory")
    result = {}
    for relative, expected in PACKAGE_FILES.items():
        path = package_root
        for part in relative.split("/"):
            path = path / part
            if path.is_symlink() or path.is_junction():
                raise ValueError(f"linked LPIPS path: {relative}")
        if not path.is_file():
            raise ValueError(f"missing LPIPS file: {relative}")
        observed = _file_digest(path)
        if observed != expected:
            raise ValueError(f"LPIPS SHA-256 mismatch: {relative}")
        result[relative] = observed
    if (package_root / "weights/v0.1/alex.pth").stat().st_size != 6009:
        raise ValueError("LPIPS learned-weight size mismatch")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--asset-root", type=Path, required=True)
    parser.add_argument("--lock", type=Path, required=True)
    parser.add_argument("--lpips-root", type=Path, required=True)
    args = parser.parse_args()
    raw_lock = args.lock.read_bytes()
    if hashlib.sha256(raw_lock).hexdigest() != LOCK_SHA256:
        raise ValueError("candidate model-asset lock SHA-256 changed")
    lock = json.loads(raw_lock)
    receipt = verify(args.asset_root, lock)
    if len(receipt["files"]) != 17:
        raise ValueError("candidate model-asset inventory is not 17 files")
    package_files = verify_package(args.lpips_root)
    print(json.dumps({"status": "bytes_only", "asset_lock_sha256": LOCK_SHA256,
                      "asset_files": 17, "lpips_files": package_files}, sort_keys=True))


if __name__ == "__main__":
    main()
