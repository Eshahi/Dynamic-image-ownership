# Server sizing and cost accounting (WP5 support)

Prospective, 2026-10-25. No server contacted and no experimental computation performed. Existing JSONL timings alone were aggregated with isolated stdlib Python. This is a proposed budget, not authorization or a prediction that all derivatives will fit. Parent protocol controls final counts and resource limits.

## Measured basis and limitations

Sources: retained `report/tables.md`, Table 7; MAIN `.thesis-build/dev-runs/20261025-0128-encoder-transfer-stage2b/run.json`; its `results/stage2b-full/rows.jsonl`; read-only runtime definitions in `scripts/encoder_transfer_runtime.py`. Reproducible accounting script: [cost-analysis.py](cost-analysis.py), numeric output: [cost-analysis.json](cost-analysis.json). There are **39,896 journal lines, 11,040 last-per-ID units**, 11,017 final `ok` and 23 `safety_blocked`. Summing every journal line would repeatedly count generation/detection as statuses accumulate. Final-state means below include attempted generations, including safety blocks; they are not successful-output-only throughput.

| Measured item on historical RTX 4090 | Mean seconds | Median seconds | Timer scope |
|---|---:|---:|---|
| Clean F5 mark |118.846|118.679|Input loading, embedding and save; excludes adapter initialization|
| Clean v5 mark |6.086|6.002|Same|
| Clean WAM / VINE-R / C0 |.114 / .176 / .087|.111 / .174 / .085|Same|
| R0 .1 / .2 / .4 |.216 / .411 / .375|.215 / .412 / .375|Complete native pipeline, input/save; excludes family load|
| R1 .1 / .2 / .4 |.804 / 1.300 / 1.306|.805 / 1.300 / 1.308|Same, native 1024 processing then 512 save|
| Kandinsky 3 .2 |1.287|1.288|Same|
| F5 C1 / C0 detector batch |1.921 / 1.165|1.623 / 1.010|One marked-input batch includes both owners; C0 has one owner|
| v5 C1 / C0 detector batch |1.414 / .741|1.153 / .604|Same|
| WAM C1 / C0 batch |.0251 / .0245|.0211 / .0207|One extraction; wrong-message comparison reuses extracted bits|
| VINE-R C1 / C0 batch |.0238 / .0235|.0201 / .0198|Same|
| Historical metric assessment |.312|.247|Saved RGB8 quality and original-source total quality; CPU LPIPS included|

These are elapsed unit timers, **not GPU-active time, kernel profiling, or invoice hours**. Model construction, downloads, text precomputation and most family switching sit outside them. Table 7 calls a detector batch a call; its F5 C1 batch already includes two owner evaluations, so multiplying that duration by two would overcharge. Conversely, summing nested owner `seconds` would omit shared semantic/latent feature preparation. Read `detection_seconds[method]` for planning.

R0 .4 is faster than .2 in this mixed-stage journal; cells run at different times/stages and kernels/precision/workload may differ. Do not fit a universal seconds-per-denoiser curve to these means. R1 .2 has 1,260 units because historical optional clean arms appear there; schedule forecasts below use only five inputs. The inherited stage-2a timings remain historical, not fresh stage-2b benchmarks.

Cache caveat: P5 smoothing averages eight perturbed encodes once per input and reuses its latent across three seeds. Its median .781 s disguises its mean 1.250 s. This illustrates why **whole scheduled sums/means and explicitly counted caches**, not the fastest or median seed, must set budgets. Core R0/R1 tables are native calls; existing historical pixels cannot provide the new paired explicit-noise latent law or derivatives.

Stage 2a full wall time was 4.80 h; stage 2b incremental full wall time 4.02 h with 3,840 inherited units and 7,200 new units. The stage-2b instance existed about 6.42 h to stop, estimated USD 2.88 at .448/h. The older conservative stage-2a clock was 25.9 h including a stopped interval, chosen by the user rather than reconstructed billing. **Do not scale 4.02 h as if it regenerated the union, and do not call 25.9 h GPU compute.** Provider invoice/stop records remain authoritative for charges.

## Unit schedule: Phase B, n=200

