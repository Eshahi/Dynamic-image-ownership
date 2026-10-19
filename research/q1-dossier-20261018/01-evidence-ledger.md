# Article evidence ledger

Prepared 2026-10-18 by Codex agent. This is a read-only synthesis of completed runs. It neither changes frozen endpoints nor advances a lifecycle gate. All thesis numbers in later dossier files must cite these EV IDs. Literature-reported numbers belong in paper cards, not this ledger.

## Units, uncertainty and provenance

`H` means held-out evidence under a frozen protocol; `H-D` a descriptive endpoint within that held-out run, not a new confirmatory test; `D` development; `P` explicitly post-hoc; `A` read-only aggregation of existing measurements. A source-majority event needs at least two of three scheduled seeds. Seeds, repeated calls, records sharing a source and frames sharing a film shot are not independent sample units. Fixed, admitted cohorts are not demonstrated random population samples.

`CP(k/n)` denotes the exact binomial interval for hypothetical exchangeable independent units. The [count artifact](01c-counts-and-bounds.json) gives separate one-sided 95% lower and upper bounds and two-sided 95% intervals. These are per-cell bounds, not simultaneous confidence guarantees. On clustered panels use the source or shot count; a naive pair bound is labelled sensitivity only. Bounds on descriptive panels remain descriptive. Continuous quality/cost summaries have no prespecified uncertainty interval; no new bootstrap or experiment was run.

Verification codes: `R` = read from a previously reviewed report, not independently recounted this session; `C` = aggregated retained JSON/JSONL using permitted stdlib Python; `D-doc` = read from a development report, no independent outcome recount; `M2-C` = registry reviewer recount of saved rows/availability; `M2-S` = reviewer cross-check of saved aggregate acceptance numerators, not independent rescoring; both documented in [independent review](01b-heldout-registry-m2-review.md). Do not convert `R` or `D-doc` into a claim of raw verification. Exact artifact hashes and calculation convention for the F5 recount are in 01c. An initial cost aggregation stopped on an absent timing field; the corrected aggregation reports missing fields explicitly.

## Exact source index

All `WT` paths below resolve under `C:/Users/Soroush/.codex/worktrees/codex-q1-research/`. `MAIN` is `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/`. `CLAUDE` is `C:/Users/Soroush/.codex/worktrees/claude-registry-research/`. These aliases are exact absolute roots, not inferred locations.

| Alias | Exact source and sections/fields |
|---|---|
| F5-R | WT `research/m2-coco512-results.md`, §§1–3, 5; corrected after independent review at `e01d63c` |
| F5-J | MAIN `.thesis-build/m1b-confirm/artifacts/M1b-test/coco512-confirm-rerun-1/outputs/journal.jsonl`; `stage=embed`, `stage=clean`, `method`, `quality`, `seconds`, `detection` |
| F5-E | Same run, `metrics/endpoints.json`; SHA-256 `59d90d0f7d11aff86f11674a3c0c31061663d9212dbcfd9d739a7b724d6d36bd` in reviewed report |
| E3-R | WT `research/journal-upgrade-20261009/e3-s1-m2-results.md`, tables under primary comparison, clean coverage, negative calls and transfer sections; independent review linked there |
| E3-S | WT `research/journal-upgrade-20261009/e3-s1-m2-sensitivity.md`, Paired results and Interpretation; retained endpoint input SHA-256 `95f228c4d56f4c1089a44462a51eca3dfe5e8a010ff466ac72972af45eead80b` |
| U-R | WT `research/journal-upgrade-20261009/unseen-regenerator-results.md`, Clean construction, Source-majority endpoints, VAE comparison and Execution |
| REG-D | WT `research/journal-upgrade-20261009/registry-verification-results.md`, opening verdict, fresh primary evaluation, cost table, fresh regenerate-and-enroll and accounting |
| R3-R | CLAUDE `research/claude-round3-results-20261017.md`, Result, Verdict and User decision |
| REG-P | CLAUDE `research/claude-registry-confirmation-plan-20261017.md`, §§2–5; approved frozen definition and endpoints |
| REG-G | CLAUDE `research/claude-registry-heldout-gap-note-20261017.md`, approved pre-result reading and user decision |
| REG-R | CLAUDE `research/claude-registry-heldout-results-20261018.md`, endpoint/E3 tables, failure detail, operational facts and user decision |
| REG-E | MAIN `.thesis-build/registry-package/artifacts/M1b-test/registry-div2k300-confirm-01/metrics/endpoints.json`; exact fields and source hash in the independent review/recount |
| REG-J | Same registry run, `outputs/journal.jsonl` and `outputs/run.json`; retained artifacts, never edited |
| WAM-D | WT `research/journal-upgrade-20261009/literature-comparison.md`, Local evidence added on October 10; primary development reports linked there |

