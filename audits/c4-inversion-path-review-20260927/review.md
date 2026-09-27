# Pinned inversion path composition review

Author `/root`; actual independent actor `/root/b3_intake_review`.
Authority: AGENTS.md, research/approval-policy.md and the recorded user reconstruction
amendment. Exact initial composition `dc6a3c2ba5c58fe46a54592d25d252cd332e1d41`;
repair `e29af8a`, final exact reviewed `5afd84354a0f60f90f6526cf769de35b7154cd15`.

Reviewed source: src/embedding/inversion_path.py, scripts/test_c4_inversion_path.py,
research/c4-inversion-path-design-20260927.md, with the unchanged previously reviewed
pair solver. This is narrow ordinary composition review, not a lifecycle decision,
real-model parity, scientific execution permission, reconstruction gain or C4 closure.

## Actual independent blocker and repair

The initial 15 authored path tests passed, but independent owned CPU probes found
one blocker: root UNet identity/device/dtype/eval checks did not bind named child,
parameter/buffer objects or mutation versions. Replacing a frozen fp32 parameter
with different-content same-profile data, or ordinarily modifying a buffer in
place, still passed `_validate()`, allowing predictor drift between inverse and
replay. This was a concrete defect, not a theoretical weight-authentication request.

Repair binds named module and parameter/buffer identities, Torch mutation versions,
shape/strides/device/dtype/gradient/training state; retains original objects against
id recycling; validates before and after each prediction. Untracked inference-mode
tensors are explicitly refused. Regression tests cover replacement, ordinary
in-place changes, same-profile new children and forward-side changes.

The first repair test run had one fixture assertion failure: a newly added
nn.Identity defaulted to training mode, so the existing training guard correctly
refused it before the fixture's expected identity-guard message. Final fixture uses
`.eval()` to isolate the new identity check. The failed e29af8a checkpoint is retained;
no history rewrite or scientific outcome tuning.

The actual reviewer independently reran original substitution/in-place probes;
both now reject. It ran all 19 final owned CPU path tests and separately verified
sequential affine inverse arithmetic against returned states. No remaining narrow
composition blocker at exact5afd843. Inverse/replay order, nonunit terminal alpha,
replay budget reservation, returned residuals and persistence-before-completion
also showed no blocker. No source edits made by reviewer.

## Author test evidence and remaining limitations

- WSL owned combined inversion-path/pair/reconstruction/localization suite:
  final47 tests, 46 passed, one explicit Windows-path skip. New path suite19 passed.
  Actual pinned scheduler arithmetic and owned CPU fake UNet only.
- Verified Windows base scripts discovery: final261 tests, 197 passed,64 expected
  dependency/platform skips. New Torch tests were actually executed in WSL, not
  represented as completed Windows learned-model checks.
- Broader Windows tests/ discovery:156 cases,120 passed,34 skips,2 actual import
  errors (`test_b4_canonical`, `test_preprocess`) because NumPy is absent from that
  base venv. These are preserved failures, not rewritten as expected skips.
  After inspecting their synthetic fixtures, existing WSL canonical/preprocess/
  embedding suite27 tests:26 passed,one JSON-Schema skip. No install inferred.
- GitHub dependency reads: #18 and #19 open; #16/#17 closed. Official read-only
  controller: d916749c paused plan-acceptance, null choice, workflowSHA
  772a1a3b1a4ff674c878b0532485820f860e81490e026441a0bb384a3aebda51.
  No lifecycle transition or invented verdict. No active Python/WSL/curl writer
  appeared in the initial native process inventory.

Tensor `_version` is a pinned private runtime dependency and not a content hash.
Deliberate `.data`/raw-storage edits and hostile method tampering are excluded from
the accidental-drift guard; trusted source ownership and actual loader asset hashes
remain mandatory. No bitwise CUDA determinism or real UNet/VAE numerical parity
is established. Cooperative deadlines cannot kill a stuck model call; external
runner timeout/memory checks and durable worker journals are still required.

Next coherent package: versioned reconstruction comparison config, real-loader/
VAE/native PNG/safety/metric bindings and full worker/manifest review before actual
exact user compute approval. Original random-noise route stays a historical control.
All old negative/OOM records and consumed approvals remain; old localization question
unchanged, no repetition. No learned model/study image/GPU/download/install/paid run
was used for these checks. C4/#18 open, PR #67 draft; C5 remains dependent.
