# WP6 probabilities: separate efficacy, useful experiments and publication

Five fresh gpt-6-astra/xhigh agents independently elicit probabilities from the same [frozen packet](forecasts/PACKET-FREEZE.md), without author probability estimates, candidate scores or peer answers. They are **five independently elicited judgments from one model family**, not five independent empirical replications or calibrated human experts. Shared model, evidence selection and possible common blind spots remain. Every probability in this package is **JUDGMENT, subjective and uncalibrated**; aggregation and conditional multiplication are DERIVED arithmetic.

All five forecasts are complete and validated. The frozen elicitation record is preserved unchanged; no scientific experiment or F6 observation was made.

## What the events mean

[Instructions](forecasts/forecast-instructions.md) fix all events before elicitation. A1 concerns completion of the full campaign, not the inexpensive first screen. A2 is a preregistered development C gain of at least 10 percentage points over the strongest equal-total-budget non-RL, with a positive paired lower bound, no adverse stated J/C differences, strict clean quality on every attempted final mark, and observed plus bounded negative-rate preservation. A3 conditions excluded-family success on A2. A4 conditions fresh-source reproduction on **both A2 and A3**. Missing results cannot pass. C09 security discovery and C18 allocation efficiency are structurally N/A for defensive A2-A4; their OWN_SUCCESS events are explicitly separate.

B1 concerns novelty. B2 is desk review with **currently available evidence** at a named venue; B3 is acceptance given that desk review. Neither assumes that an unperformed RL study has succeeded. FUTURE_ACCEPT separately covers the entire bounded future campaign and subsequent acceptance, including negative findings and failure to obtain a publishable result. This prevents a proposal from borrowing nonexistent experimental evidence while still answering the user's future-publication question.

The overall defense event selects among C03/C04 within one shared 600-hour campaign, including unsuccessful selection and multiplicity; it is not an oracle over unlimited experiments. Overall publication permits at most two fully pursued RL-informed routes within that same shared ceiling, excludes the two no-RL baselines and does not assume route independence. No GO/FAIL/RESOURCE_STOP probability or actual F6 observation is used. A scenario's positive F6 mechanism evidence and stronger non-RL comparator can have opposing effects on RL's incremental chance.

The 600-hour ceiling ($330.60 at the historical $0.551/h anchor) and 200-hour individual C09/C18 ceilings ($110.20) are elicitation conventions, not spending recommendations or approved protocols. Matched non-RL fitting, failed calls, controls and fresh confirmation consume the ceiling. The illustrative 1,500 RL training writes alone cost 150–301 hours at unmeasured F6-like anchors, before equally budgeted comparator search; even a nominal design may not finish. Future WP8 designs can be narrower, but these numbers cannot silently become predictions for a different design.

Forecasters explicitly identify unresolved **operational** details: the excluded family's operating cell, confirmation cohort size, external binding implementation/labels and deployment workload for amortized cost. They integrate over reasonable prespecified choices within the stated contract rather than assuming favorable values. Consequently this is a campaign-level forecast, not a calibrated forecast of a completely executable protocol. WP8 must fix those details for any recommended screen or state the later design gate; it cannot claim these quantiles are exact probabilities for that narrower experiment. No clarification was sent to later forecasters that earlier ones did not receive.

## Historical reference class

[The auditable census](forecasts/history-reference.md) distinguishes three strata. Among three families explicitly assessed against comparative M1a, two qualified under their reported conventions and one failed. Three additional families stopped at earlier failed screens; their full M1a status is unassessed. E3 original/S1 are one dependent family, including a preserved failed safety amendment. One independently encoded primary transfer decision, F5 on SDXL, failed; its follow-up is not a second trial. Two held-out studies had positive **different** primary endpoints, while neither preserved strict quality on every source. They are not 2/2 replications of the present RL contract.

No direct RL-versus-strongest-non-RL project experiment exists. These selected, dependent cases support qualitative caution about transfer and quality; neither 2/6 nor 2/2 is an empirical success prior. Existing fixed-menu personalization headroom, method ancestry, unavailable negatives and source consumption are visible in the common packet. Root cross-checked A-C, E3 safety/M1a and F5 confirmation locators before aggregation; no F6 output or protected journal was opened.

## Aggregation and reproducibility

Each forecaster supplies epistemic p10/p50/p90 quantiles for an event probability. They are not percentiles of a binary observation. Reported central ranges are the minimum and maximum of five p50s. Coordinatewise median p10/p50/p90 triplets summarize elicited uncertainty; they are **not a pooled posterior interval**, a confidence interval, or calibrated coverage. The outer envelope is retained in the JSON rather than advertised as an 80% interval.

Only nested conditional central estimates are multiplied, separately within each forecaster: `A2 * P(A3|A2) * P(A4|A2,A3)` and `B2 * P(B3|B2)`. This is a plug-in chain-rule calculation, not an independence assumption. It does not multiply A1 again, does not multiply B1 into an unconditional B2, and does not multiply epistemic quantile endpoints. Median central products are descriptive; integrating a joint posterior over uncertain probabilities would require information not elicited here.

