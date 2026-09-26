"""CPU-only native canonical identities and coarse leakage fingerprints, no models."""
import argparse
import csv
import io
import json
import sys
import zipfile
from collections import Counter
from pathlib import Path, PurePosixPath

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
from PIL import Image
from src.data.preprocess import PreprocessError, decode_source, load_config, no_links, pixel_sha, runtime, sha
from b3_raw_duplicate_groups import inventory_records


def leakage_fingerprint(rgb):
    """Separate from A5 detector pHash; resizing is only a grouping diagnostic."""
    image = Image.fromarray(rgb)
    # Pillow pinned RGB->L and bilinear operations; no model or scientific code.
    small = np.array(image.convert("L").resize((9, 8), Image.Resampling.BILINEAR), dtype=np.uint8)
    bits = (small[:, 1:] > small[:, :-1]).ravel()
    value = sum(int(bit) << i for i, bit in enumerate(bits))
    color = np.array(image.resize((8, 8), Image.Resampling.BILINEAR), dtype=np.uint8).tobytes()
    return {"leakage_dhash64": f"{value:016x}", "private_color8_rgb_hex": color.hex()}


def fingerprint(raw, expected, config):
    if len(raw) != expected["bytes"] or sha(raw) != expected["sha256"]:
        raise ValueError("raw image size/hash mismatch; provenance failure")
    result = {"id": expected["uid"], "raw_sha256": expected["sha256"],
              "source_width": expected["width"], "source_height": expected["height"]}
    try:
        rgb, receipt = decode_source(raw, config)
        if receipt["source_size"] != [expected["width"], expected["height"]]:
            raise ValueError("native image dimension mismatch")
        result.update(status="canonical_pass", canonical_pixel_sha256=pixel_sha(rgb),
                      width=receipt["width"], height=receipt["height"],
                      color_action=receipt["color_action"], exif_orientation=receipt["exif_orientation"],
                      **leakage_fingerprint(rgb))
    except PreprocessError as exc:
        result.update(status="canonical_rejected_coverage_failure", reason=str(exc))
    return result


def pinned(path, digest, maximum):
    no_links(path)
    if path.stat().st_size > maximum:
        raise ValueError("inventory input resource limit")
    raw = path.read_bytes()
    if len(raw) > maximum or sha(raw) != digest:
        raise ValueError("inventory pin mismatch")
    return raw


def run(stable, provenance, config_path, output, summary):
    config, config_sha = load_config(config_path)
    no_links(stable); no_links(output); no_links(summary)
    if output.exists() or summary.exists():
        raise ValueError("existing evidence retained; use fresh output paths")
    evidence = json.loads(provenance.read_bytes())
    original = evidence["original_inventory"]
    original_raw = pinned(stable/original["local_csv"], original["sha256"], 8*1024*1024)
    validated = inventory_records(original_raw)
    original_rows = list(csv.DictReader(io.StringIO(original_raw.decode())))
    if len(original_rows) != len(validated):
        raise ValueError("source inventory frame mismatch")
    count, colors, orientations, failures = Counter(), Counter(), Counter(), []
    identities = set()
    with output.open("x", encoding="utf-8", newline="\n") as out:
        def emit(raw, expected):
            uid = expected["uid"]
            if uid in identities:
                raise ValueError("duplicate canonical input UID")
            identities.add(uid)
            row = fingerprint(raw, expected, config)
            out.write(json.dumps(row, sort_keys=True, separators=(",", ":"))+"\n")
            count[row["status"]] += 1
            if row["status"] == "canonical_pass":
                colors[row["color_action"]] += 1; orientations[str(row["exif_orientation"])] += 1
            else:
                failures.append({k:row[k] for k in ("id", "raw_sha256", "reason")})
        for row in original_rows:
            relative = PurePosixPath(row["relative_path"])
            if relative.is_absolute() or ".." in relative.parts or "\\" in str(relative) or ":" in str(relative):
                raise ValueError("source inventory traversal")
            path = stable/"data/raw"/str(relative); no_links(path)
            size = int(row["bytes"])
            if path.stat().st_size != size or size > config["max_source_bytes"]:
                raise ValueError("source snapshot size mismatch")
            uid = ("ms-coco:" if row["source"] == "coco2017-val" else "div2k:") + row["source_id"]
            emit(path.read_bytes(), {"uid":uid, "bytes":size, "sha256":row["sha256"],
                                     "width":int(row["width"]), "height":int(row["height"])})
        print(json.dumps({"checkpoint":"original5900-complete", "counts":dict(count)}), flush=True)
        for part in evidence["diffusiondb"]["parts"]:
            split = part["source_split"]
            records = inventory_records(pinned(
                stable/(".thesis-build/b3-diffusiondb-integrity-20260926/"+split+".csv"),
                part["image_inventory_sha256"], 2*1024*1024))
            archive = stable/("data/raw/diffusiondb-2m/archives/"+split+".zip")
            no_links(archive)
            with zipfile.ZipFile(archive) as zipped:
                for item in records:
                    name = item["id"].split(":",1)[1]
                    # Reviewed acquisition archives store PNG at their root.
                    info = zipped.getinfo(name)
                    if info.file_size != item["bytes"] or info.file_size > config["max_source_bytes"]:
                        raise ValueError("ZIP source size mismatch")
                    with zipped.open(info) as member:
                        raw = member.read(config["max_source_bytes"]+1)
                    emit(raw, dict(item, uid="diffusiondb:"+name[:-4]))
            out.flush()
            print(json.dumps({"checkpoint":split, "counts":dict(count)}), flush=True)
    if len(identities) != 19900:
        raise ValueError("canonical frame incomplete; preserve failed inventory")
    report = {"status":"private_canonical_leakage_inventory_not_splits_or_science",
              "counts":dict(count), "color_actions":dict(colors), "orientations":dict(orientations),
              "coverage_failures":failures, "output_sha256":sha(output.read_bytes()),
              "config_sha256":config_sha, "preprocess_code_sha256":sha(Path("src/data/preprocess.py").read_bytes()),
              "fingerprint_code_sha256":sha(Path(__file__).read_bytes()), "runtime":runtime(),
              "frame_images":19900, "resize_for_method":False, "scientific_compute":False,
              "limits":"coarse near-duplicate screening is not proof of all content independence"}
    with summary.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(report, handle, sort_keys=True, indent=2); handle.write("\n")
    print(json.dumps(report), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("stable", "provenance", "config", "output", "summary"):
        parser.add_argument("--"+name, type=Path, required=True)
    args=parser.parse_args()
    run(args.stable, args.provenance, args.config, args.output, args.summary)
