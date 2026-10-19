# Manuscript continuation: protocol, results, discussion and conclusion

Author working draft, Codex agent, 2026-10-19. Continues Sections 1–4 in [11-draft-sections.md](11-draft-sections.md). This is research-only writing after the original session deadline, explicitly requested by the user. No new experiment, analysis of image content, threshold revision or publication approval is represented here. The manuscript remains scientifically incomplete for the proposed Q1 submission.

EV identifiers point to the [evidence ledger](01-evidence-ledger.md), whose source index resolves the retained reports and artifacts. They are editorial provenance markers to retain during review and later convert into appendix/table references. Tables below transcribe saved results and previously checked counts. They do not replace missing individual decision rows with reconstructed outcomes.

## 5. Evaluation Protocol and Analysis

### 5.1 Development history and confirmation cohort

We distinguish method development from the final registry confirmation. The earlier F5 and E3-S1 studies evaluated image-domain watermark constructions and their predecessor comparator. A subsequent development comparison selected F5 under a fixed strength-.2 rule: E3 needed an advantage of at least three sources on the development panel to replace it, whereas both methods recovered checked semantic information on all evaluated sources. This decision does not establish equivalence between the methods, and a different result at stronger regeneration did not change the declared selection criterion (EV-33–35). Registry development then changed the content-verification rule before the final confirmation. Its earlier unsuccessful and successful rounds remain development evidence; they are not combined with the final cohort (EV-36–39).

The registry confirmation, `registry-div2k300-confirm-01`, uses the admitted 300 DIV2K test sources. The real look-alike panel contains 60 pairs from 20 further eligible shots of Tears of Steel, with eligibility and temporal offsets fixed before the outcomes. Its remaining connection to the development negatives is the same underlying film. A separate synthetic panel is reported descriptively. Earlier confirmations consumed all 600 admitted COCO test groups, so they cannot supply fresh confirmation for subsequent method revisions (EV-79). The cohort was held out at the time of the completed run; it is now consumed evidence and must not be reused as an untouched test set.

Both regeneration channels use the declared DDIM20 image-to-image configuration, empty prompt, guidance 1 and scheduled seeds 15, 16 and 17. Strengths .1, .2 and .4 are recorded, with .2 defining the primary recovery endpoint. SD1.5 retains its safety checker; the SD2.1-base configuration does not use that checker. T4 transfers a donor's marked-minus-clean residual to the scheduled recipient at scales .5 and 1.0 in fixed cyclic source order (EV-68/78). These settings define the tested channels. A numerical strength shared by different checkpoints is not a claim that they induce equal perceptual distortion.

The registry stores descriptors of the published marked reference and supplies additional trusted information to the verifier. The descriptor-only comparison uses the same available bank and the same content predicate. It removes pointer eligibility; it is not an external fingerprint method and does not remove the registry. Passive competing enrollment supplies a beta record for a regenerated copy without adding a beta watermark. Its exact-copy and further-regeneration queries test that specific enrollment scenario, rather than active beta re-marking or adaptive optimization.

### 5.2 Frozen endpoints and availability

E1 is intended-record acceptance at strength .2 for a majority of the three scheduled seeds of a source. Every planned source remains in its denominator; marking failures and unavailable regenerations count as misses. The frozen criterion requires at least 266 of 300 sources and a one-sided 95% Clopper–Pearson lower bound of at least .85 for each checkpoint (EV-50–52). It does not require success on every seed or every source.

E2 requires zero observed false accepts in the scored negative families. Real look-alike eligibility uses the frozen gray-PSNR distance rule, not a retrospective visual judgment. The rule leaves 45 real pairs across 16 shots in the scored negative panel. The remaining real pairs and the synthetic panel remain reported separately. The real look-alike stress test evaluates the content predicate without requiring a watermark pointer; a false acceptance there violates E2 but is not itself an end-to-end forgery (EV-55–57/71/72/76).

E3 reports accepted owner sets after passive competing enrollment. Any accepted beta record is an error, including simultaneous alpha and beta acceptance. Original-only acceptance, beta-only acceptance, ambiguity and no acceptance must remain separate outcomes. The pointer-assisted rule is compared with descriptor-only matching on the corresponding saved records. The displayed best record does not replace these set-valued decisions.

Operational failures made the strict bank-completeness conditions false. A contemporaneous, documented user-approved amendment, recorded before descriptor scoring and endpoints, therefore adds a conditional reading while retaining the automated verdict (EV-80). E1 is unchanged. E2 reports existing comparisons and missing comparisons separately. E3 is evaluable when its query and the source's own original and competing records are available, with the required native calls and code information. Other unavailable competitor records still limit interpretation: removing an absent record may remove an otherwise accepted competitor. The amendment does not establish outcomes for those absent records (EV-53/54/58–70).

