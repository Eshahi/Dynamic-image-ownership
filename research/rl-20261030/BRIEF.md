# Can reinforcement learning help this project? Codex research brief, 2026-10-30

Written by Claude (Opus 5.5). The user asked, verbatim:

> "is using RL algorithms for defining a policy help us improve this? I am thinking of a policy before getting into the encoder ( or other things)"

> "I want to examine the probelity of using RL algoriths in two sides : 1- improving the experiment and 2- use it as a creativity for article publishing. I have many gpt 6 astra credit so you can have as much as time you want, and I want you to set up this research and then give me the prompt to start it in codex"

So this session answers two questions, each with a probability and the reasoning behind it:

- **Side A, the experiment.** Can an RL-based component measurably improve the watermark results, beyond the best non-RL method at the same compute budget?
- **Side B, the article.** Can RL give the project a publishable new idea, and in which venue, with what evidence?

"No" is an acceptable answer to either side. A well-argued "no", with what would change it, is a full result. A well-supported "yes" is worth more than confirming anyone's expectations, including Claude's below.

## 1. Rules

**Research only.**
- Nothing runs on this laptop except the stdlib analysis below: no image generation, marking, regeneration, attack, detection, metric, encoder pass, training or timing.
- No GPU, and no `.thesis-build/a6-science-venv` or other interpreter with torch, diffusers, numpy, scipy, PIL, lpips or open_clip.
- No downloads of images, datasets, model weights or code, and no package installs. Papers are the exception; see below.
- No paid compute, no vast.ai, no SSH. The dedicated vast key is off limits.

**Allowed.**
- Reading files anywhere, except what the data rules below exclude.
- Web search, and reading papers and code online. Save paper PDFs only, under MAIN `.thesis-build/cache-rl/papers/`, where MAIN is `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5`.
- Stdlib Python (MAIN `.thesis-build/venv/Scripts/python.exe -I`) for analysing saved results, computing bounds and costs, and toy simulations with no images or models. Keep each run under 10 minutes.
- Writing in `research/rl-20261030/` only. Call this folder RD. Analysis scripts go in `RD/analysis/`.
- Committing and pushing this branch.

**Do not touch.**
- `scripts/`, `research/tifs-20261028/`, or any other existing file. You write no server code in this session.
- The proposal, claim ledger, `THESIS_GUIDE_OFFLINE.html`, retained run outputs under `.thesis-build/*runs*`, and MAIN `thesis-runs/d916749c/STATE.md`. Claude updates STATE.

**The approved F6 run is frozen and separate.**
- The user approved the F6 package (receipt `research/tifs-20261028/decisions/round3-user-choice.json`, commit f32a322). Claude may run it on a rented server while you work.
- This session does not amend it, and you do not recommend changing it before its outputs exist.
- Stay blind to its outcome. Do not read `.thesis-build/dev-runs/*tifs*` or later commits of `codex/tifs-20261028`, and do not merge other branches. If you see an F6 outcome by accident, record that in PROGRESS and say what it may have influenced.
- Your report must answer conditionally, for each F6 outcome: GO, fail, and RESOURCE_STOP.

**Data rules.**
- Open no image files from any run folder. You work with numbers only.
- **Development journals** (stage 2a, stage 2b, Phase A and the pilot) are always allowed, read-only.
- **Phase B per-source journals** (MAIN `.thesis-build/dev-runs/20261027-0121-et-final-phase-b/results/*.jsonl`) depend on the user's setting in the first message of this thread, `PHASE_B_JOURNALS=on` or `off`.
  - Record the setting verbatim at the top of PROGRESS.
  - `on`: read them for descriptive analysis only, and label every use. The frozen Phase B numbers stay frozen; this does not reopen them.
  - `off`, or missing: use only the committed `phase-b-results.json`, `phase-b-tables.md` and `PHASE-B-REPORT.md`, and state which WP3 questions could not be answered.
- The 40 reserve sources and the Stage C identifiers stay untouched.
- Nothing may be tuned against these outputs. Any design that comes out of this session must later be tested on sources it has never used.

**Threat scope.** Primary claims stay on T3 regeneration, T4 copy-paste forgery and T5 semantic collision, as defined in `research/threat-model.md`. T1/T2 ordinary distortions never carry verdict weight.

