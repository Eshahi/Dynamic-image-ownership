# Draft submission materials

Extension E6, 19 October 2026. Conditional destination: IEEE Transactions on Information Forensics and Security (TIFS), with TMM and TOMM as backups. These materials are an editable draft, not a submitted or submission-ready package. No author approval, institutional decision, conflict declaration, originality statement or public-release commitment is inferred. Current evidence does not establish a sufficient Q1 contribution; F1/F2 and the documentary gaps in `FINAL-REPORT.md` remain substantive prerequisites for the recommended route.

## Cover-letter draft

`[Date of an actual future submission]`

Dear Editor,

Please consider our manuscript, “From Watermark Recovery to Registered-Image Attribution: An Empirical Study Under Diffusion Regeneration,” for publication in IEEE Transactions on Information Forensics and Security.

The manuscript examines a distinction relevant to image forensics: recovering a watermark does not by itself establish that a suspect image corresponds to the correct enrolled record. We study an image-domain, encoder-directed watermark with a trusted registry of published-image descriptors. The registry is declared detector side information, and the study separates recovery, content specificity, accepted-owner ambiguity and abstention. We acknowledge prior watermark–registry hybrids, including DREW, TrustMark and SynthID-Image; we make no priority claim for that architecture.

The retained frozen evaluation illustrates why these distinctions matter. Intended-record recovery by a majority of three scheduled regeneration seeds succeeds for 277 of 300 sources with SD1.5 and 280 of 300 with SD2.1-base at strength .2. Nevertheless, the frozen descriptor check accepts three operationally different real look-alike pairs among 45, from two of 16 shots of one film, causing the overall confirmation to fail. These descriptor-only accepts are not presented as demonstrated whole-system forgeries. We also report unavailable observations and the dependence created by shared sources and records.

In passive competing enrollment, the complete-case pointer-assisted rule returns no competing-owner attribution, while fingerprint-only matching frequently admits both owners. The frozen banks are incomplete, and stronger further regeneration increases abstention. A post-hoc count of saved native calls shows that the competing owner already fails the owner gate in every completed query. Consequently, these observations do not identify incremental rejection from the code or content check and do not establish active re-marking security.

`[TODO:EVIDENCE — Replace this paragraph with the actual externally relevant scientific increment after the component-identifying comparison and fresh, diverse hard-negative study have been completed and reviewed. If those studies do not support the planned contribution, revise the framing and destination before sending this letter. Do not claim a matched baseline, an independently trained encoder, active-attack resistance or a successful confirmation that has not been measured.]`

We believe the precisely bounded question of registered-image attribution is relevant to TIFS's information-forensics and security audience. The manuscript distinguishes empirical error events from legal ownership, secret-key authentication and general security guarantees. Its negative results and missingness are retained rather than hidden behind recovery metrics.

`[TODO:AUTHOR — Insert the confirmed author list, corresponding author's affiliation and contact details, author-approval and concurrent-submission declarations, relevant earlier dissemination, conflicts and funding, and the actual artifact-access statement. Verify any journal-specific disclosure requirements at submission. No declaration has been made on the authors' behalf.]`

Sincerely,

`[Corresponding author, confirmed by the user]`

### Letter evidence map and use boundary

Recovery numbers: EV-50–52. Real look-alike failure and interpretation: EV-55/70/71. E3 ambiguity, abstention and completeness: EV-58–66/75. Owner-gate explanation: EV-77. Registry/method assumptions: EV-72 and `05-theory-security.md`. Prior-art and later-citation boundaries: `03-novelty-positioning.md` and `14-forward-citation-sweep.md`. EV annotations need not appear in an eventual letter, but every numerical sentence must remain traceable.

Do not send this draft with the TODO paragraphs or merely delete them to imply readiness. The existing TIFS fit assessment is conditional; a negative result in one locally designed system is not automatically an externally consequential negative result. The user controls publication and author declarations. This session neither contacts an editor nor selects reviewers.

## Highlights draft

These four short statements are optional editorial material, not a claim that TIFS currently mandates an Elsevier-style highlights file. Verify the chosen journal's live format at submission.

- Source-level recovery does not establish registered-image specificity.
- A frozen descriptor check accepts 3 of 45 real look-alike pairs.
- Passive zero-beta attribution is explained by owner-gate rejection.
- Missing banks, ambiguity and abstention bound the security interpretation.

The second highlight must accompany the one-film, descriptor-only qualification in the abstract/text. The third is a post-hoc explanation of saved calls, not a newly tested owner-only arm. None claims a first architecture or a general impossibility theorem.

## Graphical-abstract description — no image produced

**Communication job:** Show that watermark recovery, correct registered-image matching and competing-owner rejection are distinct questions. Lead with the measured separation, not an ownership shield or certification symbol. The visual should be understandable without reading bit-level implementation details.

**Proposed layout:** A clean horizontal schematic, adaptable to the eventual venue's verified dimensions. On the left, a plain labeled rectangle represents an existing photograph; no real source pixels or synthetic example are required. The middle shows “Image-domain mark + trusted registry,” with a clearly labeled registry side-information arrow to the verifier. On the right, three aligned outcome rows have short text and small count labels. Use the same color and pattern definitions as Figure 3 in `15-figure-specifications.md`.

**Exact text hierarchy:**

1. Main heading: “Recovery is only one part of attribution.”
2. Recovery row: “Strength .2: 277/300 and 280/300 source-majority successes.” Small qualifier: “SD1.5 / SD2.1-base; missing outputs count as misses.”
3. Specificity row: “Descriptor check: 3/45 real look-alike pairs accepted.” Small qualifier: “2/16 shots, one film; overall frozen confirmation fails.”
4. Competition row: “Conditional zero beta; owner gate already rejects beta.” Small qualifier: “Passive enrollment; incomplete banks; q/content benefit not identified.”
5. Footer: “Trusted registry side information • Image-domain writer • No active-forgery guarantee.”

Do not put “secure,” “proof of ownership,” “independent-encoder robustness,” “first hybrid,” or a universal zero-error claim in the visual. Avoid a large green checkmark for the full system: the recovery endpoint succeeds while the overall frozen confirmation fails. Use a warning/error label only for the measured descriptor endpoint, not as evidence of an executed full-pipeline attack. An explanatory empty/ambiguous owner-set icon may supplement text, but no rendered example should imply a human identity judgment.

**Caption/alt-text draft:** “A registry-assisted watermarking study separates regeneration recovery from image-specific attribution. Source-majority recovery succeeds for 277/300 and 280/300 photographs under two fixed strength-.2 channels, but a descriptor check accepts 3/45 operationally different real look-alike pairs. Conditional passive competing-owner rejection is already explained by the owner gate; missing banks and abstention constrain the interpretation.”

**Production boundary:** This is a text brief only. No graphic, illustrative image, plotting script or graphical-abstract submission file was created. Later production must retain the qualifications and use actual accepted manuscript evidence. The diagram does not replace the full field-level specifications in `15-figure-specifications.md`.

## Adaptation if the destination changes

For TMM, emphasize multimedia attribution and the recovery–specificity trade-off, but do not remove the security/side-information limits. For TOMM, emphasize the complete multimedia system and reproducible decision contract, with its current format and open-access requirements verified before submission. In either case, the same missing scientific evidence remains; changing the venue name in the letter does not resolve it. Current rankings, institutional eligibility, page rules and costs are recorded with their remaining verification gaps in the WP4 files.
