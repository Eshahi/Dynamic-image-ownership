# InvisMark v2 targeted method inspection

Inspected 2026-09-23 UTC by /root. Source: https://arxiv.org/html/2411.07795v2
Same paper/revision as invismark-v2.md; deeper access, not a second publication.

Locators: sections 2.1–2.4.1, 3 introductory evaluation paragraph, 3.3–3.5.
The method adds a scaled neural residual and uses a trained ConvNeXT-base decoder. Authors evaluate generated images and DIV2K. The proposal at inputs/proposal-text.md:177 says these methods focus on generated images and usually lack comprehensive real-camera-image evaluation, not that they evaluate generated images only. DIV2K inclusion qualifies that discussion but does not refute the concern about comprehensiveness. Training images are nonpublic. Section 3.3 reports residual-transfer forgery with public encoder access and regeneration vulnerability; these are author results, not our reproduction.

Inference: this is a neural-decoder candidate for RQ-03, not an inversion comparator for METRIC-07. No baseline commitment follows yet.

Limits: targeted sections only; no full-paper proof or execution audit. Notes checksum identifies this local observer record, not remote paper bytes. The original abstract record remains historical.
