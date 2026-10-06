---
name: m1-regeneration-gate
description: "2026-10-04 review of Codex's first autonomous M1 day: candidates A/A-C/B/C, the M1a regeneration gate the user approved, A-C gate numbers, and where results live"
metadata:
  node_type: memory
  type: project
  originSessionId: 306009c7-f156-43a4-a6a7-e543c6058349
  modified: 2026-10-04T20:51:59.391Z
---

On 2026-10-04 the user thought Codex's algorithm "worked" after one autonomous day that exhausted the Codex quota, and asked Claude to check. It had not: the main threat (SD1.5 img2img regeneration at .1/.2) was not solved.

**Facts (verified from raw rows):**
- A hybrid source-bypass (latent-optimized residual read by the v5 DCT detector): C1 semantic 12/12 VAE, 36/36 at .05, 3/33 at .1, 0/33 at .2/.4, far below v5.
- A-C terminal candidate (VAE posterior-mode reader, continuous CLIP + pHash templates, public OwnerID, threshold 4, 35.2 dB cap): Claude ran Codex's unchanged assessor `scripts/m1_assess_terminal_e2e.py` (manifest `research/m1-ac-t3-claude-dev.json`, outputs MAIN `.thesis-build/dev-runs/20261004-2100-ac-t3-claude/`). C1 semantic 27/9/1 of 33 at .1/.2/.4; paired with v5 r3: 22 vs 25 at .1, 9 vs 17 at .2. 0 of 1113 negative calls detected (max null 3.40). Fails M1a.
- Families B (Gaussian Shading on photos) and C (progressive latent) were closed by Codex.
- Day cost: ~274M input tokens (97% cached), 1.7M output; 83 M1 scripts (~20k lines) mostly execution/audit tooling (broker, private pipe, authority verifier, bit-exact CUDA re-audits).

**User decision ("هر دو رو انجام بده"):** run the A-C test and add a gate. `AGENTS.md` now has M1a (beat v5 at .1 and .2 on paired development identities, strict clean quality, zero negatives) before M1b packaging; no new infrastructure until M1a passes; short-lived sub-agents; no bit-exact re-audits of dev runs. Recorded in `research/approval-policy.md`. WT branch `codex/m1-latent-research`, commits `1918b18` (manifest), `6bc325d` (gate + report). STATE.md rewritten readable; Codex's old STATE in `thesis-runs/d916749c/archive/STATE-codex-20261004-1247utc.md`.

**Why:** the user wants results, not machinery; the quota is the binding constraint.

**How to apply:** judge any "it works" claim by the M1a table in STATE.md; a fourth design family must beat v5 at .2 or the honest negative exit applies. Running a candidate through the assessor shards costs ~1 GPU-minute per shard plus ~1 min CPU re-audit.

Related: [[codex-autonomous-handoff]], [[watermark-v5-two-tier]], [[thesis-project-layout]]
