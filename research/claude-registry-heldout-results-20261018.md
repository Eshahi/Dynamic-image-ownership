# Held-out registry confirmation: results (M2 first pass)

Claude, 2026-10-18. This is the result of run `registry-div2k300-confirm-01`:
- approved manifest `a8ef7edc…`, scientific core `3ced354af2bd2a1e`, commit `c58a9ca`;
- 300 DIV2K test photographs and 60 new Tears of Steel look-alike pairs;
- local laptop GPU, USD 0.

The pre-result reading the user approved is in `claude-registry-heldout-gap-note-20261017.md` (commits 12b798d and 0c1da43). Every number below was recomputed independently from the raw journal, the images and the descriptor caches with Claude's own code (`scripts/claude_verify_heldout_registry.py`), and matches the frozen scorer exactly.

## Verdict

**The confirmation does not pass. E1 and E3 pass; E2 fails on clearly different real look-alikes.**

| Endpoint | Pass condition | Result | Verdict |
|---|---|---|---|
| E1, SD1.5 at .2 | ≥ 266/300 (one-sided 95% CP lower ≥ .85) | **277/300**, lower bound .893 | pass |
| E1, SD2.1 at .2 | ≥ 266/300 | **280/300**, lower bound .905 | pass |
| E2, unrelated pairs | 0 false accepts | **0** of 3,343,081 observed (3,408,600 planned, 65,519 unavailable; 300 clusters, upper 95% ≈ 1.0%) | pass |
| E2, T4 copy-paste transfers | 0 | **0** of 594 observed (600 planned, 297 donor groups) | pass |
| E2, real look-alikes below 18.126 dB | 0 | **3** of 45 pairs, in 2 of 16 shots | **fail** |
| E3, wrong-owner attributions (approved reading) | 0 | **0** in all 8 cells; 293-297 of 300 evaluable per cell | pass |

- **Frozen automated verdict:** `pass_ = false` and `plan_view_E1_E2_pass = false`.
  - The cause is the 3 look-alike false accepts.
  - The completeness checks fail too: 6 missing T4 rows, and every E3 entry is marked unknown.
- **Approved scientific reading:** E2 fails on the same 3 accepts, which have nothing to do with missing data. So the overall result is the same under both readings.

## E2 failure detail

All three accepts passed the main two-part rule, with D1 present, not the plain-image fallback. All three sit within 1.3 dB of the cutoff:

| Pair | PSNR (dB) | D1 (τ1 .0594) | B1 (τ2 .90) |
|---|---|---|---|
| tos-07_1c-o144 | 16.89 | .069 | .902 |
| tos-05_4h-o072 | 17.24 | .208 | .955 |
| tos-05_4h-o144 | 17.68 | .352 | .958 |

The other 42 different pairs were rejected. Ambiguous pairs (15) are reported only: 2 accepts (tos-05_3b), as expected for near-copies.

**Scope of this test:** under the pre-registered protocol, look-alike negatives are scored with the descriptor rule alone, without the watermark pointer. This is the worst case, in which both frames are enrolled under the same owner key with close semantic codes. The result therefore shows that the D1+B1 record check cannot reliably separate frames of the same shot at about 17 dB.

## E3 detail (approved complete-case reading)

| Cell | Evaluable | Pointer registry | Fingerprint-only (no watermark) |
|---|---|---|---|
| SD1.5 .2, exact copy | 294 | 280 original owner, 14 none, **0 wrong** | 293 ambiguous, 1 wrong owner |
| SD1.5 .2, further regeneration | 294 | 242 / 52 / **0** | 285 ambiguous, 8 wrong, 1 none |
| SD1.5 .4, exact copy | 294 | 201 / 93 / **0** | 266 ambiguous, 28 wrong |
| SD1.5 .4, further regeneration | 293 | 81 / 212 / **0** | 188 ambiguous, 75 wrong, 30 none |
| SD2.1 .2, exact copy | 297 | 282 / 15 / **0** | 296 ambiguous, 1 wrong |
| SD2.1 .2, further regeneration | 297 | 249 / 48 / **0** | 289 ambiguous, 7 wrong, 1 none |
| SD2.1 .4, exact copy | 297 | 199 / 98 / **0** | 266 ambiguous, 31 wrong |
| SD2.1 .4, further regeneration | 297 | 81 / 216 / **0** | 190 ambiguous, 75 wrong, 32 none |