Four marked inputs (F5, v5, WAM, VINE-R) plus shared C0 per source. A source/condition with all five inputs costs, using historical mean batches, **6.898 s assessment**: one positive batch and one C0 batch for each detector, plus five historical metric timers. Wrong owner needs no extra generation. Running every detector on every foreign marked arm would be a larger, separately specified study; that is not included here.

| Component | Unique saved outputs | Additional calculation |
|---|---:|---|
| Clean |1,000|800 new marked images and 200 C0|
| Native seven cells × three seeds |21,000|R0 .1/.2/.4; R1 .1/.2/.4; K3 .2|
| F5 full-pipeline law |No new marked native output counted|**4,200 JVP evaluations**, one per source/cell/seed, around paired C0; primal C0/C1 already in native schedule|
| Selected A × three seeds |3,000 final + 3,000 first-pass controls|Two pipelines per final; keep first pass, never regenerate it solely as control|
| Selected B |1,000|One inversion and selected 20-step optimizer per input|
| B-fidelity |1,000|Same selected radius; no inversion|
| B-codec |1,000|Reuse B's encoded mode; one decode|
| Optional FLUX native cell × three seeds |3,000|+600 F5 law JVPs; quality-selected cell only|

Native and clean have **22 source-condition settings** (21 stochastic native replicates + one clean); the four attack/control schedules have nine (A three, first-pass three, B/fidelity/codec one each). Thus base+attacks assess 31,000 output units, through **49,600 detector batches** (eight batches per source-condition: four positive, four shared-C0 detector methods). Optional FLUX adds 3,000 outputs and 4,800 detector batches. These are computational counts. Seeds, arms, repeated attacks and shared C0 are correlated within source; none increases the confirmatory sample size beyond 200 independent source groups. Missing/blocked outputs remain attempted units, with no imputed negative detector result.

| Historical-component extrapolation for Phase B | Hours |
|---|---:|
| Clean generation/embedding |6.96|
| Seven native cells generation |4.75|
| Native + clean assessment |8.43|
| **Subtotal with historical analogues** |**20.14**|
| Attack/paired-first-pass assessment |3.45|
| Selected A generation at s=.2 proxy |1.43|
| **Subtotal including A, before all unknown work** |**25.02**|

A's 1.43 h is 3,000 × (historical R1 .2 mean + R0 .2 mean), not a measured chained-attack timing or bound for new hardware. Smaller .05/.15 settings have no exact timing here. Use this conservative-within-observed-.1/.2 analogy for initial sizing only; pilot supersedes it. No generation credit is taken for overlapping native first-pass cells. Exact duplicate requests may be cached only if immutable input bytes, precision, native sampler, seed/explicit noise, model revision and save convention all agree; log credits before inference. A first-pass control itself needs detection and quality even when generation is cached.

The unrounded Phase-B historical-native/clean subtotal is **20.1409042 h**, plus **3.4490307 h** attack/control assessment and **1.4256070 h** A generation proxy, giving **25.0155419 h**. A simple30% contingency gives **32.5202045 h** before unknown B/JVP, extra quality references, setup and transfer. These decimal digits make accounting reproducible; they do not describe forecasting precision. Final pilot forecast must use actual pilot maxima and apply30% to the unknown measured work too, rather than only the known subtotal.

Additional Phase-B model calls, excluding metric/detector assessment:

- A: 6,000 encoder and 6,000 decoder forwards; **6,000m denoiser forwards**, m=1..4, i.e. 6,000–24,000 total split equally between R1/R0. Different-family forwards do not have equal seconds.
- B: 1,000 encoder forwards, 20,000 SD1.5 denoiser inversion forwards, 21,000 decoder forwards and 20,000 decoder/LPIPS backward steps.
- B-fidelity: 21,000 decoder forwards and 20,000 decoder/LPIPS backward steps; no inversion.
- B-codec: 1,000 decoder forwards using cached B z0.
- Total B suite: **43,000 decoder forwards and 40,000 backward steps**, plus 20,000 denoiser forwards and 1,000 encodes. LPIPS reference features can be cached once per input; variable-image LPIPS forward/backward still occurs every optimizer step. No UNet backward in B.

