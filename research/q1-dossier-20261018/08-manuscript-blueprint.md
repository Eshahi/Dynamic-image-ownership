# Manuscript blueprint and bounded draft prose

WP7, 18 October 2026. Author: Codex agent. **Working draft, not a submission-ready or human-approved manuscript.** Primary framing C and conditional TIFS destination follow [WP3](03-novelty-positioning.md) and [WP4](04-venues.md). Every local result below is linked to the corrected [evidence ledger](01-evidence-ledger.md). Citation keys refer to inspected V2 versions in `02-literature/references.bib`; a later journal version is not silently substituted. The independent WP9 review may require revisions.

## Title options

1. **From Watermark Recovery to Registered-Image Attribution: An Empirical Study Under Diffusion Regeneration** — preferred, makes the distinction the research question.
2. **Pointer-Assisted Attribution Under Passive Competing Enrollment: Recovery, Ambiguity, and Abstention** — narrower fallback; passive access appears in the title.
3. **When Regeneration Robustness Is Insufficient for Image Attribution: Evidence from a Frozen Registry Study** — negative-result emphasis; retain “a” to avoid claiming a universal impossibility.

Avoid “secure ownership,” “unforgeable,” “first hybrid,” “latent insertion,” and “independent-encoder robust” in the title.

## Structured abstract draft

**Problem.** Recovering a watermark after diffusion regeneration does not by itself establish that the recovered identifier belongs to the correct registered image. **Approach.** We study this distinction using an image-domain, encoder-directed watermark and a trusted registry of marked-image descriptors. A frozen evaluation separates regeneration recovery, record specificity, and passive competing enrollment. **Results.** On 300 held-out photographs, intended-record recovery by a majority of three seeds was 277/300 for SD1.5 and 280/300 for SD2.1-base at strength .2 (EV-50–51). The frozen descriptor check accepted 3/45 operationally different real look-alike pairs from 2/16 shots, so the overall confirmation failed (EV-55/70/71). Pointer-assisted attribution accepted no competing-owner record in eight conditional complete-case cells of 293–297 sources; the descriptor-only arm frequently accepted both owners (EV-58–66/75). These cells have incomplete banks and do not override the failed strict completeness gate. Stronger further regeneration retained the original owner for only 81/293 and 81/297 sources (EV-62/66). **Conclusion.** The results distinguish watermark recovery, record binding, ambiguity and abstention in one evaluated system. They support a bounded attribution study, not legal ownership or active-forgery security. Matched external controls and diverse fresh hard negatives remain necessary before a general comparative claim.

Editorial note: remove the final prospective sentence only when the required evidence exists and the abstract is rewritten to report it; do not turn a missing experiment into a completed result. The numerical conditions and registry side information must survive shortening. Abstract is under 250 words including EV annotations.

## Contribution bullets

- A frozen, explicitly scoped evaluation separates source-majority regeneration recovery, descriptor specificity and accepted-owner-set outcomes under passive competing enrollment (EV-50–75).
- A within-system pointer ablation exposes ambiguity and abstention alongside any-competing-owner acceptance, while preserving the incomplete-bank qualification (EV-58–66/70/75).
- A negative specificity result on operationally different same-shot pairs is reported together with unrelated/transfer negatives, availability and clustering, rather than replaced by the larger zero-error panels (EV-53–57/71).
- A reproducible interpretation distinguishes image-domain carrier evidence, declared registry side information and remaining proposal obligations. This is reporting discipline, not a new statistical estimator or security theorem.

These are candidate contributions. Their adequacy for TIFS depends on the scientific increments in F1/F2, and possibly F3/F4 according to the final claim. No acceptance probability is asserted.

## Section budget for a TIFS regular article

Plan within the current 13-page initial limit; word budgets are layout estimates, not publisher word caps. Tables, references and equations take space, so target about 6,500–7,000 main-text words and trim after typesetting. No TeX/PDF artifact is produced in this session.

