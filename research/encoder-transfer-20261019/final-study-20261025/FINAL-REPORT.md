STATUS: COMPLETE

# Final-study research dossier

Research-only session complete, 2026-10-25. WP0–WP7 and the ordered E1–E3 article/venue extensions are delivered. WP6's hostile-review corrections and E3's article-frame corrections are applied and verified by their original reviewers. **No experiment or server execution is approved by this report.** The historical verdict remains **FAILS, ROUTE C**. Completion refers to the research dossier and design, not success of the proposed predictor, attacks or final experiment. Start with the [reading map](READING-MAP.md) or the [fifteen-objection disposition map](analysis/objection-disposition.md).

The decisive next step is a separately approved server feasibility/development phase. It must establish whether the full-chain derivative measurements fit the budget before confirmation is considered. The proposed predictor has not been fitted or evaluated on new data. The current evidence supports a bounded empirical article; a stronger predictive mechanism claim depends on the prospective test below.

## 1. What the research established

### WP1: prior work narrows the contribution

The original review contains 30 inspected method/experiment cards: ten attacks/benchmarks, twelve watermark studies and eight encoder studies, plus six theory/transfer cards and later bounded additions. V2 denotes inspection, not reproduction or guaranteed validity. The closest inspected no-box latent attack is MarkNull; its compatible-latent/inversion assumptions do not establish removal under arbitrary independently trained encoders. Stable Signature and LaWa show that own-autoencoder survival is method dependent. Rank/direction scrambling is also prior work. Neither another cross-family failure table nor a two-pass rinse is a defensible first-ever contribution. The remaining target is **a stage-resolved, prediction-tested account of readable signal transport**. See [literature synthesis](01-literature-synthesis.md), [positioning](02-positioning.md), [versioned cards/searches](literature/search-log.md) and the [rank/direction limitation](analysis/rank-direction-limit.md).

SDXL has primary from-scratch-autoencoder evidence. FLUX.1 also has such a family-level statement, but identity/configuration of the exact released schnell checkpoint remains qualified. Architecture or weight independence does not establish independent Jacobians, disjoint training data or an encoder-only causal intervention. Source versions and unresolved access are retained rather than promoted to verified claims.

### WP2: the whole readable path matters

The reanalysis used saved development journals only: **60 sources, 11,040 final unit identities, 23 blocked outputs retained**. Three regeneration seeds are repeated observations within a source. The following are descriptive, reused-development results, not fresh confirmation ([mechanism and analysis links](04-mechanism.md), [retained stage-2b results](../results-2b.md)).

| Historical condition | F5 source-majority compound semantic C | Interpretation |
|---|---:|---|
| SD1.5 .1 / .2 / .4 | 60 / 57 / 39 of 60 | Retention varies within the writer-associated pipeline. |
| SDXL .1 / .2 / .4 | 0 / 0 / 0 of 60 | The complete foreign pipeline defeats this endpoint. |
| SDXL codec / MoVQ codec round trip | 55 / 55 of 60 | Encoder/codec reconstruction alone does not reproduce the full-pipeline loss. |
| Kandinsky 3 full img2img .2 | 5 of 60 | Historically observed extra-family limitation; excluded from the proposed fit. |
| SDXL .1, comparison arms | v5 50, WAM 48, VINE-R 60 of 60 | Endpoints, payloads, detector information and clean quality differ. |

On all **58** F5 sources with complete paired qualities, SDXL .1 is milder than SD1.5 .2 in the three recorded metrics; **56/58** retain C in the latter and lose it in the former. Yet the frozen matched-distortion caliper grid yields only **two** F5 matched sources. This challenges a simple monotone quality-only explanation on these sources, while leaving a matched-quality population comparison and causal identification unresolved. Source-grouped diagnostic CV Brier is about **.2459** for F5's constrained quality-only forms versus **.0433** for the family-augmented form. Family labels are explanatory shortcuts, not an out-of-family mechanism ([quality report](analysis/quality-model-report.md)).

