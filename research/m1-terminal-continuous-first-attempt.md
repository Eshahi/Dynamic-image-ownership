# A-C first attempt: partial positive evidence, execution failure

2026-10-04. Source MAIN `.thesis-build/dev-runs/20261004-0940-terminal-continuous`, source commit7be2a6c; duration455.156 seconds. The second source ran out of CUDA memory during its first cycle-gradient backward. This is not a completed scientific pilot or a failed scientific gate.

All four source1675 conditions completed. Source4795 retains its initial checkpoint and four explicitly missing conditions. The CPU analysis at commit69e7b95, MAIN `20261004-0950-terminal-continuous-analysis`, independently rechecked the first source's PNG/array/score/cap receipts; its only errors are the second source's failed event, missing final checkpoint and retained source OOM. The directory label0950 is approximate; the analysis ran at09:48 UTC. Promotion is null, with4/8 observed conditions,16/32 observed owner queries and14/28 observed negatives. No missing query is counted as negative.

|1675 output|Blind semantic score|Blind instance score|State|
|---|---:|---:|---|
|C0 clean|.654909|-.302347|neither_supported|
|C0 VAE cycle|.457442|-.199504|neither_supported|
|C1 clean|5.897694|7.365052|both_match|
|C1 VAE cycle|5.724235|6.343547|both_match|

Threshold4 is inclusive and unchanged. All14 completed negative queries remain below both thresholds. C1 clean source quality is PSNR36.381449, SSIM.980189, LPIPS.010324; its clean quality conjunction passes. These are one source's exploratory measurements, not the two-source promotion or evidence of diffusion survival. VAE output quality against the source fails independently (PSNR26.364697), and is not substituted for clean embedding quality.

The error reports9.67 GiB allocated and332.85 MiB reserved but unallocated under the10 GiB allocation cap. A reader leak or allocator fragmentation has not been established. Execution recovery is diagnosed separately in `m1-terminal-continuous-recovery.md`; no margins, loss, steps, endpoint rule, source order or quality/reader thresholds may change. The original failed run and every checkpoint remain untouched. A fresh two-source rerun will preserve both planned sources and check the completed first-source replay, rather than select only the promising image or convert this partial attempt into a passed pilot.
