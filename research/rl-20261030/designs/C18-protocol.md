# C18 prospective protocol: acquire action differences at full cost

Date: 2026-10-30. Status: DESIGN ONLY; no expenditure, acquisition, implementation or execution is authorized.
JUDGMENT identifies design choices; DERIVED identifies arithmetic. No new empirical result is reported.
This implements WP8 for [C18](../05-candidates/C18.md) and [R07](../07-article-routes.md#r07--action-advantage-allocation-rather-than-difficulty-prediction).
Only the conditional first screen is recommended for a later user decision. The larger stage is a bounded feasibility specification, not a recommendation to spend 200 hours.

## 1. Question, scope and hypotheses

JUDGMENT: can prospective acquisition of uncertain configuration differences save at least 25% of total study-to-deployment cost while keeping C/J decision regret within .05 of a strong, independently selected classical allocator?
H0-cost: the full cost ratio is greater than .75. H0-regret: at least one registered C/J regret difference exceeds .05.
Success requires both cost and regret conditions, strict quality and complete finite negative checks; label-count reduction alone fails.
The object is experiment efficiency, not improved defense. C18 has no defensive A2/A3/A4 event and cannot establish stronger T3/T4/T5 protection.
The posterior-sampling method below is bandit-style active acquisition; there is no actor-critic, policy-gradient or learned delayed-reward controller.
Calling Bayesian experimental design or successive halving “RL” would not earn an algorithmic contribution.
SOURCE: [WP3](../03-logged-analysis.md) found only 1/420 within-cell C oracle improvement for retained arms; this motivates a headroom screen, not an assumed new action advantage.

## 2. Frozen physical action menu and observations

Use four separately named non-F6 configurations of the F5 r2 image-domain comparator; keep its q32/h32 payload, reader, thresholds, public owner conditioning, band, radius and refinement fixed.
SOURCE: `configs/f5-r2.json` pins 150 robust steps, PSNR budget 52, target margin 4, one refinement and the existing reader/profile.
SOURCE: `scripts/f5_latent_codec.py` uses normalized-gradient step size `budget*(.2 if t<75 else .05)` for the 150-step robust pass.
JUDGMENT menu: A0 multiplies that step size by 1; A1 by .5; A2 by 1.5; A3 by 1.5 for t<75 and .5 thereafter.
Change only the first robust pass; keep the existing refinement unchanged. Every action uses the same number of gradient evaluations, RGB8 finalization and original payload.
No early writer stopping, best-restart selection, F6 parameter, foreign surrogate, learned reader or new detector threshold enters this menu.
Future implementation must record exact repository/config/model revisions and verify these differences before first acquisition; mismatch yields DESIGN_UNAVAILABLE, never an unnoticed menu change.
The 122-second write proxy is conditional: changed step sizes may alter realized runtime. Measure it only in a separately authorized future stage.
Available source context is intercept, RGB means, luminance standard deviation, mean absolute first spatial difference and log aspect ratio, measured from the unmarked source.
Standardization uses fitting sources only. No clean marked margin, quality outcome or future regenerator is a free context feature.
Both source-feature extraction and image preparation are metered. A costly extra feature requires a new prospective protocol, not an uncharged improvement.
The downstream selector fits separate ridge regressions for each action's known-cell C and J utility; choose the largest predicted `(C+J)/2`, breaking ties by action index.
Fit ridge lambda in {.1,1,10} using only selection groups; every allocator gets the same model, grid, features and observed-outcome access.
The full-information supervised selector uses a fully purchased fitting table and the identical regression class; its extra outcomes are fully charged.

## 3. Sources, operational cells and seeds

Apply the [fresh-data contract](../ideas/fresh-data-contract.md) without acquiring anything now: frozen Commons metadata, eligible explicit per-file CC0/BY/BY-SA, recorded licence versions/attribution/revisions, deterministic identifier ordering, grouped duplicates and outcome-independent exclusions.
An authorized custodian excludes every old/assigned/protected source pool, including P/S, pilot/Phase A/B, COCO/DIV2K, reserves and Stage C, by IDs/hashes and related-image checks. This protocol does not open those lists.
First screen: exactly 48 independent connected groups, split 24 fit /12 selection /12 sealed check in the fixed ordering, before outcomes.
Each group contains one target photograph plus separately fixed T4 recipient and unmodified T5 look-alike; all connected images remain in one split.
Fix T4 as a public-pixel central 128×128 donor patch pasted into the central 128×128 recipient region at the common 512×512 analysis size, without private residual access or post-hoc placement search.
Fix T5 by the metadata/independent identity-label rule before any detector result; it remains unedited. Missing independent semantic/identity labels mean the endpoint is unavailable.
One T4 and one T5 challenge per source/action are a narrow finite challenge, not comprehensive attacker coverage. Additional pair construction/annotation cost is not measured by the compute proxy.
Known cells: R0=SD1.5 DDIM img2img strength .2 and R1=SDXL img2img strength .1, with the retained native pipeline settings frozen by revision before fitting.
Known-cell regeneration seeds are 0,1,2. Source-majority means at least two of these three outcomes; absent/failed outcomes are non-success, never replaced.
Optimization-excluded cell: native Kandinsky 3 img2img strength .2, seeds 0,1,2, frozen before fitting with model revision, scheduler, step count, CFG, resolution and fixed empty prompts copied from the retained native K3 recipe.
No K3 output, score, timing reward, descriptor or oracle table is available to any allocator, stopping rule, model selection or fitting stage.
The first 48-group table does not run K3. Only a later sealed evaluation runs it; K3 is excluded from optimization, but is historically known to the project, not a newly discovered family.
If the pinned native recipe/assets cannot be recovered without reading forbidden data, return DESIGN_UNAVAILABLE; do not pick a more convenient family/cell after seeing outcomes.
Acquisition/randomization seeds are 101,202,303; regeneration seeds are separate and never count as independent fitted policies.
No writer restart search is allowed. Register an immutable source/action-to-writer RNG mapping before acquisition if the implementation contains any stochastic operation.

## 4. Allocators, classical controls and matched access

The first screen evaluates all eight entries below, with three disclosed acquisition seeds on the same masked table; this is replay, not three paid studies.

| Entry | Frozen acquisition rule and tuning |
|---|---|
| B: bandit-style candidate | Gaussian linear posterior for each action; sample 64 posterior draws, identify pairs disagreeing about the best action on the permitted source pool, buy maximal sampled disagreement reduction per incremental cost. |
| F: balanced factorial | Fixed hash-ordered round robin over sources and four actions, equal counts before the next round. |
| N: stratified/Neyman | Four luminance-variance quartiles fixed from fitting contexts; start balanced, then allocate proportional to observed action-difference standard deviation per square-root cost. |
| E: classical Bayesian design | Same linear posterior as B; enumerate admissible purchases and choose maximum expected integrated action-difference variance reduction per cost. |
| I: adaptive importance | Sample by fitted action-difference uncertainty with positive probabilities; use the recorded inverse-probability weights and a declared reward model, not reconstructed historical propensities. |
| G: greedy active learning | Buy the highest predicted uncertainty of the best-versus-runner-up difference per cost, with the same posterior/representation. |
| U: uniform random | Uniformly sample remaining admissible source/action bundles, with the same caching and paid feedback. |
| H: halving | Four global configurations, fixed 4/8/16/24-source rungs; halve by mean `(C+J)/2`, then continue the survivor. Evaluate its global-arm objective separately. |

B/E/G use posterior noise floors {.05,.2}; B/I/G use epsilon in {.1,.25}, retaining an epsilon-uniform component over every remaining admissible purchase.
Before any new outcome, a numerical readiness freeze must specify posterior priors, C/J scalarization and covariance, the exact disagreement/variance-reduction acquisition calculation, and all ties and RNG mappings identically where shared across B/E/G. These unresolved implementation details are not free tuning on the screen. Without that freeze the stage is DESIGN_NOT_READY; this dossier does not supply an executable algorithm or server code.
For N use an epsilon-uniform floor .1; deterministic controls record exact selection rules, not fictitious positive propensities.
The first acquisition is four hash-first sources × all four actions. Each purchased bundle returns both known cells × three seeds plus clean/negative rows; cache that mark within that allocator only.
Thus this narrow implementation allocates source/configuration bundles, not arbitrary individual cheap rows. Changing bundle granularity requires a separately priced design.
At checkpoints 16/32/64/96 purchased bundles, evaluate selection-group regret; choose settings by smallest total cost meeting the same selection criterion, else by lowest regret at the cap.
Selection criterion: mean oracle regret ≤.05 for both known-cell C and J, with selected actions unchanged on at least 11/12 selection groups since the preceding checkpoint; no stopping at the first checkpoint.
The 48-group screen caps all allocator/downstream fitting, tuning and analysis at 2 billed instance-hours, with equal family caps and identical grids; actual runtime is logged.
If a serious classical implementation cannot fit that allowance, return RESOURCE_STOP or reduce the claim before running; do not substitute an untuned weak control.
Supervised full-information fitting and best fixed action are mandatory reference policies using the complete fit table; they are not free counterfactual algorithms.
No method sees sealed check outcomes during fitting, stopping or champion choice. Missing outcomes are preserved and training/attempt/failure costs count.

## 5. Endpoints, eligibility and first-screen rule

C is decoded content-compatible acceptance; J adds exact original q, not exact h. Report exact h and joint q/h separately, without changing the primary endpoints.
For source s/action a, `u_C` and `u_J` are the average of the two known-cell source-majority indicators; K3 has its own single-cell utility.
The oracle utility is the maximum over the frozen finite menu, with quality/security-ineligible outcomes scored zero; it is a paid evaluation reference, never a deployment policy.
Regret is oracle utility minus the selected action utility, separately for C and J. The oracle may differ by endpoint; disclose that it is an upper bound, not one simultaneously realizable policy.
Strict quality on every final deployed mark is PSNR>35, SSIM>.9, LPIPS<.1 relative to its original, measured on saved RGB8. No mean-quality substitute is allowed.
Report every attempted C0, wrong-owner, T4 and T5 outcome, the exact false donor attribution/binding predicates and missingness. J's absence of an original payload cannot make a negative automatically pass.
Any selected final mark's quality failure, new finite negative acceptance, incomplete negative block or unresolved label prevents a success verdict; no security failure trades against compute saving.
Probe/configuration failures remain in the menu/table as failures; they are not replaced. Their cost counts even if the final selector avoids them.
Twelve check groups cannot certify rare false-acceptance rates, broad security preservation or a .05 population regret margin.
First-screen continuation requires all needed rows/labels, check-table J oracle headroom over the selection-chosen fixed action of at least 1/12, and a fitted selector recovering at least 1/24 check J utility without lower C.
Also require B's masked-reveal cost to be below the strongest tuned classical rule at matched observed regret after adding fit cost. This is exploratory triage, not a significance or online-savings claim.
Failing these fixed criteria closes this menu for C18; saturation does not permit new cells, schedules or convenient replacements. A sparse pilot null is not proof that every allocator fails.
Choose the classical champion before unsealing the first-screen check: among controls meeting the same selection regret/stability criterion, minimize full acquisition+fit cost; if none meets it, minimize the larger C/J selection regret, then cost, then fixed entry order F,N,E,I,G,H,supervised. The full-information supervised option pays its actual acquisition cost.
The larger stage uses that frozen tuned champion. The eventual claim names this finite-portfolio selection; it does not claim superiority to every possible non-RL method.

## 6. First-screen inventory and hard limit

SOURCE cost anchors from [ledger L](../ideas/sheets-systems.md): `w=122s`, `f=2.19–3.63s`, extra read `r=1.4s`, clean/two-owner/quality row `3.05s`; historical rental rate `.551 USD/h`.
The 122 seconds is derived device-equivalent throughput from 732-second six-shard latency; it is not a measured isolated kernel or measured new-configuration runtime.
For n groups, k actions, c cells, define `p=3cnk`, `z=3cn`; core hours are `[122nk+f(p+z)+1.4p+3.05(3nk)]/3600`.
The final term includes nk clean and 2nk T4/T5 rows. Add 20% attempted-call/runtime reserve, then separately listed setup/features/fitting.

| First table | Count / accounting |
|---|---:|
| Writes / clean checks | 192 /192 |
| Marked C1 native / C0 native | 1,152 /288 |
| Extra wrong-owner reads / T4+T5 pairs | 1,152 /384 |
| Core | 8.319–8.895 h |
| Upper core×1.2 +1 h setup +2 h complete fitting/replay | **13.674 h; $7.53** |
| Hard all-in compute stop | **20 h; $11.02** at the historical rate |

All 192 writes and table rows are purchased even when a replay hides them. Report masked reveal cost separately from actual total cost; there are no realized GPU-hour savings here.
The 20-hour stop also covers unmeasured feature/preparation/pair work that consumes billed instance time. Human/licensing work and storage/network charges are separately unpriced dependencies.

## 7. Conditional prospective validation, not an authorized extension

Only after a successful first screen and a new user decision, acquire 266 further groups: three disjoint trajectory cohorts of 48 fit+12 selection groups, plus 86 common sealed check groups.
These are disjoint from all 48 screen groups and all old/protected pools; with the screen there are 314 target groups, plus the two fixed auxiliary images per group.
Run B, the frozen classical champion and U separately in each trajectory. Each has its own actual paid acquisitions, cache, fits and RNG seed; one method cannot read another's outcomes.
The three trajectories use seeds 101/202/303 and disjoint fitting/selection groups. They are three independent acquisition histories, not three permutations of one purchased master table.
Extend acquisition checkpoints to 16/32/64/96/128/192 bundles; apply the same selection stopping rule. Maximum per method/trajectory is the complete 48×4 known-cell table.
The selection tables are complete, separately paid 12×4 tables per trajectory and common to the three methods only for their declared tuning/stopping role.
Freeze every selector, stopping time, classical champion and outcome predicate before any 86-group check result exists or is revealed.
Deployment workload is fixed at exactly 86 new-source marking decisions per method per trajectory, hence 258 decisions for each allocator across its three runs; no hypothetical future volume amortizes training.
Actually execute the chosen action on each deployment source and all three cells, including K3. Keep each method/trajectory's deployment cost; do not replace actual deployment with a free auditor lookup.
An independent auditor also buys a complete 86×4×3-cell reference table, keeps it sealed until all choices are frozen, and computes oracle regret and all alternatives afterward.
The complete reference has its own writes even when a deployed configuration matches; this conservative inventory prevents free counterfactuals. A future symmetric cache-sharing amendment must be fixed before outcomes and cannot claim replicated physical writes it did not perform.
The auditor's complete table is one common validation instrument, not three independent source samples. The 86 source groups, not seed-level rows, are the precision units.
Full-information supervised and fixed-action benchmarks are reported from the screen/paid audit with their access limitations; a new fully trained competing selector needs separately paid fitting, deployment and an amended inventory.
This narrower trial tests B against the preselected tuned champion and random allocation; superiority over all named classical controls would require extra prospective arms and simultaneous inference.

## 8. Precision, multiplicity and verdicts

Four co-primary regret contrasts are fixed: C-known, J-known, C-K3, J-K3, comparing B with the preselected classical champion.
For each check source and endpoint, let `D_s=1` if B has greater regret than the champion in **any** of the three frozen trajectories, else 0; since utilities lie in [0,1], each trajectory's mean harmful regret difference is bounded above by `P(D=1)`.
Use a one-sided Clopper–Pearson upper bound with alpha=.05/4=.0125 for each endpoint. Success needs all four upper bounds ≤.05; no check-based champion selection is allowed.
DERIVED: with n=86 and zero harmful groups, the upper bound is `1-.0125^(1/86)=.04968`; with n=12 it is `.30592`. At n=86, one or more harmful groups cannot pass this fixed conservative rule.
This bound requires independent, identically distributed source-level Bernoulli indicators with a common endpoint probability under a justified source sampling model, conditional on all frozen fitted policies (or a separately justified valid sampling design). Exchangeability alone is insufficient. If that model is unjustified, give finite-cohort results only and do not award the inferential regret gate.
The deterministic acquisition ordering supplies reproducibility, not a proof of iid sampling; record this assumption and the eligible finite population before claiming population coverage.
Report absolute oracle regret, per-cell utilities, all three seeds and random/fixed references descriptively with source-level intervals. They are not additional uncorrected superiority tests.
The max-over-three construction addresses these three particular trained policies; it does not estimate general training-seed variance or make three runs a large replication sample.
Early negative/resource stopping is allowed, but there is no early positive stop, no sample increase after harmful checks, and no switch of endpoint or comparator.
The exact zero-harm rule is sufficient, not necessary; it is not an information-theoretic sample-size lower bound. For comparison, a chosen Hoeffding upper bound needs 877 zero-mean [0,1] units for .05 at alpha .0125, showing how conservative bound choice changes cost.
If precision, full controls or labels cannot be achieved within the 200-hour total ceiling, record RESOURCE_STOP/INCONCLUSIVE rather than “no allocator can work.” A failure of the fixed scientific gate is reported separately.
Multiplicity for searching the initial eight allocators/menu is handled by independent sealed validation of the frozen B-versus-champion comparison; first-screen results remain exploratory and are not pooled as confirmation.
No cross-candidate C03/C18 family-wide positive claim follows without a separately declared combined analysis; their benefit events are different.

## 9. Full costs, savings denominator and feasibility gate

The following is a conservative maximum inventory, not promised consumption; the same anchors, reserve and accounting apply to every method.

| Prospective component | Inventory | Upper hours with 20% reserve |
|---|---|---:|
| Nine independent acquisition trajectories | 9×L48×4, two cells: 1,728 writes | 96.062 |
| Three selection tables | 3×L12×4, two cells: 144 writes | 8.005 |
| Nine actual deployments | 9×L86×1, three cells: 774 writes | 53.945 |
| One sealed full reference | L86×4, three cells: 344 writes | 21.166 |
| Future setup / fitting+features+analysis caps | 1 h /8 h; fitting 2 h per allocator over its three runs, shared work 2 h | 9.000 |
| Prior first-screen estimate included | All initial table/fitting cost, including failures | 13.674 |
| Whole campaign upper planning inventory | 3,182 writes including screen; no extra confirmation cohort | **201.853 h /$111.22** |

Prospective rows alone contain 2,990 writes, 21,294 C1 native outputs, 10,548 C0 native outputs, 21,294 extra wrong-owner reads, 5,980 T4/T5 pairs and 2,990 clean checks.
Add the first-screen counts above; unmeasured overrun can only increase the required bill. If the first screen uses its whole 20-hour cap, this maximum rises to 208.179 hours.
For each allocator, cold-start total includes the **entire** first screen, selection tables, common audit and shared setup/features/analysis, plus its own three acquisition/fitting/deployment runs.
Shared validation is charged equally in each decision denominator, never subtracted because it is common and never divided by the number of competitors to manufacture amortization.
Savings is `1-H_B/H_champion`, at the fixed 258-decision workload and matched regret/eligibility target. The physical campaign bill counts shared components once and every distinct trajectory; report both ledgers.
With the quoted maxima, common cost is 45.845 h; own deployment+fit is 19.982 h; champion acquisition at the full cap is 32.021 h, giving 97.848 h cold-start total.
DERIVED: attaining 25% saving in that favorable full-cap champion case requires B acquisition ≤7.559 h across all three runs, assuming equal other costs. If the champion stops earlier, the requirement is stricter and may be impossible.
A 24-fit-group version would have too little avoidable acquisition cost relative to these same audit/deployment costs; it cannot earn 25% at this workload even if B acquisition were free. Hence the larger 48-fit-group feasibility envelope is explicit.
Actual prospective savings can occur only if fewer acquisitions are genuinely executed; replay reveal counts cannot substitute. Report all three realized cost ratios and the pooled ratio, without claiming a precise population mean saving from three trajectories.
Before any larger-stage acquisition, use future measured write/feedback/fitting costs to reserve the complete sealed-check/deployment bill and enforce a cumulative stop before 200 hours ($110.20 historically).
If the remaining affordable acquisition allowance cannot meet the frozen stopping and inference rules, do not start/continue that stage: RESOURCE_STOP. The 201.853-hour maximum already exceeds 200 before unpriced engineering/labels, so this is not presently an executable guaranteed-completion campaign.
Conversely, the exact n=86 rule and possible early acquisition stopping mean this arithmetic does not prove every valid 200-hour study impossible. No full-campaign success probability is refuted by this accounting.

## 10. F6 branches and claim boundary

F6 GO: keep its approved outcome separate; consider only the C18 first screen if experiment efficiency is useful. Do not substitute F6 writes or claim C18 improved the successful defense.
F6 FAIL: the same cheap headroom screen can test whether this non-F6 menu supports useful decisions; saturation/headroom failure closes it without RL retraining around the failed F6 result.
F6 RESOURCE_STOP: F6's science remains unknown. Resolve whether the resource cause also affects C18 before authorizing even the first screen; do not treat resource exhaustion as efficacy failure.
In every branch, DATA_UNAVAILABLE, DESIGN_UNAVAILABLE, incomplete security labels or the measured cost gate can stop C18. No F6 outcome has been inspected for this document.
SOURCE: [WP6](../06-probabilities.md) gives C18 OWN_SUCCESS medians 13%/8.5%/10.5% and R07 future acceptance 18%/18%/17% for GO/FAIL/RESOURCE_STOP.
Those subjective uncalibrated forecasts describe the earlier broad campaign, not the exact step-size menu, n=86 rule or inventory specified here. They neither authorize spending nor predict this screen precisely.
A successful result supports allocation efficiency for the frozen source/menu/workload contract; a useful null separates predictable difficulty from useful action differences. Neither is a new watermark, a cryptographic guarantee or a general RL theorem.
