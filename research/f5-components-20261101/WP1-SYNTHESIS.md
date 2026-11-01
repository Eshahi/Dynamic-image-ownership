# WP1 structure, loss ceilings and challenge to the judge

JUDGMENT: All dispositions here are PROPOSED. Gate 1 requests Claude's ruling; this document selects no method, changes no endpoint, reopens no closed line, and authorizes no compute. Scope: BRIEF.md sections 1 and 4. `PHASE_B_JOURNALS=off`.

## What is established and what is not

MEASURED: The independent accounting reproduces all 14 F5/v5 native-cell loss partitions in the judge's saved JSON and all 84 radius counts produced by its actual code. It extends to every Stage-2 union cell (15 per method) and every Phase-A detector cell (7 per method): 44 marked cells, 88 corresponding C0/wrong-owner cells. No model was loaded, no writer was executed, and no image, held-out journal or Phase-B transfer archive was opened. Exact input files, line-level source locators, hashes, commands and code commits are in `results/wp1-accounting/provenance.json:1`, `source-accounting.csv:1` and `analysis/account_saved_development.py:1`.

SOURCE: Phase A includes six native R0/R1 cells and its B-codec control. The K3 mechanism module is not a 60-source native detector cell. The 5,040 attack-grid outputs were quality-ineligible and not released for detection; their C/J and component ceilings are UNKNOWN. The pilot and regeneration-channel study contain mechanism/channel diagnostics rather than an additional complete C/J grid. Earlier development variants are retained as report-level evidence in `context/wp1-prior-evidence.md`; absence of a raw endpoint is not filled with a fabricated count. Locators: `results/wp1-accounting/phase-a-coverage.csv:1`; `research/encoder-transfer-20261019/final-study-20261025/phase-a/PHASE-A-REPORT.md:9,35-46`; `context/wp1-distortion-challenge.md` sections 5–6.

DERIVED: Stage 2 and Phase A use the same 60 sources and three prescribed seeds; they are not independent validation sets. Source-majority means at least 2/3, while clean/codec/resize one-image controls use 1/1. Missing calls count unsuccessful in the primary count and have separate possible-success bounds. All new counts are exploratory development evidence. The committed Phase-B, M2 and registry reports are frozen contextual evidence only; no setting was selected from them. Locators: `results/wp1-accounting/provenance.json` source_overlap; `analysis/WP1-ACCOUNTING-SPEC.md:13`; component B sections and historical evidence inventory.

## Corrected component map

SOURCE/DERIVED: These corrections follow the executable code audited in `context/wp1-code-structure.md`, K1–K12 sections (each supplies exact repository code lines). Preserve the 12 IDs for continuity; split subfunctions inside IDs rather than inventing extra literature floors.

| ID | Corrected component boundary | Material correction |
|---|---|---|
| K1 | Descriptor and preprocessing | Seven-view normalized CLIP mean for F5; one view for retained v5; self-check may use supplied source features. |
| K2 | Content code and compatibility model | 32 Rademacher bits plus a continuous soft-angle approximation; it is not an exact angular-distribution identity. |
| K3 | Segment codebooks and payload | Two random ten-chip options per semantic bit, four per instance segment; no parity across bits. Not literal tenfold repetition. |
| K4 | Carrier and normalization | 3,272 latent-DCT slots, radius [4,32), 10/11 slots per chip, two distinct normalization operations. |
| K5 | Reader encoder and writer channel surrogate | Same pinned SD1.5 encoder, but replacing the reader and expanding the writer's channel model are distinct interventions. |
| K6 | Objective and optimizer | Unnormalized hinge margins; 150 initial + 50 refinement gradients, with no saved convergence certificate. |
| K7 | Global/local quality and quantization | Separate source centers for 52/58 dB solves, four RGB8 conversions, no final source-centered budget. |
| K8 | Instance descriptor, fragile fits and order | Robust → fragile → robust refinement → fragile; two fragile fits with recomputed h. |
| K9 | Statistic, null calibration and error model | Normalized score, search multiplicity, approximate bit-error correction are separate assumptions. |
| K10 | Binding decision and endpoint interface | C/J/F/H/A differ; J concerns original semantic q, not the fragile tier. |
| K11 | Key derivation, side information and identity | Public deterministic streams; evaluator q/h is not reader input; profile hash alone omits some F5 settings. |
| K12 | Protocol and measurement | Source/seed nesting, negative A versus positive C, unavailable calls, family/resolution/schedule confounding. |

