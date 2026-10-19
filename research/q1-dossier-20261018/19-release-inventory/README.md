# Prospective reproducibility and release inventory

Prepared by Codex agent as an authoring follow-up, not an independent review. Local clock at start: **2026-10-19T04:09:35.4688337-08:00**. The original session deadline, **2026-10-19T04:04:04.3769833-08:00**, had expired; no new ten-hour deadline is created. This bounded follow-up inventories existing text and filesystem metadata only. No image pixels, descriptor arrays or model weights were opened; no Python, science program, experiment, package installation, download or public release occurred.

**Finding:** a useful, small, model-free package can reconstruct the manuscript's reported tables from saved counts and decisions. The local materials do **not** yet constitute an approved public artifact or a portable science-replay package. Availability, rights, scientific sufficiency and authority to release are separate columns in [inventory.csv](inventory.csv).

## 1. What was checked

The inventory has 64 scoped entries: 59 exact paths available locally, four absent at the tested path, and one production deliverable not yet authored. A directory's existence does not certify every child, complete descriptor coverage, file correctness or redistribution rights. File sizes are metadata, not hash verification. Existing hash checks in the saved recount are historical evidence, not new checks performed here.

The four absent-path findings are informative path-resolution cases:

| Entry | Exact absent path relative to alias | Resolution or consequence |
|---|---|---|
| R12 | MAIN `.thesis-build/registry-package/configs/f5-r2.json` | The frozen path is repository-relative. WT `configs/f5-r2.json` exists (R58), as does the predecessor profile (R59). Do not label the configuration globally missing. Exact snapshot/hash matching remains a later packaging check. |
| R40 | WT `scripts/claude_verify_heldout_registry.py` | The corresponding script exists in CLAUDE (R41). Its image-loading execution is outside the table-only package. |
| R55 | WT `data/splits.csv` | The pinned source plan exists in the B3 admission worktree (R60), with its admission manifest (R61). These are protected read-only inputs. |
| R56 | WT `LICENSE` | No blanket project license was found in the scoped filename searches. This neither proves that no permission exists elsewhere nor grants reuse rights. |

Evidence comes from dossier `01-evidence-ledger.md`, `01b-heldout-registry-recount.json`, `01c-counts-and-bounds.json`, `01d-e3-owner-gate-counts.json`, manuscript `11-draft-sections.md`, figure specifications `15-figure-specifications.md`, the named frozen configurations/manifests, source receipts and local path checks. Existing papers were not reopened for a new substantive claim. No web search was needed; therefore there are no new web queries or retrieval dates.

## 2. Minimal table-reconstruction bundle

This is a proposed content list, not a new execution manifest, approval or copied release archive. All source files remain unchanged.

1. **Interpretation and provenance:** ledger 01; review 01b and the pre-result gap reading in CLAUDE; owner-gate audit 01d; frozen-config and source-pins; the corrected results description; manuscript 11 and figure specifications 15. Include exact source-version labels and the negative overall confirmation verdict (EV-70).
2. **Reported numerical inputs:** 01b recount JSON, 01c count/bound JSON and 01d owner-gate JSON, plus the unchanged registry `metrics/endpoints.json`, `outputs/run.json` and saved scorer `metrics/frozen-scorer-1792330103671103400/scoring/run.json`. The latter two give historical cost and saved E1/E2 numerators. They do not transform those numerators into independently rescored measurements.
3. **Optional audit layer:** the registry journal's text rows, run-context and historical manifests, with appropriate identity/path review. A future metadata-only derivative should retain unit IDs, source/shot joins, outcomes, native `found/read` flags, payload/reference availability and recorded quality/timing fields. It must preserve all missing and failed entries. Do not silently copy images, cache arrays or everything referred to by a path. Retain originals privately and document any redaction in the derivative.
4. **Historical tables if retained in the paper:** F5 endpoint and journal files (R44–45); E3 endpoint and sensitivity report/script (R46–47, R62–63); unseen-regenerator summary (R48); registry development reports and run records (R49). The current five main figures primarily concern the registry case study, so these are conditional additions rather than obligatory full-run archives.
5. **A later table-only producer:** no new producer was written or executed here (R57). It should consume JSON/JSONL as data, never import a worker, load a model, open pixels, recompute a descriptor or re-score an image. It should emit tidy CSV tables with EV IDs and input locators; use saved bounds or a separately declared stdlib bound routine; reject schema errors, duplicate IDs and impossible count sums. Figure 15 specifies the fields and acceptance checks. Rendered figures remain future work.