| Section | Target words | Main job and evidence |
|---|---:|---|
| Abstract | ≤250 | Separate outcomes and preserve overall negative verdict; EV-50/51/55/58–66/70. |
| 1 Introduction | 700 | Motivate recovery versus attribution; identify precise empirical question and closest hybrids. |
| 2 Related Work | 900–1,050 | Existing-photo versus generation-time methods; registry prior art; copy/ambiguity attacks and evaluation standards. V2 keys below. |
| 3 Setting and threat model | 700 | Public owner-conditioned calls, trusted associations, marked references, passive enrollment, T3/T4/T5 and limits. WP5; EV-72. |
| 4 Evaluated system | 850 | RGB writer, carried q, candidate selection, exact D1/B1/fallback rule, all-owner outputs; source-function locators. |
| 5 Protocol and analysis | 950 | Split history, method selection, frozen thresholds, source-majority and negative definitions, complete-case amendment, clustering/multiplicity. EV-33/50–76. |
| 6 Results | 1,100 | E1 then E2 then E3 with availability; quality/cost; matched external results only if later obtained. EV-50–76; separate historical panel EV-01–43. |
| 7 Interpretation and limitations | 800 | What differs from recovery, what fails, partial banks, shared encoder ancestry, access and population limitations. |
| 8 Reproducibility, data and ethics | 300 | Actual artifact availability, licensing, no human ratings, no ownership adjudication. |
| 9 Conclusion | 150 | Bounded measured findings; no new claims or future results. |

Supplement: exact configuration/version table; per-cell owner sets and missingness; derivation of conditional bounds; full comparison-access table; detailed earlier-run provenance. Do not use a supplement to hide E2 or the failed strict E3 gate. TMM's four-page supplement limit requires a distinct shorter version; TOMM's current guide remains unverified.

## Figure and table plan

No plots, image composites or new visual ratings are created. The extension will supply exact file/field specifications.

| Item | Content and intended inference | Source |
|---|---|---|
| Figure 1 | System and endpoint diagram: RGB writer → marked-image enrollment; suspect → native pointer → candidate set → record check → accepted-owner set. Separate descriptor-only E2 from joint attribution. | WP5 equations and source functions; no empirical pixels. |
| Figure 2 | E1 source-majority proportions with one-sided lower bounds and attempt denominator; two models shown separately. | REG-E; EV-50–52; `01b-heldout-registry-recount.json`. |
| Figure 3 | E3 four-outcome stacked proportions, eight cells, pointer versus descriptor-only, with unavailable rows/bank status explicit. | Saved E3 sets in REG-E; EV-58–66/70/75; review recount. |
| Figure 4 | E2 panel distinguishing observed/planned comparisons, source/shot incidence, and operationally different look-alike failure; no million-trial binomial interval. | EV-53–57/71; review recount and count artifact. |
| Figure 5 | Evidence/claim map: recovery, content specificity, passive disambiguation and broader untested security. Alternatively a measured quality/cost panel if later F1 supplies a fair comparative trade-off. | EV-50–75, WP5; any cost view must preserve measured scope. |
| Table 1 | Closest-method setting, writer variable, attacker access, detector side information and measured endpoint. | V2 matrix/cards, WP3. Not a ranking of incomparable paper-reported numbers. |
| Table 2 | Frozen protocol, thresholds, seeds, sampling units and missingness policies. | REG-P/REG-G; EV-72; frozen files referenced by M2 review. |
| Table 3 | Main E1/E2/E3 endpoints with observed/planned counts and verdicts. | EV-50–76. |
| Table 4 | Quality, cost, storage and failure accounting, separating historical runs and cached operations. | EV-03–09/17/34/40–42/67–69/73. |
| Table S1 | Earlier F5/E3 comparisons and post-hoc no-exact-H sensitivity. | F5-R/E3-R/E3-S; EV-01–35. Not pooled with registry results. |

## Draft Related Work

Watermark recovery and image attribution ask related but different questions. A detector may establish that a signal is present, recover a payload, or associate a query with stored content. These outcomes depend on distinct side information and error events. For existing photographs, a post-hoc writer changes an already available image; a generation-time system instead controls some part of synthesis. This distinction matters when interpreting robustness, training access and detector cost. Our study concerns post-hoc images and a declared registry, and therefore does not treat all watermarking results as interchangeable attribution evidence.

Post-hoc learned systems already provide substantial robustness and payload functionality. StegaStamp encodes identifiers for photographs subject to physical recapture [@Tancik2020StegaStamp]. RoSteALS uses a frozen autoencoder with learned latent offsets and an image decoder [@Bui2023RoSteALS]. VINE uses generative priors and staged training to address image editing, with evaluation designed around that setting [@Lu2025VINE]. Watermark Anything extends watermarking toward localization and multiple regions [@Sander2025WAM]. These systems establish that learned visual channels and useful identifiers precede the evaluated carrier. Their bit or detection metrics, however, do not directly estimate acceptance of a competing registered record under our enrollment procedure.

