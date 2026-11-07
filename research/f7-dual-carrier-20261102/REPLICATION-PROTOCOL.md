# F7 registry replication on fresh sources (f7c): frozen protocol

Claude, 2026-11-07, frozen before any f7c output exists. The user asked Claude to work on the thesis, improve the remaining weaknesses and proceed to the next experiment.

This is a pre-registered **fresh development replication**, not a held-out confirmation. The images have never been used in this project, but they are development-reserved, not part of a held-out manifest. A held-out confirmation would still need the user's approval and a new held-out cohort.

## 1. Why

Stage B ([RESULTS-REGISTRY.md](RESULTS-REGISTRY.md)) passed every gate with F7 as the registry pointer. Three weaknesses remain:

1. **Thin evidence.** It used 16 development sources, and 10 of them were round-3 calibration sources of the rule.
2. **Stronger regeneration breaks the pointer.** At SDXL .2 the 32-bit code is read in only 1 of 16 sources. SD1.5 .4 loses 2.
3. **Copy-paste safety rests on one factor (B1).** It was measured on 96 copy-paste images only.

**A fix for weakness 2, designed on stage-B data (exploratory, post hoc).** The owner's keyed presence test is still positive in many copies where the code cannot be read. The 32-bit code is not needed to bind: the enrolled record binds. So presence alone can open the owner's records, and the frozen rule then decides each one.

On the stage-B screen this fallback (P2 below) gives:
- 16, 16 and 16 sources on SD1.5 .2, SDXL .1 and Kandinsky 3 .2;
- 11 on SDXL .2 (1 with P1) and 15 on SD1.5 .4;
- still zero accepts for copy-paste, false claim, wrong source, unmarked images and wrong owner, with 252 unrelated distractor records added to the owner's registry.

Probe: `scripts/f7_presence_probe.py` (5d4c49a); outputs: MAIN `.thesis-build/dev-runs/20261107-f7-presence-probe/`. These numbers designed the rule and confirm nothing. This run tests the rule on new images.

## 2. Data (fixed before download)

- **Cohort:** 128 COCO train2017 photographs, IDs 4051-8074. They are the next 128 eligible IDs above round 3's last ID (4020), under the project's original rule: CC BY 2.0, shorter side at least 256, train2017 URL, Flickr attribution hook.
- **Exclusions:** every identity, Flickr photo and recorded hash in all prior inventories. That is 1,400 identities and 30,537 hashes, including round 3, registry-fresh, fresh-development, Stage S/P and the M1b plans.
- **Commits:**
  - selection: `replication/fresh-selection.json`, committed before any download;
  - acquisition: `scripts/f7c_fresh_sources.py`. All 128 were acquired; none overlapped the exclusions by raw, PNG or pixel hash.
- **Split:** `replication/source-manifest.json` (SHA-256 ee997470…) orders the 128 by SHA-256(`f7c-replication-v1/20261107/` + uid).
  - The first 64 are **donors**: they are marked and enrolled.
  - The next 64 are **targets**: unmarked hosts for copy-paste and false claims.
  - No image or outcome informed the order.
- **Rehearsal:** the Stage S rehearsal rows. It is a smoke test only and is never scored.

## 3. Run

- **Driver:** `bash scripts/f6l_driver.sh /workspace/assets /workspace/runs/f6l START PRICE f7c`, from a code archive of branch `claude/f7-confirm-20261107`. The F7 writer and reader are unchanged since the F7 screen (06545ee). The f7c plumbing is commit ff98480.
- **Steps:** the rehearsal, then the fit check, then the screen.
- **Screen contents:**
  - arms: F7 and unmarked;
  - cells: SD1.5 .2, SDXL .1, SDXL .2, Kandinsky 3 .2 and SD1.5 .4;
  - seeds: 0, 1 and 2;
  - threats: T4 (patch 128 and 256, their shams, residual .5 and 1.0) and T5 (recipient unmodified), with donor-target pairs by the Stage S CLIP rule;
  - no distortion stage.

## 4. Registry (frozen)

