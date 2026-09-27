# Frozen-decoder latent refinement: bounded independent component review

Issue #18 / draft PR #67. Author /root; actual independent reviewer
/root/b3_intake_review. Authority: research/approval-policy.md, delegated technical
review only. No human verdict, lifecycle transition, scientific execution or C4
acceptance is recorded here.

## Exact reviewed artifacts

- Initial implementation: 31d807755ab5dc4677d7662a3d9ff638659b79c9.
- Final repair: 39a8c38492d498571e80c13263f1f1564fc794c3.
- src/embedding/latent_refinement.py, scripts/test_c4_latent_refinement.py and
  research/c4-frozen-decoder-refinement-design-20260927.md.

The reviewer read exact code/design and ran only owned synthetic CPU fixtures in
the already installed pinned WSL environment. No pretrained assets, study pixels,
GPU, downloads, installs or scientific worker were used.

## Actual failures preserved and resolved

1. Author's initial expanded suite: 85 tests, 83 passed, one actual detached-decoder
   failure, one expected Windows-only skip. A zero-weight latent penalty created
   an autograd edge even when decoder output was detached. Repaired before initial
   commit by separately requiring gradient_image.requires_grad; no objective or
   parameter changes. Final initial suite: 85 tests, 84 passed, one expected skip.
2. Reviewer reproduced rounded fp32 trust-ball violation at 31d8077: nonzero initial
   latent and radius 1e-4 yielded accepted displacement 0.000100184167098642;
   radius 1e-5 yielded 1.0103119157251248e-5. A mathematical projection was not an
   actual tensor bound. Final repair measures actual displacement in float64,
   persists an unevaluated refusal and aborts before trial decoding if beyond the
   exact radius. No unreported tolerance or adaptive rescue is introduced.
3. Reviewer reproduced slow final persistence returning a terminal diagnostic
   after the cooperative deadline. Final repair rechecks time after final save,
   retaining partial evidence and refusing terminal completion on overrun.
4. First strict-radius repair run: 18 tests, 17 passed, one actual error in the old
   .01-radius test. Its previous .01000001 assertion hid rounded overshoot. The
   test now explicitly expects refusal and checks evaluated states respect the
   hard radius; no implementation relaxation to make the old test pass.

Reviewer independently re-ran both original blocker probes at final39a8c38: retained
refusal/partial states, no trial decode/false terminal and hooks removed. All 18
owned CPU component tests passed. Reviewer independently derived the nearest-
decoder native-crop MSE gradient from pixel multiplicities; first normalized step
matched within maximum absolute difference 1.49e-8 (rtol1e-6/atol1e-7).

## Final checks and narrow conclusion

Author final WSL combined component suite: 87 tests, 86 passed and one expected
Windows-only skip. Verified Windows base scripts discovery: 294 tests, 197 passed,
97 expected missing-dependency/platform skips; no install to remove them.
git diff --check passed; no active native wsl/python/curl process observed after
tests. These checks are not a full learned-model runtime validation.

Actual reviewer found no remaining narrow component blocker at exact39a8c38.
Required explicit policy, exact frozen decoder owner/profile checks, checkpoint-
preserving delegation, saved rejected/failed states, native crop/scale, separate
forward/backward accounting and NOT_RUN quality/safety claims were inspected.
Hard-radius rounding refusals may impede real feasibility and remain explicit.
No learned-model parity, quality gain, full resource fit, scientific compute
permission, C4 closure or general efficacy is established. A complete reviewed
worker/config/input closure/helper/clean manifest and actual runner-bound user
decision are still required before any new learned-model execution.
