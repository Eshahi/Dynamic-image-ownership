# Superseded first extraction: retained, not scientific evidence

Two analysis implementation errors were found against the frozen contract before interpretation:

1. Rinse journal rows retain the base seed 12/13/14. The adapter adds 100 internally for the second pass. Looking up rows under 112/113/114 incorrectly made every rinse call appear missing. Correcting the join changes no underlying experiment or hypothesis.
2. The initial caliper diagnostic omitted the requirement that both LPIPS values occupy the same frozen bin and used an L1 rather than squared distance tie-break. It returned three F5 matches; the frozen T7 same-bin algorithm returns two. The correct bins and selection rule are in `design-research/T7-fair-reporting/synthesis.md`, lines 50–66.

The copies in this folder preserve the failed script/output. Use the parent-folder corrected analysis only. The original journals and experiment files were not changed. Continuous WAM bit accuracy also needs explicit coverage because empty masks yield missing accuracy, not chance or zero accuracy.
