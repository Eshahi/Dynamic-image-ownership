# WP2 source-inspection contract

Read BRIEF.md and these rules. Research only; write only your assigned single Markdown file under this folder. No code/models/images/datasets downloaded, no installs, science, SSH, paid compute or F6 outcomes. No need to reread AGENTS or STATE; root already read authoritative STATE once. PHASE_B_JOURNALS=off. No run data needed for literature.

Use primary sources. Search live, then open full text and inspect substantive method AND evaluation sections (theory papers: assumptions/theorems and implications). Search snippets, abstracts, bibliographic pages and another paper's description do not count. Use HTML/PDF web reading, not local scientific libraries. Existing local paper cards are leads, never a substitute for opening the source. Papers unavailable after reasonable alternative primary/author access stay UNINSPECTED. Do not fabricate metadata, locators or effects. No model or other scientific work runs here.

Output one file with (1) query log; (2) inspected cards; (3) inaccessible/duplicate/irrelevant leads; (4) cluster-specific synthesis and exact counts. No git mutations. Root consolidates logs/cards and checks coverage.

## Query log

Every actual query gets unique ID, exact query string, tool/access route, index searched, primary result URLs, discovered new papers and failures. A web search with site/domain restriction is an **indirect index search**; label it, do not pretend to have used a site's native search. General web discovery is separately labelled. At least four distinct scholarly index contents (arXiv, OpenReview, CVF, IEEE Xplore, ACM DL, DBLP, Semantic Scholar etc.) should be searched per cluster when feasible. Record empty/blocked searches honestly. More than one query differing only punctuation does not count as distinct. Root may add native-index verification. Queries are counted only if actually issued.

Aim for12 distinct meaningful queries/cluster across >=4 scholarly indexes, so an evidence-based exhaustion assessment is possible. Do not call a cluster exhausted merely because time/tokens are short. If below its card floor, identify the final searches that found no new eligible accessible work, enumerate inaccessible relevant leads, and explain limits. Adjacent work may count only if the cluster explicitly covers that topic; do not fill a watermark-specific cluster with generic attacks or generative-text RL.

## Every inspected card

Use ID `Cxx-NN`, unique within the assigned range, title, full author metadata as available (first author et al. with linked canonical author list if long), venue/year (preprint if not verified), DOI null if unknown, canonical URL, access date2026-10-30, inspected version and exact sections/table/equation locators. State `FULL_TEXT_INSPECTED_ONLINE` (or local artifact/hash if actually inspected locally); this is not a claim of publisher-final verification. Respect source word limits: keep source-derived paraphrase compact, normally <=180 words per paper; separate brief project-specific inference.

Required substantive fields: setting (post-hoc/generation-time; image/text/other), RL class (R-full/R-bandit/R-game or explicitly comparator-not-RL), state/action/reward (or N/A for non-RL), comparator used, effect size with exact table/section or explicitly no comparable numerical effect, pre-emption, limits. Distinguish SOURCE paper report, DERIVED calculation and JUDGMENT project inference. Never turn published bit accuracy into our C/J acceptance, statistical significance or T4/T5 guarantee. Record negative evidence and costs where inspected. A paper cannot count twice within one cluster; root will disclose overlap across clusters.

For every numerical claim, give table/figure/section and the measured endpoint, setting, baseline and direction. If no reliable numeric comparison can be extracted, explicitly say why; do not infer an effect from an abstract. If authors compare only weak methods, say so. Inspect at least one actual evaluation detail even when no effect is transportable.

## Synthesis question

What exactly does this cluster say about RL beating its simplest strong non-RL alternative under an equal total budget for post-hoc content-bound image watermarking under diffusion regeneration? Separate an occupied ingredient from an identical task/construction. No absence/first-ever claim from limited retrieval. Flag links to the user's P1/P2/P3 readings, unseen-family transfer, strict quality and T3/T4/T5.

The literature-synthesis skill's local-artifact verification and generic synthesis command are not asserted complete by online cards. The user requires web full-text inspection and only permits stdlib saved-data/toy execution; its session-specific structure and execution boundaries control. Online inspection provenance remains explicit rather than claiming a locally verified package.
