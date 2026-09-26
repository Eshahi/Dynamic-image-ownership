# B3 prospective source-candidate ordering, 2026-09-26

Issue [#10](https://github.com/Eshahi/Dynamic-image-ownership/issues/10), draft PR [#60](https://github.com/Eshahi/Dynamic-image-ownership/pull/60). The download-part rule deliberately was not a final-image algorithm. This supplies an outcome-independent **prospective order** so later image/content/handling exclusions cannot trigger ad-hoc favorable sampling. It does not claim accepted final source IDs or shorten the 5,000-image commitment.

## Ordering fixed before scientific outcomes

The [candidate-order helper](../scripts/b3_source_candidate_order.py) consumes only the previously independently reviewed private eligibility ledger, exact SHA-256 `8c465e630e299a57ab7979c358a5cff614e78923a4eeceee339fa363f2a38049`. No model, quality score, experiment result or archive-arrival order enters ranking. Group and member namespaces differ:

```text
group_rank = SHA256(UTF8("b3-diffusiondb-source-group-v1") || 0x00
                    || revision_bytes || prompt_group_digest_bytes)
member_rank = SHA256(UTF8("b3-diffusiondb-source-member-v1") || 0x00
                     || revision_bytes || canonical_uuid_bytes)
```

Order groups by `(group_rank_hex, prompt_group_digest_hex)` and eligible members within each group by `(member_rank_hex, canonical_image_name)`. Preserve every metadata-eligible member, not just one preferred image. No raw prompts/users/fingerprints are exported publicly. Sorting is invariant to input mapping order; UUIDs, unique source identities and group digests are validated. The CLI additionally binds the exact ledger snapshot and verifies group/member counts against its strict production evidence. It refuses to overwrite earlier outputs.

## Candidate versus final source admission

The pool contains **6,219 exact-prompt groups / 6,791 metadata-eligible members**. Ignored output at stable `.thesis-build/b3-diffusiondb-integrity-20260926/prospective-source-order.json`, SHA-256 `36943976f7ce7e6704669a1aaa7211c6d8ee18dbd28bb87e693ad66fa9f95479`. It does **not** select the first 5,000 now, discard alternatives or claim complete bytes/rights/content. Group ranking is separate from prior part-download order, which is unchanged.

After all fourteen image inventories are complete and independently accepted, a separately reviewed source-admission step may visit this fixed order, consider at most one accepted member per exact-prompt group, and consider members in their fixed order when an earlier candidate fails documented eligibility/content/handling constraints. Every exclusion/replacement must retain a reason. Shared raw-byte groups and stronger dependence evidence may require additional group exclusions; do not use the current eligible-node partial components as final B4 independence groups. B4 must separately address excluded bridges, canonical/near/user dependence and held-out allocation. If fewer than 5,000 admissible sources remain, report the measured shortfall instead of shrinking the target, changing this order, relaxing NSFW/rights constraints or downloading more parts implicitly. No such shortfall or amendment is claimed here.

The source-admission step is not implemented or accepted by this ordering artifact. Any future relaxation/change must be reviewed before outcome exposure; material dataset/resource changes need the user. B3 final manifest/dev IDs, B5 preprocessing, B4 split lock and scientific execution remain separate deliverables, not inferred from this candidate pool.

## Additional completed archive evidence

[Part1467](../data/intake/20260926-diffusiondb-part-001467-integrity.json) and [part558](../data/intake/20260926-diffusiondb-part-000558-integrity.json) each passed pinned full ZIP size/SHA, all 1,001 member CRCs and 1,000 full native PNG verification/decode/dimension/byte-hash checks. Eight parts/8,000 images now have aggregate intake receipts; earlier six-part dependence output is not extrapolated to these two. Original parent38904 continues the authorized batch. Part558 recovered from curl56 at193,960,925 bytes within its second resumable attempt; errors/partials/logs preserved. No new writer, unsafe extraction, model/data acquisition outside the batch or scientific compute occurred.

## Checks and reproduction

Three focused model-free tests cover literal revision-bound rank vectors, permutation/all-member preservation, malformed groups/UUIDs and duplicate source identity. Use the verified workflow interpreter with `scripts/b3_source_candidate_order.py --eligibility '<existing ignored private index>' --output '<new ignored pool path>'`. Independent exact-artifact review is pending at this authored checkpoint. All acceptance flags remain false; the official run stays paused at plan-acceptance and B3 stays open.
