# C-Q5M5 conditional T3 result

The frozen conditional T3 gate fails at both strengths: **6/8 marked images qualify at strength 0.1; 0/8 qualify at strength 0.4**. All four C0 images remain absent against both public words at each strength. The run is complete and passes the recorded provenance, inventory, timestep and raw-word checks. This is a scientific carrier-survival failure, not a missing run or launch defect. Under the prospective stopping rule, the scalar/vote/window tuning branch closes; expansion is not triggered.

## Frozen source and complete inventory

Source: MAIN `.thesis-build/dev-runs/20261004-1004-progressive-t3`, commit `96b9b66ed116514db3fba882f38300c904c6b015`; `run.json` SHA-256 `e9c5b12020189ad2421e179a69c47c4f3752ee9d453c656c7d6a794217cfe04d`. Manifest SHA-256 is `c3283ab8b189ad81c5077413bb1ab18127156cff994d14d4f8e901fcdd086474`. The source primary run is `20261004-0950-progressive-redundancy`, SHA-256 `a232861b4062025afe501e27916b3ed96528df750aff8fb8774891aacec8d5e0`, whose all-eight clean-quality/clean/VAE gates and replay controls passed before the conditional manifest was frozen.

All twelve source PNGs were reused: eight marked original/complement outputs and four C0 outputs across seeds 1000–1003. Each received both declared strengths. No image was selected, replaced or regenerated. All 24 attack conditions completed, with zero missing, failed, excluded or safety-blocked conditions. The attacks used pinned SD1.5 fp16, fresh DDIM per condition, 20 inference steps, empty positive/negative prompts, CFG 1, sampler eta 0 and attack seed 0. Actual UNet and scheduler traces equal `[51,1]` at 0.1 and `[351,301,251,201,151,101,51,1]` at 0.4: 120 total UNet calls.

The run took 31.921 seconds, below 180 seconds. The 24 output PNG receipts sum to 10,707,634 bytes; maximum recorded Torch allocation was 3,440,968,192 bytes, below the recorded effective GPU cap. These are PNG artifact bytes and Torch allocation, not total process/disk usage. RAM peak is not recorded; a runtime guard is not a measured peak.

Read-only analyzer `scripts/m1_progressive_t3_results.py` revalidates the complete primary snapshot and its 160 artifact receipts, attack historical code/blob receipts, copied manifest, all 24 output hashes/sizes, source-image receipts, completion journal/conditions agreement, actual attack traces, raw coefficient majority words, both readout fields and their 64-hypothesis panels. Recomputed gates exactly match the runner. Model receipt identities match the primary source; the analysis does not load or rerun the models. The retained JSON is `research/m1-progressive-t3-summary.json`, SHA-256 `6223f1c24f73eb32658751e311e4b1e3339a1ba9889dd9351cfbd155f9330014`, with source/spec/analyzer/helper hashes and every raw word and per-bit group. An initial analyzer-only schema check rejected readout timing metadata as an unexpected reader; correcting that new checker made the rerun pass. No scientific source was changed.

```powershell
& 'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/venv/Scripts/python.exe' scripts/m1_progressive_t3_results.py --input-dir 'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/20261004-1004-progressive-t3' --output '<fresh-summary.json>'
```

## Native saved-image readout

Presence remains at least 14/16 matching bits. The native detector opens the attacked saved RGB8 image and uses VAE posterior-mode encoding, scaled-latent channel-zero DCT and the unchanged eight-vote reader. It receives neither source PNG, prompt, generation seed nor a selected-coefficient mask from embedding. The source PNG is used only by the attack and descriptive quality evaluation. Image-DCT remains a separately retained diagnostic; no oracle or alternative reader substitutes for native detection.

| Seed | Word | Primary clean | Primary extra VAE | T3 0.1 | T3 0.4 |
|---|---|---:|---:|---:|---:|
| 1000 | Original | 16 | 16 | 16 | 12 |
| 1000 | Complement | 16 | 16 | 13 | 10 |
| 1001 | Original | 16 | 16 | 14 | 12 |
| 1001 | Complement | 16 | 16 | 14 | 7 |
| 1002 | Original | 16 | 16 | 14 | 13 |
| 1002 | Complement | 16 | 15 | 14 | 8 |
| 1003 | Original | 16 | 16 | 11 | 11 |
| 1003 | Complement | 16 | 16 | 15 | 11 |
| Presence | Eight conditions | 8/8 | 8/8 | 6/8 | 0/8 |
| Exact word | Eight conditions | 8/8 | 7/8 | 1/8 | 0/8 |

