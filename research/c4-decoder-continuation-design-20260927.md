# Same-start decoder continuation: prospective exploratory package

Issue #18 / PR #67; author /root, 2026-09-27. Apply research-contract.md,
scope-guard.md and approval-policy.md. All other tasks remain paused by user.
This package is ordinary implementation until exact runner approval; no approval
has been requested or granted. Previous runs remain immutable and consumed.

The original64-update refinement stopped at its iteration budget while improving.
Late steps accepted.25 after rejecting1/.5, never testing smaller steps. This is
not an established decoder ceiling. Source25.57dB/.808/.075 still fails joint
targets and LPIPS worsened; no prediction that iterations will bridge8.775xMSE.

Both arms start saved000152; original encoded000000 remains the radius80 anchor.
The old API receives an explicit constraint_anchor while None retains historical
behavior. Control:step1 reset,two halvings,strict decrease,original rounded-radius
refusal. Adaptive:initial.25/min2^-16/max1,16backtracks,Armijo1e-4 on actual
projected displacement,warm start,cautious doubling. Engineering choices, not
literature-optimal values. Whole-policy contrast, not a one-factor ablation.

research/c4-continuation-inputs-20260927.json pins the failed parent runner/report/
journal plus two49232-byte F32[1,4,48,64]states. Load verified in-memory bytes, not
pickle/path reread. Initial decoder pixels must replay before continuation.
Same native source,fp32 frozen VAE,_decode checkpoint,scale.18215,clamp/crop MSE.
No fresh encode,UNet prediction,DDIM inverse,watermark or training. The reused
loader still loads its pinned full SD snapshot/conditioning; that does not
authorize use of unused UNet. Exact closure binds all imported dependencies.

## LONG revision after actual conditional user reply

The user approved only conditionally with a request to raise time toward an
optimum. The earlier20-minute f399 manifest is NOT authorized. Revise BOTH arms
symmetrically to the following prospective finite ceilings; obtain a new exact
decision after delta review. More time/steps cannot certify a global optimum.
Do not restart an early-stopped arm or bypass existing target/gradient/line-search
or radius stops. This is the same policy-bundle comparison, not unlimited tuning.

Each arm:512iterations/2049optimizer decoderNFE/512backwards, plus ONE final
image/gradient evaluation and backward. Actual final-state gradient is measured.
Each1500s INCLUDES final measurement/persistence; composition3060s. Fixed order,
3060>2*1500,no borrowed evaluation/time quota. Replay/persistence overhead also
consumes global time: refuse BEFORE either optimized arm if its entire1500s
allowance no longer fits. This is a retained package failure, not a shortened
arm or evidence against that optimizer. Report actual usage and early stops;
equal ceilings do not imply equal work. Every evaluated/rejected state is saved.
Normal state bound4106:2shared+2armstarts+4098evaluations+2optimizerfinals+
2finalmeasurements. Reserve4112 for bounded refusals;202,441,984bytes at49232each,
below256MiB. Journal32MiB with failure reserve. Exclusive fsynced persistence;
terminal-named row does not prove normal return or successful runner outcome.

Three saved native PNGs:retained_start,fixed_continuation,adaptive_continuation.
All receive safety,source PSNR/SSIM/LPIPS and diagnostic public q/h; all13 cells
and failures retained. One source,noCI,no blind detection or MSE-only acceptance.
Primary directional contrast is adaptive saved-PNG MSE minus fixed MSE; also
report progress at shared NFE and actual work,not winner-only endpoints.

Local existing WSL environment;no downloads/installs/cost. Torch9216MiB cap,
freeVRAM>=10240MiB,RAMavailable>=13GiB,disk>=4GiB. Recorded GPU total is below
12GiB,so12GiB with headroom is not runnable. Prior allocation~8.47GB fits9GiB,
new fit/time unproved. RAM12GiB/disk4GiB are estimates,not whole-system caps.
Linux3540s(+10sTERMkill),parent3590s,official3600s include loads and metrics.
Review complete package,clean commit,design helper and preview before exact
user question. OrdinaryCPU tests are not scientific compute or approval.

Gain supports optimizer-limited development,not promised35dB/fullmethod success.
Local plateau without active resource bounds may motivate explicit architecture
revision,not global decoder incapacity. Original targets/native2K/6900sources
remain. Inverse,DCT controllability,blindkeys/synchronization are separate gates.