**Honesty.**
- Label each claim MEASURED (with file), SOURCE (with locator), DERIVED (with the calculation) or JUDGMENT.
- Never invent a citation, number or result. If you could not read a paper's full text, it is UNINSPECTED. The abstract is not the paper.
- Every probability is labelled subjective and not calibrated.
- **Call things by their true names.** Gradient optimization is not RL. Stage P's successive halving is a bandit-style allocation that already exists, not a new RL contribution. Do not relabel existing work as RL to make it look new.
- Do not retrofit RL onto results already obtained.
- An image-domain watermark stays labelled as a pixel comparator; never report it as the proposal's latent method (RQ-02/HYP-02 stay open).
- You never write an approval for the user.

**Time.**
- There is no deadline and no time budget. The floors in section 5 define when you are done.
- Never wait for time to pass. If work is finished, go to the next item. Earlier sessions idled to a clock, and others rushed despite having time; neither is acceptable.
- Do not pad either. Once the floors pass and fresh reviewers find no blocker, finish.
- If you hit a usage limit, commit, push, record where to resume in PROGRESS, and stop cleanly.

**Working.**
- Nobody answers questions during the session. Record decisions for the user in PROGRESS and continue.
- Commit and push after every work package. Use the repository's git identity, add no AI co-author or attribution trailer, push only this branch, never main, never force-push. If the default TLS backend stalls, use `git -c http.sslBackend=openssl push`.
- Spawned agents use `gpt-6-astra` at `xhigh` or below. They are short-lived: one question, one file. Reviewers and forecasters are fresh, with no prior context.

## 2. Where the project stands

Verify these at source before relying on them. Paths are relative to the repository root unless they say MAIN. FS means `research/encoder-transfer-20261019/final-study-20261025`, and TD means `research/tifs-20261028`.

**Vocabulary.**
- **F5 r2:** the retained encoder-amplified image-domain writer and its reader. Never changed.
- **F6:** a new writer optimizing the unchanged F5 reader through surrogates of foreign encoders. F6-noise uses codec plus noise; F6-x0 adds one native denoiser step. No F6 result exists yet.
- **R0, R1, K3:** native img2img regeneration by SD1.5, SDXL and Kandinsky 3. The number after them is the strength.
- **C, J:** source-majority content-compatible detection, and exact original code with content consistency.
- **VINE-R:** a published robust watermark used as a baseline. **VINE-B:** the F5 content code carried inside VINE-R's 100 bits.

**Measured results (Phase B, 200 held-out sources, `FS/phase-b/PHASE-B-REPORT.md`).**
- F5 source-majority C: SD1.5 at .1/.2/.4 is 186/182/140 of 200; SDXL at .1/.2/.4 is 19/0/0; K3 at .2 is 61.
- VINE-R: 194 at R0 .2, 200 at R1 .1 and R1 .2, 200 at K3 .2.
- Clean quality: F5 about 45.1 dB and LPIPS .035; VINE-R LPIPS .008.
- Codec round trips alone retained 55/60 on development data, so the encoder pass by itself is not what kills the mark.
- Holm family: H2 and H6 supported; H1 and H3 inconclusive; H4 and H5 not evaluable.
- All negative gates are incomplete (4 to 8 unresolved sources from 134 safety blocks).
- Ownership: F5 T4/T5 on development only, 0/20 and 0/66.

**Mechanism (`FS/phase-a/PHASE-A-REPORT.md`, `TD/01-tifs-bar.md`).**
- The first-order transfer law was falsified: SDXL tangents are 8 to 15 times too large and nearly orthogonal.
- Encoder gain of 1.6 to 3.1 times does not predict survival. Retention fell from .66 to .08 at noise injection.

**Measured compute (instance 57877693, RTX 4090 with 48 GB, USD .551/h, `MAIN .thesis-build/dev-runs/20261027-0121-et-final-phase-b/results/`).**
- Native regeneration medians: R0 .2 .54 s, R1 .1 .99 s, R1 .2 1.24 s, K3 .2 1.98 s.
- Detector row about 1.4 s; quality row about .25 s.
- Median writing seconds per mark, from that run's `clean.jsonl`: F5 r2 732, v5 r3 5.5, WAM .21, VINE-R .33. F5 ran in six shards sharing the machine, so one F5 mark used about 2 minutes of the whole machine. Anything that rewrites an F5-style mark per rollout pays this cost; anything acting on a published carrier may not.
- F6 writing time is unmeasured; Claude's planning anchor is 361 to 723 s per mark.
- Use these numbers, not guesses. Earlier forecasts were 5 to 10 times too slow because they assumed.

