# Development image inspection notes

2026-10-04, primary researcher machine inspection, exploratory only. This is not a human visual-quality or semantic assessment and supplies no human verdict for the research contract.

- Viewed source and saved hybrid C1 for reserved source1675 from `20261003-2347-A-hybrid-pilot`; no obvious gross spatial/content disruption was visible in these previews. Use saved RGB quality metrics and the fixed threat inventory, not this qualitative observation, for quantitative claims.
- Viewed `20261004-0000-gs-native/prompt-0-C1-clean.png` and its `regen-0.4-seed0` counterpart. Both show the requested mountain lake scene; ridge/shoreline and reflection detail change. This is an agent observation on one selected engineering example, not proof of admissibility across the cohort. Retain every attack and numeric CLIP/quality result, including failures.
- Native GS `run.json` currently contains the inherited phrase `secret whitening key` in its detector-side-information description. The manifest exposes the fixed development key and nonce; the experiment uses public development fixtures. Treat that field as imprecise historical metadata, never a security guarantee. The adaptation document, B-LW1 design and final comparison must state the public fixture and enrolled reference payload explicitly. Do not edit the retained run to correct this wording.
