# WP4 offline results ledger

MEASURED/JUDGMENT: All results are exploratory saved-development analyses with prospective kills in [WP4-TEST-PLAN](../analysis/WP4-TEST-PLAN.md). Required T1-T4 and T0 rules/code preceded execution at6fcde02; TQ at65bb95a and TK2 at e029ff3. No endpoint replacement or Claude verdict is recorded. Frozen C/J stay frozen. PHASE_B_JOURNALS=off; CPU only, no writer/diffusion/training/install. Each Python invocation was under ten minutes. The79 reader batches total2265.023seconds but the longest single invocation is68.266seconds, with four CPU threads and one worker.

## Inputs, units and missingness

SOURCE: T0/T1/T4 use the declared Stage2-union and Phase-A development journals. Both studies reuse the same60 sources and are reported separately. Sorted even positions are DESIGN, odd positions EVALUATE;30 sources each. Pixel tests use the fixed first eight Stage2 sources30,72,73,89,127,165,309,370, four per half. Clean/D1/D3/X1/X2 controls are one call each; six regeneration cells use seeds12/13/14 and source-majority>=2. Missing seeds remain unsuccessful in the denominator.

SOURCE: The pixel inventory includes old development T4 and clean T5 panels, all available images, with the separate twelve-source sorted split fixed in the plan. Recipient split governs T4; donor split remains visible, so these reused pairs are not independent holdout attacks. The T5 manifest contains66 unordered pairs:7 same-semantic,57 different and2 uncertain, evaluated in both directions for each method. EVALUATE has30 directed different-content pairs; DESIGN30 and CROSS72 directions are reported separately. Reference-assisted T5 uses another image's clean q as center; it is not native blind verification or a successful forged image.

MEASURED: Inventory730 physical records,728 existing PNGs, includes10 accidentally overincluded old v5 C2 marks retained as supplemental, excluded from every primary result. Intended panel720 records. There are914 method/image items (432 F5,482 v5),911 successful reads and three missing method/image records from two physical safety-blocked files; no unprocessed items and no error attempts. Saved C0 is read by both readers. [Inventory/status](wp4-pixel-summary/inventory-status.csv), [supplement](wp4-pixel-summary/supplemental-C2.json), [failures](wp4-pixel-summary/failures.json).

## Reproducible commands and commits

SOURCE: Paths below are relative to this worktree. `STD` denotes MAIN `.thesis-build/venv/Scripts/python.exe -I`; `SCI` denotes MAIN `.thesis-build/a6-science-venv/Scripts/python.exe`. MAIN is `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5`. Exact argument arrays, full commit IDs, input/script/output hashes and durations are in each linked provenance. Read-only reductions use new output directories rather than overwriting retained results. Reader batch outputs retain the exact start/count in their filename and provenance.

| Test | Command after interpreter | Code commit(s) | Duration / result files |
|---|---|---|---|
| T0 | `analysis/offline_code_diagnostics.py --out wp4-t0` |6fcde02|2.063s; [provenance](wp4-t0/provenance.json), [summary](wp4-t0/summary.json) |
| T1 | `analysis/offline_metadata_tests.py T1 --out wp4-t1` |6fcde02|2.938s; [provenance](wp4-t1/provenance.json), [all cells](wp4-t1/cells.csv), [route/content calls](wp4-t1/calls.csv) |
| T4 | `analysis/offline_metadata_tests.py T4 --out wp4-t4` |6fcde02|2.047s; [provenance](wp4-t4/provenance.json), [summary](wp4-t4/summary.json) |
| T2/T3 inventory | `analysis/offline_pixel_tests.py inventory` (STD) |6fcde02|[inventory](wp4-pixels/inventory.json), [inventory provenance](wp4-pixels/inventory-provenance.json) |
| T2/T3 readers | `analysis/offline_pixel_tests.py batch --method {v5-r3,f5-r2} --start N --count B` (SCI) |30 batches6fcde02,30 batches9c607f8,19 batches65bb95a; reader unchanged|79 batches, longest68.266s; [batch run table](wp4-pixel-summary/batch-runs.csv), every paired JSONL/run.json in [raw outputs](wp4-pixels/) |
| T2/T3 reduction | `analysis/summarize_pixel_tests.py --out wp4-pixel-summary` (STD) |65bb95a; reducer correction first committed9c607f8|1.156s; [provenance](wp4-pixel-summary/provenance.json), [summary](wp4-pixel-summary/summary.json) |
| TQ | `analysis/quality_concentration.py` (SCI) |65bb95a|.485s; [provenance](wp4-tq/provenance.json), [summary](wp4-tq/summary.json) |
| TK2 | `analysis/content_calibration.py --out research/f5-components-20261101/results/wp4-tk2` (STD) |e029ff3|.384s; [run](wp4-tk2/run.json), [summary](wp4-tk2/summary.json) |
| Fixed-result reporting | `analysis/summarize_wp4_findings.py --out wp4-findings` (STD) |61f2935|.062s; [provenance](wp4-findings/provenance.json), [all findings](wp4-findings/summary.json) |

