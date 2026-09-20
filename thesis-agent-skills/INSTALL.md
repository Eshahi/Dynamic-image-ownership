# Installation

Prerequisites: Python 3.11 or 3.12, Git, PowerShell 7 on Windows or Bash on Linux/WSL2.
Use a dedicated virtual environment; nothing is globally installed by these helpers.
The build was exercised on Windows/Python 3.12. Other platforms require the included CI
matrix or equivalent local validation before production use.

From this bundle directory, prepare an environment using your chosen Python executable:

```text
python -m venv .venv
```

Activate `.venv` using your shell, then install the reviewed source and pinned dependencies:

```text
python -m pip install -r requirements-tested.txt
python -m pip install -r requirements-spec-kit.txt
python -m pip install .
```

Review package/source changes before installing. No remote install script is executed.
Spec Kit is pinned to commit `d4229c071c7ea3885b43e8a7739847300f618f13` (1.0.9.dev0).

## Skill profiles

Every invocation requires an explicit target. Default is preview; add `--execute`/`-Execute`
to copy. Existing files are preserved; `--force`/`-Force` permits overwrite after your backup.
The installer reports every file and embeds the reviewed runtime in each skill so profile
subsets can run independently. Keep Python dependencies installed in the worker environment.

PowerShell examples (targets are local project directories):

```powershell
./installers/install.ps1 -Profile controller -Target './local-hermes-skills' -DryRun
./installers/install.ps1 -Profile worker -Target './.agents/skills' -DryRun
./installers/install.ps1 -Profile reviewer -Target './reviewer-skills' -DryRun
```

Bash equivalents:

```bash
bash installers/install.sh --profile controller --target './local-hermes-skills' --dry-run
bash installers/install.sh --profile worker --target './.agents/skills' --dry-run
bash installers/install.sh --profile reviewer --target './reviewer-skills' --dry-run
```

Controller includes workflow-control and research-handoff. Worker includes all eight.
Reviewer includes literature-synthesis, results-analysis, evidence-audit and writing.
For actual user-wide `~/.codex/skills` or `~/.hermes/skills`, explicitly add `--allow-global`
(PowerShell `-AllowGlobal`) as well as execution. No global install was made during build.
Reviewer configuration is behavioral guidance, not an OS read-only sandbox.

## Spec Kit workflows

Install the runtime above, then preview or install into a dedicated thesis project:

```text
python installers/install_workflows.py --project "../thesis project"
python installers/install_workflows.py --project "../thesis project" --execute
python -m thesis_agents validate_bundle .
```

The helper copies the fixed `thesis-safe` step and calls the actual pinned CLI's
`specify workflow add` for both local packages. This validates the official schema.
There is no `specify workflow validate` subcommand in the pinned CLI, despite a mention
in the online documentation. The validator also calls upstream `validate_workflow`.
The full lifecycle uses the official Codex integration; configure Codex separately.
The smoke workflow requires no agent API, key, GPU or RunPod account.

Generate the reviewed execution plan from the immutable source guide before operational use:

```text
python skills/thesis-workflow-control/scripts/import_thesis_guide.py THESIS_GUIDE_OFFLINE.html guide-plan-38.json --profile thesis-38 --issues-output github-issue-seed-38.json
```

The result contains 38 acyclic execution tasks, five milestones, seven human gates and an exact
mapping back to all 58 source tasks. The GitHub issue seed is a local dry-run artifact; it does
not contact GitHub. Once a repository is explicitly scoped, use it to create one issue per task
and retain issue references in branches, commits, pull requests and evidence records.

Optional read-only overlay example is under `spec-kit/overlays`. Inspect it and use the
official overlay installation interface only when requested. The controller refuses active
overlay directories until edits are reviewed and flattened into a new local workflow version;
this prevents its gate allowlist from disagreeing with the composed workflow. Never replace
gates or add shell interpolation in an overlay.

## Local smoke test

Preview is read-only:

```text
python skills/thesis-workflow-control/scripts/spec_control.py --project "../thesis project" start thesis-smoke
```

Add `--execute` to create the synthetic workflow. It pauses at `evidence-review`. Use `status`
and `prepare-approval` with the returned exact run ID. After human review, supply a decision
JSON following `gate-decision.schema.json`, with the package's exact state hash and a short
expiry; resume first without `--execute`, then with it. Repeat at `compute-approval`.
Never reuse a decision for another gate/run. Test fixtures explicitly labeled synthetic are
not authorization for real workflows.

For unattended offline validation using only isolated synthetic decisions:

```text
python -m unittest discover -s tests -v
```

The tests exercise the actual Spec Kit smoke gates and complete research → review → design
→ compute gate → no-op → analysis → independent audit → completion.

## Hermes and secrets

Create a dedicated Hermes profile using its installed version's profile interface. Review and
merge `hermes/controller-profile/config.yaml`, load the companion system prompt, and install
the controller skill profile. Keep dangerous-command approval enabled. Pair the Telegram user
or set `TELEGRAM_ALLOWED_USERS` in Hermes's private environment file; never enable allow-all.
Do not commit Telegram credentials or API tokens. `RUNPOD_API_KEY`, if ever needed by a future
reviewed live provider, is read only from the environment. No sample credential values ship.

No cron job is registered. `hermes/examples/cron-prompt.md` remains disabled until explicitly
enabled through Hermes's supported cron interface. Watch-once is read-only; the delivery
cursor is updated by Hermes only after a successful message. Do not schedule gate resumption.

## Safety and current limits

Status/list/summarize/watch-once/prepare-approval, plan reduction, GitHub issue-seed generation,
provider capabilities and dry-run previews
are read-only. Research, design, analysis, audits and writing create local files. Workflow
start/resume and `--execute` change local state. Full lifecycle prompts invoke Codex and can
consume the user's agent subscription/API allocation. Real local experiments require approval
and can consume GPU resources. This package never creates issues/PRs, pushes or publishes.

Live RunPod creation is blocked: upstream removed deadline flags because its backend ignored
them. No unsafe fallback is enabled. Live artifact transfer and account integration therefore
remain unvalidated and unavailable. See BUILD_REPORT.md and compute runner execution guidance.

## Rollback

Back up target skills before `--force`. Installation receipts enumerate copied files and hashes.
To uninstall, compare each listed file to its receipt, preserve modified files, and remove only
explicitly reviewed individual files or move the selected skill directory to a named backup.
No recursive deletion helper is provided. Remove local workflows with Spec Kit's official
`workflow remove` after preserving run/evidence history. Deactivate or remove only the dedicated
virtual environment using your normal environment management tools. Never delete `.specify`
wholesale or remove unrelated user skills.
