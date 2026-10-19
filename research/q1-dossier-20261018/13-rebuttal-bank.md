# Prepared responses to fifteen likely reviewer objections

Prepared 2026-10-19 for extension E3. This is an internal drafting bank, not a submitted rebuttal or a record of an actual review. Responses describe only the evidence and manuscript drafts presently in this dossier. They must be checked against the eventual submitted version. No experiment, baseline implementation, threshold change, human approval or public release is promised as completed. The evidence ledger and its missingness qualifications control every numerical statement.

**Use rule.** A defensible limitation does not necessarily resolve a rejection-level objection. Each entry therefore states both a usable response and its remaining consequence. W = writing; A = permitted desk analysis already performed; E = future experiment, not authorized here; S = scope restriction. F1–F7 and N1–N10 refer to `07-gap-closure-plan.md`. Reference keys resolve in `02-literature/references.bib`; E2 audited their bibliographic identities without upgrading unread papers to V2.

## 1. The watermark-plus-registry design is already known

**Objection.** DREW, TrustMark and SynthID-Image already combine a watermark with stored content information. What is the new contribution?

**Prepared response.** We agree that a watermark used with a content registry is not an architectural novelty. DREW provides a watermark-assisted retrieval system, final TrustMark describes fingerprint/thumbnail integration, and SynthID-Image discusses joint payload and stored-embedding verification. Our proposed framing is an empirical distinction between surviving-mark recovery and registered-image attribution under explicitly specified competing-enrollment and look-alike conditions. The existing study documents a successful recovery endpoint alongside a failed hard-negative endpoint, incomplete-bank constraints and an owner-gate explanation for a passive competing-enrollment result. We do not claim that these observations establish a superior system or the first registry design.

**Disposition.** W/S addressed in the draft; scientific contribution remains conditional on F1/F2. A case study of one's own system may still be insufficient for TIFS. Do not answer with a novelty claim about merely combining components.

**Evidence.** EV-50–58, EV-77; `03-novelty-positioning.md`; `11-draft-sections.md`; `saberi2024drew`, `Bui2025TrustMark`, `gowal2025synthidimage`.

## 2. The zero-beta result is explained by owner detection alone

**Objection.** The wrong owner never passes the watermark detector. Your experiment cannot show that the record code or content verifier prevents its acceptance.

**Prepared response.** That interpretation is supported by the saved outputs. Our post-hoc Boolean audit finds beta `found` and `read` false in every completed E3 query, across cells with 293–297 sources. Consequently, beta is rejected before the record-code and content checks. We now treat the zero-beta observation as a property of the evaluated full policy in this passive scenario, not an identified benefit of adding the record code or verifier. The fingerprint-only contrast simultaneously removes multiple conditions and cannot estimate their individual contributions. No new owner-only experimental arm was run during this audit.

**Disposition.** A/W correction complete; component-effect claim unavailable. F1 now also requires readable-code-plus-owner-plus-verifier as an intermediate control, so the primary Full-versus-ORVF contrast removes only code-distance selection. Full versus owner-plus-verifier conflates reading and matching. Multiple records per owner, same-owner confusions and paired recovery/error tradeoffs remain necessary; the [future contract](23-component-study-contract.md) makes these requirements precise. No added code benefit is established.

**Evidence.** EV-77; `01d-e3-owner-gate-audit.md`; `10a-review-response.md`; F1.

## 3. The nearest baseline is being evaluated under a different contract

**Objection.** Calling DREW a baseline is misleading if you change its enrollment, fallback or decision rule to fit this system.

**Prepared response.** We agree. The dossier does not report a completed DREW comparison. Its future comparison specification separates native DREW from a labeled adaptation. Native DREW enrolls marked records, returns a top-one result or rejection, and can fall back to a global fingerprint search when watermark decoding is unreliable. Our passive-beta scenario includes an unmarked competing record, our decision is a set of all accepted owners, and the pointer condition is mandatory. These differences are part of the evaluation contract. An unsupported scenario must be reported as not applicable, and a changed fallback, enrollment rule or output semantics must be identified as an adaptation rather than silently assigned to the original method.

**Disposition.** W/S specification complete; E comparison remains absent. External baseline work is currently closed by the user's earlier decision and requires explicit reopening. This bank does not reopen it.

**Evidence.** `saberi2024drew`, especially method and retrieval policy; F1 comparison contract; `10a-review-response.md`.

## 4. Passive enrollment is not an active forgery attack