SOURCE: Prefix `analysis/` commands above with `research/f5-components-20261101/` when running from the worktree root. New output names are mandatory for reducers; batch output collisions are refused. Each reader batch repeats880 exhaustive synthetic checks of the exact-ball algorithm (sizes1..8, all radii in20 deterministic cases each). These checks validate the maximizer, not the watermark's statistical null.

## T1 — complementary evidence is real; direct union promotion fails

MEASURED: All14 judge native method/cells reproduced, then extended to all22 development study/cells per method, including mode/smooth/rinse and PhaseA. [Report](wp4-t1/REPORT.md) and source/call tables retain all routes and missingness. F5 EVALUATE Stage2 source-majority counts, denominator30:

| Native cell | Frozen C | Frozen J | O | O_U | O_Q |
|---|---:|---:|---:|---:|---:|
| SD1.5 .1 |30|20|30|30|30|
| SD1.5 .2 |30|20|30|30|30|
| SD1.5 .4 |21|7|21|20|20|
| SDXL .1 |0|0|19|19|4|
| SDXL .2 |0|0|8|7|2|
| SDXL .4 |0|0|2|1|0|
| K3 .2 |3|0|8|6|2|

DERIVED: O=C OR(instance.found AND instance.content_match). It combines one decoded semantic route and two instance routes. Under the original conditional random-sign null, original either-found<=4e-6 while O<=3e-6; neither inherits a1e-6 total budget. O_U allocates alpha/4 to each included route: recomputed threshold5.2438041053, decoded8.4232311967, conditional union<=.75e-6 with one unused share. O_Q additionally enumerates all possible q choices; its decoded instance threshold10.7163841531 is much stricter. These are conditional model bounds, not security against a fixed-public-key adaptive image attacker. No observed zero panel empirically certifies1e-6.

SOURCE/MEASURED: When semantic evidence is absent its comparison is unchecked, not independently consistent with a decoded q. The instance route checks h under the selected/recomputed q. The raw routing/content states are frozen in the journal analysis; thresholds do not trigger a fictitious reroute. On Stage2 EVALUATE the semantic-absent instance-content source successes are15/8/2/3 in SDXL .1/.2/.4 and K3 .2. Across overlapping study/cells O_U initially passes necessary F5 metadata screens (57 foreign source-cell gains,0 SD1.5 .1/.2 losses,0 saved C0/wrong events); v5 fails with4 low-strength source-cell losses despite15 foreign gains. These are not57 or15 independent recovered sources.

MEASURED: The saved T4 pixel panel falsifies safe F5 union promotion: **1/20 EVALUATE residual-transfer images** accepts O/O_U while C accepts0/20. Exact event `t4-residual-177015-25394-0.5`, donor177015 DESIGN, recipient25394 EVALUATE. Historical attack-row PSNR49.9810dB and SSIM.995024 pass those two checks; LPIPS and human visibility are MISSING, so no complete strict-quality attack claim is made. The old combined outcome was instance_only, semantic_found=false. The error-budget adjustment does not remove it. [Event and provenance](wp4-findings/summary.json).

JUDGMENT — KILL: K08-O1/K09-O2/K10-O2 fail promotion under the fixed new-negative rule. Preserve complementarity as a physical/research observation. A cross-tier-only veto cannot remove this semantic-absent attack, so K10-O3 as specified is insufficient. Gate-2 N3 corrects the broader inference: an intra-tier decoded-word contradiction DOES exist (12 bits from h), ignored by the recomputed route just below the decoded cutoff. Rejecting every unchecked case would sacrifice exactly the foreign evidence N1 highlighted and is a different future policy, not a post-hoc rescue here.

## T2 — exact maximization adds little and exposes binding failure

