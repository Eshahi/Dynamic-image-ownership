"""Model-free strict-mode CUDA DCT/autograd compatibility probe for A6.

This tiny fixed arithmetic vector uses no image, model, checkpoint or dataset.
Launch in a fresh process with CUBLAS_WORKSPACE_CONFIG=:4096:8 and
PYTHONHASHSEED=0. It is not an A5 method run or a scientific result.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
import sys

from check_torch_determinism import check_launcher, configure


def dct_basis() -> tuple[tuple[float, ...], ...]:
    return tuple(tuple(
        (math.sqrt(1 / 8) if k == 0 else math.sqrt(2 / 8))
        * math.cos(math.pi * (n + .5) * k / 8)
        for n in range(8)) for k in range(8))


def f32_digest(values: list[float]) -> str:
    if any(not math.isfinite(value) for value in values):
        raise ValueError("probe tensor contains nonfinite values")
    return hashlib.sha256(struct.pack("<" + "f" * len(values), *values)).hexdigest()


def scalar_reference() -> tuple[list[float], list[float]]:
    """Separate float64 scalar sums for the fixed four-frequency vector."""
    basis = dct_basis()
    frequencies = ((1, 2), (2, 1), (2, 2), (1, 3))
    selected = [math.fsum(
        basis[u][y] * ((8 * y + x) / 63) * basis[v][x]
        for y in range(8) for x in range(8)) for u, v in frequencies]
    gradient = [2 * math.fsum(
        score * basis[u][y] * basis[v][x]
        for score, (u, v) in zip(selected, frequencies))
        for y in range(8) for x in range(8)]
    return selected, gradient


def probe(torch: object) -> dict[str, object]:
    if torch.version.cuda is None or not torch.cuda.is_available():
        raise RuntimeError("CUDA runtime or device unavailable")
    device = torch.device("cuda:0")
    basis = torch.tensor(dct_basis(), dtype=torch.float32, device=device)
    pixels = (torch.arange(64, dtype=torch.float32, device=device) / 63).reshape(8, 8)
    pixels.requires_grad_()
    coefficients = basis @ pixels @ basis.T
    selected = torch.stack((coefficients[1, 2], coefficients[2, 1],
                            coefficients[2, 2], coefficients[1, 3]))
    loss = (selected * selected).sum()
    loss.backward()
    torch.cuda.synchronize()
    if pixels.grad is None:
        raise RuntimeError("DCT probe produced no gradient")
    scores = selected.detach().cpu().flatten().tolist()
    gradient = pixels.grad.detach().cpu().flatten().tolist()
    if not any(value != 0 for value in gradient):
        raise RuntimeError("DCT probe gradient is identically zero")
    reference_scores, reference_gradient = scalar_reference()
    score_error = max(abs(actual - expected)
                      for actual, expected in zip(scores, reference_scores))
    gradient_error = max(abs(actual - expected)
                         for actual, expected in zip(gradient, reference_gradient))
    if not math.isfinite(score_error) or not math.isfinite(gradient_error) or max(score_error, gradient_error) > 2e-5:
        raise RuntimeError("DCT probe differs from scalar CPU reference")
    return {
        "schema_version": "a6-dct-cuda-probe-v1",
        "scope": "model-free-fixed-8x8-dct-autograd-only",
        "torch": torch.__version__,
        "torch_cuda_runtime": torch.version.cuda,
        "device_name": torch.cuda.get_device_name(0),
        "capability": list(torch.cuda.get_device_capability(0)),
        "selected_f32le_sha256": f32_digest(scores),
        "gradient_f32le_sha256": f32_digest(gradient),
        "gradient_nonzero": True,
        "score_max_abs_error_vs_scalar": score_error,
        "gradient_max_abs_error_vs_scalar": gradient_error,
        "smoke_tolerance": 2e-5,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, required=True)
    args = parser.parse_args()
    try:
        import os
        check_launcher(os.environ, sys.modules)
        import torch
        configure(torch, args.seed)
        record = probe(torch)
    except (ImportError, ValueError, RuntimeError, AttributeError, OverflowError) as error:
        print(json.dumps({"status": "probe_failed", "error": str(error)}, sort_keys=True))
        return 2
    record["status"] = "model_free_dct_cuda_pass"
    print(json.dumps(record, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
