# m1b runner progress — 2026-10-05

## 20:52 UTC — start
- Worktree claude/f5-m1b at 0cfb528 clean. Read frozen spec, configs, manifest, endpoints, f5 codec/gate/t4, sample-size, external-index. No held-out touched.

## 21:30 UTC — runner + tests + cohort memo
- Wrote scripts/m1b_f5_runner.py (candidate-agnostic): validate_manifest, shard_sources (sorted round-robin), journal (journal.jsonl append + read), resume (skip completed row ids), never substitutes seeds (t3_strengths/t3_seeds exact in manifest, no silent fill), embeds via f5_latent_codec.embed_rgb at configs/f5-r2.json, T3 grid (.05/.1/.2/.4 x3 seeds + VAE, 20 steps CFG1 eta0), T4 residual-transfer (scales .5/1, donor_C1/sham, residual_transfer helper), T5 cross-owner pairs (C0 and C1 vs other owner), C0/wrong-owner controls, receipts (path+sha256) + run.json + per-cell endpoints via m1_confirmatory_endpoints.cell (Clopper-Pearson one-sided 95% + Wilson). Reuses existing code, no new broker/launcher/audit layers.

## 22:05 UTC — tests + rehearsal
- Unit tests tests/test_m1b_f5_runner.py: 20 tests — manifest validation, duplicate rejection, sharding (deterministic, no overlap, cover), journal append/read + truncated-journal corruption surfacing, resume skip, never-substitute-seeds invariants. All 20 pass (stdlib venv).
- End-to-end rehearsal (CPU) on two development images only (dev-1675, dev-4795 from f4_transfer_probe.SOURCES, never held-out): manifest validation + sharding (2 shards) + journal/resume + non-substitution. Report at research/m1b-rehearse-two/report.json + manifest.dev-two.json. Held-out not touched.
- Endpoints verified (science venv): 0/300 -> 0.009936, 1/300 -> 0.0157 via m1_confirmatory_endpoints.bounds.
- GPU smoke (short, development only) requested in research/f5-gpu-queue-requests.md for GPU lead: exact command with selection rule, two dev images, frozen 52 dB soft 7-view, verifies both_match self-verification; never held-out.

## 22:10 UTC — cohort memo
- Wrote research/m1b-cohort-decision.md: narrow COCO512 (300 test groups, T3/T4/T5 30-unit descriptive slices) vs all-domain (600/300/3000 = 3900 test groups), Wilson/zero-FP bounds table, per-cell resolution, what each lets thesis claim, costs and prerequisites (BLOCKED_DATA/PROTOCOL/RESOURCE). No choice made.

## Next
- Commit + push claude/f5-m1b; write worker report research/worker-report-m1b-20261005.md; end by 00:30 UTC.

## 2026-10-06 — runner v2 (Claude Code, Opus 5.5 supervisor)
- User decision: narrow COCO512 (see `m1b-cohort-decision.md`).
- **Bug fixed:** v1 scored T3 C1 success as final `both_match`. Regeneration is expected to remove the fragile instance tier, so T3 success would have read near 0 even when the semantic channel found the owner with matching content. The development stress gates always scored T3 by the semantic channel, and the confirmatory draft asks for component states to be recorded separately.
- **v2 T3 cells,** for each dose (VAE round trip, .05/.1/.2/.4):
  - semantic success, split into **checked** (the mark was read and its code compared) and **assumed** (found only by the recomputed pattern, so the content was not compared);
  - `both_match`, descriptive;
  - wrong-owner semantic and any-found negatives.
- C0 T3 negatives are reported as semantic, any-found and both_match.
- Secondary semantic and any-found negatives are added for clean wrong-owner, T4 donor claim and T5 cross-owner. The primary clean positive (both_match), the clean wrong-owner negative and the T4/T5 full-attribution cells are unchanged.
- Why the split matters: on the paired remote stress run (`claude/f5-r3-256` result), 17 of F5 r2's 36 successes at .5 were recomputed-only.
- `success_of()` is pure and unit-tested: 4 new tests, 24 in total, all passing.
