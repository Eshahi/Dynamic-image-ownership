# T3 floor audit

Author self-check, 2026-10-20. This records the topic package's structural and source checks; it is not the independent stage 1b review or a lifecycle verdict.

| Requirement | Actual evidence |
|---|---|
| At least 12 distinct post-hoc methods with V2 method/evaluation reading | **24** distinct methods, 24 dedicated cards and exact versioned primary texts. WAM/VINE settings, final TrustMark, v1/v2 revisions and generation-time variants are not counted again. The survey index is excluded. |
| Native operating point, thresholds and detector side information | Present in each method record/card. Missing calibrated cutoffs or release preprocessing stay explicitly unresolved. |
| Code, weights and license status | Present in all 24 records, including negative/unresolved status. A public repository, paper license and model license are separate. Remote weight metadata is not a download. |
| Conditional regeneration evaluation and costs | Present in each card; missing attack tuples stay missing. Published timing, training fit, parameter storage and unmeasured planning assumptions are separated. |
| At least 10 substantive discovery queries across at least 3 categories | **22 successful distinct discovery queries, 3 categories:** 18 web, one OpenAlex and three official GitHub repository searches. Three failed arXiv API requests and file-fetch retries are excluded. |
| Durable search receipts and coverage discussion | 115 event records, explicit query rows, failure notes and exact heading `what we might still have missed` in search log and synthesis. |
| Source identity and references | 24 versioned method bibliography records plus separately inspected final TrustMark = **25** records. Authors, title, year, version, venue/unknown status, canonical URL, stable ID, citekey and access date are recorded; DOI is null where not established for the inspected version. |
| Cache and hash traceability | **24/24 current method texts match.** Of **122** acquisition/reuse cache records, **120** match the recorded digest. Two earlier GitHub HTML snapshots were overwritten by later fetches of the same URL; historical digests remain preserved, current hashes are recorded, and both extracted-text hashes remained identical. No false all-receipts-match claim. |
| Scope and proposals | Only WAM and VINE-R remain approved external core arms. P1/P9 are conditional additions; P2/P3 deferred. No P11, GPU run, weight download, image access, new scoring/outcome or shared-state change. |

The executable self-check is `tools/check_package.py`, using only stdlib and this topic's own documents. It checks card/metadata completeness, unique method/reference identities, source hashes, query categories, critical corrections, relative links and whitespace. It does not execute upstream code, judge scientific success, certify a license, or replace the fresh independent reviewer. Its output is [floor-audit.json](floor-audit.json).

All primary full text stays in the external MAIN cache. Source acquisition/HTML extraction and topic-document builders are reproducibility aids, not experiment infrastructure. Unavailable journal full texts are not V2. Complete native adapters, exact mutable checkpoint hashes, dependency permissions and target-server measurements remain future work if a proposal is approved.

## what we might still have missed

The two inaccessible 2026 journal leads, unindexed/renamed methods, updated releases, unavailable supplements and the failed arXiv API route limit coverage. The floor is exceeded without claiming an exhaustive literature census. See [search-log.md](search-log.md) and [synthesis.md](synthesis.md) for the concrete leads and boundaries.
