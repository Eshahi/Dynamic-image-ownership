# B3 private item-level metadata eligibility ledger, 2026-09-26

Issue [#10](https://github.com/Eshahi/Dynamic-image-ownership/issues/10), draft PR [#60](https://github.com/Eshahi/Dynamic-image-ownership/pull/60). This is the metadata-to-image eligibility bridge required before a final source manifest. It uses the existing pinned Parquet and installed metadata-only PyArrow 21 environment, not another download, model load or experiment. No source/study IDs are frozen.

## Scope and implementation

Previously the strict production selector emitted part-level counts only. The new [private eligibility index](../scripts/b3_diffusiondb_eligibility_index.py) records a source-image-name-keyed eligibility reason and normalized exact-prompt-group digest for each of all fourteen candidate parts' 1,000 metadata rows. These are source metadata identities, **not chosen final source IDs**. Raw prompts, user identifiers, prompt scores and private ZIP JSON content are not exported. Prompt-group fingerprints can disclose low-entropy text through guessing, so they remain in the ignored private index, never Git or a public report.

An optional observer in the [existing strict reader](../scripts/b3_read_diffusiondb_metadata.py) consumes the same immutable hash-verified Parquet snapshot through a read-only mapping of scalar columns, so the callback cannot rewrite authoritative row values. The production selector still checks all candidate image names, scores, dimensions, text and all 2M rows/2,000 x 1,000 part cardinalities. The ledger is written only after complete production success and a match of every part's cardinality and production counts/group totals. Observer-only output cannot substitute for production acceptance. Existing command behavior without the observer is unchanged.

Criteria remain identical: native minimum side 64; both image/prompt NSFW scores strictly below 0.10; image sentinel 2.0 excluded; normalized nonempty prompt. Malformed text/scores/dimensions block even a row that would otherwise be excluded. Production precedence is preserved: score/size exclusion before empty prompt. No subjective image-content, rights, canonical-pixel or near-duplicate verdict is inferred from these metadata flags.

## Actual local evidence

All **14,000 candidate rows** now have private item-level records: **6,791 metadata-eligible images**, **7,206 score/size exclusions**, **three empty-text exclusions**, and **6,219 distinct eligible exact-prompt groups**. The embedded production receipt matches the already-authorized strict selection evidence and the preserved 5,000-image commitment/reserve policy. This is not a 6,791-image final dataset or a 6,219 independent-observation claim.

Ignored output: stable-project `.thesis-build/b3-diffusiondb-integrity-20260926/private-eligibility-index.json`, SHA-256 `8c465e630e299a57ab7979c358a5cff614e78923a4eeceee339fa363f2a38049`. Pinned metadata SHA-256 remains `eecd341187bc91c07f5994ad0660d40228ea025616fd57a509bef8323677c68f`. Only this aggregate/digest is tracked. Do not select final source/dev IDs until actual image integrity, canonical suitability, dependence and handling/content/rights evidence are joined and reviewed.

The fourth completed archive, [part420](../data/intake/20260926-diffusiondb-part-000420-integrity.json), separately passed pinned archive size/full digest, all 1,001 member CRCs and 1,000 full native PNG verification/decode/dimension checks. It recovered within the original writer's third resumable attempt after curl18 at 257,216,331 bytes and curl56 at 565,093,698 bytes; final 593,965,660 bytes matched. The original download writer continues on the existing batch; no partial archive, duplicate writer, source extraction or extra dataset acquisition occurred. The earlier three-part raw-overlap receipt does not automatically include this fourth part.

## Reproduction and open boundaries

Run from the B3 checkout with a NEW ignored output path:

```powershell
& 'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/b3-metadata-venv/Scripts/python.exe' `
  scripts/b3_diffusiondb_eligibility_index.py `
  --metadata 'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/data/raw/metadata.parquet' `
  --output '<new ignored private eligibility index path>'
```

Six focused model-free tests cover normalized groups/no text export, cutoff/sentinel/empty/precedence, malformed excluded rows, incomplete production frame, complete synthetic ledger/count-disagreement failure, and callback mutation rejection. Initial independent review of `ec9810b` found no narrow blocker and independently replayed every candidate row plus part420 CRC/PNG/CSV evidence, while warning that the original observer interface was mutable. This warning was repaired with a read-only scalar mapping; actor `/root/b3_intake_review` re-reviewed exact `302fed4889e560f2aa2427e1860c72949d33d8d9`, passed six focused tests and fresh Parquet replay with identical ledger/production hashes and no remaining narrow finding. Full workflow suite: **168 tests, 160 pass/eight expected dependency skips**; `git diff --check` passed. See [the independent record](../audits/b3-eligibility-ledger-review-20260926/review.md). B3 remains open for remaining actual archives, item-level content/rights and dependence controls, final manifest and development IDs; B5/B4/C2 remain dependent, and the official plan gate stays paused. No scientific compute is authorized or claimed.
