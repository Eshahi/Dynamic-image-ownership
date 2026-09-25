# A6 WSL Torch/CUDA Stage-1 receipt (2026-09-25)

Issue: [#7](https://github.com/Eshahi/Dynamic-image-ownership/issues/7). This is a bounded software/device preflight, not A6 acceptance or scientific compute.

## Authority and boundary

The user authorized installing PyTorch 2.12.1+cu130, TorchVision 0.27.1+cu130, and necessary software dependencies in an isolated WSL environment with at most 8 GB of new downloads, followed by a tiny model-free CUDA/package-import check. This did **not** authorize downloading model weights or datasets, loading a model, running image inference or method gradients, changing Windows security, or spending on RunPod. No sudo command or user password was used.

## Environment and acquisition

- WSL 2 Ubuntu 26.04.1 LTS; Linux kernel `6.18.33.2-microsoft-standard-WSL2`; CPython 3.14.4.
- Isolated, untracked venv: `/home/soroush/.cache/thesis-a6-science-py314`; pip 25.0.1 bootstrapped from the existing checked local wheelhouse.
- NVIDIA GeForce RTX 5070 Ti Laptop GPU; driver 610.88; 12,227 MiB reported by `nvidia-smi`.
- Resolver used the [official CUDA 13.0 PyTorch wheel index](https://download.pytorch.org/whl/cu130) plus PyPI. Candidate selection contained 32 wheels. The first dry-run download timed out after about 98 MB of a 170 MB dependency; a single retry with longer timeout completed. No concurrent or duplicate downloader was started.
- The completed pip dry-run and installation reports have identical selected names, versions, and archive SHA-256 values (32/32). Both ignored report JSON files have SHA-256 `fdcaaa9af989432ea7130bdf74942abb372aa68da652e4184d2c2d13f5a13b58`. The versioned candidate archive lock is [`requirements-wsl-torch-py314.txt`](../requirements-wsl-torch-py314.txt), SHA-256 `dc1e8d2a80371d81ee075ded037c17fefde16f476361903a967b58f1ec5795bd`; all 32 lock rows matched both reports and the installed version set. Only pip is extra in the venv.
- Observed pip cache occupancy after acquisition: 2,778,001,493 bytes, plus the earlier discarded partial download. This is below the authorized 8 GB cap; cache occupancy is not an exact network-traffic meter. The installed venv occupies 5,026,482,435 bytes. Neither directory is versioned.

## Checks and exact result

1. `python -m pip check`: `No broken requirements found.`
2. Installed-package comparison: 32/32 pinned names and versions matched the candidate lock and both pip reports.
3. `PYTHONHASHSEED=0 CUBLAS_WORKSPACE_CONFIG=:4096:8 python scripts/check_torch_cuda.py` from the A6 worktree, using the WSL venv, exited 0 and returned:

   ```json
   {"capability":[12,0],"cuda_available":true,"device_name":"NVIDIA GeForce RTX 5070 Ti Laptop GPU","status":"basic_cuda_pass","torch":"2.12.1+cu130","torch_cuda_runtime":"13.0","torchvision":"0.27.1+cu130"}
   ```

The probe imports Torch and TorchVision and differentiates a 4×4 constant CUDA tensor only. It uses no checkpoint, image, or research input. The prior separate WSL compatibility target imported `transformers`/`CLIPTokenizer` and tokenized an empty string from verified local tokenizer files, but those packages are **not** installed in this Torch venv and the two environments must not be represented as an integrated science lock.

## Remaining A6 blockers

Integrate and hash-lock the method's full Linux dependency set; prove local model/tokenizer/metric loading and numerical parity without weakening policy; establish rights/custody for candidate weights; test full image-conditioned gradient and VRAM fit under an exact approved manifest; obtain independent review. This Stage-1 device pass closes none of those items and does not permit scientific execution or advancement of the official Spec Kit gate.
