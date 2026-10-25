# Descriptive journal analysis

Final state: 11,040 units from 39,896 journal lines; 60 sources. No images opened.

Positive counts use source majority, with missing/blocked calls counted as failures. Continuous values use complete-source medians.

| Arm | Cell | Positive / 60 | Complete | Semantic decoded normalized margin, median | Instance decoded normalized margin, median | Bit accuracy, median |
|---|---|---:|---:|---:|---:|---:|
| f5-r2 | clean | 60 | 60 | 0.8515 (n=60) | 1.1349 (n=60) | NA |
| f5-r2 | R0@0.1 | 60 | 59 | 0.7544 (n=59) | -0.5984 (n=59) | NA |
| f5-r2 | R0@0.2 | 57 | 58 | 0.6194 (n=58) | -0.6114 (n=58) | NA |
| f5-r2 | R0@0.4 | 39 | 58 | 0.2457 (n=58) | -0.6087 (n=58) | NA |
| f5-r2 | R1@0.1 | 0 | 60 | -0.3231 (n=60) | 0.1127 (n=60) | NA |
| f5-r2 | R1@0.2 | 0 | 60 | -0.4708 (n=60) | -0.1378 (n=60) | NA |
| f5-r2 | R1@0.4 | 0 | 60 | -0.5321 (n=60) | -0.3747 (n=60) | NA |
| f5-r2 | R1-rinse@0.1 | 0 | 60 | -0.5117 (n=60) | -0.0579 (n=60) | NA |
| f5-r2 | R1-smooth@0.2 | 0 | 60 | -0.5016 (n=60) | -0.2171 (n=60) | NA |
| f5-r2 | R1-mode@0.2 | 0 | 60 | -0.4773 (n=60) | -0.1219 (n=60) | NA |
| f5-r2 | R3@0.2 | 5 | 60 | -0.2741 (n=60) | -0.2967 (n=60) | NA |
| f5-r2 | D1 | 55 | 60 | 0.5685 (n=60) | 0.6256 (n=60) | NA |
| f5-r2 | D3 | 55 | 60 | 0.6372 (n=60) | 0.6993 (n=60) | NA |
| f5-r2 | X1 | 60 | 60 | 0.7621 (n=60) | 1.1165 (n=60) | NA |
| f5-r2 | X2 | 60 | 60 | 0.6894 (n=60) | 1.1111 (n=60) | NA |
| v5-r3 | clean | 60 | 60 | 1.0118 (n=60) | 1.0643 (n=60) | NA |
| v5-r3 | R0@0.1 | 47 | 60 | 0.3510 (n=60) | -0.5974 (n=60) | NA |
| v5-r3 | R0@0.2 | 27 | 59 | 0.0164 (n=59) | -0.6001 (n=59) | NA |
| v5-r3 | R0@0.4 | 3 | 58 | -0.3208 (n=58) | -0.6034 (n=58) | NA |
| v5-r3 | R1@0.1 | 50 | 60 | 0.2047 (n=60) | 0.1274 (n=60) | NA |
| v5-r3 | R1@0.2 | 12 | 60 | -0.1365 (n=60) | -0.1505 (n=60) | NA |
| v5-r3 | R1@0.4 | 0 | 60 | -0.3746 (n=60) | -0.3767 (n=60) | NA |
| v5-r3 | R1-rinse@0.1 | 4 | 60 | -0.2263 (n=60) | -0.0694 (n=60) | NA |
| v5-r3 | R1-smooth@0.2 | 4 | 60 | -0.1777 (n=60) | -0.2634 (n=60) | NA |
| v5-r3 | R1-mode@0.2 | 6 | 60 | -0.1624 (n=60) | -0.1250 (n=60) | NA |
| v5-r3 | R3@0.2 | 57 | 60 | 0.5113 (n=60) | -0.3342 (n=60) | NA |
| v5-r3 | D1 | 60 | 60 | 0.9971 (n=60) | 0.6637 (n=60) | NA |
| v5-r3 | D3 | 60 | 60 | 0.9731 (n=60) | 0.7594 (n=60) | NA |
| v5-r3 | X1 | 60 | 60 | 1.0110 (n=60) | 1.0557 (n=60) | NA |
| v5-r3 | X2 | 60 | 60 | 1.0102 (n=60) | 1.0416 (n=60) | NA |
| wam | clean | 60 | 60 | NA | NA | 1.0000 (n=60) |
| wam | R0@0.1 | 42 | 59 | NA | NA | 0.9062 (n=50) |
| wam | R0@0.2 | 18 | 59 | NA | NA | 0.8438 (n=30) |
| wam | R0@0.4 | 1 | 59 | NA | NA | 0.6406 (n=2) |
| wam | R1@0.1 | 48 | 60 | NA | NA | 0.9688 (n=54) |
| wam | R1@0.2 | 2 | 60 | NA | NA | 0.8750 (n=3) |
| wam | R1@0.4 | 0 | 60 | NA | NA | 0.4688 (n=1) |
| wam | R1-rinse@0.1 | 21 | 60 | NA | NA | 0.9375 (n=20) |
| wam | R1-smooth@0.2 | 0 | 60 | NA | NA | 0.5938 (n=1) |
| wam | R1-mode@0.2 | 2 | 60 | NA | NA | 0.7500 (n=4) |
| wam | R3@0.2 | 44 | 60 | NA | NA | 0.9375 (n=53) |
| wam | D1 | 60 | 60 | NA | NA | 1.0000 (n=60) |
| wam | D3 | 60 | 60 | NA | NA | 1.0000 (n=60) |
| wam | X1 | 60 | 60 | NA | NA | 1.0000 (n=60) |
| wam | X2 | 60 | 60 | NA | NA | 1.0000 (n=60) |
| vine-r | clean | 60 | 60 | NA | NA | 1.0000 (n=60) |
| vine-r | R0@0.1 | 60 | 60 | NA | NA | 0.9600 (n=60) |
| vine-r | R0@0.2 | 60 | 58 | NA | NA | 0.8850 (n=58) |
| vine-r | R0@0.4 | 47 | 59 | NA | NA | 0.7300 (n=59) |
| vine-r | R1@0.1 | 60 | 60 | NA | NA | 0.9800 (n=60) |
| vine-r | R1@0.2 | 60 | 60 | NA | NA | 0.9000 (n=60) |
| vine-r | R1@0.4 | 45 | 60 | NA | NA | 0.7300 (n=60) |
| vine-r | R1-rinse@0.1 | 59 | 60 | NA | NA | 0.9300 (n=60) |
| vine-r | R1-smooth@0.2 | 60 | 60 | NA | NA | 0.9000 (n=60) |
| vine-r | R1-mode@0.2 | 60 | 60 | NA | NA | 0.9000 (n=60) |
| vine-r | R3@0.2 | 60 | 60 | NA | NA | 0.9900 (n=60) |
| vine-r | D1 | 60 | 60 | NA | NA | 1.0000 (n=60) |
| vine-r | D3 | 60 | 60 | NA | NA | 1.0000 (n=60) |
| vine-r | X1 | 60 | 60 | NA | NA | 1.0000 (n=60) |
| vine-r | X2 | 60 | 60 | NA | NA | 1.0000 (n=60) |
| trustmark-q | clean | 60 | 60 | NA | NA | 1.0000 (n=60) |
| trustmark-q | R1@0.2 | 0 | 60 | NA | NA | NA |
| trustmark-q | D1 | 58 | 60 | NA | NA | 1.0000 (n=58) |
| pixelseal | clean | 60 | 60 | NA | NA | 1.0000 (n=60) |
| pixelseal | R1@0.2 | 0 | 60 | NA | NA | 0.5215 (n=60) |

No mechanistic gain or full-chain transport parameter can be estimated from these journals. Quality/family regressions are separate diagnostic fits, not the transfer law.

The selected score/threshold switches branches. Recomputed and decoded branch margins are therefore retained separately in JSON/CSV. The continuous table above uses the decoded branch, not a claim that it alone defines C.

Negatives, source-paired intervals, complete-case quality dominance, correlations, overlap and retained timing summaries are in journal-analysis.json. Carrier states are preserved at call and source-majority level.