The core can reconstruct Figure 2's fixed E1 numerator/denominator/bounds, Figure 3's four owner-set counts and missing-source gutter, Figure 4's observed/planned coverage and accepted-pair PSNR values, and Figure 5's qualitative claim mapping. Figure 1 is a code/protocol diagram. No input image or weight is needed for these tasks. Historical table denominators and source/shot/pair units must travel with each row; zero available accepts must not replace unknown comparisons.

A future standalone registry export is a separate artifact: each record would need `record_id`, public `owner`, `q`, D1/B1 cache references and profile/version, plus source/availability joins and the distinction between native D1 abstention and missing data. The inspected journal/config and descriptor directory provide provenance components; this inventory does not certify an assembled portable export, array integrity or complete banks. Numerical vectors are unnecessary for transcription of saved decisions and remain outside the minimal package.

Existing `scripts/e3_s1_m2_sensitivity.py` is a separate, retained aggregate-analysis route for EV-18–28; it was inspected as text only. Existing `m1b_coco512_analysis.py` imports a worker and `m1b_registry_analysis.py` has a SciPy dependency, so their names alone do not certify a portable stdlib-only route. Do not execute them as a shortcut during research-only work.

## 3. Portability and reconstruction limits

| Alias | Original root |
|---|---|
| WT | `C:/Users/Soroush/.codex/worktrees/codex-q1-research` |
| MAIN | `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5` |
| CLAUDE | `C:/Users/Soroush/.codex/worktrees/claude-registry-research` |
| B3 | `C:/Users/Soroush/.codex/worktrees/b3-coco-release-audit/THESIS_GUIDE_OFFLINE_v5` |

A future portable copy should use logical paths such as `evidence/`, `saved/registry/`, `saved/f5/`, `saved/e3/` and `protocol/`, with a read-only mapping from original alias/path to copied relative path. Treat absolute paths embedded inside JSON as provenance strings, not authority to access local disks. Configure input locations explicitly; do not recreate a user's `C:`/`W:` trees or rewrite retained originals. Relative `configs/f5-r2.json` resolves against its repository snapshot, not the registry-package directory. Resolve the manifest/source-pin commit, not whichever HEAD happens to be current.

Saved aggregate outputs reproduce **reported decisions**, not the entire scientific process. In particular:

- E1/E2 accept numerators were checked against saved aggregates, with no row-level joint E1/E2 accept flags retained in the audited inputs. Independent recomputation of those accepts from scratch requires additional scoring evidence or science replay; the aggregate-only bundle cannot establish it.
- Journal metadata can check availability, saved E3 owner sets, stored owner flags and recorded quality summaries. It cannot establish correctness of the original detector, continuous descriptors, image metrics, source-image identity, or all saved-score calculations without the corresponding underlying artifacts and authorized methods.
- It cannot manufacture the missing comparisons/bank members, a human quality or perceptual-identity judgment, an owner-only experimental arm, active-forgery evidence, or an independent-encoder test. EV-77 is post-hoc explanation from saved flags, not a new arm.
- Re-running GPU construction/regeneration is a different undertaking requiring approved scope, exact code/config/model/dependency pins, source rights and hardware context. Floating-point and cross-hardware variation preclude a blanket bit-exact claim. The F5 report already records last-bit bound differences between platforms.

The retained Windows environment snapshots name Python 3.12.14, torch 2.12.1+cu130, diffusers 0.35.1, transformers 4.57.6, NumPy 2.5.2, SciPy 1.16.2, Pillow 12.3.0, LPIPS 0.1.4, scikit-image 0.26.0 and safetensors 0.6.2. They are metadata snapshots, not a complete attestation for every attempt. A later science package still needs actual driver/GPU/dtype/attempt context, upstream model revisions/notices, dependency hashes where available, and the frozen scripts matching `run-context.code_sha256`. None of that requires installing those dependencies for the table-only bundle.

## 4. Rights and prospective release boundaries