## F5 M2: earlier COCO confirmation

| ID | Statement and value/denominator | Unit and uncertainty | Evidence/source; verification |
|---|---|---|---|
| EV-01 | F5 clean correct-owner full `both_match`: 299/300; v5 300/300 | Source; F5 CP lower .984285, v5 .990064 | H; F5-R §2.1, F5-J clean C1 correct; C |
| EV-02 | F5 clean `any_found` negatives: 0/300 in each of C0 correct, C0 wrong and C1 wrong-owner cells | Source per cell; upper .009936. Not 900 independent sources | H; F5-R §§2.1,3; R |
| EV-03 | F5 PSNR >35 dB: 300/300; mean 44.488476, minimum 41.565294 dB | Source; threshold fraction CP; continuous summaries descriptive | H-D; F5-J embed quality; C |
| EV-04 | F5 SSIM >.9: 300/300; mean .983332, minimum .958678 | Source; continuous summaries descriptive | H-D; F5-J embed quality; C |
| EV-05 | F5 LPIPS <.1: 298/300; mean .02175893, maximum .10419527 | Source; lower .979164; no claim of universal quality | H-D; F5-R §2.1 and F5-J; C |
| EV-06 | Joint strict quality: F5 298/300, v5 300/300 | Source; lower .979164/.990064 | H-D; F5-J; C |
| EV-07 | Mean recorded embedding row duration: F5 22.353525 s; v5 2.296161 s; n=300 each | Source rows on mixed Windows/Linux hardware; no latency superiority test | H-D/A; F5-J `stage=embed.seconds`; C |
| EV-08 | Mean recorded clean C1 correct query row time: F5 .414335 s, v5 .338424 s; n=300 each | Source rows; includes different row overhead, not registry end-to-end latency | H-D/A; F5-J clean row `seconds`; C |
| EV-09 | F5 internal detector time mean .220574 s, median .216076 s; 300 measured calls. v5 internal field absent in all 300 | Source calls; cannot compare internal F5 time to absent v5 time | H-D/A; F5-J `detection.seconds`; C |
| EV-10 | SD1.5 .2 semantic majority: F5 30/30 versus v5 22/30 | Source; repeated seeds clustered; CP each; descriptive paired discordance 8/0 | H-D; F5-R §2.2; R |
| EV-11 | SD1.5 .2 checked semantic majority: F5 27/30 versus v5 10/30 | Source; CP; excludes assumed-code success | H-D; F5-R §2.2; R |
| EV-12 | SD1.5 .4 semantic majority: F5 21/30 versus v5 5/30; checked-only 17/30 versus 3/30 | Source; CP; small descriptive panel | H-D; F5-R §2.2; R |
| EV-13 | Full `both_match` after each DDIM strength: 0/90 seed calls in both methods | 30 source clusters; not 90 independent trials; source upper .095034 if all 30 observed | H-D; F5-R §2.2; R |
| EV-14 | T4 false donor full attribution: 0/29 eligible distinct-owner pairs, both methods | Pair; upper .098145; one same-owner pair separate | H-D; F5-R §2.3; R |
| EV-15 | T5 false full attribution: 0/27 eligible distinct-owner pairs, both methods | Pair; upper .105019; three same-owner pairs separate | H-D; F5-R §2.4; R |
| EV-16 | T4 donor delivery witness: F5 4/30, v5 8/30 | Pair; failure to deliver cannot prove content-binding rejection | H-D; F5-R §§2.3,3; R |
| EV-17 | F5 continuation: 7,741/7,741 planned rows complete; continuation wall time 9,625 s; first 14 embedded sources laptop, remaining 286 rented GPU | Operational counts and duration, no binomial generalization; rental cost not established by `max_usd=0` | H/A; F5-R §§1,5; R |

