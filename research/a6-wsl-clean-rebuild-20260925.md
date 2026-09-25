# A6 WSL clean offline software rebuild (2026-09-25)

Issue: [#7](https://github.com/Eshahi/Dynamic-image-ownership/issues/7). This is reproducibility and model-free import evidence for the candidate WSL science software environment, not A6 closure or a scientific result.

## Inputs and isolation

- Source locks: [`requirements-wsl-torch-py314.txt`](../requirements-wsl-torch-py314.txt) (32 candidate wheel hashes) and [`requirements-wsl-stage2-py314.txt`](../requirements-wsl-stage2-py314.txt) (28 additional hashes, including the first lock). The dry-run/install reports for the original venv matched all 60 names, versions and archive hashes.
- Source archives: pre-existing local pip HTTP and built-wheel caches only. `scripts/prepare_science_wheelhouse.py` selected exact-hash wheel bytes into `/home/soroush/.cache/thesis-a6-wsl-wheelhouse`: 60 files, 2,849,806,456 bytes. The wheelhouse and venv are untracked local files; no download was performed for the clean rebuild.
- Clean target: a new `/home/soroush/.cache/thesis-a6-science-clean-py314` CPython 3.14.4 venv, created without pip. Pip 25.0.1 was bootstrapped offline from the pre-existing checked local wheel.
- Install: `PIP_NO_INDEX=1 pip install --no-index --no-cache-dir --find-links <wheelhouse> --require-hashes -r requirements-wsl-stage2-py314.txt`. The actual command printed **only** the local wheelhouse as a source and installed all 60 pinned wheels. The exact official CLIP source-built wheel from the original WSL transaction, `clip-1.0-py3-none-any.whl`, was separately checked at SHA-256 `6c6f017103d9171720deb40d2592e43d5b9003a29cb48ae2567f7e09e81ac204` and installed offline with `--no-deps`.

## Failure and repair

The first clean install stopped **before installation** because the wheelhouse materializer named the cached `cuda-toolkit` wheel with its first metadata tag, `py2-none-any`, which pip correctly rejects on CPython 3.14. The same wheel's metadata also advertises `py3-none-any`. `scripts/prepare_science_wheelhouse.py` now selects that py3 tag when naming a nameless cached wheel body; a focused synthetic regression test covers a py2-first/py3-second WHEEL metadata file. The original wheel hash and contents were unchanged. Re-materialization added the correctly named local file and the fully offline retry succeeded. The rejected py2-named copy remains ignored in the local cache and was not installed.

## Checks and limits

- `pip check` in the clean venv: `No broken requirements found.`
- `pip list --format=json`: all 62 installed distribution name/version pairs match the original WSL venv. The 60 locked wheel distributions plus pip and CLIP account for the 62.
- With `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1` and `HF_DATASETS_OFFLINE=1`, the clean venv imported Torch/TorchVision, native regex, official CLIP, LPIPS, the Diffusers img2img/DDIM/UNet/VAE classes, and the Transformers CLIP text/tokenizer classes. It returned `clean_offline_import_pass` without checkpoint, image, model instance or CUDA kernel.
- The pinned CLIP Git commit was observed in the original venv's `direct_url.json`; the clean venv installed its checked local built wheel. The installed-version and wheel-byte matches do not independently reproduce the source build or prove every installed payload file matches a wheel.

The software is now cleanly installable offline as a **candidate method environment** under WSL, unlike the Windows environment blocked by native `regex`. This is still not proof that the model configuration/weights load correctly, that publisher/weight rights or custody are resolved, that CLIP/LPIPS metrics match the declared method, or that full image-conditioned gradients fit the GPU. No model/data acquisition, scientific computation, paid compute, Spec Kit gate transition or issue closure occurred. A bounded independent read-focused review of these exact artifacts is required before any A6 technical acceptance.
