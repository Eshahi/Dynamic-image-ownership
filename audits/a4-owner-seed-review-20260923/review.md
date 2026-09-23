# Independent A4 owner/seed schedule review

Date: 2026-09-23. GitHub issue #5. Author: `/root`; independent read-only reviewer: `/root/a4_protocol_review`. This is a narrow follow-up to the earlier A4 protocol-amendment review, not a Spec Kit gate decision or human approval. The primary author transcribed the reviewer's findings; the reviewer made no file, GitHub or controller edits and ran no scientific experiment.

| Exact reviewed artifact | SHA-256 |
| --- | --- |
| `research/acceptance.md` | `DE5027EB1DA96C854608ADCB6FBCA242976B3BFF5D1B44FF77A75DDDFB135E6B` |
| `research/sample-size.md` | `BF4D89FBC5D1EDBA2D172F271C91340ECD9AD9A94401F8F1222C7F5F785F2122` |
| `research/stop-rules.md` (unchanged from preceding review) | `9A4AEA670D88D77D468A9A82DF043EC0AB4A5B44C3CBA98539608A82DAFE2860` |

The reviewer verified the public 16-OwnerID roster, one deterministic uint64 seed per frozen source UID, K=1 wrong-owner assignment, absence of test-score selection and the illustrative parity vector (`owner=9`, `wrong_owner=10`, `seed=4369173439443558334`). The roster fits A5's NFC UTF-8 OwnerID contract; distinct domain tags and byte-length framing avoid accidental reuse of the owner-index digest as a seed. The resolved configuration's `embedding.noise_seed` and `embed_existing(..., seed)` must agree exactly. The new uint32 UID-length limit, full-precision JSON parsing rule and hexadecimal receipt address the reviewer's transport warning for seeds above `2^53−1`. A5's schema admits uint64 seeds. The reviewer found **no blocking documentary inconsistency within this narrow scope** and confirmed the prior threshold/missingness amendment remains coherent.

This is a **pre-data, pre-implementation** rule, not evidence that B3/B4 identities/grouping exist or that the runtime obeys it. Implementation parity tests should cover the exemplar, zero and high uint64 seeds, UID errors and resolved-config equality. A4 still lacks pinned metric implementations, attack/comparator protocols, paired margins, complete data/resource receipts and an executable authorization package. The run remains paused at `plan-acceptance`.
