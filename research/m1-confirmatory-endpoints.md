# Candidate-independent endpoint arithmetic

Preparation only, 2026-10-04. `scripts/m1_confirmatory_endpoints.py` implements the per-cell arithmetic proposed in the narrow confirmatory draft. It opens no files, models or reserved observations. Four synthetic-count tests pass. It is not a scientific worker, approval, successful rehearsal or candidate selection.

Each call takes a fixed list of unique independent source-group IDs (or independent disjoint-pair IDs) and a mapping to a Boolean event or missing observation. Repeated seeds, attack severities, owner claims and payloads belong in separate descriptive cells or a prospectively defined within-unit aggregate; they must not inflate the binomial denominator. The caller must enforce scientific group independence: unique strings alone cannot establish it.

For x events in n units, the one-sided 95% Clopper–Pearson limits are Beta quantiles `Beta.ppf(.05,x,n-x+1)` and `Beta.ppf(.95,x+1,n-x)`, with exact boundary limits zero or one. Two-sided 95% Wilson intervals are also reported. Empty denominators yield null bounds and no pass. These are per-cell intervals, without simultaneous coverage across the package.

Positive missing/invalid outputs count as misses in conservative end-to-end sensitivity; negative missing/invalid outputs count as errors in conservative end-to-end false-attribution rate. Observed-valid results are retained separately. The caller maps all safety failures, corrupt artifacts and unfinished planned units to missing and retains their reasons in the run inventory. No unavailable output is silently converted to a valid detector rejection.

The numerical flags retain the draft targets: positive lower limit at least .80, negative upper limit at most .01. They do not combine image quality, human assessment, threat coverage, public-key security or milestone readiness. Zero errors among300 gives upper bound .00993608194; one error exceeds .01. Twelve successes among12 have a lower limit below .80. The tests check these boundary identities, binomial duality, Wilson symmetry, adverse missingness and rejection of duplicate/extra unit IDs and non-Boolean detector outcomes.

Candidate/scientific-cell definitions still must freeze before authorization. No held-out values were read or simulated as if observed.
