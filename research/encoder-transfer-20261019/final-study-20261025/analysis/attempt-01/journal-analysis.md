# Descriptive journal analysis

Final state: 11,040 units from 39,896 journal lines; 60 sources. No images opened.

Positive counts use source majority, with missing/blocked calls counted as failures. Continuous values use complete-source medians.

| Arm | Cell | Positive / 60 | Complete | Semantic decoded normalized margin, median | Instance decoded normalized margin, median | Bit accuracy, median |
|---|---|---:|---:|---:|---:|---:|
| f5-r2 | clean | 60 | 60 | 0.8515 | 1.1349 | NA |
| f5-r2 | R0@0.1 | 60 | 59 | 0.7544 | -0.5984 | NA |
| f5-r2 | R0@0.2 | 57 | 58 | 0.6194 | -0.6114 | NA |
| f5-r2 | R0@0.4 | 39 | 58 | 0.2457 | -0.6087 | NA |
| f5-r2 | R1@0.1 | 0 | 60 | -0.3231 | 0.1127 | NA |
| f5-r2 | R1@0.2 | 0 | 60 | -0.4708 | -0.1378 | NA |
| f5-r2 | R1@0.4 | 0 | 60 | -0.5321 | -0.3747 | NA |
| f5-r2 | R1-rinse@0.1 | 0 | 0 | NA | NA | NA |
| f5-r2 | R1-smooth@0.2 | 0 | 60 | -0.5016 | -0.2171 | NA |
| f5-r2 | R1-mode@0.2 | 0 | 60 | -0.4773 | -0.1219 | NA |
| f5-r2 | R3@0.2 | 5 | 60 | -0.2741 | -0.2967 | NA |
| f5-r2 | D1 | 55 | 60 | 0.5685 | 0.6256 | NA |
| f5-r2 | D3 | 55 | 60 | 0.6372 | 0.6993 | NA |
| f5-r2 | X1 | 60 | 60 | 0.7621 | 1.1165 | NA |
| f5-r2 | X2 | 60 | 60 | 0.6894 | 1.1111 | NA |
| v5-r3 | clean | 60 | 60 | 1.0118 | 1.0643 | NA |
| v5-r3 | R0@0.1 | 47 | 60 | 0.3510 | -0.5974 | NA |
| v5-r3 | R0@0.2 | 27 | 59 | 0.0164 | -0.6001 | NA |
| v5-r3 | R0@0.4 | 3 | 58 | -0.3208 | -0.6034 | NA |
| v5-r3 | R1@0.1 | 50 | 60 | 0.2047 | 0.1274 | NA |
| v5-r3 | R1@0.2 | 12 | 60 | -0.1365 | -0.1505 | NA |
| v5-r3 | R1@0.4 | 0 | 60 | -0.3746 | -0.3767 | NA |
| v5-r3 | R1-rinse@0.1 | 0 | 0 | NA | NA | NA |
| v5-r3 | R1-smooth@0.2 | 4 | 60 | -0.1777 | -0.2634 | NA |
| v5-r3 | R1-mode@0.2 | 6 | 60 | -0.1624 | -0.1250 | NA |
| v5-r3 | R3@0.2 | 57 | 60 | 0.5113 | -0.3342 | NA |
| v5-r3 | D1 | 60 | 60 | 0.9971 | 0.6637 | NA |
| v5-r3 | D3 | 60 | 60 | 0.9731 | 0.7594 | NA |
| v5-r3 | X1 | 60 | 60 | 1.0110 | 1.0557 | NA |
| v5-r3 | X2 | 60 | 60 | 1.0102 | 1.0416 | NA |
| wam | clean | 60 | 60 | NA | NA | 1.0000 |
| wam | R0@0.1 | 42 | 59 | NA | NA | 0.9062 |
| wam | R0@0.2 | 18 | 59 | NA | NA | 0.8438 |
| wam | R0@0.4 | 1 | 59 | NA | NA | 0.6406 |
| wam | R1@0.1 | 48 | 60 | NA | NA | 0.9688 |
| wam | R1@0.2 | 2 | 60 | NA | NA | 0.8750 |
| wam | R1@0.4 | 0 | 60 | NA | NA | 0.4688 |
| wam | R1-rinse@0.1 | 0 | 0 | NA | NA | NA |
| wam | R1-smooth@0.2 | 0 | 60 | NA | NA | 0.5938 |
| wam | R1-mode@0.2 | 2 | 60 | NA | NA | 0.7500 |
| wam | R3@0.2 | 44 | 60 | NA | NA | 0.9375 |
| wam | D1 | 60 | 60 | NA | NA | 1.0000 |
| wam | D3 | 60 | 60 | NA | NA | 1.0000 |
| wam | X1 | 60 | 60 | NA | NA | 1.0000 |
| wam | X2 | 60 | 60 | NA | NA | 1.0000 |
| vine-r | clean | 60 | 60 | NA | NA | 1.0000 |
| vine-r | R0@0.1 | 60 | 60 | NA | NA | 0.9600 |
| vine-r | R0@0.2 | 60 | 58 | NA | NA | 0.8850 |
| vine-r | R0@0.4 | 47 | 59 | NA | NA | 0.7300 |
| vine-r | R1@0.1 | 60 | 60 | NA | NA | 0.9800 |
| vine-r | R1@0.2 | 60 | 60 | NA | NA | 0.9000 |
| vine-r | R1@0.4 | 45 | 60 | NA | NA | 0.7300 |
| vine-r | R1-rinse@0.1 | 0 | 0 | NA | NA | NA |
| vine-r | R1-smooth@0.2 | 60 | 60 | NA | NA | 0.9000 |
| vine-r | R1-mode@0.2 | 60 | 60 | NA | NA | 0.9000 |
| vine-r | R3@0.2 | 60 | 60 | NA | NA | 0.9900 |
| vine-r | D1 | 60 | 60 | NA | NA | 1.0000 |
| vine-r | D3 | 60 | 60 | NA | NA | 1.0000 |
| vine-r | X1 | 60 | 60 | NA | NA | 1.0000 |
| vine-r | X2 | 60 | 60 | NA | NA | 1.0000 |
| trustmark-q | clean | 60 | 60 | NA | NA | 1.0000 |
| trustmark-q | R1@0.2 | 0 | 60 | NA | NA | NA |
| trustmark-q | D1 | 58 | 60 | NA | NA | 1.0000 |
| pixelseal | clean | 60 | 60 | NA | NA | 1.0000 |
| pixelseal | R1@0.2 | 0 | 60 | NA | NA | 0.5215 |

No mechanistic gain or full-chain transport parameter can be estimated from these journals. Quality/family regressions are separate diagnostic fits, not the transfer law.

The selected score/threshold switches branches. Recomputed and decoded branch margins are therefore retained separately in JSON/CSV. The continuous table above uses the decoded branch, not a claim that it alone defines C.

Negatives, source-paired intervals, complete-case quality dominance, correlations, overlap and retained timing summaries are in journal-analysis.json. Carrier states are preserved at call and source-majority level.