### 5.3 Uncertainty and verification depth

The primary unit is a source for recovery and attribution, not a seed call. Shared queries, reference records, film shots and repeated regeneration cells create dependence. We report the two checkpoint-specific E1 bounds separately. They use a binomial model for hypothetical exchangeable independent source outcomes; neither the admitted cohort nor the shared registry establishes random sampling from every image population. Their interpretation is consequently narrower than a universal robustness guarantee.

The negative families require additional caution. Millions of query–record comparisons are not millions of independent trials. T4 reuses donor groups. The real look-alike panel has shot-level clustering within one film, and E3 repeats the same sources across cells. The count appendix provides conditional source- or shot-level bounds where their assumptions can be stated. We do not pool repeated cells or use a pairwise rare-event bound as population certification. A zero count with incomplete banks is not an observed zero across all scheduled negatives.

Verification of this report also has a boundary. E1 acceptance numerators and E2 false-accept numerators were cross-checked between saved aggregate outputs. The inspected artifacts do not contain all corresponding individual joint-decision rows, so these numerators were not independently regenerated. Availability denominators and E3 owner sets were recounted from retained structured outputs. A separate post-hoc count inspected already-saved native Boolean fields to locate the beta rejection stage (EV-77). It created no new score, descriptor or owner-only experimental arm.

## 6. Results

### 6.1 Confirmation verdict and recovery

The complete frozen confirmation fails. E1 satisfies its numerical criterion, but E2 records false acceptances among eligible real look-alikes. The automated E2 and E3 verdicts also remain false because of incomplete inputs and banks. The approved availability reading supports conditional reporting; it does not turn the experiment into an overall pass (EV-70).

| Primary E1 channel | Successful sources / planned sources | One-sided 95% lower bound | Frozen numerical criterion |
|---|---:|---:|---|
| SD1.5, strength .2 | 277/300 | .893130 | Met |
| SD2.1-base, strength .2 | 280/300 | .904598 | Met |

Source: EV-50–52. A source succeeds on at least two of its three scheduled seeds; unavailable outputs remain misses. These results establish recovery on the specified cohort and channels with a trusted registry. SD2.1-base is an unseen diffusion checkpoint for the writer, but its encoder ancestry does not establish independent-encoder transfer; the dedicated [VAE lineage note](02-literature/Q-VAE.md) states the inspected evidence and its limits.

### 6.2 Specificity and missing negative comparisons

| E2 negative family | Observed false accepts / evaluable comparisons | Planned comparisons | Missing comparisons | Grouping or scope |
|---|---:|---:|---:|---|
| Unrelated query–record pairs | 0/3,343,081 | 3,408,600 | 65,519 | Reused sources and records; every query bank has gaps |
| T4 residual transfers | 0/594 | 600 | 6 | 297 observed donor groups; two transfer scales |
| Eligible real look-alikes | 3/45 | 45 eligible of 60 real pairs | 0 eligible pairs | Failures in 2/16 eligible shots of one film; descriptor-only check |

Sources: EV-53–56/71/79. The unrelated comparison count is the observed denominator, not the larger planned denominator. The six missing T4 transfers stem from three unavailable marked donors. The accepted real pairs have saved gray-PSNR distances of approximately 16.89, 17.24 and 17.68 dB, all below the frozen different-image cutoff. Their eligibility cannot be changed because the descriptors accepted them.

This is a specificity failure under the operational definition of differentness. It neither supplies human validation of that definition nor proves that the three pairs would pass the full pointer-assisted verifier. Both qualifications matter: requiring a pointer after observing these failures would change the endpoint, while describing them as three full-pipeline forgeries would overstate what was tested. The ambiguous real panel records two accepts among 15 pairs and the synthetic panel four among 12; they remain descriptive under the frozen classification (EV-57/76).

### 6.3 Passive competing enrollment and abstention

Table 3 preserves the complete owner-set accounting. Here “exact” means the query is the beta-enrolled regenerated copy, not the original unmodified source. “Further” means the scheduled further regeneration of that copy. All counts are conditional on the approved available-case rule. Pointer beta-only and ambiguous outcomes are zero in every displayed cell; fingerprint original-only outcomes are zero. Fingerprint “any beta” is the sum of beta-only and ambiguous outcomes.