Continuous reader evidence sharpens the endpoint result. The decoded semantic margin's clean median is approximately **+7.03 score units**, falling to **−2.75/−3.95/−4.34** at SDXL .1/.2/.4. Paired C1-minus-C0 decoded-score medians remain **1.99/.92/.34**, respectively. Native decoded words can change between C0 and C1; these contrasts do not measure transport along a common fixed codeword, erase all signal, or prove statistical equivalence. Smoothing changes source-majority **any-carrier A**, not “instance-tier A,” from **32 to 16** relative to its posterior-mode control ([negative/background supplement](analysis/negative-background-analysis.md)).

Historical F5 SDXL negative calls are **0/540 C0 and 0/540 wrong-owner**, each aggregated over only 60 source groups. Zero source-any events at n=60 has a one-sided 95% upper bound **.0487**, not a 540-independent-trial guarantee. VINE has one observed C0 false detection at its inclusive 69/100 threshold. Strict clean quality passes are F5 60/60, v5 60/60, WAM 58/60 and VINE 31/60; the retention table therefore cannot establish an equal-quality ranking.

The proposed model is `p_hat = p_C0 + kappa * v`: a 320-chip forecast using a full-chain tangent along the C0 trajectory, followed by the unchanged reader and a declared C0 semantic-descriptor proxy. Only one global kappa and one separate q90 margin radius are learned. The primary source-majority forecast is a deterministic 0/1 decision, with Brier loss equal to classification error; q90 is a margin radius, not a calibrated probability. The computation nevertheless uses pretrained target/reader internals, paired noise, original and marked-input information, C0 outputs and derivatives. It is a privileged scientific model with substantial computational capacity. It is not a lightweight detector, independent-encoder theorem or validated transfer model ([derivation](analysis/theory-design.md), [prediction barrier](analysis/prediction-contract.md)).

The conditional Gaussian information bound and rank/direction counterexamples state their assumptions explicitly. They do not determine actual F5 erasure, prove independent training causes failure, or turn content-derived payload recovery into independent ownership evidence ([information note](analysis/conditional-information-bound.md)).

**Later author sensitivity, outside WP6/E3 review:** the saved-output comparison closes an aggregation gap. All **177/180 available same-numeric-seed F5 pairs** have strictly better SDXL .1 quality than SD1.5 .2 in all three metrics; **170** change from detection to non-detection, on **58 sources**. In the **58 fully complete sources**, the corresponding figures are **168/174 pairs on 57 sources**, consistent with the distinct **56/58 majority transitions** above. Both quality references agree. Re-pairing outputs does not create independent evidence ([all arms, missingness and provenance](analysis/quality-dominance.md)).

On the complete 348-output subset, an exact finite-data argument gives every probability score that is coordinatewise increasing in (−LPIPS, PSNR, SSIM) Brier loss at least **563/2320 ≈ .24267**; a monotone binary classifier cannot beat the always-negative error **14/29 ≈ 48.28%**, even with source identity. This is an empirical restriction on that class, not a population test or an H4 result. H4's six-feature comparator permits unrestricted signs and different inputs, so this bound does not constrain it ([derivation and precommitted premise check](analysis/monotone-brier-bound.md)).

Additional author notes distinguish [native stage gains from unique causal attribution](analysis/stage-attribution-boundary.md), [finite transport error](analysis/finite-transport-boundary.md), [chip accuracy from compound-reader stability](analysis/reader-stability-boundary.md), and [distribution similarity from paired fidelity and key-conditioned information](analysis/distribution-fidelity-boundary.md). These conditional derivations add interpretive precision without changing the accepted protocol or supplying new experimental evidence.

### WP3: informed attacks are specified, not executed

Attack A is public-proxy SDXL→SD1.5 reconstruction with four equal per-pass strengths. Attack B is a nine-setting, twenty-step latent decorrelation heuristic inspired by MarkNull, with codec and fidelity controls. Both receive only the published input and public proxy models: no original, key, owner, payload, target reader or detector feedback. A's first pass is retained. Both settings are selected by a fixed quality-only rule before new detector release; no eligible setting means inactive, without relaxed thresholds or an identity fallback.

