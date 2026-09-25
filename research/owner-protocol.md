# C3a public owner identity and signature protocol

Status: issue [#15](https://github.com/Eshahi/Dynamic-image-ownership/issues/15) implementation and synthetic contract checks, not scientific owner attribution or legal ownership evidence. The exact A5 rule is in [method-spec.md](method-spec.md), and the A3 threat boundary is in [threat-model.md](threat-model.md). `src/signatures/owner.py`, `tests/test_owner.py` and `research/key-test-vectors.json` are the executable contract and fixed known-answer vectors.

## Profile and namespaces

The default profile is **public-derived-existing-image**. OwnerID is a public 1–256-byte strict UTF-8 value after Unicode NFC normalization. No whitespace trimming or case folding occurs; distinct surface strings can canonicalize to the same NFC ID, and a purported wrong-owner control that collapses in this way is rejected. Callers supply 12-bit q as two little-bit-first bytes with the high four bits clear and 32-bit pHash as four little-bit-first bytes. Any non-null `secret_ref` fails closed; the function never accepts, stores, logs or silently ignores private secret material in this profile.

Every packed field is prefixed by its unsigned 32-bit big-endian byte length. The first field is a domain/version: `a5-ws-v1` for semantic and `a5-wi-v1` for instance. SHA-256 then derives exactly 32 bytes each from the A5 field orders `(domain, q, owner)` and `(domain, q, pHash, owner)`. This domain separation and length framing prevent accidental ambiguity between fields/components; it does **not** make the outputs secret. The static detector config ID is bound later to image-domain templates and enrollment, not silently inserted into these A5 signature formulas. Feature-code stability and cross-runtime image parity still require separate tests.

## Wrong owner, rotation and limits

`wrong_owner_control` produces C2 **candidate signatures** for a distinct canonical OwnerID using the same feature codes; downstream detection must still run with the wrong public owner input and record continuous scores. It is not an oracle-key input to the core detector, a measured C2 result or evidence of a low false-owner rate. The fixed test vectors include two owners with identical q/pHash to expose the owner-only difference.

There is no private key to rotate and no registry or automatic ownership transfer in this profile. Changing the public OwnerID requires a new explicit enrollment/marked output and new config/provenance record; `rotation_requires_reenrollment` rejects an NFC-equivalent no-op. Prior enrollment remains historically bound to its original ID and must not be silently relabeled. A future keyed/secret variant would be a separately reviewed threat and research-scope change with wrong-secret controls, not a mode switch here. Public knowledge of OwnerID, q and pHash permits anyone to recompute Ws/Wi; the proposed route cannot by itself authenticate consent, provenance authority or legal title.

The vectors and unit tests are synthetic byte-level checks only. They do not use image data, model weights, scientific compute, a secret-bearing store or paid services.
