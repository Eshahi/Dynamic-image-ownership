"""Materialize a hash-checked offline wheelhouse from existing local caches.

This does not install packages, access the network, or accept a scientific run.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import zipfile
from email.parser import BytesParser
from pathlib import Path

from audit_science_wheels import canonical, digest, parse_lock, wheel_identity


TAG = re.compile(r"^[A-Za-z0-9_.]+-[A-Za-z0-9_.]+-[A-Za-z0-9_.]+$")
INCLUDE = re.compile(r"^-r\s+([A-Za-z0-9_.-]+\.txt)$")
INDEX_OPTIONS = ("--index-url ", "--extra-index-url ")


def safe_directory(path: Path) -> None:
    if not path.is_dir() or path.is_symlink() or path.is_junction():
        raise ValueError(f"not a regular directory: {path}")


def read_lock_tree(path: Path) -> tuple[dict[tuple[str, str], str], dict[str, str]]:
    """Read same-directory hash-lock includes without using their package indexes."""
    root = path.parent.resolve()
    locked: dict[tuple[str, str], str] = {}
    fingerprints: dict[str, str] = {}
    active: set[str] = set()

    def visit(name: str) -> None:
        if name in active:
            raise ValueError(f"cyclic lock include: {name}")
        if name in fingerprints:
            raise ValueError(f"duplicate lock include: {name}")
        candidate = root / name
        if candidate.is_symlink() or candidate.is_junction() or not candidate.is_file():
            raise ValueError(f"not a regular lock file: {candidate}")
        if candidate.resolve().parent != root:
            raise ValueError(f"lock include escapes directory: {name}")
        active.add(name)
        raw = candidate.read_bytes()
        fingerprints[name] = hashlib.sha256(raw).hexdigest()
        rows: list[str] = []
        for line in raw.decode("utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            include = INCLUDE.fullmatch(stripped)
            if include:
                visit(include[1])
            elif stripped.startswith(INDEX_OPTIONS):
                continue  # The materializer never accesses an index.
            else:
                rows.append(stripped)
        if rows:
            for key, value in parse_lock("\n".join(rows)).items():
                if key in locked:
                    raise ValueError(f"duplicate locked distribution: {key}")
                locked[key] = value
        active.remove(name)

    visit(path.name)
    if not locked:
        raise ValueError("empty distribution lock")
    return locked, fingerprints


def wheel_filename(path: Path, key: tuple[str, str]) -> str:
    if path.suffix == ".whl":
        return path.name
    with zipfile.ZipFile(path) as archive:
        records = [name for name in archive.namelist()
                   if name.count("/") == 1 and name.endswith(".dist-info/WHEEL")]
        if len(records) != 1:
            raise ValueError("wheel has no unique WHEEL metadata")
        metadata = BytesParser().parsebytes(archive.read(records[0]))
    tags = metadata.get_all("Tag", [])
    if not tags or any(not TAG.fullmatch(tag) for tag in tags):
        raise ValueError("wheel has no valid compatibility tag")
    # Metadata may list a legacy py2 tag before an equally valid py3 tag.
    # A cache body has no original filename, so choose the py3 tag when present.
    tag = next((item for item in tags if item.startswith("py3-")), tags[0])
    return f"{key[0].replace('-', '_')}-{key[1]}-{tag}.whl"


def select_wheels(
    locked: dict[tuple[str, str], str], roots: list[Path],
) -> dict[tuple[str, str], tuple[Path, str]]:
    selected: dict[tuple[str, str], tuple[Path, str]] = {}
    for root in roots:
        safe_directory(root)
        candidates = list(root.rglob("*.whl")) + list(root.rglob("*.body"))
        for path in candidates:
            if path.is_symlink() or path.is_junction() or not path.is_file():
                raise ValueError(f"unsafe wheel candidate: {path}")
            if path.suffix == ".body" and not zipfile.is_zipfile(path):
                continue
            try:
                key = wheel_identity(path)
            except ValueError:
                if path.suffix == ".body":
                    continue
                raise
            if key not in locked or digest(path) != locked[key]:
                continue
            filename = wheel_filename(path, key)
            previous = selected.get(key)
            # A cache body can advertise multiple tags; its first tag can
            # differ from an existing named wheel with identical bytes.
            # Prefer the original wheel filename when one is available.
            if previous is None or (path.suffix == ".whl"
                                    and previous[0].suffix != ".whl"):
                selected[key] = (path, filename)
    missing = sorted(set(locked) - set(selected))
    if missing:
        raise ValueError(f"missing locked wheels: {missing}")
    names = [filename.lower() for _, filename in selected.values()]
    if len(names) != len(set(names)):
        raise ValueError("wheelhouse filename collision")
    return selected


def materialize(
    locked: dict[tuple[str, str], str], roots: list[Path], output: Path,
) -> dict[str, object]:
    if any(output.resolve().is_relative_to(root.resolve()) for root in roots):
        raise ValueError("output must not be inside a source root")
    selected = select_wheels(locked, roots)
    output.mkdir(parents=True, exist_ok=True)
    safe_directory(output)
    total_bytes = 0
    for key, (source, filename) in sorted(selected.items()):
        target = output / filename
        if target.exists() or target.is_symlink():
            if target.is_symlink() or target.is_junction() or not target.is_file():
                raise ValueError(f"unsafe existing target: {target}")
            if digest(target) != locked[key]:
                raise ValueError(f"existing target has wrong hash: {target}")
        else:
            partial = output / f"{filename}.partial"
            if partial.exists() or partial.is_symlink():
                raise ValueError(f"existing partial target: {partial}")
            try:
                with source.open("rb") as reader, partial.open("xb") as writer:
                    shutil.copyfileobj(reader, writer, length=8 * 1024 * 1024)
                if digest(partial) != locked[key]:
                    raise ValueError(f"copied wheel has wrong hash: {source}")
                partial.replace(target)
            except BaseException:
                partial.unlink(missing_ok=True)
                raise
        total_bytes += target.stat().st_size
    return {"status": "wheelhouse_verified", "wheel_count": len(selected),
            "bytes": total_bytes, "output": str(output)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hash-lock", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    locked, fingerprints = read_lock_tree(args.hash_lock)
    report = materialize(locked, args.source_root, args.output)
    report["hash_lock_sha256"] = fingerprints[args.hash_lock.name]
    report["lock_file_sha256"] = fingerprints
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
