# Fresh simplification screen: result

2026-10-13. Exploratory development, local USD 0. Decision: **reject the fixed lean variant under the prospective screen; keep full E3 as the retained method**. All clean checks pass, but the required 25% reduction in median complete construction cost does not. No Stage B attacks were launched. This does not establish that refinement is scientifically necessary or that lean regeneration performance is equivalent.

## Completed evidence

Run: MAIN `.thesis-build/dev-runs/20261013-1636-fresh-e3-simplification/run.json`; code `546ac1f`; protocol/source selection frozen at `cf85ea3`. Exit 0, outcome completed, 3,777.547 seconds including setup, fixed old-source warmup and evaluation. All 24 reserved sources resolved, no failed/missing supplier or source. The old source 1675 warmup is excluded from N=24 and charged to elapsed time. Source selection, exclusions and licences are in the frozen reservation and input receipts. See [compact derived evidence](fresh-simplification-summary.json).

| Clean outcome | Full E3 | Initializer + fixed quality selector |
|---|---:|---:|
| Strict quality | 24/24 | 24/24 |
| Exact semantic q | 24/24 | 24/24 |
| Exact instance h | 24/24 | 24/24 |
| Full acceptance / clean admission | 24/24 | 24/24 |
| Minimum PSNR (dB) | 39.6952 | 39.9559 |
| Minimum SSIM | .955932 | .956768 |
| Maximum LPIPS | .0926664 | .0926664 |

Each of the four negative families has zero A events on all 24 observed sources: unmarked alpha, unmarked beta, full wrong-owner beta and lean wrong-owner beta. These overlapping calls are not 96 independent source trials and establish no rare population false-positive rate. The fixed lean quality selector contracts only sources 30 and 508. Full refinement records accepted updates on 12 sources; that fact alone says nothing about their regeneration benefit.

## Complete cost and the fixed decision

| Construction cost, seconds | Full E3 measured | Lean stage-sum estimate |
|---|---:|---:|
| Median | 130.133 | 105.968 |
| Mean | 148.116 | 106.013 |
| Sum over 24 sources | 3554.779 | 2544.310 |

The predeclared ratio of medians is **0.814305**, an estimated **18.57% saving**, versus the required ratio <=.75. The median of paired ratios is separately .835673; it is not the decision statistic. The final median changes appreciably when the last slow sources enter, so preliminary running estimates are not final results.

Descriptively, the ratio of total costs suggests a 28.43% saving on this particular batch. That is a secondary observation, not a replacement for the failed median gate. It could motivate a separate future throughput question but cannot retroactively promote this candidate. Supplier and initializer medians are 53.375 and 51.305 seconds; both arms require those components.

Lean time shares the actual full-run supplier and initializer computation, adds the measured fixed selector/alpha qualification, and conservatively charges residual writer bookkeeping. It is an estimated standalone warm construction time, **not a measured end-to-end speedup of an independently run lean implementation**. Wrong-owner calls and duplicate full qualification are evaluation costs, excluded from both construction boundaries; setup and warmup are separately included in run duration. No confidence or population noninferiority claim is made from this 24-source screen.

## Next decision and limits

Stage A's fixed gate is false solely on cost; clean quality, admission, negative availability and complete timing conditions pass. Skip conditional Stage B, including all 648 T3 identities and the VAE/T4/T5 panel. The previously fixed T5 source rule produced only one of six requested pairs; no transfer-security result exists for this screen.

Proceed to the independent [chip-versus-symbol mechanism question](fresh-mechanism-protocol.md). It reuses the first six fixed supplier/initializer records, not the held-out M2 sources, and cannot relabel this failed simplification screen as a pass. It does not confer candidate or binding advancement. All previously frozen M2 results remain unchanged; human admissibility is missing.

Provenance clarification: after Stage A launch, the protocol prose's Stage B VAE count was corrected from 72 to 144 (=24 sources x3 arms x2 VAEs), before any Stage B work. The exact identities and caps, and every Stage A instruction, are unchanged. The retained run still records its original protocol hash and commit; it was not resumed or rewritten. Conditional Stage B code was prepared but never executed.
