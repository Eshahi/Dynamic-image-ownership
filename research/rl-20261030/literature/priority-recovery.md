# Priority full-text recovery: SPAR-RL and SMER

Access date: 2026-10-30. Scope: bounded supplementary search, primary full texts only. Author: priority-recovery subagent. This document adds **zero inspected-paper cards**. Both papers remain **UNINSPECTED**. No experiment, interpreter, download, install, external message, or git operation was performed. The authoritative STATE was read once at startup; its latest entry said that no F6 output existed. No F6 outcome or Phase B per-source journal was inspected.

## Outcome and interpretation

- **SPAR-RL:** bibliographic identity confirmed on an opened author-laboratory publication list, but the full text was not recovered. Its state/action/reward details, numerical effects, comparison fairness, and exact scope are therefore not certified here. It remains a priority unresolved precedent; this search does not justify claiming novelty against it.
- **SMER:** the official repository was opened and the official CVF paper was located, but the paper and landing page returned HTTP 403. No accessible primary author manuscript was found. The method/evaluation were not inspected, so no full-text card, numerical claim, RL classification, or definitive preemption judgment is supplied. The repository does not substitute for a full-text evaluation audit.
- **JUDGMENT:** retain the existing conservative novelty reservations for RL embedding-cost learning and RL ensemble reweighting. An access failure is neither evidence that the idea is unoccupied nor evidence of effectiveness against diffusion regeneration. Neither unresolved paper may increase a cluster's inspected-card count.

The recovery limit was at most 12 distinct discovery queries per paper. SPAR-RL used 12; SMER used 8. Discovery used general-web search, including indirect domain-restricted queries; no native scholarly-index search was performed. Some SPAR-RL strings repeat searches already present in `c1-watermark-stego.md`: these are new recovery attempts, **not additional distinct queries for that dossier's deduplicated total**. The final batches produced no new accessible primary manuscript. That supports ending this bounded recovery task, not a global literature-exhaustion claim.

## Paper identities and primary-source access ledger

### SPAR-RL — UNINSPECTED

Title: *An Automatic Cost Learning Framework for Image Steganography Using Deep Reinforcement Learning*. Authors: Weixuan Tang, Bin Li, Mauro Barni, Jin Li, Jiwu Huang. Venue/year/pages: IEEE Transactions on Information Forensics and Security 16 (2021), 952–967. DOI: `10.1109/TIFS.2020.3025438`. Stable ID: IEEE 9205850. Suggested citation key: `Tang2021SPARRL`.