DERIVED: F5 versus v5 is a system comparison, not an isolated K4/K5 intervention. Descriptor views, binding, writer, budgets and order differ. Thus their performance difference cannot be assigned numerically to carrier space or encoder alone. Locators: `scripts/encoder_transfer_runtime.py:154-179`; `scripts/journal_vae_probe.py:60-69`; `scripts/f5_latent_codec.py:230-250`.

## Finding 1: operational partition reproduced; causal ownership rejected

MEASURED: For F5, the following counts reproduce Stage 2. B means semantic decoded but content failed; U means semantic found only by recomputation; L means neither semantic test passed. M remains unavailable. Sources: `results/wp1-accounting/loss-cells.csv:20,22,24,26,28,30,38`.

| Cell | C/B/U/L/M calls (/180) | Frozen C /60 | Perfect content on fixed reads /60 | Convert fixed semantic found /60 |
|---|---|---:|---:|---:|
| SD1.5 .1 | 179/0/0/0/1 | 60 | 60 | 60 |
| SD1.5 .2 | 170/3/4/0/3 | 57 | 58 | 59 |
| SD1.5 .4 | 117/25/26/10/2 | 39 | 47 | 58 |
| SDXL .1 | 0/3/23/154/0 | 0 | 1 | 7 |
| SDXL .2 | 0/0/0/180/0 | 0 | 0 | 0 |
| SDXL .4 | 0/0/0/180/0 | 0 | 0 | 0 |
| K3 .2 | 16/6/46/112/0 | 5 | 7 | 23 |

MEASURED: Phase A changes F5 SD1.5 .2 to 171/3/4/0/2 and fixed-read/found ceilings to 59/60, with C still 57; .4 is 116/26/26/10/2 with C 39; SDXL .1 is 0/3/21/156/0, still C 0. v5 SDXL .2 C is 11 rather than Stage-2 12. These remain separate studies with their own rounding/kernel paths. Locators: `results/wp1-accounting/loss-cells.csv:4,6,8,11,29`.

DERIVED: A perfect decision on fixed decoded words cannot recover the U/L pool as frozen C. This supports the judge's small *conditional* content-only budget. It does not prove the original code is correct in B, that L contains zero signal, or that K4/K5 exclusively caused L. Changing the descriptor/code, statistic, writer or quality can move several classes at once. Per-component unrestricted ceilings are UNKNOWN, except the trivial 60 minus current C headroom. Shared oracle budgets must not be added. Source: `scripts/m1b_e3_s1_analysis.py:70-84`; `context/wp1-code-structure.md` section “What saved scores can and cannot identify.”

SOURCE: Phase-A mechanism evidence is more specific: SDXL target-chip retention goes .66 after mode codec to .08 after noise injection, remaining .08 at native output; encoder amplification transfers. Its report explicitly calls these paired descriptive observations noncausal. The original F5-r1 gate had a large binding bottleneck before r2's soft/7-view changes, so current foreign-cell binding losses cannot establish that K1/K2/K10 never matter. Locators: `research/encoder-transfer-20261019/final-study-20261025/phase-a/PHASE-A-REPORT.md:89-114`; `research/f5-encoder-amplified-latent.md:53-56,101-114`.

