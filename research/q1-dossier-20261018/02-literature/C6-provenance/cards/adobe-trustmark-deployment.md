# Adobe — TrustMark's deployment role

- **Title/author:** Using TrustMark with C2PA; Adobe TrustMark maintainers.
- **Version/date:** live main-branch documentation inspected 2026-10-18; commit and original publication date unverified.
- **URL:** https://github.com/adobe/trustmark/blob/main/c2pa/README.md ; DOI none.
- **Verification:** V1 under the dossier's strict experimental-paper rule: the complete deployment documentation was read, but it is neither an evaluation paper nor a normative standard. Do not count it as another TrustMark experimental paper.
- **Locators:** “Durable Content Credentials”; “Signpost watermark”.

**Direct evidence.** A random watermark identifier retrieves a retained C2PA manifest from a database. A separate signpost mode identifies another watermark decoder using a C2PA algorithm identifier. The documentation specifies BCH_SUPER for that mode. Database access and the relevant decoder are required; the page provides no dataset, robustness evaluation or false-positive numbers.

**Inference/relevance.** Deployment context only. The TrustMark research card belongs to C1. This page's commercial use does not prove that a recovered identifier authenticates an image or owner. No code was downloaded or executed.
