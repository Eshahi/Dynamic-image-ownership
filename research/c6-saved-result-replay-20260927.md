# C6 bounded saved-result replay preparation

This software checkpoint addresses the persisted-result warning in the earlier
C6 ledger review. It does not execute C6 or supply scientific CSV/summary results.
Issue #20 stays open. The frozen C4 saved-pair package is not modified.

`src/signatures/saved_key_results.py` accepts at most 8 MiB of immutable result
bytes, an externally recorded exact SHA-256, a trusted typed frozen sample/pair
plan and a trusted 32-byte projection seed. The plan fingerprint uses canonical
JSON of the typed inventories in their frozen order; it is not a raw file hash.
The caller must separately bind the original plan file and approval record.

The exact envelope version is `c6-recorded-results-v1`. It requires a complete
explicit sample status inventory, including pending and failed extractions.
Duplicate JSON keys, nonfinite values, unknown fields, missing samples, changed
plan/seed and malformed observations reject. Every pair row is recomputed from
the recorded observations through the reviewed ledger. Canonical comparison
rejects changed identities, labels, dependencies, measurements, status, extra or
missing rows and bool/integer/null substitutions before any summary is returned.

This is consistency replay, not authenticity: a caller supplying a forged
observation package and its own digest can still construct consistent rows.
Image/model/environment/extraction custody, genuine adjudication and approval
must come from the future approved extraction package. The return explicitly
states `extraction_custody=NOT_ESTABLISHED` and scientific acceptance false.
Summaries remain descriptive with unresolved dependence and no inferential CI.

Author check: verified Windows base Python, 17 owned key-ledger/replay tests
passed. Fixtures use artificial one-hot features and owned identifiers, never
study pixels, checkpoints, model execution or GPU. No installs/downloads,
scientific worker, approval artifact or lifecycle transition occurred.

Independent exact-artifact review is required before accepting this checkpoint.

Additional author check: explicit owner/semantic/instance/key/replay suite ran
45 tests, 41 passed and four expected skips. An earlier mistaken discovery glob
`test*signature*.py` matched zero tests and exited 1; this is retained as a
discovery failure, not a test pass. Actual independent read-focused review was
requested from `/root/b3_intake_review` for code commit
`8e53b7ce7afb13abb4fe090d024bc3abab624d94`. The reviewer subsequently reported
no narrow software blocker, independently passed all 17 tests and adversarial
mixed-status/type/inventory probes. See
`audits/c6-saved-result-review-20260927/review.md`. This is only software
consistency acceptance, not scientific evidence acceptance or #20 closure.
