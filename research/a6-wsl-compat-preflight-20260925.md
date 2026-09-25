# A6 WSL 2 compatibility preflight (no models)

Status 2026-09-25, issue #7 / draft PR #58: **the Windows `regex` Application Control failure does not reproduce in the newly user-installed WSL 2 Ubuntu runtime.** This is a bounded import/device-visibility result, not a complete Linux science environment, model compatibility result, scientific experiment, or A6 acceptance.

## Authorization and boundary

The user explicitly approved WSL 2 + Ubuntu installation and a no-model Python/`regex`/`transformers`/CUDA compatibility probe. The user installed WSL and Ubuntu. No credential was needed or used by the agent. We did not change Windows Application Control, install a Linux NVIDIA display driver, load model weights, acquire a dataset, run a CUDA kernel, spend on RunPod, or advance Spec Kit.

## Observed environment and exact software bytes

- `wsl.exe --list --verbose` reported Ubuntu running as WSL version 2; `wsl.exe --status` reported Ubuntu as the default and WSL 2 as the default version.
- Ubuntu 26.04.1 LTS supplies CPython 3.14.4. Its system Python had neither `pip` nor `ensurepip`; noninteractive `sudo -n true` failed. The agent did **not** use privileged installation or the user's password.
- The verified Windows project Python/pip 25.0.1 downloaded 18 Linux wheel candidates for CPython 3.14 and `manylinux_2_28_x86_64`/`manylinux2014_x86_64`, then installed them into ignored `.thesis-build/a6-wsl-compat-py314` with cross-platform pip `--target --only-binary=:all: --no-compile`. This target was exposed to Ubuntu solely through `PYTHONPATH`; it is not a Linux virtual environment or the project science lock.
- `requirements-wsl-compat-py314.txt` lists all 18 candidate versions and their measured Linux wheel SHA-256 values. A second fully offline `pip download --no-index --require-hashes` against that lock and the ignored wheelhouse succeeded for all 18. The pinned `transformers==4.57.6`, `regex==2026.9.10` and `tokenizers==0.22.1` versions match the intended Windows science package versions; several transitive versions differ from that 42-wheel Windows environment. Do not treat Windows wheel hashes as Linux hashes.

With `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1`, an Ubuntu `python3` process imported `regex`, `tokenizers`, `transformers`, `numpy`, `safetensors`, and `CLIPTokenizer` without error. It printed Python `3.14.4`, regex `2026.9.10`, tokenizers `0.22.1`, transformers `4.57.6`, NumPy `2.5.3`, safetensors `0.8.0`, and `CLIPTokenizer` class available. The only warning was the expected absence of PyTorch/TensorFlow/Flax models. This demonstrates the native Linux regex wheel can load and the Transformers top-level/tokenizer-class import path is viable in this limited runtime; no text encoder instance or pretrained weight was loaded.

`/dev/dxg` was present. NVIDIA's WSL `nvidia-smi` reported `NVIDIA GeForce RTX 5070 Ti Laptop GPU`, Windows driver `610.88`, and `12227 MiB` of GPU memory. This is GPU device visibility, **not** a PyTorch CUDA kernel, backward pass, VRAM fit, or diffusion pipeline result.

## Next A6 requirements

The existing Windows 42-wheel offline rebuild remains valid evidence of Windows package bytes but is blocked by host code integrity at native regex. This WSL result narrows the blocker to a runtime route rather than a need to weaken security. A full candidate Linux science environment still needs an appropriate Python version, a separately SHA-256-locked Linux package set (including CUDA PyTorch/Diffusers), clean local reconstruction, model/metric parity, image-conditioned full method gradient and measured resource fit. Substantial framework/model installation and exact-manifest scientific compute retain their distinct authorization boundaries. Issue #7 and the official `plan-acceptance` gate remain open.

Official runtime references: [Microsoft WSL installation](https://learn.microsoft.com/en-us/windows/wsl/install) and [NVIDIA CUDA on WSL](https://docs.nvidia.com/cuda/wsl-user-guide/). These references describe supported setup, not evidence that the project method has passed.
