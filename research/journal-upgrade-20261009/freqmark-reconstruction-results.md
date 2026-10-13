# FreqMark equation reconstruction: resource-limited result

2026-10-13. **Feasibility remains unresolved.** The fixed FM-R48-Eq10-SD2community implementation hit its 9 GiB CUDA allocator allowance during the first optimization step, before any update completed. No 400-step marked image was delivered. This is a local implementation/resource outcome, not failure of native FreqMark, a strict-quality score of 0/2, or an E3 superiority result.

The [protocol](freqmark-reconstruction-protocol.md) specifies the single recipe and its known fidelity limitations. [Compact evidence](freqmark-reconstruction-summary.json) records the retained run, configuration commit, resources, unoptimized diagnostics and actual asset receipts. The primary scientific receipt is MAIN `.thesis-build/dev-runs/20261013-1758-freqmark-reconstruction-platform-fix/run.json`, code `878a736`, outcome `allocation_failed`. The child process exited; no GPU job remains from this test.

## What ran

The original preflight at `600a46e` ended before acquisition in approximately .16 seconds because Windows returned desktop graphics applications as compute processes. Its separate terminal receipt remains unchanged at MAIN `.thesis-build/dev-runs/20261013-1758-freqmark-reconstruction/run.json`. A CIM process census found no competing Python/WSL experiment. The committed platform correction used an explicit observed desktop-PID snapshot and the original start timestamp, so the budget was not reset. This was not a retried scientific source.

Inclusive elapsed time was **580.234 seconds** (9 minutes 40 seconds), below the original 1,800-second cap. Acquisition took 480.922 seconds. Both pinned weights and their configs/cards passed the declared checks: DINOv2-small at `ed25f3a31f01632728cabb09d1542f84ab7b0056`, community SD2.1 VAE at `4e63672c03103b6c636b8fb4119ba982469b2955`. The weights total 422,893,236 bytes; exact URLs, licenses and actual hashes are in the compact receipt and downloads ledger. No new GPU stack or installer was used.

Source 30's predetermined message, unmarked extraction and zero-perturbation VAE diagnostics were recorded. During step 1, the noisy-latent VAE decode exhausted the allocator allowance while the clean branch's gradient graph was retained. It requested another 256 MiB. The CUDA error reported 8.62 GiB allocated and 235.53 MiB reserved but unallocated under the 9 GiB allowance. The device still had 1.68 GiB free of 11.94 GiB; the fixed local allowance, not proof of absolute hardware impossibility, is the relevant boundary. The last cooperative GPU sample predates the failure and is not the exact failure-time peak.

| Source | Completed updates | Final 400-step image | Status |
|---|---:|---|---|
| 30 | 0 | Unavailable | Incomplete: allocation failure during first forward step |
| 72 | 0 | Unavailable | Not started |

No gradient/update validity claim, clean exact-recovery rate, strict-quality rate, attack result or detector timing follows. The implementation never reached the ten-step latency forecast. The original fixed recipe and terminal record were not repaired, resumed or rerun; precision, iteration count and memory allowance were not changed.

## Diagnostic values, not baseline performance

On source 30, the unmarked image agrees with the fixed random target on 31/48 bits and its complement on 17/48. The zero-perturbation VAE output agrees on 29/48, with PSNR 29.114 dB, SSIM .890570 and LPIPS .036462. These describe the input and unoptimized reconstruction. They do not describe a FreqMark watermarked output, establish FPR, or show that optimization could not meet a quality budget.

The recipe remains an independent v1-equation reconstruction: author implementation identity, numeric margin, feature/FFT details, augmentation routing and community-VAE equivalence are unresolved. Those fidelity limits would still matter even if the memory issue were fixed.

## Consequence for the article plan

Do not add a failed-baseline row or claim competitive superiority. The closest external comparison is still missing. A separately designed future implementation could investigate mathematically equivalent memory-saving execution, but it would require numerical checks and a new bounded protocol; this attempt supplies no outcome for it. A larger paid GPU is not automatically required or authorized. First decide whether the intended comparison and reproduction fidelity can answer an externally meaningful question.

This closes the bounded feasibility attempt. Retain the downloaded assets and all failure evidence. The article decision remains conditional, as specified in the [viability memo](h2-article-viability-decision.md) and [updated roadmap](plan.md).
