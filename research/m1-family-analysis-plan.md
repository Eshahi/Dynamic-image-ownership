# M1 descriptive family aggregation plan

Status: prospective analysis implementation, no retained-run analysis executed by the author. Entry `scripts/m1_analyze_families.py`, optional repeated `--reconstruction-dir` in chronological order, `--reconstruction-pause-receipt`, single `--gs-dir`, single `--progressive-dir`, fresh `--output-dir` under MAIN `.thesis-build/dev-runs`. Any family subset is permitted. No GPU, model, image decoding, held-out split, new experiment, human assessment or acceptance verdict is used. CPU fixtures validate implementation only.

Input provenance pins bytes/SHA256 of source `run.json`, family row/journal file and exact manifest recovered from recorded command. Manifest must match the run's manifest hash before its cohort is used. Missing/corrupt files, invalid journal lines, mismatched manifest hashes and noncompleted source outcomes remain explicit source errors and make analysis incomplete. A missing planned endpoint remains a raw-table row when its exact cohort/config is available. If the cohort cannot be recovered, its denominator remains unknown instead of inventing a sample. Duplicate GS measurements are ambiguous, never selected for favorable scores. Progressive complete attempts are distinguished from retained failed/interrupted attempts; multiple completed duplicates are ambiguous. Partial measured endpoints from failed parents are retained and labelled `observed_partial`, alongside missing endpoints. Source errors and traceback are copied into provenance.

Reconstruction: inventory exact planned case IDs at steps0/50/100/200. Report observed/missing counts, PSNR/SSIM/LPIPS minimum/median/maximum, infinite-PSNR count, complete-quality count and conjunction count for strict PSNR>35dB, SSIM>0.9, LPIPS<0.1. Missing LPIPS or any nonfinite/incomplete metric fails the measured conjunction. Count all planned cases as the denominator. A measured optimization route cannot prove a universal VAE ceiling. Partial checkpoints remain visible and cannot close a planned trajectory.

Interrupted reconstruction and recovery: invoke the original `20261003-1455-latent-reconstruction` directory first, then `20261003-2255-latent-reconstruction-recovery`, with explicit `--reconstruction-pause-receipt research/m1-pause-artifacts-20261003.json`. Do this only after recovery finishes; implementation does not inspect its scientific output. The original manifest plans twelve sources; recovery plans eight, while the original four completed sources remain selected. These are twelve sources, not twenty. Each selected source contributes exactly four checkpoint rows. `reconstruction-attempts.csv` preserves every original/recovery planned checkpoint, including the original interrupted fifth case's partial trajectory and unattempted endpoints, with `selected_final_attempt` and ordinal attempt sequence. `reconstruction-raw.csv` contains only the selected whole trajectory per source. Its `chosen_run_directory` and `chosen_run_sha256` identify the exact contributing source run bytes; original source hash, case outcome, unchanged source-run outcome and pause qualification are retained too.

Selection is prospective chronology, never quality ranking or mixing checkpoints: a later overlapping source replaces its earlier whole trajectory only when its pinned manifest's `recovery.previous_run` names the earlier selected run basename, its `recovery.receipt_sha256` equals the explicit receipt's hash, and that predecessor is a receipt-qualified interrupted run. Both overlapping completed cases without this mapping and duplicate actual cases/checkpoints are conflicts. A mapped but missing/partial recovery trajectory stays missing/partial even if the original has better or complete measurements. Case identity/path/hash and the complete reconstruction configuration must match across attempts; run configuration must equal its manifest and retain steps `[0,50,100,200]`. Unknown cohorts remain unknown, with explicit incomplete status, rather than using observed rows to invent a denominator.

Pause qualification requires hashing every receipt-listed artifact under relevant source-run directories, including PNG/PT bytes without decoding or executing them; size and SHA256 must match. Both `run.json` and `images.jsonl` must be pinned for each qualified directory. Duplicate receipt paths, changed artifacts, mismatched receipt hash or wrong predecessor order reject recovery aggregation. Receipt provenance records its own hash and validated artifact records. The original `outcome=started` is preserved; only a matching receipt establishes the recorded interruption. An unqualified started/failed source makes aggregation incomplete. A qualified historical interruption alone does not make a fully covered recovered cohort incomplete, while any source parsing/provenance error or missing selected endpoint still does. Historical partial measurements remain visible in the attempts CSV and are never silently discarded or counted as additional sources.

