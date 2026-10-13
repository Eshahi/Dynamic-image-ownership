# Blinded attack-admissibility materials

Prepared locally, 2026-10-13. Draft materials only: no raters recruited, images assigned, ratings collected or study approval asserted. Final sampling, question wording and aggregation must be frozen before rating. These materials do not relabel existing machine measurements as human judgments.

## Purpose and display

Ask whether an attack preserves the content relevant to its declared task and whether visible changes are acceptable for that task. Raters must not know the method, watermark bits, detector output, study hypothesis or whether an item was selected as a success/failure. Use neutral random item identifiers and random left/right placement, with the reference explicitly labelled. Display equal image sizes and permit the same zoom for every item.

For T3, the reference is the marked image immediately before regeneration. For T4/T5, the reference is the recipient before the transfer attempt; donor delivery is a separate machine endpoint. Do not silently change reference to whichever image makes an attack appear less distorted. Retain source/recipient linkage privately for clustered analysis.

## Instructions shown to raters

You will see a reference image and a modified image. Compare their visible content. There is no preferred answer. Do not try to infer a hidden code or the processing method. If the images are unclear or you cannot make the requested comparison, choose "Cannot judge" and briefly explain why.

1. **Content preservation.** Does the modified image preserve the reference's main entities, their relevant actions and the scene? Choose **Yes / No / Cannot judge**. A change in lighting, texture or fine detail need not change the main content; a changed object, action or scene can. Briefly name any material change.
2. **Instance preservation.** Does it still depict the same particular subject or scene instance, rather than merely the same category? Choose **Yes / No / Cannot judge**. Do not guess identity that is not visually distinguishable. This is reported separately from broad content preservation.
3. **Visible disruption.** How disruptive are the changes for ordinary viewing of this image? Choose **None / Minor / Moderate / Major / Cannot judge**. Record the most important visible artifact, if any.

The questions deliberately separate broad semantic content, exact-instance evidence and perceptual disruption. They do not ask raters to adjudicate legal ownership or watermark validity.

## Before any collection

- Fix the item population, sampling rule, sample size and randomization seed before exposing any detector-conditioned selection. Include successes and failures through that rule; a showcase of the two H1 failures cannot estimate admissibility coverage.
- Use three independent blinded raters per assigned item. Freeze how missing ratings, disagreements and "Cannot judge" responses enter denominators before collection. Report raw rater counts and agreement; do not silently convert abstentions into admissible items.
- Preserve the roadmap's distinction between metric proxies and human judgments. LPIPS <= .30 for proposed T3 planning, with .20 sensitivity, is not itself a human semantic verdict. It is a prospective planning choice, not a universal validity threshold or a retroactive repair to M2.
- Specify which question(s) define the primary admissibility rule for each threat. A broad semantic-preservation answer must not be reused as proof of instance identity. Freeze any majority rule and whether all three responses are required; this draft does not select that rule from observed agreement.
- Keep calibration, rater instructions and final evaluation distinct. Do not change instructions in response to which method benefits. Version the final material and retain every answer, including abstentions.

## Analysis to prepare after the design is frozen

For each method/channel report all planned attack attempts, successful executions, human-rated coverage, admissibility, detector outcomes, joint admissible attack success and conditional success among admissible attempts. Retain safety blocks and unrated cases explicitly. Use source groups, not individual seeds or repeated pairs, as the independent units when uncertainty is estimated.

Exact payload recovery followed by failed content agreement can be called a false rejection of preserved content only within an independently supported admissibility definition. Otherwise its correct label is a disagreement between payload recovery and the content predicate. Rejection of a delivered donor signal is meaningful binding evidence only alongside legitimate positive acceptance and the actual attacker/recipient task.

Local preparation of this document is complete. Actual judgments and any required institutional/supervisor decisions remain human actions; no contact or rating has been performed.
