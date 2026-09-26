# Independent C4 C1 validation-bridge review

2026-09-26. Author `/root`; actual independent reviewer `/root/b3_intake_review`, delegated under AGENTS.md / research/approval-policy.md. **Narrow partial software acceptance only**, not C4 closure, human verdict, scientific acceptance or permission.

Initial exact code reviewed: `41fe458db7fb7b7de8c1d05cf04b55696db5b65f`. Final repair independently re-reviewed: **`32280d19a5723c086b507e1c37e9700138658bb4`**. Artifacts: src/embedding/validation_bridge.py, tests/test_c4_validation_bridge.py, scripts/embed.py and research/c4-c1-validation-bridge-20260926.md, against unchanged src/runtime/config.py / A5 validator/schema/dependencies. The production validator and science environment were not modified.

## Finding, repair and actual checks

Reviewer found no false full-validation verdict within the expressly documented trusted-launcher boundary. Actual Windows C1 accepted the owned full-shaped specimen and rejected an invalid safety-policy config whose changed bytes were honestly pinned in its test manifest. Input/config/schema/validator/run/seed/commit mutation and replay cases failed closed. Initial suites: Windows ten tests, nine pass / symlink skip; WSL ten tests, nine pass / missing-JSON-Schema skip.

It did find a reproducible bounded-size blocker: an owned valid config padded with trailing JSON whitespace to 1,100,000 bytes produced a 2,201,516-byte receipt due to raw-config hex expansion. That receipt exceeded the consumer's two-MiB read cap. Initial code was **not accepted** at this boundary.

Repair checks final serialized size before exclusive file publication. The regression uses actual full C1 validation in Windows and explicitly mocked owned validation snapshots in Linux; a valid but oversized receipt is now rejected without creating a receipt. Actual independent final message: original size reproduction rejects with no receipt, genuine Windows C1 exercised; **no remaining blocker for this narrow validation-bridge checkpoint**. Both reviewer bridge suites: eleven tests, ten pass / one documented platform-specific skip; clean checkout and diff check passed.

Root final suites: Windows bridge/embedding/local-assets/output/instance/owner/runtime **63 tests, 42 pass / 21 expected dependency/symlink skips**; WSL bridge/embedding/local-assets/output **38 tests, 35 pass / three expected JSON Schema skips**; legacy scripts **185 tests, 174 pass / 11 expected skips**. No pytest invocation or dependency installation. Source-inspection/path guesses and atomically failed patch context are retained in the implementation note rather than turned into successful checks.

## Delegated disposition and limits

Author `/root` accepts this narrow bridge checkpoint after the actual independent repair review. It resolves the software design prerequisite of conveying full Windows C1 validation into the existing Linux science process without an invented Linux validator or new installation. It does **not** mean an integrated launcher/worker has been built or executed. No actual scientific C4 config, manifest or approval is created; development embedding manifest still has zero execution rows. #18 remains OPEN and PR #67 remains draft.

Receipt verification is not authentication: a self-consistent fabrication outside trusted reviewed code cannot be authenticated by hashes or actor fields. The complete exact-code/environment/input inventory, real official-runner user approval and host/filesystem trust remain mandatory. The helper neither starts a process nor creates a verdict; official clean-commit checks and full execution-schema validation remain the runner's responsibility. Future integration must bind all transitive worker dependencies, not just this bridge's required set.

All checks used owned small code/config copies, synthetic full-shaped config bytes and CPU JSON/file operations. No models or checkpoint assets, real study-image files, GPU, scientific execute, downloads, installs, paid services or lifecycle writes occurred. The user's original root HTML edit was inspected and left untouched. Earlier C2 exact-run approval remains consumed. Official controller read: d916749c paused plan-acceptance, choice null, workflow SHA-256 `772a1a3b1a4ff674c878b0532485820f860e81490e026441a0bb384a3aebda51`.

Next: integrated reviewed parent/child with bounded deadline and full failure inventory; supported preregistered development feasibility outcomes; honest development/pre-calibration configuration distinction with no invented final thresholds; all resource/input pins; independent package review before a new exact-manifest compute request. Real gradient/VRAM, native saved pair, quality and full blind verification remain unmeasured.
