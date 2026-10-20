# Independent stage-1 design review

Date: 2026-10-19. Reviewer: **Astra independent reviewer**, separate from the Codex author and topic integrator. This is the single independent design review requested by BRIEF section 1a. The reviewer communicated findings; the author made the corrections. The reviewer edited only this report.

**Verdict: ACCEPT FOR FREEZING AS A BOUNDED DEVELOPMENT STUDY, with the warnings below. No substantive design or implementation blocker remains in the reviewed candidate.** Three concrete implementation/inference defects were corrected during this review and independently checked. This verdict permits the stage-1 package to be finalized for the user's decision. It is neither authorization to rent a server nor evidence of transfer, publication readiness, or successful native GPU execution.

## Scope and evidence

The review covers stage-1 changes since `44c9ad9`, including the integrated uncommitted candidate on branch `codex/encoder-transfer-20261019` above HEAD `eb517ed5f6c750ad389072b80f06815c773746f8`. It uses the authoritative MAIN `thesis-runs/d916749c/STATE.md`, BRIEF section 1a and the remaining fixed-design provisions; `design-research.md`, `protocol.md`, `frozen-config.json`, `budget-and-proposals.md`; source/asset/package metadata; all eight topic syntheses and targeted cards, search logs and primary-source passages; the six `scripts/encoder_transfer_*.py` files and `tests/test_encoder_transfer_test.py`. Historical detector, writer, metric and adapter functions were read where the new code relies on them.

This is a substantive review with targeted source verification, not a second complete literature search or an assertion that every cached paper was independently reread. For consequential claims, inspected cached primary material included the SDXL paper's autoencoder-training comparison, Zhao's theorem and assumptions, WAM's native decoding/calibration material, and VINE's native encoding/decoding implementation. Three sampled T3 source-cache files—VINE encoding, VINE decoding and WAM README—matched their recorded SHA-256 and byte counts. The final source-list hash matched the config. Paper/cache inspection did not execute upstream code.

No server was contacted, no model weights or runnable upstream implementation were downloaded by this reviewer, and no real image, mark, regeneration, detector outcome or held-out pixel was opened or scored. The only execution was CPU analytical/fake-fixture validation. No human assessment or approval is inferred.

## Blocking findings and their closure

| Finding | Why it blocked the candidate | Correction inspected and validation | Final status |
|---|---|---|---|
| B1: Completed detector calls disappeared when the later quality pass was interrupted | `call_value` and reporting `score` required row-level `status="ok"`, although successful calls were already journaled on a `generated` row. An interruption could therefore turn observed positives and negatives into missing values and change routing/completeness. | Both readers accept `generated` or `ok` only when the particular detector call itself is `ok`; absent/errored calls stay missing. Generated rows are inventoried. `test_persisted_detection_survives_interrupted_quality_pass` covers this separation. | **Closed.** |
| B2: A wholly unavailable primary comparator could receive an apparent inferential result | Fixed missing-as-failure vectors were passed directly to the paired test. A method that never ran could consequently appear significantly inferior, contrary to T6's not-estimable rule. The author identified this discrepancy during the same review; the reviewer independently checked it. | Either wholly unavailable side now yields a not-estimable status and null displayed raw/adjusted p-values. An internal p=1 preserves the fixed Holm family of three. Operational counts, paired differences and the brief's routing rule remain unchanged. The targeted unavailable-comparison test passes. | **Closed.** |
| B3: Nonfinite floating model output could become an ordinary RGB8 observation | PIL/uint8 conversion after generation or embedding could hide NaN/Inf as image pixels. That would misclassify numerical failure as scientific failure. T5 explicitly required finite and VAE precision checks. | `guard_vae` checks encode inputs/posterior and decode inputs/outputs before quantization, and asserts SDXL `force_upcast` plus full fp32 input/parameter arithmetic. WAM/VINE embedding tensors are checked before clipping/quantization. A CPU tensor/fake-VAE test rejects NaN, Inf and wrong precision. Native sampling and checkpoint selection are unchanged. | **Closed at code-contract level.** Native execution is still untested. |

A reporting gap was also corrected: a single global CUDA peak could not support T7's per-arm embedding/extraction memory table. Serial phase receipts now include resident-model allocated peaks and retain the cumulative maximum across resets/resume; the fake-CUDA test passes. The author also completed separate native/common/exact-message source-majority summaries and rinse incremental distortion. These additions implement declared measurements without changing the primary rule or creating new scientific arms.

The truthful “review pending” headers encountered at the start were not treated as a substantive defect. Final freeze/status changes, commit and push belong to the author after this review; this report does not claim those release actions have already happened.

