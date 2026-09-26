# Independent B3 first-archive integrity review, 2026-09-26

Author `/root`; independent actor `/root/b3_intake_review`. Exact reviewed commit `2bb9cf75986c16cd588721535ba66acd23dd09ae`. Authority: AGENTS.md and research/approval-policy.md delegated read-focused technical review.

Verdict: **no blocking finding for private-index and completed-part integrity evidence only**. No final IDs, content/rights acceptance, B3 closure, lifecycle transition or scientific result is accepted.

The reviewer independently rebuilt the private index in memory from the pinned hash-checked Parquet snapshot: all fourteen parts / 14,000 records match the existing ignored index and its SHA-256 `c987a60ce1c21335b6a6ef5887530e7be8b1013b86d0272d3c2441978c20f829`. Read only completed part 948; verified exact archive size/upstream digest, fully replayed CRC, Pillow verification and pixel decoding for all 1,000 PNGs, and reproduced the entire per-image CSV digest `95faffa4267a925846ca22f4ebf80b60c9e84ed0f6e48470465fd248a4c02b44`. Reproduced 1,001 members, 559,958,716 uncompressed bytes and metadata JSON digest `c2e524a1a3236d74ff8a6d73c983106c67b6e53afd89642b250e44ef5c9801d4`. All five focused adversarial/synthetic tests independently passed in the existing Pillow environment, with no model import.

Reviewed preallocation size guard and same-snapshot source parsing, directory/member/cardinality/link/encryption/compression and byte/pixel safeguards, full CRC and PNG native-dimension/mode/frame/decode checks. Metadata JSON content remains unparsed/unexported. Reviewer changed no files and did not inspect partial ZIPs or interfere with download processes.

Retained operational limits:

- Root member layout is verified for **part 948 only**. Every later part must pass independently; wrappers/layout differences must block rather than be silently admitted.
- Use the reviewed private index digest. A caller-supplied digest binds an input; it does not itself certify its provenance.
- Byte integrity is not content safety, rights, duplicate independence, final source eligibility or scientific evidence.
