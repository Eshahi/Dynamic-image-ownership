# Specifications for the five main figures

Extension E5, 19 October 2026. These are production specifications only: no figure, plot, image, detector output or new experimental result was generated. They implement the five-figure plan in `08-manuscript-blueprint.md`. Retain EV tags through manuscript review. The present case study and its negative confirmation govern the design; proposed future results must not be drawn as observed data.

## Shared source and rendering contract

`D` = `C:/Users/Soroush/.codex/worktrees/codex-q1-research/research/q1-dossier-20261018/`.
`W` = `C:/Users/Soroush/.codex/worktrees/codex-q1-research/`.
`R` = `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/registry-package/artifacts/M1b-test/registry-div2k300-confirm-01/`.

`J` denotes `D/01b-heldout-registry-recount.json`; `O` denotes `D/01d-e3-owner-gate-counts.json`. JSON paths below use quoted dictionary keys where a slash occurs. The original source for J is `R/metrics/endpoints.json`, the saved scorer JSON named in `J.scorer_json`, and `R/outputs/journal.jsonl`; O names that journal in its `source` field. J's E1/E2 accept numerators are saved-aggregate cross-checks, not independent image rescoring. J's availability and E3 sets, and O's saved native Booleans, were recounted as specified in their provenance fields. Use the corrected recount, not unqualified frozen totals.

Later production should use vector PDF/SVG with embedded fonts and legible 8–9 pt labels at final size. Target 178 mm width for Figures 1, 3 and 4; 86 mm for Figures 2 and 5 if labels fit. Use a white background, direct count labels, no gradients, 3D effects or decorative photographs. Encode alpha-only in blue, beta-only in vermilion, ambiguity in purple, abstention in gray and unavailable observations with diagonal hatching. Every distinction must also have text/pattern support for grayscale and color-vision accessibility. Do not let color alone communicate a scientific verdict.

No pooled confidence interval across repeated models, strengths or seeds. Conditional binomial limits do not establish representative sampling or independence. Render one-sided bounds as such, not as symmetric error bars. This specification does not authorize plotting now or accessing pixels later without an appropriately scoped task.

## Figure 1 — What the evaluated system observes and decides

**Question:** What does a registered-image attribution use beyond a recovered mark, and where can it abstain?

**Type/layout:** Two-lane vector flow diagram, about 178 × 80 mm. Upper lane: source RGB `x` and public owner `a` → F5 RGB optimization through pinned VAE encoder → published mark `w` → enrolled record. Lower lane: suspect `y` and candidate owner → native `found/read/qhat` → owner/code-eligible record set → descriptor rule → accepted-record set → accepted-owner set. Join the trusted record store to code eligibility and descriptor comparison with labeled dashed side-information arrows. Place the registry trust boundary around records only; do not imply authenticated or truthful enrollment.

**Exact record label:** `record_id, owner, q, D1(w), B1(w), profile/version`. Public owner-derived patterns are not a secret key. The writer changes RGB pixels; the VAE is an objective/extraction dependency, not an asserted original-generation insertion point.

**Decision labels:** `P = found AND read AND Hamming(qhat,q) <= 6`; `F = (D1 >= 0.0594367 AND B1 >= 0.90)` when valid D1 similarity exists, or `B1 >= 0.99` for a valid native D1 abstention. An absent required artifact exits to **unknown**, not to the fallback. Final records satisfy `P AND F`; all accepted owners are retained. Draw a separate descriptor-only branch labeled E2 / fingerprint-only, so its failures are not visually presented as full-pipeline forgeries.

**Inputs/locators:** `D/05-theory-security.md` §§1–3; EV-72/77; `W/scripts/f5_latent_codec.py`; `W/scripts/m1b_registry_analysis.py` functions `native_q`, `qmatch`, `attribution`, `scenario`; `W/scripts/claude_round3_two_factor.py` function `rule`. These are code-text locators, not commands to execute. The present worktree has these files; MAIN does not have these script paths.

**Required callouts:** “Trusted registry is additional detector side information”; “Registration does not prove lawful ownership”; “E3 beta owner detection already fails in completed calls (post-hoc EV-77).” The last annotation belongs beside the gate, without a causal-effect arrow claiming q or F adds rejection.

