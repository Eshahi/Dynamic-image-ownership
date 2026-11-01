"""Local, stdlib only: bundle the 60 canonical development PNGs for upload, verified against both manifests.

Never touches held-out data. Run on the laptop; the bundle goes to ASSETS/sources on the server.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import tifs_common as common


def rows():
    stage_s = common.load_json(ROOT / "research/tifs-20261028/stage-s/source-manifest.json")
    stage_p = common.load_json(ROOT / "research/tifs-20261028/stage-p/source-manifest.json")
    result = [row for group in common.SOURCE_GROUPS for row in stage_s[group]] + stage_p["tune_sources"] + stage_p["check_sources"]
    if len({row["source_id"] for row in result}) != 60:
        raise ValueError("Expected 60 distinct development sources")
    if any(row["data_split"] != "development" for row in result):
        raise ValueError("Only development sources may be bundled")
    return result


def index(folders):
    found = {}
    for folder in folders:
        for path in Path(folder).rglob("*.png"):
            found.setdefault(hashlib.sha256(path.read_bytes()).hexdigest(), path)
    return found


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dest", required=True, type=Path)
    parser.add_argument("--from", dest="folders", required=True, nargs="+", type=Path)
    args = parser.parse_args(argv)
    found = index(args.folders)
    wanted = rows()
    missing = [row["source_id"] for row in wanted if row["canonical_png_sha256"] not in found]
    if missing:
        raise SystemExit("Missing canonical PNGs: " + json.dumps(missing))
    with tarfile.open(args.dest, "w") as bundle:
        for row in wanted:
            data = found[row["canonical_png_sha256"]].read_bytes()
            info = tarfile.TarInfo(f"sources/{row['source_id']}.png")
            info.size = len(data)
            bundle.addfile(info, io.BytesIO(data))
    print(json.dumps(dict(sources=len(wanted), bytes=args.dest.stat().st_size, sha256=common.sha256_file(args.dest))))


if __name__ == "__main__":
    main()
