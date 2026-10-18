# Q1 research dossier: research-only session (brief, 2026-10-18)

Written by Claude at the user's request. The user asked, verbatim:

> for the next recommended hours(at least 7), I want to setup the codex to gather and also research for enhancing and move forward to make the thesis a Q1 nominee ( without any experiment).

You (Codex) are the lead researcher for this session. A supervisor script started you, keeps you going until the session deadline and resumes you if a turn ends early. Nobody will answer questions during the run. When something needs the user or the supervisor (professor), record it under "Decisions for the user" in `PROGRESS.md`, state the default you assumed, and continue.

The session deadline is given in your first prompt and repeated in every supervisor message. Write it at the top of `PROGRESS.md` in WP0.

## 1. Hard rules: no experiments

This session produces research, analysis and writing only. The user excluded experiments.

**Not allowed:**
- generating, marking, regenerating, attacking, detecting or scoring images;
- descriptor extraction, calibration, training, fine-tuning, benchmarking or timing runs;
- any GPU use; any use of `.thesis-build/a6-science-venv` or any interpreter with torch, diffusers, numpy or PIL;
- new dev runs, rehearsals, manifests or approvals;
- downloading images, datasets, model weights or code repositories, and installing packages (`pip`, `conda`, `npm`, installers);
- opening held-out pixels. Held-out result files (journals, `endpoints.json`, reports) may be read, because those runs are finished.

**Allowed:**
- reading any file in the main checkout and in every worktree;
- web search, and reading papers, standards, model cards and journal pages (see section 2 for downloads);
- stdlib Python only, with `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/venv/Scripts/python.exe`, to count or aggregate existing result files (JSON, JSONL, CSV) and to compute confidence bounds from existing counts;
- hashing local files, for example comparing the SHA-256 of two pinned model files;
- writing Markdown, CSV, BibTeX and JSON inside `research/q1-dossier-20261018/` of this worktree;
- committing and pushing this branch, and updating MAIN `thesis-runs/d916749c/STATE.md` at the end.

**Technical guard.** The supervisor hides CUDA (`CUDA_VISIBLE_DEVICES=-1`). It also kills any child process that uses the science interpreter, runs an experiment script, or runs Python for more than 15 minutes, and it logs the event. Do not work around the guard. If you believe a computation or experiment is essential, write it into the future-experiment plan (WP6) with its design, cost and the claim it would unlock.

**Protected files (unchanged rules):** never edit the proposal (`inputs/`, the .docx), `research/claims.csv`, the source plan, `THESIS_GUIDE_OFFLINE.html`, retained run outputs under `.thesis-build/*runs*` or `.thesis-build/registry-package/artifacts/`, or other agents' files. Never merge, rebase or check out other branches, and never write into other worktrees.

## 2. Research integrity rules

- **Primary sources.** Prefer the paper itself (arXiv HTML, CVF, OpenReview, publisher page, official standard), not blogs or summaries. Record the version you read (arXiv vN, venue version).
- **Verification level for every source:** `V2` = method and experiment sections actually read; `V1` = abstract or metadata only; `V0` = known to exist but not accessed. Only V2 sources may support a novelty or comparison statement. Never cite what you have not opened.
- **Never invent** DOIs, pages, venues, numbers, quotes, journal quartiles or impact factors. If you cannot verify something, write `UNVERIFIED` and the reason.
- **Search log.** Record every search (date, engine or API, query, number of useful hits) in the cluster's `search-log.md`. Any "no prior work does X" statement must name the search that supports it and be phrased as "we found no ..." with the date.
- **Copyright.** Store downloaded full texts only in the cache folder `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/` (gitignored, total at most 3 GB, PDF or HTML papers only). Commit paraphrased cards, not full texts. Quotations are at most 25 words, in quotation marks, with a locator. Do not use shadow libraries or paywall bypasses.
- **Useful free APIs** (use `curl.exe`, not the PowerShell `curl` alias; respect rate limits, about 1 request per second): arXiv API `http://export.arxiv.org/api/query?search_query=...`; arXiv HTML `https://arxiv.org/html/<id>`; Semantic Scholar `https://api.semanticscholar.org/graph/v1/paper/search?query=...&fields=title,year,venue,externalIds,citationCount`; OpenAlex `https://api.openalex.org/works?search=...`; Crossref `https://api.crossref.org/works?query.bibliographic=...`; DBLP `https://dblp.org/search/publ/api?q=...&format=json`; OpenReview `https://api2.openreview.net/notes/search?term=...`; SCImago `https://www.scimagojr.com/journalsearch.php?q=<name or ISSN>`. Do not put the user's e-mail or any personal data in URLs.
- **Numbers about this thesis** come only from the evidence ledger (WP1), each with an `EV-` ID.
- **Language.** All files in English. Only your final message (section 9) is in Persian.

