# B-LW1-P1 independent probe results

**The predeclared implementation gate passed, with all 24 images completed and no excluded condition.** Exact correct- and wrong-key replication, raw-sign query checks, foreign-nonce/alignment controls, zero-aware algebra and source-noise self-checks all passed. This supports the pinned synthetic initial-noise carrier observation; it is not a novel carrier claim, independent population FPR estimate, content binding, authenticated ownership or complete M1 threat result.

## Provenance and independent checks

Source: MAIN `.thesis-build/dev-runs/20261004-0037-gs-probe`, commit `ba94b542f76e57ef3270ef55e8057e9227f39202`, outcome `completed`, overall duration 13.812s; worker 10.344s. No timeout. All 24 planned images and 72 foreign/24 shift queries were retained. Four clusters × C0/C1 × clean/VAE/T3.4-seed0 were selected prospectively by [the diagnosis](m1-gs-lightweight-positive-diagnosis.md), not after scoring. [Implementation](m1-gs-lightweight-probe-implementation.md) describes the separate opaque worker and evaluator boundary.

For this report, all outer output hashes were recomputed and matched, the sealed hash matched the worker, and all 24 evaluator-map rows matched the frozen copied LW condition rows. Raw latent/sign bytes agreed under strict `>0`; an independent vectorized XOR/reshape/sum calculation reproduced **384/384 vote arrays and bit words** (24 images × four nonces × original/wrong/shift/negative queries). Full CPU evaluator recomputation equalled the saved assessment, including transport and gate values. No model or GPU was run for this report.

- Outer run SHA-256: `58358d5ef87023d2fa2b51ce2951427c58f404887c92909ff67b04cd7ce6ab55`.
- Assessment SHA-256: `b60d4f7b3a2590dffc4e2fc1815440ff5632263fa8a0b3cfa4eec072e315585b`.
- Sealed reader input SHA-256: `f275e6d80f6ee70c1d012b7651e04956152bf42bb7b25fcf7a4a633d405ce58c`.
- Evaluator map SHA-256: `07eeeaba3c50544de133ff72cc8ba7222550fba6172e36217a588e9bbe9e7665`.
- Worker run SHA-256: `e59d1c33c620905420e6166579a986e7fce3fbb61e3946887d5a6f971103e728`.
- Probe manifest SHA-256: `3d597b16ad13a0cc4956597eadb6148d6cb21799964b8fa7827ba4306410467c`.

The fixed original source commits remain native `6a46faad51d91b285d00bbb6b2a4563ef681c11b` and LW `8809c8d5dad67edfc83b914516dccbbf7fdbca58`. Their source receipts, copied runs/conditions, exact PNGs and output digests are retained in the probe. Public key/nonce fixtures plus enrolled reference messages are side information. The worker receives no payload, arm, original seed, old score or original-noise array; this is a restricted data-flow check, not a hostile-filesystem sandbox.

## Gates and primary recovery

| Predeclared engineering gate | Observed |
|---|---|
| Complete fixed 24 inventory | 24/24;0 missing/failed |
| Correct-key vote/bit/match exact replication | 24/24 |
| Wrong-key vote/bit/match exact replication | 24/24 |
| Foreign nonce below 180/256 | 72/72; maximum 154 |
| One-column shift below 180/256 | 24/24; maximum 161 |
| Zero-aware complement/sign/bit algebra | 24/24 |
| Reconstructed fp16 initial marked-noise hashes and 256-bit roundtrip | 4/4 |
| Runtime synthetic known-word/one-coordinate/tie/complement fixtures | 4/4 |
| Overall implementation gate | true |

Presence remains >=180/256; exact means 256/256. Every primary C1 image is present (12/12), while every primary C0 and wrong-key query is absent (0/12 and 0/24). Presence does not mean exact payload recovery.