## Assessment of the design

**Coverage and source fidelity — adequate for this bounded question.** T1 considers the named benchmark/removal families, recent leads and standard variants; T2 distinguishes encoder ancestry from generator diversity and includes alternatives to latent diffusion; T3 examines the native baselines and ranks additional post-hoc comparators; T4 derives bounded predictions and an adaptive proposal; T5 fixes operational semantics; T6–T8 cover uncertainty, fairness and validity. Gated, inaccessible or unverified leads are identified instead of represented as evaluated methods. The integration records the T6/T7/T8 agent interruptions and parent completion honestly. Those provenance limitations do not manufacture an independent review or invalidate the inspected synthesis.

The SDXL independence claim is supported by its reported from-scratch autoencoder training. The Zhao argument is used in the correct direction: a bound involving the attack encoder's perturbation response does not guarantee survival under a different encoder, and a loose upper bound does not become a lower bound. Neither paper supplies a predicted empirical transfer rate. Broad claims about every independent encoder would remain unsupported.

**Native baselines and pipeline — adequately specified.** F5 remains an image-domain writer using SD1.5 encoder gradients, with the historical parameters and C predicate preserved; it is not relabeled as the proposal's latent insertion method. F5/v5 content codes, arbitrary external payloads and chip redundancy are distinguished. The experiment uses no enrollment registry. F5's clean-decoded H diagnostic has its intended-code limitation disclosed.

WAM keeps the released MIT SA-1B configuration, native mask operating point and native decoding conventions; the paper calibration is not assumed to transfer. VINE-R keeps its native 100-bit message and residual-resizing workflow. A universal VINE native numeric cutoff is not invented. Independently recomputed minimal binomial cutoffs are 27/32 with tail `5.653710104525089e-05` and 69/100 with tail `9.157161244117683e-05`. These are random-message calculations, not empirical image-FPR guarantees.

R0/R1 scheduling, RNG seeds, empty prompts, guidance, 512/1024 resampling and SDXL microconditioning are fixed. The full-fp32 VAE arithmetic override retains official fp16-file checkpoint values; it does not claim to restore original fp32 weights. D1's posterior mode differs explicitly from img2img posterior sampling. Resize controls and the saved-first-pass rinse are appropriate diagnostics; the rinse is not claimed equivalent to a single .2 pass or an exact benchmark reproduction.

**Statistics, missingness and preregistration — internally coherent after B1/B2.** The source is the unit, three seeds define a fixed 2-of-3 majority, and missing positives remain failures in the planned denominator. Negative calls remain unresolved when missing; no majority operation weakens their gate. The primary is fixed at R1 .2: at least 45/60 plus complete zero prescribed negatives for TRANSFERS, below 30/60 for FAILS, margin three for the route. Inferential tests and quality matching cannot replace this rule.

The n=60 choice is a cost/sensitivity decision, not a conventional power guarantee. I reproduced the conditional TRANSFERS probability at independent source success p=.8 as `0.8693793203042368`; it assumes complete zero negatives. T6 makes seed/source dependence and negative-gate uncertainty explicit. CP intervals and exact paired tests are model-based exploratory summaries for a consulted deterministic cohort. The fixed Holm family is three; secondary cells and matching are descriptive.

Matching uses fixed bins/calipers and complete quality vectors, selects pairs before joining detection labels, preserves empty/sparse bins and does not relax tolerances after outcomes. Embedding, attack and total distortion are separate. The native embedding-qualified subset does not trigger rematching. These choices prevent a quality-selected success rate from replacing the primary denominator.

**Budget and scope — credible as a conditional plan, not a measured promise.** The integrated total correctly includes shared C0 generation: 7,500 units plus 250 smoke units. Estimates include setup, native embedding, readout, metrics, I/O and retrieval. The runtime deadline starts at actual instance creation, respects the earlier 15-hour/$15 ceiling and reserves retrieval time. Timing-only smoke, a 30% allowance, the fixed drop order and preservation of n60/R0/R1 .2/.4 are consistent with the brief. If the protected grid cannot fit, reporting a resource shortfall is the appropriate outcome.

Optional baselines, an additional independent encoder, caption prompting, smoothing and learned adaptive encoders remain costed proposals. Provisional feasibility allowances are not represented as execution-ready configurations. No extra baseline, encoder training or hidden tuning is required to make this core study interpretable.

## Warnings that remain

