# A3 independent technical review

Date: 2026-09-22. Issue: #3. Source tasks: `contract-2`, `contract-3`.
Author: primary Codex task. Independent reviewer: `/root/a3_review`, a separate read-focused subagent with no write or experiment authority. Scope: the exact three A3 artifacts against AGENTS.md, approval policy, the A3 task definition, proposal-derived claims, and scope.

## Outcome

**Accept as a specification; no blocking findings.** The reviewer checked detector/evaluator knowledge, public identifiers versus secrets, route separation, latent/image-domain compatibility obligations, source-backed 8x8 DCT, scientific TBDs, attack families/exclusions, and required controls. No invented scientific parameter was found.

Two nonblocking suggestions were applied and re-reviewed: include public-method re-embedding T6 in the owner-attribution scenario mapping, and explicitly allow absent scores/flags for invalid/unsupported detection outcomes. The reviewer also checked the explicit `image_patterns` and `image_coefficients` function signatures in the final version.

## Reviewed content identities

SHA-256 of UTF-8 file content with LF line endings (normalize CRLF to LF when checking a Windows checkout):

| Artifact | SHA-256 |
| --- | --- |
| `research/io-spec.md` | `9c257f7bd5101c51f7bdd15859ca21b969be9c3e3028df4b93c3746abd4eb27a` |
| `research/notation.csv` | `2d0999ceff28882ce49f1ee175caa3d3413122453225343c0089057f319b3634` |
| `research/threat-model.md` | `41073eb15f891dffd822477cadbc70026ff34e96e116065053355184166b9e7e` |

Local checks: all three declared outputs exist; notation parses with exactly the seven required columns, 22 unique symbols, and no empty fields; ten scenario IDs and seven control IDs exist; staged diff whitespace checks pass.

## Acceptance limits

A3 explicitly allows missing scientific interfaces to be documented and assigned downstream. IO-01 through IO-07 and unresolved attack budgets remain blocking prerequisites for dependent implementation/experiments. This acceptance does not assert that the pipeline works, validate a security claim, approve compute, or advance the paused `evidence-review` lifecycle gate. No GPU experiment or scientific test was run for this documentation task.