**Data supply.**
- All 60 development sources are assigned: 24 to Stage P and 36 to Stage S.
- COCO test and DIV2K test are consumed, and the Phase B 200 are consumed confirmation.
- A method that needs a training set must say where the images come from. New development images may be added later from free, licensed sources under a fixed rule, never from validation, test or held-out pools. Do not acquire any now.

**Publication state.**
- `TD/FINAL-REPORT.md` and `TD/02-prior-art-delta.md` map what is occupied. Do not redo them; build on them.
- Generic binding, fixed-reader optimization, noise-aware insertion and registry pointers are all pre-empted.
- `FS/venue-fit.md` covers venues. Which ranking counts as "Q1" for the user (JCR or SJR, which year and category) is still unresolved, so report both wherever you can verify them.
- The negative-result article frame in `FS/article-drafts/` is the current no-experiment fallback, and the baseline any RL route must beat.

**Read first.**
`TD/FINAL-REPORT.md`, `TD/01-tifs-bar.md`, `TD/02-prior-art-delta.md`, `TD/03-ideas.md`, `TD/04-selection.md`, `TD/09-round3-amendment.md`, `TD/stage-p/PROTOCOL.md`, `TD/design/r3-surrogate-prior-art.md`, `TD/design/r3-gate-analysis.md`, `FS/phase-a/PHASE-A-REPORT.md`, `FS/phase-b/PHASE-B-REPORT.md`, `FS/venue-fit.md`, `FS/article-drafts/README.md`, `research/threat-model.md`, `research/f5-r2-spec.md`, `scripts/tifs_writer.py`, `scripts/tifs_denoiser.py`.

## 3. Claude's current view: attack it

This is a hypothesis, not a finding. Claude gave the user this view before this session, from one quick search and no deep analysis. Try hard to break it in both directions.

1. F5's failure looks like a problem of *where the signal lives*, not of *how we search*. An optimizer of any kind puts the signal where the encoders it can see keep it. The real test is an encoder it has never seen, and RL inherits that generalization problem.
2. Where gradients exist, a policy gradient is roughly a noisy estimate of a gradient we can already compute.
3. Each rollout costs seconds, so RL's sample demands may be unaffordable, and there is no training set.
4. Reviewers will ask "why not gradients?", so the label alone adds no novelty.

Claude also thought RL fits best where decisions are discrete, gradients are absent or too costly, effects are delayed, or an opponent is strategic. That points at per-image settings, red-team attackers, games and verification policies more than at the writer itself.

**A gap in that view worth examining:** VINE-R carries 100 bits through all these regenerators at far lower distortion than F5. So the channel has room, and F5's limit may be its carrier and reader rather than any capacity bound. Whether a policy can help while keeping the F5 reader, or only by changing it, is an open question for this study.

## 4. Scope

**What counts as RL.** Every candidate names its class, and the final claims use the true name.

| Class | Includes |
|---|---|
| R-full | Sequential decision making with delayed reward: policy gradient, actor-critic, Q-learning, model-based, offline RL, meta-RL |
| R-bandit | Multi-armed and contextual bandits, no-regret learners |
| R-game | Multi-agent RL, PSRO, double oracle, fictitious play, learned equilibria |
| Comparator, not RL | Gradient methods, random search, Bayesian optimization, CMA-ES, NES, SPSA, successive halving, fixed schedules |

If a candidate works just as well in its non-RL form, say so. That counts against "RL" even if it supports the idea.

**Where a policy could sit.** The user's phrase "a policy before getting into the encoder" has several readings. Cover at least the first three, and treat the rest as starting points, not limits.

