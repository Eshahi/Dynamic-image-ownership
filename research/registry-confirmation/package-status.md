# Registry confirmation package: partial handoff, 2026-10-17

Status: incomplete; stopped on an incompatible implementation constraint, not a scientific failure. No held-out pixels were opened, decoded, canonicalized or scored. No confirmatory run, approval file, or approval template was created. All child processes have ended.

The brief requires byte-identical historical scoring files and a wrapper limited to input-path parameters. The approved protocol requires regeneration seeds 15/16/17 and twelve synthetic pairs with seeds 21-32. The historical CLI fixes regeneration seeds 12/13/14 and internally creates six synthetic pairs with seeds 7-12. No input-path substitution can change internally generated seed values or cardinality. A seed-map alias would also mislabel provenance and still leave the synthetic mismatch. A separate endpoint analysis can correctly implement E1-E3, but cannot fix this cohort construction constraint. The exact technical assessment is `research/registry-confirmation-contract-assessment.md`.

Required clarification: allow a separately reviewed, hash-pinned cohort adapter to supply the already approved regeneration and synthetic seeds, while keeping both historical scorer files byte-identical and retaining the frozen descriptor/rule functions. This is a narrow implementation exception to the path-only clause; no threshold, scientific endpoint or data definition change is proposed. The approved plan itself remains unchanged. No such adapter was implemented or executed.

## Saved work

- Both scorer files copied byte-identically from 47bb19ca20e91d50b6c05d1174c17c233eba63f9; SHA-256 values are in `research/registry-confirmation/source-pins.json`.
- Approved plan and frozen threshold JSON copied from that same commit.
- Partial frozen configuration: `research/registry-confirmation/frozen-config.json`, explicitly non-executable. Full dependency and model pins remain outstanding.
- Development reproduction entry point: `scripts/registry_confirmation_reproduce.py`, committed before execution at 7656870. It supplies existing input paths to the unchanged scorer.
- Reproduction artifact: `.thesis-build/dev-runs/20261017-registry-confirmation-reproduction/run.json` in MAIN. Assertion report: `reproduction-checks.json` alongside it. Duration: 56.375 seconds, CPU, USD 0.

## Reproduction result

Both regenerators reproduce F_R source-majority 39/40 at .2 and 30/40 at .4. Descriptor false accepts reproduce zero in all 59,280 unrelated pairs, 80 T4 transfers and 40 different real look-alikes. Synthetic seeds 11 and 12 are accepted. Their ambiguity classification was not asserted: the historical CLI does not compute their PSNR or classify synthetic rows. Consequently its legacy `development_pass` is false and its false-accept total is two. This is retained unchanged, not presented as the approved confirmatory verdict.

## Outstanding package work

The held-out metadata index and footage reservation, runtime/worker/dispatcher extensions, full scoring adapter, held-out guard tests, full-pipeline/fault/stop rehearsals, measured runtime/disk estimates and final manifest preview are not complete. There is no manifest path, manifest SHA-256 or scientific-core hash to approve. The approved plan's 10-12 hours and about 15 GB remain unvalidated planning assumptions, not measured estimates.

The fresh Astra/high assessment was a consequential contract consultation, not the required independent whole-package review. That review has not occurred. Do not count it against the one final review.

The existing dispatcher requires an approval for execution. This is not a separate user blocker: the brief permits extending the existing dispatcher with a strictly development-only, local USD 0 rehearsal mode while preserving test approval requirements. Do not generate a delegated rehearsal approval or call a direct-worker run a dispatcher rehearsal.

Resume on codex/journal-upgrade-plan in the journal worktree. Preserve completed reproduction and source copies. After the narrow adapter clarification, implement the package, commit before new development runs, perform the prescribed rehearsals and one final independent review, and return an exact manifest preview without executing held-out work.
