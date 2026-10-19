# Forward-citation sweep and novelty update

Extension E4, 19 October 2026. This bounded sweep covers 2025–2026 citing works available at the session date for DREW, final TrustMark, SynthID-Image, Rel-Zero and the October 2026 soft-binding benchmark. Primary reference lists establish edges; method and evaluation inspection establish V2 depth. Neither an indexed citation nor V2 status certifies the paper's correctness. All work was documentary; no experiment or media inspection occurred.

## Findings across the five targets

| Target | Verified incoming edges in this sweep | Qualification |
|---|---:|---|
| DREW, arXiv 2406.02836 | 1: IConMark | The reference names the work, not specifically its v2. |
| Final TrustMark, ICCV 2025 | 5: NRGMark, Signpost, Nemecek et al., Soft Bindings, Watermarks Attack Watermarks | Final and older 2023 TrustMark are kept separate. Soft Bindings was already read in WP2. |
| SynthID-Image, arXiv 2510.09263 | 8: Luminark, AWPD, MarkNull, Beyond Generation, Pixel Seal, Jarvers et al., Nemecek et al., RAVEN | Pixel Seal was already V2. Jarvers remains V1 for scientific claims despite a verified reference. Citation is not evidence that SynthID was evaluated. |
| Rel-Zero, arXiv 2603.17531 | 1: Zeng and Tondi | Primary publisher reference preview only; truncated entry, cited version unknown, full text inaccessible. V1 for scientific claims. |
| Soft Bindings, arXiv 2610.04151 | 0 verified | Only about seventeen days old. This is a bounded search result, not evidence of no citations. |

The [edge register](14-forward-citation-sweep/verified-edges.csv) contains these 15 work-level edges. It includes two edges whose citing papers remain V1, and two citing papers already covered by WP2. Older-TrustMark edges are recorded separately in lane registers and excluded from the final-TrustMark count. The sweep adds **11 V2 works** to the master matrix: four from the DREW/TrustMark lane, four from the SynthID lane, two active-removal papers and Nemecek et al. One additional inspected paper, Ni et al., is quarantined because of internal numerical/optimization inconsistencies; it is not in the master count or used as positive scientific evidence.

After integration the master has **98 matrix works, 90 V2 (88 research papers and two standards/guidance), eight V1**, and **99 bibliography entries**. The extra bibliography entry preserves TrustMark's predecessor version. The two newly discovered V1 citing papers and unresolved leads remain in this sweep's registers rather than being silently promoted or counted as substantive additions. E2's original 88-entry audit remains a historical checkpoint; the 11 additions have their own [identity audit](14-forward-citation-sweep/bibliography-additions-audit.csv).

## What changes in the novelty assessment

**Registry routing remains established prior art.** NRGMark decodes a UUID that resolves a C2PA manifest in a cloud repository. It strengthens the objection to a broad pointer-plus-registry claim, although its localized energy-provenance task is different from continuous image-instance matching. Signpost routes to watermark technologies through a registry; it does not store enrolled original-image descriptors. That distinction prevents treating every registry as the same scientific system.

**Combining signals and checking inconsistency also have antecedents.** IConMark combines semantic concepts with conventional watermark detection, Coexistence studies layered signals at explicit operating points, and Nemecek et al. check signed metadata against expected watermark payloads. Nemecek's controlled assertions and self-signed certificates do not establish lawful ownership or the truth of a manifest. These papers narrow architecture-level novelty without establishing performance on our frozen attribution game.

**Detection, decoding and attribution need separate outcomes.** AWPD classifies watermark presence without recovering an owner. Luminark's random-key guarantee does not automatically become fixed-key adaptive security. MarkNull's reported SynthID success uses 20 Imagen images and Gemini verification, not an audit of an internal production detector. Beyond Generation's reconstruction ablation changes more than the watermark and cannot by itself identify a causal watermark effect. These cautions support compatible controls rather than numerical cross-paper rankings.

**Active manipulation remains untested locally.** Watermarks Attack Watermarks distinguishes victim detection, message corruption and replacement-payload recovery; a cited victim is not necessarily an evaluated victim. RAVEN's inspected preprint has inconsistent narrative counts and reports separate detection/bit-accuracy columns. Its semantic preservation metrics do not prove same-instance identity. Neither source tests F5 or the local registry. They strengthen the active-threat limitation; they do not authorize experiments or reopen closed baseline work.

The primary framing therefore remains an empirical study of recovery versus registered-image attribution, with a narrower passive-enrollment case-study fallback. EV-77 still shows that beta owner detection fails before q/content checks in every completed E3 call. None of the new literature identifies the missing component effect or repairs E2's failed hard-negative endpoint. The manuscript remains **not submission-ready**.

## Coverage and reproducibility limits

OpenAlex returned zero DREW citers despite the verified IConMark edge, one SynthID citer despite several primary references, and zero Rel-Zero citers despite the publisher preview. The new soft-binding record also had zero indexed outgoing references despite an extensive primary bibliography. Semantic Scholar returned HTTP 429. These observations demonstrate incomplete ingestion and access; zero index results are not absence claims.

Searches used exact titles, arXiv identifiers, authors and references/citations terms, then inspected primary text. No authenticated Web of Science, Scopus or Scholar census was performed. The registers preserve failed opens, metadata-only leads, anonymous submissions, older/final version separation and fulltext gaps. A November–December issue label for the Rel-Zero citer does not establish its online-first date; only the accessible primary preview at this retrieval date is claimed.

RAVEN's final CVPR metadata is verified, while its scientific card remains pinned to arXiv v1 after the continuation's failed final-text routes. Beyond Generation was initially inspected at v1 and has now been refreshed to **v2** for the focused method, evaluation, limitations and SynthID reference; its earlier cache and agent access logs remain v1 history. See [version checks](17-completion/version-checks.md). NRGMark's author PDF is not asserted byte-identical to the proceedings. Source-specific numbers must retain these version qualifications. Final TrustMark is ICCV 2025; an initial delegation label saying CVPR was corrected before integration.

## Audit trail

- [DREW / TrustMark lane](14-forward-citation-sweep/drew-trustmark/sweep.md): four additions, quarantine card, 26 classified candidates, primary hashes and identity records.
- [SynthID / Rel-Zero lane](14-forward-citation-sweep/synthid-relzero/sweep.md): four additions, two V1 cards, exact query log, index responses and identity checks.
- [Active-removal lane](14-forward-citation-sweep/active-removal/sweep.md): two additions, twelve target checks and version caveats.
- [Soft-binding lane](14-forward-citation-sweep/soft-bindings/sweep.md): zero verified forward edges, explicit index/access limitations and the existing incoming TrustMark edge.
- [Provenance-conflict reading](14-forward-citation-sweep/provenance-conflicts/sweep.md): Nemecek addition and its two seed edges.

The parent read all lane reports/cards before integration and checked new identities, unique citekeys and card paths. No paper's claim is elevated to a replicated result, and no new experimental result is attributed to this thesis.