**Caption draft:** “The evaluated image-domain writer and registry-assisted decision. Owner-conditioned recovery and code eligibility precede a frozen content check. The verifier preserves accepted sets, ambiguity, abstention and unavailable evidence. E2 evaluates descriptor specificity separately; E3 uses passive competing enrollment without beta re-marking.”

## Figure 2 — Source-majority attribution at strength .2

**Type/layout:** Horizontal dot-and-one-sided-lower-limit plot, two rows: SD1.5 then SD2.1-base. X axis 0–1, label “Source-majority success proportion”; include a dashed line at the fixed .85 lower-bound criterion. Put `277/300` and `280/300` beside their respective points. Use a solid one-sided 95% lower segment and a distinct open endpoint for the Bonferroni two-model 97.5% lower limit; label the legend with the actual confidence convention. No upper error segment is estimated or implied.

| Data item | Exact field in J | Expected value |
|---|---|---|
| Numerator | `E1[model].saved_endpoint.successes` | sd15 277; sd21 280 |
| Denominator | `E1[model].saved_endpoint.n` | 300 each |
| Plotted point | numerator / denominator | 0.923333…; 0.933333… |
| Per-model lower limit | `E1[model].CP_lower_95_recomputed` | 0.893130493; 0.904598024 |
| Two-model lower limit | `E1[model].CP_lower_975_bonferroni_two_models` | 0.887181885; 0.898914355 |
| Evidence scope | `E1[model].verification_level` | Saved-aggregate cross-check, not rescoring |

Model keys are exactly `sd15` and `sd21`. The .85 criterion and threshold of 266 successful sources come from EV-52 and the frozen plan; do not infer them by optimizing the current figure. The event is at least two of three scheduled seeds, with unavailable outputs counted as misses. No binomial transformation from these majority proportions to single-seed accuracy is valid without additional assumptions. The same 300 sources appear in both rows; do not add an independent-sample significance comparison.

**Caption draft:** “The fixed strength-.2 source-majority endpoint meets its .85 one-sided lower-bound criterion for both checkpoints. Points and count labels use all 300 attempted sources, including unavailable outputs as misses. Bounds are conditional binomial summaries; the two rows reuse sources. SD2.1-base is an unseen diffusion checkpoint, not demonstrated independent-encoder transfer (EV-50–52; Q-VAE).”

## Figure 3 — Competing attribution, ambiguity and abstention

**Type/layout:** Two panels, SD1.5 and SD2.1-base, each with four ordered cell groups: `.2/exact_copy`, `.2/further_regeneration`, `.4/exact_copy`, `.4/further_regeneration`. Within each group place two horizontal 100% stacked bars, `pointer_registry` then `fingerprint_only`. Use the four observed outcomes in the shared palette. A separate right-hand hatched gutter reports unavailable count / 300 and “bank incomplete”; missingness is not a fifth observed attribution outcome. X axis is explicitly “Share among evaluable sources in this cell.”

**Fields:** For full cell key `c`, use `J.E3[c].planned_sources`, `.evaluable_sources`, `.arms[a].attributions`, `.arms[a].wrong_owner_present_including_ambiguity`, `.unknown_records_in_frozen_cell`. Outcome keys are `original_owner_unique`, `wrong_owner`, `ambiguous_owners`, `no_attribution`. An absent outcome key is zero only within an existing, complete attribution-count dictionary whose counts sum to `evaluable_sources`; absence of the entire arm or data artifact is an error, never zero. Available-case proportions divide by `evaluable_sources`. Gutter count is `planned_sources - evaluable_sources`. Do not reinterpret `unknown_records_in_frozen_cell` as a source count.

