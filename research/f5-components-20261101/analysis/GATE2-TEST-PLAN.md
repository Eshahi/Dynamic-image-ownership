# Fixed Gate 2 tests, before any B EVALUATE computation

SOURCE: Claude's [Gate 2 ruling R5](../gates/GATE-2-RULING.md) fixes the rules; this file operationalizes them without tuning. G2-A/B code is committed before any EVALUATE outcome. CPU, saved development only, CUDA_VISIBLE_DEVICES=-1, PHASE_B_JOURNALS=off, each invocation <540 seconds, at most 8 workers. No writer or diffusion calls. Preserve all outcomes, missingness and failures. Tests are exploratory on already consumed development data; the old T4 event was visible to the judge before the rule and is not fresh confirmation.

## G2-A

DERIVED: For each tier use decoded score and word, hard Hamming distance to suspect q or h, production decoding-error model, and corrected distance clamp `(d-32e)/(1-2e)`. Accept iff score >= `_threshold(5e-7, sum(comb(32,j),j=0..9))` (7.7791 rounded) and corrected <=6. Use full-precision threshold and distance, not rounded display values. Nonpositive denominator is a nonaccept; such low scores cannot pass threshold. The analytic monotonicity proof and boundary assertion establish effective radius <10 for every higher score. No recomputed route. Frozen semantic.read && !semantic.content_match vetoes only Bi; Bs is unvetoed. B=Bs OR(Bi&&!veto). Frozen C/J unchanged; C OR B separate.

MEASURED plan: all 22 existing study/cells, both methods, DESIGN/EVALUATE/ALL, expected seeds including missing calls as failures and missingness upper bounds. Source majority is >=2/3, single-image cells >=1/1. G2-A primary gains are Stage2 F5 foreign native cells only: SDXL .1/.2/.4,K3 .2, 120 EVALUATE source-cells, not overlapping Phase-A totals. Report both studies separately.

JUDGMENT fixed promotion kills (any one suffices): <5 foreign gains over C/120; any F5 C-positive loss on SD1.5 .1/.2; any B C0/wrong-owner acceptance in any saved call (both halves, methods, pixel panels); any new B acceptance over C on saved F5 T4 EVALUATE; any new acceptance over the frozen-style decoded>=8.2593/corrected<=6 comparator at the same reference center on different-content T5 EVALUATE directions. No rescue threshold/radius/veto after outcomes.

DERIVED T5 implementation: retain the existing 66 unordered pair records and both directions, with DESIGN/EVALUATE only when both members share the split and CROSS otherwise. The previous T5 diagnostic concerns semantic-word scores at the other image's q center: compare new Bs to frozen-style semantic acceptance exactly there. Also report the instance decoded word at reference h, both tier comparisons and combined diagnostic, retaining the saved table routing and explicitly marking reference-assisted side information. Any new contributing tier acceptance relative to its same-center frozen-style comparison is conservatively included in the kill. This does not recompute the instance table under a new reference q or claim native blind transplantation. Categories uncertain/same remain present but do not enter the different-content kill. Frozen C/J on the suspect remain separate. This scope is fixed before outcomes and reviewer-visible.

## G2-B

SOURCE: exact historical `three_threat_protocol.residual_transfer`: recipient C0 plus scale*(donor saved F5 C1-C0), clip then round to RGB8. Stage2 sorted S60, odd-position 30 EVALUATE recipients, first8 even-position DESIGN donors, scales .5/1.0: 480 fixed units, no pair selection. CPU F5 reader/CLIP7 only. Store PSNR and SSIM against recipient for all units; LPIPS only if existing weights load with no download, else MISSING. Save PNG only for an acceptance by a reported endpoint, retaining which endpoint accepted.

JUDGMENT fixed kill: any B && !C at strict PSNR>35 and SSIM>.9 kills B promotion. Report C,O,O_U,Bs,Bi,B, all and quality-qualified, by donor and recipient. LPIPS is descriptive and does not alter the fixed kill. Zero/480 would give 1-.05**(1/480) approximately .00622 under independent Bernoulli trials; shared donors/recipients invalidate that as a population confidence bound. No human visibility verdict is supplied.

## G2-C

MEASURED plan: clean C0 q/h for all60 S60, all1770 unordered pairs:435 DESIGN,435 EVALUATE,900 CROSS. Mean, minimum, counts<=6/8/9 and exact uniform32-bit ball shares. Pair dependence explicit. No kill rule; state empirical collision concentration and its limits, not a universal transplant acceptance theorem or a Shannon entropy estimate.

## Provenance / stopping

SOURCE: scripts, plan, input inventories/hashes, commands, git revision and elapsed seconds accompany outputs. Pure-logic tests cover threshold boundaries, veto, recomputed-only exclusion and fixed ball proof before data execution. Stop after fixed batches and reductions; do not run further variants. G2-A and G2-B together determine K09 per R5: survives => proposed IMPROVE; killed => KEEP, no rescue.
