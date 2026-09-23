# A6 scientific runtime: operator preflight, not a verified lock

Status 2026-09-23: **not installed or executed**. This is the first staged compatibility check for issue #7 on the user's Windows laptop, not authorization for an experiment, a model/dataset download, or a paid remote machine. Preserve the existing `.thesis-build/venv` workflow environment. The user chose to perform substantial installs/downloads personally; the commands below are for that later supervised step, not an unattended agent action.

## Why this candidate

The [official PyTorch previous-versions guide](https://pytorch.org/get-started/previous-versions/) gives the Windows/Linux CUDA 13.0 pair `torch==2.12.1 torchvision==0.27.1` from `https://download.pytorch.org/whl/cu130`. The [PyTorch 2.12 release note](https://pytorch.org/blog/pytorch-2-12-release-blog/) recommends CUDA 13.0+ for Blackwell and lists a Windows driver minimum of 580.88; the observed laptop driver was 610.88. These are upstream compatibility indications, **not** proof of a functioning RTX 5070 Ti Laptop GPU wheel or sufficient memory. The [Diffusers v0.35.1 install page](https://huggingface.co/docs/diffusers/v0.35.1/en/installation) recommends an isolated environment but also says Windows PyTorch supports only Python 3.8–3.11, which conflicts with the newer PyTorch 2.12.1 Windows CPython 3.12 wheel listing. Treat that page as potentially stale and resolve the discrepancy by an actual clean-host install/import test; do not claim compatibility from either page alone. Diffusers v0.35.1's [pinned setup metadata](https://github.com/huggingface/diffusers/blob/v0.35.1/setup.py) names `transformers>=4.41.2`, but does not establish an upper bound or a tested combination with this CUDA wheel. Do not let pip silently choose a current major Transformers release and call it a scientific lock.

## Stage 1: only PyTorch/CUDA compatibility

Run in PowerShell **on the Windows laptop, from the repository root**, when the user is ready for the large PyTorch wheel download. Do not run on the Mac or in the existing workflow venv. The `venv` target is a new ignored directory. Confirm the printed wheel versions include the intended CUDA build; a CPU wheel is not a pass.

```powershell
& 'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/venv/Scripts/python.exe' -m venv '.thesis-build/a6-science-venv'
& '.thesis-build/a6-science-venv/Scripts/python.exe' -m pip install 'torch==2.12.1' 'torchvision==0.27.1' --index-url 'https://download.pytorch.org/whl/cu130'
& '.thesis-build/a6-science-venv/Scripts/python.exe' -m pip check
& '.thesis-build/a6-science-venv/Scripts/python.exe' scripts/check_torch_cuda.py
& '.thesis-build/a6-science-venv/Scripts/python.exe' -m pip freeze
```

Stop on a failed command. Preserve the terminal output from `pip check`, the probe, and `pip freeze`, including errors; do not post credentials, full environment variables, or private paths in GitHub. The probe deliberately performs only a 4×4 tensor allocation and backward operation, without loading any model or dataset. It exits nonzero if the CUDA build, TorchVision import, GPU availability, or tiny gradient operation fails. Its success would establish basic local wheel/device functionality only, not method feasibility, numerical parity, 12 GB VRAM fit, or scientific approval. Record `nvidia-smi` and `scripts/capture_environment.py` at the tested checkout commit alongside the output. The new venv is not a hash-locked environment merely because the top-level package versions are specified.

## Stage 2: deferred scientific stack

Only after Stage 1 succeeds, resolve and freeze a compatible **exact** Diffusers/Transformers/Accelerate/Safetensors/Pillow/NumPy/SciPy/SSIM/LPIPS set using metadata, `pip check`, import tests, image/ICC and DCT test vectors, and wheel-byte receipts. No Stage 2 installation command is prescribed yet; the A5 method and A4 metrics require more than a resolver-successful import. CLIP, diffusion and LPIPS/AlexNet checkpoints require separate approved-source, rights and SHA-256 receipts; no implicit `from_pretrained()` calls in preflight. A RunPod image requires its own OS, driver, CUDA, Python, package and artifact record and may not inherit the laptop pass.

The original proposal's method, [research-contract.md](research-contract.md), [scope-guard.md](scope-guard.md), and [method-spec.md](method-spec.md) remain the controlling scientific scope. A6 and issue #7 stay open until the actual host evidence and unresolved scientific dependencies are addressed. Routine compatibility checks are not a surrogate for the separately approved exact scientific compute manifest.
