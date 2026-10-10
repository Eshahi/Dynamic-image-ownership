# Journal discovery results and revised development decision

**Completed improvement round, 2026-10-10:** [summary and revised direction](improvement-summary.md). All six declared configurations failed advancement despite clean/VAE gains; the historical discovery below remains unchanged.

**Snapshot scope:** this report records the initial two discovery probes and their independent review. Later WAM reproduction and readable-payload development are tracked in [the current plan](plan.md), [WAM results](wam-results.md), [readability results](readability-results.md), and the [separate decoder decision](read-conditioning-decision.md). Statements below about work not yet run refer to this initial snapshot.

2026-10-10, Codex agent. Two prospective development probes completed locally for USD 0. This is an exploratory supplement to the already completed M2 scientific package. It does not revise frozen F5 r2, historical M1/M2 gates, or the pending human M2 verdict. No held-out image was read and no protected claim/source/proposal file was edited.

## Decision

**Retain F5 r2 as the frozen comparator, but prioritize readable-code robustness before a broad independent-diffusion grid.** It misses the predeclared SDXL-VAE screen: 10/12 checked semantic successes against the required 11/12, while v5 has 12/12. Both failures retain weak semantic presence but lose readable decoding. The new binding positive control works on five exact two-tier deliveries; all five are rejected. Public construction of a fresh self-consistent mark still succeeds without owner authorization, so the paper must distinguish content consistency from cryptographic ownership.

The evidence now supports a more precise paper question: can an encoder-guided pixel mark retain a **readable, content-checked payload** across autoencoders and diffusion regenerators at matched quality/FPR, and which content predicates reject physically delivered donor payloads? General robustness, superiority to external methods and authenticated ownership remain unestablished. Journal quartile is not an experimental pass threshold.

## Runs and claim inventory

| ID | Bounded claim | Direct evidence |
|---|---|---|
| D1 | All planned development observations completed: 144 VAE image rows and 31 binding image rows; no failed, missing or extra identities | `discovery-statistics.json` inventory; both original run.json files |
| D2 | F5 checked semantic 12/12 after SD1.5 VAE and 10/12 after SDXL VAE; v5 12/12 for both | VAE rows, primary combined alpha calls; paired source table |
| D3 | The two F5 SDXL failures are decoding-read failures, not binding rejections; all reconstructions meet both numerical attack proxies | VAE rows 4795/6012, read flags, scores and LPIPS |
| D4 | Exact public donor q/h delivery in 5/6 attempts; combined rejection in all five exact deliveries, with positive content-disabled read controls | Binding `public_donor_synthesis` rows and strict-both subset |
| D5 | One preselected public recipient-payload synthesis is fully accepted without an authorization mechanism | Binding `public_recipient_authorization_demo`, pair 1675/4795 |
| D6 | These probes do not establish low population FPR, independent-diffusion survival, component synergy, general ownership security or external superiority | Small repeated development sample; absent experiments; public profile |

Original artifacts are retained in MAIN:

- `.thesis-build/dev-runs/20261010-0858-journal-binding/`: commit `1e25f5f`, 31/31 rows, 315.968 seconds.
- `.thesis-build/dev-runs/20261010-0903-journal-vae/`: commit `02cfd22`, 144/144 rows, 160.719 seconds.

Both include run.json, rows.jsonl, summary.json and delivered RGB8 images. Commands and configurations are in run.json. The [descriptive analysis](discovery-statistics.json) is produced by `scripts/journal_probe_analysis.py` at `d6eafdb`; it preserves source/pair units, failed/missing identities and per-metric n/mean/median/SD/range. It is not a significance test. [VAE protocol](vae-probe-protocol.md), [binding protocol](binding-probe-protocol.md), and [prospective design decision](probe-design-decision.md) precede their runs.

## Independent VAE reconstruction

| Saved method | Clean checked / full | SD1.5 VAE checked | SDXL VAE checked | SDXL presence | Full match after either VAE |
|---|---:|---:|---:|---:|---:|
| F5 r2 | 12/12 / 12/12 | 12/12 | **10/12** | 12/12 | 0/12 |
| v5 | 12/12 / 12/12 | 12/12 | **12/12** | 12/12 | 0/12 |

