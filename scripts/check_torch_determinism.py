"""A6 model-free PyTorch determinism-setting preflight, not a reproducibility proof.

Launch a fresh process with CUBLAS_WORKSPACE_CONFIG=:4096:8 and
PYTHONHASHSEED=0. This script imports torch only after checking those values;
it executes no CUDA kernels and downloads no assets.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys


def check_launcher(environ: dict[str, str], loaded: dict[str, object]) -> None:
    if environ.get("CUBLAS_WORKSPACE_CONFIG") != ":4096:8":
        raise ValueError("launch with CUBLAS_WORKSPACE_CONFIG=:4096:8")
    if environ.get("PYTHONHASHSEED") != "0":
        raise ValueError("launch with PYTHONHASHSEED=0")
    if "torch" in loaded:
        raise ValueError("torch was imported before the launcher check")


def configure(torch: object, seed: int) -> dict[str, object]:
    if type(seed) is not int or not 0 <= seed < 2**64:
        raise ValueError("seed must be uint64")
    random.seed(seed)
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True, warn_only=False)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    torch.backends.fp32_precision = "ieee"
    torch.backends.cuda.matmul.fp32_precision = "ieee"
    torch.backends.cudnn.fp32_precision = "ieee"
    if not torch.are_deterministic_algorithms_enabled():
        raise RuntimeError("deterministic algorithms did not enable")
    if torch.backends.cudnn.benchmark or not torch.backends.cudnn.deterministic:
        raise RuntimeError("cuDNN deterministic profile did not persist")
    if any(value != "ieee" for value in (
        torch.backends.fp32_precision,
        torch.backends.cuda.matmul.fp32_precision,
        torch.backends.cudnn.fp32_precision,
    )):
        raise RuntimeError("IEEE FP32 profile did not persist")
    return {
        "schema_version": "a6-torch-determinism-settings-v1",
        "scope": "settings-only-no-kernel-parity",
        "seed_uint64": seed,
        "torch": torch.__version__,
        "torch_cuda_runtime": torch.version.cuda,
        "deterministic_algorithms": True,
        "cudnn_benchmark": False,
        "cudnn_deterministic": True,
        "fp32_precision": "ieee",
        "cublas_workspace_config": os.environ["CUBLAS_WORKSPACE_CONFIG"],
        "pythonhashseed": os.environ["PYTHONHASHSEED"],
        "numpy_seeded": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, required=True)
    args = parser.parse_args()
    try:
        check_launcher(os.environ, sys.modules)
        import torch
        record = configure(torch, args.seed)
    except (ImportError, ValueError, RuntimeError, AttributeError) as error:
        print(json.dumps({"status": "preflight_failed", "error": str(error)}, sort_keys=True))
        return 2
    record["status"] = "settings_applied"
    print(json.dumps(record, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
