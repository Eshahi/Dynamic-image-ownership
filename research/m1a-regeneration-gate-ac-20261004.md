# M1a regeneration gate: A-C terminal candidate versus v5 r3

Run by Claude (Anthropic) on 2026-10-04 at the user's request, after the first autonomous day. Exploratory development evidence on the twelve development sources only; no held-out data, threshold, code or schedule change.

## What was run

- Candidate: A-C `m1-terminal-continuous-e2e-v1` (method core `7f2cf79f76…`), the twelve completed embedding runs (`20261004-1102-e2e-1675`, `20261004-1122-e2e-4795`, `20261004-1142-e2e-6012`, and the nine `20261004-1207-e2e-expansion-queue/e2e-*`).
- Tool: Codex's own assessor `scripts/m1_assess_terminal_e2e.py`, unchanged. Manifest prepared with `--prepare` and committed as `research/m1-ac-t3-claude-dev.json` (commit `1918b18`); partitions `shard-0` to `shard-5` (clean and T3 only; the `transfers` partition with T4/T5 was not run).
- Attack: pinned SD1.5 DDIM img2img, 20 steps, empty prompt, CFG 1, eta 0, strengths .05/.1/.2/.4, seeds 0/1/2, plus deterministic VAE posterior mode. Reader: VAE posterior-mode readout with recomputed CLIP and pHash templates, public OwnerID, inclusive threshold 4.
- Outputs: MAIN `.thesis-build/dev-runs/20261004-2100-ac-t3-claude/shard-*/` (run.json, conditions.json, journal, PNGs, reader latents) and `summary-claude.txt`. About 5 minutes of GPU work in total; each shard re-audits the twelve source runs on CPU first.

## Results (owner alpha, marked image C1, semantic channel)

| Condition | Completed | Semantic detected | both_match | Median semantic score |
|---|---:|---:|---:|---:|
| Clean | 12 | 12 | 12 | 5.88 |
| VAE mode | 12 | 12 | 11 | 5.94 |
| img2img .05 | 36 | 36 | 33 | 5.86 |
| img2img .1 | 33 | 27 | 14 | 4.48 |
| img2img .2 | 33 | 9 | 2 | 3.37 |
| img2img .4 | 33 | 1 | 0 | 2.12 |

Eighteen conditions (source 6012 at .1/.2/.4, C0 and C1) were blocked by the safety checker and stay missing. Unmarked C0: 0 of 159 owner-alpha calls detected (maximum score 2.82). Wrong owners: 0 of 954 calls detected (maximum score 3.40). The null scores behave roughly like a standard normal, so the margin to threshold 4 is small; threshold 4 is an uncalibrated engineering value.

## Paired comparison with v5 r3 dev-001

v5 T3 used ten of these sources (not 1675 and 4795). Identities are joined by source, strength and seed where both completed; v5 success is its own `semantic.found and content_match` under its own thresholds (recomputed 4.98, decoded 8.26).

| Strength | Paired identities | A-C detected | v5 detected | Only A-C | Only v5 |
|---|---:|---:|---:|---:|---:|
| .05 | 30 | 30 | 30 | 0 | 0 |
| .1 | 27 | 22 | 25 | 2 | 5 |
| .2 | 27 | 9 | 17 | 2 | 10 |
| .4 | 27 | 1 | 2 | 1 | 2 |

## Verdict

**A-C fails the M1a gate:** at .1 and .2 it detects fewer paired identities than v5 (22 vs 25, 9 vs 17), although it uses a lower threshold (4) than v5 (4.98). It is a large improvement over the earlier A hybrid (3 of 33 at .1, 0 of 33 at .2), reaches v5's level at .1, and keeps strict clean quality and clean both_match on all twelve. The signal survives regeneration only partly: the median score falls from 5.9 to 4.5 at .1 and 3.4 at .2, against a null near 0. These are small dependent development counts (ten to twelve source clusters), not a statistical superiority or inferiority test.

Implication for the next design: the A-C carrier is as robust as v5 at .1 and less robust at .2, at similar clean quality (35.2 dB cap versus v5's 35.5 dB fill). Families B and C are closed. A new design must raise the post-regeneration score at .2, not only clean or VAE margins.