Checked means semantic found AND read AND content_match. Presence-only or recomputation-assumed matches are not checked recovery. The paired SDXL result has ten shared successes, two v5-only successes and zero F5-only successes; it is descriptive evidence, not a population superiority test. This is native whole-system comparison: carrier, feature views and matcher differ. It does not isolate carrier location.

Every clean mark meets PSNR >35 dB, SSIM >.9 and LPIPS <.1 on these twelve sources. F5 mean/max clean LPIPS is .01732/.05016; v5 .01762/.03833. This does not repair the two historical M2 quality failures or establish all-image quality.

F5 attack-input LPIPS mean/max: SD1.5 VAE .08915/.14346; SDXL VAE .06830/.12159. v5 corresponding values are .07541/.12805 and .06872/.11846. All twelve C1 outputs per condition meet both <=.20 and <=.30 numerical proxies. Human admissibility remains missing. Lower mean SDXL distortion does not guarantee equivalent perceptual/semantic severity or establish monotonicity for a later diffusion attack.

The two F5 read failures are source 4795 (decoded score 7.86278, LPIPS .09375) and 6012 (6.74483, LPIPS .05538). Both fall below the frozen decoded threshold 8.25933, while recomputed scores 6.98957 and 5.78616 exceed 4.98203. The returned content match is therefore assumed from recomputation, not verification of a readable payload. No read-and-rejected case occurs. This identifies the decision stage; it does not distinguish carrier attenuation, host interference, or changed feature geometry. The intact SD1.5 control and correct clean detections make a generic preprocessing explanation less supported, but do not rule out an SDXL-specific implementation issue. Nonidentical weights establish checkpoint difference, not physical causality. No threshold is relaxed to hide the gap.

Each method has zero detections in 72 negative calls: C0-alpha and C1-beta for each of three conditions, 12 calls per cell. They reuse twelve sources and are not 72 independent negatives. No new FPR calibration or low-error guarantee follows.

