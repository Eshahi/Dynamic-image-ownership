# Independent review of the article-viability package

2026-10-13. Fresh independent Codex reviewer, GPT-6 Astra, high reasoning. The reviewer did not author the protocols, results, strategy or implementation and changed only this review file. No GPU execution, floating-point replay, retained-output modification, held-out tuning, public communication or human verdict occurred.

## Verdict

**PASS for the scientific interpretation and bounded article-viability decision. No material blocking finding was identified.** Retaining full E3, rejecting fixed lean under its original cost gate, recording H1 as unsupported, leaving H2 unused and pursuing only a conditional empirical article are justified by the inspected evidence. This is not a finding that an article is publication-ready, that a novel mechanism exists, that all research routes are exhausted, or that the user accepted M2.

The FreqMark reconstruction has a terminal allocation failure, independently checked in its retained receipt and newly written [result report](freqmark-reconstruction-results.md) and [compact summary](freqmark-reconstruction-summary.json). It provides no optimized baseline quality/recovery outcome and no external ranking. The final inspected roadmap/claim-map updates and dated decision-memo completion note preserve this qualification; they do not present acquisition success or VAE diagnostics as successful watermark construction.

## Scope and method

Reviewed the scientific changes after previously reviewed commit `5d5d314` through `878a736`, together with the current uncommitted roadmap, claim map, H1 wording corrections, article-viability decision, endpoint atlas and terminal FreqMark report/summary. Inspected the simplification and mechanism protocols, compact summaries, relevant construction/analysis code, reader endpoint definitions, geometry note, and FreqMark reconstruction protocol/implementation. Also inspected the bounded [human-admissibility materials](human-admissibility-draft.md): they correctly remain drafts with no selected sample, collected ratings or final aggregation rule. Raw SVG diffs and unrelated infrastructure history were excluded.

Read authoritative MAIN STATE once. Directly inspected these ordinary retained development receipts under MAIN `.thesis-build/dev-runs/`:

- `20261013-1636-fresh-e3-simplification/run.json`, executable commit `546ac1fbf644e3d1ab3f454c9eb8ae736dbd072a`.
- `20261013-1741-fresh-symbol-objective/run.json`, executable commit `a2e3fa19fa4f21008b52bbded9623a26cdbc607b`.
- `20261013-1758-freqmark-reconstruction/run.json` and `20261013-1758-freqmark-reconstruction-platform-fix/run.json`.

Recomputed ordinary source/endpoint counts, cost arithmetic, failure identities and codeword-error histograms from the first two receipts. Their stored summaries equal the versioned compact summaries. Inspected source-level distortion controls and relevant implementation semantics. Did not rerun scientific models or re-hash all development artifacts. M2 claims were checked against the qualified [M2 report](e3-s1-m2-results.md) and [prior independent review](e3-s1-m2-independent-review.md), not a repeated raw-M2 audit. This review does not certify an exhaustive literature novelty search or every prospective implementation branch.

## Findings checked

