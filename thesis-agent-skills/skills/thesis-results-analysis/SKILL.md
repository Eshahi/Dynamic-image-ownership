---
name: thesis-results-analysis
description: "Analyze declared CSV or JSON runs against a preregistered experiment, preserving failed seeds, missing runs and reproducible output provenance."
---

# thesis-results-analysis

Use when experiment outputs and their specification are available. Read the spec before looking for favorable patterns. Run the helper on declared CSV/JSON files with an unused analysis output directory. It rejects malformed/duplicate/unexpected runs, wrong seeds/conditions, non-finite metrics and mismatched columns; it reports missing and failed runs without hiding them.

Independent seed is the analysis unit. Aggregate within-seed repeated measurements using a preregistered rule before calling the helper; never treat correlated observations as independent runs. Report n, mean, median, SD and range. The optional deterministic paired-seed bootstrap requires at least five complete pairs; intervals are withheld for missing/failed runs. Cohen's dz is reported only where mathematically defined. Few seeds trigger a power warning; neither five seeds nor an interval proves adequate power.

The shipped backend supports one planned comparison and no significance test. For multiple comparisons, choose a family and correction (for example Holm) before results, then add a reviewed analysis extension with validated statistical dependencies. Do not substitute uncorrected repeated tests. Label exploratory work explicitly. Never claim significance/superiority automatically, delete outliers, or silently select successful seeds.

Review deterministic SVG labels and table values. Provenance records input hashes, specification hash, script hash, parameters and output hashes. Keep script and original input artifacts available for independent audit.

Authorization: local analysis of declared files is permitted; publication, changing preregistration or excluding data requires explicit documented review.

## Input/output contract

Inputs must match the strict JSON schemas in `scripts/_runtime/thesis_agents/schemas` after installation, or the bundle's `src/thesis_agents/schemas` during development. analysis/<experiment-id>/{analysis-report.md,statistics.json,tables,figures,exclusions.json,provenance.json}.

Use `python scripts/analyze_results.py --help` for the actual argument contract. Errors return nonzero JSON diagnostics. Do not infer success from artifact filenames alone.
