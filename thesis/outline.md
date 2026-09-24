# Thesis outline for Dynamic Image Ownership With Robust Neural Watermarking

Status: **working outline, not a completed thesis or an approved university format**. Issue #13 (B6), source tasks `write-1` and `repair-6`. The four questions and both proposal titles remain authoritative in [`research/scope.md`](../research/scope.md); this outline maps them to chapters without rewriting the approved questions or treating hypotheses as findings. Apply the [`research contract`](../research/research-contract.md), [`scope guard`](../research/scope-guard.md), and [`approval policy`](../research/approval-policy.md) when drafting. The official university thesis template has not been identified or supplied, so this file must not be taken as a formatting approval.

## Front matter

- University-required title and approval pages: pending official template and institutional details. Retain the approved Persian and English titles exactly as recorded in `research/scope.md` until a material title change is authorized.
- Abstracts and keywords in the languages required by the university: write only after results and claims are audited. State negative or inconclusive findings plainly.
- Acknowledgments, contents, lists of figures/tables, abbreviations, and any declarations: include only as required by the verified university guide.

## Chapter 1 Introduction and research contract

1. Motivation: limitations of image watermark robustness and owner attribution; distinguish a technical watermark decision from legal ownership proof.
2. Problem, approved scope, four research questions and corresponding falsifiable hypotheses. Reproduce the exact Persian questions from `research/scope.md` in the final thesis; an English explanation may accompany them but must not replace them.
3. The proposal's narrative dynamic-ownership/transfer language versus the approved execution boundary. State that a transfer/ledger protocol is not implemented; do not claim that this resolves the institutional scope question.
4. Contributions **only as supported by completed evidence**; do not preannounce novelty or successful robustness.
5. Chapter map and terminology.

## Chapter 2 Background and related work

1. Image watermarking, existing-image versus prompt-only generation, and detector knowledge/access models.
2. Semantic and perceptual signatures, pHash, CLIP, image-domain DCT, diffusion latent/noise manipulation, and their distinct roles.
3. Inspected prior work and comparator families from the source/claim ledgers. Separate neural-decoder and inversion-based comparator obligations; do not represent a document-only baseline registry as reproduced performance.
4. Threats and limitations: benign edits, regeneration, copy-paste transfer, spoofed public OwnerID, and semantic collisions. Distinguish the permitted T1–T6 study from excluded or untested attacks.
5. Evidence-supported research gap. Preserve contradictory findings and inaccessible-source limits.

## Chapter 3 Method and implementation

1. Input, owner identifier, fixed configurations, canonical image handling, and the existing-image route.
2. Semantic/perceptual extraction, owner-bound semantic and instance signatures, serialization and candidate enumeration.
3. Proposed key-derived initial-noise/latent embedding through the image-conditioned diffusion path. Describe the exact implemented path and its failure/quality guards, not a substituted pixel-domain method.
4. Image-domain 8×8 DCT template construction, scores, common-candidate rule and error/unsupported states.
5. Controls, ablations and baselines. Keep oracle/reference-assisted routes visibly separate from blind core detection.
6. Software/model/data provenance, deterministic settings, hardware/resource envelope, safety components and known custody/rights limits.

## Chapter 4 Experimental design and data

1. Dataset releases, licenses, source IDs, integrity hashes, grouping/deduplication and frozen development/validation/test splits. Preserve the proposal's MS-COCO, DIV2K and DiffusionDB final commitments unless an authorized amendment is recorded.
2. Preregistered endpoints, thresholds, sample units, uncertainty intervals, multiplicity, stop rules and negative-result policy.
3. C0–C6 controls and T1–T6 attack families, access assumptions, severity/attempt budgets and quality admissibility.
4. Quality (PSNR, SSIM, LPIPS), owner/signature/detector outcomes, continuous ROC/AUC, full-pipeline latency and memory; state denominators and invalid/failed-run accounting.
5. Exact run manifests, seeds, code/environment/model hashes, local versus approved remote compute, and analysis provenance.

## Chapter 5 Results

Organize by the approved questions, not by whichever result appears strongest. For each, report all preregistered controls and failed/missing runs before interpretation.

1. **RQ1:** signature stability under legitimate edits and separation of distinct but semantically similar images, including semantic-only and perceptual-only ablations.
2. **RQ2:** latent/noise versus spatial embedding under matched regeneration and quality conditions; distinguish a failed latent-to-DCT bridge from a successful image-space comparator.
3. **RQ3:** image-DCT detector accuracy and full verification latency against a neural decoder, with a separately labeled inversion comparison where required by the proposal's efficiency hypothesis.
4. **RQ4:** original versus copy-paste-forged image/owner attribution under declared attacker access, including binding-disabled and no-transfer controls.
5. Cross-domain strata, quality/resource limits, sensitivity and failure inventory. Do not pool incompatible controls or routes.

## Chapter 6 Discussion, limitations and conclusions

1. Answer each RQ with effect estimates, uncertainty and an explicit supported, contradicted or inconclusive status.
2. Evaluate construct validity, data/licensing restrictions, model-source custody, hardware fit, public OwnerID spoofing, threshold transfer and external validity.
3. Separate technical mark detection from ownership authentication or legal title; state the unresolved dynamic-transfer narrative honestly.
4. Reproducibility package, what can be released under actual licenses, and concrete future work.

## Back matter

- References from verified primary-source records; exact citation style remains pending the university guide.
- Appendices as needed for specifications, preregistration, run manifests, hashes, extra tables, failed-run logs and audit trail. Keep private/restricted materials and model/dataset bytes out of a public repository unless release rights are established.

## Evidence-to-chapter handoff

| Chapter | Required project evidence before final prose |
| --- | --- |
| 1 | `research/scope.md`, `research/research-contract.md`, `research/scope-guard.md`, approved claim ledger |
| 2 | Inspected paper cards, literature matrix, claim-to-source ledger and comparator access/status records |
| 3 | Reviewed A5 method, implemented code/tests, A6 environment/model receipts and explicit unresolved boundaries |
| 4 | Reviewed A4 protocol, B3/B4 manifests/splits/rights, frozen run and analysis manifests |
| 5 | Complete run inventory including failures, reproducible analysis outputs and independent results review |
| 6 | Claim-level evidence audit and final user/institutional acceptance decisions where required |

This map is a drafting dependency, not evidence that those deliverables already exist. No experimental or publication claim is accepted by creating the outline.
