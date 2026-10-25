# E3 independent hostile review of the article frame

Reviewer: Codex E3 independent article reviewer (`e3_article_review`), fresh agent, 2026-10-25. Reviewed snapshot: **13f8d1e**, E1/E2 scope **b2c1bba..13f8d1e**. I did not author E1, E2 or WP6. The authoritative MAIN STATE was read once. This is a bounded manuscript-framing review, not a repeat of WP6's scientific-design review or a new audit of retained run bytes. No experiment, scientific interpreter, image inspection, acquisition, installation or remote compute was used. Only this review file is written.

## Verdict

**ACCEPT WITH TARGETED CORRECTIONS FOR AUTHOR DEVELOPMENT ONLY. NOT READY FOR SUBMISSION.**

The present defensible contribution is a diagnostic development case: a fixed encoder-directed image-domain writer retains its compound endpoint after foreign codec round trips but loses it under the tested full regeneration pipelines. Its stronger quality-ordering contrast is post-hoc and narrower than matched-quality causal inference. The draft does not establish a new watermark, a general transfer law, independently trained encoders as the cause, or a verified ownership mechanism.

I found **one blocking provenance defect in the article package (B1)** and **three bounded textual corrections (R1–R3)**. No reviewed finding invalidates the retained numerical verdict or calls for changing the accepted WP6 parameters/tests. Novelty remains a material submission risk, explicitly assessed below; accepting this development frame does not certify that the case is a sufficient journal contribution. Complete corrections before describing E3 as resolved. A same-reviewer verification of the author response is sufficient; another independent reviewer is unnecessary.

## Scope and evidence basis

Read in full: `article-drafts/README.md`, `related-work.md`, `mechanism.md`, `threat-model.md`, and `venue-fit.md`. Compared with the retained `../article/route-c-skeleton.md` and `../results-2b.md`, with targeted checks of `FINAL-REPORT.md`, `02-positioning.md`, `04-mechanism.md`, `07-final-experiment.md`, `08-review.md`, the three venue notes, and relevant evidence contracts/cards. All line locators below refer to the reviewed snapshot, before author corrections.

Focused live primary inspection checked Stable Signature §4.2/§7.1, LaWa §3.2/§4.7, MarkNull §5/Assumption 2/Appendix E.2, the accessible Behera author manuscript's co-design limitation, TIFS's deep-learning guidance and IEEE Access's Negative Result category. The exact sources and limited conclusions are in the appendix. I did not independently reopen every cited paper, verify current quartiles, or establish identity between author manuscripts and inaccessible publisher versions. Those limits do not silently upgrade any V1 evidence. Historical arithmetic is assessed against the retained reviewed reports, not independently recomputed here.

## Blocking article-package defect

### B1 — A pending Q1-definition choice is labelled a recorded user decision

**Severity:** blocking provenance correction; does not invalidate the science. **Classification:** unsupported human-decision attribution.

**Locator:** `venue-fit.md:37`, paragraph beginning “The exact primary URLs,” especially the bold label `User decision recorded`.

**Evidence and consequence:** The sentence records a conditional requirement to establish an exact JCR year/category before venue commitment. Neither the authenticated task brief nor the article evidence records the user's choice of metric, category or year. The text therefore presents an author recommendation/pending choice as a completed human decision. That distinction matters because submission eligibility and institutional choices remain with the user. The surrounding conservative quartile discussion does not repair the provenance label.

**Minimal correction:** Replace the label with **“Decision reserved for the user”** or **“Author recommendation”** and say that the applicable metric/year/category remains unspecified. Preserve the current session default of no SJR–JCR equivalence and no current-Q1 certification. Do not fabricate a new approval or ask the absent user during this session.

## Required bounded text corrections

### R1 — Use “predictor” or “model,” not “law,” in the article's own claims

**Severity:** moderate framing correction. **Classification:** proposed model supported as a specification; empirical law unsupported.