VAE-aware construction is also established prior art. FreqMark optimizes frequency perturbations of an encoded latent and extracts using fixed feature directions [@Guo2024FreqMark]. SimuFreeMark processes low-frequency image content through a frozen VAE, inserts a learned latent residual and restores high-frequency content before image-domain decoding [@tang2025simufreemark]. These mechanisms differ from optimizing RGB pixels against an encoder-space objective, but the difference alone does not demonstrate a superior or more general principle. A method-level claim would require controlled comparisons and causal evidence. We instead treat the encoder-directed writer as the evaluated component of a broader attribution experiment.

Generation-time watermarks set a different boundary. Tree-Ring and Gaussian Shading organize initial noise or latent distributions, while Stable Signature and AquaLoRA modify components of the generative pipeline [@wen2023treering; @yang2024gaussianshading; @fernandez2023stable; @feng2024aqualora]. Their assumptions about model control, inversion or decoder access cannot be transferred without qualification to arbitrary existing photographs. Nor does using DCT features somewhere in a model-dependent pipeline establish a lightweight, model-free detector. We distinguish the writer's optimized variable, its objective space and the verifier's computational dependencies throughout.

Regeneration attacks show why recovery requires its own evaluation. Zhao et al. analyze removal through noisy representations and derive conditional detection limits [@zhao2024provablyremovable]. A bound becoming weak in a high-gain watermark direction does not prove survival through denoising. WAVES emphasizes evaluation across attack conditions, and CtrlRegen and UnMarker broaden the mechanisms and access models used to stress watermark robustness [@an2024waves; @liu2025ctrlregen; @kassis2025unmarker]. Such work motivates careful fidelity and attack-budget reporting. It does not make nominally equal diffusion strengths equivalent across models, or establish that two checkpoints with shared encoder ancestry provide independent-encoder evidence.

Registered content and hybrid verification are direct antecedents to our setting. Roy and Chang combine physical marking with stored index/message information [@roy2004retrieval]. DREW routes watermark information into database-assisted embedding retrieval and evaluates diffusion purification [@saberi2024drew]. The published TrustMark paper explicitly discusses checking a recovered fingerprint or thumbnail to address identifier spoofing [@Bui2025TrustMark]. SynthID-Image also describes acceptance based jointly on a correct payload and a stored embedding [@gowal2025synthidimage]. Consequently, neither an identifier linked to a record nor a watermark–fingerprint conjunction is our architectural contribution. Our narrower question is what a frozen system's accepted-owner sets reveal under a specified passive competing-enrollment procedure.

Zero-watermarking further limits broad novelty claims about content registration. It stores content-derived evidence without necessarily inserting a physical carrier. Rel-Zero, for example, registers stable patch relations and evaluates generative transformations, under its own representation and null-model assumptions [@chen2026relzero]. The distinction from a physical pointer is operational: pointer eligibility can restrict which records are considered, whereas a content-only matcher relies on the registered representation. Whether that restriction improves attribution at useful recovery is an empirical question. Registration itself neither establishes rightful creation nor guarantees separation of regenerated copies from visually similar, independently captured instances.

Copy detection provides relevant representations and challenging negatives. SSCD separates shared-source copies from nearby video frames, making it a principled reference for instance-level retrieval [@pizzi2022sscd]. DELG combines local and global features for retrieval [@cao2020delg], while the recent soft-binding benchmark examines watermark/fingerprint complementarity and false bindings to near copies [@kazempourradi2026softbindings]. These results motivate stronger controls, but do not guarantee that adding geometric verification improves a particular operating point. A benchmark's retrieval score, modeled false-positive threshold or oracle combination is not automatically the risk that any false record is accepted from a registry after candidate selection.

Attribution ambiguity and copy attacks also have a long history. Craver et al. analyze conflicting ownership claims and invertibility, and Kutter et al. study copying watermark evidence [@craver1998ownership; @kutter2000copy]. Modern diffusion-watermark forgery work demonstrates that attack access must be specified rather than inferred from a method's name [@muller2025forgery; @jain2025single]. Passive enrollment of a regenerated image does not give the attacker the same capabilities as active re-marking or detector-guided optimization. Our accepted-owner-set endpoint includes simultaneous acceptance of the original and competing owner, while distinguishing ambiguity from a unique wrong-owner assignment.