JUDGMENT: Retain channel-level priority but replace “carrier gone / K4+K5 own the failure” with “frozen semantic tests fail; joint carrier–surrogate–objective–budget failure remains incompletely identified.” This is the proposed disagreement on Finding 1, not a denial of the measured transfer failure.

## Finding 2: real implementation error; benefit still not a safe endpoint

SOURCE: `judge/reader_ball.py:61-67` uses `semantic.candidate` as the content-code center, but that field is the route label decoded/recomputed/null (`scripts/revised_watermark_v5.py:1255-1259`). The correct saved center is `raw.semantic_code`. Therefore its decoded-in-ball branch never added a hit. No judge file was edited.

MEASURED: Reproducing that actual rule matches every saved radius count. Correcting the center preserves all main r0/r3 values quoted by the judge, but changes additional radii and controls: F5 SD1.5 .4 r6 rises 42→45, F5 K3 .2 r6 8→9, v5 SDXL .1 r6 46→52, and v5 posterior-mode .2 r3 16→18. These are two-candidate lower bounds, not an executed full constrained decoder. Locators: `results/wp1-accounting/loss-cells.csv:24,38,27,33`; column names distinguish reproduction, corrected lower and global-decoded upper.

DERIVED: The two-candidate bound uses the recomputed score and the global decoded score only when its code lies in the proposed ball. It may miss the true best interior code. Radius zero is the exact single recomputed pattern; larger radii cannot be evaluated exactly from two scalars alone. A raw Hamming ball also differs from F5's soft-angle acceptance, and from v5's corrected-Hamming acceptance. It is a new endpoint B_r, never frozen C/J. Locators: `scripts/revised_watermark_v5.py:1178-1199`; `scripts/f5_latent_codec.py:148-155`; `context/wp1-code-structure.md` final two technical sections.

MEASURED: The diagnostic r0 rule has no observed C0/wrong-owner hits across the 88 negative cell groups; for r>0 the saved-score lower bounds also have none. Those larger-ball zero lower bounds do NOT establish zero hits for the full ball maximizer. Neither stratum tests copy-paste or semantic collision. Locators: `results/wp1-accounting/negative-cells.csv:1`; `analysis/account_saved_development.py` classify and summary functions.

DERIVED: A conditional random-sign argument can justify the ball cardinality if its center/set is independent of tested table signs after conditioning and image/owner selection is nonadaptive. Shared image input alone does not invalidate it. Actual public deterministic HMAC streams and adaptive chosen-image attackers do not automatically satisfy a fresh-random-key population theorem. Separate recomputed/decoded tests spend separate nominal budgets: found is an OR, so 1e-6 per branch is not 1e-6 for every composite endpoint. C is a subset of the decoded semantic branch. Locators: `scripts/revised_watermark_v5.py:1149-1175,1244-1265`; `context/wp1-code-structure.md` “Conditional null validity and multiplicity.”

JUDGMENT: Keep K9/K3 as promising cheap investigation, with specificity and exact-q constraints attached. The bug weakens the original interpretation but does not refute the useful recomputed-score signal. Do not claim the correction itself creates a deployable improvement or that independent content evidence survives at r0.

## Finding 3: budget arithmetic reproduced; forecast and universal extinction rejected

DERIVED: Converting nominal PSNRs gives MSE47=1.2974, MSE52=.4103 and MSE58=.1031 byte-squared. Relative to rounded median final44.96 dB, the first two ratios are 62.52% and 19.77%; sqrt(MSE44.96/MSE52)=2.249. These reproduce the judge's arithmetic, but are not measured orthogonal energy shares or a feasible amplitude gain. The four-stage writer has cross terms, host rejection, two fragile fits and quantization. Locators: `results/wp1-writer-metadata/summary.json:1`; `context/wp1-distortion-challenge.md` sections 1–3; `scripts/f5_latent_codec.py:230-260`.