DERIVED: Disjoint segments and a common denominator make the exact score the center score plus up to r largest positive flip gains. The candidate family has sum(j=0..r) choose(32,j) words. r3 is primary;0,1,2,4,6 are descriptive, never selected or ORed after outcomes. A ball detection event is not frozen C/J or proof the decoded payload is the original content.

MEASURED: In the Stage2 EVALUATE pixel subset, F5 has0 extra calls/91 and0 extra source-cells over the corrected two-candidate bound. v5 has1 extra call/92 but0 extra source-cells, plus1 new T4 negative beyond the lower bound. F5 T4 r3 accepts1/20 images versus C=0/20 (that event was already accepted by the lower bound). v5 T4 r3 accepts29/40 versus C=1/40, including its residual/public-projection panels; sham0. Shared-owner marked images are not an unmarked null, so those counts specifically challenge binding interpretation.

MEASURED: Reference-assisted different-content T5 EVALUATE gives F5 exact30/30 versus lower28/30; v5 exact30/30 versus lower30/30. Two F5 extra negative comparisons violate the fixed negative rule. These30 directions involve only six report-half images and are dependent. Gate-2 verification extends the F5 wrong-content result to114/114 total directions:22 DESIGN,30 EVALUATE,62 CROSS. Same-semantic and uncertain cross-half pairs remain in the raw table, not filtered away. No native blind T5 forgery rate is inferred.

MEASURED: No C0 or wrong-owner r3 event appears in the evaluated pixel calls. Across both halves1100 calls with saved comparable scores pass the predeclared replication tolerances (v5 absolute1e-3; F5 CPU.05);312 old-panel calls have no matched historical full-score reference and are labeled NO_MATCHED_REFERENCE. There are0 failed comparisons, not1412 validated comparisons. The exactness checks and raw projections remain available for audit.

JUDGMENT — KILL: K09-O1 has no primary F5 recovery and new wrong-content events; v5 gains one call but adds a new negative and no source recovery. No radius retuning follows. This rejects promotion on the prespecified panel, not the mathematical algorithm or all untested stronger cells. Antipodal/global-code writer options remain unmeasured; T2 cannot simulate their new targets.

## T3 — tier order is consistent with scale, but scale's causal share is unidentified

MEASURED: Paired C1-C0 original-pattern alignment, normalized to each clean source then averaged over seeds and median over four EVALUATE sources:

| Method/cell | Robust retention | Second-carrier retention |
|---|---:|---:|
| F5 SD1.5 .2 |.726189|.005154|
| F5 SDXL .2 |.093426|.269442|
| F5 K3 .2 |.161632|.143618|
| F5 SDXL mode .2 |.087173|.255887|
| F5 SDXL smooth .2 |.069535|.194070|
| F5 SDXL rinse .1 |.078010|.266856|
| v5 SD1.5 .2 |.259359|.004871|
| v5 SDXL .2 |.240816|.273259|
| v5 K3 .2 |.441258|.148867|

MEASURED: F5 passes the prespecified ordering check on both halves. v5 passes EVALUATE but fails DESIGN, weakening any broad universal story. Resize-only F5 second-carrier retention is.984584/.983106 for X1/X2, versus robust.883887/.795503; simple resizing alone does not reproduce the SD1.5 collapse. Codec controls D1/D3 and all raw band/host values are in [response cells](wp4-pixel-summary/T3-cell-responses.csv), [source responses](wp4-pixel-summary/T3-source-responses.csv) and [paired values](wp4-pixel-summary/T3-pairs.csv). The six second-tier block-DCT positions, pixel robust band, F5 latent band, marked/C0 norms and aligned differences are all retained, not replaced by a single detection score.

JUDGMENT: Family and working resolution are aliased in native cells. The design matrix lacks independent family/scale variation, so no percentage attributable to resolution can be estimated. Matching response order is compatible with N2, not proof of it. Nonlinear C1-C0 host interactions also prevent calling this an isolated transported mark; F5 h target is a clean decoded proxy, not a saved intended h. Q-RES is the discriminating intervention. “All carrier gone” and “mostly resolution” remain unsupported causal claims.

## T4 — final margin predicts survival, not its cause

