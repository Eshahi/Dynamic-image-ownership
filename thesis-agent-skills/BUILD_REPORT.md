# Build report

Built and validated on 2026-09-20. This is a tested local/mock thesis automation bundle,
**not a validated live-cloud production deployment**. Live RunPod creation and transfer are
unavailable for the documented upstream deadline reason below. No cloud workload was launched.

## What was built

- Eight discoverable Agent Skills with valid YAML frontmatter, automatic invocation enabled,
  explicit input/output and authorization boundaries, deterministic entrypoints, and embedded
  copies of the reviewed shared runtime so each skill can be moved independently.
- Nine strict Draft 2020-12 JSON Schemas: approval, execution, run, paper, evidence, research
  response, experiment, claims and workflow gate decision.
- A literal-only importer for this offline guide revision. It recovered **58 tasks, 10 phases**,
  original titles/IDs, dependency graph, gates, evidence requirements and original task/contract
  fields. No unsupported fields or dependency cycles were reported. HTML was never executed.
- A deterministic **38-task execution profile** covering every source task exactly once, with
  five milestones, an acyclic dependency graph, deduplicated milestone checks, seven human gates
  and local dry-run GitHub issue drafts. The 58-task import remains immutable provenance.
- An official-schema `thesis-lifecycle` v1.1.0 workflow with 21 steps and 7 human gates, plus the
  8-step/2-gate `thesis-smoke`. A fixed non-shell `thesis-safe` extension executes synthetic
  smoke stages inside Spec Kit; it is not a separate state engine.
- Constitution, read-only overlay example, deterministic Telegram transport,
  controller/worker/reviewer installers, reproducible packaging and checksums.
- Local execution, mock provider lifecycle/recovery, source/evidence validation, seed-aware
  analysis, audit classification and conservative writing/finalization guards.

## Final directory tree

The complete file tree is in DIRECTORY_TREE.txt; bundle-manifest.json inventories every
payload file and SHA-256. Runtime files are repeated under each skill for standalone use.

```text
thesis-agent-skills/
├── .github/workflows/ci.yml
├── skills/
│   ├── thesis-workflow-control/
│   ├── thesis-research-handoff/
│   ├── thesis-literature-synthesis/
│   ├── thesis-experiment-design/
│   ├── thesis-compute-runner/
│   ├── thesis-results-analysis/
│   ├── thesis-evidence-audit/
│   └── thesis-writing/
│       Each: SKILL.md, agents/openai.yaml, scripts/entrypoints,
│             scripts/_runtime/thesis_agents/{modules,schemas}
├── src/thesis_agents/
│   ├── common.py, control.py, guide.py, plan.py, research.py, design.py
│   ├── compute.py, runpod.py, analysis.py, audit.py, writing.py, telegram_bridge.py
│   ├── smoke.py, validate_bundle.py, __init__.py, __main__.py
│   └── schemas/ (nine strict schemas)
├── spec-kit/
│   ├── workflows/{thesis-lifecycle,thesis-smoke}/workflow.yml
│   ├── steps/thesis-safe/{step.yml,__init__.py}
│   ├── templates/constitution.md
│   └── overlays/read-only-review.yml
├── telegram/{README.md,.env.example}
├── installers/{install.ps1,install.sh,install.py,install_workflows.py}
├── tests/{test_contracts.py,test_forward_compute.py,test_forward_evidence.py,
│          test_forward_workflow.py,test_telegram_bridge.py,validation-results.json}
├── fixtures/{guide-tasks.json,guide-plan-38.json,github-issue-seed-38.json,
│             experiment-spec.json,execution-manifest.json,results.json,
│             nvidia-smi.csv,scripts/noop.py,README.md}
├── tools/{build_assets.py,build_schemas.py,run_validation.py,package.py}
├── pyproject.toml, requirements-tested.txt, requirements-spec-kit.txt
├── INSTALL.md, BUILD_REPORT.md, RESEARCH_NOTES.md, THIRD_PARTY_NOTICES.md
├── DIRECTORY_TREE.txt, bundle-manifest.json, CHECKSUMS.sha256
└── No virtual environments, caches, credentials, models or experiment artifacts

../dist/thesis-agent-skills.zip
../dist/thesis-agent-skills.zip.sha256
```

## Design and reuse decisions

Spec Kit owns run state and resumability. Controller helpers invoke its CLI with fixed argument
arrays and preserve run IDs. A narrow standard-library Telegram client transports notifications
and exact commands but is not a scheduler, agent or state engine. The current upstream shell step
uses shell execution, so no shipped workflow uses it. Full lifecycle
stages use the official Codex prompt integration and explicit human gates. Writer stages are
sequential; the independent audit prompt can delegate to a distinct read-focused subagent.