DERIVED: The score is `max_w p·w / ||p||`. Scaling all p leaves it unchanged; even a linear signal model p=b+a*d produces a nonlinear normalized score. Thus multiplying the observed SDXL decoded score by 2.249 does not forecast threshold crossing even under linear regeneration. SDXL's measured nonlinearity is an additional obstacle. Locators: `scripts/revised_watermark_v5.py:1178-1199`; `research/encoder-transfer-20261019/final-study-20261025/phase-a/PHASE-A-REPORT.md:72-85`.

MEASURED: Fragile extinction holds in the observed SD1.5 native cells, but not across all foreign families. Stage-2 F5 SDXL .1 has instance found/read/exact-H/F source counts 52/37/3/5, and SDXL .2 has 30/19/0/0; K3 .2 has 16/2/0/8. F=`both_match` can succeed through recomputation while C/J fail. J=exact semantic-q plus content match does not test the fragile tier. F5 clean C/J/H/F is 60/52/34/60. Locators: `results/wp1-fragile/fragile-cells.csv:26,28,38,44`; `scripts/m1b_e3_s1_analysis.py:70-84`. H uses the transfer adapter's saved clean decoded h for F5, a limitation documented in `scripts/encoder_transfer_runtime.py:160-167`.

MEASURED: Saved final writer margin median is 1.036 across the 60 sources; every source median is below target4, and 56/60 have negative chips (median17, maximum72). These are final post-fragile values, not convergence traces. Root independently reproduced the agent's metadata reduction with committed stdlib code. Locators: `results/wp1-writer-metadata/summary.json:11`; `sources.csv:1`; `analysis/writer_metadata.py:1`; `scripts/f5_latent_codec.py:251-260`.

JUDGMENT: K8 may consume useful distortion budget yet also supplies observed instance detections; removing it changes interpretation and T4/T5 behavior. K6 is unresolved, not shown adequate. A later intervention needs pre/post-stage residuals and margins to distinguish infeasible target, incomplete optimization, rounding and final fragile interference. Current recovery forecasts for each are UNKNOWN.

## Finding 4: morphology is a lead, not a measured candidate capacity

SOURCE/DERIVED: The saved morphology gain is a pooled differential projection slope, not retained energy, per-source median, bit SNR or latent-reader score. Its “luma” axis is equal-RGB `(R+G+B)/sqrt(3)`, different from perceptual Y. The selected-band F5 slopes 1.76/.35/.60 reproduce for SD1.5/SDXL/K3 .2, but marks differ in distortion and structure simultaneously. Chroma residual RMS ratios span about 2.47–4.01 in the cited band, and include systematic content change. Locators: `research/coarse-lattice-20261030/measure_channel.py:37-42,96-124`; `channel_report.py:55-57,75-94`; `context/wp1-distortion-challenge.md` section 5.

SOURCE/DERIVED: The channel capacity code uses clipped host gain despite prose describing best mark-response gain. Its scalar-channel capacity estimates therefore cannot serve as measured achievable bits or rigorous general bounds under nonlinear regeneration. True coarse-lattice T3 remains simulated and visible flat-region blotches remain unresolved; positive quality metrics do not establish invisibility. Locators: `research/coarse-lattice-20261030/channel_report.py:97-111`; `PROPOSAL.md:53-64,74-87`; `context/wp1-distortion-challenge.md` section 5.

JUDGMENT: Search morphology/chroma literature, preserve F4's failures and later stronger-but-costlier variant, and retain coarse lattice as an unprivileged candidate. Evidence does not select it over the approved F6 package or establish a count recovery for K4/K7.

## Ranking by conditional loss opportunity and cost to change

JUDGMENT: This is an effort ranking, not an estimated additive causal allocation. Each component file has its own 22-cell F5 ceiling table; `results/component-ceilings.csv` is the machine-readable crosswalk. The named oracles hold specific stages fixed and may violate safety if implemented literally. Unrestricted gains remain UNKNOWN.