**Objection.** An attacker could re-mark the regenerated image, exploit public owner strings, or optimize against the detector. Your experiment does not test this.

**Prepared response.** Correct. The retained E3 scenario enrolls a regenerated derivative for beta without demonstrating an active beta re-marking attack. It evaluates passive competing enrollment under a fixed trusted-registry policy. The implementation's public owner identifier is not a secret cryptographic key, and the record does not demonstrate authentication against an adaptive adversary. We distinguish this scenario from active residual-copy, re-marking and encoder-aware attacks. T4 additionally grants access to the clean donor, which must be stated when interpreting its copy-transfer outcomes. No claim of lawful ownership, unforgeability or resistance to all ownership attacks follows from the present results.

**Disposition.** S/W defensible only with a narrow title and claims. F4 is required for broader security claims. Citations to known forgery work establish relevance, not resistance of our implementation.

**Evidence.** EV-54, EV-58–66, EV-77; `05-theory-security.md`; C3 cards; F4.

## 5. Incomplete banks invalidate an unqualified E3 pass

**Objection.** The strict experiment gate is false. Why does the article say the competing-enrollment result passed?

**Prepared response.** It should not say that without qualification. The strict complete-bank E3 gate remains false because every bank is incomplete. We preserve the approved pre-result complete-case reading separately: zero beta acceptances are observed in each of eight cells, with 293–297 completed sources, while unavailable cases remain unknown. This reading does not turn missing records or blocked regenerations into successful rejections. The overall registry confirmation is negative because E2 fails, irrespective of the qualified E3 observation. Both the strict gate and conditional interpretation are retained in the evidence ledger and proposed reporting layout.

**Disposition.** W/A reporting correction complete. Completeness of a future bank is an F2 prerequisite. A reviewer may reasonably require a new complete-bank result before accepting the intended general claim.

**Evidence.** EV-53–54, EV-58–70; `01b-heldout-registry-m2-review.md`; `01b-heldout-registry-recount.json`; F2/F7.

## 6. Millions of pairs are not millions of independent trials

**Objection.** The unrelated-pair false-positive rate appears overprecise because many comparisons share sources and records.

**Prepared response.** We report zero accepts among 3,343,081 observed comparisons, with 65,519 planned comparisons missing. This count describes exposure, not an independent Bernoulli sample of that size. Queries and records are reused, and incomplete banks further condition the estimate. A source-level descriptive bound is more transparent: zero observed source-level events among 300 source groups gives a one-sided 95% upper bound of about 0.994%, conditional on the observed calls and the sampling assumptions. It does not certify the missing comparisons or a universal population rate. The look-alike and transfer analyses likewise report shot and donor grouping rather than treating every pair as independent.

**Disposition.** A/W correction complete. F5 addresses narrower future rate targets only if sufficient independent source groups and an appropriate sampling design are available. Do not infer an ultra-low false-positive guarantee from the pair count.

**Evidence.** EV-53–56; `05-theory-security.md`; F2/F5.

## 7. Your fingerprint baseline's main failure is ambiguity, not unique beta

**Objection.** Reporting only unique wrong-owner calls hides cases where both alpha and beta are accepted.

**Prepared response.** We retain the accepted-owner set and distinguish alpha only, beta only, alpha plus beta, and neither. Any set containing beta is an attacker-acceptance event for the stated error criterion, even when alpha is also accepted. The fingerprint-only policy often accepts both owners; its unique-beta counts alone therefore understate this criterion. For example, the eight complete-case cells contain 263–297 any-beta events, which include both unique-beta and ambiguous decisions. We do not silently replace the set-valued policy with an argmax, and comparisons with methods that return a top-one result must preserve their native output semantics.

**Disposition.** W/A correction complete; native-contract comparison remains F1. Ambiguity is an outcome to expose, not a favorable tie or an automatic successful attribution.

**Evidence.** EV-59–66, EV-75; `01-evidence-ledger.md`; `05-theory-security.md`.

## 8. Zero wrong-owner acceptances may be obtained by abstaining

**Objection.** Security claims omit lost coverage and present an unusable reject-everything policy as robust.

**Prepared response.** Correct attribution and non-attribution must be reported together. At strength .4 after further regeneration, original-owner attribution is 81/293 on SD1.5 and 81/297 on SD2.1-base, with the remaining completed cases yielding neither owner under the pointer policy. The same cells' zero beta acceptances do not imply reliable recovery. The proposed figures present complete outcome partitions and unavailable cases, so the reader can see the tradeoff directly. At strength .2, E1 separately reaches 277/300 and 280/300 under its fixed source-majority criterion; these are different endpoints and cannot be substituted for E3 coverage.