Known allowlisted gates accept approve/reject, with reject aborting. The adapter refuses revise,
retry and stop as gate verdicts because this workflow does not implement those meanings. Its
`stop` operation means an explicit reject at a paused gate. It does not pretend the current
Spec Kit CLI can stop a running process or roll back an earlier stage. Revision starts a newly
reviewed attempt while retaining previous evidence.

Watch-once is read-only and emits nothing for the same meaningful-state fingerprint. The bridge
stores its cursor under ignored project-local state; only successful delivery advances a workflow
cursor. Incoming commands require exact allowlisted private user/chat IDs and exact run/step IDs.
Free-form text is rejected. Human approval is never inferred from notification delivery. Execute
and install default to preview. Remote/local target changes require an updated manifest and approval.

JSON is used as a valid YAML 1.2 serialization for generated experiment and workflow files.
Deterministic helpers use the standard library except pinned PyYAML and jsonschema. Optional
pandas/scipy/matplotlib, MLflow and DVC are unnecessary for the supported analysis subset.

The reduced execution plan is derived, never hand-edited. It preserves all source steps, checks,
failure modes, inputs and outputs under `source_task_ids`. Two unsafe quotient merges were split
to preserve A2a -> A3 -> A2b and C3a -> C2 -> C3b. Primary result QC depends directly on the
evaluation and ablation outputs; the representative rerun moved to E4 as confirmation. Task-level
phase gates were removed while the seven distinct authorization/evidence gates remain.

No upstream implementation or template is vendored. The source and skill inventory, reuse
decisions and official documentation links are in RESEARCH_NOTES.md. Attribution, inspected
repository pins, licenses and reused-files/modifications records are in THIRD_PARTY_NOTICES.md.

## Validations performed

- **51 automated tests passed**, zero failures, errors or skips, on Windows with Python 3.12.14.
  The exact test result is recorded in tests/validation-results.json.
- All **eight skills passed the provided Codex skill-creator quick_validate.py**, and the bundle
  validator checked frontmatter, naming, UI policy, references and unfinished skill scaffolds.
- Both workflow packages passed the pinned upstream validator and were actually installed
  through the pinned CLI's `workflow add` inside isolated temporary projects.
- The smoke workflow ran through research, evidence gate, design, compute gate, synthetic
  execution, analysis, audit and completion using the real pinned engine. Tests supplied
  clearly identified synthetic decisions only. No decision fixture authorizes real work.
- Every user-facing deterministic helper, installer and build tool ran with `--help` or a safe
  fixture. The actual guide importer and GPU fixture parser were exercised. A reviewed CPU-only
  fixture ran through the actual local subprocess runner with exact clean Git provenance.
- Live local GPU discovery was verified against the RTX 5070 Ti. The sanitized Windows
  subprocess environment preserves the non-secret Program Files roots required by NVML.
- PowerShell installer dry-run was exercised, with an explicit path containing spaces.
  Python installer tests exercised copy plans, actual controller installation, embedded helper
  execution and preservation of modified skills. No global skill installation occurred.
- Tests checked Windows/POSIX relative paths, traversal/injection rejection, unknown fields,
  approval scope/hash/expiry/budget, no-approval/wrong-run refusal, mock create/status/stop/delete,
  exact Pod identity, omitted artifacts, checksum tampering, recovery and secret redaction.
- Reduction tests checked exact one-time coverage of all 58 source tasks, 38-task acyclicity,
  milestone counts, corrected analysis dependencies and complete dry-run GitHub issue drafts.
- Evidence tests checked conflicting sources, duplicated/missing citation data, missing access
  dates, unmarked inferences, failed/omitted runs, deterministic bootstrap/figure output, all five
  audit classifications, changed table/script/spec hashes, self-review rejection, missing-evidence
  draft markers and finalization refusal.
- Python source parsed with the Python 3.11 grammar; this is syntax compatibility, not a 3.11
  execution claim. All nine JSON Schema definitions passed the schema validator.
- Telegram tests covered missing/malformed configuration, safe ID discovery, exact private
  user/chat authorization, free-form command rejection, gate binding, unauthorized-update
  consumption, and the rule that notification cursors advance only after successful delivery.
  No live Telegram call was made.
- The package builder verifies ZIP CRC and every archived file hash against the local payload.
  CHECKSUMS.sha256 includes bundle-manifest.json and excludes itself. The ZIP has an external
  SHA-256 file, avoiding self-referential checksum claims.
- The ZIP was extracted into an isolated path containing spaces. All extracted skill entrypoints
  ran with --help, and the extracted bundle passed skill/workflow validation. Payload checksums,
  excluded-file scan, empty-directory check and a scan for current environment-secret values passed.