| Arm | Channel | Presence | Exact | Own matches mean / median / sampleSD / range |
|---|---|---:|---:|---|
| C0 | clean | 0/4 | 0/4 | 126.50 / 128.50 / 9.75 / 113–136 |
| C0 | vae | 0/4 | 0/4 | 125.25 / 123.50 / 14.97 / 109–145 |
| C0 | regen-0.4-seed0 | 0/4 | 0/4 | 122.25 / 122.50 / 4.99 / 117–127 |
| C1 | clean | 4/4 | 2/4 | 250.75 / 255.00 / 9.22 / 237–256 |
| C1 | vae | 4/4 | 1/4 | 251.00 / 254.00 / 7.44 / 240–256 |
| C1 | regen-0.4-seed0 | 4/4 | 0/4 | 229.50 / 230.50 / 18.77 / 206–251 |

All 24 wrong-key queries range120–139/256; all 72 foreign-nonce queries range109–154; all 24 shift queries range117–161. None reaches 180. Nonces, wrong streams, shifts and three channels share only four source clusters; these are correlated engineering controls, not independent Bernoulli samples or an adaptive-public-forgery test. No cutoff was changed.

## Algebra, zeros and numerical details

Four images have one exact scaled zero each, each affecting one bit group. Their identities and zero-vote adjustments are retained in assessment.json. Strict `(-latent)>0` leaves zero signs zero; the measured correction to `64-v` matches whitening exactly. All nonzero sign complements and non-tied zero-adjusted bit relations pass. Ties decode zero on both orientations, so negated match counts need not equal 256 minus original matches; this is a surfaced decoding asymmetry, not a replication discrepancy. Negated C1 predictions are absent against the own reference but present against its complement on all 12 cases; this demonstrates algebraic reference-independent behavior, not a new threat attack.

| Source condition with scaled zero | Zero coordinates | Affected bit groups |
|---|---:|---:|
| prompt-1-C1-vae | 1 | 1 |
| prompt-1-C1-regen-0.4-seed0 | 1 | 1 |
| prompt-3-C0-vae | 1 | 1 |
| prompt-3-C1-vae | 1 | 1 |

## Raw transport measurements

Each cell below is mean [min–max], n=4. These are raw latent/noise sign agreement and cosine, not decoded bit accuracy and not acceptance criteria. The evaluator alone reconstructs initial noise. Ordinary C0 noise also transports to final VAE latents; C0 has strong own-Gaussian correlation while remaining near chance against the marked code.

| Output arm/channel | Initial noise comparator | Raw sign agreement | Cosine |
|---|---|---|---|
| C0/clean | own paired C0_gaussian | 0.691452 [0.656372–0.742920] | 0.546429 [0.446527–0.660615] |
| C0/clean | own paired C1_marked | 0.498734 [0.489014–0.504333] | 0.000842 [-0.016174–0.016015] |
| C0/vae | own paired C0_gaussian | 0.686020 [0.650391–0.733948] | 0.533208 [0.431675–0.641011] |
| C0/vae | own paired C1_marked | 0.497238 [0.487488–0.502747] | 0.001023 [-0.017222–0.016267] |
| C0/regen-0.4-seed0 | own paired C0_gaussian | 0.599640 [0.582947–0.623901] | 0.305383 [0.256502–0.376110] |
| C0/regen-0.4-seed0 | own paired C1_marked | 0.497437 [0.490967–0.504028] | 0.004336 [-0.010536–0.018685] |
| C1/clean | own paired C0_gaussian | 0.499359 [0.495911–0.502502] | 0.000270 [-0.012961–0.005483] |
| C1/clean | own paired C1_marked | 0.664185 [0.600830–0.702148] | 0.477676 [0.347017–0.567962] |
| C1/vae | own paired C0_gaussian | 0.498657 [0.491333–0.503418] | 0.000448 [-0.013554–0.007076] |
| C1/vae | own paired C1_marked | 0.658844 [0.597961–0.695801] | 0.466896 [0.343339–0.551052] |
| C1/regen-0.4-seed0 | own paired C0_gaussian | 0.499481 [0.498718–0.500183] | 0.000130 [-0.007084–0.006211] |
| C1/regen-0.4-seed0 | own paired C1_marked | 0.585541 [0.554199–0.612488] | 0.267877 [0.184421–0.345497] |

All 144 foreign-noise comparators (24 images × three foreign seeds × Gaussian/marked) have sign agreement 0.500502 [0.491455–0.510803] and cosine -0.000044 [-0.014346–0.013387]. These repeated comparisons are descriptive, without fitted threshold.