| Material | Local evidence | Proposed disposition and unresolved fields |
|---|---|---|
| Authored code/config/docs and saved scalar metadata | Named scripts, locks, reports and results exist; project-root LICENSE absent in the scoped check | Candidate for release only after actual authors/institution determine ownership, consent and an explicit license. Author names, affiliations, acknowledgments and submission authority remain pending. |
| DIV2K sources and image-derived artifacts | `div2k-heldout-index.json` explicitly says `pending-image-rights`; restricted local academic use, no redistribution/public figures; archive identity unproved | Exclude source/canonical/marked/regenerated pixels from minimal bundle. Descriptor caches also need separate derived-data/rights review; do not infer permission from their numerical format. Source `train` is distinct from study `test`. |
| COCO images | Development receipts retain image-specific CC BY2.0 metadata labels and Flickr hooks, with creator/title verification explicitly incomplete | Release IDs/hashes/URLs and scalar measurements only as reviewed metadata candidates. Do not infer a blanket image license or completed attribution review for the earlier held-out cohort. |
| Tears of Steel footage | Original-footage receipt records CC BY3.0 and attribution `(CC) Blender Foundation | mango.blender.org`; logos/trademarks excluded and actor portrait/privacy rights retained | Keep receipt and shot/pair provenance; exclude pixels from minimal bundle. Any future visual examples need the exact source/derivative attribution join and applicable rights review. |
| SD2.1-base assets | Model lock records pinned revision `4e63672c03103b6c636b8fb4119ba982469b2955`, hashes and CreativeML Open RAIL++-M label; local model card exists | Prefer upstream references plus pins, not weight redistribution. Verify notices, restrictions and component terms before any broader bundle. |
| SD1.5, CLIP, AlexNet/LPIPS assets | A6 lock contains file paths/hashes; no LICENSE/README was returned by the targeted A6 asset filename search | Exact upstream revisions, copyright/license notices and dependency-specific rights remain unresolved here. A hash is not a license grant. Never load pickle/torch formats for this inventory. |
| Paper caches and inspected third-party code | Private MAIN cache exists; `downloads.md` records mixed paper/code terms; PhaseMark has a separate noncommercial license receipt | Exclude fulltexts and unrelated inspected code. Release paraphrased cards, citation metadata, versioned URLs and verified license notices where relevant. Public availability is not blanket redistribution permission. |
| Protected proposal, claims, guide and source plans | R52–55, R60–61 locate protected or externally pinned inputs | Keep read-only and outside a public bundle by default. Refer to evidence/requirements without copying the entire checkout. Historical approvals/chat references require identity review and are not permission to publish now. |

No public release, licensing decision, human approval, supervisor verdict or lawful-ownership claim is recorded by this inventory.

## 5. Historical resources: report only the measured scope

These entries are drawn from the EV ledger and its named saved reports/fields. They are not new timings or a prospective quote. Do not sum overlapping invocations, row durations and run wall times into a total, or equate wall time with GPU utilization.

| EV IDs | Recorded quantity | Hardware/context and cost limitation |
|---|---|---|
| EV-07 | Mean embedding row: F5 22.353525 s; v5 2.296161 s | Mixed Windows/Linux hardware and row overhead; no matched latency superiority test. |
| EV-08–09 | Mean clean C1 row: F5 .414335 s; v5 .338424 s. F5 internal detector mean .220574 s, median .216076 s; v5 internal time absent | These are different timing fields; neither is registry end-to-end latency. |
| EV-17 | F5 continuation wall time 9,625 s; first 14 embedded sources laptop, remaining 286 rented GPU | Report names rented RTX 5070 Ti 16 GB/Linux and laptop Windows. Actual rental invoice/total expenditure unresolved. `max_usd=0` is not evidence of free rental. |
| EV-32 | Final E3 local continuation 15,454.774 s | Laptop CPU/RTX 5070 Ti; earlier attempts also exist. Additional local rental/API cost reported as zero; prior rented-disk storage is separate. Historical budget envelope is not measured spend. No total-study cost inferred. |
| EV-34 | Historical median embedding: E3 130.133 s; F5 52.4685 s; v5 2.578 s | Retained development constructions, not a fresh same-hardware benchmark. |
| EV-40–41 | D1 saved descriptors: 2,555,904 raw bytes for 39 searchable references of 40 planned; .016 s lookup for 3,040 paired calls; extraction snapshot 56.1892 s | Raw bytes omit metadata/index/container overhead. Lookup uses cached scores; snapshot is not cold extraction or production end-to-end time. |
| EV-42 | Recorded step-2 component wall sum 9,361.48 s; budget charge 9,601.48 s | Difference is 240 s interruption allowance, not measured compute. Not a GPU-only total or rental bill. |
| EV-69 | Registry recorded run duration 43,401.126 s (12.0559 h) | Saved `cost.saved_run.usd=0` records the run's local charge; it does not price hardware, power, storage or prior research. No hardware-normalized latency claim. The run's `completed_units=53580` is a planned-unit accounting label: journal outcome count is 53,053 completed, with failures/unavailable units retained. |

Unresolved cost fields: rental invoice amount and billing interval, retained disk charges, all-attempt accumulated expenditure, GPU-active duration, energy and complete per-attempt hardware provenance. Historical figures are adequate for scoped operational reporting, not efficiency ranking.

## 6. Next documentary actions

Resolve author/affiliation/institution and release-license decisions; prepare the table-only input mapping and producer as a separately scoped future artifact task; confirm pinned source snapshots and metadata redactions; retain source/model license notices and precise image attribution joins. These tasks do not repair the scientific gaps: complete banks, matched component controls and diverse fresh negatives remain proposed work. The present output is **README.md plus inventory.csv only**.
