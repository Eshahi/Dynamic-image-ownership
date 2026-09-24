# A6 scientific runtime: operator preflight, not a verified lock

Status 2026-09-24: **Stage 1 and the bounded Stage-2 software set are installed in the isolated science venv; no model checkpoint or scientific run exists**. The original Stage-1 command and receipt below are historical. See the [Stage-1 receipt](a6-stage1-receipt-20260923.md) and [Stage-2 software receipt](a6-stage2-install-receipt-20260924.md) for current verified results and limitations. Neither installation authorizes an experiment, model/dataset download or paid remote machine. The existing `.thesis-build/venv` workflow environment was preserved.

## Why this candidate

The [official PyTorch previous-versions guide](https://pytorch.org/get-started/previous-versions/) gives the Windows/Linux CUDA 13.0 pair `torch==2.12.1 torchvision==0.27.1` from `https://download.pytorch.org/whl/cu130`. The [PyTorch 2.12 release note](https://pytorch.org/blog/pytorch-2-12-release-blog/) recommends CUDA 13.0+ for Blackwell and lists a Windows driver minimum of 580.88; the observed laptop driver was 610.88. Those upstream indications alone did not establish host compatibility; the observed Stage-1 probe now establishes only a tiny CUDA allocation/backward pass, not full-method fit or sufficient memory. The [Diffusers v0.35.1 install page](https://huggingface.co/docs/diffusers/v0.35.1/en/installation) recommends an isolated environment but also says Windows PyTorch supports only Python 3.8–3.11, which conflicts with the tested PyTorch 2.12.1 Windows CPython 3.12 wheel. Treat that older page's range as stale for this limited PyTorch test, not as proof that Diffusers v0.35.1 works on this stack. Diffusers v0.35.1's [pinned setup metadata](https://github.com/huggingface/diffusers/blob/v0.35.1/setup.py) names `transformers>=4.41.2`, but does not establish an upper bound or a tested combination with this CUDA wheel. Do not let pip silently choose a current major Transformers release and call it a scientific lock.

## Stage 1: only PyTorch/CUDA compatibility

The following is the original PowerShell reproduction sequence for the Windows laptop from the repository root. The authorized run used the same isolated venv but, after a direct pip network timeout, installed Torch from a hash-verified locally downloaded official wheel before installing TorchVision from the official index. The exact installed inventory and results are in the receipt. Do not run on the Mac or in the existing workflow venv. Confirm that both wheel versions include the intended CUDA build; a CPU wheel is not a pass.

```powershell
& 'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/venv/Scripts/python.exe' -m venv '.thesis-build/a6-science-venv'
& '.thesis-build/a6-science-venv/Scripts/python.exe' -m pip install 'torch==2.12.1' 'torchvision==0.27.1' --index-url 'https://download.pytorch.org/whl/cu130'
& '.thesis-build/a6-science-venv/Scripts/python.exe' -m pip check
& '.thesis-build/a6-science-venv/Scripts/python.exe' scripts/check_torch_cuda.py
& '.thesis-build/a6-science-venv/Scripts/python.exe' -m pip freeze
```

Stop on a failed command. Preserve the terminal output from `pip check`, the probe, and `pip freeze`, including errors; do not post credentials, full environment variables, or private paths in GitHub. The probe deliberately performs only a 4×4 tensor allocation and backward operation, without loading any model or dataset. It exits nonzero if the CUDA build, TorchVision import, GPU availability, or tiny gradient operation fails. Its observed success establishes basic local wheel/device functionality only, not method feasibility, numerical parity, 12 GB VRAM fit, or scientific approval. `nvidia-smi` and `scripts/capture_environment.py` observations are in the receipt. The new venv is not a hash-locked environment merely because the top-level package versions are specified.

## Stage 2: installed software, incomplete science lock

The earlier [Stage-2 metadata preflight](a6-stage2-metadata-preflight-20260923.md) is now a historical candidate screen. The [Stage-2 software receipt](a6-stage2-install-receipt-20260924.md) records the installed exact Diffusers/Transformers/Accelerate/Safetensors/SciPy/scikit-image packages and a separately pinned official CLIP source install, with `pip check` and offline import-only success. This does not verify weights, full code-path compatibility, canonical image/ICC behavior, LPIPS/SSIM parity, numerical gradients or a full wheel-hash lock. CLIP, diffusion and LPIPS/AlexNet checkpoints require separate approved-source, rights and SHA-256 receipts; no implicit `from_pretrained()` or name-based `clip.load()` calls in preflight. A RunPod image requires its own OS, driver, CUDA, Python, package and artifact record and may not inherit the laptop pass.

The original proposal's method, [research-contract.md](research-contract.md), [scope-guard.md](scope-guard.md), and [method-spec.md](method-spec.md) remain the controlling scientific scope. A6 and issue #7 stay open until the actual host evidence and unresolved scientific dependencies are addressed. Routine compatibility checks are not a surrogate for the separately approved exact scientific compute manifest.