**Locators:** `article-drafts/mechanism.md:79,85,87,115`; `article-drafts/threat-model.md:15,24`; `venue-fit.md:43,45`. The mechanism heading and opening already use the better term “proposed predictor.”

**Evidence and consequence:** The quantity `p_hat = b_C0 + kappa*v` is a calibrated local-linear surrogate, whose inputs include the target program's C0 trajectory, reader and derivatives. Its decomposition separates gain and signed orientation algebraically; that identity alone supplies neither empirically established invariance nor a new causal law. No relevant tangents or fit have been measured. The text repeatedly acknowledges these limitations, so this is terminology drift, not a hidden claim of an executed experiment. Nonetheless “law” is unnecessarily stronger than the warranted contribution and risks surviving into an abstract or figure caption without its qualifications.

**Minimal correction:** Use **“proposed full-chain transport predictor”** on first mention and **“predictor/model”** thereafter in the new article/venue prose. Retain existing internal protocol identifiers or filenames where required; no mathematical or protocol change is needed. If quoting the dossier's historical name, identify it as provisional terminology. In any future successful article, a bounded predictive validation still does not by itself justify a universal or causal law.

### R2 — Carry the nontrivial-contrast guard into the article's success interpretation

**Severity:** moderate; required before interpreting future prediction success. **Classification:** current H4 description is correct but incomplete as an account of mechanism support.

**Locators:** `article-drafts/mechanism.md:85–87` (“H4 retains exactly two predictive targets”) and `:101` (“The proposed explanation therefore earns support…”); `venue-fit.md:45` for the conditional future outcome.

**Evidence and consequence:** `07-final-experiment.md`, §6, explicitly requires supported **H1 and H2** for a nontrivial high-versus-low retention forecast. H4 alone can certify useful bounded prediction while the intended high/low contrast is absent: if every cell collapses to zero and a constant-zero forecast beats a poorer comparator, the two numerical H4 conditions need not establish the intended explanation. This does not change H4's definition or show its statistics are invalid. It shows why success wording needs the already accepted reporting guard near the criterion, rather than only in a linked protocol.

**Minimal correction:** Add: **“A nontrivial high-versus-low retention claim additionally requires supported H1 and H2 under the same Holm family. H4 alone supports only its bounded predictive comparison; a common-floor outcome cannot validate the proposed explanation.”** In the final interpretation distinguish predictive support from identified causation. No new hypothesis, comparator, slot or threshold is requested.

### R3 — Separate the complete-quality denominator from the retention-transition count

**Severity:** moderate quantitative clarity correction. **Classification:** reported quality ordering supported; implicit all-source transition reading too broad.

**Locator:** `article-drafts/mechanism.md:9`, opening two sentences. Also relevant to any proposed abstract/figure caption based on this sentence.

**Evidence and consequence:** The authoritative summary at `04-mechanism.md:9` and `FINAL-REPORT.md:29` says **58** complete paired quality triples, of which **56/58** retain C at SD1.5 .2 and lose it at SDXL .1. The draft compresses quality dominance and loss into “Across all 58 … yet loses C,” while also including SD1.5 .4. It does not explicitly claim 58 retention flips, but leaves that natural reading available and omits the relevant quality reference and source aggregation. The .4 comparison has a different positive-retention count; it cannot inherit 56 or 58 from the .2 contrast.

**Minimal correction:** State the cleanest retained comparison explicitly: **“On all 58 sources with complete paired source-median qualities, SDXL .1 is milder than SD1.5 .2 on LPIPS, PSNR and SSIM; 56/58 retain C under SD1.5 .2 and lose it under SDXL .1. The ordering holds against both the published marked input and the original image. This is post-hoc sourcewise metric dominance; the fixed matched-distortion calipers retain only two F5 sources.”** If the .4 ordering remains, state it separately without implying the same transition denominator. No new reanalysis is needed to use the verified .2 contrast.

## Warnings and accepted scientific limitations