The stdlib [aggregator](analysis/aggregate_forecasts.py) checks four frozen packet hashes, all five JSON schemas, scenario/entity coverage, ordered quantiles, structural N/A values and identical C03 A2/OWN_SUCCESS events, then writes [full tables](forecasts/aggregate-tables.md) and [machine-readable summaries](forecasts/aggregate.json). It calculates only saved subjective numbers, not watermark results. Raw signed-by-ID records remain separate F1–F5 Markdown files. Any interpretation or factual amendment is recorded visibly; no forecast is edited to make it agree with the author's recommendation.

## Results

All five records passed schema, quantile, structural-N/A and unchanged-packet checks: 186 probability triples plus 21 structural nulls per forecaster, across three scenarios. Records: [F1](forecasts/F1.md), [F2](forecasts/F2.md), [F3](forecasts/F3.md), [F4](forecasts/F4.md), [F5](forecasts/F5.md). Parenthesized ranges below are **individual p50 ranges**, not uncertainty intervals.

| F6 scenario | Overall A2: defensive development gain | Full A2→A3→A4 central chain | Overall future RL-informed article |
|---|---:|---:|---:|
| GO | 8% (6.5%–9%) | 0.91% (0.69%–1.1%) | 27% (23%–33%) |
| FAIL | 4% (3.2%–4%) | 0.28% (0.22%–0.32%) | 25% (19%–30%) |
| RESOURCE_STOP | 6% (4.6%–6.2%) | 0.51% (0.42%–0.57%) | 23% (18%–28%) |

The full chain requires both excluded-family transfer and fresh-source confirmation after the stringent development result. Its small value is not a probability that RL can never improve any endpoint. The broader publication event can succeed through an informative null, attack or allocation result and therefore need not track the defensive chain.

The elicited uncertainty within each forecaster is much wider than the central inter-forecaster spread:

| F6 scenario | Event | Coordinatewise median p10 / p50 / p90 |
|---|---|---:|
| GO | Overall A2 | 1.5% / 8% / 24% |
| GO | Overall FUTURE_ACCEPT | 7% / 27% / 53% |
| FAIL | Overall A2 | 0.5% / 4% / 15% |
| FAIL | Overall FUTURE_ACCEPT | 6% / 25% / 51% |
| RESOURCE_STOP | Overall A2 | 0.8% / 6% / 20% |
| RESOURCE_STOP | Overall FUTURE_ACCEPT | 6% / 23% / 49% |

There is no corresponding elicited quantile triplet for the product chain: multiplying quantiles would fabricate one.

## Candidate comparison

A1 is full-campaign completion. OWN_SUCCESS is each candidate's distinct utility event: C03 defensive gain, C04 total-cost saving, C09 stronger valid forgery discovery, C18 prospective allocation saving. These columns must not be pooled as a common success rate.

| Scenario | Candidate / venue | A1 completion | A2 defensive gain | OWN_SUCCESS | Future acceptance |
|---|---|---:|---:|---:|---:|
| GO | C03 / TIFS | 44% (40%–50%) | 7.5% (5.5%–8%) | 7.5% (5.5%–8%) | 11% (9%–13%) |
| GO | C04 / TIFS | 43% (37%–47%) | 3.5% (2.5%–4.5%) | 9% (7.5%–11%) | 9% (7%–11%) |
| GO | C09 / TIFS | 40% (35%–48%) | N/A | 9.5% (5.5%–12%) | 12% (10%–18%) |
| GO | C18 / PRL | 58% (50%–70%) | N/A | 13% (8.5%–16%) | 18% (16%–21%) |
| FAIL | C03 / TIFS | 41% (35%–46%) | 3% (2.8%–3.5%) | 3% (2.8%–3.5%) | 7% (6%–8.5%) |
| FAIL | C04 / TIFS | 40% (37%–43%) | 1.8% (1.2%–2%) | 5.5% (4.5%–8%) | 6.5% (5%–9%) |
| FAIL | C09 / TIFS | 42% (35%–48%) | N/A | 9.5% (5.5%–13%) | 12% (11%–18%) |
| FAIL | C18 / PRL | 58% (47%–67%) | N/A | 8.5% (7.5%–16%) | 18% (13%–19%) |
| RESOURCE_STOP | C03 / TIFS | 36% (32%–43%) | 5% (4%–5.5%) | 5% (4%–5.5%) | 8.5% (6.5%–10%) |
| RESOURCE_STOP | C04 / TIFS | 36% (34%–39%) | 2.5% (1.8%–3%) | 7% (6%–9.5%) | 7.5% (5.5%–9%) |
| RESOURCE_STOP | C09 / TIFS | 38% (30%–45%) | N/A | 8.5% (5.5%–10%) | 12% (8%–17%) |
| RESOURCE_STOP | C18 / PRL | 56% (41%–63%) | N/A | 10.5% (8.5%–15%) | 17% (13%–18%) |

All conditional A3/A4, novelty B1, desk B2 and review B3 quantiles for every candidate and overall are in the [full tables](forecasts/aggregate-tables.md); no metric is omitted from the elicitation.

## No-RL alternatives and article-route comparison