## E3-S1 confirmation and labelled sensitivity

| ID | Statement and value/denominator | Unit and uncertainty | Evidence/source; verification |
|---|---|---|---|
| EV-18 | Original clean primary eligibility E3 294/300 versus v5 159/300; without exact H: 294/300 versus 293/300 | Source; target conventions differ between methods | H plus P sensitivity; E3-R clean coverage, E3-S Paired results; R |
| EV-19 | E3 joint strict quality 294/300; v5 298/300; all six E3 failures are LPIPS ≥.1 | Source; lower bound for E3 is in 01c; no all-source quality claim | H-D; E3-R Clean coverage; R |
| EV-20 | Original clean-gated majority S at .1: E3 281/300 vs v5 151/300; +43.33 percentage points | Paired source; reported bootstrap interval +37.33 to +49.33 pp; composite, not pure survival | H; E3-R Primary comparison; R |
| EV-21 | Original clean-gated majority S at .2: E3 278/300 vs v5 129/300; +49.67 pp | Paired source; reported bootstrap interval +43.33 to +55.67 pp | H; E3-R Primary comparison; R |
| EV-22 | Remove only clean exact-H gate, .1: 281/300 vs 278/300; +1.00 pp; paired one-sided p=.364 | Paired source; exploratory p, not a new confirmatory family or equivalence proof | P; E3-S Paired results; R |
| EV-23 | Remove only clean exact-H gate, .2: 278/300 vs 229/300; +16.33 pp; paired p=1.15e-8 | Paired source; post-hoc, retains quality/admission/other clean checks | P; E3-S Paired results; R |
| EV-24 | Ungated majority S at .1: 287/300 vs 283/300; +1.33 pp; paired p=.279 | Paired source; no established .1 survival advantage | H-D counts; P p value; E3-R and E3-S; R |
| EV-25 | Ungated majority S at .2: 284/300 vs 232/300; +17.33 pp; paired p=2.66e-10 | Paired source; post-hoc inference, same pinned SD1.5 channel | H-D counts; P p value; E3-R and E3-S; R |
| EV-26 | E3 exact semantic Q majority: 294/300 at .1, 297/300 at .2; v5 81/300 and 17/300 | Source; exact payload differs from detected content agreement | H-D; E3-R Clean coverage and regeneration table; R |
| EV-27 | E3 exact checked J majority: 287/300 and 284/300; v5 80/300 and 17/300 at .1/.2 | Source; J includes semantic agreement as well as payload | H-D; E3-R same table; R |
| EV-28 | H, both exact payloads D, and full F majority: 0/300 for both methods at .1 and .2 | Source; separate endpoint cells, upper .009936; means failure of full acceptance, not security | H-D; E3-R same table; R |
| EV-29 | Clean any-detection negatives: 0/300 sources each method. T3 complete sources: E3 290, unresolved 10; v5 297, unresolved 3 | Source; clean upper .009936; conservative T3 uppers .055885/.025641 with unknowns adverse | H-D; E3-R Negative calls; R |
| EV-30 | Public T4 transfer: E3 both payloads delivered 30/30, full F 0/30 | Pair panel; rejection upper .095034; delivery-conditioned evidence | H-D; E3-R Copy-paste table; R |
| EV-31 | Public T5 transfer: E3 both payloads delivered 30/30, full F 0/30; perceptual-only also 0/30 | Pair panel; upper .095034; no incremental combined-binding advantage | H-D; E3-R Copy-paste section; R |
| EV-32 | Final E3 local continuation 15,454.774 s; 42,031 planned records, 41,742 completed, 49 safety blocks, 240 unavailable dependents | Operational counts; total study spans previous attempts; no per-image or same-hardware speed inference | H/A; E3-R Execution; R |