Independent agents authored forward tests for all eight requested scenarios. The evidence
agent completed its run and found two defects, both fixed: fractional seeds were truncated,
and audit script/spec hashes were not checked. The compute/workflow agents wrote their tests
but hit an account usage limit before finishing their reports; the main agent ran and verified
their tests. Workflow testing also exposed and fixed Windows NUL stdin being treated as a TTY:
the controller now supplies an empty pipe so unattended gates pause instead of rejecting on EOF.

## Exact versions and commits

| Component | Tested/inspected version |
|---|---|
| Python execution | 3.12.14 |
| PowerShell | 7.6.5 |
| Git | 2.53.0.windows.3 |
| Spec Kit | 1.0.9.dev0, d4229c071c7ea3885b43e8a7739847300f618f13 |
| Telegram Bot API | Official HTTP API; docs accessed 2026-09-20 |
| RunPod CLI reference | 4351fca9ec454b1bdc8572aaad5d3e5a61ead0fa |
| JSON Schema validator | jsonschema 4.26.0 |
| YAML parser | PyYAML 6.0.3 |
| Package build backend | setuptools 82.0.1 |
| CI checkout action | v4.2.2, 11bd71901bbe5b1630ceea73d27597364c9af683 |
| CI setup-python action | v5.6.0, a26af69be951a213d495a4c3e4e4022e16d87065 |

The complete resolved Python dependency versions are in requirements-tested.txt. CI action
tag hashes were checked against their official repositories; the CI matrix has not been run.

## Known limitations and unvalidated components

1. **Live RunPod provisioning and artifact transfer are blocked.** The current upstream removed
   shutdown deadline flags because the backend ignored them and continued billing. This is
   documented in [RunPod PR 330](https://github.com/runpod/runpodctl/pull/330). A tested provider
   deadline, immutable worker image, artifact transport and ambiguous-create reconciliation are
   required before live enablement. The mock lifecycle and REST status/stop/delete adapter are
   implemented; no live RunPod account/API operation was tested. This prevents claiming the
   entire originally requested live execution system is production-ready.
2. Python 3.11, native Linux, WSL2, RunPod images and the Bash installer were not executed here.
   WSL is not installed on this host. Portable code and a pinned CI matrix are provided; runtime
   support on those systems remains a validation task. The Bash wrapper is small but untested.
3. Live Telegram delivery and polling were not exercised because no credential was supplied to
   the build. The implemented deployment is a local long-polling process; serverless/webhook
   operation remains optional and unvalidated. Do not run another poller or webhook for the same bot.
4. The full lifecycle validates structurally but was not run against real thesis inputs or a live
   Codex provider. Prompt completion is not proof of scientific success; gates must inspect actual
   evidence. Interrupted helper writes may need a fresh reviewed attempt directory; evidence is
   preserved rather than automatically overwritten.
5. Telegram gate records are authenticated operationally by exact numeric private user/chat IDs,
   the bot token and filesystem ownership, not cryptographic signatures. A malicious process with
   those credentials or write access to approvals/code can forge records. Use protected process
   secrets, approval storage and OS isolation as appropriate.
6. Source/schema validation cannot establish that a plausible paper or claim is true. A human or
   independent reviewer must inspect sources and check entailment. Automatic 'verified' means
   traceability checks passed. Input hashes require original artifacts; unavailable inputs produce
   blocking findings. Moving analysis inputs requires deliberate provenance-aware relocation.
7. Analysis supports one prespecified comparison, descriptive statistics and paired bootstrap;
   it does not implement general hypothesis tests, multiple-comparison families, power calculation
   or mixed-effects models. It refuses unsupported schema choices instead of inventing significance.
   Repeated within-seed observations require a reviewed aggregation step.
8. Local scripts must not launch detached descendants. The runner bounds its direct child and
   is not a complete process-tree supervisor or sandbox. Actual GPU execution was not performed.
9. The importer is intentionally tied to the supplied minified structured-data declarations; a
   different guide build can require a reviewed parser update. Unsupported input is rejected,
   never evaluated. Original task content is preserved as supplied, not endorsed as fact.
10. Markdown/LaTeX drafting is supported; Word formatting, bibliography truth, LaTeX compilation
    and university submission rules are outside the deterministic writer's validation.
11. GitHub issue drafts and governance metadata are generated locally, but no live issue, branch,
    commit, push or pull request integration is enabled until an explicit repository is supplied.

## Assumptions and decisions still needed

The workspace was used as OUTPUT_DIR. The original HTML and README were left unchanged.
The actual proposal, thesis source, datasets and experiment implementation were not supplied;
only the guide and explicitly synthetic infrastructure fixtures were used.

Before operational use, select the target thesis project and installation profile/directories,
provide missing thesis inputs, ratify scope/constitution, configure and live-test the Telegram
bridge, and supply explicit human decisions at gates. Real budgets, target hardware, dataset licenses,
statistical plans and publication decisions remain human choices. Live RunPod enablement must
wait for a separately reviewed enforceable spending boundary; no unsafe default was selected.
