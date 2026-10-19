# Manuscript table data from retained evidence

R8, 19 October 2026. **Documentary export only: no experiment, rescoring, new descriptor, new confidence-bound calculation, pixel access or public release.** These CSVs turn already corrected saved counts into portable manuscript-table inputs. They do not upgrade saved-aggregate checks into independent scientific reproduction.

The package has seven CSV files and 46 data rows. Fields retain evidence IDs, source aliases, JSON locators and scope qualifications. Use the accompanying [export provenance](export-provenance.json) for exact local input/output byte hashes, row counts, creation time and the dossier revision containing the inputs. Byte hashes describe those local serialized files; line-ending conversions during transfer require explicit normalization or fresh byte hashes, not a claim that scientific content changed.

## Files and manuscript use

| File | Rows | Use and interpretation |
|---|---:|---|
| [e1-recovery.csv](e1-recovery.csv) | 2 | Main E1 table and Figure 2: source-majority counts and previously calculated one-sided bounds. Same sources recur across checkpoints. |
| [e2-specificity.csv](e2-specificity.csv) | 5 | Main E2 table plus descriptive ambiguous panels: accepts, observed/planned comparisons, missingness and groups. Descriptive rows are explicitly not scored by E2. |
| [e2-accepted-pairs.csv](e2-accepted-pairs.csv) | 3 | Figure 4 accepted-pair detail only. These are not the distribution of all eligible negatives and not whole-pipeline forgeries. |
| [e3-attribution.csv](e3-attribution.csv) | 16 | Two arms in eight cells: all four owner-set outcomes, any-beta incidence, unavailable source count and incomplete-bank status. |
| [e3-owner-gate.csv](e3-owner-gate.csv) | 8 | Separate EV-77 post-hoc explanation: saved beta found/read flags; not a newly evaluated component arm. |
| [quality-summary.csv](quality-summary.csv) | 3 | Saved minimum/median/maximum metric values for available marks; no human quality judgment. |
| [quality-and-runtime-accounting.csv](quality-and-runtime-accounting.csv) | 9 | Quality with both denominators, journal outcome accounting and recorded duration/charge. Different rows have different units and must not be summed. |

These files cover the existing registry manuscript results and figure specifications. They do not supply a matched external comparator, component-study results, new population evidence, or graphics. Proposed F1/F2 rows must never be inserted as if observed.

## Exact source aliases and verification depth

- `J` = [01b-heldout-registry-recount.json](../01b-heldout-registry-recount.json), absolute path `C:/Users/Soroush/.codex/worktrees/codex-q1-research/research/q1-dossier-20261018/01b-heldout-registry-recount.json`.
- `O` = [01d-e3-owner-gate-counts.json](../01d-e3-owner-gate-counts.json), absolute path `C:/Users/Soroush/.codex/worktrees/codex-q1-research/research/q1-dossier-20261018/01d-e3-owner-gate-counts.json`.
- `J.run_root` names the original registry run; `J.scorer_json` names its retained scorer summary. The [ledger](../01-evidence-ledger.md) and [independent M2 review](../01b-heldout-registry-m2-review.md) state which measurements were recounted and which numerators were aggregate cross-checks.

Only J and O were parsed for this export. No raw retained result, descriptor cache, source image or model file was reopened to produce a new scientific decision. In particular, E1 success and E2 acceptance numerators retain their saved-aggregate limitation. The copied confidence bounds retain their earlier conditional sampling assumptions.

## Field mapping and production rules

**E1.** For each model, `successes` and `planned_sources` come from `J.E1[model].saved_endpoint`. The two lower-bound fields copy `CP_lower_95_recomputed` and `CP_lower_975_bonferroni_two_models`. The latter is the earlier two-model Bonferroni convention; it is not a new calculation or the only interval displayed. The frozen criterion indicator is `saved_endpoint.pass_`, not the overall experiment verdict. Majority means at least two of three scheduled seeds, with missing outcomes counted as misses (EV-50–52).

