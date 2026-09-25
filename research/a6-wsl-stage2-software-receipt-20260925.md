# A6 WSL Stage-2 software-only receipt (2026-09-25)

Issue: [#7](https://github.com/Eshahi/Dynamic-image-ownership/issues/7). This extends the separately authorized [WSL Torch/CUDA Stage-1 receipt](a6-wsl-torch-stage1-receipt-20260925.md), but is **not** a model or method acceptance test.

## Authority and environment

The user authorized installing Diffusers 0.35.1, Transformers 4.57.6, official CLIP/LPIPS and necessary dependencies into the **same isolated WSL venv**, with at most 1 GB of new downloads and model-free import checks. The authorization did not cover checkpoint/image loading, dataset acquisition, scientific experiments, Windows policy changes or paid RunPod. The venv remained `/home/soroush/.cache/thesis-a6-science-py314` on Ubuntu 26.04.1 / CPython 3.14.4; no sudo or user password was used.

## Package identity and installation

- The [Windows Stage-2 transaction pins](../requirements-science-stage2.txt) plus `lpips==0.1.4`, `ftfy==6.3.1` and `wcwidth==0.9.1` resolved to 28 new Linux wheels without replacing the 32 Stage-1 wheels. The completed pip dry-run and installation reports selected the same 28 names, versions and archive SHA-256 digests. Both ignored JSON reports have SHA-256 `c54ee3e06323ead0bc2d140dc23b1c26414babd103bc383bcdbe55ffa9f2394b`.
- The combined candidate wheel lock [`requirements-wsl-stage2-py314.txt`](../requirements-wsl-stage2-py314.txt), SHA-256 `73d5131759fa5559375a9480828e9a1a074dccd509efe57b53f785e10fccd9ff`, includes the 32 Stage-1 and 28 Stage-2 exact archive hashes. A read-only comparison matched all 60 lock rows to their respective dry-run/install reports and the 60 installed name/version pairs. `clip` and pip are the two non-wheel-lock distribution entries.
- The official [OpenAI CLIP source commit](https://github.com/openai/CLIP/tree/d05afc436d78f1c48dc0dbf8e5980a9d471f35f6) was installed separately with `--no-deps --no-build-isolation`; installed `direct_url.json` records that exact commit. Its locally built `clip-1.0-py3-none-any.whl` is 1,369,547 bytes with measured SHA-256 `6c6f017103d9171720deb40d2592e43d5b9003a29cb48ae2567f7e09e81ac204`. A source commit plus one local build hash is **not** yet a clean-source-build parity demonstration.
- Observed pip-cache occupancy increased from 2,778,732,581 to 2,861,737,339 bytes (83,004,758 bytes) across the bounded transaction, including the CLIP build. This is not an exact network-traffic meter, but no large model or data transfer occurred and it is well below the approved 1 GB new-download cap.

## Offline, model-free checks

With `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1` and `HF_DATASETS_OFFLINE=1`, a single process imported Torch/TorchVision, Diffusers, Transformers, native `regex`, Tokenizers, Safetensors, SciPy, scikit-image, LPIPS and official CLIP, plus these method candidate classes: `StableDiffusionImg2ImgPipeline`, `DDIMScheduler`, `AutoencoderKL`, `UNet2DConditionModel`, `CLIPTextModel`, `CLIPTokenizer`. The process returned `import_only_pass`, including `regex==2026.9.10`, `diffusers==0.35.1`, `transformers==4.57.6`, `tokenizers==0.22.1`, `safetensors==0.6.2`, `scipy==1.16.2`, `scikit-image==0.26.0`, `lpips==0.1.4` and `clip==1.0`. `python -m pip check` returned `No broken requirements found.` Stage-1's earlier model-free 4×4 CUDA backward probe had returned `basic_cuda_pass` in this venv before Stage-2 installation; it was not repeated here.

No `from_pretrained()`, `clip.load()`, LPIPS instance, image processing, model GPU operation or project method call was invoked. This establishes that the previous Windows-native `regex` import failure is absent in the integrated WSL software environment; it does **not** establish correct text conditioning, model/checkpoint identity, numerical parity, full gradient/VRAM fit, dataset rights, or a scientifically reproducible experiment.

## Remaining gate boundary

A6 remains open. The 60 archive hashes are a candidate wheel-byte lock, but a fresh **offline clean reconstruction** of this full WSL environment and independent technical review are still needed before software reproducibility can be accepted. The separate CLIP source build must be replayed/checked. Model custody and rights, safe local-only loaders, text/visual/metric parity and full image-conditioned gradient/VRAM fit remain unproven. The official Spec Kit gate stays pending; any scientific run requires its exact-manifest user authorization.
