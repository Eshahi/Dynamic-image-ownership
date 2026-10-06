---
name: f5-encoder-amplified-latent
description: "2026-10-05 family 5 (encoder-amplified latent carrier) by Claude passes M1a: idea, setting, gate numbers, T4/T5, remaining bottleneck (q drift), open points"
metadata:
  node_type: memory
  type: project
  originSessionId: 306009c7-f156-43a4-a6a7-e543c6058349
  modified: 2026-10-05T22:11:26.049Z
---

On 2026-10-05 the user asked for a game-changing idea; Claude designed family 5.

**Idea:** Zhao et al. removal bound (arXiv 2306.01953 Thm 4.3) depends on the attacker encoder's local Lipschitz constant L along the mark. SD1.5 VAE encoder is non-robust (PhotoGuard), so write the robust tier by gradient ascent through that encoder toward a keyed latent pattern (DCT radius 4-32 on the 64x64 latent, ~2-16 c/i) and read it from the suspect's VAE latent. Probe: 20-27x more latent displacement than decoder rendering (A-C style) at equal PSNR.

**Codec:** `scripts/f5_latent_codec.py` = v5 r3 except robust tier; v5 study profile (q, H identical to v5). Gate `scripts/f5_gate.py`; T4 `f5_t4.py`; T5 via `f4_t5.py`; diagnostic `f5_binding_diagnostic.py`. WT branch `codex/m1-latent-research`, report commit `63b8e99`, `research/f5-encoder-amplified-latent.md`.

**Results (one full gate at pre-declared 52 dB):** paired C1 semantic .1/.2/.4 = 29/25/21 vs v5 27/18/2; PSNR mean 44.7, LPIPS mean .0172 (max .051 on sky 147498 vs v5 max .038); 12/12 both_match; zero negatives. T4 0/20 false attribution and key not even delivered by copy-paste (0/20 vs v5 18/20); T5 0/66. Zero carrier failures; all failures are q drift (CLIP code), 6/9 at .4 on non-retained content.

**Revision 2 (same day, user asked for the binding experiment):** soft binding (ML angle from continuous CLIP projections, same radii) + seven-view CLIP E. Gate `20261005-0640-f5-gate-soft-views7` (`--psnr 52 --binding soft --semantic-views 7`): paired 29/28/23 vs v5 27/18/2; all C1 .2 35/35, .4 29/34; T4 0/20; T5 0/66; adopted under a pre-declared rule. Report commit `3abbb5f`.

**User verdict:** 2026-10-05 "کیفیت بصری قبوله" — F5 visual quality accepted (on revision-1 images, 52 dB).

**Why:** first family to pass M1a cleanly (not post-hoc), supersedes F4.

**How to apply:** current candidate is F5 revision 2; next stage is M1b (freeze, tests, one review, held-out manifest). Must be accepted at M1: VAE encoder + 7 CLIP passes as detector side info. Out of scope: other regenerators/pre-filters untested.

**Handoff (2026-10-05):** the user plans to continue F5 research with a new Claude agent (same model/effort); its prompt is MAIN `thesis-runs/d916749c/CLAUDE-AGENT-PROMPT.md` (own worktree, branch `claude/f5-research`, harder dev stress grid first, stop at plateau + M1b).

**Agent session (2026-10-05, branch `claude/f5-research`, HEAD `0cfb528`, pushed):** stress grid (.4/.5/.6, 5 seeds) F5 r2 = 49/58, 37/58, 10/57. Killed H1 (band/matched filter, n=4) and H4 (thresholds); H3 mask only compared at equal PSNR (not a valid kill); H2 and longer codes not tried. The plateau was declared after about an hour. M1b spec, config, 7 tests (verified pass) and a review PASS exist, but there is no executable F5 confirmatory runner and the cohort choice (COCO512) is open. Claude's review recorded in MAIN `STATE.md`.

**Opus 5 worker evening (2026-10-05, quota ran out 21:30 UTC):** branches `claude/f5-gpu` (queue + H3), `claude/f5-ideas` (15 proposals), `claude/f5-m1b` (runner, 20 tests pass, cohort memo for user: COCO512 300 vs all-domain 3,900). Supervisor analysis: H3 texture mask killed at equal T3 (masking is anti-robust: denoiser re-synthesises texture). CPU binding-ceiling test: ideal CLIP angle gives .4 55/58, .5 44/58, .6 14/57 vs production 49/37/10; random codes reach it only at ~256 bits, 32-bit draws vary 33-50 at .4. So binding loss = short 32-bit sketch, not CLIP drift; ECC on 32 bits cannot help; lever = 128-256-bit sketch decoupled from owner detection (recomputed score is L-independent). .6 is carrier-limited.

Related: [[f4-chroma-carrier]], [[m1-regeneration-gate]], [[feedback-three-threat-scope]], [[watermark-v5-two-tier]]

**r3-256 test (2026-10-06, branch `claude/f5-r3-256` 0024505, push pending: a GitHub TLS error):** this was a 256-bit sketch with antipodal chips and soft binding.
- Results, remote and paired: r2 49/36/10 against r3 39/26/2. Killed.
- Key diagnosis: 17 of r2's 36 .5 successes are recomputed-only (the content is assumed, never compared). Under strict checking r2 is 19 and r3 26 at .5.
- The carrier cannot deliver 256 reliable bits at 52 dB, so the ceiling analysis's noiseless-bit assumption failed.

**User decision (2026-10-06):** move F5 r2 to M1b with the narrow **COCO512** cohort (300 MS-COCO test groups). The algorithm search is closed for this stage.
- Runner v2 is at `claude/f5-m1b` 471b7c5. It fixed a v1 bug: T3 success counted only both_match, which regeneration breaks.
- T3 now uses semantic-channel success with a checked/assumed split.
- Next: GPU smoke on 2 dev images, then the user approves the exact manifest, then a single held-out run.