## Development selection and registry history

| ID | Statement and value/denominator | Unit and uncertainty | Evidence/source; verification |
|---|---|---|---|
| EV-33 | SD2.1-base .2 checked semantic majority: E3 24/24, F5 24/24, v5 5/24; rule retains E3 only if E3−F5 ≥3/24, so selects F5 | Source; 24/24 lower .882654; no equivalence claim | D; U-R opening, Source-majority C; D-doc |
| EV-34 | Unseen-grid strict quality 24/24 all methods; median retained embedding E3 130.133 s, F5 52.4685 s, v5 2.578 s | Source; different quality and historical timing basis; not fresh benchmark | D; U-R Clean construction; D-doc |
| EV-35 | SD2.1 .4 checked majority E3 22/24, F5 12/24; full F/H 0/24 both methods | Source; small exploratory panel; .4 was not the selection rule | D; U-R Source-majority; D-doc |
| EV-36 | Registry first fresh D1 gate: .2 F_R 30/40 SD1.5, 32/40 SD2.1; required 36/40; fails | Source; CP bounds in 01c; calibration amended pre-evaluation after initial failure | D; REG-D opening and Fresh primary evaluation; D-doc |
| EV-37 | First fresh real-near-duplicate panel: fingerprint 4/13 accepts; pointer registry 0/13; all 13 lack pointer candidates | Pair; zero registry events do not isolate descriptor specificity; upper .205817 for 0/13 | D; REG-D opening; D-doc |
| EV-38 | Round 3 .2 F_R: 39/40 both regenerators; .4 30/40 both | Source; CP lower for 39/40 in 01c; development only | D; R3-R Result; D-doc |
| EV-39 | Round 3: 0/40 different real look-alikes; 0/59,280 unrelated; 0/80 transfers; 2/6 synthetic siblings accepted | Pairs clustered; raw failure under original bar; post-result sibling reclassification must remain explicit | D/P; R3-R Result and Verdict; D-doc |
| EV-40 | First fresh D1 registry: 39/40 searchable references, 2,555,904 raw descriptor bytes; planned registry 40 | Records; bytes exclude metadata/index/container overhead | D/A; REG-D cost table; D-doc |
| EV-41 | Fresh D1 lookup total .016 s for 3,040 saved paired registry/fingerprint calls; extraction snapshot 56.1892 s | Cached-score lookup and invocation snapshot only; not cold end-to-end detection time | D/A; REG-D cost caveat; D-doc |
| EV-42 | Step-2 recorded component wall sum 9,361.48 s; budget charge 9,601.48 s includes 240 s interruption allowance | Operational accounting; not all GPU time, no scientific uncertainty | D/A; REG-D Execution accounting; D-doc |
| EV-43 | Native WAM exact message recovery on the earlier 12-source development grid: 3/36 seed calls at .1, 0/36 at .2; frozen F5 exact q 27/36 and 20/36 | 12 source clusters; payload, detector/FPR and checkpoint differences prevent whole-system ranking | D; WAM-D Local evidence; D-doc |

## Registry held-out confirmation: report with the independent corrections

The complete confirmation fails. The frozen automated verdict and the pre-result approved scientific reading must both be retained. The reviewer verdict is ACCEPT WITH CORRECTIONS for bounded reporting, not a successful experiment. E3 here denotes the registry attribution endpoint, not the earlier E3-S1 writer. The registry uses F5 r2 and additional trusted enrolled descriptors.

