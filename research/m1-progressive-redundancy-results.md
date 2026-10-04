# C-Q5M5 primary development screen

Status: completed primary screen; eligible for the frozen conditional T3 extension. This report contains no T3 result. Analysis by the method author (GPT-6-astra, high), not an independent milestone review.

The single prospective change from C-Q5 was the embedding margin, 0.3 to 0.5. The nearest-five-of-eight objective, deterministic tie handling, final five guidance steps, eta 100, public payload, reader and 14/16 presence threshold stayed fixed. All eight candidate cells pass both the clean-quality gate and clean/additional-VAE presence gate. Clean extraction is exact in 8/8 cells; additional-VAE extraction is exact in 7/8 and present in 8/8. These are eight payload conditions on four reused generated-image clusters, not eight independent source images.

## Source and validation

The immutable source is MAIN `.thesis-build/dev-runs/20261004-0950-progressive-redundancy/run.json`, generated at commit `f762f336229310947e1047cdbe37b97bb5b7a2d5`. Its SHA-256 is `a232861b4062025afe501e27916b3ed96528df750aff8fb8774891aacec8d5e0`; copied manifest SHA-256 is `56cd7081887f437d395c20842b412dff1960a3e87c8407ebf931da7a9226bd05`. The run completed in 133.265 seconds with 20 generations, 40 primary clean/VAE conditions and 1,000 UNet calls. It used seeds 1000–1003, SD1.5 fp16, DDIM 50 steps and CFG 7.5. Per seed, the inventory was C0, two old-Q5 replays and two new-Q5M5 payload arms.

The read-only CPU analysis in `scripts/m1_progressive_redundancy_results.py` invokes the strict source validator from `scripts/m1_progressive_t3.py`. It validates completion, the exact inventory and gates, historical code receipts, all 160 artifact hashes and sizes (113,601,897 bytes), all 24 old-PNG replay receipts, equal paired initial-noise hashes, and trace/endpoint coefficient-to-word consistency. All checks passed. C0 remains below 14/16 for both public words in both primary channels. The script then recomputes stage summaries from the retained raw coefficient records; it performs no image generation, model inference, threshold selection or source-file mutation.

The generated analysis artifact is `research/m1-progressive-redundancy-stage-summary.json`, SHA-256 `d816043016f400d9877b2a3d9cece078e4745298fabcc9c5b69d0423ba7eb642`. It records the source snapshot, analyzer/helper hashes, all 20 row summaries and the eight matched old/new comparisons. Reproduction requires a fresh output filename:

```powershell
& 'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/venv/Scripts/python.exe' scripts/m1_progressive_redundancy_results.py --input-dir 'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/20261004-0950-progressive-redundancy' --output '<fresh-summary.json>'
```

## Candidate primary results

Quality compares each generated candidate with its same-seed generated C0. It is not preservation quality relative to an existing photograph. The strict gate is PSNR >35 dB, SSIM >0.9 and LPIPS <0.1 in every candidate cell. Presence requires at least 14 matching bits out of 16 in every clean and additional-VAE cell. Original payload is `1011010001101001`; complement is `0100101110010110`.

| Seed | Payload | PSNR dB | SSIM | LPIPS | Clean matches | Additional-VAE matches | Joint gate |
|---|---|---:|---:|---:|---:|---:|---|
| 1000 | Original | 36.770386 | 0.976419 | 0.010644 | 16/16 | 16/16 | Pass |
| 1000 | Complement | 40.246742 | 0.987552 | 0.005106 | 16/16 | 16/16 | Pass |
| 1001 | Original | 37.304047 | 0.992255 | 0.003093 | 16/16 | 16/16 | Pass |
| 1001 | Complement | 35.302524 | 0.988226 | 0.004769 | 16/16 | 16/16 | Pass |
| 1002 | Original | 38.926276 | 0.989583 | 0.003688 | 16/16 | 16/16 | Pass |
| 1002 | Complement | 40.784591 | 0.992714 | 0.002499 | 16/16 | 15/16 | Pass |
| 1003 | Original | 41.495113 | 0.988863 | 0.004249 | 16/16 | 16/16 | Pass |
| 1003 | Complement | 44.333081 | 0.994002 | 0.002268 | 16/16 | 16/16 | Pass |
| Mean | Eight cells | 39.395345 | 0.988702 | 0.004539 | 16/16 | 15.875/16 | 8/8 |

