# Independent B3 COCO candidate review, 2026-09-26

- Author/controller: `/root`.
- Independent reviewer: `/root/b3_intake_review`, a read-focused delegated subagent.
- Exact reviewed commit: `c598b7e6b1c6de72b04ac6604da9f3ee08147410`.
- Review returned: 2026-09-26, before author checkpoint 09:12:49 UTC.
- Authority: `research/approval-policy.md` and AGENTS.md technical-review delegation.
- Scope: source-candidate generation and reproducible provenance only; **not** final dataset IDs, item-level rights, study allocation, B3 acceptance, scientific execution or a Spec Kit gate decision.

The reviewer returned no blocking findings. Independently checked whole-frame validation including excluded-license rows, same-snapshot CLI hashing/parsing and fixed production counts/output exclusivity. In-memory replay matched the complete committed JSON; separate eligible-population and rank computation confirmed all candidate/reserve IDs. Confirmed 1,274 eligible, 3,726 license-label exclusions, 1,000 candidates (677 BY / 323 BY-SA), 274 reserves and output digest `37dbd65045497b54a02d14b965824c2155606a0a39d194eced4bc5bdfceff270`. All eight focused tests passed independently. The reviewer accepted only these narrow implementation/provenance claims and found documentation appropriately separates labels, attribution hooks, rights, sampling limitations and study splits.

Non-blocking warnings and disposition:

1. Known-vector test recomputed its expected formula rather than pinning literal digests/order. Author repaired the test with three literal digests and exact ordering; no production implementation or candidate JSON changed.
2. Reserve capacity is not a guarantee of 1,000 finally acceptable images. Retain this warning: later rights/content/dependence exclusions must preserve ranked replacements and report a shortfall.
3. Bound inventories/selection were reviewed, not renewed image decoding/current Flickr rights. Retain this evidence limit explicitly. Prior intake evidence is not a current rights certification.

No reviewer file writes or external mutations occurred. The author records the actual returned verdict; no human verdict is asserted and the official Spec Kit remains paused at plan-acceptance.
