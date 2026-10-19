# C6 search and inspection log

Researcher: Codex C6 agent. Session access date: 2026-10-18. Primary sources only. No experiment, image generation, model loading, extraction, scoring, package installation, or code/data/weight download was performed.

## Discovery

The following web-search queries were used. Counts mean useful primary sources retained for this cluster, not all search-engine hits or exhaustive literature coverage.

| Query | Useful retained primary hits | Disposition |
|---|---:|---|
| `DREW Towards Robust Data Provenance by Leveraging Error-Controlled Watermarking 2024 paper` | 1 | DREW arXiv paper; current v2 methods and evaluation inspected. |
| `site.spec.c2pa.org soft binding durable content credentials specification` | 1 normative source | Several specification versions appeared; current inspected 2.4 consolidated HTML used, earlier versions not counted independently. |
| `site.deepmind.google SynthID image limitations watermark technical images` | 3 | Official product and introductory documentation provided context; SynthID-Image technical paper selected for substantive evidence. |
| `site.nist.gov AI 100-4 reducing risks posed synthetic content provenance watermark fingerprint` | 2 | Official publication metadata and final PDF; one underlying report counted. |

Direct primary-source requests complemented search: arXiv 2610.04151, 2502.04901 and 2510.09263; Adobe TrustMark's C2PA README; C2PA 2.4; NIST AI 100-4. These were supplied leads or references found during inspection, not discoveries claimed from an exhaustive search.

## Inspection record

| Source | Primary URLs inspected | Evidence retained |
|---|---|---|
| Kazempourradi et al. | https://arxiv.org/abs/2610.04151 ; https://arxiv.org/html/2610.04151v1 | Full substantive method/evaluation sections listed in card, especially hybrid Table 19 and near-copy analysis. Submission history showed v1; a v2 request failed. V2 verification is not an arXiv version claim. |
| DREW | https://arxiv.org/abs/2406.02836 ; https://arxiv.org/html/2406.02836v2 | Routing/ECC algorithms, dataset and attack setting, Table 1, limitations and Appendix C. |
| Fairoze et al. | https://arxiv.org/abs/2502.04901 ; https://arxiv.org/html/2502.04901v2 | Signed embedding construction, theorem assumptions, component attacks and explicit deferred-storage passage. An initial older-version cache is retained but superseded for citation. |
| SynthID-Image | https://arxiv.org/abs/2510.09263 ; https://arxiv.org/html/2510.09263v1 | Architecture/training, deployment access model, watermark AND stored-embedding proposal, empirical setup and Tables 1–3. |
| C2PA 2.4 | https://spec.c2pa.org/specifications/specifications/2.4/specs/ContentCredentials.html | Operative clauses on hard/soft binding and repository recovery. Standard V2, not an empirical experiment. |
| NIST AI 100-4 | https://www.nist.gov/publications/reducing-risks-posed-synthetic-content-overview-technical-approaches-digital-content ; https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-4.pdf | Final publication metadata; mechanisms and evaluation framework in §§3–4. Guidance V2, not a benchmark paper. |
| Adobe deployment documentation | https://github.com/adobe/trustmark/blob/main/c2pa/README.md | Entire short README; pointer lookup and decoder signpost. V1 because it provides no evaluation and is not a normative specification. No repository/code download. |

Official SynthID context pages: https://deepmind.google/models/synthid/ and https://deepmind.google/blog/identifying-ai-generated-images-with-synthid/ . They are not separately counted as V2 research.

## Evidence handling and gaps

Substantive primary HTML sections were read through the web tool and locally cached HTML text; NIST PDF passages were read through the web PDF interface. Files, URLs, versions, byte counts and SHA-256 checksums are in `source-artifacts.json`. The cache contains paper/specification text only and lives in the authorized MAIN cache directory. No primary full text is copied into this dossier.

Current source versions were checked for the decisive 2025–2026 papers. No final peer-reviewed venue was verified for the three relevant 2025–2026 arXiv entries; they remain preprints. C2PA's precise publication year and Adobe README's immutable commit were not verified, so neither is invented. The SynthID HTML exposes a limitations heading without substantive body; the card does not claim to have read missing material. SynthID's private deployment and model weights limit independent reproduction, which is separate from V2 source inspection. Exact Copydays pair count was not recovered from the inspected Fairoze passage and remains unreported.

The search supports positive antecedents, not a proof that all prior art has been found. No blanket absence or first-ever novelty claim follows. TrustMark and StegaStamp experimental cards belong to C1, and Roy–Chang retrieval work belongs to C4; this cluster does not duplicate their counts.

## Validation scope

CSV schema, unique citekeys, card references, bibliography keys and synthesis word count are checked as document metadata only. No experiment or analysis script is executed. The skill's generic script-based validation workflow is superseded by this session's research-only restrictions; no scientific interpreter is used.

Validation result: exact 15-column schema; seven rows and seven unique citekeys; six V2 and one V1; all seven referenced cards and bibliography keys exist; synthesis 553 whitespace-delimited words. The primary-text cache contains seven files totaling 8,182,081 bytes, including the superseded Fairoze cache. No shared dossier file or repository history was changed.