| Point | Decision | Example |
|---|---|---|
| P1 | Per-image choice before marking | Budget, carrier or writer configuration, from clean-image features |
| P2 | Spatial or frequency allocation before the encoder | Where the signal goes, by region or band |
| P3 | Pre-encoder transforms in the writer loop | Which surrogate, timestep or transform at each step, as in AutoAugment |
| P4 | Optimizer control | Step size, loss weights and stopping per image, as in learning to optimize |
| P5 | Verifier side | Which views to read, sequential testing, with multiple-testing correction |
| P6 | Attacker side, within T3/T4/T5 | Red-team choice of regeneration chain, strength or prompt; forgery policy; collision finder |
| P7 | Game between writer and attacker | Mixed strategies over carriers and writers |
| P8 | Experiment management | Allocating compute across sources, configurations and rungs |
| P9 | Carrier combination | What to place in each carrier, per image, for example with VINE-B |
| P10 | Registry and lookup | When to query, and how to treat candidate-set size |

## 5. Work packages and floors

Floors are minimums, not targets. Never meet one by lowering quality. A literature floor may be missed only under the exhaustion rule in WP2.

### WP0: start
Create `RD/PROGRESS.md`: start time, the `PHASE_B_JOURNALS` setting, and a floors table you update after every work package. Read section 2's list.

### WP1: decision map, `RD/01-decision-map.md`
Go through the pipeline stage by stage, reading the actual code and specs. Floor: **at least 12 decision points.** For each, record:
- the current setting, and who or what chose it;
- discrete or continuous;
- whether a gradient is available, and its measured cost;
- how long feedback is delayed;
- what information exists at decision time;
- whether it is truly sequential, meaning an early action changes later states;
- what evidence says it limits results (cite the file);
- the natural tool: RL, bandit, gradient, or none.

Then state which necessary conditions must hold for RL to beat the comparator there.

### WP2: literature, `RD/literature/` and `RD/02-prior-art.md`
Floor: **at least 80 logged queries across at least 5 indexes** (arXiv, Semantic Scholar, Google Scholar or equivalent, IEEE Xplore, ACM DL, DBLP, OpenReview, CVF) in `RD/literature/search-log.md`.

Card floors per cluster. Only full-text-inspected cards count. Every card has: title, authors, venue and year, URL, access date, version and sections read, setting (post-hoc or generation-time, image or text), RL class, state, action and reward, comparator used, effect size, what it pre-empts, and its limits.

| Cluster | Topic | Cards |
|---|---|---|
| C1 | RL or bandits for watermark embedding or steganography, classic and deep | 15 |
| C2 | RL or learned-policy attacks on watermarks and detectors; adaptive black-box attacks | 15 |
| C3 | Learned augmentation policies versus random (AutoAugment line), and whether RL beat random | 10 |
| C4 | Transfer across unseen models in adversarial attacks: ensembles, learned or bandit model weighting, effect sizes | 15 |
| C5 | Game-theoretic watermarking and security games; PSRO, double oracle; information-theoretic watermark games | 12 |
| C6 | Learning to optimize; RL-controlled attack or optimization loops | 8 |
| C7 | Per-image adaptive settings; contextual bandits; off-policy evaluation with logged data | 8 |
| C8 | RL with diffusion models: sampling schedules, latent policies, trajectory attacks | 10 |
| C9 | Sequential and active verification; test-time view selection; false-positive control | 8 |
| C10 | How reviewers judge RL work: reproducibility, seeds, RL versus simpler baselines; RL papers in TIFS and similar venues and how they evaluate | 10 |
| C11 | Sim-to-real and domain randomization as an analogy for unseen regenerators | 8 |
| C12 | Regeneration and transfer robustness from the last 12 months, updating `TD/02-prior-art-delta.md` | 15 |

**Exhaustion rule.** A cluster may finish below its floor only if the log shows at least 12 distinct queries across at least 4 indexes for it, and you state that further queries found nothing new. Say what that absence does and does not show.

**Starting pointers, from Claude's memory and unverified. Check each one before use:**
- Tang et al., SPAR-RL, RL for steganography cost learning, reportedly in TIFS. This may be the closest TIFS precedent.
- Lukas et al., adaptive attacks on image watermarks (ICLR 2024); UnMarker.
- AutoAugment and RandAugment; Henderson et al., "Deep Reinforcement Learning that Matters"; Li and Talwalkar on random search for architecture search.
- Lanctot et al., PSRO.
- MI-FGSM and ensemble transfer attacks.

