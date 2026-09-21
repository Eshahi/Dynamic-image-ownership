# Official capability review (2026-09-19)

Implementation followed review of these primary sources and the checked-out pinned source.

- [Spec Kit workflow reference](https://github.github.com/spec-kit/reference/workflows.html):
  use official engine state, JSON CLI status and bound gate verdict inputs; no substitute engine.
- [Pinned Spec Kit source](https://github.com/github/spec-kit/tree/d4229c071c7ea3885b43e8a7739847300f618f13):
  reviewed workflow definitions, validator, run/resume/status payloads, custom step loader,
  gate semantics, prompt integration and shell executor. The shell executor uses a shell,
  so this bundle uses prompt/gate/slot plus one fixed Python extension for smoke operations.
- [Codex Remote connections](https://learn.chatgpt.com/docs/remote-connections): the connected
  Codex task already supports follow-up instructions, action approvals, review and attention
  notifications from mobile. The host must remain awake, online and signed in. Remote is treated
  as an interaction surface, while Spec Kit remains the workflow state owner.
- Hermes and a custom Telegram bridge were evaluated for messaging and approval. Both were removed
  from the project path because Codex Remote supplies the required user channel without another
  agent runtime, bot credential, polling process or delivery-state store.
- [RunPod REST create](https://docs.runpod.io/api-reference/pods/POST/pods),
  [official CLI](https://github.com/runpod/runpodctl),
  [timer removal](https://github.com/runpod/runpodctl/pull/330):
  confirmed current source lacks enforced shutdown timers. Live creation is blocked rather than
  trusting stale guidance or representing a client timeout as a service spending guarantee.
- [Agent Skills format](https://agentskills.io/specification): eight separately discoverable
  directories, YAML frontmatter, optional scripts/references and implicit invocation enabled.

## Existing skill inventory and reuse decision

The local trusted catalog includes skill-creator, PDF, documents, spreadsheets, presentations,
computer-use and openai-docs. Reuse skill-creator for format/validation. Do not copy document
renderers into a Markdown/LaTeX evidence package. External research capabilities may gather
papers or guide general writing, but they do not enforce this project's task IDs,
approval/artifact schemas or evidence gates. Import inspected evidence into these contracts.
No unreviewed skill is auto-installed.

RunPod's official runpodctl skill was inspected as a capability reference, not copied. Its
deadline advice is stale relative to PR 330 and the current CLI source; this is why blindly
reusing that instruction would violate this bundle's spending requirement. OpenAI's broader
research skills are domain-specific and do not provide a ready-made thesis lifecycle contract.

Custom additions are limited to missing thesis contracts: literal-guide import, file exchange,
source/claim validation, scoped approvals, deterministic analysis, exact-run controller adapter
and fixed non-shell smoke stages. Spec Kit remains the only workflow engine. The authenticated
Codex task carries human messages but stores no separate project delivery state.
