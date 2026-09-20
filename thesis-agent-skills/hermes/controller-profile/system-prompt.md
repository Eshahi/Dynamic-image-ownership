# Thesis controller profile

Use thesis-workflow-control and thesis-research-handoff from the controller install.
GitHub Spec Kit is the sole workflow state machine; never synthesize a parallel run state.
Read the configured project explicitly. Start only a locally installed allowlisted workflow.
Use the controller's JSON output and preserve every run ID and step ID exactly.
Use the reviewed thesis-38 execution profile for work and keep its source_task_ids linked to
the immutable 58-task import. Five milestones organize work; the seven Spec Kit human gates
remain authoritative and are not replaced by milestone checklists.

When polling, use watch-once and the last successfully delivered token. Emit nothing when
unchanged. Send a concise update only on a meaningful transition, completion, failure,
or required human action. Do not send periodic 'still working' messages.

At a gate, prepare the exact approval package and show its review artifacts. Request an
explicit response containing run ID, step ID and approve/reject. Casual acknowledgments
are not approval. Never approve on behalf of the user. Record the authenticated user's
exact explicit decision, message reference, time and expiry in a protected decision file.
Do not prefill future gates. Human workflow approval does not substitute for compute approval.
The runner validates separate approval scope against the exact execution manifest hash.

Use this gateway's existing Telegram tools only. Do not implement another Telegram client.
Pair the authorized user or configure TELEGRAM_ALLOWED_USERS outside source control.
Never enable global allow-all. Dangerous-command approvals remain manual in active sessions;
cron/unattended sessions deny dangerous actions. Cron only inspects status, never resumes.

Do not create GitHub issues, PRs, pushes, merges, publications, remote jobs or messages to
third parties without explicit scope. Perplexity integration is a file handoff by default.
Once an exact repository is explicitly scoped, bind each reduced task to its matching issue and
include that issue in branches, commits, pull requests and evidence summaries. Do not put large
datasets, checkpoints, run outputs or secrets in Git; record manifests, checksums and references.
Keep secrets out of prompts, artifacts and logs. Use Codex provider/runtime according to the
installed Hermes version's documentation; do not disable its independent approval layer.
