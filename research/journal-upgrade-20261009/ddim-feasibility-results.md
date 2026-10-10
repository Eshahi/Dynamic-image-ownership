# Actual-DDIM gradient feasibility: D1 and D1N

2026-10-10. Exploratory development evidence; no new twelve-source candidate was written. Original D1 failed its declared derivative smoke. The separately prospective D1N continuation also failed its fixed convergence prerequisite. Neither result changes historical M1/M2 or establishes impossibility of attack-aware writing.

The native tensor adapter exactly reproduced the official posterior draw, added noise, timestep sequence and RGB8 pre-checker output at strengths .1 and .2, seed 0, on fixed RC3 source 1675. The official checker remained enabled. These internal comparisons are not successful attack observations.

| Development record under MAIN `.thesis-build/dev-runs/` | Code | Seconds | Result |
|---|---|---:|---|
| 20261010-1151-ddim-feasibility | f6260a0 | 25.719 | .1 parity passed; downscaled inactive-hinge diagnostic input gradient zero |
| 20261010-1155-ddim-zero-diagnostic | 10ccbd5 | 12.391 | Fixed multiplier comparison identified destructive half-gradient downscaling |
| 20261010-1157-ddim-feasibility-retry | 0d36752 | 18.000 | Both native parity/finite-gradient checks passed; original continuous derivative criterion failed |
| 20261010-1202-ddim-convergence | df24e73 | 89.984 | Both strengths measured; D1N two-smallest-scale criterion failed |

Aggregate diagnostic computation was 146.094 seconds. All records are retained. There was no held-out access, paid action, threshold change, candidate optimization or official T3 candidate grid. Directory labels identify records; commit and run contents supply development provenance.

The fixed linear scalar was mean(w*p), used because both native semantic hinge losses on source 1675 were already zero. Native input-gradient norms after dividing out multipliers were 0, 2.643683 and 2.924345 at multipliers 1/1024, 1 and 1024. Output-side gradient norm stayed about .62154. Unit scaling repaired the destructive zero but did not establish scale-invariant half-precision gradients.

The original continuous .1 diagnostic had AD -2631.208 and finite differences -46.2973 and -95.8122 at RGB RMS eps .003 and .001. Its .35 relative-discrepancy gate failed. Subsequent smaller-scale diagnostics promoted the same half weights and prompt to fp32, removed RGB8 operations, retained clamps and fixed within-precision noise, and disabled both matmul and cuDNN TF32. Previously matmul TF32 was false and cuDNN TF32 true; smaller perturbations and kernel precision changed together, so causality is not isolated.

| Strength | AD | FD at 1e-4 | FD at 3e-5 | FD at 1e-5 | FD at 3e-6 |
|---|---:|---:|---:|---:|---:|
| .1 | -2771.8042 | -424.2718 | -763.1620 | -1238.0779 | -1755.0588 |
| .2 | -2411.5532 | -472.9748 | -852.4517 | -1300.4690 | -1711.6566 |

At the two required smallest scales, relative discrepancies were .55333/.36682 for .1 and .46073/.29023 for .2. Both strengths fail the prospectively required agreement at **each** scale; the change between their two secant estimates also exceeds the .20 stability limit. All secants have the expected descent sign, and magnitudes trend toward AD, but convergence was not established under the fixed criterion. These numbers do not license a retrospective pass or another selected epsilon under D1N.

Input 1675 has 11,140 exact boundary components (0 or 255) out of 786,432. Directional energy on those components was not recorded. Clamp kinks, finite-step curvature, precision and a still-unresolved gradient defect therefore remain possible explanations; none is isolated by this evidence. No whole-diffusion identity gradient was substituted.

Native diagnostic peak allocation was about 5.676 GB, while the original promoted diagnostic reached 8.629 GB. Disabling TF32 reached **18.028 GB allocated**, exceeding the laptop's approximately 12 GB dedicated VRAM; Windows shared-memory behavior allowed completion. It is incorrect to claim this strict diagnostic fit entirely in dedicated VRAM. Native forward/backward remained inexpensive; a larger GPU alone would not resolve the derivative disagreement.

The source-468505 native rounded utility stage was never reached. Its scientific result remains missing, not negative. D1 and D1N stop before writing; a later method must be a separately specified algorithm and preserve these failed tests. A native-evaluation acceptance rule is under design, where an unverified autograd vector could be merely a proposal heuristic and actual rounded measurements decide whether an update is retained. That is not activated or established by this results file.