| Checkpoint / strength / query | Evaluable / planned | Pointer original only | Pointer none | Fingerprint both owners | Fingerprint beta only | Fingerprint none | Fingerprint any beta |
|---|---:|---:|---:|---:|---:|---:|---:|
| SD1.5 / .2 / exact | 294/300 | 280 | 14 | 293 | 1 | 0 | 294 |
| SD1.5 / .2 / further | 294/300 | 242 | 52 | 285 | 8 | 1 | 293 |
| SD1.5 / .4 / exact | 294/300 | 201 | 93 | 266 | 28 | 0 | 294 |
| SD1.5 / .4 / further | 293/300 | 81 | 212 | 188 | 75 | 30 | 263 |
| SD2.1-base / .2 / exact | 297/300 | 282 | 15 | 296 | 1 | 0 | 297 |
| SD2.1-base / .2 / further | 297/300 | 249 | 48 | 289 | 7 | 1 | 296 |
| SD2.1-base / .4 / exact | 297/300 | 199 | 98 | 266 | 31 | 0 | 297 |
| SD2.1-base / .4 / further | 297/300 | 81 | 216 | 190 | 75 | 32 | 265 |

Sources: EV-58–66/75. The fingerprint comparison's beta-only count reaches 75, but this alone understates the declared error, which also includes ambiguity. Conversely, an ambiguous result does not mean the implementation silently chose beta. Both interpretations are avoided by retaining the owner sets.

The pointer-assisted rule has no observed beta acceptance in these evaluable cases, but this accompanies substantial abstention. At strength .4 with further regeneration, only 81/293 and 81/297 queries retain original-only attribution. Zero competing attribution therefore cannot be read independently of recovery. Moreover, every strict bank remains incomplete: the conditional counts say nothing definitive about matches to absent competing records.

The saved native beta calls provide a further explanation. In every completed E3 call, both `semantic.found` and `read` are false for beta before code-distance and content verification (EV-77). This post-hoc observation shows that the owner gate is sufficient to explain the observed lack of beta candidates in these cells. It does not measure the marginal contribution of record code or content binding. An owner-only system was not separately evaluated, and no missing call is assigned the same behavior by assumption.

### 6.4 Quality, availability and recorded cost

F5 produced marks for 297 of 300 attempted sources. Of the available marks, 291 meet the earlier strict conjunction of PSNR greater than 35 dB, SSIM greater than .9 and LPIPS less than .1; the six failures among available marks are LPIPS failures. Reporting 291/297 describes available-mark quality, while 291/300 preserves the attempted-source denominator. These quality measures are descriptive in the registry protocol, rather than an added post-hoc pass condition, and no human visual ratings exist for this cohort (EV-67/73/74).

The retained journal records 53,580 planned operational units: 53,053 completed successfully, 53 scientific failures and 474 dependent unavailable units. Fifty scientific failures are safety-checker blocks. Recorded run duration is 43,401.126 seconds, approximately 12.0559 local hours (EV-68/69). These are historical operational totals with mixed stages and dependencies, not a detector-latency benchmark or a forecast for another machine. Earlier cached descriptor-lookup timing excludes extraction and cannot support a deployment-speed claim (EV-40–42). Cost and availability should therefore be reported alongside their measurement boundaries, rather than reduced to a per-image number inferred from total duration.

## 7. Discussion and Limitations

### 7.1 Recovery is distinct from record specificity

The principal empirical observation is that useful source-majority recovery can coexist with failed content specificity. E1 demonstrates intended-record acceptance under the specified regeneration channels; E2 exposes a weakness in the content predicate on operationally different real look-alikes. Neither observation cancels the other. A verifier that recovers a pointer can still need a more discriminative record check, and a strict check can avoid competing attribution by abstaining on difficult positives. The results therefore support an evaluation of this tradeoff for the present construction rather than a general solution to ownership verification.

The passive-enrollment comparison also separates two questions that are easy to conflate. A watermark owner gate can reject a claimant whose signal was never inserted. Discriminating between several plausible records belonging to the same detected owner is a different task. Since beta never passes the native owner gate here, the observed E3 difference from descriptor-only matching does not identify joint owner–code–content binding as its cause. A defensible component comparison also needs the readable-code-plus-owner-plus-content control described in Section 4.4: removing the entire code gate confounds read availability with record-code matching. Multiple records per owner and paired recovery/error outcomes are necessary. That evidence is absent and cannot be supplied by relabelling the current comparison.

### 7.2 What the study contributes relative to prior art

The literature review in Section 2 already identifies watermark-to-record hybrids and registered-content verification. Accordingly, this manuscript does not claim to originate the architecture. Its prospective contribution is a reproducible empirical account of recovery, false acceptance, ambiguity, abstention and availability under a precisely defined scenario. At present this remains a single-system case study. A stronger external claim requires a task-compatible comparison and a broader independent source population, as specified in [the future evidence plan](07-gap-closure-plan.md).

Compatibility is substantive. A system that marks every enrolled reference and returns a native top-ranked record does not implement the same task as passive enrollment with a set of accepted owners. DREW's native enrollment, routing and fallback behavior cannot be silently altered and then presented as native performance. Similarly, a retrieval baseline needs an explicit owner/record wrapper before being scored for attribution. No new external baseline was implemented here, and existing restrictions on reopening that work remain in force.

### 7.3 Limits of transfer and security interpretation

