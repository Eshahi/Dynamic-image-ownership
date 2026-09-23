# A2b research contract and requirement traceability

Status: **PLANNED research contract**, not preregistration, implementation, or evidence acceptance. Issue #4; source tasks `repair-2`, `contract-4`, `method-6`. Inputs: the unchanged 42-row `claims.csv`, A3 interfaces/notation/threat model, source proposal and extraction, current scope, and `approval-policy.md`.

## Authority and unchanged commitments

The original local `پروپوزال 2.docx` is identified by SHA-256 `15a02877be74f5118cc7b3d3ded9ab447cc07551773486264ac4755119adfeff`. Preserve both approved titles and all four research questions verbatim in `scope.md`; the matrix refers to the exact claim IDs and source locators rather than paraphrasing the questions as new commitments.

The method to investigate remains semantic and perceptual feature extraction, owner-bound semantic/instance signatures, diffusion latent/noise embedding, and lightweight image-domain 8x8 DCT detection. Its effectiveness is unproven. The three-week target is a usable research system with controlled initial results; it does not establish all hypotheses, dataset completion, or publication readiness by the deadline.

Final reference data commitments remain 1,000 MS-COCO images, DIV2K 800 training plus 100 validation images, and 5,000 DiffusionDB images. Their release identity, licenses, subset IDs, split counts and deduplication are pending A5/data specification. DIV2K's source split labels are not automatically the study's experimental train/test split. The proposal's hardware caveat is not permission for an unrecorded reduction.

The 32-image feasibility and up-to-300-image development pilots in the execution decision are development-only; they do not replace those reference counts or provide statistical power by assertion. Resized DIV2K pilots cannot support native-2K claims. Exact allocations and independent sample sizes belong to A4/preregistration.

Quality targets from the proposal remain PSNR >35 dB, SSIM >0.9, LPIPS <0.1. Their aggregation and final acceptance rule are still pending. No target is reported as achieved. Detection, owner attribution, instance binding, and semantic binding are distinct outcomes; no output establishes legal ownership.

## Matrix convention and coverage

`scope-matrix.csv` has the 14 prescribed fields. Its composite row key is `(requirement_id, input_route)`. It covers all 42 source IDs in 81 rows: two routes for each applicable requirement, except the three dataset commitments, which use only their relevant route. `real` refers to camera-originated source images; `generated` means pre-existing generated-image inputs from DiffusionDB, not an automatically approved prompt-only generation algorithm.

Each row preserves its exact `claims.csv` source locator. Semicolon-separated cells denote sets of components, candidate comparisons or controls. Baselines and metrics are proposed design mappings, not literature-verified selections or preregistered rules. Both status columns remain `PLANNED`; unresolved implementation prerequisites are recorded below instead of silently changing source commitments. Coverage does not mean satisfaction.

`evidence_path` names a **future** artifact, and none is claimed to exist. Scientific results are planned under ignored `outputs/planned/<experiment>/<route>/`; actual immutable run IDs/manifests must replace these planning locations before execution. Document reviews are planned under `research/planned/`. Existing specification files are not substituted for future evidence of effectiveness.

Titles, the broad ownership motivation, and narrative transfer (`TITLE-FA`, `TITLE-EN`, `SCOPE-01`, `SCOPE-03`) use `DOC-SCOPE`. They have a documentary fidelity/conflict check rather than an invented experiment, numeric performance metric, or synthetic control (`N/A_DOCUMENTARY`). `SCOPE-03` remains `BLOCKED_SCOPE` for operational transfer evidence. `NOVELTY-01` uses a source-comparison review; absence of a search result cannot prove novelty. All other requirements map to planned empirical families.

## Planned experiment and review registry

These identifiers are traceability groupings, not runnable jobs. A4 and the experiment design must define primary endpoints, margins, thresholds, sample sizes, independent units, multiplicity, seed inventory and stopping rules. A5 must establish implementable interfaces before method runs. Every family reports both supported and contradicted/inconclusive findings.

