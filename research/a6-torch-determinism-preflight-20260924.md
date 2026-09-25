# A6 PyTorch determinism-setting preflight

Status 2026-09-24: **settings applied in a fresh, model-free local CPU process; method determinism and cross-host parity unverified**. Issue #7 / draft PR #58. This is not scientific compute, a model run, or approval of a final precision policy.

[PyTorch 2.12 reproducibility guidance](https://docs.pytorch.org/docs/2.12/notes/randomness.html) explicitly does not promise identical results across releases, platforms or CPU/GPU even with the same seed. It recommends explicit RNG controls, disabling cuDNN benchmarking, and using deterministic algorithms where available; deterministic mode may fail on unsupported operations and may be slower. [PyTorch 2.12 CUDA semantics](https://docs.pytorch.org/docs/2.12/notes/cuda.html#tensorfloat-32-tf32-on-ampere-and-later-devices) documents the newer per-backend `fp32_precision` controls; TF32 changes numerical behavior. Therefore `scripts/check_torch_determinism.py` is a fail-closed **setting check**, not evidence of output parity.

The preflight requires `CUBLAS_WORKSPACE_CONFIG=:4096:8` and `PYTHONHASHSEED=0` in the *parent process environment before PyTorch import*. The `:4096:8` choice is among the [CUDA 13.0 cuBLAS documented reproducibility settings](https://docs.nvidia.com/cuda/archive/13.0.0/pdf/CUBLAS_Library.pdf), with a roughly 24 MiB workspace-footprint tradeoff; this is not a guarantee for other kernels. It refuses a process that has already imported `torch`. It then seeds Python and Torch from the supplied uint64, enables `torch.use_deterministic_algorithms(True, warn_only=False)`, disables cuDNN benchmarking, requests deterministic cuDNN behavior, and selects `ieee` for generic, CUDA-matmul and cuDNN float32 precision. It reads those settings back. It intentionally does **not** seed NumPy, object-specific NumPy Generators, DataLoader workers, Diffusers generators, or any other library. The A5 canonical SHAKE256 noise and carrier streams remain separate from this framework seed. This preflight does not execute a CUDA kernel or test a model.

The isolated Stage-1 venv already authorized and installed on the user's laptop ran this command from the A6 checkout:

```powershell
$env:CUBLAS_WORKSPACE_CONFIG=':4096:8'
$env:PYTHONHASHSEED='0'
& 'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/a6-science-venv/Scripts/python.exe' scripts/check_torch_determinism.py --seed 42
```

It returned `settings_applied`, `torch=2.12.1+cu130`, `torch_cuda_runtime=13.0`, `deterministic_algorithms=true`, `cudnn_benchmark=false`, `cudnn_deterministic=true`, `fp32_precision=ieee`, `numpy_seeded=false`, and `scope=settings-only-no-kernel-parity`. Seed 42 was a software-preflight input, **not** a selected scientific seed. The standard-library fake-Torch tests exercised missing/incorrect launch variables, pre-import ordering, flag readback and invalid seeds. The workflow script suite discovered 52 tests: 50 passed and 2 were skipped (Torch unavailable in that venv; symlink creation unavailable on this Windows host).

Before A6 scientific acceptance, the reviewed runner must apply this or an explicitly revised profile *inside its exact execution process*, seed every actually used random source, record the precision and library state with the run, test the full differentiable A5 path under strict mode, and repeat controlled vectors on both local and RunPod environments. A setting receipt cannot substitute for observed output stability, numerical tolerance, resource fit, model rights/byte checks, or the user's exact-manifest compute approval. Any strict-mode failure remains a failure/deviation record, not a reason to silently switch to warning-only mode.