**Disposition.** W/A resolved as reporting; performance remains limited. F1's proposed benefit criterion includes a recovery noninferiority condition, preventing a claimed improvement from being obtained only by more rejection. Its proposed margin is not a retrospectively passed gate.

**Evidence.** EV-50–52, EV-62, EV-66; F1.

## 9. Three look-alike accepts are a failure, and PSNR is not identity

**Objection.** The E2 result undermines instance verification. A gray-PSNR cutoff does not establish semantic or legal distinctness.

**Prepared response.** E2 fails its frozen operational criterion: three of 45 eligible real look-alike pairs are accepted, involving two of 16 shots from one film. Their gray PSNR values are approximately 16.89, 17.24 and 17.68 dB, below the fixed 18.126 dB operational boundary. We use that boundary to describe the registered test, not to define semantic identity or legal ownership. These are descriptor-only acceptances; a whole-pipeline watermark forgery was not demonstrated. The narrow corpus and shot dependence also prevent estimating a broad rate for natural near duplicates. We preserve the negative result and do not repair it by moving a threshold on the evaluated pairs.

**Disposition.** S/W honest reporting complete; F2 is submission-critical. F6 is only a conditional future verifier repair with separate development data, not evidence that a repair will work.

**Evidence.** EV-55–57, EV-71–72; F2/F6.

## 10. SD2.1 does not establish independent-autoencoder transfer

**Objection.** The encoder family is shared or closely related. The unseen-regenerator result may be much narrower than stated.

**Prepared response.** We use “unseen diffusion checkpoint.” Primary SDXL documentation distinguishes SD2.x decoder fine-tuning within the earlier autoencoder lineage from an SDXL autoencoder trained from scratch. The local SD1.5 and SD2.1 serialized VAE files have different hashes, but that does not prove that their encoder tensors differ. No tensors were loaded in this research-only session. Consequently, the result is not evidence of transfer to an independently trained encoder or to an encoder deliberately robustified against the writing direction. SDXL is a motivated candidate for a later independent-encoder check, subject to a fixed protocol and available resources.

**Disposition.** W/S correction complete. F3 is necessary for the broader transfer claim; a new model label alone is insufficient. The original result still measures the specified SD2.1 pipeline.

**Evidence.** EV-33–35, EV-50–51; `02-literature/Q-VAE.md`; F3.

## 11. F5 is neither direct latent insertion nor a lightweight extractor

**Objection.** The method name and thesis motivation overstate what was implemented.

**Prepared response.** F5 modifies RGB pixels using gradients through an encoder, with an objective expressed in latent DCT coordinates. That is an image-domain, encoder-directed writer. Expressing the objective in a latent space does not make the optimized variable a latent inserted directly into the generator. The registry verifier also uses neural features and stored records; it is not a model-free or lightweight DCT-only extractor. The manuscript draft states these dependencies, and the thesis alignment file leaves the original latent-insertion, lightweight-extraction and CLIP-plus-pHash hypotheses open. The registry development amendment does not silently satisfy or rewrite those original obligations.

**Disposition.** W/S addressed. Thesis scope or objective amendments require the user and supervisor; no approval is fabricated. This is separate from the question of whether the bounded empirical article has value.

**Evidence.** `09-thesis-alignment.md`; `11-draft-sections.md`; source code locators therein; EV-07–09, EV-40–42.

## 12. Pointer capacity and conjunction do not prove security

**Objection.** Your collision bound assumes uniform independent bits, and multiplying watermark and verifier error rates is unjustified.

**Prepared response.** We do not present the idealized 32-bit calculation as an empirical entropy estimate. The decoder's real code distribution, error tolerance, owner context and registry size determine the relevant risk; semantic construction can make idealized assumptions unsuitable. Likewise, the pointer and content checks operate on the same image and need not be independent. Without justified independence, a conjunction's error probability is bounded by the smaller marginal error probability, not their product. Our security section therefore gives conditional statements and explicitly separates toy capacity calculations from measured behavior. Registry integrity is assumed, while truthful enrollment and lawful ownership are not established by a successful match.

**Disposition.** W/S corrected. A stronger cryptographic claim would require a different, explicit threat model and proof or evidence. It is outside the currently supported contribution.

