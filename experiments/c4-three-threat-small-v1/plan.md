# Small three-threat DCT-QIM development experiment

Status: prospective design, not an executable/reviewed compute manifest. Date2026-09-30. Issue18/C4. Governing documents: research/proposal-aligned-plan-20260930.md, research/research-contract.md, research/scope-guard.md and research/approval-policy.md. No experiment is executed by the design request.

Approved source-count amendment: read `cohort-expansion-addendum.md` and `development-expansion.json`. T5 and clean controls now use twelve images, while T3/T4 retain the original ten. Historical ten-source counts below remain the original design; the addendum governs current accounting. Frozen labels are in `semantic-labels.json`. This is still not an executable package.

Adversarial-control qualification: `wrong-owner-590` was selected against the historical `owner-alpha` tag, not the present `qim-pilot-owner-alpha` tag. Retain it as a previously selected wrong-owner string without predicting a collision here; it is not an independently sampled negative or proof of a present-owner attack.

## Question and falsifiable hypotheses

Does the unchanged supplied DCT-QIM v2 candidate provide useful clean verification, reject watermark transfer to different content, survive image-conditioned generative regeneration and distinguish perceptually bound instances within semantically similar pairs? These are three separate endpoints, not one pooled accuracy. The candidate has no CLIP/pHash dual-key or latent embedder; this experiment cannot test latent superiority, semantic-key-only regeneration classification or complete proposal compliance.

## Sources and preprocessing

Use all ten previously reserved COCO2017 validation development IDs in numeric order:6012,25394,80932,109798,134882,147498,177015,190676,468505,499768. Reuse their raw hashes and private/local academic-use restrictions from the reviewed c4-qim-rgb-development-v1 cohort in C:/Users/Soroush/.codex/worktrees/c4-qim-pilot/THESIS_GUIDE_OFFLINE_v5. No new dataset or locked-test access. Preserve item-level rights restrictions and no-public-redistribution status. This is previously accessed, nonrandom development evidence, not confirmatory power or generalization.

For all three threat arms, canonicalize EXIF/ICC RGB8 as in the previous reviewed adapter, then bicubic-resize to512x512 and save/reopen RGB8PNG. This deliberately standardizes attack geometry; it is a new resized pilot, not native2K evidence. Embed on this grid using unchanged profile QIMstep4.0, thresholds owner.75/instance.75/confidence.65 and intended OwnerID qim-pilot-owner-alpha. Use the previous three fixed wrong OwnerIDs and add the already-demonstrated selected wrong-owner collision as a separately labelled adversarial control; no globalFPR claim.

Freeze all source IDs/hashes, canonical output hashes, profile/code hashes and semantic labels before detector outcomes. Detect only from the suspect image, claimed OwnerID and public profile. Clean references, pair labels, attack provenance and metric models are evaluator-only.

## T4 copy-paste

Every recipient in all patch, sham, residual and no-transfer conditions is the **unmarked canonical C0** image, never its marked variant. The positive donor control is the unattacked marked donor PNG. Retain each no-transfer C0 recipient outcome: a baseline-positive recipient is not transfer-caused false attribution and prevents preliminary specificity support for that arm. The phrase donor clean positive below means this unattacked marked donor, not an unmarked positive.

For each donor index i in the sorted ten IDs, choose recipient indices(i+1)mod10 and(i+5)mod10:20 directed edges, no self edges. Use two central square patch sizes128 and256pixels at fixed same-coordinate centers. Primary public-image arm copies donor marked RGB pixels directly into the recipient:40attempts. Matched sham copies the unmarked donor patch into the recipient:40controls. No oracle clean donor is provided to the primary attacker. Do not interpret a visually destroyed recipient as admissible successful forgery.

Separate stronger-access diagnostic arm explicitly provides the clean donor to form its marked-minus-clean RGB residual, adds the whole residual to each recipient at scales.5and1.0, clips/rints/saves/reopens:40attempts. This is not pooled with public-only patch attacks. No best scale/patch selection and no detector feedback during construction(Q=0). Score all attempts; donor-owner acceptance on a distinct recipient is false attribution, not evidence of legitimate ownership. A no-transfer recipient and donor clean positive baseline are retained.

Measure RGBPSNR/SSIM/LPIPS against the intended recipient. Pilot admissibility requires PSNR>35,SSIM>.9,LPIPS<.1 AND two evaluator reviewers agree the recipient's principal content remains. These thresholds are explicitly chosen pilot constraints, not a claim that the proposal prescribed attack budgets. Keep inadmissible/unresolved/missing attempts visible. If fewer than10distinct recipients have admissible transfers in an arm, its security endpoint is inconclusive regardless of rejection count. Report valid-only outcomes alongside all-attempt counts.

