# H1 blinded human development panel

Protocol fixed 2026-10-13 before human annotation; researcher machine outcomes are already known. Preparation only: no recruitment, ratings, institutional approval or human M2 acceptance is asserted. This supersedes sampling/aggregation placeholders in [the draft](human-admissibility-draft.md) for this panel only.

## Decision and fixed population

Use the **census of 72 existing marked T3 outputs**, not a smaller sample: six development sources (30, 72, 73, 89, 127, 165), chipwise C and symbol-mean S arms, strengths .2/.4, seeds 9/10/11. This small complete panel includes all outcomes without detector-conditioned selection. It is post-outcome development annotation, not prospective confirmation or full E3/M2 generalization.

Use retained PNGs in MAIN `.thesis-build/dev-runs/20261013-1741-fresh-symbol-objective/images/`. Each T3 image is paired with its own `{sid}-{arm}-matched.png` preattack input. Do not substitute unmarked originals or another arm's reference. Add **12 unchanged controls**, one for each source/arm, pairing that matched PNG with itself. Thus each of three independent raters receives all 84 pairs (252 assignments). Controls diagnose display/instruction problems and establish a descriptive unchanged-content anchor; they cannot establish rater validity or real-person identity.

No new images, regeneration, method tuning, quality thresholds, FreqMark attempt or H2 use. The serial FreqMark attempt stopped before photo optimization because deterministic antialiased bicubic CUDA backward was unsupported; the no-more-attempt bound stands. Native closest-comparator evidence remains missing. The existing 12-source observational WAM test cannot replace it.

## Raters and display

Seek three adults who did not develop this method or inspect its detector outcomes. Human recruitment and any applicable institutional decisions are separate human actions; this protocol does not authorize contact. Raters work independently, without discussion or machine assistance. Record prior familiarity with these images/research as disclosed metadata, not an exclusion rule. Researchers already know the results, so this is rater blinding, not researcher blinding.

The portable offline HTML/ZIP contains neutral instructions, PNG assets, response entry/export and no detector outputs, method/arm names, source IDs, strengths, seeds or hypothesis. Rename assets neutrally; keep the linkage manifest outside the distributed ZIP. Label the two panels **Reference** and **Comparison**, with randomized placement. Display equal uncropped dimensions, identical zoom and neutral backgrounds. Preserve PNG pixels. Permit breaks, revision and “Cannot judge”; use no time-based exclusion. Recommended pacing: six blocks of 14, with saved progress. No study images serve as coached calibration examples.

## Fixed questions

Instruction: “Compare visible content. There is no preferred answer. Some pairs may be identical. Do not infer a hidden code or processing method. If uncertain, choose Cannot judge and explain.”

1. **Broad content (primary):** “Does the comparison preserve the reference's main entities, their relevant actions and the scene?” Yes / No / Cannot judge. Lighting, texture and fine-detail differences alone need not change broad content. Briefly describe material changes or uncertainty.
2. **Instance (secondary):** “Does it depict the same particular subject or scene instance, rather than merely the same category?” Yes / No / Cannot judge. Do not infer identities that are not visually distinguishable.
3. **Disruption (secondary):** “How disruptive are the visible changes for ordinary viewing?” None / Minor / Moderate / Major / Cannot judge. Optional short explanation.

Broad admissibility does not establish instance identity, ownership, authorization or overall attack acceptability. Unknown identifiability remains an explicit limitation.

## Reproducible blinding

Freeze rater order seeds **2026101301, 2026101302, 2026101303**, side seeds **2026101311, 2026101312, 2026101313**, and ID seed **2026101391**. Use SHA-256 of UTF-8, pipe-delimited fields, lowercase hex, lexicographic sorting; ties use canonical keys. Canonical private keys are `T3|source|arm|strength|seed` or `CTRL|source|arm`, with decimal source/seed, C/S, and strengths `0.2`/`0.4`.

For each rater, independently sort each source's 14 items by hash of `orderseed|item|key`. For rounds 1–14, sort the six sources by hash of `orderseed|round|roundnumber|source` and emit each source's next item. If a round starts with the preceding round's last source, rotate its source order left once. This separates repeated sources without selecting outcomes. Neutral IDs are `P` plus the full hash of `IDseed|raternumber|key`; filenames follow these IDs. Reference is left when the first byte of hash `sideseed|key` is even. Store orders and linkage before collection; do not reshuffle after inspection.

## Frozen analysis

Primary denominator is all **72 attacks**; analyze controls separately. A pair is complete only with three recorded primary answers. Complete pairs are admissible with at least two Yes, nonadmissible with at least two No, otherwise indeterminate. Any absent primary answer makes the pair missing, even with two Yes. Cannot judge is an answer, never imputed. Report all four counts, admissible/72, and the unresolved upper bound `(admissible + indeterminate + missing)/72`; these are coverage bounds, not confidence intervals.

Retain every rater and answer, including control errors. Report raw response distributions, unanimity, any Yes/No disagreement and pairwise exact agreement with denominators. No adjudication or automatic exclusions. Instance and disruption remain separate descriptive distributions.

Report six source-level summaries and arm/strength tables; repeated seeds/arms/raters are not independent samples. No significance tests or population confidence claim. Cross-tabulate admissibility with Q/J; report joint admissible-and-J/72 and J among admissible with its denominator. Q is 72/72; four J failures are the two identities 72/.4/9 and 165/.4/10 in both arms. Show their ratings alongside the census, without treating four images as four independent failures. Human-supported broad preservation with failed J means rejection under this panel's broad criterion, not proven detector error under every semantic definition. Do not tune thresholds from ratings.

This supports bounded decision-validity work only. Familiar scenes, six source clusters, known researcher outcomes, one regeneration channel and uncertain instance identifiability limit inference. External comparison, independent transfer and article novelty remain unresolved, as in [the viability decision](h2-article-viability-decision.md) and [endpoint atlas](endpoint-interpretation-atlas.md).
