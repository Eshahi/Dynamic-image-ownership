# T6 discovery-intent gap audit

Date: 2026-10-20 UTC. Bounded response to design-review-2 B3; parent acceptance and independent reviewer closure remain pending.

## Reconciled counts

The historical 12 successful query strings met the literal string floor but overstated independent search intent. They are now conservatively merged to six intents. Four new, actually executed OpenAlex discoveries add four distinct design questions. Total: 16 successful query strings, 10 substantive intents, three existing categories (5 arXiv API, 8 OpenAlex, 3 web). Direct retrievals, backend duplicates and the old broad-overlap query #10 earn no extra intent credit.

| Intent | Design question | Query numbers |
|---|---|---|
| I01 | Beta-binomial latent heterogeneity / ICC | 1, 5 |
| I02 | Missing binary calls or clusters and selection sensitivity | 2, 4, 8 |
| I03 | Exact binomial intervals and sample-size precision | 3, 6 |
| I04 | Dependence in aggregate benchmark uncertainty | 7, 12 |
| I05 | Correlated seed-majority aggregation | 9 |
| I06 | Paired significance and multiplicity control | 11 |
| I07 | Joint paired-method law for a fixed superiority-margin route | 13 |
| I08 | Intersection of positive-success and zero-event safety gates | 14 |
| I09 | Selection induced by achieved-quality matching / common support | 15 |
| I10 | Runtime-induced cluster completion under a shared compute cutoff | 16 |

## Distinctness boundaries

I07 asks for the joint mass required to calculate a fixed finite-margin decision probability. I06 asks how paired hypothesis tests and multiplicity behave; they are different mathematical outputs. I08 asks for the probability of the intersection of a positive-count event with a zero-negative event; it is distinct from across-method paired margins and within-positive-seed ICC. I09 asks what conditioning on an achieved processing variable does to the comparison population; it is not an interval or missing-call model.

I10 concerns an execution-induced selection mechanism: a shared wall-clock budget, source order and source-dependent runtime determine which entire clusters finish. I02 concerns missing calls/clusters conditional on an otherwise specified observation roster, with missingness laws and fixed denominators. Although both can produce absent data, the discovery questions differ in the causal selection mechanism and the design control being assessed. We deliberately merge all three old missingness queries (#2, #4, #8) into I02 rather than counting wording variants. I10 does not add a new missingness model or claimed guarantee to the retained analysis.

## Exact new searches and receipts

Each request has its exact URL, method, request headers and UTC time in MAIN cache. Full response bytes, response headers, final URL, HTTP status, UTC receipt time, byte length and SHA-256 are retained. Six ranked metadata records per response were screened individually in intent-gap-screening.json. Duplicate records/versions are flagged. No lead becomes a V2 source merely by being returned.

| Query | Exact search text | UTC receipt | Raw SHA-256 |
|---|---|---|---|
| paired-joint-route | `correlated paired binary outcomes joint probability superiority margin` | 2026-10-20T22:21:37.605372+00:00 | `663a2de60590c40cfa2f8d7cef0029a941b37d7b3bbe053f95725a5a4e2446dd` |
| composite-safety | `co primary efficacy safety endpoints joint probability dependence` | 2026-10-20T22:21:38.894940+00:00 | `80e4fe600b0e102a4363975cabcc1becec33c4a4fafdf9868dd031e551ad1fc8` |
| quality-selection | `matching post treatment variable collider bias common support caliper` | 2026-10-20T22:21:37.691373+00:00 | `70fecb97b377d80a1be207ec8db27041bedeb0e1feec9b8a0467a006635c3bcc` |
| budget-censoring | `computational experiments time budget informative censoring runtime algorithm benchmarking` | 2026-10-20T22:21:39.513849+00:00 | `7a85a89146bf191e18447bc3fdf56e4cbe53011d91bd25d9e226f997f5c03b28` |

## Evidence boundary and decision

All 24 ranked records remain primary-text unread discovery leads, including recent 2025–2026 results. Their titles/metadata motivate possible future reading; they support no empirical number, method claim, design amendment or absence claim. Several results are indirect clinical/forecasting/algorithm-configuration analogues or plainly irrelevant lexical matches. The targeted quality-selection query did not establish a direct finite-grid distortion study. No source was added to satisfy a numeric floor.

The accepted scientific evidence remains eight V2 papers plus five official references. All 15 analytic tables (5,154 rows), planning-table-v2.json and its nine check groups, source-manifest.json, cards, references and historical receipts remain byte-identical. The n=60 recommendation, route and thresholds remain unchanged. No new scientific evidence requiring a design amendment was established by this metadata-only addendum.

## Preservation and limitations

Before edits, all pre-existing topic files were copied byte-for-byte to MAIN cache/T6-1b-intent-gap/before and indexed by size and SHA-256 in preservation-before.json. Current old query objects remain equal to the original first 12 objects. The current summaries explicitly supersede their old overstatement; historical raw bytes and receipts remain available. query-gap-checks.json records mechanical validation.

Search breadth is still not exhaustive. These four focused searches did not produce newly inspected primary evidence. Exact runtime-selection laws, arbitrary safety/positive dependence and post-processing collider effects remain bounded limitations, not solved problems. Future claims from any lead require primary method-and-evaluation inspection, an own V2 card and the literature-skill validation workflow before integration.
