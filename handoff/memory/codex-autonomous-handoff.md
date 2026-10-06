---
name: codex-autonomous-handoff
description: "2026-10-03 switch of Codex to autonomous handoff mode: why, what was changed (config, AGENTS.md, policy), and how the user starts it"
metadata:
  node_type: memory
  type: project
  originSessionId: 306009c7-f156-43a4-a6a7-e543c6058349
  modified: 2026-10-03T21:38:04.710Z
---

On 2026-10-03 the user said Codex was slow, kept waiting for approval and seemed "dumb" (not using its CV, cryptography and research ability); they want to hand the thesis fully to Codex and review only at milestones such as "proposed algorithm complete", with Codex as its own primary research source.

**Diagnosis:** tool approvals were already `never`/full access; the stalls came from project rules (one bounded task per user message, authorization JSON per user sentence, reviewer per package, user approval per run). Live web search was off (0 searches in the latest thread); compaction at 120k and tool output at 4k (set by Claude on 2026-10-02 for cost) shrank working memory. Codex's `goals` feature (`/goal`, auto-continuation across turns) was enabled but never used.

**User decisions:** open-source downloads allowed with license record, SHA-256 and a 30 GB cap; first "quality over token cost", then medium default with agent-chosen escalation (a sol-high switch was reverted). Codex cannot raise its own thread effort (`reasoning_effort_override` is under development), so AGENTS.md "Effort and tokens" authorizes fresh `gpt-6-astra` high/xhigh sub-agents for design, hard diagnosis, amendments and the M1 review; the spawn_agent tool only sets model/effort when AGENTS.md authorizes it. The desktop app can rewrite `model_reasoning_effort` from its UI picker.

**Changed:**
- `~/.codex/config.toml` (backup `config.toml.bak-20261003`): gpt-6-astra at effort medium (a later switch to gpt-6.1-sol high was reverted at the user's request: they pick model/effort themselves in the Codex UI, so do not change it in config unasked), compaction 160000, tool output 10000, `web_search = "live"`, `background_terminal_max_timeout = 10800000`, subagent effort medium, `[features] prevent_idle_sleep = true`. Supersedes the cost settings in [[codex-cost-and-harness-plan]].
- Main checkout (uncommitted) and worktree v5-study (commits `aa35cae`, `07a294f`; `c09eb75` reverted by `ffb026a`; Codex then moved the worktree to branch `codex/m1-latent-research`): new `AGENTS.md` (keep working, decide yourself, hard stops, milestones M1/M2, research standard, lightweight dev-run provenance under `.thesis-build/dev-runs/` + `experiments/dev-log.md`); `research/approval-policy.md` section "Autonomous handoff, 2026-10-03" with the verbatim Persian message; amendment pointers in `stop-rules.md`, `scope-guard.md`. STATE.md, continuation entry, and `thesis-runs/d916749c/NEW-THREAD.md` (fresh thread + `/goal` text).

**Why:** the user wants minimal involvement; integrity rules (held-out data, protected files, no fabricated verdicts, no paid/publication) were kept; push and new development images were allowed on 2026-10-05, see [[feedback-push-and-dev-images]].

**How to apply:** if asked about Codex progress, read STATE.md and `experiments/dev-log.md`; the next user touchpoint is the M1 package or the 2026-10-13 report. Confirmatory held-out runs still need the user's approval at M1. After a day of goal mode, check the token burn and whether Codex actually used web search and iterated.

Related: [[thesis-project-layout]], [[watermark-v5-two-tier]]