## Runtime and limits

Exactly 24 VAE encodes, zero U-Net and zero text-encoder evaluations were recorded. Posterior mode and fp16 scaling .18215 were fixed; no sign changed after positive scaling. Model/preprocessor/package hashes remain in worker receipts. Mean per-image encode time .07104s, range .046–.437s includes preprocessing, synchronization and the initial warmup. Peak allocated bytes 611,523,584 (~.570GiB) and artifacts 23,881,991bytes (~22.776MiB) are below 10GiB/100MiB; duration is below 120s. Torch allocation is not total resident GPU memory. No new generation, inversion, image-quality scoring or human judgment was performed by P1.

P1 independently supports exact reproduction of the original positive reading on these three predeclared channels. It does not add new generated samples, broader strength/seed/model coverage, photographic source preservation, CLIP/DCT content binding, T4/T5 evidence, authentication or an independent milestone review. The fixed four clusters cannot establish universal regeneration survival or population FPR. Human visual assessments remain null. The prospective registered-content B2-R amendment remains a separate next experiment; no method was changed here.

## Every retained condition

All values are matches/256. Foreign scores are in increasing foreign-seed order; the own seed is omitted. Shift is exactly one wrapped column. Negated scores are own/complement.

| Case | Arm | Channel | Own | Wrong | Foreign three | Shift | Negated own/complement |
|---|---|---|---:|---:|---|---:|---|
| prompt-0 | C0 | clean | 130 | 127 | 122/131/139 | 127 | 127/129 |
| prompt-0 | C0 | vae | 126 | 125 | 116/140/133 | 120 | 125/131 |
| prompt-0 | C0 | regen-0.4-seed0 | 127 | 125 | 126/129/130 | 131 | 132/124 |
| prompt-0 | C1 | clean | 237 | 125 | 138/115/123 | 138 | 18/238 |
| prompt-0 | C1 | vae | 240 | 134 | 144/119/116 | 134 | 19/237 |
| prompt-0 | C1 | regen-0.4-seed0 | 206 | 120 | 136/128/119 | 137 | 51/205 |
| prompt-1 | C0 | clean | 127 | 131 | 128/133/133 | 124 | 125/131 |
| prompt-1 | C0 | vae | 121 | 128 | 129/139/123 | 122 | 137/119 |
| prompt-1 | C0 | regen-0.4-seed0 | 119 | 125 | 136/119/112 | 125 | 127/129 |
| prompt-1 | C1 | clean | 256 | 126 | 137/130/144 | 161 | 0/256 |
| prompt-1 | C1 | vae | 256 | 130 | 137/122/143 | 158 | 0/256 |
| prompt-1 | C1 | regen-0.4-seed0 | 251 | 128 | 154/128/142 | 153 | 6/250 |
| prompt-2 | C0 | clean | 113 | 139 | 122/143/126 | 134 | 140/116 |
| prompt-2 | C0 | vae | 109 | 129 | 132/130/119 | 131 | 148/108 |
| prompt-2 | C0 | regen-0.4-seed0 | 117 | 132 | 126/132/120 | 126 | 142/114 |
| prompt-2 | C1 | clean | 254 | 134 | 129/126/126 | 154 | 2/254 |
| prompt-2 | C1 | vae | 253 | 131 | 140/131/119 | 153 | 3/253 |
| prompt-2 | C1 | regen-0.4-seed0 | 235 | 126 | 141/128/132 | 159 | 23/233 |
| prompt-3 | C0 | clean | 136 | 120 | 109/128/122 | 137 | 119/137 |
| prompt-3 | C0 | vae | 145 | 133 | 113/121/133 | 130 | 121/135 |
| prompt-3 | C0 | regen-0.4-seed0 | 126 | 124 | 129/133/125 | 117 | 127/129 |
| prompt-3 | C1 | clean | 256 | 136 | 141/132/120 | 140 | 1/255 |
| prompt-3 | C1 | vae | 255 | 135 | 132/132/118 | 139 | 1/255 |
| prompt-3 | C1 | regen-0.4-seed0 | 226 | 126 | 138/130/123 | 144 | 24/232 |
