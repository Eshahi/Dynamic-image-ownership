# Cohort decision: narrow COCO512 vs all-domain (M1b)

Status 2026-10-05 — decision memo for the user. No choice made here. No held-out data opened to write it. Threat scope T3/T4/T5 only.

## Two options on the table

| | Narrow COCO512 (the frozen intent) | All-domain (protected plan in `research/sample-size.md`) |
|---|---|---|
| What it is | Amendment: evaluate one frozen existing-photo method on **MS-COCO test only**, 512x512 canonical, as drafted in `research/m1-confirmatory-draft.md` and pinned in `research/f5-r2-spec.md` / `research/m1b-f5-confirmatory-manifest.md`. Leaves `research/sample-size.md` unchanged. | The proposal's original study allocation: **MS-COCO + DIV2K + DiffusionDB**, each with development / validation / locked-test splits, at the resolutions/rights that B3/B4 admit. Documented in `research/sample-size.md` (fixed-N precision planning). |
| Cohort (independent test groups) | **300** COCO test group representatives (metadata-only freeze, ranked by `m1-coco512-confirm-v1` tag) | **3,900** locked-test groups total: **600 COCO + 300 DIV2K + 3,000 DiffusionDB** group representatives (one per leakage-screen component). Table row "Total / 6,900" in `research/sample-size.md`. DIV2K uses 300 train-HR + 100 valid-HR groups in test (native labels retained as a stratum). DiffusionDB uses the 2M PNG candidate subset; current metadata shows a group shortfall (759/751 vs 600 plan) that B3/B4 must resolve — see interface doc. |
| Threat grids on that cohort | T3: **30** sources x (VAE + .05/.1/.2/.4 x3 seeds) x2 arms = 780 outputs + 1170 detector rows per method. T4: **30** donor-recipient pairs, 2 sizes, sham. T5: bounded **up to 30** disjoint pairs from 44,850 candidates (identical nonempty category signatures, pHash >=8). Cohort is the same 300 for T3/T4/T5; no replacement on failure. | Same T3/T4/T5 structure but replica per domain (or a domain-stratified version). The `research/sample-size.md` row-level **T1** block (benign transforms) is already sized at **300 test groups/domain**, 4 transforms each (separate from T3/T4/T5). T3/T4/T5 confirmatory protocols are still `BLOCKED_PROTOCOL` there — severity/admissibility/pairing, comparator, paired margins, multiplicity still to freeze. |
| Controls on every cell | Clean: C0-source, C0-reconstruction (matched watermark-off path), C1 correct-owner, C1 wrong-owner (next roster id). One uint64 schedule seed per source (`thesis:owner:00..15` roster). Thresholds fixed inclusive (decoded 8.259..., recomputed 4.982..., FPR 1e-6, roster 1) — no calibration on test. Missing/invalid counts adverse. | Same control logic per `research/sample-size.md` / `acceptance.md`: primary denominators are **full predeclared eligible counts** even when reconstruction/marking fails (adverse counting). Observed-valid rates reported separately. One K=1 wrong-owner call per marked test image is planned. |

## What each lets the thesis claim — numerically

All bounds below are **fixed-N precision**, not pilot-derived power. Values from `research/sample-size.md` section "Design method, precision and FPR resolution" (Wilson worst-case p=0.5, one-sided 95% exact zero-FP bound `1 - 0.05^(1/n)`).

| Independent n (per cell) | Wilson 95% half-width at p=0.5 | Zero-FP one-sided 95% upper bound | Can it resolve 1% with zero FP? |
|---:|---:|---:|---|
| 30 (T3/T4/T5 descriptive cluster) | ~17.9% | **~9.50%** | No — descriptive only. Zero errors in 30 gives 9.5% upper bound, far from 1%. |
| 100 | 9.62% | 2.95% | No |
| 200 | 6.86% | 1.49% | No |
| **300 (narrow COCO512 clean cell; DIV2K test)** | **5.62%** | **0.994%** | **Yes, but only just: needs 0/300. One FP -> 1.57%, over 1%. Sensitive to a single error.** |
| 381 | 5.00% | 0.78% | Meets +/-5pp Wilson target |
| 600 (COCO locked-test) | 3.99% | 0.498% | Yes; tolerates a few FP |
| 1,000 | 3.09% | 0.299% | Yes |
| 3,000 (DiffusionDB locked-test) | 1.79% | 0.100% | Yes |
| 3,900 (all-domain pooled test) | ~1.57% | ~0.076% | Pooled only — does not replace domain-specific criteria |