## T3 regeneration

Use an offline Stable Diffusion1.5 image-to-image attack candidate whose existing local components are recorded by a6-weight-acquisition-receipt-20260924.md: mirror revision451f4fe16113bff5a5d2269ed5ad43b0592e9a14, not an assertion of first-party custody or resolved rights. Bind the actual local asset lock/runtime and resolve retained rights/runtime concerns before this arm becomes runnable; do not invoke an automatic model loader/download. No replacement model may be silently substituted.

Fixed DDIM configuration:20inference steps, eta0, strengths.20and.40, guidance1.0, empty prompt/negative prompt, seeds0,1,2,512x512; keep the pinned safety handling intact, unsafe/blocked outputs recorded as failures. Ten marked sources x two strengths x three seeds =60attempts; the same settings/seeds on C0unmarked sources produce60matched controls. Couple source/marked noise streams with separate generators reset to the same seed. No attack chains or retries. Save/reopen output before detection. Score intended and three fixed wrong owners on every output; do not choose a favorable seed/strength.

Measure attack distortion against its immediate marked input and end-to-end against canonical source. Content retention requires evaluator-only CLIPViT-B/32 cosine>=.90 and independent two-reviewer agreement on principal scene/object identity. This .90 is a prospective pilot decision, not a universal semantic threshold. Report retained and nonretained outcomes separately; missing CLIP/labels makes retention unresolved, not automatically valid. LPIPS/quality are descriptors for regeneration, not the T4pixel-fidelity filter. Source-level success requires all three seeds at each fixed strength retain content and pass intended-owner detection; report strengths separately. Failure cannot be labelled regeneration specifically by detector output alone: ground truth is attack provenance.

## T5 semantic collision

Inspect all45unordered source pairs before computing detector/binding outcomes. Two evaluator reviewers independently label them sameprincipal-subject/content, different, or uncertain, with written rationale; exclude none from the inventory. Resolve disagreements by a third reviewer before scores. At least5same-semantic and5different-semantic distinct-source pairs are required for a stratified descriptive result; otherwise declare insufficient semantic cohort and propose a separately approved source expansion, never manufacture similar pairs or tune similarity labels after scores.

Measure the supplied12-bit binding distance between clean canonical images and between marked/source images. Report how often distinct-instance pairs satisfy the frozen binding threshold(distance<=3), stratified by semantic labels, and same-instance binding retention. This is a component collision diagnostic, NOT the detector's instance-attribution accuracy: its public interface has no enrolled-image identifier and all images deliberately share one owner. Use T4 residual-transfer outcomes on their actual selected pairs as separate delivered-watermark evidence, not interchangeable T5samples. CLIP is evaluator-only descriptive similarity and is never silently added to the core detector.

## Metrics, controls and analysis

Preliminary clean/survival support requires zero intended-owner positives on all completed matched C0 controls. For T3 assess this separately at each strength across all30C0outputs; any positive makes survival attribution inconclusive and is reported as a false positive, rather than allowing mere acceptance to count as watermark survival. Missing C0calls block support. Wrong/adversarial-owner positives remain separate contradicted attribution claims, never hidden by good C1survival.

Clean:10marked positives and10unmarked controls, fourwrong-owner controls permarked input, nonzero marked-channel changes, native-to-pilot preprocessing accounting. RGBPSNR, fixed Gaussian-window SSIM and existing pinned AlexNetLPIPS on savedbyteimages; weights/runtime must be verified and reused offline. No weight acquisition. The previous LPIPSNOT_RUN result remains unchanged.

Primary outputs are three axis-specific source/pair outcome tables, not one averaged passfraction. Source is the clustering unit; directededges share donors/recipients, pairs and seeds are correlated. Report exactnumerator/denominator, every failure/missing/inadmissible outcome, medians/ranges and source summaries; no p-values, independent-pair binomialCI, superiority or populationFPR claims in this tiny exploratory study. No parameter tuning, optional stopping, seed replacement, outlier removal or follow-up scientific run. Fixed inventory completion is the stopping rule; user-imposed elapsed-time limit is none.

## Execution readiness

Not runnable yet: exact semantic labels/coverage, attack adapters and synthetic parity tests, local model/metric rights-runtime receipts, measured resource envelope, reviewed clean entrypoint and final hash-bound manifest are required. The official design helper requires that actual executable contract; it must not be fed fabricated hashes or a placeholder entrypoint. Emit BLOCKED_PACKAGE until those prerequisites exist. Only official controller/runner may mutate lifecycle/dispatch state. Design review is not a human approval artifact.