### W1 — The diagnostic case is plausible; journal-level novelty is still unestablished

**Severity:** major submission risk, not a reason to suppress the negative result. **Locators:** `related-work.md:31–37`; `venue-fit.md:39–45`; `README.md:13–19`.

The draft correctly acknowledges that regeneration removal, foreign-codec attacks, rinsing, directional arguments and VAE-specific co-design already exist. The inspected Behera author text reports SD1.5 co-design failing under SDXL reconstruction. Stable Signature and LaWa already establish method-dependent codec retention. Consequently neither “cross-encoder failure” alone nor putting a direction into an equation supplies a distinct contribution. The closest-prior-work paragraph is honest, but the author's burden remains to explain why this particular codec/full-chain dissociation and reader-state analysis changes a useful evaluation inference.

The phrase **“counterexample to treating codec-round-trip retention as sufficient”** at `venue-fit.md:41` is logically defensible as a counterexample to an explicitly posited sufficiency inference. The same paragraph correctly says that no cited author is alleged to have made that universal claim. Keep that qualification. Do not recast this as refuting published consensus or satisfying TIFS's negative-result provision by contradiction of an actual paper. A minimal contribution statement is a **diagnostic case about an insufficient evaluation proxy for this fixed writer and these pipelines**. Its general methodological interest is a reasoned argument, not a measured population fact. No search inspected here proves priority, and no additional scope is demanded to manufacture novelty.

**Disposition:** accepted limitation for author development; unresolved for submission. If the eventual manuscript depends on a successful new predictor for its contribution, it must await that evidence. If the predictor fails, the article must stand or fall on the bounded negative case itself.

### W2 — Prediction is privileged and mostly on historically familiar pipeline choices

**Severity:** material limit, adequately disclosed in the reviewed draft. **Locators:** `mechanism.md:79–85`; `threat-model.md:15–24,38,54`.

The target/reader derivative and C0 access is much richer than the attack's information, the operational verifier's information, or six scalar quality features. Success against that comparator would show usefulness under those unequal resources; it would not show equal-cost superiority or a lightweight detector. The fixed source-disjoint test is valuable, but K3 is excluded from fitting while historically known, not a blind discovery of a never-consulted family. R0/R1 are familiar families; optional FLUX is conditional. The manuscript currently says this accurately. Do not replace it with “unseen encoder generalization,” “encoder-free prediction,” or “two-parameter explanation” in a later title/abstract/caption.

**Disposition:** accepted. Future measured cost and per-family performance remain necessary to interpret any claimed practical utility; this review does not add a resource or experiment requirement beyond the existing protocol.

### W3 — Metadata freshness and source-level intervals do not establish an image population

**Severity:** material external-validity limit, adequately disclosed. **Locators:** `threat-model.md:48,52,54`; `mechanism.md:7–9`.

Three seeds are repeated observations. The existing 60-source cohort is development evidence; the 200+40 future list is curated metadata, not acquired independent samples or verified pretraining exclusions. The .0487 zero-event bound is a source-any bound under an independent-source population model, not an operational per-query FPR. Exact hashes cannot prove near-duplicate absence or statistical independence. The text preserves these distinctions and does not claim held-out completion. C0 and wrong-owner negative controls do not establish adaptive unforgeability.

**Disposition:** accepted. Preserve the population-model qualifier and distinguish historical all-attempt counts from conservative future missingness inference.

### W4 — Native comparisons are contextual and security scope remains narrow

**Severity:** material interpretation limit, adequately disclosed. **Locators:** `related-work.md:13–15`; `threat-model.md:7–9,28–32,40–48`.

F5/v5 C and WAM/VINE known-message presence are distinct endpoints. Strict clean-quality passes 60/60, 60/60, 58/60 and 31/60 prohibit an equal-quality ranking; the VINE threshold event prevents erasing specificity qualifications. The article correctly separates carrier presence A, readable decoding, original-code recovery, content compatibility and ownership. Its restricted detector-free attacks do not establish security against the public method's full adversary. T4/T5 and the failed registry result are not promoted into achieved contributions.