The common eligibility region is **LPIPS ≤.15, PSNR ≥25 dB, SSIM ≥.75 relative to the published input**, with at least **48/60 passing source majorities in every arm**; A also needs **144/180 passing outputs per arm**. This is a measurable fidelity budget, not a claim of imperceptibility or maximum possible removal. Historical rinse and D1/D3 results remain historical comparisons, not additional uncosted Phase-B cells ([complete attack specification](05-informed-attacks.md)).

### WP4: an extra family is conditional

Kandinsky 3 is the required core family excluded from fitting/calibration, but it is historically observed and therefore not a blind new-family discovery. Preferred optional FLUX.1-schnell requires personal access/licence action, a pinned checkpoint/configuration and feasibility verification. Its selected weights total about **33.714 GB**; **48 GB VRAM is preferred**, and forward execution does not establish derivative feasibility. At four configured steps, nominal .1/.2 strengths collapse to the same one-update condition. The proposed distinct grid uses .25/.5/.75. Sana-Sprint remains a reserve with unresolved released-autoencoder lineage; SD3.5 is gated. Neither silently substitutes for failed FLUX access ([family audit](06-third-family.md), [severity contract](analysis/severity-contract.md)).

## 2. Final server experiment: decision sheet

The binding specification is [07-final-experiment.md](07-final-experiment.md), with the [mechanism interface](analysis/mechanism-server-spec.md), [training/missingness contract](analysis/training-missingness-design.md) and [confirmatory statistics](analysis/confirmatory-statistics.md). This sheet summarizes rather than replaces them.

| Item | Fixed prospective plan |
|---|---|
| Methods/endpoints | Unchanged F5 r2, v5 r3, WAM, VINE-R plus C0; separate compound C, carrier A, known-message presence, quality and specificity. No equal-task leaderboard. |
| Native grid | SD1.5 and SDXL at .1/.2/.4 = six cells; required K3 .2 = seventh. Optional qualified FLUX adds one quality-selected cell. Three fixed seeds per source/cell. |
| Phase A | Existing 60 development sources, deterministic 30 fit / 30 calibration split; first six for bounded pilot and twelve for detailed stage/direction controls. Fit global kappa and q90, fit a six-feature pre-output quality comparator, freeze quality-selected attacks and optional FLUX activity before new detector release. Required K3 remains fit/calibration excluded. |
| Freeze | Commit assets/configuration, masks, learned quantities, eligibility/inactivity, paired randomness, failures, budget and exact analysis. Pilot failure or over-budget forecast stops the study. Stop for the user before Phase B. |
| Phase B | 200 fresh preassigned source groups, plus 40 ordered acquisition reserves usable only before scientific outcomes. Seal the entire native-grid forecast inventory before generating/releasing any marked TARGET outcome. No refit, threshold tuning or outcome-selected replacement. |
| H1 | F5 C probability <.10 at both SDXL .1/.2. |
| H2 | F5 C probability >.80 at SD1.5 .2. |
| H3 | Joint F5 SD1.5 .2 retention, SDXL .1 loss and strictly milder SDXL in all three complete median qualities on >.80 of sources. |
| H4 | Every native cell's absolute prediction-rate error ≤.10; family-balanced predictor Brier risk at least 20% below the frozen quality comparator. Use conservative completions for unavailable values; full numerical delivery is a separate flag. Nontrivial high/low prediction additionally needs supported H1 and H2. |
| H5 | A/B × four arm-specific claims: clean-positive, completed, quality-valid removal on >.50 of all sources and quality validity on >.80. A requires removal and quality on at least two same outputs. |
| H6 | VINE-R known-message presence >.90 in SD1.5 .2, SDXL .1 and .2; clean quality and negative gates remain separate. |
| Inference | Source is the unit; fixed 13-slot Holm family at .05, intersection-union components, CP binomial tests and fixed six-bet H4 mean test. Inactive attacks keep p=1 slots. No outcome-dependent sample enlargement. |
| Negatives | Eight method/query strata, source-any event across required calls. A pass needs zero observed events and complete calls. Zero/200 gives marginal one-sided 95% upper bound **.014867**, or **.025057** for eight simultaneous bounds—not 1e−6 specificity. |
| Machine | RTX4090-class or larger, ≥64 GB host RAM, ≥150 GB disk; optional FLUX prefers 48 GB VRAM. Exact JVP support, peak memory and runtime remain unmeasured. |
| Allocation/cost | Proposed core ceiling **100 instance-hours: A≤40, B≤60**, separately approved. At illustrative $.45–.60/h: **$45–60**. Optional FLUX may request ≤40 extra hours; **$18–24 only if the actual larger-device rate fits that range**. No live market rate is asserted. |