**Evidence.** `05-theory-security.md`; C8 theory cards; EV-72, EV-77.

## 13. Quality, failures and latency are selectively reported

**Objection.** Clean quality excludes failures, human ratings are absent, and cached timing conceals actual verification costs.

**Prepared response.** We distinguish availability from conditional quality. In the registry run, 297 marks are available and 291 satisfy all strict clean-quality gates: 291/297 available marks, or 291/300 attempts. Human visual ratings are missing. The journal also records three marking failures and 50 safety-blocked regenerations, whose dependent outputs cannot be counted as successful results. Timing reports state their measurement boundaries: historical embedding/detection measurements, cached registry lookup and feature extraction are different quantities. We do not call cached lookup an end-to-end cold-query benchmark, or compare measurements from different hardware and protocols as a controlled speedup.

**Disposition.** W/A correction complete. F7 keeps availability explicit; any new timing or human assessment is future work. The current evidence supports only the recorded conditions.

**Evidence.** EV-07–09, EV-34, EV-40–42, EV-67–74; `01-evidence-ledger.md`.

## 14. Literature access, versions and reproducibility remain incomplete

**Objection.** Some closest journal papers were not read in full, and a polished bibliography does not ensure a complete novelty assessment or reproducible artifact.

**Prepared response.** We agree. V2 denotes inspected method and evaluation content; V1 does not. The dossier lists consequential access gaps rather than inferring results from abstracts. E2 cross-checks publication identities, preserves inspected preprint versions and logs discrepancies with final metadata; this does not upgrade an unread final article. Similarly, frozen configuration hashes and saved-output paths support provenance of the retained study, but do not by themselves constitute a tested public reproduction package. No public release, license clearance, anonymous artifact or third-party reproduction is asserted. Broad novelty statements remain conditional on closing the identified literature gaps.

**Disposition.** W/A audit complete within access limits; missing evidence remains material. Retrieve the specified full texts lawfully and prepare a release only under later authorization. Do not substitute a citation count for reading the closest work.

**Evidence.** `02-literature/access-refresh/access-gaps.md`; `02-literature/C4-zero-watermarking/cards/access-gaps.md`; `02-literature/matrix.csv` V1 rows; `12-bibliography-audit.md`; `10a-review-response.md`; `08-manuscript-blueprint.md`.

## 15. A negative result on one implementation is not yet a Q1 contribution

**Objection.** The observed limitations may be implementation-specific. What would make this more than an unsuccessful method paper?

**Prepared response.** That is the central unresolved editorial risk. Our current recommendation is not to submit on writing improvements alone. A useful empirical paper needs a precise externally relevant proposition, compatible reference methods and enough independent data to distinguish an informative negative result from an underpowered test. F1 specifies a component question and an outcome map before future results: support, refutation of a prespecified useful increment, or unresolved evidence. F2 supplies diverse fresh hard negatives and complete banks for the corresponding interpretation. A repeated failure without precision or external relevance would not become a contribution merely by relabeling it a boundary study.

**Disposition.** E remains submission-critical. TIFS is conditional; TMM/TOMM are alternatives subject to fit and verified institutional ranking rules. Venue guidance about negative results is not a promise of acceptance. The user and supervisor retain the thesis and submission decisions.

**Evidence.** `03-novelty-positioning.md`; F1/F2; `04-venues.md`; `10-independent-review.md`; `FINAL-REPORT.md`.

## Decision map for using this bank

| Objections | Present usable resolution | What remains before a stronger answer |
|---|---|---|
| 1–3, 15 | Narrow contribution; identify owner-gate confound; specify native comparison contracts | F1 with compatible external evidence and informative precision; user must reopen closed baseline work |
| 5–9 | Preserve strict/conditional gates, clusters, ambiguity, abstention and the E2 failure | F2 diverse fresh data and complete banks; F5 only if a narrower risk target is needed |
| 4, 10 | Restrict attacker and transfer scope | F3/F4 if the article claims independent-encoder transfer or active security |
| 11–12 | Correct method terminology and conditional mathematical claims | Supervisor decisions for thesis amendments; no unsupported cryptographic claims |
| 13–14 | Transparent quality, timing, versions and missingness | Access/release work; later human assessment and any new measurements explicitly unperformed |

No response in this bank changes a frozen endpoint, excludes a failed seed, treats missingness as rejection, or turns a future study into completed evidence.
