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

Each arm:128iterations/513optimizer decoderNFE/128backwards, plus ONE final
image/gradient evaluation and backward. Actual final-state gradient is measured.
Each430s INCLUDES final measurement/persistence; composition900s. Fixed order,
900>2*430,no borrowed evaluation/time quota. Report actual usage and early stops;
equal ceilings do not imply equal work. Every evaluated/rejected state is saved.
Normal state bound1034:2shared+2armstarts+1026evaluations+2optimizerfinals+
2finalmeasurements. Reserve1040 for bounded refusals;51,201,280bytes at49232each,
below64MiB. Journal8MiB with failure reserve. Exclusive fsynced persistence;
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
Linux1140s(+10sTERMkill),parent1190s,official1200s include loads and metrics.
Review complete package,clean commit,design helper and preview before exact
user question. OrdinaryCPU tests are not scientific compute or approval.

Gain supports optimizer-limited development,not promised35dB/fullmethod success.
Local plateau without active resource bounds may motivate explicit architecture
revision,not global decoder incapacity. Original targets/native2K/6900sources
remain. Inverse,DCT controllability,blindkeys/synchronization are separate gates.
