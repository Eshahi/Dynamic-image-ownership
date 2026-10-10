# D2 execution decision: retained-state caching and complete cost accounting

2026-10-10. Codex method/execution decision agent, gpt-6-astra, high effort. Prospective decision only; no experiment or code change performed here.

## Decision

**Accept the accounting correction and permit the single already specified D2 writer within the unchanged 3300-second writing/qualification cap.** Caching the complete objective vector of the retained saved state is explicitly required by `native-validated-writer-decision.md`. Removing its redundant recomputation changes neither the objective nor the proposal policy. This is not an iteration shortcut, relaxed gate, new method, smoke retry or extension of the study budget. The twenty logical iterations, three proposals, two phases, twelve sources and all acceptance/qualification requirements remain fixed.

The immutable utility run remains `qualification=budget_infeasible`, `utility_pass=true`, `outcome=completed_internal_utility_only`. Its recorded estimate was correct for the work counted by its code, but that code counted an unnecessary current-state nine-branch pass at every iteration. Do not edit either retained JSON file or present the original run as having passed its recorded throughput gate. The writer's separate record must cite this prospective correction and both estimates.

## Inspected evidence

Inspected the D2 decision, `scripts/journal_native_utility.py`, relevant objective/channel/evaluator/call implementations, and MAIN `.thesis-build/dev-runs/20261010-1206-native-utility/{run.json,results.json}` at commit `941a4014689247b9213e67ef0203a2ad7883af3b`.

The screen completed in 32.297 seconds. Its eight official RNG/timestep/RGB8 parity observations passed. Source 468505's initial maximum loss was 0.3529827595. Saved proposals at 0.10, 0.50 and 1.00 B had maximum losses 0.3220713735, 0.0796464905 and 0.0632745698; all three passed the fixed decrease, clean exact q/h, both_match, strict quality and continuous/saved feasibility rules. These are useful internal proposals, not candidate images or attack-success observations. Discard their role as candidate outputs; preserve the files as exploratory evidence.

Measured maxima used below are: nine forward branches N=2.828 s, native gradient G=1.890 s, clean detector/quality check C=0.813 s and load L=7.688 s. The measured gradient is for `ddim_0.2_seed1`, the four-step DDIM path, not merely the shorter .1 path. This supports a practical throughput projection but is not a mathematical runtime bound for every image or branch. D1/D1N derivative failures remain unchanged; D2's gradient is a heuristic.

## Inclusive prospective budget

The utility script reported `L + 240*(N+G+3*(N+C)) + 24*(N+C) = 3848.912 s`. The declared cached-state algorithm instead needs `L + 240*(G+3*(N+C)) + 24*(N+C) = 3170.192 s`. The 678.720-second difference is exactly 240 redundant nine-branch passes. Do not use early inactivity, failed proposals or stalls to make this estimate fit.

The 3170.192-second figure alone is not sufficient: summed branch times omit proposal projection/PNG work, and a final nine-loss vector is not final semantic qualification. Use this expanded prospective ledger:

| Work, without logical-iteration shortcuts | Seconds |
| --- | ---: |
| One model/evaluator load L | 7.688 |
| 240 native gradients at G | 453.600 |
| 720 proposals at N+C+0.062 | 2666.160 |
| Twelve baseline nine-vectors plus initial clean checks, 12(N+C) | 43.692 |
| Twelve final qualifications, allowance 12(N+6C) | 92.472 |
| Twelve source payload/setup checks, allowance 12C | 9.756 |
| Accounted total | 3273.368 |
| Remaining allowance for record I/O, source setup and shared extra owner calls | 26.632 |
| Absolute writing/qualification cap | 3300.000 |

The 0.062-second proposal overhead is the largest observed full proposal duration minus its separately timed clean check and branch sum; the three residuals were 0.048, 0.062 and 0.046 seconds. Charge it on all 720 proposals, even though independently taking maximum N and C already overestimates observed complete proposal durations.

Final allowance N is available for the two VAE reconstruction/save operations and final vector handling. Six C allowances per source cover all three final C1 conditions and up to three shared C0 condition calls. Wrong-owner calls must share only that suspect image's features and latent, as the existing evaluator supports; their additional decoder work belongs to the explicit remaining allowance. Reused frozen C0 records require the exact unchanged source/condition/operator/detector identity and an explicit reuse label. No target or source feature may be supplied to a suspect detector. Payload extraction uses one additional C allowance per source; the load observation already includes the smoke source's payload, so this is conservative duplication.