1. **One independent encoder and a changed full pipeline.** SDXL differs in encoder, denoiser, latent scaling, resolution and conditioning. D1 and resize controls narrow interpretation but do not isolate a causal encoder effect. Success supports this SDXL channel; failure cannot establish that all independent encoders erase F5. Additional diversity is a separately approved proposal.
2. **Consulted development data and conditional uncertainty.** ID/hash separation does not establish semantic independence, independent creators or absence from pretrained training sets. The deterministic 60-source cohort cannot support a confirmatory population claim. No held-out inference should be added without a new decision.
3. **Endpoint and operating-point inequivalence.** F5 C, WAM native zero-bit presence, common known-message agreement and exact payload recovery answer different questions. Native payload, quality and readout side information differ. Even a favorable margin is not noninferiority, equal-capacity superiority or a validated low-FPR claim. Missing external arms must remain visibly unavailable in the narrative even when the operational route uses fixed failure counts.
4. **Finite quality overlap and human judgment.** Calipers are declared design choices, not proof of perceptual equivalence. Sparse/empty overlap is informative and must stay visible. LPIPS/SSIM/PSNR do not supply the missing human visual verdict.
5. **Native compatibility and cost remain unverifiable in stage 1.** Metadata availability and CPU tests do not prove CUDA installation, native model loading, deterministic-kernel compatibility, throughput or VRAM fit. Package metadata checks are not a complete transitive environment lock. The authorized stage-2 smoke must record actual software/hardware and measurement receipts; implementation-only repairs must retain provenance and cannot become outcome-guided retuning.
6. **Runtime/resource interruption is not mechanistic evidence.** Hard-budget truncation, unavailable baselines and numerical errors can produce operational failures under the fixed denominator. Reports must preserve those literal labels while distinguishing incomplete execution from measured watermark erasure. Actual all-in rental charges and retrieval/stop time must fit the ceiling; example prices are not live quotes.
7. **Reporting remains a stage-2 obligation.** This review checks the frozen table/figure contract and available measurements, not nonexistent result figures or a publication manuscript. Native source summaries, all failure inventories, missingness bounds, low-FPR resolution and fixed illustration selection must survive into the results. VINE license restrictions continue to govern release.

## Validation and release disposition

The reviewer independently ran:

```text
W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/a6-science-venv/Scripts/python.exe
  -m unittest discover -s tests -p test_encoder_transfer_test.py -v
```

**24 tests passed in 2.875 seconds.** They cover decision boundaries, historical predicates/parameters, exact thresholds, source-majority missingness, source/asset scheduling, inventory, torn journals and terminal failures, comparison availability, interruption-safe readout, blind quality matching, ROC ties/abstention, budget reductions, rinse reuse, phase memory and finite/precision guards. They use CPU fixtures/fakes, including synthetic scalar tensors; they are not native model or scientific-outcome validation.

The design is ready for its final status change and stage-1 commit/push with this review. Preserve the warnings in the protocol/results, present the proposals for the user's choice, and stop at the prescribed stage-1 boundary. No server, paid computation, new scope, publication or held-out run is authorized by this verdict.

## Release-preflight correction, 2026-10-20

This is a narrow closure within the same independent review, not a second review. After the initial verdict, the author found that Windows CRLF manifest bytes had been hashed while Git stores LF bytes. Those references would reject the Linux checkout before execution. **B4, cross-platform manifest hash mismatch: closed.**

The reviewer inspected the correction: `source-list.json` and `asset-download-plan.json` are LF-only; their hash references were updated in the config, protocol and download ledger; the common JSON writer and standalone source writer now explicitly request LF. The new test checks LF bytes, referenced hashes and writer output. No source identity, asset entry, scientific setting or decision rule changed.

The reviewer independently compared working-file bytes with `git show :<path>` for sources, asset plan and profile. All three were byte-identical to the Git index, LF-only, semantically identical JSON and consistent with their configured hashes. Reconstructing CRLF for the source manifest also reproduced its original reviewed hash `e3bdfeb43308f880f02be6794d05e63bd7fe0fdf768c1181f0c8ff02eac3cfd1`.

| Manifest | Correct LF SHA-256 |
|---|---|
| Source list | `490d3d04efcf6e02a61eeadeacb7494313d2a5607b84fd57a7a2c0e6faea8b72` |
| Asset plan | `e7e742094fa1da7d0536f2f25820b963ce1d14ceb8a9a201687b9ec03ac3df0d` |

The profile hash remains unchanged. The reviewer reran the same CPU command above: **25 tests passed in 3.021 seconds**, including `test_json_hashes_survive_git_lf_checkout`. This supersedes the earlier 24-test count. The acceptance verdict and warnings remain unchanged; no open blocker was introduced.
