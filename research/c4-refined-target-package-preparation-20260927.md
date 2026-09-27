# C4 refined-target reconstruction package preparation

Date: 2026-09-27. Author: `/root`. Scientific status: **NOT_RUN**.

## Exact prospective execution

- Experiment: `c4-refined-target-reconstruction-development-v1`.
- Run: `c4-refined-target-dev-001`; target: `local`; seed: 0.
- Clean execution commit: `dd347afb861774f7a86138e7170dba96d4f47044`.
- Isolated checkout: `C:/Users/Soroush/.codex/worktrees/c4-localization-exec/THESIS_GUIDE_OFFLINE_v5`.
- External manifest: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/c4-refinement-package-20260927/v2-isolated-manifest.json`.
- Canonical manifest SHA-256: `78bcae98866135714d0f7847a8de7d076f1adea29c20509d8766079d95088683`.

The audit/document checkpoint does not replace that separate clean execution
binding. All 46 required worktree/Git input pins were independently checked.
The v1, isolated v2, in-memory builder and official design-helper manifests agree
canonically. The official runner's dry dispatch returned `dry_run=true`,
`target=local`, the exact digest above and `requires_approval=true`. No approval
artifact or scientific execution was created.

## One coherent diagnostic batch

Only the retained COCO development source 109798, native 500x333 with existing
512x384 padding, and existing checked local SD1.5/CLIP/LPIPS assets are used.
Six fixed arms share the source encode: VAE-only, unchanged zero-noise DDIM,
unchanged base-noise DDIM, frozen-decoder source-latent refinement, fixed-point
inverse/replay of the original encoded target, and fixed-point inverse/replay of
the refined target. No watermark, optimizer from the historical embedding method,
new image, held-out image, training, download or remote service is introduced.

The versioned refinement policy has 64 updates, normalized step 1, maximum two
backtracks, radius 80, no latent prior and continuous MSE tolerance 0.0003.
The two inverse arms have the same fixed-point policy and separate 128-NFE
budgets. These are preregistered exploratory engineering choices, not reproduced
literature settings or a promise of quality. Original configuration and negative
results remain unchanged. A refused radius, exhausted budget, nonconverged
inverse, OOM, timeout or quality failure is retained without decoder fallback.

The worker measures native saved-PNG source PSNR/SSIM/LPIPS and source-relative
q/h diagnostics, preserves all evaluated/rejected states as bounded safetensors,
and checks exact old-control replay. Its 25-cell inventory retains missing and
failed entries. Completion requires normal composition return, complete cells
and a consistent final report, not a terminal journal row alone.

## Resources and limits

Outer duration: 1200 seconds; Linux timeout: 1140 seconds plus ten-second kill
escalation; parent allowance: 1190 seconds. Cost: USD 0. Torch allocation ceiling:
9216 MiB (9 GiB), **not total GPU memory**. RAM 12288 MiB and disk 4096 MiB are
estimates, not an enforced process RAM cap. Before model use, require measured
free GPU memory at least 10240 MiB, available RAM at least 13 GiB and disk at
least 4 GiB. No automatic retry or cap increase. Actual fit remains unknown.
The fixed launcher uses the existing pinned WSL science environment and offline
flags. No paid RunPod/API operation is included.

## Ordinary checks and independent review

Composition commit `43331bca48396c0117a67cb1ce84e16432e346fa` was reviewed by
actual independent actor `/root/b3_intake_review`; see
`audits/c4-refined-target-comparison-review-20260927/review.md`. A slow terminal
callback warning is addressed by the worker's normal-return/final-report rule.
Initial author test incorrectly expected a replay-budget refusal at the policy
constructor; corrected to test path preflight, preserving the failed test history.
Final 17 composition tests passed.

The complete package at the exact execution commit and its final isolated binding
were independently reviewed by the same reviewer, distinct from the author; see
`audits/c4-refined-target-package-review-20260927/review.md`. No narrow launch-design
or binding blocker remained. This is not scientific acceptance or compute consent.

Final author checks: related WSL suite 91 tests, 90 passed/one expected Windows
launcher skip; Windows scripts suite 317 tests, 202 passed/115 expected dependency
or platform skips; related Windows runtime/bridge/package suite 28 tests,
26 passed/two skips; `git diff --check` passed. Independent package/composition
WSL suite: 23 tests, 22 passed/one skip; independent Windows package suite:
six tests, five passed/one missing storage-dependency skip. Tiny owned CPU
fixtures only: no learned models, study pixel decoding, metrics or GPU executed.
Official design helper validated the spec and generated the five preparation
artifacts; official runner dry dispatch only was performed.

## Scientific boundary

Continuous decoder MSE does not guarantee quantized PNG quality. One image's six
dependent arms cannot establish population success, native2K coverage, the
6900-source obligations, watermark controllability, suspect-only key recovery,
blind detection, rights clearance or C4 acceptance. Targets PSNR >35 dB,
SSIM >0.9 and LPIPS <0.1 remain unchanged. All prior scientific approvals are
consumed. A new actual user decision on this exact manifest/target/resources must
be validated by the official runner before any worker starts. C4/#18 stays open,
C5/#19 dependent, and Spec Kit d916749c remains paused at plan-acceptance with
no fabricated verdict. This package is being presented for that one decision.