MEASURED: DESIGN median margin cutoff1.0033376911 frozen before EVALUATE. On30 EVALUATE sources, Spearman rho=.6315906563 between clean median margin and mean foreign decoded score;17 above-cut versus13 below-cut sources differ by+.7768209856 score units. DESIGN rho=.5506117909, gap+.9768072870. Thus rho>=.30 and positive-gap rules retain a predictive lead. Per-cell and diagnostic covariates are retained in [T4 files](wp4-t4/).

JUDGMENT: Final-only metadata cannot distinguish failure to converge from clipping, RGB8 rounding, second writing or refinement. No actual per-stage distortion share or spendable budget follows from nominal dB settings. Q-STAGE must save residuals and margins at each stage and compare a robust-only equal-final-quality arm. No writer optimization was run.

## Additional decisive checks

MEASURED: T0 binding-only headroom on F5 foreign EVALUATE source-cells is1/207 losses (.483%); v5 is2/121(1.653%). Overlapping studies are not independent. Both fail the10% primary-repair rule. The two-owner deterministic codebook has64 option pairs, six at distance2 and minimum2: no guaranteed one-chip correction. This is about payload segment code, not q32 hash distance or random-key security.

MEASURED: TQ's fixed C0 texture masks give F5 EVALUATE median max-patch/global residual RMS1.3092 and flat/textured1.1619, below the respective2 and1.5 thresholds. Kill local concentration as a demonstrated F5 priority. v5's2.8886 and.3283 retain only a concentration diagnostic. No human visibility, SSIM or LPIPS verdict is inferred.

MEASURED: TK2 on historical single-view v5 saved features fits DESIGN additive bias+.1448109 bits. EVALUATE source-weighted MAE falls1.5253129 to1.4595937, only4.3086%, below10%; kill this simple calibration priority. Five DESIGN planned feature rows are unavailable, retained; EVALUATE has65/65 across five planned T3 sources. The two clean-only sources determine parity but are not invented T3 attempts. This does not test F5 seven-view soft likelihood, an uncertainty interval or a new detector.

JUDGMENT: K11's public-image entropy and self-signed-tuple counterexamples are logical tests of claimed guarantees; no experiment can make a deterministic public feature secret merely by hashing it. T1's null audit also blocks ungrounded e-value fusion. These are limits on claims, not measured attack rates. Every option is mapped to a run, logical falsifier or specifically unavailable intervention in [OPTIONS](../OPTIONS.md); no feasible writer execution is silently omitted because all such execution is forbidden here.

## Gate-2 fixed follow-up tests

SOURCE: Rules/code committed dde7280 before any B EVALUATE outcome; no threshold, radius, veto, pair list or scale changed. Commands use the same STD/SCI interpreters above. [Plan](../analysis/GATE2-TEST-PLAN.md), [complete interpretation](../GATE2-SYNTHESIS.md).

| Test | Command (RD prefix) | Run HEAD / output commit | Outcome and provenance |
|---|---|---|---|
| G2-A | analysis/gate2_saved_tests.py G2-A (STD) | dde7280 / f37ca3b | KILL:19/120 foreign gains but3 distinct SD1.5 .2 losses, repeated in2 studies;4.63s. [provenance](g2-a/provenance.json), [22study/cells](g2-a/cells.csv), [diagnosis](g2-a/DIAGNOSIS.md) |
| G2-B | analysis/gate2_transfer_panel.py --inventory; --start N --count8 (SCI); --summarize (STD) | f37ca3b / db98c6f; test code unchanged since dde7280 | KILL:2 B-not-C events/480, one donor-recipient pair at both scales.60 batches<=63.437s,4workers, no missing/error; all480 strict PSNR/SSIM, local LPIPS available. [summary/provenance](g2-b-transfer/summary.json), [donor](g2-b-transfer/by-donor.csv), [recipient](g2-b-transfer/by-recipient.csv) |
| G2-C | analysis/gate2_saved_tests.py G2-C (STD) | db98c6f / a0bd31e | No kill.1,770 dependent clean-code pairs; q concentrated relative to uniform, h more separated.0.953s. [provenance](g2-c/provenance.json), [all split summaries](g2-c/summary.csv) |

JUDGMENT: Gate-1 SDXL32/12 recomputed-inclusive content-ok values are withdrawn as gains; physical found52/30 remains. N3 is specifically a recomputed-route failure, while G2-B also demonstrates a decoded-route failure. Conditional-q is the primary PRF honest-null statement, O_Q sensitivity only; neither covers same-owner signal transplants or public adaptive images. C/J remain frozen. No soft rescue or new B policy follows.
