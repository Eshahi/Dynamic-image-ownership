"""Exact-hash exclusion set for the Phase-B acquisition (AMENDMENT-B1.md section 4). Text/metadata only.

Written by Claude (Opus 5.5) on 2026-10-26. Reads the 79 ledgers the held-out metadata audit checked
(analysis/heldout-metadata/exclusion-files.json) plus this study's development source list, and collects every
64-hex-digit token as a recorded SHA256. Any token match with a new file's raw, canonical-PNG or RGB8 SHA256 excludes
that file. Collecting every token, not only keyed hashes, is deliberately conservative.

Usage: python -I build_exclusions.py > exclusion-sha256.json
"""
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STUDY = HERE.parents[1]


def main():
    files = json.loads((HERE.parent / "analysis/heldout-metadata/exclusion-files.json").read_text(encoding="utf-8"))
    paths = [Path(f["path"]) for f in files] + [STUDY / "source-list.json"]
    tokens, receipts = set(), []
    for p in paths:
        if not p.exists():
            receipts.append(dict(path=str(p), status="missing"))
            continue
        raw = p.read_bytes()
        found = set(re.findall(rb"(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])", raw.lower()))
        tokens |= {t.decode() for t in found}
        receipts.append(dict(path=str(p), status="read", sha256=hashlib.sha256(raw).hexdigest(), tokens=len(found)))
    json.dump(dict(schema="et-final-phase-b-exclusions-v1", files=receipts, sha256_tokens=sorted(tokens)), sys.stdout, indent=0)


if __name__ == "__main__":
    main()