| Item | Independent check and conclusion |
|---|---|
| Stage A completeness | All 24 sources have strict quality and exact Q/H/F admission in both arms. Four negative families each have 24 observed calls, zero events and no missing outcome. No attack rows exist. |
| Frozen cost decision | Full median 130.1329999999 s; lean stage-sum median 105.9679999999 s. Their ratio is 0.8143053645, giving 18.56946355% saving, below the 25% gate. Full/lean sums are 3554.779/2544.310 s; 28.42564896% mean saving is correctly secondary. Rejecting fixed lean and skipping Stage B are the original decision, not a substituted endpoint. |
| Timing interpretation | Shared supplier/initializer costs are charged to both alternatives; residual full bookkeeping is conservatively charged to lean. The report distinguishes measured full duration from estimated standalone lean time and does not assert independently measured end-to-end acceleration. |
| H1 completeness and controls | Exactly 162 unique rows are present and all are `ok`: 18 clean, 36 VAE and 108 T3 rows. Both arms pass six clean paired controls. Maximum relative energy discrepancy is 0.0001023432262, well below 1%; LPIPS and SSIM pair differences remain inside the frozen tolerances. |
| H1 primary decision | Each arm has exact Q 18/18 at both .2 and .4, J 18/18 and 16/18, and majority J 6/6 at both. No two-source C advantage exists. Clean heterogeneity decreases on all six pairs, but both stress raw-error medians are zero. H1 is correctly unsupported despite a functioning intervention. |
| H1 failure attribution | Both arms lose J at `72/.4/9` and `165/.4/10` while retaining exact Q. These are content-predicate rejections. No independent human semantic verdict exists, so neither false rejection nor semantic drift is established. |
| Coding interpretation | T3 raw-codeword-error histograms reproduce as C `{0:27, 1:8, 2:1}` and S `{0:28, 1:6, 2:1, 3:1}`. Exact decoded recovery does not establish BCH redundancy; the old systematic-bit diagnostic is a different question. |
| Geometry | The projection decomposition and Jensen inequality match the implemented reader/objectives. The score is `sum(m)/norm(m)`, not a unit cosine. The conditional sign/score distinction and additive-isotropic thought experiment do not order nonlinear regenerated recovery. No theorem of diffusion robustness is claimed. |
| Endpoint atlas | Reviewed M2 counts reproduce E3 majority Q/J 294/287 and 297/284, and v5 81/80 and 17/17. Since same-call J implies Q, the common three-call majority sets are nested: differences 7/13 and 1/0 are valid source-level set differences. They are explicitly post hoc, not same-seed drift counts or a new primary endpoint. The atlas correctly avoids a clean-eligibility waterfall and does not infer equal success sets from equal aggregate S/J counts. |
| M2 qualifications | Composite gains remain qualified by eligibility 294/159 and native h asymmetry. Six E3 strict-quality failures, zero majority full acceptance, unresolved negative families, alpha-only ownership and absent human admissibility remain visible. No matched-FPR external superiority follows. |
| Article decision | Closing the maximum-two-hypothesis round after one hypothesis is permitted: a maximum is not a requirement to spend both. The new route is an allocation decision and conditional empirical question, not a retrospective M1/M2 failure or a claimed Q1 contribution. |

The retained FreqMark platform-corrected receipt records `allocation_failed` after 580.233748 seconds inclusive, with acquisition 480.922 seconds and loading 0.781 seconds. Source 30 is incomplete and source 72 is unstarted; no 400-update image was delivered. The failed allocation occurred in the first noisy VAE decode before any completed optimization update. The original and corrected receipts preserve the same approximately 1,800-second deadline. A 256 MiB allocation was refused under the 9 GiB allocator allowance. The last sampled GPU peak precedes the failure and is not an exact failure-time peak.

Unmarked and zero-perturbation VAE outputs are diagnostics, not optimized marks. Therefore neither `0/2 strict quality` nor native-FreqMark failure is an admissible interpretation. The appropriate conclusion is inability of this fixed fp32 equation reconstruction to finish under the fixed local allocation envelope; baseline competitiveness remains unavailable. The unknown native equivalence, feature/FFT/margin/noise defaults and distinct 48-bit task remain material limitations even if a future implementation completes.

## Blocking findings

None for the inspected scientific decision, numerical reporting and claim boundaries. The terminal baseline result does not overturn the decision or require an unplanned retry.

## Warnings and limits

1. The 24-source and six-source cohorts are development evidence. Clean ties and small zero-event controls cannot establish population equivalence, calibrated low FPR or general security. The reports already make this distinction.
2. The prospectively frozen protocol and historical result memos retain some future-tense instructions, such as running H1, reassessing H2 or preparing the atlas. The current roadmap and dated completion notes supersede them; they must not trigger another experiment automatically. The terminal baseline outcome is now correctly reflected in current prose. Updating the package's review-status reference after this verdict is an administrative completion step, not new scientific evidence.
3. Readable exact Q also includes the unchanged reader's readability rule; it is not merely an unthresholded bit equality. The atlas should be read with the linked endpoint definitions. No new raw-bit endpoint is justified by its abbreviated table label.
4. The closest-baseline obstacle, absent independent transfer/admissibility and unresolved incremental binding value remain substantive article gaps. This PASS establishes faithful reporting and a defensible next allocation, not a methods contribution, external competitiveness, human acceptance or publication readiness.

Reviewed evidence anchors: [Stage A](fresh-simplification-results.md), [Stage A compact summary](fresh-simplification-summary.json), [H1](fresh-mechanism-results.md), [H1 compact summary](fresh-mechanism-summary.json), [geometry](chip-symbol-geometry-note.md), [decision](h2-article-viability-decision.md), [atlas](endpoint-interpretation-atlas.md), [claim map](article-claim-map.md), [roadmap](plan.md), and [bounded reconstruction protocol](freqmark-reconstruction-protocol.md).
