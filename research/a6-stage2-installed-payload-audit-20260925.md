# A6 installed Stage-2 payload byte audit

Status 2026-09-25: **24/24 Stage-2 installed package payloads match their hash-locked candidate wheels in the checked scope**. This is a read-only, model-free environment audit for issue #7 / draft PR #58, not a clean installation, complete environment lock, metric/model check or scientific experiment.

The source lock is `requirements-science-stage2-win312-hashes.txt`, SHA-256 `0f9cc032fdda00a220cff6272f0219e1eb41ec3fb5c9513368746649e2d35271`. The candidate root is the existing ignored `.thesis-build/wheels/a6-stage2-all` directory containing the 24 previously PyPI-matched wheels. The interpreter is the existing isolated Windows CPython 3.12 science venv. The verifier rehashes candidate wheels, checks wheel-embedded name/version against the lock, checks the installed name/version, then SHA-256-compares each wheel package-payload file with the corresponding installed `site-packages` file. It rejects a missing/linked file, a byte mismatch, duplicate or unsafe archive member paths, ambiguous/incorrect wheel identity and a metadata-only wheel. It reports only relative file names, not local user paths or environment variables.

Command from the A6 checkout, with the explicit science interpreter:

```powershell
& 'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/a6-science-venv/Scripts/python.exe' scripts/check_stage2_installed_payload.py --wheel-root 'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/wheels/a6-stage2-all' --hash-lock requirements-science-stage2-win312-hashes.txt
```

The observed JSON summary is `status=payload-match`, `locked_distribution_count=24`, `payload_match_count=24`, **5388 compared package-payload files**, **zero mismatches**, **124 excluded wheel metadata files**, and **zero `.data` files requiring an installation transform**. The full per-distribution file counts and locked wheel digests are emitted by the command; the 24 digest values are also preserved in the lock. The workflow Python suite discovered **81 tests: 79 passed, two expected skips**, including four new synthetic tests for matching bytes, altered bytes, skipped `.data`, unsafe/duplicate members and metadata-only artifacts. `git diff --check` passed.

This check does **not** compare `.dist-info` metadata, generated console scripts, post-install additions or files not declared in a candidate wheel; it does not establish that the exact same installation can be repeated on a clean host. It covers only the 24 Stage-2 locked distributions, not Torch/CUDA, CLIP, LPIPS, bootstrap packages or the remaining dependencies. It does not load any model, execute an image, test numerical equivalence, resolve model custody/rights, measure method VRAM/gradients, approve compute, close A6 or advance Spec Kit `plan-acceptance`. Those are separate prerequisites.
