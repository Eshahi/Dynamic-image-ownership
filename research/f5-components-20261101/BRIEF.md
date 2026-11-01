# F5 component research. Codex brief, 2026-11-01

Written by Claude (Opus 5.5), who is the judge and orchestrator of this research. The user asked, verbatim:

> "I want the core research to be more robust. I want you to follow this approach : first, the best solution we have for now ( I think it is F5) then separate it to the components it has. then proceed with this pipelines : based on the previous experiments, first analyze the current structure, then break it to the different system components. then, analyze each one and research the new Q1 Articles related to each component and then find out if we can improve each one for this purpose or not. I want you to be the judge and orchestrator and use the codex for the research and also find results."

**Purpose of every judgement here:** survive regeneration by independent encoders (T3) at strict quality with no visible flaw, while keeping copy-paste (T4) and semantic collision (T5) safe. A component improvement that does not serve this purpose does not count, however good it is elsewhere.

**Roles.** You research, measure and propose. Claude judges. Every verdict you write is PROPOSED. It becomes a ruling only in a Claude ruling file. "No improvement is possible for this component" is a full and acceptable answer when the evidence says so. Do not try to please the judge; [the judge's findings](judge/JUDGE-FINDINGS.md) are hypotheses for you to attack.

RD below means `research/f5-components-20261101/`. MAIN means `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5`.

## 1. Rules

**Compute.**
- CPU only, on saved development data. `CUDA_VISIBLE_DEVICES=-1` is set; do not change it.
- Allowed interpreters: MAIN `.thesis-build/venv/Scripts/python.exe -I` (stdlib) and MAIN `.thesis-build/a6-science-venv/Scripts/python.exe` (numpy, scipy, PIL, torch on CPU, lpips).
- Each run stays under 10 minutes and uses at most 8 worker processes. The guard kills Python running longer than 15 minutes.
- You may load the pinned SD1.5 VAE and CLIP from MAIN `.thesis-build/assets/` read-only, on CPU, in small batches, for reader-side tests on saved images.
- Not allowed: diffusion or UNet passes, regeneration, running any writer's optimization, training, GPU, installs, downloads other than paper PDFs, paid compute, vast.ai, SSH. Anything that needs these goes in the server queue (WP5). Claude runs the server, and the user decides whether it is rented.

**Data.**
- Allowed, read-only: development journals and images under MAIN `.thesis-build/dev-runs/`, namely `20261024-1431-encoder-transfer-stage2a`, `20261025-0128-encoder-transfer-stage2b`, `20261026-0705-et-final-pilot`, `20261026-0855-et-final-phase-a`, `20261030-regen-channel`, and earlier development runs. Committed reports of every study.
- `PHASE_B_JOURNALS=off`. Phase B per-source journals and transfer tars (`20261027-0121-et-final-phase-b/results/*.jsonl`, `xfer/`) are forbidden. Use its committed report only.
- Forbidden: pixels and journals of any held-out cohort, including `.thesis-build/m1b-confirm/`, `.thesis-build/registry-package/artifacts/`, and any E3 held-out analysis folder; Stage C and reserve identifiers. Their committed reports are allowed. Every number from a report is frozen and may not be used to tune anything.
- Later study designs must use fresh disjoint sources.

**Writing.**
- Write only in RD. `RD/judge/` and every `RULING` file belong to Claude; never edit them.
- Do not touch `scripts/`, `configs/`, the proposal, `research/claims.csv`, `THESIS_GUIDE_OFFLINE.html`, retained outputs under `.thesis-build/*runs*`, or MAIN `thesis-runs/d916749c/STATE.md`.
- Analysis scripts go in `RD/analysis/`, outputs in `RD/results/`. Paper PDFs go in MAIN `.thesis-build/cache-f5c/papers/`.
- Commit and push this branch after each work package, using the repository's identity, with no attribution trailers. Never push another branch, never force-push.

**Frozen elsewhere.** The approved F6 package (`research/tifs-20261028/`, receipt `decisions/round3-user-choice.json`) has not run and stays unchanged. You may say whether your findings change the order of next tests. Do not edit or amend it. The coarse-lattice mark (`research/coarse-lattice-20261030/PROPOSAL.md`) is a candidate like any other, with no privilege.

**Scope.** T3, T4, T5 only for design decisions. A cheap new removal route gets one unweighted line. Standard distortions are a secondary article section, never a verdict input.

**Closed lines.** AGENTS.md closes reference-free instance-descriptor variants, E3 micro-variants, FreqMark retries and new external baselines. You may propose reopening one only with new evidence, labelled `REOPENS-CLOSED-LINE`. The judge decides.

**No clock.** There is no deadline. Never wait for time to pass. Floors and rulings define done. Do not stop early and do not pad. Nobody answers questions during the run: record what the judge must decide in the gate request.

**Honesty rules.**
- Label every statement MEASURED, DERIVED, SOURCE or JUDGMENT, with a file and line, or a paper and table.
- Keep failed tests and negative results.
- Separate development counts from frozen held-out counts.
- A new endpoint is never reported as frozen C or J. Report both.
- Never call an image-domain mark the proposal's latent method. State each reader's side information.
- Never fabricate a citation, a quartile, a number or a human verdict. A card you did not read in full text does not count. Metrics do not prove invisibility; human visual verdicts stay MISSING.

## 2. The components

These are the judge's starting map, from the code. Correct it at Gate 1 if the code disagrees: merge, split or add, with reasons.

| ID | Component | Current design | Where |
|---|---|---|---|
| K1 | Semantic descriptor | CLIP ViT-B/32, 7 fixed views averaged, unit vector | `scripts/f5_gate.py:35-54`, `scripts/three_threat_models.py:150-159` |
| K2 | Content code | 32-bit signs of keyed Rademacher projections; soft ML angle | `scripts/f5_latent_codec.py:115-155`, `scripts/revised_watermark_v5.py` `_semantic` |
| K3 | Payload and channel code | 32 segments x 10 chips, 320 chips, repetition only, owner-conditioned tables | `scripts/revised_watermark_v5.py` `_semantic_table`, `:1178-1199` |
| K4 | Carrier space | Posterior-mode latent 4x64x64, 2-D DCT per channel, radius 4-32, 3,272 slots, weight radius/4, keyed signs | `scripts/f5_latent_codec.py:44-85` |
| K5 | Encoder model | One pinned SD1.5 VAE, as both writer surrogate and reader. Robust VAE (RVAE), surrogate ensembles and F6's noise objective belong here | `scripts/f5_latent_codec.py:88-107` |
| K6 | Writer optimizer | 150 steps normalized-gradient PGD, squared hinge, margin 4, learning-rate switch at half | `scripts/f5_latent_codec.py:175-215` |
| K7 | Quality budget and allocation | Global L2 ball at 52 dB, [0,1] box, no mask (`mask_power=0`), RGB8 rounding | `scripts/f5_latent_codec.py:164-172,186,231` |
| K8 | Fragile instance tier and write order | Perceptual hash h, luminance tier at 47 dB, one refinement at 58 dB | `scripts/f5_latent_codec.py:233-250`, v5 `_Fragile` |
| K9 | Reader statistic and thresholds | Normalized correlation; decoded over 2^32 codes (8.26) or recomputed (4.98); Bentkus-Dzindzalieta bound at 1e-6 | `scripts/revised_watermark_v5.py:1149-1199,1232-1278` |
| K10 | Binding decision | Radii 6 and 10, decision table, C and J endpoints | `scripts/revised_watermark_v4.py:978-1016`, `scripts/f5_latent_codec.py:296-311`, `scripts/m1b_e3_s1_analysis.py:70-84` |
| K11 | Keys and side information | Public-derived profile, public OwnerID, no secret; reader needs VAE and CLIP | `experiments/c4-v5-two-tier-regeneration-v1/profile.json`, `research/threat-model.md` |
| K12 | Evaluation protocol | Regenerator families and cells, seeds, T4/T5 construction, source-majority rule, gates | `research/threat-model.md`, `research/encoder-transfer-20261019/`, `research/tifs-20261028/` |

Start from existing maps, then verify against code: `C:/Users/Soroush/.codex/worktrees/codex-rl/research/rl-20261030/01-decision-map.md` and `context/wp1-reader-semantics.md`.

**Existing evidence to read first.** STATE (once), [judge findings](judge/JUDGE-FINDINGS.md), `research/f5-encoder-amplified-latent.md`, `research/f5-plateau-20261005.md`, `research/f5-research-plan.md`, `research/f5-r2-spec.md`, `research/method-amendment-v5.md`, `research/encoder-transfer-20261019/results.md`, `results-2b.md`, `final-study-20261025/phase-a/PHASE-A-REPORT.md`, `final-study-20261025/phase-b/PHASE-B-REPORT.md`, `research/m2-coco512-results.md` (on `claude/m2-coco512-results`, read with `git show`), `research/tifs-20261028/FINAL-REPORT.md`, `research/coarse-lattice-20261030/PROPOSAL.md`, and `research/rl-20261030/FINAL-REPORT.md` in worktree `codex-rl`. Reusable literature, to be re-inspected before counting: `codex-rl/research/rl-20261030/literature/`, `research/q1-dossier-20261018/` in worktree `codex-q1-research`, `research/encoder-transfer-20261019/final-study-20261025/literature/`.

## 3. What counts as a "new Q1 article"

| Class | Meaning | Counts toward floors |
|---|---|---|
| Q1J | Published 2024 or later in a journal with Q1 status under JCR or SJR, with metric, year and category recorded in `RD/literature/venues.md`, plus the evidence URL and access date. Mark `PRIMARY` or `THIRD-PARTY`. Earlier attempts hit 403 on SCImago; a third-party label is acceptable if it says so. | Yes |
| TOP | Published 2024 or later at CVPR, ICCV, ECCV, NeurIPS, ICML, ICLR, AAAI, ACM MM, USENIX Security, IEEE S&P, ACM CCS or NDSS. No quartile is claimed for a conference. | Yes |
| PRE | Preprints and other venues | No. Allowed as leads, labelled |
| OLD | Before 2024, foundational | No. Allowed, labelled |

**Floor per component:** at least 5 Q1J and 3 TOP cards, full text inspected, from at least 15 exact logged queries across at least 4 indexes. K11 and K12 need at least 3 Q1J and 3 TOP. If a component genuinely cannot reach this, log at least 30 queries and report it as an exhaustion, with the reason. One paper may serve two components; report total and unique counts.

**Each card:** full citation, DOI or URL, class, venue evidence, sections and tables read, claim, mechanism, threat model, key numbers with locators, whether it tests regeneration by an independent encoder, what could transfer to this component, and why it might not. Unread leads are listed as UNINSPECTED and count for nothing.

## 4. Work packages and gates

### WP1. Structure and prior evidence, then stop at Gate 1

For each component, create `RD/components/Kxx-name.md` with:
- **A. Structure:** what it does, inputs, outputs, code locators, assumptions, and what it costs in time and in distortion.
- **B. Prior evidence:** every earlier experiment bearing on it, with numbers and paths, including killed variants (H1 carrier geometry, H3 texture mask, H4 thresholds, r3-256 sketch, F4 chroma, E3, registry, descriptor round). State what each actually ruled out and what it did not.

Also in WP1:
- Attack the judge's four findings. Reproduce the loss budget, extend it to Phase A and every development cell, and attribute losses to components wherever saved data allow.
- Give each component a measured or derived **ceiling**: how many sources it could recover at best on each cell. Say UNKNOWN where the data cannot tell.
- Rank components by loss owned and by cost to change.
- Write the query plan for WP2, per component.

**Gate 1.** Commit, push, write `RD/gates/GATE-1-REQUEST.md` (corrected map, ranking, disagreements with the judge, anything that surprised you), then end your turn. Claude replies with `RD/gates/GATE-1-RULING.md` and resumes you. The ruling may reweight the literature effort.

### WP2. Literature per component

Meet the floors in section 3. Write section **C** of each component file: what is new since 2024 for this component, who has solved what under which threat model, and what the literature says cannot be done. Keep `RD/literature/search-log.md`, cards in `RD/literature/cards/`, and `RD/literature/venues.md`.

### WP3. Improvement options

Section **D** of each component file: at least 3 options, or a reasoned statement of why fewer exist. Each option states:
- the mechanism, and the source it comes from;
- which loss class and which cells it targets, with the ceiling from WP1;
- the predicted effect as a range, and the reasoning;
- the price in quality, T4, T5, reader cost, side information and writer cost;
- how flat-region visibility will be checked, for any writer change;
- the strongest simpler alternative;
- the cheapest decisive test and its kill rule, written before the test;
- whether it reopens a closed line.

Options aimed at a class with a small budget must say so and rank low.

### WP4. Offline results

Run the cheapest decisive test now for every option that saved data and the compute rules allow. Fix the kill rule before looking. Design on one half of the development sources and report on the other: even positions design, odd positions evaluate, in sorted source order. Write section **E** of each component file and `RD/results/LEDGER.md`: option, data, command, commit, numbers, kill-rule outcome. Reproducible from committed scripts. Nothing may be tuned on held-out numbers.

### WP5. Proposed verdicts and designs

- Section **F** of each component file: PROPOSED verdict of KEEP, IMPROVE, REPLACE or UNKNOWN, with confidence and the evidence that would change it.
- `RD/INTERACTIONS.md`: which changes conflict or compound. For example, a lower reader threshold against T4, or a robust-only writer against instance binding.
- `RD/CANDIDATE-DESIGNS.md`: at most 2 integrated designs, each naming one choice per component, predicted performance per cell with reasoning, every side-information change and what it could not claim.
- `RD/SERVER-QUEUE.md`: ranked tests needing a GPU. Each has exact sources (fresh or development), cells, seeds, unit counts, cost computed from measured timings, kill rule and which ruling it would decide. Measured anchors: regeneration SD1.5 .2 .54 s, SDXL .1 .99 s, SDXL .2 1.24 s, K3 .2 1.98 s; detector row about 1.5 s; F5 write 119 s per mark alone on one RTX 4090; v5 write 6 s. USD .551 per hour is historical, not a live quote. Say whether these change the order against the approved F6 and the coarse-lattice test.

**Gate 2.** Commit, push, write `RD/gates/GATE-2-REQUEST.md` with the floor table, the verdict table, the top options and everything the judge must decide. End your turn. Claude verifies a sample of cards, quartiles and numbers, and may send it back with numbered findings.

### WP6. Independent reviews

After the Gate 2 ruling, commission fresh agents with no inherited context (`fork_turns: "none"`, `gpt-6-astra` at `xhigh` or below), each writing one file:
- `RD/reviews/floor.md`: counts floors; independently verifies at least 20 cards online across all components, including venue status.
- `RD/reviews/hostile.md`: attacks attribution, ceilings, predicted effects, leakage, multiplicity and bias in both directions.
- `RD/reviews/steelman.md`: looks for the best idea the verdicts wrongly rejected, and for at least 3 missed options.

Close every blocker with a recorded disposition and a fresh rerun of the affected review.

### WP7. Final report, then stop

`RD/FINAL-REPORT.md`. Its first lines are exactly:

```
STATUS: COMPLETE | PARTIAL
COMPONENTS-TO-IMPROVE: <ids>
TOP-OPTION: <one line>
```

Then, in plain language: the per-component table, what was measured against what is only predicted, what the literature changes, what cannot be improved, and the decisions left for the user. Claude writes the final ruling.

## 5. How to work

- Keep `RD/PROGRESS.md`: first line `PHASE_B_JOURNALS=off`, then decisions, floors, deviations and pushes.
- Spawned agents use `gpt-6-astra` at `xhigh` or below, fresh context, one bounded question and one file. Literature agents can run per component in parallel, as long as they write separate files.
- The thread itself may run at `ultra`.
- End your turn only at a gate or when WP7 is complete. A turn ending anywhere else wastes the session. If you truly cannot proceed, write the gate request saying exactly why.
- Your final message at each gate is at most five lines: the gate reached, the commit, and what you need ruled.