| Priority | Components | Loss opportunity actually supported | Cost to change and evidence cost | Proposed literature emphasis |
|---|---|---|---|---|
| 1 | K4/K5 with K6/K7 interaction | Stage-2 SDXL .2/.4 have 180/180 semantic L calls; individual ownership UNKNOWN. Phase A localizes much loss after codec/noise. | High: new writer/native outputs; unknown incremental runtime. Historical F5 total119 s/mark is an anchor, not a marginal component cost. | Noise-stage signal alignment, finite-response surrogate, representation, interference. |
| 2 | K9/K3 | Fixed semantic-found envelope adds at most19 C sources at SD1.5 .4,18 at K3 .2,7 at SDXL .1; zero at SDXL .2/.4 under this restriction. Exact-q reliability also fails on 8/60 clean marks. | K9 score diagnostics cheapest; full CPU reader rerun more expensive; K3 code changes generally require new marks and calibration. | Constrained soft decoding, short codebooks, valid null and content-specific rejection. |
| 3 | K7/K8 | Distortion saving UNKNOWN; foreign fragile found/read is nonzero. Any semantic improvement requires a physical intervention. | High: save stage intermediates, rewrite, measure actual quality/T4/T5 and native outcomes. | Perceptual/local budget and tier interference; never infer savings from nominal budgets. |
| 4 | K6 as a separate diagnostic | Final target shortfall all60; optimization-specific share UNKNOWN. | Metadata cheapest; actual convergence/target feasibility test requires later writer permission. | Objective versus final normalized statistic, quantization-aware and constrained optimization. |
| 5 | K1/K2/K10 | Fixed-read C oracle adds at most8 at SD1.5 .4,2 at K3 .2,1 at SDXL .1; original-q J oracle there adds2,0,0. Binding protection remains crucial to T4/T5. | K10 checks cheap; K1 extraction adds seven CLIP passes; changing descriptor/code with marks is high cost. | Specificity-preserving compatibility, calibration, near-duplicate separation; no reopened descriptor variants yet. |
| Cross-cutting | K11/K12 | No direct algorithmic recovery under unchanged pixels/scores; they determine valid claims and missingness, not extra detections. | Low for assumptions/accounting; new trust model or fresh evaluation has separate cost. | Public-derived limits, independent families, operational T4/T5, source-level evidence. |

SOURCE: Historical full write cost119 s and approximate detector-row1.5 s are BRIEF.md WP5 anchors; no CPU timing or per-component speed is inferred from them. Cost ranking distinguishes reader arithmetic, feature/model passes, rewritten images and fresh native regeneration. K1/K2/K10 can be cheap to inspect while low in current restricted T3 headroom. Code timing scopes: `context/wp1-code-structure.md` K1/K5/K6/K12.

JUDGMENT: Proposed order is offline K9/K12 diagnosis alongside focused K4/K5/K6 literature, without changing the approved F6 priority or package. No current result warrants authorizing robust-only, coarse-lattice, RL or new external-baseline compute. A later proposal can request a changed order after Gate 2 evidence. Sources: BRIEF.md “Frozen elsewhere” and “Closed lines”; `context/wp1-distortion-challenge.md` section 6.

## WP2 plan and gate boundary

JUDGMENT: `literature/WP2-QUERY-PLAN.md` supplies 15 exact planned queries per component across five planned indexes, 180 total, with a 30-query exhaustion route. No query is represented as executed and no paper/card/venue is counted at WP1. Required totals are 56 Q1J +36 TOP component assignments; no conference is labelled Q1. Claude may reweight emphasis at Gate 1 while the brief's floors remain in force unless explicitly ruled otherwise. Source: BRIEF.md sections 3–4.

JUDGMENT: Gate 1 must rule on map corrections, conditional versus causal loss ownership, proposed search weighting, the reader-ball interpretation, and the narrowed fragile/morphology claims. Subsequent literature/options/tests remain WP2–WP5. This turn stops after the Gate-1 request and complete WP1 package are committed and pushed.
