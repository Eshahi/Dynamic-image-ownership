"""Offline receipt for the three pinned TrustMark Q inference assets.

This inspects existing local files only. It never imports TrustMark, loads a
checkpoint, downloads a file, or grants permission to run an experiment.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


SOURCE_COMMIT = "2ecb73ad28d1a3f66ac9dc19e1b667711f14314f"
SOURCE_URL = (
    "https://github.com/adobe/trustmark/blob/"
    + SOURCE_COMMIT + "/python/trustmark/trustmark.py"
)
# MODEL_CHECKSUMS at SOURCE_COMMIT. These MD5 values identify the upstream
# loader's expected files; SHA-256 below is computed from actual local bytes.
Q_ASSETS = {
    "trustmark_Q.yaml": "fe40df84a7feeebfceb7a7678d7e6ec6",
    "encoder_Q.ckpt": "700328b8754db934b2f6cb5e5185d81f",
    "decoder_Q.ckpt": "4ced90e9cfe13e3295ad082887fe9187",
}


def _digests(path: Path) -> tuple[int, str, str]:
    md5 = hashlib.md5()
    sha256 = hashlib.sha256()
    size = 0
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            size += len(chunk)
            md5.update(chunk)
            sha256.update(chunk)
    return size, md5.hexdigest(), sha256.hexdigest()


def inspect_assets(directory: Path, checksums: dict[str, str] = Q_ASSETS) -> dict:
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError("asset directory must be an existing non-symlink directory")
    assets = {}
    for name, expected_md5 in checksums.items():
        path = directory / name
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"missing or non-regular asset: {name}")
        size, actual_md5, sha256 = _digests(path)
        if size == 0 or actual_md5 != expected_md5:
            raise ValueError(f"empty or upstream MD5 mismatch: {name}")
        assets[name] = {"size_bytes": size, "upstream_md5": actual_md5,
                        "sha256": sha256}
    return {"source_commit": SOURCE_COMMIT, "source_url": SOURCE_URL,
            "profile": "TrustMark Q encoder/decoder/config only",
            "status": "UPSTREAM_MD5_MATCH_SHA256_RECEIPT_NOT_RUN_READY",
            "assets": assets}


def verify_lock(receipt: dict, lock: dict) -> None:
    if not isinstance(lock, dict):
        raise ValueError("SHA-256 lock must be a JSON object")
    if lock.get("source_commit") != SOURCE_COMMIT:
        raise ValueError("SHA-256 lock source commit mismatch")
    expected = lock.get("sha256")
    if not isinstance(expected, dict) or set(expected) != set(Q_ASSETS):
        raise ValueError("SHA-256 lock must contain exactly the three Q assets")
    for name, digest in expected.items():
        if not isinstance(digest, str) or len(digest) != 64 or any(
                character not in "0123456789abcdef" for character in digest):
            raise ValueError(f"invalid SHA-256 lock value: {name}")
        if digest != receipt["assets"][name]["sha256"]:
            raise ValueError(f"SHA-256 lock mismatch: {name}")
    receipt["status"] = "UPSTREAM_MD5_AND_SUPPLIED_SHA256_LOCK_MATCH_NOT_RUN_READY"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("asset_directory", type=Path)
    parser.add_argument("--sha256-lock", type=Path,
                        help="pre-reviewed JSON with source_commit and sha256 map")
    args = parser.parse_args()
    try:
        receipt = inspect_assets(args.asset_directory)
        if args.sha256_lock is not None:
            verify_lock(receipt, json.loads(args.sha256_lock.read_text(encoding="utf-8")))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        parser.exit(2, f"asset receipt failed: {error}\n")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