No measured timing exists for any complete-pipeline JVP, decoder backward, differentiable LPIPS, FLUX pass or FLUX derivative. Let `j_f,s`, `b`, `d`, `l`, `u20`, `e` denote server-pilot seconds for each distinct family's JVP, backward bundle, decode, remaining bookkeeping, twenty-forward inversion and encode. Count complete actual operations; an empirical 20-step B bundle is preferable to blindly adding separately timed components. Phase-B unknown derivative time is `200*3*sum_sev(j_f,s)` seconds, plus measured B/fidelity/codec bundles ×1,000, family loads and additional quality-reference work. Do not add native primal forward time twice if a pilot JVP bundle includes its primal.

Sensitivity illustration, **not a benchmark**: 4,200 JVPs at assumed 10/30/60 s each would add 11.7/35/70 h. This single unknown dominates low dollar estimates; advertising a USD 15 complete final study would be unsupported.

## Phase A: 60 existing development sources

Core fit/calibration schedule: six R0/R1 native cells × three seeds × five inputs = **5,400 outputs**, plus 300 clean units if re-assessed; **1,080 F5 JVPs**. Fixed 30/30 source split contributes 540 JVPs each. Native generation analogue is **1.10 h**; six-cell assessment **2.07 h** (add .115 h if clean re-assessed). Existing four marks/C0 may be copied with hashes and no repeat embedding if their exact retained bytes are the intended study inputs. Otherwise recreating all clean inputs costs approximately **2.09 h** and changes input identity, which must be declared. **Native law trajectories must be recomputed on the server with the required paired randomness; old endpoints do not contain new latent/JVP observations.** No historical output is a fresh held-out datum.

The integrated [mechanism-server-spec.md](mechanism-server-spec.md), section6, now fixes the twelve-source mechanism module. Each actual residual has five directions: the actual direction, two independently norm-matched Gaussian controls and two Fourier-phase controls. This adds **720 mode-encoder JVPs** (`12*4 arms*3 families*5 directions`) and **540 differential full-chain JVPs** (`12*3 families*3 seeds*5 directions`, F5-only). These are in addition to the **1,080 main-law full-chain JVPs**. Do not subtract the72 superficially overlapping R0/R1 main-law tangents: the law starts from the exact finite input-encoder displacement, whereas these controls start from the differential encoder response. Their initial directions differ, even when the actual pixel residual and C0 primal coincide. Exact downstream C0 primal reuse may save work; it does not remove these scientific derivative evaluations.

| Additional stage-primal component | Incremental saved outputs |
|---|---:|
| Deterministic/mode codec, three families |180|
| Sampled codec, R0/R1, three seeds |360|
| Noise-only direct decode, three families/seeds |540|
| Mode full paths, R0/R1, three seeds |360|
| K3 native deterministic full path .2 |180|
| **Increment beyond main-grid R0/R1 reuse** |**1,620**|

The full native stage schedule contains540 outputs, of which360 R0/R1 native outputs already belong to the main Phase-A grid; only its180 K3 outputs are incremental. Preprocessing controls add **60 outputs per unique resize/normalization/inverse-conversion path**, with identical paths shared and logged once. Control directions remain derivatives, not generated marked images. Stage outputs require their prescribed quality/chip/descriptor/retention measurements; they are not1,620 equal-cost native generations. Mode versus sampled paths, direct noisy decode and exact finite input displacements have distinct costs.

**All720 encoder JVPs,540 differential full-chain JVPs,1,620 incremental stage outputs, distinct preprocessing controls and their extra measurements need separate future-server pilot timings. They are not fully covered by the historical native/attack subtotal or by the1,080 main-law count.** Report Phase-A full-chain derivative count as1,620 (1,080 main law +540 differential), with720 encoder-only derivatives separately. Neither historic native forwards nor the B optimizer's backwards establish their memory/time feasibility. The final maximum-path forecast must add this module before checking the40-hour proposed Phase-A ceiling. Insufficient resource support is declared missing mechanism evidence/H4 unresolved as applicable, never claimed completed.