These are measured-cost extrapolations with an explicit finite overhead allowance, not an empirical assertion that each unmeasured operation has already been timed. Static implementation review must account for every operation against these categories before launch. In particular, do not add model reloads, per-iteration parity runs, repeated all-history JSON rewrites, extra detector variants or a new measurement trial. If the implementation needs further work outside these allowances, it has not qualified under this decision. The original conservative requirement is met by charging every prescribed operation using available slow measured components and an explicit reserve, not by calling omitted work free. The margin is narrow; successful completion is not guaranteed.

## Exact execution requirements

1. Commit the writer and this decision before executing one ordinary USD 0 development run. Preserve the utility run and link it from the new run.json. Keep screen <=300 s, writing plus qualifications <=3300 s, and official T3/summaries <=1800 s; no borrowing between caps and no new smoke. The total cap remains 5400 s.
2. Start each of the twelve sources from its original RC3 saved RGB8, in the original order, with its fixed original q and frozen operational h. Compute one complete initial nine-loss/detail vector. Keep its first-maximum branch order exactly unchanged.
3. The retained state is one inseparable record: authoritative saved RGB8, its complete ordered nine-loss/detail vector, and its passed clean/feasibility checks. After selecting an eligible proposal, replace the entire retained record with that proposal's record. After rejection, keep the entire existing record. Do not mix branch values across states, use continuous unsaved pixels, cache gradients across accepted updates or use the differentiable forward's loss as a replacement for measured no-grad objective values.
4. Every branch invocation must retain its fixed strength/seed and reset its private RNG and scheduler as the inspected channel does. Frozen models, precision and detector settings remain unchanged. Caching is valid because it retains the already observed deterministic evaluation of the exact state; it cannot be used across changed settings or sources. Any discovered nondeterminism or operator mismatch is a study failure, not permission to average, resample or change the cache policy.
5. Execute the twenty-iteration two-phase policy, full three-proposal evaluations and fixed eligibility/decrease rules verbatim. The previously declared exact no-op/stall rules remain available at runtime, but none is credited in the throughput projection. Log rejected proposals and logical no-ops. Do not overwrite failed evidence or pick a best checkpoint after the fact.
6. Final clean and both deterministic VAE conditions require saved/re-read RGB8 and actual unchanged F5-RC1 semantic predicates, decoded q, clean operational h, both_match and strict quality where prescribed. A small proxy loss or cached vector does not certify them. Reuse the identical retained state's nine-vector if useful, but evaluate final qualification predicates and zero-negative continuity explicitly, with shared controls labelled. Require SD1.5 joint exact-q/semantic 12/12 and SDXL >=11/12, reporting 12/12 preservation separately. All twelve final clean images must pass the original strict rules.
7. Include load, source setup, image/log I/O, failures and final qualifications in the actual wall-clock cap. Keep progress records compact so accumulated history is not rewritten inside every branch. If the cap is exhausted or an implementation/numerical error occurs, stop and retain an incomplete/ineligible candidate; do not shorten the schedule, skip a branch, reuse smoke pixels, restart the study or extend the cap. Routine records suffice; no new execution infrastructure is authorized by this decision.
8. Only complete prerequisite passage allows the unchanged official T3 grid and assessors. Its safety checker/validation path remains mandatory; pre-checker objective evaluations are not attack outcomes. Preserve fixed-I targets, frozen identity continuity, C0/wrong-owner rules and downstream T4/T5 requirements exactly as the parent D2 decision states.

## Honest classification

Current evidence is **positive fixed-source D2 utility, original implementation accounting budget-infeasible, prospectively corrected cached-writer estimate feasible with a narrow margin**. It is not a twelve-source qualification, T3 survivor, M1/M2 change, independent generalization result or validated derivative. This is the same image-domain refinement family, with missing human admissibility and unchanged population-FPR limitations. A writer overrun must be reported as budget incomplete despite this estimate; a completed but unsuccessful writer must keep its measured scientific failure.