- **Rule:** the round-3 rule, unchanged (`research/claude-round3-frozen-20261017.json`, blob 6c87e117). Accept when D1 ≥ .0594367 and B1 ≥ .90; if D1 abstains, accept when B1 ≥ .99.
- **The owner's registry** (`qim-pilot-owner-alpha`) has two parts:
  - the 64 F7 clean marks, each with q = its payload q;
  - **distractor records**: every canonical PNG under MAIN `.thesis-build/assets/` `registry-round3-20261017/canonical`, `registry-fresh-20261016/canonical` and `fresh-development-20261013`. A distractor whose bytes equal a screen original is dropped (none is expected). Distractors have no q.
- **P1:** the stage-B pointer. A carrier's code is found, read, scores at least 8.341671 and lies within Hamming distance 6 of the record's q.
- **P2:** P1, or else owner presence. Presence means semantic-tier `found` under the owner's key in the F5, v5 or combined test, each at its own frozen false-positive target. Presence opens every record of that owner.
- **F_R:** the query's own record is accepted. Source majority: at least 2 of 3 seeds.

## 5. Gates (all must hold for PASS)

| Gate | Bar |
|---|---|
| F_R under P2, SD1.5 .2 | ≥ 55/64 (one-sided 95% lower bound .767) |
| F_R under P2, SDXL .1 | ≥ 55/64 |
| F_R under P2, Kandinsky 3 .2 | ≥ 55/64 |
| N1 T4 copy-paste (384 images): accepts of any record except the recipient's, under P1 or P2 | 0 |
| N2 T5 false claim (64 images), likewise | 0 |
| N3 wrong source: every F7 clean and native query against every other record, distractors included | 0 |
| N4 C0: 64 unmarked clean images and 960 unmarked natives against every record, their own source's included | 0 |
| N5 wrong owner: beta enrols each seed-0 F7 copy (all five cells) under its own q; any beta accept under P1 or P2 | 0 |

- **Missing and blocked units:** a safety-blocked or missing positive seed counts as a miss. A blocked negative is listed apart, as in stage B. An unknown negative makes the verdict INCOMPLETE.
- **Verdicts:**
  - **PASS:** every gate holds and no negative is unknown.
  - **SCIENTIFIC_KILL:** any F_R bar or any zero gate fails.

**Secondary hypothesis H-fix (pre-registered):** on SDXL .2, P2 recovers more sources than P1. Test: exact one-sided McNemar on the source-majority outcomes, p < .05.

**Reported, not gated:**
- F_R under P1 in every cell, and under P2 on SDXL .2 and SD1.5 .4;
- presence rates;
- fingerprint-only accepts;
- D1 and B1 margins;
- other-record accepts under P2;
- strict clean quality of the F7 marks.

The driver computes no F7-alone verdict.

## 6. Cost and stops

- **Estimate** from stage-B unit times: setup about 1 h, rehearsal about 0.2 h, screen about 2.1 h, fetch about 0.4 h. That totals about 4 h, about USD 2.5 at USD .60/h.
- **Stop rules:**
  - Claude stops the run if the fit check forecasts more than 6 h in total.
  - Claude stops the instance from inside after the fetch. It is never destroyed.
- **Fetch:** the journals and every clean, native and threat image of the F7 and unmarked arms (`scripts/f7c_fetch_list.py`). Scoring runs on the laptop with `scripts/f7c_registry_score.py`.

## 7. Claim limits

- This is a development replication on 64 fresh sources, not a held-out confirmation.
- P2 was designed on stage-B outputs. This run is its first test on unseen images.
- **Registry scale:** the registry has about 350 records. Larger registries raise P2's false-accept exposure, which grows with the owner's record count. P1 does not have this exposure.
- **Presence false positives:** the design rate is about 1e-6 per test. It is measured only on this run's unmarked rows.
- **Not covered:** the look-alike limitation (E2) belongs to the rule and is not retested. Further regeneration is not tested.
- **Method domain:** F7 is an image-domain mark, not the proposal's latent method. Human visual review is missing.
