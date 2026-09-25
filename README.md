# Dynamic Image Ownership

This repository contains the reproducible research harness and execution plan for a thesis on dynamic image ownership and watermarking.

## Current status

- The thesis workflow has been reduced from 58 source tasks to 38 traceable execution issues.
- Five milestones and seven lifecycle gates define delivery. Routine technical acceptance is delegated; user decisions are reserved for material scope changes, compute authorization, and final acceptance. See [approval policy](research/approval-policy.md).
- Eight reusable agent skills cover workflow control, research handoff, literature synthesis, experiment design, compute execution, results analysis, evidence audit, and thesis writing.
- Local and mock-provider execution are implemented and tested.
- Live RunPod creation remains disabled until an enforceable time and spending boundary is validated.
- Codex Remote is the human interaction channel for progress notifications, review, and explicit
  necessary decisions; no project-specific messaging bot or gateway is required.

Read [the continuation record](thesis-runs/d916749c/continuation.md) for actual task readiness. A completed workflow prompt does not prove its scientific outputs are complete.

## Repository policy

GitHub-facing project management content is written in English. The original offline guide remains unchanged as a provenance artifact. Work must be linked to its GitHub issue through the branch name, commits, pull request, manifests, and evidence records.

Never commit credentials, API keys, environment files, raw private tokens, large datasets, model checkpoints, or large run outputs. Store manifests, checksums, and durable artifact references instead.

## Execution plan

The reviewed execution profile contains five milestones:

1. Specification
2. Data & Literature
3. Implementation
4. Evaluation & Statistics
5. First Review

The deterministic issue seed is stored at `thesis-agent-skills/fixtures/github-issue-seed-38.json`. The immutable source-to-task mapping is stored at `thesis-agent-skills/fixtures/guide-plan-38.json`.

## Local setup

See `thesis-agent-skills/INSTALL.md` for environment preparation, skill installation, Spec Kit workflow installation, Codex Remote requirements, and the synthetic smoke test.

On this Windows host, use the verified Python 3.12 interpreter to create an ignored CPU workflow/contract-test venv and install the [pinned workflow lock](requirements.lock). For another host or a fresh clone, substitute its verified Python 3.12 executable for the first command:

```powershell
& '.thesis-build/venv/Scripts/python.exe' -m venv '.thesis-build/a6-cpu-venv'
& '.thesis-build/a6-cpu-venv/Scripts/python.exe' -m pip install -r requirements.lock
& '.thesis-build/a6-cpu-venv/Scripts/python.exe' -m pip check
```

The workflow lock does not install PyTorch, model weights, datasets, or a RunPod environment. The [environment record](research/environment.md) distinguishes the Windows-native `regex` security block from the separately rebuilt WSL scientific-software environment.

For the **same-host offline WSL science setup**, use Ubuntu 26.04.1 / CPython 3.14 and the existing hash-checked local wheelhouse. The tested source lock is [`requirements-wsl-stage2-py314.txt`](requirements-wsl-stage2-py314.txt), which includes the Stage-1 Torch/CUDA lock. Ubuntu's system CPython 3.14 here lacks `ensurepip`, so the fresh venv must bootstrap pip from the already checked local wheel. From the repository root in WSL:

```bash
SCIENCE_VENV=/home/soroush/.cache/thesis-a6-science-rebuild
SCIENCE_WHEELS=/home/soroush/.cache/thesis-a6-wsl-wheelhouse-reviewed
PIP_WHEEL="/mnt/w/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/a6-offline-wheelhouse/pip-25.0.1-py3-none-any.whl"
python3.14 -m venv --without-pip "$SCIENCE_VENV"
PYTHONPATH="$PIP_WHEEL" "$SCIENCE_VENV/bin/python" -m pip install --no-index --no-deps "$PIP_WHEEL"
"$SCIENCE_VENV/bin/python" -m pip install --no-index --no-cache-dir --find-links "$SCIENCE_WHEELS" --require-hashes -r requirements-wsl-stage2-py314.txt
"$SCIENCE_VENV/bin/python" -m pip check
```

The separately pinned official CLIP source-built wheel must be verified and installed `--no-index --no-deps` as described in the [clean WSL rebuild receipt](research/a6-wsl-clean-rebuild-20260925.md); it is **not** covered by the 60-wheel lock above. That receipt records the tested offline pip-bootstrap path and first failed attempt. These commands require already-present checked wheels and do not fetch models or datasets. A fresh host, model rights, scientific numerical parity, full gradient/VRAM fit and paid remote execution are not certified by this setup.

## Scientific status

The [research contract](research/research-contract.md) and [scope guard](research/scope-guard.md) bind implementation to the source method. Transfer/ledger development and automatic substitutions of the embedding or detector are outside routine execution authority. Unresolved scientific choices remain explicit downstream prerequisites; traceability coverage is not experimental validation.

The repository provides infrastructure and a research plan. It does not, by itself, prove the proposed method, validate a scientific claim, or constitute university approval.

## Approved proposal provenance

Task A1 preserves the approved Persian proposal as immutable local source material. The source file is intentionally excluded from Git, while its identity, SHA-256 checksum, size, extraction method, content inventory, and known extraction limitations are recorded in `inputs/proposal-source.json`. A mechanically extracted, non-translated text representation is stored in `inputs/proposal-text.md`.

The extracted representation retains document-order paragraphs and explicitly labelled table cells. Equations and embedded visuals that could not be converted reliably are represented by numbered placeholders and remain authoritative only in the original proposal file. No scientific claims in the proposal are treated as experimentally validated by ingestion.
