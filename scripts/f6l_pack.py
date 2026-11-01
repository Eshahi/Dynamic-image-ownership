"""SERVER ONLY by use, stdlib only: pack what the plan retrieves. Run folders stay on the instance disk.

Keeps every journal, config, decision and log, all clean marks, and seed 0 regenerated
images of the arms that reached a decision. The fetch is bounded so retrieval stays near an hour.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import tarfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tifs_common as common

KEEP_SUFFIX = (".json", ".jsonl", ".log")
SAMPLE_ARMS = ("unmarked", "f5-r2")


def selected(root):
    files = sorted(p for p in root.rglob("*") if p.is_file() and p.suffix in KEEP_SUFFIX)
    images = set()
    for folder in {p.parent for p in root.rglob("clean.jsonl")}:
        decision = folder / "decision.json"
        keep = set(SAMPLE_ARMS)
        if decision.exists():
            value = common.load_json(decision)
            keep.update(value.get("finalists") or [])
            keep.update(a for a in [value.get("winner")] if a)
        for row in common.Journal(folder / "clean.jsonl", read_only=True).latest.values():
            if row.get("status") == "ok":
                images.add(Path(row["output"]["path"]))
        native = common.Journal(folder / "native.jsonl", read_only=True).latest
        for row in native.values():
            if row.get("status") == "ok" and row.get("seed") == 0 and row.get("arm") in keep:
                images.add(Path(row["output"]["path"]))
    return files, sorted(images)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--dest", required=True, type=Path)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    files, images = selected(root)
    with tarfile.open(args.dest, "w:gz", compresslevel=6) as bundle:
        for path in [*files, *images]:
            bundle.add(path, arcname=str(path.relative_to(root)))
    digest = hashlib.sha256(args.dest.read_bytes()).hexdigest()
    report = dict(files=len(files), images=len(images), bytes=args.dest.stat().st_size, sha256=digest)
    args.dest.with_name(args.dest.name + ".json").write_text(json.dumps(report, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