The low-strength failures are seed 1000 complement (wrong zero-based bits 3,4,9; extracted `0101001111010110`) and seed 1003 original (bits 6,10,12,13,15; extracted `1011011001000100`). Every marked image fails at 0.4, including the 0.1 exact-recovery case. The observed high-strength range is 7–13 matches, not a claim of zero signal or a random-noise distribution.

Two payloads on a seed are correlated repetitions. For descriptive statistics, average their match counts within each seed, then summarize the four cluster means; no confidence interval, bootstrap or significance test is justified here.

| Strength | Four seed means | Mean | Median | Sample SD | Range |
|---|---|---:|---:|---:|---:|
| 0.1 | 14.5,14,14,13 | 13.875 | 14.000 | 0.629153 | 13–14.5 |
| 0.4 | 11,9.5,10.5,11 | 10.500 | 10.750 | 0.707107 | 9.5–11 |

Neither a mean above the threshold nor successful individual payloads replace the all-eight criterion. There are four reused source clusters, not sixteen independent attacked marked images.

## Controls and attack quality

| Seed | C0 at 0.1: original/complement matches | C0 at 0.4: original/complement matches |
|---|---:|---:|
| 1000 | 10 / 6 | 7 / 9 |
| 1001 | 8 / 8 | 11 / 5 |
| 1002 | 6 / 10 | 10 / 6 |
| 1003 | 3 / 13 | 9 / 7 |

All controls are below 14/16 against both words, although seed 1003 C0 at 0.1 has 13 complement matches. The native fixed wrong-message panel has 3/768 findings at 0.1 and 0/768 at 0.4. These queries reuse the same words and source clusters; they are not independent image-level negatives, a calibrated population FPR, or an authentication test.

The following attack changes compare each attacked marked image with its own clean marked source. They are descriptive and do not rerun the clean embedding-quality gate. Each statistic is over the four means of the two payloads within a seed.

| Strength | Metric | Mean | Median | Sample SD | Min–max |
|---|---|---:|---:|---:|---:|
| 0.1 | PSNR dB | 26.073472 | 26.240415 | 2.921769 | 22.505091–29.307966 |
| 0.1 | SSIM | 0.798346 | 0.817880 | 0.077376 | 0.689769–0.867852 |
| 0.1 | LPIPS | 0.072033 | 0.066179 | 0.020936 | 0.054754–0.101019 |
| 0.4 | PSNR dB | 20.417690 | 21.029127 | 2.736269 | 16.579042–23.033462 |
| 0.4 | SSIM | 0.582445 | 0.570927 | 0.114732 | 0.466390–0.721535 |
| 0.4 | LPIPS | 0.208336 | 0.211909 | 0.036302 | 0.161126–0.248399 |

No CLIP retention score or human semantic/visual verdict is available for this extension. The table does not establish that every regenerated image preserves intended content. Conversely, attack distortion does not retrospectively alter the frozen T3 gate, which prescribed these exact strengths and did not condition eligibility on post-attack quality.

## Bounded decision

The prospective margin amendment answered a real mechanism question: margin 0.5 repaired the measured extra-VAE all-eight gate at an observed clean-quality cost, with worst PSNR only 0.302524 dB above 35. The next mandatory challenge was diffusion transport, and its completed data now fail at both strengths. We have no unresolved positive carrier result whose required expansion is being skipped: the qualifying clean/VAE result received its prescribed conditional test.

Apply `m1-progressive-redundancy-design.md` without amendment: close further scalar margin, vote-count and guidance-window tuning on these blocks. No 0.4/0.6 margin grid, six/seven-vote retry, seed substitution, shortened attack, changed threshold or extra favorable payload is triggered. The twelve-cluster carrier expansion and binding follow-up are not triggered. A corrected execution defect could warrant an unchanged retry, but none was found in this receipt analysis.

This closes a finite public-carrier branch and supports the bounded family-C package receipt in `m1-family-C-bounded-receipt.md`. It does not prove that guided latent watermarking, decoder-aware optimization, trained extraction or dual binding is impossible. The final candidate still lacks CLIP+pHash+OwnerID binding and three qualified decision states; T4/T5 and held-out performance remain unimplemented/unmeasured for C. The author is the method designer, not the independent M1 reviewer. No GPU execution, threshold fitting, source-output edit or protected-file edit occurred in this analysis.