Attack-development counts from 05-informed-attacks.md, explicitly adding C0 only after setting freeze:

| Task | Marked grid units | Selected C0 additions | Model-call accounting |
|---|---:|---:|---|
| A four settings ×3 seeds |2,880 final +2,880 first passes|180 final +180 first passes|Grid 14,400 denoiser +5,760 E +5,760 D; selected C0 adds 360m denoiser +360 E +360 D|
| B nine-setting grid |2,160 final|60 selected final|Cache 240 marked inversions:4,800 denoiser+240 E; grid45,360 D+43,200 backwards; C0 adds1,200 denoiser+60 E+1,260 D+1,200 backwards|
| B-fidelity |240|60|6,300 D+6,000 backwards combined|
| B-codec |240|60|300 D, cached encoded modes|

A's selected marked outputs are already in its full grid; do not add them again. Keep all quality-grid candidates even though only frozen selected settings receive target-detector release. C0 generation is not multiplied by four marked arms. Total B suite in Phase A is **53,220 D +50,400 backwards +6,000 inversion-denoiser +300 E**. This excludes metric quality/detection and is not an equal-work sum. A grid+C0 generation proxy at the maximum measured .2 per-pass cost is **1.45 h**, with the same caveats as Phase B. At least every grid output and final control needs declared quality assessment; the retained .312 s/output is only a starting analogy because attack quality includes published-u references and may require extra comparisons. Target detection only after freeze: nine selected attack/control source-settings cost about **1.03 h** assessment across 60 sources, before cache credits, with full-grid quality work separately charged.

Optional FLUX quality-only grid: three distinct suffixes ×60×4×3 = **2,160 marked outputs**, totaling 4,320 transformer updates if suffix lengths are exactly1/2/3. No C0 full tuning grid. Optional selected Phase-A C0 adds180 native outputs; its marked selected-setting outputs already exist in that grid. The fixed codec-only five-input control additionally contributes **300 Phase-A reconstructions and1,000 Phase-B reconstructions**, each deterministic with no three-seed duplication. Both codec controls are descriptive extras outside H4: **no codec-only JVP is scheduled by the integrated protocol**. Phase-B codec assessment has200 source-condition settings (approximately .383 h at historical assessment rates), plus unmeasured codec generation. Thus optional Phase-B FLUX adds **4,000 outputs and6,400 detector batches** in total:3,000/4,800 native plus1,000/1,600 codec. They are **outside the31,000-output/49,600-batch core**; the expanded Phase-B ledger is35,000 outputs,56,000 detector batches and4,800 native full-chain law JVPs (4,200 core +600 FLUX). FLUX seconds remain unknown. A48 GB device may change all throughput estimates, so preserve device-specific pilots.

## Proposed approval envelope and server-only cutoff

Planning recommendation: present a **100 instance-hour maximum for the complete non-FLUX design**, split Phase A ≤40 h and Phase B ≤60 h, with each phase requiring its own later authorization. At the requested **illustrative .45–.60 USD/h range**, that is USD45–60 total, not a market quote. Allocate from each phase **at most 2 h detector-sealed pilot**, **2 h collection/stop reserve**, and the remainder to setup, downloads, frozen computation and margin. No inference that the unknown workloads fit follows from this envelope. The native+clean Phase-B historical subtotal alone is20.14 h; after A it is25.02 h, leaving about35 h for unknowns, loading, pilot and transfer within the proposed60 h phase cap. Phase-A historical native/A/selected-assessment subtotal is about5.8 h plus full-grid quality, clean assessment/recreation as needed and all mechanism/B work.

Optional FLUX: propose a separately approved **additional ≤40 instance-hours**, USD18–24 only **if the actual chosen device rate really is .45–.60/h**. A 48 GB GPU could cost more; recalculate dollars at its actual quoted rate before rental. This is an optional maximum allocation, not expected time. Do not silently charge a 48 GB run at a 4090 rate or reuse the older study's remaining budget as approval.

