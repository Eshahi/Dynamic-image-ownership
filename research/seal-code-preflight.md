# SEAL code preflight — no execution approval

Issue #8, downstream METRIC-07/HYP-03. Read-only inspection 2026-09-23 UTC.
Repository: https://github.com/Kasraarabi/SEAL
Default branch discovered from API: master.
Pinned commit: `92d31b31b93a6e373fe88a584c640beafb68c6fa`.
Inspected tree, README.md, setup.sh, requirements.txt, SEAL.py, semantic.py, and relevant utils.py functions. Pin file links under `https://github.com/Kasraarabi/SEAL/blob/92d31b31b93a6e373fe88a584c640beafb68c6fa/`.

## Findings affecting readiness

- setup.sh uses sudo/apt and conda then force-reinstalls requirements. It is not a native Windows setup procedure. Do not run it on this project environment.
- requirements.txt pins diffusers 0.20.2, transformers 4.47.1 and mixed CUDA package generations. Native Windows/5070 Ti compatibility and sufficient memory remain untested; no claim that these pins are usable here.
- SEAL.py calls wandb.init unconditionally after parsing an --online flag. That flag does not guard initialization in this entry point; semantic.py does guard its own call. Actual network behavior depends on external W&B settings, so do not assume an offline run by omission of --online.
- SEAL.py loads Stable Diffusion 2.1 base, BLIP-2 FLAN-T5-XL, a fine-tuned sentence embedding model, and a prompt dataset using network-capable loaders. Download sizes, access terms, hashes and available memory must be inventoried before execution.
- Entry-point defaults process 1000 prompts. It generates proxy, marked and unrelated images and performs 50-step inversion calls. This is a scientific experiment, not a harmless import/smoke test.
- SEAL.py supplies fixed seed 42 to generate_initial_noise. utils.py's simhash uses seeded random projections and hashes a tuple containing projection bits and index offsets. Do not describe the inspected example as deploying the paper's per-user secret-salt security model; reconcile code and threat model before a security comparison.
- generate_initial_noise fixes the noise shape to [1,4,64,64]. Arbitrary resolution/model portability is not established.
- No LICENSE/COPYING file appears in the inspected tree. Record repository reuse permissions as unresolved; public readability is not an affirmative permission check. No upstream code has been copied into the project or modified.

## Next bounded work

Decide a clearly labeled reproduction adapter versus paper-faithful implementation, preserving provenance of any differences. Pin model/configuration and preprocessing; explicitly disable external logging; preserve exact candidate access; validate outputs with ordinary isolated tests before any approved scientific run. Do not silently substitute this baseline into the proposed DCT detector. No checkpoint, dataset or package acquired; only public source text read. No experiment, remote rental or new service activated.

Initial main-branch API request failed422 and dependent read requests failed404; recovered by querying default_branch and pinning master. These were discovery failures, not evidence of a missing repository.