The smallest PSNR margin is only 0.302524 dB, in seed 1001 complement. At fixed peak range this corresponds to approximately 7.2% extra pixel-MSE headroom before reaching 35 dB. The mean cannot substitute for the all-eight gate or establish generalization to new source clusters.

## Matched comparison and signal evolution

Only the eight old-Q5 replays from this same run are used for the following comparison: identical seed, prompt, initial noise and intended word for each pair. Their exact replay receipts link them to the earlier Q5 screen. C-Q5M5 lowers mean PSNR from 42.298353 to 39.395345 dB (a 2.903008 dB mean decrease), lowers mean SSIM from 0.993591 to 0.988702, and increases mean LPIPS from 0.002426 to 0.004539. The measured pixel-MSE increase is 1.720–2.459 times across the eight matched pairs. All eight old and new cells nevertheless pass the fixed quality gate.

The terminal predecode and clipped-float-cycle stages below are diagnostic access to internal states. They are not additional blind image detections. Clean RGB8 and additional-VAE RGB8 are the primary saved-image readouts through the unchanged VAE-mode latent DCT reader.

| Stage | Old Q5 exact | Old Q5 present | Old mean matches | Q5M5 exact | Q5M5 present | New mean matches |
|---|---:|---:|---:|---:|---:|---:|
| Terminal predecode diagnostic | 8/8 | 8/8 | 16.000 | 8/8 | 8/8 | 16.000 |
| Clipped float cycle diagnostic | 6/8 | 8/8 | 15.750 | 8/8 | 8/8 | 16.000 |
| Clean RGB8 primary | 6/8 | 8/8 | 15.750 | 8/8 | 8/8 | 16.000 |
| Additional-VAE RGB8 primary | 1/8 | 6/8 | 14.250 | 7/8 | 8/8 | 15.875 |

The previously failing original-payload arms improve from 13 to 16 VAE matches for seed 1002 and from 11 to 16 for seed 1003. The remaining Q5M5 error is bit 14 (zero-based) of seed 1002 complement, whose intended value is one. Its trace explains why exact recovery and thresholded presence differ:

| Stage | Positive votes out of eight | Fifth signed coefficient | Extracted bit |
|---|---:|---:|---:|
| Terminal predecode | 5 | 0.523065 | 1 |
| Clipped float cycle | 5 | 0.188923 | 1 |
| Clean RGB8 | 5 | 0.169794 | 1 |
| Additional-VAE RGB8 | 4 | -0.030090 | 0 |

The unchanged reader resolves a four/four tie as zero, producing `0100101110010100` after the extra VAE cycle: 15/16 matches and therefore presence. In the matched old Q5 complement, bit 7 was also wrong after clean decoding and the VAE cycle; the larger margin repairs that error while bit 14 still erodes. This is direct evidence that the added coefficient margin improves survival through this measured codec path. It does not identify a universal channel-noise bound or prove diffusion robustness.

## Prospective consequence and limits

The primary result activates, without further tuning, the already frozen T3 extension: all eight marked sources and four C0 sources at strengths 0.1 and 0.4, 20-step DDIM, empty prompts, CFG 1, eta 0 and attack seed 0, with a fresh scheduler per image. This gives 24 attack conditions and a nominal 120 UNet calls. The manifest pins the actual completed primary source hash; the adapter revalidates source completion, all gates and receipts before GPU loading. T3 results must be reported separately when available; primary success is not T3 success.

The finite stopping rule in `m1-progressive-redundancy-design.md` remains unchanged. A genuine failure of the frozen conditional T3 gate closes this scalar/vote/window tuning branch; there is no post-result margin grid, seed selection or weakened 14/16/all-eight requirement. A different channel-aware objective would require a separately justified mechanism amendment and would not automatically count as a new design family.

This screen concerns a public 16-bit carrier with eight repetitions and a lightweight, non-inverting image reader. It does not yet implement the proposal's combined CLIP/pHash/OwnerID binding or three qualified decision states. No authentication, resistance to public-key forgery, T4/T5 robustness, existing-photo quality, human visual acceptance, held-out performance or M1 completion follows from these results. Four reused synthetic clusters and two dependent payloads per cluster remain exploratory evidence. No held-out data or additional GPU work was used in this analysis.
