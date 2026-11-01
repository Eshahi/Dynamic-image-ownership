# WP1 analysis ledger

SOURCE: These are saved-development accounting reductions under `analysis/WP1-ACCOUNTING-SPEC.md`, not WP4 option tests, new watermark runs or a preregistered performance comparison. MAIN stdlib interpreter was invoked with `-I`; one process each; no ML imports, pixels, held-out journals or Phase-B xfer. Full commands, input/output hashes and code identity are in each provenance JSON.

| Reduction | Committed code | Command suffix after MAIN `.thesis-build/venv/Scripts/python.exe -I` | Seconds | Outcome and locators |
|---|---|---|---:|---|
| MEASURED: loss/reader-bound accounting | 9c8d1b4 | `research/f5-components-20261101/analysis/account_saved_development.py` | 2.093 | 44 marked +88 negative cells; 14 judge partitions +84 radius counts reproduced; 58 unavailable role-specific calls retained. `wp1-accounting/provenance.json`, `REPORT.md`, CSV files. |
| MEASURED: fragile and exact-code endpoint supplement | 1066f48 | `research/f5-components-20261101/analysis/account_fragile.py` | 1.485 | 44 cells; F/H/A/instance-found/read separate from J. Original C/J rechecked. `wp1-fragile/provenance.json`, `REPORT.md`. |
| MEASURED: final writer-metadata diagnosis | f9c04a8 | `research/f5-components-20261101/analysis/writer_metadata.py` | .953 | 60 final margin medians below target4; 56 sources with negative chips; no convergence claim. `wp1-writer-metadata/provenance.json`, `summary.json`, `sources.csv`. |

DERIVED: 58 unavailable role-specific calls are not 58 independent failed images: a blocked marked output affects its correct- and wrong-owner roles, and missing C0 is counted for each reader. The detailed identities and reasons are in `wp1-accounting/missing-calls.csv`. Native blocks, law unavailability and quality-grid blocks are separately inventoried in `phase-a-coverage.csv`; none was silently retried or dropped.

SOURCE: Provenance byte hashes describe execution-time files on Windows. Git's configured line-ending normalization can change checked-out text bytes without changing parsed rows; compare content after accounting for LF/CRLF when reproducing output hashes. Input journal hashes remain the recorded hashes of the read-only originals. The analysis scripts refuse to overwrite an existing output directory; retain the originals and use a separate output location for any future authorized reproduction.

JUDGMENT: Failed historical variants and negative results remain in `context/wp1-prior-evidence.md` and every relevant component B. The three committed aggregation runs completed without failure, within ten minutes. Descriptive schema-inspection commands and agent scalar calculations also used stdlib and completed in seconds; they created no scientific output. No option was selected, no threshold tuned, no frozen held-out number used as training data, and no new human visibility verdict was fabricated.
