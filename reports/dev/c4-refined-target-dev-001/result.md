# C4 refined-target reconstruction: retained partial failure

Issue #18 / draft PR #67. Exploratory one-source, six dependent arms, seed0.
No watermark, blind detector, population/native2K acceptance or method success.

## Actual execution and authority

The authenticated user replied `تایید میکنم. لطفا اجرا کن سرعتمون خیلی پایینه.`
to the sole pending exact six-arm package question. The actual reply was serialized
outside the checkout; its timestamp records receipt/serialization rather than an
invented transport timestamp. Official approval validation returned true.

- Run `c4-refined-target-dev-001`, experiment
  `c4-refined-target-reconstruction-development-v1`, target local, USD0.
- Exact clean executed commit `dd347afb861774f7a86138e7170dba96d4f47044`.
- Canonical execution manifest SHA-256
  `78bcae98866135714d0f7847a8de7d076f1adea29c20509d8766079d95088683`.
- Actual approval canonical reference
  `ca2d4f7642e3d2895a1865603896d6579f8653c65b54f073a4ca378218680db9`,
  issued12:39:44Z/expires13:39:44Z on2026-09-27. Approval now **CONSUMED**.
- One official dispatch started12:40:18.298769Z, ended12:43:33.001767Z.
  Official status failed/exit1. Worker elapsed189.895960392 seconds.
- Stable artifacts remain outside Git at
  `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/c4-runs/C4-refined-target-development/c4-refined-target-dev-001/`.
  No downloaded data/models/software, new source, held-out image, paid service
  or security change. Source109798, native500x333, unchanged restricted local
  research rights. Existing pinned WSL scientific environment used.

## Complete arm inventory, not a selected successful run

Unchanged strict targets: PSNR>35dB, SSIM>0.9, LPIPS<0.1.

| Arm | Source RGB MSE | PSNR dB | SSIM | AlexNet LPIPS v0.1 | Outcome |
| --- | ---: | ---: | ---: | ---: | --- |
| VAE-only | 0.0056457428439589145 | 22.48278907271824 | 0.7429099151683972 | 0.058493178337812424 | PSNR/SSIM fail; LPIPS passes |
| Zero-noise DDIM | 0.00719192869147502 | 21.431546273166017 | 0.6935376799565754 | 0.1362507939338684 | All fail |
| Historical fixed-base DDIM | 0.009128101388585818 | 20.39619544722751 | 0.6679027647010946 | 0.11984674632549286 | All fail; exact old control pixels |
| Direct decoder refinement | 0.0027749505753350426 | 25.56744747694608 | 0.8079225830219287 | 0.07541167736053467 | PSNR/SSIM fail; LPIPS passes |
| Original-target inverse/replay | Missing | Missing | Missing | Missing | Pair not converged; no fallback image |
| Refined-target inverse/replay | Missing | Missing | Missing | Missing | Pair not converged; no fallback image |

Direct refinement stopped at its declared 64-iteration budget:150 decoder
evaluations,64 backwards,214 actual decoder forward starts including64 checkpoint
recomputations. Continuous source MSE0.0027736618649214506 differs from quantized
saved-PNG MSE above. Final latent displacement L2=14.437770824773114; no strict-radius
refusal. The continuous0.0003 diagnostic tolerance was not reached.

Both inverse arms report39 actual UNet forwards, zero backward/recomputation,
`pair_not_converged`, and null whole-path roundtrip residual. Failed pair states
are retained. Whole replay quality is **unobserved**, not zero or assumed equal
to direct refinement. Both targets were attempted under the same declared solver.

Four rendered images passed the pinned safety checker (flags false), which is
not a rights or general safety certificate. Exact historical control pixel replay
was true. Source enrollment replay passed. q/h Hamming diagnostics are VAE1/0,
zero-noise1/0, fixed-base0/1, direct-refinement1/0. These source-relative radius1
observations are not suspect-only blind detection or recovered-owner authority.

## Failure semantics and durable evidence

After recording metrics for all four rendered arms, the worker deliberately
raised `ValueError: retained nonconverged inverse arms; package incomplete`.
Its phase was `lpips_completed`, status `failed_retained_partial`. Of25 fixed
cells,17 completed,2 render cells failed,6 dependent metric/safety/code cells
remained pending. Missing cells are never zero or successful observations.

