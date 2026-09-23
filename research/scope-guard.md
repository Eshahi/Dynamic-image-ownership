# Scope guard

Issue #4, source task `method-6`. Applies to README, architecture specifications, code, experiments and thesis claims. Authority: immutable proposal/source ledger, `research-contract.md`, and `approval-policy.md`. The original plan and hash-bound historical decisions remain unchanged.

## allowed_method

- Investigate semantic features plus pHash, OwnerID-bound semantic/instance signatures, diffusion latent/noise embedding, and image-domain 8x8 DCT detection according to the source method.
- Resolve the explicit A3 scientific TBDs through inspected sources, concrete architecture decisions, and reviewed feasibility design. Record exact versions and the reason for every selected parameter.
- Implement/configure the approved architecture, tests, controls, documented ablations and fair baselines. Preserve source IDs, split boundaries, failure records and reproducibility provenance.
- Continue public-source literature work, traceability, specifications, ordinary software tests and documentation independently of pending scientific execution decisions.
- Use small development pilots only under the existing plan/compute requirements; distinguish them from the full proposal data commitments and held-out evidence.

## forbidden_automatic_changes

- Do not add ownership transfer, registry/ledger infrastructure, a marketplace or a rights-management service to the required implementation. Narrative ownership language is not authorization for product expansion.
- Do not replace latent/noise embedding with an image-space watermark and report the replacement as the approved latent method. Image-space watermarking may be a labeled baseline.
- Do not add inversion or a neural watermark decoder to the proposed detection path and still claim it implements the lightweight image-DCT hypothesis. Such methods can be separately labeled comparators.
- Do not give the core detector original images, enrollment features, oracle keys or prompts without declaring a changed knowledge profile. Diagnostic/oracle results cannot stand in for the proposal-faithful route.
- Do not silently introduce a secret-key model and attribute its security to the public-derived proposal profile. OwnerID is public; ownership authentication requires evidence beyond an owner string.
- Do not delete or rewrite an approved research question/hypothesis, suppress failed experiments, relabel a contradicted hypothesis, or claim novelty without source inspection.
- Do not silently shrink/substitute final datasets, treat pilots as sufficient final sample size, or claim native-2K behavior from resized inputs. Keep split/deduplication and held-out evaluation constraints.
- Do not select thresholds on test data, hide multiple owner/key trials, pool incompatible attack access regimes, or compare DCT-only runtime against another method's full verification cost.
- Do not launch scientific compute without the required exact authorization or create paid services/API usage without a specified user-approved budget. A deadline does not override these boundaries.

## Alternatives and decision boundary

| Alternative | Current role | When a new material decision is needed |
| --- | --- | --- |
| Pixel/image-domain watermark | Labeled comparator | Replacing proposed latent embedding. |
| Inversion or neural watermark decoder | Labeled comparator | Becoming necessary to the proposed detector rather than comparison. |
| Original-image / reference-feature / oracle-key detector | Diagnostic comparison with disclosed side information | Claiming it fulfills the core recomputation detector requirement. |
| Keyed/secret variant | Design candidate, separately analyzed threat model | Changing the main security/ownership claim or required access model. |
| New dataset, fewer final images, changed source domains | Proposed amendment, not execution default | Any final departure from DATA-01..03 after measured resource assessment. |
| Native prompt-only generation with new signing order | Unresolved IO-07 branch | A revised method or claim beyond the source-supported route. |
| Transfer protocol/ledger | Outside required implementation | Making operational transfer a promised result or product feature. |

A5 may select ordinary model/preprocessing/configuration details where the proposal leaves them open, with technical rationale and review; this is not an excuse to substitute a different core method. If feasibility fails, retain the failed evidence and prepare a concrete amendment rather than silently changing the method. Only the dependent branch pauses; other authorized work continues.

## unresolved_scope_conflicts

1. **SC-01 / BLOCKED_SCOPE:** titles and SCOPE-03 narratively promise dynamic ownership/transfer/history; the reviewed plan excludes automatic transfer/ledger implementation. The project execution correction preserves that exclusion but does not assert a supervisor-approved removal of the narrative requirement. No transfer efficacy experiment or implemented protocol exists. Resolve with a concrete claim-level proposal before making a final thesis claim that the full dynamic-ownership requirement is satisfied.
2. **SC-02 / BLOCKED_DECISION:** image-conditioned preservation and the latent-to-image-DCT detection mechanism are unspecified (IO-03, IO-04). A5 must make them testable. A failed experiment may refute the hypothesis; it does not authorize replacing it silently.
3. **SC-03 / BLOCKED_DECISION:** an unmatched candidate cannot distinguish an absent mark from a transferred mark; semantic-only detection does not establish regeneration (IO-06). Keep component observations and attack ground truth separate until supported decision rules exist.
4. **SC-04 / BLOCKED_DECISION:** public-derived signatures alone do not establish authenticated owner enrollment. Analyze T6 and state limits; do not imply legal ownership or cryptographic unforgeability.

For an actual proposed departure, record the source requirement, present evidence, exact alternative, effect on questions/data/claims, cost/schedule consequence, and required decision authority in one package. Supervisor/university acceptance must cite real evidence. No such acceptance is fabricated here.
