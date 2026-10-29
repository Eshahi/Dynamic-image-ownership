# Round 3 independent preparation review

**Verdict: ACCEPTED FOR PREPARATION after closure of R3-IR-1. No open preparation blocker was found in the reviewed scope.**

2026-10-29. Reviewer: fresh independent Codex agent `r3_independent_review`, separate from the authors. This is acceptance of a bounded design/code package for handoff. It is not scientific validation, authorization to execute or spend, approval of proposed gates or budget, human visual acceptance, thesis confirmation, or publication approval.

## Scope and evidence

Reviewed `01bf24f..551afc59fe860d34315a32902e30f0435229592a` on `codex/tifs-20261028`, followed by the author's working-tree correction of R3-IR-1 and its four regression tests. Also reviewed the eight metadata-only tests in `scripts/tifs_test_stage_s_forecast_integration.py` and the prospective result-interpretation note. Retained code was inspected only where needed to assess these changes. This was not a repository-wide audit or another literature survey; ForenMark was outside scope.

The authoritative MAIN `STATE.md`, `BRIEF-R3.md`, section 1 of `BRIEF.md`, and `09-round3-amendment.md` governed the review. The requested writer/denoiser, Stage P selection and runtime, profiles, Stage S setup/runtime/read/forecast/analysis, drivers, tests, design documents, frozen configurations, manifests and cost arithmetic were examined. The evidence-audit skill's distinction between traceable preparation and unsupported scientific claims was applied; the requested single review file replaces its generic multi-file output format.

No model, image, metric, encoder, gradient or scientific timing computation ran. Verification used the MAIN standard-library interpreter with `-B -I`, pure logic/mocks and metadata. Synthetic JSON and opaque byte fixtures are test inputs, not scientific results or real approval receipts. No retained results or protected files were changed by this reviewer.

## Blocking finding and closure

### R3-IR-1 — CLOSED: required-control resource stops could become incomplete or scientific-stop outcomes

**Original location:** `scripts/tifs_stage_p.py`, `comparison` at line 345 and `eligibility` at line 369 of the reviewed commit, propagating through `select_rung` and `check_winner`.

**Trigger and observed result:** A retained-F5 control with `RESOURCE_STOP` and complete rung-4 candidates produced `INCOMPLETE`. With scientifically rejected candidates, the same required-control resource stop produced `SCIENTIFIC_STOP`. A resource-stopped budget control at proposed-profile rung 16 likewise became `INCOMPLETE`. These were independently reproduced with metadata-only summaries.

**Impact:** The selector lost the cause of missing allocated evidence and could describe resource exhaustion as scientific exhaustion. This violated the frozen Stage P policy; a candidate rejection does not discharge its required comparator allocation.

**Required correction:** Preserve resource status in comparisons; inspect every required candidate/control before allowing rejection to determine the aggregate outcome; use `RESOURCE_STOP` before `INCOMPLETE` before scientific rejection, while retaining observed rejection reasons and control diagnostics. Budget controls must remain optional at the early rungs and required at the final rung/check.

**Closure inspected:** The author added the resource branch at current line 347 and required-evidence aggregation at current lines 380 onward. The four tests beginning at lines 96, 113, 127 and 140 of `scripts/tifs_test_stage_p.py` cover retained and budget resource stops, already rejected candidates, both final-rung profiles, the veto check, and missing versus optional controls. All 42 affected Stage P/profile/runtime tests passed independently; all three original reproductions now return `RESOURCE_STOP`. The diagnostic reasons remain available. This finding is closed, provided these reviewed changes are included in the handoff commit.

Closure file SHA-256 values:

| File | SHA-256 |
|---|---|
| `scripts/tifs_stage_p.py` | `d1cda215171bc3a49e733b3804f508e468e8b6087f280bb2b47698a556674214` |
| `scripts/tifs_test_stage_p.py` | `7dbdb20148edbbbb832be089cf4588a85c77fe6bb2534c3c0a5017d274df862c` |
| `scripts/tifs_test_stage_s_forecast_integration.py` | `f1850554ca0b8e5a68428089cf3b8451b165a45c02051573ace5d4c7ca42c347` |

