"""Minimal, model-free CUDA wheel check for the A6 operator preflight."""

from __future__ import annotations

import json
import sys


def main() -> int:
    try:
        import torch
        import torchvision
    except Exception as exc:
        print(json.dumps({"status": "import_failed", "error": str(exc)}))
        return 2

    result = {
        "torch": torch.__version__,
        "torchvision": torchvision.__version__,
        "torch_cuda_runtime": torch.version.cuda,
        "cuda_available": torch.cuda.is_available(),
    }
    if torch.version.cuda is None or not result["cuda_available"]:
        result["status"] = "cuda_unavailable"
        print(json.dumps(result, sort_keys=True))
        return 2

    try:
        result["device_name"] = torch.cuda.get_device_name(0)
        result["capability"] = list(torch.cuda.get_device_capability(0))
        x = torch.ones((4, 4), device="cuda", requires_grad=True)
        (x * x).sum().backward()
        torch.cuda.synchronize()
        if x.grad is None or not torch.all(x.grad == 2).item():
            raise RuntimeError("unexpected tiny CUDA gradient")
    except Exception as exc:
        result["status"] = "cuda_operation_failed"
        result["error"] = str(exc)
        print(json.dumps(result, sort_keys=True))
        return 2

    result["status"] = "basic_cuda_pass"
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
