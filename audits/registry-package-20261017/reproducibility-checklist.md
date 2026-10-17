# Reproducibility checklist

- Verified scorer byte identity against 558239d and pinned paths.
- Inspected frozen config, source indices, exposure metadata, fixed seeds and pairing.
- Inspected adapter geometry, E1/E2 missingness checks, E3 competing-record handling and clustered bounds.
- Inspected exact-approval and development-only dispatcher guards.
- Read reproduction-checks.json: passed; no development numerical replay performed.
- Pending final full-pipeline/fault/stop artifacts, recovery fixes, final manifest/core and runtime/disk estimates.
- Held-out raw byte/hash validation intentionally deferred to approved preflight.
- Human visual assessment, final held-out approval and confirmatory outcomes are outside this review.