| ID | Statement and value/denominator | Unit and uncertainty | Evidence/source; verification |
|---|---|---|---|
| EV-50 | E1 SD1.5 .2 F_R majority: 277/300; .923333 | Source; one-sided 95% CP lower .893130; gaps count as misses | H; REG-E E1 plan_view; M2-S numerator, C bound |
| EV-51 | E1 SD2.1-base .2: 280/300; .933333 | Source; one-sided 95% CP lower .904598; gaps count as misses | H; REG-E E1 plan_view; M2-S numerator, C bound |
| EV-52 | E1 pass threshold: 266/300 and lower CP ≥.85 in both models | Frozen criterion, not observed performance or journal criterion | Protocol; REG-P §5 |
| EV-53 | E2 unrelated comparisons: 0 observed accepts among **3,343,081 scored**; **3,408,600 planned**, **65,519 missing** | Repeated cross-source pairs, not millions of independent trials; missing negative outcomes are unknown | H; REG-E E2 wrong_source; M2-C availability, M2-S accepts. Corrects REG-R's unqualified 0/3,408,600 wording |
| EV-54 | E2 T4: 0/594 observed transfers; 600 planned, 6 missing | Repeated donor/source clusters; 297 evaluable donors, not 594 independent units | H; REG-E E2 T4; M2-C availability, M2-S accepts |
| EV-55 | E2 different real look-alikes: 3/45 accepted pairs; failures in 2/16 shots | Shot is primary uncertainty unit; upper CP(2/16)=.343825. Naive pair upper CP(3/45)=.163388 is not a cluster correction | H; REG-E saved scorer, saved PSNR dictionary; M2-C denominators, M2-S accepts |
| EV-56 | Accepted different pairs: tos-07_1c-o144 16.89 dB; tos-05_4h-o072 17.24 dB; tos-05_4h-o144 17.68 dB | Three paired grey-PSNR observations; no human perceptual identity validation | H-D; REG-R Failure detail; exact saved values 16.89217345, 17.23795413, 17.67512947 in reviewer artifact |
| EV-57 | Ambiguous real look-alikes: 2 accepts among 15 pairs; full panel 60 pairs | Descriptive, excluded by frozen distance rule; no negative-rate pooling | H-D; REG-R E2 failure detail, saved scorer; M2-S accepts |
| EV-58 | E3 wrong-owner pointer attributions: zero in each of 8 cells | Per-cell evaluable source counts 293–297; no pooled 2,000+-independent-trial claim; incomplete-case and abstention caveats below | H under REG-G approved reading; REG-E E3 rows; M2-C |
| EV-59 | E3 SD1.5 .2 exact: 280 original /14 none /0 wrong among 294; fingerprint 293 ambiguous /1 wrong | Source in one cell; wrong-owner upper CP(0/294)≈.010138 | H under approved reading; REG-R E3 table, REG-E rows; M2-C |
| EV-60 | E3 SD1.5 .2 further: 242 original /52 none /0 wrong among 294; fingerprint 285 ambiguous /8 wrong /1 none | Source; report abstention and ambiguity separately from wrong-owner decisions | H under approved reading; same source; M2-C |
| EV-61 | E3 SD1.5 .4 exact: 201 original /93 none /0 wrong among 294; fingerprint 266 ambiguous /28 wrong | Source; descriptive severity, not E1's primary .2 claim | H-D under approved reading; same source; M2-C |
| EV-62 | E3 SD1.5 .4 further: 81 original /212 none /0 wrong among 293; fingerprint 188 ambiguous /75 wrong /30 none | Source; zero wrong includes substantial abstention; upper CP(0/293)≈.010172 | H-D under approved reading; same source; M2-C |
| EV-63 | E3 SD2.1 .2 exact: 282 original /15 none /0 wrong among 297; fingerprint 296 ambiguous /1 wrong | Source; upper CP(0/297)≈.010036 | H under approved reading; same source; M2-C |
| EV-64 | E3 SD2.1 .2 further: 249 original /48 none /0 wrong among 297; fingerprint 289 ambiguous /7 wrong /1 none | Source; no pooled independent cell claim | H under approved reading; same source; M2-C |
| EV-65 | E3 SD2.1 .4 exact: 199 original /98 none /0 wrong among 297; fingerprint 266 ambiguous /31 wrong | Source; descriptive severity | H-D under approved reading; same source; M2-C |
| EV-66 | E3 SD2.1 .4 further: 81 original /216 none /0 wrong among 297; fingerprint 190 ambiguous /75 wrong /32 none | Source; the 75 wrong-owner count is cell-specific; ambiguity is not forced attribution | H-D under approved reading; same source; M2-C |
| EV-67 | F5 failed to mark 3/300 DIV2K photos; downstream unavailable entries retained | Attempted source; 1% observed failure, no universal embedding claim | H-D; REG-G/REG-R, REG-J; M2-C |
| EV-68 | Safety checker blocked 50 regeneration outputs; at primary .2 three SD1.5 sources lose all three seeds | Regeneration attempts and source clusters; missingness differs from SD2.1 without safety checker | H-D; REG-G/REG-R, REG-J; M2-C |
| EV-69 | Registry journal: 53,580 planned units; 53,053 completed, 53 scientific failures, 474 dependent unavailable; recorded run duration 43,401.126 s (12.0559 h) | Operational counts; multiple attempts retained; not per-image detector benchmark | H/A; REG-J and reviewer recount; M2-C |
| EV-70 | Frozen `pass_`, E2 pass and E3 pass are false; approved reading E1 passes, E2 fails, E3 zero wrong among evaluable cases | Protocol verdict, not estimated success probability; no overall confirmation pass | H plus approved pre-result amendment; REG-G, REG-E, REG-R; M2-C |
| EV-71 | Negative-look-alike scoring uses descriptor rule alone, without requiring watermark pointer | Protocol scope, intentionally adverse conditional record check; not observed whole-system attack success | H protocol; REG-P, REG-R failure-detail scope; reviewer source check |
| EV-72 | Registry condition: D1≥.0594367 and B1≥.90; if native D1 abstains, B1≥.99; different-image cutoff grey PSNR<18.126 dB | Frozen operational constants; no human or legal identity definition | Protocol; REG-P §2 and frozen rule |
| EV-73 | Registry mark quality available for 297/300 attempts; 291/297 available marks satisfy prior strict quality, hence 291/300 attempted sources have observed strict-quality marks | Source; descriptive in registry protocol, not an added endpoint; six available LPIPS failures and three marking failures | H-D/A; REG-J embed quality, reviewer recount; M2-C |
| EV-74 | Registry available-mark PSNR min/median/max 41.8551/44.3333/45.4611 dB; SSIM .929167/.985054/.997852; LPIPS .000846884/.0182147/.149810 | 297 available marks; continuous descriptive summaries, no human visual verdict | H-D/A; REG-J embed quality, reviewer recount; M2-C |
| EV-75 | Fingerprint E3 **any attacker accepted**, including ambiguity, per EV-59–66 order: 294/294, 293/294, 294/294, 263/293, 297/297, 296/297, 297/297, 265/297 | Source per cell; this is the frozen wrong-owner-present predicate. Distinguish unique wrong owner (1–75) from ambiguous multiple owners | H/H-D under approved reading; REG-E E3 rows; M2-C |
| EV-76 | Ambiguous synthetic registry panel: 4 accepts among 12 pairs | Reported only under frozen distance definition; not an E2 different-image panel | H-D; saved scorer summary; M2-S |
| EV-77 | In all eight E3 cells, beta native `semantic.found` and `read` are both false for every completed call: 0/294, 0/294, 0/294, 0/293, 0/297, 0/297, 0/297, 0/297 in EV-59–66 order | Source within cell; repeated sources, unavailable calls excluded. The owner gate already implies no beta candidates; this does not isolate q or descriptor contributions and is not a newly evaluated owner-only arm | Post-hoc count of saved Boolean outputs, WP9 author desk check; REG-J; [specification](01d-e3-owner-gate-audit.md) and [JSON](01d-e3-owner-gate-counts.json); stdlib only, no rescoring |

