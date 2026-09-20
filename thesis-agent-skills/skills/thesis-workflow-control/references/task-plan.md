# Reviewed task execution profile

Use `source-58` only to preserve the exact task and dependency data extracted from the offline
guide. Use `thesis-38` for execution, research handoffs and future GitHub issue creation.

The reduction is deterministic and covers every source task exactly once. It uses five milestones
with task counts 7, 6, 11, 9 and 5. Detailed steps, checks, failure modes, inputs and outputs remain
attached to each reduced task with `source_task_ids` provenance.

The important ordering corrections are:

- Claims/scope and traceability are split around I/O/threat-model work: A2a -> A3 -> A2b.
- Owner protocol, semantic key and instance fusion remain ordered C3a -> C2 -> C3b.
- Result QC D6 depends on D2, D3, D4, D5 and D9. The representative rerun is moved to E4 and
  confirms results rather than blocking primary analysis.

Task-level copies of phase gates are removed. Milestones retain deduplicated acceptance checks,
while the Spec Kit lifecycle retains seven human gates: scope, evidence, plan, compute, results,
claims and chapter finalization. Do not turn milestone checks into approvals or remove the compute
gate merely to reduce ceremony.

Generate the execution plan and local issue drafts with:

```text
python scripts/import_thesis_guide.py THESIS_GUIDE_OFFLINE.html guide-plan-38.json --profile thesis-38 --issues-output github-issue-seed-38.json
```

The issue seed is dry-run data. Creating issues, branches, commits, pushes, pull requests or merges
requires an explicitly scoped repository. Large datasets, checkpoints and run outputs stay outside
Git; issues and commits record manifests, checksums and durable references.