Finally, provenance standards and statistical practice constrain interpretation. C2PA's soft-binding framework and NIST's synthetic-content guidance situate watermarking within a larger evidence system [@c2pa24contentcredentials; @chandra2024nist1004]. They do not make a perceptual match a legal ownership judgment. Reusing sources, references and video shots creates dependence that a large pair count cannot remove; exact binomial intervals require a specified unit and sampling model [@brown2001binomial; @cameron2015cluster]. We therefore report recovery, specificity, ambiguity, abstention and unavailable outcomes separately. The intended contribution is a bounded empirical account of their interaction, with matched controls and broader hard-negative evidence identified as remaining requirements.

## Draft Threat Model

The publisher produces a marked version of an existing photograph using a public owner identifier and the fixed F5 r2 profile. The registry preserves owner–record associations and stores descriptors of the marked image. It is trusted for record integrity and availability reporting; it does not certify that an enrolling party created an image or holds legal rights. A competing party may submit a derived image under its own identifier without modifying the original record. Ownership transfer, rights ledgers and policy enforcement are outside the evaluated system.

The verifier performs owner-conditioned native detection and code recovery, selects records whose carried code lies within Hamming radius six, and applies the frozen record check. It retains every accepted owner, including ambiguous multi-owner outcomes. The reference check uses D1, the native fine-detail descriptor, and B1, a centered normalized gray-layout vector. A valid native D1 abstention invokes the stricter B1 fallback; an absent cached artifact instead produces an unknown outcome. These descriptors are detector side information, and neither is the proposal's CLIP-plus-pHash signature (EV-72; WP5).

T3 comprises the specified nonadaptive diffusion-regeneration channel. The primary endpoint is intended-record acceptance for a majority of three scheduled seeds at strength .2, with unavailable outcomes retained as misses. T4 transfers a marked donor's residual to a different recipient, with access to both the clean and marked donor. T5 evaluates unrelated and same-shot negative content. The real-pair negative definition is frozen gray PSNR below 18.126065828471827 dB; it is an operational criterion derived from development regeneration, not a human-validated identity relation (EV-50–55/72).

In passive competing enrollment, the second party regenerates the marked image, computes its own owner-conditioned record code and enrolls the resulting content without adding a new watermark. Queries are that image or a specified further regeneration. An error occurs whenever a competing-owner record is accepted, including acceptance alongside the original owner. We report abstention separately because zero false attribution alone can be achieved by rejecting every query. Complete-case observations do not establish results for absent records in an incomplete bank (EV-58–66/70/75).

Active re-marking, arbitrary public-writer forgery, adaptive detector queries, robustified encoders and optimized attacks are not evaluated. Public owner-profile derivation is not secret-key authentication. Our results therefore concern the stated channels and enrollment procedure, with conditional empirical uncertainty; they imply neither cryptographic unforgeability nor legal ownership.

## Draft Limitations

The complete frozen confirmation failed. E1 met its source-majority recovery criterion, but E2 accepted three operationally different real pairs, and the strict E3 bank-completeness gate remained false (EV-50–55/70/71). The approved pre-result complete-case reading provides a conditional view of available E3 outcomes; it does not change the frozen artifact. Missing cross-source competing records can suppress observed errors, so a zero complete-case count cannot certify a complete registry.

The positive and negative populations are narrow. The held-out recovery cohort contains 300 DIV2K photographs, and the eligible real look-alikes arise from 16 shots in one film (EV-50/55). Shared sources, repeated seeds, reused records and neighboring frames preclude treating every comparison as independent. The millions of scored unrelated comparisons measure workload and observed matches, not millions of independent opportunities from a target population (EV-53). Conditional source/shot intervals do not remove all bank or production-level dependence.

The evaluated channels do not establish broad encoder transfer. SD2.1-base is an unseen diffusion checkpoint, but the inspected architecture evidence identifies shared SD1.x encoder ancestry. Different full-VAE file hashes do not prove independent encoder weights. Higher strength and further regeneration also lead to substantial abstention, which must be interpreted jointly with the zero observed competing-owner count (EV-62/66; Q-VAE).

The record rule is a particular implementation and includes a one-descriptor fallback. Its failure does not establish that robust instance verification is impossible. Conversely, increasing descriptor complexity or adding geometry is not a demonstrated remedy. The descriptor-only ablation is not a matched external baseline. Current evidence therefore supports one system's operating point rather than a general comparison across watermark–fingerprint methods.