Gaussian Shading: inventory clean, VAE and every predeclared regeneration-strength/attack-seed channel for each planned C0/C1 case. Count C1 correct-key detections, C0 detections and wrong-key detections separately, alongside detector runtime distribution and inversion UNet calls. Missing endpoints are not true negatives. Quality C1 versus paired C0 is generated counterfactual distortion because initial signs differ; it is not fixed-source imperceptibility or photographic-source fidelity. Same-arm attack quality is included with `attack_` prefixes, not reinterpreted as a source-quality result.

Progressive guidance: inventory C0 and each alpha/eta C1 at clean/VAE/T3 conditions, separately for native VAE+DCT extractor and image-DCT diagnostic. Count correct-payload detections, complementary wrong-payload detections, and fixed64 wrong-query positives/queries. These hypotheses share an extracted word and repeat across dependent variants/attacks, so aggregate query counts are descriptive and do not provide independent-image population FPR. Report native/diagnostic timing separately. Quality summary uses unique clean native C1 row per seed/variant versus matched same-initial-noise C0, avoiding multiplication of quality denominators by repeated extractors/attacks. No CLIP/content/OwnerID dual-key authenticity claim is derived from this carrier.

Outputs: `analysis.json`, family raw and grouped summary CSVs, reconstruction/progressive attempt CSVs, `manifest.json` and analysis `run.json` with script/commit/command/config/input hashes, each reconstruction attempt's source commit/config/split/duration/errors, receipt provenance, source statuses/seeds, elapsed duration and outcome. `completed_descriptive_analysis` denotes completed aggregation only. Any missing/failed input or selected endpoint produces `incomplete`, except the verified historical interruption described above; failed parsing of one family is retained without hiding available other families. Thresholds and payloads are read from preregistered source records; no threshold search, best-variant selection, confidence interval or generalized method-success claim is performed. Standard scientific plots can consume CSVs later.

Same-arm attack PSNR/SSIM/LPIPS and CLIP cosine are exported for GS/progressive when present, including minimum/mean/median/maximum. Optional `detect_and_semantic_retention_proxy` is observed detector-positive AND same-arm CLIP cosine>=0.85. This analysis-only descriptive proxy is fixed before analysis, does not change the source detector threshold or existing three-metric quality criterion, and cannot substitute for human visual assessment or semantic equivalence. Missing cosine remains unmeasured, never false/zero by imputation.

## Appendix: A dual-latent and D PhaseMark pilot adapters

Added CLI inputs: repeated `--dual-dir PATH` and one `--phasemark-dir PATH`. Other family adapters and reconstruction recovery selection remain unchanged. This extension was tested on generated JSON metadata fixtures only; no moving retained run, image, tensor checkpoint, model or GPU result was analyzed. Parent should invoke it only on stopped/final input snapshots. A `started`, failed/interrupted or partially recorded run remains `incomplete`; completed analysis is descriptive only.

A uses its exact manifest `case_ids` and `config.routes`, checks run/manifest configuration equality, and reads only the development reservation metadata `research/m1-reconstruction-dev.json`. The source metadata JSON is pinned alongside run, manifest and journal hashes; image paths in it are not opened or hashed. It exports five cells per declared source/route: C0_source, C0_matched, C1, C0_VAE_cycle and C1_VAE_cycle. Source PSNR/SSIM/LPIPS, recorded admissibility, correct/wrong-owner found/present states, semantic/instance found/content states, distances/raw channel dictionaries, operational proposal/qualified states, detector timing, optimizer timing/surrogate scores and optimizer events are retained. Recorded image receipts are exported without verifying image bytes. Source quality is distinguished from paired C1/C0 quality, which remains null unless explicitly recorded; it is never synthesized by subtracting two source-quality values. Missing measurements remain null, including the three-metric quality conjunction.

`dual-source-routes.csv` is the unique optimization/enrollment inventory. `dual-coverage.csv` separately inventories the full reserved cohort, declared pilot membership, completed routes and `reserved_not_declared` status. In a two-source pilot with a twelve-source reservation, the JSON reports declared=2, reserved=12 and reserved-not-declared=10; success on two never becomes success on twelve. C0_source appears in each declared route for matched comparisons and does not multiply unique source N. Repeated directories may contribute disjoint source/route pairs; any overlapping pair, duplicate actual source, duplicate route or unplanned route is explicitly rejected, with no automatic merge or favorable attempt selection. Recorded cases/routes/errors remain untouched. Native CLIP extraction happens before the v5 detector's internal `timing_ms`; its timing must not be described as complete CLIP-plus-extractor runtime when the source provides only that internal timer.

