# Stage 1b parent acceptance audit

This file records the parent author's checks under BRIEF section 1b. It is not the independent second design review. The prior freeze at `c2384e7` remains historical. No topic is accepted merely because its agent reports completion.

## Acceptance method

For each topic, count distinct qualifying sources or model families from individual cards, excluding duplicate versions and metadata-only leads. Read the cards' method/evaluation evidence and the required table fields. Reused sources need a topic-specific account of what was rechecked. Inspect consequential assertions against the cited primary text or exact pinned code; a search result snippet is not inspected evidence.

Count distinct substantive queries from the query-event ledger, classify their actual endpoints under the brief's four allowed categories, and distinguish unsuccessful access attempts from returned discovery evidence. Require at least ten queries across three categories, a coverage statement, and a section named "what we might still have missed". Check that table rows, card IDs and counts agree. Unknown source details must be stated as unknown with the inspected scope; invented parameters cannot repair an unknown.

T4 additionally needs falsifiable predictions for all core channels and P1-P8 plus any added proposal. T5 needs exact pinned file/line evidence for every protocol-relevant setting in all six required implementations. T6 needs reproducible, purely analytic operating characteristics for all three sample sizes, including seed dependence and missing units. T8 needs at least 25 distinct mechanisms with mitigation or a retained limitation and supporting evidence or argument.

Record unresolved gaps before acceptance. A below-floor delivery returns to a fresh topic agent with the explicit gap list; the parent does not substitute its own hurried topic research. After acceptance, commit and push the topic on the Codex branch and record its commit. The fresh xhigh reviewer will independently audit these floors before judging the integrated design.

## Dispositions

| Topic | Required content floor | Qualifying count | Distinct queries / categories | Parent disposition | Accepted topic commit |
|---|---|---:|---|---|---|
| T1 | 15 benchmark/attack sources; complete settings table | 20 direct; 34 total V2 | 30 queries, 20 intents / 3 categories | Accepted after parent inspection | This acceptance commit |
| T2 | 15 model families; lineage and implementation table | Pending | Pending | In research | Pending |
| T3 | 12 post-hoc methods; fidelity and run-cost table | Pending | Pending | In research | Pending |
| T4 | 8 mechanism sources; all-channel and proposal predictions | Pending | Pending | In research, fresh Astra xhigh | Pending |
| T5 | Six named implementations; all relied-on settings pinned by file/line | Pending | Pending | Not yet assigned | Pending |
| T6 | n60/90/120; seed correlation and missing-unit sensitivity | Pending | Pending | Not yet assigned | Pending |
| T7 | 12 evaluation sections from 2024-2026 eligible venues | Pending | Pending | Not yet assigned | Pending |
| T8 | 25 distinct validity threats | Pending | Pending | Not yet assigned | Pending |

## Evidence inspection and gaps

Detailed checks and any rejection/resubmission history will be appended here as the topic deliveries arrive.

### Interim primary-source checks, not acceptance

The parent opened the full primary texts of WARP (`2609.40031`), the local-watermark benchmark (`2609.16832`) and latent-frequency masking (`2610.02010`). WARP's benchmark section distinguishes theoretical random-message thresholds from empirical negative-image calibration; the eventual T1/T7 summaries must preserve that distinction. These openings do not add parent-authored cards to a topic's count.

The parent also checked the agent's cached primary text for three consequential T2 claims. `T2-1b/T2-lens-paper.read.txt` lines 125 and 129 explicitly describe adopting the FLUX.2 VAE. `HiDream-ai--HiDream-I1-Full--README.md.txt` lines 105 and 109 attribute the VAE to FLUX.1-schnell, while the configuration's `_name_or_path` mentions flux-dev; this supports FLUX-family reuse without independently proving exact weight identity. The Qwen-Image-2.1 VAE configuration specifies spatial scale 16, latent dimension 64 and four input/output channels; those fields alone do not establish initialization independence. These distinctions were sent to the topic agent before final delivery.

The parent read the nineteen newly drafted T1 individual cards and cross-checked consequential numerical claims in the cached primary texts: MarkCleaner Table 1/Section 5.1, LiBRA Table IV/Section V, and the local-watermark benchmark Sections 4.1-4.3. Draft corrections were returned before final delivery: WARP had an unsupported forensic-evaluation description; UnMarker Appendix A settings were available but not transcribed; MarkCleaner needed its main learned-attack row as well as the illustrative geometry result; VINE paper versus release lineage and its conflicting image denominators must remain explicit. The final corrected versions, new cards, settings table and search ledger are still pending acceptance.

The parent read the substantive fields of all thirty T2 draft family records: eighteen conservatively counted model families and twelve supporting/availability records. Versions sharing a family are not counted again (SD1/2, SD3/3.5, Kandinsky2/3/5, SANA/DC-AE/Sprint, HiDreamI1/O1). SDXL Table3 and Section2.4, Qwen encoder/decoder text and Table2, and SD3 component-resource numbers were checked against the cached full primary texts. Corrections sent before acceptance concern official checkpoint precision versus arithmetic dtype, the selected SDXL download-byte total, an inaccurate frozen-diffusers version reference, Qwen section numbering and spaces inserted into opaque revision strings. Model-paper eligibility does not imply executable weights or an established independent encoder; Lens/PixSGR and FLUX-related uncertainties remain explicit.

### T1 accepted, 2026-10-20

The parent read all 34 individual V2 cards and checked the 34-row settings table. Twenty distinct direct attack/benchmark sources meet the 15-source floor without the fourteen supplemental sources. All 34 primary cached files independently match the recorded SHA-256 values. Historical aggregate cards, discovery pointers, inaccessible papers and duplicate software releases do not increase this count.

The query ledger contains 34 events: 30 successful distinct query strings, conservatively grouped into 20 substantive intents, across 26 web queries, two OpenAlex queries and two official-repository searches. Zero-result repository searches remain search attempts, not evidence of absence. Failed retrievals do not count. The coverage register and exact "what we might still have missed" section identify the inaccessible ICDMW2025 full text and the adjacent or out-of-scope leads.

Consequential corrections were verified in the primary texts: DIP Appendix B specifies a maximum of 500 optimization iterations and the baseline grids; UnMarker Appendix A supplies its optimization schedules; MarkCleaner needs its main attack row and cannot collapse bit accuracy into calibrated detection; VINE's paper and release differ in generator lineage and its reported evaluation denominators conflict. The competition report's conflicting attack-score and calibration descriptions are retained rather than silently reconciled. The parent also checked ProxyEraseAgent's 128-pixel evaluation and BER-at-least-.1 success criterion, the autoregressive benchmark's three-pass rinse results, and SNW's conflicting 1,000-versus-200 attack-image denominators. These prevent importing unlike endpoints as F5 performance predictions.

The result is acceptance of documentary coverage, not endorsement of every source's inference. Inaccessible full text, omitted settings, questionable endpoint definitions and unconfirmed preprint venues remain visible limitations. T1 recommends reporting and lineage corrections, not another core attack variant. No outcomes were produced.