Stage S retains its existing decisive-scientific-failure precedence. The closure does not silently change that separate final conjunction into Stage P's required-allocation rule. The protocol and interpretation note now explain the distinction.

## Preparation checks

| Area | Finding and classification |
|---|---|
| Native x0 surrogate | **Verified as a coherent implementation design; numerical behavior unverified.** The epsilon-prediction x0 formula retains the denoiser derivative, uses native DDIM windows, and domain-separates timestep sampling by source/family/strength/update. Current empty prompts and guidance 1 take the native single-branch path. SDXL pooled embeddings and time IDs use native helpers. The writer rejects unsupported native-conditioning changes. |
| Precision, checkpointing and parity | **Verified at code/API level only.** UNet fp16 casts, disabled autocast, fp32 x0/VAE arithmetic, classic attention, frozen parameters, checkpoint flags and graph/offload lifetime are explicit. Separate nonzero epsilon-input probes prevent an identity-only x0 gradient from masquerading as denoiser differentiation. First-step native parity rebuilds conditioning on a captured native noisy latent; exact C0 tape replay is separate. Neither check establishes whole-pipeline gradient accuracy. |
| F5 control | **Verified construction and disclosed limits.** `f5-budget` delegates to retained `robust_pgd` with the declared 150+50 schedule, margin/mask and target budget. Callable/argument tests do not claim numerical equality. It has 200 reader-gradient evaluations versus F6's 350 plus surrogate work; this is not compute matching. |
| Stage P sources | **Verified metadata isolation.** The 24 identities are exactly the original 60-source pool minus all 36 Stage S donor/target/rehearsal identities. Ordering matches the frozen domain-prefixed SHA-256 rule. Tune/check are 16/8; manifest/sidecar and four exclusion-source hashes match. Source IDs, UIDs and available raw/PNG/RGB8 hashes have no P/S overlap; available Phase B/C identifiers and hashes have no P overlap. No held-out image was opened. |
| Frozen search and veto | **Verified bounded allocation.** Eight configurations, entrants 8/4/2 on cumulative 4/8/16 prefixes, fixed ranking and one immutable nomination lead to a single eight-source veto. Prior decisions bind expected prefix evidence. Runtime allocation rejects source enlargement/eliminated candidates. A failed check cannot select a runner-up, enlarge the search or fall back to the default writer. The existing mocked lifecycle test covers planner through Stage S consumption; separate journal tests cover evidence summaries. |
| Missingness and resources | **Verified after R3-IR-1.** Required rows, pairing identities, seed coverage, quality, negative calls and controls remain mandatory. Invalid/missing data cannot promote a candidate. Resource diagnostics survive candidate rejection. Forecasts bind selection/profile/identity and reject bad status/type/timing or inconsistent device/capacity evidence; diagnostic memory contributes to peak checks. |
| Gate profiles and article rule | **Verified.** `round1` remains default and effective unless an external pre-output decision selects `round3-proposed`. Both profiles are reported; an inactive favorable report cannot choose the effective verdict. No actual user receipt was created. Article VINE-B numerical rules are unchanged from the base, and `tifs_article_decision.py` is unchanged. Its dependence on a complete thesis GO follows the preselected profile. |
| K3 scope | **Verified disclosure.** Executable K3-out excludes K3 from writer gradients but uses K3 in Stage P selection. K3-in is a precise deferred design, explicitly not implemented and not a ninth rescue configuration. Prospective SD3.5 confirmation remains separate and approval-dependent. |
| Cost and probability artifacts | **Verified analytical arithmetic, not empirical evidence.** Both calculators' self-tests pass, and regenerated in-memory reports exactly equal their committed JSON artifacts. Probability grids are finite-sum sensitivity models, with endpoint/seed/dependence qualifications; they do not measure the method's success probability. |

