# Deterministic inversion component review

Author `/root`; actual independent reviewer `/root/b3_intake_review`.
Exact reviewed commit `2be476ea2461769a8e228948e74a4a91fc7437b0`.
Authority: AGENTS.md, research/approval-policy.md and the actual reconstruction-path
direction recorded in research/c4-reconstruction-path-amendment-20260927.md.

Artifacts: src/embedding/inversion.py, scripts/test_c4_inversion.py and
research/c4-inversion-component-design-20260927.md. Reviewer read the exact
component/design, independently ran its 16 owned synthetic CPU tests in the
existing WSL clean science environment and checked 12 mixed-coordinate inversion
probes, actual predictor-call counts, evaluation ceilings and returned residuals.
No blocking component defect found. This is narrow ordinary software acceptance,
not a lifecycle verdict, scientific evidence or C4 closure.

The review checked DDIM algebra, mutation isolation, rejected-trial counting,
forward residual versus guided objective, detached return values and callback
failure propagation. Explicit modified guided-coordinate safeguards are not a
faithful GNRI reproduction. Frozen deterministic predictor weights, prior
selection, full trajectory/source-terminal-alpha semantics, durable crash-safe
storage, whole-path resources and guarded scientific integration remain unproved.
No learned model, study image, CUDA computation, install or download was run.

## Author checks and preserved failures

- Initial 13-test component suite passed. Expanding it to 16 found a failed
  unsafe-denominator fixture expectation: on a positive target the solver correctly
  stopped after 7 evaluations rather than the fixture's expected first evaluation.
  The fixture changed to a negative target so initial `gradient + eta` cancels;
  the same solver then explicitly refuses the first unsafe update. Final 16 tests
  passed. This is a test correction, not scientific tuning or efficacy evidence.
- Author Windows full discovery: 242 tests, 197 passed, 45 expected skips in the
  base environment. Torch-owned tests were actually run in the existing WSL venv,
  not counted as executed Windows learned-model tests.
- An author combined WSL command named nonexistent `scripts.test_c4_embedding`:
  25 loader cases, one import error, 24 actual tests passed. No installation or
  fabricated pass. Correct existing inversion/reconstruction/localization suites:
  28 tests, 27 passed, one explicit Windows-only path skip.
- Independent reviewer ran all 16 component tests successfully and confirmed the
  earlier fixture repair. Its additional 12 probes were synthetic CPU evidence.

No original negative/OOM evidence or pending exact localization authorization was
changed. C4/#18 remains open, PR #67 draft, C5 dependent. No quality gain or blind
detection is established; the existing localization question is not repeated.
