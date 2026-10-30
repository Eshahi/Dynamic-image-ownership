# Frozen elicitation instructions

2026-10-30. You are one of five fresh independent gpt-6-astra/xhigh forecasters. Read only this file, evidence-packet.md, history-reference.md and venue-context.md in this directory. Do not open peers' outputs, candidate scores, any other project files, F6 output or the author's probability opinions. No external search: every forecaster receives the same inspected evidence. Write one assigned Markdown file, no other mutations and no git. No experiments, downloads or tool installation.

All estimates are **subjective and uncalibrated**. A triple `[p10,p50,p90]` contains your epistemic quantiles for an unknown event probability, on0..1; these are not quantiles of a binary outcome, measured confidence intervals, or calibrated publication rates. Use broad uncertainty where warranted. Explain your own reference classes, including the gate-specific historical census and its dependence/selection limits. Never pool2/6 or2/2 as a Bernoulli prior. No author estimate anchors you.

## Fixed meanings

Estimate every item separately under hypothetical `GO`, `FAIL`, `RESOURCE_STOP` F6 outcomes as defined in the evidence packet. Do not infer which actually occurred or assign scenario weights.

- **A1:** the full candidate campaign, including matched controls, tuning, evaluation and fresh confirmation, can be built and completed within its stated ceiling. It is not merely the20h first diagnostic. The ceiling is600h for C03/C04 and200h for C09/C18. A counterfactual later authorization is assumed; infrastructure/data/label feasibility still contributes uncertainty.
- **A2:** unconditional probability of achieving the packet's exact defensive development gain contract, including scientific/implementation/budget failure. Do not multiply by A1 again. The margin is at least10pp C versus the best equal-total-budget non-RL, positive paired lower bound, and all specified J/quality/negative gates.
- **A3:** that same comparative defensive contract holds on one prespecified family excluded from all policy fitting, reward queries and selection, **given A2**. The family may have historical project observations; this is an optimization exclusion, not a universal unseen-family guarantee.
- **A4:** the comparative result is reproduced on a new, independently frozen source cohort with the same thresholds and controls, **given A2 and A3**. Confirmation and its controls must fit the stated campaign ceiling. This is the nested reading of “given A3”; an A3 without A2 is not a stage in this chain.
- C09 and C18 do not improve defensive watermark performance. Their **A2/A3/A4 must be null (N/A)**, with a reason, not zero and not attack success or allocation efficiency relabelled as defense. A1 and every B estimate still apply. Supply their separate OWN_SUCCESS below.
- **B1:** the specific route's novelty survives thorough prior-art scrutiny. This is distinct from experimental success or editor acceptance.
- **B2:** a competently written manuscript based only on the **currently available evidence plus the stipulated F6 scenario** passes desk review at its named venue. Do not assume the proposed RL experiment succeeded. A conceptual proposal can therefore have low B2. 
- **B3:** acceptance at that venue **given B2**, under the same current-evidence frame. Competent ordinary revision is allowed, but no undisclosed new scientific campaign is assumed. B1 is not a condition of B2 in this elicitation.
- **FUTURE_ACCEPT:** supplemental direct probability that the stated bounded prospective campaign ultimately supports an accepted article at the named venue, including implementation, null/positive outcome, novelty and editorial risk. This directly answers the user's future-publication question. It is not B2*B3, not conditional on successful experiments, and must not be multiplied by B1.
- **OWN_SUCCESS:** separate prospective utility probability, inclusive of completion risk. C03: same event as A2. C04: at least20% lower total training+tuning+probe+deployment cost at matched C/J (no negative point difference), strict quality and packet negative gates versus the strongest non-RL. C09: at least10pp higher exact-donor false-attribution rate with a positive paired95% lower bound over the strongest matched non-RL, on valid independently labelled recipient groups, with same query budget/fidelity and a modern external binding baseline. C18: the packet's25% total-cost reduction at decision regret within.05 of strongest non-RL and same uncertainty target, prospectively measured. These do not substitute for A2-A4.

**OVERALL A** asks whether the best defensively relevant RL candidate selected from C03/C04 beats the best non-RL under the same contract, under **one shared600h total campaign**, not600h for every attempt or an omniscient best-result oracle. Preliminary selection costs, all failed attempts and multiplicity are included; a prespecified selection rule precedes locked evaluation. Overall A1 means that program completes, A3/A4 use the same nested meanings. 

**OVERALL B** is at least one RL-informed article from R01-R07/R10 under one shared600h program and honest study selection (at most two fully pursued routes, all screens paid). It excludes no-RL R08/R09. B1 means at least one selected route has a surviving specific novelty; B2/B3 concern an honestly selected manuscript using current evidence at its route's named venue; FUTURE_ACCEPT includes the future campaign and may include a rigorous null. Do not assume route independence. OVERALL OWN_SUCCESS is null because mixing defense, efficiency and attack discovery would obscure the event.

## Output format

Write one Markdown memo with a single valid JSON code block and concise reasoning after it. No prose inside JSON. Exact schema:

    {
      "forecaster": "F1",
      "scenario_estimates": {
        "GO": {
          "C03": {"A1":[...],"A2":[...],"A3":[...],"A4":[...],"B1":[...],"B2":[...],"B3":[...],"FUTURE_ACCEPT":[...],"OWN_SUCCESS":[...]},
          "C04": {same keys},
          "C09": {same keys, A2/A3/A4:null},
          "C18": {same keys, A2/A3/A4:null},
          "OVERALL": {same keys, OWN_SUCCESS:null}
        },
        "FAIL": {same five objects},
        "RESOURCE_STOP": {same five objects}
      },
      "route_estimates": {
        "GO": {
          "R02": {"B1":[...],"B2":[...],"B3":[...],"FUTURE_ACCEPT":[...]},
          "R05": {same four keys}, "R06": {same four keys},
          "R08": {same four keys}, "R09": {same four keys}, "R10": {same four keys}
        },
        "FAIL": {same six objects},
        "RESOURCE_STOP": {same six objects}
      }
    }

Use your assigned F1..F5 identifier. R01/R03/R04/R07 inherit C03/C04/C09/C18 B and future estimates respectively; do not duplicate or inconsistently re-forecast them. N0 and N1 are R08 and R09 and provide no-RL comparisons. R08 future acceptance has zero new science; R09 uses the existing75h scenario and no additional science. Evidence-dependent editorial work is allowed. Their current and future estimates may reasonably be similar; explain if different.

After the JSON, give reasons and relevant reference classes for each of the four candidates and overall, a compact explanation of the six additional routes, the effect of each F6 branch, and the three largest uncertainties likely to cause disagreement with another forecaster. Include both a plausible RL advantage and a plausible simpler-method explanation. No need to calculate products; the aggregator will report each forecaster's conditional central product A2*A3*A4 and B2*B3, not products of marginal intervals or a pooled posterior. Coordinatewise median quantiles will remain descriptive expert summaries. Complete this single bounded memo and stop.
