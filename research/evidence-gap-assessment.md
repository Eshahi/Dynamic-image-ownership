# Claim-to-evidence reconciliation — partial B1

Issue #8. 2026-09-23. This maps all 42 immutable `claims.csv` IDs to the consolidated root `evidence-ledger.jsonl`. It is an assessment layer, not a replacement claim ledger or experiment result. Source statements and their locators/limitations remain in that ledger and the `literature/consolidated/papers/` cards.

## How to read the map

`thesis_status` refers to the thesis requirement/result, not the reliability of the cited publication. `REQUIREMENT_NOT_RESULT` preserves a title, scope, dataset or metric commitment. `UNRESOLVED` marks unanswered questions or incomplete implementation/evaluation. `UNTESTED` covers hypotheses and planned claims. None means accepted scientific performance.

Every relationship is an author inference about relevance, not direct support of the original thesis proposition. In particular, comparator existence and threat motivation do not validate the proposed mechanism. Empty evidence IDs mean no admitted mapping in this eight-card package, not proof of a global literature gap. The response's separate B1 claim IDs are retained and referenced explicitly. Requirements need provenance and implementation/design work; they need not all be proved by literature.

## Priority scientific gaps

1. METHOD-06 to METHOD-08: the latent/noise-to-image-DCT detection bridge is unestablished. Complete A5's executable mechanism and preregister an early controlled feasibility check before investing in full dataset runs. Do not replace the core detector with inversion/neural decoding to make a successful demonstration.
2. METHOD-04/05/07 and HYP-01: stable feature/key recomputation and instance distinction need direct analysis, not an assumption that hashing similar continuous features preserves matching keys. No admitted evidence currently validates the proposed combination.
3. RQ-03 versus METRIC-07: preserve separate neural and inversion comparator roles; both also inform HYP-03's accuracy/cost tradeoff. Benchmark common task outputs and timing boundaries; do not report DCT-only cost against a comparator's end-to-end cost.
4. PROB-01/RQ-04/HYP-04: inspected attack sources motivate testing, but their access differs. Keep T4 donor-only, encoder/residual-assisted and proxy/adaptive scenarios separate under the approved threat model. Neither reported forgery elsewhere nor semantic binding elsewhere settles thesis security.
5. RQ-02/HYP-02: isolated pixel/latent papers do not establish a causal survival advantage. The mapped decoder entry identifies a candidate, not its embedding domain; admit explicit encoder-domain evidence before selecting a pixel baseline. Primary regeneration evidence is now admitted with conditional bounds and qualifying defense results; a matched thesis comparison remains unperformed.
6. SCOPE-02: DIV2K inclusion qualifies literature discussion; it does not establish comprehensive real-camera generalization. Define domains/splits before making the gap narrower or claiming it solved.

No prior claim, dataset count or scope is removed. Transfer/history remains the explicit SC-01 boundary. All four research questions and hypotheses remain open. Legal ownership, final acceptance, novelty and scientific feasibility are not certified.

## Next evidence work

Regeneration, SEAL preflight and root consolidation are recorded. See `literature/consolidated/README.md` for explicit source selection and remaining qualifying-source/version screening. Independently review the whole package before acceptance. This mapping's completeness is documentary coverage only, not readiness for the evidence gate or permission for compute.