Practical reading:

- **Narrow COCO512** can support the thesis sentence: *"On 300 independent MS-COCO photographs resized to 512, the frozen detector held false attributions at <=1% (95% upper bound 0.99% with 0/300) and separated the operational semantic/instance states on clean images; regeneration/transplantation/collision outcomes with 30 independent sources/pairs are descriptive (e.g., 0/30 -> <9.5%) and not a 1% population claim."* It **cannot** support a three-domain claim, a native-2K claim, an unseen-model-generalization claim, or a cryptographic ownership claim. T3/T4/T5 at n=30 remain exploratory by design; the manifest already declares them descriptive. Other regenerators or a pixel pre-filter before encoding (T2 composition) remain untested — one-line limitation.

- **All-domain** (600/300/3,000) can additionally support: *"Across the three photographed/generated domains at their admitted resolutions, per-domain clean false-positive bounds meet 1% when zero-FP is observed, with tighter bound on the large DiffusionDB locked test; cross-domain pooling can be described but does not replace per-domain criteria."* To earn that sentence the project must first clear `BLOCKED_DATA / BLOCKED_PROTOCOL / BLOCKED_RESOURCE` in `research/sample-size.md`: pin exact releases/licenses/IDs/grouping/rights/archive hashes and split assignment; freeze T2–T6 severity/admissibility/pairing/comparator/paired-margin/multiplicity; and acquire/verify checkpoints, implementation, storage/VRAM and bounded execution. A 300-image pilot does not count as held-out evidence. The large DiffusionDB corpus (1.6 TB PNG subset / 6.5 TB Large) and native DIV2K keep resource risk open.

Shared prerequisites for either choice before any held-out read: frozen candidate/config/spec and side information (pinned SD1.5 VAE encoder + 7 CLIP passes) accepted at M1; independent M1 review passes; synthetic rehearsals pass; user approves the exact execution manifest; official runner runs the single held-out execution.

## Cost / feasibility delta (development-only estimate; pending real p95 receipts)

Narrow COCO512 is **one domain, 300 clean groups + 30-unit threat slices**. All-domain is **~13x** the clean units and multiplies the attack matrix by domain. The draft's runtime worksheet (development p95s) is still pending — see `research/m1-confirmatory-draft.md` "Runtime budget" — and must be filled before approval for either option. Both options are USD0 local only under the current plan; paid/remote compute needs separate authorization and deadline-enforcement work that is currently unavailable. Do not treat the 86,400 s schema maximum as acceptable project scheduling; size shards at <=3600 s with a 3500 s cooperative stop.

## Recommendation for the record

This memo makes **no recommendation**. Adopting the narrow amendment does not amend `research/sample-size.md`; rejecting it leaves the draft as a proposal with no held-out data opened. Either way, report per-domain bounds with counts, distinguish source-C0 from matched-reconstruction C0, and retain same-owner T4/T5 descriptive support separately from false cross-owner attribution (see `m1-same-owner-endpoint-clarification.md`). A negative no-admissible-threshold result remains reportable with narrower scope if a comparator cannot be run.

---
References: `research/sample-size.md`, `research/m1-confirmatory-draft.md`, `research/m1-confirmatory-interface.md`, `research/m1-confirmatory-external-index.json`, `research/m1-confirmatory-external-index.md`, `research/m1-confirmatory-planned-inventory.md`, `configs/f5-r2.json`, `research/f5-r2-spec.md`.

## User decision — 2026-10-06

The user chose **narrow COCO512** (300 MS-COCO test group representatives at 512 x 512; T3/T4/T5 slices of 30, descriptive). The choice was made in chat on 2026-10-06, after the r3-256 test (`claude/f5-r3-256`) ended the algorithm search for this stage. `research/sample-size.md` is unchanged; the all-domain plan remains the protected proposal plan and is not run.

Still required before any held-out pixel is opened:
1. the GPU smoke of `scripts/m1b_f5_runner.py` on two development images;
2. the exact execution manifest, approved by the user;
3. the single held-out run, started under that approval.
