# Independent A4 protocol-amendment review

Date: 2026-09-23, approximately 12:42 UTC. GitHub issue #5. Author: `/root`; independent read-only reviewer: `/root/a4_protocol_review`. This is a narrow review of prospective threshold selection, failure denominators, quality-summary limits and the stop-rule interaction. It is not a review of executable implementation, data releases, model rights, workload, scientific results or Spec Kit gate acceptance. The primary author transcribed the reviewer's findings; the reviewer did not write this file, alter GitHub/controller state or run a scientific experiment.

| Final reviewed artifact | SHA-256 |
| --- | --- |
| `research/acceptance.md` | `FFF05C4777751BF603004B48D45A6E16A0112985013E9DE6FE52A3282365506A` |
| `research/sample-size.md` | `C4E1E297A24568F0898CC01CDC3C8BC297AA50CF74A70195D09E300E037D7EE1` |
| `research/stop-rules.md` | `9A4AEA670D88D77D468A9A82DF043EC0AB4A5B44C3CBA98539608A82DAFE2860` |

The first reviewer pass found a blocking inconsistency: one A4 paragraph reduced the primary C0-reconstruction/C2 denominator after failed outputs while the new rule kept all predeclared eligible independent groups and counted missing negative outputs adversely. It also flagged a subjective "useful detection" veto, ROC/AUC missingness labeling and the need to retain systemic `STOP_PIPELINE`. The author repaired those points. A second pass found one remaining ambiguous phrase about failed outputs reducing independent N; the author corrected it. The reviewer verified the final hashes and found **no remaining blocker within this narrow amendment scope**.

Reviewer checks: 101 thresholds per component yield 10,201 pairs; the strict `M>0` cutoff agrees with A5's eligible common-q `both_match` rule. The 299-independent-negative resolution claim and failure accounting are mathematically coherent when a failed output from an eligible group stays in the primary denominator, while a missing/ineligible source group or compromised grouping reduces independent N. Valid-output conditional rates/AUC are labeled separately. Individual adverse counts never override a systemic conformance stop or turn a quarantined run into confirmatory evidence. `git diff --check` passed on the three changed files; the standard-library rational-grid check produced unique endpoints −1 and +1 with 1/50 increments.

A4 remains **partial and pre-validation**: B3/B4 data identities/grouping, OwnerID roster/K, seed schedule, actual metric implementations, attack/comparator profiles, paired margins, protocol implementation parity and resource/compute prerequisites are open. The older full-document review in `audits/a4-review-20260923/` remains historical and hash-bound to its earlier version. No user or delegated gate verdict is inferred from this amendment review; the official run is still paused at `plan-acceptance`.