**Disposition:** accepted. Side-by-side bars must keep native endpoint labels and clean-quality qualifications in the figure/caption, rather than relying on a distant threat-model paragraph.

## Editorial improvements for a future integrated manuscript

These are not new experiments or blockers to the bounded development deliverable.

1. **Make the current and prospective narratives visually separate.** `mechanism.md:23–101` devotes most of the section to an unexecuted study, including fit order statistics and exact betting constants. In a manuscript based only on historical results, place the calibrated predictor in a labelled proposed-model/discussion section or supplement. Keep observed codec/full-pipeline counts and their uncertainty central. Do not let the largest section become an implied achieved result.
2. **Reduce protocol machinery in reader-facing prose.** The mixture's six lambdas and the internal H1–H6 labels matter for reproducibility but interrupt the mechanism story. Preserve the exact contract in a methods appendix and explain the main-text test in terms of what would falsify the model. This is relocation, not omission of essential assumptions.
3. **Finish attribution without inventing novelty.** `mechanism.md:69,93–99,119` uses standard directional/local-linear/information arguments documented in local notes. Add primary attribution from inspected sources where appropriate and state information units as **nats** for the displayed Gaussian bound. Its expectation averages over the stated conditional population; it is not automatically a sourcewise guarantee. No mathematical-novelty claim is warranted by rederiving the bound.
4. **Avoid reviving weaker skeleton rhetoric.** The new title is appropriately singular and diagnostic. The older skeleton's broad “same-family regeneration overstates…” title, “not explained by distortion” shorthand and loose instance-tier A wording should not be copied back into the integrated article. The new prose intentionally corrects those inherited shortcuts.

## Venue and Q1 interpretation

The E2 recommendation is sound as a **conditional fit assessment**: TIFS is a direct subject match; IEEE Access explicitly offers a meaningful negative-result article category; neither fact certifies this manuscript's sufficiency. TIFS's special negative-result language concerns contradiction of published work, which failure of this unpublished writer does not automatically provide. The inspected publisher pages support those distinctions. No acceptance probability is justified or offered.

The ledger properly separates SJR from JCR, indexed 2024 evidence from current status, and category-specific values from an unspecified best/journal-level display. I did not independently reverify the quartile records, and no current-Q1 or institutional-eligibility conclusion is adopted. Historical/inaccessible format rules remain qualified. Apart from B1's human-decision label, the venue text does not require a speculative server study as a purported universal publisher rule.

## Residual author and user decisions

**Author work now:** apply B1 and R1–R3; preserve the accepted limitations; record a response with exact changed locators; integrate citations and any figure without changing prospective criteria or upgrading the scientific result. The authors must choose a coherent empirical-case contribution statement for the eventual manuscript, rather than borrow novelty from unexecuted prediction/attack plans. This can be done without user interruption.

**Still reserved for the user later:** whether and when to fund the two server phases; the applicable Q1 metric/year/category if Q1 remains a requirement; eventual venue, authorship, submission, publication timing and fees. No response or approval is assumed by this review.

**Final review status:** corrections requested for an otherwise defensible **author-development frame**. Submission readiness remains unestablished because the manuscript is incomplete, its novelty argument is unresolved, and the proposed predictive evidence does not exist. This verdict is not a thesis gate, acceptance forecast or authorization to execute or publish.

## Appendix — Focused independent primary-source checks

Accessed 2026-10-25. These checks support the stated limited points, not every result in each source. No paper citation based only on an abstract is adopted.

