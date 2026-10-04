# Exact generated-source normalization audit correction

2026-10-04; gpt-6-astra/xhigh requested execution diagnosis. No GPU operations, models, held-out inputs, thresholds, retained outputs or frozen source files were changed. This is a numerical audit correction, not a scientific method amendment or a tolerance exception.

The completed generated shared-engine run `MAIN/.thesis-build/rehearsal/20261004-1219-candidate-real/real-0` has worker receipt SHA-256 `39d24cbc5cdfccd676a1555792ea51cbad0865fa0a033dbb82d3b6f09e95260c`. Frozen `m1_candidate_adapter.py:100` moves an FP32 integer tensor to CUDA and then divides by scalar255. Frozen `m1_candidate_rehearsal_worker.py:385` constructs its audit target by dividing on CPU. These sequences give different FP32 bytes on the recorded Torch2.12.1+cu130/CUDA13.0 runtime.

The independently specified CPU expression is `RN32(float32(RGB8) * RN32(1/255))`, followed by the same NCHW tensor layout. The rounded reciprocal is binary32 `0x3b808081`. Torch CPU multiplication and independent NumPy FP32 multiplication both reproduce the recorded CUDA target hash exactly:

| Construction | Full typed-tensor SHA-256 |
|---|---|
| Recorded CUDA target; CPU rounded-reciprocal multiplication | `7c0be0278b495bdd73fcca76fda249e9c7737b1b26c9e4d67441eae60395482e` |
| Original CPU direct division | `5b685af1f0c49f8ef271f0f2ec54b4f21ff62f3674c3eff420445cdfccf6081c` |

The generated source contains all256 byte values. Exactly360408 of786432 components differ between the two CPU constructions; maximum absolute difference is `2^-24 = 5.960464477539063e-08`. This small size explains the cause but is **not** used as an acceptance tolerance. The corrected hash must be exactly equal. This evidence is scoped to the pinned execution policy; it is not a claim that all CUDA versions, tensor divisions or future kernels use this arithmetic.

New `scripts/m1_target_normalization_audit.py` supplies `target_from_rgb8(rgb, runtime)`. It selects the fixed reciprocal construction solely from the declared runtime, never tries alternatives to satisfy an observed hash, rejects unknown Torch/CUDA/device policy and returns only a CPU tensor. Its `diagnostic(directory)` invokes the existing unmodified `validate_phase_checkpoint` with that tensor for every checkpoint. On the retained full run all32 sealed states passed:21 initialization states and11 embedding states, including binding, target hash, latent shape, optimizer provenance, full state integrity and RNG validation. CUDA remained uninitialized. This focused proof does not reclassify the failed original full artifact audit or certify lifecycle parity.

Four CPU tests passed in0.101s: every RGB8 symbol against independent NumPy arithmetic; exact generated-source recorded hash and direct-division counterexample; rejection of unvalidated runtime/noncanonical input; and source immutability. The diagnostic read preserved checkpoint receipts and loaded only CPU `weights_only=True` state.

Minimal integration, after the live prefix finishes: replace only the audit target construction with `target_from_rgb8(source, record['binding']['runtime'])`, and include `scripts/m1_target_normalization_audit.py` in the worker's declared dependency inventory. Leave `CandidateAdapter._source`, initialization, embedding, quality, reader and resumed state restoration unchanged. Worker resume itself calls the audit at line212, so the correction must be present there through the same audit function; correcting only an external coordinator would be insufficient.

The parent chose a new committed audit dependency/core and fresh generated full/prefix/resume suite, retaining the original full and prefix and their audit failures. This avoids patched-process entrypoints and mislabeled dependency receipts. Because the helper enters the declared core, the old full/prefix cannot be passed off as a new-core recovery reference. The new run must pass the complete artifact audit and exact full-versus-resumed states/Adam/RNG/endpoints; numerical tolerance remains zero. No monkeypatch, audit bypass, checkpoint rewrite or original-result replacement is recommended or implemented.