D derives its declared inventory from manifest cases/config arms, then C0/C1 × clean/VAE-cycle, with all owner hypotheses declared in config. The fixed two-source, two-arm, four-query pilot therefore produces sixteen condition rows and sixty-four query rows, not sixty-four independent sources. `phasemark-conditions.csv` contains unique quality/latency/soft-score/zero-magnitude/embedding/source/image receipts per condition; `phasemark-raw.csv` expands it per owner query. Source, same-arm-clean and paired C1/C0 quality retain separate references. `phasemark-summary.csv` contains raw matches, bit accuracy, positive/query counts and extraction-time distributions per arm/control/dose/query; repeated query rows do not create new quality samples or source N. Recorded descriptive thresholds/pilot states are preserved without selecting a better threshold. Zero-amplitude coefficient counts and spectral/direct-latent embedding diagnostics remain explicit raw fields.

`phasemark-arm-screen.csv` reports planned/observed condition/query counts and descriptive carrier/source-quality gates. The carrier gate requires every planned condition and owner query to be observed: C1 correct-owner present and all other queries absent, including all C0 queries. If the arm is incomplete its gates are null. Source-quality gate is also null if any needed clean C1 quality component is missing. Original recorded arm screens are retained separately; derived screens do not impute them. Human visual verdicts remain missing. Public payload pilot presence/absence is not a three-state content detector, a causal regeneration decision, or cryptographic ownership evidence.

Eight added CPU fixtures verify 2-versus-12 accounting, partial/missing cells, disjoint-run merge and duplicate rejection, the 16×4 inventory, incomplete gates/missing queries, missing quality and manifest-hash mismatch without changing source bytes. Together with eleven existing reconstruction fixtures, nineteen tests passed. No scientific acceptance, threshold fit, official gate or run-output mutation is performed.
# B-LW1 paired native/lightweight appendix

The read-only analyzer accepts `--gs-lightweight-dir` for frozen
`m1-gs-terminal-sign-v1` assessor output. This is separate from `--gs-dir`;
native scores are the unchanged joined source row, not recomputed detector
outputs. Analysis never opens images or models. `conditions.json` supplies the
fixed 112-condition inventory; missing cells remain missing. Duplicate,
unplanned or inconsistent identities/decisions, and native-row/image hash join
mismatches are rejected. Native scores remain observable when the LW attempt
failed. The loader hashes the copied source run/artifact/journal/receipt
snapshots and assessor output receipts; missing or mismatching provenance marks
analysis incomplete and makes carrier gates null. It does not hash/read image
files. Retained source errors and both receipt inventories remain in analysis.

Outputs are `gs_lightweight-raw.csv` (224 planned decoder rows),
`gs_lightweight-summary.csv` (14 channels by two decoders),
`gs_lightweight-paired.csv` (112 planned image pairs), and
`gs_lightweight-gates.csv` (clean/VAE by decoder). Raw rows retain correct/wrong
matches, accuracy, exact-message and presence decisions, image/source-row
hashes, payload/key/nonce identifiers, preprocessing, VAE asset receipt,
diagnostic timing and NFE. Native wrong exact-message is arithmetically derived
from its integer agreement count. Paired rows report native minus LW agreement
and the four presence cells only when both decoders are observed; incomplete
pairs remain null. Channel summaries preserve four planned prompt clusters per
arm, observed/missing counts, every observed C1 accuracy, exact/presence counts,
correct/wrong C0 counts and C1 wrong-key counts. Carrier gates require completed
source analysis, all four C1 and four C0 observations, C1 presence 4/4, C0
positives 0/4 and wrong-key C1 positives 0/4. Gates are descriptive, not human or
method verdicts. Repeated attack seeds/channels never increase independent N
beyond four prompts. No population FPR or three-state/content-binding claim is
created.

CPU fixtures cover complete/missing/failed-LW inventories, native-only pairs,
agreement deltas, duplicate/unplanned/hash/score rejection, pending parent
outcomes, provenance errors and snapshot corruption. Existing reconstruction,
native GS, progressive, A and PhaseMark analysis behavior remains unchanged.


