# C2 candidate-code review, not issue closure

Recorded 2026-09-26 by author `/root`, from actual independent actor
`/root/b3_intake_review`, under project AGENTS.md/research approval-policy.
Reviewer and author differ. Issue #16 remains open, zero real development cases.

Initial exact author commit `0dacbb9bfed42f5c8cdc3b8454d5a3349d3e5ac2` had a
reproduced cache provenance blocker: a synthetic basis vector could be replaced
with another valid unit vector and its colocated checksum updated while retaining
the image/model identity. Cache reuse accepted it without encoder agreement,
changing q from110d to2509 and changing Ws. Eleven synthetic WSL tests passed but
did not cover that extraction-path substitution; link coverage was also missing.

Exact repair `07be8be37d79ac56f6061b7fefce4fdbe4e68c31` was independently
re-reviewed. Every hit recomputes fresh encoder features, compares exact values,
rejects mismatch without overwriting, and returns the fresh vector. The reviewer
verified the coherent substitution regression (three encoder calls, unchanged
tampered bytes), real linked-directory rejection, all13 WSL synthetic tests and
Windows9passes/4expected host/dependency skips, plus whitespace checks.

Actual verdict: cache finding resolved; no remaining blocker to this bounded
candidate-code repair acceptance. Arithmetic/packing/norm/tie/owner protocol
comparisons conform to the A5 and independent B2/C3a references. The cache is
comparison storage, not acceleration or independent provenance. Failed79f238e
test fixture restoration evidence remains documented and repaired.

This review did not load a model or access scientific images. Configuration,
worker and launcher preparation at lateraf28c07 are outside this core review and
require their own exact review. No #16 closure, scientific compute, method/result
acceptance, rights clearance, human verdict or lifecycle advancement is granted.