Quality thresholds are objective metrics, not human judgments. Of 297 available marks, 291 met every strict quality bound; three further marking attempts were unavailable, and human visual ratings were not collected (EV-67/73). Historical costs involve different workloads and sometimes different hardware. Cached lookup latency excludes feature extraction and cannot substantiate end-to-end lightweight verification (EV-17/34/41). Finally, passive enrollment does not cover active re-marking, and record integrity does not establish truthful ownership claims.

## Draft reproducibility, data and ethics statements

**Reproducibility.** The evidence is linked to exact retained run IDs, frozen configuration files, saved endpoint outputs and a versioned source repository. The registry study is `registry-div2k300-confirm-01`; earlier F5 and E3 studies remain separately identified in the ledger and are not pooled. This dossier independently recounted availability and saved E3 owner sets and cross-checked saved E1/E2 acceptance aggregates; it did not rescore images. The future artifact package should expose scripts, configuration hashes, aggregate tables, source-group identifiers, model revisions and a clear missingness schema. `TODO:EVIDENCE` — public archival DOI, release contents, reproducible environment and reviewer-access route have not been finalized.

**Data availability.** Current COCO and DIV2K test pools have been used and will not serve as untouched validation for a modified verifier. Existing image and model licenses govern redistribution; an accessible source URL is not a blanket release permission. Planned future sources and license checks are specified in WP6, but no fresh cohort has been acquired or certified in this session. `TODO:EVIDENCE` — final per-asset rights and release manifest require a later authorized packaging review. Only aggregate results are described here; no held-out images were inspected for this dossier.

**Ethics and interpretation.** Owner labels denote experimental identities, not verified persons or legal title. The work studies recovery and attribution errors and makes no accusation against real claimants. It does not implement ownership transfer or rights management. Human visual or identity judgments are absent unless separately collected under an approved procedure; metric thresholds must not be presented as such judgments. Safety blocks and missing outcomes remain reported. Any later adversarial evaluation must preserve declared access, quality conditions and responsible artifact-release decisions.

## Cover-letter key points, conditional on a completed manuscript

- The question is whether regeneration recovery supports reliable registered-image attribution under explicitly declared side information and enrollment access.
- The article preserves a failed confirmation and separates recovery, specificity, accepted-owner ambiguity, abstention and availability.
- Closest hybrid antecedents are acknowledged; no identifier/registry architecture priority is claimed.
- Fit with TIFS is information forensics and security evaluation. The evidence increment over one system must be established before submission.
- `TODO:EVIDENCE` — completed matched controls/fresh negatives, author approval, originality/concurrent-submission declaration, conflicts/funding and actual artifact access. Do not assert these administrative facts on the user's behalf.

## Claim provenance inventory

| Claim ID / kind | Author | Evidence and exact run/source | Permitted interpretation |
|---|---|---|---|
| MS-01 result | Codex agent | EV-50/51, `registry-div2k300-confirm-01`, REG-E and M2 review | Source-majority recovery at .2, all attempts retained. |
| MS-02 result/limitation | Codex agent | EV-55/71, same run, REG-E/REG-R | Frozen descriptor-only look-alike endpoint fails; not three full-pipeline forgeries. |
| MS-03 result/limitation | Codex agent | EV-58–66/70/75, same run, saved E3 owner sets and review recount | Conditional any-beta comparison and abstention; strict bank gate false. |
| MS-04 result/limitation | Codex agent | EV-53/54, same run, review availability recount | Zero observed unrelated/transfer accepts with missing comparisons and dependent units. |
| MS-05 method | Codex agent | EV-72; REG-P/REG-G; WP5 source-function locators | Image-domain writer, trusted marked-image descriptors, exact conditional rule. |
| MS-06 interpretation | Codex agent | Q-VAE primary SDXL source and local hash records | Shared encoder ancestry; no independent-encoder demonstration. |
| MS-07 result/limitation | Codex agent | EV-67/69/73, registry saved outputs | Attempt-level quality and unavailable outcomes; no human imperceptibility claim. |
| MS-08 interpretation | Codex agent | V2 DREW, TrustMark final, SynthID, soft-binding benchmark | Architecture novelty pre-empted; bounded empirical question remains conditional. |
| MS-09 future work | Codex agent | WP6 F1–F7, no run IDs | NOT RUN; no reported success or authorization. |

This inventory is local draft traceability. It does not modify the protected thesis claim ledger or record a lifecycle/human acceptance decision.
