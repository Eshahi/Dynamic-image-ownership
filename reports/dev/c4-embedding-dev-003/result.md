# C4 run003: bounded checkpoint/residency pilot completed locally

The actual latest user message `تایید میکنم` approved the separately presented
fixed9GiB package, not the earlier conditional12GB request alone. Official runner
approval validation passed and executed exactly once. Authorization is consumed;
no retry, expanded sample, new download, paid provider or scientific task is authorized.

- Experiment: `c4-embedding-checkpoint-development-v1`; run: `c4-embedding-dev-003`.
- Executed clean commit: `0ac89f587554c27b4fd6b143f270a65770c6d11f`.
- Canonical manifest: `6681e972a7fb249e66d6cb31f0e0b09f4bc6e6e6890e45ce4df0cc4816d3156e`.
- Target local,1200seconds/USD0/Torch9216MiB; unchanged method/config/source/seed.
- Official runner start2026-09-26T22:17:37.751321Z/end22:18:48.372754Z;
  exit0/completed. Worker elapsed65.392459240seconds; launch/validation included
  in runner wall time70.621433seconds.

## Observed scope

One original development source COCO109798/native500x333/padded512x384, seed0.
All48 transitive pins and clean executed commit were validated. Offline WSL
CPython3.14.4/CUDA13.0/fp32 path; the Windows runner's own Python3.12.14/platform
metadata is not the scientific child environment. No additional images/models.

Explicit idle-component residency and nonreentrant per-UNet/VAE-decoder
checkpointing completed the matched control, both backward/gradient checks,
both optimizer/projection steps, final render/objective and saved-pixel safety.
Recorded gradients, in iteration order: **0.004541896027909649** and
**0.004539294158349571**. Both nonzero/finite. Post-projection norms
0.010000000379108165 and0.010000000292520012 satisfy rho0.01+absolute1e-8 tolerance.
Final norm0.010000000292520012; final continuous enrolled scores
semantic-0.01087809599390532 and instance-0.0067633890823166724.
These are not calibrated blind detections or proof of successful watermark recovery.

Matched-control and marked-candidate native PNGs were retained with recorded
saved-pixel safety flags false. A model flag is not legal/content certification.
No public image redistribution is authorized by source rights; raw pixels/models
remain ignored locally. PNG byte SHA256:

- Control: `53aceddd708642bb26c9fbd5393670282d7feb813cfab0aece824305a0b71d2c`.
- Candidate: `3d561c3b431943096a06e65abffb46eea2b0cd97b52e55893c38b12f6ed27289`.

Measured Torch peak allocated8,452,371,968bytes (about7.87GiB), reserved
9,590,276,096bytes (about8.93GiB), allocation ceiling9,663,676,416bytes (9GiB).
Peak worker RSS8,386,772,992bytes. These are not whole-GPU/OS memory caps or
minimum required capacity. Current allocation before/after idle parking
5,541,973,504/3,833,067,520bytes; reserved unchanged5,639,241,728bytes there.
The profile fits **this one source**, not every image, size or full workload.
Because cap and checkpoint profile changed together, no causal checkpoint-only
memory benefit or numerical equivalence claim is supported. Real checkpoint
replay numerical parity remains NOT_PROVEN despite successful backward.

## Exact evidence and reproducible descriptive analysis

Stable ignored run root:
`.thesis-build/c4-runs/C4-development/c4-embedding-dev-003/`.
Runner recordSHA `e3b54a21cc594a6eacd445b2f6772ebf97ed0e579275cee20339e6c324c40539`.
Declared output/report/progress/launcherSHA:
`3e34800b623607086c06c58a077e7e87952e30645913107013b62eb6955be75d`,
`ed1089c569dc96c37247a0e2a01e999e3927eccd35051173f662dc95a73290fd`,
`6c605d9f52ce573e86374794a348ba91e9170946e15a775241625880b7642048`.
TrajectorySHA `7b024cb2ce6bb5f8a11d5a39625d6882fc22842d0c7db30fa5ec80f5bb0507a7`.
Approval rawSHA `1b528a942e979b4caf77676a6231d3ecfeb21612e222ab9d65a0d92fe2358a8e`;
runner canonical approval reference
`0c24d22baade65538634934e5d32341c4072c95a958655fe58fc672390187cba`.

Metadata-only analyzer `scripts/summarize_c4_checkpoint_run.py` verifies exact
record/trajectory hashes, all48 executed Git blobs, three declared outputs,
source snapshot, all15 retained SD snapshot files, PNG byte identities,
ordered expected completed operations/gradient/projection/final/safety evidence.
This is a verifier of this immutable retained outcome, not a generic run validator.
Initial metadata analysis attempt used the wrong model snapshot subdirectory,
failed before output creation, and was repaired; no scientific rerun occurred.
v1 is preserved. Hardened v2 analysisSHA
`c35e91ef7567dab0ee702131c87cfdf7e7153e5913d93c85a0243ce2488eaf71`,
at ignored `.thesis-build/c4-analysis-20260926/retained-checkpoint-run003-v2/`.
Analyzer commit `bf9f1f1304865a585b466337c5feaa0b428543db`;
scriptSHA `bb1425bcdaa9ab62c688a59b6a43d91320b3ec722376909be4f63d1c11e62817`.
Seven model-free ledger tests passed; subsequent test relocation makes them
discoverable alongside existing scripts:193tests,182pass/11expectedskips.

Specification was read before outcomes. The independent unit is **one trial**;
the two gradients and matched outputs are dependent observations, not extra seeds.
No within-seed scalar gradient aggregation was preregistered, so no arbitrary
first/last/mean selection is fed to the scalar statistics helper. Both ordered
observations are retained descriptively; no CI, significance, superiority or
population-power claim. Prior001/002 OOMs remain immutable and are not excluded.

## Remaining work, not acceptance

Actual independent actor `/root/b3_intake_review` found no blocker for this bounded
retained engineering evidence; see audits/c4-checkpoint-results-review-20260926/review.md
and externalreceiptSHA61a3f3ab2d04bb0b84031421021f4d8a1acdda274d0cee0b2d4d924c29e75a11.
This supports bounded engineering completion only. C4/#18 and PR67 remain open/draft.
PSNR/SSIM/LPIPS, saved q/h drift,
blind recovery/calibration, real SD numerical parity, determinism/identity
coverage, fuller development coverage and method quality remain unfinished.
No runnable-system or final thesis acceptance, ownership authority or6900-image
claim follows. No RunPod rental was needed for this approved pilot; a larger
workload's resource need remains unmeasured. Official lifecycle stays paused at
plan-acceptance; this compute reply is not a lifecycle gate verdict.
