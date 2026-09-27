# Shared-source five-arm reconstruction component review

Author `/root`; actual independent reviewer `/root/b3_intake_review`.
Issue #18 / draft PR #67. Authority: AGENTS.md, approval-policy.md, research-contract.md,
scope-guard.md and the actual user reconstruction-path amendment.

Initial composition `2006c328937dc2dfb118f53cf7f17d6d83de13a4`;
checkpoint repair `0a0003b8704ad1de74a9638edf9b276bc8676129`;
final independently reviewed repair `ef614b60bb9d16baa3be22e419c1aae45cad886c`.
This is narrow ordinary component acceptance, not a lifecycle verdict, scientific
execution permission, learned-model parity, quality improvement or C4 completion.

## Exact composition and actual reviews

The component shares one source encode across VAE-only, unchanged zero-noise DDIM,
unchanged fixed-base-noise DDIM, fixed-point inverse/replay and explicitly modified
GNRI-inspired safeguarded coordinate inverse/replay with effective-transition L2
prior. Independent review of 2006c32 found no additional arithmetic or component
custody blocker; 28 owned path/comparison tests passed. The reviewer separately
intercepted solver inputs and verified effective beta and mean from each current
inverse boundary, not repeated use of the original terminal source.

The author then found a concrete integration blocker: the real checked loader can
return exact `CheckpointedComponents`, but the first path accepted only exact base
`DiffusersComponents`, and direct UNet prediction would bypass checkpointing.
Repair 0a0003b explicitly whitelists those two concrete profiles, delegates to bound
`_predict`, and separately journals root-UNet forward starts including checkpoint
backward recomputation. The temporary hook has a twice-NFE start ceiling and always
cleans up; mathematical NFE and backward counts remain separate. The original
checkpoint helper and loader were not modified.

Actual independent review blocked 0a0003b: `__func__` alone did not bind the method
owner. Assigning another backend's same-class bound method passed validation;
the owned reproduction completed seven evaluations while the bound model received
zero calls and the other model received seven, defeating custody and accounting.
Repair ef614b6 checks `__self__ is backend` at construction and every guard.
Regressions cover both exact base and checkpointed profiles before either model
call. The actual reviewer replayed the original bypasses, confirmed rejection and
hook cleanup, ran all 41 relevant owned CPU tests, and found no remaining narrow
checkpoint-integration blocker at that exact repair. Reviewer made no source edits.

## Tests and preserved failed checks

- Author initial composition: 44 owned CPU pair/path/comparison tests passed;
  combined reconstruction/localization suite 56 cases, 55 passed, one expected
  Windows-only path skip. Windows scripts discovery 270 cases: 197 passed,
  73 dependency/platform skips.
- First checkpoint repair test run: 44 cases, two actual assertion failures from
  stale fixtures expecting `evaluation_started` rather than the newly journaled
  `unet_forward_started`. Corrected only the expected phase; model drift still
  refuses after one started call, without false completion.
- Newly added full checkpointed comparison regression initially used nonexistent
  metadata key `evaluations`: 56 cases, 55 passed and one KeyError. Corrected to
  declared `scheduler_evaluations`; no numerical policy or output changed.
- Author final pinned WSL suite: 69 cases, 68 passed, one explicit Windows-only
  path skip. Modules: scripts.test_c4_reconstruction_comparison,
  scripts.test_c4_inversion_path, scripts.test_c4_inversion,
  tests.test_c4_checkpointing, scripts.test_c4_reconstruction,
  scripts.test_c4_localization_package. Owned CPU modules and installed scheduler
  only, not pretrained assets or study images.
- Final verified Windows base scripts discovery: 276 cases, 197 passed,
  79 expected dependency/platform skips. Torch-specific assertions were executed
  in the existing pinned WSL environment, not described as Windows model parity.
- Reviewer first repair command mistakenly named nonexistent
  scripts.test_c4_checkpointing: 33 passed plus one actual import error. Corrected
  command with tests.test_c4_checkpointing passed all 40 then-current cases.
  Final owner-repair review passed 41 cases. None of these failures was hidden or
  rewritten as a skip; no package installation was inferred.

## Boundaries and next coherent package

Normal nonconvergence retains failed arm metadata/intermediate states and does not
decode a fallback image. Model/profile/journal/persistence exceptions stop the
composition; earlier callbacks remain and later arms are missing. Native callback
images and metadata are copied, VAE/model identities and mutation versions guarded,
and persistence precedes saved-arm records. Counts are forward starts, not completed
operations, FLOPs, peak memory or learned-model numerical parity. Private Torch
version counters are accidental-drift guards, not content hashes or a hostile-code
sandbox. External timeout/allocation checks and durable worker journals remain
mandatory; no Torch/GPU cap or additional execution permission is introduced.

No model loads, study pixels, GPU kernels, new data/downloads/installs or scientific
worker were used. Parameters in owned fixtures are not experiment selections.
PNG quantization, actual safety, source PSNR/SSIM/LPIPS and q/h evaluation are not
performed by this library. The effective skipped-transition prior, L2 norm and
solver safeguards differ from GNRI; no faithful reproduction or paper-performance
transfer is claimed. No carrier/watermark optimization or blind detection occurs.

Next coherent deliverable is the versioned real-asset comparison config/worker,
durable PNG/latent/outcome inventory, unchanged control pixel replay, native quality
and safety bindings, then full exact-manifest/design-helper/runner and independent
package review before one actual compute decision. The earlier localization
question remains pending at clean commit 36b4fa85942d744b7c1749947b675da784215d3a,
manifest 065979dd13b7a6665c149d96baf8c9eceb7c06882321b99b15cf6445412337da;
current author HEAD cannot execute it. No duplicate question or consumed approval
reuse. Preserve all prior quality failures/OOM records and unchanged thesis targets.
C4/#18 stays open, PR #67 draft, C5 dependent. Actual read-only controller evidence
remains d916749c paused at plan-acceptance, null choice, workflow SHA
772a1a3b1a4ff674c878b0532485820f860e81490e026441a0bb384a3aebda51;
no transition or invented human verdict. Initial native writer inventory was empty.
