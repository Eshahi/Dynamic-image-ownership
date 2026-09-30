# Pre-execution semantic coverage finding

Date: 2026-09-30. Trigger: authenticated user explicitly requested starting the designed experiment. Preparation began on branch codex/18-three-threats, preserving the earlier completed pilot branch and outputs. No new scientific execution was dispatched, no authorization record was fabricated, no GPU/model/detector/binding/CLIP calls were made, and no source/model/software download occurred.

Root author directly inspected all ten raw source JPEGs. Independent read-focused reviewer /root/three_threat_design_review (gpt-6-astra, high reasoning) also viewed all ten files. Its inspection was independent of detector outcomes, but **not blinded to the parent's suggested pairs**. No claim of blind annotation is made. Both assessments agree that the semantic-coverage minimum cannot be met by this cohort.

Criterion: shared principal object/activity at a meaningful level, not merely generic food, human, animal or outdoor categories.

Same-semantic pairs:
- 80932/468505: restaurant dining with people and meals, distinct instances.
- 134882/177015: resting indoor domestic cats, distinct instances/scenes.

Uncertain pairs:
- 25394/80932 and25394/468505: bar service versus restaurant dining, similar context but different principal activity.

All remaining41pairs are different under this criterion. Total45pairs retained:2same,2uncertain,41different. Even assigning both uncertain pairs to same yields only4, below the preregistered minimum5. A third rater cannot fix that arithmetic. No binding outcome was observed or used for selection; labels were not widened to manufacture coverage.

The retained ten-source cohort permits T4/T3 preparation and a descriptive T5 component check, but not preliminary support of allthreeaxes under the current criteria. The designed fallback is T5inconclusive; it must not be presented as correctness of the full method.

Necessary decision for a meaningful full three-axis execution: authorize a small development-cohort expansion using existing local images with separately frozen IDs/hashes/rights and same-subject coverage, or explicitly proceed with the existing10sources accepting an inconclusiveT5 result. At least two additional suitably matched cat/restaurant images could suffice combinatorially, but their actual selection/rights/coverage must be inspected; no identities or guaranteed eligibility are invented. No newdownload or lockedtestaccess is implied.

Preparation preserves supplied algorithm/profile and immutable proposal/taskplan. Operational workflow remains unchanged. Exact reviewed clean attack-entrypoint/resource/runtime manifest still must precede any official dispatch; local time/GPU freedom does not remove those integrity checks. Pending dataset choice is not an invented scientific failure or lifecycle verdict.