The existing negative article R08 costs zero new science hours in this forecast. R09 uses only the separately frozen 75-hour F6 scenario. The prospective RL routes permit substantial new work, so their larger future probabilities do not by themselves establish a better return on time or money.

| Scenario | Route | Current-evidence B2×B3 central chain | Direct future acceptance |
|---|---|---:|---:|
| GO | R08 / TIFS | 8.75% (6.48%–10.5%) | 9% (7%–11%) |
| GO | R09 / TIFS | 14.04% (11.2%–22.5%) | 14% (12%–23%) |
| FAIL | R08 / TIFS | 9.52% (7.83%–13.68%) | 10% (8%–14%) |
| FAIL | R09 / TIFS | 4.59% (3.52%–5.28%) | 5% (4%–5.5%) |
| RESOURCE_STOP | R08 / TIFS | 8.06% (6.48%–8.88%) | 8.5% (7%–9.5%) |
| RESOURCE_STOP | R09 / TIFS | 0.55% (0.3%–0.83%) | 0.6% (0.4%–1%) |

| Route / named venue | GO future acceptance | FAIL future acceptance | RESOURCE_STOP future acceptance |
|---|---:|---:|---:|
| R01 / TIFS | 11% (9%–13%) | 7% (6%–8.5%) | 8.5% (6.5%–10%) |
| R02 / TIFS | 13% (12.5%–17%) | 15% (14%–19%) | 11.5% (10%–15%) |
| R03 / TIFS | 9% (7%–11%) | 6.5% (5%–9%) | 7.5% (5.5%–9%) |
| R04 / TIFS | 12% (10%–18%) | 12% (11%–18%) | 12% (8%–17%) |
| R05 / TIFS | 7.5% (6%–7.5%) | 6.5% (4.5%–7.5%) | 5.5% (4.5%–6.5%) |
| R06 / TIFS | 12% (7.5%–17%) | 12% (7.5%–17%) | 11% (7.5%–15.5%) |
| R07 / PRL | 18% (16%–21%) | 18% (13%–19%) | 17% (13%–18%) |
| R08 / TIFS | 9% (7%–11%) | 10% (8%–14%) | 8.5% (7%–9.5%) |
| R09 / TIFS | 14% (12%–23%) | 5% (4%–5.5%) | 0.6% (0.4%–1%) |
| R10 / TIFS | 22% (15%–25%) | 20% (12.5%–23%) | 18% (10%–20%) |

## Where the judgments differ

The forecasters agree on a plausible state-dependent or information-dependent mechanism but see no measured action advantage beyond strong controls. Their probabilities differ in how much credit they give that possibility and to a useful narrower paper when the strict utility event fails. F1–F5 each explain their reference classes and strongest simpler-method alternative in the raw memo.

A concrete scenario disagreement is completion: F1 leaves A1 unchanged across F6 branches because RESOURCE_STOP has no specified cause; F2–F5 apply a modest feasibility discount for shared resource uncertainty. Both are explicit judgments, not observations of F6. For the zero-new-science R08 article, F1 treats the fixed evidence frame as invariant, while F4/F5 allow contextual framing to affect editorial prospects. The report preserves these differences instead of averaging away their reasons.

Across the panel, the main unresolved quantities are controllable action advantage, full matched comparator and confirmation cost, all-source quality/negative performance, external binding labels, and residual novelty/significance. Most forecasters give R10's factor-separation study more article potential than a positive writer-policy claim, while recognizing that valid matched factorial arms may be infeasible. C18 is more buildable but still faces strong classical allocation controls. A broad interval is the appropriate statement of this missing evidence; agreement among the five does not calibrate the estimates.

**JUDGMENT:** these forecasts support bounded falsification or diagnostic screens before any full RL program. They do not support replacing the frozen F6 study, promising a Q1 paper, or funding a 600-hour campaign on the strength of a short pilot. WP7 develops claim-specific routes; WP8 chooses at most two prospective screens with explicit operating conditions and later decision gates.

## Boundaries of use

**Visible post-elicitation cost correction (WP7):** enumerating C09's named controls separately requires seven rather than six procedure slots. Its conditional first-screen inventory becomes 11,400 feedback units and 11.21–15.77 hours, before extra fitting; independent final policy seeds cost more. The larger study inherits the correction. See [C09's dated clarification](05-candidates/C09.md). C14's three search slots likewise do not fund every named method separately. The original packet, hashes and raw forecasts remain unchanged; no forecaster was silently given the corrected inventory. These are therefore estimates under the original campaign-level information set, with an additional known cost caveat, not exact predictions for the corrected designs. The 200-hour C09 ceiling was never a claim of sufficient funding; the correction reinforces that risk.

These are decision aids under explicit event/budget conventions, not empirical probabilities that RL works, journal acceptance statistics, guarantees of Q1 eligibility, or approval to run anything. Publication probabilities concern TIFS for C03/C04/C09 and PRL for C18; a change of venue requires a new interpretation. Current JCR/SJR requirements are unresolved at elicitation and will be verified or marked UNKNOWN in WP7. An informative attacker, allocation or null-result paper can be plausible even when defensive improvement is unlikely. Conversely, a scientifically useful result can fail novelty or editorial review.