## Missingness and interpretation rules

1. E1 keeps all planned sources, including mark failures and blocks. Do not inflate rates by dividing by successful embeddings.
2. E2 has missing negatives. Zero observed unrelated/T4 accepts is not zero established outcomes for all planned comparisons. The original source-cluster upper near 1% presumes 300 complete exchangeable source clusters; cite the independent review's missingness qualifications whenever discussing it. A pairwise million-trial CP bound is inappropriate even before missingness.
3. E3's pre-result complete-case rule is authorized and distinct from frozen automated completeness. It conditions on query and own original/attacker record availability; absent cross-source competitor records may still matter. Do not promote zero observed wrong-owner events to cryptographic soundness or a claim about every planned case.
   The declared E3 error is any accepted attacker record, including an ambiguous owner set. Both arms must use this definition (EV-75); the unique-attacker counts alone understate fingerprint endpoint failures. No ambiguity is silently relabelled as a unique wrong assignment.
4. The descriptor-only E2 failure is substantive under the frozen endpoint, even though it is not a measured full pointer-plus-descriptor forgery. Do not erase the failure or equate it with a proved end-to-end attack.
5. The two E1 models share sources. Eight E3 cells share sources. The 16 look-alike shots are sampled from one film and may have film-level dependence. No multiplication of these panels into independent sample size is allowed.
6. No new detector score, threshold, image metric, descriptor, calibration or timing run was produced. CP calculations only derive uncertainty from existing counts.

