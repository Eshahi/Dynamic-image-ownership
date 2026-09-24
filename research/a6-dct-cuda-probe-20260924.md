# A6 fixed DCT/autograd CUDA probe

Status 2026-09-24: **model-free Stage-1 compatibility evidence only**, issue [#7](https://github.com/Eshahi/Dynamic-image-ownership/issues/7), draft PR #58. No model, image, checkpoint, dataset, Stage-2 package, paid resource or scientific experiment was used. The user's bounded Stage-1 authorization covered a local model-free GPU probe; this is a second fixed arithmetic vector in that environment, not permission for scientific compute.

`scripts/check_torch_dct_cuda.py` requires a fresh process with `CUBLAS_WORKSPACE_CONFIG=:4096:8` and `PYTHONHASHSEED=0` before importing Torch. It applies the strict setting profile from `scripts/check_torch_determinism.py`, evaluates a fixed 8×8 float32 orthonormal DCT on a synthetic ramp, selects A5's four semantic frequencies, differentiates the squared-coefficient sum, and checks a separately summed float64 CPU scalar reference. It makes no claim about the full image-block detector or diffusion gradients. `--seed 42` is a preflight input, not a study seed.

The RTX 5070 Ti Laptop GPU (capability 12.0), Torch `2.12.1+cu130`, CUDA runtime `13.0` returned `model_free_dct_cuda_pass` in two fresh processes. Both selected-coefficient and gradient float32 little-endian SHA-256 fingerprints matched across those processes: `412ebd98983e0d3b1887c880cbe87f2ca7b9d5b8c7347ecf11668c50466f1b92` and `6715a8b3f3c0ad98ed9bbdfee3edf8bb13d1a1d98d813c075be1d1232ea67f47`, respectively. The maximum absolute differences from the scalar CPU reference were `8.940696746449414e-08` for selected coefficients and `8.577208636996161e-08` for the gradient. The `2e-5` smoke tolerance is a prospective engineering check for this vector only, **not** a calibrated numerical-parity or hypothesis threshold.

Reproduction from the A6 checkout, with the already-authorized isolated Stage-1 venv:

```powershell
$env:CUBLAS_WORKSPACE_CONFIG=':4096:8'
$env:PYTHONHASHSEED='0'
& 'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/a6-science-venv/Scripts/python.exe' scripts/check_torch_dct_cuda.py --seed 42
```

The workflow venv discovered 55 script tests, with 53 passing and two expected skips (Torch absent from the workflow venv; Windows symlink creation unavailable on this host). This probe does not test CLIP inference, source-image preprocessing, 429-candidate scoring, the image-conditioned denoising suffix, VAE, LPIPS, large tensors, peak VRAM, precision policy for the actual method, RunPod parity or cross-version determinism. The same-host repeat is not independent host replication. A6 and the official plan gate remain open; Stage-2 installation and scientific compute still require their separate decisions.
