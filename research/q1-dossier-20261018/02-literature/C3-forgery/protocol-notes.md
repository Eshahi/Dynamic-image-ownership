# Protocol context: trusted timestamps are not ownership adjudication

Supplemental standard, not counted toward the ten V2 research papers.

- Citation: C. Adams, P. Cain, D. Pinkas and R. Zuccherato. *Internet X.509 Public Key Infrastructure Time-Stamp Protocol (TSP).* RFC 3161, August 2001.
- Source: [RFC Editor full text](https://www.rfc-editor.org/rfc/rfc3161.html).
- DOI: not independently looked up; omitted.
- Access date: 2026-10-18.
- Inspection: §§1, 2.1, 2.2, 2.3 and 2.4.1. This is selected protocol text, not a complete security audit or current cryptographic deployment recommendation.

Section 1 defines evidence that data existed before a time. Section 2.1 requires a trustworthy time source, collision-resistant data imprint and timestamp signing key. It also says the authority does not inspect the imprint beyond specified checks and excludes requester identity from the token. Section 2.4.1 requires separate authentication means if requester identity is needed.

**Inference for the thesis:** a timestamp over a record can support chronological commitment under an explicit trusted-authority assumption. It cannot by itself establish image authorship, make an inadmissible enrollment legitimate, or prove that semantically similar images share a creator. A signed enrollment can authenticate the submitting key without proving content origin. These are threat-model requirements; designing ownership ledgers remains outside thesis scope.

