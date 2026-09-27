# C4 saved-pair quality component review

Scope: quality/key-drift library and exploratory design only, issue #18 / PR
#67. Not an executable scientific package, C4 closure, metric numerical parity,
blind detection, rights certification or lifecycle transition.

## Actual independent review and repair history

Author `/root`; independent reader `/root/b3_intake_review`, requested under
AGENTS and research/approval-policy.md. Initial exact commit
`c2188b114200cf3236a34a8f7dd3248e1c9a4082` contained one blocking profile
finding: root `eval` plus parameter flags did not prevent version/baseline/
spatial/child-Dropout mutations. Reviewer reproduced a changed finite return
with fake CPU tensors/modules, without any actual model, Torch GPU or images.
Initial acceptance was withheld. Reviewer independently passed all ten owned
synthetic tests; constant-image SSIM agreed with its analytic reference within
2.22e-16. Reference pairs, PSNR formula and AlexNet slices were consistent.

Repairs `972ef66` and `c043f87` bind a frozen loader receipt to full configuration,
all submodule eval flags/identities and a digest of all parameter/buffer tensors
requiring CUDA fp32/no gradients. Negative tests cover version, learned/baseline,
spatial, bool-as-layer-count, child-training, substitution and buffer/value/
dtype/device/gradient mutation. Reviewer warning about executing mutable cached
LPIPS modules was addressed by requiring a fresh import and matching actual
imported module paths/hashes to the checked distribution, plus class origin.
This does not claim protection from arbitrary hostile in-process Python.

Re-review exact `c043f87121a9874b7d8d951147c5aed29e5cf61a` completed by
`/root/b3_intake_review`: no remaining narrow component blocker. The actor
independently repeated forward-boundary fake probes: version0.0, lpipsFalse,
spatialTrue, L=True, child training and child replacement all rejected before
any tensor/model call. All twelve owned synthetic tests independently passed,
including buffer mutation/dtype/device/grad failures. Cached/shadow-import
warning conservatively resolved for the future fresh worker. Runtime neural
numeric parity remains unmeasured; this verdict does not accept a runnable
exact package, scientific result, C4 task, compute or official lifecycle gate.

## Author verification (no pretrained model or study-image computation)

- Existing clean WSL science venv: 12 owned synthetic CPU tests passed at
  `c043f87`; all classical fixtures are synthetic generated arrays.
- Windows base venv initially could not import the owned test because NumPy
  is absent; optional dependency handling repaired before initial review.
  Windows full scripts discovery at `c2188b1`: 203 tests, 182 passed, 21
  expected skips, including ten owned NumPy-dependent tests. A skip is not
  cross-platform numerical parity.
- Final Windows base full scripts discovery after repairs: 205 tests, 182
  passed and 23 expected skips. The twelve owned tests are covered by WSL,
  not by the Windows dependency skips.
- Full WSL scripts discovery at `c2188b1`: 181 tests attempted, two import
  errors and one skip, because unrelated `test_validate_method_config` and
  `test_pixel_dct_control` need jsonschema, absent from this pinned science
  environment. Failure retained; no environment change/install was made and
  the full WSL suite is NOT reported as passing. The owned 12 tests do pass.
- No study metrics, CLIP/AlexNet/LPIPS load, diffusion, dataset read/download,
  execution approval, paid compute or official state transition performed.

Remaining: dedicated retained-byte/environment/recipe binding, execution
entrypoint/launcher, exact clean-commit manifest and runner preview; independent
full-package review and actual exact user approval before real computations.
