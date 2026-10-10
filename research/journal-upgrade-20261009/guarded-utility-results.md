# D3 guarded utility: useful direction, infeasible fixed budget

Exploratory development result, 2026-10-10. Protocol: [prospective D3 decision](post-d2-method-decision.md), committed before execution. Code `cc96923381a787ca36f375cc38129cc0570d4084`; immutable run `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/20261010-1245-guarded-utility`. All six planned proposals completed in 64.969 seconds, USD 0, below the 180-second screen cap. Numbers below come from `run.json` and actual stage A/V records in `rows.jsonl`.

| Source | Fraction of added-distortion radius | Maximum nine-branch loss | Both actual VAE guards | Eligible improvement |
|---|---:|---:|---|---|
| 6012 baseline | 0 | 3.154572 | yes | baseline |
| 6012 | .1 | 2.841856 | yes | yes |
| 6012 | .5 | 2.786447 | no, SDXL failed | no |
| 6012 | 1 | 2.728422 | no, both failed | no; also clean qualification failed |
| 468505 baseline | 0 | .352983 | yes | baseline |
| 468505 | .1 | .317983 | yes | yes |
| 468505 | .5 | .077460 | yes | yes |
| 468505 | 1 | .064760 | yes | yes |

Each fixed source has at least one eligible improvement. Both baseline final qualifications pass. Thus a decreasing proxy can preserve actual payloads for some steps, but the unconstrained larger steps on 6012 again show why proxy decrease alone is inadequate. These are two adaptively selected development sources, not a twelve-source candidate or official T3 result. Every screen image is discarded as a candidate.

The binding, prospectively fixed cost estimate is **4352.734 seconds**, exceeding **3300 seconds**. Inclusive stage maxima in seconds are L=8.422, P=.750, A=5.406, Gt=1.781 (charged floor 1.890), V=5.172 and F=5.250. Substitution in `L + 12P + 12A + 240*max(Gt,1.890) + 720V + 12F + 30` gives the recorded estimate. No inactive-step or rejection shortcut credit is allowed. The estimate is not a measured full-writer runtime; nevertheless it fails the predeclared execution rule.

**Decision: no full D3 writer and no D3 T3 run.** Close the RC3/native-gradient refinement route, as its protocol requires. Do not revise the formula, raise the cap, shorten the schedule or rename another step/weight retry. This is a resource-constrained closure of one local algorithm route, not proof of scientific impossibility, a third independent family failure, or a new M1a pass. The next study must change the representation or detector hypothesis. Frozen F5 and historical M2 remain unchanged.
