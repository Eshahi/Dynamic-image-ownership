# A6 Stage-1 CUDA compatibility receipt

Date: 2026-09-23 UTC. Issue [#7](https://github.com/Eshahi/Dynamic-image-ownership/issues/7). This is a **model-free local software compatibility test**, not a scientific experiment, complete A6 environment lock, resource-fit result, or compute approval. The user explicitly authorized this bounded PyTorch/TorchVision installation in the authenticated Codex task on 2026-09-23; that authorization did not include model/data downloads, Stage 2 packages, or RunPod spending.

## Exact input and recovery

- Test scripts: A6 worktree commit `dffc7d653a6d8c4126905a006668b0c04cb288fb`; `scripts/check_torch_cuda.py` and `scripts/capture_environment.py`. New ignored environment: `.thesis-build/a6-science-venv` under the main Windows project checkout, created with the verified Python 3.12.14 interpreter. The existing workflow venv was preserved.
- Official CUDA 13.0 [PyTorch wheel index](https://download.pytorch.org/whl/cu130/torch/): `torch-2.12.1+cu130-cp312-cp312-win_amd64.whl`, 1,926,431,198 bytes, published SHA-256 `52c5da6a0898d5d3473c02bd304b7a3bc0b72e351c6f3bfa0783e45ef9f4cd61`. The locally downloaded wheel matched **both** byte count and SHA-256 before installation.
- Official CUDA 13.0 [TorchVision wheel index](https://download.pytorch.org/whl/cu130/torchvision/): `torchvision-0.27.1+cu130-cp312-cp312-win_amd64.whl`, 9,083,741 bytes, published SHA-256 `1bf254c102bfaf97d3e7878b76b68999bcd4dcd4303c109e76b4fbf9b15265c5`. A separate local receipt download matched this SHA-256; pip installed the same named build from that official index, but no claim of a fully hash-locked dependency set follows.
- The first direct `pip install` failed after roughly 0.4/1.9 GB with a `download-r2.pytorch.org` read timeout. Pip discarded its partial file. A resumed-range `curl` transfer to the ignored wheel cache completed and passed the exact hash check; the local Torch wheel plus TorchVision from the official index then installed successfully. The failed attempt is retained here as operational provenance, not suppressed or counted as a scientific failure.

## Observed checks

| Check | Result |
| --- | --- |
| `pip check` in the Stage-1 venv | `No broken requirements found.` |
| `scripts/check_torch_cuda.py` | Exit 0; `basic_cuda_pass`; Torch `2.12.1+cu130`, TorchVision `0.27.1+cu130`, CUDA runtime `13.0`, CUDA available; device `NVIDIA GeForce RTX 5070 Ti Laptop GPU`, compute capability `12.0`. The 4×4 tensor allocation and backward gradient check passed. |
| Host GPU query | Driver `610.88`, 12,227 MiB total and 11,576 MiB free at capture; free memory is transient. |
| `scripts/capture_environment.py` | UTC `2026-09-23T22:47:43Z`; Windows 11, AMD64, Python `3.12.14`; A6 script checkout `dffc7d6` clean; workflow `requirements.lock` SHA-256 `c26d467d208f6cfecf6dcfb6ac8a21a18824ff7f7ad56e5bbdfb7adeb6de0aaf`. That workflow lock does **not** describe the Stage-1 scientific venv. |

Installed version inventory from `pip freeze`: `filelock==3.32.3`, `fsspec==2026.7.0`, `Jinja2==3.1.6`, `MarkupSafe==3.0.3`, `mpmath==1.3.0`, `networkx==3.6.1`, `numpy==2.5.2`, `pillow==12.3.0`, `setuptools==78.1.0`, `sympy==1.14.0`, `torch==2.12.1+cu130` from the hash-verified local wheel, `torchvision==0.27.1+cu130`, and `typing_extensions==4.16.0`. The actual pip freeze records Torch as a machine-local `file://` reference to the ignored wheel; this paragraph normalizes that nonportable path and preserves its verified content hash. Exact transitive wheel hashes and a clean reinstall from a committed scientific lock are **not** yet established.

## Boundary and next work

This pass proves only that the candidate wheel pair imports, sees this GPU, and performs one tiny CUDA backward operation. It does not prove that Diffusers/Transformers/CLIP/LPIPS imports, checkpoints or numerical parity work; that the proposed reverse-diffusion gradient path is differentiable; that native-resolution images fit available VRAM; that CUDA results are deterministic; or that a RunPod image is equivalent. No model checkpoint, image dataset, scientific seed, or paid VM was acquired or executed. A6 stays **open** until the complete method-relevant environment, exact artifact rights/hashes, deterministic settings and resource compatibility are reviewed. The official Spec Kit run remains paused at `plan-acceptance` with no transition from this test.