Core Phase B schedules **31,000 output units, 49,600 detector batches and 4,200 F5 full-chain JVPs**. The known historical-time subtotal is approximately **25.02 hours before B optimization/backward passes, JVPs, setup and retrieval**. Ten/thirty/sixty seconds per JVP would add 11.7/35/70 hours; these are sensitivity examples, not measured timings. Detailed Phase A adds 720 encoder JVPs, 540 differential full-chain JVPs and 1,620 stage outputs beyond its native/fit/attack grid. **The 100-hour ceiling does not establish that the study fits.** The later pilot must project the entire frozen schedule, collection and 30% margin inside approved limits or stop ([cost audit](analysis/server-costs.md)).

Core selected model assets are approximately **48.6 GB**, rising to **82.3 GB with FLUX**, before environment/output/staging. Both exceed the historical 30 GB download allowance. The later plan needs a separately approved selective asset ceiling. At historical .85 MB/s retrieval, 10 GB alone takes about 3.27 hours; collection must fit the paid allocation. Stop the instance after verified retrieval; destruction remains the user's action.

The [200+40 manifest](heldout-manifest.json) contains **identifiers and official metadata only**, all `NOT_DOWNLOADED`. Its [rule](heldout-selection-rule.md) was committed before the draw; the [audit](analysis/heldout-metadata-audit.md) discloses exclusions and metadata limitations. Exact identifiers/creator grouping do not prove iid sampling, independence from model pretraining, absence of mirrors or absence of near duplicates. Later authorized raw/canonical hash checks precede scientific use. The source-superpopulation inference assumption remains a model assumption.

At the strictest Holm threshold, planning counts are H1≤9, H2/H3/quality≥175, H6≥191 and H5 removal≥120 of 200; exact adjusted p-values decide. H4 remains potentially underpowered against an already accurate quality comparator. For example, even a perfect predictor against constant comparator Brier .04 needs **n=228** for its mean component at that threshold. Do not interpret an inconclusive n=200 result as proof of no mechanism ([power and fixed-bet limitations](analysis/betting-mean-design.md)).

## 3. What a Q1 reviewer can and cannot be told

**Can be told now:** the saved development evidence has been reanalysed with source-level denominators, actual compound-reader states, continuous scores, retained failures, fixed calipers and explicit detector information. It presents a sharp round-trip/full-regeneration contrast and a falsifiable prospective alternative to norm-only or quality-only explanations. Literature overlap, access gaps, statistical assumptions and feasibility risks are documented. This supports a bounded empirical framing and a more demanding final study.

**Cannot be told now:** that fresh-outcome predictive accuracy is established, that the informed attacks work, that independent encoder training is the identified cause, that cross-family transfer or signal erasure is proved, that a small fitted parameter count makes the model lightweight, that VINE's presence endpoint equals owner/content binding, that specificity is zero or cryptographic, that T4/T5/registry/proposal-latent hypotheses pass, or that a Q1 article is submission-ready or likely accepted. F5 remains an image-domain encoder-directed comparator. Human perceptual judgments remain missing. The separate registry result remains failed overall and uses enrolled-record side information.

## 4. Independent hostile review and corrections

The single fresh WP6 reviewer returned **ACCEPTED WITH CORRECTIONS for the research-only dossier/design**, with no remaining blocker in the inspected scope ([review](08-review.md), [author dispositions](analysis/review-response.md)). The author applied the sampled-posterior noise-only versus sampled full-path correction and clarified historical versus future attack controls. The MAIN STATE handoff corrects “instance-tier A” to **any-carrier A, 32→16**. No requested correction was rejected.

