# C4 retained-triplet quality and key-drift diagnostic

Experiment `c4-saved-pair-quality-development-v1`, run `c4-saved-pair-dev-001`.
Exploratory follow-up to retained embedding run003; one source, three dependent
comparisons, not three independent observations. No population CI or success
rate is estimated. No study image is redistributed in this report.

## Exact authority and execution

Actual user replied “بله، همین بسته.” after the complete run/local/20-minute/
Torch4GiB/USD0/hash scope was restated in authenticated task
`01a0b9bd-fd47-7cf1-8123-ff77a4ca9dd8`. This actual decision was serialized, not
chosen by the agent. Official runner preview accepted the approval binding;
one official `--execute` invocation completed with exit0 and no runner errors.
Approval is consumed; no retry or further model execution is authorized.

- Executed clean commit: `6d03666ba6abee5d830d5e7229bc0e337881a1b5`.
- Canonical execution manifest: `de1a315271892c5e47609159dd94c2667f812610e23a142496b05ac0608fbc2b`.
- Approval reference: `f180bbf968f9e1d0c98333299725ff4a9ec43a20ca5a92cf6ee3484fa3875575`.
- Runner start/end: 2026-09-27T09:03:23.211295Z / 09:03:37.333754Z.
- Worker elapsed9.762197602 seconds; launcher child returned0.
- RTX5070Ti Laptop GPU; worker Linux CPython3.14.4, Torch2.12.1+cu130.
- Peak Torch allocated644345344 bytes, reserved700448768 bytes; peak worker
  RSS2296467456 bytes. Fixed Torch allocation ceiling4294967296 bytes.

Nine declared outcome cells completed, with durable intermediate values.
Source enrollment exactly replayed q=`5f0f`, h=`40a9a967` and enrolled Ws/Wi.
The existing raw source/control/candidate bytes and canonical pixel hashes were
checked by the approved worker. No new data, regeneration or download occurred.

## All native-grid quality comparisons

Source means the original source, NOT the reconstructed matched control.
Strict proposal diagnostics are PSNR>35, SSIM>0.9 and LPIPS<0.1.

| Comparison | RGB MSE | PSNR dB | RGB SSIM | LPIPS AlexNet v0.1 | Three targets |
| --- | ---: | ---: | ---: | ---: | --- |
| Control / source | 0.009128101388585818 | 20.39619544722751 | 0.6679027647010946 | 0.11984674632549286 | All fail |
| Candidate / source | 0.00912828839604695 | 20.396106474205563 | 0.6679135064238734 | 0.11986691504716873 | All fail |
| Candidate / control | 0.0000005474755801553187 | 62.61635247520382 | 0.9998763961467837 | 0.00001449994306312874 | All pass |

The per-image source-quality target conjunction is refuted for this retained
candidate. Excellent candidate/control similarity must not hide reconstruction
loss. The matched unmarked control also fails all source-quality targets and is
nearly identical in these metrics to the candidate. This locates a preservation
problem already present in this reconstruction path; it does not isolate VAE,
padding, noise/scheduler or optimizer causality, or establish population behavior.
No parameter change, new source, retry or favorable reference was selected.

## Key drift, not blind detection

Both control and candidate have q=`5f0f`, h=`40a9a96f`: q Hamming0 and h Hamming1
versus the replayed source. Both output-centered radius-one neighborhoods include
the source codes. Both retain source Ws but differ from source Wi. This is only
search-coverage evidence; original enrollment is side information in this
diagnostic. Blind detection remains NOT_RUN.

Control and candidate pHash minimum margins are zero, versus source
0.017229259905522376. Zero margin is a tie/stability warning, not evidence of
robustness. No calibrated owner attribution, watermark recovery, authenticity,
legal ownership, metric parity or full-workload GPU fit is established.

## Retained artifact provenance and review boundary

Ignored root: stable project `.thesis-build/c4-runs/C4-quality-development/c4-saved-pair-dev-001/`.
All three declared output hashes were independently recomputed by the author
and matched the runner record before this transcription:

- `outputs/saved-pair-quality.json`: `43489969ac356cfd82eae84c47494a4c3376e1b2e1b290c55d651ede121c60e7`.
- `logs/saved-pair-progress.jsonl`: `e3e7a89c5bebb2efaedfa12eabe6b9929181d8ea05bf299c3792b4d8f25685f8`.
- `logs/saved-pair-launcher.jsonl`: `61f4038a5cb2d190c1dfecce1517260b19c12f253d611a5ce3f141f8913124b8`.
- Runner `manifest.json`: `8657860ac094ad74ca4a29c3064ddb1bc9676cdbad3a6e0a1f78980e5e227741`.

This report is a direct unaggregated transcription of declared JSON outcomes.
The generic paired-seed statistics helper is not applied: there is one dependent
triplet and no preregistered seed-level aggregation or inferential comparison.
The exact spec, worker and raw outputs remain available for reproduction/audit.
Independent retained-result review is requested; no results gate or C4 closure
is claimed before that review. Even a complete negative-result audit cannot
establish the missing C4 quality success or blind detector deliverables.

Next bounded work: inspect the matched reconstruction implementation and design
a method-preserving localization package with fixed controls. Any new model run
needs a new exact user-approved manifest. Do not substitute an image-space mark,
hide source-reference loss, weaken targets or procure paid compute by inference.