| Cell order | n | Pointer: alpha / beta / ambiguous / none | Fingerprint: alpha / beta / ambiguous / none |
|---|---:|---|---|
| sd15/.2/exact | 294 | 280 / 0 / 0 / 14 | 0 / 1 / 293 / 0 |
| sd15/.2/further | 294 | 242 / 0 / 0 / 52 | 0 / 8 / 285 / 1 |
| sd15/.4/exact | 294 | 201 / 0 / 0 / 93 | 0 / 28 / 266 / 0 |
| sd15/.4/further | 293 | 81 / 0 / 0 / 212 | 0 / 75 / 188 / 30 |
| sd21/.2/exact | 297 | 282 / 0 / 0 / 15 | 0 / 1 / 296 / 0 |
| sd21/.2/further | 297 | 249 / 0 / 0 / 48 | 0 / 7 / 289 / 1 |
| sd21/.4/exact | 297 | 199 / 0 / 0 / 98 | 0 / 31 / 266 / 0 |
| sd21/.4/further | 297 | 81 / 0 / 0 / 216 | 0 / 75 / 190 / 32 |

The table abbreviates display labels only; JSON keys contain `0.2`/`0.4` and full scenario names. Draw a bracket over beta-only plus ambiguous segments, labeled “any accepted beta.” This prevents presenting only the 75 unique-beta outcomes as the complete comparison. Do not include `d1_only` in the main figure; it is a distinct supplementary ablation.

**Mandatory gate strip:** Match `O.cells[*].cell` to `c`. Display `found = 0`, `read = 0`, `completed = n`, with `missing_semantic = 0`. Title the strip “Post-hoc saved-call explanation, not a new arm.” It shows why the whole-gate comparison cannot identify incremental q/content rejection. Do not infer what the q or F decision would have been when those components were never reached.

**Caption draft:** “Complete-case owner-set outcomes under passive regenerate-and-enroll. Ambiguity includes the competing owner and counts toward any-beta acceptance. All frozen banks are incomplete: the strict E3 gate remains false, while the approved pre-result reading permits these conditional descriptive counts. Beta fails the native owner gate in every completed call (EV-77), so the comparison does not isolate q/content value. The eight cells repeat source groups and are not pooled.”

Use EV-58–66/70/75/77. Do not put confidence whiskers on every stacked segment or claim simultaneous success from zero bars. Optional caption bounds must use the saved per-cell fields `pointer_zero_error_CP_upper_95_per_cell` and `pointer_zero_error_CP_upper_bonferroni_eight_cells`, explicitly conditional on evaluability.

## Figure 4 — Specificity failure and observation coverage

**Type/layout:** Three panels across a double-column figure, about 178 × 85 mm. A is a count/coverage table graphic; B is a paired-unit incidence graphic; C is a horizontal dot plot of the three accepted eligible pairs' PSNR. No pixel examples are used.

**Panel A, coverage:** Draw two labeled rows without a shared “number of independent trials” axis. Unrelated: `J.E2.wrong_source_recount.planned_pairs = 3,408,600`, `.observed_pairs = 3,343,081`, `.unknown_pairs = 65,519`. Add a small breakdown from `.missing_by_cause.record_missing = 33,825`, `.query_missing = 31,433`, `.query_and_record_missing = 261`; these disjoint fields sum to the unknown total. State `.fully_observed_sources = 0` and `.sources_with_any_unknown_pair = 300`. T4: `J.E2.T4_recount.planned = 600`, `.observed = 594`, `.observed_donor_clusters = 297`; missing is six from three donors. Both available accept numerators are zero, from `J.E2.frozen.families.wrong_source.accepts` and `.T4.accepts`. Do not use frozen `.wrong_source.n` as the observed denominator or frozen `.T4.cluster_n` as the observed donor count.

**Panel B, hard negatives:** Two clearly separated glyph rows, “3 accepted / 45 eligible pairs” and “2 affected / 16 shots, one film.” Fields are `J.E2.lookalike_recount.accepted_pair_count_from_saved_ids`, `.different_pair_count`, `.accepted_shots`, `.different_shots`. The one-film scope comes from EV-55 and the reviewed source report. Optional text: “conditional shot-level one-sided 95% upper limit 0.343825,” from `.CP_upper_95_shots`; this does not remove film/shot dependence or establish population representativeness. Do not display the naive pair bound as the primary uncertainty.

