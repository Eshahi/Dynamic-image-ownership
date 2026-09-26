# B4 observed grouping and provisional engineering allocation

Issue #11; 2026-09-26. This is CPU data preparation, not a scientific experiment,
method score, accepted study freeze or compute authorization. B3/#10 and B5/#12
were verified closed after PRs #60 and #63 merged. The original proposal,
6,900-source commitment, A4 analysis contract and A5 rejection policy are unchanged.

## Actual full-frame inventory

`scripts/b4_canonical_inventory.py` read all 5,900 supplied original images and
all 14,000 acquired DiffusionDB images, including excluded bridge records.
Every read was checked against its recorded raw size and SHA-256. There was no
download, model, arbitrary dataset loader, extraction, image inference or resize
for the method. Native B5 canonical processing ran once in the pinned WSL
science environment (Python 3.14.4, Pillow 12.3.0, NumPy 2.5.3, LittleCMS 2.19).

19,884 canonical images passed; 16 COCO records were explicitly rejected:
ten unsupported source modes, four ICC/PyCMSError failures and two ICC/OSError
failures. Passed color actions were 17,619 explicit no-ICC sRGB assumptions and
2,265 ICC conversions. The private inventory contains actual pixel hashes and
separate coarse leakage fingerprints, not detector pHash or CLIP features.

Private evidence stays under the stable project's ignored `.thesis-build/`:

- `b4-private-canonical-20260926.jsonl`: SHA-256
  `f867a38c0a8fce164fd01290378425ea674a9f4609061f38f7b81abb66b87b15`.
- `b4-private-canonical-20260926-summary.json`: SHA-256
  `924f7d43f8c5dd817d48dc1749afac7832618b451b3b0b418383c1d89cd64a3b`.
- Metadata bridge SHA-256
  `e54e3e4a82d7938ffbd2f6d9c77aaec0b6126dc983be19f2ae8218152a6d3d23`.

The three selected rejects are COCO 205289 and 431848 (8-bit grayscale) and
455597 (RGB with failing embedded ICC). All three remain in the 1,000-source
reference set, with explicit rejection reasons and empty canonical identities.
No grayscale fallback, ignored ICC, reserve substitution or deletion occurred.
Canonical eligibility and possible cross-split bridges remain unresolved.

## Prospective grouping and observed allocation

`configs/splits.json` and `src/data/splits.py` implement connected components over
raw bytes, canonical pixels, normalized prompts, prompt/seed, known producers,
an explicitly uncertain unknown-producer quarantine, and coarse pixel similarity.
All 19,900 records participate, not just selected images. Private prompt/producer
fingerprints are not exported to Git; group IDs are opaque membership hashes.

Coarse similarity is a fixed data-screening heuristic: dHash64 distance at most
6, RGB 8x8 mean absolute difference at most 4, and aspect difference at most 5%.
The four-block distance-one candidate index covers every radius-six pair and
checks the complete predicate. This finite screen does not certify all content
independence or replace a visual/rights review.

Observed edge counts: raw 21; canonical 55; coarse near 118; prompt 1,769;
prompt/seed 142; known producer 12,113; unknown cohort 133. Counts are recorded
edges, not distinct independent discoveries. Full frame: 7,627 components.
Selected frame: 3,167 components. Components, including all links to the 32
development reservations, stay in one engineering allocation. No observed
component crosses allocations. The exact source-image quotas remain intact.

| Domain | Development images / observed groups | Validation images / observed groups | Test images / observed groups |
| --- | ---: | ---: | ---: |
| COCO | 200 / 200 | 200 / 200 | 600 / 600 (three unresolved canonical groups) |
| DIV2K | 300 / 300 | 300 / 300 | 300 / 300 |
| DiffusionDB | 1,000 / 259 | 1,000 / 251 | 3,000 / 757 |

One prospective representative per domain/component is selected by a fixed hash
before any method outcome. Other images are retained for coverage, not silently
removed or counted as extra independent observations. This is a proposed unit
rule for review, not a change to an accepted confirmatory analysis.

`data/b4-provisional-v2-20260926/` contains the actual 6,900-row engineering
CSV, conditional precision check, source-partition holdout and grouping summary.
CSV SHA-256: `d295814a40f6cde3b5255ba1a7cf28df53340cf00278652b8cff78e2a4a1630d`.
All rows explicitly set `independence_certified=false`; companion files explicitly
set `final_scientific_split_accepted=false`. These are deliberately not published
as accepted `data/splits.csv`, `data/holdout.json` or a completed B4 deliverable.

The 100 original DIV2K validation images and their linked components are reserved
for test, not fitting/calibration. A source-partition holdout is not demonstrated
new-domain OOD evidence; that B4 objective remains unresolved.

## Scientific boundary and preserved failures

A4 distinguishes unavailable outcomes from otherwise eligible groups (adverse
primary accounting) from invalid source eligibility/unresolved dependence
(uncertain or reduced independent N). The three source rejects are not asserted
eligible independent negatives. Conditional precision uses 597 canonical-screened
COCO test candidate groups, not an assertion of 600 usable independent negatives.
DiffusionDB validation has 251 observed groups: even hypothetical zero-FP 95%
resolution is about 1.186%, not 1%. DiffusionDB test has 757 observed groups,
not the nominal 3,000 independent groups. No actual FP, power, TPR or performance
result is reported. Rights, unobserved links and eligibility can further invalidate
the conditional bounds. No threshold was calibrated and no test score inspected.

The actual independent reviewer `/root/b3_intake_review` accepted the narrow
metadata bridge at `cb402d69d59fcee2987443e281dc04026e60185b` and advised that
retained engineering allocations are defensible but scientific freeze must remain
blocked for unresolved source/bridge/N evidence. That advice is not final B4
acceptance; exact implementation/artifact review is requested separately.

Two early metadata sentinel failures are preserved as described in the metadata
receipt. The initial allocation version used hypothetical counts without separating
the three unresolved groups; its four files are preserved, not overwritten, in
ignored `.thesis-build/b4-provisional-v1-history-20260926/`. Version 2 separates
canonical-screened candidate N and binds the exact canonical-summary digest.
No scientific execution or official Spec Kit state transition occurred.

Checks: nine split tests (including actual public artifact coverage, reservations,
reject preservation and false scientific-acceptance flags) passed in the workflow
venv; two canonical tests and ten preprocessing tests passed in WSL. Existing
script suite: 183 tests, 172 pass and eleven expected dependency skips. Existing
runtime suite: ten tests, nine pass and one expected skip. Broad root discovery
in the workflow venv failed because Pillow/NumPy are intentionally absent; broad
WSL discovery failed because the workflow-only jsonschema dependency is absent.
An initial `scripts/tests` discovery path did not exist. These invocation failures
were followed by the correct environment-specific suites, not an unauthorized
install or an assertion that either broad discovery passed.

Next: independently verify the actual grouping/CSV/reservations and bounds;
resolve source eligibility, cross-split uncertainty, inferential unit/precision and
the OOD requirement under the existing contract before scientific freeze. Issue
#11 stays open and dependent C2/#16 is not ready for acceptance. Technical gaps
do not justify fabricating a human verdict, dropping sources or weakening policy.
