---
name: thesis-evidence-audit
description: "Independently classify thesis claims against source ledgers, experiment manifests and analysis provenance, separating blocking findings from warnings."
---

# thesis-evidence-audit

Use for an independent evidence review, not evidence repair. Require claim inventory, inspected-source root, paper cards, evidence ledger, all expected run IDs, run artifacts and analysis outputs. Missing inputs are findings, not permission to reconstruct evidence. Use a reviewer identity different from the claims' author; do not approve your own work.

Check claim semantics against inspected source passages and scientific scope in addition to running the helper. Automated 'verified' means traceability checks passed, not that a string matcher has proved entailment. Map every claim to source entries, exact run manifests, tables or figures; inspect supporting and contradicting entries. The five classifications are verified, partially supported, unsupported, conflicting and unverifiable.

Validate source existence/inspection checksums; run command, seeds, Git commit/dirty status, environment, dataset version and approval references; input/output hashes; analysis script/spec hashes and parameters; expected run coverage including failures. Look for selective successful seeds, omitted failed experiments, mismatched tables and figures, unsupported generalizations and post-hoc criteria. Input hashes need the original dataset/artifact root, so absent data must remain an unresolved verification item.

Report blocking and non-blocking findings separately. Never silently repair a broken hash, invent a missing citation, edit a source artifact, or grant human acceptance. Forward the exact audit and unresolved items to the human gate. Keep read-focused review outputs in their own directory so concurrent reviewers never write the same files.

Authorization: read evidence and write a separate requested audit; source changes, final acceptance and external publication are out of scope.

## Input/output contract

Inputs must match the strict JSON schemas in `scripts/_runtime/thesis_agents/schemas` after installation, or the bundle's `src/thesis_agents/schemas` during development. audits/<audit-id>/{audit-report.md,findings.json,claim-matrix.csv,reproducibility-checklist.md,unresolved-items.md}.

Use `python scripts/audit_evidence.py --help` for the actual argument contract. Errors return nonzero JSON diagnostics. Do not infer success from artifact filenames alone.