F5 modifies RGB pixels through an encoder objective. These results do not fulfill the original proposal's latent-insertion or lightweight DCT-extractor hypotheses. The verifier also relies on its native model components and trusted enrolled descriptors. SD2.1-base broadens the tested diffusion checkpoint, but shared encoder ancestry prevents attributing this result to transfer across independently trained encoders. Broader transfer would require separately justified channels and evidence.

The owner patterns are publicly derived; detection is not proof of possession of a secret signing key. Registry integrity is assumed, and enrollment is not evidence of lawful creation or ownership. The present adversary does not re-mark beta's copy, search adaptively with verifier feedback or optimize a forgery against the complete decision rule. Consequently, the passive zero-beta count is not an unforgeability result. A content-derived short code also cannot be assigned uniform collision probability merely from its bit length; the conditional calculations in [the theory note](05-theory-security.md) are illustrative assumptions, not measured entropy.

### 7.4 Limits of the evidence and the next falsifiable questions

The real-negative panel is concentrated in one film. Its distance predicate is operational and has no corresponding held-out human identity judgment. Missing records affect every bank, and unavailable images are not exchangeable with successful cases by demonstration. These limitations constrain both uncertainty estimates and claims of population transfer. The safety-checker asymmetry further cautions against interpreting the checkpoint difference as a clean model-only effect.

The next scientific questions are whether code-to-record matching adds useful discrimination beyond a readable-code-plus-owner-plus-content rule, and whether the observed specificity/recovery boundary persists on diverse fresh source groups with complete-bank accounting. A negative answer would narrow the method claim rather than justify retuning on the consumed confirmation set. Independently trained encoders and active attacks are additional requirements only for the corresponding broader claims. Prospective work must preserve failed cases, declare missingness policy and group-based selection before outcomes, and report inconclusive comparisons without treating nonsignificance as equivalence. Shared-bank dependence must be addressed in addition to creator/source grouping. None of those studies has been run or approved by this writing exercise.

## 8. Reproducibility, Data and Ethical Scope

The retained run identifiers, frozen protocol, parameter sources and result locations are indexed in the evidence ledger and independent M2 review. The dossier separates original outcomes, saved-aggregate cross-checks, structured-output recounts and post-hoc interpretation. Existing figure specifications identify the fields needed to reproduce the displayed tables and proposed plots. The [table-data package](24-manuscript-tables/README.md) exports the corrected existing counts into seven CSVs with field mapping and provenance; it does not independently reproduce the underlying scientific decisions. No plot or new scientific result was generated during this research-only session.

Public artifact availability is pending. Local possession of scripts, source images, weights, descriptors or journal records does not imply permission to redistribute them. A prospective release should identify each artifact's version, provenance, dependency and release status, avoid protected or identity-bearing records, and supply metadata-based instructions where the underlying asset cannot be distributed. The [release inventory](19-release-inventory/README.md) is an authoring aid, not a legal clearance or a public archive. Reproducing E1/E2 acceptance from individual decisions also remains limited by the absence of those decision rows in the inspected retained outputs.

Future data must be independently assigned after license and overlap review; the used COCO and DIV2K test pools are consumed. The [prospective metadata plan](20-fresh-data-plan/README.md) defines the proposed grouping and overlap checks without selecting assets. Human judgments, authorship, institutional permissions and any broader thesis amendment remain decisions for the responsible people. Matching registered content should not be presented as legal ownership adjudication, and the research does not implement ownership transfer or rights management.

## 9. Conclusion

The evaluated image-domain watermark and trusted registry recover intended records for a majority of scheduled strength-.2 regenerations on 277/300 SD1.5 and 280/300 SD2.1-base sources. The overall confirmation nevertheless fails: the descriptor check accepts 3/45 operationally different real look-alikes (EV-50/51/55/70). Passive competing enrollment yields no observed beta acceptance on the available cases, but the native owner gate already explains this result and stronger regeneration causes substantial abstention (EV-58–66/77). The evidence therefore supports a bounded account of recovery, specificity and availability, not a general claim of secure ownership. Component-identifying comparisons and fresh diverse negatives are necessary before making the proposed broader contribution.

## Editorial delivery and unresolved submission gates

- Sections 1–9 now have complete working prose across files 11 and 18, assembled in 21; references, tables and explanatory provenance still require final typesetting and length editing after the scientific/author decisions.
- The tables use only EV-50–80 and the documented historical evidence. No new experimental arm or statistical test is reported.
- Scientific blockers remain F1/F2, with additional evidence needed for expanded transfer/security claims. Documentary blockers remain the inaccessible V1 papers, current journal-policy fields and institution-accepted ranking definition.
- The author-created inventory and fresh-data plan in folders 19 and 20 are prospective supporting documents, not release approval, acquisition, or execution authorization.