| Primary URL | What was actually obtained |
|---|---|
| [Author laboratory publication list](https://clem.diism.unisi.it/~vipp/journals.html) | Opened successfully; 2021 section, lines 159–161 of extracted page identifies all five authors, title, volume, pages and DOI. The paper's link 64 goes to IEEE, not an author PDF. |
| [IEEE record](https://ieeexplore.ieee.org/document/9205850) | Open returned only a JavaScript/robot verification page; no paper. |
| [University of Siena record](https://usiena-air.unisi.it/handle/11365/1204063) | Direct open returned HTTP 403. Search-index rendering lists the editorial PDF as private/restricted and offers a copy request. This is an access lead, not method/evaluation inspection. No request was sent. |
| [Bin Li faculty page](https://ceie.szu.edu.cn/en/info/1017/1107.htm) | Discovery showed the bibliographic entry; direct open timed out. No manuscript obtained. |
| [Shenzhen laboratory news](https://media-sec.szu.edu.cn/xwdt/a2021xwdt.htm) | Search discovery found an acceptance announcement, not a manuscript. Not used for scientific claims. |

No paper-derived effect or mechanism claim is added. Secondary catalogues, later papers citing SPAR-RL, and abstract reproductions were rejected as substitutes.

### SMER — UNINSPECTED

Title: *Ensemble Diversity Facilitates Adversarial Transferability*. Authors: Bowen Tang, Zheng Wang, Yi Bin, Qi Dou, Yang Yang, Heng Tao Shen. Venue/year/pages: CVPR 2024, 24377–24386. DOI lead: `10.1109/CVPR52733.2024.02301` (discovery metadata; publisher full text not opened). Suggested citation key: `Tang2024SMER`.

| Primary URL | What was actually obtained |
|---|---|
| [Official CVF PDF](https://openaccess.thecvf.com/content/CVPR2024/papers/Tang_Ensemble_Diversity_Facilitates_Adversarial_Transferability_CVPR_2024_paper.pdf) | Direct HTTPS open returned HTTP 403. HTTP redirected to the same failing HTTPS URL. A second available web connector also returned 403. `?download=1` and the `www.openaccess` host variant were inaccessible. |
| [Official CVF landing page](https://openaccess.thecvf.com/content/CVPR2024/html/Tang_Ensemble_Diversity_Facilitates_Adversarial_Transferability_CVPR_2024_paper.html) | Direct open returned HTTP 403. Indexed discovery exposed citation metadata and abstract; these do not satisfy full-text inspection. |
| [Official repository](https://github.com/tangbwb/SMER) | Opened successfully. README identifies an official MI-FGSM example; root listing contains configs, utils, README, attack_method.py, release.py. No paper file/link was present in the inspected root/README. Dataset/model links were not followed. No code was downloaded or run. |

Search returned an indexed first-page extraction from CVF and an apparent third-party Bytez transcription. Neither was treated as a successfully inspected primary full text: the CVF extraction did not include the method/evaluation and Bytez was not an authorized primary manuscript source. ResearchGate discovery was request-only; no request was made. Generic author or citation aggregators did not provide a primary manuscript.

## Exact discovery queries

Tool: `web.run.search_query`, invoked through `functions.exec`. Queries in each labelled batch were sent together; result descriptions deliberately report batch leads rather than fabricating a per-query result ranking. A URL in the access tables identifies the exact retained primary lead. General discovery and indirect site searches are distinguished below.

### SPAR-RL: 12 distinct queries

| ID | Exact query | Route | Observed batch result |
|---|---|---|---|
| S01 | `"An Automatic Cost Learning Framework" pdf` | General web | S01–02: Siena restricted record; no qualifying full text. |
| S02 | `"SPAR-RL" Tang pdf` | General web | Same S01–02 batch. |
| S03 | `"3025438" pdf` | General web | S03–05: overwhelmingly unrelated numeric-ID matches; one secondary bibliographic catalogue. No manuscript. |
| S04 | `"An Automatic Cost Learning" Tang author manuscript` | General web | Same S03–05 batch. |
| S05 | `"SPAR-RL" "Weixuan"` | General web | Same S03–05 batch. |
| S06 | `"An Automatic Cost Learning Framework for Image Steganography" -site:scinapse.io -site:usiena-air.unisi.it` | General web | S06–08: secondary bibliographic/abstract pages and later citing papers; no target primary full text. |
| S07 | `"SPAR-RL" site:github.com` | Indirect GitHub-domain search | Same S06–08 batch; no author manuscript obtained. |
| S08 | `"SPAR-RL" site:arxiv.org` | Indirect arXiv-domain search | Same S06–08 batch; unrelated 2026 SPAR title also surfaced. |
| S09 | `"Weixuan Tang" "SPAR" pdf` | General web | S09–12: Siena author-lab list, Shenzhen faculty/news pages, restricted Siena record, secondary catalogues. Follow-up opened the lab list and IEEE; no target full text. |
| S10 | `"An Automatic Cost Learning" site:arxiv.org` | Indirect arXiv-domain search | Same S09–12 batch; no arXiv version verified. |
| S11 | `"An Automatic Cost Learning" site:szu.edu.cn` | Indirect institutional-domain search | Same S09–12 batch; faculty/news leads only. |
| S12 | `"An Automatic Cost Learning" site:unisi.it pdf` | Indirect institutional-domain search | Same S09–12 batch; author-list IEEE link and restricted institutional record. |

### SMER: 8 distinct queries

| ID | Exact query | Route | Observed result |
|---|---|---|---|
| M01 | `"Ensemble Diversity Facilitates Adversarial Transferability" pdf` | General web | Official CVF landing/PDF, secondary catalogues, Bytez transcription lead. CVF direct access failed. |
| M02 | `"Ensemble Diversity Facilitates Adversarial Transferability" arxiv` | General web | Same official CVF source and citation catalogues; no arXiv identifier verified. |
| M03 | `"Ensemble Diversity Facilitates" site:cuhk.edu.hk` | Indirect institutional-domain search | M03–05: official repository, request-only ResearchGate, CVPR proceedings listing and citations in other papers; no primary author PDF. |
| M04 | `"Ensemble Diversity Facilitates" site:arxiv.org` | Indirect arXiv-domain search | Same M03–05 batch; no arXiv identifier verified. |
| M05 | `"Ensemble Diversity Facilitates" Tang pdf -site:openaccess.thecvf.com -site:bytez.com` | General web | Same M03–05 batch. |
| M06 | `"Ensemble Diversity Facilitates" site:uestc.edu.cn` | Indirect institutional-domain search | M06–08: same CVF/repository, request-only ResearchGate, author aggregators, and citing articles; no new primary manuscript. |
| M07 | `"Ensemble Diversity Facilitates" "Qi Dou" pdf` | General web | Same M06–08 batch. |
| M08 | `"Ensemble Diversity Facilitates" "pdf" "Tang" -site:openaccess.thecvf.com -site:bytez.com -site:researchgate.net -site:openreview.net` | General web | Same M06–08 batch. |

## Integration instruction

Keep both existing UNINSPECTED entries. Do not add this recovery note as a paper or count it toward a floor. The C1 shortfall and its broader exhaustion justification remain the responsibility of the parent dossier; these 12 repeated/extra recovery queries do not independently establish the required four-index coverage. This task does not revise any scientific conclusion, candidate score, probability, or frozen run.
