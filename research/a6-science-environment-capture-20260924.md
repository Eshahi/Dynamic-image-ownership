# A6 science environment capture receipt

Status 2026-09-24: **clean-checkout metadata capture, not full reproducibility or method qualification**. Issue #7 / draft PR #58. `scripts/capture_science_environment.py` is a read-only science-venv companion to the older CPU/workflow `scripts/capture_environment.py`. It records every installed distribution name/version, exact digests of six declared project lock/config files, Git commit/dirty state, Python/OS/architecture and `nvidia-smi` GPU identity. It does not emit host/user paths, environment variables, credentials, model contents or dataset entries; it does not import Torch/CLIP/LPIPS or load a model.

The first actual science-venv invocation, from clean commit `5923f7a5f082a1e5b139ae4b62179d1920dc447d` at `2026-09-24T20:14:03.020833+00:00`, returned `a6-science-environment-v1`, `git_dirty=false`, Python 3.12.14 on Windows 11 AMD64 and **42 installed distributions**. Selected installed versions: Torch `2.12.1+cu130`, TorchVision `0.27.1+cu130`, Diffusers `0.35.1`, Transformers `4.57.6`, CLIP `1.0`, LPIPS `0.1.4`, NumPy `2.5.2`, Pillow `12.3.0`, pip `25.0.1`, setuptools `78.1.0`. The output JSON includes all 42, not only these selected examples.

The `nvidia-smi` snapshot returned `observed`: NVIDIA GeForce RTX 5070 Ti Laptop GPU, driver `610.88`, capability `12.0`, 12,227 MiB total and 11,262 MiB free at capture time. Free memory is transient; these numbers do not establish full gradient fit or performance.

| Declared project file | Captured SHA-256 |
| --- | --- |
| `requirements.lock` | `c26d467d208f6cfecf6dcfb6ac8a21a18824ff7f7ad56e5bbdfb7adeb6de0aaf` |
| `requirements-science-stage2.txt` | `b355e29d7c1f8d9dddd52a0826a2c3a490108578c2a071714b6072cfc800f7b9` |
| `requirements-science-stage2-win312-hashes.txt` | `0f9cc032fdda00a220cff6272f0219e1eb41ec3fb5c9513368746649e2d35271` |
| `requirements-science-lpips-win312-hashes.txt` | `267e9fed598c0494fee1d3a1ab34d139b0938c1df9bcccffcb200dd15caf01a4` |
| `requirements-science-clip.txt` | `b78e17c1e0de9dc5e90ef647fc2cca8f0f71f9faed3627ad6e0f04453a460853` |
| `research/a6-candidate-model-assets.json` | `b8c2595857853ea5b7835bb71f12a34dde07b78623c5e638f692dc7eb220b27e` |

All six files were present. A missing file would be recorded as `null`, not a fabricated digest. The repository suite found **75 tests: 73 passed and two expected skips**, including three new synthetic capture tests; `git diff --check` passed. No download, install, dataset read, model/metric load, CUDA operation or Spec Kit transition occurred.

This receipt is a version and input-identity snapshot, **not** a complete wheel/source lock, installed-file equivalence proof for all packages, verified model rights, local-to-RunPod parity, or scientific result. The [wheel inventory](a6-science-wheel-inventory-20260924.md) still reports missing checked candidate wheels for pip/setuptools, and the [pinned CLIP file audit](a6-clip-install-byte-audit-20260924.md) covers only its five source-package files. Capture must be repeated with the exact reviewed commit and approved execution manifest on every actual host. A6/#7 remains open; the bounded metric-load permission question remains pending.
