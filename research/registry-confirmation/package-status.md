# Registry confirmation package, 2026-10-17

The package is built; final independent review and preview validation are being closed. No held-out pixel has been opened, no confirmatory run started, and no approval file written. The exact manifest must be approved by the user before execution.

## Frozen science and metadata

The scorer and helper are byte-identical to 558239d. The adapter and missing-path wrapper only supply layout, paths, IDs and approved seeds; both are included in the scientific-core hash. Primary reporting uses plan_view.E1_E2_pass with independent E3 and explicit completeness checks. Any accepted beta record, including ambiguous alpha+beta attribution, fails E3. The trusted registry adds owner/record/q lookup and continuous D1+B1 descriptors as detector side information.

All 300 admitted DIV2K test groups and 20 new Tears of Steel shots (60 pairs) are reserved by metadata. Only three fixed replacement shots remain. Downloading, canonicalizing and excluding duplicate footage happens after exact approval, before model initialization disables networking. Reserve exhaustion stops preflight without reducing the cohort. See metadata-status.md and execution-notes.md.

## Development evidence

- Frozen reproduction: .2 F_R majority 39/40 and .4 30/40 on each regenerator; zero accepts on 59,280 unrelated pairs, 80 T4 transfers and 40 different real pairs. Accepted synthetic seeds 11/12 are ambiguous; plan_view passes.
- Full real worker/dispatcher rehearsal: MAIN `.thesis-build/registry-package/artifacts/M1b-development/registry-rehearsal-02`, commit 358be77, eight fixed development sources and six pairs, seeds15/16/17 and synthetic21-32. Completed in1170.031 seconds, USD0, 1464 journal units:1460 completed, one SD1.5 safety rejection retained, three dependent unavailable calls. Rehearsal-01's journal-path failure is preserved.
- Cooperative stop after21 units, followed by exact-manifest dispatcher resume. All21 saved rows are unchanged. Prior dispatcher state/logs remain in attempts/attempt-001. Evidence: MAIN `.thesis-build/registry-package/rehearsal-evidence.json`.
- Rehearsal scientific results: E1 8/8 each, CP lower .688 (not a pass); E2 zero accepts but seven unknown wrong-source pairs from the safety rejection; E3 passes. Operational completion is not a confirmation claim. No outcome was used to change thresholds or cohorts.
- Synthetic fault tests exercise the actual worker run loop with a mock Runtime, infrastructure interruption, torn append, exactly-once completed work and retained scientific failure. Footage tests use synthetic fixtures only. Final dispatcher tests exercise PID reuse, real Windows process birth identity, lock exclusion and a two-continuation held-out cap.

Final verification logs are under MAIN `.thesis-build/agent-logs/registry-final-*.log`. Final scoring-only replay is retained under MAIN `.thesis-build/dev-runs/20261017-registry-final-analysis-replay`; final wrapper reproduction is `20261017-registry-final-reproduction`. These do not repeat the GPU pipeline or change its retained outputs.

## Resources and recovery

Measured phase costs imply12.31 hours for300 sources, including a conservative quadratic scorer extrapolation from40 development sources. A25% margin gives15.38 hours, below the16-hour warning threshold. Estimated incremental disk is10.79GiB, including acquisition allowance and margin; the manifest reserves20GiB. Measured free disk was174.9GiB. Registry descriptors alone project21.24MiB. Model weights stay referenced in place. See resource-estimate.json and rehearsal-environment.json.

The user reports Acronis automatically restarted the laptop at07:04 and the prior session was killed at07:37 on October17. Estimates exclude reboot downtime and an unfinished unit's repeated work. The dispatcher stores process birth identity, preserves attempt receipts, and resumes completed journal units. An uncertain launch window still fails closed; no system reboot settings were changed. The exact held-out manifest permits at most two continuations while approval remains valid.

## Review and preview

One fresh Astra/high reviewer inspects the whole diff since5874385. The review lives in independent-review.md and audits/registry-package-20261017; the earlier contract consultation is separate. No human acceptance or lifecycle gate is fabricated.

Final manifest path: MAIN `.thesis-build/registry-package/registry-confirmation-manifest.json`. The matching `manifest-preview.json` reports canonical approval SHA-256 and scientific-core hash plus an unfilled approval template. The raw-file SHA-256 is reported separately in `manifest-validation.json`; approval uses the canonical digest. No runnable approval file is created.

Before execution the user decides whether to approve that exact manifest, with the stated reboot risk and finite footage reserve. The professor's definition confirmation remains as stated in the approved plan unless the user reports otherwise. No new scientific choice, paid compute or optional DiffusionDB arm is added.