The official runner additionally recorded
`ContractError: Declared artifact missing: outputs/fixed_point_encoded_inverse.png`.
Its `output_artifacts` is empty because the declared inventory was incomplete;
this does NOT mean no partial files exist. Do not edit the historical runner
record or manufacture missing PNGs. Both expected inverse PNGs are absent.

Author metadata-only custody check:1230 worker journal rows,159 exclusive state
files totaling7,827,888 bytes; every state size/digest matched its recorded row.
Four PNG byte digests matched the worker. No metrics or study decoding rerun.

| Retained file | Measured SHA-256 |
| --- | --- |
| manifest.json (raw runner record) | 2d3cde49d1c0857e0464002e6a863771f7d556859c57d7724fb8d5aa4e9baa21 |
| outputs/refinement.json | c63202c36206ee251338417f62d1006cf37f1f32e46fedffaeea50fff57fc794 |
| outputs/vae_only.png | 7dd86185dd695193f81ad250f346edf72be6ecaada155fb3afa07a259b11be67 |
| outputs/ddim_zero_noise.png | 0e929c1cb3a442284ddd9ff8e26708e463c2fef6b089073135ba6db70b1842ab |
| outputs/ddim_fixed_base_noise.png | 53aceddd708642bb26c9fbd5393670282d7feb813cfab0aece824305a0b71d2c |
| outputs/decoder_refinement.png | d8c929ee70e09617ac6639e64ab1a077ff6e028f6b5808cb978bd39f6bc56242 |
| logs/refinement-progress.jsonl | 11fba38f0263db064fef5e9be6d711307496717fc83a695bdeaf44ee9193a8aa |
| logs/refinement-launcher.jsonl | 5c15d0bf8993890e78076203438c61d92f80d0ce86a4d86551860a7b8c544de3 |

## Interpretation and resources

In this source, direct refinement reduced saved-PNG source MSE by50.8488%
relative to VAE-only and increased PSNR by3.08466dB. SSIM improved, while LPIPS
**worsened** from0.05849 to0.07541, though it remains below0.1. Hence no universal
quality improvement. Saved-PNG MSE still needs more than8.775-fold reduction to
exceed35dB; no proof that this is attainable or impossible through this decoder.

The first hypothesis has narrow one-source support for direct source-MSE reduction;
retaining that improvement through inverse/replay was not demonstrated. The
fixed-point route failed under this specific budget/policy; it does not establish
universal inversion impossibility. A stronger GPU alone does not fix numerical
nonconvergence or prove quality. Next safe work is a bounded read-focused numerical
failure diagnosis and a versioned source-preserving reconstruction/inversion route,
not repeating this consumed run or guessing a larger budget.

Peak Torch allocation8,466,363,904 bytes; reservation9,632,219,136 bytes; worker
RSS8,313,290,752 bytes. No OOM or timeout. The9GiB allocator cap is not totalVRAM.
These observations support only this diagnostic's fit, not fullmethod/native2K
or6900-source fit. No paid GPU need established. C4 stays open and C5 dependent;
Spec Kit plan-acceptance remains paused/no verdict. Targets and all prior
negative/OOM results remain unchanged.

The generic seed-aware helper receives the single failed package in metrics.json
with null package-level MSE; it must not promote the four correlated partial arms
to independent completed runs. Arm-wise values above remain separate exploratory
descriptions, no CI, significance test, population mean or superiority claim.
Official helper analysis at the external package directory's
`analysis-retained-failure-v1` reports expected1/observed1/failed1/missing0, n0,
all descriptive estimates null and no comparison/CI. Its CSV retains the empty
estimates and deterministic SVG contains no seed points; axis0/1 placeholders
are not measured values. The existing torchvision deprecation warnings remain
in process.log, not hidden as successful scientific evidence.

Actual independent reviewer `/root/b3_intake_review` found no narrow retained-
evidence/transcription blocker at report commit
`677961fce4fd242eec59a027b3658f4604f65709`; see
`audits/c4-refined-target-results-review-20260927/review.md`. All159 state hashes,
1230 journal rows/25 transitions, four PNG raw hashes, source/custody/environment,
approval/binding and helper analysis provenance were independently checked.
This does not reproduce learned metrics or grant scientific acceptance/C4 closure.