The SDXL VAE is pinned at [6f5909a7](https://huggingface.co/stabilityai/sdxl-vae/tree/6f5909a7e596173e25d4e97b07fd19cdf9611c76), MIT declared in its model card. It is a separately trained checkpoint of the same architecture, not an unrelated architecture or training-data claim. All 3,456 entries of the inspected first encoder convolution differ from the SD1.5 checkpoint. Both reconstructions use posterior mode, fp32, direct unscaled latent decode and 512 RGB8 output; the detector always keeps the frozen SD1.5 encoder. This is VAE-only reconstruction, **not SDXL diffusion at strength .2/.4**. Those full-backbone results remain absent.

## Delivered-payload binding

| Arm | Attempts | Exact donor q/h recovery | Combined full acceptance |
|---|---:|---:|---:|
| Legitimate donor positive | 6 | 6 | 6 |
| Recipient sham | 6 | 0 | 0 |
| Residual transfer .5 | 6 | 0 | 0 |
| Residual transfer 1.0 | 6 | 0 | 0 |
| Public fixed donor-payload synthesis | 6 | **5** | **0** |

Residual failures still cannot isolate binding: neither scale delivers the exact two-tier donor payload. Public synthesis writes fixed codes decoded from D1; it does not substitute recipient h. Five of six attempts recover both exact donor codes, and all five have positive two-tier read-presence with content predicates disabled and negative combined acceptance. On the identical extracted signals, both semantic and instance-own content checks reject those five. This supplies a small physical-delivery mechanism result that historical M2 lacked. It does not show that combining the predicates improves over either alone; native modes share q-conditioned instance extraction and semantic-status propagation.

The sixth synthesis, pair 468505/499768, differs by one decoded q bit (h exact). It is retained as an attempted but non-exact delivery, not silently added to the strict subset. All six have native `none` full presence and combined content_mismatch. This unchecked `none` output is not authentication.

Public donor synthesis PSNR is 43.12–45.37 dB; LPIPS .00827–.04891 against recipient C0. All six satisfy the numerical proxies and strict quality limits, but have no human visual verdict. Six attempts/five exact deliveries do not establish a low false-acceptance probability: with zero acceptances in five independent fixed-distribution trials, the illustrative one-sided 95% upper bound would still be 45.07% (`1 - .05**(1/5)`). The selected development pairs are not a random population sample, so even that bound is only a planning illustration.

The separate preselected recipient-payload synthesis under public alpha is accepted as `both_match` (1/1), with exact q/h, PSNR 44.98 dB, SSIM .98939 and LPIPS .00832. No secret or authorization is consulted. This is a white-box construction counterexample to an unrestricted unforgeability claim, not a default copy-paste success or an empirical population attack-rate estimate. It is also not a legitimate same-owner-image false positive: the experimental scenario assigns distinct recipient ownership while the algorithm permits public construction. Legal ownership is outside this experiment.

## Revised sequence and thresholds

1. **Fix the hypothesis before increasing compute.** Keep F5 r2 frozen. Prepare a bounded readable-code robustness amendment with hard quality constraints, comparing the identical marked-image payload before/after both VAEs. Diagnose decoded-score loss separately from semantic-feature drift; do not lower thresholds based on these twelve images. Consider robust embedding objectives only after an explicit method decision and cheapest fixed-source test. Limit a development round to six configurations, retain every failure, and replicate survivors on a separately reserved development panel. Once its observations or transformations inform the amendment, report SDXL as a seen development transformation; reserve an untouched transformation/backbone for any claim of unseen-model transfer. New images alone do not restore unseen-model status. No new method was selected or tuned in these probes.
2. **Run the feasible external baseline early.** [Official-source feasibility](baseline-feasibility.md) changes implementation priority to WAM's explicitly named SA-1B MIT checkpoint. Its 32-bit/native localization result must be separated from the original paper's COCO model and F5's binding endpoint. Vet weights/dependencies and perform one-image memory/quality smoke before the twelve-source native and quality-matched arms. ZoDiac's license/SD2.1/port requirements remain unresolved; FreqMark is paper-specified until official image code is found or a labeled reconstruction is implemented. No external baseline has run, so there is still no matched claim that F5 beats those methods.
3. **Expand the delivered-binding mechanism study.** Target at least 100 exact delivered independent pairs as previously planned, plus explicitly difficult semantic collisions and matched component controls. Freeze independent pair/source selection, total attempt cap and stopping rule before outcomes; reserve new development sources under the existing source policy. Retain failed deliveries and report delivery/all attempts, acceptance/all attempts and acceptance conditional on exact delivery separately. A fixed attempt budget may end below 100 exact deliveries; report that shortfall. For component interventions, specify which decoded codes and q-conditioned instance projections remain fixed, and include cases where component decisions differ; repeated all-reject cases cannot establish synergy. Native T5 was not rerun here. Do not combine these five successes with historical M2 to manufacture a confirmatory bound.
4. **Return to full independent diffusion after the decoding screen.** The prospective 11/12 SDXL-VAE screen was missed; the full independent backbone is not installed. No multi-GB backbone/grid is started just to bypass this negative. A later candidate passing the screen still requires .2/.4 strengths and seeds 0–2; source-majority targets remain at least 11/12 and 9/12 on a 12-source development grid. VAE-screen failure alone cannot prove full-diffusion failure, and future work may run the declared narrow .2/seed-0 diagnostic when its backbone becomes locally available.
5. **Separate calibration, confirmation and writing.** Frozen probes use native nominal 1e-6/profile thresholds; the proposed later empirical operating target remains .001 with fresh calibration data and familywise controls. Keep clean PSNR>35/SSIM>.9/LPIPS<.1, checked T3 targets >=.90/.70 at .2/.4, and T4/T5 simultaneous upper error targets <=.01 as prospective engineering choices. They are not changed M2 gates, measured guarantees or Q1 acceptance criteria. Any revised method needs fresh held-out confirmation and the existing human milestone approval. Build no new runner around this discovery.

The relevant autoresearch lesson remains a bounded hypothesis/commit/measure/log cycle with a frozen evaluator and retained failures. Its GPT-training stack is unnecessary. The result of this cycle is a sharper experimental priority and a narrowed claim, not a successful journal qualification.

## Independent review

The [fresh independent review](discovery-review.md) verified D1-D6 within their stated scopes and accepted exploratory reporting and bounded development routing, with no blocking finding or required scientific rerun. Its four non-blocking clarifications are incorporated above: decision-stage versus physical cause, seen versus unseen transformation, a fixed binding-attempt budget, and controlled component interventions. This records a scientific review, not human M2 acceptance or publication readiness.