The reviewer independently checked 60 arm/cell summaries, saved regression predictions/conditions, the exact bootstrap recipe, calipers, schedules, cost arithmetic, the 240 metadata entries and the statistical/theory supplements. Scope limits remain: this is not an exhaustive literature/metadata forensic audit, empirical predictor validation, server feasibility proof, thesis gate, user approval or publication review. No new experimental result was manufactured by accepting the design.

## 5. Decisions for the user

These are the next decision points, not questions awaiting an answer during this detached session. Every default remains in force until the user explicitly decides otherwise.

| Yes/no decision | Default and consequence |
|---|---|
| Approve later implementation and Phase A on a rented server, with a measured feasibility pilot and ≤40 core instance-hours? | **No.** Research/design only; no server is rented or used. The actual hourly price and dollar cap must be supplied at approval. |
| Replace the legacy 30 GB model-download cap with an explicit selective core asset allowance above the estimated ~48.6 GB, plus justified environment/output/storage reserve? | **No.** Core acquisition cannot proceed under the old cap. No scientific assets are downloaded to this laptop. |
| Personally accept the required FLUX access/licence terms and approve its ~33.714 GB extra assets, larger-device rate and ≤40-hour optional allocation? | **No.** Keep the seven-cell K3 core; do not silently substitute another family. |
| After Phase A freeze and measured budget review, approve fresh Phase B with 200 sources and ≤60 core instance-hours? | **No.** A separate later decision is required; identifier preparation is not pixel or execution approval. |
| Retain a bounded ROUTE C empirical article if the predictor, derivative feasibility or informed attacks fail? | **Yes as the working reporting route.** Preserve negative outcomes and uncertainty; do not tune a replacement on confirmation and call it confirmed. Submission remains a separate user decision. |

## 6. Article extensions and completed session

The research-only restriction held throughout the core work: saved JSON/JSONL and source text were read, primary papers/metadata were inspected, and permitted standard-library calculations were performed. No image generation, marking, regeneration, attack, detection, metric, encoder, training or experimental timing pass ran; no models/images/data/code were downloaded, no package installed, no GPU/paid service/SSH used, and no held-out pixels inspected.

The ordered extensions are complete:

- **E1:** [Related work, Mechanism and Threat model](article-drafts/README.md), with evidence ledgers, a twelve-key bibliography and qualified figure captions. They are article sections for author development, not a complete submission or finalized thesis chapter. The schematic was checked as source text; publication-layout rendering was not performed.
- **E2:** [Venue fit](venue-fit.md) identifies TIFS as the strongest direct subject fit and IEEE Access as a venue with an explicitly supported Negative Result article type. Current Q1 eligibility, metric/year/category and sufficient novelty remain unresolved; neither fit nor article type implies acceptance.
- **E3:** the [independent article-frame review](09-review-article.md) closed B1 and R1–R3, including the unchosen Q1 definition, predictor terminology, H1/H2 interpretation guard and the 58-pair/56-transition distinction. Its verdict is **accepted for author development, not ready for submission**; the [response](article-drafts/review-response.md) records closure.

After these reviews, the [source-closure index](literature/source-closure-index.md) and [25-entry late bibliography](literature/late-sources.bib) record exact inspected versions, partial access and metadata-only leads. Close derivative/subspace and regeneration prior art limits novelty claims. The [comparison map](article-drafts/close-prior-art-map.md), conditional mathematical notes, saved-output sensitivity and [future-outcome atlas](analysis/future-outcome-interpretation.md) are later **author supplements**, outside completed WP6/E3 review scopes. They neither amend the frozen experiment nor inherit an independent acceptance verdict.

The session began at **2026-10-25 13:14:53.9657180 UTC**, with the fixed six-hour deadline **19:14:53.9657180 UTC**. This final refresh occurs during the requested last-40-minute window. MAIN STATE and the single continuation entry are updated, preserving other MAIN edits; exact completion and successful branch pushes are recorded in [PROGRESS.md](PROGRESS.md). No server process is running and no further work is scheduled automatically. The next scientific action requires the separate Phase-A decision in section 5.
