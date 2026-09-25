# A6 offline scientific-environment reconstruction receipt

Status 2026-09-25, issue #7 / draft PR #58: a **clean, isolated Windows CPython 3.12 software rebuild succeeded from 42 locally cached, SHA-256-pinned wheels**, but the full proposed scientific runtime is **not usable on this host** because Windows Application Control blocks the `regex` native extension required by `transformers`. This is environment reconstruction evidence, not A6 closure or scientific acceptance.

## Inputs and isolation

- Host: the same Windows laptop and verified project Python 3.12 interpreter. The earlier original science venv and public model assets were not modified or re-downloaded.
- Lock: `requirements-science-candidates-win312.txt`, SHA-256 `05537bfedd17a093583a4710fad7593ad3770ab14acf52e44b2ccebb10fbd7ef`, with 42 exact wheel hashes. The 24 Stage-2 hashes remain its exact subset. This file is a local candidate-byte lock, not independent provenance for every package.
- `scripts/prepare_science_wheelhouse.py` selected only byte-matching wheel archives from the already-existing ignored `.thesis-build/wheels`, pip HTTP/built-wheel caches and the bundled `ensurepip` wheel. It copied them into ignored `.thesis-build/a6-offline-wheelhouse`: 42 wheels, 2,042,347,979 bytes. No network, package installation, model load, GPU work or scientific data was involved in materializing the wheelhouse.
- A new ignored `.thesis-build/a6-science-rebuild-20260925` virtual environment was created with the verified interpreter. Its install used `pip install --no-index --no-cache-dir --require-hashes --find-links <offline-wheelhouse> -r requirements-science-candidates-win312.txt`. It exited zero and installed all 42 pinned distributions. This was a bounded local software-reproducibility check, not new asset acquisition or scientific compute.

## Checks and observed failure

- `pip check`: `No broken requirements found.` The original and clean venv `pip list --format=json` each contained the same 42 name/version pairs, with no comparison difference.
- In the clean venv, importing `torch==2.12.1+cu130`, `torchvision==0.27.1+cu130` and `diffusers==0.35.1` succeeded; `torch.cuda.is_available()` returned `True`. No model was loaded or inferred.
- The existing payload checker compared 21,914 package files across all 42 wheels with zero byte mismatches. It reported 41 `payload-match` and one `payload-partial`, solely because SymPy's wheel places `share/man/man1/isympy.1` under a PEP 427 `.data` scheme the checker deliberately excludes. The wheel member and clean installed manual both measured SHA-256 `f4365d48e2102e292b0131e56e4743674e0b0508a0643504d3fa025c10ef741b`. The checker also excluded 238 `.dist-info` metadata entries; do not call this a complete byte-for-byte installation proof.
- Importing `transformers==4.57.6` in the clean venv failed with `ImportError: DLL load failed while importing _regex: An Application Control policy has blocked this file.` The same import in the original science venv failed identically. This corroborates the previously recorded Code Integrity restriction on the unsigned `regex` extension; the clean build did not repair it. `pip check` and successful package installation do not detect this runtime failure.

## Acceptance boundary and next decision

The verified image-only CLIP adapter does not import `regex`, so its bounded A5 image-encoder path remains available. It does **not** fix `transformers` or make the text-conditioned Diffusers method runnable on this Windows host. Do not disable Smart App Control, bypass Code Integrity, replace upstream tokenization with an unreviewed approximation, or claim scientific parity. A6 remains open. A compatible separately approved execution environment, or a reviewed method-preserving implementation that avoids the blocked native dependency, must pass clean imports and later exact-manifest scientific checks before method execution. RunPod spending, WSL/host configuration changes and scientific runs are not authorized by this receipt.
