"""Read-only installed numerical-package hashing; no study pixels or kernels."""
import argparse
import hashlib
import json
import sys
from pathlib import Path


def collect():
    site = Path(sys.executable).resolve().parents[1] / "lib/python3.14/site-packages"
    # Virtualenv executable resolves outside the environment, so use sys.prefix.
    site = Path(sys.prefix) / "lib/python3.14/site-packages"
    roots = [site / name for name in ("numpy", "PIL", "skimage", "scipy", "numpy.libs", "scipy.libs", "pillow.libs")]
    files = [Path(sys.executable).resolve()]
    for root in roots:
        if not root.is_dir():
            raise ValueError("missing pinned numerical package: " + str(root))
        files.extend(path for path in root.rglob("*") if path.is_file() and "__pycache__" not in path.parts and (path.suffix == ".py" or ".so" in path.name))
    return {"python_prefix": sys.prefix, "scope": "interpreter and Python/shared-object bytes of numerical/codec packages; stdlib/OS libraries remain platform receipt only", "files": [{"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()} for path in sorted(set(files))]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    with Path(args.out).open("x", encoding="utf-8") as stream:
        result = collect()
        json.dump(result, stream, sort_keys=True, indent=2)
    print(json.dumps({"files": len(result["files"]), "out": args.out}))