| ID | Question or obligation | Comparison and required evidence | Principal prerequisites |
| --- | --- | --- | --- |
| DOC-SCOPE | Preserve title/motivation, delimit ownership claims and resolve narrative transfer conflict | Source-to-contract review; no empirical efficacy claim or metric/control required | Institutional requirements if an amendment is needed; BLOCKED_SCOPE for transfer protocol. |
| DOC-NOVELTY | Inspect actual related work and novelty limits | Primary-source support/contradiction ledger and nearest-method comparison; inspected artifacts and access depth | B1 source work and independent evidence review. |
| EXP-SIGNATURE | RQ1/HYP1: stability and distinct-instance separation | Semantic-only, perceptual-only and combined signatures; C0,C1,C2,C4,C6; continuous matching/collision outcomes under T1,T5 | IO-01, IO-02; define legitimate edits, distinct instances and thresholds. |
| EXP-EMBED | RQ2/HYP2: latent versus spatial embedding under regeneration | Matched quality/attack conditions; C0,C1,C3,C6; per-component survival and false positives; disclose architecture differences | IO-03, IO-04; baseline compatibility and T3 protocol. |
| EXP-DETECT | RQ3/HYP3: detection performance and cost | Proposed detector versus a neural decoder for RQ3 and an inversion baseline for HYP3/METRIC-07; C0,C1,C2,C3; ROC/AUC, TPR/FPR, full-pipeline latency and memory | IO-04, IO-05; B1 baseline validation; fair input knowledge, hardware, timing and margins. |
| EXP-FORGERY | RQ4/HYP4: reject copy-paste attribution | T4 donor/recipient pairs with C0-C6, including no-transfer and binding-disabled comparisons; ACC/AUC and false attribution with Q,K | IO-02, IO-06; attack generation and target-quality admissibility. T6 spoofing is a separate access/control analysis, not pooled with T4. |
| EXP-QUALITY | Proposal image-quality commitments | PSNR, SSIM, LPIPS versus I, plus separately labeled matched reconstruction I_ref when available; C0,C1 | IO-03; pinned metric implementations, alignment/color policy; never hide reconstruction loss. |
| EXP-ROBUST | Proposal benign-transform/removal/regeneration commitments | T1,T2,T3 per-family and per-severity survival and quality against untouched marked outputs/compatible baselines; C0-C3 | IO-03..05; attack budgets/admissibility and validation-frozen rules. |
| EXP-DOMAINS | Data coverage, full pipeline and cross-domain generalization | Source/split/count audit and stratified results from **all applicable empirical families above** on both domains; same frozen method and controls | Dataset releases/IDs/licenses/deduplication/splits; existing-image route, model/config pins. |

The matrix's `GOAL-01` and `METHOD-01` entries use EXP-DOMAINS as this integrated acceptance family; a count report alone cannot establish end-to-end implementation. Dataset rows require provenance/count/split evidence and the applicable stratified performance results, not a claim that merely acquiring files proves generalization.

The neural-decoder comparison in RQ-03 and inversion-based comparison in HYP-03/METRIC-07 are separate comparator obligations. B2/A5 must select and justify both roles. A single baseline may cover both only if inspected implementation evidence shows that it actually satisfies both definitions; neither requirement can be dropped merely to reduce runtime.

## Open obligations and change authority

| Obligation | Source / A3 anchor | Next owner | Work blocked |
| --- | --- | --- | --- |
| Narrative dynamic ownership/transfer versus excluded implementation | TITLE-FA, TITLE-EN, SCOPE-03; approval-policy scope correction | Research contract and eventual user/supervisor decision if material | Transfer-protocol implementation and claims of implemented transfer; independent watermark work continues. |
| Feature shapes, preprocessing, stability/quantization and encoding | METHOD-02..05; IO-01, IO-02 | A5 and key implementation tasks | Scientific feature/key configurations and dependent experiments. |
| Real/existing-generated route and latent-to-image detector link | METHOD-06, METHOD-08; IO-03, IO-04 | A5/feasibility design | Claims of end-to-end feasibility or latent embedding success. |
| DCT channel/band/synchronization, score and presence witness | METHOD-08, METHOD-09; IO-05, IO-06 | A5 | Executable detector and copy-paste-specific labels. Candidate mismatch alone does not identify forgery. |
| Prompt-only signing order | IO-07 | A5; scope review if method changes | Prompt-only route; existing generated-image research may continue. |
| Dataset versions, study splits, test locking and licenses | DATA-01..03 | A5/data tasks, A4 for counts/power | Acquisition/use without defined provenance; final generalization claims. |
| Baseline identities, revisions and reproducibility | RQ-02, RQ-03, METRIC-07 | B1/B2 and A5 | Fair comparisons and novelty claims. SEAL is a cited candidate, not verified implementation. |
| Attack severities, attempts, Q,K and quality criteria | Threat scenarios T1-T6 | A5 and preregistration | Attack execution and security acceptance. Excluded T7-T9 stay outside initial claims. |
| Primary endpoints, practical margins, FPR, independent sample size and uncertainty | All RQs/HYPs/METRICs | A4 and experiment design | Confirmatory analysis/claims; no thresholds chosen from test outcomes. |
| Actual compute environment, resource estimate and execution authority | Approval policy | A6 and compute package | Scientific execution; routine document/software validation remains authorized. |

Routine technical choices inside these boundaries may proceed under delegated review. The [scope guard](scope-guard.md) defines changes requiring a new decision. The only scope-acceptance record is the delegated project decision; no supervisor-signed amendment or university acceptance is present. This document does not create one.

## Acceptance and continuation

A2b completion means exhaustive traceability, explicit unresolved work and faithful change boundaries. It does not mean every mapped experiment is executable or every claim has evidence. A3 is complete as a specification; A5 architecture and B1 literature work are ready next subject to their dependencies. The workflow remains paused at `evidence-review` until actual inspected-source work passes independent review. A2b approval cannot supply that missing evidence.
