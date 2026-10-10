# D2 native-measured refinement: development evidence

2026-10-10. Exploratory development only. D1 and D1N remain failed derivative screens; see [their retained results](ddim-feasibility-results.md). D2 treats autograd as an unverified proposal mechanism and accepts changes using actual native forward measurements. It supplies no accurate-gradient or generalization guarantee.

## Fixed utility screen

Protocol and code were committed at `941a401` before execution. The immutable run is `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/20261010-1206-native-utility`, completed in 32.297 seconds at USD 0. All eight declared official comparisons pass exact RNG, timestep and pre-checker RGB8 parity. These comparisons do not supply attack acceptance observations.

The utility source was fixed as 468505 before this screen because RC3 had lost an earlier exact-q identity there. All nine branches were evaluated on the baseline and every saved/reloaded proposal. The baseline maximum loss was 0.3529827595, on DDIM .2 seed 1; the native heuristic input gradient norm was 31.7818985. This is selection using development evidence, not an independent replication.

| Proposal length | Worst nine-branch loss | PSNR dB | SSIM | LPIPS | Changed pixels | Eligible |
|---|---:|---:|---:|---:|---:|---|
| .10 B | .3220713735 | 43.3638 | .974862 | .029353 | 823 | Yes |
| .50 B | .0796464905 | 43.2219 | .974106 | .030318 | 11,207 | Yes |
| 1.00 B | .0632745698 | 42.8109 | .972444 | .034491 | 29,694 | Yes |

Each proposal preserved exact operational q/h, clean `both_match`, strict quality, and both distortion balls in both continuous and saved RGB8 states. Each exceeded the fixed decrease margin of 0.0000352983. All three images are retained as discarded internal diagnostics; none is a selected candidate. Peak allocated CUDA memory was 5.679 GB. Human visual admissibility is unmeasured.

## Runtime qualification discrepancy

The run records `utility_pass=true` and `qualification=budget_infeasible`; neither field has been rewritten. Its 3848.912-second writer estimate includes a complete current-state nine-branch forward pass in every iteration, although the prospective algorithm explicitly caches that exact vector. Removing only those 240 duplicate passes gives 3170.192 seconds before checking any omitted qualification work. A [prospective execution decision](native-writer-execution-decision.md) subsequently includes proposal overheads, payload reads, baseline and final actual detector/VAE/negative qualifications: 3273.368 seconds plus 26.632 seconds reserve under the unchanged 3300-second cap. This correction permits the declared writer; it is not a new smoke or a relaxed scientific gate. Writer code was committed at `569f483` before the single twelve-source run, `20261010-1212-native-writer`.

No official matched T3 result, T4/T5 result, population false-positive calibration or publication claim follows from this utility screen.
