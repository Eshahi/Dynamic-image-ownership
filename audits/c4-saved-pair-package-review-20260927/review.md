# C4 retained-triplet execution package: independent launch/design review

Author `/root`; actual independent actor `/root/b3_intake_review` under AGENTS
and research/approval-policy.md. This review is qualified software/design
launch readiness only, NOT execution approval, scientific results, C4 closure,
neural metric parity, rights certification or Spec Kit gate acceptance.

## Exact candidate and retained scope

Final reviewed code commit `ac5bd9a04d7d83bfa88cb6fc368d77b5239e182f`;
candidate canonical manifest SHA-256
`9dc57c699c783a2a8d3ad3b6ecebed6c5d7be7e9754c5edec5f6667b49a19b38`.
Experiment `c4-saved-pair-quality-development-v1`, one run
`c4-saved-pair-dev-001`, local, USD0, 1200 seconds, fixed Torch4096MiB.
Exactly the retained source/control/candidate from run003, three native quality
comparisons, three C2/C3b re-extractions and output/source radius-one diagnostics.
No new data, regeneration, attacks, calibration, held-out images or downloads.
All21 exact source/config/spec/environment input pins were independently
reproduced; official design helper and runner dry preview agree and explicitly
require a new actual exact user approval. The consumed003 approval is not reused.
Final documentation-only commit must be rebound before the actual question;
its manifest remains outside Git to avoid circular commit binding.

## Findings, repairs and actual verdict

Initial `56327a7e3aa15f84c17c306ef3696e37b80a241f` blocker: fsynced completion
events retained labels but actual measured values existed only in memory until
terminal JSON. Forced interruption could lose completed outcomes. Repairs
`109d81c`, `6a413ee`, `a770941` retain full classical/code/drift/LPIPS payloads
and exactly nine pending/running/completed/failed outcome cells in fsynced
progress; no terminal report means interrupted/incomplete, never completed.

Re-review `a770941` found caught failures left active cells running rather
than terminal-failed. `ac5bd9a` repairs this with a tested pure helper: active
cells become failed, previously completed/pending cells remain unchanged,
and original failure phase survives durable cell-failure events.

Failure-telemetry warning also repaired: bounded message/phase and isolated
best-effort resource readings do not mask the original error. On timeout a
missing final file remains missing; no fabricated clean negative/result.

Actual final reviewer verdict: **no remaining narrow code/design blocker** at
`ac5bd9a04d7d83bfa88cb6fc368d77b5239e182f`. Reviewer independently verified
encoder.extract_features API/signature tuples, fixed reference pairs/source
enrollment replay, package/environment/local-weight binding, offline defenses,
resource headroom and child1140s+10s within parent1190s/outer1200s. Socket
blocking is defense-in-depth, not an OS network sandbox; RAM/disk/time/VRAM
planning estimates are not measured fit or whole-system allocation enforcement.
No CPU/GPU replacement, retries, reference switching or source relabeling.

## Verification and preserved limitations

- Actual independent + author WSL: all21 owned synthetic CPU tests pass,
  nine package tests and twelve quality/drift tests. No real pixels/models/GPU.
- Author Windows base scripts suite: 214 tests, 191 passed/23 expected skips.
  Owned quality NumPy tests run in the pinned WSL science venv, not base Windows.
- Byte-only prior custody check verifies source125000/control293695/
  candidate293660 and enrollment q/h/Ws/Wi without decoding or scoring images.
- Intermediate reviewer v2 helper directory was absent, and HEAD advanced
  during its v2 comparison; that transient comparison failed. Final ac5/v3
  comparison passed. No intermediate failure was converted into a science run.
- Prior full WSL discovery's unrelated jsonschema import errors remain
  recorded in the component audit; no package installation/false full-suite pass.
- Official d916749c remains paused at plan-acceptance, null choice, state hash
  `772a1a3b1a4ff674c878b0532485820f860e81490e026441a0bb384a3aebda51`.
- No study quality/key-drift results exist yet. One original source is not
  independent N=3, final dataset coverage, blind detection or ownership proof.

Before execution, final exact clean-commit manifest must pass independent
binding check and official preview, then an actual user decision bound to that
manifest/target/resource ceiling. Do not invoke either scientific entrypoint
directly or infer compute approval from user resumption.