## Phase residual diagnostic adapter (2026-10-04)

`--phase-residual-dir` accepts the separate `m1-phasemark-residual-v1` schema.
It never changes the original PhaseMark adapter or its16/64 denominator. The
new frozen design is two source clusters ×APM/IPS ×full/quality-cap ×C0/C1
×clean/VAE =32 conditions and128 four-owner queries. Reused C0 and repeated
owner hypotheses are correlated; the sample size remains two sources.

Outputs are `phase_residual-raw.csv`, `phase_residual-summary.csv`,
`phase_residual-conditions.csv`, `phase_residual-arm-screen.csv` and the
corresponding `analysis.json` object. Each arm/profile screen separates clean
source-quality, clean carrier and VAE carrier gates, and reports C1 correct
presence, C1 wrong-owner positives and all C0 query positives. Missing/failed
rows stay in the fixed inventory; gates are null for incomplete parent runs
or invalid provenance. Quality failure and carrier failure remain distinct.
Human verdicts remain null, and no three-state or content-binding label is
introduced.

Rows preserve lambda, the35.2dB cap declaration, recorded cap MSE/SSE,
composition hash/precision/bisection fields, source and suspect image receipts,
source/same-arm quality, phase scores, zero-amplitude counts, errors/tracebacks
and extraction time. Lambda is not selected by detector performance. Metadata
is pinned by the existing manifest SHA mechanism; the adapter additionally
checks the copied `input-run.json` against the declared source SHA and receipt,
compares `conditions.json` with the run's condition objects, and checks retained
manifest/conditions/journal hashes for completed runs. It does not open PNGs
or tensors: artifact receipts are retained, not independently pixel-verified.
The source runner performs those scientific artifact checks.

Duplicate/unplanned conditions, identity mismatches, unexpected owners and
match/accuracy/presence inconsistencies fail closed. Present is frozen at
82/128. Seven new synthetic CPU tests cover complete inventories, independent
quality/carrier screens, missing and failed conditions, pending parents,
controls at the exact threshold, malformed identities/decisions and changed
snapshot provenance without opening scientific assets. All33 analyzer fixture
tests pass (residual7 + prior26). No actual D-residual run was analyzed while
queued/running; parent may execute after committing code and finalizing inputs.

## IPS expansion and combined12-source adapter (2026-10-04)

`--phase-residual-expansion-dir` accepts the separate frozen
`m1-phasemark-residual-expansion-v1` schema:10sources, IPS/quality-cap,
40conditions and160owner queries. Raw source receipts must match the manifest
cases for completed cells. Retained latent/embedding receipts are included.
Manifest/conditions/journal output hashes and conditions-vs-run identity are
checked without opening images/tensors. This fresh-source schema does not
require historical `input-run.json`; the original two-source adapter still
does. Older family schemas and outputs stay unchanged.

Pass both `--phase-residual-dir <completed0030>` and
`--phase-residual-expansion-dir <completed-new-run>` to create an additional
`phase_residual_combined` analysis object and raw/conditions/summary/coverage/
gates CSVs. The combined operating profile is explicitly IPS/quality-cap only;
APM/full mechanism controls remain in the original run tables. It fixes
12source clusters,48logical conditions and192correlated queries. Combined
source IDs must be disjoint. Owners,82 threshold,35.2dB cap and36-step search
must agree; copied committed phase-code and model-inventory SHA receipts and
VAE scale.18215 must also agree. Any overlap, incompatible profile or missing
identity rejects combination instead of selecting an attempt. Every row keeps
its source run directory/SHA/outcome and original condition receipt.

The combined view reports independent clean-quality and clean/VAE carrier
gates, C1correct presence, C1wrong queries and C0 roster positives, plus
per-source completion coverage. Incomplete parents or missing conditions leave
gates null; failed/raw rows remain in the planned denominator. It does not
promote a successful gate into acceptance or population FPR. The source-bypass
operator and missing CLIP+pHash binding/human verdict remain explicit.

Four added CPU fixture tests cover40/160 and48/192 denominators/profile filter,
source overlap/profile/model incompatibility, missing expansion cells and raw
source mismatch, and changed expansion metadata receipts without historical
latents. All37 analyzer fixtures pass (11residual/expansion +26prior). No actual
expansion results or mutable run outcomes were read for this implementation.
