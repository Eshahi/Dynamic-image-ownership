# Fragile-tier and exact-code endpoint supplement

SOURCE: scripts/m1b_e3_s1_analysis.py:70-84 defines J = exact decoded q AND semantic content_match; H = exact decoded h; D = exact q AND exact h; F = both_match; A = either tier found. J alone says nothing about fragile-tier survival. This supplement resolves the endpoint ambiguity in the Gate-1 finding-3 challenge.

MEASURED: Only saved marked/self-owner development calls. Missing calls remain unsuccessful; each source denominator is 60. Original C/J reproduced as assertions. Line locators and input hashes are in the CSV/provenance files.

| Study | Cell | Arm | C | J | H | F | A | Instance found | Instance read |
|---|---|---|---|---|---|---|---|---|---|
| phase-a | R0-0.1 | f5-r2 | 60 | 41 | 0 | 0 | 60 | 0 | 0 |
| phase-a | R0-0.1 | v5-r3 | 47 | 23 | 0 | 0 | 58 | 0 | 0 |
| phase-a | R0-0.2 | f5-r2 | 57 | 38 | 0 | 0 | 60 | 0 | 0 |
| phase-a | R0-0.2 | v5-r3 | 27 | 6 | 0 | 0 | 47 | 0 | 0 |
| phase-a | R0-0.4 | f5-r2 | 39 | 14 | 0 | 0 | 58 | 0 | 0 |
| phase-a | R0-0.4 | v5-r3 | 3 | 0 | 0 | 0 | 12 | 0 | 0 |
| phase-a | R1-0.1 | f5-r2 | 0 | 0 | 3 | 4 | 53 | 52 | 37 |
| phase-a | R1-0.1 | v5-r3 | 50 | 6 | 1 | 25 | 60 | 43 | 36 |
| phase-a | R1-0.2 | f5-r2 | 0 | 0 | 1 | 0 | 30 | 30 | 19 |
| phase-a | R1-0.2 | v5-r3 | 11 | 0 | 0 | 5 | 52 | 28 | 18 |
| phase-a | R1-0.4 | f5-r2 | 0 | 0 | 0 | 0 | 5 | 5 | 1 |
| phase-a | R1-0.4 | v5-r3 | 0 | 0 | 0 | 0 | 7 | 4 | 0 |
| phase-a | ctrlB-codec | f5-r2 | 60 | 47 | 0 | 0 | 60 | 0 | 0 |
| phase-a | ctrlB-codec | v5-r3 | 60 | 42 | 0 | 0 | 60 | 0 | 0 |
| stage2-union | D1 | f5-r2 | 55 | 31 | 17 | 57 | 60 | 60 | 59 |
| stage2-union | D1 | v5-r3 | 60 | 58 | 11 | 58 | 60 | 59 | 51 |
| stage2-union | D3 | f5-r2 | 55 | 35 | 20 | 59 | 60 | 60 | 60 |
| stage2-union | D3 | v5-r3 | 60 | 58 | 11 | 59 | 60 | 59 | 53 |
| stage2-union | R0-0.1 | f5-r2 | 60 | 41 | 0 | 0 | 60 | 0 | 0 |
| stage2-union | R0-0.1 | v5-r3 | 47 | 23 | 0 | 0 | 58 | 0 | 0 |
| stage2-union | R0-0.2 | f5-r2 | 57 | 38 | 0 | 0 | 59 | 0 | 0 |
| stage2-union | R0-0.2 | v5-r3 | 27 | 6 | 0 | 0 | 47 | 0 | 0 |
| stage2-union | R0-0.4 | f5-r2 | 39 | 14 | 0 | 0 | 58 | 0 | 0 |
| stage2-union | R0-0.4 | v5-r3 | 3 | 0 | 0 | 0 | 12 | 0 | 0 |
| stage2-union | R1-0.1 | f5-r2 | 0 | 0 | 3 | 5 | 52 | 52 | 37 |
| stage2-union | R1-0.1 | v5-r3 | 50 | 6 | 1 | 24 | 60 | 43 | 36 |
| stage2-union | R1-0.2 | f5-r2 | 0 | 0 | 0 | 0 | 30 | 30 | 19 |
| stage2-union | R1-0.2 | v5-r3 | 12 | 0 | 0 | 5 | 52 | 28 | 18 |
| stage2-union | R1-0.4 | f5-r2 | 0 | 0 | 0 | 0 | 5 | 5 | 1 |
| stage2-union | R1-0.4 | v5-r3 | 0 | 0 | 0 | 0 | 7 | 4 | 1 |
| stage2-union | R1-mode-0.2 | f5-r2 | 0 | 0 | 0 | 0 | 32 | 32 | 20 |
| stage2-union | R1-mode-0.2 | v5-r3 | 6 | 0 | 0 | 7 | 52 | 31 | 21 |
| stage2-union | R1-rinse-0.1 | f5-r2 | 0 | 0 | 1 | 0 | 34 | 34 | 27 |
| stage2-union | R1-rinse-0.1 | v5-r3 | 4 | 0 | 0 | 2 | 48 | 35 | 26 |
| stage2-union | R1-smooth-0.2 | f5-r2 | 0 | 0 | 0 | 0 | 16 | 16 | 7 |
| stage2-union | R1-smooth-0.2 | v5-r3 | 4 | 0 | 0 | 4 | 42 | 18 | 7 |
| stage2-union | R3-0.2 | f5-r2 | 5 | 0 | 0 | 8 | 29 | 16 | 2 |
| stage2-union | R3-0.2 | v5-r3 | 57 | 31 | 0 | 11 | 60 | 14 | 4 |
| stage2-union | X1 | f5-r2 | 60 | 46 | 33 | 60 | 60 | 60 | 60 |
| stage2-union | X1 | v5-r3 | 60 | 60 | 28 | 60 | 60 | 60 | 60 |
| stage2-union | X2 | f5-r2 | 60 | 41 | 32 | 60 | 60 | 60 | 60 |
| stage2-union | X2 | v5-r3 | 60 | 60 | 27 | 60 | 60 | 60 | 60 |
| stage2-union | clean | f5-r2 | 60 | 52 | 34 | 60 | 60 | 60 | 60 |
| stage2-union | clean | v5-r3 | 60 | 60 | 28 | 60 | 60 | 60 | 60 |
