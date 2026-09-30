"""Installed runtime byte inventory only; no imports, models or kernels."""
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import sys

PACKAGES = ("numpy", "PIL", "skimage", "scipy", "numpy.libs", "scipy.libs", "pillow.libs",
            "torch", "torchvision", "torchvision.libs", "diffusers", "transformers",
            "huggingface_hub", "safetensors", "tokenizers", "clip", "lpips", "nvidia")


def collect():
    site = Path(sys.prefix) / "lib/python3.14/site-packages"
    files = [Path(sys.executable).resolve()]
    for name in PACKAGES:
        root = site / name
        if not root.is_dir():
            raise ValueError("required existing runtime package missing: " + name)
    # Include transitive packages, distribution metadata and packaged native
    # kernel data too; do not silently leave tokenizer/regex/Triton code unbound.
    files.extend(path for path in site.rglob("*") if path.is_file()
                 and "__pycache__" not in path.parts and path.suffix != ".pyc")
    versions = {name: importlib.metadata.version(name) for name in
                ("numpy", "Pillow", "scikit-image", "scipy", "torch", "torchvision",
                 "diffusers", "transformers", "safetensors", "tokenizers", "lpips", "clip")}
    result = []
    for path in sorted(set(files)):
        value = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                value.update(chunk)
        result.append({"path": str(path), "size_bytes": path.stat().st_size, "sha256": value.hexdigest()})
    return {"python_prefix": sys.prefix, "versions": versions,
            "scope": "interpreter and all installed site-package files except bytecode caches, including transitive modules and packaged kernels; stdlib, OS and driver remain platform-receipt dependencies",
            "files": result}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    result = collect()
    with Path(args.out).open("x", encoding="utf-8") as stream:
        json.dump(result, stream, sort_keys=True, indent=2)
        stream.write("\n")
    print(json.dumps({"files": len(result["files"]), "versions": result["versions"]}))
