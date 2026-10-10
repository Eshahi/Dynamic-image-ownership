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

## Twelve-source outcome: prerequisite failure

The single writer at `569f483` completed all twelve sources in 947.765 seconds, inside the fixed 3300-second cap. No retry or source replacement occurred. Independent CPU analysis of the retained full detector calls reproduces clean exact operational q/h and both_match 12/12, strict quality 12/12, and final saved-pixel feasibility 12/12. SD1.5 VAE joint exact-q/read/semantic recovery is 12/12; SDXL is **10/12**, below the fixed >=11/12 requirement. **D2 is ineligible and no official T3 grid was run.**

| Source | Accepted updates | Initial worst loss | Final worst loss | SDXL intended-q bit errors | SDXL joint |
|---|---:|---:|---:|---:|---|
| 1675 | 1 | 0.003660 | 0.002353 | 0 | True |
| 4795 | 9 | 0.113090 | 0.001011 | 0 | True |
| 6012 | 11 | 3.154572 | 0.223488 | 1 | False |
| 25394 | 0 | 0.000000 | 0.000000 | 0 | True |
| 80932 | 4 | 0.102002 | 0.001213 | 0 | True |
| 109798 | 8 | 0.111095 | 0.000000 | 0 | True |
| 134882 | 6 | 0.517947 | 0.177348 | 1 | False |
| 147498 | 0 | 0.000000 | 0.000000 | 0 | True |
| 177015 | 4 | 0.066888 | 0.000000 | 0 | True |
| 190676 | 2 | 0.159907 | 0.031926 | 0 | True |
| 468505 | 4 | 0.352983 | 0.031355 | 0 | True |
| 499768 | 1 | 0.012322 | 0.000021 | 0 | True |

The two failures, 6012 and 134882, each lose one intended-q bit. Both still have semantic read, found and content_match true. The second source target is b2c0b53c, decoded b2c0953c; its recomputed semantic code is a different observation and must not be substituted for the intended payload. Mean squared bit hinges and a maximum across branches allow individual bit/branch regression while the maximum decreases. Positive final SDXL hinges remain in both cases; this is an expected objective tradeoff, not evidence of an evaluator discrepancy.

Clean PSNR mean/minimum is 43.9087/42.7317 dB; SSIM mean/minimum .980557/.969663; LPIPS mean/maximum .022359/.056261. No human visual verdict is present. C0 and wrong-owner any-channel detections are 0/36 each, 0/72 observed calls overall, reusing twelve sources and cached C0 pixels. They do not establish population FPR.

The screen and writer together cost 980.062 seconds at USD 0. Internal pre-checker loss branches are training measurements and supply no official attack-survival counts. Historical F5/M1/M2 outcomes remain unchanged; D2 is another algorithm in the same image-domain refinement family. A separate prospective method decision is required for any acceptance-rule change. No T4/T5 improvement, independent generalization or publication claim follows.

Analysis: [statistics](native-writer-statistics.json), regenerated with `scripts/journal_native_writer_analysis.py --run <retained D2 run> --output research/journal-upgrade-20261009/native-writer-statistics.json`. The script uses full calls and logged measurements, not the run summary and not floating-point replay.