**Panel C, selected failures:** Three dots from `J.E2.lookalike_recount.accepted_pairs_psnr`, keyed by exact pair ID; values are 17.237954, 17.675129 and 16.892173 dB. Use a nonzero detailed x range, for example 16–19 dB, visibly labeled. Draw a vertical eligibility cutoff at `.frozen_cutoff = 18.126065828471827`. Label “Accepted pairs only; not the distribution of all 45 pairs.” The cutoff defines operational negative eligibility, not a watermark quality requirement or human identity verdict.

**Caption draft:** “The frozen descriptor endpoint fails on three operationally different real look-alike pairs from two shots of one film, despite zero available unrelated and transfer accepts. Missing comparisons and shared sources prevent interpreting millions of pairs as independent trials. These descriptor-only accepts are not demonstrated whole-pipeline forgeries (EV-53–57/71).”

Synthetic ambiguous pairs and the 15 operationally ambiguous real pairs belong in the table/supplement, labeled descriptive; do not silently merge them into the 45 eligible negatives.

## Figure 5 — Which claims the evidence supports

**Type/layout:** Qualitative evidence-to-claim matrix, six rows and three columns: “Observed evidence,” “Permitted statement,” “Unresolved extension.” Use words and distinct line styles, not numerical heatmap values, readiness scores or an invented confidence scale. About 86 × 110 mm, expanding to double-column width if text would fall below 8 pt.

| Row | Evidence fields / EV locators | Permitted statement and unresolved extension |
|---|---|---|
| Recovery | J `E1.sd15/sd21.saved_endpoint`; EV-50–52 | Fixed strength-.2 majority recovery; broader channels and independent encoders unmeasured. |
| Instance specificity | J `E2.lookalike_recount`; EV-55/70/71 | Frozen descriptor endpoint fails; diverse fresh hard negatives and a changed verifier are future work. |
| Passive competition | J `E3`; EV-58–66/75 | Conditional zero-beta whole-gate result with abstention; full-bank and active security unestablished. |
| Component attribution | O `cells[].found/read/completed`; EV-77 | Owner gate already rejects beta; added q/content value not identified. |
| Quality and resources | J `quality.strict_old_quality_gate_count`, `.available`, `.planned`, `.status`; `cost.saved_run.duration_seconds`, `.usd`; EV-67–69/73/74 | Summarize measured scope only: 291/297 available marks meet strict quality, 291/300 attempts; human ratings absent. No matched speed superiority. |
| Thesis / security scope | `09-thesis-alignment.md` OBJ/RQ/HYP map; `05-theory-security.md` §§1–4 | Image-domain registry-assisted study; original latent insertion, lightweight extraction, lawful ownership and cryptographic security remain unfulfilled or outside scope. |

The row labels and judgments are editorial mappings from the ledger, not additional statistical measurements. Exact E1/E2/E3 numbers should remain in Figures 2–4; Figure 5 carries their implications. Mark unresolved items as “not tested” or “not identified,” not as observed failures. Use “failed frozen endpoint” only where the evidence actually establishes that verdict.

**Caption draft:** “Evidence and claim boundaries of the frozen case study. Recovery, specificity, passive competition and component effects are separate questions. Writing and source verification do not substitute for the proposed fresh comparisons. The current evidence supports a bounded empirical account, not a secure-ownership or new-hybrid-architecture claim.”

## Later production acceptance checks

1. Match each field and count above to the committed J/O artifacts and ledger; stop on missing data or changed schema. Preserve the historical/frozen versus corrected-recount distinction.
2. For every E3 bar, verify four outcome counts sum to its evaluable n, and beta-only plus ambiguity equals the saved any-beta field. Gutter counts must bring evaluable plus unavailable to 300, without turning incomplete-bank status into rejection.
3. Keep source, pair, shot and donor units explicit. No interval derived from 3.34 million supposedly independent comparisons; no pooled eight-cell denominator.
4. Check grayscale, label size, axis labels, count labels and caption limits at final manuscript size. Keep the negative overall verdict, owner-gate caveat and missingness visible in the main figures.
5. Record any later production script and its input paths in the future manuscript artifact package. This session created specifications only; it did not implement or run that production step.