| Source inspected | Method/experiment locator and bounded check |
|---|---|
| [Stable Signature, arXiv:2303.15435v2](https://arxiv.org/html/2303.15435v2) | §4.2 describes decoder fine-tuning; §7.1/Figure 7 compares autoencoder removal. The corresponding codec can remove more effectively than foreign codecs in that setting. Appendix attack details qualify the PSNR reference. The E1 account is faithful. |
| [LaWa, arXiv:2408.05868v3](https://arxiv.org/html/2408.05868v3) | §3.2 freezes the original encoder/decoder layers; §4.7 compares autoencoder attacks and reports own KL-f8 bit retention with a marked-image PSNR reference. This supports method-dependent codec behavior, not an SDXL causal comparison. |
| [MarkNull, arXiv:2608.10166v1](https://arxiv.org/html/2608.10166v1) | §5 specifies proxy latent optimization; §6.2 Assumption 2 requires compatible latent parameterization and discrete inversion. Appendix E.2 separately reports FLUX-to-SD2.1 experiments with fidelity costs. E1 correctly separates those empirical results from theorem applicability and does not inherit the paper's orthogonality-to-independence assertion. |
| [Behera accessible author manuscript](https://www.researchgate.net/publication/410879983_A_Rank-Ratio_Bound_for_Pixel-Space_Signal_Fragility_in_Latent-Diffusion_Autoencoders) | §V/Table 13 and the co-design limitation directly describe frozen-VAE co-design and SDXL transfer failure. This is real overlap, already acknowledged. I inspected the exposed author text, not the final publisher PDF; version equivalence remains unresolved. The live text retains provisional volume/header material while displaying the resolved DOI in footers. |
| [TIFS deep-learning submission guidance](https://signalprocessingsociety.org/sites/default/files/uploads/publications_resources/docs/Guidelines__deep_learning_submissions.pdf) | pp.1–2 distinguish reproducibility guidance from mandatory universal code release and give stronger expectations for negative results contradicting published research. This supports E2's qualified interpretation, not article acceptance. |
| [IEEE Access submission guidance](https://ieeeaccess.ieee.org/authors/submission-guidelines/) | Negative Result subsection admits nontrivial negative/null work when the question is meaningful and the study rigorous. It does not remove the contribution burden. |

No author response or correction verification has yet occurred at this reviewed snapshot. Subsequent verification, if requested, should be appended here without replacing the original findings.

## Same-reviewer correction verification — 2026-10-25

Reviewer: the same independent E3 agent. Verified the author working-tree corrections above HEAD `13f8d1e19d29c51ba5f3b8d631dab1fae75940e9`, including `article-drafts/review-response.md`. The original findings above are preserved as the review of the earlier snapshot. This appendix supersedes their open/closed status only. The check used local text reads, a bounded citation-key comparison, and the new SVG's source text. No scientific computation, new audit, protocol change, external execution or image rendering was performed.

**Updated verdict: ACCEPTED FOR AUTHOR DEVELOPMENT; B1 AND R1–R3 RESOLVED. NOT READY FOR SUBMISSION.**

| Finding | Same-reviewer verification |
|---|---|
| B1 | **Closed.** `venue-fit.md:37` now says “Decision reserved for the user” and explicitly leaves metric, reporting year and category unspecified. No approval or human choice is manufactured. |
| R1 | **Closed.** The amended mechanism, threat-model, README and venue prose uses predictor/model for the proposed scientific account. The supporting venue notes use the same terminology. Historical protocol identities and ordinary mathematical “laws” are not being silently rewritten. |
| R2 | **Closed.** `mechanism.md:89` places supported H1 and H2 under the same Holm family beside the H4 interpretation. The concluding paragraph and `venue-fit.md:45` preserve the common-floor restriction and deny encoder-only causal identification. No new hypothesis or criterion was added. |
| R3 | **Closed.** `mechanism.md:9` now distinguishes 58 complete source-median quality pairs from 56/58 retention transitions, identifies both quality references, keeps the post-hoc label and the two-source caliper limit, and removes the compressed .4 comparison. |
| Information-bound editorial note | **Addressed.** `mechanism.md:95–103` states nats, the population expectation, lack of automatic sourcewise guarantee and lack of mathematical-novelty or F5-theorem claims. The linked background arguments remain distinct from the local derivation. This verification does not re-audit their proofs. |

### Figure and caption verification

Inspected `article-drafts/figure-captions.md` and the actual source at `figures/transport-observation-map.svg` (the SVG is not located inside `article-drafts/`). Panel A's clean 60/60, SDXL-codec 55/60, full-SDXL 0/60 at each tested strength and SD1.5 .2 57/60 agree with the retained report used by this review. The caption distinguishes three-seed source majorities from one-output deterministic controls. The arrows branch from the marked input to different programs; there is no encoded claim that applying full regeneration to a previously codec-reconstructed output produced the reported counts. Both text and caption disclaim encoder-only causality.

Panel B is explicitly unmeasured, discloses C0/target-model information, and puts the complete forecast freeze before marked-target generation/release. It represents a prospective information flow, not observed transport or a validated causal diagram. During this check I flagged the generic “paired posterior draws” label because deterministic MoVQ has no such posterior. The author changed it to **“native mode or paired draws,”** and I verified the source correction at SVG line 53. The nontrivial H1/H2 guard remains in the caption. The contextual all-arm caption retains native endpoint differences, all four unequal clean-quality counts, the VINE threshold event and the absence of equal-FPR inference. These are adequate factual/caption qualifications.

This is a **source-text and scientific-caption check**, not visual rendering QA, a recomputation of plot values, or verification of a publication-ready layout. The existing all-arm SVG was not modified or visually inspected in this follow-up.

### Citation integration verification

Inspected `references.bib` and `bibliography-audit.md`, and independently compared Related-work citation syntax with BibTeX entry keys using PowerShell text parsing: **12 unique cited keys, 12 entries, zero missing keys, zero extra keys, zero duplicate keys**. This validates the claimed key integration for Related work; it is not a compiled bibliography or a claim that every prose URL in other sections is already in a final journal citation style.

The bibliography preserves version-qualified URLs/notes and the Behera, PhaseMark, original-SIH and SDXL identity/access limitations. I flagged one inherited malformed SDXL author accent. The author corrected the standalone entry and audit table to **Müller**, while documenting the formatting-only exception and leaving shared source bibliographies unchanged; this correction was verified. No additional final-version inspection or bibliographic truth certification follows from copying an entry.

### Source-access record for the literature log

**The initial E3 source check used direct URL opens and in-page `find` only. No search-engine `search_query` calls or discovery queries were made.** The six directly opened primary URLs are those listed in the preceding appendix: Stable Signature, LaWa, MarkNull, the accessible Behera author manuscript, TIFS guidance and IEEE Access submission guidance. Section/line opens were used to read the located method, experiment and policy passages.

For exact reproducibility, in-page find strings were: `same latent`, `E.2 Transferability`, `7.1`, `same auto-encoder`, `freeze`, `4.7 Learning`, `co-design`, `Table 13`, `frozen`, `Negative Result`, and `isotrop`. The `freeze` and `isotrop` searches returned no exact match; later passage reads, not those absent matches, supplied the evidence. These strings are page-local navigation, not literature-search queries. This correction-verification follow-up used **local files only**, with no new web access.

### Accepted residual limits and final disposition

W1–W4 remain accepted limitations, not findings erased by the corrections. The present contribution remains a scoped diagnostic case on a development cohort. Whether it contributes enough beyond close prior work for a journal remains unresolved. The manuscript is incomplete; the privileged predictor, new attacks and derivative feasibility are unmeasured; K3 is excluded from fitting but historically known; metadata freshness and source independence remain qualified. Native endpoints and clean qualities remain unequal, and T4/T5 or ownership security are not established.

The author response accurately records those limits. No new blocking article-frame defect remains in the checked integration. **E3 is complete for the author-development package.** Submission readiness, current-Q1 eligibility, authorship and publication decisions are not certified. Later server funding/approval and the exact Q1 definition remain user decisions. No further experiment, parameter adjustment or independent review is requested by this verification.