For the API-dependent checkpoint/conditioning claims, the reviewer independently inspected the official pinned [Diffusers 0.35.1 SDXL img2img implementation](https://raw.githubusercontent.com/huggingface/diffusers/v0.35.1/src/diffusers/pipelines/stable_diffusion_xl/pipeline_stable_diffusion_xl_img2img.py) and [UNet blocks](https://raw.githubusercontent.com/huggingface/diffusers/v0.35.1/src/diffusers/models/unets/unet_2d_blocks.py). The time-ID helper matches the intended native call. Checkpoint branches depend on gradient enablement plus checkpoint flags, so frozen/eval UNets do not alone disable this path. These source inspections support API feasibility, not measured runtime or memory fit.

### Exact accounting reproduced

- Stage P: 72 candidate marks + 24 retained-F5 marks + at most 40 budget-control marks = **136 marks**, with 136 duplicated C0 directory units, **3,264 native attempts** and **3,536 producer identities**.
- Candidate work respects the joint bound: at most **56 x0 and 16 noise** writes, or the reverse, totaling 72; incompatible maxima are not added.
- Complete P plus eleven-arm S and S rehearsal: **316 marks, 9,080 producer identities, 13,616 detector rows and 70,400 logical reader-gradient evaluations**. Maximum writer x0 differentiated graphs are **11,100**, before separately charged diagnostic probes.
- Assumed fast/middle/stress totals are **61.99512083333333 / 125.81750833333334 / 264.9848833333333 hours**, whose whole-hour ceilings are **62 / 126 / 265**.

The 126-hour figure is the rounded middle planning scenario, not a measured minimum or authorization. The effective cap remains 15 hours. Runtime qualification is deliberately more conservative than this scenario, including full P reservation after calibration and slower-writer/load proxies. P calibration and the later full S rehearsal must each qualify their remaining work on the same paid clock, with collection reserve. Neither forecast may shrink the frozen scientific inventory to fit.

## Nonblocking warnings and remaining validation

**W1 — Server numerical qualification is unavailable, by design.** Real fp16 backward support, nonzero finite gradients, native conditioning/parity, clean saved-image behavior, achieved quality, latency, host/device peak memory and exact replay are not established by mocks or source reading. Run the prescribed diagnostics and measured forecasts only after execution authorization. Any failed diagnostic remains a qualification failure; it must not be presented as observed method efficacy or silently repaired by changing this frozen run. This is a scientific/server validation boundary, not an outstanding preparation defect.

**W2 — Partition isolation is narrower than freshness or unseen-family generalization.** All 60 originals have previous development exposure. Available metadata excludes known P/S and B/C identity overlap, not every perceptual duplicate; some B-reserve/C entries lack comparable byte/pixel hashes, and Commons SHA-1 cannot be compared directly with COCO SHA-256. The check set is untouched by the current nomination, not fresh confirmation. K3 is selection-seen. Preserve these qualifications in later claims.

**W3 — Arm contrasts do not isolate denoiser causality or equal compute.** x0 versus noise also changes timestep sampling. Equal target budget does not ensure equal achieved quality, and passing a paired median margin does not match each source. F6 uses more reader evaluations than budget F5. The package and interpretation note disclose these limits; later reports must retain them.

**W4 — Forecasts and probabilities remain conditional.** Device timing/fit is unmeasured, assumed hourly prices are not live quotes, and the engineering allowance is not a completion bound. The subjective thesis/article percentages are explicitly personal judgments, not calibrated probabilities or journal acceptance estimates. A resource stop is not evidence for the scientific null.

## Independent verification record and acceptance boundary

Before the correction, reviewer discovery of `scripts/tifs_test_*.py` passed **181 tests** in the permitted isolated interpreter, including the eight new full-forecast metadata tests. The loaded-module check found none of `torch`, `diffusers`, `numpy`, `scipy`, `PIL`, `lpips` or `open_clip`. After correction, **42 affected tests**, including four added regressions, and the three direct failure reproductions passed. This is not a claim that the entire resulting 185-test suite was independently rerun. The exact cost/probability regeneration and source-manifest checks were also performed independently.

The report accepts preparation after the documented fix is included. No measured F6 result, TIFS novelty/acceptance result, held-out approval, human assessment or paid-run decision follows. The handoff must continue to state that F6 is untested, the proposed profile and 126-hour scenario are inactive until an authorized decision, K3-in is unimplemented, and future scientific conclusions depend on complete authorized server evidence.