A quick search by Claude found a [KAIST thesis](https://dspace.kaist.ac.kr/handle/10203/283328) on an RL-style framework for blind robust watermarking, and no paper using RL to embed against diffusion regeneration. That was one search, so it proves nothing.

`02-prior-art.md` ends with a novelty map and answers this directly: has anyone used RL to write, select or attack a post-hoc image mark under diffusion regeneration? State how hard you searched.

### WP3: analysis of saved results, `RD/03-logged-analysis.md` and `RD/analysis/`
Stdlib only, read-only, numbers only. Some older results are inside tar files in the run folders; read them in memory and never extract into run folders. Journals have detector scores and thresholds, for example `calls.<owner>.raw.semantic` and `.instance`, with `score`, `threshold`, `code_distance` and `content_match`. Establish the exact meaning of those fields from the code before using them.

These numbers decide whether a policy has anything to learn. Answer each one:

1. **Reward signal.** For each cell and arm, how far below the threshold is the soft margin (score minus threshold)? What fraction of pass/fail rewards are not stuck at the floor?
2. **Source versus seed.** Decompose soft-margin variance into source, seed and residual. If seed dominates, a per-image policy has little to learn. If source dominates, there is something to learn.
3. **Personalization ceiling.** The data are full-information: every source saw every arm and cell. Compute the best fixed arm against the per-source oracle, as an upper bound on any per-image selection. Keep each arm's different payload and quality visible.
4. **Predictability.** Can numeric features known before regeneration (clean reader margin, embedding report, quality) rank which sources survive? Use leave-one-source-out and compare with a constant predictor. This is post-hoc and descriptive.
5. **Sample cost.** From the measured seed-level variance, how many rollouts are needed to rank K options at stated confidence, for K = 8, 64, 1024, and for a score-function gradient on a continuous policy? Convert to GPU-hours and USD with the measured seconds.
6. **Attacker room.** Across family, strength and source, is there any spread that an attacker policy could exploit, including against VINE-R?

State the limits: nothing was randomized, the arms are fixed methods, and none of this shows what a new policy would do.

### WP4: theory, `RD/04-theory.md`
- When does RL beat gradient methods? Derive it for this setting: score-function versus pathwise estimator variance, with this project's measured magnitudes; bandit regret at short horizons.
- What can any policy learn about an unseen encoder from at most three or four seen families? Is leave-one-family-out meaningful at this n?
- What limits any writer that keeps the F5 reader, given VINE-R's survival? Is the limit the reader, the carrier, or the quality budget?
- Toy simulations are allowed under the rules above and are labelled as toys.

### WP5: candidates, `RD/05a-raw-ideas.md`, `RD/05-screen-rule.md`, `RD/05-candidates/`, `RD/05-candidate-table.md`
**Diverge first.** Floor: **at least 40 raw ideas**, unfiltered, from at least 3 fresh agents with different framings: an RL theorist, a watermark and security researcher, and an outsider drawing analogies from fields like robotics sim-to-real, compiler autotuning, chip placement and game AI.

**Fix the screening rule before scoring.** Write and commit `05-screen-rule.md` and record its hash. It must at least require:
- one necessary condition from WP1 is met;
- a non-RL comparator is named;
- no held-out data is needed;
- the novelty is not already fully occupied.

The first decisive test should cost at most 20 instance-hours, about USD 11 at the measured price. Mark costlier candidates EXPENSIVE rather than dropping them silently.

**Then write full sheets.** Floor: **at least 20 candidates**, covering at least 7 policy points, all three RL classes, at least 3 readings of "before the encoder", and at least 4 ideas from outside watermarking. Check each against `TD/03-ideas.md` so you do not repeat a rejected idea unknowingly.

Each sheet has:
- class and policy point;
- state, action, transition, reward and horizon;
- what the policy sees in training and at test, and any leakage;
- the simplest non-RL comparator at the same budget (mandatory);
- why RL would beat that comparator, and which condition it relies on;
- expected effect size and its evidence;
- data needed and its source;
- compute as rollouts times measured seconds, then GPU-hours and USD;
- effect on T3, T4/T5 binding and quality (strict bar: PSNR above 35, SSIM above .9, LPIPS below .1);
- the kill rule, and the cost of the cheapest decisive test;
- the closest three works, and novelty status;
- one sentence stating the claim it could publish;
- one steelman paragraph, one hostile paragraph, and your verdict.

Apply the rule to get a **shortlist of at most 6**, in the table.

### WP6: probabilities, `RD/06-probabilities.md` and `RD/forecasts/`
Floor: **at least 5 independent fresh forecasters** (`gpt-6-astra`, `xhigh`), who do not see each other's answers or yours. Give them all the same neutral evidence packet, with the project's own history as a reference class: how many past candidates passed their gates (derive it from the repository and record it).

For each shortlisted candidate, and for the overall question "does the best RL candidate beat the best non-RL method?", elicit 10th, 50th and 90th percentiles with reasons and reference classes:

| Item | Probability that... |
|---|---|
| A1 | It can be built and run within the stated hours |
| A2 | On development data it beats its non-RL comparator at equal budget, by a margin fixed in advance, with strict quality and T4/T5 preserved |
| A3 | That also holds on a family excluded from training, given A2 |
| A4 | It is confirmed on fresh sources, given A3 |
| B1 | Its novelty survives a thorough search |
| B2 | It passes desk review at the named venue, given the evidence so far |
| B3 | It is accepted, given B2 |

Report the median and the spread, and show where forecasters disagree and why. Multiply only conditional probabilities, and say so. Answer for each F6 outcome. Compare with the current no-RL routes.

### WP7: article routes, `RD/07-article-routes.md`
Floor: **at least 10 routes**, including at least:
- 3 that do not need F6 to succeed;
- 1 rigorous null ("RL does not beat gradients here");
- 1 attacker or red-team paper;
- 1 game-theoretic paper;
- 1 where RL is only a small arm;
- the two no-RL baselines: the existing negative-result frame and the F6 paper.

For each route:
- the claim in one sentence, and why that venue's readers would care;
- at least three closest inspected works, and what is actually new;
- evidence needed, in hours and USD, and its dependencies, such as the F6 outcome or a licence;
- target venues with their fit and verified JCR and SJR status;
- the top five objections from a hostile reviewer, with answers;
- the probability chain from WP6.

**Decoration test for each route:** remove the word "RL" from the claim. If the claim still stands, RL is not the contribution, so say that plainly.

### WP8: next experiment, `RD/08-next-experiment.md`
If any candidate survives, write a prospective design for **at most two**. No server code. Include:
- question and hypotheses;
- arms, including the non-RL comparator at equal budget and a random policy;
- sources, disjoint from Stage S, Stage P, Phase B, the reserves and Stage C;
- cells and seeds;
- a family excluded from training;
- metrics (C, J, strict quality, T4/T5);
- stop rules fixed in advance, and multiplicity disclosure;
- full inventory, with GPU-hours and USD from measured numbers;
- a decision tree across the F6 outcomes.

If none survives, write what evidence would change the verdict and what it would cost to get.

### WP9: independent review, `RD/09-review.md`
Use fresh agents with no prior context:
- **Floor auditor.** Counts every floor and fails on any unmet one. Samples at least 15 cards and verifies online that each paper exists and that the card's claims match the cited section. Checks that exhaustion claims are backed by the search log.
- **Hostile scientific reviewer.** Looks for overclaiming, RL used as decoration, unfair comparators, leakage, and bias in either direction: toward novelty, or toward agreeing with Claude's view.
- **Steelman reviewer.** Tries to rescue the candidates you killed, and proposes at least 3 ideas you missed, each checked.

Apply the findings and record each disposition. After any blocker or unmet floor, fix it and rerun with new fresh agents.

### WP10: final report, `RD/FINAL-REPORT.md`
The first three lines must be exactly:

```
STATUS: COMPLETE | PARTIAL
SIDE-A: PURSUE | CONDITIONAL | DO-NOT-PURSUE
SIDE-B: PURSUE | CONDITIONAL | DO-NOT-PURSUE
```

Then, in plain language:
- one paragraph answering each side;
- the probability table: median, range, and whose estimate;
- the best candidate and what it must beat;
- what was ruled out, and why;
- the recommended action with its cost, for each F6 outcome;
- decisions for the user;
- limits, including what remained uninspected;
- a reading map.

Commit, push, and end the thread with a short Persian summary for the user: both verdicts, the key probabilities, and what they need to decide.

## 6. When the goal is complete

All of these must be true:
- The fresh floor audit passes.
- Every review blocker is closed.
- `FINAL-REPORT.md` starts with the three lines above, with `STATUS: COMPLETE`.
- Everything is pushed.
- You have ended with the Persian summary.

If you cannot get there, write `STATUS: PARTIAL`, say exactly what is missing and why, push, and stop.