Server pilot is mandatory and uses fixed development inputs, no target-detector inspection: exercise each unique generation/derivative/backward path, serialization, failed-output handling and peak host/VRAM allocation. Warm-up, load and download timings must remain in elapsed billing accounting. Forecast the **entire frozen schedule** with maximum measured source/path duration, **30% margin**, explicit loading and transfer reserve, spent time and approved price. If projected ceiling exceeds either approved dollars or hours, stop before full Phase A. Optional B or FLUX may be removed only by the predeclared feasibility hierarchy before full Phase A outcomes and detection release; record resource non-execution. Do not reduce samples, seeds, optimizer steps or difficult sources after outcomes. Failure of required law/JVP feasibility prevents a completed law test; it is not fixed by quietly omitting derivatives.

The pilot must identify unsupported MoVQ derivatives, precision/autodiff problems, decoder backward OOM and larger-than-planned offload latency. No laptop rehearsal is permitted. The machine itself has no authorization from this document. Phase B stays off pending the later human decision after Phase A and protocol freeze.

## Machine, storage, transfer and downloads

Core: RTX4090-class GPU, **≥64 GB host RAM, ≥150 GB disk**. Historical K3 peak allocated CUDA memory was20.38 GiB; history supports native forward operation, not new derivative feasibility. FLUX: **48 GB VRAM preferred**, same minimum RAM/disk, batch one, frozen unquantized model, inactive-module offload and cached text embeddings; actual fit is a pilot question.

Known selected historical core assets total **20.206 GB** (SDXL6.941 GB and VINE native stack9.534 GB included), plus selected K3 approximately **28.38–28.391 GB**. Thus known combined core model assets are approximately **48.6 GB**, before packages, duplicates, output images or transfer staging. FLUX adds **33.714 GB** selected weights, bringing models to approximately **82.3 GB**. These are rounded size accounting, not exact-byte download manifests. Request a revised explicit total-download ceiling; the legacy30 GB allowance cannot cover even this combined core. Parent asset plan must count pinned WAM/internal reader/LPIPS/CLIP components already included in the historical core, avoid double counting, and add any genuinely new derivative-only dependency. No full-repository model snapshot and no duplicate FP32/FP16/original-format checkpoints.

FLUX primary component listings at frozen revision: [transformer23.78 GB](https://huggingface.co/black-forest-labs/FLUX.1-schnell/tree/741f7c3ce8b383c54771c7003378a50191e9efe9/transformer), [T5 9.52 GB](https://huggingface.co/black-forest-labs/FLUX.1-schnell/tree/741f7c3ce8b383c54771c7003378a50191e9efe9/text_encoder_2), [CLIP .246 GB](https://huggingface.co/black-forest-labs/FLUX.1-schnell/tree/741f7c3ce8b383c54771c7003378a50191e9efe9/text_encoder), [VAE .168 GB](https://huggingface.co/black-forest-labs/FLUX.1-schnell/tree/741f7c3ce8b383c54771c7003378a50191e9efe9/vae), inspected by the WP4 audit and recorded in [flux-feasibility.md](flux-feasibility.md). K3/other selected-representation accounting is in [third-family-alternatives.md](third-family-alternatives.md) and the retained study `budget-and-proposals.md`. No new market search or download occurred for this cost audit.

150 GB is a minimum, not proof of adequate output capacity. Output-image compression size is unknown for new sources. Before rental, project retained 512px RGB8 outputs, mechanism traces/arrays, packages, extraction copies and archives; use an approved larger disk or bounded streaming if the manifest exceeds available space. Do not store every intermediate gradient graph. Detach serialized summaries and release graphs per step.

Do not route model downloads through the laptop. Historical collection was approximately .85 MB/s and uploads .10 MB/s; at the former, **10 decimal GB requires about3.27 h**, already larger than a2 h collection reserve. Measure server-to-home retrieval in the pilot and enlarge reserve or downscope *stored nonessential diagnostic artifacts before full data*, retaining required outputs and failures. Streaming collection during compute may reduce final idle time but cannot erase billable overlap. Track bytes, download/retry time, instance start/stop, GPU-active intervals where available, model loading, compute wall time, idle time, retrieval and provider charges separately. Stop the instance after verified retrieval; never destroy it on the user's behalf.
