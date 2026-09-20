# Synthetic fixture boundary

All fixtures except the three guide-plan files are infrastructure examples, not thesis evidence.
guide-tasks.json contains the actual 58 tasks and 10 phases imported from the user-supplied
offline guide, including original task/contract data and the source HTML hash. Its bibliography
or task instructions do not mean sources or results have been verified by this package.

guide-plan-38.json is the deterministic reviewed execution view. It maps every source task
exactly once into 38 acyclic tasks, five milestones and seven human gates while retaining
source_task_ids, checks, steps, failures, inputs and outputs. github-issue-seed-38.json contains
38 local dry-run issue drafts and governance metadata; it does not prove that GitHub issues exist
or authorize any repository mutation.

experiment-spec.json and execution-manifest.json describe a synthetic no-op. All-zero Git and
script hashes intentionally make the illustrative manifest non-executable as shipped. The
tests initialize isolated Git repositories and bind the actual reviewed fixture script hash
and real fixture commit before exercising execution. No approval fixture is valid for real work.

scripts/noop.py is a functional CPU-only entrypoint with --manifest and --output-dir; it emits
zero-valued synthetic metric records. nvidia-smi.csv is simulated output, not a measurement of
this laptop. Conflicting-paper fixtures are generated inside isolated tests and use
example.invalid; they are not genuine papers or citations.
