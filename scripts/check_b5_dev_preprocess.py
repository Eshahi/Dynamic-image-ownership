"""Explicit reserved-image CPU preprocessing check; no model or scientific outcome."""
import argparse
import csv
import json
import sys
from pathlib import Path, PurePosixPath

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data.preprocess import (PreprocessError, load_config, no_links,
                                 preprocess_file, runtime, sha)


def run(manifest, development, asset_root, cache_root, config):
    no_links(asset_root)
    raw_manifest = manifest.read_bytes()
    dev = json.loads(development.read_bytes())
    if dev["manifest_sha256"] != sha(raw_manifest):
        raise PreprocessError("development_manifest_mismatch")
    if dev["status"] != "development_reservation_not_study_split_or_compute_approval":
        raise PreprocessError("unexpected_development_reservation_status")
    with manifest.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    index = {(r["domain"], r["release_id"], r["source_split"], r["source_id"]): r for r in rows}
    if len(index) != len(rows):
        raise PreprocessError("duplicate_manifest_identity")
    results, seen = [], set()
    for item in dev["images"]:
        identity = tuple(item[k] for k in ("domain", "release_id", "source_split", "source_id"))
        if identity in seen or identity not in index:
            raise PreprocessError("invalid_development_identity")
        seen.add(identity)
        row = index[identity]
        if any(item[k] != row[k] for k in ("raw_sha256", "relative_path", "group_id")):
            raise PreprocessError("development_row_mismatch")
        relative = PurePosixPath(row["relative_path"])
        if relative.is_absolute() or ".." in relative.parts or "\\" in str(relative) or ":" in str(relative):
            raise PreprocessError("invalid_source_path")
        result = {"domain": row["domain"], "source_id": row["source_id"],
                  "raw_sha256": row["raw_sha256"]}
        try:
            _, receipt = preprocess_file(asset_root.joinpath(*relative.parts), row["raw_sha256"],
                                         int(row["raw_size_bytes"]), cache_root, config)
            result.update(status="pass", receipt=receipt)
        except PreprocessError as exc:
            result.update(status="rejected_coverage_failure", reason=str(exc))
        results.append(result)
    _, config_sha = load_config(config)
    return {"schema_version": "b5-development-preprocessing-check-v1", "runtime": runtime(),
            "manifest_sha256": sha(raw_manifest), "dev_ids_sha256": sha(development.read_bytes()),
            "config_sha256": config_sha, "code_sha256": sha(Path(__file__).read_bytes()),
            "counts": {"total": len(results), "pass": sum(r["status"] == "pass" for r in results),
                       "rejected": sum(r["status"] != "pass" for r in results)},
            "scientific_compute": False, "rights_clearance": False, "images": results}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("manifest", "development", "asset-root", "cache-root", "config", "report"):
        parser.add_argument("--" + name, required=True, type=Path)
    args = parser.parse_args()
    no_links(args.report)
    if args.report.exists():
        raise PreprocessError("report_exists_not_overwritten")
    report = run(args.manifest, args.development, args.asset_root, args.cache_root, args.config)
    with args.report.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(report, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
    print(json.dumps({"counts": report["counts"], "report_sha256": sha(args.report.read_bytes())}))
    raise SystemExit(0 if report["counts"]["rejected"] == 0 else 1)
