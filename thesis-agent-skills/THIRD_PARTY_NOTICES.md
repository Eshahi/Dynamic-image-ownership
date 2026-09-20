# Upstream provenance and attribution

All shipped application source, skill prose, templates and workflow definitions were authored
for this bundle. No upstream implementation, skill, template, model or dataset is vendored.
API/schema compatibility does not imply copying the implementation. The guide task JSON is
derived from the user-supplied HTML, retaining original task content and source checksum;
its redistribution rights are not inferred beyond the user's requested package.

| Component | Repository/version inspected | License | Reused files | Local modifications |
|---|---|---|---|---|
| GitHub Spec Kit | github/spec-kit @ d4229c071c7ea3885b43e8a7739847300f618f13; 1.0.9.dev0 | MIT, GitHub Inc. | None vendored; CLI and workflow validator used as dependency | None |
| Hermes Agent | NousResearch/hermes-agent @ 8f1542422b6806a20f8248d582db2f47b5cb34cc | MIT (repository) | None; evaluated then removed from the runtime path | None |
| Telegram Bot API | Official HTTP API, accessed 2026-09-20 | Service API; no client source vendored | None; protocol documentation consulted | Standard-library HTTP adapter authored locally |
| RunPod CLI | runpod/runpodctl @ 4351fca9ec454b1bdc8572aaad5d3e5a61ead0fa | GPL-3.0 (repository LICENSE) | None; source and CLI reference inspected only | None |
| RunPod official skills | runpod/runpod-plugins-official, runpodctl skill 1.2.0 documentation snapshot | Apache-2.0 as declared in skill | None; inventory/reference only | None |
| Agent Skills specification | agentskills.io/specification, accessed 2026-09-19 | Specification reference; not vendored | None | None |
| Local skill-creator guidance and validator | Available Codex system skill, accessed 2026-09-19 | Not redistributed | Validator executed externally; no files copied | None |

Pinned installed dependencies are listed in requirements-tested.txt. PyYAML and jsonschema
are runtime dependencies rather than bundled source. Their distributions retain their own
license notices. Spec Kit source installation likewise retains upstream notices.

OpenColab was not copied, installed or used. No Prefect, Airflow, dstack, email/SMS integration,
MLflow or DVC dependency is introduced. The Telegram adapter uses Python's standard library and
adds no client package.