## 3. Where the evidence is

Paths are absolute unless they start with `research/`, which means this worktree (`C:/Users/Soroush/.codex/worktrees/codex-q1-research`, branch `codex/q1-research-20261018`, based on `codex/journal-upgrade-plan` at `c58a9ca`).

- **MAIN checkout:** `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5`. Its `thesis-runs/d916749c/STATE.md` (updated by Claude on 2026-10-18) is authoritative. Read it once at the start.
- **Claude's registry branch (newest results; read-only):** worktree `C:/Users/Soroush/.codex/worktrees/claude-registry-research`, branch `claude/registry-research` at `7a2b904`. These files exist only there:
  - `research/claude-registry-research-20261014.md` (registry idea, grounding, CPU screen);
  - `research/claude-round3-results-20261017.md` and `research/claude-round3-frozen-20261017.json` (frozen two-factor rule, distance definition of a different image);
  - `research/claude-registry-confirmation-plan-20261017.md` (approved held-out plan and endpoints E1-E3);
  - `research/claude-registry-heldout-gap-note-20261017.md` (approved pre-result reading of the gaps);
  - `research/claude-registry-heldout-results-20261018.md` (held-out results and the user's decision);
  - `scripts/claude_verify_heldout_registry.py` (Claude's verifier; it loads images, so do not run it).
- **Held-out registry run (finished):** MAIN `.thesis-build/registry-package/artifacts/M1b-test/registry-div2k300-confirm-01/` (`metrics/endpoints.json`, `manifest.json`, `execution-manifest.json`, `outputs/`, `logs/`). Manifest and package: MAIN `.thesis-build/registry-package/registry-confirmation-manifest.json`, `research/registry-confirmation/`.
- **In this worktree:**
  - method: `research/f5-encoder-amplified-latent.md`, `research/threat-model.md`, `research/research-contract.md`, `research/scope-guard.md`;
  - F5 confirmatory run: `research/m2-coco512-results.md`, `research/m2-independent-review.md`;
  - journal round (Codex, 2026-10-09 to 10-17): `research/journal-upgrade-20261009/` (start with `plan.md`, `article-claim-map.md`, `h2-article-viability-decision.md`, `literature-comparison.md`, `e3-s1-m2-results.md`, `e3-s1-m2-sensitivity.md`, `unseen-regenerator-results.md`, `registry-verification-results.md`);
  - literature already collected: `research/literature/**` (cards, matrices, bib files, inspected HTML) and `research/literature/journal-upgrade-20261009/synthesis/findings.md`;
  - thesis draft material: `thesis/` (outline, chapters 05-06, `references.bib`, claim inventory, tables, one figure);
  - proposal (Persian, read-only): `inputs/proposal-text.md`; objectives and questions in English in `research/claims.csv` (OBJ-01..04, RQ-01..04, HYP-01..04).
- **Interpreters:** stdlib only, `.thesis-build/venv/Scripts/python.exe` in MAIN.

## 4. Where the thesis stands (starting summary; verify in WP1)

**Thesis:** "Dynamic Image Ownership With Robust Neural Watermarking" (master's thesis). The defended threats are T3 regeneration, T4 copy-paste forgery and T5 semantic collision only (`research/threat-model.md`). Do not plan work on other attacks (JPEG, crops, colour changes); at most mention them in one line as an unweighted limitation.

**Method line, F5 r2 ("encoder-amplified latent carrier").** It is an image-domain writer. It optimizes RGB pixels by gradient ascent through the SD1.5 VAE encoder toward a keyed DCT pattern in the 64x64 latent (robust tier, about 32 reliable bits), plus a fragile instance tier and a CLIP-derived semantic code. The idea comes from the removal bound of Zhao et al. (arXiv 2306.01953): that bound depends on the attacker encoder's local Lipschitz constant along the mark, and the SD VAE encoder is not robust. F5 is not the proposal's latent-insertion method (OBJ-02, RQ-02, HYP-02 stay open) and not a lightweight DCT detector (OBJ-03, RQ-03, HYP-03 stay open).

**Confirmatory (held-out) results:**
1. **F5 r2 versus v5 r3 on 300 MS-COCO test groups** (2026-10-07; `research/m2-coco512-results.md`, review verdict ACCEPT WITH CORRECTIONS).
   - Clean correct-owner `both_match` 299/300; unmarked negatives 0/300.
   - T3 on 30 sources (descriptive): source-majority semantic detection F5 versus v5 is 30/22 at img2img strength .2 and 21/5 at .4.
   - T4 0/29 and T5 0/27 false attributions; units are small, so zero errors give upper bounds near 10%.
2. **E3-S1 versus v5 on 300 COCO groups** (2026-10-13; `e3-s1-m2-results.md`, `e3-s1-m2-sensitivity.md`). The headline gain at .1 is a clean exact-H gate artifact; the real gain is at .2 and in exact payload recovery. E3 is not the thesis method: F5 was selected on 2026-10-16 by a fixed rule (`unseen-regenerator-results.md`).
3. **Registry verification on 300 DIV2K test photographs plus 60 Tears of Steel look-alike pairs** (2026-10-18). The watermark acts as an owner-and-record pointer. A trusted registry holds continuous descriptors: D1, native fine features, and B1, a 32x32 layout. The two-factor rule was frozen before the data existed.
   - E1, registry attribution of regenerations at strength .2: 277/300 on SD1.5 and 280/300 on SD2.1-base (one-sided 95% Clopper-Pearson lower bounds .893 and .905). Pass.
   - E2: zero false accepts on 3,408,600 unrelated pairs and 594 copy-paste transfers. But 3 of 45 clearly different real look-alikes (16.9-17.7 dB grey PSNR, 2 of 16 shots) were accepted. Fail.
   - E3: zero wrong-owner attributions after regenerate-and-enroll, in all 8 cells. Fingerprint-only matching made up to 75 wrong-owner calls of about 294.
   - F5 could not mark 3/300 photos; SD1.5's safety checker blocked 50 regenerations.
   - The user decided on 2026-10-18 to report the result as it is: E1 and E3 confirmed, E2 a stated limitation. No threshold or definition may be changed on this data.
   - The independent M2 review of this run is still pending; it is part of WP1.

**Development evidence:** unseen-regenerator transfer on SD2.1-base (24 sources; E3 and F5 both 24/24 at .2); registry development rounds (step 2 negative, 30/40 and 32/40 against a 36 bar; round 3 39/40); many closed negative rounds listed in `plan.md`.

**Held-out pools already used:** MS-COCO test (all 600 groups) and DIV2K test (300). Any future confirmation needs a new pool.

**Scope rulings:**
- Dynamic ownership, ownership transfer, ledgers and rights management are product scope, not thesis scope (supervisor, 2026-10-14). Do not propose them as thesis work.
- Human visual ratings do not exist; never imply them.
- The registry is trusted detector side information; say so.
- No legal or cryptographic ownership claim.

**Earlier article assessment:** Codex judged, on 2026-10-13 to 10-17, that a mechanism-led headline was unsupported and suggested a conditional empirical article (`plan.md`, `article-claim-map.md`, `h2-article-viability-decision.md`). That assessment predates the registry held-out result. Re-assess it with the new evidence; do not simply repeat it.

## 5. Goal and definition of done

"Q1 nominee" here means: a submission-ready plan for one specific journal that is Q1 in the ranking the user's university uses, with an honest readiness verdict. Deliver:

1. a verified evidence ledger and the pending M2 review;
2. a current literature map;
3. a novelty and positioning decision;
4. a verified venue shortlist;
5. a theory and security argument;
6. reviewer simulation and a gap-closure plan: no-experiment fixes now, and a ranked future-experiment plan that is not run;
7. a manuscript blueprint with draft sections;
8. a thesis-alignment note;
9. one independent hostile review;
10. `FINAL-REPORT.md`.

The scientific result, not polish, decides readiness. If the honest answer is "not Q1-ready without experiments X and Y", say so, and make X and Y concrete and cheap.

## 6. Work packages

Allocate time in proportion to the session length, using these shares. After each package, commit, push and add a line to the `PROGRESS.md` log. Each package writes its files into `research/q1-dossier-20261018/`.

| WP | Share | Deliverable |
|---|---|---|
| WP0 Orientation | 3% | `PROGRESS.md` |
| WP1 Evidence ledger and M2 review | 12% | `01-evidence-ledger.md`, `01b-heldout-registry-m2-review.md` |
| WP2 Literature | 28% | `02-literature/` |
| WP3 Novelty and positioning | 8% | `03-novelty-positioning.md` |
| WP4 Venues | 9% | `04-venues.md` |
| WP5 Theory and security argument | 7% | `05-theory-security.md` |
| WP6 Reviewer simulation and gap-closure plan | 9% | `06-reviewer-simulation.md`, `07-gap-closure-plan.md` |
| WP7 Manuscript blueprint | 12% | `08-manuscript-blueprint.md` |
| WP8 Thesis alignment | 3% | `09-thesis-alignment.md` |
| WP9 Independent hostile review | 6% | `10-independent-review.md` |
| WP10 Final report | 3% | `FINAL-REPORT.md` |

### WP0 Orientation
- Read MAIN `STATE.md` once and this brief; skim the evidence index in section 3. Do not re-read whole long files; search or read by line range.
- Create `PROGRESS.md` with:
  - the session start time, the deadline and your model;
  - the planned start time of each package, computed from the shares;
  - a "Decisions for the user" list;
  - a "Log" section, one line per finished package (time, package, commit).
- First commit, then `git push -u origin codex/q1-research-20261018`. If the default Windows TLS backend stalls, use `git -c http.sslBackend=openssl push`.

### WP1 Evidence ledger and M2 review
- **`01-evidence-ledger.md`:** one row per number that could appear in an article. Each row gives:
  - an ID (EV-01, ...), the statement, value and denominator;
  - the unit of analysis (source, pair or seed) and the uncertainty (Clopper-Pearson, and a cluster-level reading where units are clustered);
  - the exact source file and section;
  - the evidence status: confirmatory held-out, development, exploratory or post-hoc;
  - whether you re-counted it from raw result files with stdlib Python, or took it from a reviewed report.
  - Cover F5 M2 COCO512 (including quality and cost), E3-S1 M2 with its sensitivity, unseen-regenerator transfer, the registry development rounds, the registry held-out run, and embedding and detection cost where measured.
  - End with a "may claim / may not claim" table for the article.
- **`01b-heldout-registry-m2-review.md`:** the pending independent M2 review of `registry-div2k300-confirm-01`. Act as a fresh reviewer.
  - Read the approved plan, the gap note, the results note and the manifest.
  - Re-count E1, E2 and E3 from `metrics/endpoints.json` with stdlib Python (no images, no numpy).
  - Check that the reported reading follows the pre-registered plan and the approved pre-result reading, and that no post-hoc change slipped in.
  - Give a verdict (ACCEPT, ACCEPT WITH CORRECTIONS or REJECT) and numbered findings. Do not edit Claude's files; corrections go in your review.
  - Cap this review at 40% of WP1's time; if the raw re-count is not feasible in that time, review the documents and say so.

### WP2 Literature
- **Inventory first.** Write `02-literature/existing-inventory.md`: what `research/literature/**` and `literature-comparison.md` already cover, at which verification level, and which entries are stale (for example a newer arXiv version or a published venue version). Do not redo covered papers; refresh only what is stale or decisive.
- **Clusters.** Work cluster by cluster, each in `02-literature/C<n>-<slug>/` with:
  - `search-log.md`;
  - `cards/<citekey>.md` with: citation key, title, authors, year, venue and version, URL, DOI or arXiv ID, verification level, access date, setting (existing photo or generation time), mechanism, threat model and attacker access, detector side information, payload or capacity, datasets and image counts, attacks and regenerators, key numbers with their conditions, stated limits, and relevance to this thesis (closest-to-us, competitor, threat to novelty, method idea, evaluation norm);
  - `cluster.bib` (verified entries only);
  - `synthesis.md`, at most 900 words: what is known, the closest work to ours, threats to our novelty, enhancement ideas, evaluation norms.
- Then merge into `02-literature/matrix.csv`, `02-literature/references.bib` and `02-literature/synthesis.md` (at most 2,500 words).
- **Targets:** at least 45 sources at V2 across clusters; at least 25 full cards; a V1/V0 list for the rest. Every 2025-2026 paper in C1, C3, C4 or C6 that could pre-empt our contribution must be read at V2.
- **Clusters and seeds** (seeds are starting points to verify, not facts; look for newer work, especially 2025-2026):
  - **C1, post-hoc watermarking of existing images robust to diffusion regeneration.** Watermark Anything (WAM), VINE and the W-Bench benchmark, TrustMark, InvisMark, StegaStamp, RoSteALS, ZoDiac, FreqMark, APT, GrOW, PhaseMark, MetaSeal, RAIN, and newer methods. Question: who already writes through or against a VAE encoder, and with what results under regeneration?
  - **C2, regeneration and removal attacks and benchmarks.** Zhao et al. provable removal (2306.01953), WAVES, W-Bench, CtrlRegen, UnMarker, rinsing or multi-step regeneration, diffusion purification, adaptive attacks on watermarks. Question: what attacks would a Q1 reviewer expect against an encoder-amplified mark, especially regenerators with a different autoencoder (SDXL, SD3, FLUX) and attackers who use a robustified encoder?
  - **C3, ownership ambiguity, forgery and copy attacks.** The classic invertibility (rightful-ownership) attack of Craver et al. (1998), the copy attack of Kutter et al. (2000), protocol defenses (non-invertible marks, trusted third parties, timestamps), modern forgery and spoofing of diffusion watermarks (for example Mueller et al., CVPR 2025, and single-image forging of latent-noise watermarks). Question: is "regenerate-and-enroll" a known attack under another name, and what defenses exist?
  - **C4, zero-watermarking and registration-based copyright protection.** Classic zero-watermarking with a trusted registry, deep-feature zero-watermarking from 2020 to 2026, and robustness to generative regeneration. This literature is large in Elsevier and IEEE journals and is a direct novelty threat to a registry design. State precisely how pointer plus registry differs.
  - **C5, content fingerprinting, copy detection and perceptual hashing under generative edits.** SSCD, the ISC 2021 benchmark, DINOv2 or CLIP retrieval, PDQ, pHash and NeuralHash with their collision attacks, and diffusion copy detection. Question: which descriptors or verifiers (for example local features with geometric verification) could separate same-shot look-alikes at about 17 dB, the E2 failure, while staying stable under regeneration?
  - **C6, provenance standards and hybrid watermark-plus-fingerprint systems.** C2PA 2.x soft binding and durable content credentials, Adobe TrustMark's role, SynthID-Image documentation, NIST AI 100-4, Fairoze et al. deferred storage (arXiv 2502.04901), and any paper that uses a watermark as a pointer into a database. Question: how much of our system design is already standard practice, and what is new?
  - **C7, generation-time latent watermarks (for related-work boundaries).** Tree-Ring, Gaussian Shading, PRC watermark, SEAL, WIND, RingID, ROBIN, Stable Signature, AquaLoRA, WOUAF. Mostly carded already; refresh versions and note what transfers to existing photos.
  - **C8, theory.** Removal bounds, detection theory for watermark false-positive rates, secure sketches and fuzzy extractors for noisy features, and statistics for clustered evaluation units.
  - **C9, evaluation norms in the target venues.** In recent (2024-2026) watermarking and provenance papers in the shortlisted journals: dataset sizes, metrics (TPR at fixed FPR, bit accuracy, PSNR, SSIM, LPIPS, FID), attack suites, baselines and reproducibility practice. This calibrates what reviewers will expect from 300-image held-out sets.
- **Specific question to settle (Q-VAE).** From primary sources (model cards and configs, and the SHA-256 of the local pinned VAE weight files if both exist), do SD1.5 and SD2.1-base share the same autoencoder weights? If they do, the SD2.1 result does not show transfer across autoencoders. Analyze what that means for the "unseen regenerator" claim and which regenerator a reviewer would accept as independent. Hashing local files is allowed; loading models is not.

### WP3 Novelty and positioning (`03-novelty-positioning.md`)
- List the candidate contributions supported by the ledger.
- For each, give the two or more closest prior works (V2 only), the exact difference (setting, attacker access, side information, guarantee), and a novelty-risk rating with reasons.
- Assess at least three article framings, for example:
  - A, registry-anchored attribution with a pointer watermark against regenerate-and-enroll;
  - B, a method paper on the encoder-amplified carrier;
  - C, an empirical study of where content-conditioned marks fail as ownership evidence.
  - For each: novelty, evidence sufficiency, missing experiments, venue fit and a qualitative Q1 chance.
- Recommend one primary framing and one fallback.
- Write a one-paragraph contribution statement, three or four contribution bullets, and a "must not claim" list.

### WP4 Venues (`04-venues.md`)
- At least 10 candidate journals; consider, among others, IEEE TIFS, IEEE TDSC, IEEE TIP, IEEE TCSVT, IEEE TMM, ACM TOMM, Pattern Recognition, Signal Processing, Computers and Security, JISA, Expert Systems with Applications, Engineering Applications of AI, Information Sciences, Neurocomputing and Neural Networks.
- For each journal give:
  - the quartile, with source, edition, subject category and retrieval date (SCImago is free; JCR only if publicly verifiable, otherwise UNVERIFIED);
  - a short scope quote;
  - two or three related papers it published in 2024-2026, with DOI, as evidence of fit;
  - length and format limits, review model, published decision times if any, APC and open-access options, and data and code policy;
  - fit with the recommended framing, and desk-reject risks.
- Exclude predatory or borderline outlets. Note relevant special issues.
- End with a primary journal, two backups and the reasons. Record "which ranking and edition does the university use (JCR or SCImago)?" as a user decision.

### WP5 Theory and security argument (`05-theory-security.md`)
- **Formal setting.** Roles, trusted registry, enrollment, the pointer, admissible regeneration, the distance definition of a different image (fifth percentile of strength-.2 regeneration PSNR, 18.126 dB), and T3/T4/T5 plus regenerate-and-enroll as attribution games.
- **Statements the system can support.** Correctness and soundness, with their assumptions; what E1, E2 and E3 estimate, and what they do not.
- **Bounds from existing counts.** Clopper-Pearson; cluster-aware readings; multiplicity across endpoints.
- **Pointer capacity and collisions.** For about 32 bits: collision probability against registry size, and why the two-factor record check bounds false accepts independently of pointer collisions.
- **The encoder-amplification argument and its failure modes.** Different or robustified encoders, adaptive attackers. State these as limitations and as future tests.
- No new data.

### WP6 Reviewer simulation and gap-closure plan
- **`06-reviewer-simulation.md`:** three reviewer personas: a security and forensics reviewer at TIFS level, an image-processing and machine-learning reviewer, and a statistics and reproducibility reviewer.
  - Each persona raises at least eight concrete objections.
  - Each objection gets a severity (fatal, major or minor) and a response route: W writing or framing, A desk analysis of existing data, E new experiment, S scope statement or limitation.
- **`07-gap-closure-plan.md`:**
  - (a) the no-experiment actions, ranked, each with effort and the file to change;
  - (b) a ranked future-experiment plan, NOT run. Each item gives the hypothesis, a design sketch, data needs, laptop versus rented-GPU compute estimate, kill and success criteria, and the claims it would unlock. For data needs, propose fresh held-out cohorts with licenses (metadata only; nothing downloaded), because COCO test and DIV2K test are used up.
  - (c) the minimal submission-critical set versus nice-to-have.
  - Candidates to evaluate include: external baselines under the same attacks, a regenerator with a different autoencoder, an adaptive encoder attack, larger held-out sets, a stronger look-alike verifier for E2, and the effect of the safety checker.

### WP7 Manuscript blueprint (`08-manuscript-blueprint.md`)
- Three title options and a structured abstract draft of at most 250 words. Numbers come only from the ledger, with their EV IDs.
- The contribution bullets.
- A section-by-section outline with target lengths and evidence IDs.
- A figure and table plan, with the data source for each.
- Draft prose for:
  - Related Work, about 800-1,200 words, with verified citation keys;
  - Threat Model;
  - Limitations;
  - the reproducibility, data and ethics statements.
- Cover-letter key points.
- Mark any unsupported sentence `TODO:EVIDENCE` or `TODO:CITATION`.

### WP8 Thesis alignment (`09-thesis-alignment.md`)
- Map OBJ-01..04, RQ-01..04 and HYP-01..04 to the current evidence and to the article: what the article covers, what stays open (latent insertion, lightweight DCT detector, CLIP plus pHash signature), and how to state "image-domain" versus "latent" honestly.
- List the items the supervisor must decide.

### WP9 Independent hostile review (`10-independent-review.md`)
- Spawn one fresh agent: `gpt-6-astra`, effort `xhigh`, `fork_turns: "none"`.
- Brief it to act as a Q1 associate editor plus reviewer. It reads 01-09 and the ledger and checks:
  - (i) numbers against the ledger and sources;
  - (ii) novelty claims against the V2 literature;
  - (iii) the venue choice;
  - (iv) missing items and overclaims.
- It writes its verdict and numbered findings to the file. Then you fix what is fixable and list the rest with reasons.

### WP10 Final report (`FINAL-REPORT.md`)
Use the template in section 8. Then update MAIN `thesis-runs/d916749c/STATE.md` (at most 60 lines, plain English) with the session outcome and pointers, commit, push, and end with the Persian message (section 9).

## 7. Time, checkpoints and sub-agents

- **Clock.** Check it (`Get-Date`) at the start of every package. Do not start a new package when less than 40 minutes remain: finish or trim the current one, then do WP10. If you are behind, shrink WP2's breadth first; never skip WP1, WP3, WP4 or WP10.
- **Checkpoints.** Commit and push after every package, and at least every 45 minutes. A restart of the laptop must not lose more than one package. After a context compaction, re-read `PROGRESS.md` and only the brief sections you need.
- **Commits.** Author "Codex agent" with the repository's configured e-mail and your usual co-author trailer, as in `AGENTS.md`.
- **Sub-agents.** At most 3 at a time; this session allows up to about 40 turns each for literature work.
  - Use `gpt-6-astra` at `high` for C1, C3, C4 and C6, and `gpt-6.1-sol` at `high` for the other clusters and for mechanical card or bib work.
  - Give each a self-contained brief: the cluster, these rules, its output folder, and the instruction not to commit.
  - Each writes only inside its own cluster folder; you merge and commit. Log each spawn in the `PROGRESS.md` log.
- **If you finish the core packages early**, work through the extension tier in this order, then refresh `FINAL-REPORT.md`:
  - **E1.** Full prose drafts of Introduction, Related Work, Threat Model and Method sections (`11-draft-sections.md`), using only verified citations and ledger numbers.
  - **E2.** Cross-check every BibTeX entry against Crossref, DBLP or arXiv (title, authors, year, venue, DOI), and log the mismatches.
  - **E3.** A rebuttal bank: prepared answers to the 15 most likely objections.
  - **E4.** Forward-citation sweep (2025-2026) of the five closest prior works, for scoops.
  - **E5.** Exact specifications of the five main figures: data files, fields, plot type. Specify only; do not plot.
  - **E6.** Cover letter draft, highlights and graphical-abstract description.
- **Never stop early to ask.** Missing information is work: record the gap and continue.

## 8. FINAL-REPORT.md template

The first line must be exactly `STATUS: COMPLETE`, or `STATUS: PARTIAL` followed by the missing packages.

1. **Session:** start, end, model, packages done, commits, push status.
2. **Bottom line, five sentences or fewer:** Q1 readiness now (not ready / ready after writing / ready after the named experiments), the recommended framing, the recommended journal and two backups.
3. **What the evidence supports:** the top claims with EV IDs, and what it does not support.
4. **Novelty verdict** per contribution, with the closest prior art.
5. **Top 10 actions, ranked,** no-experiment actions first, each with effort and file.
6. **Future experiments,** ranked and not run, each with cost and the claims it unlocks.
7. **Decisions for the user and the supervisor.**
8. **Risks:** scoops and possible fatal reviewer objections.
9. **What was not done, and why.**
10. **File index.**

## 9. Final message

Your final message in each turn is read by the supervisor, and the last one by the user. When the session is complete, make it a short Persian summary of at most 12 lines: the readiness verdict, the recommended framing and journal, the three most important next actions and the path of `FINAL-REPORT.md`. In intermediate turns, a one-line English status is enough.
