# Held-out run: gaps found mid-run, and how to read them (pre-result note)

Written by Claude on 2026-10-17 at about 14:50 PST, while run `registry-div2k300-confirm-01` was still executing.

**Status:** approved by the user on 2026-10-17, before any outcome was computed. See "User decision" at the end.

## What had and had not been seen when this was written

- **Not yet computed by the run:** descriptors, F_R scores and endpoints. The descriptor and analysis stages had not started.
- **What Claude read:** only each journal row's `outcome` status and the error messages of failed rows.
- **Incidental exposure:** while reading the row schema, Claude saw two raw detection rows for unmarked (C0) copies of source 497. These carry no endpoint.
- **Not opened:** no held-out pixels, pointer rates or acceptance counts.

## Gaps (from journal status fields)

1. **F5 could not mark 3 of the 300 photos** (sources 38, 463 and 821), failing with `ValueError: Fresh F5 bootstrap native channels unreadable`. Everything downstream of these three is `input_unavailable`: enrollment, regenerations, copy-paste transfers and attack scenarios.
2. **SD1.5's safety checker blocked 50 regenerations** (`safety_checker_blocked_output`), concentrated on a few photos.
   - At strength .2, sources 181, 442 and 838 lose all three seeds on SD1.5.
   - SD2.1 has no safety checker and had no blocks.

## What the frozen code will do with these gaps

- **E1 (plan_view):** every gap already counts as a miss, which is conservative.
  - At most 294/300 are possible on SD1.5 and 297/300 on SD2.1.
  - The pass line is 266.
- **E2 (frozen `E2.pass_`):** it also requires completeness. Six copy-paste transfers from the three unmarked photos do not exist, so `E2.pass_` will be false whatever the false-accept count is.
- **E3 (frozen `E3.pass_`):** `m1b_registry_analysis.py:107` marks **every** attribution in a cell as unknown if **any** registry record in that cell is incomplete. The three missing owner records alone make every E3 entry unknown, so `E3.pass_` and the combined `pass_` will be false whatever the attributions are. The per-entry attributions are still computed and saved in `metrics/endpoints.json` (`E3.rows`).

The frozen combined verdict is therefore already fixed as "not pass (incomplete)" by operational gaps, independent of the science.

## Proposed reading (Claude's recommendation; the user decides)

1. **Frozen verdict:** report the frozen automated verdict verbatim, including that it fails on completeness and why.
2. **Scientific reading,** declared here before any outcome is known, with E1 unchanged:
   - **E1:** the frozen plan_view result, in which gaps are misses.
   - **E2:** zero false accepts among all negative pairs that exist. Missing pairs are listed with their cause.
   - **E3:** an attribution counts as evaluable when the query image and that source's own owner and attacker records exist. Zero wrong-owner attributions are required among evaluable entries, using the saved `E3.rows`. Non-evaluable entries are listed with their cause.
     - **Why:** a missing record cannot create a wrong-owner accept. It can only remove a competitor. Whether an absent attacker record would have matched another source's query is the cross-source false-accept question that E2 covers.
3. **No changes during the run:** no code, manifest or threshold changes. The M2 analysis applies this reading in a separate script over the frozen outputs.
4. **F5's 1% marking failure is a finding,** to be reported as a limit of F5 on DIV2K.

**Alternative:** strict reading only. The run then reports "not pass (incomplete)", and E2 and E3 stay unresolved.

## User decision

On 2026-10-17, while the run was paused by a cooperative stop at 14:56 PST, the user replied in chat:

> "Approve your proposed reading: report the automatic verdict as is, and also judge E2 and E3 on the images that exist, with E1 unchanged (gaps count as misses)."

**State when the decision was made:**
- the run was paused with 20,369 journal rows;
- no descriptors, F_R scores or endpoints existed;
- nobody had seen any outcome.

**What M2 reports:**
1. **Frozen verdict:** the frozen automated verdict (`metrics/endpoints.json` `pass_`, `E2.pass_`, `E3.pass_`) verbatim, with the reasons it fails on completeness.
2. **E1:** the frozen plan_view result. Gaps count as misses.
3. **E2:** false accepts among all negative pairs that exist, which must be zero. Missing pairs are listed by cause.
4. **E3:** wrong-owner attributions among evaluable entries, read from the saved `E3.rows`, which must be zero. An entry is evaluable when the query image and that source's own owner and attacker records exist. Non-evaluable entries are listed by cause.

**What stays fixed:** the scientific reading is E1, E2 and E3 as defined here. The code, manifest and thresholds of the run are unchanged.

Recorded by Claude at 2026-10-17 14:59 PST.
