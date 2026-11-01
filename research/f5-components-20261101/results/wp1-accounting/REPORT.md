# Saved-development loss accounting

MEASURED: stdlib aggregation of declared saved journals; no new reader/model/image execution. See provenance.json for exact paths, hashes, command and code commit. Each CSV row is a file-line locator (header is line 1).

DERIVED: B = decoded/content-failed; U = recomputed-only; L = neither frozen test passed; M = unavailable. L does not prove physical erasure. Read/found are fixed-stage oracle ceilings, not safe endpoints or component-causal budgets. Missing calls count unsuccessful. Source majority = 2/3, one-image controls = 1/1.

MEASURED: All 14 judge loss-budget cells and all 84 radius counts reproduce exactly. Corrected lower bounds use raw.semantic_code rather than semantic.candidate. A Hamming-ball endpoint is distinct from frozen F5 soft-binding C and J; these counts do not establish calibrated false-positive control or T4/T5 safety.

| Study | Cell | Arm | C/B/U/L/M calls | C/J sources | Content oracle | Found oracle | r0 | r3 old -> corrected lower |
|---|---|---|---|---|---|---|---|---|
| phase-a | R0-0.1 | f5-r2 | 179/0/0/0/1 | 60/41 | 60 | 60 | 60 | 60 -> 60 |
| phase-a | R0-0.1 | v5-r3 | 144/6/24/6/0 | 47/23 | 49 | 58 | 58 | 54 -> 54 |
| phase-a | R0-0.2 | f5-r2 | 171/3/4/0/2 | 57/38 | 59 | 60 | 60 | 59 -> 59 |
| phase-a | R0-0.2 | v5-r3 | 82/7/54/36/1 | 27/6 | 30 | 47 | 47 | 36 -> 36 |
| phase-a | R0-0.4 | f5-r2 | 116/26/26/10/2 | 39/14 | 47 | 58 | 57 | 48 -> 48 |
| phase-a | R0-0.4 | v5-r3 | 7/3/28/140/2 | 3/0 | 3 | 12 | 12 | 2 -> 2 |
| phase-a | R1-0.1 | f5-r2 | 0/3/21/156/0 | 0/0 | 1 | 7 | 7 | 1 -> 1 |
| phase-a | R1-0.1 | v5-r3 | 138/8/32/2/0 | 50/6 | 50 | 59 | 59 | 57 -> 57 |
| phase-a | R1-0.2 | f5-r2 | 0/0/0/180/0 | 0/0 | 0 | 0 | 0 | 0 -> 0 |
| phase-a | R1-0.2 | v5-r3 | 37/5/75/63/0 | 11/0 | 14 | 40 | 40 | 21 -> 21 |
| phase-a | R1-0.4 | f5-r2 | 0/0/0/180/0 | 0/0 | 0 | 0 | 0 | 0 -> 0 |
| phase-a | R1-0.4 | v5-r3 | 0/0/11/169/0 | 0/0 | 0 | 2 | 2 | 0 -> 0 |
| phase-a | ctrlB-codec | f5-r2 | 60/0/0/0/0 | 60/47 | 60 | 60 | 60 | 60 -> 60 |
| phase-a | ctrlB-codec | v5-r3 | 60/0/0/0/0 | 60/42 | 60 | 60 | 60 | 60 -> 60 |
| stage2-union | D1 | f5-r2 | 55/0/5/0/0 | 55/31 | 55 | 60 | 60 | 59 -> 59 |
| stage2-union | D1 | v5-r3 | 60/0/0/0/0 | 60/58 | 60 | 60 | 60 | 60 -> 60 |
| stage2-union | D3 | f5-r2 | 55/0/5/0/0 | 55/35 | 55 | 60 | 60 | 59 -> 59 |
| stage2-union | D3 | v5-r3 | 60/0/0/0/0 | 60/58 | 60 | 60 | 60 | 60 -> 60 |
| stage2-union | R0-0.1 | f5-r2 | 179/0/0/0/1 | 60/41 | 60 | 60 | 60 | 60 -> 60 |
| stage2-union | R0-0.1 | v5-r3 | 144/6/23/7/0 | 47/23 | 49 | 58 | 58 | 54 -> 54 |
| stage2-union | R0-0.2 | f5-r2 | 170/3/4/0/3 | 57/38 | 58 | 59 | 59 | 59 -> 59 |
| stage2-union | R0-0.2 | v5-r3 | 82/8/54/35/1 | 27/6 | 30 | 47 | 47 | 36 -> 36 |
| stage2-union | R0-0.4 | f5-r2 | 117/25/26/10/2 | 39/14 | 47 | 58 | 57 | 48 -> 48 |
| stage2-union | R0-0.4 | v5-r3 | 7/3/28/140/2 | 3/0 | 3 | 12 | 12 | 2 -> 2 |
| stage2-union | R1-0.1 | f5-r2 | 0/3/23/154/0 | 0/0 | 1 | 7 | 7 | 1 -> 1 |
| stage2-union | R1-0.1 | v5-r3 | 140/6/32/2/0 | 50/6 | 50 | 59 | 59 | 57 -> 57 |
| stage2-union | R1-0.2 | f5-r2 | 0/0/0/180/0 | 0/0 | 0 | 0 | 0 | 0 -> 0 |
| stage2-union | R1-0.2 | v5-r3 | 38/4/74/64/0 | 12/0 | 14 | 40 | 40 | 21 -> 21 |
| stage2-union | R1-0.4 | f5-r2 | 0/0/0/180/0 | 0/0 | 0 | 0 | 0 | 0 -> 0 |
| stage2-union | R1-0.4 | v5-r3 | 0/0/11/169/0 | 0/0 | 0 | 2 | 2 | 0 -> 0 |
| stage2-union | R1-mode-0.2 | f5-r2 | 0/0/0/180/0 | 0/0 | 0 | 0 | 0 | 0 -> 0 |
| stage2-union | R1-mode-0.2 | v5-r3 | 24/3/97/56/0 | 6/0 | 6 | 42 | 42 | 16 -> 18 |
| stage2-union | R1-rinse-0.1 | f5-r2 | 0/0/0/180/0 | 0/0 | 0 | 0 | 0 | 0 -> 0 |
| stage2-union | R1-rinse-0.1 | v5-r3 | 15/2/59/104/0 | 4/0 | 5 | 24 | 24 | 10 -> 10 |
| stage2-union | R1-smooth-0.2 | f5-r2 | 0/0/0/180/0 | 0/0 | 0 | 0 | 0 | 0 -> 0 |
| stage2-union | R1-smooth-0.2 | v5-r3 | 19/3/83/75/0 | 4/0 | 4 | 34 | 34 | 13 -> 13 |
| stage2-union | R3-0.2 | f5-r2 | 16/6/46/112/0 | 5/0 | 7 | 23 | 23 | 11 -> 11 |
| stage2-union | R3-0.2 | v5-r3 | 167/6/6/1/0 | 57/31 | 58 | 60 | 60 | 58 -> 58 |
| stage2-union | X1 | f5-r2 | 60/0/0/0/0 | 60/46 | 60 | 60 | 60 | 60 -> 60 |
| stage2-union | X1 | v5-r3 | 60/0/0/0/0 | 60/60 | 60 | 60 | 60 | 60 -> 60 |
| stage2-union | X2 | f5-r2 | 60/0/0/0/0 | 60/41 | 60 | 60 | 60 | 60 -> 60 |
| stage2-union | X2 | v5-r3 | 60/0/0/0/0 | 60/60 | 60 | 60 | 60 | 60 -> 60 |
| stage2-union | clean | f5-r2 | 60/0/0/0/0 | 60/52 | 60 | 60 | 60 | 60 -> 60 |
| stage2-union | clean | v5-r3 | 60/0/0/0/0 | 60/60 | 60 | 60 | 60 | 60 -> 60 |

SOURCE: Phase A native covers R0/R1 only. K3 has mechanism diagnostics, not a 60-source Phase-A detector grid. Its gridA/gridB outputs were quality-ineligible and never detector-released: ceilings there are UNKNOWN. Coverage is explicit in phase-a-coverage.csv. Stage2 union includes clean, both codecs, resize controls, native families, rinse, mode and smoothing. Earlier development variants are report-level evidence in context/wp1-prior-evidence.md; no unavailable raw endpoint is invented.

JUDGMENT: No ball radius is selected. C0 and wrong-owner results in negative-cells.csv are descriptive diagnostics, not copy-paste or semantic-collision tests. The two studies reuse the same 60 sources and are not independent replications. Stats are descriptive across correlated seed calls, not confidence intervals.
