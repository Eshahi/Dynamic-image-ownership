# Independent C4 partial component review

2026-09-26. Author `/root`; actual independent reviewer `/root/b3_intake_review`, delegated under AGENTS.md and research/approval-policy.md. This is a **partial implementation checkpoint only**, not #18 closure, a human verdict, a scientific acceptance gate or execution permission.

## Exact artifact chain

- Base main: `19c704a10d9d88f5d249eea0a57f98d0df00c19b` (C3b PR #66 actually merged, #17 closed).
- Initial component/code/test record: `d8e4258`.
- First independently reviewed snapshot: `e7dc2330bf09d1de61e15f51685f47ccd4968125`.
- Diagnostic/early stream validation addition independently re-reviewed: `40cbeb3c112751e356c85d53d497c8fc7fb6bb21`.
- Final tolerance enforcement and clarified diagnostics independently re-reviewed: **`2e475a192f6540b79271bf7759b960e7a9e0a9cb`**.

Reviewed files: src/embedding/proposed.py, scripts/embed.py, tests/test_embedding.py, header-only reports/dev/embedding-manifest.csv, research/c4-embedding-component-20260926.md, immutable C4 task and A5 method/noise contracts. Draft PR #67 is attached to this chat; #18 remains open.

## Actual reviewer checks / disposition

Reviewer initially found **no narrow blocker**. It ran the initial 12-test WSL CPU suite (11 pass, one JSON Schema skip) and 12-test Windows controller suite (three pass, nine Torch skips); successful temporary synthetic full-schema CLI preview was checked on Windows. Independently calculated 16 DDIM steps across three additional schedules and two bias-corrected Adam updates, which matched. Reviewed native crop, DCT block order/centering, retained input graph, frozen parameters, exact unkeyed C0, detached/nonfinite failures and callback failure propagation.

It recorded two minor warnings: owned float32 projection norm `0.010000000218209463` for rho `0.01`, and absent total/noisy-latent displacement diagnostics. Repair 40cbeb3 records actual u and total keyed displacement, cumulative alpha and mathematically scaled displacement, explicit float tolerance, and checks stream arguments before encoding. Reviewer independently recomputed total displacement `0.3808967012629055`, u norm and zero-control diagnostics; values matched. A follow-up warning distinguished reported versus enforced tolerance and mathematical versus rounded-state subtraction. Repair 2e475a1 enforces the norm ceiling `rho*(1+1e-6)` and explicitly labels the alpha-scaled diagnostic rather than claiming a measured state difference.

Final reviewer message: **no blocker at 2e475a192f6540b79271bf7759b960e7a9e0a9cb**, 12 WSL tests pass / one expected skip, clean checkout and diff check pass, previous minor warnings resolved. Actual root checks on the final component chain: WSL 13 total / 12 pass / one expected skip; Windows combined embedding/instance/owner/runtime 38 total / 27 pass / 11 expected skips; unchanged legacy scripts 185 total / 174 pass / 11 expected skips. No pytest invocation is asserted; neither existing environment has it.

The first expanded WSL suite's `ModuleNotFoundError: jsonschema` is preserved in the implementation history and checkpoint documentation; the full C1 success-preview test now explicitly skips only in the environment without that package. No installation or dependency lock change occurred. The actual Windows preview passes full C1 schema validation on a temporary synthetic specimen; it does not validate real component custody or calibrations.

## Boundaries and delegated disposition

Actual reviewer performed only read-focused code/evidence checks and owned synthetic CPU arithmetic. No source study images, learned checkpoints, model/GPU inference, CUDA run, downloads, package installations, raw dataset changes, scientific runner execution or official lifecycle write occurred. The concrete scheduler is installed Diffusers 0.35.1, but tiny author-defined VAE/UNet modules are test doubles, not pretrained model evidence.

Author `/root` accepts this narrow software checkpoint under the project delegation after actual independent review; **does not accept C4 or any scientific claim**. Continuous target-template scores are not blind detector results. The manifest has zero execution rows and no fabricated image/path/hash pairs. The CLI's non-preview path fails with `execution_adapter_not_ready` rather than bypassing approval.

Remaining: verified pinned loader/empty conditioning/safety, source feature extraction, B5 saved-PNG output, true quality/verification integration and a reviewed exact scientific development package with new user approval. Real input-conditioned gradient/VRAM/native output-pair feasibility remains unmeasured. C4/C5 dependent integration must be coordinated honestly; a missing C5 result cannot be invented to close C4. C2's earlier one-run approval is consumed. The official d916749c controller read is paused at plan-acceptance/null choice, workflow SHA-256 `772a1a3b1a4ff674c878b0532485820f860e81490e026441a0bb384a3aebda51`; no state-bound gate decision is recorded by this partial checkpoint.
