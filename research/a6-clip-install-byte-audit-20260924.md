# A6 pinned CLIP installed-source byte audit

Status 2026-09-24: **five pinned source-package files match a cached wheel byte-for-byte; model and full environment remain unverified**. Issue #7 / draft PR #58. This read-only check did not import or load CLIP, run a checkpoint or image, touch CUDA, acquire data, download/install software, or advance Spec Kit. It applies the [research contract](research-contract.md) and [scope guard](scope-guard.md).

`scripts/audit_a6_clip_install.py` first hashes the existing pip-built `clip-1.0-py3-none-any.whl` and requires SHA-256 `68fc1aa1fc25591c3c61e621cfd47b6f8e19536901db70f5da0c1af1ba485969`. Its adjacent pip-cache `origin.json` and the science venv's installed `clip-1.0.dist-info/direct_url.json` must both name `https://github.com/openai/CLIP.git` and exact commit `d05afc436d78f1c48dc0dbf8e5980a9d471f35f6`. It rejects missing or linked inputs. It then compares the bytes of the five source payload files in that wheel with the installed science-venv files:

| File | Matched SHA-256 |
| --- | --- |
| `clip/__init__.py` | `f6ddc7cbe2e119c937398de04e4d064976cc0110c5618bc7312fa595967ae3b4` |
| `clip/bpe_simple_vocab_16e6.txt.gz` | `924691ac288e54409236115652ad4aa250f48203de50a9e4722a6ecd48d6804a` |
| `clip/clip.py` | `3891eee0ad659a781ec3fd0240f9d69b7f3845837f671ff6670accf0d4bad0a2` |
| `clip/model.py` | `dc4981bbd17867430890cfe711bb813466232f3b19c5753e26de0b7b047b0926` |
| `clip/simple_tokenizer.py` | `acf0cda10cad73193af7a0d7184364cca3139b7de464f163fd4953bf2648c608` |

The actual report returned `pinned_clip_source_files_match_cached_wheel` and `source_file_count=5`. The repository suite discovered **72 tests: 70 passed, two expected skips**. Two new synthetic tests cover exact-match and changed installed bytes, wrong origin, and wheel-digest failure; `git diff --check` passed.

This resolves the narrow earlier uncertainty about those *installed source files* versus the locally built cached wheel. It is not an independent attestation that the wheel was reproducibly built from the pinned Git commit, a comparison of all distribution metadata or generated scripts, a proof of the CLIP checkpoint bytes (recorded separately), a model-load/feature numerical parity result, or a complete transitive wheel lock. In particular, `pip` and `setuptools` still lack checked candidate wheels in the existing cache inventory. A6/#7 remains open and the separate CLIP/LPIPS synthetic runtime-probe permission question remains pending.