**E2.** Accept counts come from `J.E2.frozen.families[family].accepts`. Corrected unrelated denominators use `wrong_source_recount`, giving 3,343,081 observed of 3,408,600 planned and 65,519 unknown (EV-53). T4 uses `T4_recount`, giving 594 observed of 600 planned, six missing and 297 observed donor groups (EV-54); never substitute the frozen family's misleading zero missing count or 300 cluster count. Real eligible and ambiguous panels use their frozen family counts and shot grouping, cross-checked by the saved recount. “Planned or frozen eligible” is intentionally explicit: 45 is the eligible subset of the 60 real pairs, not the entire acquired real panel (EV-55/57/79). Group fields do not assert independent sampling; the real panels come from one film. Synthetic groups are administrative pair entries, not evidence of population independence.

**Accepted pairs.** Values copy `J.E2.lookalike_recount.accepted_pairs_psnr` and `frozen_cutoff`. Retain exact pair IDs, the descriptor-only scope and the frozen operational definition. No human judgment or new image-distance computation is represented (EV-55/56/71).

**E3.** Read the two named arms under `J.E3[cell].arms`; the separate `d1_only` arm is outside this main-table export. Only an omitted outcome key inside an existing attribution dictionary is rendered as zero, and only after verifying that its four categories sum to `evaluable_sources`. An absent dictionary or arm is an error, never zero. `beta_only` maps to `wrong_owner`; `any_beta` maps to `wrong_owner_present_including_ambiguity` and equals beta-only plus ambiguous. `unavailable_sources` is planned minus evaluable. `unknown_records_in_frozen_cell` counts records, not unavailable sources; it must not be used as a source denominator. The strict-bank flag is false throughout, as in the retained frozen verdict (EV-58–66/70/75).

Use cell order SD1.5 .2 exact/further, .4 exact/further, then SD2.1-base in the same order. Counts are conditional on the approved available-case rule. Missing competitor records remain unknown even for an evaluable source. The optional pointer upper bounds are copied only for pointer rows; blank fields for the fingerprint arm mean not supplied, not zero. Do not pool the repeated eight cells into a larger independent sample.

**Owner gate.** O supplies `planned`, `completed`, `missing_semantic`, `found`, `read` and `found_and_read`. Completed-call counts are checked against J's evaluable counts by cell. The zero beta flags explain rejection before q/content checks in the observed calls. They do not state what q or F would do if beta passed, and say nothing about unavailable calls (EV-77).

**Quality and runtime.** Continuous metrics copy `J.quality.summaries`; the three quality-accounting rows preserve 297/300 available marks, 291/297 strict-quality available marks, and 291/300 strict-quality attempted sources (EV-67/73/74). Strict quality remains descriptive, not a newly imposed registry endpoint. Journal outcomes use `J.journal.outcomes` and `unique_ids`: 53,053 completed, 53 scientific failures, 474 dependent unavailable, totaling 53,580 units (EV-69). Run seconds/hours and recorded USD copy `J.cost`; these describe the same historical run. Hours and seconds are alternative units, not additive costs. Recorded local USD 0 does not include hardware, electricity, labor or prior spending, and whole-run duration is not detector latency.

## Checks and remaining production work

The export checks the corrected E2 denominator identities, E3 four-way partitions and any-beta sums, and the J/O cell join. CSV row counts and local SHA-256 values are recorded. These are documentary integrity checks, not an independent milestone review or scientific validation. No thresholds, labels, source membership, native outputs or frozen endpoints changed.

A reusable standalone table producer and rendered figures remain unauthored. The transient PowerShell operation parsed documented JSON as data and exported CSVs; it is not a scientific entrypoint or execution contract. The [release inventory](../19-release-inventory/README.md) still governs rights and identity review before public sharing. The historical inventory's R57 future-production entry is now partially addressed by these CSVs; its reusable producer and graphics remain pending. The current package is local documentation, not a published artifact archive.