## May claim / may not claim

| May claim, with IDs and conditions | May not claim |
|---|---|
| On the frozen DIV2K protocol, F5 plus a trusted descriptor registry attributes .2 regenerations at 277/300 and 280/300, with gaps as misses (EV-50/51) | General diffusion robustness, SDXL/FLUX robustness, independent-autoencoder transfer without Q-VAE evidence, or all-endpoint confirmation |
| Zero observed wrong-owner attributions in the eight evaluable regenerate-and-enroll cells, with the complete counts/abstentions and pre-result amendment (EV-58–66) | Legal ownership, cryptographic unforgeability, authenticated enrollment, adaptive/watermark-reembedding security, or zero population error |
| No observed unrelated or copy-transfer false accepts among scored available comparisons (EV-53/54) | 3.4 million independent or completely observed negative trials; rare-FPR certification from the pair count |
| D1+B1 fails on 3/45 operationally different look-alike pairs in two shots (EV-55/71) | Perfect record binding; human-confirmed differentness; a proven successful whole-system forgery from descriptor-only accepts |
| F5 whole-system semantic recovery exceeds v5 on the earlier SD1.5 descriptive panel (EV-10–12) | Causal proof of encoder amplification or latent insertion, or matched-FPR superiority over modern external methods |
| E3 exact semantic payload recovery remains high, but .1 composite advantage is mostly admission-dependent (EV-18–28) | Pure .1 semantic robustness gain, equivalence from a nonsignificant test, or full ownership acceptance after regeneration |
| Recorded query durations and embedding costs describe their specific hardware/measurement boundaries (EV-07–09/34/41) | Lightweight DCT-only extraction, total registry latency from cached lookup time, or external latency superiority |
| The original image-domain method and subsequent registry amendment are clearly labelled | Claiming the proposal's latent-insertion or lightweight-DCT objectives are fulfilled; fabricated human ratings or supervisor approval |

The registry review is the authoritative correction layer for REG-R. Source reports remain untouched. Registry quality/cost additions below are existing recorded measurements, not new measurements.

