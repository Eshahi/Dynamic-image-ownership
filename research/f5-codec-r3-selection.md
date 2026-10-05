# Codec r3 selection — longer semantic code (64/128-bit)

## Motivation
Binding failures dominate F5 r2 at .4/.5 (content_uncertain/mismatch even though carrier found). Carrier has 3272 latent slots vs 320 chips, so more code bits could fit. The prompt asks to test 64- and 128-bit codes before declaring plateau.

## Design
- Keep v5 profile thresholds (radius 6/10 at 32 bits) scaled proportionally: 64→12/20, 128→24/40 (same angles 6pi/32, 10pi/32).
- Two variants:
  - r3-64x5: 64 segments × 5 chips = 320 chips (same total, 2× slots/chip density halves, per-segment SNR -3 dB).
  - r3-64x10: 64 segments × 10 chips = 640 chips (2× total, slots/chip ~5.1 vs 10.2, still >=5, feasible).
  - r3-128x5: 128 segments × 5 chips = 640 chips (same total as 64x10).
- All use same band/whitening/DCT, same encoder PGD, same fragile tier and soft binding (angles scaled by CODE_BITS).
- False-positive bound: decoded threshold for 2^bits search space.
  - 32→8.259, 64→10.587, 128→14.151 at FPR 1e-6 (Bentkus-Dzindzalieta, computed in 21:15 analysis).
  - Corrected distance threshold = radius scaled as above.
  - Decision table unchanged, only limits scale.

## Why this is cheap to kill (pre-run prediction)
Stress baseline decoded scores: .4 mean 10.25 (p10 8.62), .5 mean 7.92 (p10 4.79), .6 mean 5.07.
At 64-bit threshold 10.59, expected additional failures vs 32-bit:
- .4: <8.26 fails 4/58 → <10.59 fails 35/58 (Δ +31)
- .5: 25/58 → 52/58 (Δ +27)
So carrier, not binding, would become the bottleneck. Even with 10-chip variant keeping per-segment SNR, total energy per code scales sqrt(chips) only if budget spreads. Budget is fixed at 52 dB, so per-chip margin unchanged; total decoded score scales sqrt(bits) only if chips add coherently, but per-bit threshold also scales. Net predicted Δ is strongly negative.

## Selection rule (commit-before-run)
- Primary metric: paired C1 semantic success on stress grid .4/.5/.6 (same 12×5) vs F5 r2 baseline 86/116 on .4+.5 and 49/58, 37/58, 10/57 individually.
- Kill: no variant beats F5 r2 on .4+.5 combined (needs >=87/116 and >=+2 at .5 individually) at equal quality (LPIPS mean ≤.0173, PSNR ≥44) AND T4 0/20, T5 0/66, C0/wrong-owner 0.
- Cheap kill first: re-read F5 r2 rows through r3 scoring without re-embedding (carrier projections unchanged if chips=320 and carrier mapping reinterpreted as first 32 segments; not exact — so pilot must re-embed 4 sources at 64x5, clean quality check, then quick stress on 4 sources).
- If re-read/4-source pilot shows -.4 or -.5 vs baseline at equal PSNR, kill longer code family without full 12-source runs.

## Execution order
1. Commit this doc + r3 codec (parameterized CODE_BITS override, not touching v5.py).
2. 4-source pilot: 64x5 at PSNR 52, stress .4/.5/.6 × 5 seeds on sources 1675/6012/25394/80932, compare vs F5 r2 same subset.
3. If pilot not killed, enqueue full 12-source stress for winner + T4/T5 + binding adapt check.

## Cost / limitation note
Longer code is expected to fail the carrier threshold before it can help binding. If pilot confirms, record as H4a kill and note as limitation: longer code needs stronger latent gain (higher budget or attack-aware embedding) to be viable; not a replacement at 52 dB.