Non-evaluable entries: 3 sources per cell where F5 could not mark the photo. On SD1.5, 3-4 more per cell where the safety checker blocked the attacker's regeneration.

Without the watermark, fingerprint matching cannot tell owner from attacker (almost all ambiguous, up to 75 wrong). The pointer never names the attacker.

## Operational facts

- **Size and duration:**
  - 53,580 journal units: 53,053 completed, 53 scientific failures, 474 unavailable because of those failures.
  - 12.06 h of compute over three attempts:
    - attempt 1 failed on an approval-path mistake before any held-out pixel was read;
    - attempt 2 ended with a cooperative stop at the user's request;
    - attempt 3 was the last approved continuation.
- **F5 marking:** F5 could not mark 3/300 DIV2K photos (sources 38, 463, 821: "bootstrap native channels unreadable"). This is a method limit.
- **Safety checker:** SD1.5's safety checker blocked 50 regenerations. In E1 these count as misses.

## What may and may not be claimed

- **May claim:**
  - registry attribution of SD1.5/SD2.1 regenerations at strength .2 on new real photographs (277/300 and 280/300);
  - zero false accepts among 3,343,081 observed unrelated comparisons and 594 observed copy-paste transfers. These are correlated comparisons, not millions of independent trials;
  - under the approved pre-result complete-case reading, zero attacker accepts among 293-297 evaluable sources per cell after passive regenerate-and-enroll. Fingerprint-only matching fails the same criterion, mostly through ambiguity: it accepts both owners. Unique attacker attributions are reported separately from that ambiguity.
- **May not claim:**
  - the confirmation as a whole;
  - zero false accepts on clearly different look-alikes. Observed: 3/45 pairs, 2/16 shots, cluster upper 95% bound .34.
- **No post-hoc fix on this data counts as confirmation.** A stricter threshold or a different cutoff chosen now would be exploratory and would need a new held-out set.

## Still open in M2

- **Claims audit and one independent review.** These are planned on Codex with its strongest model, after the laptop restart. Codex is currently unable to start because of the 60-second launch delay.
- **The user's decision on next steps.**

## User decision (2026-10-18)

The user chose to report the result as it stands ("Treat it"). Claude asked them to choose between "report as is" and "fix, then retest"; their reply is read as the first, Claude's recommendation.

**What the thesis states:**
- E1 and E3 are confirmed on held-out data.
- E2 fails on close real look-alikes (3/45 pairs, 2/16 shots, 16.9-17.7 dB). This is a stated limitation of the D1+B1 record check.
- No thresholds or definitions are changed on this data.

**Next M2 step:** one independent review and claims audit by Codex (strongest model), once Codex runs again.

## Independent M2 review (Codex, 2026-10-18)

**Verdict: accept with corrections, for reporting a bounded negative overall confirmation.** Review file: `research/q1-dossier-20261018/01b-heldout-registry-m2-review.md` on branch `codex/q1-research-20261018`.

The four blocking corrections are applied above:
1. **Unrelated pairs:** 3,343,081 observed of 3,408,600 planned. Claude checked this against `metrics/endpoints.json` (`E2.unknown_pairs` = 65,519).
2. **E3 wording:** stated as complete-case. The frozen flags stay false: `pass_`, `plan_view_E1_E2_pass`, `E2.pass_` and `E3.pass_`.
3. **Fingerprint comparison:** ambiguity is a failure of the criterion, reported apart from unique wrong-owner calls.
4. **Effective units:** 297 observed T4 donors, 16 shots for the look-alikes, and 293-297 sources per E3 cell.

**Post-hoc explanation of E3 (EV-77, a count of saved results only).** In every completed query, the attacker's own owner detection returned `found=false`, because a passive attacker never embeds a mark. The zero-attacker result therefore follows from owner detection alone. It does not show any added benefit from the q-code match or the D1+B1 record check. The reportable value of E3 is narrower: the original owner's mark survives and names that owner, where fingerprint-only matching cannot decide.

**Wording change in the user decision above:** "E1 and E3 are confirmed" should be read as E1 confirmed, and E3 observed under the complete-case reading with the EV-77 explanation.
